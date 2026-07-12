from src.qa.neo4j_service import answer


class FakeRepository:
    def __init__(self, rows): self.rows, self.calls = rows, []
    def run(self, query, **parameters):
        self.calls.append((query, parameters)); return self.rows


def test_neo4j_qa_uses_parameterized_catalog_query():
    repository = FakeRepository([{"movie_id": 1, "title": "Inception", "relationship": "DIRECTED"}])
    text, intent, evidence = answer("Những phim nào do Christopher Nolan đạo diễn?", repository)
    assert intent == "movies_by_director" and "Inception" in text and evidence
    query, parameters = repository.calls[0]
    assert "$director" in query and "Christopher Nolan" not in query
    assert parameters == {"director": "christopher nolan"}


def test_neo4j_qa_links_entity_to_canonical_name():
    repository = FakeRepository([{"movie_id": 1, "title": "Inception", "relationship": "DIRECTED"}])
    repository.search_entities = lambda query, limit: [
        {"id": "tmdb:525", "name": "Christopher Nolan", "type": "Person"}]
    _, _, evidence = answer("Những phim nào do Cristopher Nolan đạo diễn?", repository)
    assert repository.calls[0][1] == {"director": "Christopher Nolan"}
    assert evidence[0]["entity_links"][0]["confidence"] >= .7
