"""Export a raw-compatible experiment snapshot from the current Neo4j graph."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from src.config import get_settings
from src.kg.repository import Neo4jRepository


def _json_value(value):
    if isinstance(value, (date, datetime)): return value.isoformat()
    if hasattr(value, "iso_format"): return value.iso_format()
    return value


def export(repository, destination: Path) -> dict:
    movies = {}
    for row in repository.run("MATCH (m:Movie) RETURN m{.*} AS movie ORDER BY m.tmdb_id"):
        movie = {key: _json_value(value) for key, value in row["movie"].items()}
        movie.update({"actors": [], "directors": [], "genres": [], "keywords": [], "studios": []})
        movies[movie["tmdb_id"]] = movie
    relations = {
        "actors": """MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) RETURN m.tmdb_id AS movie_id,
          p.tmdb_id AS source_id,p.name AS name,r.character AS character,r.cast_order AS cast_order""",
        "directors": """MATCH (p:Person)-[:DIRECTED]->(m:Movie) RETURN m.tmdb_id AS movie_id,
          p.tmdb_id AS source_id,p.name AS name""",
        "genres": """MATCH (m:Movie)-[:HAS_GENRE]->(n:Genre) RETURN m.tmdb_id AS movie_id,
          n.genre_id AS source_id,n.name AS name""",
        "keywords": """MATCH (m:Movie)-[:HAS_KEYWORD]->(n:Keyword) RETURN m.tmdb_id AS movie_id,
          n.keyword_id AS source_id,n.name AS name""",
        "studios": """MATCH (m:Movie)-[:PRODUCED_BY]->(n:Studio) RETURN m.tmdb_id AS movie_id,
          n.company_id AS source_id,n.name AS name,n.country AS country""",
    }
    id_keys = {"actors": "tmdb_id", "directors": "tmdb_id", "genres": "genre_id",
               "keywords": "keyword_id", "studios": "company_id"}
    counts = {}
    for key, query in relations.items():
        rows = repository.run(query); counts[key] = len(rows)
        for row in rows:
            item = {"name": row["name"], id_keys[key]: row["source_id"]}
            for field in ("character", "cast_order", "country"):
                if field in row: item[field] = row[field]
            movies[row["movie_id"]][key].append(item)
    payload = {"snapshot_source": "neo4j", "counts": {"movies": len(movies), **counts},
               "movies": list(movies.values())}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=_json_value), encoding="utf-8")
    return payload["counts"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/interim/neo4j_snapshot.json"))
    args = parser.parse_args(); settings = get_settings()
    repository = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user,
                                 settings.neo4j_password, settings.neo4j_database)
    try: counts = export(repository, args.output)
    finally: repository.close()
    print(json.dumps(counts, indent=2))
