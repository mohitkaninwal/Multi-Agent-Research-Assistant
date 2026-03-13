from __future__ import annotations

from app.graph.state import ResearchState
from app.tools.tavily_search import TavilySearchTool
from app.utils.formatting import dedupe_preserve_order


def searcher_node(state: ResearchState) -> ResearchState:
    tool = TavilySearchTool()
    search_results: dict[str, list[dict]] = {}
    references: list[str] = list(state.get("references", []))
    errors: list[str] = list(state.get("errors", []))

    for topic in state.get("sub_topics", []):
        try:
            results = tool.search(topic)
            search_results[topic] = results
            references.extend(
                [result.get("url", "") for result in results if result.get("url")]
            )
            if not results:
                errors.append(f"No results returned for sub-topic: {topic}")
        except Exception as exc:
            search_results[topic] = []
            errors.append(f"Search failed for '{topic}': {exc}")

    return {
        **state,
        "search_results": search_results,
        "references": dedupe_preserve_order(references),
        "errors": errors,
        "current_step": "searcher",
    }
