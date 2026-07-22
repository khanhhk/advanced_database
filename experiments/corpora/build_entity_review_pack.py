"""Create a blind, human-reviewable entity-resolution labeling pack."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


RUBRIC = (
    "Chọn đúng một candidate nếu mention và candidate là cùng thực thể; chọn no_match "
    "nếu không có candidate phù hợp; chọn abstain nếu bằng chứng không đủ. Không xem silver label khi gán nhãn."
)


def build(source: Path, destination: Path) -> dict:
    cases = json.loads(source.read_text(encoding="utf-8"))
    pack = {
        "schema_version": "1.0",
        "generated_by": "experiments.corpora.build_entity_review_pack",
        "source_file": str(source),
        "rubric": RUBRIC,
        "status": "pending-human-review",
        "cases": [],
    }
    for case in cases:
        pack["cases"].append({
            "case_id": case["case_id"],
            "left": case["left"],
            "candidates": case["candidates"],
            "threshold": case.get("threshold", 90),
            "human_review": {
                "reviewer_id": "",
                "reviewed_at": "",
                "decision": "",
                "expected_id": "",
                "confidence": "",
                "adjudication_note": "",
                "rubric_version": "1.0",
            },
        })
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"cases": len(pack["cases"]), "output": str(destination), "status": pack["status"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path,
                        default=Path("experiments/corpora/silver/entity_resolution.json"))
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/corpora/human_review/entity_resolution.json"))
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.output), ensure_ascii=False, indent=2))
