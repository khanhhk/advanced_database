// 1. Movies by director
MATCH (p:Person)-[:DIRECTED]->(m:Movie) WHERE toLower(p.name)=toLower($director) RETURN m;
// 2. Actors of a movie
MATCH (p:Person)-[:ACTED_IN]->(m:Movie {tmdb_id:$movie_id}) RETURN p;
// 3. Genre and rating
MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre) WHERE toLower(g.name)=toLower($genre) AND m.rating>$rating RETURN m;
// 4. Common movies
MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(b:Person) WHERE a.name=$actor_a AND b.name=$actor_b RETURN m;
// 5. Frequent collaborators
MATCH (a:Person {name:$actor})-[r:CO_STARRED_WITH]-(b:Person) RETURN b,r.movie_count ORDER BY r.movie_count DESC;
// 6. Directors by genre
MATCH (p:Person)-[:DIRECTED]->(m:Movie)-[:HAS_GENRE]->(g:Genre {name:$genre}) RETURN p,count(m) AS movies ORDER BY movies DESC;
// 7. Shortest person path
MATCH p=shortestPath((a:Person {name:$person_a})-[*..8]-(b:Person {name:$person_b})) RETURN p;
// 8. Similar movie metadata
MATCH (source:Movie {tmdb_id:$movie_id})-[r]->(x)<-[r2]-(candidate:Movie) RETURN candidate,count(DISTINCT x) AS shared ORDER BY shared DESC;
// 9. Node counts
MATCH (n) UNWIND labels(n) AS label RETURN label,count(*) AS count;
// 10. Verify inferred facts
MATCH (a:Person)-[r:CO_STARRED_WITH]->(b:Person) RETURN a.name,b.name,r.movie_count,r.evidence_movie_ids;

