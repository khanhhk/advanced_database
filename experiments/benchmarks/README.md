# Benchmark

Thư mục chứa benchmark truy vấn trên Neo4j, SQLite và workflow đa quy mô.

- `benchmark_neo4j.py`: đo latency QA trên Neo4j.
- `benchmark_relational.py`: baseline SQLite cùng snapshot.
- `snapshot_subset.py`: tạo induced snapshot xác định theo số Movie.
- `benchmark_multiscale.py`: chạy hai backend ở 500/1.000/2.000/4.999 Movie.

Kết quả nằm trong `experiments/results/benchmarks/`. Workflow đa quy mô có thể
reset Neo4j test nên chỉ chạy với Bolt 7688 và các guard
`RUN_NEO4J_TESTS=1`, `ALLOW_NEO4J_TEST_RESET=1`,
`ALLOW_MULTISCALE_BENCHMARK=1`. Không trỏ workflow này vào graph demo.
