import re

from models import ActionModel

_EXPR_RE = re.compile(r"\d+(?:\s*[+\-*/×]\s*\d+)+")


class ActionRouter:
    def route(self, step):
        if "搜索" in step or "收集资料" in step:
            return ActionModel(type="tool", tool="search", args={"query": step})

        if "计算" in step:
            expr = _extract_expression(step)
            if expr:
                return ActionModel(
                    type="tool", tool="calculator", args={"expression": expr}
                )

        return ActionModel(type="llm", prompt=step)


def _extract_expression(step):
    match = _EXPR_RE.search(step)
    if not match:
        return None
    return match.group().replace("×", "*").replace(" ", "")
