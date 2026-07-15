from pathlib import Path

from rdflib import Graph, Literal

from src.kg.export_rdf import export
from src.kg.semantic_reasoning import materialize
from src.kg.sparql_catalog import execute_catalog, load_catalog


def test_all_ten_sparql_queries_parse_and_execute(tmp_path):
    rdf = tmp_path / "movies.ttl"
    export(Path("tests/fixtures/movies.json"), rdf)
    data, ontology = Graph(), Graph(); data.parse(rdf); ontology.parse("ontology/movie_ontology.ttl")
    materialize(data, ontology)
    report = execute_catalog(data, {"name": Literal("Christopher Nolan"),
        "movieTitle": Literal("Inception"), "movieId": Literal(27205),
        "wantedGenre": Literal("Science Fiction")})
    assert len(load_catalog()) == 10 and len(report) == 10
    assert next(x for x in report if x["query_id"] == "Q7")["result_count"] > 0
