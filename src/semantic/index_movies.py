"""Create Neo4j search indexes and attach local multilingual movie embeddings."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import get_settings
from src.kg.repository import Neo4jRepository
from src.semantic.embeddings import embed, movie_document


def index(input_path: Path, batch_size: int = 64, force: bool = False) -> dict:
    settings = get_settings()
    source_sha256 = hashlib.sha256(input_path.read_bytes()).hexdigest()
    movies = json.loads(input_path.read_text(encoding="utf-8"))["movies"]
    manifest_path = Path("data/processed/semantic_manifest.json")
    repository = Neo4jRepository(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password, settings.neo4j_database)
    try:
        repository.run("CREATE FULLTEXT INDEX movie_text IF NOT EXISTS FOR (m:Movie) ON EACH [m.title, m.overview]")
        repository.run("CREATE FULLTEXT INDEX entity_names IF NOT EXISTS FOR (n:Person|Movie) ON EACH [n.name, n.title]")
        embedded = repository.run("MATCH (m:Movie) RETURN count(m) AS total,count(m.embedding) AS embedded")[0]
        if not force and manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if (manifest.get("source_sha256") == source_sha256 and manifest.get("model") == settings.embedding_model
                    and embedded["total"] == len(movies) == embedded["embedded"]):
                return {**manifest, "status": "reused"}
        dimensions = 0
        for start in range(0, len(movies), batch_size):
            batch = movies[start:start + batch_size]
            vectors = embed([movie_document(movie) for movie in batch])
            dimensions = len(vectors[0])
            repository.run("UNWIND $rows AS row MATCH (m:Movie {tmdb_id:row.id}) SET m.embedding=row.embedding",
                           rows=[{"id": movie["tmdb_id"], "embedding": vector} for movie, vector in zip(batch, vectors)])
        repository.run(f"CREATE VECTOR INDEX movie_embedding IF NOT EXISTS FOR (m:Movie) ON m.embedding "
                       f"OPTIONS {{indexConfig: {{`vector.dimensions`: {dimensions}, `vector.similarity_function`: 'cosine'}}}}")
        manifest = {"generated_at": datetime.now(timezone.utc).isoformat(), "source": str(input_path),
                    "source_sha256": source_sha256, "movies": len(movies), "dimensions": dimensions,
                    "model": settings.embedding_model, "fastembed_version": "0.8.0", "pooling": "mean"}
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return {**manifest, "status": "generated"}
    finally:
        repository.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--input", type=Path, default=Path("data/raw/tmdb_movies.json"))
    parser.add_argument("--batch-size", type=int, default=64); parser.add_argument("--force", action="store_true"); args = parser.parse_args()
    print(json.dumps(index(args.input, args.batch_size, args.force), indent=2))
