# XÂY DỰNG đồ thị tri thức phim ĐA NGUỒN

> **Báo cáo chính.** Số liệu trong báo cáo được khóa theo sản phẩm đầu ra
> thực nghiệm đã xác nhận; sau khi `make data` hoàn tất, chạy lại evaluation và
> chỉ cập nhật số liệu thông qua `manifest.json` và `experiments/results/`.

**Học phần:** Cơ sở dữ liệu nâng cao  
**Giảng viên:** TS. Trần Ngọc Thăng
**Nhóm thực hiện:** Cá nhân
**Thành viên:** Hoàng Kim Khánh – 20252307M
**Thời gian:** 2026

## Lời mở đầu

đồ thị tri thức là một hướng tiếp cận phù hợp với dữ liệu có nhiều loại thực thể
và quan hệ liên kết. Trong miền phim, một bộ phim liên hệ với diễn viên, đạo diễn,
thể loại, từ khóa và hãng sản xuất; các quan hệ này tạo ra nhiều câu hỏi mà cách
biểu diễn đồ thị có thể mô tả trực tiếp và dễ theo dõi hơn.

Báo cáo trình bày quá trình xây dựng đồ thị tri thức phim từ dữ liệu TMDB và
IMDb, bao gồm thu thập và chuẩn hóa dữ liệu, thiết kế ontology và graph schema,
nạp dữ liệu vào Neo4j, truy vấn Cypher, biểu diễn RDF/OWL và một số luật suy diễn.
Trên nền tảng đó, project triển khai hai chức năng chính: hỏi–đáp về phim bằng
ngôn ngữ tự nhiên và gợi ý phim kèm lý do dựa trên các quan hệ chung trong graph.

Mục tiêu của project là minh họa một quy trình đồ thị tri thức đầu cuối có thể
chạy, kiểm tra và trình diễn trong phạm vi học phần Cơ sở dữ liệu nâng cao. Báo
cáo được tổ chức thành sáu chương nội dung bám các tiêu chí chuyên môn trong
`ChecklistCSDLNCv2.XLS`, sau đó là một chương kết luận. Ba tiêu chí cuối của nhóm
VI đánh giá chất lượng báo cáo, trang chiếu/thuyết trình và trả lời phản biện nên không
được biến thành các mục tự mô tả trong thân báo cáo:

1. **Chương 1 – Đặt vấn đề và tổng quan:** bài toán, survey và so sánh với mô
   hình quan hệ hoặc giải pháp thay thế.
2. **Chương 2 – Lý thuyết và mô hình dữ liệu:** biểu diễn tri thức, cơ chế suy
   diễn và chất lượng tri thức.
3. **Chương 3 – Thiết kế và cài đặt hệ thống:** công cụ, dữ liệu thực nghiệm,
   ontology/lược đồ đồ thị tri thức và cấu hình engine/reasoner.
4. **Chương 4 – Truy vấn, xử lý và nghiệp vụ:** ngôn ngữ đặc thù, bộ truy vấn từ
   CRUD đến nâng cao và truy vấn có suy luận.
5. **Chương 5 – Thực nghiệm và đánh giá:** tiêu chí, phép đo hiệu năng/mốc so sánh và phân
   tích kết quả, hạn chế, hướng cải tiến.
6. **Chương 6 – Ứng dụng và trình diễn chương trình:** ngữ cảnh sử dụng, hai ứng dụng,
   API, giao diện và tính faithful của lời giải thích.
7. **Chương 7 – Kết luận và hướng phát triển:** tổng kết kết quả đạt được và các
   hướng mở rộng.

Phần phụ lục cung cấp hướng dẫn cài đặt và chạy chương trình, ví dụ sử dụng API,
một số truy vấn minh họa và vị trí các tệp dữ liệu, kết quả thực nghiệm.

---

# Chương 1. I. Đặt vấn đề và tổng quan

## 1.1. Mô tả bài toán, ngữ cảnh, phạm vi, mục tiêu và lý do lựa chọn công nghệ CSDL

### Bối cảnh

Một bộ phim không tồn tại như một bản ghi độc lập. Nó liên hệ nhiều–nhiều với
diễn viên, đạo diễn, thể loại, từ khóa và hãng sản xuất. Một người có thể đồng
thời là diễn viên và đạo diễn; hai diễn viên có thể đóng chung trong nhiều phim;
một nhóm phim có thể liên hệ gián tiếp qua đạo diễn, cast hoặc chủ đề. Dữ liệu
này lại nằm ở nhiều nguồn với định danh, mức đầy đủ và cách chấm điểm khác nhau.
TMDB cung cấp metadata, credits, keywords và external ID, trong khi IMDb cung cấp
rating và vote count độc lập.

Các câu hỏi như “đường liên hệ giữa hai diễn viên là gì?”, “đạo diễn nào thường
làm phim thuộc một thể loại?” hoặc “phim nào tương tự và vì sao?” không chỉ là
lookup một bản ghi. Chúng yêu cầu duyệt nhiều quan hệ và giữ lại bằng chứng của
đường duyệt. Đồ thị tri thức phù hợp với bài toán này vì thực thể và quan hệ được
biểu diễn tường minh, còn câu hỏi nghiệp vụ có thể ánh xạ thành graph pattern.

### Phát biểu bài toán

Đề tài xây dựng một biểu diễn thống nhất cho năm loại thực thể `Movie`, `Person`,
`Genre`, `Keyword` và `Studio`; tích hợp chính xác dữ liệu TMDB–IMDb; cung cấp
truy vấn nhiều bước và suy diễn có thể kiểm chứng; đồng thời minh họa giá trị của
graph thông qua hỏi–đáp và gợi ý phim có giải thích.

Bài toán không chỉ là “đưa dữ liệu vào Neo4j”. Một hệ thống đạt yêu cầu phải giải
quyết đồng thời:

1. Định danh: không dùng tên làm khóa vì tên có thể trùng hoặc thay đổi.
2. Provenance: phân biệt rating TMDB và IMDb, truy vết fact gốc hoặc fact suy ra.
3. Chất lượng: phát hiện bản ghi lỗi, duplicate, orphan và quan hệ sai kiểu/hướng.
4. An toàn truy vấn: không ghép chuỗi người dùng vào Cypher.
5. Tái lập: cache, checksum, manifest, cấu hình và kết quả đo phải kiểm chứng được.
6. Đánh giá: lưu cấu hình, dữ liệu đầu vào và kết quả để có thể chạy lại.

### Câu hỏi nghiên cứu

**RQ chính:** đồ thị tri thức có thể tích hợp dữ liệu phim đa nguồn, hỗ trợ truy
vấn multi-hop và suy diễn, đồng thời tạo câu trả lời và gợi ý có bằng chứng như
thế nào?

Các câu hỏi phụ gồm:

- **RQ1:** Exact-ID enrichment và stable source ID bảo đảm identity/provenance đến
  mức nào?
- **RQ2:** đồ thị thuộc tính hỗ trợ các competency question đa bước ra sao?
- **RQ3:** Rule materialization và semantic entailment sinh tri thức mới như thế
  nào, và làm sao kiểm tra tri thức đó?
- **RQ4:** IDF-weighted graph similarity cung cấp gợi ý và lời giải thích
  như thế nào so với các phương pháp overlap khác?
- **RQ5:** Hệ thống có giới hạn gì về độ bao phủ, accuracy, validity và scalability?

### Mục tiêu

Mục tiêu tổng quát là xây dựng một đồ thị tri thức phim chạy được từ dữ liệu
nguồn đến ứng dụng. Các mục tiêu kiểm chứng được là:

- Thu thập và chuẩn hóa 2.000–5.000 phim cùng thực thể liên quan.
- Bảo toàn source ID, provenance và metadata quan trọng trên node/edge.
- Nạp graph idempotent vào Neo4j, có constraint/index và kiểm tra hợp lệ.
- Xây ontology RDF/OWL, RDF export và ít nhất 10 SPARQL query.
- Xây ít nhất 10 Cypher query, gồm multi-hop, aggregation và shortest path.
- Materialize `CO_STARRED_WITH` với bằng chứng và chạy semantic entailment.
- Cung cấp API/UI cho QA và explainable gợi ý.
- Đánh giá data quality, phân giải thực thể, reasoning, QA, gợi ý và latency.

### Phạm vi

TMDB là nguồn graph chính; IMDb chỉ enrichment cho Movie bằng exact `imdb_id`.
Mỗi phim giữ tối đa 20 cast member nhằm giới hạn kích thước và thời gian thu thập.
MVP không bao gồm Award/Wikidata, NLP trên overview, user-history personalization,
vector search, embedding, GraphRAG hoặc LLM-to-Cypher tự do. Các thành phần này là
hướng mở rộng, không được dùng để mô tả chức năng hiện có.

### Đóng góp

Đóng góp của đề tài gồm:

- Quy trình xử lý dữ liệu đa nguồn storage-bounded và tái lập được.
- Chiến lược identity dựa trên stable source ID thay vì tên.
- Mô hình kết hợp Neo4j operational graph và RDF/OWL standards view.
- Rule suy diễn lưu bằng chứng, cùng semantic materializer/validator chạy được.
- QA tất định với entity linking và catalog Cypher có tham số.
- Gợi ý graph-native với lời giải thích từ chính feature đóng góp.
- Bộ test/evaluation phân loại rõ bằng chứng và giới hạn validity.

## 1.2. Khảo sát tổng quan công nghệ và mô hình liên quan

### Phương pháp khảo sát

Khảo sát tập trung vào ba cụm: Đồ thị tri thức construction/phân giải thực thể,
KG hỏi--đáp và explainable KG gợi ý. Từ khóa gồm “knowledge
graph hỏi--đáp”, “đồ thị tri thức recommender systems”, “explainable
graph gợi ý”, “đồ thị tri thức phim gợi ý” và “temporal
đồ thị tri thức QA”. Nguồn ưu tiên là W3C, tài liệu chính thức của nền tảng,
proceedings hội nghị, tạp chí đã qua bình duyệt và bản paper của tác giả. Khoảng thời
gian ưu tiên là 2023–2026; nguồn nền tảng cũ hơn chỉ dùng cho định nghĩa chuẩn.

Tiêu chí đưa vào gồm: liên quan trực tiếp tới KGQA/gợi ý/construction;
có mô tả phương pháp hoặc evaluation; có metadata xuất bản xác minh được. Bài
blog, trang tổng hợp và nội dung không có phương pháp rõ ràng bị loại khỏi survey
cốt lõi.

### Tổng hợp nghiên cứu

Guo và cộng sự khảo sát các hệ gợi ý dựa trên đồ thị tri thức, phân loại cách
khai thác graph và nhấn mạnh hai mục tiêu accuracy và explainability [8]. Kết quả
này hỗ trợ quyết định đánh giá đồng thời ranking metric và độ bao phủ lời giải thích.
Các nghiên cứu về explainable graph gợi ý cho thấy đường/feature graph
có thể cung cấp lý do dễ kiểm tra hơn latent factor [9], [10]. Tuy nhiên, nhiều
phương pháp tối ưu personalization từ user–item interaction hoặc dùng embedding;
đề tài này không có lịch sử người dùng nên chỉ tuyên bố item-to-item gợi ý.

Các công trình conversational gợi ý dùng explicit reasoning chain để
tạo gợi ý rationale [11]. Đề tài chia QA và gợi ý thành hai
endpoint, nhưng chia sẻ nguyên tắc: mọi kết quả phải có bằng chứng từ đồ thị. Với miền
phim, các nghiên cứu kết hợp KG với time series hoặc topic model nhằm tăng độ
chính xác [12], [13]. Đây là mốc so sánh khái niệm quan trọng, đồng thời chỉ ra giới
hạn của đề tài: chưa mô hình hóa thời gian tương tác hoặc nội dung overview bằng
topic model.

Khảo sát Temporal KGQA năm 2024 phân biệt câu hỏi trên fact thay đổi theo thời
gian với graph tĩnh [14]. Movie KG hiện chỉ lưu `release_date` như datatype
property để filter/sort; nó chưa phải Temporal KG và không hỗ trợ valid time hay
transaction time. BYOKG dùng LLM-backed symbolic agent để khám phá KG chưa thấy,
sinh query-program exemplar và tổng hợp chương trình truy vấn zero-shot [15].
Khác với hướng đó, đề tài cố định schema/operation whitelist để ưu tiên safety và
reproducibility trong phạm vi Movie KG. Vì vậy smoke test 10 câu của đề tài chỉ
được dùng để kiểm tra hệ thống, không gọi là phép đo hiệu năng cho môi trường thực tế.

### Khoảng trống và vị trí đề tài

Đề tài không cố cạnh tranh với KGQA/recommender quy mô nghiên cứu. Khoảng trống
được chọn là một quy trình học phần nhưng đầu cuối và kiểm chứng được: thu thập
đa nguồn, identity/provenance, hai biểu diễn graph, suy diễn có bằng chứng, API/UI,
test và sản phẩm đầu ra thực nghiệm. Điểm khác biệt quan trọng là QA chỉ thực thi các
ý định và Cypher pattern đã xác định, gợi ý score được giải thích bằng các quan
hệ trong graph, và các kết quả đo đều gắn với ảnh chụp dữ liệu cùng cấu hình cụ thể.

### So sánh có cấu trúc các công trình liên quan

| Công trình | Dữ liệu/tín hiệu | Phương pháp | Lời giải thích | Khác biệt với đề tài |
|---|---|---|---|---|
| Guo et al. [8] | nhiều phép đo hiệu năng | survey taxonomy | phân tích nhiều họ | dùng để định vị, không phải mốc so sánh chạy |
| Caro-Martínez et al. [9] | interaction graph | link prediction/common neighbors | graph-interpretable | đề tài dùng metadata graph, không user interaction |
| Colas et al. [10] | user–item + item KG | gợi ý/NLG | natural-language grounding | đề tài trả bằng chứng xác định, không NLG |
| Ren et al. [11] | conversational gợi ý | KG reasoning chain | explicit chain | QA stateless, gợi ý tách endpoint |
| Zhang et al. [12] | rating + KG + time series | collaborative filtering | quan hệ KG | không có temporal user signal |
| Saat et al. [13] | MovieLens + topic/metadata | content-based KG | feature/profile | dùng TMDB, không topic model |
| Su et al. [14] | temporal KGQA studies | survey taxonomy | temporal reasoning | release date mới là property |
| Agarwal et al. [15] | unseen/domain KG | LLM program synthesis | query program/path | fixed schema/whitelist compiler |

“Dùng đồ thị tri thức” không phải một phương pháp duy nhất. KG có thể là nguồn
side information cho model, không gian reasoning, cấu trúc lời giải thích hoặc
operational database. Trong đề tài, graph đồng thời là operational store và
bằng chứng substrate; model học sâu không trực tiếp quyết định ranking hoặc fact.

### Liên hệ survey với quyết định thiết kế

Survey dẫn đến bốn quyết định. Thứ nhất, explainability phải được định nghĩa bằng
bằng chứng có thể kiểm tra, không chỉ text nghe hợp lý. Thứ hai, metric gợi ý
phải đi cùng corpus/rubric và K. Thứ ba, QA sinh query tự do có flexibility nhưng
execution risk cao; constrained plan phù hợp phạm vi học phần hơn. Thứ tư, các
phương pháp personalized không được dùng để quảng bá hệ thống không có hồ sơ người dùng.

## 1.3. So sánh với mô hình quan hệ truyền thống và giải pháp thay thế

### Đồ thị thuộc tính và Neo4j

đồ thị thuộc tính gồm node có label, relationship có type/hướng và property trên cả
node lẫn relationship. Neo4j dùng Cypher để match graph pattern. Unique constraint
bảo vệ stable key; index/full-text index tăng tốc lookup; transaction bảo đảm một
batch import không ở trạng thái dở dang. Property trên `ACTED_IN` như `character`
và `cast_order` là lý do thực dụng để chọn đồ thị thuộc tính làm operational store [5].

### So sánh mô hình

| Khía cạnh | Quan hệ | Document | RDF/OWL | Đồ thị thuộc tính |
|---|---|---|---|---|
| Đơn vị | bảng/hàng/khóa | document/collection | triple/quad/IRI | node/edge/property |
| Quan hệ nhiều–nhiều | bảng nối | nhúng hoặc tham chiếu | predicate | edge trực tiếp |
| Chuẩn liên thông | SQL nhưng schema riêng | JSON/BSON, schema ứng dụng | W3C, cao | phụ thuộc engine |
| Edge property | đặt ở bảng nối | lồng trong document | reification/RDF-star | trực tiếp |
| Reasoning | logic ứng dụng | logic ứng dụng | RDFS/OWL reasoner | rule/procedure |
| Traversal | JOIN/CTE đệ quy | lookup nhiều collection | graph pattern | graph-native pattern |
| Phù hợp | OLTP, aggregate ổn định | aggregate tự chứa, schema linh hoạt | semantic integration | operational traversal |

Không có mô hình luôn tốt hơn. CSDL quan hệ phù hợp giao dịch và báo cáo có
schema ổn định; document store phù hợp khi một aggregate thường được đọc/ghi
nguyên khối và ít quan hệ chéo; RDF phù hợp liên thông và semantics; Neo4j phù
hợp traversal và ứng dụng graph. Đề tài không chọn document store vì cast,
director, genre và keyword được dùng lại qua nhiều phim: nhúng gây lặp, còn tham
chiếu lại đưa bài toán về nhiều phép lookup. Đề tài đo một SQLite mốc so sánh trên cùng ảnh chụp dữ liệu thay vì dùng
lập luận lý thuyết để tuyên bố Neo4j luôn nhanh hơn.

Đồ thị tri thức cũng không nên được dùng chỉ vì dữ liệu “có quan hệ”. Nếu workload
chủ yếu là transaction theo khóa, báo cáo tổng hợp cố định hoặc dữ liệu nhỏ với
schema ổn định, CSDL quan hệ đơn giản hơn và có thể hiệu quả hơn. RDF/OWL chỉ đáng
đổi chi phí khi interoperability, định danh toàn cục hoặc entailment là yêu cầu
thật. Đồ thị thuộc tính phù hợp đề tài vì competency question tập trung vào đường
đi, neighborhood và bằng chứng trên quan hệ; lựa chọn này là workload-driven,
không phải tuyên bố ưu thế phổ quát.

# Chương 2. II. Lý thuyết và mô hình dữ liệu

## 2.1. Biểu diễn tri thức và ngữ nghĩa

### Tri thức và đồ thị tri thức

Dữ liệu là các giá trị thô; thông tin xuất hiện khi dữ liệu được đặt trong ngữ
cảnh; tri thức thể hiện các thực thể, quan hệ và quy tắc cho phép giải thích hoặc
suy ra điều mới. Trong đồ thị tri thức, một fact được biểu diễn bằng quan hệ giữa
các thực thể có định danh. Fact có thể là **asserted fact**, lấy trực tiếp từ nguồn,
hoặc **derived fact**, sinh bởi luật và phải truy ngược được về tiền đề [16].

### Ontology

Ontology là đặc tả hình thức cho một miền tri thức, gồm class, individual,
object property, datatype property và axiom. Taxonomy chủ yếu biểu diễn phân cấp
“is-a”, trong khi ontology còn mô tả domain/range, inverse, disjointness,
cardinality và các ràng buộc ngữ nghĩa khác. Đề tài thiết kế ontology từ
competency question: chỉ đưa class/property cần thiết để trả lời câu hỏi, tránh
mở rộng schema không có dữ liệu hoặc trường hợp sử dụng.

### RDF, RDFS, OWL và SPARQL

RDF biểu diễn phát biểu bằng triple `(subject, predicate, object)` [1]. Subject và
predicate là IRI; object có thể là IRI hoặc literal. Một quad bổ sung graph name,
cho phép tổ chức nhiều named graph trong một RDF dataset, hữu ích khi tách nguồn
hoặc provenance. Namespace rút gọn IRI và giúp tránh xung đột định danh. Linked
Data nhấn mạnh IRI ổn định, có thể tham chiếu và liên kết giữa các nguồn.

RDFS cung cấp class, subclass, domain và range [2]. OWL bổ sung inverse property,
symmetric property, disjoint class, functional property và nhiều axiom mạnh hơn [3].
Ontology vận hành theo Open World Assumption: thiếu một fact không có nghĩa fact
đó sai. Vì vậy OWL reasoning và data kiểm tra hợp lệ là hai nhiệm vụ khác nhau. Đề tài
materialize tập con RDFS/OWL-RL đã khai báo, đồng thời dùng kiểm tra hợp lệ đóng để
kiểm tra functional conflict, disjoint type và required title.

SPARQL truy vấn đồ thị bằng mẫu đồ thị cơ bản (basic graph pattern) [4].
`OPTIONAL` xử lý thuộc tính có thể
thiếu; `GROUP BY/COUNT` hỗ trợ aggregation; `ASK` kiểm tra sự tồn tại; `CONSTRUCT`
tạo một graph kết quả. Catalog của đề tài bao phủ cả bốn dạng này và có query dùng
inverse fact sau materialization.

## 2.2. Cơ chế suy diễn và lập luận

Phần này phân biệt suy diễn cấu trúc trong đồ thị thuộc tính với entailment ngữ nghĩa trên RDF/OWL; phần cài đặt và bằng chứng được trình bày theo đúng thứ tự ở tiêu chí 13.

### Hai loại suy diễn

| Thuộc tính | Semantic entailment | Business rule |
|---|---|---|
| Engine | RDFLib materializer + Apache Jena/Fuseki | Neo4j/Cypher |
| Ví dụ | `actedIn` → inverse `hasActor` | shared Movie → co-star |
| Cơ sở | ontology axiom | domain-specific rule |
| Output | inferred RDF triple | materialized relationship |
| Kiểm tra hợp lệ | functional/disjoint/required | supporting movie audit |

Có ontology file không đồng nghĩa hệ thống tự động chạy OWL reasoning; ngược lại,
Cypher materialization sinh tri thức mới nhưng không phải OWL entailment.

## 2.3. Chất lượng tri thức: liên kết thực thể, tính nhất quán và tính đầy đủ

### Phân giải thực thể

phân giải thực thể xác định hai record có mô tả cùng thực thể hay không. Exact
source ID có precision cao và được ưu tiên. Fuzzy matching chỉ là fallback, trả
confidence và từ chối trường hợp hai candidate có top score bằng nhau. Precision,
Recall và F1 được tính từ TP, FP, FN; accuracy riêng lẻ không phù hợp khi class
phân bố lệch.

### Tính đúng, tính đầy đủ và tính nhất quán

Ba khái niệm này cần được phân biệt. **Tính đúng cấu trúc** trả lời liệu node/edge
có tuân theo schema và constraint hay không. **Tính nhất quán ngữ nghĩa** trả lời
liệu một individual có đồng thời thuộc hai class disjoint, hoặc một functional
property có nhiều value xung đột hay không. **Tính đầy đủ** đo mức phủ của dữ liệu
so với yêu cầu, chẳng hạn tỷ lệ phim có cast, director, genre hoặc IMDb rating.

Zero structural violation không chứng minh graph phản ánh hoàn hảo thế giới thật.
Một phim có thể thiếu cast do giới hạn nguồn nhưng vẫn hợp lệ về schema. Ngược
lại, graph có độ bao phủ cao vẫn có thể merge sai hai người trùng tên. Vì vậy đề tài
báo cáo đồng thời constraint/kiểm tra hợp lệ, độ bao phủ và sample review thay vì gộp
tất cả thành một “quality score”.

Audit trên toàn bộ ảnh chụp dữ liệu đã xử lý kiểm tra stable-ID trùng, required field,
foreign key của edge, endpoint pair trùng, conflicting value và provenance. Hai
credit TMDB lặp cùng Person–Movie nhưng khác tên vai được gộp thành một
`ACTED_IN`: nối các character khác nhau và giữ `cast_order` nhỏ nhất. Sản phẩm đầu ra
sau chuẩn hóa có zero violation; 54 tên Person trùng được ghi nhận nhưng không
merge vì tên không phải khóa. Corpus ER silver 100 case gồm 50 exact-ID, 25 fuzzy
positive và 25 hard negative; metric chỉ được diễn giải trong phạm vi protocol
tất định này, không khái quát thành độ chính xác production.

### Provenance

Provenance có ba mức. Mức source: node/edge gốc có `source=tmdb`, Movie giữ IMDb
ID và ratings riêng. Mức ảnh chụp dữ liệu: manifest giữ path/checksum/count và match
method. Mức derivation: `CO_STARRED_WITH` giữ `derived`, count và supporting
movie IDs. RDF export chưa dùng named graph đầy đủ cho từng nguồn; đây là giới
hạn thay vì một claim provenance chuẩn hóa toàn diện.

# Chương 3. III. Thiết kế và cài đặt hệ thống

## 3.1. Lựa chọn, cấu hình và triển khai DBMS/công cụ

### Kiến trúc tổng thể

```text
TMDB API/cache --+
                 +-> clean/normalize/exact-ID enrich -> CSV + manifest
IMDb ratings.gz -+                          +-> Neo4j -> QA/recommend -> FastAPI/UI
                                            +-> RDF -> entailment -> SPARQL
```

QA dùng parser chín ý định, entity linker và query catalog có tham số. Neo4j là
nguồn dữ liệu và bằng chứng của runtime.

### Yêu cầu phi chức năng

Hệ thống phải idempotent, query-safe, có provenance, chạy trình diễn không phụ thuộc
Internet sau import, không commit API key/raw dataset, và có quy trình tái lập.
Public API là read-only; CRUD chỉ phục vụ maintenance có kiểm soát. Câu hỏi ngoài
chín ý định phải được từ chối rõ ràng và không ảnh hưởng gợi ý.

## 3.2. Chuẩn bị bộ dữ liệu thực nghiệm

### Thu thập TMDB

Collector duyệt popular pages đến khi đủ số movie ID duy nhất, sau đó tải detail,
credits, keywords và external IDs theo TMDB API [6]. Response được cache nguyên dạng; request có
timeout, retry và interval. Cache giúp chạy lại không tiêu tốn API quota và giữ
ảnh chụp dữ liệu nguồn cho reproducibility.

### Tích hợp IMDb

quy trình xử lý dữ liệu chỉ tải `title.ratings.tsv.gz` từ bộ dữ liệu phi thương mại IMDb [7], kiểm tra gzip/checksum và ghi metadata.
File được stream từng dòng, chỉ giữ record có `tconst` thuộc tập IMDb ID của 5.000
phim TMDB. Cách này không giải nén toàn bộ và không nạp IMDb đầy đủ vào RAM/Neo4j.
`Movie.rating` và `Movie.imdb_rating` không ghi đè nhau.

### Quản trị nguồn, điều khoản sử dụng và đạo đức dữ liệu

TMDB API được sử dụng theo tài liệu và điều khoản dành cho nhà phát triển; khóa
API là secret cục bộ, không đưa vào repository. Dữ liệu hiển thị phải ghi nhận
TMDB theo yêu cầu của nền tảng và không được mô tả như dữ liệu do nhóm sở hữu [6].
IMDb cung cấp các dataset này cho mục đích sử dụng phi thương mại; đề tài chỉ tải
file ratings công khai cần thiết, không phân phối lại toàn bộ dataset và không
mở rộng phạm vi sang mục đích thương mại [7]. Người tái lập phải tự kiểm tra điều
khoản hiện hành tại thời điểm chạy vì điều khoản dịch vụ có thể thay đổi.

Corpus chỉ chứa metadata nghề nghiệp công khai về phim và người tham gia, không
thu thập lịch sử xem, hồ sơ người dùng hoặc dữ liệu nhạy cảm. Rating của nguồn là
tín hiệu tổng hợp, không được diễn giải như sự thật khách quan về chất lượng phim.
Sampling theo popular pages có popularity bias; giới hạn cast tạo độ bao phủ bias.
Hai bias này được công bố để tránh suy rộng kết quả sang toàn bộ điện ảnh hoặc
mọi nhóm người dùng.

### Cleaning và phân giải thực thể

Cleaning chuẩn hóa Unicode/whitespace, kiểu số/ngày và trường bắt buộc. Duplicate
TMDB ID bị loại và log. Exact TMDB/IMDb ID được ưu tiên; fuzzy name fallback dùng
threshold và từ chối tied top score. Ambiguous case không được tự động merge.

### Normalized artifacts và manifest

quy trình xử lý dữ liệu tạo `movies.csv`, `people.csv`, `genres.csv`, `keywords.csv`,
`studios.csv` và năm edge CSV. Manifest ghi source checksum, thời điểm tạo, counts,
IMDb độ bao phủ/match, invalid record, duplicate/missing rate và độ bao phủ cast,
director, genre. Raw, interim và processed data được tách để tránh nhầm nguồn với
sản phẩm đầu ra dẫn xuất.

### Thuật toán quy trình xử lý dữ liệu

```text
INPUT: raw TMDB records, optional compressed IMDb ratings
1. Validate required movie ID/title; reject and log invalid records.
2. Deduplicate Movie by tmdb_id.
3. Normalize scalar fields and names.
4. Build stable IDs from TMDB source IDs.
5. Emit node maps and relationship rows with source metadata.
6. Stream IMDb ratings; retain only wanted tconst values.
7. Enrich Movie without overwriting TMDB rating.
8. Write deterministic CSV tables.
9. Compute checksum, counts, error rates and coverage into manifest.
OUTPUT: normalized CSVs + manifest + invalid-record log
```

Độ phức tạp bộ nhớ của IMDb join phụ thuộc số IMDb ID thuộc tập phim mục tiêu,
không phụ thuộc toàn bộ file ratings. Entity maps phụ thuộc số entity trong
2.000–5.000 phim. Cast limit kiểm soát kích thước nhưng đồng thời tạo độ bao phủ bias.

### Xử lý lỗi

Downloader dùng file `.part`, chỉ rename sau khi gzip hợp lệ để tránh coi partial
download là hoàn chỉnh. Collector retry lỗi tạm thời và cache response. Quy trình xử lý dữ liệu
fail rõ nếu IMDb path được chỉ định nhưng không tồn tại. Runtime không tự dùng seed
khi thiếu data thật; nó dừng và yêu cầu chuẩn bị dataset. Cách fail closed tránh
trình diễn vô tình chạy fixture rồi báo như corpus thật.

### Tái lập và thay đổi nguồn

TMDB/IMDb là nguồn động, nên chạy lại ngày khác có thể tạo ảnh chụp dữ liệu khác.
Reproducibility ở đây là tái lập quy trình và truy vết ảnh chụp dữ liệu, không cam kết API
luôn trả byte giống nhau. Raw cache/checksum cho phép chạy transform trên ảnh chụp dữ liệu
cũ. Nếu data thay đổi, evaluation/phép đo hiệu năng phải chạy lại cùng ảnh chụp dữ liệu.

### Idempotency và reproducibility

Idempotency nghĩa là thực hiện cùng một import nhiều lần tạo cùng trạng thái logic,
không nhân đôi node/edge. Reproducibility rộng hơn: người khác phải biết input,
version, configuration, code path và protocol để tái tạo sản phẩm đầu ra/kết quả. `MERGE`
giải quyết một phần idempotency; checksum, manifest, metadata máy và command
quy trình giải quyết reproducibility. Import có thể idempotent nhưng không tái lập
nếu nguồn thay đổi mà không có ảnh chụp dữ liệu/checksum.

## 3.3. Thiết kế và tinh chỉnh ontology hoặc lược đồ đồ thị tri thức

### Các lớp và định danh

| Class/label | Khóa | Thuộc tính chính |
|---|---|---|
| Movie | `tmdb_id` | imdb_id, title, release_date, runtime, rating, imdb_rating, imdb_votes, popularity, overview |
| Person | `person_id` | tmdb_id, imdb_id, name, source |
| Genre | `genre_id` | name, source |
| Keyword | `keyword_id` | name, source |
| Studio | `company_id` | name, country, source |

Person dùng một label duy nhất vì một người có thể vừa đóng phim vừa đạo diễn.
Vai trò được biểu diễn bởi relationship. Với dữ liệu mới, `person_id=tmdb:<id>`;
hash tên chỉ là legacy fallback khi fixture/cache cũ không có source ID.

### Relationship

| Relationship | Hướng | Property |
|---|---|---|
| ACTED_IN | Person → Movie | character, cast_order, source |
| DIRECTED | Person → Movie | source |
| HAS_GENRE | Movie → Genre | source |
| HAS_KEYWORD | Movie → Keyword | source |
| PRODUCED_BY | Movie → Studio | source |
| CO_STARRED_WITH | Person → Person | movie_count, evidence_movie_ids, derived |

### Ontology RDF/OWL

Ontology khai báo năm class disjoint, object property với domain/range, inverse
`actedIn/hasActor`, inverse `directed/directedBy`, symmetric `coStarredWith`, và
functional `tmdbId/imdbId`. Datatype property mô tả title, ratings, votes và name.
Functional property không đồng nghĩa global inverse-functional identity; stable
URI vẫn được tạo từ source ID.

### Ánh xạ RDF–Neo4j

| Neo4j | RDF/OWL |
|---|---|
| `(:Movie {tmdb_id})` | `:movie/<id> a :Movie; :tmdbId ...` |
| `(:Person)-[:ACTED_IN]->(:Movie)` | `:person/... :actedIn :movie/...` |
| `[:DIRECTED]` | `:directed` / inverse `:directedBy` |
| edge property | cần reification/RDF-star nếu xuất đầy đủ |
| constraint | ontology axiom + kiểm tra hợp lệ đóng |

### Các quyết định mô hình hóa

#### Một Person label thay vì Actor/Director

Nếu dùng hai label loại trừ nhau, người vừa diễn vừa đạo diễn phải duplicate node
hoặc mang hai label không phản ánh role theo từng phim. Một `Person` và role trên
relationship tránh hai vấn đề này. Query “phim của một người” có thể match
`ACTED_IN|DIRECTED`, còn query chuyên biệt vẫn chọn đúng type.

#### Source ID thay cho name

Tên không ổn định và không duy nhất. Source ID được dùng làm constraint key; name
là thuộc tính hiển thị/tìm kiếm. Fuzzy matching chỉ liên kết input người dùng tới
entity đã có, không thay stable identity trong storage.

#### Tách TMDB và IMDb rating

Hai rating có population và thời điểm cập nhật khác nhau. Gộp vào một property sẽ
mất provenance. Vì vậy `rating`, `imdb_rating`, `imdb_votes` được giữ riêng. Khi
QA cần một rating ưu tiên, compiler dùng `coalesce(imdb_rating,rating)` theo quyết
định công khai.

#### Materialize co-star

Co-star có thể tính tại query time nhưng được dùng thường xuyên và cần audit.
Materialization lưu aggregate/bằng chứng và minh họa derived fact. Chi phí là phải
recompute sau authoritative import; runtime preparation xử lý phụ thuộc này.

### Từ điển dữ liệu và quy tắc miền

| Trường | Kiểu/miền | Bắt buộc | Nguồn | Quy tắc và<br>ý nghĩa |
|---|---|---|---|---|
| Movie.tmdb_id | integer dương | có | TMDB | khóa ổn định, duy nhất trong Movie |
| Movie.imdb_id | chuỗi `tt...` | không | TMDB external ID | khóa nối chính xác sang IMDb |
| Movie.title | Unicode string | có | TMDB | trim whitespace, không được rỗng |
| `Movie.`<br>`release_date` | ISO date | không | TMDB | ngày phát hành, không phải valid-time của temporal KG |
| Movie.rating | số 0–10 | không | TMDB | giữ riêng với IMDb rating |
| `Movie.`<br>`imdb_rating` | số 0–10 | không | IMDb | chỉ ghi khi exact `imdb_id` match |
| `Movie.`<br>`imdb_votes` | integer không âm | không | IMDb | số phiếu tại ảnh chụp dữ liệu thu thập |
| `Person.`<br>`person_id` | source-qualified ID | có | TMDB/<br>quy trình xử lý dữ liệu | identity key, không dùng tên làm khóa |
| `ACTED_IN.`<br>`character` | string | không | TMDB credits | vai diễn được công bố ở nguồn |
| `ACTED_IN.`<br>`cast_order` | integer không âm | không | TMDB credits | thứ tự cast, không phải độ quan trọng tuyệt đối |
| `CO_STARRED_WITH.`<br>`movie_count` | integer dương | có | luật | số phim chung hỗ trợ fact suy ra |
| `CO_STARRED_WITH.`<br>`evidence_`<br>`movie_ids` | danh sách ID | có | luật | đường truy vết về các Movie tiền đề |

Các miền giá trị được kiểm tra ở quy trình xử lý dữ liệu/kiểm tra hợp lệ thay vì xem OWL là cơ chế
kiểm tra dữ liệu đóng. Required field là yêu cầu của ứng dụng; functional và
disjoint axiom là yêu cầu ngữ nghĩa; constraint Neo4j bảo vệ identity/storage.
Ba lớp ràng buộc bổ sung cho nhau nhưng không được đánh đồng.

## 3.4. Cài đặt trên đồ thị tri thức engine và cấu hình reasoner

Neo4j là operational đồ thị tri thức engine. RDFLib cung cấp nhánh kiểm thử semantic
nhẹ; Apache Jena Fuseki 6.1.0 là triple-store/SPARQL endpoint độc lập dùng để chạy
cùng tập luật suy diễn trên ảnh chụp dữ liệu RDF đầy đủ.

### Import và kiểm tra hợp lệ Neo4j

Thứ tự import là constraint/index → node → edge → reasoning → kiểm tra hợp lệ. Mỗi
batch dùng parameterized `UNWIND`; `MERGE` trên stable key giúp import lặp không
tạo duplicate. `--replace` dành cho authoritative rebuild. Kiểm tra hợp lệ kiểm tra:

- orphan Movie;
- duplicate stable IDs;
- missing required property;
- invalid relationship type;
- endpoint/hướng sai schema;
- `CO_STARRED_WITH` không còn supporting movie.

Integration test dùng Neo4j test riêng ở cổng 7688 với storage tạm, import hai lần
và kiểm tra QA, gợi ý, CRUD; graph trình diễn không bị reset.

Jena chạy trong Docker profile `semantic`, đọc ontology và `movies.ttl` qua
assembler. `GenericRuleReasoner` ở chế độ forward nạp năm luật khai báo tường minh:
domain, range, hai chiều của `owl:inverseOf` và `owl:SymmetricProperty`. Profile
này cố ý khớp phạm vi mà báo cáo tuyên bố, tránh ngụ ý hỗ trợ toàn bộ OWL 2 DL.
Fuseki chỉ phục vụ endpoint query cho quy trình đánh giá, không nằm trên critical
path của `make demo`.

# Chương 4. IV. Truy vấn, xử lý và nghiệp vụ

## 4.1. Ngôn ngữ truy vấn và suy diễn đặc thù

### SPARQL

Mười query bao phủ phim theo đạo diễn, cast, shared genre, co-star aggregation,
director–genre multi-hop, OPTIONAL IMDb enrichment, inverse `hasActor`, semantic
path, ASK quality và CONSTRUCT bằng chứng gợi ý. Loader bắt buộc đúng 10
query, parse rồi chạy từng query trên graph đã materialize.

### An toàn truy vấn

An toàn có nhiều tầng. Pydantic giới hạn request length/type; parser chỉ nhận
chín ý định; mỗi ý định ánh xạ đến một Cypher pattern do ứng dụng sở hữu; entity
value nằm trong Neo4j parameter; public API không có write operation. Không có
raw user input nào được dùng làm cấu trúc Cypher.

Parameterized query ngăn injection qua value nhưng không tự ngăn query đắt. Vì
vậy query catalog còn áp giới hạn kết quả, shortest-path depth `≤8`, fixed pattern và không
cho arbitrary Cypher. Query safety không thể chỉ mô tả bằng một câu “đã dùng
parameter”.

## 4.2. Bộ truy vấn và thao tác nghiệp vụ từ cơ bản đến nâng cao

### Cypher catalog và CRUD

Catalog có 10 query từ lookup đến shortest path, aggregation và kiểm tra fact suy
ra. CRUD Movie gồm create/upsert, read neighborhood, update metadata, guarded
delete và upsert `ACTED_IN`; mọi value là parameter. CRUD không mở qua public API.

### Competency questions

1. Phim nào do một đạo diễn thực hiện?
2. Ai đóng trong một phim?
3. Hai diễn viên có phim chung nào?
4. Phim thuộc thể loại X có rating trên ngưỡng?
5. Ai từng đóng chung với một người?
6. Đạo diễn nào thường làm phim thuộc thể loại X?
7. Đường ngắn nhất giữa hai người?
8. Phim nào tương tự một phim nguồn và vì sao?
9. Thống kê số node theo label?
10. Fact co-star nào được suy ra và bằng chứng là phim nào?

### Ma trận truy vết competency question

| CQ | Pattern chính | Số bước | Đầu ra/bằng chứng |
|---:|---|---:|---|
| 1 | Person-DIRECTED-Movie | 1 | Movie ID/title, director link |
| 2 | Person-ACTED_IN-Movie | 1 | Person và edge metadata |
| 3 | Person-ACTED_IN-Movie-ACTED_IN-Person | 2 | shared Movie |
| 4 | Movie-HAS_GENRE-Genre + rating | 1 + filter | Movie/rating/genre |
| 5 | Person-CO_STARRED_WITH-Person | derived | count/bằng chứng IDs |
| 6 | Person-DIRECTED-Movie-HAS_GENRE-Genre | 2 + aggregate | director/count |
| 7 | variable path giữa Person | tối đa 8 edge | node/relationship path |
| 8 | Movie-feature-Movie | 2 mỗi feature | contribution/feature |
| 9 | scan label | 0 | count theo label |
| 10 | CO_STARRED_WITH | derived audit | pair/count/bằng chứng IDs |

Ma trận là cầu nối giữa yêu cầu, schema, query catalog, API và test. Class hoặc
relationship không hỗ trợ competency question nào cần được cân nhắc loại khỏi
MVP; một CQ không ánh xạ được query chỉ ra thiếu sót thiết kế.

### Acceptance criteria

Dataset phải đạt ít nhất 2.000 Movie; import hai lần không đổi counts; kiểm tra hợp lệ
không có violation chưa giải thích; catalog Cypher/SPARQL phải parse/chạy; API trả
schema hợp lệ; gợi ý trả lời giải thích; evaluation ghi backend, corpus và
protocol; integration test phải kết nối Neo4j test riêng thay vì skip do graph
trình diễn có dữ liệu.

## 4.3. Truy vấn có suy luận và tri thức ẩn

### Suy diễn `CO_STARRED_WITH`

Luật:

```text
Person A -[:ACTED_IN]-> Movie <-[:ACTED_IN]- Person B
=> A -[:CO_STARRED_WITH]-> B
```

Điều kiện sắp thứ tự ID tránh cặp trùng/ngược. Relationship lưu `movie_count`,
`evidence_movie_ids` và `derived=true`. `MERGE` bảo đảm materialization idempotent.
Đây là rule nghiệp vụ bằng Cypher, không được gọi là OWL reasoning.

### Semantic entailment

RDFLib materializer và Jena Generic Rule Reasoner cùng chạy profile RDFS/OWL
subset xác định:

- property domain → type của subject;
- property range → type của object;
- `owl:inverseOf` → inverse triple;
- `owl:SymmetricProperty` → triple chiều ngược.

Validator kiểm tra functional property, disjoint class và Movie thiếu title. RDFLib
ghi data graph 342.683 → 429.192 triple. Jena tính trên union data + 70 ontology
triple, do đó 342.753 → 429.262; cả hai engine đều suy ra đúng 86.509 triple mới.
Fuseki thực thi 10/10 query, trong đó có 81.030 inverse `hasActor`. Profile này
chạy được và test được, nhưng không thay thế OWL 2 DL reasoner đầy đủ.

# Chương 5. V. Thực nghiệm và đánh giá

## 5.1. Tiêu chí đánh giá

### Gợi ý dựa trên graph

Hai phim có thể tương tự vì chung đạo diễn, diễn viên, thể loại, từ khóa hoặc
studio. Raw overlap thiên về phim có metadata dày và feature phổ biến. Đề tài dùng:

```text
contribution(feature) = type_weight × (1 + ln((N+1)/(df(feature)+1)))
score(source,candidate) = tổng contribution của các feature chung
```

Trong đó `N` là số phim và `df` là số phim liên kết với feature. Feature hiếm có
giá trị phân biệt cao hơn. Đây là item-to-item similarity, không phải xác suất
yêu thích và không phải personalization theo người dùng.

### Chỉ số đánh giá

- Data quality: missing, duplicate, invalid edge, orphan và độ bao phủ.
- Phân giải thực thể: Precision, Recall, F1.
- Reasoning: precision của fact suy ra và độ bao phủ bằng chứng.
- QA: ý định accuracy, answer correctness và bằng chứng.
- Gợi ý: Precision@K, DCG/NDCG@K, độ bao phủ lời giải thích.
- Performance: median, p95 và standard deviation sau warm-up.

### Cách đọc kết quả

Các kết quả dưới đây được ghi kèm backend, số lượng phim, số case, K, số lần lặp
và cấu hình cần thiết. Các bộ kiểm thử do nhóm chuẩn bị nhằm kiểm tra hệ thống
trên ảnh chụp dữ liệu hiện tại; số liệu QA và hiệu năng được lấy từ Neo4j thực tế.

## 5.2. Kịch bản thực nghiệm, phép đo hiệu năng, bảng biểu và mốc so sánh

### Dataset và graph

ảnh chụp dữ liệu đầu vào có 5.000 record và giữ 4.999 Movie hợp lệ; một record không có
quan hệ graph bị loại bởi quality gate. Exact IMDb ratings match 4.351/4.558 phim có IMDb ID.
Graph sau reasoning có 76.612 node và 846.309 relationship, với zero
orphan, duplicate stable ID, missing required property và invalid relationship.

Các số liệu này lấy từ `data/processed/manifest.json` và
`experiments/results/quality/neo4j_validation.json` của cùng source checksum
`44cda033...58fd09`.

| Chỉ số ảnh chụp dữ liệu/graph | Giá trị cuối |
|---|---:|
| Record TMDB đầu vào | 5.000 |
| Movie hợp lệ sau quality gate | 4.999 |
| Movie bị loại do không có quan hệ | 1 |
| Movie có IMDb ID | 4.558 (91,18%) |
| IMDb rating exact-match | 4.351/4.558 (95,46%) |
| Movie có cast | 99,26% |
| Movie có director | 98,92% |
| Movie có genre | 97,40% |
| Orphan/duplicate/missing/invalid/unsupported fact sau import | 0 |

Quality gate không xóa im lặng record lỗi: nếu phát hiện Movie không có quan hệ,
record sẽ được ghi trong `invalid_records` với reason và source row/TMDB ID.
Ảnh chụp dữ liệu hiện tại ghi một lỗi `no_graph_relationships` cho TMDB ID `1038919`;
vì vậy valid count nhỏ hơn input count một record.

### Phân giải thực thể

Corpus kiểm thử gồm 100 case: 75 positive và 25 negative, có source ID/bằng chứng.
Candidate set dùng bốn tên cùng loại gần nhất thay vì decoy tùy ý. Kết quả là
TP=70, TN=25, FP=0, FN=5: precision=1,000, recall=0,933 và F1=0,966. Bốn missed
match là typo ngắn dưới ngưỡng 0,90; case còn lại có hai phim cùng tên `Alter Ego`
nên resolver từ chối tie thay vì merge tùy tiện. Chính sách này ưu tiên precision
vì false merge làm ô nhiễm graph nghiêm trọng hơn một match bị bỏ lỡ.

Audit toàn ảnh chụp dữ liệu
ghi nhận zero duplicate stable ID, conflicting required value, missing required
field, invalid foreign key và duplicate endpoint pair; provenance độ bao phủ của
node/edge có trường source đạt 100%. Hai trăm linh chín tên Person trùng không bị merge
vì stable source ID là identity key. Corpus silver là phép đo hiệu năng tất định dựa trên
source ID, typo có kiểm soát và nearest-name hard negative; kết quả không đại diện
cho mọi lỗi định danh có thể xuất hiện ngoài ảnh chụp dữ liệu.

### Reasoning

Năm mươi fact `CO_STARRED_WITH` được kiểm tra bằng supporting movie và
source cast; 50/50 fact hợp lệ, precision bằng 1,00. Kiểm tra hợp lệ bổ sung còn kiểm
tra mọi derived edge phải có ít nhất một shared Movie. Semantic quy trình trên
full normalized ảnh chụp dữ liệu materialize 86.509 triple, tăng từ 342.683 lên 429.192
triple và không có semantic violation. RDF export dùng chính ảnh chụp dữ liệu đã xử lý
4.999 Movie như Neo4j. Apache Jena Fuseki 6.1.0 tái hiện đúng mức tăng 86.509
triple bằng forward rule profile; 10/10 SPARQL query thực thi thành công trên cả
RDFLib và endpoint Jena.

### QA

Corpus deterministic gồm 20 câu phủ chín ý định, yêu cầu đúng ý định, nội dung
mong đợi và tối thiểu một bằng chứng record (riêng top-5 yêu cầu đủ năm bằng chứng).
Production path trên Neo4j đạt 20/20. Rubric shortest-path chấp nhận mọi đường hợp
lệ thay vì khóa vào một quy mô trung gian; câu hỏi gợi ý kiểm tra giao ước
và bằng chứng, còn chất lượng ranking được chấm riêng bằng P@10/NDCG@10. Đây vẫn là
bộ kiểm thử chức năng do nhóm xây dựng và có thể mở rộng thêm paraphrase hoặc câu
mơ hồ trong các phiên bản sau.

### Gợi ý

| Phương pháp | P@10 | NDCG@10 | Vai trò |
|---|---:|---:|---|
| Overlap | 0,670 | 0,723 | mốc so sánh lịch sử |
| Weighted Jaccard | 0,640 | 0,699 | mốc so sánh lịch sử |
| Hybrid | 0,590 | 0,657 | mốc so sánh lịch sử |
| IDF-weighted graph | **0,635** | **0,672** | production Neo4j hiện tại |

IDF đạt P@10=0,635 và NDCG@10=0,672 trên 20 case hiện tại; mọi gợi ý có
lời giải thích. Ba hàng mốc so sánh là lịch sử thiết kế trên ảnh chụp dữ liệu/cấu hình trước,
vì vậy không dùng để kết luận IDF tốt hơn nếu chưa tái chạy chung protocol. Corpus
nhỏ và relevance rubric dựa trên metadata graph; kết quả không đồng nghĩa người
dùng thực sẽ ưa thích gợi ý.

### Hiệu năng

phép đo hiệu năng đa quy mô dùng bốn ảnh chụp dữ liệu con tất định 500/1.000/2.000/4.999 Movie từ
cùng processed order. Mỗi scale được import authoritative vào Neo4j test riêng;
SQLite dựng bảng/index từ đúng các CSV cùng scale. Bốn query tương đương chạy trên
cùng máy, một warm-up và 100 lần/query. Mỗi ảnh chụp dữ liệu lưu checksum, count node/edge,
phiên bản runtime và protocol trong metadata.

| Backend / số Movie | Khoảng median 4 query (ms) | Khoảng p95 4 query (ms) |
|---|---:|---:|
| Neo4j / 500 | 4,688–15,156 | 7,042–22,406 |
| Neo4j / 1.000 | 7,569–16,902 | 9,614–23,112 |
| Neo4j / 2.000 | 6,562–25,666 | 9,510–37,530 |
| Neo4j / 4.999 | 7,831–44,312 | 11,603–52,081 |
| SQLite / 500 | 0,216–2,771 | 0,233–2,854 |
| SQLite / 1.000 | 0,530–7,308 | 0,828–10,936 |
| SQLite / 2.000 | 1,063–14,193 | 1,424–17,893 |
| SQLite / 4.999 | 2,177–39,995 | 2,414–48,822 |

SQLite nhanh hơn trong bốn query kiểm soát này. Kết quả là bằng chứng chống lại
tuyên bố đơn giản “graph luôn nhanh hơn SQL”; lợi ích chính của Neo4j trong đề tài
là mô hình traversal/bằng chứng và một execution surface thống nhất, không phải ưu
thế latency phổ quát. Bốn điểm đo cho thấy xu hướng latency theo workload trong
phạm vi 500–4.999 Movie; chúng không phải tuyên bố scalability tổng quát vì chưa
đo concurrency, cold cache, tài nguyên hoặc dataset lớn hơn.

### Protocol tái chạy thực nghiệm

1. Cố định ảnh chụp dữ liệu thô và ghi checksum.
2. Transform/import authoritative, chạy kiểm tra hợp lệ và lưu counts.
3. Chạy reasoning trước evaluation phụ thuộc derived edges.
4. Chạy corpus bằng đúng backend được khai báo.
5. Sinh ảnh chụp dữ liệu con 500/1.000/2.000/4.999; phép đo hiệu năng một warm-up và 100
   iterations/query; không chạy workload khác song song.
6. Lưu Python/Neo4j/platform/movie count trong metadata.
7. Sinh bảng/biểu đồ từ JSON/CSV sản phẩm đầu ra, không nhập số bằng tay.
8. Kiểm tra báo cáo/trang chiếu dùng cùng sản phẩm đầu ra version.

Với relational mốc so sánh, ảnh chụp dữ liệu và máy phải giống Neo4j run. Nếu không đáp ứng,
kết quả chỉ được báo riêng, không dùng để xếp hạng engine.

### Kiểm thử và quy trình chạy

Lần chạy cuối của `make test` đạt 33/33 test. Bộ test gồm unit test cho cleaning,
phân giải thực thể, ý định parsing, RDF export, semantic materialization,
SPARQL catalog, CRUD, phép đo hiệu năng quan hệ và bằng chứng summary. Integration test
dùng Neo4j riêng ở Bolt 7688, thực hiện import hai lần để xác nhận idempotency,
sau đó kiểm tra QA, gợi ý và vòng đời CRUD trước khi dọn graph test.

Docker healthcheck gọi `cypher-shell RETURN 1`, nên trạng thái healthy chỉ được
báo sau khi Bolt thực sự nhận query; điều này loại race condition trong đó
container đã chạy nhưng driver chưa handshake được. Quy trình còn chạy
`compileall`, kiểm tra dependency và xác minh checksum của tài liệu nguồn.

## 5.3. Phân tích, bàn luận, hạn chế và hướng cải tiến

### Threats to validity

- Popular-movie sampling tạo selection bias.
- Top-20 cast bỏ diễn viên phụ.
- Nguồn TMDB thay đổi theo thời gian; cache chỉ cố định một ảnh chụp dữ liệu.
- IMDb chỉ enrich Movie, chưa link Person.
- Các bộ case đánh giá do nhóm xây dựng và còn nhỏ.
- QA corpus deterministic 20 câu chưa phủ paraphrase rộng.
- Gợi ý không có user interaction, nên không đánh giá personalization.
- Phép đo hiệu năng có bốn quy mô nhưng vẫn phụ thuộc phần cứng/warm cache, chưa đo concurrency.

### Trả lời câu hỏi nghiên cứu

**RQ1:** Stable source ID và exact IMDb join tích hợp hai nguồn mà không ghi đè
rating; checksum/manifest cung cấp provenance ở mức ảnh chụp dữ liệu.
**RQ2:** Mười competency question được biểu diễn bằng pattern trực tiếp, multi-hop,
aggregation và shortest path; bằng chứng là node/relationship thực thi.
**RQ3:** Cypher rule tạo co-star có supporting movie; semantic profile tạo inverse
và type entailment, đồng thời validator phát hiện conflict.
**RQ4:** IDF giảm ảnh hưởng feature phổ biến, đạt P@10=0,635 và NDCG@10=0,672,
đồng thời giữ độ bao phủ lời giải thích. Ba mốc so sánh lịch sử chỉ cung cấp design
history, không dùng để khẳng định production vượt trội nếu chưa tái chạy chung protocol.
**RQ5:** Hệ thống đạt mục tiêu trình diễn và khả năng chạy lại ở 4.999 phim; phạm vi
hiện tại chưa gồm cá nhân hóa; phép đo hiệu năng bốn quy mô mới mô tả trend trong phạm vi
500–4.999 Movie, chưa chứng minh scalability tổng quát.

### Phân tích lỗi và hướng khắc phục

#### QA

Rubric cũ khóa shortest path vào một intermediate và đã được thay bằng yêu cầu
đúng ý định, có đường/bằng chứng hợp lệ. Gợi ý question chỉ kiểm tra API
contract; relevance dùng corpus P@10/NDCG@10 riêng. Bước tiếp theo là bổ sung
paraphrase, câu mơ hồ và expected abstention thay vì chỉ dùng các câu gần template.

#### Phân giải thực thể

Corpus exact-ID dễ hơn dữ liệu mention thực tế. Cần bổ sung hard negative cùng tên,
alias, Unicode, tên đảo, thiếu ID và candidate tie. Từng error phải phân loại false
merge hoặc missed match vì false merge gây ô nhiễm graph nghiêm trọng hơn.

#### Gợi ý

IDF có thể ưu tiên feature quá hiếm do metadata noise. Có thể đặt minimum document
frequency hoặc review contribution distribution. Tuy nhiên thay đổi trọng số phải
đánh giá trên corpus tách biệt, không điều chỉnh trực tiếp theo 20 case rồi báo
trên chính các case đó.

#### Performance

Similar-movie chậm nhất gợi ý cần inspect query plan, cardinality và index; nhưng
index không giúp mọi traversal. Bước tiếp theo là đo cold/warm cache riêng,
concurrency, CPU/RAM và scale lớn hơn trước khi tối ưu.

# Chương 6. VI. Ứng dụng và trình diễn chương trình

## 6.1. Ứng dụng nghiệp vụ và trình diễn chương trình

### Bên liên quan và trường hợp sử dụng

- Người dùng cuối hỏi thông tin phim và nhận gợi ý có lý do.
- Data engineer thu thập, chuẩn hóa, enrich và import dữ liệu.
- Người vận hành khởi động Neo4j/API và kiểm tra health/stats.
- Người đánh giá chạy test, query, phép đo hiệu năng và truy vết bằng chứng.

### Yêu cầu chức năng

| ID | Yêu cầu | Sản phẩm đầu ra chính |
|---|---|---|
| F01 | Thu thập/cache TMDB | `collect_tmdb.py`, `tmdb_client.py` |
| F02 | Tải/stream IMDb ratings | `download_imdb.py`, `imdb_loader.py` |
| F03 | Clean, normalize, phân giải thực thể | `processing/` |
| F04 | Sinh 5 node CSV + 5 edge CSV + manifest | `pipeline.py` |
| F05 | Import/validate Neo4j idempotent | `load_neo4j.py` |
| F06 | RDF export, entailment, 10 SPARQL | `export_rdf.py`, `semantic_reasoning.py` |
| F07 | 10 Cypher và CRUD parameterized | `cypher/`, `kg/crud.py` |
| F08 | QA answer + bằng chứng | `/ask` |
| F09 | Gợi ý + lời giải thích | `/recommend` |
| F10 | Search/stats/health và UI | FastAPI/static UI |

### Hỏi–đáp

```text
Question → parser 9 intent → trích xuất slot → entity linking
         → fixed query catalog → parameterized Cypher
         → Neo4j → answer + evidence + latency
```

Parser tất định nhận diện chín ý định và trích xuất slot. Entity linker
canonicalize tên trước query và trả confidence trong bằng chứng. Mỗi ý định ánh xạ
tới một graph pattern cố định; user input luôn nằm trong parameter.

### Gợi ý

Neo4j tạo candidate bằng các phim chia sẻ ít nhất một director, actor, keyword,
genre hoặc studio. Mỗi feature được tính document frequency trong graph và đóng
góp IDF theo type weight. Query trả candidate, score và feature chung; Python chỉ
định dạng `Recommendation` và lời giải thích. Tie-break theo title giúp kết quả xác
định. Endpoint nhận `movie_id` thay vì title để tránh nhập nhằng.

### API và UI

| Endpoint | Chức năng |
|---|---|
| GET `/health` | kiểm tra Neo4j connectivity |
| GET `/stats` | số node theo label và tổng relationship |
| GET `/entities/search` | full-text rồi fallback parameterized search |
| POST `/ask` | QA answer, ý định, bằng chứng, query time |
| POST `/recommend` | top-K gợi ý và lời giải thích |

UI có hai tab QA và gợi ý, autocomplete phim, lịch sử hiển thị và state
loading/error/success. Lịch sử chỉ ở frontend; backend hiện stateless.

### An toàn và vận hành

Secret nằm trong `.env`; raw data không commit. Public API không có write
endpoint. Hạn chế hiện tại
là chưa có authentication/rate limiting, nên cấu hình phù hợp trình diễn local chứ
không phải public production deployment.

### Failure modes

| Tình huống | Hành vi |
|---|---|
| Câu hỏi ngoài 9 ý định | trả ý định `unknown` và gợi ý dạng câu hỏi hỗ trợ |
| confidence thấp/thiếu slot | trả clarification |
| entity không tồn tại | trả entity-not-found/không tìm thấy |
| movie ID recommend sai | HTTP 404 |
| Neo4j không sẵn sàng | health 503 |
| tên fuzzy nhập nhằng | không tự chọn tied candidate |

Failure behavior là một phần correctness. Hệ QA an toàn nên thừa nhận không biết
hoặc yêu cầu làm rõ thay vì chạy query với entity đoán sai.

### Tính faithful của lời giải thích

QA bằng chứng gồm canonical entity/link confidence và record/path trả từ Neo4j.
Gợi ý lời giải thích không được model sinh: nó tổng hợp từ shared feature
đã đóng góp score. Cách làm giảm độ tự nhiên so với NLG lời giải thích [10] nhưng
có tính faithful cao trong phạm vi hệ thống: mỗi lý do tương ứng quan hệ tồn tại
trong graph và contribution xác định.

# Chương 7. Kết luận và hướng phát triển

Đề tài đã xây dựng một đồ thị tri thức phim đầu cuối từ thu thập dữ liệu đến hai
ứng dụng. Neo4j phục vụ operational traversal; RDF/OWL cung cấp semantic standards
view. Stable ID, provenance, safe query compiler, evidence-backed inference và
explainable recommendation giúp kết quả không chỉ chạy được mà còn kiểm tra được.

Hạn chế chính nằm ở độ bao phủ dữ liệu, phạm vi QA và external validity. Thứ tự phát
triển hợp lý là: hoàn tất independent review; xây QA corpus lớn hơn; phép đo hiệu năng
concurrency và ảnh chụp dữ liệu lớn hơn; cải thiện
ambiguity handling; sau đó mới mở rộng Wikidata/Award, temporal graph, vector
retrieval, GraphRAG hoặc graph embedding. Mọi mở rộng phải giữ nguyên nguyên tắc: model lập kế hoạch,
compiler kiểm soát execution, graph cung cấp fact và bằng chứng.

# Tài liệu tham khảo

[1] W3C, “RDF 1.1 Concepts and Abstract Syntax.”  
[2] W3C, “RDF Schema 1.1.”  
[3] W3C, “OWL 2 Web Ontology Language Document Overview.”  
[4] W3C, “SPARQL 1.1 Query Language.”  
[5] Neo4j, “Cypher Manual, Neo4j 5.”  
[6] TMDB, “TMDB API Documentation.”  
[7] IMDb, “IMDb Non-Commercial Datasets.”  
[8] Q. Guo, F. Zhuang, C. Qin, H. Zhu, X. Xie, H. Xiong, and Q. He, “A Survey
on Knowledge Graph-Based Recommender Systems: Extended Abstract,” in *Proc. 39th
IEEE Int. Conf. Data Engineering (ICDE)*, 2023.  
[9] M. Caro-Martínez, G. Jiménez-Díaz, and J. A. Recio-Garcia, “A graph-based
approach for minimising the knowledge requirement of explainable recommender
systems,” *Knowledge and Information Systems*, vol. 65, pp. 4379–4409, 2023,
doi: 10.1007/s10115-023-01903-9.  
[10] A. Colas, J. Araki, Z. Zhou, B. Wang, and Z. Feng, “Knowledge-grounded
Natural Language Recommendation Explanation,” in *Proc. 6th BlackboxNLP
Workshop*, pp. 1–15, 2023.  
[11] X. Ren, T. Chen, Q. V. H. Nguyen, L. Cui, Z. Huang, and H. Yin, “Explicit
Knowledge Graph Reasoning for Conversational Recommendation,” *ACM Transactions
on Intelligent Systems and Technology*, vol. 15, no. 4, pp. 1–21, 2024,
doi: 10.1145/3637216.  
[12] Y. Zhang, L. Zhang, Y. Dong, J. Chu, X. Wang, and Z. Ying, “A movie
recommendation method based on knowledge graph and time series,” *Journal of
Intelligent & Fuzzy Systems*, vol. 45, no. 3, 2023, doi: 10.3233/JIFS-230795.  
[13] N. I. Y. Saat, S. A. M. Noah, and M. Mohd, “Enhanced Content-Based
Recommendation Using Topic Modelling and Knowledge Graph,” *Elektronika ir
Elektrotechnika*, vol. 30, no. 2, pp. 73–79, 2024,
doi: 10.5755/j02.eie.35642.  
[14] M. Su, Z. Li, Z. Chen, L. Bai, X. Jin, and J. Guo, “Temporal Knowledge
Graph Question Answering: A Survey,” arXiv:2406.14191, 2024.
[15] D. Agarwal, R. Das, S. Khosla, and R. Gangadharaiah, “Bring Your Own KG:
Self-Supervised Program Synthesis for Zero-Shot KGQA,” in *Findings of the
Association for Computational Linguistics: NAACL 2024*, pp. 896–919, 2024.  
[16] A. Hogan et al., “Knowledge Graphs,” *ACM Computing Surveys*, vol. 54,
no. 4, 2021.

# Phụ lục A. Hướng dẫn cài đặt và chạy chương trình

Môi trường yêu cầu Python 3.11 trở lên, Docker và Docker Compose. Các biến cấu
hình được khai báo trong `.env`; khóa `TMDB_API_KEY` chỉ cần thiết khi thu thập
lại dữ liệu. Quy trình chạy cơ bản như sau:

```bash
make setup
make data DATA_COUNT=5000
make demo
```

Sau khi khởi động, giao diện web có tại `http://localhost:8000/` và tài liệu API
Swagger có tại `http://localhost:8000/docs`. Kiểm tra toàn bộ hệ thống bằng:

```bash
make test
.venv/bin/python -m experiments.evaluation.audit_knowledge_quality
.venv/bin/python -m experiments.evaluation.evaluate_entity_resolution \
  experiments/corpora/silver/entity_resolution.json \
  --output experiments/results/evaluation/entity_resolution.json
docker compose --profile semantic up -d --build jena
.venv/bin/python -m experiments.semantic.evaluate_jena
docker compose --profile semantic stop jena
docker compose --profile test up -d --wait neo4j-test
RUN_NEO4J_TESTS=1 ALLOW_NEO4J_TEST_RESET=1 \
  ALLOW_MULTISCALE_BENCHMARK=1 NEO4J_URI=bolt://localhost:7688 \
  NEO4J_PASSWORD=test-password \
  .venv/bin/python -m experiments.benchmarks.benchmark_multiscale
```

`make demo` so processed checksum để chỉ import lại khi CSV graph thực sự thay đổi.
Dữ liệu Neo4j kiểm thử chạy ở Bolt 7688 và tách biệt với graph trình diễn. Bốn lệnh đánh
giá phía trên không cần chạy trong buổi trình diễn; chúng tái tạo quality audit, review
pack, Jena/Fuseki result và phép đo hiệu năng đa quy mô.

# Phụ lục B. API và ví dụ sử dụng

| Phương thức | Endpoint | Chức năng |
|---|---|---|
| `GET` | `/health` | Kiểm tra kết nối đồ thị tri thức |
| `GET` | `/stats` | Trả số lượng node và relationship |
| `GET` | `/entities/search?q=...` | Tìm Movie, Person, Genre, Keyword hoặc Studio |
| `POST` | `/ask` | Hỏi–đáp bằng ngôn ngữ tự nhiên |
| `POST` | `/recommend` | Gợi ý phim theo TMDB ID |

Ví dụ gửi câu hỏi:

```bash
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Những phim nào do Christopher Nolan đạo diễn?"}'
```

Response gồm `answer`, `intent`, `evidence` và `query_time_ms`. Ví dụ yêu cầu gợi
ý ba phim tương tự `Inception`:

```bash
curl -X POST http://localhost:8000/recommend \
  -H 'Content-Type: application/json' \
  -d '{"movie_id":27205,"top_k":3}'
```

Mỗi gợi ý trả `movie_id`, `title`, `score`, các feature chung theo từng
loại và câu giải thích được dựng từ chính các feature đã đóng góp vào điểm.

# Phụ lục C. Truy vấn minh họa

Truy vấn Cypher tìm phim theo đạo diễn:

```cypher
MATCH (p:Person)-[:DIRECTED]->(m:Movie)
WHERE toLower(p.name) = toLower($director)
RETURN m.tmdb_id AS movie_id, m.title AS title
ORDER BY m.release_date
```

Truy vấn Cypher sử dụng quan hệ suy diễn để tìm bạn diễn:

```cypher
MATCH (a:Person)-[r:CO_STARRED_WITH]-(b:Person)
WHERE toLower(a.name) = toLower($person)
RETURN b.name, r.movie_count, r.evidence_movie_ids
ORDER BY r.movie_count DESC
```

Truy vấn SPARQL sử dụng inverse relation sau semantic materialization:

```sparql
PREFIX : <https://example.org/movie-kg/>
SELECT ?movie ?actor
WHERE { ?movie :hasActor ?actor }
```

Catalog đầy đủ gồm 10 truy vấn Cypher tại `cypher/queries.cypher` và 10 truy vấn
SPARQL tại `sparql/queries.rq`. Các truy vấn do ứng dụng thực thi được tham số hóa
và quản lý tập trung trong `src/kg/query_catalog.py`.

# Phụ lục D. Cấu trúc dữ liệu và kết quả thực nghiệm

Các đường dẫn kết quả trong bảng được tính tương đối từ `experiments/results/`.

| Đường dẫn | Nội dung |
|---|---|
| `data/processed/`<br>`manifest.json` | Checksum nguồn, số lượng bản ghi và chỉ số chất lượng dữ liệu |
| `data/processed/`<br>`*.csv` | Năm bảng node và năm bảng relationship đã chuẩn hóa |
| `data/processed/`<br>`movies.ttl` | RDF export từ ảnh chụp dữ liệu đã xử lý |
| `data/processed/`<br>`movies.inferred.ttl` | RDF sau semantic materialization |
| `quality/`<br>`neo4j_validation.json` | Kết quả kiểm tra cấu trúc graph |
| `evaluation/`<br>`qa_neo4j.json` | Kết quả bộ câu hỏi QA trên Neo4j |
| `evaluation/`<br>`recommendation.json` | P@10 và NDCG@10 của gợi ý |
| `benchmarks/`<br>`neo4j_benchmark.csv` | Median, p95 và độ lệch chuẩn theo truy vấn |
| `benchmarks/`<br>`relational_benchmark.csv` | Mốc so sánh SQLite trên cùng ảnh chụp dữ liệu đã xử lý |
| `quality/`<br>`knowledge_quality_audit.json` | Audit identity, consistency, completeness và provenance |
| `semantic/`<br>`jena_semantic_evaluation.json` | Jena/Fuseki reasoner và kết quả 10 SPARQL |
| `benchmarks/`<br>`multiscale_benchmark.csv` | Neo4j–SQLite tại 500/1.000/2.000/4.999 Movie |

Ảnh chụp dữ liệu hiện tại gồm 4.999 Movie, 53.555 Person, 19 Genre, 12.509 Keyword và
5.530 Studio. Các sản phẩm đầu ra thực nghiệm được lưu dưới CSV hoặc JSON để có thể kiểm
tra lại số liệu và tái tạo bảng, biểu đồ trong Chương 5.
