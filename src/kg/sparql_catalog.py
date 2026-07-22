"""Load, parse and execute the repository's numbered SPARQL catalog."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from rdflib import Graph, Literal
from rdflib.plugins.sparql.parser import parseQuery

PREFIXES = """PREFIX : <https://example.org/movie-kg/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"""


def load_catalog(path: Path = Path("sparql/queries.rq")) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"(?m)^# Q(?=\d+\.)", text)
    result = []
    for section in sections[1:]:
        number, body = section.split(".", 1)
        query = re.sub(r"^.*\n", "", body, count=1).strip()
        full = PREFIXES + query
        parseQuery(full)
        result.append((f"Q{number.strip()}", full))
    if len(result) != 10:
        raise ValueError(f"Expected 10 numbered SPARQL queries, found {len(result)}")
    return result


def execute_catalog(graph: Graph, bindings: dict | None = None) -> list[dict]:
    report = []
    for query_id, query in load_catalog():
        result = graph.query(query, initBindings=bindings or {})
        if result.type == "ASK":
            count = int(bool(result.askAnswer))
        elif result.type in {"CONSTRUCT", "DESCRIBE"}:
            count = len(result.graph)
        else:
            count = len(list(result))
        report.append({"query_id": query_id, "result_type": result.type, "result_count": count})
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/processed/movies.inferred.ttl"))
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/results/semantic/sparql_execution.json"))
    args = parser.parse_args(); graph = Graph(); graph.parse(args.input)
    report = execute_catalog(graph, {
        "name": Literal("Christopher Nolan"), "movieTitle": Literal("Inception"),
        "movieId": Literal(27205), "wantedGenre": Literal("Science Fiction")})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
