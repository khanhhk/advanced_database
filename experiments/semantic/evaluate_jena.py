"""Run the SPARQL catalog against a real Apache Jena Fuseki inference model."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import httpx
from rdflib import Graph

from src.kg.sparql_catalog import load_catalog


BINDINGS = """VALUES (?name ?movieTitle ?movieId ?wantedGenre) {
  (\"Christopher Nolan\" \"Inception\" 27205 \"Science Fiction\")
}
"""


def _bounded(query: str) -> str:
    where = query.find("WHERE")
    opening = query.find("{", where if where >= 0 else 0)
    bound = query[:opening + 1] + "\n" + BINDINGS + query[opening + 1:]
    return bound if "ASK WHERE" in bound else bound + "\nLIMIT 5"


def _query(client: httpx.Client, endpoint: str, query: str) -> httpx.Response:
    response = client.post(endpoint, data={"query": query},
                           headers={"Accept": "application/sparql-results+json, text/turtle;q=0.8"})
    response.raise_for_status()
    return response


def _wait(client: httpx.Client, base_url: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        try:
            response = client.get(base_url.rstrip("/") + "/$/ping")
            if response.is_success:
                return
        except httpx.HTTPError as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"Fuseki did not become ready within {timeout}s: {last_error}")


def evaluate(base_url: str, ontology: Path, data: Path, timeout: float = 120) -> dict:
    endpoint = base_url.rstrip("/") + "/movies/sparql"
    asserted = Graph(); asserted.parse(ontology); asserted.parse(data)
    with httpx.Client(timeout=timeout) as client:
        _wait(client, base_url, timeout)
        count_response = _query(client, endpoint,
            "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }")
        inferred_total = int(count_response.json()["results"]["bindings"][0]["count"]["value"])
        inverse_response = _query(client, endpoint,
            "PREFIX : <https://example.org/movie-kg/> "
            "SELECT (COUNT(*) AS ?count) WHERE { ?movie :hasActor ?actor }")
        inverse_count = int(inverse_response.json()["results"]["bindings"][0]["count"]["value"])
        queries = []
        for query_id, query in load_catalog():
            started = time.perf_counter()
            response = _query(client, endpoint, _bounded(query))
            content_type = response.headers.get("content-type", "")
            if "json" in content_type:
                body = response.json()
                result_count = (int(bool(body.get("boolean"))) if "boolean" in body
                                else len(body.get("results", {}).get("bindings", [])))
                result_type = "ASK" if "boolean" in body else "SELECT"
            else:
                graph = Graph(); graph.parse(data=response.text, format="turtle")
                result_count, result_type = len(graph), "CONSTRUCT"
            queries.append({"query_id": query_id, "status": "ok", "result_type": result_type,
                            "result_count_capped": result_count,
                            "latency_ms": round((time.perf_counter() - started) * 1000, 3)})
    return {
        "engine": "Apache Jena Fuseki", "jena_version": "6.1.0",
        "reasoner": "GenericRuleReasoner/forward", "endpoint": endpoint,
        "asserted_union_triples": len(asserted), "inference_model_triples": inferred_total,
        "additional_visible_triples": inferred_total - len(asserted),
        "inverse_hasActor_triples": inverse_count,
        "queries": queries, "queries_executed": len(queries),
        "all_queries_ok": len(queries) == 10 and all(row["status"] == "ok" for row in queries),
        "interpretation_limit": "Declared RDFS/OWL rule subset on Jena; not a full OWL 2 DL completeness claim.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:3030")
    parser.add_argument("--ontology", type=Path, default=Path("ontology/movie_ontology.ttl"))
    parser.add_argument("--data", type=Path, default=Path("data/processed/movies.ttl"))
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/results/semantic/jena_semantic_evaluation.json"))
    parser.add_argument("--timeout", type=float, default=120)
    args = parser.parse_args()
    result = evaluate(args.base_url, args.ontology, args.data, args.timeout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
