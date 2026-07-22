from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.processing.entity_resolution import resolve_entity


def evaluate(path: Path) -> dict:
    cases = json.loads(path.read_text(encoding="utf-8")); tp = fp = fn = tn = 0
    errors = []
    for case in cases:
        match = resolve_entity(case["left"], case["candidates"], case.get("threshold", 90))
        predicted = bool(match) and (not case.get("expected_id") or match.right_id == case["expected_id"]); actual = case["is_match"]
        tp += predicted and actual; fp += predicted and not actual; fn += not predicted and actual; tn += not predicted and not actual
        if predicted != actual:
            errors.append({"case_id": case["case_id"], "difficulty": case.get("difficulty"),
                           "expected_id": case.get("expected_id"),
                           "predicted_id": match.right_id if match else None,
                           "method": match.method if match else None,
                           "confidence": match.confidence if match else None})
    precision = tp / (tp + fp) if tp + fp else 0; recall = tp / (tp + fn) if tp + fn else 0
    return {"cases": len(cases), "tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision,
            "recall": recall, "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0,
            "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(); result = evaluate(args.dataset)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
