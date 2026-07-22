import csv
import json
from pathlib import Path

from experiments.benchmarks.snapshot_subset import build_induced_snapshot
from experiments.corpora.build_entity_review_pack import build as build_review_pack
from experiments.corpora.validate_human_review import validate
from experiments.evaluation.audit_knowledge_quality import audit
from experiments.evaluation.evaluate_entity_review import evaluate as evaluate_human_entity_review
from experiments.semantic.evaluate_jena import _bounded
from src.processing.pipeline import transform


def _processed_fixture(tmp_path: Path) -> Path:
    source = tmp_path / "movies.json"
    source.write_text(json.dumps({"movies": [
        {"tmdb_id": 1, "title": "Movie One", "imdb_id": "tt1",
         "actors": [{"tmdb_id": 10, "name": "Actor One"}],
         "directors": [{"tmdb_id": 11, "name": "Director One"}],
         "genres": [{"genre_id": 20, "name": "Drama"}], "keywords": [], "studios": []},
        {"tmdb_id": 2, "title": "Movie Two",
         "actors": [{"tmdb_id": 10, "name": "Actor One"}],
         "directors": [{"tmdb_id": 12, "name": "Director Two"}],
         "genres": [{"genre_id": 20, "name": "Drama"}], "keywords": [], "studios": []},
    ]}), encoding="utf-8")
    processed = tmp_path / "processed"
    transform(source, processed)
    return processed


def test_quality_audit_and_induced_snapshot(tmp_path):
    processed = _processed_fixture(tmp_path)
    result = audit(processed)
    assert result["valid"] and result["violation_count"] == 0
    subset = tmp_path / "subset"
    manifest = build_induced_snapshot(processed, subset, 1)
    assert manifest["counts"]["movies"] == 1
    with (subset / "acted_in.csv").open(encoding="utf-8") as stream:
        assert {row["tmdb_id"] for row in csv.DictReader(stream)} == {"1"}
    assert audit(subset)["valid"]


def test_pipeline_collapses_repeated_actor_credit_without_losing_roles(tmp_path):
    source = tmp_path / "movies.json"
    source.write_text(json.dumps({"movies": [{"tmdb_id": 1, "title": "A",
        "actors": [{"tmdb_id": 10, "name": "Actor", "character": "Voice B", "cast_order": 4},
                   {"tmdb_id": 10, "name": "Actor", "character": "Voice A", "cast_order": 2}],
        "directors": [], "genres": [{"genre_id": 20, "name": "Drama"}],
        "keywords": [], "studios": []}]}), encoding="utf-8")
    processed = tmp_path / "processed"
    manifest = transform(source, processed)
    with (processed / "acted_in.csv").open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1 and rows[0]["cast_order"] == "2"
    assert rows[0]["character"] == "Voice B | Voice A"
    assert manifest["quality"]["duplicate_edges_collapsed"]["acted_in"] == 1
    assert len(manifest["processed_sha256"]) == 64


def test_blind_review_pack_requires_real_reviewer_and_can_be_evaluated(tmp_path):
    silver = tmp_path / "silver.json"
    silver.write_text(json.dumps([{"case_id": "er-001", "left": {"id": "m1", "tmdb_id": 1,
        "title": "Movie One"}, "candidates": [{"id": "tmdb:1", "tmdb_id": 1,
        "title": "Movie One"}], "threshold": 85, "is_match": True,
        "expected_id": "tmdb:1"}]), encoding="utf-8")
    review = tmp_path / "review.json"
    build_review_pack(silver, review)
    document = json.loads(review.read_text(encoding="utf-8"))
    assert "is_match" not in document["cases"][0]
    assert not validate([review])["conforms"]
    human = document["cases"][0]["human_review"]
    human.update({"reviewer_id": "reviewer-01", "reviewed_at": "2026-07-22T12:00:00+07:00",
                  "decision": "match", "expected_id": "tmdb:1", "confidence": "high"})
    review.write_text(json.dumps(document), encoding="utf-8")
    assert validate([review])["conforms"]
    assert evaluate_human_entity_review(review)["f1"] == 1.0


def test_jena_catalog_query_is_bounded_and_bound():
    query = "PREFIX : <https://example.org/movie-kg/> SELECT ?movie WHERE { ?movie a :Movie }"
    result = _bounded(query)
    assert "VALUES (?name ?movieTitle ?movieId ?wantedGenre)" in result
    assert result.rstrip().endswith("LIMIT 5")
