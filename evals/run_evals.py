"""Run the eval set and write a results table.

Usage:
    uv run python evals/run_evals.py                 # offline mode, used in CI
    LLM_PROVIDER=anthropic uv run python evals/run_evals.py

Metrics:
    retrieval_hit_rate   share of questions where the expected source is in the top-k results
    answer_match_rate    share of answers containing every required phrase (case-insensitive)
    p50 / p95 latency    per-question pipeline latency

For real projects, add an LLM-as-judge faithfulness check and a human-labelled sample.
Exits with code 1 if a metric falls below its threshold, so CI catches regressions.
"""

import argparse
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

from app.config import settings
from app.pipeline import Pipeline

HERE = Path(__file__).parent
THRESHOLDS = {"retrieval_hit_rate": 0.8, "answer_match_rate": 0.7}


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, round(pct / 100 * (len(ordered) - 1)))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=HERE / "dataset.jsonl")
    parser.add_argument("--out", type=Path, default=HERE / "results")
    args = parser.parse_args()

    cases = [json.loads(line) for line in args.dataset.read_text().splitlines() if line.strip()]
    pipeline = Pipeline.from_settings(settings)

    rows = []
    for case in cases:
        result = pipeline.ask(case["question"])
        hit = case["expected_source"] in result.sources
        match = all(p.lower() in result.answer.lower() for p in case["must_include"])
        rows.append(
            {
                "id": case["id"],
                "question": case["question"],
                "retrieval_hit": hit,
                "answer_match": match,
                "latency_ms": result.latency_ms,
                "sources": result.sources,
                "answer": result.answer,
            }
        )

    latencies = [r["latency_ms"] for r in rows]
    summary = {
        "run_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "provider": settings.llm_provider,
        "model": settings.llm_model if settings.llm_provider != "offline" else "offline",
        "cases": len(rows),
        "retrieval_hit_rate": round(sum(r["retrieval_hit"] for r in rows) / len(rows), 3),
        "answer_match_rate": round(sum(r["answer_match"] for r in rows) / len(rows), 3),
        "latency_p50_ms": round(statistics.median(latencies), 2),
        "latency_p95_ms": round(percentile(latencies, 95), 2),
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "results.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=2))

    lines = [
        f"# Eval results ({summary['run_at']})",
        "",
        f"Provider: {summary['provider']} | Model: {summary['model']} | Cases: {summary['cases']}",
        "",
        "| Metric | Value | Threshold |",
        "| --- | --- | --- |",
        f"| Retrieval hit rate | {summary['retrieval_hit_rate']:.0%} "
        f"| {THRESHOLDS['retrieval_hit_rate']:.0%} |",
        f"| Answer match rate | {summary['answer_match_rate']:.0%} "
        f"| {THRESHOLDS['answer_match_rate']:.0%} |",
        f"| Latency p50 / p95 | {summary['latency_p50_ms']} / {summary['latency_p95_ms']} ms | - |",
        "",
        "## Failures",
        "",
    ]
    failures = [r for r in rows if not (r["retrieval_hit"] and r["answer_match"])]
    lines += [f"- `{r['id']}` {r['question']} -> sources {r['sources']}" for r in failures] or [
        "None."
    ]
    (args.out / "results.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    failed = [k for k, t in THRESHOLDS.items() if summary[k] < t]
    if failed:
        print(f"\nBelow threshold: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
