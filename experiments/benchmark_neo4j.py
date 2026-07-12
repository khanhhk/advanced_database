"""Measure end-to-end QA latency against the real Neo4j graph."""
from __future__ import annotations

import argparse
import csv
import json
import platform
import statistics
import time
from pathlib import Path

from src.config import get_settings
from src.kg.repository import Neo4jRepository


def percentile(values, p):
    ordered = sorted(values)
    return ordered[min(round((len(ordered) - 1) * p), len(ordered) - 1)]


def benchmark(repository, cases, iterations):
    movie_count = repository.stats()["nodes"].get("Movie", 0)
    rows = []
    for case in cases:
        repository.answer(case["question"])  # warm query plan and page cache
        timings = []
        for _ in range(iterations):
            start = time.perf_counter()
            repository.answer(case["question"])
            timings.append((time.perf_counter() - start) * 1000)
        rows.append({"backend": "neo4j", "movie_count": movie_count, "intent": case["intent"],
                     "iterations": iterations, "median_ms": round(statistics.median(timings), 4),
                     "p95_ms": round(percentile(timings, .95), 4),
                     "stdev_ms": round(statistics.pstdev(timings), 4)})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, default=Path("tests/test_questions.json"))
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("experiments/results/neo4j_benchmark.csv"))
    parser.add_argument("--metadata", type=Path, default=Path("experiments/results/neo4j_benchmark.metadata.json"))
    args = parser.parse_args()
    settings = get_settings()
    repo = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password, settings.neo4j_database)
    try:
        rows = benchmark(repo, json.loads(args.questions.read_text(encoding="utf-8")), args.iterations)
        version = repo.run("CALL dbms.components() YIELD versions RETURN versions[0] AS version")[0]["version"]
    finally:
        repo.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    args.metadata.write_text(json.dumps({"generated_at_epoch": time.time(), "neo4j_version": version,
        "python_version": platform.python_version(), "platform": platform.platform(),
        "processor": platform.processor() or "not reported", "iterations_per_query": args.iterations,
        "warmup_runs_per_query": 1, "question_count": len(rows), "movie_count": rows[0]["movie_count"]}, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
