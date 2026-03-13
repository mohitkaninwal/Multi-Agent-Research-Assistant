from __future__ import annotations

from collections import OrderedDict


def dedupe_preserve_order(items: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(item for item in items if item))


def format_search_results(results: list[dict]) -> str:
    formatted_chunks: list[str] = []
    for idx, result in enumerate(results, start=1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        content = result.get("content", "")
        formatted_chunks.append(
            f"[{idx}] Title: {title}\nURL: {url}\nSnippet: {content}"
        )
    return "\n\n".join(formatted_chunks)
