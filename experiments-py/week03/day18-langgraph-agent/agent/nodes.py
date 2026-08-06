from .prompt import create_planner_prompt,create_decision_prompt,create_reflection_prompt
from .llm import chat,parse_json

# 计划
def planner_node(state):
    print("执行Planner")

    prompt = create_planner_prompt(state)
    result = chat(prompt)
    data = parse_json(result)

    state.steps = data["steps"]

    state.current_step = (
        state.steps[0]
    )
    return state

# 执行
def executor_node(state):
    print(
        "执行:",
        state.current_step
    )
    step = state.current_step

    # 模拟失败
    if state.retry_count < 1:
        state.observation = ""
    else :
        state.observation = (f"{step}执行成功")
    return state


# 决策
def decision_node(state):
    prompt = create_decision_prompt(state)
    result = chat(prompt)
    data = parse_json(result)
    state.action = data["action"]

    return state


# 反思
def reflection_node(state):
    print("Reflection")

    prompt =create_reflection_prompt(state)
    result = chat(prompt)
    data = parse_json(result)
    state.evaluation = data

    # state["answer"] = (
    #     "学习计划完成"
    # )

    return state