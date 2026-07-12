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
make data              # thu thập TMDB + IMDb ratings và chuẩn hóa 2.000 phim
make semantic-index    # cài local embedding, tạo full-text/vector index
make imdb-data         # chỉ tải IMDb title.ratings.tsv.gz
make run               # dựng Neo4j + import data + chạy API/UI
make experiments
make stop
```

Swagger UI: `http://localhost:8000/docs`.
Web demo: `http://localhost:8000/`.

Giao diện gồm ba tab: hội thoại Knowledge Graph nhiều lượt, tìm phim bằng mô tả
tự nhiên và gợi ý phim có giải thích. Recommendation UI giải thích rõ TMDB ID,
số kết quả và cho phép so sánh overlap/Jaccard/hybrid; người dùng thông thường
nên giữ lựa chọn “Khuyến nghị — quan hệ chung”.

```bash
curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question":"Những phim nào do Christopher Nolan đạo diễn?"}'
curl -X POST http://localhost:8000/recommend -H 'Content-Type: application/json' \
  -d '{"movie_id":27205,"top_k":3}'
curl -X POST http://localhost:8000/search -H 'Content-Type: application/json' \
  -d '{"query":"phim khoa học viễn tưởng về không gian rating trên 7","top_k":5}'
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
- `POST /search` — multilingual vector retrieval kết hợp genre/rating filter trên graph.
- `POST /ask` — 8 intent: phim theo đạo diễn, cast, phim chung, genre/rating, co-star, director/genre, shortest path, similar movie.
- `POST /recommend` — mặc định `overlap`; hỗ trợ `weighted_jaccard` và `hybrid` thử nghiệm.

## Semantic search, hybrid QA và recommendation

`make semantic-index` dùng FastEmbed với mô hình multilingual chạy cục bộ để
embedding `title + overview + genres + keywords` của 2.000 phim thành vector 384
chiều. Neo4j lưu vector index `movie_embedding` và full-text indexes
`movie_text`/`entity_names`; nội dung phim không được gửi tới API embedding ngoài.

QA giữ catalog Cypher tham số hóa cho 8 intent. Entity linker ưu tiên full-text
candidate rồi fuzzy rerank; câu ngoài catalog chuyển sang semantic retrieval có
evidence thay vì trả lỗi ngay. Đây là controlled hybrid GraphRAG, chưa bật
LLM-to-Cypher tự do. Recommendation hybrid thử nghiệm kết hợp 75% weighted graph Jaccard,
20% cosine nội dung và 5% rating có vote-confidence, đồng thời trả riêng từng
score và metadata chung để giải thích. Ablation silver hiện cho thấy overlap
tốt hơn hybrid, nên production default vẫn là overlap; không chọn công nghệ mới
chỉ vì mới. Các candidate thiếu overview/vote bị giới hạn.

`make run` không cài lại thư viện hoặc import lại dữ liệu ở mỗi lần chạy. Make
dùng stamp dependency theo `pyproject.toml`; runtime manifest so checksum nguồn,
số Movie và embedding coverage. Graph/index chỉ dựng lại khi các giá trị này
thay đổi. `pip check` vẫn chạy nhanh nhưng không tải hoặc cài package.

## Dữ liệu ngoài

Đặt `TMDB_API_KEY` trong `.env`; `TMDBClient` cache nguyên response vào `data/raw/tmdb`. Raw data và secret được loại khỏi Git. Pipeline chỉ tải `title.ratings.tsv.gz` của IMDb, đọc streaming trực tiếp từ gzip và giữ các dòng khớp chính xác với `imdb_id` của phim TMDB. Không giải nén hay nạp toàn bộ IMDb vào RAM/Neo4j. `Movie.rating` giữ rating TMDB; `Movie.imdb_rating` và `Movie.imdb_votes` giữ dữ liệu IMDb riêng. Dùng `make clean-imdb-raw` khi cần giải phóng file nén sau khi đã xử lý.

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

`experiments/results/qa.json` là smoke test 10 câu trên corpus TMDB hiện có,
không phải đánh giá production. Benchmark memory được gắn nhãn
`memory-synthetic` và ghi rõ
`movie_count`. Corpus hiện có đúng 2.000 phim. Benchmark end-to-end Neo4j thật
được lưu tại `experiments/results/neo4j_benchmark.csv` (100 lần/câu, một warm-up)
và cấu hình tại file `.metadata.json` tương ứng.

TMDB credits được giữ dưới dạng object có source ID; `Person.person_id` ưu tiên
`tmdb:<id>` thay vì hash tên, và `ACTED_IN` giữ `character`/`cast_order`. QA
Neo4j liên kết slot phim/người về tên canonical trước khi chạy catalog Cypher và
đưa confidence vào evidence. Các evaluator có sẵn tại
`experiments/evaluate_entity_resolution.py`, `evaluate_reasoning.py` và
`evaluate_recommendation.py`; schema corpus review nằm tại
`experiments/labels/README.md`. `make evaluation-corpora` sinh bộ silver có
evidence/rubric (100 entity cases, 50 reasoning facts, 20 recommendation cases).
Phải gọi đúng là silver evaluation cho đến khi có reviewer độc lập.
