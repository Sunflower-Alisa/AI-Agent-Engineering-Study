from llm import chat
import json

def replan_static(state,reason):
    print("重新规划原因：",reason)

    state.steps = [
        "学习LangGraph",
        "学习Tool Calling",
        "实现Agent项目"
    ]

    state.failed.append(reason)

def replan_dynamic(state,observation):
    prompt = f"""你是一个重新规划Agent,
    当前目标：{state.goal},
    已经完成：{state.completed},
    当前计划：{state.steps},
    请重新指定下一步计划。
    返回JSON:
    {{
    "steps":[]
    }}
    """
    result = chat(prompt)
    return json.loads(result)