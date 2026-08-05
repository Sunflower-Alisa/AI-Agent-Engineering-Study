from .models import Execution
from .tools.registry import TOOLS


class Executor:
    def __init__(self, chat):
        self.chat = chat

    def execute_llm(self, prompt):
        result = self.chat(prompt)
        return Execution(result=result, issues="")

    # 暂时只是个空的，什么都没做
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
            return Execution(
                result="", issues=f"错误：未知工具 {name}，可用工具：{list(TOOLS)}"
            )
        try:
            if args:
                result = tool.run(**args)
            else:
                result = tool.run()
            return Execution(result=f"[{name}] {result}", issues="")
        except TypeError as e:
            return Execution(
                result="",
                issues=f"错误：工具 {name} 调用失败，参数应匹配：{tool.description.strip()}：{e}",
            )
