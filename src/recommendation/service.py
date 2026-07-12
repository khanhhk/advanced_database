import math
from collections import Counter

from src.models import Recommendation

WEIGHTS = {"directors": 3.0, "actors": 2.0, "keywords": 1.5, "genres": 1.0, "studios": 0.75}


def _join_names(values: list[str]) -> str:
    if len(values) < 2:
        return "".join(values)
    return ", ".join(values[:-1]) + " và " + values[-1]


def build_explanation(shared: dict[str, list[str]]) -> str:
    sentences = []
    if shared["directors"]:
        sentences.append(f"Cùng đạo diễn là {_join_names(shared['directors'])}.")
    if shared["actors"]:
        sentences.append(f"Dàn diễn viên chung gồm {_join_names(shared['actors'])}.")
    if shared["keywords"]:
        sentences.append(f"Nội dung có các chủ đề tương đồng như {_join_names(shared['keywords'])}.")
    if shared["genres"]:
        sentences.append(f"Cùng thuộc thể loại {_join_names(shared['genres'])}.")
    if shared["studios"]:
        sentences.append(f"Đều do {_join_names(shared['studios'])} sản xuất.")
    return " ".join(sentences)


def _similarity(source: dict, candidate: dict, frequencies: dict[str, Counter], movie_count: int) -> tuple[float, dict[str, list[str]]]:
    shared = {key: sorted(set(source[key]) & set(candidate[key])) for key in WEIGHTS}
    score = sum(
        WEIGHTS[key] * (1.0 + math.log((movie_count + 1.0) / (frequencies[key][value] + 1.0)))
        for key, values in shared.items() for value in values
    )
    return score, shared


def recommend(movies: list[dict], movie_id: int, top_k: int = 10) -> list[Recommendation]:
    movies = [_name_view(movie) for movie in movies]
    source = next((m for m in movies if m["tmdb_id"] == movie_id), None)
    if not source: raise KeyError(movie_id)
    frequencies = {key: Counter(value for movie in movies for value in set(movie[key])) for key in WEIGHTS}
    results = []
    for candidate in movies:
        if candidate["tmdb_id"] == movie_id: continue
        score, shared = _similarity(source, candidate, frequencies, len(movies))
        if score <= 0: continue
        results.append(Recommendation(movie_id=candidate["tmdb_id"], title=candidate["title"], score=round(score, 6),
            shared_directors=shared["directors"], shared_actors=shared["actors"], shared_genres=shared["genres"],
            shared_keywords=shared["keywords"], shared_studios=shared["studios"],
            explanation=build_explanation(shared)))
    return sorted(results, key=lambda r: (-r.score, r.title))[:top_k]


def _name_view(movie):
    result = dict(movie)
    for key in WEIGHTS:
        result[key] = [value.get("name", "") if isinstance(value, dict) else value for value in movie.get(key, [])]
    return result
