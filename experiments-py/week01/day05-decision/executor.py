from models import Execution
def excute_step(step):
    print("执行：",step)

    if "LangChain" in step:
        return Execution( result = "完成学习", issues = "发现LangGraph更适合作为Agent框架" )

    return Execution( result = "完成", issues = "" )