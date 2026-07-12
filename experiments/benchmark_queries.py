from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
from pathlib import Path

from src.qa.service import answer


def percentile(values, p):
    ordered = sorted(values); return ordered[min(round((len(ordered) - 1) * p), len(ordered) - 1)]


def benchmark(seed: Path, questions: Path, iterations: int, scales: list[int] | None = None) -> list[dict]:
    movies = json.loads(seed.read_text(encoding="utf-8"))["movies"]
    cases = json.loads(questions.read_text(encoding="utf-8")); results = []
    for scale in scales or [len(movies)]:
        # Repetition is an explicitly synthetic CPU-scaling benchmark. IDs are
        # shifted so lookup and recommendation still traverse distinct records.
        dataset = []
        for index in range(scale):
            item = dict(movies[index % len(movies)])
            item["tmdb_id"] = item["tmdb_id"] + 10_000_000 * (index // len(movies))
            dataset.append(item)
        for case in cases:
            timings = []
            for _ in range(iterations):
                start = time.perf_counter(); answer(case["question"], dataset); timings.append((time.perf_counter() - start) * 1000)
            results.append({"backend": "memory-synthetic", "movie_count": len(dataset), "intent": case["intent"],
                            "iterations": iterations, "median_ms": round(statistics.median(timings), 4),
                            "p95_ms": round(percentile(timings, .95), 4), "stdev_ms": round(statistics.pstdev(timings), 4)})
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--seed", type=Path, default=Path("data/samples/movies.json"))
    parser.add_argument("--questions", type=Path, default=Path("tests/test_questions.json")); parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--scales", default="5,100,1000,5000", help="comma-separated synthetic movie counts")
    parser.add_argument("--output", type=Path, default=Path("experiments/results/query_benchmark.csv")); args = parser.parse_args()
    rows = benchmark(args.seed, args.questions, args.iterations, [int(x) for x in args.scales.split(",")]); args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    print(f"Wrote {len(rows)} benchmark rows to {args.output}")
