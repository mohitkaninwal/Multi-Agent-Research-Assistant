from __future__ import annotations

import json
from collections.abc import Generator
from typing import Any, Optional

from app.graph.graph import build_graph
from app.graph.state import ResearchState
from app.models import GraphStepEvent, ResearchResponse


def build_initial_state(query: str) -> ResearchState:
    return {
        "query": query,
        "sub_topics": [],
        "search_results": {},
        "summaries": {},
        "contradictions": [],
        "final_report": "",
        "current_step": "starting",
        "references": [],
        "critique_round": 0,
        "errors": [],
    }


def _graph() -> Any:
    return build_graph()


def run_research(query: str) -> ResearchResponse:
    result = _graph().invoke(build_initial_state(query), config=_graph_config())
    return ResearchResponse(
        query=result["query"],
        sub_topics=result.get("sub_topics", []),
        summaries=result.get("summaries", {}),
        contradictions=result.get("contradictions", []),
        final_report=result.get("final_report", ""),
        references=result.get("references", []),
    )


def stream_research(query: str) -> Generator[str, None, None]:
    try:
        graph = _graph()
        initial_state = build_initial_state(query)
        final_state: Optional[ResearchState] = None
        for payload in graph.stream(initial_state, config=_graph_config(), stream_mode="values"):
            final_state = payload
            current_step = payload.get("current_step", "")
            if current_step in {"", "starting"}:
                continue
            model = GraphStepEvent(
                event="node_complete",
                node=current_step,
                current_step=current_step,
                payload=payload,
            )
            yield f"data: {model.model_dump_json()}\n\n"

        if final_state is None:
            final_state = initial_state
        completed_event = GraphStepEvent(
            event="completed",
            node="writer",
            current_step=final_state.get("current_step", "writer"),
            payload={
                "final_report": final_state.get("final_report", ""),
                "sub_topics": final_state.get("sub_topics", []),
                "summaries": final_state.get("summaries", {}),
                "contradictions": final_state.get("contradictions", []),
                "references": final_state.get("references", []),
            },
        )
        yield f"data: {json.dumps(completed_event.model_dump())}\n\n"
    except Exception as exc:
        error_event = GraphStepEvent(
            event="error",
            node="system",
            current_step="error",
            payload={"message": str(exc)},
        )
        yield f"data: {json.dumps(error_event.model_dump())}\n\n"


def _graph_config() -> dict[str, Any]:
    from app.utils.observability import get_langfuse_handler

    handler = get_langfuse_handler()
    if not handler:
        return {}
    return {"callbacks": [handler]}
