import argparse
import csv
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


def export_processed(processed_dir: Path, destination: Path) -> None:
    """Export the exact normalized snapshot used by Neo4j, not the raw API list."""
    graph = Graph(); graph.bind("movie", NS)

    def rows(name: str) -> list[dict]:
        with (processed_dir / f"{name}.csv").open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    movies = {row["tmdb_id"]: URIRef(NS[f"movie/{row['tmdb_id']}"]) for row in rows("movies")}
    for row in rows("movies"):
        node = movies[row["tmdb_id"]]
        graph.add((node, RDF.type, NS.Movie)); graph.add((node, NS.title, Literal(row["title"])))
        graph.add((node, NS.tmdbId, Literal(int(row["tmdb_id"]))))
        for field, predicate, cast in (("imdb_id", "imdbId", str), ("rating", "rating", float),
                                       ("imdb_rating", "imdbRating", float), ("imdb_votes", "imdbVotes", int)):
            if row.get(field) not in (None, ""):
                graph.add((node, NS[predicate], Literal(cast(row[field]))))

    entity_specs = {
        "people": ("person_id", "Person", "person"), "genres": ("genre_id", "Genre", "genre"),
        "keywords": ("keyword_id", "Keyword", "keyword"), "studios": ("company_id", "Studio", "studio"),
    }
    entities: dict[str, dict[str, URIRef]] = {}
    for name, (key, cls, uri_part) in entity_specs.items():
        entities[name] = {}
        for row in rows(name):
            node = URIRef(NS[f"{uri_part}/{row[key]}"]); entities[name][row[key]] = node
            graph.add((node, RDF.type, NS[cls])); graph.add((node, NS.name, Literal(row["name"])))

    edge_specs = {
        "acted_in": ("people", "person_id", "actedIn", True),
        "directed": ("people", "person_id", "directed", True),
        "has_genre": ("genres", "genre_id", "hasGenre", False),
        "has_keyword": ("keywords", "keyword_id", "hasKeyword", False),
        "produced_by": ("studios", "company_id", "producedBy", False),
    }
    for name, (entity_name, entity_key, predicate, entity_first) in edge_specs.items():
        for row in rows(name):
            movie, entity = movies[row["tmdb_id"]], entities[entity_name][row[entity_key]]
            graph.add((entity, NS[predicate], movie) if entity_first else (movie, NS[predicate], entity))
    destination.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=destination, format="turtle")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="Legacy/raw JSON input for fixture compatibility")
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/movies.ttl"))
    args = parser.parse_args()
    export(args.input, args.output) if args.input else export_processed(args.processed_dir, args.output)
