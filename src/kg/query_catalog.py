"""Centralized, parameterized Cypher templates used by the application."""

QUERIES = {
    "movies_by_director": "MATCH (p:Person)-[:DIRECTED]->(m:Movie) WHERE toLower(p.name) CONTAINS toLower($director) RETURN m.tmdb_id AS movie_id,m.title AS title,m.release_date AS release_date,'DIRECTED' AS relationship ORDER BY m.release_date LIMIT 50",
    "movies_by_person": "MATCH (p:Person)-[r:ACTED_IN|DIRECTED]->(m:Movie) WHERE toLower(p.name) CONTAINS toLower($person) RETURN DISTINCT m.tmdb_id AS movie_id,m.title AS title,type(r) AS relationship,m.release_date AS release_date ORDER BY m.release_date DESC LIMIT 50",
    "actors_in_movie": "MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) WHERE toLower(m.title) CONTAINS toLower($movie) RETURN p.name AS name,m.tmdb_id AS movie_id,r.character AS character,r.cast_order AS cast_order,'ACTED_IN' AS relationship ORDER BY r.cast_order LIMIT 50",
    "common_movies": "MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(b:Person) WHERE toLower(a.name) CONTAINS toLower($person1) AND toLower(b.name) CONTAINS toLower($person2) RETURN DISTINCT m.tmdb_id AS movie_id,m.title AS title,'ACTED_IN' AS relationship",
    "movies_by_genre_rating": "MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre) WHERE toLower(g.name)=toLower($genre) AND coalesce(m.imdb_rating,m.rating)>$rating RETURN m.tmdb_id AS movie_id,m.title AS title,coalesce(m.imdb_rating,m.rating) AS rating ORDER BY rating DESC LIMIT 50",
    "co_stars": "MATCH (a:Person)-[r:CO_STARRED_WITH]-(b:Person) WHERE toLower(a.name) CONTAINS toLower($person) RETURN b.name AS name,r.movie_count AS movie_count,r.evidence_movie_ids AS evidence_movie_ids,true AS derived ORDER BY r.movie_count DESC LIMIT 50",
    "directors_by_genre": "MATCH (p:Person)-[:DIRECTED]->(m:Movie)-[:HAS_GENRE]->(g:Genre) WHERE toLower(g.name)=toLower($genre) RETURN p.name AS name,count(m) AS movie_count,collect(m.tmdb_id) AS movie_ids ORDER BY movie_count DESC LIMIT 50",
    "shortest_path": "MATCH p=shortestPath((a:Person)-[*..8]-(b:Person)) WHERE toLower(a.name) CONTAINS toLower($person1) AND toLower(b.name) CONTAINS toLower($person2) RETURN [n IN nodes(p) | coalesce(n.name,n.title)] AS labels,[r IN relationships(p) | type(r)] AS relationships LIMIT 1",
    "resolve_movie": "MATCH (m:Movie) WHERE toLower(m.title) CONTAINS toLower($movie) RETURN m.tmdb_id AS movie_id ORDER BY size(m.title) LIMIT 1",
}
