"""Same-snapshot SQLite baseline for representative relational multi-hop queries.

This is a controlled baseline, not a claim that SQLite represents every RDBMS.
Run it on the same processed CSV snapshot and machine as the Neo4j benchmark.
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import sqlite3
import statistics
import time
from pathlib import Path


SCHEMA = """
CREATE TABLE movie(tmdb_id INTEGER PRIMARY KEY, title TEXT, rating REAL);
CREATE TABLE person(person_id TEXT PRIMARY KEY, name TEXT);
CREATE TABLE genre(genre_id TEXT PRIMARY KEY, name TEXT);
CREATE TABLE acted_in(person_id TEXT, tmdb_id INTEGER);
CREATE TABLE directed(person_id TEXT, tmdb_id INTEGER);
CREATE TABLE has_genre(tmdb_id INTEGER, genre_id TEXT);
CREATE INDEX acted_person ON acted_in(person_id); CREATE INDEX acted_movie ON acted_in(tmdb_id);
CREATE INDEX directed_person ON directed(person_id); CREATE INDEX genre_movie ON has_genre(tmdb_id);
"""

QUERIES = {
    "movies_by_director": ("""SELECT m.title FROM person p JOIN directed d USING(person_id)
        JOIN movie m USING(tmdb_id) WHERE lower(p.name)=lower(?)""", ("Christopher Nolan",)),
    "common_movies": ("""SELECT DISTINCT m.title FROM person a JOIN acted_in aa ON a.person_id=aa.person_id
        JOIN movie m ON m.tmdb_id=aa.tmdb_id JOIN acted_in ab ON ab.tmdb_id=m.tmdb_id
        JOIN person b ON b.person_id=ab.person_id WHERE a.name=? AND b.name=?""",
        ("Christian Bale", "Tom Hardy")),
    "movies_by_genre_rating": ("""SELECT m.title FROM movie m JOIN has_genre hg USING(tmdb_id)
        JOIN genre g USING(genre_id) WHERE lower(g.name)=lower(?) AND m.rating>?""", ("Crime", 8.0)),
    "directors_by_genre": ("""SELECT p.name,count(*) n FROM person p JOIN directed d USING(person_id)
        JOIN has_genre hg USING(tmdb_id) JOIN genre g USING(genre_id) WHERE lower(g.name)=lower(?)
        GROUP BY p.person_id ORDER BY n DESC""", ("Action",)),
}


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def build_database(processed: Path) -> sqlite3.Connection:
    db = sqlite3.connect(":memory:"); db.executescript(SCHEMA)
    mappings = {
        "movie": ("movies.csv", ("tmdb_id", "title", "rating")),
        "person": ("people.csv", ("person_id", "name")),
        "genre": ("genres.csv", ("genre_id", "name")),
        "acted_in": ("acted_in.csv", ("person_id", "tmdb_id")),
        "directed": ("directed.csv", ("person_id", "tmdb_id")),
        "has_genre": ("has_genre.csv", ("tmdb_id", "genre_id")),
    }
    for table, (filename, fields) in mappings.items():
        rows = _read(processed / filename)
        values = [[row[field] or None for field in fields] for row in rows]
        db.executemany(f"INSERT INTO {table} VALUES ({','.join('?' for _ in fields)})", values)
    db.commit(); return db


def benchmark(db: sqlite3.Connection, iterations: int) -> list[dict]:
    results = []
    for name, (query, params) in QUERIES.items():
        db.execute(query, params).fetchall()  # one explicit warm-up
        samples = []
        for _ in range(iterations):
            start = time.perf_counter_ns(); db.execute(query, params).fetchall()
            samples.append((time.perf_counter_ns() - start) / 1_000_000)
        ordered = sorted(samples); p95 = ordered[min(len(ordered) - 1, int(.95 * len(ordered)))]
        results.append({"backend": "sqlite", "intent": name, "iterations": iterations,
                        "median_ms": statistics.median(samples), "p95_ms": p95,
                        "stdev_ms": statistics.pstdev(samples)})
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("experiments/results/relational_benchmark.csv"))
    args = parser.parse_args(); db = build_database(args.processed_dir)
    rows = benchmark(db, args.iterations); args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    metadata = {"backend": "sqlite", "sqlite_version": sqlite3.sqlite_version,
                "python_version": platform.python_version(), "platform": platform.platform(),
                "iterations_per_query": args.iterations, "warmup_runs_per_query": 1,
                "movie_count": db.execute("SELECT count(*) FROM movie").fetchone()[0],
                "scope": "controlled relational baseline; same processed snapshot required"}
    args.output.with_suffix(".metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
