import re
import unicodedata


def _fold(value: str) -> str:
    value = "".join(c for c in unicodedata.normalize("NFKD", value.casefold()) if not unicodedata.combining(c))
    return " ".join(value.replace("đ", "d").split())


PATTERNS = [
    ("common_movies", r"phim chung(?: cua)?\s+(?P<person1>.+?)\s+(?:va|voi)\s+(?P<person2>.+?)(?:\?|$)"),
    ("movies_by_director", r"(?:phim.*?\s+do\s+)(?P<director>.+?)(?:\s+dao dien|\?|$)"),
    ("actors_in_movie", r"(?:dien vien.*phim|ai.*(?:dong|tham gia).*phim)\s+(?P<movie>.+?)(?:\?|$)"),
    ("movies_by_genre_rating", r"phim\s+(?P<genre>\S+).*rating\s*(?:tren|>|hon)\s*(?P<rating>[0-9.]+)"),
    ("co_stars", r"(?:ai|dien vien nao).*?dong chung voi\s+(?P<person>.+?)(?:\?|$)"),
    ("directors_by_genre", r"dao dien nao.*?(?:the loai)\s+(?P<genre>.+?)(?:\?|$)"),
    ("shortest_path", r"(?:duong|lien he).*?(?:giua|tu)\s+(?P<person1>.+?)\s+(?:va|den)\s+(?P<person2>.+?)(?:\?|$)"),
    ("similar_movies", r"(?:phim.*(?:giong|tuong tu)|goi y.*(?:tu|cho))\s+(?P<movie>.+?)(?:\?|$)"),
]


def detect_intent(question: str) -> tuple[str, dict[str, str]]:
    normalized = _fold(question.strip())
    for intent, pattern in PATTERNS:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match: return intent, {k: v.strip(" .?") for k, v in match.groupdict().items()}
    return "unknown", {}
