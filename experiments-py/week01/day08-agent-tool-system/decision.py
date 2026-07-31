from llm import chat, parse_json
from models import Decision as DecisionModel
from tools.registry import TOOLS


class Decision:
    def decide(self, state):
        tools_desc = "\n".join(
            f"- {name}: {tool.description.strip()}" for name, tool in TOOLS.items()
        )
        cached = (
            "\n".join(
                f"- {name}({args}): {result}"
                for (name, args), result in state.tool_results.items()
            )
            or "（无）"
        )
        prompt = f"""
你是Agent决策模块，
当前状态：
目标：{state.goal}
当前步骤：{state.current_step}
观察结果：{state.observation}
评估结果：{state.evaluation}
已完成的计算结果：
{cached}

可用工具：
{tools_desc}

请选择下一步动作：
- continue：本步已完成，继续下一步
- tool：需要调用工具获取信息（必须同时给出 tool 名称和 args 参数）
- replan：当前计划需要调整
- finish：目标已达成，结束任务

规则：
- 如果观察结果或已完成的计算结果中已经包含所需答案，直接选择 continue 或 finish，禁止重复调用工具。
- 不要对同一个计算反复调用工具。

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
