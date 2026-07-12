"""Graph-native QA using a fixed catalog of parameterized Cypher queries."""

from src.kg.query_catalog import QUERIES
from src.qa.intents import detect_intent


def answer(question: str, repository) -> tuple[str, str, list[dict]]:
    intent, slots = detect_intent(question)
    if intent == "unknown":
        return "Xin lỗi, tôi chưa hiểu câu hỏi. Hãy hỏi theo đạo diễn, diễn viên, thể loại, đường liên hệ hoặc phim tương tự.", intent, []
    if intent == "similar_movies":
        rows = repository.run(QUERIES["resolve_movie"], movie=slots["movie"])
        if not rows:
            return "Không tìm thấy phim.", intent, []
        items = repository.recommend(rows[0]["movie_id"], 5, "weighted_jaccard")
        return "Phim tương tự: " + ", ".join(x.title for x in items), intent, [x.model_dump() for x in items]

    params = {key: (float(value) if key == "rating" else value) for key, value in slots.items()}
    rows = repository.run(QUERIES[intent], **params)
    evidence = [_serializable(row) for row in rows]
    if intent in {"movies_by_director", "common_movies", "movies_by_genre_rating"}:
        return _list("Các phim tìm thấy" if intent == "movies_by_director" else "Phim đóng chung" if intent == "common_movies" else "Các phim phù hợp", rows, "title"), intent, evidence
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
