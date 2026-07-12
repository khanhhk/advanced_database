# Dàn ý báo cáo cuối khóa

Độ dài đề xuất: **35–50 trang**, chưa tính phụ lục.

## Trang đầu

- Trang bìa.
- Nhận xét của giảng viên nếu được yêu cầu.
- Lời cảm ơn.
- Tóm tắt tiếng Việt.
- Abstract tiếng Anh.
- Mục lục.
- Danh mục hình, bảng và từ viết tắt.

## Chương 1 — Giới thiệu

### 1.1. Bối cảnh

- Sự phát triển của dữ liệu phim.
- Dữ liệu phân tán và quan hệ đa chiều.
- Hạn chế của mô hình lưu trữ truyền thống đối với truy vấn multi-hop.

### 1.2. Bài toán

- Tích hợp dữ liệu TMDB và IMDb.
- Chuẩn hóa và liên kết thực thể.
- Truy vấn, suy diễn, hỏi–đáp và gợi ý.

### 1.3. Mục tiêu

- Mục tiêu tổng quát.
- Các mục tiêu cụ thể, đo được.

### 1.4. Câu hỏi nghiên cứu

### 1.5. Phạm vi và giới hạn

### 1.6. Đóng góp của đề tài

### 1.7. Cấu trúc báo cáo

## Chương 2 — Cơ sở lý thuyết

### 2.1. Biểu diễn tri thức

### 2.2. Ontology

- Class, individual, property và axiom.
- Taxonomy và ontology.
- Domain, range và cardinality.

### 2.3. RDF, RDFS và OWL

### 2.4. SPARQL và reasoning

### 2.5. Knowledge Graph

### 2.6. Graph Database và Property Graph

### 2.7. Neo4j và Cypher

### 2.8. Entity resolution

### 2.9. Knowledge-based recommendation

### 2.10. So sánh RDF Triple Store và Property Graph

## Chương 3 — Công trình và dữ liệu liên quan

### 3.1. MovieLens, IMDb, TMDB và Wikidata

### 3.2. Các Movie Knowledge Graph hiện có

### 3.3. Hệ hỏi–đáp dựa trên Knowledge Graph

### 3.4. Hệ gợi ý dựa trên Knowledge Graph

### 3.5. Khoảng trống và hướng tiếp cận của đề tài

## Chương 4 — Phân tích yêu cầu

### 4.1. Yêu cầu chức năng

### 4.2. Yêu cầu phi chức năng

### 4.3. Use case

### 4.4. Competency questions

### 4.5. Phạm vi MVP và phần mở rộng

## Chương 5 — Thiết kế ontology và graph schema

### 5.1. Phương pháp thiết kế ontology

### 5.2. Class hierarchy

### 5.3. Object property và data property

### 5.4. Domain, range và ràng buộc

### 5.5. Property Graph schema

### 5.6. Ánh xạ ontology sang Neo4j

### 5.7. Kiểm tra ontology bằng reasoner

## Chương 6 — Kiến trúc và pipeline dữ liệu

### 6.1. Kiến trúc tổng thể

### 6.2. Nguồn dữ liệu

### 6.3. Thu thập và cache dữ liệu

### 6.4. Làm sạch và chuẩn hóa

### 6.5. Entity resolution

### 6.6. Sinh node và relationship

### 6.7. Nạp dữ liệu vào Neo4j

### 6.8. Xuất tập con RDF

## Chương 7 — Truy vấn và suy diễn

### 7.1. Constraints và indexes

### 7.2. Truy vấn Cypher cơ bản

### 7.3. Truy vấn multi-hop

### 7.4. Aggregation và shortest path

### 7.5. Luật suy diễn `CO_STARRED_WITH`

### 7.6. Truy vấn SPARQL tương đương

### 7.7. So sánh Cypher và SPARQL

## Chương 8 — Ứng dụng

### 8.1. Kiến trúc FastAPI

### 8.2. Hệ hỏi–đáp

- Intent detection.
- Slot extraction.
- Entity linking.
- Cypher template.
- Answer formatting và evidence.

### 8.3. Hệ gợi ý phim

- Weighted overlap.
- Weighted Jaccard.
- Cơ chế explanation.

### 8.4. Giao diện demo

### 8.5. An toàn truy vấn

## Chương 9 — Thực nghiệm và kết quả

### 9.1. Môi trường thực nghiệm

### 9.2. Thống kê dataset và đồ thị

### 9.3. Đánh giá entity resolution

### 9.4. Đánh giá tính đúng đắn của đồ thị

### 9.5. Đánh giá reasoning

### 9.6. Đánh giá hiệu năng truy vấn

### 9.7. Đánh giá QA

### 9.8. Đánh giá recommendation

### 9.9. Thảo luận kết quả

Không chỉ báo cáo giá trị trung bình; nên có median, p95, độ lệch và mô tả cấu hình máy.

## Chương 10 — Kết luận

### 10.1. Kết quả đạt được

### 10.2. Trả lời câu hỏi nghiên cứu

### 10.3. Hạn chế

### 10.4. Hướng phát triển

- Award/Wikidata.
- LLM sinh Cypher.
- Vector search và GraphRAG.
- Graph embedding và link prediction.
- Cập nhật dữ liệu gần thời gian thực.

## Tài liệu tham khảo

Ưu tiên:

- Tài liệu W3C về RDF, RDFS, OWL và SPARQL.
- Neo4j Cypher Manual.
- Apache Jena documentation.
- TMDB API documentation.
- IMDb dataset documentation.
- Bài báo học thuật về KG construction, entity resolution và recommender systems.

## Phụ lục

- Ontology đầy đủ.
- Danh sách competency questions.
- Cypher và SPARQL query.
- API specification.
- Test cases.
- Hướng dẫn cài đặt và chạy demo.
- Bảng kết quả thực nghiệm chi tiết.

## Quy tắc nhất quán

- Phân biệt fact lấy từ nguồn, fact đã entity linking và fact được suy diễn.
- Recommendation score không được trình bày như một fact chắc chắn.
- Mọi bảng và hình cần được đánh số, đặt tên và dẫn chiếu trong nội dung.
- Số liệu trong report, slide và demo phải thống nhất.
- Mọi kết luận thực nghiệm phải gắn với metric hoặc bằng chứng.

