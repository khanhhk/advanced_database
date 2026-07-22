"""Deterministic raw-to-processed transformation for the movie graph."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from src.ingestion.imdb_loader import load_tsv

from .clean import clean_movie, normalize_name

NODE_FILES = ("movies", "people", "genres", "keywords", "studios")
EDGE_FILES = ("acted_in", "directed", "has_genre", "has_keyword", "produced_by")


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha1(value.casefold().encode("utf-8"), usedforsecurity=False).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _entity(value, id_key: str, prefix: str) -> tuple[str, str, dict]:
    """Accept legacy names and source-rich objects while preferring source IDs."""
    item = value if isinstance(value, dict) else {"name": value}
    name = normalize_name(item.get("name"))
    source_id = item.get(id_key)
    entity_id = f"tmdb:{source_id}" if source_id not in (None, "") else _stable_id(prefix, name)
    return entity_id, name, item


def _write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _deduplicate_edges(edges: dict[str, list[dict]]) -> dict[str, int]:
    """Collapse repeated source credits to the relationship identity used by Neo4j.

    TMDB can credit one person more than once in a movie for different characters.
    The graph models one ACTED_IN edge per Person–Movie pair, so character evidence
    is combined instead of being overwritten by MERGE.
    """
    removed = {}
    for name, rows in edges.items():
        if name in {"acted_in", "directed"}:
            key = lambda row: (row["person_id"], row["tmdb_id"])
        else:
            foreign_key = {"has_genre": "genre_id", "has_keyword": "keyword_id",
                           "produced_by": "company_id"}[name]
            key = lambda row, foreign_key=foreign_key: (row["tmdb_id"], row[foreign_key])
        grouped = {}
        for row in rows:
            identity = key(row)
            if identity not in grouped:
                grouped[identity] = dict(row)
                continue
            if name == "acted_in":
                current = grouped[identity]
                characters = [value.strip() for value in
                              (current.get("character", ""), row.get("character", "")) if value.strip()]
                current["character"] = " | ".join(dict.fromkeys(characters))
                orders = [int(value) for value in (current.get("cast_order"), row.get("cast_order"))
                          if value not in (None, "")]
                current["cast_order"] = min(orders) if orders else ""
        removed[name] = len(rows) - len(grouped)
        edges[name] = list(grouped.values())
    return removed


def _imdb_ratings(path: Path | None, wanted_ids: set[str]) -> dict[str, dict]:
    if not path:
        return {}
    if not path.is_file():
        raise FileNotFoundError(f"IMDb ratings file not found: {path}")
    found = {}
    for row in load_tsv(path):
        imdb_id = row.get("tconst")
        if imdb_id in wanted_ids:
            found[imdb_id] = {"imdb_rating": float(row["averageRating"]),
                              "imdb_votes": int(row["numVotes"])}
            if len(found) == len(wanted_ids):
                break
    return found


def transform(source: Path, output_dir: Path, imdb_ratings_path: Path | None = None) -> dict:
    """Create normalized node/edge tables plus a reproducible quality manifest."""
    raw = json.loads(source.read_text(encoding="utf-8"))
    records = raw.get("movies", raw) if isinstance(raw, dict) else raw
    output_dir.mkdir(parents=True, exist_ok=True)
    movies, invalid = [], []
    entities: dict[str, dict[str, dict]] = {key: {} for key in NODE_FILES[1:]}
    edges: dict[str, list[dict]] = defaultdict(list)

    seen_movies: set[int] = set()
    movie_rows: dict[int, int] = {}
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
        movie_rows[movie_id] = index
        movies.append({key: movie.get(key) for key in
                       ("tmdb_id", "imdb_id", "title", "release_date", "runtime", "rating",
                        "imdb_rating", "imdb_votes", "popularity", "overview")})
        for value in movie.get("actors", []):
            person_id, name, item = _entity(value, "tmdb_id", "person")
            if not name: continue
            entities["people"][person_id] = {"person_id": person_id, "tmdb_id": item.get("tmdb_id"),
                                               "imdb_id": item.get("imdb_id"), "name": name, "source": "tmdb"}
            edges["acted_in"].append({"person_id": person_id, "tmdb_id": movie_id,
                                       "character": item.get("character") or "",
                                       "cast_order": item.get("cast_order") if item.get("cast_order") is not None else "",
                                       "source": "tmdb"})
        for value in movie.get("directors", []):
            person_id, name, item = _entity(value, "tmdb_id", "person")
            if not name: continue
            entities["people"][person_id] = {"person_id": person_id, "tmdb_id": item.get("tmdb_id"),
                                               "imdb_id": item.get("imdb_id"), "name": name, "source": "tmdb"}
            edges["directed"].append({"person_id": person_id, "tmdb_id": movie_id, "source": "tmdb"})
        for plural, edge_name, id_name, prefix in (("genres", "has_genre", "genre_id", "genre"),
                                                    ("keywords", "has_keyword", "keyword_id", "keyword"),
                                                    ("studios", "produced_by", "company_id", "studio")):
            for value in movie.get(plural, []):
                entity_id, name, item = _entity(value, id_name, prefix)
                if not name: continue
                row = {id_name: entity_id, "name": name, "source": "tmdb"}
                if plural == "studios": row["country"] = item.get("country") or ""
                entities[plural][entity_id] = row
                edges[edge_name].append({"tmdb_id": movie_id, id_name: entity_id, "source": "tmdb"})

    duplicate_edges_collapsed = _deduplicate_edges(edges)

    # A Movie without any graph relationship cannot answer a competency question
    # and would violate the import quality gate. Keep the rejection explicit in
    # the manifest instead of silently loading an isolated node.
    linked_movie_ids = {row["tmdb_id"] for name in EDGE_FILES for row in edges[name]}
    orphan_ids = {movie["tmdb_id"] for movie in movies} - linked_movie_ids
    if orphan_ids:
        movies = [movie for movie in movies if movie["tmdb_id"] not in orphan_ids]
        invalid.extend({"row": movie_rows[movie_id], "reason": "no_graph_relationships", "tmdb_id": movie_id}
                       for movie_id in sorted(orphan_ids))

    wanted_imdb_ids = {m["imdb_id"] for m in movies if m.get("imdb_id")}
    ratings = _imdb_ratings(imdb_ratings_path, wanted_imdb_ids)
    for movie in movies:
        if movie.get("imdb_id") in ratings:
            movie.update(ratings[movie["imdb_id"]])
        else:
            movie.setdefault("imdb_rating", None); movie.setdefault("imdb_votes", None)
    matched_rating_count = sum(movie.get("imdb_rating") is not None for movie in movies)
    node_rows = {"movies": movies, **{key: list(values.values()) for key, values in entities.items()}}
    node_fields = {
        "movies": ["tmdb_id", "imdb_id", "title", "release_date", "runtime", "rating", "imdb_rating", "imdb_votes", "popularity", "overview"],
        "people": ["person_id", "tmdb_id", "imdb_id", "name", "source"], "genres": ["genre_id", "name", "source"],
        "keywords": ["keyword_id", "name", "source"], "studios": ["company_id", "name", "country", "source"],
    }
    edge_fields = {"acted_in": ["person_id", "tmdb_id", "character", "cast_order", "source"],
                   "directed": ["person_id", "tmdb_id", "source"],
                   "has_genre": ["tmdb_id", "genre_id", "source"],
                   "has_keyword": ["tmdb_id", "keyword_id", "source"],
                   "produced_by": ["tmdb_id", "company_id", "source"]}
    for name, rows in node_rows.items(): _write_csv(output_dir / f"{name}.csv", rows, node_fields[name])
    for name in EDGE_FILES: _write_csv(output_dir / f"{name}.csv", edges[name], edge_fields[name])
    processed_hash = hashlib.sha256()
    for name in (*NODE_FILES, *EDGE_FILES):
        path = output_dir / f"{name}.csv"
        processed_hash.update(path.name.encode("utf-8")); processed_hash.update(path.read_bytes())
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "source": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "imdb": {"source": str(imdb_ratings_path) if imdb_ratings_path else None,
                 "source_sha256": hashlib.sha256(imdb_ratings_path.read_bytes()).hexdigest() if imdb_ratings_path else None,
                 "tmdb_movies_with_imdb_id": len(wanted_imdb_ids), "matched_ratings": matched_rating_count,
                 "match_method": "exact_imdb_id" if imdb_ratings_path else "preserved_from_snapshot"},
        "processed_sha256": processed_hash.hexdigest(),
        "counts": {**{k: len(v) for k, v in node_rows.items()}, **{k: len(edges[k]) for k in EDGE_FILES}},
        "quality": {"input_records": len(records), "valid_movies": len(movies), "invalid_records": len(invalid),
                    "duplicate_movie_rate": sum(x["reason"] == "duplicate_tmdb_id" for x in invalid) / max(len(records), 1),
                    "missing_required_rate": sum(x["reason"].startswith("missing") for x in invalid) / max(len(records), 1),
                    "invalid_edges": 0,
                    "duplicate_edges_collapsed": duplicate_edges_collapsed,
                    "rejected_orphan_movies": len(orphan_ids),
                    "imdb_id_coverage": len(wanted_imdb_ids) / max(len(movies), 1),
                    "imdb_rating_match_coverage": matched_rating_count / max(len(wanted_imdb_ids), 1),
                    "movies_with_cast": len({row["tmdb_id"] for row in edges["acted_in"]}) / max(len(movies), 1),
                    "movies_with_director": len({row["tmdb_id"] for row in edges["directed"]}) / max(len(movies), 1),
                    "movies_with_genre": len({row["tmdb_id"] for row in edges["has_genre"]}) / max(len(movies), 1)},
        "invalid_records": invalid,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize movie JSON into graph node/edge CSV files")
    parser.add_argument("--input", type=Path, default=Path("data/raw/tmdb_movies.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed"))
    parser.add_argument("--imdb-ratings", type=Path)
    args = parser.parse_args()
    print(json.dumps(transform(args.input, args.output, args.imdb_ratings), ensure_ascii=False, indent=2))
