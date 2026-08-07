from tool.registry import get_all_tools

def create_planner_prompt(state):
    prompt = f"""
    你是一个任务规划Agent。

    用户目标：
    {state.goal}

    请拆解成3-5个可执行步骤。

    只返回JSON：
    {{
    "steps":[
    "步骤1",
    "步骤2"
    ]
    }}

    """
    return prompt


def create_decision_prompt(state):
    tools=get_all_tools()
    tool_prompt= "\n".join(
        f"""
        {name}:
        {tool.description}
        """

        for name,tool in tools.items()
    )
    prompt=f"""你是Agent决策模块。
        目标：
        {state.goal}

        当前步骤：
        {state.current_step}

        已有观察：
        {state.observation}

        可用工具：
        {tool_prompt}

        请选择：
        tool:需要工具
        execute:直接回答
        replan:无法完成

        返回JSON
        {{
            "action":"tool/execute/replan",
            "reason":"",
            "tool":"",
            "args":{{}}
        }}

        """
    return prompt


def create_reflection_prompt(state):
    prompt=f"""你是Agent评估模块。

        目标：
        {state.goal}

        当前步骤：
        {state.current_step}

        执行结果：
        {state.observation}

        判断：
        是否完成？

        返回：
        {{
            "success":true,
            "reason":""
        }}

        """
    return prompt


def create_router_prompt(state):
    tools=get_all_tools()
    tool_prompt= "\n".join(
        f"""
        {name}:
        {tool.description}
        """

        for name,tool in tools.items()
    )
    prompt = f"""你是Agent任务路由模块。
        请判断用户任务应该如何处理。
        任务：
        {state.goal}

        可用工具：
        {tool_prompt}
                
        可选路线：
        1. tool
        适合：
        - 简单计算
        - 信息查询
        - 明确调用某个工具即可完成的问题

        2. planner
        适合：
        - 多步骤任务
        - 需要分析、规划、执行的问题
        - 复杂目标

        返回JSON：
        {{
            "route":"tool 或 planner",
            "reason":"原因",
            "tool":"工具名称，没有则为空",
            "args":""
        }}

"""
    return prompt