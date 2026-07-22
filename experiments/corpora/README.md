# Corpus đánh giá

`build_review_corpora.py` tạo ba corpus **silver** tất định từ source ID và
evidence TMDB trong `silver/`; `qa.json` là corpus smoke QA được quản lý cùng
nhóm:

- `entity_resolution.json`: 100 case gồm 50 exact-ID, 25 fuzzy positive và 25
  nearest-name hard negative.
- `reasoning.json`: 50 fact có person ID và danh sách phim làm evidence.
- `recommendation.json`: 20 anchor với relevance rubric trong từng case.
- `qa.json`: 20 câu smoke test chạy trên production Neo4j path.

Corpus được sinh tất định để regression và tái lập thực nghiệm. Metric chỉ có ý
nghĩa trong phạm vi case, rubric và snapshot đã khai báo; không được khái quát
thành độ chính xác production hoặc sở thích người dùng thực tế.

## Input và output

- Input chính: `data/raw/tmdb_movies.json` và processed snapshot.
- Output: các file JSON trong `silver/`.
- Kết quả evaluator: `experiments/results/evaluation/`.

Chạy lại từ repository root:

```bash
.venv/bin/python -m experiments.corpora.build_review_corpora
```

Lệnh ghi đè corpus silver, vì vậy chỉ chạy khi chủ động thay đổi snapshot hoặc
protocol đánh giá và phải chạy lại các evaluator phụ thuộc sau đó.
