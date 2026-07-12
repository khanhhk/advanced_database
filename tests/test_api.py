from types import SimpleNamespace

from fastapi import HTTPException

from src.api.main import ask, health, recommendations
from src.kg.repository import MemoryRepository
from src.models import AskRequest, RecommendRequest
from pathlib import Path


def test_api_end_to_end():
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(
        repository=MemoryRepository(Path("tests/fixtures/movies.json")))))
    assert health(request) == {"status": "ok"}
    response = ask(AskRequest(question="Những phim nào do Christopher Nolan đạo diễn?"), request)
    assert response.intent == "movies_by_director"
    assert len(recommendations(RecommendRequest(movie_id=27205, top_k=2), request)) == 2
    try:
        recommendations(RecommendRequest(movie_id=-1), request)
        assert False, "missing movie must return 404"
    except HTTPException as exc:
        assert exc.status_code == 404


def test_api_delegates_graph_operations_to_repository():
    class Repository:
        def answer(self, question): return "ok", "graph", [{"query": "parameterized"}]
        def recommend(self, movie_id, top_k, method): return []
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(repository=Repository())))
    assert ask(AskRequest(question="graph question"), request).intent == "graph"
    assert recommendations(RecommendRequest(movie_id=1), request) == []
