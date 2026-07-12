from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import get_settings
from src.ingestion.tmdb_client import TMDBClient


def normalize_response(item: dict) -> dict:
    crew = item.get("credits", {}).get("crew", [])
    return {
        "tmdb_id": item["id"], "imdb_id": item.get("external_ids", {}).get("imdb_id"),
        "title": item.get("title"), "release_date": item.get("release_date"), "runtime": item.get("runtime"),
        "rating": item.get("vote_average"), "popularity": item.get("popularity"), "overview": item.get("overview"),
        "directors": [{"tmdb_id": p["id"], "name": p["name"]}
                      for p in crew if p.get("job") == "Director" and p.get("id") and p.get("name")],
        "actors": [{"tmdb_id": p["id"], "name": p["name"], "character": p.get("character") or "",
                    "cast_order": p.get("order")}
                   for p in item.get("credits", {}).get("cast", [])[:20] if p.get("id") and p.get("name")],
        "genres": [{"genre_id": x["id"], "name": x["name"]} for x in item.get("genres", [])],
        "keywords": [{"keyword_id": x["id"], "name": x["name"]}
                     for x in item.get("keywords", {}).get("keywords", [])],
        "studios": [{"company_id": x["id"], "name": x["name"], "country": x.get("origin_country") or ""}
                    for x in item.get("production_companies", [])],
        "source": "tmdb", "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def collect(ids: list[int] | None, output: Path, count: int | None = None) -> None:
    settings = get_settings(); client = TMDBClient(settings.tmdb_api_key or "")
    if ids is None: ids = client.popular_ids(count or 2000)
    movies = [normalize_response(client.movie(movie_id)) for movie_id in ids]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"movies": movies}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect immutable TMDB movie records")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ids", help="Comma-separated TMDB movie IDs")
    group.add_argument("--count", type=int, choices=range(2000, 5001), metavar="2000..5000",
                       help="Discover this many popular movies for the full evaluation dataset")
    parser.add_argument("--output", type=Path, default=Path("data/raw/tmdb_movies.json"))
    args = parser.parse_args(); collect([int(x) for x in args.ids.split(",")] if args.ids else None, args.output, args.count)
