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

    def create_plan_dynamic(self, goal):
        prompt = f"""你是一个任务规划Agent，用户目标：{goal},请拆解成可执行步骤。
        要求返回JSON:
        {{
        "goal":"{goal}",
        "steps":[
        "步骤1",
        "步骤2",
        "步骤3"
        ]
        }}
        不要输出其他内容。
        """
        result = chat(prompt)
        data = parse_json(result)
        data.setdefault("goal", goal)
        plan = Plan(**data)
        return plan
