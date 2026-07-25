# Kịch bản bảo vệ và trình diễn

Mục tiêu: 14 phút trình bày + 4 phút trình diễn, giữ 2 phút dự phòng. Nội dung dưới đây
là cơ sở để chuẩn bị trang chiếu thủ công khi cần.

| Trang chiếu | Thời lượng | Thông điệp phải nói |
|---:|---:|---|
| 1 | 20s | Tên đề tài, bài toán QA và gợi ý phim có giải thích. |
| 2 | 35s | Dữ liệu phim là mạng nhiều–nhiều; lookup một bảng không đủ cho multi-hop. |
| 3 | 45s | Nêu RQ chính và năm câu hỏi phụ về identity, traversal, inference, gợi ý, validity. |
| 4 | 35s | Chốt các mục tiêu đo được, không hứa các extension ngoài MVP. |
| 5 | 30s | TMDB là graph source, IMDb chỉ enrich Movie bằng exact ID; top-20 cast là giới hạn có chủ đích. |
| 6 | 40s | Một Person có thể mang nhiều vai trò; stable source ID là khóa, không dùng tên. |
| 7 | 45s | Property Graph gồm node, relationship và property; đây là mô hình duy nhất của ứng dụng. |
| 8 | 35s | Neo4j là graph engine duy nhất; SQLite chỉ là mốc so sánh kiểm soát. |
| 9 | 45s | Đi theo luồng nguồn → xử lý → Neo4j → API/UI/evaluation. |
| 10 | 35s | Nêu ảnh chụp dữ liệu, checksum, độ bao phủ IMDb và provenance. |
| 11 | 40s | Cache bất biến, clean, exact join, CSV/manifest, import idempotent. |
| 12 | 45s | Đọc đúng các con số quality gate; không có orphan/duplicate/invalid edge. |
| 13 | 40s | Exact ID trước, fuzzy fallback có confidence; metric 1,0 chỉ là silver corpus. |
| 14 | 45s | Minh họa CRUD, multi-hop, aggregation, shortest path và parameterized Cypher. |
| 15 | 40s | Cypher vừa truy vấn vừa materialize `CO_STARRED_WITH` từ các phim chung. |
| 16 | 40s | Fact suy ra luôn có supporting movie; đây là luật minh bạch, kiểm tra được. |
| 17 | 45s | Parser nhận diện 9 ý định; entity linker + query catalog quyết định Cypher. |
| 18 | 40s | IDF giảm trọng số feature phổ biến; lời giải thích lấy từ contribution thật. |
| 19 | 35s | Giải thích silver/review gate và phép đo hiệu năng 500/1.000/2.000/4.999 cùng protocol. |
| 20 | 45s | QA 20/20; ER P=1,000/R=0,933/F1=0,966; P@10=0,635; NDCG@10=0,672. |
| 21 | 45s | SQLite nhanh hơn cả bốn query; giá trị graph nằm ở mô hình/bằng chứng, không phải luôn nhanh hơn SQL. |
| 22 | 20s | Giới thiệu luồng trình diễn rồi chuyển sang terminal/browser. |
| 23 | 35s | Nêu selection bias, corpus nhỏ, warm-cache/concurrency limit và hướng nâng cấp. |
| 24 | 30s | Trả lời RQ bằng ba kết luận, sau đó mời phản biện. |

## Trình diễn trực tiếp — 4 phút

Chuẩn bị trước giờ bảo vệ:

```bash
make demo
```

Giữ terminal này chạy. Mở sẵn ba tab:

- UI: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- Neo4j Browser: `http://127.0.0.1:7474/`

Trình tự trình diễn:

1. **Health/stats (20s):** mở Swagger, chạy `GET /health` và `GET /stats`.
2. **QA lookup (35s):** hỏi “Ai đóng trong The Dark Knight?”; chỉ vào canonical
   movie, link confidence và bằng chứng.
3. **QA multi-hop (45s):** hỏi phim chung của hai diễn viên hoặc đường liên hệ;
   mở Cypher tương ứng và chỉ ra shared-neighbor pattern hoặc
   `shortestPath([*..8])`; giải thích ý định chỉ chọn query, còn Neo4j thực hiện
   traversal và trả path bằng chứng.
4. **Gợi ý (50s):** chọn một phim bằng autocomplete; chỉ vào shared
   director/actor/genre/keyword/studio và contribution.
5. **Neo4j Browser (50s):** chạy một query trong `cypher/queries.cypher`, ví dụ
   shortest path hoặc co-star; trực quan hóa node/edge.

Nếu UI gặp lỗi, dùng Swagger. Nếu Neo4j Browser không tải, giữ phần QA và
gợi ý trên UI vì chúng vẫn chứng minh backend Neo4j thật. Không thu thập
dữ liệu mới trong buổi trình diễn.

## Nhật ký diễn tập bắt buộc

Chỉ đánh dấu sau khi người trình bày thực sự diễn tập:

- [ ] Chạy trọn vẹn dưới 18 phút, ghi thời gian: ____ phút ____ giây.
- [ ] Trình diễn chạy được khi tắt Internet.
- [ ] Font/biểu đồ đọc được trên màn hình 1920×1080.
- [ ] Thử phương án Swagger khi UI lỗi.
- [ ] Trả lời ngẫu nhiên ít nhất 10 câu trong `docs/deliverables/defense/defense-qa.md`.
- [ ] Người phản biện thử: ____________________  Ngày: ____/____/______.
