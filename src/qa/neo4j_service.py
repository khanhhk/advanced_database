"""Graph-native QA using a fixed catalog of parameterized Cypher queries."""

from src.kg.query_catalog import QUERIES
from src.qa.entity_linker import link
from src.qa.intents import detect_intent

SLOT_TYPES = {"director": "Person", "person": "Person", "person1": "Person",
              "person2": "Person", "movie": "Movie", "genre": "Genre"}


def answer(question: str, repository) -> tuple[str, str, list[dict]]:
    intent, slots = detect_intent(question)
    if intent == "unknown":
        return "Xin lỗi, tôi chưa hiểu câu hỏi. Hãy hỏi theo đạo diễn, diễn viên, thể loại hoặc đường liên hệ.", intent, []
    slots, links = _link_slots(repository, slots)
    if intent == "similar_movies":
        rows = repository.run(QUERIES["resolve_movie"], movie=slots["movie"],
                              movie_id=slots.get("movie_id"))
        if not rows:
            return "Không tìm thấy phim.", intent, []
        items = repository.recommend(rows[0]["movie_id"], 5)
        evidence = [x.model_dump() for x in items]
        if links: evidence.insert(0, {"entity_links": links})
        return "Phim tương tự: " + ", ".join(x.title for x in items), intent, evidence

    params = {key: (float(value) if key == "rating" else value) for key, value in slots.items()}
    rows = repository.run(QUERIES[intent], **params)
    evidence = [_serializable(row) for row in rows]
    if links: evidence.insert(0, {"entity_links": links})
    if intent in {"movies_by_director", "movies_by_person", "common_movies", "movies_by_genre_rating"}:
        prefix = ("Các phim có sự tham gia của người này" if intent == "movies_by_person" else
                  "Các phim tìm thấy" if intent == "movies_by_director" else
                  "Phim đóng chung" if intent == "common_movies" else "Các phim phù hợp")
        return _list(prefix, rows, "title"), intent, evidence
    if intent == "actors_in_movie": return _list("Các diễn viên", rows, "name"), intent, evidence
    if intent == "co_stars": return _list("Các bạn diễn", rows, "name"), intent, evidence
    if intent == "directors_by_genre": return _list("Các đạo diễn", rows, "name"), intent, evidence
    if intent == "shortest_path":
        return ("Đường liên hệ: " + " → ".join(rows[0]["labels"]) if rows else "Không tìm thấy đường liên hệ."), intent, evidence
    return "Không tìm thấy kết quả.", intent, evidence


def _list(prefix, rows, key):
    return f"{prefix}: " + ", ".join(str(row[key]) for row in rows) if rows else "Không tìm thấy kết quả."


def _serializable(value):
    if isinstance(value, dict): return {key: _serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [_serializable(item) for item in value]
    if hasattr(value, "iso_format"): return value.iso_format()
    return value


def _link_slots(repository, slots):
    if not hasattr(repository, "search_entities"):
        resolved = dict(slots)
        for key in SLOT_TYPES:
            if key in slots:
                resolved[f"{key}_id"] = None
        return resolved, []
    resolved, evidence = dict(slots), []
    for key, entity_type in SLOT_TYPES.items():
        if key not in slots:
            continue
        resolved[f"{key}_id"] = None
        candidates = repository.search_entities(slots[key], 20)
        linked = link(slots[key], candidates, entity_type)
        if linked:
            resolved[key] = linked.canonical_name
            resolved[f"{key}_id"] = linked.entity_id
            evidence.append({"slot": key, "input": slots[key], "entity_id": linked.entity_id,
                             "canonical_name": linked.canonical_name, "entity_type": linked.entity_type,
                             "confidence": linked.confidence})
    return resolved, evidence
