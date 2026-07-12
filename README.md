# Movie Knowledge Graph

Project Knowledge Graph hoàn chỉnh cho miền phim: thu thập TMDB/IMDb, pipeline chuẩn hóa, Neo4j Property Graph, RDF/OWL, reasoning, hỏi–đáp theo intent/template, gợi ý có giải thích, UI và evaluation. Mặc định API dùng seed dataset trong bộ nhớ để demo không phụ thuộc mạng; production backend dùng Neo4j.

## Chạy nhanh

Yêu cầu Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn src.api.main:app --reload
```

Swagger UI: `http://localhost:8000/docs`.
Web demo: `http://localhost:8000/`.

```bash
curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question":"Những phim nào do Christopher Nolan đạo diễn?"}'
curl -X POST http://localhost:8000/recommend -H 'Content-Type: application/json' \
  -d '{"movie_id":27205,"top_k":3}'
```

## Pipeline dữ liệu và Neo4j

```bash
cp .env.example .env
docker compose up -d neo4j
# tùy chọn: thu thập raw records (cần TMDB_API_KEY)
python -m src.ingestion.collect_tmdb --ids 27205,157336,155
# dataset đánh giá đầy đủ (cần TMDB_API_KEY, cache raw để chạy lại an toàn)
python -m src.ingestion.collect_tmdb --count 2000
# tạo 5 node tables, 5 edge tables và quality manifest
python -m src.processing.pipeline --input data/raw/tmdb_movies.json
python -m src.kg.load_neo4j
# đổi KG_BACKEND=neo4j trong .env
uvicorn src.api.main:app
```

Importer tạo constraints/index, dùng transaction batch + `MERGE` theo stable ID, sinh `CO_STARRED_WITH`, rồi kiểm tra orphan/duplicate/invalid edge. Có thể chạy lại không sinh bản ghi trùng. Mật khẩu Compose chỉ dành cho local demo; hãy thay trong `.env` ở môi trường khác.

## RDF và kiểm thử

```bash
python -m src.kg.export_rdf
pytest
RUN_NEO4J_TESTS=1 pytest -m neo4j
python experiments/evaluate.py
python experiments/benchmark_queries.py --iterations 100 --scales 5,100,1000,5000
```

Ontology nằm tại `ontology/movie_ontology.ttl`; 10 truy vấn mẫu và luật `CO_STARRED_WITH` nằm trong `cypher/`; SPARQL mẫu nằm trong `sparql/`.

## API

- `GET /health`
- `GET /stats`
- `GET /entities/search?q=nolan`
- `POST /ask` — 8 intent: phim theo đạo diễn, cast, phim chung, genre/rating, co-star, director/genre, shortest path, similar movie.
- `POST /recommend` — `weighted_jaccard` hoặc `overlap`, trả score và metadata chung.

## Dữ liệu ngoài

Đặt `TMDB_API_KEY` trong `.env`; `TMDBClient` cache nguyên response vào `data/raw/tmdb`. Raw data và secret được loại khỏi Git. IMDb TSV hoặc TSV.GZ có thể đọc bằng `src.ingestion.imdb_loader.load_tsv`.

## Cấu trúc đầu ra và tái lập

- `data/raw`: response bất biến từ nguồn.
- `data/processed`: CSV node/edge cùng `manifest.json` chứa checksum, counts và quality metrics.
- `cypher`: constraint, query catalog và reasoning rule.
- `ontology` / `sparql`: ontology OWL/Turtle và query semantic tương đương.
- `experiments/results`: kết quả QA và benchmark có thể sinh lại bằng các lệnh trên.

Seed data chỉ phục vụ demo nhanh. Quy mô 2.000–5.000 phim đạt được bằng cách truyền danh sách TMDB ID lớn hơn vào collector; dataset lớn và API key không được commit theo yêu cầu của đề tài.

Khi `KG_BACKEND=neo4j`, `/ask` chạy catalog Cypher cố định có tham số và
`/recommend` tính độ tương đồng trong Neo4j; ứng dụng không tải toàn bộ graph về
Python. Backend memory chỉ dành cho smoke test và demo offline.

`experiments/results/qa.json` là smoke test trên seed nhỏ, không phải đánh giá
production. Benchmark memory được gắn nhãn `memory-synthetic` và ghi rõ
`movie_count`; benchmark Neo4j và các chỉ số entity resolution/recommendation
cần được sinh trên corpus gán nhãn trước khi đưa vào báo cáo cuối.
