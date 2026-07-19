import os
from pathlib import Path

import pytest

from src.kg.load_neo4j import load
from src.kg.repository import Neo4jRepository
from src.config import get_settings
from src.processing.pipeline import transform
from src.kg import crud


@pytest.mark.neo4j
@pytest.mark.skipif(not (os.getenv("RUN_NEO4J_TESTS") and os.getenv("ALLOW_NEO4J_TEST_RESET")),
                    reason="requires a disposable Neo4j and explicit reset permission")
def test_import_is_idempotent(tmp_path):
    settings = get_settings()
    transform(Path("tests/fixtures/movies.json"), tmp_path)
    first = load(tmp_path, replace=True); second = load(tmp_path)
    assert first == second and second["valid"]
    repository = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password, settings.neo4j_database)
    try:
        text, intent, evidence = repository.answer("Những phim nào do Christopher Nolan đạo diễn?")
        assert intent == "movies_by_director" and "Inception" in text and evidence
        text, intent, evidence = repository.answer("Diễn viên nào đóng trong phim The Dark Knight?")
        assert intent == "actors_in_movie" and "Heath Ledger" in text and evidence
        assert "Tom Hardy" not in text and "Anne Hathaway" not in text
        recommendations = repository.recommend(27205, 3)
        assert recommendations and all(item.explanation for item in recommendations)
        created = crud.create_movie(repository, tmdb_id=99999999, title="Integration Test Movie")
        assert created["title"] == "Integration Test Movie"
        assert crud.update_movie(repository, tmdb_id=99999999, overview="updated", runtime=90)["runtime"] == 90
        assert crud.read_movie(repository, 99999999)["movie"]["overview"] == "updated"
        assert crud.delete_movie(repository, 99999999)
        assert crud.read_movie(repository, 99999999) is None
    finally:
        repository.run("MATCH (n) DETACH DELETE n")
        repository.close()
