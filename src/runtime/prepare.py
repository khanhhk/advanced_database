"""Idempotently prepare Neo4j for serving."""
from __future__ import annotations

import json
from pathlib import Path

from src.config import get_settings
from src.kg.load_neo4j import load, validate
from src.kg.repository import Neo4jRepository


PROCESSED = Path("data/processed")
STATE = PROCESSED / "runtime_manifest.json"
VALIDATION_RESULT = Path("experiments/results/neo4j_validation.json")


def prepare() -> dict:
    manifest = json.loads((PROCESSED / "manifest.json").read_text(encoding="utf-8"))
    expected_movies = manifest["counts"]["movies"]
    source_sha = manifest["source_sha256"]
    settings = get_settings()
    repository = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password, settings.neo4j_database)
    try:
        row = repository.run("MATCH (m:Movie) RETURN count(m) AS movies")[0]
    finally:
        repository.close()
    prior = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    recorded_sha = prior.get("source_sha256")
    graph_current = row["movies"] == expected_movies and recorded_sha == source_sha
    if not graph_current:
        validation = load(PROCESSED, run_reasoning=True, replace=True)
    else:
        repository = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user,
                                     settings.neo4j_password, settings.neo4j_database)
        try:
            with repository.driver.session(database=settings.neo4j_database) as session:
                validation = {"status": "reused", **validate(session)}
        finally:
            repository.close()
    state = {"source_sha256": source_sha, "movies": expected_movies,
             "graph": "reused" if graph_current else "loaded"}
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    VALIDATION_RESULT.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_RESULT.write_text(json.dumps({"source_sha256": source_sha, **validation}, indent=2),
                                 encoding="utf-8")
    return {"runtime": state, "validation": validation}


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
