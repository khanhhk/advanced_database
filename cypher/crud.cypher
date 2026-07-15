// C1 CREATE/UPSERT a Movie with a stable key (administrative workflow only).
MERGE (m:Movie {tmdb_id: $tmdb_id})
ON CREATE SET m.created_at = datetime()
SET m.title = $title, m.release_date = $release_date, m.source = $source
RETURN m;

// C2 READ a Movie and its graph neighborhood.
MATCH (m:Movie {tmdb_id: $tmdb_id})
OPTIONAL MATCH (m)<-[acted:ACTED_IN]-(actor:Person)
OPTIONAL MATCH (m)<-[:DIRECTED]-(director:Person)
OPTIONAL MATCH (m)-[:HAS_GENRE]->(genre:Genre)
RETURN m, collect(DISTINCT actor) AS actors,
       collect(DISTINCT director) AS directors, collect(DISTINCT genre) AS genres;

// C3 UPDATE only whitelisted mutable metadata using parameters.
MATCH (m:Movie {tmdb_id: $tmdb_id})
SET m.overview = $overview, m.runtime = $runtime, m.updated_at = datetime()
RETURN m;

// C4 DELETE is deliberately guarded: detach only an explicitly selected Movie.
// Production ingestion normally uses authoritative --replace instead.
MATCH (m:Movie {tmdb_id: $tmdb_id}) DETACH DELETE m;

// C5 Idempotent relationship upsert with provenance.
MATCH (p:Person {person_id: $person_id}), (m:Movie {tmdb_id: $tmdb_id})
MERGE (p)-[r:ACTED_IN]->(m)
SET r.character = $character, r.cast_order = $cast_order, r.source = $source
RETURN r;
