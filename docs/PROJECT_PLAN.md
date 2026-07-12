# Kế hoạch tổng thể — Movie Knowledge Graph

## 1. Bài toán

Dữ liệu phim phân tán trên nhiều nguồn và chứa nhiều quan hệ đa chiều giữa phim, diễn viên, đạo diễn, thể loại, từ khóa và hãng sản xuất. Mô hình quan hệ có thể lưu trữ dữ liệu này, nhưng các truy vấn nhiều bước thường cần nhiều phép `JOIN` và khó thể hiện ngữ nghĩa.

Project xây dựng một Knowledge Graph nhằm:

- Tích hợp dữ liệu phim từ nhiều nguồn.
- Biểu diễn rõ thực thể, quan hệ và ràng buộc ngữ nghĩa.
- Truy vấn các quan hệ nhiều bước.
- Suy ra tri thức mới từ dữ kiện hiện có.
- Cung cấp hỏi–đáp và gợi ý phim có bằng chứng giải thích.

### Câu hỏi nghiên cứu

> Knowledge Graph có thể tích hợp dữ liệu phim từ nhiều nguồn, hỗ trợ truy vấn nhiều bước, suy diễn và tạo gợi ý dễ giải thích tốt hơn mô hình dữ liệu truyền thống như thế nào?

## 2. Mục tiêu

1. Thiết kế ontology cho miền phim ảnh.
2. Xây dựng pipeline thu thập, làm sạch và liên kết thực thể.
3. Lưu trữ Knowledge Graph chính bằng Neo4j Property Graph.
4. Xây dựng tập RDF/OWL thu nhỏ để minh họa SPARQL và reasoning.
5. Xây dựng API hỏi–đáp bằng Cypher template.
6. Xây dựng hệ gợi ý phim dựa trên quan hệ đồ thị.
7. Đánh giá chất lượng dữ liệu, độ chính xác và hiệu năng hệ thống.

## 3. Phạm vi

### 3.1. Phần bắt buộc — MVP

- 2.000–5.000 phim.
- Các thực thể: `Movie`, `Person`, `Genre`, `Keyword`, `Studio`.
- Các quan hệ: `ACTED_IN`, `DIRECTED`, `HAS_GENRE`, `HAS_KEYWORD`, `PRODUCED_BY`.
- Thu thập dữ liệu chính từ TMDB.
- Liên kết với IMDb qua `imdb_id`.
- Nạp dữ liệu vào Neo4j theo batch.
- Ít nhất 10 truy vấn Cypher, trong đó có 4–5 truy vấn multi-hop.
- Suy ra quan hệ `CO_STARRED_WITH`.
- Endpoint `/ask` hỗ trợ 5–7 loại câu hỏi.
- Endpoint `/recommend` trả top-N phim và lý do gợi ý.
- Bộ test và số liệu đánh giá.

### 3.2. Phần nâng cao

- Thực thể `Award` và quan hệ `WON` lấy từ Wikidata.
- So sánh RDF/OWL/SPARQL với Neo4j/Cypher.
- LLM sinh Cypher có kiểm soát.
- Vector search trên trường `overview`.
- GraphRAG hoặc Knowledge Graph Embedding.

`Award` không thuộc MVP vì TMDB và các IMDb dataset phổ biến không cung cấp dữ liệu giải thưởng đầy đủ. Tích hợp Wikidata cũng làm tăng đáng kể khối lượng entity linking.

## 4. Mô hình tri thức

### 4.1. Node

| Node | Thuộc tính quan trọng |
|---|---|
| `Movie` | `tmdb_id`, `imdb_id`, `title`, `release_date`, `runtime`, `rating`, `popularity`, `overview` |
| `Person` | `tmdb_id`, `imdb_id`, `name`, `birthday` |
| `Genre` | `genre_id`, `name` |
| `Keyword` | `keyword_id`, `name` |
| `Studio` | `company_id`, `name`, `country` |
| `Award` | `award_id`, `name`, `category`, `year` — nâng cao |

Nên dùng một label `Person` và phân biệt vai trò bằng relationship. Một người có thể vừa là diễn viên vừa là đạo diễn.

### 4.2. Relationship

| Quan hệ | Hướng | Thuộc tính |
|---|---|---|
| `ACTED_IN` | `Person → Movie` | `character`, `cast_order` |
| `DIRECTED` | `Person → Movie` | — |
| `HAS_GENRE` | `Movie → Genre` | — |
| `HAS_KEYWORD` | `Movie → Keyword` | — |
| `PRODUCED_BY` | `Movie → Studio` | — |
| `WON` | `Movie/Person → Award` | `result` — nâng cao |
| `CO_STARRED_WITH` | `Person → Person` | `movie_count`, `derived` |

## 5. Competency questions

Ontology và hệ thống phải trả lời được tối thiểu:

1. Những phim nào do đạo diễn X thực hiện?
2. Diễn viên nào đóng trong phim Y?
3. Diễn viên nào từng đóng chung với X?
4. Hai diễn viên A và B từng đóng chung trong phim nào?
5. Phim kinh dị nào của đạo diễn X có rating trên 7?
6. Đường liên hệ giữa hai diễn viên là gì?
7. Những phim nào có chung đạo diễn, diễn viên hoặc thể loại với phim X?
8. Đạo diễn nào thường làm phim thuộc thể loại Y?
9. Cặp diễn viên nào cộng tác nhiều nhất?
10. Top-N phim tương tự phim X và lý do tương tự?

## 6. Kiến trúc

```text
TMDB API ───────┐
                ├──> Raw JSON
IMDb datasets ──┘
                      │
                      ▼
             Cleaning & Validation
                      │
                      ▼
             Entity Resolution
           ID matching + fuzzy match
                      │
             ┌────────┴────────┐
             ▼                 ▼
        CSV/Parquet         RDF/Turtle
             │                 │
             ▼                 ▼
           Neo4j          Jena/Protégé
             │
       ┌─────┴───────────┐
       ▼                 ▼
   QA service       Recommendation
       └───────┬─────────┘
               ▼
          FastAPI + UI
```

### Công nghệ đề xuất

- Python 3.11.
- Pandas hoặc Polars.
- Neo4j 5.x và `neo4j-driver`.
- FastAPI và Pydantic.
- RapidFuzz cho entity resolution.
- RDFLib để xuất RDF/Turtle.
- Protégé/Jena cho ontology và reasoning.
- Docker Compose để chạy Neo4j và ứng dụng.
- Pytest cho kiểm thử.
- Streamlit hoặc HTML/CSS/JS đơn giản cho demo.

## 7. Work package

### WP1 — Khảo sát và đặc tả

- Tổng hợp RDF, RDFS, OWL, Property Graph và Knowledge Graph.
- So sánh RDF Triple Store với Neo4j.
- Chốt phạm vi và competency questions.
- Xây data dictionary và chỉ số đánh giá.

Đầu ra: problem statement, requirements và competency questions.

### WP2 — Thiết kế ontology

- Thiết kế class, property và relationship.
- Xác định domain, range và ràng buộc cần thiết.
- Tạo ontology bằng Protégé.
- Kiểm tra consistency bằng reasoner.
- Vẽ ontology diagram.

Đầu ra: OWL, Turtle, ontology diagram và data dictionary.

### WP3 — Thu thập dữ liệu

- Gọi TMDB API theo batch.
- Thu thập movie detail, credits, keywords và external IDs.
- Tải IMDb title/rating datasets nếu cần.
- Cache response để pipeline có thể chạy lại.
- Ghi nguồn và thời gian thu thập.

Không commit API key hoặc dataset lớn lên Git.

### WP4 — Làm sạch và entity resolution

- Chuẩn hóa ID, ngày, tên và kiểu dữ liệu.
- Loại bản ghi không có trường thiết yếu.
- Khử trùng lặp.
- Khớp TMDB–IMDb bằng `imdb_id`.
- Chỉ fuzzy matching khi không có ID.
- Lưu confidence score và log trường hợp mơ hồ.

### WP5 — Xây Knowledge Graph

- Tạo constraints và indexes trước khi import.
- Nạp node và relationship theo batch bằng `MERGE`.
- Bảo đảm pipeline idempotent.
- Kiểm tra node/edge count và orphan node.
- Tạo seed dataset cho demo.

### WP6 — Truy vấn và suy diễn

- Xây ít nhất 10 Cypher query.
- Bao phủ query một bước, multi-hop, aggregation và shortest path.
- Sinh `CO_STARRED_WITH` từ `ACTED_IN`.
- Lưu bằng chứng của fact suy diễn.
- Xuất tập con sang RDF.
- Viết 3–5 truy vấn SPARQL tương đương.

### WP7 — Ứng dụng hỏi–đáp

```text
Question
   → intent detection
   → entity/slot extraction
   → entity linking
   → parameterized Cypher template
   → Neo4j
   → answer + evidence
```

API tối thiểu:

- `POST /ask`
- `GET /entities/search`
- `GET /health`

Không ghép trực tiếp input của người dùng vào Cypher; mọi truy vấn phải dùng parameter.

### WP8 — Gợi ý phim

Điểm khởi đầu:

```text
score =
  3.0 × shared_directors
+ 2.0 × shared_actors
+ 1.5 × shared_genres
+ 1.0 × shared_keywords
```

Nên thử weighted Jaccard để tránh phim có cast lớn chiếm ưu thế. Endpoint `/recommend` phải trả cả `score` và `explanation`.

### WP9 — Đánh giá

| Hạng mục | Chỉ số |
|---|---|
| Entity resolution | Precision, Recall, F1 trên 100 mẫu |
| Data quality | Missing rate, duplicate rate, invalid edge rate |
| Graph correctness | Constraint violations, orphan nodes |
| Query performance | Median và p95 latency |
| Scalability | Mốc 1K, 5K và 20K node hoặc tương ứng |
| Reasoning | Precision trên 50 fact suy ra |
| QA | Accuracy trên 20–30 câu hỏi |
| Recommendation | Precision@K/NDCG@K hoặc đánh giá thủ công |
| Explainability | Tỷ lệ recommendation có evidence path |

## 8. Timeline 9 tuần

| Tuần | Công việc | Definition of Done |
|---|---|---|
| 1 | Khảo sát, chốt bài toán và competency questions | Đặc tả và phạm vi MVP được cố định |
| 2 | Thiết kế ontology và data model | OWL/TTL hợp lệ, sơ đồ hoàn thành |
| 3 | Thu thập TMDB/IMDb | Có raw dataset tái sử dụng được |
| 4 | Cleaning và entity resolution | Sinh bảng node/edge chuẩn hóa |
| 5 | Import Neo4j | Import idempotent, không trùng ID |
| 6 | Cypher, reasoning, RDF/SPARQL | Query và luật suy diễn chạy đúng |
| 7 | QA API và recommendation API | Hai endpoint hoạt động end-to-end |
| 8 | UI, test và thực nghiệm | Có demo ổn định và bảng kết quả |
| 9 | Report, slide và rehearsal | Đóng gói code và chạy thử từ đầu |

Nếu chỉ có 4–5 tuần, bỏ Award, NLP từ overview, LLM và collaborative filtering; giữ Neo4j, ontology, QA template và graph recommendation.

## 9. Kịch bản demo

1. Mở Neo4j Browser và hiển thị subgraph của một phim.
2. Chạy query diễn viên–phim–đạo diễn nhiều bước.
3. Hiển thị quan hệ `CO_STARRED_WITH` được suy ra.
4. Hỏi: “Những phim nào do Christopher Nolan đạo diễn?”.
5. Hỏi một câu có nhiều điều kiện.
6. Gợi ý phim tương tự `Inception`.
7. Hiển thị explanation và các cạnh chung.
8. Hiển thị thống kê dữ liệu và query latency.

Chuẩn bị seed dataset và video dự phòng để demo không phụ thuộc Internet hoặc TMDB API.

## 10. Definition of Done

- [ ] Ontology mở được bằng Protégé và không có lỗi consistency nghiêm trọng.
- [ ] Pipeline chạy lại không tạo node/edge trùng.
- [ ] Mọi node chính có ID ổn định và nguồn dữ liệu.
- [ ] Có ít nhất 10 Cypher query chạy đúng.
- [ ] Có ít nhất một luật suy diễn được kiểm chứng.
- [ ] `/ask` trả lời đúng ít nhất 80% bộ câu hỏi MVP.
- [ ] `/recommend` trả kết quả kèm evidence.
- [ ] Có bảng thực nghiệm, không chỉ ảnh chụp demo.
- [ ] Code chạy được theo README trên môi trường sạch.
- [ ] Slide, report và code dùng cùng thuật ngữ, schema và số liệu.
- [ ] Không chứa API key, mật khẩu hoặc dữ liệu bị hạn chế bản quyền.

