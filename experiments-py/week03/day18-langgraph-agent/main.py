from agent.graph import create_graph
from agent.state import AgentState

app = create_graph()

result = app.invoke(
    AgentState(
        goal = "学习AI Agent",
        steps = [],
        current_step = "",
        observation = "",
        answer = "",
        evaluation = {},
        action = "",
        retry_count = 1
    )
)

print (result)