from langgraph.graph import END, START, StateGraph

from app.agents.router import route_intent, route_to_tool
from app.agents.state import AgentState
from app.agents.tools import (
    edit_interaction_tool,
    follow_up_plan_tool,
    log_interaction_tool,
    search_history_tool,
    summarize_interaction_tool,
)

TOOL_NODES = {
    "log_interaction": log_interaction_tool,
    "edit_interaction": edit_interaction_tool,
    "search_history": search_history_tool,
    "follow_up_plan": follow_up_plan_tool,
    "summarize_interaction": summarize_interaction_tool,
}


TOOL_NODE_NAMES = {
    "log_interaction": "log_interaction",
    "edit_interaction": "edit_interaction",
    "search_history": "search_history",
    "follow_up_plan": "follow_up_plan",
    "summarize_interaction": "summarize_interaction",
}


def build_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("router", route_intent)
    for name, handler in TOOL_NODES.items():
        workflow.add_node(name, handler)

    workflow.add_edge(START, "router")
    workflow.add_conditional_edges("router", route_to_tool, TOOL_NODE_NAMES)

    for name in TOOL_NODES:
        workflow.add_edge(name, END)

    return workflow.compile()


agent_graph = build_agent_graph()
