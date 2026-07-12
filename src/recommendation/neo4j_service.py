"""Explainable IDF-weighted recommendation executed inside Neo4j."""

from src.models import Recommendation
from src.recommendation.service import build_explanation


# A shared feature contributes type_weight * (1 + ln((N + 1) / (df + 1))).
# Common features are discounted while rare, discriminative graph connections
# contribute more. Candidate generation only traverses features of the source.
QUERY = """
MATCH (source:Movie {tmdb_id: $movie_id})
MATCH (movie:Movie)
WITH source, count(movie) AS movie_count
CALL (source, movie_count) {
  MATCH (source)<-[:DIRECTED]-(feature:Person)-[:DIRECTED]->(candidate:Movie)
  WHERE candidate <> source
  WITH DISTINCT candidate, feature, movie_count
  MATCH (feature)-[:DIRECTED]->(linked:Movie)
  WITH candidate, feature.name AS name, movie_count, count(DISTINCT linked) AS frequency
  RETURN candidate, 'directors' AS kind, name,
         3.0 * (1.0 + log((movie_count + 1.0) / (frequency + 1.0))) AS contribution
  UNION ALL
  MATCH (source)<-[:ACTED_IN]-(feature:Person)-[:ACTED_IN]->(candidate:Movie)
  WHERE candidate <> source
  WITH DISTINCT candidate, feature, movie_count
  MATCH (feature)-[:ACTED_IN]->(linked:Movie)
  WITH candidate, feature.name AS name, movie_count, count(DISTINCT linked) AS frequency
  RETURN candidate, 'actors' AS kind, name,
         2.0 * (1.0 + log((movie_count + 1.0) / (frequency + 1.0))) AS contribution
  UNION ALL
  MATCH (source)-[:HAS_KEYWORD]->(feature:Keyword)<-[:HAS_KEYWORD]-(candidate:Movie)
  WHERE candidate <> source
  WITH DISTINCT candidate, feature, movie_count
  MATCH (feature)<-[:HAS_KEYWORD]-(linked:Movie)
  WITH candidate, feature.name AS name, movie_count, count(DISTINCT linked) AS frequency
  RETURN candidate, 'keywords' AS kind, name,
         1.5 * (1.0 + log((movie_count + 1.0) / (frequency + 1.0))) AS contribution
  UNION ALL
  MATCH (source)-[:HAS_GENRE]->(feature:Genre)<-[:HAS_GENRE]-(candidate:Movie)
  WHERE candidate <> source
  WITH DISTINCT candidate, feature, movie_count
  MATCH (feature)<-[:HAS_GENRE]-(linked:Movie)
  WITH candidate, feature.name AS name, movie_count, count(DISTINCT linked) AS frequency
  RETURN candidate, 'genres' AS kind, name,
         1.0 * (1.0 + log((movie_count + 1.0) / (frequency + 1.0))) AS contribution
  UNION ALL
  MATCH (source)-[:PRODUCED_BY]->(feature:Studio)<-[:PRODUCED_BY]-(candidate:Movie)
  WHERE candidate <> source
  WITH DISTINCT candidate, feature, movie_count
  MATCH (feature)<-[:PRODUCED_BY]-(linked:Movie)
  WITH candidate, feature.name AS name, movie_count, count(DISTINCT linked) AS frequency
  RETURN candidate, 'studios' AS kind, name,
         0.75 * (1.0 + log((movie_count + 1.0) / (frequency + 1.0))) AS contribution
}
WITH candidate, sum(contribution) AS score, collect({kind: kind, name: name}) AS evidence
RETURN candidate.tmdb_id AS movie_id, candidate.title AS title, score,
       [x IN evidence WHERE x.kind = 'directors' | x.name] AS directors,
       [x IN evidence WHERE x.kind = 'actors' | x.name] AS actors,
       [x IN evidence WHERE x.kind = 'genres' | x.name] AS genres,
       [x IN evidence WHERE x.kind = 'keywords' | x.name] AS keywords,
       [x IN evidence WHERE x.kind = 'studios' | x.name] AS studios
ORDER BY score DESC, title
LIMIT $top_k
"""


def recommend(repository, movie_id: int, top_k: int) -> list[Recommendation]:
    exists = repository.run("MATCH (m:Movie {tmdb_id:$movie_id}) RETURN count(m) AS n", movie_id=movie_id)
    if not exists[0]["n"]:
        raise KeyError(movie_id)
    rows = repository.run(QUERY, movie_id=movie_id, top_k=top_k)
    result = []
    for row in rows:
        shared = {"directors": row["directors"], "actors": row["actors"],
                  "keywords": row["keywords"], "genres": row["genres"], "studios": row["studios"]}
        result.append(Recommendation(
            movie_id=row["movie_id"], title=row["title"], score=round(row["score"], 6),
            shared_directors=row["directors"], shared_actors=row["actors"],
            shared_genres=row["genres"], shared_keywords=row["keywords"], shared_studios=row["studios"],
            explanation=build_explanation(shared),
        ))
    return result
