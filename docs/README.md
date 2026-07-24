# Đồ thị tri thức phim — Tài liệu dự án

Thư mục này tập hợp tài liệu kỹ thuật, hướng dẫn vận hành và tài liệu chuẩn bị
nộp/bảo vệ project **Advanced Database** về đồ thị tri thức phim.

## Nhóm tài liệu

- [Technical](technical/README.md): kiến trúc hệ thống, sơ đồ và kế hoạch triển
  khai code.
- [Runbooks](runbooks/README.md): quy trình chạy trình diễn và DBeaver.
- [Deliverables](deliverables/README.md): ma trận tiêu chí, nội dung báo cáo và
  tài liệu chuẩn bị bảo vệ.

## Thứ tự ưu tiên

1. Source code, cấu hình, test và root `README.md` mô tả hệ thống đang chạy.
2. `report_latex/` là nguồn báo cáo chính thức để tải thủ công lên Overleaf.
3. [Bản thảo Markdown](deliverables/report/draft.md) chỉ là tài liệu tham khảo.
4. [Dàn ý báo cáo](deliverables/report/outline.md) và
   [dàn ý trang chiếu](deliverables/defense/slide-outline.md) là danh sách kiểm tra nội dung.
5. [Hướng dẫn trình diễn](runbooks/demo.md) là tài liệu dùng trực tiếp khi trình bày.

## Quy ước thuật ngữ

Tài liệu ưu tiên tiếng Việt. Thuật ngữ chuyên ngành được giới thiệu theo dạng
“tiếng Việt (English)”, chẳng hạn đồ thị tri thức (Knowledge Graph), đồ thị thuộc
tính (Property Graph), phân giải thực thể (entity resolution), ảnh chụp dữ liệu
(snapshot), mốc so sánh (baseline) và quy trình xử lý dữ liệu (pipeline). Tên
API, lệnh, đường dẫn, trường dữ liệu, nhãn Neo4j, Cypher và SPARQL được giữ nguyên
để bảo đảm khả năng thực thi.

Repository không lưu PDF/PPTX đầu ra hoặc script tự sinh các file đó.

## Tên đề tài

> Xây dựng đồ thị tri thức phim phục vụ hỏi–đáp và gợi ý phim có khả năng giải thích

## Sản phẩm chính

- Quy trình xử lý dữ liệu thu thập, làm sạch và liên kết dữ liệu TMDB/IMDb.
- Neo4j đồ thị thuộc tính và tập con RDF/OWL/SPARQL.
- Reasoning, hỏi–đáp theo ý định/template và gợi ý có giải thích.
- API, giao diện web, kiểm thử và bằng chứng đánh giá tái lập được.
- Mã nguồn LaTeX của báo cáo và bộ tài liệu chuẩn bị bảo vệ.
