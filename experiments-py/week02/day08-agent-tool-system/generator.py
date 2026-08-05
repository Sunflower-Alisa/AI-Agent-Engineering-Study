from .llm import chat

class AnswerGenerator:
    def generate(self,state):
        prompt = f"""
根据以下执行结果，完成用户任务：
目标：{state.goal}

信息：{state.observations}

请输出最终答案
"""
        return chat(prompt)