import csv
import json

from src.processing.pipeline import transform


def test_pipeline_is_deterministic_and_reports_quality(tmp_path):
    source = tmp_path / "raw.json"
    source.write_text(json.dumps({"movies": [{"tmdb_id": 1, "title": "A", "actors": ["Person A"], "directors": [], "genres": ["Drama"], "keywords": [], "studios": []}, {"tmdb_id": 1, "title": "duplicate"}, {"title": "invalid"}]}))
    first = transform(source, tmp_path / "out")
    first_movies = (tmp_path / "out/movies.csv").read_text()
    second = transform(source, tmp_path / "out")
    assert first["counts"] == second["counts"] and first_movies == (tmp_path / "out/movies.csv").read_text()
    assert first["quality"]["invalid_records"] == 2
    with (tmp_path / "out/acted_in.csv").open() as f: assert len(list(csv.DictReader(f))) == 1

