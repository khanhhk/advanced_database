"""Build deterministic, auditable silver corpora from the collected TMDB facts.

These labels are useful for reproducible pre-submission evaluation.  They are
not a substitute for an independent human annotator; every case includes the
evidence/rule needed for a second reviewer to accept or override it.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import unicodedata
from pathlib import Path

from rapidfuzz.fuzz import ratio


def name(value):
    return value.get("name", "") if isinstance(value, dict) else value


def identifier(value):
    return value.get("tmdb_id") if isinstance(value, dict) else None


def typo(text: str) -> str:
    """Produce a deterministic realistic one-character transposition."""
    chars = list(text)
    positions = [i for i in range(1, len(chars) - 1) if chars[i].isalpha() and chars[i + 1].isalpha()]
    if positions:
        i = positions[len(positions) // 2]
        chars[i], chars[i + 1] = chars[i + 1], chars[i]
    return "".join(chars)


def folded(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def entity_cases(movies: list[dict], count: int, rng: random.Random) -> list[dict]:
    entities = {}
    for movie in movies:
        entities[("movie", movie["tmdb_id"])] = {"id": f"tmdb:{movie['tmdb_id']}", "tmdb_id": movie["tmdb_id"], "title": movie["title"]}
        for role in ("actors", "directors"):
            for person in movie.get(role, []):
                if identifier(person):
                    entities[("person", identifier(person))] = {"id": f"tmdb:{identifier(person)}", "tmdb_id": identifier(person), "name": name(person)}
    pool = list(entities.values())
    rng.shuffle(pool)
    cases = []
    for index, target in enumerate(pool[:count]):
        label_key = "title" if "title" in target else "name"
        surface = target[label_key]
        left = {"id": f"mention:{index}", label_key: typo(folded(surface))}
        is_match = index % 4 != 3  # 75 positives (ID/fuzzy), 25 auditable negatives.
        # Alternate exact-ID positives and fuzzy-name positives.
        if is_match and index % 2 == 0:
            left["tmdb_id"] = target["tmdb_id"]
        decoys = sorted(
            (x for x in pool[count:] if x.get(label_key) and x["tmdb_id"] != target["tmdb_id"]),
            key=lambda candidate: ratio(folded(surface), folded(candidate[label_key])), reverse=True,
        )[:4]
        candidates = decoys + ([target] if is_match else [])
        rng.shuffle(candidates)
        cases.append({"case_id": f"er-{index + 1:03d}", "left": left, "candidates": candidates,
                      "threshold": 90, "is_match": is_match, "expected_id": target["id"] if is_match else None,
                      "difficulty": ("hard-negative-nearest-name" if not is_match else
                                     "exact-id" if index % 2 == 0 else "fuzzy-nearest-name"),
                      "label_source": ("target excluded; candidates are four closest same-type names" if not is_match else
                                       "exact TMDB ID" if index % 2 == 0 else "TMDB canonical name with deterministic typo"),
                      "review_status": "silver-auto"})
    return cases


def reasoning_cases(movies: list[dict], count: int) -> list[dict]:
    pairs = {}
    for movie in movies:
        cast = sorted({(identifier(p), name(p)) for p in movie.get("actors", []) if identifier(p)})
        for i, a in enumerate(cast):
            for b in cast[i + 1:]:
                pairs.setdefault((a, b), []).append(movie["tmdb_id"])
    ranked = sorted(pairs.items(), key=lambda item: (-len(item[1]), item[0][0][1], item[0][1][1]))[:count]
    return [{"case_id": f"reason-{i + 1:03d}", "person_a": {"tmdb_id": pair[0][0], "name": pair[0][1]},
             "person_b": {"tmdb_id": pair[1][0], "name": pair[1][1]}, "movie_ids": ids,
             "valid": True, "evidence_rule": "both TMDB person IDs occur in the cast of every listed movie",
             "review_status": "silver-auto"} for i, (pair, ids) in enumerate(ranked)]


def recommendation_cases(movies: list[dict], case_count: int, relevant_per_case: int) -> list[dict]:
    """Label relevance using a documented rule independent of recommender rank.

    Relevant means same genre plus either same director, or at least two shared
    credited actors.  Candidate labels are computed exhaustively over all movies.
    """
    prepared = []
    for m in movies:
        prepared.append((m, {name(x) for x in m.get("genres", [])}, {identifier(x) or name(x) for x in m.get("directors", [])},
                         {identifier(x) or name(x) for x in m.get("actors", [])}))
    anchors = sorted(prepared, key=lambda x: (-len(x[1]), -float(x[0].get("rating") or 0), x[0]["tmdb_id"]))
    cases = []
    for anchor, genres, directors, actors in anchors:
        relevant = []
        evidence = {}
        for candidate, cg, cd, ca in prepared:
            if candidate["tmdb_id"] == anchor["tmdb_id"] or not (genres & cg):
                continue
            shared_directors, shared_actors = directors & cd, actors & ca
            if shared_directors or len(shared_actors) >= 2:
                relevant.append(candidate["tmdb_id"])
                evidence[str(candidate["tmdb_id"])] = {"shared_genres": sorted(genres & cg),
                    "shared_directors": len(shared_directors), "shared_actors": len(shared_actors)}
        if len(relevant) >= relevant_per_case:
            relevant = relevant[:relevant_per_case]
            cases.append({"case_id": f"rec-{len(cases) + 1:03d}", "movie_id": anchor["tmdb_id"],
                          "movie_title": anchor["title"], "relevant_movie_ids": relevant,
                          "evidence": {str(k): evidence[str(k)] for k in relevant},
                          "rubric": "shared genre AND (same director OR at least two shared top-20 actors)",
                          "review_status": "silver-auto"})
        if len(cases) == case_count:
            break
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/raw/tmdb_movies.json"))
    parser.add_argument("--output", type=Path, default=Path("experiments/corpora/silver"))
    parser.add_argument("--seed", type=int, default=20260712)
    args = parser.parse_args()
    movies = json.loads(args.input.read_text(encoding="utf-8"))["movies"]
    args.output.mkdir(parents=True, exist_ok=True)
    corpora = {"entity_resolution.json": entity_cases(movies, 100, random.Random(args.seed)),
               "reasoning.json": reasoning_cases(movies, 50),
               "recommendation.json": recommendation_cases(movies, 20, 10)}
    for filename, rows in corpora.items():
        (args.output / filename).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {len(rows)} cases to {args.output / filename}")


if __name__ == "__main__":
    main()
