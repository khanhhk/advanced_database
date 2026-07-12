# Nguồn nội dung cho report và slide

Tài liệu này ánh xạ claim cần trình bày tới tài liệu kỹ thuật và artifact, giúp
report/slide nhất quán với implementation.

## 1. Narrative cốt lõi

1. Dữ liệu phim tự nhiên là graph vì các thực thể liên kết nhiều-nhiều.
2. Pipeline đa nguồn tạo graph có stable ID, provenance và quality checks.
3. Neo4j hỗ trợ traversal, reasoning và evidence-backed applications.
4. Qwen tăng khả năng hiểu cách diễn đạt nhưng bị giới hạn ở QueryPlan.
5. Safe compiler giữ quyền kiểm soát query; Neo4j vẫn là nguồn trả lời.
6. Recommendation dùng rarity-weighted graph evidence và explanation.
7. Evaluation/reproducibility ngăn claim chỉ dựa trên demo case.

## 2. Mapping chương báo cáo

| Phần report | Nguồn chính |
|---|---|
| Bài toán và động lực graph | `PROJECT_PLAN.md`, `ARCHITECTURE_EXPLAINED.md` |
| Lựa chọn công nghệ | `DESIGN_DECISIONS.md` |
| Pipeline dữ liệu | `TECHNICAL_DOCUMENTATION.md` mục 4 |
| Graph schema | `TECHNICAL_DOCUMENTATION.md` mục 5 |
| Kiến trúc tổng thể | draw.io + `ARCHITECTURE_EXPLAINED.md` |
| QA/LLM | `ARCHITECTURE_EXPLAINED.md` mục 4, `QWEN_VLLM_DEPLOYMENT.md` |
| Recommendation | `TECHNICAL_DOCUMENTATION.md` mục 7, `DESIGN_DECISIONS.md` DD-16 |
| API/UI | `TECHNICAL_DOCUMENTATION.md` mục 8–9 |
| Security/guardrail | `TECHNICAL_DOCUMENTATION.md` mục 12 |
| Evaluation | `TECHNICAL_DOCUMENTATION.md` mục 14 + `experiments/results` |
| Limitations | `TECHNICAL_DOCUMENTATION.md` mục 17 |

## 3. Mapping slide

### Slide kiến trúc

Dùng `movie_knowledge_graph_flow.drawio`. Khi thuyết trình, đi theo request path,
không đọc mọi block:

> Dữ liệu được chuẩn hóa vào Neo4j. Với QA, Qwen chỉ tạo QueryPlan; entity linker
> và compiler kiểm soát Cypher; Neo4j trả evidence. Với recommendation, Neo4j
> tính IDF similarity trực tiếp. FastAPI trình bày hai chức năng trên UI.

### Slide “Vì sao dùng LLM nhưng vẫn an toàn”

Ba dòng:

- Regex cứng → không hiểu nhiều cách diễn đạt.
- LLM-to-Cypher → khó kiểm soát.
- QueryPlan constrained → cân bằng flexibility và safety.

### Slide Qwen deployment

Chỉ hiển thị:

- Qwen3-8B-AWQ, vLLM 0.25.0.
- RTX 3060 12 GB, context 4096, non-thinking.
- JSON Schema constrained output.
- Localhost/SSH tunnel.

Chi tiết lỗi torchcodec/nvcc để ở backup slide hoặc phần hỏi đáp.

### Slide recommendation

Hiển thị công thức:

```text
weight(type) × (1 + ln((N+1)/(df+1)))
```

Giải thích một câu: feature chung hiếm có giá trị phân biệt cao hơn feature phổ
biến; explanation liệt kê chính các feature đóng góp.

### Slide evaluation

Phải ghi rõ:

- Dataset 2.000 Movie.
- Corpus silver.
- K=10 cho P@10/NDCG@10.
- Backend Neo4j thật đối với result production ranker.
- Benchmark có warm-up, 100 iteration và metadata máy.

## 4. Claim → evidence

| Claim | Evidence/artifact |
|---|---|
| Import không duplicate | constraints, MERGE, integration test, validation result |
| Graph không orphan/invalid edge | processed/validation output và project memory |
| Entity linking tốt trên silver corpus | `experiments/results/entity_resolution.json` |
| Reasoning có evidence | `experiments/results/reasoning.json` |
| Recommendation cải thiện baseline | `recommendation.json`, `recommendation_ablation.json` |
| Neo4j latency | `neo4j_benchmark.csv` + `.metadata.json` |
| Qwen output đúng schema | `tests/unit/test_planner.py` + smoke-test runbook |
| Query chống injection | Pydantic Literals, whitelist mapping, parameter tests |

## 5. Những điều không nên claim

- Không nói Knowledge Graph luôn nhanh hơn relational database.
- Không nói silver corpus là gold human evaluation.
- Không nói P@10/NDCG chứng minh mọi người dùng sẽ thích recommendation.
- Không gọi IDF score là xác suất hoặc phần trăm yêu thích.
- Không nói Qwen trả lời câu hỏi; Qwen chỉ lập kế hoạch.
- Không gọi hệ thống open-domain QA.
- Không suy rộng benchmark một quy mô thành scalability result.

## 6. Câu trả lời chuẩn cho các câu hỏi bảo vệ

### “Tại sao không cho LLM sinh Cypher?”

Vì model có thể hallucinate label/relationship, tạo query đắt hoặc không bảo đảm
read-only. QueryPlan + compiler giữ flexibility ngôn ngữ nhưng giới hạn execution
surface.

### “Nếu GPU/model chết thì sao?”

QA fallback về parser 9 intent. Recommendation và Neo4j không phụ thuộc LLM.

### “Tại sao Qwen3-8B-AWQ?”

Nó cân bằng multilingual instruction-following và footprint trên RTX 3060 12 GB;
AWQ giảm memory, vLLM cung cấp structured output.

### “Recommendation dựa vào tiêu chí gì?”

Mức hiếm và loại của các quan hệ chung: director, actor, keyword, genre, studio.
Feature phổ biến bị discount; mọi đóng góp đều có evidence trong graph.

### “Ba chức năng cũ đâu?”

Semantic search bị loại vì overlap với recommendation và phần ranking chính dựa
trên vector, không làm nổi bật Knowledge Graph. UI giữ QA và recommendation.

## 7. Checklist trước khi chốt report/slide

- [ ] Kiểm tra claim với source code hiện tại.
- [ ] Dùng đúng số liệu trong result artifacts.
- [ ] Ghi backend, dataset size, corpus type và metric definition.
- [ ] Đồng bộ tên operation/endpoint/model.
- [ ] Không đưa semantic search đã xóa vào kiến trúc hiện tại.
- [ ] Phân biệt TMDB rating và IMDb rating.
- [ ] Giải thích trade-off, không chỉ liệt kê công nghệ.
- [ ] Có backup slide cho QueryPlan schema, guardrail và Qwen deployment.
