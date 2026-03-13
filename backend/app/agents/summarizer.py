from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.state import ResearchState
from app.models import SummaryOutput
from app.utils.formatting import format_search_results
from app.utils.llm import get_chat_model


def summarizer_node(state: ResearchState) -> ResearchState:
    llm = get_chat_model().with_structured_output(SummaryOutput)
    summaries: dict[str, str] = {}

    for topic, results in state.get("search_results", {}).items():
        if not results:
            summaries[topic] = "No external evidence was found for this sub-topic."
            continue
        formatted_results = format_search_results(results)
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a research summarizer. Produce a concise 2-3 sentence "
                        "summary grounded only in the provided evidence. Mention uncertainty "
                        "when sources are sparse or disagree."
                    )
                ),
                HumanMessage(
                    content=(
                        f"Sub-topic: {topic}\n\n"
                        f"Research question: {state['query']}\n\n"
                        f"Evidence:\n{formatted_results}"
                    )
                ),
            ]
        )
        summaries[topic] = response.summary

    return {**state, "summaries": summaries, "current_step": "summarizer"}
