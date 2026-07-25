# Hình minh họa của báo cáo

Các chương gọi sẵn các tệp dưới đây bằng `\reportfigure`. Đây là asset của bộ
nguồn LaTeX và phải được tải lên Overleaf cùng các file `.tex`.

- `movie_kg_overview.pdf`
- `property_graph_schema.pdf`
- `entity_resolution_flow.pdf`
- `costar_reasoning.pdf`
- `qa_sequence.pdf`
- `recommendation_explanation.pdf`
- `web_ui.pdf`
- `quality_metrics.pdf`
- `recommendation_ablation.pdf`
- `query_latency.pdf`

Ưu tiên PDF cho sơ đồ/biểu đồ để chữ và đường nét không vỡ. Nếu dùng PNG/JPG,
đổi phần mở rộng tương ứng trong lời gọi `\reportfigure` của file chương.

- Nguồn chỉnh sửa của 11 sơ đồ nằm trong `images/sources/*.drawio`.
- Ba biểu đồ thực nghiệm phản ánh snapshot kết quả hiện tại trong
  `experiments/results/`.
- `web_ui.pdf` là wireframe trung thực với HTML hiện tại, không phải ảnh chụp.
  Có thể thay file này bằng screenshot thật cùng tên mà không sửa LaTeX.

Repository không còn script tái tạo các PDF này. Khi thay đổi số liệu hoặc sơ đồ,
cần xuất lại asset tương ứng theo đúng tên file trước khi tải lên Overleaf.
