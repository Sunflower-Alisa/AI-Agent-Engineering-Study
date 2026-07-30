def evaluate(state,observation):
    if observation["issues"]:
        return{
            "need_replan":True,
            "reason":observation["issues"]
        }

    return {
        "need_replan":False
    }