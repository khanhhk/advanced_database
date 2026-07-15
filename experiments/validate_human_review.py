"""Enforce independent-review metadata before labels may be called human-reviewed."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(paths: list[Path]) -> dict:
    errors = []
    for path in paths:
        cases = json.loads(path.read_text(encoding="utf-8"))
        for index, case in enumerate(cases):
            prefix = f"{path}:{case.get('case_id', index)}"
            review = case.get("human_review")
            if not isinstance(review, dict):
                errors.append(f"{prefix}: missing human_review")
                continue
            for field in ("reviewer_id", "reviewed_at", "decision", "rubric_version"):
                if not review.get(field): errors.append(f"{prefix}: missing {field}")
            if review.get("reviewer_id") == case.get("generated_by"):
                errors.append(f"{prefix}: reviewer must be independent from generator")
            if review.get("decision") == "changed" and not review.get("adjudication_note"):
                errors.append(f"{prefix}: changed label requires adjudication_note")
    return {"conforms": not errors, "files": len(paths), "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(); report = validate(args.paths)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["conforms"] else 1)
