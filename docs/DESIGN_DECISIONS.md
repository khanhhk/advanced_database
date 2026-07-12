# Design decisions và lý do lựa chọn

Tài liệu này ghi lại quyết định kiến trúc theo dạng: vấn đề, lựa chọn, lý do,
trade-off và phương án bị loại. Nội dung có thể dùng trực tiếp cho chương thiết
kế hệ thống và phần hỏi đáp khi bảo vệ.

## DD-01 — Neo4j là operational database

**Vấn đề:** Dữ liệu phim có nhiều quan hệ many-to-many và competency questions
cần traversal/multi-hop.

**Quyết định:** Dùng Neo4j 5 Property Graph làm serving backend.

**Lý do:** Cypher biểu diễn pattern traversal trực tiếp; relationship có property;
shortest path, common neighbor và recommendation cùng chạy trên một mô hình.

**Trade-off:** Neo4j thêm một runtime riêng và kỹ năng Cypher; không chứng minh nó
luôn nhanh hơn SQL.

**Không chọn:** PostgreSQL làm serving store vì join table và recursive query làm
giảm độ trực quan của phần graph-centric; RDF store vì property-rich operational
query và triển khai demo phức tạp hơn.

## DD-02 — RDF/OWL là standards artifact, không phải serving backend

**Quyết định:** Export một tập con RDF/OWL và cung cấp SPARQL equivalents.

**Lý do:** Đáp ứng phần ontology/interoperability và so sánh semantic standards
nhưng không nhân đôi operational path.

**Trade-off:** RDF export không phản ánh mọi tối ưu/property của Neo4j runtime.

## DD-03 — Stable source ID thay cho tên

**Quyết định:** Dùng TMDB/IMDb/source IDs làm khóa; tên chỉ để hiển thị/tìm kiếm.

**Lý do:** Tên có thể trùng, đổi hoặc khác dấu/chính tả. Stable ID giúp import
idempotent và entity resolution có thể audit.

## DD-04 — Một label Person, vai trò nằm trên relationship

**Quyết định:** Không tách Actor và Director thành hai node class.

**Lý do:** Một người có thể giữ cả hai vai trò. `ACTED_IN` và `DIRECTED` biểu diễn
semantics chính xác hơn duplicate Person node.

## DD-05 — Raw cache bất biến và processed manifest

**Quyết định:** Cache raw response/file, tạo normalized artifacts và manifest.

**Lý do:** Giảm network dependency, giữ provenance, cho phép tái xử lý và so sánh
dataset.

**Trade-off:** Tốn disk và cần quản lý cache/version.

## DD-06 — Chỉ stream IMDb Ratings

**Quyết định:** Không tải/nạp toàn bộ IMDb datasets; chỉ stream file rating GZIP.

**Lý do:** Storage-bounded, đúng nhu cầu enrichment và tránh biến đề tài thành
data engineering quy mô lớn không cần thiết.

## DD-07 — LLM chỉ làm Question Planner

**Vấn đề:** Regex intent buộc người dùng hỏi gần đúng form; LLM-to-Cypher lại khó
kiểm soát.

**Quyết định:** LLM chuyển câu hỏi thành QueryPlan JSON, không viết Cypher.

**Lý do:** Tăng độ linh hoạt ngôn ngữ nhưng giữ query surface trong whitelist,
test được và có failure mode rõ.

**Trade-off:** Compiler vẫn phải được mở rộng khi thêm kiểu query mới; hệ thống
không phải open-domain QA.

**Không chọn:** LLM trả lời trực tiếp vì không đảm bảo grounded evidence; LLM sinh
Cypher tự do vì có nguy cơ schema hallucination, query đắt và khó đánh giá.

## DD-08 — QueryPlan DSL thay cho danh sách intent ngày càng dài

**Quyết định:** Dùng operation + target + entities + filters + sort + limit.

**Lý do:** Một plan có thể tổ hợp director, genre, rating và sort mà không cần
intent riêng cho mọi tổ hợp.

**Trade-off:** DSL và compiler phức tạp hơn catalog template nhỏ.

## DD-09 — Giữ 9-intent parser làm fallback

**Quyết định:** Không xóa parser deterministic.

**Lý do:** Demo vẫn hoạt động khi model/GPU/network tunnel không khả dụng; test
catalog vẫn nhanh và deterministic.

**Trade-off:** Duy trì hai đường parsing và cần test để tránh lệch behavior.

## DD-10 — Chọn Qwen3-8B-AWQ

**Yêu cầu:** Hiểu tiếng Việt, instruction following tốt, output có cấu trúc và
chạy trên RTX 3060 12 GB.

**Quyết định:** `Qwen/Qwen3-8B-AWQ`.

**Lý do:**

- Qwen3 có multilingual instruction-following.
- 8B đủ năng lực cho câu hỏi kết hợp nhưng vẫn triển khai được trên một GPU.
- AWQ giảm footprint weights so với BF16.
- vLLM hỗ trợ OpenAI-compatible endpoint và constrained JSON output.
- Apache 2.0 thuận tiện cho nghiên cứu/demo.

**Trade-off:** Quantization có thể giảm nhẹ chất lượng; VRAM gần đầy; máy GPU là
dependency của nhánh planner.

**Không chọn:** Model 3B vì rủi ro kém ổn định với tiếng Việt và schema phức tạp;
BF16 8B vì khoảng 16 GB weights không vừa 12 GB VRAM; API cloud vì phụ thuộc
Internet/quota và khó tái lập.

## DD-11 — vLLM làm model server

**Quyết định:** Chạy Qwen bằng vLLM trong `.venv-llm` riêng.

**Lý do:** OpenAI-compatible API khớp client hiện tại; quản lý KV cache và GPU
serving tốt; hỗ trợ JSON Schema constrained decoding.

**Trade-off:** Dependency CUDA/PyTorch lớn. Vì vậy không cài chung `.venv`.

## DD-12 — AWQ + 4.096 context + non-thinking

**Quyết định:** AWQ, context 4096, `/no_think`, GPU utilization 0.85.

**Lý do:** Prompt/schema và câu hỏi ngắn; context dài hơn không đem lại giá trị
nhưng tốn KV cache. Thinking content không cần cho extraction và có thể làm tăng
latency/rủi ro output.

## DD-13 — Native sampler trên máy hiện tại

**Quyết định:** `VLLM_USE_FLASHINFER_SAMPLER=0`.

**Lý do:** FlashInfer sampling warm-up cố JIT bằng `nvcc`, trong khi máy có NVIDIA
driver nhưng không có CUDA toolkit tại `/usr/local/cuda`. Native sampler chạy
được mà không thay đổi hệ thống.

## DD-14 — Pydantic JSON Schema constrained decoding

**Quyết định:** Gửi `QueryPlan.model_json_schema()` trong `response_format`.

**Lý do:** `json_object` chỉ bảo đảm JSON hợp lệ, không ngăn model đổi list thành
object hoặc bỏ field. JSON Schema buộc output đúng cấu trúc trước Pydantic
validation.

## DD-15 — Entity linking sau LLM

**Quyết định:** LLM trích surface name; application liên kết về canonical node.

**Lý do:** Model không biết chắc entity nào tồn tại trong graph. Tách extraction
và linking cho phép đo confidence và trả evidence.

## DD-16 — IDF-weighted graph similarity

**Vấn đề:** Đếm số quan hệ chung khiến genre/actor quá phổ biến chi phối ranking.

**Quyết định:** Mỗi feature chung nhận type weight nhân IDF-like rarity.

**Lý do:** Feature hiếm có tính phân biệt cao hơn; score và explanation đều truy
vết được về graph.

**Không chọn:** Cosine embedding vì làm mờ đóng góp Knowledge Graph; ba ranker cho
người dùng chọn vì tăng phức tạp mà không tăng giá trị UX.

## DD-17 — Chỉ hai chức năng trên UI

**Quyết định:** QA và similar-movie recommendation.

**Lý do:** Hai chức năng có mục đích khác nhau và đều graph-native. Semantic
search bị loại vì overlap với recommendation và phụ thuộc vector retrieval.

## DD-18 — Explainability từ evidence, không từ text generation

**Quyết định:** Explanation recommendation được dựng bằng template từ shared
features; QA evidence là graph rows/path/entity links.

**Lý do:** Người dùng có thể kiểm tra lý do; không để LLM bịa explanation.

## DD-19 — Silver evaluation và claim discipline

**Quyết định:** Lưu labels, rubric, config và result; gọi rõ là silver.

**Lý do:** Tránh biến vài demo case thành claim khoa học quá mức. Metric phải gắn
với dataset, backend, K và protocol.

## DD-20 — SSH tunnel cho demo từ máy khác

**Quyết định:** vLLM bind localhost; máy demo forward port bằng SSH.

**Lý do:** Không public unauthenticated model endpoint; không cần cài model/GPU ở
máy demo; FastAPI vẫn gọi `127.0.0.1:8001`.

## Cách dùng trong báo cáo

Mỗi quyết định có thể chuyển thành một đoạn gồm: yêu cầu → lựa chọn → lý do →
trade-off. Không chỉ liệt kê technology stack; phải chứng minh lựa chọn giải
quyết một vấn đề cụ thể của domain hoặc deployment.
