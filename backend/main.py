from __future__ import annotations

import argparse
import json

from app.graph.graph import build_graph


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AutoResearch pipeline from the CLI.")
    parser.add_argument("query", help="Research question to investigate.")
    args = parser.parse_args()

    graph = build_graph()
    initial_state = {
        "query": args.query,
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
    result = graph.invoke(initial_state)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
