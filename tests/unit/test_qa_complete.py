import json
from pathlib import Path

from src.qa.service import answer


def test_question_dataset_reaches_required_accuracy():
    movies = json.loads(Path("data/samples/movies.json").read_text())["movies"]
    cases = json.loads(Path("tests/test_questions.json").read_text())
    correct = 0
    for case in cases:
        text, intent, evidence = answer(case["question"], movies)
        correct += intent == case["intent"] and case["contains"].casefold() in text.casefold() and bool(evidence)
    assert correct / len(cases) >= .8
