"""Controlled multi-scale benchmark on induced snapshots for Neo4j and SQLite."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

from experiments.benchmarks.benchmark_neo4j import benchmark as benchmark_neo4j
from experiments.benchmarks.benchmark_relational import benchmark as benchmark_sqlite, build_database
from experiments.benchmarks.snapshot_subset import build_induced_snapshot
from src.config import get_settings
from src.kg.load_neo4j import load
from src.kg.repository import Neo4jRepository


COMPARABLE_INTENTS = {"movies_by_director", "common_movies", "movies_by_genre_rating", "directors_by_genre"}


def _safe_test_target(uri: str) -> bool:
    parsed = urlparse(uri)
    return parsed.hostname in {"localhost", "127.0.0.1"} and parsed.port == 7688


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def run(processed: Path, questions: Path, sizes: list[int], iterations: int,
        output: Path, metadata_path: Path) -> dict:
    settings = get_settings()
    if not _safe_test_target(settings.neo4j_uri) or os.getenv("ALLOW_MULTISCALE_BENCHMARK") != "1":
        raise RuntimeError("Refusing destructive scale benchmark: use local Neo4j test on port 7688 "
                           "and set ALLOW_MULTISCALE_BENCHMARK=1")
    all_cases = json.loads(questions.read_text(encoding="utf-8"))
    cases = []
    seen_intents = set()
    for case in all_cases:
        if case["intent"] in COMPARABLE_INTENTS and case["intent"] not in seen_intents:
            cases.append(case); seen_intents.add(case["intent"])
    all_rows = []
    snapshot_manifests = []
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="movie-kg-scales-") as tmp:
        for size in sizes:
            subset = Path(tmp) / str(size)
            manifest = build_induced_snapshot(processed, subset, size)
            snapshot_manifests.append(manifest)
            load(subset, run_reasoning=True, replace=True)
            repository = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user,
                                          settings.neo4j_password, settings.neo4j_database)
            try:
                neo_rows = benchmark_neo4j(repository, cases, iterations)
            finally:
                repository.close()
            sqlite = build_database(subset)
            try:
                sqlite_rows = benchmark_sqlite(sqlite, iterations)
            finally:
                sqlite.close()
            all_rows.extend(neo_rows)
            all_rows.extend(sqlite_rows)
    _write_csv(output, all_rows)
    source_hash = hashlib.sha256((processed / "manifest.json").read_bytes()).hexdigest()
    metadata = {
        "protocol": "same-machine induced-snapshot Neo4j/SQLite comparison",
        "generated_at_epoch": time.time(), "duration_seconds": time.time() - started,
        "python_version": platform.python_version(), "platform": platform.platform(),
        "processor": platform.processor() or "not reported", "source_manifest_sha256": source_hash,
        "sizes": sizes, "iterations_per_query": iterations, "warmup_runs_per_query": 1,
        "selection": "first-n-processed-source-order", "test_neo4j_uri": settings.neo4j_uri,
        "snapshots": snapshot_manifests,
        "interpretation_limit": "Latency trend on one machine and one workload; not a universal DBMS ranking.",
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--questions", type=Path, default=Path("tests/test_questions.json"))
    parser.add_argument("--sizes", default="500,1000,2000,4999")
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/results/benchmarks/multiscale_benchmark.csv"))
    parser.add_argument("--metadata", type=Path,
                        default=Path("experiments/results/benchmarks/multiscale_benchmark.metadata.json"))
    args = parser.parse_args()
    sizes = [int(value) for value in args.sizes.split(",") if value.strip()]
    result = run(args.processed_dir, args.questions, sizes, args.iterations,
                 args.output, args.metadata)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
