import json

from experiments.validate_human_review import validate


def test_human_review_gate_requires_independent_complete_metadata(tmp_path):
    path = tmp_path / "labels.json"
    path.write_text(json.dumps([{"case_id": "x", "generated_by": "generator",
        "human_review": {"reviewer_id": "reviewer", "reviewed_at": "2026-07-15",
                         "decision": "accepted", "rubric_version": "1.0"}}]))
    assert validate([path])["conforms"]
    path.write_text(json.dumps([{"case_id": "x", "generated_by": "same",
        "human_review": {"reviewer_id": "same"}}]))
    assert not validate([path])["conforms"]
