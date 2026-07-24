# Giải thích kiến trúc theo sơ đồ draw.io

Tài liệu này là phần diễn giải chính thức cho
[`architecture-flow.drawio`](architecture-flow.drawio). Mục
tiêu là giúp người đọc không chỉ nhìn thấy các block mà hiểu vì sao chúng tồn
tại, dữ liệu nào đi qua mỗi đường nối và block nào chịu trách nhiệm cuối cùng.

## 1. Cách đọc sơ đồ

Sơ đồ được đọc từ trái sang phải, gồm sáu vùng:

1. Data Sources & Processing.
2. Knowledge Layer.
3. QA Planning & Safety.
4. Graph Applications.
5. API & User Experience.
6. Verification & Reproducibility.

Mũi tên biểu diễn dependency hoặc dữ liệu truyền giữa hai block. Đầu mũi tên kết
thúc ở biên block đích. Đường nét đứt biểu diễn fallback, kiểm tra hoặc sản phẩm đầu ra
không nằm trên request path chính.

## 2. Data Sources & Processing

### 2.1. TMDB API + IMDb Ratings

TMDB cung cấp cấu trúc graph chính: phim, người, credits, thể loại, keyword và
studio. IMDb chỉ bổ sung rating/vote vì dữ liệu rating của IMDb có giá trị tham
khảo nhưng tải toàn bộ các dataset IMDb không cần thiết cho quy mô đề tài.

Tại sao dùng hai nguồn:

- TMDB có API thuận tiện và source ID ổn định cho entity/relationship.
- IMDb Ratings tạo minh chứng tích hợp đa nguồn bằng exact identifier.
- Hai nguồn có vai trò tách biệt, tránh trộn hai thang rating vào một thuộc tính.

### 2.2. Immutable raw cache

Response TMDB và file IMDb GZIP được giữ nguyên sau khi tải.

Lý do cần cache:

- Có thể chạy lại processing mà không phụ thuộc mạng.
- Không tiêu tốn lại quota TMDB.
- Có sản phẩm đầu ra để truy vết lỗi và kiểm tra provenance.
- Input bất biến giúp kết quả thí nghiệm tái lập được.

### 2.3. Processing quy trình xử lý dữ liệu

quy trình xử lý dữ liệu làm sạch kiểu dữ liệu, chuẩn hóa field, giữ stable ID, exact join IMDb,
phân giải thực thể và tạo node/edge tables.

Quy trình xử lý dữ liệu tách khỏi importer vì hai trách nhiệm khác nhau:

- Processing giải quyết chất lượng và semantics của dữ liệu.
- Importer giải quyết cách ghi dữ liệu đã chuẩn hóa vào Neo4j.

Nếu viết tất cả trực tiếp vào Neo4j, việc kiểm tra đầu ra trung gian, chạy lại và
so sánh dataset sẽ khó hơn.

### 2.4. Idempotent runtime preparation

Runtime preparation so checksum và số Movie giữa manifest với graph hiện tại.
Nếu khớp, graph được tái sử dụng; nếu lệch, importer chạy lại.

Block này ngăn `make demo` xóa/import 4.999 phim mỗi lần khởi động, đồng thời vẫn
phát hiện khi source thực sự thay đổi.

## 3. Knowledge Layer

### 3.1. Neo4j importer

Importer tạo constraint/index trước, import node trước edge, dùng batch
transaction và `MERGE`, sau đó sinh `CO_STARRED_WITH`.

Thứ tự này bảo đảm:

- Edge không tham chiếu node chưa tồn tại.
- Stable ID ngăn duplicate.
- Import lại không nhân bản dữ liệu.
- Constraint phát hiện sai lệch sớm.

### 3.2. Neo4j đồ thị thuộc tính

Neo4j là operational store, không chỉ là nơi lưu dữ liệu. Các traversal hỏi đáp,
shortest path, common neighbor và gợi ý đều chạy trên graph.

Tại sao chọn Neo4j thay vì relational database:

- Domain có nhiều quan hệ many-to-many giữa Movie, Person, Genre, Keyword,
  Studio.
- Multi-hop traversal là nhu cầu trung tâm.
- Relationship có property, ví dụ `character`, `cast_order`, `movie_count`.
- Cypher diễn đạt pattern traversal gần với competency question.
- Kết quả query có thể giữ đường đi bằng chứng rõ ràng.

Neo4j không được chọn vì “graph luôn nhanh hơn SQL”; lựa chọn dựa trên độ phù hợp
mô hình và truy vấn.

### 3.3. RDF / OWL / SPARQL

RDF/OWL là sản phẩm đầu ra standards-oriented để minh họa ontology, interoperability và
SPARQL equivalent. Nó không phục vụ API vì Neo4j đơn giản hơn cho traversal và
property-rich relationships trong phạm vi triển khai.

### 3.4. Graph kiểm tra hợp lệ

kiểm tra hợp lệ kiểm tra duplicate, orphan, invalid edge và constraint. Đây là quality
gate sau import, không phải chức năng người dùng.

## 4. QA Parsing & Safety

### 4.1. Natural-language question

Người dùng đặt câu hỏi tiếng Việt thuộc chín ý định đã công bố. Parser tất định
nhận diện ý định và trích xuất các slot như tên phim, tên người, thể loại hoặc
ngưỡng rating. Câu hỏi ngoài phạm vi trả `unknown` thay vì sinh truy vấn tùy ý.

### 4.2. Entity linker

Tên trong slot chưa chắc đúng canonical spelling. Entity linker tìm candidate
trong Neo4j, exact match trước rồi fuzzy rerank.

Ví dụ `Cristopher Nolan` có thể liên kết về `Christopher Nolan`. Confidence của
quá trình này được trả làm bằng chứng thay vì che giấu việc hệ thống đã chuẩn hóa.

### 4.3. Fixed parameterized query catalog

Mỗi ý định ánh xạ đến một Cypher pattern cố định trong query catalog. Giá trị
trích xuất từ câu hỏi chỉ được truyền qua parameter.

Các lớp bảo vệ:

- Ý định thuộc danh sách cố định.
- Label và relationship nằm trong source code của catalog.
- Giá trị dùng `$parameter`.
- Query chỉ đọc.
- Shortest path bị giới hạn tối đa tám edge.

### 4.4. Safety boundary

Parser chỉ chọn ý định và slot; query catalog quyết định cấu trúc Cypher; Neo4j
cung cấp dữ liệu và bằng chứng. Ranh giới này giữ execution surface nhỏ, xác định
và có thể kiểm thử.

## 5. Graph Applications

### 5.1. Neo4j Repository

Repository là boundary duy nhất giữa application service và driver Neo4j. Nó
quản lý session, parameter execution, health, stats, entity search, QA và
gợi ý.

Boundary này giúp FastAPI không chứa Cypher và giúp test thay repository thật
bằng fixture/fake.

### 5.2. QA service

QA service điều phối ý định parser, entity linking, query catalog, query execution
và answer formatting. Response gồm answer, ý định, bằng chứng và latency.

Giá trị của QA nằm ở việc mở các năng lực Cypher cho người dùng không viết
truy vấn: lookup một bước, shared-neighbor nhiều bước, aggregation với
`count/collect`, traversal trên quan hệ suy ra và `shortestPath` có giới hạn.
Parser chỉ chọn ý định và slot; Neo4j vẫn thực hiện traversal, filter, aggregation
và trả bằng chứng từ đồ thị.

### 5.3. Gợi ý service

gợi ý chạy IDF-weighted graph similarity trực tiếp
trong Neo4j dựa trên director, actor, keyword, genre và studio chung.

Tách gợi ý khỏi QA vì:

- Gợi ý là ranking task, không phải question parsing task.
- Có thuật toán và evaluation metric riêng.
- Lời giải thích được tạo từ feature chung, không cần text generation.

### 5.4. Bằng chứng & lời giải thích

QA bằng chứng là entity links và graph rows/path. Bằng chứng gợi ý là các
feature chung. Human wording chỉ là lớp trình bày trên bằng chứng đó.

## 6. API & User Experience

### 6.1. FastAPI

FastAPI cung cấp kiểm tra hợp lệ, OpenAPI docs, dependency boundary rõ và phù hợp
Python quy trình xử lý dữ liệu. Endpoint chính là `/ask` và `/recommend`; `/entities/search`
phục vụ autocomplete/entity linking; `/health` và `/stats` phục vụ vận hành.

### 6.2. Web UI — hai chức năng

UI chỉ giữ hai chức năng graph-native:

- Hỏi kiến thức/quan hệ từ graph.
- Tìm phim tương tự một phim đã biết.

Semantic vector search bị loại vì overlap với gợi ý và làm mờ đóng góp
của đồ thị tri thức.

### 6.3. User-visible result

Người dùng thấy title/rating/reasons thay vì raw JSON. Bằng chứng có thể mở rộng
để không làm giao diện quá nặng nhưng vẫn bảo toàn explainability.

## 7. Verification & Reproducibility

### 7.1. Automated verification

Unit/API/integration test, Python compile, draw.io kiểm tra hợp lệ và checksum kiểm
tra code, query, tài liệu và sản phẩm đầu ra.

### 7.2. Silver evaluation corpora

Corpus silver giúp evaluation có protocol rõ thay vì chọn vài ví dụ đẹp khi
trình diễn. Metric phải được giới hạn theo case, rubric và ảnh chụp dữ liệu của corpus, không
khái quát thành độ chính xác production.

### 7.3. Metrics

- Phân giải thực thể: precision/recall/F1.
- Reasoning: precision và bằng chứng.
- Gợi ý: P@K, NDCG@K, độ bao phủ lời giải thích.
- Performance: median, p95 và metadata môi trường.

### 7.4. Reproducible artifacts

Manifest, checksum, labels, result JSON/CSV và Make workflows
cho phép người khác truy ngược claim trong báo cáo về sản phẩm đầu ra tương ứng.

## 8. Hai request path hoàn chỉnh

### 8.1. QA request

```text
Browser
→ POST /ask
→ deterministic 9-intent parser
→ extracted slots
→ entity candidate search
→ canonical linking
→ fixed parameterized Cypher catalog
→ Neo4j Repository
→ graph rows/path
→ answer + evidence
→ Browser
```

### 8.2. Gợi ý request

```text
Browser title input
→ GET /entities/search
→ user selects Movie
→ hidden TMDB ID
→ POST /recommend
→ Neo4j IDF candidate traversal/ranking
→ shared feature evidence
→ human explanation
→ ranked cards
```

## 9. Câu kết luận dùng cho báo cáo/trang chiếu

Kiến trúc ưu tiên tính xác định và khả năng kiểm chứng: parser nhận diện ý định,
query catalog quyết định cấu trúc truy vấn, còn Neo4j thực thi và trả bằng chứng.
Gợi ý là graph-native và có thể giải thích bằng các quan hệ chung được
discount theo IDF.
