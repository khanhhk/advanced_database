import re
import unicodedata


GENRES = {
    "hanh dong": "Action", "action": "Action", "khoa hoc vien tuong": "Science Fiction",
    "vien tuong": "Science Fiction", "science fiction": "Science Fiction", "sci-fi": "Science Fiction",
    "hai": "Comedy", "comedy": "Comedy", "kinh di": "Horror", "horror": "Horror",
    "lang man": "Romance", "romance": "Romance", "hoat hinh": "Animation", "animation": "Animation",
    "toi pham": "Crime", "crime": "Crime", "bi an": "Mystery", "mystery": "Mystery",
    "chien tranh": "War", "war": "War", "tai lieu": "Documentary", "documentary": "Documentary",
    "phieu luu": "Adventure", "adventure": "Adventure", "chinh kich": "Drama", "drama": "Drama",
}

CONCEPTS = {"giac mo": "dream", "khong gian": "space", "ho den": "black hole", "du hanh": "travel",
            "nguoi may": "robot", "tuong lai": "future", "khung long": "dinosaur", "the gioi ao": "virtual world",
            "may moc": "machines", "sieu anh hung": "superhero", "nguoi nhen": "spider-man", "da vu tru": "multiverse",
            "nguoi ngoai hanh tinh": "alien", "san con nguoi": "hunts humans", "chien tranh giua cac vi sao": "star wars",
            "don rac": "garbage cleaning", "co doc": "lonely", "sao hoa": "Mars", "tham hiem": "exploration"}


def _fold(text: str) -> str:
    value = "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c))
    return value.replace("đ", "d")


def parse_filters(query: str) -> tuple[str | None, float | None]:
    folded = _fold(query)
    genre = next((canonical for token, canonical in sorted(GENRES.items(), key=lambda x: -len(x[0])) if token in folded), None)
    rating_match = re.search(r"(?:rating|diem|danh gia)\s*(?:tren|hon|>=?|tu)?\s*([0-9]+(?:\.[0-9]+)?)", folded)
    return genre, float(rating_match.group(1)) if rating_match else None


def expand_query(query: str) -> str:
    """Add a small auditable bilingual concept layer for an English overview corpus."""
    folded = _fold(query)
    additions = [english for vietnamese, english in CONCEPTS.items() if vietnamese in folded]
    return query + (". " + ", ".join(additions) if additions else "")
