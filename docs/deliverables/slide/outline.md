# Dàn ý trang chiếu: Knowledge Graph từ lý thuyết đến ứng dụng

Deck hiện có **24 trang chiếu, không kèm phụ lục**. Project chỉ trình bày và
triển khai một mô hình graph: Neo4j Property Graph.

## Phần I — Nền tảng Knowledge Graph

1. Trang bìa: khái niệm, Property Graph, schema, suy diễn và Cypher.
2. Data → Information → Knowledge → Inference.
3. Entity, relationship, property và stable identifier.
4. Graph schema và instance data.
5. Property Graph: node, relationship và property trên cạnh.
6. Cypher cho pattern query và materialized business rule.
7. Chuyển từ lý thuyết sang Movie Knowledge Graph.

Thông điệp chính:

- Knowledge Graph không chỉ là tập node/edge; identity, schema, provenance và
  bằng chứng quyết định độ tin cậy.
- Schema định nghĩa label, loại quan hệ, property và constraint.
- `CO_STARRED_WITH` là derived relationship được vật chất hóa bằng Cypher.

## Phần II — Movie Knowledge Graph

8. Vì sao chọn Neo4j thay vì chỉ dùng mô hình bảng.
9. Kiến trúc đầu cuối TMDB/IMDb → Neo4j → FastAPI/UI.
10. Tích hợp IMDb theo exact ID và streaming gzip.
11. Property Graph schema: Movie, Person, Genre, Keyword, Studio.
12. Pipeline: collect, cache, clean, normalize, load, reason, validate.
13. Quality gate và quy mô graph.
14. Entity resolution, stable ID và provenance.
15. Cypher catalog: lookup, multi-hop, aggregation, shortest path.
16. Suy diễn `CO_STARRED_WITH` và evidence.
17. Hệ hỏi–đáp chín intent.
18. Gợi ý IDF-weighted có giải thích.
19. Thiết kế đánh giá theo từng claim.
20. Kết quả QA, entity resolution, reasoning và recommendation.
21. Benchmark Neo4j–SQLite và trade-off.
22. Kịch bản demo end-to-end.
23. Giới hạn và hướng phát triển.
24. Kết luận.

## Phân bổ thời gian đề xuất

| Phần | Slide | Thời gian |
|---|---:|---:|
| Nền tảng Knowledge Graph | 1–7 | 5–6 phút |
| Thiết kế và dữ liệu | 8–14 | 4–5 phút |
| Truy vấn và ứng dụng | 15–18 | 3–4 phút |
| Đánh giá, demo, kết luận | 19–24 | 4–5 phút |

## Kiểm tra trước khi trình bày

1. Giải thích được node, relationship, property, schema và instance.
2. Giải thích được vì sao stable ID quan trọng hơn tên.
3. Phân biệt asserted fact với derived fact.
4. Giải thích `CO_STARRED_WITH` hoàn toàn bằng Cypher và supporting movies.
5. Không nói Neo4j luôn nhanh hơn relational database.
6. Không gọi silver corpus là đánh giá người dùng độc lập.
7. Đối chiếu số liệu với `experiments/results/` trước ngày bảo vệ.
