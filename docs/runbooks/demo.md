# Hướng dẫn trình diễn đồ thị tri thức phim

Mục tiêu của buổi trình diễn là chứng minh toàn bộ chuỗi:

```text
TMDB + IMDb → xử lý dữ liệu → Neo4j → truy vấn/suy diễn
            → QA → recommendation → đánh giá
```

Thời lượng đề xuất: 12–15 phút. Không chạy `make data` trong buổi trình diễn vì bước
thu thập phụ thuộc Internet. Dùng ảnh chụp dữ liệu 4.999 phim hợp lệ đã chuẩn bị sẵn.

## A. Chuẩn bị trước buổi trình diễn

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

Nếu thiếu image, tải trước khi đến buổi trình diễn:

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
- kiểm tra hợp lệ có `"valid": true`;
- Uvicorn chạy tại `http://127.0.0.1:8000`.

Mở thử ba địa chỉ:

- Web UI: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- Neo4j Browser: `http://127.0.0.1:7474/`

Sau khi kiểm tra, nhấn `Ctrl+C` rồi chạy:

```bash
make stop
```

## B. Trình tự trình diễn trực tiếp

| Bước | Nội dung | Thời gian |
|---:|---|---:|
| 1 | Khởi động và kiểm tra hợp lệ | 1 phút |
| 2 | Dataset đa nguồn và provenance | 1 phút |
| 3 | Schema và truy vấn graph | 3 phút |
| 4 | Suy diễn có bằng chứng | 2 phút |
| 5 | QA và entity linking | 2 phút |
| 6 | Gợi ý có giải thích | 2 phút |
| 7 | Kết quả đánh giá và kết luận | 2 phút |

### Bước 1 — Khởi động hệ thống

Mở Terminal 1 và chạy:

```bash
cd ~/VNPTAI/advanced_database
make demo
```

Giữ terminal này chạy trong suốt buổi trình diễn.

Điểm cần nói:

- `runtime.prepare` so checksum và số Movie với graph hiện tại;
- nếu ảnh chụp dữ liệu không đổi, graph được tái sử dụng thay vì import lại;
- kiểm tra hợp lệ kiểm tra orphan, duplicate ID, property bắt buộc, kiểu/hướng quan hệ
  và supporting bằng chứng của derived fact.

Kết quả mong đợi: `movies: 4999`, `graph: reused` và `valid: true`.

### Bước 2 — Trình bày dataset đa nguồn

Mở Terminal 2:

```bash
cd ~/VNPTAI/advanced_database
python3 -m json.tool data/processed/manifest.json
```

Chỉ vào các trường:

- `source_sha256`: định danh chính xác ảnh chụp dữ liệu TMDB;
- `tmdb_movies_with_imdb_id` và `matched_ratings`: exact join IMDb;
- `counts`: số node/edge table đã chuẩn hóa;
- `quality`: duplicate, missing, invalid edge và độ bao phủ.

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

Với mỗi câu, chỉ vào bằng chứng và giải thích:

1. câu hỏi được nhận diện thành một trong chín ý định;
2. tên được link về canonical entity và stable ID;
3. backend chỉ chạy Cypher có tham số trong query catalog cố định;
4. câu trả lời được dựng từ record/path Neo4j.

#### 5.1. Kiểm chứng kết quả Web UI trong Neo4j Browser

Sau câu hỏi về diễn viên của `Inception`, mở Neo4j Browser và chạy:

```cypher
MATCH (p:Person)-[r:ACTED_IN]->(m:Movie)
WHERE toLower(m.title) = toLower('Inception')
RETURN p.name AS actor, r.character AS character
ORDER BY r.cast_order
LIMIT 50;
```

Đối chiếu danh sách với Web UI. Sau câu hỏi về phim chung của Christian Bale và
Tom Hardy, chạy:

```cypher
MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(b:Person)
WHERE toLower(a.name) = toLower('Christian Bale')
  AND toLower(b.name) = toLower('Tom Hardy')
RETURN DISTINCT m.title AS common_movie;
```

Điểm phải nói: Web UI gửi câu tự nhiên qua FastAPI để chọn Cypher có tham số;
Neo4j Browser nhận Cypher trực tiếp. Cả hai cùng đọc một graph nên tập fact phải
thống nhất, dù cách trình bày kết quả khác nhau.

### Bước 6 — Trình bày gợi ý có giải thích

Trong Web UI:

1. chuyển sang tab gợi ý;
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
- lời giải thích liệt kê đúng các feature đã đóng góp vào score;
- đây là graph-native gợi ý chạy trực tiếp trong Neo4j.

#### 6.1. Kiểm chứng bằng chứng gợi ý trong Neo4j Browser

Ghi lại tên phim đứng đầu trên Web UI. Trong Neo4j Browser, thay `Interstellar`
bằng đúng tên vừa nhận:

```cypher
:param candidate_title => 'Interstellar';
```

Sau đó chạy:

```cypher
MATCH (source:Movie {tmdb_id: 27205})
MATCH (candidate:Movie {title: $candidate_title})
CALL (source, candidate) {
  MATCH (source)<-[:DIRECTED]-(f:Person)-[:DIRECTED]->(candidate)
  RETURN 'director' AS kind, f.name AS feature
  UNION
  MATCH (source)<-[:ACTED_IN]-(f:Person)-[:ACTED_IN]->(candidate)
  RETURN 'actor' AS kind, f.name AS feature
  UNION
  MATCH (source)-[:HAS_GENRE]->(f:Genre)<-[:HAS_GENRE]-(candidate)
  RETURN 'genre' AS kind, f.name AS feature
  UNION
  MATCH (source)-[:HAS_KEYWORD]->(f:Keyword)<-[:HAS_KEYWORD]-(candidate)
  RETURN 'keyword' AS kind, f.name AS feature
  UNION
  MATCH (source)-[:PRODUCED_BY]->(f:Studio)<-[:PRODUCED_BY]-(candidate)
  RETURN 'studio' AS kind, f.name AS feature
}
RETURN candidate.title AS recommended_movie,
       kind, collect(DISTINCT feature) AS shared_features;
```

Đối chiếu từng `shared_features` với phần giải thích của cùng phim trên Web UI.
Đây là phép kiểm chứng trực tiếp các đường graph tạo ra lời giải thích. Muốn tái
tạo chính xác điểm và thứ hạng, dùng query IDF đầy đủ trong
`src/recommendation/neo4j_service.py`; không dùng query rút gọn bên trên để tuyên
bố hai score bằng nhau.

Nếu cần chứng minh bằng API, mở Swagger và chạy `POST /recommend` với:

```json
{
  "movie_id": 27205,
  "top_k": 5
}
```

### Bước 7 — Trình bày kết quả đánh giá

Trong Terminal 2:

```bash
sed -n '1,80p' experiments/results/summary/quality_metrics.md
sed -n '1,80p' experiments/results/summary/benchmark_comparison.md
```

Các số cần nhấn mạnh:

- QA smoke: 20/20 có bằng chứng;
- gợi ý: P@10 `0,635`, NDCG@10 `0,672` trên 20 case silver;
- phân giải thực thể đạt P=`1,000`, R=`0,933`, F1=`0,966`; co-star precision `1,00`;
  quality audit có zero identity/consistency violation và 100% provenance;
- Neo4j structural validation không có violation;
- SQLite nhanh hơn trong bốn query mốc so sánh đã đo.

Phải nói rõ: metric corpus silver chỉ áp dụng cho case/rubric/ảnh chụp dữ liệu đã khai
báo; phép đo hiệu năng có bốn ảnh chụp dữ liệu con 500/1.000/2.000/4.999 nhưng chưa chứng minh
scalability tổng quát hay khẳng định một database luôn nhanh hơn database còn
lại.

Số node/relationship live có thể khác sản phẩm đầu ra đánh giá cũ nếu ảnh chụp dữ liệu được tạo
lại. Khi trình bày, lấy số trực tiếp từ đầu ra `make demo`; chỉ dùng tệp đánh giá
cho đúng experiment ảnh chụp dữ liệu đã ghi trong sản phẩm đầu ra.

## C. Kết thúc trình diễn

Nhấn `Ctrl+C` trong Terminal 1, sau đó chạy:

```bash
make stop
```

Ba câu kết luận:

1. Graph phù hợp tự nhiên với dữ liệu phim nhiều–nhiều và truy vấn multi-hop.
2. Answer, gợi ý và derived fact đều có bằng chứng truy ngược được.
3. Dự án công bố rõ giới hạn của evaluation và phép đo hiệu năng.

## D. Phương án dự phòng

- Không có Internet: vẫn trình diễn được vì raw/ảnh chụp dữ liệu đã xử lý và Docker image đã
  chuẩn bị local.
- Web UI lỗi: dùng Swagger tại `/docs` để gọi `/health`, `/stats`, `/ask` và
  `/recommend`.
- API lỗi nhưng Neo4j còn chạy: tiếp tục trình diễn schema, Cypher, suy diễn và
  các artifact evaluation.
- Neo4j Browser khó trình chiếu: dùng runbook DBeaver tại
  `docs/runbooks/dbeaver-neo4j.md` làm phương án thay thế.
