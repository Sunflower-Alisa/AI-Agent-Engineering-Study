from langgraph.graph import StateGraph,END
from .state import AgentState

from .nodes import (planner_node,executor_node,reflection_node,decision_node)
from .router import action_router,result_router,step_router

def create_graph():
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("planner",planner_node)
    graph.add_node("executor",executor_node)
    graph.add_node("reflection",reflection_node)
    graph.add_node("decision",decision_node)
    graph.add_node("step_check",lambda state:state)

    # 设置入口
    graph.set_entry_point("planner")

    # 边
    graph.add_edge("planner","decision")
    graph.add_conditional_edges(
        "decision",
        action_router,
        {
            "tool":"executor",
            "execute":"executor",
            "replan":"planner"
        }
    )
    graph.add_edge("executor","reflection")
    graph.add_conditional_edges(
        "reflection",
        result_router,
        {
            "finish":END,
            "retry":"planner"
        }
        # step_router,
        # {
        #     "continue":"executor",
        #     "finish":END
        # }
    )

    graph.add_conditional_edges(
        "step_check",
        step_router,
        {
            "continue":"decision",
            "finish":END
        }
    )

    return graph.compile()