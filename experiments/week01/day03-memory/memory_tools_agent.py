import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
_VENV = os.path.join(
    os.path.dirname(__file__), "../day01-agent-loop/.venv/Lib/site-packages"
)
sys.path.insert(0, _VENV)
os.environ["PATH"] = (
    os.path.join(os.path.dirname(__file__), "../day01-agent-loop/.venv/Scripts")
    + ";"
    + os.environ.get("PATH", "")
)

from openai import OpenAI
from config import api_key, MODEL, cfg
from memory import Memory

memory = Memory()

# ========== Memory 工具函数 ==========


def memory_save(key: str, value: str, info_type: str = "general"):
    memory.save(key, value, {"type": info_type})
    return f"已保存：{key}"


def memory_update(key: str, value: str, info_type: str = "general"):
    old = memory.retrieve(key)
    if old is None:
        memory.save(key, value, {"type": info_type})
        return f"未找到 {key}，已作为新记忆保存"
    else:
        memory.update(key, value, {"type": info_type})
        return f"已更新：{key}（原：{old} → 新：{value}）"


def memory_delete(key: str):
    old = memory.retrieve(key)
    if old is None:
        return f"未找到 {key}，无需删除"
    memory.delete(key)
    return f"已删除：{key}"


def memory_search(query: str):
    results = memory.search(query, n_results=3)
    if not results:
        return "未找到相关记忆"
    return "\n".join(f"- {r}" for r in results)


# ========== Tool 定义 ==========

tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "memory_save",
            "description": "保存一条新记忆。当用户首次提供个人信息、偏好、事实时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "记忆的键名，如 user_name、user_city",
                    },
                    "value": {"type": "string", "description": "记忆的内容"},
                    "info_type": {
                        "type": "string",
                        "description": "信息类型：profile/preference/fact",
                    },
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "memory_update",
            "description": "更新已有记忆。当用户修改或更正之前提供的信息时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "要更新的记忆键名"},
                    "value": {"type": "string", "description": "新的记忆内容"},
                    "info_type": {"type": "string", "description": "信息类型"},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "memory_delete",
            "description": "删除记忆。当用户要求忘记或删除某条信息时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "要删除的记忆键名"}
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "memory_search",
            "description": "搜索记忆。回答用户问题前，先搜索相关记忆来提供上下文",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词或问题"}
                },
                "required": ["query"],
            },
        },
    },
]

tool_functions = {
    "memory_save": memory_save,
    "memory_update": memory_update,
    "memory_delete": memory_delete,
    "memory_search": memory_search,
}


class MemoryAgent:
    def __init__(self, max_steps=10):
        self.client = OpenAI(base_url=cfg["base_url"], api_key=api_key)
        self.tools = tool_definitions
        self.functions = tool_functions
        self.messages = [
            {
                "role": "system",
                "content": (
                    "你是拥有记忆能力的 AI 助手。"
                    "当用户提供个人信息、偏好或事实时，调用 memory_save 记住它。"
                    "当用户修改之前的信息时，调用 memory_update。"
                    "当用户要求忘记时，调用 memory_delete。"
                    "回答用户问题前，先调用 memory_search 搜索相关记忆。"
                ),
            }
        ]
        self.max_steps = max_steps

    def observe(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})

    def think(self):
        return self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            tools=self.tools,
        )

    def act(self, tool_call):
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        func = self.functions[func_name]
        result = func(**func_args)
        return {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)}

    def run(self, user_query: str):
        self.observe(user_query)

        for _ in range(self.max_steps):
            response = self.think()
            message = response.choices[0].message
            self.messages.append(message)

            if not message.tool_calls:
                return message.content

            for tool_call in message.tool_calls:
                self.messages.append(self.act(tool_call))

        return "达到最大执行轮次，任务停止"


if __name__ == "__main__":
    agent = MemoryAgent()

    print("==== Memory Tool Agent Demo ====")
    print("输入 exit 退出\n")

    while True:
        query = input("User: ")
        if query.lower() in ("exit", "quit"):
            break
        answer = agent.run(query)
        print(f"Agent: {answer}")

    print(f"\n当前记忆总数: {memory.count()}")
    print("最终记忆内容:")
    for key in ["user_name", "user_city", "user_hobby"]:
        val = memory.retrieve(key)
        if val:
            print(f"  {key} = {val}")
