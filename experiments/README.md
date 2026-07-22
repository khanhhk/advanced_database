# Thực nghiệm và đánh giá

Thư mục này chứa corpus, evaluator, benchmark, semantic runtime và các artifact
được dùng để kiểm chứng các tuyên bố trong báo cáo. Đây không phải runtime của
API; các lệnh demo chính vẫn nằm trong `Makefile` ở repository root.

## Cấu trúc

- `corpora/`: sinh corpus silver tất định có evidence và rubric.
- `evaluation/`: đánh giá chất lượng dữ liệu, QA, reasoning và recommendation.
- `benchmarks/`: benchmark Neo4j/SQLite và tạo snapshot đa quy mô.
- `semantic/`: đánh giá RDF/SPARQL bằng Apache Jena/Fuseki.
- `reporting/`: tổng hợp kết quả thành bảng và biểu đồ bằng chứng.
- `results/`: artifact đo được, phân nhóm theo loại thực nghiệm.

Chạy module từ repository root bằng `.venv/bin/python -m experiments.<module>`.
Mỗi thư mục con có README riêng mô tả input, output, phụ thuộc và giới hạn.
Các thư mục cache sinh tự động như `__pycache__/` không thuộc cấu trúc nguồn này.

## Quy tắc

- Không chỉnh sửa số liệu trong `results/` bằng tay.
- Không khái quát metric trên corpus silver thành độ chính xác production.
- Benchmark reset graph chỉ được chạy trên Neo4j test ở Bolt 7688 với guard env.
- Artifact lịch sử phải nằm trong `results/history/` và không được trình bày như
  kết quả production hiện tại.
