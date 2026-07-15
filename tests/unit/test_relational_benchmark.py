from experiments.benchmark_relational import QUERIES, benchmark, build_database
from src.processing.pipeline import transform
import json


def test_relational_baseline_runs_on_processed_snapshot(tmp_path):
    source = tmp_path / "movies.json"
    source.write_text(json.dumps({"movies": [{"tmdb_id": 1, "title": "A", "rating": 9,
        "actors": [{"tmdb_id": 10, "name": "Actor"}],
        "directors": [{"tmdb_id": 11, "name": "Christopher Nolan"}],
        "genres": [{"genre_id": 2, "name": "Crime"}], "keywords": [], "studios": []}]}))
    processed = tmp_path / "processed"; transform(source, processed)
    rows = benchmark(build_database(processed), 2)
    assert len(rows) == len(QUERIES)
    assert all(row["iterations"] == 2 for row in rows)
