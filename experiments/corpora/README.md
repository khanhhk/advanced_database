# Corpus đánh giá và human review

`build_review_corpora.py` tạo ba corpus **silver** tất định từ source ID/evidence
TMDB trong `silver/`; `qa.json` là corpus smoke QA được quản lý cùng nhóm:

- `entity_resolution.json`: 100 case (75 positive/25 negative), có `label_source`.
- `reasoning.json`: 50 fact, có person ID và danh sách phim làm evidence.
- `recommendation.json`: 20 anchor; relevance theo rubric ghi trong từng case.

Chỉ gọi đây là **silver evaluation**, không phải human evaluation độc lập. Reviewer
thứ hai cần đổi `review_status`, sửa nhãn nếu cần và ghi ngày/rubric adjudication.
`.venv/bin/python -m experiments.corpora.build_review_corpora` sẽ ghi đè corpus
silver. Human review phải được lưu trong `human_review/`, không sửa nhãn silver.

Trước khi đổi cách gọi từ `silver` sang `human-reviewed`, mỗi case phải có:

```json
{"generated_by":"generator-id","human_review":{"reviewer_id":"independent-id",
 "reviewed_at":"ISO-8601","decision":"accepted|changed|rejected",
 "rubric_version":"1.0","adjudication_note":"required when changed"}}
```

Chạy `.venv/bin/python -m experiments.corpora.validate_human_review <review-file>`.
Lệnh cố ý thất
bại với corpus silver hoặc review chưa điền; đây là guardrail chống báo cáo nhãn
tự sinh như đánh giá độc lập.

Để tạo pack mù riêng cho entity resolution, chạy
`.venv/bin/python -m experiments.corpora.build_entity_review_pack` rồi điền
`experiments/corpora/human_review/entity_resolution.json`. Mỗi case chỉ hiển thị mention,
candidate và rubric; `is_match`/`expected_id` của silver source không được sao
chép sang pack. Decision hợp lệ là `match`, `no_match` hoặc `abstain`; `match`
phải có `expected_id`, còn `abstain` phải có ghi chú. Sau khi điền:

```bash
.venv/bin/python -m experiments.corpora.validate_human_review \
  experiments/corpora/human_review/entity_resolution.json
.venv/bin/python -m experiments.evaluation.evaluate_entity_review \
  experiments/corpora/human_review/entity_resolution.json
```

## Input và output

- Input chính: `data/raw/tmdb_movies.json` và corpus trong `silver/`.
- Output review: `human_review/entity_resolution.json`.
- Kết quả đánh giá: `experiments/results/evaluation/`.
