"""Idempotent, batched Neo4j loader for normalized CSV artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from src.config import get_settings
from src.processing.pipeline import transform


def _rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream: return list(csv.DictReader(stream))


QUERIES = {
    "movies": """UNWIND $rows AS r MERGE (n:Movie {tmdb_id:toInteger(r.tmdb_id)})
      SET n.imdb_id=r.imdb_id,n.title=r.title,n.release_date=r.release_date,
      n.runtime=CASE WHEN r.runtime='' THEN null ELSE toInteger(r.runtime) END,
      n.rating=CASE WHEN r.rating='' THEN null ELSE toFloat(r.rating) END,
      n.imdb_rating=CASE WHEN r.imdb_rating='' THEN null ELSE toFloat(r.imdb_rating) END,
      n.imdb_votes=CASE WHEN r.imdb_votes='' THEN null ELSE toInteger(r.imdb_votes) END,
      n.popularity=CASE WHEN r.popularity='' THEN null ELSE toFloat(r.popularity) END,n.overview=r.overview,n.source='tmdb'""",
    "people": "UNWIND $rows AS r MERGE (n:Person {person_id:r.person_id}) SET n.name=r.name,n.source=r.source",
    "genres": "UNWIND $rows AS r MERGE (n:Genre {genre_id:r.genre_id}) SET n.name=r.name,n.source=r.source",
    "keywords": "UNWIND $rows AS r MERGE (n:Keyword {keyword_id:r.keyword_id}) SET n.name=r.name,n.source=r.source",
    "studios": "UNWIND $rows AS r MERGE (n:Studio {company_id:r.company_id}) SET n.name=r.name,n.source=r.source",
    "acted_in": """UNWIND $rows AS r MATCH (p:Person {person_id:r.person_id}),(m:Movie {tmdb_id:toInteger(r.tmdb_id)})
      MERGE (p)-[e:ACTED_IN]->(m) SET e.character=r.character,e.cast_order=CASE WHEN r.cast_order='' THEN null ELSE toInteger(r.cast_order) END,e.source=r.source""",
    "directed": "UNWIND $rows AS r MATCH (p:Person {person_id:r.person_id}),(m:Movie {tmdb_id:toInteger(r.tmdb_id)}) MERGE (p)-[e:DIRECTED]->(m) SET e.source=r.source",
    "has_genre": "UNWIND $rows AS r MATCH (m:Movie {tmdb_id:toInteger(r.tmdb_id)}),(n:Genre {genre_id:r.genre_id}) MERGE (m)-[e:HAS_GENRE]->(n) SET e.source=r.source",
    "has_keyword": "UNWIND $rows AS r MATCH (m:Movie {tmdb_id:toInteger(r.tmdb_id)}),(n:Keyword {keyword_id:r.keyword_id}) MERGE (m)-[e:HAS_KEYWORD]->(n) SET e.source=r.source",
    "produced_by": "UNWIND $rows AS r MATCH (m:Movie {tmdb_id:toInteger(r.tmdb_id)}),(n:Studio {company_id:r.company_id}) MERGE (m)-[e:PRODUCED_BY]->(n) SET e.source=r.source",
}


def _statements(path: Path):
    for statement in path.read_text(encoding="utf-8").split(";"):
        statement = "\n".join(line for line in statement.splitlines() if not line.strip().startswith("//")).strip()
        if statement: yield statement


def validate(session) -> dict:
    result = {}
    result["nodes"] = session.run("MATCH (n) RETURN count(n) AS n").single()["n"]
    result["relationships"] = session.run("MATCH ()-[r]->() RETURN count(r) AS n").single()["n"]
    result["orphan_movies"] = session.run("MATCH (m:Movie) WHERE NOT (m)--() RETURN count(m) AS n").single()["n"]
    result["duplicate_stable_ids"] = session.run("""MATCH (m:Movie) WITH m.tmdb_id AS id,count(*) AS n
      WHERE n>1 RETURN coalesce(sum(n-1),0) AS n""").single()["n"]
    result["invalid_edges"] = session.run("MATCH ()-[r]->() WHERE startNode(r) IS NULL OR endNode(r) IS NULL RETURN count(r) AS n").single()["n"]
    result["valid"] = result["orphan_movies"] == result["duplicate_stable_ids"] == result["invalid_edges"] == 0
    return result


def load(processed_dir: Path, batch_size: int = 500, run_reasoning: bool = True) -> dict:
    from neo4j import GraphDatabase
    settings = get_settings()
    driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
    try:
        with driver.session(database=settings.neo4j_database) as session:
            for query in _statements(Path("cypher/constraints.cypher")): session.run(query).consume()
            for table, query in QUERIES.items():
                rows = _rows(processed_dir / f"{table}.csv")
                for offset in range(0, len(rows), batch_size): session.run(query, rows=rows[offset:offset + batch_size]).consume()
            if run_reasoning:
                for query in _statements(Path("cypher/reasoning.cypher")): session.run(query).consume()
            return validate(session)
    finally: driver.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--source", type=Path, default=Path("data/raw/tmdb_movies.json"))
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--skip-transform", action="store_true")
    parser.add_argument("--skip-reasoning", action="store_true")
    args = parser.parse_args()
    if not args.skip_transform: transform(args.source, args.processed_dir)
    print(json.dumps(load(args.processed_dir, args.batch_size, not args.skip_reasoning), indent=2))
