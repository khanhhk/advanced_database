"""Deterministic RDFS/OWL-RL subset materializer and semantic validator."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, OWL, RDF, RDFS


def materialize(data: Graph, ontology: Graph) -> dict:
    """Apply declared domain/range, inverse and symmetric-property rules."""
    before = len(data)
    inferred: set[tuple] = set()
    domains = dict(ontology.subject_objects(RDFS.domain))
    ranges = dict(ontology.subject_objects(RDFS.range))
    inverses = list(ontology.subject_objects(OWL.inverseOf))
    symmetric = set(ontology.subjects(RDF.type, OWL.SymmetricProperty))

    for subject, predicate, obj in list(data):
        if predicate in domains:
            inferred.add((subject, RDF.type, domains[predicate]))
        if predicate in ranges and not str(ranges[predicate]).startswith(
            "http://www.w3.org/2001/XMLSchema"
        ):
            inferred.add((obj, RDF.type, ranges[predicate]))
        for forward, inverse in inverses:
            if predicate == forward:
                inferred.add((obj, inverse, subject))
            elif predicate == inverse:
                inferred.add((obj, forward, subject))
        if predicate in symmetric:
            inferred.add((obj, predicate, subject))

    for triple in inferred:
        data.add(triple)
    return {
        "triples_before": before,
        "triples_after": len(data),
        "inferred_triples": len(data) - before,
    }


def validate(data: Graph, ontology: Graph) -> dict:
    """Check functional properties, disjoint classes and required Movie titles."""
    violations: list[dict] = []
    for prop in ontology.subjects(RDF.type, OWL.FunctionalProperty):
        values: dict = defaultdict(set)
        for subject, obj in data.subject_objects(prop):
            values[subject].add(obj)
        for subject, objects in values.items():
            if len(objects) > 1:
                violations.append(
                    {
                        "type": "functional_property",
                        "subject": str(subject),
                        "property": str(prop),
                        "value_count": len(objects),
                    }
                )

    for subject in set(data.subjects(RDF.type, None)):
        types = set(data.objects(subject, RDF.type))
        for left, right in ontology.subject_objects(OWL.disjointWith):
            if left in types and right in types:
                violations.append(
                    {
                        "type": "disjoint_classes",
                        "subject": str(subject),
                        "classes": [str(left), str(right)],
                    }
                )

    movie_types = [
        item for item in ontology.subjects(RDF.type, OWL.Class)
        if str(item).endswith("/Movie")
    ]
    title_props = [
        item for item in ontology.subjects(RDF.type, OWL.DatatypeProperty)
        if str(item).endswith("/title")
    ]
    if movie_types and title_props:
        for subject in data.subjects(RDF.type, movie_types[0]):
            if not any(str(value).strip() for value in data.objects(subject, title_props[0])):
                violations.append({"type": "required_movie_title", "subject": str(subject)})

    return {
        "conforms": not violations,
        "violation_count": len(violations),
        "violations": violations,
    }


def run(
    ontology_path: Path,
    input_path: Path,
    output_path: Path,
    report_path: Path,
) -> dict:
    ontology, data = Graph(), Graph()
    ontology.parse(ontology_path)
    data.parse(input_path)
    report = {
        "profile": "declared-rdfs-owl-rl-subset",
        **materialize(data, ontology),
        "validation": validate(data, ontology),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data.serialize(output_path, format="turtle")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ontology", type=Path, default=Path("ontology/movie_ontology.ttl"))
    parser.add_argument("--input", type=Path, default=Path("data/processed/movies.ttl"))
    parser.add_argument(
        "--output", type=Path, default=Path("data/processed/movies.inferred.ttl")
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("experiments/results/semantic/semantic_reasoning.json"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.ontology, args.input, args.output, args.report), indent=2))
