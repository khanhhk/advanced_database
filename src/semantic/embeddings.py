from __future__ import annotations

from functools import lru_cache

from src.config import get_settings


@lru_cache(maxsize=1)
def _model():
    try:
        from fastembed import TextEmbedding
    except ImportError as exc:
        raise RuntimeError("Semantic features require: pip install -e '.[semantic]'") from exc
    return TextEmbedding(model_name=get_settings().embedding_model)


def embed(texts: list[str]) -> list[list[float]]:
    return [vector.tolist() for vector in _model().embed(texts)]


def movie_document(movie: dict) -> str:
    fields = [movie.get("title", ""), movie.get("overview", "")]
    for key in ("genres", "keywords"):
        values = movie.get(key, [])
        fields.append(", ".join(v.get("name", "") if isinstance(v, dict) else str(v) for v in values))
    return ". ".join(value for value in fields if value)
