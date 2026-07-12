from src.processing.clean import clean_movie, normalize_for_match, parse_date
from src.processing.entity_resolution import resolve_entity


def test_clean_and_normalize():
    assert normalize_for_match("  Nguyễn   Văn A ") == "nguyen van a"
    assert parse_date("bad") is None
    assert clean_movie({"tmdb_id": "1", "title": "  Film  ", "rating": "7.5"})["rating"] == 7.5
    assert clean_movie({"title": "missing id"}) is None


def test_resolution_prefers_id_and_can_fuzzy_match():
    assert resolve_entity({"id": "a", "imdb_id": "tt1", "name": "X"}, [{"id": "b", "imdb_id": "tt1", "name": "Y"}]).method == "imdb_id"
    assert resolve_entity({"id": "a", "name": "Christopher Nolan"}, [{"id": "b", "name": "Cristopher Nolan"}], 80).method == "fuzzy_name"

