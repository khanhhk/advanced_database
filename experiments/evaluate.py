from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.kg.repository import MemoryRepository


def evaluate(input_path: Path, questions: Path) -> dict:
    repository = MemoryRepository(input_path)
    cases = json.loads(questions.read_text(encoding="utf-8")); details = []
    for case in cases:
        text, intent, evidence = repository.answer(case["question"])
        expected = case.get("contains_any", [case.get("contains")])
        content_ok = any(value and value.casefold() in text.casefold() for value in expected)
        evidence_ok = len(evidence) >= case.get("min_evidence", 1)
        passed = intent == case["intent"] and content_ok and evidence_ok
        details.append({**case, "actual_intent": intent, "answer": text, "evidence_count": len(evidence), "passed": passed})
    passed = sum(x["passed"] for x in details)
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "backend": "memory",
            "dataset_movie_count": repository.stats()["nodes"]["Movie"], "cases": len(cases), "passed": passed,
            "accuracy": passed / len(cases) if cases else 0,
            "limitations": "Deterministic 20-question smoke corpus with graph evidence; not independent human-reviewed gold QA.", "details": details}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--input", type=Path, default=Path("data/raw/tmdb_movies.json"))
    parser.add_argument("--questions", type=Path, default=Path("experiments/labels/qa.json"))
    parser.add_argument("--output", type=Path, default=Path("experiments/results/qa.json")); args = parser.parse_args()
    result = evaluate(args.input, args.questions); args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"); print(json.dumps(result, ensure_ascii=False, indent=2))
