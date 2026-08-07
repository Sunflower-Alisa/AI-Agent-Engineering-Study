from langgraph.graph import StateGraph,END
from .state import AgentState

from .nodes import (planner_node,executor_node,reflection_node,decision_node,router_node)
from .router import action_router,result_router,step_router

def router_selector(state):
    if  state.router is not None:
        return  state.router["route"]
    else:
        return "planner"

def create_graph():
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("router",router_node)
    graph.add_node("planner",planner_node)
    graph.add_node("executor",executor_node)
    graph.add_node("reflection",reflection_node)
    graph.add_node("decision",decision_node)
    graph.add_node("step_check",lambda state:state)

    # 设置入口
    graph.set_entry_point("router")

    # 边
    graph.add_conditional_edges(
        "router",
        router_selector,
        {
            "tool":"executor",
            "planner":"planner"
        }
    )
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