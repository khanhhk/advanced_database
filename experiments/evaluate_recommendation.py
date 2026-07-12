"""Evaluate recommendations against a human-labeled relevance corpus."""
import argparse
import json
import math
from pathlib import Path

from src.kg.repository import MemoryRepository


def evaluate(repository, cases: list[dict], k: int = 10) -> dict:
    details = []
    for case in cases:
        relevant = set(case["relevant_movie_ids"])
        predicted = repository.recommend(case["movie_id"], k)
        ids = [item.movie_id for item in predicted]
        hits = [movie_id in relevant for movie_id in ids]
        dcg = sum(hit / math.log2(index + 2) for index, hit in enumerate(hits))
        ideal = sum(1 / math.log2(index + 2) for index in range(min(len(relevant), k)))
        details.append({"movie_id": case["movie_id"], "predicted": ids,
                        "precision_at_k": sum(hits) / k, "ndcg_at_k": dcg / ideal if ideal else 0,
                        "explanation_coverage": sum(bool(x.explanation) for x in predicted) / len(predicted) if predicted else 0})
    mean = lambda key: sum(x[key] for x in details) / len(details) if details else 0
    return {"cases": len(details), "k": k, "precision_at_k": mean("precision_at_k"),
            "ndcg_at_k": mean("ndcg_at_k"), "explanation_coverage": mean("explanation_coverage"),
            "details": details}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("labels", type=Path, help="JSON cases with movie_id and relevant_movie_ids")
    parser.add_argument("--input", type=Path, default=Path("tests/fixtures/movies.json"))
    parser.add_argument("--k", type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(evaluate(MemoryRepository(args.input), json.loads(args.labels.read_text()), args.k), indent=2))
