from experiments.evaluate_reasoning import evaluate as evaluate_reasoning
from experiments.evaluate_recommendation import evaluate as evaluate_recommendation
from experiments.evaluate_qa_neo4j import case_passes
from src.kg.repository import MemoryRepository
from pathlib import Path


def test_reasoning_metrics_ignore_unreviewed_facts():
    assert evaluate_reasoning([{"valid": True}, {"valid": False}, {"valid": None}])["precision"] == .5


def test_recommendation_metrics_and_explanation_coverage():
    repository = MemoryRepository(Path("tests/fixtures/movies.json"))
    result = evaluate_recommendation(repository, [{"movie_id": 27205, "relevant_movie_ids": [157336]}], 2)
    assert result["cases"] == 1 and result["explanation_coverage"] == 1


def test_qa_case_can_reject_known_cross_title_contamination():
    case = {"intent": "actors_in_movie", "contains": "Christian Bale",
            "excludes": ["Tom Hardy", "Anne Hathaway"]}
    evidence = [{"movie_id": 155}]
    assert case_passes(case, "Các diễn viên: Christian Bale, Heath Ledger",
                       "actors_in_movie", evidence)
    assert not case_passes(case, "Các diễn viên: Christian Bale, Tom Hardy",
                           "actors_in_movie", evidence)
