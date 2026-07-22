"""Build deterministic induced processed snapshots for scale experiments."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


NODE_KEYS = {
    "people": "person_id", "genres": "genre_id", "keywords": "keyword_id", "studios": "company_id",
}
EDGE_SPECS = {
    "acted_in": ("people", "person_id"), "directed": ("people", "person_id"),
    "has_genre": ("genres", "genre_id"), "has_keyword": ("keywords", "keyword_id"),
    "produced_by": ("studios", "company_id"),
}


def _read(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def _write(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def build_induced_snapshot(source: Path, destination: Path, movie_count: int) -> dict:
    movie_fields, movies = _read(source / "movies.csv")
    if movie_count < 1 or movie_count > len(movies):
        raise ValueError(f"movie_count must be in 1..{len(movies)}, got {movie_count}")
    selected_movies = movies[:movie_count]
    movie_ids = {row["tmdb_id"] for row in selected_movies}
    destination.mkdir(parents=True, exist_ok=True)
    _write(destination / "movies.csv", movie_fields, selected_movies)

    filtered_edges = {}
    referenced = {name: set() for name in NODE_KEYS}
    for edge, (node_name, foreign_key) in EDGE_SPECS.items():
        fields, rows = _read(source / f"{edge}.csv")
        kept = [row for row in rows if row["tmdb_id"] in movie_ids]
        filtered_edges[edge] = kept
        referenced[node_name].update(row[foreign_key] for row in kept)
        _write(destination / f"{edge}.csv", fields, kept)

    selected_nodes = {}
    for name, key in NODE_KEYS.items():
        fields, rows = _read(source / f"{name}.csv")
        kept = [row for row in rows if row[key] in referenced[name]]
        selected_nodes[name] = kept
        _write(destination / f"{name}.csv", fields, kept)

    source_manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    manifest = {
        "kind": "deterministic-induced-benchmark-snapshot",
        "selection": "first-n-processed-source-order",
        "requested_movies": movie_count,
        "source_sha256": source_manifest.get("source_sha256"),
        "counts": {"movies": len(selected_movies),
                   **{name: len(rows) for name, rows in selected_nodes.items()},
                   **{name: len(rows) for name, rows in filtered_edges.items()}},
    }
    manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    manifest["snapshot_sha256"] = hashlib.sha256(manifest_bytes).hexdigest()
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
