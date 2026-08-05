from llm import chat, parse_json
from models import Plan


class Replanner:
    def replan_static(self, state, reason):
        print("重新规划原因：", reason)

        state.steps = ["学习LangGraph", "学习Tool Calling", "实现Agent项目"]

        state.failed.append(reason)

    def replan_dynamic(self, state,context, observation):
        cached = (
            "\n".join(
                f"- {name}({args}): {result}"
                for (name, args), result in state.tool_results.items()
            )
            or "（无）"
        )
        prompt = f"""你是一个重新规划Agent,
        当前目标：{state.goal},
        已经完成：{state.completed},
        当前计划：{state.steps},

        当前执行结果:
        {observation}

        当前上下文:
        {context}

        判断:
        1. 是否需要调整计划
        2. 是否需要新增步骤
        3. 是否可以结束任务
        
        已完成的计算结果：
        {cached}
        请重新指定下一步计划。
        注意：只生成尚未完成的步骤，不要重复已经完成的计算或步骤。
        返回JSON:
        {{
        "goal":"{state.goal}",
        "steps":[]
        }}
        """
        result = chat(prompt)
        data = parse_json(result)
        # data.setdefault("goal", state.goal)
        return Plan(**data)
