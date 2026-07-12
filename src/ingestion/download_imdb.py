"""Download the single IMDb dataset used by the project, safely."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

URL = "https://datasets.imdbws.com/title.ratings.tsv.gz"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _valid_gzip(path: Path) -> bool:
    try:
        with gzip.open(path, "rb") as stream:
            for _ in iter(lambda: stream.read(1024 * 1024), b""):
                pass
        return True
    except (OSError, EOFError):
        return False


def download(destination: Path, url: str = URL, force: bool = False) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force and _valid_gzip(destination):
        return {"url": url, "path": str(destination), "sha256": _sha256(destination),
                "bytes": destination.stat().st_size, "reused": True}
    partial = destination.with_suffix(destination.suffix + ".part")
    partial.unlink(missing_ok=True)
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=120) as response:
            response.raise_for_status()
            with partial.open("wb") as stream:
                for chunk in response.iter_bytes(1024 * 1024):
                    stream.write(chunk)
        if not _valid_gzip(partial):
            raise RuntimeError("Downloaded IMDb file is not a valid gzip archive")
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)
    metadata = {"url": url, "path": str(destination), "sha256": _sha256(destination),
                "bytes": destination.stat().st_size, "downloaded_at": datetime.now(timezone.utc).isoformat(),
                "reused": False}
    destination.with_suffix(destination.suffix + ".metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download IMDb title ratings only")
    parser.add_argument("--output", type=Path, default=Path("data/raw/imdb/title.ratings.tsv.gz"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    print(json.dumps(download(args.output, force=args.force), indent=2))
