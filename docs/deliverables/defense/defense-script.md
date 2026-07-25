# Kịch bản bảo vệ và trình diễn

Mục tiêu: 14 phút trình bày + 4 phút trình diễn, giữ 2 phút dự phòng. Nội dung dưới đây
là bảng nhắc nhanh. Nội dung nói chi tiết theo từng slide nằm tại
[speaker-notes-by-slide.md](speaker-notes-by-slide.md).

| Trang chiếu | Thời lượng | Thông điệp phải nói |
|---:|---:|---|
| 1 | 20s | Tên đề tài, phần lý thuyết và nghiên cứu tình huống phim. |
| 2 | 40s | Phân biệt dữ liệu, thông tin, tri thức và suy luận. |
| 3 | 45s | Entity, relationship, property và stable identifier. |
| 4 | 40s | Schema quy định cấu trúc; instance chứa các fact cụ thể. |
| 5 | 40s | Property Graph là mô hình duy nhất; node và cạnh đều có property. |
| 6 | 45s | Cypher vừa query pattern vừa materialize luật `CO_STARRED_WITH`. |
| 7 | 40s | Neo4j phù hợp traversal; không tuyên bố luôn nhanh hơn SQL. |
| 8 | 45s | Đi theo luồng nguồn → cache/processing → Neo4j → FastAPI/UI. |
| 9 | 40s | IMDb chỉ enrich Movie bằng exact ID và streaming gzip. |
| 10 | 40s | Stable ID là khóa; vai trò và metadata được đặt trên cạnh. |
| 11 | 45s | Cache bất biến, manifest, MERGE và import idempotent. |
| 12 | 40s | Đọc đúng quy mô graph và bốn quality gate bằng không. |
| 13 | 45s | Exact trước, fuzzy có kiểm soát; metric chỉ thuộc silver corpus. |
| 14 | 40s | Pattern multi-hop và Cypher có tham số từ catalog cố định. |
| 15 | 40s | Phân biệt asserted fact và derived fact có supporting movie. |
| 16 | 45s | Chín intent; entity linker + query catalog; không sinh Cypher tự do. |
| 17 | 45s | IDF giảm trọng số feature phổ biến; explanation từ contribution thật. |
| 18 | 35s | Giải thích silver/review gate và phép đo hiệu năng 500/1.000/2.000/4.999 cùng protocol. |
| 19 | 45s | QA 20/20; ER P=1,000/R=0,933/F1=0,966; P@10=0,635; NDCG@10=0,672. |
| 20 | 45s | SQLite nhanh hơn cả bốn query; giá trị graph nằm ở mô hình/bằng chứng, không phải luôn nhanh hơn SQL. |
| 21 | 35s | Copy câu QA lookup sang Web UI rồi dùng Cypher bên phải kiểm chứng trong Browser. |
| 22 | 35s | Copy câu QA multi-hop và chỉ ra shared-neighbor pattern trong Browser. |
| 23 | 50s | Chạy gợi ý Inception, thay tên top-1 vào parameter và kiểm chứng shared features. |
| 24 | 35s | Nêu selection bias, corpus nhỏ, warm-cache/concurrency limit và hướng nâng cấp. |
| 25 | 30s | Trả lời RQ bằng ba kết luận, sau đó mời phản biện. |

## Trình diễn trực tiếp — 4 phút

Chuẩn bị trước giờ bảo vệ:

```bash
make demo
```

Giữ terminal này chạy. Mở sẵn ba tab:

- UI: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- Neo4j Browser: `http://127.0.0.1:7474/`

Trình tự trình diễn theo nguyên tắc: **chạy trên Web UI trước, kiểm chứng cùng
sự kiện trên Neo4j Browser ngay sau đó**.

1. **QA trên Web UI (35s):** hỏi:

   ```text
   Diễn viên nào đóng trong phim Inception?
   ```

   Chỉ vào tên phim đã được liên kết, danh sách diễn viên và bằng chứng.

2. **Kiểm chứng lookup trong Neo4j Browser (35s):** chạy:

   ```cypher
   MATCH (p:Person)-[r:ACTED_IN]->(m:Movie)
   WHERE toLower(m.title) = toLower('Inception')
   RETURN p.name AS actor, r.character AS character
   ORDER BY r.cast_order
   LIMIT 50;
   ```

   Đối chiếu các tên với Web UI. Giải thích rằng UI gọi FastAPI, còn Browser
   truy vấn trực tiếp cùng graph Neo4j; cách hiển thị khác nhau nhưng fact phải
   thống nhất.

3. **Multi-hop trên Web UI (35s):** hỏi:

   ```text
   Phim chung của Christian Bale và Tom Hardy?
   ```

   Chỉ vào kết quả `The Dark Knight Rises` và bằng chứng hai diễn viên cùng tham
   gia phim.

4. **Kiểm chứng multi-hop trong Neo4j Browser (35s):** chạy:

   ```cypher
   MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(b:Person)
   WHERE toLower(a.name) = toLower('Christian Bale')
     AND toLower(b.name) = toLower('Tom Hardy')
   RETURN DISTINCT m.title AS common_movie;
   ```

   Chuyển chế độ hiển thị giữa bảng và graph để chỉ ra shared-neighbor pattern.

5. **Gợi ý trên Web UI (45s):** chọn `Inception`, chạy top 5, ghi lại tên kết
   quả đứng đầu và mở phần giải thích. Chỉ vào các đặc trưng chung và contribution.

6. **Kiểm chứng gợi ý trong Neo4j Browser (45s):** thay giá trị dưới đây bằng
   đúng tên kết quả đứng đầu vừa thấy trên Web UI:

   ```cypher
   :param candidate_title => 'Interstellar';
   ```

   Sau đó chạy query kiểm tra bằng chứng:

   ```cypher
   MATCH (source:Movie {tmdb_id: 27205})
   MATCH (candidate:Movie {title: $candidate_title})
   CALL (source, candidate) {
     MATCH (source)<-[:DIRECTED]-(f:Person)-[:DIRECTED]->(candidate)
     RETURN 'director' AS kind, f.name AS feature
     UNION
     MATCH (source)<-[:ACTED_IN]-(f:Person)-[:ACTED_IN]->(candidate)
     RETURN 'actor' AS kind, f.name AS feature
     UNION
     MATCH (source)-[:HAS_GENRE]->(f:Genre)<-[:HAS_GENRE]-(candidate)
     RETURN 'genre' AS kind, f.name AS feature
     UNION
     MATCH (source)-[:HAS_KEYWORD]->(f:Keyword)<-[:HAS_KEYWORD]-(candidate)
     RETURN 'keyword' AS kind, f.name AS feature
     UNION
     MATCH (source)-[:PRODUCED_BY]->(f:Studio)<-[:PRODUCED_BY]-(candidate)
     RETURN 'studio' AS kind, f.name AS feature
   }
   RETURN candidate.title AS recommended_movie,
          kind, collect(DISTINCT feature) AS shared_features;
   ```

   Đối chiếu `shared_features` với phần giải thích trên Web UI. Query này kiểm
   chứng bằng chứng graph; điểm và thứ hạng vẫn do query IDF đầy đủ của ứng dụng
   tính trong `src/recommendation/neo4j_service.py`.

7. **Kết luận luồng (20s):** nói rõ:

   ```text
   Web UI → FastAPI → Cypher có tham số → Neo4j
   Neo4j Browser ─────────────────────→ Neo4j
   ```

   Hai đường truy cập khác nhau nhưng đọc cùng một cơ sở dữ liệu.

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
