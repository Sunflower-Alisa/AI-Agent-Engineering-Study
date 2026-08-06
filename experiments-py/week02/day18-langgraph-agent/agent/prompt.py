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
    prompt=f"""你是Agent决策模块。
        目标：
        {state.goal}

        当前步骤：
        {state.current_step}

        已有观察：
        {state.observation}

        请选择：
        tool:需要工具
        execute:直接回答
        replan:无法完成

        返回JSON
        {{
            "action":"tool/execute/replan",
            "content":""
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