# Dàn ý trang chiếu: Knowledge Graph từ lý thuyết đến ứng dụng

Deck hiện có **25 trang chiếu, không kèm phụ lục**. Project chỉ trình bày và
triển khai một mô hình graph: Neo4j Property Graph.

## Phần I — Nền tảng Knowledge Graph

1. Trang bìa: khái niệm, Property Graph, schema, suy diễn và Cypher.
2. Data → Information → Knowledge → Inference.
3. Entity, relationship, property và stable identifier.
4. Graph schema và instance data.
5. Property Graph: node, relationship và property trên cạnh.
6. Cypher cho pattern query và materialized business rule.

Thông điệp chính:

- Knowledge Graph không chỉ là tập node/edge; identity, schema, provenance và
  bằng chứng quyết định độ tin cậy.
- Schema định nghĩa label, loại quan hệ, property và constraint.
- `CO_STARRED_WITH` là derived relationship được vật chất hóa bằng Cypher.

## Phần II — Movie Knowledge Graph

7. Vì sao chọn Neo4j thay vì chỉ dùng mô hình bảng.
8. Kiến trúc đầu cuối TMDB/IMDb → Neo4j → FastAPI/UI.
9. Tích hợp IMDb theo exact ID và streaming gzip.
10. Property Graph schema: Movie, Person, Genre, Keyword, Studio.
11. Pipeline: collect, cache, clean, normalize, load, reason, validate.
12. Quality gate và quy mô graph.
13. Entity resolution, stable ID và provenance.
14. Cypher catalog: lookup, multi-hop, aggregation, shortest path.
15. Suy diễn `CO_STARRED_WITH` và evidence.
16. Hệ hỏi–đáp chín intent.
17. Gợi ý IDF-weighted có giải thích.
18. Thiết kế đánh giá theo từng claim.
19. Kết quả QA, entity resolution, reasoning và recommendation.
20. Benchmark Neo4j–SQLite và trade-off.
21. Demo QA lookup trên Web UI và Cypher kiểm chứng trong Neo4j Browser.
22. Demo QA multi-hop trên Web UI và shared-neighbor query trong Browser.
23. Demo gợi ý trên Web UI và query kiểm chứng shared features trong Browser.
24. Giới hạn và hướng phát triển.
25. Kết luận.

## Phân bổ thời gian đề xuất

| Phần | Slide | Thời gian |
|---|---:|---:|
| Nền tảng Knowledge Graph | 1–6 | khoảng 5 phút |
| Thiết kế và dữ liệu | 7–13 | 4–5 phút |
| Truy vấn và ứng dụng | 14–17 | 3–4 phút |
| Đánh giá, demo, kết luận | 18–25 | 4–5 phút |

## Kiểm tra trước khi trình bày

1. Giải thích được node, relationship, property, schema và instance.
2. Giải thích được vì sao stable ID quan trọng hơn tên.
3. Phân biệt asserted fact với derived fact.
4. Giải thích `CO_STARRED_WITH` hoàn toàn bằng Cypher và supporting movies.
5. Không nói Neo4j luôn nhanh hơn relational database.
6. Không gọi silver corpus là đánh giá người dùng độc lập.
7. Đối chiếu số liệu với `experiments/results/` trước ngày bảo vệ.
