from state import AgentState
import json


class Agent:
    MAX_TOOL_PER_STEP = 3

    def __init__(self, planner, executor, replanner, evaluator, decision, max_steps=30):
        self.planner = planner
        self.executor = executor
        self.replanner = replanner
        self.evaluator = evaluator
        self.decision = decision
        self.max_steps = max_steps

    def _tool_key(self, name, args):
        return (name, json.dumps(args or {}, sort_keys=True))

    def run(self, goal):
        state = AgentState(goal)
        state.steps = self.planner.create_plan_dynamic(goal).steps

        steps_done = 0
        tool_attempts = 0
        while state.steps and steps_done < self.max_steps:
            steps_done += 1
            step = state.steps[0]
            state.current_step = step

            # Act
            observation = self.executor.execute_step(step)
            state.observation = observation
            state.observations.append(observation)

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

                # 相同工具+参数结果缓存，命中则不重复执行
                key = self._tool_key(decision.tool, decision.args)
                if key in state.tool_results:
                    tool_result = state.tool_results[key]
                else:
                    tool_result = self.executor.execute_tool(
                        decision.tool, decision.args
                    )
                    state.tool_results[key] = tool_result

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
                break

        if not state.completed:
            return f"目标未完成：{goal}"

        return f"完成 {len(state.completed)} 步：\n" + "\n".join(state.completed)
