# Kế hoạch triển khai code

## 1. Cấu trúc repository

```text
movie-knowledge-graph/
├── README.md
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── samples/
├── ontology/
│   └── movie_ontology.ttl
├── cypher/
│   ├── constraints.cypher
│   ├── queries.cypher
│   └── reasoning.cypher
├── sparql/
│   └── queries.rq
├── src/
│   ├── ingestion/
│   │   ├── tmdb_client.py
│   │   └── imdb_loader.py
│   ├── processing/
│   │   ├── clean.py
│   │   └── entity_resolution.py
│   ├── kg/
│   │   ├── load_neo4j.py
│   │   ├── export_rdf.py
│   │   └── repository.py
│   ├── qa/
│   │   ├── intents.py
│   │   ├── entity_linker.py
│   │   └── service.py
│   ├── recommendation/
│   │   └── service.py
│   └── api/
│       └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── test_questions.json
├── experiments/
│   ├── corpora/       # silver corpus và human review
│   ├── evaluation/    # quality, entity, QA, reasoning, recommendation
│   ├── benchmarks/    # Neo4j, SQLite và multi-scale
│   ├── semantic/      # Jena/Fuseki và SPARQL evaluation
│   ├── reporting/     # tổng hợp bảng/biểu đồ bằng chứng
│   └── results/       # artifact phân nhóm theo workflow
└── report_latex/
```

## 2. Thứ tự triển khai

### Giai đoạn 1 — Nền tảng

- Khởi tạo Python project và dependency management.
- Tạo `.env.example` nhưng không commit `.env`.
- Tạo Docker Compose cho Neo4j.
- Thêm logging, configuration và test framework.
- Viết README hướng dẫn chạy tối thiểu.

### Giai đoạn 2 — Ingestion

- Xây `TMDBClient` có retry, rate limiting và cache.
- Thu thập movie details, credits, keywords và external IDs.
- Viết loader cho IMDb TSV/CSV.
- Lưu raw data bất biến; không sửa trực tiếp dữ liệu raw.

### Giai đoạn 3 — Processing

- Chuẩn hóa schema dữ liệu.
- Validate các trường bắt buộc.
- Tách node table và relationship table.
- Entity resolution ưu tiên ID chính xác.
- Ghi log fuzzy matches và confidence score.

### Giai đoạn 4 — Graph loading

- Tạo uniqueness constraints.
- Import node trước, relationship sau.
- Dùng transaction batch.
- Dùng `MERGE` theo stable ID.
- Tạo validation query sau import.

### Giai đoạn 5 — Query và reasoning

- Đưa Cypher vào file riêng thay vì hard-code rải rác.
- Viết repository layer cho Neo4j.
- Viết query từ đơn giản đến multi-hop.
- Materialize `CO_STARRED_WITH` và lưu thuộc tính `derived: true`.
- Xuất RDF/Turtle cho tập con dữ liệu.

### Giai đoạn 6 — API

- Xây FastAPI app và dependency quản lý Neo4j driver.
- Validate request bằng Pydantic.
- Dùng parameterized Cypher.
- Chuẩn hóa error response.
- Thêm timeout và health check.

### Giai đoạn 7 — QA

- Định nghĩa danh sách intent.
- Viết rule/pattern nhận diện intent.
- Trích slot và liên kết entity với KG.
- Ánh xạ intent sang Cypher template.
- Trả answer cùng evidence.

### Giai đoạn 8 — Recommendation

- Cài đặt IDF-weighted graph similarity, ưu tiên quan hệ chung hiếm và trả evidence theo từng loại quan hệ.
- Thử weighted Jaccard.
- Trả danh sách shared actors/directors/genres/keywords.
- Benchmark và chọn công thức cuối cùng dựa trên thực nghiệm.

### Giai đoạn 9 — Testing và evaluation

- Unit test cleaning, matching, intent và scoring.
- Integration test Neo4j repository và API.
- Test pipeline idempotency.
- Benchmark query ở nhiều quy mô.
- Lưu kết quả thí nghiệm dưới CSV/JSON để tái lập biểu đồ.

## 3. API tối thiểu

### `POST /ask`

Request:

```json
{
  "question": "Những phim nào do Christopher Nolan đạo diễn?"
}
```

Response:

```json
{
  "answer": "...",
  "intent": "movies_by_director",
  "evidence": [],
  "query_time_ms": 12
}
```

### `POST /recommend`

Request:

```json
{
  "movie_id": 27205,
  "top_k": 10
}
```

Mỗi kết quả cần có:

- Movie ID và title.
- Similarity score.
- Các đạo diễn, diễn viên, thể loại hoặc từ khóa chung.
- Câu giải thích ngắn.

### Endpoint hỗ trợ

- `GET /entities/search?q=...`
- `GET /health`
- `GET /stats` — tùy chọn.

## 4. Bộ truy vấn Cypher cần có

1. Tìm phim theo đạo diễn.
2. Tìm diễn viên của một phim.
3. Tìm phim theo thể loại và rating.
4. Tìm phim chung của hai diễn viên.
5. Tìm cộng sự thường xuyên nhất của một diễn viên.
6. Tìm đạo diễn thường làm một thể loại.
7. Tìm đường ngắn nhất giữa hai người.
8. Tìm phim tương tự theo metadata chung.
9. Thống kê số node/edge theo loại.
10. Sinh và kiểm tra `CO_STARRED_WITH`.

## 5. Chiến lược test

### Unit test

- Chuẩn hóa tên và ngày.
- Loại bản ghi lỗi.
- ID matching và fuzzy matching.
- Nhận diện intent.
- Trích slot.
- Tính recommendation score.

### Integration test

- Kết nối Neo4j.
- Import seed dataset.
- Chạy Cypher template.
- Kiểm tra `/ask` và `/recommend`.
- Chạy import hai lần và xác nhận số node/edge không đổi.

### Evaluation dataset

- Khoảng 100 cặp entity match/non-match được gán nhãn thủ công.
- 20–30 câu hỏi cùng đáp án mong đợi.
- 20 phim đầu vào và danh sách gợi ý được đánh giá thủ công.
- Danh sách 50 fact suy diễn được kiểm tra thủ công.

## 6. Lệnh chạy mục tiêu

README cuối cùng nên hỗ trợ luồng tương tự:

```bash
docker compose up -d
python -m src.kg.load_neo4j
uvicorn src.api.main:app
```

Các lệnh ingestion và processing nên tách riêng để demo không cần gọi lại API bên ngoài.

## 7. Quy tắc chất lượng

- Không hard-code secret hoặc mật khẩu.
- Không nối chuỗi input vào Cypher.
- Raw data là bất biến.
- Stable ID là khóa chính, không dùng tên làm khóa duy nhất.
- Import phải idempotent.
- Mỗi fact cần truy được nguồn hoặc cách suy diễn.
- Thí nghiệm phải lưu được cấu hình và kết quả.
- Seed dataset phải đủ nhỏ để chạy demo nhanh.
