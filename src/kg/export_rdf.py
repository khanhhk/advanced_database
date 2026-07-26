"""Export the normalized Neo4j input snapshot as portable RDF/Turtle.

Neo4j remains the operational database. This exporter gives the same entities
stable HTTP IRIs so the schema and selected entailments can be checked with
standards-based semantic tools without introducing a second runtime datastore.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef

NS = Namespace("https://example.org/movie-kg/")


def _rows(processed_dir: Path, name: str) -> list[dict]:
    with (processed_dir / f"{name}.csv").open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def export_processed(processed_dir: Path, destination: Path) -> dict:
    """Export the exact normalized CSV snapshot consumed by Neo4j."""
    graph = Graph()
    graph.bind("movie", NS)

    movies = {
        row["tmdb_id"]: URIRef(NS[f"movie/{row['tmdb_id']}"])
        for row in _rows(processed_dir, "movies")
    }
    for row in _rows(processed_dir, "movies"):
        node = movies[row["tmdb_id"]]
        graph.add((node, RDF.type, NS.Movie))
        graph.add((node, NS.title, Literal(row["title"])))
        graph.add((node, NS.tmdbId, Literal(int(row["tmdb_id"]))))
        for field, predicate, cast in (
            ("imdb_id", "imdbId", str),
            ("rating", "rating", float),
            ("imdb_rating", "imdbRating", float),
            ("imdb_votes", "imdbVotes", int),
        ):
            if row.get(field) not in (None, ""):
                graph.add((node, NS[predicate], Literal(cast(row[field]))))

    entity_specs = {
        "people": ("person_id", "Person", "person"),
        "genres": ("genre_id", "Genre", "genre"),
        "keywords": ("keyword_id", "Keyword", "keyword"),
        "studios": ("company_id", "Studio", "studio"),
    }
    entities: dict[str, dict[str, URIRef]] = {}
    for table, (key, cls, uri_part) in entity_specs.items():
        entities[table] = {}
        for row in _rows(processed_dir, table):
            node = URIRef(NS[f"{uri_part}/{row[key]}"])
            entities[table][row[key]] = node
            graph.add((node, RDF.type, NS[cls]))
            graph.add((node, NS.name, Literal(row["name"])))

    edge_specs = {
        "acted_in": ("people", "person_id", "actedIn", True),
        "directed": ("people", "person_id", "directed", True),
        "has_genre": ("genres", "genre_id", "hasGenre", False),
        "has_keyword": ("keywords", "keyword_id", "hasKeyword", False),
        "produced_by": ("studios", "company_id", "producedBy", False),
    }
    for table, (entity_table, key, predicate, entity_first) in edge_specs.items():
        for row in _rows(processed_dir, table):
            movie = movies[row["tmdb_id"]]
            entity = entities[entity_table][row[key]]
            triple = (
                (entity, NS[predicate], movie)
                if entity_first
                else (movie, NS[predicate], entity)
            )
            graph.add(triple)

    destination.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=destination, format="turtle")
    return {"format": "turtle", "triples": len(graph), "namespace": str(NS)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/movies.ttl"))
    args = parser.parse_args()
    print(export_processed(args.processed_dir, args.output))
