from models import Execution
from tools.registry import TOOLS


class Executor:
    def execute_step(self, step):
        print("执行：", step)

        if "LangChain" in step:
            return Execution(
                result="完成学习", issues="发现LangGraph更适合作为Agent框架"
            )

        return Execution(result="完成", issues="")

    def execute_tool(self, name, args):
        print("执行工具：", name)
        tool = TOOLS.get(name)
        if tool is None:
            return f"错误：未知工具 {name}，可用工具：{list(TOOLS)}"
        try:
            if args:
                return tool.run(**args)
            return tool.run()
        except TypeError as e:
            return f"错误：工具 {name} 调用失败，参数应匹配：{tool.description.strip()}：{e}"
