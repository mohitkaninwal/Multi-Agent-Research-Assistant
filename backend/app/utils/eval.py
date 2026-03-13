from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from app.service import run_research
from app.utils.llm import get_chat_model


@dataclass(frozen=True)
class EvalCase:
    query: str
    expected_facts: list[str]


EVAL_CASES = [
    EvalCase(
        query="What is quantum computing?",
        expected_facts=["qubits", "superposition", "error correction"],
    ),
    EvalCase(
        query="What are the benefits and risks of autonomous vehicles?",
        expected_facts=["safety", "regulation", "sensor"],
    ),
    EvalCase(
        query="How do small language models differ from large language models?",
        expected_facts=["latency", "cost", "performance"],
    ),
]


def single_agent_answer(query: str) -> str:
    llm = get_chat_model()
    response = llm.invoke(
        f"Write a concise research brief answering this question:\n\n{query}"
    )
    return response.content


def score_report(report: str, expected_facts: list[str]) -> float:
    lowered = report.lower()
    matches = sum(1 for fact in expected_facts if fact.lower() in lowered)
    return matches / len(expected_facts)


def run_eval(output_path: str = "eval_results.csv") -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["query", "mode", "score", "expected_facts"],
        )
        writer.writeheader()
        for case in EVAL_CASES:
            multi_agent = run_research(case.query)
            writer.writerow(
                {
                    "query": case.query,
                    "mode": "multi_agent",
                    "score": score_report(multi_agent.final_report, case.expected_facts),
                    "expected_facts": ", ".join(case.expected_facts),
                }
            )
            baseline = single_agent_answer(case.query)
            writer.writerow(
                {
                    "query": case.query,
                    "mode": "single_agent",
                    "score": score_report(baseline, case.expected_facts),
                    "expected_facts": ", ".join(case.expected_facts),
                }
            )
    return destination


if __name__ == "__main__":
    result_file = run_eval("artifacts/eval_results.csv")
    print(f"Wrote evaluation results to {result_file}")
