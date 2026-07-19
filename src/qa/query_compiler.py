"""Whitelist compiler from validated query plans to parameterized Cypher."""
from __future__ import annotations

from dataclasses import dataclass

from src.qa.planner import QueryPlan


@dataclass(frozen=True)
class CompiledQuery:
    cypher: str
    parameters: dict


RELATION = {
    "Genre": ("HAS_GENRE", "Genre"),
    "Keyword": ("HAS_KEYWORD", "Keyword"),
    "Studio": ("PRODUCED_BY", "Studio"),
}
FIELD = {"rating": "coalesce(m.imdb_rating,m.rating)", "imdb_rating": "m.imdb_rating",
         "release_date": "m.release_date", "runtime": "m.runtime", "popularity": "m.popularity"}
OPERATOR = {"eq": "=", "gt": ">", "gte": ">=", "lt": "<", "lte": "<="}


ID_PROPERTY = {"Movie": "tmdb_id", "Person": "person_id", "Genre": "genre_id",
               "Keyword": "keyword_id", "Studio": "company_id"}


def compile_plan(plan: QueryPlan, entity_ids: dict[int, int | str] | None = None) -> CompiledQuery:
    entity_ids = entity_ids or {}
    if plan.operation in {"find", "describe"} and plan.target == "Movie":
        return _find_movies(plan, entity_ids)
    if plan.operation == "path":
        people = [(index, entity) for index, entity in enumerate(plan.entities)
                  if entity.type == "Person"]
        if len(people) != 2: raise ValueError("Path queries require exactly two people")
        params = _entity_parameters(people, entity_ids, "person")
        conditions = [_identity_condition("a", "Person", "person0", params),
                      _identity_condition("b", "Person", "person1", params)]
        return CompiledQuery(
            "MATCH p=shortestPath((a:Person)-[*..8]-(b:Person)) WHERE "
            + " AND ".join(conditions) + " "
            "RETURN [n IN nodes(p)|coalesce(n.name,n.title)] AS labels,"
            "[r IN relationships(p)|type(r)] AS relationships LIMIT 1",
            params)
    if plan.operation == "recommend":
        movies = [(index, entity) for index, entity in enumerate(plan.entities)
                  if entity.type == "Movie"]
        if len(movies) != 1: raise ValueError("Recommendation requires one movie")
        index, movie = movies[0]
        params = {"movie": movie.name, "movie_id": entity_ids.get(index)}
        return CompiledQuery(
            "MATCH (m:Movie) WHERE " + _identity_condition("m", "Movie", "movie", params) + " "
            "RETURN m.tmdb_id AS movie_id,m.title AS title LIMIT 1", params)
    if plan.operation == "aggregate":
        return _aggregate(plan, entity_ids)
    if plan.operation == "common_neighbors":
        people = [(index, entity) for index, entity in enumerate(plan.entities)
                  if entity.type == "Person"]
        if plan.target != "Movie" or len(people) != 2: raise ValueError("Common-neighbor query requires two people")
        params = _entity_parameters(people, entity_ids, "person")
        return CompiledQuery(
            "MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(b:Person) "
            "WHERE " + _identity_condition("a", "Person", "person0", params) + " AND "
            + _identity_condition("b", "Person", "person1", params) + " "
            "RETURN DISTINCT m.tmdb_id AS movie_id,m.title AS title,'ACTED_IN' AS relationship LIMIT $limit",
            {**params, "limit": plan.limit})
    raise ValueError("The query plan is outside the supported graph operations")


def _find_movies(plan: QueryPlan, entity_ids: dict[int, int | str]) -> CompiledQuery:
    matches, where, params = ["MATCH (m:Movie)"], [], {"limit": plan.limit}
    for index, entity in enumerate(plan.entities):
        key = f"entity{index}"; params[key] = entity.name; params[f"{key}_id"] = entity_ids.get(index)
        if entity.type == "Movie": where.append(_identity_condition("m", "Movie", key, params))
        elif entity.type == "Person":
            relationship = "DIRECTED" if entity.role == "director" else "ACTED_IN" if entity.role == "actor" else "ACTED_IN|DIRECTED"
            matches.append(f"MATCH (p{index}:Person)-[:{relationship}]->(m)")
            where.append(_identity_condition(f"p{index}", "Person", key, params))
        elif entity.type in RELATION:
            relationship, label = RELATION[entity.type]
            matches.append(f"MATCH (m)-[:{relationship}]->(e{index}:{label})")
            where.append(_identity_condition(f"e{index}", entity.type, key, params))
    for index, item in enumerate(plan.filters):
        key = f"filter{index}"; params[key] = item.value
        where.append(f"{FIELD[item.field]} {OPERATOR[item.operator]} ${key}")
    order = ""
    if plan.sort and plan.sort.field != "count":
        order = f" ORDER BY {FIELD[plan.sort.field]} {plan.sort.direction.upper()}"
    cypher = " ".join(matches) + (" WHERE " + " AND ".join(where) if where else "")
    cypher += " RETURN DISTINCT m.tmdb_id AS movie_id,m.title AS title,m.release_date AS release_date," \
              "coalesce(m.imdb_rating,m.rating) AS rating" + order + " LIMIT $limit"
    return CompiledQuery(cypher, params)


def _aggregate(plan: QueryPlan, entity_ids: dict[int, int | str]) -> CompiledQuery:
    if plan.target == "Person":
        genres = [(index, entity) for index, entity in enumerate(plan.entities)
                  if entity.type == "Genre"]
        params = {"limit": plan.limit}
        match = "MATCH (p:Person)-[:DIRECTED]->(m:Movie)"
        where = ""
        if genres:
            index, genre = genres[0]
            params.update({"genre": genre.name, "genre_id": entity_ids.get(index)})
            match += "-[:HAS_GENRE]->(g:Genre)"
            where = " WHERE " + _identity_condition("g", "Genre", "genre", params)
        return CompiledQuery(match + where + " RETURN p.name AS name,count(DISTINCT m) AS count ORDER BY count DESC LIMIT $limit", params)
    raise ValueError("This aggregation target is not supported")


def _identity_condition(alias: str, entity_type: str, key: str, params: dict) -> str:
    id_key = f"{key}_id"
    return (f"((${id_key} IS NOT NULL AND {alias}.{ID_PROPERTY[entity_type]} = ${id_key}) OR "
            f"(${id_key} IS NULL AND toLower({alias}.{'title' if entity_type == 'Movie' else 'name'}) "
            f"= toLower(${key})))")


def _entity_parameters(indexed_entities, entity_ids, prefix):
    params = {}
    for offset, (index, entity) in enumerate(indexed_entities):
        params[f"{prefix}{offset}"] = entity.name
        params[f"{prefix}{offset}_id"] = entity_ids.get(index)
    return params
