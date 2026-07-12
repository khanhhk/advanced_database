import json
import time
from pathlib import Path

import httpx


class TMDBClient:
    def __init__(self, api_key: str, cache_dir: Path = Path("data/raw/tmdb"), interval: float = 0.25):
        if not api_key:
            raise ValueError("TMDB_API_KEY is required")
        self.api_key, self.cache_dir, self.interval = api_key, cache_dir, interval
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def movie(self, movie_id: int) -> dict:
        path = self.cache_dir / f"movie-{movie_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        params = {"api_key": self.api_key, "append_to_response": "credits,keywords,external_ids"}
        last_error = None
        for attempt in range(3):
            try:
                response = httpx.get(f"https://api.themoviedb.org/3/movie/{movie_id}", params=params, timeout=20)
                response.raise_for_status()
                data = response.json()
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(self.interval)
                return data
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                time.sleep(2 ** attempt)
        raise RuntimeError(f"TMDB request failed after retries: {last_error}")

    def popular_ids(self, count: int) -> list[int]:
        """Discover a deterministic popularity-ordered set of movie IDs."""
        ids, page = [], 1
        while len(ids) < count:
            path = self.cache_dir / f"popular-{page}.json"
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
            else:
                response = httpx.get("https://api.themoviedb.org/3/movie/popular",
                    params={"api_key": self.api_key, "page": page}, timeout=20)
                response.raise_for_status(); data = response.json()
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(self.interval)
            page_ids = [item["id"] for item in data.get("results", []) if item.get("id")]
            if not page_ids: break
            ids.extend(page_ids); page += 1
        if len(ids) < count: raise RuntimeError(f"TMDB returned only {len(ids)} movie IDs")
        return list(dict.fromkeys(ids))[:count]
