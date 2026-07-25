# Trang chiếu

Thư mục này quản lý nội dung dành riêng cho bộ trang chiếu:

- [outline.md](outline.md): cấu trúc, nội dung và thời lượng dự kiến
  của từng trang chiếu.
- `build.js`: nguồn PptxGenJS tạo bộ trang chiếu.
- `assets/`: ảnh xuất từ các nguồn draw.io của báo cáo.
- `movie_knowledge_graph_defense.pptx`: bản PowerPoint hoàn chỉnh gồm 31 trang
  và ghi chú thuyết trình. Deck giải thích tương đối đầy đủ các khái niệm được
  dùng trong project, gồm identity, schema/instance, Property Graph, traversal,
  constraint/index, entity resolution/linking, inference, provenance/evidence,
  graph similarity và evaluation metrics. Movie Knowledge Graph được dùng làm
  ví dụ xuyên suốt; chi tiết source code và vận hành được giữ trong báo cáo.
- `rendered/movie_knowledge_graph_defense.pdf`: bản kết xuất dùng để kiểm tra
  bố cục và trình chiếu dự phòng.

Văn bản, hình khối, bảng và biểu đồ trong PPTX là các đối tượng PowerPoint có
thể chỉnh sửa. Các sơ đồ phức tạp được chèn dưới dạng ảnh có độ phân giải cao;
nguồn chỉnh sửa tương ứng nằm trong `report_latex/images/sources/*.drawio`.

Tạo lại PPTX:

```bash
npm ci
node docs/deliverables/slide/build.js
```

Số liệu trên trang chiếu phải thống nhất với báo cáo và các sản phẩm thực
nghiệm hiện tại.
