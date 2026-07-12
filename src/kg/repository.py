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
    def semantic_search(self, query: str, top_k: int = 10, genre: str | None = None, min_rating: float | None = None) -> list: ...


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
        # The deterministic fixture backend has no embeddings; hybrid degrades
        # explicitly to its graph component for tests and offline evaluation.
        return recommend_from_movies(self.movies(), movie_id, top_k,
                                     "weighted_jaccard" if method == "hybrid" else method)

    def semantic_search(self, query: str, top_k: int = 10, genre: str | None = None, min_rating: float | None = None):
        from src.models import SearchResult
        terms = {x for x in query.casefold().split() if len(x) > 2}
        rows = []
        for movie in self.movies():
            if genre and genre.casefold() not in {x.casefold() for x in movie["genres"]}: continue
            if min_rating is not None and float(movie.get("rating") or 0) < min_rating: continue
            haystack = " ".join([movie["title"], movie.get("overview", ""), *movie["genres"], *movie["keywords"]]).casefold()
            score = sum(term in haystack for term in terms) / max(len(terms), 1)
            if score: rows.append(SearchResult(movie_id=movie["tmdb_id"], title=movie["title"], score=score,
                rating=movie.get("rating"), genres=movie["genres"], explanation="Khớp từ khóa/ngữ nghĩa trong metadata phim"))
        return sorted(rows, key=lambda x: (-x.score, x.title))[:top_k]


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
        WHERE node:Movie OR node:Person
        RETURN coalesce(node.tmdb_id,node.name) AS id,coalesce(node.title,node.name) AS name,
        CASE WHEN node:Movie THEN 'Movie' ELSE 'Person' END AS type,score ORDER BY score DESC LIMIT $limit"""
        try:
            with self.driver.session(database=self.database) as session:
                rows = [dict(r) for r in session.run(fulltext, q=query.replace('"', ''), limit=limit)]
            if rows: return rows
        except Exception:
            pass
        cypher = """WITH [token IN split(toLower($q),' ') WHERE size(token)>=3] AS tokens
        MATCH (n) WHERE (n:Movie OR n:Person) AND
        (toLower(coalesce(n.title,n.name)) CONTAINS toLower($q) OR
         any(token IN tokens WHERE toLower(coalesce(n.title,n.name)) CONTAINS token))
        RETURN coalesce(n.tmdb_id,n.name) AS id, coalesce(n.title,n.name) AS name,
        CASE WHEN n:Movie THEN 'Movie' ELSE 'Person' END AS type
        ORDER BY CASE WHEN toLower(coalesce(n.title,n.name))=toLower($q) THEN 0 ELSE 1 END,
        size(coalesce(n.title,n.name)) LIMIT $limit"""
        with self.driver.session(database=self.database) as session:
            return [dict(r) for r in session.run(cypher, q=query, limit=limit)]

    def semantic_search(self, query: str, top_k: int = 10, genre: str | None = None, min_rating: float | None = None):
        from src.models import SearchResult
        from src.semantic.embeddings import embed
        from src.semantic.query_parser import expand_query
        vector = embed([expand_query(query)])[0]
        cypher = """CALL db.index.vector.queryNodes('movie_embedding', $candidate_k, $embedding) YIELD node, score AS semantic_score
        OPTIONAL MATCH (node)-[:HAS_GENRE]->(g:Genre)
        WITH node,semantic_score,collect(DISTINCT g.name) AS genres,
          CASE WHEN coalesce(node.imdb_votes,0) <= 0 THEN 0.0
               ELSE (coalesce(node.imdb_rating,node.rating,0.0)/10.0) *
                    (log10(toFloat(node.imdb_votes)+1.0)/7.0) END AS confidence
        WHERE ($genre IS NULL OR any(x IN genres WHERE toLower(x)=toLower($genre)))
          AND ($min_rating IS NULL OR coalesce(node.imdb_rating,node.rating,0.0) >= $min_rating)
          AND size(coalesce(node.overview,'')) >= 30
        WITH node,genres,semantic_score,confidence,0.85*semantic_score+0.15*confidence AS score
        RETURN node.tmdb_id AS movie_id,node.title AS title,score,semantic_score,confidence,
          coalesce(node.imdb_rating,node.rating) AS rating,genres ORDER BY score DESC LIMIT $top_k"""
        rows = self.run(cypher, embedding=vector, candidate_k=max(top_k * 5, 50), top_k=top_k,
                        genre=genre, min_rating=min_rating)
        return [SearchResult(**row, explanation=f"Vector cosine={row['semantic_score']:.3f}; confidence={row['confidence']:.3f}; " +
                (f"thể loại {genre}; " if genre else "") + "lọc trực tiếp trên Knowledge Graph") for row in rows]

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
