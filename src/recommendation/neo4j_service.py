"""Graph-native explainable movie recommendation."""

from src.models import Recommendation


QUERY = """
MATCH (source:Movie {tmdb_id: $movie_id})
OPTIONAL MATCH (source)<-[:DIRECTED]-(sd:Person)
WITH source, collect(DISTINCT sd.name) AS source_directors
OPTIONAL MATCH (source)<-[:ACTED_IN]-(sa:Person)
WITH source, source_directors, collect(DISTINCT sa.name) AS source_actors
OPTIONAL MATCH (source)-[:HAS_GENRE]->(sg:Genre)
WITH source, source_directors, source_actors, collect(DISTINCT sg.name) AS source_genres
OPTIONAL MATCH (source)-[:HAS_KEYWORD]->(sk:Keyword)
WITH source, source_directors, source_actors, source_genres, collect(DISTINCT sk.name) AS source_keywords
MATCH (candidate:Movie) WHERE candidate <> source
OPTIONAL MATCH (candidate)<-[:DIRECTED]-(cd:Person)
WITH source_directors,source_actors,source_genres,source_keywords,candidate,collect(DISTINCT cd.name) AS cd
OPTIONAL MATCH (candidate)<-[:ACTED_IN]-(ca:Person)
WITH source_directors,source_actors,source_genres,source_keywords,candidate,cd,collect(DISTINCT ca.name) AS ca
OPTIONAL MATCH (candidate)-[:HAS_GENRE]->(cg:Genre)
WITH source_directors,source_actors,source_genres,source_keywords,candidate,cd,ca,collect(DISTINCT cg.name) AS cg
OPTIONAL MATCH (candidate)-[:HAS_KEYWORD]->(ck:Keyword)
WITH source_directors,source_actors,source_genres,source_keywords,candidate,cd,ca,cg,collect(DISTINCT ck.name) AS candidate_keywords
WITH candidate,
 [x IN cd WHERE x IN source_directors] AS directors,
 [x IN ca WHERE x IN source_actors] AS actors,
 [x IN cg WHERE x IN source_genres] AS genres,
 [x IN candidate_keywords WHERE x IN source_keywords] AS keywords,
 source_directors,source_actors,source_genres,source_keywords,cd,ca,cg,candidate_keywords
WITH *, 3.0*size(directors)+2.0*size(actors)+1.5*size(genres)+size(keywords) AS overlap,
 3.0*(size(source_directors)+size([x IN cd WHERE NOT x IN source_directors]))+
 2.0*(size(source_actors)+size([x IN ca WHERE NOT x IN source_actors]))+
 1.5*(size(source_genres)+size([x IN cg WHERE NOT x IN source_genres]))+
 size(source_keywords)+size([x IN candidate_keywords WHERE NOT x IN source_keywords]) AS union_weight
WITH *, CASE WHEN $method='overlap' THEN overlap ELSE CASE WHEN union_weight=0 THEN 0.0 ELSE overlap/union_weight END END AS score
WHERE score > 0
RETURN candidate.tmdb_id AS movie_id,candidate.title AS title,score,directors,actors,genres,keywords
ORDER BY score DESC,title LIMIT $top_k
"""


def recommend(repository, movie_id: int, top_k: int, method: str) -> list[Recommendation]:
    exists = repository.run("MATCH (m:Movie {tmdb_id:$movie_id}) RETURN count(m) AS n", movie_id=movie_id)
    if not exists[0]["n"]: raise KeyError(movie_id)
    rows = repository.run(QUERY, movie_id=movie_id, top_k=top_k, method=method)
    labels = {"directors": "đạo diễn", "actors": "diễn viên", "genres": "thể loại", "keywords": "từ khóa"}
    result = []
    for row in rows:
        reasons = [f"{labels[k]}: {', '.join(row[k])}" for k in labels if row[k]]
        result.append(Recommendation(movie_id=row["movie_id"], title=row["title"], score=round(row["score"], 6),
            shared_directors=row["directors"], shared_actors=row["actors"], shared_genres=row["genres"],
            shared_keywords=row["keywords"], explanation="Tương đồng qua " + "; ".join(reasons)))
    return result
