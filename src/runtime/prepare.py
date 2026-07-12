"""Idempotently prepare Neo4j for serving."""
from __future__ import annotations

import json
from pathlib import Path

from src.config import get_settings
from src.kg.load_neo4j import load
from src.kg.repository import Neo4jRepository


PROCESSED = Path("data/processed")
STATE = PROCESSED / "runtime_manifest.json"


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
        validation = {"valid": True, "status": "reused", "movies": row["movies"]}
    state = {"source_sha256": source_sha, "movies": expected_movies,
             "graph": "reused" if graph_current else "loaded"}
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return {"runtime": state, "validation": validation}


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
