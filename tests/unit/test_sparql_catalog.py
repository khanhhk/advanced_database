from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF

from src.kg.semantic_reasoning import materialize
from src.kg.sparql_catalog import execute_catalog, load_catalog

NS = Namespace("https://example.org/movie-kg/")


def test_all_ten_sparql_queries_parse_and_execute():
    data = Graph()
    data.add((NS.nolan, NS.name, Literal("Christopher Nolan")))
    data.add((NS.nolan, NS.directed, NS.inception))
    data.add((NS.leonardo, NS.name, Literal("Leonardo DiCaprio")))
    data.add((NS.leonardo, NS.actedIn, NS.inception))
    data.add((NS.inception, RDF.type, NS.Movie))
    data.add((NS.inception, NS.tmdbId, Literal(27205)))
    data.add((NS.inception, NS.title, Literal("Inception")))
    data.add((NS.inception, NS.rating, Literal(8.8)))
    data.add((NS.inception, NS.hasGenre, NS.scifi))
    data.add((NS.scifi, NS.name, Literal("Science Fiction")))
    ontology = Graph()
    ontology.parse(Path("ontology/movie_ontology.ttl"))
    materialize(data, ontology)
    report = execute_catalog(
        data,
        {
            "name": Literal("Christopher Nolan"),
            "movieTitle": Literal("Inception"),
            "movieId": Literal(27205),
            "wantedGenre": Literal("Science Fiction"),
        },
    )
    assert len(load_catalog()) == 10
    assert len(report) == 10
    assert next(row for row in report if row["query_id"] == "Q7")["result_count"] > 0
