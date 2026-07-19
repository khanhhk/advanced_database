"""Centralized, parameterized Cypher templates used by the application.

Entity-linked queries prefer stable source IDs. Canonical names remain as a
fallback for repositories that cannot provide an ID (mainly legacy fixtures).
"""

QUERIES = {
    "movies_by_director": """MATCH (p:Person)-[:DIRECTED]->(m:Movie)
      WHERE ($director_id IS NOT NULL AND p.person_id = $director_id)
         OR ($director_id IS NULL AND toLower(p.name) = toLower($director))
      RETURN m.tmdb_id AS movie_id,m.title AS title,m.release_date AS release_date,
             'DIRECTED' AS relationship ORDER BY m.release_date LIMIT 50""",
    "movies_by_person": """MATCH (p:Person)-[r:ACTED_IN|DIRECTED]->(m:Movie)
      WHERE ($person_id IS NOT NULL AND p.person_id = $person_id)
         OR ($person_id IS NULL AND toLower(p.name) = toLower($person))
      RETURN DISTINCT m.tmdb_id AS movie_id,m.title AS title,type(r) AS relationship,
             m.release_date AS release_date ORDER BY m.release_date DESC LIMIT 50""",
    "actors_in_movie": """MATCH (p:Person)-[r:ACTED_IN]->(m:Movie)
      WHERE ($movie_id IS NOT NULL AND m.tmdb_id = $movie_id)
         OR ($movie_id IS NULL AND toLower(m.title) = toLower($movie))
      RETURN p.name AS name,m.tmdb_id AS movie_id,r.character AS character,
             r.cast_order AS cast_order,'ACTED_IN' AS relationship
      ORDER BY r.cast_order LIMIT 50""",
    "common_movies": """MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(b:Person)
      WHERE (($person1_id IS NOT NULL AND a.person_id = $person1_id)
          OR ($person1_id IS NULL AND toLower(a.name) = toLower($person1)))
        AND (($person2_id IS NOT NULL AND b.person_id = $person2_id)
          OR ($person2_id IS NULL AND toLower(b.name) = toLower($person2)))
      RETURN DISTINCT m.tmdb_id AS movie_id,m.title AS title,'ACTED_IN' AS relationship""",
    "movies_by_genre_rating": """MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre)
      WHERE (($genre_id IS NOT NULL AND g.genre_id = $genre_id)
          OR ($genre_id IS NULL AND toLower(g.name) = toLower($genre)))
        AND coalesce(m.imdb_rating,m.rating) > $rating
      RETURN m.tmdb_id AS movie_id,m.title AS title,
             coalesce(m.imdb_rating,m.rating) AS rating ORDER BY rating DESC LIMIT 50""",
    "co_stars": """MATCH (a:Person)-[r:CO_STARRED_WITH]-(b:Person)
      WHERE ($person_id IS NOT NULL AND a.person_id = $person_id)
         OR ($person_id IS NULL AND toLower(a.name) = toLower($person))
      RETURN b.name AS name,r.movie_count AS movie_count,
             r.evidence_movie_ids AS evidence_movie_ids,true AS derived
      ORDER BY r.movie_count DESC LIMIT 50""",
    "directors_by_genre": """MATCH (p:Person)-[:DIRECTED]->(m:Movie)-[:HAS_GENRE]->(g:Genre)
      WHERE ($genre_id IS NOT NULL AND g.genre_id = $genre_id)
         OR ($genre_id IS NULL AND toLower(g.name) = toLower($genre))
      RETURN p.name AS name,count(m) AS movie_count,collect(m.tmdb_id) AS movie_ids
      ORDER BY movie_count DESC LIMIT 50""",
    "shortest_path": """MATCH p=shortestPath((a:Person)-[*..8]-(b:Person))
      WHERE (($person1_id IS NOT NULL AND a.person_id = $person1_id)
          OR ($person1_id IS NULL AND toLower(a.name) = toLower($person1)))
        AND (($person2_id IS NOT NULL AND b.person_id = $person2_id)
          OR ($person2_id IS NULL AND toLower(b.name) = toLower($person2)))
      RETURN [n IN nodes(p) | coalesce(n.name,n.title)] AS labels,
             [r IN relationships(p) | type(r)] AS relationships LIMIT 1""",
    "resolve_movie": """MATCH (m:Movie)
      WHERE ($movie_id IS NOT NULL AND m.tmdb_id = $movie_id)
         OR ($movie_id IS NULL AND toLower(m.title) = toLower($movie))
      RETURN m.tmdb_id AS movie_id ORDER BY size(m.title) LIMIT 1""",
}
