from state import AgentState
import json
from memory.short_memory import ShortMemory
from memory.long_memory import LongMemory
from memory.extractor import MemoryExtractor


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
        context_manager,
        max_steps=30
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
        self.short_memory = ShortMemory()
        # Day17 新增
        self.long_memory = LongMemory()
        self.context_manager = (context_manager)
        self.history = []
        self.extractor = MemoryExtractor()

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
        state = AgentState(goal)
        # 1、查询长期Memory
        state.memory_context = (self.long_memory.retrieve(goal))
        # 2、查询知识库
        state.knowledge_context = []

        # 如果需要RAG
        # 后续有Decision触发

        # 3、构建Context
        context =(self.context_manager.build_context(goal,self.history,state.memory_context,state.knowledge_context))

        state.steps = self.planner.create_plan_dynamic(goal,context).steps
        steps_done = 0
        tool_attempts = 0
        while state.steps and steps_done < self.max_steps:
            steps_done += 1
            step = state.steps[0]
            state.current_step = step

            # Think
            decision = self.decision.decide_currentstep(state)

            if decision.action == "tool":
                observation = self._run_tool(state, decision.tool, decision.args)
            if decision.action == "replan":
                state.failed.append(step)
                state.failed.append(decision.reason)
                new_plan = self.replanner.replan_dynamic(state,context,decision.reason)
                state.steps = new_plan.steps
            if decision.action == "llm":
                observation = self.executor.execute_llm(state.current_step)

            if decision.tool == "knowledge_search":
                state.knowledge_context.extend(observation)
                state.observations.append(
                    {
                        "tool":"knowledge_search",
                        "query":decision.args,
                        "status":"success"
                    }
                )
            else:
                state.observation = observation
                state.observations.append(
                    {"step": step, "action": decision.action, "result": observation}
                )

            # 评价
            state.evaluation = self.evaluator.evaluate(state, observation)

            state.steps.pop(0)

        # 根据计划生成结果
        answer = self.generator.generate(state)

        # reflection 评价
        reflection = self.reflection.evaluate_answer(goal, answer)

        if reflection.score < self.reflection_threshold:
            answer = self.improver.improve_answer(goal, answer, reflection.issues)

        self.short_memory.save(
            {
                "goal": goal,
                "completed": state.completed,
                "failed": state.failed,
                "observations": state.observations,  # 暂时全存，未做压缩筛选
                "reflection": reflection,
                "final_answer": answer,
            }
        )

        self.history.append({"role":"user","content":goal})

        # Day17 新增长期记忆保存
        memories = self.extractor.extract(
            self.history
        )
        if not memories:
            for m in memories:
                self.long_memory.save(m)

        return answer
