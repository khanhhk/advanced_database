from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.processing.entity_resolution import resolve_entity


def evaluate(path: Path) -> dict:
    cases = json.loads(path.read_text(encoding="utf-8")); tp = fp = fn = tn = 0
    for case in cases:
        match = resolve_entity(case["left"], case["candidates"], case.get("threshold", 90))
        predicted = bool(match); actual = case["is_match"]
        tp += predicted and actual; fp += predicted and not actual; fn += not predicted and actual; tn += not predicted and not actual
    precision = tp / (tp + fp) if tp + fp else 0; recall = tp / (tp + fn) if tp + fn else 0
    return {"cases": len(cases), "tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision,
            "recall": recall, "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("dataset", type=Path); args = parser.parse_args()
    print(json.dumps(evaluate(args.dataset), indent=2))

