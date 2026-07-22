"""Measure precision of derived co-star facts against reviewed labels."""
import argparse
import json
from pathlib import Path


def evaluate(cases: list[dict]) -> dict:
    reviewed = [case for case in cases if case.get("valid") is not None]
    correct = sum(bool(case["valid"]) for case in reviewed)
    return {"reviewed_facts": len(reviewed), "correct_facts": correct,
            "precision": correct / len(reviewed) if reviewed else 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("labels", type=Path, help="JSON co-star facts with a reviewed valid boolean")
    args = parser.parse_args()
    print(json.dumps(evaluate(json.loads(args.labels.read_text())), indent=2))
