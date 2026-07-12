import json
from pathlib import Path

from src.qa.intents import detect_intent
from src.qa.service import answer
from src.recommendation.service import recommend


MOVIES = json.loads(Path("data/samples/movies.json").read_text())["movies"]


def test_director_qa():
    intent, slots = detect_intent("Những phim nào do Christopher Nolan đạo diễn?")
    assert intent == "movies_by_director"
    text, _, evidence = answer("Những phim nào do Christopher Nolan đạo diễn?", MOVIES)
    assert "Inception" in text and len(evidence) == 4


def test_recommendation_explains_score():
    results = recommend(MOVIES, 27205, 2)
    assert results[0].score > 0
    assert results[0].explanation.startswith("Tương đồng qua")
    assert any("Christopher Nolan" in r.shared_directors for r in results)

