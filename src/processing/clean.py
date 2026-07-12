import re
import unicodedata
from datetime import date


def normalize_name(value: str | None) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFKC", value).strip()
    return re.sub(r"\s+", " ", value)


def normalize_for_match(value: str | None) -> str:
    value = normalize_name(value).casefold()
    value = "".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c))
    return re.sub(r"[^\w]+", " ", value).strip()


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def clean_movie(record: dict) -> dict | None:
    try:
        tmdb_id = int(record["tmdb_id"])
    except (KeyError, TypeError, ValueError):
        return None
    title = normalize_name(record.get("title"))
    if not title:
        return None
    rating = record.get("rating")
    return {**record, "tmdb_id": tmdb_id, "title": title,
            "rating": float(rating) if rating is not None else None,
            "release_date": str(parse_date(record.get("release_date")) or "") or None}

