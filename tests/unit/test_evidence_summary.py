import json

from experiments.reporting import build_evidence_summary


def test_builds_tables_and_chart(tmp_path, monkeypatch):
    results = tmp_path / "results"
    for directory in ("evaluation", "semantic", "quality", "benchmarks"):
        (results / directory).mkdir(parents=True)
    (results / "evaluation/entity_resolution.json").write_text(json.dumps({"precision": 1, "recall": .9, "f1": .947, "cases": 10}))
    (results / "evaluation/reasoning.json").write_text(json.dumps({"precision": .8, "reviewed_facts": 5}))
    (results / "evaluation/recommendation.json").write_text(json.dumps({"result": {"precision_at_k": .7, "ndcg_at_k": .75, "cases": 4}}))
    (results / "evaluation/qa_neo4j.json").write_text(json.dumps({"accuracy": 1, "cases": 20}))
    (results / "semantic/semantic_reasoning.json").write_text(json.dumps({
        "triples_before": 100, "validation": {"conforms": True}}))
    (results / "quality/neo4j_validation.json").write_text(json.dumps({"valid": True, "nodes": 50}))
    header = "backend,movie_count,intent,iterations,median_ms,p95_ms,stdev_ms\n"
    (results / "benchmarks/neo4j_benchmark.csv").write_text(
        header + "neo4j,10,movies_by_director,100,2.0,3.0,0.2\n")
    (results / "benchmarks/relational_benchmark.csv").write_text(
        "backend,intent,iterations,median_ms,p95_ms,stdev_ms\n"
        "sqlite,movies_by_director,100,1.0,1.5,0.1\n")
    monkeypatch.setattr(build_evidence_summary, "RESULTS", results)
    output = tmp_path / "summary"
    build_evidence_summary.build(output)
    assert "ER precision" in (output / "quality_metrics.svg").read_text()
    assert (output / "quality_metrics.csv").is_file()
    assert (output / "benchmark_comparison.svg").is_file()
