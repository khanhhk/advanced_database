# Evaluator

Các module trong thư mục này tính metric từ processed snapshot, corpus silver
hoặc Neo4j. Chạy từ repository root với `python -m`.

- `audit_knowledge_quality.py`: identity, consistency, completeness, provenance.
- `evaluate_entity_resolution.py`: precision/recall/F1 trên corpus entity.
- `evaluate_qa_neo4j.py`: smoke QA trên Neo4j production path.
- `evaluate_reasoning.py`: precision của fact co-star.
- `evaluate_recommendation_neo4j.py`: P@K/NDCG@K của ranker production.
- `evaluate_recommendation_fixture.py`: regression evaluator trên fixture nhỏ;
  không phải bằng chứng production.

Output mặc định nằm trong `experiments/results/evaluation/` hoặc
`experiments/results/quality/`. Các evaluator dùng Neo4j chỉ đọc graph; chúng
không được tự reset database.
