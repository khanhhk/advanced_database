"""Compare Neo4j recommendation baselines with the hybrid ranker."""
import argparse
import json
import math
from pathlib import Path
from src.config import get_settings
from src.kg.repository import Neo4jRepository


def metrics(repo,cases,method,k):
    values=[]
    for case in cases:
        ids=[x.movie_id for x in repo.recommend(case["movie_id"],k,method)]; rel=set(case["relevant_movie_ids"])
        hits=[x in rel for x in ids]; dcg=sum(h/math.log2(i+2) for i,h in enumerate(hits)); ideal=sum(1/math.log2(i+2) for i in range(min(len(rel),k)))
        values.append((sum(hits)/k,dcg/ideal if ideal else 0))
    return {"method":method,"cases":len(cases),"k":k,"precision_at_k":sum(x[0] for x in values)/len(values),"ndcg_at_k":sum(x[1] for x in values)/len(values)}

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--labels",type=Path,default=Path("experiments/labels/recommendation.json")); p.add_argument("--output",type=Path,default=Path("experiments/results/recommendation_ablation.json")); p.add_argument("--k",type=int,default=10); a=p.parse_args()
    cases=json.loads(a.labels.read_text()); s=get_settings(); repo=Neo4jRepository(s.neo4j_uri,s.neo4j_user,s.neo4j_password,s.neo4j_database)
    try: result={"backend":"neo4j","results":[metrics(repo,cases,m,a.k) for m in ("overlap","weighted_jaccard","hybrid")]}
    finally: repo.close()
    a.output.write_text(json.dumps(result,indent=2),encoding="utf-8"); print(json.dumps(result,indent=2))
