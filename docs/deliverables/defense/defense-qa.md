# Bộ câu hỏi phản biện

## Mô hình và lựa chọn công nghệ

1. **Vì sao không chỉ dùng PostgreSQL?** Quan hệ nhiều–nhiều vẫn biểu diễn được
   trong SQL, nhưng các pattern multi-hop, shortest path và evidence path tự nhiên
   hơn trong property graph. Benchmark cho thấy SQLite nhanh hơn bốn query kiểm
   soát, nên đề tài không tuyên bố graph luôn nhanh hơn relational.
2. **Vì sao dùng cả Neo4j và RDF/OWL?** Neo4j là operational store cho API;
   RDF/OWL là standards view cho namespace, ontology, SPARQL và entailment.
3. **Đây có thật sự là Knowledge Graph hay chỉ là graph database?** Hệ thống có
   stable identity, provenance, ontology, RDF export, semantic constraints,
   inference và evidence; Neo4j chỉ là một lớp thực thi.
4. **Vì sao không dùng quad/named graph?** Snapshot hiện dùng triple với namespace
   và provenance ở property/manifest. Named graph là hướng phù hợp khi cần quản lý
   provenance theo nguồn ở mức từng statement.
5. **Vì sao chỉ một label Person?** Một người có thể vừa ACTED_IN vừa DIRECTED;
   vai trò thuộc relationship, không phải hai identity tách biệt.

## Dữ liệu và chất lượng

6. **Làm sao tránh trùng người/phim?** Dùng source-qualified stable ID; exact ID
   là chính, fuzzy chỉ fallback có threshold, confidence và log.
7. **Tại sao rating TMDB và IMDb không gộp?** Hai nguồn có thang đo/cộng đồng bỏ
   phiếu khác nhau; giữ riêng bảo toàn provenance và tránh tạo số liệu giả.
8. **Con số 1,0 của entity resolution có đáng tin?** Đó là silver corpus 100 case.
   Full-snapshot audit bổ sung zero duplicate/conflict/invalid FK và 100% provenance;
   review pack mù đã sẵn sàng nhưng chưa là gold trước khi reviewer độc lập ký.
9. **Top-20 cast gây ảnh hưởng gì?** Giảm kích thước và thời gian thu thập nhưng
   bỏ diễn viên phụ, làm thiếu edge và có thể ảnh hưởng shortest path/recommendation.
10. **Pipeline có tái lập không?** Raw cache, SHA-256, manifest, exact versions,
    idempotent MERGE và artifact kết quả cho phép chạy lại cùng snapshot.

## Suy diễn và truy vấn

11. **`CO_STARRED_WITH` được suy ra thế nào?** Hai Person cùng `ACTED_IN` một
    Movie tạo quan hệ đối xứng, lưu count và supporting movie làm evidence.
12. **Làm sao biết fact suy ra đúng?** Validator kiểm supporting movie/endpoints;
    50 case silver đều có bằng chứng trong source cast.
13. **Reasoner có phải OWL 2 DL đầy đủ?** Không. Đây là RDFS/OWL subset thực thi
    bằng RDFLib và Jena/Fuseki: domain/range, inverse, symmetric cùng các constraint
    rõ ràng. Hai engine đều sinh thêm đúng 36.201 triple.
14. **Truy vấn inference-enabled là gì?** Query dùng inverse property hoặc derived
    relation chỉ xuất hiện sau materialization để rút tri thức không assert trực tiếp.
15. **Có nguy cơ Cypher injection không?** Input được link thành entity, plan qua
    Pydantic schema và compiler whitelist; Cypher dùng parameter, không nối chuỗi.

## QA, recommendation và đánh giá

16. **LLM có bịa câu trả lời không?** LLM tùy chọn chỉ lập QueryPlan JSON; Neo4j
    trả fact/evidence. Khi không có LLM, parser deterministic vẫn chạy.
17. **Vì sao recommendation gọi là explainable?** Mỗi shared feature đóng góp một
    số điểm xác định; response trả chính feature, loại edge và contribution đó.
18. **Tại sao IDF?** Feature xuất hiện ở nhiều phim ít phân biệt; IDF tăng đóng
    góp của director/actor/keyword hiếm hơn.
19. **Tại sao metric hiện thấp hơn artifact cũ?** Snapshot/candidate set thay đổi;
    run hiện tại là nguồn sự thật. Baseline cũ chỉ là lịch sử và không được dùng
    để kết luận so sánh nếu chưa tái chạy cùng protocol.
20. **QA 20/20 có đủ không?** Đủ cho smoke/regression của chín intent, chưa đủ để
    chứng minh robust với paraphrase, ambiguity hoặc câu ngoài miền.
21. **Vì sao SQLite nhanh hơn?** Dataset nhỏ và query kiểm soát có index/join phù
    hợp. Neo4j được chọn cho expressiveness, traversal và evidence path, không vì
    một cam kết latency phổ quát.
22. **Benchmark có chứng minh scalability không?** Chưa. Đã đo ba induced snapshot
    500/1.000/2.000 trên cùng máy và protocol, nhưng chưa đo concurrency, cold cache,
    tài nguyên hoặc quy mô lớn hơn.
23. **Threat lớn nhất là gì?** Popularity sampling, top-20 cast, silver labels và
    external validity benchmark; báo cáo nêu rõ thay vì khái quát hóa quá mức.
24. **Nếu nâng cấp một việc trước tiên?** Hoàn tất independent review/adjudication,
    sau đó đo concurrency và snapshot lớn hơn trước khi thêm vector search/GraphRAG.
25. **Đóng góp cá nhân quan trọng nhất?** Một workflow end-to-end có thể chạy lại,
    kết nối property graph và semantic standards, đồng thời mọi answer/derived
    fact/recommendation đều truy ngược được evidence.
