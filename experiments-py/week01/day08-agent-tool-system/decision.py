from llm import chat, parse_json
from models import Decision as DecisionModel
from tools.registry import TOOLS


class Decision:
    def decide(self, state):
        tools_desc = "\n".join(
            f"- {name}: {tool.description.strip()}" for name, tool in TOOLS.items()
        )
        prompt = f"""
你是Agent决策模块，
当前状态：
目标：{state.goal}
当前步骤：{state.current_step}
观察结果：{state.observation}
评估结果：{state.evaluation}

可用工具：
{tools_desc}

请选择下一步动作：
- continue：本步已完成，继续下一步
- tool：需要调用工具获取信息（必须同时给出 tool 名称和 args 参数）
- replan：当前计划需要调整
- finish：目标已达成，结束任务

只返回JSON：
{{
    "action": "continue 或 tool 或 replan 或 finish",
    "reason": "选择该动作的原因",
    "tool": "工具名（action=tool 时必填）",
    "args": {{"参数名": "参数值"}}（action=tool 时必填）
}}
"""

        result = chat(prompt)
        data = parse_json(result)
        return DecisionModel(**data)
