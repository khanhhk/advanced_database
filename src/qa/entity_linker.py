from dataclasses import dataclass

from rapidfuzz import process

from src.processing.clean import normalize_for_match


@dataclass(frozen=True)
class LinkedEntity:
    entity_id: int | str
    canonical_name: str
    entity_type: str
    confidence: float


def link(value: str, entities: list[dict], entity_type: str | None = None, threshold: float = 70) -> LinkedEntity | None:
    candidates = [e for e in entities if not entity_type or e.get("type") == entity_type]
    exact = next((e for e in candidates if normalize_for_match(e["name"]) == normalize_for_match(value)), None)
    if exact: return LinkedEntity(exact["id"], exact["name"], exact["type"], 1.0)
    names = {normalize_for_match(e["name"]): e for e in candidates}
    match = process.extractOne(normalize_for_match(value), names.keys())
    if not match or match[1] < threshold: return None
    entity = names[match[0]]
    return LinkedEntity(entity["id"], entity["name"], entity["type"], match[1] / 100)

