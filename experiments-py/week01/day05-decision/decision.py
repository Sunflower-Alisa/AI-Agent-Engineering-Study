from llm import chat
from models import Decision
import json

def decide(state):
    prompt = f"""
你是Agent决策模块，
当前状态：
目标：{state.goal}
当前步骤：{state.current_step}
观察结果：{state.observation}

请选择下一步：
continue
tool
replan
finish

只返回JSON：
{
    {
        "action":"",
        "reason":""
    }
}
"""

    result = chat(prompt)
    data = json.loads(result)
    return Decision(**data)
