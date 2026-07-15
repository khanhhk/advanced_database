from dataclasses import dataclass

from rapidfuzz.fuzz import ratio

from .clean import normalize_for_match


@dataclass(frozen=True)
class Match:
    left_id: str
    right_id: str
    confidence: float
    method: str


def resolve_entity(left: dict, candidates: list[dict], threshold: float = 90) -> Match | None:
    """Prefer stable external IDs; fall back to a conservative name match."""
    for candidate in candidates:
        for key in ("imdb_id", "tmdb_id"):
            if left.get(key) and left.get(key) == candidate.get(key):
                return Match(str(left.get("id", left[key])), str(candidate.get("id", candidate[key])), 1.0, key)
    name = normalize_for_match(left.get("name") or left.get("title"))
    scored = [(ratio(name, normalize_for_match(c.get("name") or c.get("title"))), c) for c in candidates]
    if not name or not scored:
        return None
    scored.sort(key=lambda item: item[0], reverse=True)
    score, candidate = scored[0]
    if score < threshold:
        return None
    if len(scored) > 1 and scored[1][0] == score:
        return None
    return Match(str(left.get("id", "")), str(candidate.get("id", candidate.get("tmdb_id", ""))), score / 100, "fuzzy_name")
