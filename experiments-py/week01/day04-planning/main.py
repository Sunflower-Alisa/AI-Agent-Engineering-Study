from state import AgentState
from planner import create_plan_static, create_plan_dynamic
from executor import excute_step
from replanner import replan_static, replan_dynamic
from evaluator import evaluate

goal = "帮我制定学习AI Agent路线"

state = AgentState(goal)

# Static Planning  测试代码
# state.steps = create_plan_static(goal)
# Dynamic Planning 测试代码
state.steps = create_plan_dynamic(goal)["steps"]

while state.steps:
    step = state.steps.pop(0)
    state.current_step = step
    # Act
    observation = excute_step(step)

    # Observe + Think
    decision = evaluate(state,observation)

    if decision["need_replan"]:
        # Static Planning  测试代码
        # replan_static(state,result["reason"])
        # Dynamic Planning 测试代码
        new_plan = replan_dynamic(state, decision["reason"])
        state.steps = new_plan["steps"]

    else:
        state.completed.append(step)
       

print("目标：")
print(state.goal)

print("\n计划：")
for step in state.steps:
    print(".", step)


print("计划完成：", state.completed)
print("计划失败：", state.failed)
