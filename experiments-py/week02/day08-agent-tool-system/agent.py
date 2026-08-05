from .state import AgentState
import json
from .memory import Memory


class Agent:
    MAX_TOOL_PER_STEP = 3

    def __init__(
        self,
        planner,
        executor,
        replanner,
        evaluator,
        decision,
        generator,
        reflection,
        improver,
        router,
        max_steps=30,
    ):
        self.planner = planner
        self.executor = executor
        self.replanner = replanner
        self.evaluator = evaluator
        self.decision = decision
        self.max_steps = max_steps
        # Day9 新增
        self.generator = generator
        self.reflection = reflection
        self.improver = improver
        # 改进触发标准
        self.reflection_threshold = 8
        self.router = router

        # Day10 新增
        self.memory = Memory()

    def _tool_key(self, name, args):
        return (name, json.dumps(args or {}, sort_keys=True))

    def _run_tool(self, state, name, args):
        """执行工具并写入缓存，相同 (工具, 参数) 命中缓存不再重复执行。"""
        key = self._tool_key(name, args)
        if key in state.tool_results:
            return state.tool_results[key]
        result = self.executor.execute_tool(name, args)
        state.tool_results[key] = result
        return result

    def run(self, goal):
        history = self.memory.retrieve()
        state = AgentState(goal)
        state.steps = self.planner.create_plan_dynamic(goal, history).steps
        first_action = True
        steps_done = 0
        tool_attempts = 0
        while state.steps and steps_done < self.max_steps:
            steps_done += 1
            step = state.steps[0]
            state.current_step = step

            # Act：对当前步骤生成动作，工具动作走统一缓存入口，避免重复执行
            action = None
            if first_action:
                action = self.router.route(step)
                if action.type == "tool":
                    observation = self._run_tool(state, action.tool, action.args)
                else:
                    observation = self.executor.execute_llm(action.prompt)
                first_action = False
            else:
                # Act
                observation = self.executor.execute_llm(step)

            state.observation = observation
            state.observations.append(
                {"step": step, "action": action, "result": observation}
            )

            # 评价
            state.evaluation = self.evaluator.evaluate(state, observation)

            # Think
            decision = self.decision.decide(state)
            state.next_action = decision.action

            if decision.action == "tool":
                # 同一步工具尝试次数上限，防止 LLM 反复调用同一工具
                if tool_attempts >= self.MAX_TOOL_PER_STEP:
                    state.steps.pop(0)
                    state.completed.append(step)
                    tool_attempts = 0
                    continue
                tool_attempts += 1

                # 走统一缓存入口，命中则不重复执行
                tool_result = self._run_tool(state, decision.tool, decision.args)

                state.observation = tool_result
                state.observations.append(tool_result)
                continue

            # 非 tool 动作：本步结束，弹出该步骤
            tool_attempts = 0
            state.steps.pop(0)

            if decision.action == "continue":
                state.completed.append(step)
                continue

            if decision.action == "replan":
                state.failed.append(step)
                state.failed.append(decision.reason)
                new_plan = self.replanner.replan_dynamic(state, decision.reason)
                state.steps = new_plan.steps

            if decision.action == "finish":
                state.completed.append(step)
                break

        if not state.completed:
            return f"目标未完成：{goal}"
        # else:
        #     answer = f"完成 {len(state.completed)} 步：\n" + "\n".join(state.completed)

        # 根据计划生成结果
        answer = self.generator.generate(state)

        # reflection 评价
        reflection = self.reflection.evaluate_answer(goal, answer)

        if reflection.score < self.reflection_threshold:
            answer = self.improver.improve_answer(goal, answer, reflection.issues)

        self.memory.save(
            {
                "goal": goal,
                "completed": state.completed,
                "failed": state.failed,
                "observations": state.observations,  # 暂时全存，未做压缩筛选
                "reflection": reflection,
                "final_answer": answer,
            }
        )

        return answer
