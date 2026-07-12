# Dàn ý slide bảo vệ

Số lượng đề xuất: **18–22 slide** cho phần trình bày **15–20 phút**.

## Slide 1 — Trang bìa

- Tên đề tài.
- Thành viên.
- Giảng viên và học phần.

## Slide 2 — Bối cảnh

- Dữ liệu phim đến từ nhiều nguồn.
- Quan hệ giữa phim, người, thể loại và từ khóa rất đa chiều.

## Slide 3 — Vấn đề

- Dữ liệu phân tán và trùng lặp thực thể.
- Truy vấn nhiều bước phức tạp.
- Recommendation truyền thống khó giải thích.

## Slide 4 — Mục tiêu và phạm vi

- Ontology.
- Pipeline dữ liệu.
- Neo4j Knowledge Graph.
- QA và recommendation.

## Slide 5 — Câu hỏi nghiên cứu

Trình bày một câu hỏi nghiên cứu chính và 3–4 câu hỏi phụ.

## Slide 6 — Vì sao dùng Knowledge Graph?

So sánh ngắn với relational database:

- Biểu diễn quan hệ.
- Truy vấn multi-hop.
- Suy diễn.
- Explainability.

## Slide 7 — Kiến trúc tổng thể

Sử dụng một sơ đồ từ nguồn dữ liệu đến giao diện ứng dụng.

## Slide 8 — Nguồn dữ liệu

- TMDB và IMDb.
- Số phim, người, thể loại và relationship.
- Tỷ lệ thiếu dữ liệu.

## Slide 9 — Movie ontology

- Class hierarchy.
- Object property.
- Data property.
- Một competency question tiêu biểu.

## Slide 10 — Property Graph schema

Hiển thị node và relationship chính bằng sơ đồ trực quan.

## Slide 11 — Pipeline ETL

```text
Collect → Clean → Resolve → Transform → Load → Validate
```

## Slide 12 — Entity resolution

- Khớp chính bằng ID.
- Fuzzy matching khi thiếu ID.
- Precision, Recall và F1.

## Slide 13 — Truy vấn multi-hop

- Một câu hỏi tự nhiên.
- Cypher rút gọn.
- Hình subgraph kết quả.

## Slide 14 — Suy diễn

- Dữ kiện đầu vào.
- Luật `CO_STARRED_WITH`.
- Fact mới được sinh ra.
- Evidence path.

## Slide 15 — Hệ hỏi–đáp

```text
Question → Intent/Slots → Entity Linking → Cypher → Answer + Evidence
```

## Slide 16 — Hệ gợi ý phim

- Công thức scoring.
- Phim đầu vào.
- Top recommendation.
- Lý do gợi ý.

## Slide 17 — Demo

Demo trực tiếp hoặc chèn QR/link. Không dành cả slide cho ảnh giao diện nếu không làm rõ chức năng.

## Slide 18 — Thiết kế thực nghiệm

- Entity resolution metrics.
- Query latency.
- QA accuracy.
- Recommendation relevance.

## Slide 19 — Kết quả

Dùng biểu đồ hoặc bảng nhỏ, tập trung vào 3–5 con số quan trọng nhất.

## Slide 20 — RDF và Property Graph

So sánh ngắn:

| Tiêu chí | RDF/OWL | Neo4j Property Graph |
|---|---|---|
| Chuẩn ngữ nghĩa | Mạnh | Phụ thuộc hệ thống |
| Reasoning | Tốt | Cần query/rule bổ sung |
| Traversal | Phù hợp | Rất thuận tiện |
| Triển khai ứng dụng | Phức tạp hơn | Nhanh và trực quan |

## Slide 21 — Hạn chế và hướng phát triển

- Dữ liệu giải thưởng chưa thuộc MVP.
- QA mới dùng intent/template.
- Mở rộng sang Wikidata, LLM, Vector Search hoặc GraphRAG.

## Slide 22 — Kết luận

- Hệ thống đã xây dựng được gì.
- Kết quả chính.
- Giá trị của Knowledge Graph trong miền phim.

## Phân bổ thời gian

| Phần | Thời gian |
|---|---:|
| Đặt vấn đề và mục tiêu | 2 phút |
| Thiết kế và kiến trúc | 4 phút |
| Triển khai | 4 phút |
| Demo | 4–5 phút |
| Thực nghiệm và kết luận | 3 phút |

## Nguyên tắc thiết kế slide

- Mỗi slide chỉ truyền tải một ý chính.
- Ưu tiên sơ đồ, graph visualization và biểu đồ.
- Không sao chép nguyên đoạn lý thuyết từ report.
- Code chỉ hiển thị phần ngắn cần giải thích.
- Dùng cùng thuật ngữ và màu cho node/relationship trên mọi slide.
- Số liệu phải trùng với report và kết quả chạy cuối cùng.
- Chuẩn bị video demo dự phòng dài dưới 3 phút.

## Checklist trước khi bảo vệ

- [ ] Tất cả hình và chữ đọc được từ cuối phòng.
- [ ] Demo chạy từ seed data, không phụ thuộc mạng.
- [ ] Có sẵn câu hỏi demo và kết quả dự kiến.
- [ ] Slide kết quả có metric và quy mô dataset.
- [ ] Không để lộ API key hoặc mật khẩu.
- [ ] Tập nói thử và giữ đúng thời lượng.
- [ ] Chuẩn bị câu trả lời về ontology, entity resolution, reasoning và lựa chọn Neo4j.

