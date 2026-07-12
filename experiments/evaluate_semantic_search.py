"""Evaluate real Neo4j semantic retrieval on a reviewed/silver query corpus."""
import argparse
import json
from pathlib import Path

from src.config import get_settings
from src.kg.repository import Neo4jRepository


def evaluate(repository, cases, k=10):
    details = []
    for case in cases:
        results = repository.semantic_search(case["query"], k, case.get("genre"), case.get("min_rating"))
        ids, relevant = [x.movie_id for x in results], set(case["relevant_movie_ids"])
        ranks = [i + 1 for i, value in enumerate(ids) if value in relevant]
        details.append({"query": case["query"], "retrieved": ids, "hit": bool(ranks),
                        "reciprocal_rank": 1 / min(ranks) if ranks else 0})
    return {"backend": "neo4j-vector", "cases": len(cases), "k": k,
            "recall_at_k": sum(x["hit"] for x in details) / len(details),
            "mrr": sum(x["reciprocal_rank"] for x in details) / len(details), "details": details}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--labels", type=Path, default=Path("experiments/labels/semantic_search.json"))
    parser.add_argument("--output", type=Path, default=Path("experiments/results/semantic_search.json")); parser.add_argument("--k", type=int, default=10); args = parser.parse_args()
    s = get_settings(); repo = Neo4jRepository(s.neo4j_uri,s.neo4j_user,s.neo4j_password,s.neo4j_database)
    try: result = evaluate(repo,json.loads(args.labels.read_text()),args.k)
    finally: repo.close()
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8"); print(json.dumps({k:v for k,v in result.items() if k!='details'},indent=2))
