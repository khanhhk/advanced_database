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


def compile_plan(plan: QueryPlan) -> CompiledQuery:
    if plan.operation in {"find", "describe"} and plan.target == "Movie":
        return _find_movies(plan)
    if plan.operation == "path":
        people = [e for e in plan.entities if e.type == "Person"]
        if len(people) != 2: raise ValueError("Path queries require exactly two people")
        return CompiledQuery(
            "MATCH p=shortestPath((a:Person)-[*..8]-(b:Person)) "
            "WHERE toLower(a.name)=toLower($person0) AND toLower(b.name)=toLower($person1) "
            "RETURN [n IN nodes(p)|coalesce(n.name,n.title)] AS labels,"
            "[r IN relationships(p)|type(r)] AS relationships LIMIT 1",
            {"person0": people[0].name, "person1": people[1].name})
    if plan.operation == "recommend":
        movies = [e for e in plan.entities if e.type == "Movie"]
        if len(movies) != 1: raise ValueError("Recommendation requires one movie")
        return CompiledQuery(
            "MATCH (m:Movie) WHERE toLower(m.title)=toLower($movie) "
            "RETURN m.tmdb_id AS movie_id,m.title AS title LIMIT 1", {"movie": movies[0].name})
    if plan.operation == "aggregate":
        return _aggregate(plan)
    if plan.operation == "common_neighbors":
        people = [e for e in plan.entities if e.type == "Person"]
        if plan.target != "Movie" or len(people) != 2: raise ValueError("Common-neighbor query requires two people")
        return CompiledQuery(
            "MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(b:Person) "
            "WHERE toLower(a.name)=toLower($person0) AND toLower(b.name)=toLower($person1) "
            "RETURN DISTINCT m.tmdb_id AS movie_id,m.title AS title,'ACTED_IN' AS relationship LIMIT $limit",
            {"person0": people[0].name, "person1": people[1].name, "limit": plan.limit})
    raise ValueError("The query plan is outside the supported graph operations")


def _find_movies(plan: QueryPlan) -> CompiledQuery:
    matches, where, params = ["MATCH (m:Movie)"], [], {"limit": plan.limit}
    for index, entity in enumerate(plan.entities):
        key = f"entity{index}"; params[key] = entity.name
        if entity.type == "Movie": where.append(f"toLower(m.title)=toLower(${key})")
        elif entity.type == "Person":
            relationship = "DIRECTED" if entity.role == "director" else "ACTED_IN" if entity.role == "actor" else "ACTED_IN|DIRECTED"
            matches.append(f"MATCH (p{index}:Person)-[:{relationship}]->(m)")
            where.append(f"toLower(p{index}.name)=toLower(${key})")
        elif entity.type in RELATION:
            relationship, label = RELATION[entity.type]
            matches.append(f"MATCH (m)-[:{relationship}]->(e{index}:{label})")
            where.append(f"toLower(e{index}.name)=toLower(${key})")
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


def _aggregate(plan: QueryPlan) -> CompiledQuery:
    if plan.target == "Person":
        genres = [e for e in plan.entities if e.type == "Genre"]
        params = {"limit": plan.limit}
        match = "MATCH (p:Person)-[:DIRECTED]->(m:Movie)"
        where = ""
        if genres:
            match += "-[:HAS_GENRE]->(g:Genre)"; where = " WHERE toLower(g.name)=toLower($genre)"; params["genre"] = genres[0].name
        return CompiledQuery(match + where + " RETURN p.name AS name,count(DISTINCT m) AS count ORDER BY count DESC LIMIT $limit", params)
    raise ValueError("This aggregation target is not supported")
