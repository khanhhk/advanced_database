"""Evaluate the fixed QA corpus against the production Neo4j execution path."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import get_settings
from src.kg.repository import Neo4jRepository


def case_passes(case: dict, text: str, intent: str, evidence: list[dict]) -> bool:
    expected = case.get("contains_any", [case.get("contains")])
    content_ok = any(value and value.casefold() in text.casefold() for value in expected)
    excluded_ok = all(value.casefold() not in text.casefold()
                      for value in case.get("excludes", []))
    evidence_ok = len(evidence) >= case.get("min_evidence", 1)
    return intent == case["intent"] and content_ok and excluded_ok and evidence_ok


def evaluate(questions: Path) -> dict:
    settings = get_settings()
    repository = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user,
                                 settings.neo4j_password, settings.neo4j_database)
    cases = json.loads(questions.read_text(encoding="utf-8"))
    details = []
    try:
        movie_count = repository.stats()["nodes"].get("Movie", 0)
        for case in cases:
            text, intent, evidence = repository.answer(case["question"])
            passed = case_passes(case, text, intent, evidence)
            details.append({**case, "actual_intent": intent, "answer": text,
                            "evidence_count": len(evidence), "passed": passed})
    finally:
        repository.close()
    passed = sum(item["passed"] for item in details)
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "backend": "neo4j",
            "dataset_movie_count": movie_count, "cases": len(cases), "passed": passed,
            "accuracy": passed / len(cases) if cases else 0,
            "limitations": "Deterministic evidence-backed smoke corpus; not independent human-reviewed gold QA.",
            "details": details}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path,
                        default=Path("experiments/corpora/silver/qa.json"))
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/results/evaluation/qa_neo4j.json"))
    args = parser.parse_args()
    result = evaluate(args.questions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("backend", "dataset_movie_count", "cases", "passed", "accuracy")}, indent=2))
