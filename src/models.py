from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)


class AskResponse(BaseModel):
    answer: str
    intent: str
    evidence: list[dict]
    query_time_ms: float


class RecommendRequest(BaseModel):
    movie_id: int
    top_k: int = Field(default=10, ge=1, le=50)
    method: str = Field(default="overlap", pattern="^(overlap|weighted_jaccard|hybrid)$")


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=10, ge=1, le=50)
    min_rating: float | None = Field(default=None, ge=0, le=10)
    genre: str | None = Field(default=None, max_length=80)


class SearchResult(BaseModel):
    movie_id: int
    title: str
    score: float
    rating: float | None = None
    genres: list[str] = Field(default_factory=list)
    explanation: str


class Recommendation(BaseModel):
    movie_id: int
    title: str
    score: float
    graph_score: float | None = None
    semantic_score: float | None = None
    quality_score: float | None = None
    shared_directors: list[str] = Field(default_factory=list)
    shared_actors: list[str] = Field(default_factory=list)
    shared_genres: list[str] = Field(default_factory=list)
    shared_keywords: list[str] = Field(default_factory=list)
    explanation: str
