# Kịch bản bảo vệ và trình diễn

Mục tiêu: khoảng 18 phút trình bày + 4 phút trình diễn, giữ 2 phút dự phòng. Nội dung dưới đây
là bảng nhắc nhanh. Nội dung nói chi tiết theo từng slide nằm tại
[speaker-notes-by-slide.md](speaker-notes-by-slide.md).

| Trang chiếu | Thời lượng | Thông điệp phải nói |
|---:|---:|---|
| 1 | 35s | Giới thiệu phạm vi lý thuyết, Property Graph, identity và traversal. |
| 2 | 50s | Dẫn từ dữ liệu tới thông tin, tri thức và suy luận có luật. |
| 3 | 45s | Entity, relationship, property và identifier tạo nên một sự kiện có nghĩa. |
| 4 | 45s | Schema quy định cấu trúc; instance chứa các sự kiện cụ thể. |
| 5 | 45s | Property Graph cho phép cả node và relationship mang thuộc tính. |
| 6 | 45s | Neighborhood, path và subgraph phục vụ ba cách khai thác cấu trúc. |
| 7 | 50s | Identity, schema, provenance và competency question tạo lớp tri thức. |
| 8 | 45s | Constraint bảo vệ tính đúng; validation kiểm tra miền; index tăng tốc tìm kiếm. |
| 9 | 45s | Cypher vừa đọc pattern vừa vật chất hóa luật `CO_STARRED_WITH`. |
| 10 | 45s | Hop, degree, common neighbor và shortest path mô tả traversal. |
| 11 | 40s | Neo4j được chọn vì độ phù hợp với quan hệ, traversal và evidence. |
| 12 | 45s | Đi theo luồng nguồn → xử lý → Neo4j → FastAPI/UI. |
| 13 | 45s | Stable ID là khóa; vai trò và metadata được đặt trên quan hệ. |
| 14 | 40s | Đọc đúng quy mô graph và bốn quality gate bằng không. |
| 15 | 45s | Entity resolution ưu tiên exact, fuzzy có kiểm soát và có thể abstain. |
| 16 | 45s | Phân biệt resolution khi xây graph với linking khi xử lý câu hỏi. |
| 17 | 45s | Đọc pattern multi-hop và cách tham số hóa catalog Cypher. |
| 18 | 40s | Phân biệt asserted fact với derived fact có supporting movie. |
| 19 | 45s | Provenance, lineage và evidence trả lời ba câu hỏi truy vết khác nhau. |
| 20 | 45s | Chín intent, entity linker và query catalog; không sinh Cypher tự do. |
| 21 | 45s | IDF giảm ảnh hưởng feature phổ biến; explanation dùng contribution thật. |
| 22 | 45s | Phân biệt precision, recall, F1, P@K và NDCG@K. |
| 23 | 40s | Mỗi claim có corpus, metric, protocol và giới hạn diễn giải riêng. |
| 24 | 45s | Trình bày QA, ER, co-star và recommendation metrics một cách thận trọng. |
| 25 | 40s | Competency question dẫn từ yêu cầu tới schema, query và evidence. |
| 26 | 40s | Demo bước 1–2: QA lookup trên UI và kiểm chứng `ACTED_IN` trong Browser. |
| 27 | 40s | Demo bước 3–4: QA multi-hop và shared-neighbor pattern trong Browser. |
| 28 | 50s | Demo bước 5–6: gợi ý Inception và kiểm chứng shared features. |
| 29 | 40s | Nêu giới hạn và hướng phát triển tương ứng. |
| 30 | 30s | Kết luận bằng tích hợp nhất quán, khai thác quan hệ và evidence. |

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
