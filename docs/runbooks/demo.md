# Hướng dẫn demo Movie Knowledge Graph

Mục tiêu của buổi demo là chứng minh toàn bộ chuỗi:

```text
TMDB + IMDb → xử lý dữ liệu → Neo4j → truy vấn/suy diễn
            → QA → recommendation → RDF/OWL/SPARQL → đánh giá
```

Thời lượng đề xuất: 12–15 phút. Không chạy `make data` trong buổi demo vì bước
thu thập phụ thuộc Internet. Dùng snapshot 4.999 phim hợp lệ đã chuẩn bị sẵn.

## A. Chuẩn bị trước buổi demo

### Bước A1 — Kiểm tra dữ liệu và Docker image

```bash
cd ~/VNPTAI/advanced_database
test -f data/processed/manifest.json && echo "Dataset: OK"
docker image inspect neo4j:5.26-community >/dev/null && echo "Neo4j image: OK"
```

Kết quả cần có:

```text
Dataset: OK
Neo4j image: OK
```

Nếu thiếu image, tải trước khi đến buổi demo:

```bash
docker pull neo4j:5.26-community
```

### Bước A2 — Chạy thử ứng dụng

```bash
make setup
make demo
```

Chỉ tiếp tục khi terminal hiển thị:

- container Neo4j `Healthy`;
- graph có trạng thái `reused` hoặc `imported`;
- validation có `"valid": true`;
- Uvicorn chạy tại `http://127.0.0.1:8000`.

Mở thử ba địa chỉ:

- Web UI: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- Neo4j Browser: `http://127.0.0.1:7474/`

Sau khi kiểm tra, nhấn `Ctrl+C` rồi chạy:

```bash
make stop
```

### Bước A3 — Chuẩn bị artifact RDF/OWL/SPARQL

Chạy trước để không phải chờ materialization trong lúc trình bày:

```bash
cd ~/VNPTAI/advanced_database

.venv/bin/python -m src.kg.export_rdf \
  --output data/processed/demo_movies.ttl

.venv/bin/python -m src.kg.semantic_reasoning \
  --input data/processed/demo_movies.ttl \
  --output data/processed/demo_movies.inferred.ttl \
  --report data/processed/demo_semantic_reasoning.json

.venv/bin/python -m src.kg.sparql_catalog \
  --input data/processed/demo_movies.inferred.ttl \
  --output data/processed/demo_sparql_execution.json
```

Kiểm tra hai report đã được tạo:

```bash
test -f data/processed/demo_semantic_reasoning.json && echo "Semantic report: OK"
test -f data/processed/demo_sparql_execution.json && echo "SPARQL report: OK"
```

## B. Trình tự demo trực tiếp

| Bước | Nội dung | Thời gian |
|---:|---|---:|
| 1 | Khởi động và validation | 1 phút |
| 2 | Dataset đa nguồn và provenance | 1 phút |
| 3 | Schema và truy vấn graph | 3 phút |
| 4 | Suy diễn có bằng chứng | 2 phút |
| 5 | QA và entity linking | 2 phút |
| 6 | Recommendation có giải thích | 2 phút |
| 7 | RDF/OWL/SPARQL | 2 phút |
| 8 | Kết quả đánh giá và kết luận | 2 phút |

### Bước 1 — Khởi động hệ thống

Mở Terminal 1 và chạy:

```bash
cd ~/VNPTAI/advanced_database
make demo
```

Giữ terminal này chạy trong suốt buổi demo.

Điểm cần nói:

- `runtime.prepare` so checksum và số Movie với graph hiện tại;
- nếu snapshot không đổi, graph được tái sử dụng thay vì import lại;
- validation kiểm tra orphan, duplicate ID, property bắt buộc, kiểu/hướng quan hệ
  và supporting evidence của derived fact.

Kết quả mong đợi: `movies: 4999`, `graph: reused` và `valid: true`.

### Bước 2 — Trình bày dataset đa nguồn

Mở Terminal 2:

```bash
cd ~/VNPTAI/advanced_database
python3 -m json.tool data/processed/manifest.json
```

Chỉ vào các trường:

- `source_sha256`: định danh chính xác snapshot TMDB;
- `tmdb_movies_with_imdb_id` và `matched_ratings`: exact join IMDb;
- `counts`: số node/edge table đã chuẩn hóa;
- `quality`: duplicate, missing, invalid edge và coverage.

Điểm cần nói: TMDB là nguồn graph chính; IMDb chỉ enrich Movie bằng exact
`imdb_id`. `rating` của TMDB và `imdb_rating` không bị trộn.

### Bước 3 — Trình bày schema và truy vấn graph

Mở Neo4j Browser tại `http://127.0.0.1:7474/` và đăng nhập:

```text
Username: neo4j
Password: change-me
```

#### 3.1. Hiển thị schema

```cypher
CALL db.schema.visualization();
```

Giải thích năm node chính: `Movie`, `Person`, `Genre`, `Keyword`, `Studio`; một
`Person` có thể vừa `ACTED_IN` vừa `DIRECTED`.

#### 3.2. Hiển thị quy mô graph live

```cypher
MATCH (n)
UNWIND labels(n) AS label
RETURN label, count(*) AS nodes
ORDER BY nodes DESC;
```

```cypher
MATCH ()-[r]->()
RETURN type(r) AS relationship, count(*) AS total
ORDER BY total DESC;
```

#### 3.3. Chứng minh provenance của Inception

```cypher
MATCH (m:Movie {tmdb_id: 27205})
OPTIONAL MATCH (d:Person)-[:DIRECTED]->(m)
RETURN m.title AS movie,
       m.rating AS tmdb_rating,
       m.imdb_rating AS imdb_rating,
       m.imdb_votes AS imdb_votes,
       collect(DISTINCT d.name) AS directors;
```

#### 3.4. Truy vấn multi-hop và aggregation

```cypher
MATCH (p:Person)-[:DIRECTED]->(m:Movie)-[:HAS_GENRE]->(g:Genre)
WHERE g.name = 'Action'
RETURN p.name AS director, count(DISTINCT m) AS movies
ORDER BY movies DESC
LIMIT 10;
```

#### 3.5. Shortest path trực quan

```cypher
MATCH (a:Person {name: 'Leonardo DiCaprio'}),
      (b:Person {name: 'Christian Bale'})
MATCH p = shortestPath((a)-[*..8]-(b))
RETURN p;
```

Chọn chế độ Graph trong Neo4j Browser để trình bày đường liên hệ.

### Bước 4 — Trình bày suy diễn có bằng chứng

Chạy trong Neo4j Browser:

```cypher
MATCH (a:Person {name: 'Leonardo DiCaprio'})-[r:CO_STARRED_WITH]-(b:Person)
RETURN b.name AS co_star,
       r.movie_count AS shared_movies,
       r.derived AS derived,
       r.evidence_movie_ids AS evidence
ORDER BY shared_movies DESC, co_star
LIMIT 10;
```

Sau đó đối chiếu một derived fact với phim support:

```cypher
MATCH (a:Person {name: 'Leonardo DiCaprio'})-[:ACTED_IN]->(m:Movie)
      <-[:ACTED_IN]-(b:Person {name: 'Tom Hardy'})
RETURN m.tmdb_id AS movie_id, m.title AS supporting_movie;
```

Điểm cần nói: `CO_STARRED_WITH` không phải dữ liệu TMDB gốc. Quan hệ được suy ra
từ hai cạnh `ACTED_IN`, mang `derived: true`, `movie_count` và danh sách movie ID
làm bằng chứng.

### Bước 5 — Trình bày QA và entity linking

Mở Web UI tại `http://127.0.0.1:8000/`, chọn tab hỏi–đáp và hỏi lần lượt:

```text
Những phim nào do Christopher Nolan đạo diễn?
```

```text
Diễn viên nào đóng trong phim Inception?
```

```text
Phim chung của Christian Bale và Tom Hardy?
```

```text
Đường liên hệ giữa Leonardo DiCaprio và Christian Bale?
```

```text
Phim tương tự Inception?
```

Với mỗi câu, chỉ vào evidence và giải thích:

1. câu hỏi được nhận diện thành một trong chín intent;
2. tên được link về canonical entity và stable ID;
3. backend chỉ chạy Cypher có tham số trong query catalog cố định;
4. câu trả lời được dựng từ record/path Neo4j.

### Bước 6 — Trình bày recommendation có giải thích

Trong Web UI:

1. chuyển sang tab recommendation;
2. nhập `Inception`;
3. chọn đúng phim theo năm phát hành;
4. chọn top 5 và chạy gợi ý;
5. mở phần giải thích của từng kết quả.

Công thức đóng góp của shared feature:

```text
type_weight × (1 + ln((N + 1) / (df + 1)))
```

Điểm cần nói:

- feature phổ biến bị giảm ảnh hưởng, feature hiếm được ưu tiên;
- director, actor, keyword, genre và studio có trọng số khác nhau;
- explanation liệt kê đúng các feature đã đóng góp vào score;
- đây là graph-native recommendation chạy trực tiếp trong Neo4j.

Nếu cần chứng minh bằng API, mở Swagger và chạy `POST /recommend` với:

```json
{
  "movie_id": 27205,
  "top_k": 5
}
```

### Bước 7 — Trình bày RDF/OWL và SPARQL

Trong Terminal 2, hiển thị report đã chuẩn bị:

```bash
python3 -m json.tool data/processed/demo_semantic_reasoning.json
python3 -m json.tool data/processed/demo_sparql_execution.json
```

Kết quả đã kiểm tra trên snapshot hiện tại:

```text
Triples trước materialization: 156491
Triples sau materialization:   192692
Triples suy diễn thêm:          36201
Semantic violation:                 0
SPARQL queries thực thi:            10
```

Điểm cần nói:

- Neo4j/property graph phục vụ truy vấn vận hành và traversal;
- RDF/OWL là standards view có thể trao đổi;
- materializer minh họa domain/range, inverse và symmetric property;
- validator kiểm tra functional property, disjoint class và title bắt buộc;
- query SPARQL inference-enabled sử dụng inverse relation `hasActor` chỉ xuất
  hiện sau materialization.

### Bước 8 — Trình bày kết quả đánh giá

Trong Terminal 2:

```bash
sed -n '1,80p' experiments/results/summary/quality_metrics.md
sed -n '1,80p' experiments/results/summary/benchmark_comparison.md
```

Các số cần nhấn mạnh:

- QA smoke: 20/20 có evidence;
- recommendation: P@10 `0,635`, NDCG@10 `0,672` trên 20 case silver;
- entity resolution đạt P=`1,000`, R=`0,933`, F1=`0,966`; co-star precision `1,00`;
  quality audit có zero identity/consistency violation và 100% provenance;
- semantic và structural validation không có violation;
- SQLite nhanh hơn trong bốn query baseline đã đo.

Phải nói rõ: metric corpus silver chỉ áp dụng cho case/rubric/snapshot đã khai
báo; benchmark có bốn induced snapshot 500/1.000/2.000/4.999 nhưng chưa chứng minh
scalability tổng quát hay khẳng định một database luôn nhanh hơn database còn
lại. Jena/Fuseki là workflow evaluation riêng, không cần bật trong `make demo`.

Số node/relationship live có thể khác artifact đánh giá cũ nếu snapshot được tạo
lại. Khi trình bày, lấy số live từ output `make demo`; chỉ dùng file evaluation
cho đúng experiment snapshot đã ghi trong artifact.

## C. Kết thúc demo

Nhấn `Ctrl+C` trong Terminal 1, sau đó chạy:

```bash
make stop
```

Ba câu kết luận:

1. Graph phù hợp tự nhiên với dữ liệu phim nhiều–nhiều và truy vấn multi-hop.
2. Answer, recommendation và derived fact đều có evidence truy ngược được.
3. Dự án kết hợp property graph vận hành với RDF/OWL tiêu chuẩn và công bố rõ
   giới hạn của evaluation, benchmark.

## D. Phương án dự phòng

- Không có Internet: vẫn demo được vì raw/processed snapshot và Docker image đã
  chuẩn bị local.
- Web UI lỗi: dùng Swagger tại `/docs` để gọi `/health`, `/stats`, `/ask` và
  `/recommend`.
- API lỗi nhưng Neo4j còn chạy: tiếp tục demo schema, Cypher, suy diễn và artifact
  semantic/evaluation.
- Neo4j Browser khó trình chiếu: dùng runbook DBeaver tại
  `docs/runbooks/dbeaver-neo4j.md` làm phương án thay thế.
