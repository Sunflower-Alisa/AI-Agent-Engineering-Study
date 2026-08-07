from agent.graph import create_graph
from agent.state import AgentState
import tool

app = create_graph()


result = app.invoke(
    AgentState(
        goal = "2+3",
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