# Dàn ý chi tiết báo cáo cuối khóa

Độ dài mục tiêu: **40–55 trang nội dung chính**, chưa tính phụ lục. Báo cáo phải
phân biệt rõ: thiết kế dự kiến, chức năng đã triển khai, kết quả đã đo và phần còn
chờ đánh giá. Source code/config/test là căn cứ cho hiện trạng; số liệu lấy từ
manifest, Neo4j validation và artifact thực nghiệm cuối.

## Phần đầu báo cáo

### Trang bìa và thông tin hành chính

- Tên trường/khoa/học phần, đề tài, giảng viên, thành viên, thời gian.

### Tóm tắt tiếng Việt (250–350 từ)

- Bối cảnh dữ liệu phim đa nguồn và multi-hop.
- Phương pháp: TMDB + IMDb, ontology, Neo4j, QA template, graph recommendation.
- Kết quả định lượng đã xác nhận; không đưa metric pending.
- Hạn chế và một câu kết luận về explainability.

### Abstract tiếng Anh

- Nội dung tương ứng bản tiếng Việt, thống nhất thuật ngữ và số liệu.

### Các danh mục

- Mục lục; danh mục hình/bảng; từ viết tắt: KG, RDF, RDFS, OWL, SPARQL, ETL,
  QA, API, P@K, NDCG.

## Chương 1 — Giới thiệu (4–5 trang)

### 1.1. Bối cảnh

- Dữ liệu phim tăng nhanh, phân tán và có quan hệ nhiều-nhiều.
- Vai trò của TMDB, IMDb và nhu cầu tích hợp.
- Nhu cầu truy vấn multi-hop và recommendation có giải thích.

### 1.2. Phát biểu bài toán

- Xây một biểu diễn thống nhất cho Movie/Person/Genre/Keyword/Studio.
- Giải quyết identity, provenance, truy vấn và suy diễn.
- Cung cấp hai ứng dụng: QA và recommendation.

### 1.3. Câu hỏi nghiên cứu

- Câu hỏi chính như trong project memory.
- Câu hỏi phụ:
  1. Exact-ID enrichment đảm bảo tính đúng/provenance thế nào?
  2. Property Graph hỗ trợ competency questions ra sao?
  3. Evidence path cải thiện khả năng giải thích như thế nào?
  4. Hệ thống có giới hạn gì về coverage, accuracy và scalability?

### 1.4. Mục tiêu

- Mục tiêu tổng quát.
- Mục tiêu cụ thể có tiêu chí nghiệm thu: dataset, schema, query, API, test,
  evaluation artifacts.

### 1.5. Phạm vi và giả định

- MVP và extension.
- TMDB là nguồn graph chính; IMDb Ratings là nguồn enrichment.
- Chỉ top-20 cast; Award/Wikidata, LLM-to-Cypher tự do và multimodal ngoài MVP;
  vector retrieval và controlled GraphRAG là extension đã triển khai.
- Nêu trạng thái dataset tại thời điểm nộp.

### 1.6. Đóng góp

- Pipeline đa nguồn storage-bounded, tái lập được.
- Stable source IDs và provenance.
- Graph schema + rule suy diễn có evidence.
- QA/recommendation graph-native và bộ evaluation workflow.

### 1.7. Cấu trúc báo cáo

- Một đoạn tóm tắt nội dung chương 2–10.

## Chương 2 — Cơ sở lý thuyết (6–8 trang)

### 2.1. Biểu diễn tri thức và Knowledge Graph

- Data–information–knowledge; entity, relation, fact, provenance.
- Asserted fact và derived fact.

### 2.2. Ontology

- Class, individual, object/data property, domain/range, cardinality.
- Taxonomy so với ontology; competency-question-driven design.

### 2.3. RDF, RDFS, OWL và SPARQL

- Triple, URI, graph RDF; entailment cơ bản.
- Vai trò RDFS/OWL; giới hạn Open World Assumption khi validation dữ liệu.
- SPARQL graph pattern.

### 2.4. Property Graph và Neo4j

- Node, relationship, property, label.
- Constraint/index, transaction, Cypher pattern matching, shortest path.

### 2.5. RDF graph và Property Graph

So sánh semantics, interoperability, property trên edge, traversal, reasoning và
độ thuận tiện triển khai. Giải thích lựa chọn kết hợp thay vì tuyên bố một mô
hình luôn tốt hơn.

### 2.6. Entity resolution

- Deterministic matching bằng source ID.
- Fuzzy name fallback, threshold, confidence, ambiguity và human review.
- Precision, Recall, F1.

### 2.7. Knowledge-based recommendation

- Content/graph neighborhood similarity.
- Weighted overlap và weighted Jaccard.
- Explainability qua shared entities/evidence path.

### 2.8. Chỉ số đánh giá

- Data quality, median/p95/stdev, QA accuracy, P@K, DCG/NDCG, explanation coverage.

## Chương 3 — Công trình, nền tảng và dữ liệu liên quan (4–5 trang)

### 3.1. TMDB, IMDb, MovieLens và Wikidata

- Loại dữ liệu, định danh, giấy phép/phạm vi sử dụng, điểm mạnh/yếu.
- Lý do chọn TMDB + IMDb Ratings; lý do chưa dùng MovieLens/Wikidata trong MVP.

### 3.2. Movie Knowledge Graph và hệ QA liên quan

- Tổng hợp 3–5 công trình hoặc hệ thống có nguồn trích dẫn chính thống.
- So sánh nguồn dữ liệu, graph model, query/QA và evaluation.

### 3.3. Graph-based recommender liên quan

- Neighborhood, path-based explanation, embedding-based extension.

### 3.4. Khoảng trống và vị trí của đề tài

- Đề tài tập trung end-to-end reproducibility và explainability ở quy mô học phần,
  không cạnh tranh với recommender production.

## Chương 4 — Phân tích yêu cầu (4–5 trang)

### 4.1. Stakeholder và use case

- Người dùng hỏi graph, nhận recommendation; nhóm phát triển thu thập/import;
  người đánh giá kiểm tra facts/metrics.

### 4.2. Yêu cầu chức năng

- Collect/cache TMDB; enrich IMDb; transform/load/validate.
- 10 Cypher query; reasoning; RDF export.
- `/health`, `/stats`, `/entities/search`, `/ask`, `/recommend`, UI.

### 4.3. Yêu cầu phi chức năng

- Idempotency, reproducibility, query safety, offline demo, provenance, giới hạn
  dung lượng, không commit secret/raw data.

### 4.4. Competency questions

- Liệt kê 10 câu; ánh xạ mỗi câu sang intent/query và số hop.
- Dùng bảng: ID, câu hỏi, entity/relationship liên quan, Cypher template, output.

### 4.5. Tiêu chí hoàn thành và traceability

- Ma trận requirement → implementation file → test/evidence.
- Đánh dấu `Done`, `Partial`, `Pending evaluation`.

## Chương 5 — Thiết kế ontology và graph schema (5–6 trang)

### 5.1. Phương pháp thiết kế

- Bắt đầu từ competency questions; chọn class/property tối thiểu.

### 5.2. Ontology RDF/OWL

- Namespace, 5 class, object property, datatype property.
- Functional source IDs; domain/range.
- Hình ontology diagram xuất từ Protégé hoặc công cụ tương đương.

### 5.3. Property Graph schema

- Sơ đồ node/edge có hướng.
- Bảng data dictionary đầy đủ cho node và relationship.

### 5.4. Định danh thực thể

- `Movie.tmdb_id`, `Person.person_id=tmdb:<id>` và source IDs cho metadata nodes.
- Vì sao không dùng name làm khóa.
- Legacy fallback và migration bằng `--replace`.

### 5.5. Provenance và derived facts

- `source` trên node/edge, hai rating tách biệt.
- `derived`, `movie_count`, `evidence_movie_ids` trên `CO_STARRED_WITH`.

### 5.6. Ánh xạ RDF ↔ Neo4j

- Bảng class-label, object property-relationship, datatype-property.
- Khác biệt hướng `actedIn`, edge properties và URI strategy.

## Chương 6 — Kiến trúc và pipeline dữ liệu (7–9 trang)

### 6.1. Kiến trúc tổng thể

- Component diagram và data-flow diagram.

### 6.2. Thu thập TMDB

- Popular discovery, exact count unique, movie detail + credits + keyword +
  external IDs, retry, interval và immutable cache.

### 6.3. Tích hợp IMDb tiết kiệm dung lượng

- Chỉ `title.ratings.tsv.gz`; downloader `.part` → gzip validation → atomic rename.
- Streaming join bằng set 2.000–5.000 IDs.
- Checksum, byte count, download timestamp; chính sách giữ/xóa raw.

### 6.4. Cleaning và normalization

- Unicode/name/date/numeric normalization.
- Required fields, duplicate TMDB ID và invalid-record logging.

### 6.5. Entity resolution

- Exact Movie join, stable TMDB Person ID, fuzzy QA linking.
- Pseudocode; confidence và review policy.

### 6.6. Sinh normalized tables

- 5 node CSV, 5 edge CSV; field mapping.
- Character/cast order và studio country.

### 6.7. Manifest và reproducibility

- Source checksum, IMDb match counts, table counts, quality metrics.
- Phân biệt raw/interim/processed; Git ignore và secrets.

### 6.8. Import Neo4j

- Constraints/index → nodes → edges → reasoning → validation.
- Batch transaction, parameterized `UNWIND`, `MERGE`.
- Incremental idempotency so với authoritative `--replace` rebuild.

### 6.9. Rủi ro pipeline

- API rate limit, source update hằng ngày, missing IMDb IDs, tên trùng, partial
  download và migration stale nodes; biện pháp tương ứng.

## Chương 7 — Truy vấn, suy diễn và semantic export (5–6 trang)

### 7.1. Constraints và indexes

- Unique constraints và indexes; ảnh hưởng tới correctness/performance.

### 7.2. Query catalog

- Nhóm 10 query; trình bày 4 query tiêu biểu với input/output.
- Ít nhất hai multi-hop, một aggregation, một shortest path.

### 7.3. Query safety

- Whitelist template; parameter binding; validation request bằng Pydantic.

### 7.4. Rule `CO_STARRED_WITH`

- Tiền đề, Cypher materialization, hướng cạnh, idempotency và evidence.
- Phân biệt rule này với OWL entailment.

### 7.5. Graph validation

- Orphan, duplicate stable IDs, missing required property, invalid relationship.
- Nêu giới hạn của validation hiện tại và khả năng bổ sung SHACL.

### 7.6. RDF export và SPARQL

- Stable URI, source IDs và rating properties.
- 3–5 SPARQL query tương đương; thảo luận khác biệt biểu diễn.

## Chương 8 — Thiết kế và triển khai ứng dụng (6–7 trang)

### 8.1. FastAPI và repository boundary

- Lifespan, Neo4j repository, Pydantic models, static UI.
- Memory repository chỉ dành cho test/benchmark synthetic.

### 8.2. QA service

- 8 intent và regex normalization tiếng Việt.
- Slot extraction, candidate search, exact/fuzzy linking, confidence.
- Catalog Cypher, answer formatting, evidence và latency.
- Failure behavior: unknown intent, entity not found, ambiguity.

### 8.3. Recommendation service

- Công thức overlap và weighted Jaccard.
- Query graph-native; top-K và deterministic tie-break.
- Explanation từ shared directors/actors/genres/keywords.

### 8.4. API contract

- Request/response mẫu cho `/ask`, `/recommend`, `/entities/search`, `/stats`.
- Error status 404/503 và validation constraints.

### 8.5. Giao diện demo

- Hình UI; luồng tương tác; giới hạn giao diện hiện tại.

### 8.6. Bảo mật và vận hành

- Không ghép Cypher; `.env`; local demo password; Docker/network assumptions.

## Chương 9 — Thực nghiệm và kết quả (7–10 trang)

### 9.1. Câu hỏi và giả thuyết thực nghiệm

- RQ về data quality, correctness, QA, recommendation, explainability, latency.

### 9.2. Môi trường

- CPU/RAM/OS/Python/Neo4j version, Docker, ngày dataset, commit hash.
- Warm-up, iterations, cache state và backend.

### 9.3. Thống kê dataset

- Bảng node/edge counts và coverage IMDb.
- Biểu đồ phân bố genre/cast/degree nếu sinh thêm.

### 9.4. Data quality và graph correctness

- Input/valid/invalid/duplicate rates.
- Neo4j validation: node/relationship total, orphan, duplicate, missing required.
- Không suy ra chất lượng ngữ nghĩa chỉ từ structural validation.

### 9.5. Entity resolution

- Cách tạo 100 cặp silver (75 positive/25 negative), provenance và protocol reviewer/adjudication.
- Confusion matrix, Precision/Recall/F1 và error analysis.
- Silver: TP=75, TN=25, FP=FN=0, P/R/F1=1,00; không khái quát thành
  chất lượng human-labeled vì case được sinh từ source ID/rule.

### 9.6. Reasoning

- Sample ~50 `CO_STARRED_WITH` facts; kiểm tra evidence movies.
- Silver precision 50/50=1,00 nhờ audit cast/source ID; vẫn cần reviewer độc lập.

### 9.7. QA

- Tách smoke test 10 câu và reviewed corpus 20–30 câu.
- Đánh giá intent và answer correctness riêng.
- Nêu vấn đề nhiều shortest paths đúng và expected substring quá chặt.
- Hiện trạng smoke: 8/10 trên 2.000 phim, chỉ dùng như tín hiệu kiểm tra.

### 9.8. Recommendation

- Relevance-label protocol hoặc manual review có rubric.
- P@K, NDCG@K, explanation coverage; so sánh overlap/Jaccard.
- Với 20 case silver, K=10: P@10=0,64; NDCG@10=0,699; explanation coverage=1,00.
- Bổ sung ablation Neo4j thật: overlap 0,67/0,723; weighted Jaccard
  0,64/0,699; hybrid 0,59/0,657 theo P@10/NDCG@10. Thảo luận vì sao rubric
  thiên graph và không tuyên bố hybrid tốt hơn khi bằng chứng chưa hỗ trợ.

### 9.8a. Semantic retrieval

- Corpus silver 10 truy vấn tiếng Việt có relevant movie IDs.
- Recall@10=0,80; MRR=0,492 sau bilingual concept expansion.
- Phân tích ba nhóm lỗi: cross-lingual wording, overview thiếu và popular-data drift.
- Case study Inception với explanation path.

### 9.9. Hiệu năng và scalability

- Benchmark Neo4j thật tại các quy mô dataset có thật nếu có thể.
- Median/p95/stdev, ≥100 iterations/query, warm/cold cache ghi rõ.
- Neo4j 5.26.28 ở 2.000 phim, một warm-up và 100 lần/câu: median theo intent
  2,34–110,65 ms; p95 3,83–126,20 ms.
- Synthetic memory benchmark để kiểm tra CPU scaling, không so ngang Neo4j.
- Shortest-path outlier/error analysis.

### 9.10. Threats to validity

- Popular-movie sampling bias, top-20 cast, daily source drift.
- Nhãn nhỏ/chủ quan, query templates hạn chế, hardware-specific latency.
- IMDb rating availability bias.

### 9.11. Thảo luận

- Trả lời từng research question dựa trên bảng kết quả.
- Phân biệt kết quả đạt được, chưa đạt và nguyên nhân.

## Chương 10 — Kết luận và hướng phát triển (3–4 trang)

### 10.1. Tổng kết

- Nhắc lại bài toán, phương pháp và đóng góp kỹ thuật.

### 10.2. Trả lời câu hỏi nghiên cứu

- Một đoạn cho mỗi câu hỏi; chỉ dùng evidence đã đo.

### 10.3. Hạn chế

- Quy mô hiện tại, corpus nhãn, QA template, Person IMDb chưa liên kết, top-20
  cast, ontology/semantic validation còn tối giản.

### 10.4. Hướng phát triển

- Hoàn thiện corpus/evaluation và Neo4j benchmark trước.
- Sau đó mới mở rộng Wikidata/Award, robust entity resolution, full-text search,
  LLM-to-Cypher có guardrail, vector/GraphRAG và embeddings.

## Tài liệu tham khảo

- Dùng một chuẩn nhất quán như IEEE.
- Ưu tiên W3C, Neo4j manual, TMDB/IMDb official docs và bài báo peer-reviewed.
- Mọi hình/số liệu ngoài repo phải có nguồn; tránh trích blog cho định nghĩa cốt lõi.

## Phụ lục

- A. Data dictionary và ontology đầy đủ.
- B. 10 competency questions, Cypher catalog và SPARQL.
- C. OpenAPI/request-response samples.
- D. Test cases và lệnh tái lập.
- E. Evaluation label schema/rubric và raw result tables.
- F. Manifest/checksum, cấu hình máy và commit hash.

## Danh sách hình và bảng tối thiểu

### Hình

1. Kiến trúc tổng thể.
2. Ontology diagram.
3. Property Graph schema.
4. Pipeline sequence/data flow.
5. Entity-resolution decision flow.
6. `CO_STARRED_WITH` inference/evidence.
7. QA sequence diagram.
8. Recommendation scoring/explanation.
9. UI/demo screenshot.
10. Biểu đồ kết quả thực nghiệm cuối.

### Bảng

1. So sánh nguồn dữ liệu.
2. RDF/OWL và Property Graph.
3. Node/relationship data dictionary.
4. Competency-question traceability.
5. Dataset/graph statistics.
6. Data-quality/validation results.
7. Entity-resolution results.
8. QA results/error analysis.
9. Recommendation results.
10. Query latency/scalability.

## Checklist trước khi nộp

- [ ] Dataset đạt ≥2.000 phim hoặc phạm vi được sửa trung thực.
- [ ] Hoàn thành corpus nhãn và reviewer protocol cho metric được báo cáo.
- [ ] Chạy benchmark Neo4j thật với cấu hình/iterations rõ ràng.
- [ ] Số liệu report = slide = manifest/result artifacts.
- [ ] Không gọi smoke test hoặc synthetic benchmark là production result.
- [ ] Ontology mở được, RDF parse được, mọi Cypher/SPARQL đã chạy kiểm tra.
- [ ] Hướng dẫn chạy trên môi trường sạch được rehearsal.
- [ ] Không chứa API key, raw dataset hoặc mật khẩu production.
