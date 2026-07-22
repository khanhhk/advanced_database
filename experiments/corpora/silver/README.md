# Corpus silver

Các JSON trong thư mục này được sinh tất định từ TMDB và rubric của project. Chúng
phục vụ smoke test và đánh giá tái lập, nhưng không phải nhãn độc lập của con người.

- `entity_resolution.json`: 100 cặp entity resolution.
- `qa.json`: 20 câu hỏi QA có assertion và evidence mong đợi.
- `reasoning.json`: 50 fact co-star có evidence phim chung.
- `recommendation.json`: 20 anchor với tập relevance theo rubric.

Sinh lại bằng `.venv/bin/python -m experiments.corpora.build_review_corpora`.
Không chỉnh sửa thủ công để làm tăng metric.
