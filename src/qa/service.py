from .intents import detect_intent


def answer(question: str, movies: list[dict]) -> tuple[str, str, list[dict]]:
    movies = [_name_view(movie) for movie in movies]
    intent, slots = detect_intent(question)
    if intent == "movies_by_director":
        found = [m for m in movies if _has(m["directors"], slots["director"])]
        return _movies(found, "Các phim tìm thấy"), intent, _movie_evidence(found, "DIRECTED")
    if intent == "movies_by_person":
        found = [m for m in movies if _has(m["actors"], slots["person"]) or _has(m["directors"], slots["person"])]
        evidence = [{"movie_id": m["tmdb_id"], "title": m["title"],
                     "relationship": "ACTED_IN" if _has(m["actors"], slots["person"]) else "DIRECTED",
                     "source": "tmdb"} for m in found]
        return _movies(found, "Các phim có sự tham gia của người này"), intent, evidence
    if intent == "actors_in_movie":
        movie = _find_movie(movies, slots["movie"])
        evidence = [{"person": a, "movie_id": movie["tmdb_id"], "relationship": "ACTED_IN", "source": "tmdb"} for a in movie["actors"]] if movie else []
        return ("Các diễn viên: " + ", ".join(movie["actors"]) if movie else "Không tìm thấy phim."), intent, evidence
    if intent == "common_movies":
        found = [m for m in movies if _has(m["actors"], slots["person1"]) and _has(m["actors"], slots["person2"])]
        return _movies(found, "Phim đóng chung"), intent, _movie_evidence(found, "ACTED_IN")
    if intent == "movies_by_genre_rating":
        found = [m for m in movies if _has(m["genres"], slots["genre"]) and (m.get("rating") or 0) > float(slots["rating"])]
        return _movies(found, "Các phim phù hợp"), intent, [{"movie_id": m["tmdb_id"], "rating": m["rating"], "source": "tmdb"} for m in found]
    if intent == "co_stars":
        counts: dict[str, list[int]] = {}
        for movie in movies:
            if _has(movie["actors"], slots["person"]):
                for actor in movie["actors"]:
                    if slots["person"].casefold() not in actor.casefold(): counts.setdefault(actor, []).append(movie["tmdb_id"])
        ordered = sorted(counts.items(), key=lambda x: (-len(x[1]), x[0]))
        evidence = [{"person": name, "movie_count": len(ids), "evidence_movie_ids": ids, "derived": True} for name, ids in ordered]
        return ("Các bạn diễn: " + ", ".join(x[0] for x in ordered) if ordered else "Không tìm thấy kết quả."), intent, evidence
    if intent == "directors_by_genre":
        counts: dict[str, list[int]] = {}
        for movie in movies:
            if _has(movie["genres"], slots["genre"]):
                for director in movie["directors"]: counts.setdefault(director, []).append(movie["tmdb_id"])
        ordered = sorted(counts.items(), key=lambda x: (-len(x[1]), x[0]))
        evidence = [{"director": d, "movie_count": len(ids), "movie_ids": ids} for d, ids in ordered]
        return ("Các đạo diễn: " + ", ".join(d for d, _ in ordered) if ordered else "Không tìm thấy kết quả."), intent, evidence
    if intent == "shortest_path":
        return _shortest_path(movies, slots["person1"], slots["person2"]), intent, _path_evidence(movies, slots["person1"], slots["person2"])
    if intent == "similar_movies":
        movie = _find_movie(movies, slots["movie"])
        if not movie: return "Không tìm thấy phim.", intent, []
        from src.recommendation.service import recommend
        items = recommend(movies, movie["tmdb_id"], 5)
        return "Phim tương tự: " + ", ".join(x.title for x in items), intent, [x.model_dump() for x in items]
    return "Xin lỗi, tôi chưa hiểu câu hỏi. Hãy hỏi theo đạo diễn, diễn viên, thể loại, đường liên hệ hoặc phim tương tự.", intent, []


def _has(values, needle): return any(needle.casefold() in value.casefold() for value in values)
def _name_view(movie):
    result = dict(movie)
    for key in ("actors", "directors", "genres", "keywords", "studios"):
        result[key] = [value.get("name", "") if isinstance(value, dict) else value for value in movie.get(key, [])]
    return result
def _find_movie(movies, name): return next((m for m in movies if name.casefold() in m["title"].casefold()), None)
def _movies(items, prefix): return f"{prefix}: " + ", ".join(m["title"] for m in items) if items else "Không tìm thấy kết quả."
def _movie_evidence(items, relation): return [{"movie_id": m["tmdb_id"], "title": m["title"], "relationship": relation, "source": "tmdb"} for m in items]


def _path_evidence(movies, source, target):
    # Person -> Movie -> Person breadth-first search with explicit evidence.
    # Keep the bipartite structure instead of expanding every cast into an O(c²)
    # person clique. This matters for the documented 5,000-movie smoke scale.
    person_movies: dict[str, list[dict]] = {}
    for m in movies:
        people = list(dict.fromkeys(m["actors"] + m["directors"]))
        movie = {"tmdb_id": m["tmdb_id"], "title": m["title"], "people": people}
        for person in people:
            person_movies.setdefault(person, []).append(movie)
    start = next((p for p in person_movies if source.casefold() in p.casefold()), None)
    goal = next((p for p in person_movies if target.casefold() in p.casefold()), None)
    if not start or not goal: return []
    queue = [(start, [])]; visited_people = {start}; visited_movies = set()
    for node, path in queue:
        if node == goal: return path
        for movie in person_movies.get(node, []):
            if movie["tmdb_id"] in visited_movies:
                continue
            visited_movies.add(movie["tmdb_id"])
            for neighbor in movie["people"]:
                if neighbor not in visited_people:
                    visited_people.add(neighbor)
                    edge = {"from": node, "movie_id": movie["tmdb_id"],
                            "movie": movie["title"], "to": neighbor}
                    queue.append((neighbor, path + [edge]))
    return []


def _shortest_path(movies, source, target):
    path = _path_evidence(movies, source, target)
    return "Đường liên hệ: " + " → ".join([path[0]["from"]] + [f'{e["movie"]} → {e["to"]}' for e in path]) if path else "Không tìm thấy đường liên hệ."
