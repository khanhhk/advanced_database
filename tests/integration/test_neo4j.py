import os
from pathlib import Path

import pytest

from src.kg.load_neo4j import load
from src.kg.repository import Neo4jRepository
from src.config import get_settings
from src.processing.pipeline import transform


@pytest.mark.neo4j
@pytest.mark.skipif(not os.getenv("RUN_NEO4J_TESTS"), reason="set RUN_NEO4J_TESTS=1 with Neo4j running")
def test_import_is_idempotent(tmp_path):
    settings = get_settings()
    probe = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password, settings.neo4j_database)
    try:
        if probe.run("MATCH (n) RETURN count(n) AS n")[0]["n"]:
            pytest.skip("integration import requires an empty disposable Neo4j database")
    finally:
        probe.close()
    transform(Path("tests/fixtures/movies.json"), tmp_path)
    first = load(tmp_path, replace=True); second = load(tmp_path)
    assert first == second and second["valid"]
    repository = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password, settings.neo4j_database)
    try:
        text, intent, evidence = repository.answer("Những phim nào do Christopher Nolan đạo diễn?")
        assert intent == "movies_by_director" and "Inception" in text and evidence
        recommendations = repository.recommend(27205, 3, "weighted_jaccard")
        assert recommendations and all(item.explanation for item in recommendations)
    finally:
        repository.run("MATCH (n) DETACH DELETE n")
        repository.close()
