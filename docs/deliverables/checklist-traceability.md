# Ma trận truy vết 20 tiêu chí ChecklistCSDLNCv2

Nguồn chuẩn: sheet **N5. Tri thức & Ngữ nghĩa** trong `ChecklistCSDLNCv2.XLS`.
“Đủ bằng chứng repo” nghĩa là nội dung và sản phẩm đầu ra đã tồn tại; điểm chữ vẫn do
giảng viên quyết định. Tiêu chí 19–20 phụ thuộc phần thể hiện trực tiếp của người
trình bày nên repo chỉ có thể chuẩn bị và kiểm soát đầu vào.

| # | Tiêu chí rút gọn | Bằng chứng chính | Trạng thái |
|---:|---|---|---|
| 1 | Bài toán, phạm vi, mục tiêu, lý do chọn CSDL | Báo cáo §1.1; trang chiếu 2–5 | Đủ bằng chứng repo |
| 2 | Survey, trích dẫn tài liệu/bài báo mới | Báo cáo §1.2; `report_latex/ref.bib` | Đủ bằng chứng repo |
| 3 | So sánh relational/giải pháp thay thế | Báo cáo §1.3; trang chiếu 6, 21; phép đo hiệu năng SQLite | Đủ bằng chứng repo |
| 4 | Ontology, KG schema, triple/quad, namespace, Linked Data | Báo cáo §2.1; `ontology/movie_ontology.ttl`; trang chiếu 9, 17 | Đủ; nêu rõ triple, named graph là extension |
| 5 | Entailment, rule và suy luận ontology | Báo cáo §2.2; `cypher/reasoning.cypher`; semantic result | Đủ bằng chứng repo |
| 6 | Phân giải thực thể, nhất quán, đầy đủ | Báo cáo §2.3; quality audit; ER silver corpus và metrics | Đủ bằng chứng kỹ thuật; giới hạn silver được nêu rõ |
| 7 | Chọn/cấu hình DBMS và công cụ | Báo cáo §3.1; Compose/Dockerfile/pyproject; trang chiếu 6 | Đủ bằng chứng repo |
| 8 | Nguồn, kích thước, tiền xử lý, nạp dữ liệu | Báo cáo §3.2; manifest; quy trình xử lý dữ liệu; trang chiếu 8–10 | Đủ bằng chứng repo |
| 9 | Thiết kế/tinh chỉnh ontology/KG schema | Báo cáo §3.3; ontology; graph schema; RDF exporter | Đủ bằng chứng repo |
| 10 | Cài engine, nạp triple, cấu hình reasoner | Báo cáo §3.4; Neo4j; Jena/Fuseki 6.1; forward rules; 10/10 SPARQL | Đủ trên ảnh chụp dữ liệu RDF đầy đủ |
| 11 | SPARQL/luật/semantic path | Báo cáo §4.1; `sparql/queries.rq`; 10/10 execution | Đủ bằng chứng repo |
| 12 | CRUD đến truy vấn nâng cao | Báo cáo §4.2; `cypher/crud.cypher`, `queries.cypher`; tests | Đủ bằng chứng repo |
| 13 | Truy vấn inference-enabled | Báo cáo §4.3; inferred Turtle; semantic/SPARQL result | Đủ bằng chứng repo |
| 14 | Tiêu chí đánh giá phù hợp | Báo cáo §5.1; trang chiếu 19 | Đủ bằng chứng repo |
| 15 | Phép đo hiệu năng, bảng/biểu đồ, mốc so sánh | Báo cáo §5.2; multi-scale Neo4j/SQLite CSV+metadata+figure | Đủ tại 500/1.000/2.000/4.999; không khái quát ngoài protocol |
| 16 | Phân tích, hạn chế, hướng cải tiến | Báo cáo §5.3; trang chiếu 23 | Đủ bằng chứng repo |
| 17 | Ứng dụng nghiệp vụ và trình diễn UI | Báo cáo chương 6; API/UI; `docs/runbooks/demo.md` | Đủ bằng chứng repo |
| 18 | Chất lượng báo cáo, hình, tham khảo | `report_latex/`, 14 hình PDF/draw.io, `ref.bib` | Đủ bằng chứng repo; PDF cuối phải được kiểm tra trực quan |
| 19 | Trang chiếu, thuyết trình, đúng thời gian | `docs/deliverables/slide/outline.md`; `defense-script.md` | Người trình bày tự chuẩn bị trang chiếu và phải diễn tập |
| 20 | Trả lời phản biện | `docs/deliverables/defense/defense-qa.md` (25 câu), rehearsal checklist | Chuẩn bị đủ; chỉ hội đồng đánh giá trực tiếp |

## Cổng nộp bài

- [x] Đồng bộ MSSV 20252307M giữa bản thảo và trang bìa.
- [ ] Tải `report_latex/` lên Overleaf, biên dịch bằng XeLaTeX và kiểm tra trực quan bản PDF cuối.
- [x] Chạy `make test`: 33/33 cùng compileall và checksum pass.
- [ ] Chạy `make demo` không Internet trên máy sẽ dùng để bảo vệ.
- [ ] Hoàn thành nhật ký diễn tập trong `docs/deliverables/defense/defense-script.md`.
- [ ] Không khái quát silver corpus thành production accuracy và không dùng mốc so sánh lịch
  sử để kết luận production tốt hơn.
