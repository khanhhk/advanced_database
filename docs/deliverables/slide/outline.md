# Dàn ý trang chiếu: các khái niệm Knowledge Graph dùng trong dự án

Deck gồm **29 trang chiếu, không kèm phụ lục**. Nội dung được viết theo hướng
học thuật và có thể đọc độc lập: mỗi khái niệm thực sự dùng trong dự án đều có
định nghĩa, vai trò và ví dụ liên hệ với Movie Knowledge Graph. Slide được phép
nhiều chữ hơn một deck trình diễn tối giản; chi tiết source code và vận hành vẫn
để trong báo cáo LaTeX.

## Phần I — Khái niệm và mô hình biểu diễn

1. Trang bìa: Knowledge Graph — nền tảng lý thuyết.
2. Data → Information → Knowledge → Inference.
3. Knowledge Graph: entity, relationship, property, identifier và phân biệt
   ngắn gọn schema–instance.
4. Property Graph: node, relationship và property trên cạnh.
5. Neighborhood, path và subgraph.
6. Bốn nguyên tắc: identity, schema, provenance, competency questions.
7. Uniqueness constraint, validation, index và full-text index.
8. Pattern matching và luật suy diễn bằng Cypher.
9. Hop, degree, common neighbor và shortest path.
10. Đồ thị thuộc tính và mô hình bảng: mức độ phù hợp theo loại truy vấn.

## Phần II — Xây dựng Movie Knowledge Graph

11. Kiến trúc theo lớp: nguồn → xử lý → tri thức → khai thác.
12. Thiết kế schema Movie–Person–Genre–Keyword–Studio.
13. Các chiều chất lượng và quality gate của graph.
14. Entity resolution: candidate, exact match, fuzzy match và abstention.
15. Phân biệt entity resolution với entity linking.
16. Cypher lookup, aggregation, multi-hop và shortest path.
17. Asserted fact và derived fact qua luật `CO_STARRED_WITH`.
18. Phân biệt provenance, lineage và evidence.

## Phần III — Khai thác và đánh giá

19. QA như lớp ánh xạ ngôn ngữ tự nhiên vào graph pattern an toàn.
20. Explainable recommendation bằng IDF-weighted graph similarity.
21. Precision, recall, F1, Precision@K và NDCG@K.
22. Thiết kế evaluation theo từng claim.
23. Kết quả chất lượng, entity resolution, reasoning, QA và recommendation.
24. Competency question dẫn dắt schema và truy vấn.
25. Demo bước 1–2: QA lookup trên Web UI và kiểm chứng trong Neo4j Browser.
26. Demo bước 3–4: QA multi-hop và kiểm chứng shared-neighbor pattern.
27. Demo bước 5–6: gợi ý phim và kiểm chứng các shared feature.
28. Giới hạn và hướng phát triển.
29. Kết luận và hỏi đáp.

## Phân bổ thời gian gợi ý

| Phần | Slide | Thời gian |
|---|---:|---:|
| Khái niệm và mô hình biểu diễn | 1–10 | 7–9 phút |
| Xây dựng Movie Knowledge Graph | 11–18 | 6–8 phút |
| Khai thác, đánh giá, demo và kết luận | 19–29 | 8–10 phút |

Nếu thời lượng bảo vệ ngắn, có thể lướt nhanh slide 8 và 22 nhưng
giữ chúng trong file để trả lời phản biện.

## Ranh giới slide–báo cáo

Slide giải thích khái niệm, vai trò, ví dụ và kết quả chính. Báo cáo giữ phần
chi tiết:

- cấu trúc module, endpoint FastAPI, response schema và Web UI;
- toàn bộ chín intent và từng Cypher template;
- truy vấn recommendation đầy đủ và lựa chọn trọng số;
- tích hợp TMDB–IMDb, ETL chi tiết, cache, manifest, idempotent import, runtime
  preparation, Docker và runbook;
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
