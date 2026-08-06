def action_router(state):
    action = state.action

    if action == "tool":
        return "tool"

    if action == "execute":
        return "execute"

    if action == "replan":
        return "replan"

    return "execute"


def result_router(state):
    evaluation = state.evaluation

    if evaluation["success"]:
        return "finish"

    else:
        return "retry"


def step_router(state):
    steps = state.steps

    if len(steps)>0:
        return "continue"

    return "finish"