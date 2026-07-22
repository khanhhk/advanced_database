# Movie Knowledge Graph — Bộ kế hoạch project

Đây là bộ tài liệu lập kế hoạch cho project cuối khóa **Advanced Database** với chủ đề Knowledge Graph trong miền phim ảnh.

## Danh sách tài liệu

1. [Kế hoạch triển khai code](CODE_PLAN.md)
2. [Dàn ý báo cáo](REPORT_OUTLINE.md)
3. [Bản thảo báo cáo chính](REPORT_DRAFT.md)
4. [Dàn ý slide bảo vệ](SLIDE_OUTLINE.md)
5. [Sơ đồ flow kỹ thuật](movie_knowledge_graph_flow.drawio)
6. [Giải thích từng block và flow kiến trúc](ARCHITECTURE_EXPLAINED.md)
7. [Runbook dựng Qwen3-8B-AWQ với vLLM](QWEN_VLLM_DEPLOYMENT.md)
8. [Runbook demo Neo4j trên DBeaver Community](DBEAVER_NEO4J_DEMO.md)

## Tên đề tài đề xuất

> Xây dựng Movie Knowledge Graph phục vụ hỏi–đáp và gợi ý phim có khả năng giải thích

## Sản phẩm cuối cùng

- Movie ontology ở định dạng OWL/Turtle.
- Pipeline thu thập, làm sạch và liên kết dữ liệu phim.
- Knowledge Graph trên Neo4j.
- Tập con RDF để minh họa SPARQL và reasoning.
- API hỏi–đáp dựa trên Cypher template.
- API gợi ý phim kèm lý do gợi ý.
- Web demo tối giản.
- Báo cáo thực nghiệm.
- Slide bảo vệ.

## Tài liệu nguồn

Các tài liệu Office dung lượng lớn đã được dùng trong giai đoạn tổng hợp nhưng
không còn lưu trong repository demo. Bản thảo báo cáo, code, cấu hình và artifact
đo hiện tại là nguồn có thể kiểm chứng trong repo.
