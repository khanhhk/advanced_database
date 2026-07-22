"""Build submission-ready tables and an SVG chart from committed result artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


RESULTS = Path("experiments/results")


def _load(relative_path: str) -> dict:
    return json.loads((RESULTS / relative_path).read_text(encoding="utf-8"))


def build(output_dir: Path = RESULTS / "summary") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    entity = _load("evaluation/entity_resolution.json")
    reasoning = _load("evaluation/reasoning.json")
    recommendation = _load("evaluation/recommendation.json")["result"]
    qa = _load("evaluation/qa_neo4j.json")
    semantic = _load("semantic/semantic_reasoning.json")
    validation = _load("quality/neo4j_validation.json")
    rows = [
        ("Entity resolution precision", entity["precision"], "silver", entity["cases"]),
        ("Entity resolution recall", entity["recall"], "silver", entity["cases"]),
        ("Entity resolution F1", entity["f1"], "silver", entity["cases"]),
        ("Co-star precision", reasoning["precision"], "silver", reasoning["reviewed_facts"]),
        ("Recommendation P@10", recommendation["precision_at_k"], "silver/neo4j", recommendation["cases"]),
        ("Recommendation NDCG@10", recommendation["ndcg_at_k"], "silver/neo4j", recommendation["cases"]),
        ("QA smoke accuracy", qa["accuracy"], "smoke/neo4j", qa["cases"]),
        ("Semantic conformance", 1.0 if semantic["validation"]["conforms"] else 0.0,
         "semantic-validation", semantic["triples_before"]),
        ("Neo4j structural validity", 1.0 if validation["valid"] else 0.0,
         "graph-validation", validation["nodes"]),
    ]
    with (output_dir / "quality_metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n"); writer.writerow(["metric", "value", "evidence_class", "cases"]); writer.writerows(rows)
    markdown = ["| Metric | Value | Evidence | Cases |", "|---|---:|---|---:|"]
    markdown += [f"| {name} | {value:.3f} | {kind} | {cases} |" for name, value, kind, cases in rows]
    (output_dir / "quality_metrics.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")

    width, height, margin = 900, 420, 55
    bar_width = (width - margin * 2) / len(rows) * .62
    gap = (width - margin * 2) / len(rows)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<style>text{font-family:Arial,sans-serif;fill:#172033}.label{font-size:12px}.value{font-size:13px;font-weight:bold}</style>',
           f'<line x1="{margin}" y1="20" x2="{margin}" y2="350" stroke="#667085"/>',
           f'<line x1="{margin}" y1="350" x2="{width-margin}" y2="350" stroke="#667085"/>']
    for index, (name, value, _, _) in enumerate(rows):
        x = margin + index * gap + (gap - bar_width) / 2
        bar_height = value * 300
        y = 350 - bar_height
        short = name.replace("Entity resolution ", "ER ").replace("Recommendation ", "Rec. ")
        svg += [f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="#2563eb"/>',
                f'<text class="value" x="{x+bar_width/2:.1f}" y="{y-7:.1f}" text-anchor="middle">{value:.3f}</text>',
                f'<text class="label" x="{x+bar_width/2:.1f}" y="374" text-anchor="middle">{short}</text>']
    svg.append('</svg>')
    (output_dir / "quality_metrics.svg").write_text("\n".join(svg), encoding="utf-8")

    with (RESULTS / "benchmarks/neo4j_benchmark.csv").open(encoding="utf-8", newline="") as stream:
        neo4j = list(csv.DictReader(stream))
    with (RESULTS / "benchmarks/relational_benchmark.csv").open(encoding="utf-8", newline="") as stream:
        sqlite = list(csv.DictReader(stream))
    sqlite_by_intent = {row["intent"]: row for row in sqlite}
    comparisons = []
    for row in neo4j:
        if row["intent"] in sqlite_by_intent and row["intent"] not in {x["intent"] for x in comparisons}:
            baseline = sqlite_by_intent[row["intent"]]
            comparisons.append({"intent": row["intent"], "iterations": row["iterations"],
                                "neo4j_median_ms": float(row["median_ms"]),
                                "neo4j_p95_ms": float(row["p95_ms"]),
                                "sqlite_median_ms": float(baseline["median_ms"]),
                                "sqlite_p95_ms": float(baseline["p95_ms"])})
    with (output_dir / "benchmark_comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=comparisons[0], lineterminator="\n"); writer.writeheader(); writer.writerows(comparisons)
    lines = ["| Intent | Iterations | Neo4j median (ms) | Neo4j p95 (ms) | SQLite median (ms) | SQLite p95 (ms) |",
             "|---|---:|---:|---:|---:|---:|"]
    lines += [f"| {x['intent']} | {x['iterations']} | {x['neo4j_median_ms']:.3f} | {x['neo4j_p95_ms']:.3f} | {x['sqlite_median_ms']:.3f} | {x['sqlite_p95_ms']:.3f} |" for x in comparisons]
    lines += ["", "Controlled same-snapshot comparison; different execution models and no universal speed claim."]
    (output_dir / "benchmark_comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    chart_width, chart_height = 920, 430
    maximum = max(max(x["neo4j_p95_ms"], x["sqlite_p95_ms"]) for x in comparisons)
    chart = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="{chart_height}" viewBox="0 0 {chart_width} {chart_height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<style>text{font-family:Arial,sans-serif;fill:#172033}.axis{font-size:12px}.title{font-size:17px;font-weight:bold}</style>',
             '<text class="title" x="460" y="26" text-anchor="middle">Same-snapshot query latency (100 iterations)</text>',
             '<line x1="70" y1="365" x2="890" y2="365" stroke="#667085"/>']
    group = 800 / len(comparisons)
    for index, item in enumerate(comparisons):
        x = 85 + index * group; scale = 300 / maximum
        for offset, key, color in ((0, "neo4j_p95_ms", "#2563eb"), (38, "sqlite_p95_ms", "#f59e0b")):
            height_value = item[key] * scale; y = 365 - height_value
            chart.append(f'<rect x="{x+offset:.1f}" y="{y:.1f}" width="32" height="{height_value:.1f}" fill="{color}"/>')
            chart.append(f'<text class="axis" x="{x+offset+16:.1f}" y="{max(y-5,42):.1f}" text-anchor="middle">{item[key]:.2f}</text>')
        chart.append(f'<text class="axis" x="{x+35:.1f}" y="389" text-anchor="middle">{item["intent"]}</text>')
    chart += ['<rect x="690" y="40" width="14" height="14" fill="#2563eb"/><text class="axis" x="710" y="52">Neo4j p95</text>',
              '<rect x="790" y="40" width="14" height="14" fill="#f59e0b"/><text class="axis" x="810" y="52">SQLite p95</text>', '</svg>']
    (output_dir / "benchmark_comparison.svg").write_text("\n".join(chart), encoding="utf-8")

    multiscale_path = RESULTS / "benchmarks/multiscale_benchmark.csv"
    if multiscale_path.is_file():
        with multiscale_path.open(encoding="utf-8", newline="") as stream:
            multiscale = list(csv.DictReader(stream))
        with (output_dir / "multiscale_benchmark.csv").open("w", newline="", encoding="utf-8") as stream:
            fields = ["backend", "movie_count", "intent", "iterations", "median_ms", "p95_ms"]
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
            writer.writeheader(); writer.writerows(multiscale)
        lines = ["| Backend | Movies | Intent | Iterations | Median (ms) | P95 (ms) |",
                 "|---|---:|---|---:|---:|---:|"]
        lines += [f"| {row['backend']} | {row['movie_count']} | {row['intent']} | "
                  f"{row['iterations']} | {float(row['median_ms']):.3f} | {float(row['p95_ms']):.3f} |"
                  for row in multiscale]
        lines += ["", "Deterministic induced snapshots; same machine, warm-up and iteration policy."]
        (output_dir / "multiscale_benchmark.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    global RESULTS
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=RESULTS)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    RESULTS = args.results_dir
    build(args.output_dir or RESULTS / "summary")


if __name__ == "__main__":
    main()
