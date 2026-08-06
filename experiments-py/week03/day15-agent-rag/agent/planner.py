from llm import chat, parse_json
from models import Plan


class Planner:
    def create_plan_static(self, goal):
        if "AI Agent" in goal:
            return [
                "理解Agent基础",
                "学习Agent Loop",
                "学习LangChain",
                "学习Tool Calling",
                "学习Memory",
                "实现RAG Agent",
            ]

        return ["分析目标", "制定步骤"]

    def complete_step(self, state, step):
        state.completed.append(step)
        state.steps.remove(step)

    def create_plan_dynamic(self, goal,context):
        # prompt = f"""你是一个任务规划Agent，用户目标：{goal},请拆解成可执行步骤。

        # 请根据历史记录生成下一步计划。
        # 要求:
        # 1. 不重复已经完成的步骤
        # 2. 优先执行未完成内容
        # 3. 如果历史为空，从头规划

        # 要求返回JSON:
        # {{
        # "goal":"{goal}",
        # "steps":[
        # "步骤1",
        # "步骤2",
        # "步骤3"
        # ]
        # }}
        # 不要输出其他内容。
        # """

        prompt = f"""
你是一个智能Agent任务规划器。

你的任务：
根据用户目标和当前上下文，生成可执行任务计划。


用户目标:
{goal}


当前上下文:

{context}


上下文包含:
- 用户历史对话
- Agent执行记录
- 用户长期记忆
- 知识库信息


规划要求:

1. 理解用户真实目标
2. 优先利用已有上下文信息
3. 不重复已经完成的任务
4. 如果已有知识足够，不重复检索
5. 如果缺少信息，规划获取信息的步骤
6. 将复杂任务拆解为多个可执行步骤


请返回JSON格式:

{{
    "goal":"{goal}",
    "steps":[
        "步骤1",
        "步骤2",
        "步骤3"
    ]
}}


不要输出JSON以外的内容。
"""
        result = chat(prompt)
        data = parse_json(result)
        print (f"动态计划内容：{data}")
        data.setdefault("goal", goal)
        plan = Plan(**data)
        return plan
