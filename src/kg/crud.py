"""Explicit, parameterized administrative CRUD for Movie records.

These functions are intentionally not exposed through the public API. Production
bulk synchronization remains the authoritative importer; CRUD exists for the
course's operational exercise and controlled maintenance.
"""
from __future__ import annotations


CREATE_MOVIE = """MERGE (m:Movie {tmdb_id:$tmdb_id})
ON CREATE SET m.created_at=datetime()
SET m.title=$title,m.release_date=$release_date,m.source=$source RETURN m{.*} AS movie"""
READ_MOVIE = """MATCH (m:Movie {tmdb_id:$tmdb_id})
OPTIONAL MATCH (m)<-[:ACTED_IN]-(actor:Person)
OPTIONAL MATCH (m)<-[:DIRECTED]-(director:Person)
OPTIONAL MATCH (m)-[:HAS_GENRE]->(genre:Genre)
RETURN m{.*} AS movie,collect(DISTINCT actor.name) AS actors,
collect(DISTINCT director.name) AS directors,collect(DISTINCT genre.name) AS genres"""
UPDATE_MOVIE = """MATCH (m:Movie {tmdb_id:$tmdb_id})
SET m.overview=$overview,m.runtime=$runtime,m.updated_at=datetime() RETURN m{.*} AS movie"""
DELETE_MOVIE = "MATCH (m:Movie {tmdb_id:$tmdb_id}) DETACH DELETE m RETURN count(m) AS deleted"
UPSERT_CAST = """MATCH (p:Person {person_id:$person_id}),(m:Movie {tmdb_id:$tmdb_id})
MERGE (p)-[r:ACTED_IN]->(m)
SET r.character=$character,r.cast_order=$cast_order,r.source=$source RETURN type(r) AS relationship"""


def create_movie(repository, *, tmdb_id: int, title: str, release_date: str = "", source: str = "manual") -> dict:
    return repository.run(CREATE_MOVIE, tmdb_id=tmdb_id, title=title,
                          release_date=release_date, source=source)[0]["movie"]


def read_movie(repository, tmdb_id: int) -> dict | None:
    rows = repository.run(READ_MOVIE, tmdb_id=tmdb_id)
    return rows[0] if rows else None


def update_movie(repository, *, tmdb_id: int, overview: str, runtime: int | None) -> dict | None:
    rows = repository.run(UPDATE_MOVIE, tmdb_id=tmdb_id, overview=overview, runtime=runtime)
    return rows[0]["movie"] if rows else None


def delete_movie(repository, tmdb_id: int) -> bool:
    rows = repository.run(DELETE_MOVIE, tmdb_id=tmdb_id)
    return bool(rows and rows[0]["deleted"])


def upsert_cast(repository, *, person_id: str, tmdb_id: int, character: str,
                cast_order: int | None, source: str = "manual") -> bool:
    rows = repository.run(UPSERT_CAST, person_id=person_id, tmdb_id=tmdb_id,
                          character=character, cast_order=cast_order, source=source)
    return bool(rows)
