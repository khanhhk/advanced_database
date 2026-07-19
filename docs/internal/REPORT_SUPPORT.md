# Tài liệu nội bộ hỗ trợ hoàn thiện report và bảo vệ

Tệp này không thuộc nội dung report chính thức và không được đưa vào bản PDF nộp.
Nó tập hợp các lưu ý trình bày, ma trận truy vết, câu hỏi phản biện và checklist
phục vụ nội bộ cho nhóm.

## Lưu ý khi trình bày

- Không nói Knowledge Graph luôn nhanh hơn SQL.
- Không gọi Cypher rule là OWL reasoning.
- Nêu rõ số lượng case và snapshot khi trình bày metric.
- Không gọi item-to-item similarity là personalization hoặc xác suất yêu thích.
- Không nói Qwen trả lời; Qwen chỉ tạo `QueryPlan`.
- Không gọi hệ thống là open-domain QA.
- Không suy rộng benchmark 2.000 phim thành kết quả về khả năng mở rộng.

## Ma trận truy vết tiêu chí

| STT | Tiêu chí | Vị trí nội dung | Minh chứng chính |
|---|---|---|---|
| 1 | Bài toán, phạm vi, mục tiêu và lý do chọn KG | Chương 1; Mục 2.5 | Lập luận và câu hỏi nghiên cứu |
| 2 | Công trình liên quan | Chương 3 | Tổng hợp và bảng so sánh |
| 3 | So sánh mô hình thay thế | Mục 2.5; Chương 9 | Bảng so sánh và SQLite baseline |
| 4 | Biểu diễn tri thức và ngữ nghĩa | Chương 2; Chương 5 | Ontology, RDF/RDFS/OWL |
| 5 | Entailment và luật suy diễn | Chương 7 | Semantic entailment và Cypher materialization |
| 6 | Chất lượng dữ liệu và entity resolution | Chương 6; Chương 9 | Manifest và validation |
| 7 | Công cụ, phiên bản và triển khai | Chương 6; Chương 8; Phụ lục A | Cấu hình và lệnh chạy |
| 8 | Dataset, nguồn và tiền xử lý | Mục 6.2–6.10 | Sampling, provenance và checksum |
| 9 | Ontology, graph schema và mapping | Chương 5 | Data dictionary và sơ đồ |
| 10 | Graph loading và reasoner | Mục 6.7; Chương 7 | Import, materialization và validation |
| 11 | Cypher và SPARQL | Chương 7; Phụ lục C | Query catalog |
| 12 | CRUD và nghiệp vụ | Chương 4; Mục 7.1 | Competency question và CRUD tham số hóa |
| 13 | Truy vấn sử dụng fact suy diễn | Chương 7 | `CO_STARRED_WITH` và evidence path |
| 14 | Tiêu chí đánh giá | Mục 2.8; Chương 9 | Metric và protocol |
| 15 | Benchmark và baseline | Mục 9.2–9.7 | Bảng, biểu đồ và artifact |
| 16 | Hạn chế và hướng cải tiến | Mục 9.8–9.12; Chương 10 | Phân tích lỗi và roadmap |
| 17 | Ứng dụng nghiệp vụ | Chương 4; Chương 8 | QA, recommendation, API và UI |
| 18 | Chất lượng trình bày | Toàn bộ report | Bố cục, hình, bảng và tài liệu tham khảo |

## Câu hỏi phản biện và gợi ý trả lời

### Vì sao không dùng CSDL quan hệ?

CSDL quan hệ vẫn lưu được dữ liệu và là baseline hợp lệ. Neo4j được chọn vì
workload chính gồm pattern nhiều bước, shortest path và dựng evidence từ quan hệ.
Với giao dịch theo khóa hoặc aggregate cố định, hệ quan hệ có thể đơn giản hơn.

### Vì sao cần đồng thời Neo4j và RDF/OWL?

Neo4j là operational store thuận tiện cho property trên edge và traversal của
ứng dụng. RDF/OWL cung cấp standards view cho IRI, interoperability và entailment.
Hai biểu diễn phục vụ hai mục tiêu khác nhau.

### Cypher rule có phải OWL reasoning không?

Không. `CO_STARRED_WITH` là luật nghiệp vụ closed-world được materialize từ
`ACTED_IN`. Semantic materializer xử lý tập con RDFS/OWL-RL như domain, range,
inverse và symmetric property.

### Tại sao không dùng tên làm khóa thực thể?

Tên có thể trùng, thay đổi hoặc khác cách viết. Stable source ID giữ identity và
cho phép tạo constraint; fuzzy name chỉ dùng cho entity linking có ngưỡng.

### Vì sao rating TMDB và IMDb không gộp lại?

Hai nguồn có cộng đồng bình chọn và thời điểm cập nhật khác nhau. Hệ thống giữ
hai thuộc tính riêng để không làm mất provenance.

### Fact suy ra được kiểm chứng như thế nào?

Mỗi `CO_STARRED_WITH` giữ `movie_count` và `evidence_movie_ids`. Validation yêu
cầu phải tồn tại ít nhất một Movie mà cả hai Person đều có `ACTED_IN`.

### LLM có thể sinh Cypher hoặc tự trả lời không?

Không. LLM chỉ tạo JSON theo `QueryPlan` schema. Entity linker ánh xạ slot,
compiler whitelist sinh Cypher tham số hóa và Neo4j cung cấp fact cùng evidence.

### Recommendation có phải cá nhân hóa không?

Không. Đây là item-to-item similarity vì hệ thống không lưu lịch sử hay hồ sơ
người dùng. Điểm được tính từ các feature chung trong graph.

### Vì sao metric kiểm thử cao chưa chứng minh hệ thống hoàn hảo?

Các bộ case còn nhỏ và do nhóm xây dựng. Chúng cho thấy hệ thống xử lý tốt những
tình huống đã kiểm tra nhưng chưa phủ mọi dữ liệu khó hoặc cách diễn đạt.

### Benchmark hiện tại chứng minh điều gì?

Benchmark mô tả latency của workload, snapshot, máy và protocol đã nêu. Một quy
mô 2.000 phim không đủ để kết luận về khả năng mở rộng ở mọi quy mô.

### Những bias dữ liệu quan trọng nhất là gì?

Popular-page sampling thiên về phim phổ biến, cast limit bỏ vai phụ, IMDb chỉ
match khi TMDB có external ID và rating phản ánh nhóm người đã bình chọn.

### Đóng góp quan trọng nhất của project là gì?

Đó là workflow đầu cuối: tích hợp đa nguồn, hai cách biểu diễn graph, suy diễn có
evidence, QA an toàn và recommendation giải thích được trên cùng Knowledge Graph.

### Nếu có thêm thời gian, nên mở rộng gì trước?

Ưu tiên corpus QA lớn hơn, xử lý tên trùng và benchmark nhiều snapshot; sau đó
mới mở rộng Wikidata, Award, temporal model, vector retrieval hoặc embedding.

## Checklist trước khi xuất PDF

- Điền đủ thông tin hành chính trên trang bìa.
- Chạy lại thực nghiệm trên cùng snapshot và đồng bộ số liệu.
- Kiểm tra caption, độ phân giải và khả năng đọc của toàn bộ hình.
- Biên dịch ít nhất hai lần để cập nhật mục lục, danh sách hình và danh sách bảng.
- Kiểm tra citation và bibliography.
- Kiểm tra bảng dài, code block, hyperlink và lỗi tràn lề.
- Ghi số trang minh chứng vào checklist chấm điểm sau khi khóa PDF.
- Xác nhận phần hạn chế phản ánh đúng phạm vi đã triển khai.
