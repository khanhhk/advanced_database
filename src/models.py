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
    method: str = Field(default="weighted_jaccard", pattern="^(overlap|weighted_jaccard)$")


class Recommendation(BaseModel):
    movie_id: int
    title: str
    score: float
    shared_directors: list[str] = Field(default_factory=list)
    shared_actors: list[str] = Field(default_factory=list)
    shared_genres: list[str] = Field(default_factory=list)
    shared_keywords: list[str] = Field(default_factory=list)
    explanation: str
