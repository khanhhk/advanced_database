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
        graph.add((m, NS.tmdbId, Literal(movie["tmdb_id"])))
        if movie.get("imdb_id"): graph.add((m, NS.imdbId, Literal(movie["imdb_id"])))
        if movie.get("rating") is not None: graph.add((m, NS.rating, Literal(movie["rating"])))
        if movie.get("imdb_rating") is not None: graph.add((m, NS.imdbRating, Literal(movie["imdb_rating"])))
        if movie.get("imdb_votes") is not None: graph.add((m, NS.imdbVotes, Literal(movie["imdb_votes"])))
        for relation, values, target_type in (("directed", movie["directors"], "Person"),
                                               ("actedIn", movie["actors"], "Person")):
            for value in values:
                item = value if isinstance(value, dict) else {"name": value}
                identifier = f"tmdb-{item['tmdb_id']}" if item.get("tmdb_id") else item["name"].replace(" ", "_")
                person = URIRef(NS["person/" + identifier])
                graph.add((person, RDF.type, NS[target_type])); graph.add((person, NS.name, Literal(item["name"])))
                graph.add((person, NS[relation], m))
        for relation, key, cls in (("hasGenre", "genres", "Genre"), ("hasKeyword", "keywords", "Keyword"), ("producedBy", "studios", "Studio")):
            for value in movie[key]:
                item = value if isinstance(value, dict) else {"name": value}
                source_key = {"Genre": "genre_id", "Keyword": "keyword_id", "Studio": "company_id"}[cls]
                identifier = f"tmdb-{item[source_key]}" if item.get(source_key) else item["name"].replace(" ", "_")
                node = URIRef(NS[f"{cls.lower()}/{identifier}"])
                graph.add((node, RDF.type, NS[cls])); graph.add((node, NS.name, Literal(item["name"])))
                graph.add((m, NS[relation], node))
    destination.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=destination, format="turtle")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/raw/tmdb_movies.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/movies.ttl"))
    args = parser.parse_args(); export(args.input, args.output)
