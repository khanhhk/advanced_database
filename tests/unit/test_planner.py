import json
from types import SimpleNamespace

from src.qa.planner import QuestionPlanner, QueryPlan, configured_planner
from src.qa.query_compiler import compile_plan


def test_compiler_builds_parameterized_movie_query():
    plan = QueryPlan.model_validate({
        "operation": "find", "target": "Movie",
        "entities": [{"type": "Person", "name": "Christopher Nolan", "role": "director"},
                     {"type": "Genre", "name": "Science Fiction"}],
        "filters": [{"field": "rating", "operator": "gt", "value": 7}],
        "sort": {"field": "release_date", "direction": "desc"},
        "limit": 10, "confidence": .95, "clarification": None,
    })
    compiled = compile_plan(plan)
    assert "Christopher Nolan" not in compiled.cypher
    assert "$entity0" in compiled.cypher and "$filter0" in compiled.cypher
    assert compiled.parameters["entity0"] == "Christopher Nolan"
    assert "DIRECTED" in compiled.cypher and "HAS_GENRE" in compiled.cypher


def test_planner_validates_structured_llm_output(monkeypatch):
    payload = {"operation": "find", "target": "Movie",
               "entities": [{"type": "Person", "name": "Elisa Gabrielli", "role": "any"}],
               "filters": [], "sort": None, "limit": 10, "confidence": .9, "clarification": None}
    response = SimpleNamespace(raise_for_status=lambda: None,
        json=lambda: {"choices": [{"message": {"content": json.dumps(payload)}}]})
    monkeypatch.setattr("src.qa.planner.httpx.post", lambda *args, **kwargs: response)
    plan = QuestionPlanner("key", "https://example.test/v1", "model").plan("phim của Elisa")
    assert plan.entities[0].name == "Elisa Gabrielli"
    assert plan.operation == "find"


def test_planner_is_optional_without_configuration():
    settings = SimpleNamespace(llm_api_key=None, llm_model=None, llm_base_url="", llm_timeout=20)
    assert configured_planner(settings) is None
