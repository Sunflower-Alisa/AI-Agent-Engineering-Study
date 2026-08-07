from .base import Tool

class CalculatorTool(Tool):
    name = "calculator"

    description = """
    执行数学计算
    输入表达式，例如：
    1+1
"""

    def run(self,args):
        expression = args
        return eval(expression)