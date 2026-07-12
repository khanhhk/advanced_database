from src.models import Recommendation

WEIGHTS = {"directors": 3.0, "actors": 2.0, "genres": 1.5, "keywords": 1.0}


def _similarity(source: dict, candidate: dict, method: str) -> tuple[float, dict[str, list[str]]]:
    shared = {key: sorted(set(source[key]) & set(candidate[key])) for key in WEIGHTS}
    if method == "overlap": return sum(WEIGHTS[k] * len(v) for k, v in shared.items()), shared
    if method != "weighted_jaccard": raise ValueError("method must be overlap or weighted_jaccard")
    numerator = sum(WEIGHTS[k] * len(shared[k]) for k in WEIGHTS)
    denominator = sum(WEIGHTS[k] * len(set(source[k]) | set(candidate[k])) for k in WEIGHTS)
    return (numerator / denominator if denominator else 0.0), shared


def recommend(movies: list[dict], movie_id: int, top_k: int = 10, method: str = "overlap") -> list[Recommendation]:
    movies = [_name_view(movie) for movie in movies]
    source = next((m for m in movies if m["tmdb_id"] == movie_id), None)
    if not source: raise KeyError(movie_id)
    results = []
    for candidate in movies:
        if candidate["tmdb_id"] == movie_id: continue
        score, shared = _similarity(source, candidate, method)
        if score <= 0: continue
        labels = {"directors": "đạo diễn", "actors": "diễn viên", "genres": "thể loại", "keywords": "từ khóa"}
        reasons = [f"{labels[key]}: {', '.join(values)}" for key, values in shared.items() if values]
        results.append(Recommendation(movie_id=candidate["tmdb_id"], title=candidate["title"], score=round(score, 6),
            shared_directors=shared["directors"], shared_actors=shared["actors"], shared_genres=shared["genres"],
            shared_keywords=shared["keywords"], explanation="Tương đồng qua " + "; ".join(reasons)))
    return sorted(results, key=lambda r: (-r.score, r.title))[:top_k]


def _name_view(movie):
    result = dict(movie)
    for key in WEIGHTS:
        result[key] = [value.get("name", "") if isinstance(value, dict) else value for value in movie.get(key, [])]
    return result
