from ..llm import chat

# Day9 新增
class Improver:
    def improve_answer(self,question,answer,issues):
        prompt = f"""
    原问题：{question}
    原答案：{answer}
    存在问题：{issues}

    请重新生成优化后的答案

    要求：解决上述问题
    """

        return chat(prompt)