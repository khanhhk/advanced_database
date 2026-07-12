# Tài liệu kỹ thuật — Movie Knowledge Graph

## 1. Mục đích và phạm vi

Movie Knowledge Graph là hệ thống tích hợp dữ liệu phim vào Neo4j và cung cấp hai
chức năng hướng người dùng:

1. Hỏi đáp bằng ngôn ngữ tự nhiên trên Knowledge Graph, có bằng chứng.
2. Gợi ý các phim tương tự một phim đã chọn, có giải thích từ các quan hệ chung.

Knowledge Graph là nguồn dữ liệu và nguồn bằng chứng duy nhất khi ứng dụng trả
lời. LLM chỉ phân tích câu hỏi thành kế hoạch truy vấn có cấu trúc; LLM không tự
trả lời bằng kiến thức có sẵn và không được phép sinh Cypher tự do.

Semantic/vector search đã được loại khỏi kiến trúc chạy hiện tại. RDF/OWL/SPARQL
được giữ để minh họa chuẩn biểu diễn tri thức và so sánh, không phải backend phục
vụ ứng dụng.

Sơ đồ kiến trúc có thể mở bằng diagrams.net tại
[`movie_knowledge_graph_flow.drawio`](movie_knowledge_graph_flow.drawio).

Các tài liệu đi sâu theo mục đích:

- [`ARCHITECTURE_EXPLAINED.md`](ARCHITECTURE_EXPLAINED.md): giải thích từng block,
  connector và request path trong draw.io.
- [`DESIGN_DECISIONS.md`](DESIGN_DECISIONS.md): tại sao chọn từng công nghệ và
  trade-off/phương án bị loại.
- [`QWEN_VLLM_DEPLOYMENT.md`](QWEN_VLLM_DEPLOYMENT.md): dựng và xử lý sự cố Qwen
  từ GPU đến tích hợp application.
- [`REPORT_SLIDE_SOURCE_GUIDE.md`](REPORT_SLIDE_SOURCE_GUIDE.md): ánh xạ claim,
  evidence và narrative cho report/slide.

## 2. Kiến trúc tổng thể

```text
TMDB API + IMDb Ratings
          │
          ▼
Raw cache bất biến → làm sạch / kiểm tra / entity resolution
          │
          ▼
Node/edge CSV + manifest → Neo4j importer → Neo4j Property Graph
                                                │
                    ┌───────────────────────────┴──────────────────────┐
                    │                                                  │
                    ▼                                                  ▼
Question → Qwen → QueryPlan → entity linking → safe compiler   IDF recommendation
                    │                                                  │
                    └─────────────────────┬────────────────────────────┘
                                          ▼
                              FastAPI → Web UI → evidence
```

Các boundary chính:

- `src/ingestion` chịu trách nhiệm lấy và cache dữ liệu nguồn.
- `src/processing` chuẩn hóa và tạo dữ liệu trung gian có thể tái lập.
- `src/kg` quản lý import, repository, query và RDF export.
- `src/qa` lập kế hoạch, liên kết thực thể, biên dịch và định dạng câu trả lời.
- `src/recommendation` xếp hạng phim trực tiếp trên graph.
- `src/api` cung cấp HTTP API và giao diện web.
- `src/runtime` quyết định tái sử dụng hay import lại graph.
- `experiments` lưu evaluator, corpus và kết quả đo.

Production runtime chỉ dùng `Neo4jRepository`. `MemoryRepository` và dữ liệu nhỏ
trong `tests/fixtures` chỉ phục vụ kiểm thử hoặc benchmark synthetic.

## 3. Công nghệ

| Thành phần | Công nghệ |
|---|---|
| API và UI | FastAPI, Pydantic, HTML/CSS/JavaScript |
| Graph operational | Neo4j 5, Cypher |
| Chuẩn semantic | RDFLib, RDF/OWL, SPARQL |
| Xử lý dữ liệu | Python 3.11, JSON, TSV/GZIP, CSV |
| LLM planner | Qwen3-8B-AWQ, vLLM 0.25.0 |
| LLM protocol | OpenAI-compatible `/v1/chat/completions` |
| Kiểm thử | pytest, Neo4j integration test |
| Điều phối | Makefile, Docker Compose |

Hai Python environment được tách biệt:

- `.venv`: ứng dụng, pipeline và test.
- `.venv-llm`: vLLM, PyTorch và CUDA runtime dành cho model.

Việc tách môi trường ngăn dependency CUDA làm thay đổi FastAPI hoặc pipeline.

## 4. Nguồn và pipeline dữ liệu

### 4.1. TMDB

TMDB là nguồn chính của graph. Pipeline thu thập phim, credits, genres, keywords
và studios. Response được cache nguyên bản trong `data/raw/tmdb` để có thể chạy
lại processing mà không gọi API nhiều lần.

`TMDB_API_KEY` chỉ nằm trong `.env`, không được commit.

### 4.2. IMDb Ratings

IMDb chỉ enrichment rating và vote count. Hệ thống tải
`title.ratings.tsv.gz`, đọc streaming trực tiếp từ GZIP và chỉ giữ các dòng có
`imdb_id` khớp chính xác với phim TMDB. Không giải nén hay nạp toàn bộ IMDb vào
RAM/Neo4j.

Các trường được giữ riêng:

- `Movie.rating`: rating từ TMDB.
- `Movie.imdb_rating`: rating từ IMDb.
- `Movie.imdb_votes`: số vote từ IMDb.

### 4.3. Chuẩn hóa

`src.processing.pipeline` thực hiện:

1. Đọc raw source.
2. Làm sạch chuỗi, ngày, số và danh sách credits.
3. Giữ stable source ID cho tất cả thực thể.
4. Exact join TMDB–IMDb bằng `imdb_id`.
5. Entity resolution có log/confidence cho trường hợp fuzzy cần thiết.
6. Tạo node/edge tables và `manifest.json`.
7. Ghi counts, checksum và quality metrics.

Person ưu tiên khóa `tmdb:<id>`, không dùng tên làm primary key. `ACTED_IN` giữ
`character` và `cast_order`.

### 4.4. Import Neo4j

`src.kg.load_neo4j`:

1. Tạo constraints/indexes.
2. Import node trước relationship.
3. Dùng transaction batch và `MERGE`.
4. Sinh quan hệ suy diễn `CO_STARRED_WITH`.
5. Kiểm tra duplicate, orphan, invalid edge và constraint.

`src.runtime.prepare` so sánh source checksum, số Movie dự kiến và số Movie thực
tế. Graph đúng trạng thái được tái sử dụng; graph lệch trạng thái được import lại.

## 5. Mô hình Knowledge Graph

### 5.1. Node

| Label | Khóa chính | Thuộc tính tiêu biểu |
|---|---|---|
| `Movie` | `tmdb_id` | `imdb_id`, `title`, `release_date`, `runtime`, `rating`, `imdb_rating`, `imdb_votes`, `popularity`, `overview` |
| `Person` | `person_id` | `tmdb_id`, `imdb_id`, `name`, `birthday` |
| `Genre` | `genre_id` | `name` |
| `Keyword` | `keyword_id` | `name` |
| `Studio` | `company_id` | `name`, `country` |

### 5.2. Relationship

| Relationship | Hướng | Ý nghĩa |
|---|---|---|
| `ACTED_IN` | `Person → Movie` | Người tham gia diễn xuất; có `character`, `cast_order` |
| `DIRECTED` | `Person → Movie` | Người đạo diễn phim |
| `HAS_GENRE` | `Movie → Genre` | Thể loại phim |
| `HAS_KEYWORD` | `Movie → Keyword` | Chủ đề/từ khóa nội dung |
| `PRODUCED_BY` | `Movie → Studio` | Hãng sản xuất |
| `CO_STARRED_WITH` | `Person ↔ Person` | Quan hệ suy diễn; có `movie_count`, `evidence_movie_ids`, `derived=true` |

Việc dùng một label `Person` cho phép một người vừa là diễn viên vừa là đạo diễn;
vai trò được biểu diễn bằng relationship thay vì node type riêng.

## 6. Chức năng hỏi đáp

### 6.1. Luồng chính

```text
Question
  → QuestionPlanner
  → QueryPlan JSON
  → Pydantic validation
  → entity linking
  → whitelist Cypher compiler
  → Neo4j
  → answer + intent/operation + evidence + latency
```

### 6.2. Qwen Question Planner

`src.qa.planner.QuestionPlanner` gọi Qwen qua `/v1/chat/completions`.

Model runtime hiện tại:

- Model: `Qwen/Qwen3-8B-AWQ`.
- Server: vLLM `0.25.0`.
- Context: 4.096 token.
- Mode: `/no_think`.
- Output: JSON Schema constrained decoding.
- GPU mục tiêu: RTX 3060 12 GB.
- Endpoint local: `http://127.0.0.1:8001/v1`.

Planner sử dụng `temperature=0` để giảm biến thiên. Pydantic JSON Schema được gửi
trong `response_format`; vì vậy model phải trả đúng field và type của QueryPlan.

### 6.3. QueryPlan DSL

`QueryPlan` hỗ trợ sáu operation:

- `find`: tìm node theo entity, relationship và filter.
- `aggregate`: đếm/xếp hạng trên graph.
- `common_neighbors`: tìm hàng xóm chung, ví dụ phim chung của hai diễn viên.
- `path`: tìm đường liên hệ giữa hai Person.
- `recommend`: chuyển sang recommendation service.
- `describe`: mô tả một thực thể từ graph.

Các thành phần được kiểm soát:

- Target: `Movie`, `Person`, `Genre`, `Keyword`, `Studio`.
- Filter field: `rating`, `imdb_rating`, `release_date`, `runtime`, `popularity`.
- Operator: `eq`, `gt`, `gte`, `lt`, `lte`.
- Sort direction: `asc`, `desc`.
- `limit`: 1–50.
- Tối đa 5 entity và 5 filter.

Nếu confidence dưới `0.6` hoặc có `clarification`, hệ thống không chạy query mà
trả câu hỏi làm rõ.

### 6.4. Entity linking

Tên do người dùng/LLM trích xuất được đối chiếu với Neo4j qua
`GET /entities/search` nội bộ:

1. Full-text candidate search nếu index khả dụng.
2. Fallback substring/token search.
3. Exact normalized match.
4. Fuzzy reranking bằng RapidFuzz.
5. Ngưỡng mặc định 70/100.

Canonical name và confidence được đưa vào evidence. Movie autocomplete trên UI
dùng title và năm phát hành để phân biệt phim trùng tên.

### 6.5. Safe Cypher compiler

`src.qa.query_compiler` không nhận Cypher từ LLM. Compiler chỉ ghép:

- label từ `Literal` đã validate;
- relationship từ mapping whitelist;
- field và operator từ dictionary cố định;
- value qua Neo4j parameter `$...`;
- `LIMIT` tối đa 50;
- truy vấn chỉ đọc.

Ví dụ QueryPlan:

```json
{
  "operation": "find",
  "target": "Movie",
  "entities": [
    {"type": "Person", "name": "Christopher Nolan", "role": "director"},
    {"type": "Genre", "name": "Science Fiction", "role": null}
  ],
  "filters": [{"field": "imdb_rating", "operator": "gt", "value": 7}],
  "sort": {"field": "release_date", "direction": "desc"},
  "limit": 10,
  "confidence": 0.95,
  "clarification": ""
}
```

### 6.6. Fallback deterministic

Khi thiếu `LLM_API_KEY`/`LLM_MODEL`, endpoint lỗi hoặc output không hợp lệ, QA
quay về parser 9 intent trong `src.qa.intents` và catalog Cypher tham số hóa.
Fallback giúp ứng dụng vẫn demo được khi model tạm thời không khả dụng, nhưng khả
năng hiểu cách diễn đạt kém linh hoạt hơn LLM planner.

## 7. Recommendation

### 7.1. Giao diện

Người dùng nhập tên phim và chọn đúng phim từ autocomplete. TMDB ID được lưu ẩn
và gửi tới `POST /recommend`; người dùng không cần biết mã TMDB.

### 7.2. Candidate generation

Neo4j chỉ duyệt các phim chia sẻ ít nhất một đặc trưng với phim nguồn:

- đạo diễn;
- diễn viên;
- keyword;
- thể loại;
- studio.

### 7.3. IDF-weighted graph similarity

Mỗi đặc trưng chung đóng góp:

```text
type_weight × (1 + ln((N + 1) / (df + 1)))
```

Trong đó:

- `N`: tổng số Movie.
- `df`: số Movie liên kết với đặc trưng.
- `type_weight`: trọng số loại quan hệ.

| Đặc trưng | Trọng số |
|---|---:|
| Đạo diễn | 3.00 |
| Diễn viên | 2.00 |
| Keyword | 1.50 |
| Thể loại | 1.00 |
| Studio | 0.75 |

Đặc trưng hiếm có tính phân biệt nhận điểm cao hơn đặc trưng phổ biến. Tổng đóng
góp tạo `score` để sắp xếp; đây là điểm IDF thô, không phải xác suất người dùng
sẽ thích phim.

### 7.4. Explanation

Recommendation trả các danh sách chung và chuyển chúng thành câu thân thiện:

- `Cùng đạo diễn là ...`
- `Dàn diễn viên chung gồm ...`
- `Nội dung có các chủ đề tương đồng như ...`
- `Cùng thuộc thể loại ...`
- `Đều do ... sản xuất.`

Explanation được tạo từ relationship thực tế trong graph, không do LLM viết.

## 8. API

### 8.1. `POST /ask`

Request:

```json
{"question": "Elisa Gabrielli từng góp mặt trong phim nào?"}
```

Response:

```json
{
  "answer": "Các phim tìm thấy: Luca, Madagascar: Escape 2 Africa, Madagascar",
  "intent": "find",
  "evidence": [],
  "query_time_ms": 250.0
}
```

`evidence` thực tế gồm entity link và các row graph; ví dụ trên rút gọn để dễ đọc.

### 8.2. `POST /recommend`

Request:

```json
{"movie_id": 27205, "top_k": 5}
```

Response là danh sách `Recommendation` gồm `movie_id`, `title`, `score`, năm nhóm
đặc trưng chung và `explanation`.

### 8.3. Supporting endpoints

- `GET /health`: kiểm tra Neo4j.
- `GET /stats`: thống kê node/relationship.
- `GET /entities/search?q=...&limit=...`: candidate search/autocomplete.
- `GET /`: giao diện web.
- `GET /docs`: Swagger UI.

Không còn endpoint semantic search.

## 9. Web UI

UI có hai tab:

1. `Hỏi đáp`: lưu lịch sử hiển thị ở client; mỗi request backend vẫn stateless.
2. `Gợi ý phim tương tự`: title autocomplete, top-K và các card giải thích.

Frontend dùng explicit DOM selector và event listener. Nội dung từ API được escape
trước khi chèn vào HTML. Asset query version được tăng khi cần tránh cache cũ.

## 10. Cấu hình

Các biến trong `.env`:

```dotenv
TMDB_API_KEY=
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=change-me
NEO4J_DATABASE=neo4j
LLM_API_KEY=local
LLM_BASE_URL=http://127.0.0.1:8001/v1
LLM_MODEL=Qwen/Qwen3-8B-AWQ
LLM_TIMEOUT=60
```

Không commit `.env`, raw data lớn hoặc model weights.

## 11. Cài đặt và vận hành

### 11.1. Chuẩn bị dữ liệu và ứng dụng

```bash
make setup
make data DATA_COUNT=2000
```

`make data` cần `TMDB_API_KEY` và kết nối mạng ở lần thu thập.

### 11.2. Cài và chạy LLM

Chạy một lần:

```bash
make llm-setup
```

Lệnh tạo `.venv-llm`, cài `vllm==0.25.0` và bỏ `torchcodec`. Torchcodec không cần
cho model text-only và yêu cầu FFmpeg shared library không có trên máy hiện tại.

Terminal 1:

```bash
make llm-run
```

Lệnh tương đương:

```bash
VLLM_USE_FLASHINFER_SAMPLER=0 .venv-llm/bin/vllm serve \
  Qwen/Qwen3-8B-AWQ \
  --host 127.0.0.1 \
  --port 8001 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.85
```

Native sampler được dùng vì máy có driver CUDA nhưng không có CUDA toolkit/nvcc
tại `/usr/local/cuda`. Service chỉ bind localhost; máy khác nên truy cập bằng SSH
tunnel thay vì mở cổng công khai.

### 11.3. Chạy ứng dụng

Terminal 2:

```bash
make run
```

Lệnh khởi động Neo4j, kiểm tra/import graph nếu cần rồi chạy Uvicorn tại
`http://127.0.0.1:8000`.

### 11.4. Demo qua SSH

Trên máy demo:

```bash
ssh -L 8001:127.0.0.1:8001 user@may-gpu
```

Nếu FastAPI chạy trên máy demo, giữ `LLM_BASE_URL=http://127.0.0.1:8001/v1`.
Neo4j có thể chạy tại máy demo hoặc được tunnel riêng tùy topology triển khai.

## 12. Bảo mật và guardrail

- Không cho LLM sinh hoặc thực thi Cypher tự do.
- QueryPlan được validate bằng Pydantic và JSON Schema.
- Label, relationship, field và operator đều nằm trong whitelist.
- Giá trị đầu vào dùng Neo4j parameters.
- Query compiler chỉ tạo read query và giới hạn kết quả.
- Entity phải được liên kết về node canonical trước khi query.
- LLM endpoint chỉ bind `127.0.0.1`; truy cập từ xa qua SSH tunnel.
- Secret chỉ nằm trong `.env`.
- Câu trả lời và explanation lấy từ graph evidence.

Giới hạn hiện tại: API chưa có authentication/rate limiting; phù hợp local demo,
không nên public trực tiếp ra Internet.

## 13. Kiểm thử

```bash
pytest -q
```

Test suite bao phủ:

- cleaning và processing;
- entity resolution/linking;
- intent fallback;
- QueryPlan validation và safe compiler;
- Neo4j QA service bằng repository giả;
- recommendation memory/Neo4j query behavior;
- API contract;
- evaluator logic;
- integration với Neo4j khi bật marker/môi trường phù hợp.

`make test` còn chạy Python compile và kiểm tra checksum nguồn trong
`.agents/memory/SOURCES.sha256`.

## 14. Evaluation và kết quả hiện có

Các corpus silver:

- 100 trường hợp entity resolution: 75 positive, 25 negative.
- 50 fact `CO_STARRED_WITH` có evidence.
- 20 recommendation cases có relevance rubric.

Kết quả đã ghi nhận trên corpus 2.000 phim:

- Graph: 36.574 node, 337.822 relationship, không có structural violation.
- Exact IMDb rating match: 1.677/1.785 phim có IMDb ID.
- Entity-resolution silver P/R/F1: 1,00.
- Co-star silver precision: 1,00.
- IDF recommendation trên Neo4j thật: P@10 = 0,70; NDCG@10 = 0,748.
- Neo4j benchmark: 100 iteration/câu sau một warm-up; median 2,34–110,65 ms,
  p95 3,83–126,20 ms trên dataset 2.000 phim.

Đây là silver evaluation, không được diễn giải như human gold evaluation hoặc
kết luận scalability nhiều quy mô.

LLM planner cần một corpus riêng gồm cách diễn đạt tiếng Việt, typo, câu kết hợp,
câu mơ hồ và câu ngoài schema. Các metric nên gồm operation accuracy, entity F1,
QueryPlan exact match, execution accuracy, clarification accuracy và latency.

## 15. Reproducibility

- Raw response được cache bất biến.
- Processed manifest ghi checksum và counts.
- Import dùng stable IDs và idempotent `MERGE`.
- Runtime manifest quyết định reuse/rebuild.
- Model, vLLM version, context và GPU utilization được cố định.
- Evaluation labels và results được lưu trong `experiments`.
- Tài liệu nguồn quan trọng được bảo vệ bằng SHA-256.

Các workflow chính:

```bash
make setup
make data DATA_COUNT=2000
make llm-setup
make llm-run
make run
make test
make experiments
make evaluation-corpora
make neo4j-benchmark
```

## 16. Cấu trúc repository

```text
advanced_database/
├── src/
│   ├── api/                 # FastAPI + static UI
│   ├── ingestion/           # TMDB/IMDb acquisition
│   ├── processing/          # cleaning, ER, normalized artifacts
│   ├── kg/                  # Neo4j import/repository/query/RDF export
│   ├── qa/                  # planner, linker, compiler, fallback, answer
│   ├── recommendation/      # IDF graph ranker + explanation
│   └── runtime/             # idempotent serving preparation
├── cypher/                  # constraints, examples, reasoning
├── ontology/                # OWL/Turtle
├── sparql/                  # SPARQL equivalents
├── experiments/             # evaluators, labels, measured results
├── tests/                   # unit/API/integration + fixtures
├── docs/                    # plans, outlines, architecture, this document
├── Makefile
├── docker-compose.yml
└── pyproject.toml
```

## 17. Giới hạn và hướng phát triển

Giới hạn hiện tại:

- Query compiler chưa bao phủ mọi tổ hợp có thể biểu diễn trong schema.
- Aggregate hiện chủ yếu hỗ trợ xếp hạng Person/đạo diễn theo Movie và Genre.
- `describe` hiện dùng đường biên dịch Movie-oriented.
- LLM planner chưa có bộ benchmark độc lập đủ lớn.
- QA conversation chỉ lưu lịch sử hiển thị, chưa có backend conversational state.
- Một máy GPU đơn là single point of failure cho nhánh LLM; fallback vẫn hoạt động.

Ưu tiên tiếp theo:

1. Xây corpus 100–200 câu hỏi tiếng Việt và đo QueryPlan/execution accuracy.
2. Mở rộng compiler theo competency questions thực tế, không mở Cypher tự do.
3. Thêm ambiguity handling khi nhiều entity cùng tên.
4. Thêm request timeout, rate limit và structured logging cho production-like demo.
5. Đóng gói vLLM thành service có health check và script SSH deployment.

Mọi mở rộng phải giữ nguyên nguyên tắc: LLM lập kế hoạch; compiler kiểm soát truy
vấn; Neo4j cung cấp dữ liệu và bằng chứng.
