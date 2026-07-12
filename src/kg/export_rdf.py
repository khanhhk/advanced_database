import argparse
import json
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef

NS = Namespace("https://example.org/movie-kg/")


def export(source: Path, destination: Path) -> None:
    graph = Graph()
    graph.bind("movie", NS)
    for movie in json.loads(source.read_text(encoding="utf-8"))["movies"]:
        m = URIRef(NS[f"movie/{movie['tmdb_id']}"])
        graph.add((m, RDF.type, NS.Movie)); graph.add((m, NS.title, Literal(movie["title"])))
        graph.add((m, NS.rating, Literal(movie["rating"])))
        for relation, values, target_type in (("directed", movie["directors"], "Person"),
                                               ("actedIn", movie["actors"], "Person")):
            for value in values:
                person = URIRef(NS["person/" + value.replace(" ", "_")])
                graph.add((person, RDF.type, NS[target_type])); graph.add((person, NS[relation], m))
        for relation, key, cls in (("hasGenre", "genres", "Genre"), ("hasKeyword", "keywords", "Keyword"), ("producedBy", "studios", "Studio")):
            for value in movie[key]:
                node = URIRef(NS[f"{cls.lower()}/{value.replace(' ', '_')}"])
                graph.add((node, RDF.type, NS[cls])); graph.add((m, NS[relation], node))
    destination.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=destination, format="turtle")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/samples/movies.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/movies.ttl"))
    args = parser.parse_args(); export(args.input, args.output)

