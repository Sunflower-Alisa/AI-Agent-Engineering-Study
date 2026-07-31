from state import AgentState


class Agent:
    def __init__(self, planner, executor, replanner, evaluator, decision, max_steps=30):
        self.planner = planner
        self.executor = executor
        self.replanner = replanner
        self.evaluator = evaluator
        self.decision = decision
        self.max_steps = max_steps

    def run(self, goal):
        state = AgentState(goal)
        state.steps = self.planner.create_plan_dynamic(goal).steps

        steps_done = 0
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

            # 工具动作：执行后把结果回填，重新决策，不推进步骤
            if decision.action == "tool":
                tool_result = self.executor.execute_tool(decision.tool, decision.args)
                state.observation = tool_result
                state.observations.append(tool_result)
                continue

            # 以下动作表示本步已结束，弹出该步骤
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
