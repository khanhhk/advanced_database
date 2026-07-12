# Movie Knowledge Graph

Project Knowledge Graph hoàn chỉnh cho miền phim: thu thập TMDB/IMDb, pipeline chuẩn hóa, Neo4j Property Graph, RDF/OWL, reasoning, hỏi–đáp theo intent/template, gợi ý có giải thích, UI và evaluation. Ứng dụng chỉ chạy trên dữ liệu TMDB thật đã được thu thập và import vào Neo4j.

## Chạy nhanh

Yêu cầu Python 3.11+.

```bash
make setup
make test
make run
```

Không cần tự activate virtual environment: Makefile luôn gọi executable trong
`.venv`. Chạy `make help` để xem toàn bộ workflow. Các lệnh thường dùng:

```bash
make setup             # tạo .env + .venv + cài và kiểm tra dependencies
make test              # toàn bộ test, gồm cả integration Neo4j
make data              # thu thập + chuẩn hóa 2.000 phim
make run               # dựng Neo4j + import data + chạy API/UI
make experiments
make stop
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

Chạy `make data DATA_COUNT=2000` để thu thập và chuẩn hóa dữ liệu. Sau đó
`make run` tự dựng Neo4j, import processed data và mở API/UI. Nếu chưa có data
thật, lệnh sẽ dừng và yêu cầu chạy `make data`.

Importer tạo constraints/index, dùng transaction batch + `MERGE` theo stable ID, sinh `CO_STARRED_WITH`, rồi kiểm tra orphan/duplicate/invalid edge. Có thể chạy lại không sinh bản ghi trùng. Mật khẩu Compose chỉ dành cho local demo; hãy thay trong `.env` ở môi trường khác.

## RDF và kiểm thử

```bash
make test
make experiments
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

Quy mô 2.000–5.000 phim được điều khiển bằng `DATA_COUNT`; dataset lớn và API key không được commit theo yêu cầu của đề tài.

`/ask` chạy catalog Cypher cố định có tham số và `/recommend` tính độ tương đồng
trong Neo4j; ứng dụng không tải toàn bộ graph về Python. Memory repository chỉ
được dùng nội bộ bởi test, không phải backend chạy ứng dụng.

`experiments/results/qa.json` là smoke test trên seed nhỏ, không phải đánh giá
production. Benchmark memory được gắn nhãn `memory-synthetic` và ghi rõ
`movie_count`; benchmark Neo4j và các chỉ số entity resolution/recommendation
cần được sinh trên corpus gán nhãn trước khi đưa vào báo cáo cuối.
