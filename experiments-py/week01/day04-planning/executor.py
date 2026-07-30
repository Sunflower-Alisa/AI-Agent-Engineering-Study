def excute_step(step):
    print("执行：",step)

    if "LangChain" in step:
        return {
            "result":"完成学习",
            "issues":"发现LangGraph更适合作为Agent框架"
        }

    return {
        "issues":[],
        "result":"完成"
    }