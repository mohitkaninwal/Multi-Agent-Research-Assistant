from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.state import ResearchState
from app.models import CriticOutput
from app.utils.llm import get_chat_model


def critic_node(state: ResearchState) -> ResearchState:
    llm = get_chat_model().with_structured_output(CriticOutput)
    compiled_summaries = "\n\n".join(
        [f"Sub-topic: {topic}\nSummary: {summary}" for topic, summary in state.get("summaries", {}).items()]
    )
    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a research critic. Identify factual contradictions, unsupported "
                    "claims, or major evidence gaps. Return an empty list if the summaries are "
                    "coherent and adequately supported."
                )
            ),
            HumanMessage(
                content=(
                    f"Research question: {state['query']}\n\n"
                    f"Summaries to review:\n{compiled_summaries}"
                )
            ),
        ]
    )
    return {
        **state,
        "contradictions": response.contradictions,
        "critique_round": state.get("critique_round", 0) + 1,
        "current_step": "critic",
    }
