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
| 4 | Mô hình khái niệm và KG schema | Báo cáo §2.1; `ontology/movie_ontology.ttl`; RDF exporter | Đủ Property Graph schema, OWL class/property, namespace và RDF/Turtle mapping |
| 5 | Luật và suy luận | `cypher/reasoning.cypher`; `src/kg/semantic_reasoning.py`; semantic result JSON | Có rule nghiệp vụ và domain/range/inverse/symmetric entailment, validation tự động |
| 6 | Phân giải thực thể, nhất quán, đầy đủ | Báo cáo §2.3; quality audit; ER silver corpus và metrics | Đủ bằng chứng kỹ thuật; giới hạn silver được nêu rõ |
| 7 | Chọn/cấu hình DBMS và công cụ | Báo cáo §3.1; Compose/Dockerfile/pyproject; trang chiếu 6 | Đủ bằng chứng repo |
| 8 | Nguồn, kích thước, tiền xử lý, nạp dữ liệu | Báo cáo §3.2; manifest; quy trình xử lý dữ liệu; trang chiếu 8–10 | Đủ bằng chứng repo |
| 9 | Thiết kế và tinh chỉnh KG schema | Báo cáo §3.3; Property Graph schema | Đủ bằng chứng trong phạm vi Property Graph |
| 10 | Cài engine, nạp dữ liệu và cấu hình suy luận | Neo4j importer và Cypher materialization | Đủ bằng chứng trong phạm vi Neo4j |
| 11 | Ngôn ngữ truy vấn và đường suy luận | `cypher/reasoning.cypher` | Triển khai bằng Cypher |
| 12 | CRUD đến truy vấn nâng cao | Báo cáo §4.2; `cypher/crud.cypher`, `queries.cypher`; tests | Đủ bằng chứng repo |
| 13 | Truy vấn inference-enabled | Báo cáo §4.3; `CO_STARRED_WITH`; SPARQL Q7–Q8; `sparql_execution.json` | Cypher dùng fact vật chất hóa và SPARQL dùng inverse fact chỉ có sau suy diễn |
| 14 | Tiêu chí đánh giá phù hợp | Báo cáo §5.1; trang chiếu 19 | Đủ bằng chứng repo |
| 15 | Phép đo hiệu năng, bảng/biểu đồ, mốc so sánh | Báo cáo §5.2; multi-scale Neo4j/SQLite CSV+metadata+figure | Đủ tại 500/1.000/2.000/4.999; không khái quát ngoài protocol |
| 16 | Phân tích, hạn chế, hướng cải tiến | Báo cáo §5.3; trang chiếu 23 | Đủ bằng chứng repo |
| 17 | Ứng dụng nghiệp vụ và trình diễn UI | Báo cáo chương 6; API/UI; `docs/runbooks/demo.md` | Đủ bằng chứng repo |
| 18 | Chất lượng báo cáo, hình, tham khảo | `report_latex/`, hình PDF/draw.io, `ref.bib`, PDF đã biên dịch và rà soát | Đủ bằng chứng sau cổng biên dịch/kiểm tra trực quan |
| 19 | Trang chiếu, thuyết trình, đúng thời gian | `docs/deliverables/slide/outline.md`; `defense-script.md` | Người trình bày tự chuẩn bị trang chiếu và phải diễn tập |
| 20 | Trả lời phản biện | `docs/deliverables/defense/defense-qa.md` (22 câu), rehearsal checklist | Chuẩn bị đủ; chỉ hội đồng đánh giá trực tiếp |

## Cổng nộp bài

- [x] Đồng bộ MSSV 20252307M giữa bản thảo và trang bìa.
- [x] Biên dịch XeLaTeX/Tectonic và kiểm tra trực quan PDF 54 trang; khi nộp vẫn
  cần tải toàn bộ `report_latex/` lên Overleaf.
- [x] Chạy lại `make test` sau khi thu hẹp phạm vi: 29/29 test đạt ngày 25/07/2026.
- [ ] Chạy `make demo` không Internet trên máy sẽ dùng để bảo vệ.
- [ ] Hoàn thành nhật ký diễn tập trong `docs/deliverables/defense/defense-script.md`.
- [ ] Không khái quát silver corpus thành production accuracy và không dùng mốc so sánh lịch
  sử để kết luận production tốt hơn.
