// Idempotently materialize inferred co-starring facts and their support count.
MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(b:Person)
WHERE elementId(a) < elementId(b)
WITH a, b, count(DISTINCT m) AS movie_count, collect(DISTINCT m.tmdb_id) AS evidence_movie_ids
MERGE (a)-[r:CO_STARRED_WITH]->(b)
SET r.movie_count = movie_count, r.derived = true, r.evidence_movie_ids = evidence_movie_ids;

