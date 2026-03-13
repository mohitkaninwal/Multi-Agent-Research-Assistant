from __future__ import annotations

from typing import NotRequired, TypedDict


class ResearchState(TypedDict):
    query: str
    sub_topics: list[str]
    search_results: dict[str, list[dict]]
    summaries: dict[str, str]
    contradictions: list[str]
    final_report: str
    current_step: str
    references: list[str]
    critique_round: int
    errors: NotRequired[list[str]]
