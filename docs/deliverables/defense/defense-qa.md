# Bộ câu hỏi phản biện

## Mô hình và lựa chọn công nghệ

1. **Vì sao không chỉ dùng PostgreSQL?** Quan hệ nhiều–nhiều vẫn biểu diễn được
   trong SQL, nhưng các pattern multi-hop, shortest path và đường đi bằng chứng tự nhiên
   hơn trong đồ thị thuộc tính. Phép đo hiệu năng cho thấy SQLite nhanh hơn bốn query kiểm
   soát, nên đề tài không tuyên bố graph luôn nhanh hơn relational.
2. **Đây có thật sự là đồ thị tri thức hay chỉ là graph database?** Hệ thống có stable identity, provenance, graph schema, derived relationship và bằng chứng; Neo4j là lớp lưu trữ và thực thi.
3. **Vì sao chỉ một label Person?** Một người có thể vừa ACTED_IN vừa DIRECTED;
   vai trò thuộc relationship, không phải hai identity tách biệt.

## Dữ liệu và chất lượng

4. **Làm sao tránh trùng người/phim?** Dùng source-qualified stable ID; exact ID
   là chính, fuzzy chỉ fallback có threshold, confidence và log.
5. **Tại sao rating TMDB và IMDb không gộp?** Hai nguồn có thang đo/cộng đồng bỏ
   phiếu khác nhau; giữ riêng bảo toàn provenance và tránh tạo số liệu giả.
6. **Con số 1,0 của phân giải thực thể có đáng tin?** Đó là silver corpus 100 case.
   Kiểm tra toàn bộ ảnh chụp dữ liệu bổ sung zero duplicate/conflict/invalid FK và 100% provenance;
   metric chỉ được dùng trong phạm vi 50 exact-ID, 25 fuzzy positive và 25 hard
   negative của protocol tất định.
7. **Top-20 cast gây ảnh hưởng gì?** Giảm kích thước và thời gian thu thập nhưng
   bỏ diễn viên phụ, làm thiếu edge và có thể ảnh hưởng shortest path/gợi ý.
8. **Quy trình xử lý dữ liệu có tái lập không?** Raw cache, SHA-256, manifest, exact versions,
    idempotent MERGE và sản phẩm đầu ra kết quả cho phép chạy lại cùng ảnh chụp dữ liệu.

## Suy diễn và truy vấn

9. **`CO_STARRED_WITH` được suy ra thế nào?** Hai Person cùng `ACTED_IN` một
    Movie tạo quan hệ đối xứng, lưu count và supporting movie làm bằng chứng.
10. **Làm sao biết fact suy ra đúng?** Validator kiểm supporting movie/endpoints;
    50 case silver đều có bằng chứng trong source cast.
11. **Truy vấn derived-edge là gì?** Query dùng `CO_STARRED_WITH` sau khi luật Cypher materialize quan hệ từ các phim chung.
12. **Có nguy cơ Cypher injection không?** Input được link thành entity, plan qua
    parser chỉ nhận chín ý định và query catalog cố định; Cypher dùng parameter,
    không nối chuỗi.

## QA, gợi ý và đánh giá

13. **Hệ thống xử lý câu hỏi ngoài phạm vi thế nào?** Parser trả ý định
    `unknown`; hệ thống không sinh Cypher tùy ý. Mọi fact/bằng chứng đều do Neo4j
    trả về.
14. **Vì sao gợi ý gọi là explainable?** Mỗi shared feature đóng góp một
    số điểm xác định; response trả chính feature, loại edge và contribution đó.
15. **Tại sao IDF?** Feature xuất hiện ở nhiều phim ít phân biệt; IDF tăng đóng
    góp của director/actor/keyword hiếm hơn.
16. **Tại sao chỉ số hiện thấp hơn sản phẩm đầu ra cũ?** Ảnh chụp dữ liệu/tập ứng viên thay đổi;
    run hiện tại là nguồn sự thật. Mốc so sánh cũ chỉ là lịch sử và không được dùng
    để kết luận so sánh nếu chưa tái chạy cùng protocol.
17. **QA 20/20 có đủ không?** Đủ cho smoke/regression của chín ý định, chưa đủ để
    chứng minh robust với paraphrase, ambiguity hoặc câu ngoài miền.
18. **Vì sao SQLite nhanh hơn?** Dataset nhỏ và query kiểm soát có index/join phù
    hợp. Neo4j được chọn cho expressiveness, traversal và đường đi bằng chứng, không vì
    một cam kết latency phổ quát.
19. **Phép đo hiệu năng có chứng minh scalability không?** Chưa. Đã đo bốn ảnh chụp dữ liệu con
    500/1.000/2.000/4.999 trên cùng máy và protocol, nhưng chưa đo concurrency, cold cache,
    tài nguyên hoặc quy mô lớn hơn.
20. **Threat lớn nhất là gì?** Popularity sampling, top-20 cast, silver labels và
    external validity phép đo hiệu năng; báo cáo nêu rõ thay vì khái quát hóa quá mức.
21. **Nếu nâng cấp một việc trước tiên?** Bổ sung ER case tự nhiên từ nguồn thứ ba,
    sau đó đo concurrency và ảnh chụp dữ liệu lớn hơn trước khi thêm vector search/GraphRAG.
22. **Đóng góp cá nhân quan trọng nhất?** Một quy trình end-to-end có thể chạy lại,
    dùng một Neo4j Property Graph thống nhất, đồng thời mọi answer/derived
    fact/gợi ý đều truy ngược được bằng chứng.
