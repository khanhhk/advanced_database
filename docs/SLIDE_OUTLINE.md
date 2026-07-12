# Dàn ý chi tiết slide bảo vệ

Phiên bản mục tiêu: **22 slide / 15–20 phút**. Mạch kể chuyện chính: bài toán
đa nguồn → mô hình tri thức → pipeline tái lập → truy vấn/suy diễn → hai ứng
dụng giải thích được → bằng chứng thực nghiệm → giới hạn trung thực.

## Nguyên tắc sử dụng số liệu

- Chỉ dùng số liệu lấy từ `data/processed/manifest.json`, Neo4j validation và
  `experiments/results/` tại lần chạy cuối.
- Hiện có đúng 2.000 phim, đạt mốc tối thiểu của MVP.
- QA 8/10 chỉ là smoke test 10 câu, không gọi là accuracy production.
- Benchmark hiện là `memory-synthetic`, 10 iterations; không gọi là hiệu năng
  Neo4j và không dùng làm kết luận cuối.
- Entity resolution, reasoning precision, Precision@K và NDCG@K để ô
  `CHỜ ĐÁNH GIÁ` cho tới khi có corpus review.

## Slide 1 — Trang bìa (20 giây)

**Thông điệp:** Xây dựng Movie Knowledge Graph đa nguồn có truy vấn, suy diễn,
hỏi–đáp và gợi ý giải thích được.

- Tên đề tài, học phần, giảng viên, thành viên.
- Một hình hero graph nhỏ: Movie ở trung tâm nối Person/Genre/Keyword/Studio.
- Không đặt kiến trúc hoặc danh sách công nghệ lên trang bìa.

## Slide 2 — Bối cảnh và động lực (40 giây)

**Thông điệp:** Dữ liệu phim là dữ liệu quan hệ dày đặc và phân tán.

- Một phim liên hệ với nhiều người, vai trò, thể loại, từ khóa và studio.
- TMDB giàu metadata/credits; IMDb có rating và vote count độc lập.
- Truy vấn thường cần nhiều bước và câu trả lời cần bằng chứng.
- Hình đề xuất: hai nguồn TMDB/IMDb đi vào một thực thể Movie hợp nhất.

## Slide 3 — Bài toán và khoảng trống (45 giây)

**Thông điệp:** Lưu dữ liệu chưa đủ; cần định danh, provenance và traversal.

- Trùng tên người không đồng nghĩa cùng thực thể.
- Rating từ hai nguồn không được ghi đè lẫn nhau.
- Các câu hỏi co-star, shortest path và recommendation khó giải thích bằng bảng
  phẳng hoặc lookup một bước.
- Chốt ba yêu cầu: tích hợp đúng, truy vấn nhiều bước, giải thích được.

## Slide 4 — Câu hỏi nghiên cứu và mục tiêu (45 giây)

**Câu hỏi chính:** Knowledge Graph có thể tích hợp dữ liệu phim đa nguồn, hỗ trợ
multi-hop/inference và tạo câu trả lời/gợi ý có bằng chứng như thế nào?

Mục tiêu đo được:

1. Pipeline TMDB + IMDb tái lập được.
2. Neo4j graph có constraint, stable ID và validation.
3. Ít nhất 10 Cypher query, gồm multi-hop và shortest path.
4. QA theo 8 intent và recommendation có explanation.
5. Thiết kế evaluation cho data quality, QA, reasoning và recommendation.

## Slide 5 — Phạm vi và ranh giới (35 giây)

- MVP: Movie, Person, Genre, Keyword, Studio và 5 quan hệ gốc.
- Quan hệ suy diễn: `CO_STARRED_WITH`.
- TMDB là graph source; IMDb chỉ enrichment rating/votes bằng exact ID.
- Ngoài phạm vi: Award/Wikidata, LLM-to-Cypher, vector search, GraphRAG,
  embeddings.
- Nêu dataset hiện tại 2.000 phim; dải mục tiêu của đề tài là 2.000–5.000.

## Slide 6 — Vì sao Knowledge Graph/Neo4j? (45 giây)

So sánh ngắn:

| Yêu cầu | Mô hình bảng | Property Graph |
|---|---|---|
| Quan hệ nhiều-nhiều | bảng nối | cạnh trực tiếp |
| Multi-hop | nhiều JOIN | traversal pattern |
| Suy diễn co-star | materialized logic | derived relationship |
| Explanation | phải dựng lại | evidence path tự nhiên |

Kết luận: Neo4j là operational store; RDF/OWL dùng cho lớp chuẩn ngữ nghĩa.

## Slide 7 — Kiến trúc tổng thể (60 giây)

```text
TMDB API/cache ─┐
                ├→ Clean/Normalize → CSV nodes/edges → Neo4j
IMDb ratings.gz ┘          │                         ├→ QA API
                           └→ RDF/Turtle             └→ Recommend API
                                                        ↓
                                                   FastAPI + UI
```

Nhấn mạnh: raw cache bất biến, processed manifest có checksum, runtime không phụ
thuộc Internet sau khi import.

## Slide 8 — Nguồn dữ liệu và tích hợp IMDb (50 giây)

- Chỉ tải `title.ratings.tsv.gz` khoảng 8,2 MB.
- Đọc streaming, không giải nén và không nạp toàn bộ IMDb vào RAM/Neo4j.
- Join: `TMDB.external_ids.imdb_id = IMDb.tconst`.
- 1.785/2.000 phim có IMDb ID; 1.677 rating match chính xác.
- Giữ riêng `rating`, `imdb_rating`, `imdb_votes`.
- Hình: một record Inception trước/sau enrichment.

## Slide 9 — Ontology và Property Graph schema (55 giây)

- Node: Movie, Person, Genre, Keyword, Studio.
- Edge: ACTED_IN, DIRECTED, HAS_GENRE, HAS_KEYWORD, PRODUCED_BY.
- Person dùng một label; vai trò nằm trên relationship.
- `ACTED_IN` có `character`, `cast_order`, `source`.
- `Person.person_id = tmdb:<id>`; không dùng tên làm khóa chính.
- Hình bắt buộc: schema với hướng cạnh và cardinality trực quan.

## Slide 10 — Pipeline ETL và reproducibility (55 giây)

```text
Collect → Cache → Clean → Exact-ID enrich → Normalize → Load → Reason → Validate
```

- Raw JSON/gzip bị Git ignore nhưng giữ checksum.
- CSV node/edge sinh deterministic; manifest ghi count, source hash và quality.
- Import theo batch, constraint trước, `MERGE` theo stable ID.
- `--replace` dùng cho rebuild authoritative; import lặp không tạo duplicate.

## Slide 11 — Chất lượng dữ liệu và graph validation (45 giây)

Hiển thị bảng số liệu chạy cuối:

| Chỉ số | Giá trị hiện tại |
|---|---:|
| Movie | 2.000 |
| Person | 23.585 |
| Genre / Keyword / Studio | 19 / 8.059 / 2.618 |
| Tổng node | 36.253 |
| Tổng relationship, gồm suy diễn | 334.598 |
| Orphan / duplicate / missing required | 0 / 0 / 0 |

Ghi chú: cập nhật lại từ manifest/Neo4j ngay trước ngày bảo vệ.

## Slide 12 — Entity resolution và provenance (50 giây)

- Movie TMDB↔IMDb: exact `imdb_id`, confidence 1.0.
- Person/Genre/Keyword/Studio: ưu tiên TMDB source ID.
- Legacy hash tên chỉ để tương thích cache/fixture cũ.
- QA entity linker: exact/fuzzy canonicalization; confidence được đưa vào evidence.
- Trình bày workflow review ambiguous match; không trình bày F1 khi chưa có nhãn.

## Slide 13 — Cypher và competency questions (50 giây)

- Phân nhóm 10 query: lookup, aggregation, multi-hop, shortest path, similarity.
- Chọn một query 2–3 hop để trình bày, ví dụ director → movie → genre.
- Chỉ hiện 5–7 dòng Cypher và highlight parameter `$genre`.
- Nêu nguyên tắc: user input không được nối chuỗi vào Cypher.

## Slide 14 — Suy diễn `CO_STARRED_WITH` (50 giây)

```text
Person A -[:ACTED_IN]-> Movie <-[:ACTED_IN]- Person B
                         ↓
A -[:CO_STARRED_WITH {movie_count, evidence_movie_ids, derived:true}]-> B
```

- Phân biệt asserted facts và derived facts.
- `movie_count` và `evidence_movie_ids` giúp kiểm tra/lần ngược.
- Không gọi đây là OWL reasoning; đây là rule-based materialization bằng Cypher.

## Slide 15 — Hệ hỏi–đáp (55 giây)

```text
Question → Intent/Slots → Entity linking → Whitelisted Cypher
         → Neo4j → Answer + evidence + latency
```

- 8 intent được hỗ trợ.
- Ví dụ typo `Cristopher Nolan` → canonical `Christopher Nolan`.
- Response minh họa gồm intent, answer, entity-link confidence và evidence.
- Nêu giới hạn: rule/regex intent, chưa phải open-domain NLP.

## Slide 16 — Recommendation có giải thích (60 giây)

- Hai phương pháp: weighted overlap và weighted Jaccard.
- Trọng số: director 3.0, actor 2.0, genre 1.5, keyword 1.0.
- Weighted Jaccard giảm thiên lệch về movie có nhiều metadata/cast.
- Query tính trong Neo4j, không tải toàn graph về Python.
- Ví dụ card kết quả: title, score và shared director/actor/genre/keyword.

## Slide 17 — RDF/OWL và SPARQL (40 giây)

- Xuất subset sang Turtle với stable URI.
- Ontology có class, object property, datatype property và functional source IDs.
- SPARQL minh họa truy vấn tương đương.
- Kết luận: RDF/OWL mạnh về interoperability/semantics; Neo4j thuận tiện cho
  traversal và ứng dụng operational.

## Slide 18 — Thiết kế thực nghiệm (55 giây)

Ma trận metric:

| Hạng mục | Dataset | Metric |
|---|---|---|
| Data quality | toàn corpus | missing/duplicate/orphan |
| Entity resolution | 100 cặp silver có provenance | P/R/F1 |
| Reasoning | 50 fact silver có evidence | precision |
| QA | 20–30 câu review | intent + answer accuracy |
| Recommendation | 20 case silver theo rubric | P@K, NDCG@K |
| Explainability | recommendation output | evidence coverage |
| Performance | Neo4j thật, nhiều quy mô | median/p95/stdev |

## Slide 19 — Kết quả hiện có và cách đọc (55 giây)

- Corpus/graph: 2.000 Movie; 36.574 node; 337.822 relationship; validation hợp lệ,
  orphan/duplicate/missing/invalid đều bằng 0.
- IMDb exact-match: 1.677/1.785 Movie có IMDb ID ghép được rating.
- QA smoke: chạy lại 10 câu trên corpus 2.000 phim; chỉ là smoke test.
- Silver: entity P/R/F1=1,00; reasoning precision=1,00; recommendation
  P@10=0,64, NDCG@10=0,699, explanation coverage=1,00.
- Neo4j thật, 100 lần/câu sau một warm-up: median 2,34–110,65 ms;
  p95 3,83–126,20 ms; cấu hình máy nằm trong metadata.
- Hai case smoke fail cần giải thích: shortest path có nhiều đáp án hợp lệ; top-5
  recommendation không chứa expected movie.
- Không đưa benchmark synthetic thành kết luận Neo4j.
- Gắn chữ `silver`, không diễn giải metric là human evaluation độc lập.

## Slide 20 — Demo end-to-end (60–90 giây trong slide, 4 phút tổng demo)

Kịch bản cố định:

1. `/stats` chứng minh graph đang chạy.
2. Hỏi phim theo đạo diễn có typo để thấy entity linking.
3. Hỏi shortest path/co-star để thấy multi-hop và derived evidence.
4. Recommend từ Inception, mở explanation.
5. Nếu đủ thời gian, mở Neo4j Browser xem subgraph.

Chuẩn bị video dưới 3 phút và dữ liệu đã import; không gọi Internet lúc demo.

## Slide 21 — Hạn chế, rủi ro và hướng phát triển (45 giây)

- QA dựa trên template; ambiguity và nhiều đáp án đúng chưa được chấm tốt.
- Corpus silver vẫn cần reviewer độc lập/adjudication để thành human labels.
- Benchmark mới đo một quy mô thật 2.000 phim, chưa chứng minh scalability nhiều quy mô.
- Top-20 cast làm mất diễn viên phụ; IMDb mới enrich Movie, chưa link Person.
- Hướng sau MVP: Wikidata/Award, full-text/fuzzy index tốt hơn, LLM-to-Cypher có
  guardrail, vector search/GraphRAG, graph embedding.

## Slide 22 — Kết luận (35 giây)

- Đã xây được pipeline đa nguồn có provenance và stable identity.
- Graph hỗ trợ traversal, materialized inference, QA và recommendation giải thích được.
- Neo4j và RDF/OWL đóng hai vai trò bổ trợ.
- Kết luận phải gắn với bằng chứng hiện có, không vượt quá metric đã đo.

## Phân bổ thời gian

| Phần | Slide | Thời gian |
|---|---:|---:|
| Bài toán, mục tiêu, phạm vi | 1–5 | 3 phút |
| Thiết kế và pipeline | 6–12 | 5 phút |
| Query, reasoning, ứng dụng | 13–17 | 4 phút |
| Thực nghiệm và demo | 18–20 | 5 phút |
| Hạn chế và kết luận | 21–22 | 2 phút |

## Checklist trước khi đóng slide

- [ ] Thu đủ ≥2.000 phim hoặc sửa toàn bộ tuyên bố phạm vi.
- [ ] Chạy lại manifest, Neo4j validation và chụp số liệu cuối.
- [ ] Hoàn thành corpus nhãn hoặc đánh dấu rõ metric còn pending.
- [ ] Benchmark Neo4j thật, ít nhất 100 iterations/query nếu dùng trong kết luận.
- [ ] Mọi biểu đồ có backend, movie count, cấu hình máy và ngày chạy.
- [ ] Demo không phụ thuộc TMDB/IMDb network.
- [ ] Report, slide và API dùng cùng thuật ngữ/schema/số liệu.
