"""Evaluate the production IDF-weighted recommender on Neo4j."""
import argparse, json, math
from pathlib import Path
from src.config import get_settings
from src.kg.repository import Neo4jRepository


def metrics(repo, cases, k):
    values = []
    for case in cases:
        ids = [x.movie_id for x in repo.recommend(case["movie_id"], k)]
        relevant = set(case["relevant_movie_ids"])
        precision = sum(x in relevant for x in ids) / k
        dcg = sum((1 / math.log2(i + 2)) for i, x in enumerate(ids) if x in relevant)
        ideal = sum(1 / math.log2(i + 2) for i in range(min(len(relevant), k)))
        values.append((precision, dcg / ideal if ideal else 0.0))
    return {"method": "idf_weighted_graph", "cases": len(cases), "k": k,
            "precision_at_k": sum(x[0] for x in values) / len(values),
            "ndcg_at_k": sum(x[1] for x in values) / len(values)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=10)
    args = parser.parse_args()
    cases = json.loads(Path("experiments/labels/recommendation.json").read_text())
    settings = get_settings()
    repo = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password, settings.neo4j_database)
    try:
        result = {"backend": "neo4j", "result": metrics(repo, cases, args.k)}
    finally:
        repo.close()
    Path("experiments/results/recommendation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
