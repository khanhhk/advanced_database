# Đánh giá semantic

`evaluate_jena.py` chạy catalog 10 truy vấn SPARQL trên Apache Jena/Fuseki với
RDFS/OWL rule subset đã khai báo. Cấu hình container nằm trong `jena/`; input là
`ontology/movie_ontology.ttl` và `data/processed/movies.ttl`.

Khởi động profile `semantic`, chạy
`.venv/bin/python -m experiments.semantic.evaluate_jena`, rồi dừng service.
Output mặc định là
`experiments/results/semantic/jena_semantic_evaluation.json`.

Workflow này dùng GenericRuleReasoner forward và không tuyên bố đầy đủ OWL 2 DL.
