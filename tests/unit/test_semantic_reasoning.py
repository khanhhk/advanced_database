from rdflib import Graph, Namespace, RDF

from src.kg.semantic_reasoning import materialize, validate

NS = Namespace("https://example.org/movie-kg/")


def ontology() -> Graph:
    graph = Graph()
    graph.parse("ontology/movie_ontology.ttl")
    return graph


def test_materializes_inverse_domain_and_range():
    data = Graph()
    data.add((NS.alice, NS.actedIn, NS.movie1))
    result = materialize(data, ontology())
    assert (NS.movie1, NS.hasActor, NS.alice) in data
    assert (NS.alice, RDF.type, NS.Person) in data
    assert (NS.movie1, RDF.type, NS.Movie) in data
    assert result["inferred_triples"] >= 3


def test_materializes_symmetric_property():
    data = Graph()
    data.add((NS.alice, NS.coStarredWith, NS.bob))
    materialize(data, ontology())
    assert (NS.bob, NS.coStarredWith, NS.alice) in data


def test_detects_functional_and_disjoint_violations():
    data = Graph()
    data.add((NS.movie1, RDF.type, NS.Movie))
    data.add((NS.movie1, RDF.type, NS.Person))
    data.add((NS.movie1, NS.title, NS.title1))
    data.add((NS.movie1, NS.tmdbId, NS.id1))
    data.add((NS.movie1, NS.tmdbId, NS.id2))
    report = validate(data, ontology())
    kinds = {item["type"] for item in report["violations"]}
    assert {"functional_property", "disjoint_classes"} <= kinds
