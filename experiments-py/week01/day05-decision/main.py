from state import AgentState
from planner import create_plan_static, create_plan_dynamic
from executor import excute_step
from replanner import replan_static, replan_dynamic
from evaluator import evaluate
from decision import decide

goal = "帮我制定学习AI Agent路线"

state = AgentState(goal)

# Static Planning  测试代码
# state.steps = create_plan_static(goal)
# Dynamic Planning 测试代码
state.steps = create_plan_dynamic(goal).steps

while state.steps:
    step = state.steps.pop(0)
    state.current_step = step
    # Act
    observation = excute_step(step)

    # 评价
    evaluation = evaluate(state, observation)

    state.observation = observation
    state.evaluation = evaluation

    # Think
    decision = decide(state)
    state.next_action = decision.action

    if decision.action == "continue":
        state.completed.append(step)
        continue

    if decision.action == "replan":
        new_plan = replan_dynamic(state, decision.reason)
        state.steps = new_plan.steps

    if decision.action == "finish":
        break


print("目标：")
print(state.goal)

print("\n计划：")
for step in state.steps:
    print(".", step)


print("计划完成：", state.completed)
print("计划失败：", state.failed)
