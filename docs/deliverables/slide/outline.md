# Dàn ý trang chiếu: các khái niệm Knowledge Graph dùng trong dự án

Deck gồm **31 trang chiếu, không kèm phụ lục**. Nội dung được viết theo hướng
học thuật và có thể đọc độc lập: mỗi khái niệm thực sự dùng trong dự án đều có
định nghĩa, vai trò và ví dụ liên hệ với Movie Knowledge Graph. Slide được phép
nhiều chữ hơn một deck trình diễn tối giản; chi tiết source code và vận hành vẫn
để trong báo cáo LaTeX.

## Phần I — Khái niệm và mô hình biểu diễn

1. Trang bìa: Knowledge Graph — nền tảng lý thuyết.
2. Data → Information → Knowledge → Inference.
3. Knowledge Graph: entity, relationship, property và identifier.
4. Schema/TBox và instance/ABox.
5. Property Graph: node, relationship và property trên cạnh.
6. Neighborhood, path và subgraph.
7. Bốn nguyên tắc: identity, schema, provenance, competency questions.
8. Uniqueness constraint, validation, index và full-text index.
9. Pattern matching và luật suy diễn bằng Cypher.
10. Hop, degree, common neighbor và shortest path.
11. Đồ thị thuộc tính và mô hình bảng: mức độ phù hợp theo loại truy vấn.

## Phần II — Xây dựng Movie Knowledge Graph

12. Kiến trúc theo lớp: nguồn → xử lý → tri thức → khai thác.
13. Tích hợp đa nguồn TMDB–IMDb bằng exact identifier.
14. Thiết kế schema Movie–Person–Genre–Keyword–Studio.
15. ETL, raw cache, normalized tables, idempotent import và validation.
16. Các chiều chất lượng và quality gate của graph.
17. Entity resolution: candidate, exact match, fuzzy match và abstention.
18. Phân biệt entity resolution với entity linking.
19. Cypher lookup, aggregation, multi-hop và shortest path.
20. Asserted fact và derived fact qua luật `CO_STARRED_WITH`.
21. Phân biệt provenance, lineage và evidence.

## Phần III — Khai thác và đánh giá

22. QA như lớp ánh xạ ngôn ngữ tự nhiên vào graph pattern an toàn.
23. Explainable recommendation bằng IDF-weighted graph similarity.
24. Precision, recall, F1, Precision@K và NDCG@K.
25. Thiết kế evaluation theo từng claim.
26. Kết quả chất lượng, entity resolution, reasoning, QA và recommendation.
27. Benchmark Neo4j–SQLite và giới hạn diễn giải.
28. Competency question dẫn dắt schema và truy vấn.
29. Demo tổng hợp: câu hỏi → entity link → Cypher → evidence path.
30. Giới hạn và hướng phát triển.
31. Kết luận và hỏi đáp.

## Phân bổ thời gian gợi ý

| Phần | Slide | Thời gian |
|---|---:|---:|
| Khái niệm và mô hình biểu diễn | 1–11 | 8–10 phút |
| Xây dựng Movie Knowledge Graph | 12–21 | 7–9 phút |
| Khai thác, đánh giá và kết luận | 22–31 | 6–8 phút |

Nếu thời lượng bảo vệ ngắn, có thể lướt nhanh slide 8, 13, 15, 24 và 27 nhưng
giữ chúng trong file để trả lời phản biện.

## Ranh giới slide–báo cáo

Slide giải thích khái niệm, vai trò, ví dụ và kết quả chính. Báo cáo giữ phần
chi tiết:

- cấu trúc module, endpoint FastAPI, response schema và Web UI;
- toàn bộ chín intent và từng Cypher template;
- truy vấn recommendation đầy đủ và lựa chọn trọng số;
- cache, manifest, runtime preparation, Docker và runbook;
- protocol sinh corpus, bảng kết quả và metadata benchmark đầy đủ.

## Kiểm tra trước khi trình bày

1. Phân biệt schema với instance; entity với record; name với identity.
2. Giải thích được constraint khác index như thế nào.
3. Dùng đúng hop, path, neighborhood, common neighbor và subgraph.
4. Phân biệt entity resolution với entity linking.
5. Phân biệt asserted fact, derived fact, provenance, lineage và evidence.
6. Giải thích `CO_STARRED_WITH` bằng supporting movies.
7. Giải thích vì sao IDF giảm ảnh hưởng của feature phổ biến.
8. Phân biệt Precision@K với NDCG@K.
9. Không nói Neo4j luôn nhanh hơn relational database.
10. Không khái quát metric silver thành độ chính xác production.
