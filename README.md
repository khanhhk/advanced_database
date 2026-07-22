# Movie Knowledge Graph

Project Knowledge Graph hoàn chỉnh cho miền phim: thu thập TMDB/IMDb, pipeline chuẩn hóa, Neo4j Property Graph, RDF/OWL, reasoning, hỏi–đáp theo intent/template, gợi ý có giải thích, UI và evaluation. Ứng dụng chỉ chạy trên dữ liệu TMDB thật đã được thu thập và import vào Neo4j.

## Chạy nhanh

Yêu cầu Python 3.11+.

```bash
make setup
make demo
```

Không cần tự activate virtual environment: Makefile luôn gọi executable trong
`.venv`. Snapshot đã xử lý có thể được dùng lại mà không cần gọi TMDB/IMDb khi
demo. Chạy `make help` để xem các lệnh chính:

```bash
make setup             # tạo .env, .venv và cài dependencies
make data              # thu thập/enrich/chuẩn hóa dữ liệu khi cần snapshot mới
make demo              # dựng Neo4j, import khi cần và chạy API/UI
make test              # unit/API + integration trên Neo4j test riêng
make stop              # dừng Docker nhưng giữ data volume
```

Swagger UI: `http://localhost:8000/docs`.
Web demo: `http://localhost:8000/`.

Kịch bản trình bày đầy đủ gồm graph, multi-hop query, inference, QA,
recommendation, RDF/OWL/SPARQL và evidence đánh giá nằm tại
[docs/runbooks/demo.md](docs/runbooks/demo.md).

Giao diện gồm hai tab: hội thoại Knowledge Graph nhiều lượt và gợi ý phim có
giải thích. Recommendation UI cho phép tìm/chọn phim
theo tên và năm phát hành; TMDB ID chỉ được lưu nội bộ. Hệ thống dùng duy nhất
IDF-weighted graph similarity.

```bash
curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question":"Những phim nào do Christopher Nolan đạo diễn?"}'
curl -X POST http://localhost:8000/recommend -H 'Content-Type: application/json' \
  -d '{"movie_id":27205,"top_k":3}'
```

## Pipeline dữ liệu và Neo4j

Chạy `make data DATA_COUNT=2000` khi cần thu thập và chuẩn hóa snapshot mới. Sau
đó `make demo` tự dựng Neo4j, import processed data và mở API/UI. Nếu chưa có data
thật, lệnh sẽ dừng và yêu cầu chạy `make data`.

Importer tạo constraints/index, dùng transaction batch + `MERGE` theo stable ID, sinh `CO_STARRED_WITH`, rồi kiểm tra orphan/duplicate/invalid edge. Có thể chạy lại không sinh bản ghi trùng. Mật khẩu Compose chỉ dành cho local demo; hãy thay trong `.env` ở môi trường khác.

Để duyệt graph và demo truy vấn dạng bảng trên DBeaver Community, xem
[runbook DBeaver + Neo4j JDBC](docs/runbooks/dbeaver-neo4j.md). Tài liệu bao gồm cách
tạo Generic JDBC driver bằng full bundle chính thức của Neo4j, chạy SQL qua lớp
dịch SQL-to-Cypher, chạy Cypher trực tiếp và xử lý lỗi kết nối thường gặp.

## Kiểm thử và artifact nghiên cứu

```bash
make test
```

Ontology nằm tại `ontology/movie_ontology.ttl`; 10 truy vấn mẫu và luật
`CO_STARRED_WITH` nằm trong `cypher/`; SPARQL mẫu nằm trong `sparql/`. Các workflow
RDF, evaluation và benchmark vẫn được giữ dưới dạng module/script trong `src/kg/`
và `experiments/`. Các lệnh đánh giá tách khỏi luồng demo:

```bash
.venv/bin/python -m experiments.evaluation.audit_knowledge_quality
.venv/bin/python -m experiments.evaluation.evaluate_entity_resolution \
  experiments/corpora/silver/entity_resolution.json \
  --output experiments/results/evaluation/entity_resolution.json
docker compose --profile semantic up -d --build jena
.venv/bin/python -m experiments.semantic.evaluate_jena
docker compose --profile semantic stop jena
docker compose --profile test up -d --wait neo4j-test
RUN_NEO4J_TESTS=1 ALLOW_NEO4J_TEST_RESET=1 \
  ALLOW_MULTISCALE_BENCHMARK=1 NEO4J_URI=bolt://localhost:7688 \
  NEO4J_PASSWORD=test-password \
  .venv/bin/python -m experiments.benchmarks.benchmark_multiscale
```

CRUD hành chính có
implementation tại `src/kg/crud.py` nhưng không mở ra public API. `make test`
dùng Neo4j test riêng trên cổng 7688 và storage tạm, không reset graph demo.

## API

- `GET /health`
- `GET /stats`
- `GET /entities/search?q=nolan`
- `POST /ask` — 9 intent, gồm tìm phim của một người mà không cần biết trước họ là diễn viên hay đạo diễn.
- `POST /recommend` — IDF-weighted graph similarity có giải thích.

## Hỏi đáp và recommendation

QA ưu tiên dùng một LLM làm Question Planner: câu hỏi tự nhiên được chuyển thành
Query Plan JSON, kiểm tra bằng Pydantic, liên kết thực thể rồi biên dịch thành
Cypher tham số hóa từ whitelist. LLM không viết Cypher và không tự trả lời.
Parser 9 intent được giữ làm fallback khi chưa cấu hình LLM. Recommendation dùng
trọng số IDF để giảm ảnh hưởng của quan
hệ quá phổ biến và ưu tiên đặc trưng chung hiếm, có tính phân biệt. Điểm của mỗi
đặc trưng chung là `type_weight * (1 + ln((N+1)/(df+1)))`; kết quả trả lại chính
các đạo diễn, diễn viên, keyword, thể loại và studio chung làm bằng chứng. Đây là
phương pháp graph-native duy nhất của API. Trên 20 case silver chạy với Neo4j
thật, phương pháp đạt P@10 `0,640` và NDCG@10 `0,677`.

`make demo` không cài lại thư viện hoặc import lại dữ liệu ở mỗi lần chạy. Make
dùng stamp dependency theo `pyproject.toml`; runtime manifest so checksum toàn bộ
processed CSV và số Movie. Graph chỉ dựng lại khi các giá trị này thay đổi. `pip check` vẫn
chạy nhanh nhưng không tải hoặc cài package.

Để bật Question Planner, đặt các biến sau trong `.env` rồi chạy lại `make demo`:

```dotenv
LLM_API_KEY=local
LLM_BASE_URL=http://127.0.0.1:8001/v1
LLM_MODEL=Qwen/Qwen3-8B-AWQ
LLM_TIMEOUT=60
```

Endpoint phải tương thích `POST /chat/completions` và JSON response format. Nếu
không có `LLM_API_KEY` hoặc `LLM_MODEL`, QA vẫn chạy bằng parser deterministic.

GPU runtime được tách khỏi `.venv` của ứng dụng. Trên RTX 3060 12 GB:

```bash
make llm-setup  # chạy một lần; cài vLLM 0.25.0 trong .venv-llm
make llm-run    # phục vụ Qwen3-8B-AWQ tại 127.0.0.1:8001
```

Giữ terminal model hoạt động rồi chạy `make demo` ở terminal khác. Lệnh dùng
native sampler vì máy chỉ có NVIDIA driver, không yêu cầu CUDA toolkit/nvcc.

## Dữ liệu ngoài

Đặt `TMDB_API_KEY` trong `.env`; `TMDBClient` cache nguyên response vào
`data/raw/tmdb`. Raw data và secret được loại khỏi Git. Pipeline chỉ tải
`title.ratings.tsv.gz` của IMDb, đọc streaming trực tiếp từ gzip và giữ các dòng
khớp chính xác với `imdb_id` của phim TMDB. Không giải nén hay nạp toàn bộ IMDb
vào RAM/Neo4j. `Movie.rating` giữ rating TMDB; `Movie.imdb_rating` và
`Movie.imdb_votes` giữ dữ liệu IMDb riêng.

## Cấu trúc đầu ra và tái lập

- `data/raw`: response bất biến từ nguồn.
- `data/processed`: CSV node/edge cùng `manifest.json` chứa checksum, counts và quality metrics.
- `cypher`: constraint, query catalog và reasoning rule.
- `ontology` / `sparql`: ontology Turtle chuẩn duy nhất và query semantic tương đương.
- `experiments/results`: kết quả QA và benchmark có thể sinh lại bằng các lệnh trên.

Quy mô 2.000–5.000 phim được điều khiển bằng `DATA_COUNT`; dataset lớn và API key không được commit theo yêu cầu của đề tài.

`/ask` chạy Query Plan compiler hoặc catalog fallback có tham số và `/recommend` tính độ tương đồng
trong Neo4j; ứng dụng không tải toàn bộ graph về Python. Memory repository chỉ
được dùng nội bộ bởi test, không phải backend chạy ứng dụng.

QA được đánh giá trực tiếp trên Neo4j production tại
`experiments/results/evaluation/qa_neo4j.json`. Corpus hiện có đúng 2.000 phim. Benchmark
end-to-end Neo4j thật được lưu tại `experiments/results/benchmarks/neo4j_benchmark.csv`
(100 lần/câu, một warm-up) và cấu hình tại file `.metadata.json` tương ứng.
Benchmark kiểm soát đa quy mô 500/1.000/2.000 Movie nằm trong
`experiments/results/benchmarks/multiscale_benchmark.csv`. Apache Jena Fuseki 6.1.0 chạy
forward rule profile trên full RDF snapshot; kết quả 10/10 SPARQL nằm tại
`experiments/results/semantic/jena_semantic_evaluation.json`.

TMDB credits được giữ dưới dạng object có source ID; `Person.person_id` ưu tiên
`tmdb:<id>` thay vì hash tên, và `ACTED_IN` giữ `character`/`cast_order`. QA
Neo4j liên kết slot về thực thể canonical, dùng stable ID để chạy catalog Cypher
và đưa ID/confidence vào evidence. Tên canonical chỉ là fallback cho fixture cũ
không có ID. Các evaluator có sẵn tại
`experiments/evaluation/evaluate_entity_resolution.py`, `evaluate_reasoning.py`
và `evaluate_recommendation_neo4j.py`. Các module trong `experiments/` sinh bộ
silver có evidence/rubric (100 entity cases, 50 reasoning facts, 20
recommendation cases). Đây là benchmark tất định dựa trên source ID và hard
negative, không phải ground truth đại diện cho toàn bộ dữ liệu thực tế.
