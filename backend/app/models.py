from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    title: str
    url: str
    content: str = ""
    score: Optional[float] = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ResearchRequest(BaseModel):
    query: str = Field(min_length=5, description="Research question to investigate.")


class ResearchResponse(BaseModel):
    query: str
    sub_topics: list[str]
    summaries: dict[str, str]
    contradictions: list[str]
    final_report: str
    references: list[str]


class GraphStepEvent(BaseModel):
    event: str
    node: str
    current_step: str
    payload: dict[str, Any] = Field(default_factory=dict)


class PlannerOutput(BaseModel):
    sub_topics: list[str] = Field(
        min_length=3,
        max_length=5,
        description="Focused sub-topics needed to answer the research question.",
    )


class SummaryOutput(BaseModel):
    summary: str = Field(description="A concise evidence-based summary for a sub-topic.")


class CriticOutput(BaseModel):
    contradictions: list[str] = Field(
        default_factory=list,
        description="Potential contradictions, weak claims, or evidence gaps.",
    )
