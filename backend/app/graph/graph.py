from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.critic import critic_node
from app.agents.planner import planner_node
from app.agents.searcher import searcher_node
from app.agents.summarizer import summarizer_node
from app.agents.writer import writer_node
from app.config import get_settings
from app.graph.state import ResearchState


def route_after_critic(state: ResearchState) -> str:
    settings = get_settings()
    if state.get("contradictions") and state.get("critique_round", 0) <= settings.critic_loop_limit:
        return "searcher"
    return "writer"


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("planner", planner_node)
    graph.add_node("searcher", searcher_node)
    graph.add_node("summarizer", summarizer_node)
    graph.add_node("critic", critic_node)
    graph.add_node("writer", writer_node)
    graph.set_entry_point("planner")
    graph.add_edge("planner", "searcher")
    graph.add_edge("searcher", "summarizer")
    graph.add_edge("summarizer", "critic")
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "searcher": "searcher",
            "writer": "writer",
        },
    )
    graph.add_edge("writer", END)
    return graph.compile()
