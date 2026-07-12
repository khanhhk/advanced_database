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
    def recommend(self, movie_id: int, top_k: int, method: str) -> list[Recommendation]: ...


class MemoryRepository:
    def __init__(self, seed_file: Path):
        self.data = json.loads(seed_file.read_text(encoding="utf-8"))

    def health(self) -> bool:
        return True

    def movies(self) -> list[dict]:
        return self.data["movies"]

    def search_entities(self, query: str, limit: int = 10) -> list[dict]:
        needle = query.casefold()
        found = []
        for movie in self.movies():
            if needle in movie["title"].casefold():
                found.append({"id": movie["tmdb_id"], "name": movie["title"], "type": "Movie"})
            for role in ("directors", "actors"):
                for name in movie[role]:
                    item = {"id": name, "name": name, "type": "Person"}
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

    def recommend(self, movie_id: int, top_k: int = 10, method: str = "weighted_jaccard") -> list[Recommendation]:
        return recommend_from_movies(self.movies(), movie_id, top_k, method)


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
        cypher = """MATCH (n) WHERE (n:Movie OR n:Person) AND toLower(coalesce(n.title,n.name)) CONTAINS toLower($q)
        RETURN coalesce(n.tmdb_id,n.name) AS id, coalesce(n.title,n.name) AS name,
        CASE WHEN n:Movie THEN 'Movie' ELSE 'Person' END AS type LIMIT $limit"""
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

    def recommend(self, movie_id: int, top_k: int = 10, method: str = "weighted_jaccard") -> list[Recommendation]:
        from src.recommendation.neo4j_service import recommend
        return recommend(self, movie_id, top_k, method)

    def run(self, query: str, **parameters) -> list[dict]:
        """Execute an application-owned parameterized query and materialize records."""
        with self.driver.session(database=self.database) as session:
            return [dict(record) for record in session.run(query, **parameters)]
