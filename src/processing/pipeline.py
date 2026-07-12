"""Deterministic raw-to-processed transformation for the movie graph."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .clean import clean_movie, normalize_name

NODE_FILES = ("movies", "people", "genres", "keywords", "studios")
EDGE_FILES = ("acted_in", "directed", "has_genre", "has_keyword", "produced_by")


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha1(value.casefold().encode("utf-8"), usedforsecurity=False).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def transform(source: Path, output_dir: Path) -> dict:
    """Create normalized node/edge tables plus a reproducible quality manifest."""
    raw = json.loads(source.read_text(encoding="utf-8"))
    records = raw.get("movies", raw) if isinstance(raw, dict) else raw
    output_dir.mkdir(parents=True, exist_ok=True)
    movies, invalid = [], []
    entities: dict[str, dict[str, dict]] = {key: {} for key in NODE_FILES[1:]}
    edges: dict[str, list[dict]] = defaultdict(list)

    seen_movies: set[int] = set()
    for index, record in enumerate(records):
        movie = clean_movie(record)
        if not movie:
            invalid.append({"row": index, "reason": "missing_or_invalid_tmdb_id_or_title"})
            continue
        movie_id = movie["tmdb_id"]
        if movie_id in seen_movies:
            invalid.append({"row": index, "reason": "duplicate_tmdb_id", "tmdb_id": movie_id})
            continue
        seen_movies.add(movie_id)
        movies.append({key: movie.get(key) for key in
                       ("tmdb_id", "imdb_id", "title", "release_date", "runtime", "rating", "popularity", "overview")})
        for name in movie.get("actors", []):
            name = normalize_name(name); person_id = _stable_id("person", name)
            entities["people"][person_id] = {"person_id": person_id, "name": name, "source": "tmdb"}
            edges["acted_in"].append({"person_id": person_id, "tmdb_id": movie_id,
                                       "character": "", "cast_order": "", "source": "tmdb"})
        for name in movie.get("directors", []):
            name = normalize_name(name); person_id = _stable_id("person", name)
            entities["people"][person_id] = {"person_id": person_id, "name": name, "source": "tmdb"}
            edges["directed"].append({"person_id": person_id, "tmdb_id": movie_id, "source": "tmdb"})
        for plural, edge_name, id_name, prefix in (("genres", "has_genre", "genre_id", "genre"),
                                                    ("keywords", "has_keyword", "keyword_id", "keyword"),
                                                    ("studios", "produced_by", "company_id", "studio")):
            for name in movie.get(plural, []):
                name = normalize_name(name); entity_id = _stable_id(prefix, name)
                entities[plural][entity_id] = {id_name: entity_id, "name": name, "source": "tmdb"}
                edges[edge_name].append({"tmdb_id": movie_id, id_name: entity_id, "source": "tmdb"})

    node_rows = {"movies": movies, **{key: list(values.values()) for key, values in entities.items()}}
    node_fields = {
        "movies": ["tmdb_id", "imdb_id", "title", "release_date", "runtime", "rating", "popularity", "overview"],
        "people": ["person_id", "name", "source"], "genres": ["genre_id", "name", "source"],
        "keywords": ["keyword_id", "name", "source"], "studios": ["company_id", "name", "source"],
    }
    edge_fields = {"acted_in": ["person_id", "tmdb_id", "character", "cast_order", "source"],
                   "directed": ["person_id", "tmdb_id", "source"],
                   "has_genre": ["tmdb_id", "genre_id", "source"],
                   "has_keyword": ["tmdb_id", "keyword_id", "source"],
                   "produced_by": ["tmdb_id", "company_id", "source"]}
    for name, rows in node_rows.items(): _write_csv(output_dir / f"{name}.csv", rows, node_fields[name])
    for name in EDGE_FILES: _write_csv(output_dir / f"{name}.csv", edges[name], edge_fields[name])
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "source": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "counts": {**{k: len(v) for k, v in node_rows.items()}, **{k: len(edges[k]) for k in EDGE_FILES}},
        "quality": {"input_records": len(records), "valid_movies": len(movies), "invalid_records": len(invalid),
                    "duplicate_movie_rate": sum(x["reason"] == "duplicate_tmdb_id" for x in invalid) / max(len(records), 1),
                    "missing_required_rate": sum(x["reason"].startswith("missing") for x in invalid) / max(len(records), 1),
                    "invalid_edges": 0},
        "invalid_records": invalid,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize movie JSON into graph node/edge CSV files")
    parser.add_argument("--input", type=Path, default=Path("data/samples/movies.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    print(json.dumps(transform(args.input, args.output), ensure_ascii=False, indent=2))

