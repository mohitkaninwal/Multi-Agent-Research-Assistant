from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.state import ResearchState
from app.utils.llm import get_chat_model


def writer_node(state: ResearchState) -> ResearchState:
    llm = get_chat_model()
    references = state.get("references", [])
    contradictions = state.get("contradictions", [])
    summaries_text = "\n\n".join(
        [f"## {topic}\n{summary}" for topic, summary in state.get("summaries", {}).items()]
    )
    contradictions_text = "\n".join(
        [f"- {item}" for item in contradictions]
    ) or "- No critical contradictions detected."
    references_text = "\n".join([f"- {url}" for url in references])

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a research writer. Write a structured markdown report with "
                    "an introduction, section per sub-topic, a conclusion, and caveats. "
                    "Use only the supplied summaries and explicitly mention uncertainties."
                )
            ),
            HumanMessage(
                content=(
                    f"Research question: {state['query']}\n\n"
                    f"Sub-topic summaries:\n{summaries_text}\n\n"
                    f"Critic notes:\n{contradictions_text}\n\n"
                    f"References:\n{references_text}"
                )
            ),
        ]
    )

    report = response.content
    if references_text:
        report = f"{report}\n\n## References\n{references_text}"

    return {**state, "final_report": report, "current_step": "writer"}
