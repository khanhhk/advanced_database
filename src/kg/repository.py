import json
from pathlib import Path
from typing import Protocol

from src.models import Recommendation
from src.qa.service import answer as answer_from_movies
from src.recommendation.service import recommend as recommend_from_movies


class GraphRepository(Protocol):
    def health(self) -> bool: ...
    def movies(self) -> list[dict]: ...
    def search_entities(self, query: str, limit: int = 10) -> list[dict]: ...
    def stats(self) -> dict: ...
    def answer(self, question: str) -> tuple[str, str, list[dict]]: ...
    def recommend(self, movie_id: int, top_k: int) -> list[Recommendation]: ...


class MemoryRepository:
    def __init__(self, seed_file: Path):
        self.data = json.loads(seed_file.read_text(encoding="utf-8"))
        for movie in self.data["movies"]:
            for key in ("actors", "directors", "genres", "keywords", "studios"):
                movie[key] = [value.get("name", "") if isinstance(value, dict) else value
                              for value in movie.get(key, [])]

    def health(self) -> bool:
        return True

    def movies(self) -> list[dict]:
        return self.data["movies"]

    def search_entities(self, query: str, limit: int = 10) -> list[dict]:
        needle = query.casefold()
        found = []
        for movie in self.movies():
            if needle in movie["title"].casefold():
                found.append({"id": movie["tmdb_id"], "name": movie["title"], "type": "Movie",
                              "year": str(movie.get("release_date", ""))[:4] or None})
            for role in ("directors", "actors"):
                for name in movie[role]:
                    item = {"id": name, "name": name, "type": "Person"}
                    if needle in name.casefold() and item not in found:
                        found.append(item)
            for key, entity_type in (("genres", "Genre"), ("keywords", "Keyword"), ("studios", "Studio")):
                for name in movie[key]:
                    item = {"id": name, "name": name, "type": entity_type}
                    if needle in name.casefold() and item not in found:
                        found.append(item)
        return found[:limit]

    def stats(self) -> dict:
        movies = self.movies()
        people = {p for m in movies for key in ("actors", "directors") for p in m[key]}
        genres = {g for m in movies for g in m["genres"]}
        keywords = {k for m in movies for k in m["keywords"]}
        studios = {s for m in movies for s in m.get("studios", [])}
        edges = sum(len(m[k]) for m in movies for k in ("actors", "directors", "genres", "keywords", "studios"))
        return {"nodes": {"Movie": len(movies), "Person": len(people), "Genre": len(genres),
                          "Keyword": len(keywords), "Studio": len(studios)}, "relationships": edges}

    def answer(self, question: str) -> tuple[str, str, list[dict]]:
        return answer_from_movies(question, self.movies())

    def recommend(self, movie_id: int, top_k: int = 10) -> list[Recommendation]:
        return recommend_from_movies(self.movies(), movie_id, top_k)

class Neo4jRepository:
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        from neo4j import GraphDatabase
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def health(self) -> bool:
        self.driver.verify_connectivity()
        return True

    def movies(self) -> list[dict]:
        query = """MATCH (m:Movie)
        OPTIONAL MATCH (d:Person)-[:DIRECTED]->(m)
        OPTIONAL MATCH (a:Person)-[:ACTED_IN]->(m)
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        OPTIONAL MATCH (m)-[:HAS_KEYWORD]->(k:Keyword)
        OPTIONAL MATCH (m)-[:PRODUCED_BY]->(s:Studio)
        RETURN m{.*} AS movie, collect(DISTINCT d.name) AS directors,
          collect(DISTINCT a.name) AS actors, collect(DISTINCT g.name) AS genres,
          collect(DISTINCT k.name) AS keywords, collect(DISTINCT s.name) AS studios"""
        with self.driver.session(database=self.database) as session:
            return [{**r["movie"], **{k: r[k] for k in ("directors", "actors", "genres", "keywords", "studios")}}
                    for r in session.run(query)]

    def search_entities(self, query: str, limit: int = 10) -> list[dict]:
        fulltext = """CALL db.index.fulltext.queryNodes('entity_names', $q, {limit:$limit}) YIELD node, score
        WHERE node:Movie OR node:Person OR node:Genre OR node:Keyword OR node:Studio
        RETURN CASE WHEN node:Movie THEN node.tmdb_id WHEN node:Person THEN node.person_id
                    WHEN node:Genre THEN node.genre_id WHEN node:Keyword THEN node.keyword_id
                    WHEN node:Studio THEN node.company_id END AS id,
        coalesce(node.title,node.name) AS name,
        CASE WHEN node:Movie THEN 'Movie' WHEN node:Person THEN 'Person' WHEN node:Genre THEN 'Genre'
             WHEN node:Keyword THEN 'Keyword' ELSE 'Studio' END AS type,
        CASE WHEN node:Movie THEN substring(toString(node.release_date),0,4) ELSE null END AS year,
        score ORDER BY score DESC LIMIT $limit"""
        try:
            with self.driver.session(database=self.database) as session:
                rows = [dict(r) for r in session.run(fulltext, q=query.replace('"', ''), limit=limit)]
            if rows: return rows
        except Exception:
            pass
        cypher = """WITH [token IN split(toLower($q),' ') WHERE size(token)>=3] AS tokens
        MATCH (n) WHERE (n:Movie OR n:Person OR n:Genre OR n:Keyword OR n:Studio) AND
        (toLower(coalesce(n.title,n.name)) CONTAINS toLower($q) OR
         any(token IN tokens WHERE toLower(coalesce(n.title,n.name)) CONTAINS token))
        RETURN CASE WHEN n:Movie THEN n.tmdb_id WHEN n:Person THEN n.person_id
                    WHEN n:Genre THEN n.genre_id WHEN n:Keyword THEN n.keyword_id
                    WHEN n:Studio THEN n.company_id END AS id,
        coalesce(n.title,n.name) AS name,
        CASE WHEN n:Movie THEN 'Movie' WHEN n:Person THEN 'Person' WHEN n:Genre THEN 'Genre'
             WHEN n:Keyword THEN 'Keyword' ELSE 'Studio' END AS type,
        CASE WHEN n:Movie THEN substring(toString(n.release_date),0,4) ELSE null END AS year
        ORDER BY CASE WHEN toLower(coalesce(n.title,n.name))=toLower($q) THEN 0 ELSE 1 END,
        size(coalesce(n.title,n.name)) LIMIT $limit"""
        with self.driver.session(database=self.database) as session:
            return [dict(r) for r in session.run(cypher, q=query, limit=limit)]

    def stats(self) -> dict:
        with self.driver.session(database=self.database) as session:
            nodes = {r["label"]: r["count"] for r in session.run("MATCH (n) UNWIND labels(n) AS label RETURN label,count(*) AS count")}
            edges = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
        return {"nodes": nodes, "relationships": edges}

    def answer(self, question: str) -> tuple[str, str, list[dict]]:
        from src.qa.neo4j_service import answer
        return answer(question, self)

    def recommend(self, movie_id: int, top_k: int = 10) -> list[Recommendation]:
        from src.recommendation.neo4j_service import recommend
        return recommend(self, movie_id, top_k)

    def run(self, query: str, **parameters) -> list[dict]:
        """Execute an application-owned parameterized query and materialize records."""
        with self.driver.session(database=self.database) as session:
            return [dict(record) for record in session.run(query, **parameters)]
