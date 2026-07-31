import ast
import operator

from .base import Tool

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("不支持的表达式")


def _safe_eval(expression):
    return _eval_node(ast.parse(expression, mode="eval"))


class Calculator(Tool):
    name = "calculator"

    description = """
执行数学计算
输入expression
"""

    def run(self, expression):
        try:
            return _safe_eval(expression)
        except Exception as e:
            return f"错误：无法计算 {expression}：{e}"
