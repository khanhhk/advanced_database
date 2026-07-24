# Movie Knowledge Graph — Tài liệu dự án

Thư mục này tập hợp tài liệu kỹ thuật, hướng dẫn vận hành và tài liệu chuẩn bị
nộp/bảo vệ project **Advanced Database** về Movie Knowledge Graph.

## Nhóm tài liệu

- [Technical](technical/README.md): kiến trúc hệ thống, sơ đồ và kế hoạch triển
  khai code.
- [Runbooks](runbooks/README.md): quy trình chạy demo và DBeaver.
- [Deliverables](deliverables/README.md): ma trận tiêu chí, nội dung báo cáo và
  tài liệu chuẩn bị bảo vệ.

## Thứ tự ưu tiên

1. Source code, cấu hình, test và root `README.md` mô tả hệ thống đang chạy.
2. `report_latex/` là nguồn báo cáo chính thức để tải thủ công lên Overleaf.
3. [Bản thảo Markdown](deliverables/report/draft.md) chỉ là tài liệu tham khảo.
4. [Dàn ý báo cáo](deliverables/report/outline.md) và
   [dàn ý slide](deliverables/defense/slide-outline.md) là checklist nội dung.
5. [Runbook demo](runbooks/demo.md) là tài liệu dùng trực tiếp khi trình bày.

Repository không lưu PDF/PPTX đầu ra hoặc script tự sinh các file đó.

## Tên đề tài

> Xây dựng Movie Knowledge Graph phục vụ hỏi–đáp và gợi ý phim có khả năng giải thích

## Sản phẩm chính

- Pipeline thu thập, làm sạch và liên kết dữ liệu TMDB/IMDb.
- Neo4j Property Graph và tập con RDF/OWL/SPARQL.
- Reasoning, hỏi–đáp theo intent/template và recommendation có giải thích.
- API, giao diện web, kiểm thử và bằng chứng đánh giá tái lập được.
- Mã nguồn LaTeX của báo cáo và bộ tài liệu chuẩn bị bảo vệ.
