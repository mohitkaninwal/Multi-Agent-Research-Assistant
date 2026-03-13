from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_settings
from app.graph.state import ResearchState
from app.models import PlannerOutput
from app.utils.llm import get_chat_model


def planner_node(state: ResearchState) -> ResearchState:
    settings = get_settings()
    llm = get_chat_model().with_structured_output(PlannerOutput)
    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a research planner. Break the user's question into focused "
                    "sub-topics that together answer the question comprehensively. "
                    f"Return between 3 and {settings.max_subtopics} sub-topics."
                )
            ),
            HumanMessage(content=state["query"]),
        ]
    )
    return {
        **state,
        "sub_topics": response.sub_topics[: settings.max_subtopics],
        "current_step": "planner",
    }
