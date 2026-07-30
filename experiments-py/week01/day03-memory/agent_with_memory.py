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


class AgentWithMemory:
    def __init__(self, tools, functions, max_steps):
        self.client = OpenAI(base_url=cfg["base_url"], api_key=api_key)
        self.tools = tools
        self.functions = functions
        self.messages = []
        self.max_steps = max_steps
        self.memory = Memory()

    def observe(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})

    def think(self):
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            tools=self.tools,
        )
        return response

    def act(self, tool_call):
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        func = self.functions[func_name]
        result = func(**func_args)
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result),
        }

    def run(self, user_query: str, user_id: str = "default"):
        past = self.memory.search(user_query, n_results=2)
        if past:
            context = "\n".join(past)
            self.messages.append(
                {
                    "role": "system",
                    "content": f"以下是该用户相关的历史记忆：\n{context}",
                }
            )

        self.observe(user_query)

        for _ in range(self.max_steps):
            response = self.think()
            message = response.choices[0].message
            self.messages.append(message)

            if not message.tool_calls:
                answer = message.content
                self.memory.save(
                    f"{user_id}:{user_query[:20]}",
                    f"Q: {user_query}\nA: {answer}",
                    {"user_id": user_id, "type": "qa"},
                )
                return answer

            for tool_call in message.tool_calls:
                tool_result = self.act(tool_call)
                self.messages.append(tool_result)

        return "达到最大执行轮次，任务停止"
