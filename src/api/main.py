import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.config import get_settings
from src.kg.repository import Neo4jRepository
from src.models import AskRequest, AskResponse, RecommendRequest, Recommendation, SearchRequest, SearchResult


def create_repository():
    settings = get_settings()
    return Neo4jRepository(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password, settings.neo4j_database)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.repository = create_repository()
    yield
    close = getattr(app.state.repository, "close", None)
    if close: close()


app = FastAPI(title="Movie Knowledge Graph", version="1.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse("src/api/static/index.html")


@app.get("/health")
def health(request: Request):
    try:
        return {"status": "ok" if request.app.state.repository.health() else "error"}
    except Exception as exc:
        raise HTTPException(503, detail="Knowledge graph is unavailable") from exc


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, request: Request):
    start = time.perf_counter()
    text, intent, evidence = request.app.state.repository.answer(payload.question)
    return AskResponse(answer=text, intent=intent, evidence=evidence,
                       query_time_ms=round((time.perf_counter() - start) * 1000, 3))


@app.post("/recommend", response_model=list[Recommendation])
def recommendations(payload: RecommendRequest, request: Request):
    try:
        return request.app.state.repository.recommend(payload.movie_id, payload.top_k, payload.method)
    except KeyError as exc:
        raise HTTPException(404, detail=f"Movie {payload.movie_id} not found") from exc


@app.post("/search", response_model=list[SearchResult])
def semantic_search(payload: SearchRequest, request: Request):
    try:
        from src.semantic.query_parser import parse_filters
        inferred_genre, inferred_rating = parse_filters(payload.query)
        return request.app.state.repository.semantic_search(payload.query, payload.top_k,
            payload.genre or inferred_genre, payload.min_rating if payload.min_rating is not None else inferred_rating)
    except RuntimeError as exc:
        raise HTTPException(503, detail=str(exc)) from exc


@app.get("/entities/search")
def entity_search(request: Request, q: str = Query(min_length=1), limit: int = Query(10, ge=1, le=50)):
    return request.app.state.repository.search_entities(q, limit)


@app.get("/stats")
def stats(request: Request):
    return request.app.state.repository.stats()
