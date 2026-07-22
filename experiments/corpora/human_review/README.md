# Human review

Thư mục chứa pack mù dành cho reviewer độc lập. File hiện tại vẫn ở trạng thái
`pending-human-review`; không được gọi kết quả là human-reviewed cho đến khi đủ
reviewer ID, thời gian, quyết định và adjudication theo rubric.

Tạo pack bằng `.venv/bin/python -m experiments.corpora.build_entity_review_pack`,
sau đó validate và evaluate theo hướng dẫn tại `../README.md`.
