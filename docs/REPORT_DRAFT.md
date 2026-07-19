# XÂY DỰNG MOVIE KNOWLEDGE GRAPH ĐA NGUỒN

> **Bản thảo báo cáo chính.** Các trường hành chính trong ngoặc vuông cần được
> nhóm điền trước khi xuất DOCX/PDF. Số liệu trong báo cáo được khóa theo artifact
> thực nghiệm đã xác nhận; sau khi `make data` hoàn tất, chạy lại evaluation và
> chỉ cập nhật số liệu thông qua `manifest.json` và `experiments/results/`.

**Học phần:** Cơ sở dữ liệu nâng cao  
**Giảng viên:** [Tên giảng viên]  
**Nhóm thực hiện:** [Tên nhóm]  
**Thành viên:** [Họ tên – MSSV]  
**Thời gian:** 2026

## Lời mở đầu

Knowledge Graph là một hướng tiếp cận phù hợp với dữ liệu có nhiều loại thực thể
và quan hệ liên kết. Trong miền phim, một bộ phim liên hệ với diễn viên, đạo diễn,
thể loại, từ khóa và hãng sản xuất; các quan hệ này tạo ra nhiều câu hỏi mà cách
biểu diễn đồ thị có thể mô tả trực tiếp và dễ theo dõi hơn.

Báo cáo trình bày quá trình xây dựng Movie Knowledge Graph từ dữ liệu TMDB và
IMDb, bao gồm thu thập và chuẩn hóa dữ liệu, thiết kế ontology và graph schema,
nạp dữ liệu vào Neo4j, truy vấn Cypher, biểu diễn RDF/OWL và một số luật suy diễn.
Trên nền tảng đó, project triển khai hai chức năng chính: hỏi–đáp về phim bằng
ngôn ngữ tự nhiên và gợi ý phim kèm lý do dựa trên các quan hệ chung trong graph.

Mục tiêu của project là minh họa một quy trình Knowledge Graph đầu cuối có thể
chạy, kiểm tra và trình diễn trong phạm vi học phần Cơ sở dữ liệu nâng cao. Báo
cáo được tổ chức thành mười chương với nội dung tổng quan như sau:

1. **Chương 1 – Giới thiệu:** trình bày bối cảnh, bài toán, mục tiêu, phạm vi và
   các đóng góp chính của project.
2. **Chương 2 – Cơ sở lý thuyết:** giới thiệu Knowledge Graph, ontology,
   RDF/RDFS/OWL, SPARQL, Property Graph, Neo4j, entity resolution và các chỉ số
   đánh giá được sử dụng.
3. **Chương 3 – Công trình và nền tảng liên quan:** tổng hợp các hướng tiếp cận
   liên quan đến Knowledge Graph, hỏi–đáp và recommendation để xác định vị trí
   của project.
4. **Chương 4 – Phân tích yêu cầu:** mô tả đối tượng sử dụng, yêu cầu chức năng,
   yêu cầu phi chức năng, competency question và tiêu chí nghiệm thu.
5. **Chương 5 – Thiết kế ontology và graph schema:** trình bày các lớp, thuộc
   tính, quan hệ, định danh thực thể và cách ánh xạ giữa RDF với Neo4j.
6. **Chương 6 – Kiến trúc và pipeline dữ liệu:** mô tả kiến trúc tổng thể, quá
   trình thu thập TMDB/IMDb, làm sạch, chuẩn hóa, import và kiểm tra graph.
7. **Chương 7 – Truy vấn, suy diễn và semantic workflow:** giới thiệu catalog
   Cypher/SPARQL, luật `CO_STARRED_WITH` và quá trình materialize các quan hệ ngữ
   nghĩa.
8. **Chương 8 – Ứng dụng:** trình bày hệ hỏi–đáp, chức năng gợi ý phim có giải
   thích, API, giao diện web và cách các thành phần khai thác Knowledge Graph.
9. **Chương 9 – Thực nghiệm và kết quả:** tổng hợp chất lượng dữ liệu, kết quả
   kiểm thử QA, reasoning, recommendation, benchmark Neo4j và SQLite baseline.
10. **Chương 10 – Kết luận và hướng phát triển:** tổng kết kết quả đạt được, các
    hạn chế hiện tại và những hướng có thể mở rộng trong tương lai.

Phần phụ lục cung cấp hướng dẫn cài đặt và chạy chương trình, ví dụ sử dụng API,
một số truy vấn minh họa và vị trí các tệp dữ liệu, kết quả thực nghiệm.

---

# Chương 1. Giới thiệu

## 1.1. Bối cảnh

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
đường duyệt. Knowledge Graph phù hợp với bài toán này vì thực thể và quan hệ được
biểu diễn tường minh, còn câu hỏi nghiệp vụ có thể ánh xạ thành graph pattern.

## 1.2. Phát biểu bài toán

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

## 1.3. Câu hỏi nghiên cứu

**RQ chính:** Knowledge Graph có thể tích hợp dữ liệu phim đa nguồn, hỗ trợ truy
vấn multi-hop và suy diễn, đồng thời tạo câu trả lời và gợi ý có bằng chứng như
thế nào?

Các câu hỏi phụ gồm:

- **RQ1:** Exact-ID enrichment và stable source ID bảo đảm identity/provenance đến
  mức nào?
- **RQ2:** Property Graph hỗ trợ các competency question đa bước ra sao?
- **RQ3:** Rule materialization và semantic entailment sinh tri thức mới như thế
  nào, và làm sao kiểm tra tri thức đó?
- **RQ4:** IDF-weighted graph similarity cung cấp recommendation và explanation
  như thế nào so với các phương pháp overlap khác?
- **RQ5:** Hệ thống có giới hạn gì về coverage, accuracy, validity và scalability?

## 1.4. Mục tiêu

Mục tiêu tổng quát là xây dựng một Movie Knowledge Graph chạy được từ dữ liệu
nguồn đến ứng dụng. Các mục tiêu kiểm chứng được là:

- Thu thập và chuẩn hóa 2.000–5.000 phim cùng thực thể liên quan.
- Bảo toàn source ID, provenance và metadata quan trọng trên node/edge.
- Nạp graph idempotent vào Neo4j, có constraint/index và validation.
- Xây ontology RDF/OWL, RDF export và ít nhất 10 SPARQL query.
- Xây ít nhất 10 Cypher query, gồm multi-hop, aggregation và shortest path.
- Materialize `CO_STARRED_WITH` với evidence và chạy semantic entailment.
- Cung cấp API/UI cho QA và explainable recommendation.
- Đánh giá data quality, entity resolution, reasoning, QA, recommendation và latency.

## 1.5. Phạm vi

TMDB là nguồn graph chính; IMDb chỉ enrichment cho Movie bằng exact `imdb_id`.
Mỗi phim giữ tối đa 20 cast member nhằm giới hạn kích thước và thời gian thu thập.
MVP không bao gồm Award/Wikidata, NLP trên overview, user-history personalization,
vector search, embedding, GraphRAG hoặc LLM-to-Cypher tự do. Các thành phần này là
hướng mở rộng, không được dùng để mô tả chức năng hiện có.

## 1.6. Đóng góp

Đóng góp của đề tài gồm:

- Pipeline đa nguồn storage-bounded và tái lập được.
- Chiến lược identity dựa trên stable source ID thay vì tên.
- Mô hình kết hợp Neo4j operational graph và RDF/OWL standards view.
- Rule suy diễn lưu evidence, cùng semantic materializer/validator chạy được.
- QA có LLM planner nhưng execution surface được kiểm soát.
- Recommendation graph-native với explanation từ chính feature đóng góp.
- Bộ test/evaluation phân loại rõ evidence và giới hạn validity.

## 1.7. Cấu trúc báo cáo

Chương 2 trình bày cơ sở lý thuyết; Chương 3 tổng hợp công trình liên quan; Chương
4 phân tích yêu cầu; Chương 5 mô tả ontology và graph schema; Chương 6 trình bày
kiến trúc và pipeline; Chương 7 mô tả truy vấn/suy diễn; Chương 8 trình bày hai
ứng dụng; Chương 9 báo cáo thực nghiệm; Chương 10 kết luận và hướng phát triển.

# Chương 2. Cơ sở lý thuyết

## 2.1. Tri thức và Knowledge Graph

Dữ liệu là các giá trị thô; thông tin xuất hiện khi dữ liệu được đặt trong ngữ
cảnh; tri thức thể hiện các thực thể, quan hệ và quy tắc cho phép giải thích hoặc
suy ra điều mới. Trong Knowledge Graph, một fact được biểu diễn bằng quan hệ giữa
các thực thể có định danh. Fact có thể là **asserted fact**, lấy trực tiếp từ nguồn,
hoặc **derived fact**, sinh bởi luật và phải truy ngược được về tiền đề [16].

## 2.2. Ontology

Ontology là đặc tả hình thức cho một miền tri thức, gồm class, individual,
object property, datatype property và axiom. Taxonomy chủ yếu biểu diễn phân cấp
“is-a”, trong khi ontology còn mô tả domain/range, inverse, disjointness,
cardinality và các ràng buộc ngữ nghĩa khác. Đề tài thiết kế ontology từ
competency question: chỉ đưa class/property cần thiết để trả lời câu hỏi, tránh
mở rộng schema không có dữ liệu hoặc use case.

## 2.3. RDF, RDFS, OWL và SPARQL

RDF biểu diễn phát biểu bằng triple `(subject, predicate, object)` [1]. Subject và
predicate là IRI; object có thể là IRI hoặc literal. Một quad bổ sung graph name,
cho phép tổ chức nhiều named graph trong một RDF dataset, hữu ích khi tách nguồn
hoặc provenance. Namespace rút gọn IRI và giúp tránh xung đột định danh. Linked
Data nhấn mạnh IRI ổn định, có thể tham chiếu và liên kết giữa các nguồn.

RDFS cung cấp class, subclass, domain và range [2]. OWL bổ sung inverse property,
symmetric property, disjoint class, functional property và nhiều axiom mạnh hơn [3].
Ontology vận hành theo Open World Assumption: thiếu một fact không có nghĩa fact
đó sai. Vì vậy OWL reasoning và data validation là hai nhiệm vụ khác nhau. Đề tài
materialize tập con RDFS/OWL-RL đã khai báo, đồng thời dùng validation đóng để
kiểm tra functional conflict, disjoint type và required title.

SPARQL truy vấn graph bằng basic graph pattern [4]. `OPTIONAL` xử lý thuộc tính có thể
thiếu; `GROUP BY/COUNT` hỗ trợ aggregation; `ASK` kiểm tra sự tồn tại; `CONSTRUCT`
tạo một graph kết quả. Catalog của đề tài bao phủ cả bốn dạng này và có query dùng
inverse fact sau materialization.

## 2.4. Property Graph và Neo4j

Property Graph gồm node có label, relationship có type/hướng và property trên cả
node lẫn relationship. Neo4j dùng Cypher để match graph pattern. Unique constraint
bảo vệ stable key; index/full-text index tăng tốc lookup; transaction bảo đảm một
batch import không ở trạng thái dở dang. Property trên `ACTED_IN` như `character`
và `cast_order` là lý do thực dụng để chọn Property Graph làm operational store [5].

## 2.5. So sánh mô hình

| Khía cạnh | Quan hệ | Document | RDF/OWL | Property Graph |
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
chiếu lại đưa bài toán về nhiều phép lookup. Đề tài đo một SQLite baseline trên cùng snapshot thay vì dùng
lập luận lý thuyết để tuyên bố Neo4j luôn nhanh hơn.

Knowledge Graph cũng không nên được dùng chỉ vì dữ liệu “có quan hệ”. Nếu workload
chủ yếu là transaction theo khóa, báo cáo tổng hợp cố định hoặc dữ liệu nhỏ với
schema ổn định, CSDL quan hệ đơn giản hơn và có thể hiệu quả hơn. RDF/OWL chỉ đáng
đổi chi phí khi interoperability, định danh toàn cục hoặc entailment là yêu cầu
thật. Property Graph phù hợp đề tài vì competency question tập trung vào đường
đi, neighborhood và bằng chứng trên quan hệ; lựa chọn này là workload-driven,
không phải tuyên bố ưu thế phổ quát.

## 2.6. Entity resolution

Entity resolution xác định hai record có mô tả cùng thực thể hay không. Exact
source ID có precision cao và được ưu tiên. Fuzzy matching chỉ là fallback, trả
confidence và từ chối trường hợp hai candidate có top score bằng nhau. Precision,
Recall và F1 được tính từ TP, FP, FN; accuracy riêng lẻ không phù hợp khi class
phân bố lệch.

## 2.7. Recommendation dựa trên graph

Hai phim có thể tương tự vì chung đạo diễn, diễn viên, thể loại, từ khóa hoặc
studio. Raw overlap thiên về phim có metadata dày và feature phổ biến. Đề tài dùng:

```text
contribution(feature) = type_weight × (1 + ln((N+1)/(df(feature)+1)))
score(source,candidate) = tổng contribution của các feature chung
```

Trong đó `N` là số phim và `df` là số phim liên kết với feature. Feature hiếm có
giá trị phân biệt cao hơn. Đây là item-to-item similarity, không phải xác suất
yêu thích và không phải personalization theo người dùng.

## 2.8. Chỉ số đánh giá

- Data quality: missing, duplicate, invalid edge, orphan và coverage.
- Entity resolution: Precision, Recall, F1.
- Reasoning: precision của fact suy ra và evidence coverage.
- QA: intent accuracy, answer correctness và evidence.
- Recommendation: Precision@K, DCG/NDCG@K, explanation coverage.
- Performance: median, p95 và standard deviation sau warm-up.

## 2.9. Tính đúng, tính đầy đủ và tính nhất quán

Ba khái niệm này cần được phân biệt. **Tính đúng cấu trúc** trả lời liệu node/edge
có tuân theo schema và constraint hay không. **Tính nhất quán ngữ nghĩa** trả lời
liệu một individual có đồng thời thuộc hai class disjoint, hoặc một functional
property có nhiều value xung đột hay không. **Tính đầy đủ** đo mức phủ của dữ liệu
so với yêu cầu, chẳng hạn tỷ lệ phim có cast, director, genre hoặc IMDb rating.

Zero structural violation không chứng minh graph phản ánh hoàn hảo thế giới thật.
Một phim có thể thiếu cast do giới hạn nguồn nhưng vẫn hợp lệ về schema. Ngược
lại, graph có coverage cao vẫn có thể merge sai hai người trùng tên. Vì vậy đề tài
báo cáo đồng thời constraint/validation, coverage và sample review thay vì gộp
tất cả thành một “quality score”.

## 2.10. Idempotency và reproducibility

Idempotency nghĩa là thực hiện cùng một import nhiều lần tạo cùng trạng thái logic,
không nhân đôi node/edge. Reproducibility rộng hơn: người khác phải biết input,
version, configuration, code path và protocol để tái tạo artifact/kết quả. `MERGE`
giải quyết một phần idempotency; checksum, manifest, metadata máy và command
workflow giải quyết reproducibility. Import có thể idempotent nhưng không tái lập
nếu nguồn thay đổi mà không có snapshot/checksum.

# Chương 3. Công trình và nền tảng liên quan

## 3.1. Phương pháp khảo sát

Khảo sát tập trung vào ba cụm: Knowledge Graph construction/entity resolution,
KG question answering và explainable KG recommendation. Từ khóa gồm “knowledge
graph question answering”, “knowledge graph recommender systems”, “explainable
graph recommendation”, “movie knowledge graph recommendation” và “temporal
knowledge graph QA”. Nguồn ưu tiên là W3C, tài liệu chính thức của nền tảng,
proceedings hội nghị, tạp chí peer-reviewed và bản paper của tác giả. Khoảng thời
gian ưu tiên là 2023–2026; nguồn nền tảng cũ hơn chỉ dùng cho định nghĩa chuẩn.

Tiêu chí đưa vào gồm: liên quan trực tiếp tới KGQA/recommendation/construction;
có mô tả phương pháp hoặc evaluation; có metadata xuất bản xác minh được. Bài
blog, trang tổng hợp và nội dung không có phương pháp rõ ràng bị loại khỏi survey
cốt lõi.

## 3.2. Tổng hợp nghiên cứu

Guo và cộng sự khảo sát các hệ gợi ý dựa trên Knowledge Graph, phân loại cách
khai thác graph và nhấn mạnh hai mục tiêu accuracy và explainability [8]. Kết quả
này hỗ trợ quyết định đánh giá đồng thời ranking metric và explanation coverage.
Các nghiên cứu về explainable graph recommendation cho thấy đường/feature graph
có thể cung cấp lý do dễ kiểm tra hơn latent factor [9], [10]. Tuy nhiên, nhiều
phương pháp tối ưu personalization từ user–item interaction hoặc dùng embedding;
đề tài này không có user history nên chỉ tuyên bố item-to-item recommendation.

Các công trình conversational recommendation dùng explicit reasoning chain để
tạo recommendation rationale [11]. Đề tài chia QA và recommendation thành hai
endpoint, nhưng chia sẻ nguyên tắc: mọi kết quả phải có graph evidence. Với miền
phim, các nghiên cứu kết hợp KG với time series hoặc topic model nhằm tăng độ
chính xác [12], [13]. Đây là baseline khái niệm quan trọng, đồng thời chỉ ra giới
hạn của đề tài: chưa mô hình hóa thời gian tương tác hoặc nội dung overview bằng
topic model.

Khảo sát Temporal KGQA năm 2024 phân biệt câu hỏi trên fact thay đổi theo thời
gian với graph tĩnh [14]. Movie KG hiện chỉ lưu `release_date` như datatype
property để filter/sort; nó chưa phải Temporal KG và không hỗ trợ valid time hay
transaction time. BYOKG dùng LLM-backed symbolic agent để khám phá KG chưa thấy,
sinh query-program exemplar và tổng hợp chương trình truy vấn zero-shot [15].
Khác với hướng đó, đề tài cố định schema/operation whitelist để ưu tiên safety và
reproducibility trong phạm vi Movie KG. Vì vậy smoke test 10 câu của đề tài chỉ
được dùng để kiểm tra hệ thống, không gọi là benchmark production.

## 3.3. Khoảng trống và vị trí đề tài

Đề tài không cố cạnh tranh với KGQA/recommender quy mô nghiên cứu. Khoảng trống
được chọn là một workflow học phần nhưng đầu cuối và kiểm chứng được: thu thập
đa nguồn, identity/provenance, hai biểu diễn graph, suy diễn có evidence, API/UI,
test và artifact thực nghiệm. Điểm khác biệt quan trọng là LLM không trực tiếp
sinh Cypher hoặc câu trả lời, recommendation score được giải thích bằng các quan
hệ trong graph, và các kết quả đo đều gắn với snapshot cùng cấu hình cụ thể.

## 3.4. So sánh có cấu trúc các công trình liên quan

| Công trình | Dữ liệu/tín hiệu | Phương pháp | Explanation | Khác biệt với đề tài |
|---|---|---|---|---|
| Guo et al. [8] | nhiều benchmark | survey taxonomy | phân tích nhiều họ | dùng để định vị, không phải baseline chạy |
| Caro-Martínez et al. [9] | interaction graph | link prediction/common neighbors | graph-interpretable | đề tài dùng metadata graph, không user interaction |
| Colas et al. [10] | user–item + item KG | recommendation/NLG | natural-language grounding | đề tài trả evidence xác định, không NLG |
| Ren et al. [11] | conversational recommendation | KG reasoning chain | explicit chain | QA stateless, recommendation tách endpoint |
| Zhang et al. [12] | rating + KG + time series | collaborative filtering | quan hệ KG | không có temporal user signal |
| Saat et al. [13] | MovieLens + topic/metadata | content-based KG | feature/profile | dùng TMDB, không topic model |
| Su et al. [14] | temporal KGQA studies | survey taxonomy | temporal reasoning | release date mới là property |
| Agarwal et al. [15] | unseen/domain KG | LLM program synthesis | query program/path | fixed schema/whitelist compiler |

“Dùng Knowledge Graph” không phải một phương pháp duy nhất. KG có thể là nguồn
side information cho model, không gian reasoning, cấu trúc explanation hoặc
operational database. Trong đề tài, graph đồng thời là operational store và
evidence substrate; model học sâu không trực tiếp quyết định ranking hoặc fact.

## 3.5. Liên hệ survey với quyết định thiết kế

Survey dẫn đến bốn quyết định. Thứ nhất, explainability phải được định nghĩa bằng
evidence có thể kiểm tra, không chỉ text nghe hợp lý. Thứ hai, metric recommendation
phải đi cùng corpus/rubric và K. Thứ ba, QA sinh query tự do có flexibility nhưng
execution risk cao; constrained plan phù hợp phạm vi học phần hơn. Thứ tư, các
phương pháp personalized không được dùng để quảng bá hệ thống không có user profile.

# Chương 4. Phân tích yêu cầu

## 4.1. Stakeholder và use case

- Người dùng cuối hỏi thông tin phim và nhận recommendation có lý do.
- Data engineer thu thập, chuẩn hóa, enrich và import dữ liệu.
- Người vận hành khởi động Neo4j/API và kiểm tra health/stats.
- Người đánh giá chạy test, query, benchmark và truy vết evidence.

## 4.2. Yêu cầu chức năng

| ID | Yêu cầu | Artifact chính |
|---|---|---|
| F01 | Thu thập/cache TMDB | `collect_tmdb.py`, `tmdb_client.py` |
| F02 | Tải/stream IMDb ratings | `download_imdb.py`, `imdb_loader.py` |
| F03 | Clean, normalize, entity resolution | `processing/` |
| F04 | Sinh 5 node CSV + 5 edge CSV + manifest | `pipeline.py` |
| F05 | Import/validate Neo4j idempotent | `load_neo4j.py` |
| F06 | RDF export, entailment, 10 SPARQL | `export_rdf.py`, `semantic_reasoning.py` |
| F07 | 10 Cypher và CRUD parameterized | `cypher/`, `kg/crud.py` |
| F08 | QA answer + evidence | `/ask` |
| F09 | Recommendation + explanation | `/recommend` |
| F10 | Search/stats/health và UI | FastAPI/static UI |

## 4.3. Yêu cầu phi chức năng

Hệ thống phải idempotent, query-safe, có provenance, chạy demo không phụ thuộc
Internet sau import, không commit API key/raw dataset, và có workflow tái lập.
Public API là read-only; CRUD chỉ phục vụ maintenance có kiểm soát. LLM failure
không được làm mất QA fallback hoặc recommendation.

## 4.4. Competency questions

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

## 4.5. Ma trận truy vết competency question

| CQ | Pattern chính | Số bước | Đầu ra/bằng chứng |
|---:|---|---:|---|
| 1 | Person-DIRECTED-Movie | 1 | Movie ID/title, director link |
| 2 | Person-ACTED_IN-Movie | 1 | Person và edge metadata |
| 3 | Person-ACTED_IN-Movie-ACTED_IN-Person | 2 | shared Movie |
| 4 | Movie-HAS_GENRE-Genre + rating | 1 + filter | Movie/rating/genre |
| 5 | Person-CO_STARRED_WITH-Person | derived | count/evidence IDs |
| 6 | Person-DIRECTED-Movie-HAS_GENRE-Genre | 2 + aggregate | director/count |
| 7 | variable path giữa Person | tối đa 8 edge | node/relationship path |
| 8 | Movie-feature-Movie | 2 mỗi feature | contribution/feature |
| 9 | scan label | 0 | count theo label |
| 10 | CO_STARRED_WITH | derived audit | pair/count/evidence IDs |

Ma trận là cầu nối giữa yêu cầu, schema, query catalog, API và test. Class hoặc
relationship không hỗ trợ competency question nào cần được cân nhắc loại khỏi
MVP; một CQ không ánh xạ được query chỉ ra thiếu sót thiết kế.

## 4.6. Acceptance criteria

Dataset phải đạt ít nhất 2.000 Movie; import hai lần không đổi counts; validation
không có violation chưa giải thích; catalog Cypher/SPARQL phải parse/chạy; API trả
schema hợp lệ; recommendation trả explanation; evaluation ghi backend, corpus và
protocol; integration test phải kết nối Neo4j test riêng thay vì skip do graph
demo có dữ liệu.

# Chương 5. Thiết kế ontology và graph schema

## 5.1. Các lớp và định danh

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

## 5.2. Relationship

| Relationship | Hướng | Property |
|---|---|---|
| ACTED_IN | Person → Movie | character, cast_order, source |
| DIRECTED | Person → Movie | source |
| HAS_GENRE | Movie → Genre | source |
| HAS_KEYWORD | Movie → Keyword | source |
| PRODUCED_BY | Movie → Studio | source |
| CO_STARRED_WITH | Person → Person | movie_count, evidence_movie_ids, derived |

## 5.3. Ontology RDF/OWL

Ontology khai báo năm class disjoint, object property với domain/range, inverse
`actedIn/hasActor`, inverse `directed/directedBy`, symmetric `coStarredWith`, và
functional `tmdbId/imdbId`. Datatype property mô tả title, ratings, votes và name.
Functional property không đồng nghĩa global inverse-functional identity; stable
URI vẫn được tạo từ source ID.

## 5.4. Ánh xạ RDF–Neo4j

| Neo4j | RDF/OWL |
|---|---|
| `(:Movie {tmdb_id})` | `:movie/<id> a :Movie; :tmdbId ...` |
| `(:Person)-[:ACTED_IN]->(:Movie)` | `:person/... :actedIn :movie/...` |
| `[:DIRECTED]` | `:directed` / inverse `:directedBy` |
| edge property | cần reification/RDF-star nếu xuất đầy đủ |
| constraint | ontology axiom + validation đóng |

## 5.5. Các quyết định mô hình hóa

### Một Person label thay vì Actor/Director

Nếu dùng hai label loại trừ nhau, người vừa diễn vừa đạo diễn phải duplicate node
hoặc mang hai label không phản ánh role theo từng phim. Một `Person` và role trên
relationship tránh hai vấn đề này. Query “phim của một người” có thể match
`ACTED_IN|DIRECTED`, còn query chuyên biệt vẫn chọn đúng type.

### Source ID thay cho name

Tên không ổn định và không duy nhất. Source ID được dùng làm constraint key; name
là thuộc tính hiển thị/tìm kiếm. Fuzzy matching chỉ liên kết input người dùng tới
entity đã có, không thay stable identity trong storage.

### Tách TMDB và IMDb rating

Hai rating có population và thời điểm cập nhật khác nhau. Gộp vào một property sẽ
mất provenance. Vì vậy `rating`, `imdb_rating`, `imdb_votes` được giữ riêng. Khi
QA cần một rating ưu tiên, compiler dùng `coalesce(imdb_rating,rating)` theo quyết
định công khai.

### Materialize co-star

Co-star có thể tính tại query time nhưng được dùng thường xuyên và cần audit.
Materialization lưu aggregate/evidence và minh họa derived fact. Chi phí là phải
recompute sau authoritative import; runtime preparation xử lý phụ thuộc này.

## 5.6. Provenance

Provenance có ba mức. Mức source: node/edge gốc có `source=tmdb`, Movie giữ IMDb
ID và ratings riêng. Mức snapshot: manifest giữ path/checksum/count và match
method. Mức derivation: `CO_STARRED_WITH` giữ `derived`, count và supporting
movie IDs. RDF export chưa dùng named graph đầy đủ cho từng nguồn; đây là giới
hạn thay vì một claim provenance chuẩn hóa toàn diện.

## 5.7. Từ điển dữ liệu và quy tắc miền

| Trường | Kiểu/miền | Bắt buộc | Nguồn | Quy tắc và<br>ý nghĩa |
|---|---|---|---|---|
| Movie.tmdb_id | integer dương | có | TMDB | khóa ổn định, duy nhất trong Movie |
| Movie.imdb_id | chuỗi `tt...` | không | TMDB external ID | khóa nối chính xác sang IMDb |
| Movie.title | Unicode string | có | TMDB | trim whitespace, không được rỗng |
| `Movie.`<br>`release_date` | ISO date | không | TMDB | ngày phát hành, không phải valid-time của temporal KG |
| Movie.rating | số 0–10 | không | TMDB | giữ riêng với IMDb rating |
| `Movie.`<br>`imdb_rating` | số 0–10 | không | IMDb | chỉ ghi khi exact `imdb_id` match |
| `Movie.`<br>`imdb_votes` | integer không âm | không | IMDb | số phiếu tại snapshot thu thập |
| `Person.`<br>`person_id` | source-qualified ID | có | TMDB/<br>pipeline | identity key, không dùng tên làm khóa |
| `ACTED_IN.`<br>`character` | string | không | TMDB credits | vai diễn được công bố ở nguồn |
| `ACTED_IN.`<br>`cast_order` | integer không âm | không | TMDB credits | thứ tự cast, không phải độ quan trọng tuyệt đối |
| `CO_STARRED_WITH.`<br>`movie_count` | integer dương | có | luật | số phim chung hỗ trợ fact suy ra |
| `CO_STARRED_WITH.`<br>`evidence_`<br>`movie_ids` | danh sách ID | có | luật | đường truy vết về các Movie tiền đề |

Các miền giá trị được kiểm tra ở pipeline/validation thay vì xem OWL là cơ chế
kiểm tra dữ liệu đóng. Required field là yêu cầu của ứng dụng; functional và
disjoint axiom là yêu cầu ngữ nghĩa; constraint Neo4j bảo vệ identity/storage.
Ba lớp ràng buộc bổ sung cho nhau nhưng không được đánh đồng.

# Chương 6. Kiến trúc và pipeline dữ liệu

## 6.1. Kiến trúc tổng thể

```text
TMDB API/cache ─┐
                ├→ clean/normalize/exact-ID enrich → CSV + manifest
IMDb ratings.gz ┘                         ├→ Neo4j → QA/recommend → FastAPI/UI
                                         └→ RDF → entailment → SPARQL
```

Qwen là service tùy chọn tại localhost, chỉ nhận câu hỏi và trả QueryPlan JSON.
Neo4j luôn là nguồn dữ liệu/câu trả lời của runtime.

## 6.2. Thu thập TMDB

Collector duyệt popular pages đến khi đủ số movie ID duy nhất, sau đó tải detail,
credits, keywords và external IDs theo TMDB API [6]. Response được cache nguyên dạng; request có
timeout, retry và interval. Cache giúp chạy lại không tiêu tốn API quota và giữ
snapshot nguồn cho reproducibility.

## 6.3. Tích hợp IMDb

Pipeline chỉ tải `title.ratings.tsv.gz` từ bộ dữ liệu phi thương mại IMDb [7], kiểm tra gzip/checksum và ghi metadata.
File được stream từng dòng, chỉ giữ record có `tconst` thuộc tập IMDb ID của 2.000
phim TMDB. Cách này không giải nén toàn bộ và không nạp IMDb đầy đủ vào RAM/Neo4j.
`Movie.rating` và `Movie.imdb_rating` không ghi đè nhau.

## 6.4. Quản trị nguồn, điều khoản sử dụng và đạo đức dữ liệu

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
Sampling theo popular pages có popularity bias; giới hạn cast tạo coverage bias.
Hai bias này được công bố để tránh suy rộng kết quả sang toàn bộ điện ảnh hoặc
mọi nhóm người dùng.

## 6.5. Cleaning và entity resolution

Cleaning chuẩn hóa Unicode/whitespace, kiểu số/ngày và trường bắt buộc. Duplicate
TMDB ID bị loại và log. Exact TMDB/IMDb ID được ưu tiên; fuzzy name fallback dùng
threshold và từ chối tied top score. Ambiguous case không được tự động merge.

## 6.6. Normalized artifacts và manifest

Pipeline tạo `movies.csv`, `people.csv`, `genres.csv`, `keywords.csv`,
`studios.csv` và năm edge CSV. Manifest ghi source checksum, thời điểm tạo, counts,
IMDb coverage/match, invalid record, duplicate/missing rate và coverage cast,
director, genre. Raw, interim và processed data được tách để tránh nhầm nguồn với
artifact dẫn xuất.

## 6.7. Import và validation Neo4j

Thứ tự import là constraint/index → node → edge → reasoning → validation. Mỗi
batch dùng parameterized `UNWIND`; `MERGE` trên stable key giúp import lặp không
tạo duplicate. `--replace` dành cho authoritative rebuild. Validation kiểm tra:

- orphan Movie;
- duplicate stable IDs;
- missing required property;
- invalid relationship type;
- endpoint/hướng sai schema;
- `CO_STARRED_WITH` không còn supporting movie.

Integration test dùng Neo4j test riêng ở cổng 7688 với storage tạm, import hai lần
và kiểm tra QA, recommendation, CRUD; graph demo không bị reset.

## 6.8. Thuật toán pipeline

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
2.000–5.000 phim. Cast limit kiểm soát kích thước nhưng đồng thời tạo coverage bias.

## 6.9. Xử lý lỗi

Downloader dùng file `.part`, chỉ rename sau khi gzip hợp lệ để tránh coi partial
download là hoàn chỉnh. Collector retry lỗi tạm thời và cache response. Pipeline
fail rõ nếu IMDb path được chỉ định nhưng không tồn tại. Runtime không tự dùng seed
khi thiếu data thật; nó dừng và yêu cầu chuẩn bị dataset. Cách fail closed tránh
demo vô tình chạy fixture rồi báo như corpus thật.

## 6.10. Tái lập và thay đổi nguồn

TMDB/IMDb là nguồn động, nên chạy lại ngày khác có thể tạo snapshot khác.
Reproducibility ở đây là tái lập workflow và truy vết snapshot, không cam kết API
luôn trả byte giống nhau. Raw cache/checksum cho phép chạy transform trên snapshot
cũ. Nếu data thay đổi, evaluation/benchmark phải chạy lại cùng snapshot.

# Chương 7. Truy vấn, suy diễn và semantic workflow

## 7.1. Cypher catalog và CRUD

Catalog có 10 query từ lookup đến shortest path, aggregation và kiểm tra fact suy
ra. CRUD Movie gồm create/upsert, read neighborhood, update metadata, guarded
delete và upsert `ACTED_IN`; mọi value là parameter. CRUD không mở qua public API.

## 7.2. Suy diễn `CO_STARRED_WITH`

Luật:

```text
Person A -[:ACTED_IN]-> Movie <-[:ACTED_IN]- Person B
⇒ A -[:CO_STARRED_WITH]-> B
```

Điều kiện sắp thứ tự ID tránh cặp trùng/ngược. Relationship lưu `movie_count`,
`evidence_movie_ids` và `derived=true`. `MERGE` bảo đảm materialization idempotent.
Đây là rule nghiệp vụ bằng Cypher, không được gọi là OWL reasoning.

## 7.3. Semantic entailment

RDFLib materializer chạy profile RDFS/OWL-RL subset xác định:

- property domain → type của subject;
- property range → type của object;
- `owl:inverseOf` → inverse triple;
- `owl:SymmetricProperty` → triple chiều ngược.

Validator kiểm tra functional property, disjoint class và Movie thiếu title. Báo
cáo ghi số triple trước/sau, số triple mới và violation. Profile này chạy được và
test được, nhưng không thay thế OWL 2 DL reasoner đầy đủ.

## 7.4. SPARQL

Mười query bao phủ phim theo đạo diễn, cast, shared genre, co-star aggregation,
director–genre multi-hop, OPTIONAL IMDb enrichment, inverse `hasActor`, semantic
path, ASK quality và CONSTRUCT recommendation evidence. Loader bắt buộc đúng 10
query, parse rồi chạy từng query trên graph đã materialize.

## 7.5. An toàn truy vấn

An toàn có nhiều tầng. Pydantic giới hạn request length/type; QueryPlan giới hạn
operation/target/filter; compiler ánh xạ enum sang fragment do ứng dụng sở hữu;
entity value nằm trong Neo4j parameter; public API không có write operation. Chỉ
dynamic label trong entity-link fallback được lấy từ enum nội bộ, không từ raw
user input. LLM error hoặc JSON sai bị bắt và fallback về parser.

Parameterized query ngăn injection qua value nhưng không tự ngăn query đắt. Vì
vậy compiler còn áp `limit≤50`, shortest-path depth `≤8`, fixed pattern và không
cho arbitrary Cypher. Query safety không thể chỉ mô tả bằng một câu “đã dùng
parameter”.

## 7.6. Hai loại suy diễn

| Thuộc tính | Semantic entailment | Business rule |
|---|---|---|
| Engine | RDFLib materializer | Neo4j/Cypher |
| Ví dụ | `actedIn` → inverse `hasActor` | shared Movie → co-star |
| Cơ sở | ontology axiom | domain-specific rule |
| Output | inferred RDF triple | materialized relationship |
| Validation | functional/disjoint/required | supporting movie audit |

Có ontology file không đồng nghĩa hệ thống tự động chạy OWL reasoning; ngược lại,
Cypher materialization sinh tri thức mới nhưng không phải OWL entailment.

# Chương 8. Ứng dụng

## 8.1. Hỏi–đáp

```text
Question → Qwen QueryPlan hoặc parser fallback → entity linking
         → whitelist compiler/catalog → parameterized Cypher
         → Neo4j → answer + evidence + latency
```

QueryPlan giới hạn operation, target, entity type, filter field/operator, sort và
limit bằng Pydantic JSON Schema. Qwen không sinh Cypher và không trả lời bằng kiến
thức riêng. Entity linker canonicalize tên trước query và trả confidence trong
evidence. Compiler chỉ phát sinh graph pattern đã whitelist; user input luôn nằm
trong parameter. Khi không có LLM, parser deterministic hỗ trợ chín intent.

## 8.2. Recommendation

Neo4j tạo candidate bằng các phim chia sẻ ít nhất một director, actor, keyword,
genre hoặc studio. Mỗi feature được tính document frequency trong graph và đóng
góp IDF theo type weight. Query trả candidate, score và feature chung; Python chỉ
định dạng `Recommendation` và explanation. Tie-break theo title giúp kết quả xác
định. Endpoint nhận `movie_id` thay vì title để tránh nhập nhằng.

## 8.3. API và UI

| Endpoint | Chức năng |
|---|---|
| GET `/health` | kiểm tra Neo4j connectivity |
| GET `/stats` | số node theo label và tổng relationship |
| GET `/entities/search` | full-text rồi fallback parameterized search |
| POST `/ask` | QA answer, intent, evidence, query time |
| POST `/recommend` | top-K recommendation và explanation |

UI có hai tab QA và recommendation, autocomplete phim, lịch sử hiển thị và state
loading/error/success. Lịch sử chỉ ở frontend; backend hiện stateless.

## 8.4. An toàn và vận hành

Secret nằm trong `.env`; raw data không commit. LLM endpoint bind localhost;
remote demo dùng SSH tunnel. Public API không có write endpoint. Hạn chế hiện tại
là chưa có authentication/rate limiting, nên cấu hình phù hợp demo local chứ
không phải public production deployment.

## 8.5. Failure modes

| Tình huống | Hành vi |
|---|---|
| LLM chưa cấu hình | dùng parser 9 intent |
| LLM timeout/JSON sai | fallback parser |
| confidence thấp/thiếu slot | trả clarification |
| entity không tồn tại | trả entity-not-found/không tìm thấy |
| movie ID recommend sai | HTTP 404 |
| Neo4j không sẵn sàng | health 503 |
| tên fuzzy nhập nhằng | không tự chọn tied candidate |

Failure behavior là một phần correctness. Hệ QA an toàn nên thừa nhận không biết
hoặc yêu cầu làm rõ thay vì chạy query với entity đoán sai.

## 8.6. Tính faithful của explanation

QA evidence gồm canonical entity/link confidence và record/path trả từ Neo4j.
Recommendation explanation không được model sinh: nó tổng hợp từ shared feature
đã đóng góp score. Cách làm giảm độ tự nhiên so với NLG explanation [10] nhưng
có tính faithful cao trong phạm vi hệ thống: mỗi lý do tương ứng quan hệ tồn tại
trong graph và contribution xác định.

# Chương 9. Thực nghiệm và kết quả

## 9.1. Cách đọc kết quả

Các kết quả dưới đây được ghi kèm backend, số lượng phim, số case, K, số lần lặp
và cấu hình cần thiết. Các bộ kiểm thử do nhóm chuẩn bị nhằm kiểm tra hệ thống
trên snapshot hiện tại; số liệu QA và hiệu năng được lấy từ Neo4j thực tế.

## 9.2. Dataset và graph

Snapshot đầu vào có 2.001 record; pipeline loại minh bạch một Movie không có bất
kỳ quan hệ graph nào và giữ đúng 2.000 Movie hợp lệ. Exact IMDb ratings match
1.783/1.855 phim có IMDb ID. Graph sau reasoning có 37.349 node và 353.915
relationship, với zero
orphan, duplicate stable ID, missing required property và invalid relationship.

Các số liệu này lấy từ `data/processed/manifest.json` và
`experiments/results/neo4j_validation.json` của cùng source checksum
`eeeb7e27...2c800`.

| Chỉ số snapshot/graph | Giá trị cuối |
|---|---:|
| Record TMDB đầu vào | 2.001 |
| Movie hợp lệ sau quality gate | 2.000 |
| Movie bị loại do không có quan hệ | 1 |
| Movie có IMDb ID | 1.855 (92,75%) |
| IMDb rating exact-match | 1.783/1.855 (96,12%) |
| Movie có cast | 99,00% |
| Movie có director | 99,30% |
| Movie có genre | 98,60% |
| Orphan/duplicate/missing/invalid/unsupported fact sau import | 0 |

Quality gate không xóa im lặng record lỗi: Movie bị loại được ghi trong
`invalid_records` với `reason=no_graph_relationships` và source row/TMDB ID, nhờ
đó tổng đầu vào, tổng hợp lệ và lý do chênh lệch vẫn truy vết được.

## 9.3. Entity resolution

Corpus kiểm thử gồm 100 case: 75 positive và 25 negative, có source ID/evidence.
Kết quả là TP=75, TN=25, FP=0, FN=0, do đó precision, recall và F1 đều bằng 1,00.
Kết quả cho thấy workflow xử lý đúng bộ case hiện tại; các trường hợp tên trùng,
alias hoặc dữ liệu thiếu vẫn cần được bổ sung khi mở rộng hệ thống.

## 9.4. Reasoning

Năm mươi fact `CO_STARRED_WITH` được kiểm tra bằng supporting movie và
source cast; 50/50 fact hợp lệ, precision bằng 1,00. Validation bổ sung còn kiểm
tra mọi derived edge phải có ít nhất một shared Movie. Semantic workflow trên
full normalized snapshot materialize 35.419 triple, tăng từ 154.970 lên 190.389
triple và không có semantic violation. RDF export dùng chính processed snapshot
2.000 Movie như Neo4j; cả 10 SPARQL query đều parse và thực thi thành công.

## 9.5. QA

Corpus deterministic gồm 20 câu phủ chín intent, yêu cầu đúng intent, nội dung
mong đợi và tối thiểu một evidence record (riêng top-5 yêu cầu đủ năm evidence).
Production path trên Neo4j đạt 20/20. Rubric shortest-path chấp nhận mọi đường hợp
lệ thay vì khóa vào một intermediate; recommendation question kiểm tra contract
và evidence, còn chất lượng ranking được chấm riêng bằng P@10/NDCG@10. Đây vẫn là
bộ kiểm thử chức năng do nhóm xây dựng và có thể mở rộng thêm paraphrase hoặc câu
mơ hồ trong các phiên bản sau.

## 9.6. Recommendation

| Phương pháp | P@10 | NDCG@10 | Vai trò |
|---|---:|---:|---|
| Overlap | 0,670 | 0,723 | baseline lịch sử |
| Weighted Jaccard | 0,640 | 0,699 | baseline lịch sử |
| Hybrid | 0,590 | 0,657 | baseline lịch sử |
| IDF-weighted graph | **0,715** | **0,754** | production Neo4j |

IDF đạt kết quả tốt nhất trên 20 case kiểm thử và mọi recommendation có explanation.
Tuy nhiên, corpus nhỏ và relevance rubric dựa trên metadata graph; kết quả không
đồng nghĩa người dùng thực sẽ ưa thích recommendation.

## 9.7. Hiệu năng

Benchmark Neo4j 5.26.28 chạy trên 2.000 Movie, một warm-up và 100 lần/câu. Median
theo intent nằm trong 2,67–188,74 ms; p95 nằm trong 5,08–211,24 ms. Similar-movie
query chậm nhất do candidate traversal và aggregation feature; genre/rating nhanh
nhất. Kết quả mô tả workload và máy đo, chưa chứng minh scalability.

SQLite baseline dùng cùng normalized snapshot cho bốn query tương đương. So sánh
chỉ hợp lệ nếu chạy cùng máy, snapshot, warm-up và iterations. SQLite là baseline
kiểm soát, không đại diện cho mọi RDBMS; mục tiêu là thảo luận trade-off, không
chứng minh graph luôn nhanh hơn relational.

| Intent tương đương | Neo4j median (ms) | Neo4j p95 (ms) | SQLite median (ms) | SQLite p95 (ms) |
|---|---:|---:|---:|---:|
| movies_by_director | 10,086 | 16,557 | 1,050 | 1,644 |
| common_movies | 38,324 | 48,326 | 12,041 | 13,070 |
| movies_by_genre_rating | 2,667 | 5,085 | 0,814 | 0,835 |
| directors_by_genre | 4,545 | 6,639 | 2,119 | 2,198 |

SQLite nhanh hơn trong bốn query kiểm soát này. Kết quả là bằng chứng chống lại
tuyên bố đơn giản “graph luôn nhanh hơn SQL”; lợi ích chính của Neo4j trong đề tài
là mô hình traversal/evidence và một execution surface thống nhất, không phải ưu
thế latency phổ quát.

## 9.8. Threats to validity

- Popular-movie sampling tạo selection bias.
- Top-20 cast bỏ diễn viên phụ.
- Nguồn TMDB thay đổi theo thời gian; cache chỉ cố định một snapshot.
- IMDb chỉ enrich Movie, chưa link Person.
- Các bộ case đánh giá do nhóm xây dựng và còn nhỏ.
- QA corpus deterministic 20 câu chưa phủ paraphrase rộng.
- Recommendation không có user interaction, nên không đánh giá personalization.
- Benchmark chỉ một quy mô Neo4j và phụ thuộc phần cứng/cache.

## 9.9. Trả lời câu hỏi nghiên cứu

**RQ1:** Stable source ID và exact IMDb join tích hợp hai nguồn mà không ghi đè
rating; checksum/manifest cung cấp provenance ở mức snapshot.  
**RQ2:** Mười competency question được biểu diễn bằng pattern trực tiếp, multi-hop,
aggregation và shortest path; evidence là node/relationship thực thi.  
**RQ3:** Cypher rule tạo co-star có supporting movie; semantic profile tạo inverse
và type entailment, đồng thời validator phát hiện conflict.  
**RQ4:** IDF giảm ảnh hưởng feature phổ biến, đạt P@10/NDCG@10 cao hơn ba baseline
trên corpus kiểm thử và giữ explanation coverage.
**RQ5:** Hệ thống đạt mục tiêu demo và khả năng chạy lại ở 2.000 phim; phạm vi
hiện tại chưa gồm cá nhân hóa hoặc benchmark nhiều quy mô.

## 9.10. Protocol tái chạy thực nghiệm

1. Cố định raw snapshot và ghi checksum.
2. Transform/import authoritative, chạy validation và lưu counts.
3. Chạy reasoning trước evaluation phụ thuộc derived edges.
4. Chạy corpus bằng đúng backend được khai báo.
5. Benchmark một warm-up, 100 iterations/query; không chạy workload khác song song.
6. Lưu Python/Neo4j/platform/movie count trong metadata.
7. Sinh bảng/biểu đồ từ JSON/CSV artifact, không nhập số bằng tay.
8. Kiểm tra report/slide dùng cùng artifact version.

Với relational baseline, snapshot và máy phải giống Neo4j run. Nếu không đáp ứng,
kết quả chỉ được báo riêng, không dùng để xếp hạng engine.

## 9.11. Kiểm thử và quy trình chạy

Lần chạy cuối của `make test` đạt 30/30 test. Bộ test gồm unit test cho cleaning,
entity resolution, query planning/compiler, RDF export, semantic materialization,
SPARQL catalog, CRUD, relational benchmark và evidence summary. Integration test
dùng Neo4j riêng ở Bolt 7688, thực hiện import hai lần để xác nhận idempotency,
sau đó kiểm tra QA, recommendation và vòng đời CRUD trước khi dọn graph test.

Docker healthcheck gọi `cypher-shell RETURN 1`, nên trạng thái healthy chỉ được
báo sau khi Bolt thực sự nhận query; điều này loại race condition trong đó
container đã chạy nhưng driver chưa handshake được. Quy trình còn chạy
`compileall`, kiểm tra dependency và xác minh checksum của tài liệu nguồn.

## 9.12. Phân tích lỗi và hướng khắc phục

### QA

Rubric cũ khóa shortest path vào một intermediate và đã được thay bằng yêu cầu
đúng intent, có đường/evidence hợp lệ. Recommendation question chỉ kiểm tra API
contract; relevance dùng corpus P@10/NDCG@10 riêng. Bước tiếp theo là bổ sung
paraphrase, câu mơ hồ và expected abstention thay vì chỉ dùng các câu gần template.

### Entity resolution

Corpus exact-ID dễ hơn dữ liệu mention thực tế. Cần bổ sung hard negative cùng tên,
alias, Unicode, tên đảo, thiếu ID và candidate tie. Từng error phải phân loại false
merge hoặc missed match vì false merge gây ô nhiễm graph nghiêm trọng hơn.

### Recommendation

IDF có thể ưu tiên feature quá hiếm do metadata noise. Có thể đặt minimum document
frequency hoặc review contribution distribution. Tuy nhiên thay đổi trọng số phải
đánh giá trên corpus tách biệt, không điều chỉnh trực tiếp theo 20 case rồi báo
trên chính các case đó.

### Performance

Similar-movie chậm nhất gợi ý cần inspect query plan, cardinality và index; nhưng
index không giúp mọi traversal. Cần đo cold/warm cache riêng, nhiều scale thật và
ghi concurrency trước khi tối ưu.

# Chương 10. Kết luận và hướng phát triển

Đề tài đã xây dựng một Movie Knowledge Graph đầu cuối từ thu thập dữ liệu đến hai
ứng dụng. Neo4j phục vụ operational traversal; RDF/OWL cung cấp semantic standards
view. Stable ID, provenance, safe query compiler, evidence-backed inference và
explainable recommendation giúp kết quả không chỉ chạy được mà còn kiểm tra được.

Hạn chế chính nằm ở coverage dữ liệu, phạm vi QA và quy mô benchmark. Thứ tự phát
triển hợp lý là: xây QA corpus lớn hơn; benchmark nhiều snapshot thật; cải thiện
ambiguity handling; sau đó mới mở rộng Wikidata/Award, temporal graph, vector
retrieval, GraphRAG hoặc graph embedding. Mọi mở rộng phải giữ nguyên nguyên tắc: model lập kế hoạch,
compiler kiểm soát execution, graph cung cấp fact và evidence.

# Tài liệu tham khảo sơ bộ

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

> Trước khi xuất bản cuối, chuẩn hóa ngày truy cập và URL cho [1]–[7], kiểm tra
> lại page range của [8], [11] và [12] theo metadata nhà xuất bản, và dùng một
> công cụ quản lý tài liệu tham khảo để tránh sửa số citation thủ công.

# Phụ lục A. Hướng dẫn cài đặt và chạy chương trình

Môi trường yêu cầu Python 3.11 trở lên, Docker và Docker Compose. Các biến cấu
hình được khai báo trong `.env`; khóa `TMDB_API_KEY` chỉ cần thiết khi thu thập
lại dữ liệu. Quy trình chạy cơ bản như sau:

```bash
make setup
make data DATA_COUNT=2000
make run
```

Sau khi khởi động, giao diện web có tại `http://localhost:8000/` và tài liệu API
Swagger có tại `http://localhost:8000/docs`. Các lệnh kiểm tra và thực nghiệm:

```bash
make test
make experiments
make semantic-reasoning
make sparql-check
make neo4j-benchmark
make relational-benchmark
make evidence-summary
```

`make run` sử dụng manifest để chỉ import lại khi snapshot hoặc số lượng Movie
thay đổi. Dữ liệu Neo4j kiểm thử chạy ở Bolt 7688 và tách biệt với graph demo.

# Phụ lục B. API và ví dụ sử dụng

| Phương thức | Endpoint | Chức năng |
|---|---|---|
| `GET` | `/health` | Kiểm tra kết nối Knowledge Graph |
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

Mỗi recommendation trả `movie_id`, `title`, `score`, các feature chung theo từng
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

| Đường dẫn | Nội dung |
|---|---|
| `data/processed/`<br>`manifest.json` | Checksum nguồn, số lượng bản ghi và chỉ số chất lượng dữ liệu |
| `data/processed/`<br>`*.csv` | Năm bảng node và năm bảng relationship đã chuẩn hóa |
| `data/processed/`<br>`movies.ttl` | RDF export từ processed snapshot |
| `data/processed/`<br>`movies.inferred.ttl` | RDF sau semantic materialization |
| `experiments/results/`<br>`neo4j_validation.json` | Kết quả kiểm tra cấu trúc graph |
| `experiments/results/`<br>`qa_neo4j.json` | Kết quả bộ câu hỏi QA trên Neo4j |
| `experiments/results/`<br>`recommendation.json` | P@10 và NDCG@10 của recommendation |
| `experiments/results/`<br>`neo4j_benchmark.csv` | Median, p95 và độ lệch chuẩn theo truy vấn |
| `experiments/results/`<br>`relational_benchmark.csv` | Baseline SQLite trên cùng processed snapshot |

Snapshot hiện tại gồm 2.000 Movie, 24.661 Person, 19 Genre, 7.916 Keyword và
2.753 Studio. Các artifact thực nghiệm được lưu dưới CSV hoặc JSON để có thể kiểm
tra lại số liệu và tái tạo bảng, biểu đồ trong Chương 9.
