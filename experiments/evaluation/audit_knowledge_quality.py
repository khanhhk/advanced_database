"""Audit identity, completeness, consistency and provenance on a processed snapshot."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


NODE_SPECS = {
    "movies": ("tmdb_id", ("title",)),
    "people": ("person_id", ("name",)),
    "genres": ("genre_id", ("name",)),
    "keywords": ("keyword_id", ("name",)),
    "studios": ("company_id", ("name",)),
}
EDGE_SPECS = {
    "acted_in": ("person_id", "people", "tmdb_id", "movies"),
    "directed": ("person_id", "people", "tmdb_id", "movies"),
    "has_genre": ("tmdb_id", "movies", "genre_id", "genres"),
    "has_keyword": ("tmdb_id", "movies", "keyword_id", "keywords"),
    "produced_by": ("tmdb_id", "movies", "company_id", "studios"),
}


def _rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def audit(processed: Path) -> dict:
    nodes = {name: _rows(processed / f"{name}.csv") for name in NODE_SPECS}
    edges = {name: _rows(processed / f"{name}.csv") for name in EDGE_SPECS}
    ids = {name: {row[key] for row in rows if row.get(key)}
           for name, rows in nodes.items() for key, _ in [NODE_SPECS[name]]}

    duplicate_ids = {}
    conflicting_values = []
    missing_required = {}
    for name, rows in nodes.items():
        key, required = NODE_SPECS[name]
        counts = Counter(row.get(key, "") for row in rows)
        duplicate_ids[name] = sum(count - 1 for value, count in counts.items() if value and count > 1)
        missing_required[name] = sum(not row.get(key) or any(not row.get(field) for field in required)
                                     for row in rows)
        grouped = defaultdict(set)
        for row in rows:
            if row.get(key):
                grouped[row[key]].add(tuple(row.get(field, "") for field in required))
        conflicting_values.extend({"table": name, "stable_id": stable_id,
                                   "distinct_required_values": len(values)}
                                  for stable_id, values in grouped.items() if len(values) > 1)

    invalid_foreign_keys = {}
    duplicate_edges = {}
    provenance_rows = provenance_present = 0
    for name, rows in edges.items():
        left_key, left_table, right_key, right_table = EDGE_SPECS[name]
        invalid_foreign_keys[name] = sum(row.get(left_key) not in ids[left_table]
                                         or row.get(right_key) not in ids[right_table] for row in rows)
        signatures = Counter((row.get(left_key), row.get(right_key)) for row in rows)
        duplicate_edges[name] = sum(count - 1 for count in signatures.values() if count > 1)
        provenance_rows += len(rows)
        provenance_present += sum(bool(row.get("source")) for row in rows)

    for name in ("people", "genres", "keywords", "studios"):
        provenance_rows += len(nodes[name])
        provenance_present += sum(bool(row.get("source")) for row in nodes[name])

    movies = nodes["movies"]
    movie_ids = ids["movies"]
    coverage = {
        "movies_with_imdb_id": sum(bool(row.get("imdb_id")) for row in movies) / max(len(movies), 1),
        "movies_with_imdb_rating": sum(bool(row.get("imdb_rating")) for row in movies) / max(len(movies), 1),
        "movies_with_cast": len({row["tmdb_id"] for row in edges["acted_in"]}) / max(len(movie_ids), 1),
        "movies_with_director": len({row["tmdb_id"] for row in edges["directed"]}) / max(len(movie_ids), 1),
        "movies_with_genre": len({row["tmdb_id"] for row in edges["has_genre"]}) / max(len(movie_ids), 1),
        "provenance_coverage": provenance_present / max(provenance_rows, 1),
    }
    person_names = Counter(row.get("name", "").casefold() for row in nodes["people"] if row.get("name"))
    ambiguous_names = sum(count > 1 for count in person_names.values())
    violations = (sum(duplicate_ids.values()) + sum(missing_required.values())
                  + sum(invalid_foreign_keys.values()) + sum(duplicate_edges.values())
                  + len(conflicting_values))
    return {
        "snapshot": str(processed),
        "counts": {**{name: len(rows) for name, rows in nodes.items()},
                   **{name: len(rows) for name, rows in edges.items()}},
        "identity": {"duplicate_stable_ids": duplicate_ids,
                     "conflicting_required_values": conflicting_values,
                     "ambiguous_person_names_not_used_as_keys": ambiguous_names},
        "consistency": {"missing_required": missing_required,
                        "invalid_foreign_keys": invalid_foreign_keys,
                        "duplicate_edge_pairs": duplicate_edges},
        "completeness": coverage,
        "violation_count": violations,
        "valid": violations == 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/results/quality/knowledge_quality_audit.json"))
    args = parser.parse_args()
    result = audit(args.processed_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
