# Hình minh họa của báo cáo

Các chương gọi sẵn các tệp dưới đây bằng `\reportfigure`. Toàn bộ 14 PDF hiện
đã được sinh và sẽ tự động xuất hiện khi biên dịch báo cáo.

- `movie_kg_overview.pdf`
- `ontology_diagram.pdf`
- `property_graph_schema.pdf`
- `system_architecture.pdf`
- `entity_resolution_flow.pdf`
- `etl_pipeline.pdf`
- `costar_reasoning.pdf`
- `semantic_reasoning.pdf`
- `qa_sequence.pdf`
- `recommendation_explanation.pdf`
- `web_ui.pdf`
- `quality_metrics.pdf`
- `recommendation_ablation.pdf`
- `query_latency.pdf`

Ưu tiên PDF cho sơ đồ/biểu đồ để chữ và đường nét không vỡ. Nếu dùng PNG/JPG,
đổi phần mở rộng tương ứng trong lời gọi `\reportfigure` của file chương.

## Tái tạo và chỉnh sửa

Chạy từ thư mục gốc:

```bash
python3 scripts/generate_report_figures.py
```

- Nguồn chỉnh sửa của 11 sơ đồ nằm trong `images/sources/*.drawio`.
- Ba biểu đồ thực nghiệm đọc trực tiếp CSV/JSON trong `experiments/results/`.
- `web_ui.pdf` là wireframe trung thực với HTML hiện tại, không phải ảnh chụp.
  Có thể thay file này bằng screenshot thật cùng tên mà không sửa LaTeX.
