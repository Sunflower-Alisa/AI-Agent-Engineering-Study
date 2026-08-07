from .prompt import create_planner_prompt,create_decision_prompt,create_reflection_prompt,create_router_prompt
from .llm import chat,parse_json
from tool.registry import get_tool
from .models import RouterDecision

# 任务路由
def router_node(state):
    print("执行任务路由")
    prompt = create_router_prompt(state)
    result = chat(prompt)

    decision = RouterDecision.model_validate_json(
        result
    )

    state.router = {
        "route":decision.route,
        "tool":decision.tool,
        "router_reason":decision.reason
    }

    if decision.route =="tool":
        state.action = decision.route
        state.tool = decision.tool
        state.args = decision.args

    return state
 
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

    if state.action == "tool":
        tool = get_tool(state.tool)
        if tool is None:
            raise Exception(f"Tool{state.tool} not found")
        else :
            result = tool.run(state.args)
            state.observation =f"{result}"
    else:
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
    if state.action == "tool":
        state.tool = data["tool"]
        state.args = data["args"]
    return state


# 反思
def reflection_node(state):
    print("Reflection")

    prompt =create_reflection_prompt(state)
    result = chat(prompt)
    data = parse_json(result)
    state.evaluation = data
    return state