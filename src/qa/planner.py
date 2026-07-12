"""Constrained LLM question planner for the movie graph."""
from __future__ import annotations

import json
from typing import Literal

import httpx
from pydantic import BaseModel, Field, ValidationError


NodeType = Literal["Movie", "Person", "Genre", "Keyword", "Studio"]


class EntityReference(BaseModel):
    type: NodeType
    name: str = Field(min_length=1, max_length=200)
    role: Literal["actor", "director", "any"] | None = None


class QueryFilter(BaseModel):
    field: Literal["rating", "imdb_rating", "release_date", "runtime", "popularity"]
    operator: Literal["eq", "gt", "gte", "lt", "lte"]
    value: str | float | int


class SortSpec(BaseModel):
    field: Literal["rating", "imdb_rating", "release_date", "runtime", "popularity", "count"]
    direction: Literal["asc", "desc"] = "desc"


class QueryPlan(BaseModel):
    operation: Literal["find", "aggregate", "common_neighbors", "path", "recommend", "describe"]
    target: NodeType
    entities: list[EntityReference] = Field(default_factory=list, max_length=5)
    filters: list[QueryFilter] = Field(default_factory=list, max_length=5)
    sort: SortSpec | None = None
    limit: int = Field(default=10, ge=1, le=50)
    confidence: float = Field(ge=0, le=1)
    clarification: str | None = Field(default=None, max_length=300)


SYSTEM_PROMPT = """/no_think
Bạn là bộ lập kế hoạch truy vấn cho Movie Knowledge Graph.
Chỉ trả về một JSON object, không markdown. Không trả lời câu hỏi và không viết Cypher.
Schema node: Movie, Person, Genre, Keyword, Studio.
Quan hệ: Person-ACTED_IN->Movie, Person-DIRECTED->Movie,
Movie-HAS_GENRE->Genre, Movie-HAS_KEYWORD->Keyword, Movie-PRODUCED_BY->Studio,
Person-CO_STARRED_WITH-Person.
Operation hợp lệ: find, aggregate, common_neighbors, path, recommend, describe.
Entity Person có role actor/director/any; dùng any khi người dùng không nói rõ.
Filter chỉ dùng rating, imdb_rating, release_date, runtime, popularity.
Không tự suy diễn hoặc sáng tạo ngày, rating, tên hay giá trị mà người dùng không
nói. "mới nhất trước" chỉ tạo sort release_date desc, không tạo filter ngày.
"trên/lớn hơn" dùng gt; "từ/ít nhất" dùng gte; tương tự cho lt/lte.
Câu hỏi "liên hệ như thế nào", "đường liên hệ" hoặc "kết nối giữa" đúng hai
Person luôn dùng operation path. Câu hỏi phim giống/tương tự luôn dùng recommend,
target Movie và sort null nếu người dùng không yêu cầu sắp xếp.
Nếu thiếu thông tin bắt buộc hoặc câu hỏi ngoài schema, đặt confidence dưới 0.6 và
viết câu hỏi làm rõ trong clarification. Không sáng tạo tên thực thể.
Ví dụ "phim khoa học viễn tưởng do Christopher Nolan đạo diễn, điểm trên 7, mới
nhất trước" phải có Person/Christopher Nolan/role director, Genre/Science
Fiction, đúng một filter rating gt 7, sort release_date desc và tuyệt đối không
có filter release_date.
JSON phải có: operation,target,entities,filters,sort,limit,confidence,clarification."""


class QuestionPlanner:
    def __init__(self, api_key: str, base_url: str, model: str, timeout: float = 20):
        self.api_key, self.base_url, self.model, self.timeout = api_key, base_url.rstrip("/"), model, timeout

    def plan(self, question: str) -> QueryPlan:
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "temperature": 0,
                      "response_format": {"type": "json_schema", "json_schema": {
                          "name": "movie_query_plan", "strict": True,
                          "schema": QueryPlan.model_json_schema()}},
                      "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                   {"role": "user", "content": question}]},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ValueError("LLM question planner is unavailable") from exc
        content = response.json()["choices"][0]["message"]["content"]
        try:
            return QueryPlan.model_validate(json.loads(content))
        except (KeyError, TypeError, json.JSONDecodeError, ValidationError) as exc:
            raise ValueError("LLM returned an invalid query plan") from exc


def configured_planner(settings) -> QuestionPlanner | None:
    if not settings.llm_api_key or not settings.llm_model:
        return None
    return QuestionPlanner(settings.llm_api_key, settings.llm_base_url, settings.llm_model, settings.llm_timeout)
