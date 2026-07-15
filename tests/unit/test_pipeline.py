import csv
import gzip
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


def test_pipeline_stream_joins_imdb_ratings_by_exact_id(tmp_path):
    source = tmp_path / "raw.json"
    source.write_text(json.dumps({"movies": [
        {"tmdb_id": 1, "imdb_id": "tt1", "title": "A", "actors": [], "directors": [], "genres": ["Drama"], "keywords": [], "studios": []},
        {"tmdb_id": 2, "imdb_id": "tt2", "title": "B", "rating": 7.1, "actors": [], "directors": [], "genres": ["Drama"], "keywords": [], "studios": []}]}))
    imdb = tmp_path / "title.ratings.tsv.gz"
    with gzip.open(imdb, "wt", encoding="utf-8", newline="") as stream:
        stream.write("tconst\taverageRating\tnumVotes\n")
        stream.write("tt1\t8.8\t12345\n")
        stream.write("tt999\t9.9\t1\n")
    manifest = transform(source, tmp_path / "out", imdb)
    with (tmp_path / "out/movies.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["imdb_rating"] == "8.8" and rows[0]["imdb_votes"] == "12345"
    assert rows[1]["rating"] == "7.1" and rows[1]["imdb_rating"] == ""
    assert manifest["imdb"]["matched_ratings"] == 1


def test_pipeline_preserves_snapshot_imdb_enrichment_without_raw_ratings(tmp_path):
    source = tmp_path / "snapshot.json"
    source.write_text(json.dumps({"movies": [{"tmdb_id": 1, "imdb_id": "tt1", "title": "A",
        "imdb_rating": 8.5, "imdb_votes": 100, "actors": [], "directors": [],
        "genres": ["Drama"], "keywords": [], "studios": []}]}))
    manifest = transform(source, tmp_path / "out")
    with (tmp_path / "out/movies.csv").open() as stream: row = next(csv.DictReader(stream))
    assert row["imdb_rating"] == "8.5" and row["imdb_votes"] == "100"
    assert manifest["imdb"]["matched_ratings"] == 1


def test_pipeline_rejects_movies_without_graph_relationships(tmp_path):
    source = tmp_path / "raw.json"
    source.write_text(json.dumps({"movies": [
        {"tmdb_id": 1, "title": "Connected", "genres": ["Drama"]},
        {"tmdb_id": 2, "title": "Isolated"},
    ]}))
    manifest = transform(source, tmp_path / "out")
    with (tmp_path / "out/movies.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert [row["title"] for row in rows] == ["Connected"]
    assert manifest["quality"]["rejected_orphan_movies"] == 1
    assert manifest["invalid_records"][-1]["reason"] == "no_graph_relationships"
