# Evaluation labels

`build_review_corpora.py` tạo ba corpus **silver** tất định từ source ID/evidence TMDB:

- `entity_resolution.json`: 100 case (75 positive/25 negative), có `label_source`.
- `reasoning.json`: 50 fact, có person ID và danh sách phim làm evidence.
- `recommendation.json`: 20 anchor; relevance theo rubric ghi trong từng case.

Chỉ gọi đây là **silver evaluation**, không phải human evaluation độc lập. Reviewer
thứ hai cần đổi `review_status`, sửa nhãn nếu cần và ghi ngày/rubric adjudication.
`make evaluation-corpora` sẽ ghi đè file, nên lưu bản review ở file/branch riêng.
