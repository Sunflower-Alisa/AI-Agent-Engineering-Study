from llm import chat,parse_json
from models import ReflectionResult

# Day9 新增
class Reflection_Evaluator:
    def evaluate_answer(self,question,answer):
        prompt = f"""
    你是一个答案质量评估专家。
    问题：{question}
    答案：{answer}

    请评价：

    返回JSON：
    {{
    "score":0-10,
    "issues":[
    ]
    }}

    不要输出解释。
    """
        result = chat(prompt)

        data = parse_json(result)

        reflectionResult = ReflectionResult(**data)

        return reflectionResult