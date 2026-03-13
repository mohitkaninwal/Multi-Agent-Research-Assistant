from __future__ import annotations

import time
from typing import Optional

from tavily import TavilyClient

from app.config import get_settings


class TavilySearchTool:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.tavily_api_key:
            raise RuntimeError("TAVILY_API_KEY is required to run search.")
        self._client = TavilyClient(api_key=settings.tavily_api_key)
        self._delay_seconds = settings.search_delay_seconds

    def search(self, query: str, max_results: Optional[int] = None) -> list[dict]:
        settings = get_settings()
        response = self._client.search(
            query=query,
            max_results=max_results or settings.search_max_results,
            search_depth="advanced",
        )
        time.sleep(self._delay_seconds)
        return response.get("results", [])
