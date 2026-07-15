# Movie Knowledge Graph — Bộ kế hoạch project

Đây là bộ tài liệu lập kế hoạch cho project cuối khóa **Advanced Database** với chủ đề Knowledge Graph trong miền phim ảnh.

## Danh sách tài liệu

1. [Kế hoạch tổng thể](PROJECT_PLAN.md)
2. [Kế hoạch triển khai code](CODE_PLAN.md)
3. [Dàn ý báo cáo](REPORT_OUTLINE.md)
4. [Bản thảo báo cáo chính](REPORT_DRAFT.md)
5. [Dàn ý slide bảo vệ](SLIDE_OUTLINE.md)
6. [Tài liệu kỹ thuật theo hiện trạng](TECHNICAL_DOCUMENTATION.md)
7. [Sơ đồ flow kỹ thuật](movie_knowledge_graph_flow.drawio)
8. [Giải thích từng block và flow kiến trúc](ARCHITECTURE_EXPLAINED.md)
9. [Quyết định thiết kế và lý do lựa chọn](DESIGN_DECISIONS.md)
10. [Runbook dựng Qwen3-8B-AWQ với vLLM](QWEN_VLLM_DEPLOYMENT.md)
11. [Guide nguồn nội dung cho report và slide](REPORT_SLIDE_SOURCE_GUIDE.md)

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

## Tài liệu nguồn đã sử dụng

- `sources/8_Biểu diễn tri thức.pptx`
- `sources/Ontology_va_Ung_dung.pptx`
- `sources/Co-so-du-lieu-do-thi-Graph-Database.pptx`
- `sources/KnowledgeGraph_50slide_VN  -  Repaired.pptx`
- `sources/Knowledge_Graph_AI_Agent_50slides.pptx`
- `sources/KnowledgeGraph_KhungNoiDung_ChiTiet.docx`
