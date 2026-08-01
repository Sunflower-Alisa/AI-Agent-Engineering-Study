from models import ActionModel

class ActionRouter:
    def route(self,step):
        if "搜索" in step or "收集资料" in step:
            return ActionModel(
                type="tool",
                tool="search",
                args={
                    "query":step
                }
            )
        
        if "计算" in step:
            return  ActionModel(
                type="tool",
                tool="calculator",
                args={
                    "expression":step
                }
            )

        return ActionModel(
            type="llm",
            prompt=step
        )