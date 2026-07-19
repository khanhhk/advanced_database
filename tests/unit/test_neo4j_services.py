from src.qa.neo4j_service import answer


def _disable_llm(monkeypatch):
    monkeypatch.setattr("src.qa.neo4j_service.configured_planner", lambda settings: None)


class FakeRepository:
    def __init__(self, rows): self.rows, self.calls = rows, []
    def run(self, query, **parameters):
        self.calls.append((query, parameters)); return self.rows


def test_neo4j_qa_uses_parameterized_catalog_query(monkeypatch):
    _disable_llm(monkeypatch)
    repository = FakeRepository([{"movie_id": 1, "title": "Inception", "relationship": "DIRECTED"}])
    text, intent, evidence = answer("Những phim nào do Christopher Nolan đạo diễn?", repository)
    assert intent == "movies_by_director" and "Inception" in text and evidence
    query, parameters = repository.calls[0]
    assert "$director" in query and "Christopher Nolan" not in query
    assert parameters == {"director": "christopher nolan"}


def test_neo4j_qa_links_entity_to_canonical_name(monkeypatch):
    _disable_llm(monkeypatch)
    repository = FakeRepository([{"movie_id": 1, "title": "Inception", "relationship": "DIRECTED"}])
    repository.search_entities = lambda query, limit: [
        {"id": "tmdb:525", "name": "Christopher Nolan", "type": "Person"}]
    _, _, evidence = answer("Những phim nào do Cristopher Nolan đạo diễn?", repository)
    assert repository.calls[0][1] == {"director": "Christopher Nolan"}
    assert evidence[0]["entity_links"][0]["confidence"] >= .7


def test_movie_lookup_uses_exact_canonical_title(monkeypatch):
    _disable_llm(monkeypatch)
    repository = FakeRepository([{"movie_id": 155, "name": "Christian Bale",
                                  "relationship": "ACTED_IN"}])
    repository.search_entities = lambda query, limit: [
        {"id": 155, "name": "The Dark Knight", "type": "Movie"},
        {"id": 49026, "name": "The Dark Knight Rises", "type": "Movie"},
    ]

    text, intent, _ = answer("Diễn viên nào đóng trong phim The Dark Knight?", repository)

    assert intent == "actors_in_movie" and "Christian Bale" in text
    query, parameters = repository.calls[0]
    assert "toLower(m.title) = toLower($movie)" in query
    assert "toLower(m.title) CONTAINS" not in query
    assert parameters == {"movie": "The Dark Knight"}


def test_neo4j_qa_understands_movies_by_person_without_role(monkeypatch):
    _disable_llm(monkeypatch)
    repository = FakeRepository([{"movie_id": 1, "title": "The Great Mouse Detective",
                                  "relationship": "ACTED_IN"}])
    repository.search_entities = lambda query, limit: [
        {"id": "tmdb:1219", "name": "Elisa Gabrielli", "type": "Person"}]
    text, intent, evidence = answer("tôi cần tìm phim của Elisa Gabrielli", repository)
    assert intent == "movies_by_person"
    assert "The Great Mouse Detective" in text
    assert evidence
    assert repository.calls[0][1] == {"person": "Elisa Gabrielli"}
