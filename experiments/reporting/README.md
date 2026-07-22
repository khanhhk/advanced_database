# Tổng hợp bằng chứng

`build_evidence_summary.py` đọc artifact đo được trong `experiments/results/` và
sinh bảng CSV/Markdown cùng SVG dưới `experiments/results/summary/`.

Chạy bằng `.venv/bin/python -m experiments.reporting.build_evidence_summary` sau
khi các evaluator và benchmark đã hoàn tất. Module không chạy thí nghiệm mới và
không được dùng để sửa số đo bằng tay.
