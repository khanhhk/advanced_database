"""Evaluate entity resolution against a completed independent review pack."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.processing.entity_resolution import resolve_entity


def evaluate(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    cases = document["cases"]
    tp = fp = fn = tn = abstained = 0
    errors = []
    for case in cases:
        review = case["human_review"]
        decision = review.get("decision")
        if decision == "abstain":
            abstained += 1
            continue
        actual = decision == "match"
        expected_id = review.get("expected_id") or None
        match = resolve_entity(case["left"], case["candidates"], case.get("threshold", 90))
        predicted = bool(match)
        correct_target = not predicted or not expected_id or match.right_id == expected_id
        tp += bool(predicted and actual and correct_target)
        fp += bool(predicted and (not actual or not correct_target))
        fn += bool(actual and (not predicted or not correct_target))
        tn += bool(not predicted and not actual)
        if (predicted != actual) or (predicted and not correct_target):
            errors.append({"case_id": case["case_id"], "decision": decision,
                           "expected_id": expected_id,
                           "predicted_id": match.right_id if match else None,
                           "method": match.method if match else None})
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"evidence_class": "independent-human-review", "cases": len(cases),
            "evaluated_cases": len(cases) - abstained, "abstained": abstained,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision,
            "recall": recall,
            "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
            "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/results/evaluation/entity_resolution_human.json"))
    args = parser.parse_args()
    result = evaluate(args.dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
