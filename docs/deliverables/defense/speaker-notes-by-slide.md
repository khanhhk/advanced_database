# Nội dung thuyết trình theo từng slide

Tài liệu này bám theo `movie_knowledge_graph_defense.pptx` gồm **31 slide,
không có phụ lục**. Phần **Có thể nói gần như nguyên văn** là kịch bản chính;
**Cần chỉ vào** và **Chuyển ý** hỗ trợ thao tác trình bày.

Tổng thời gian gợi ý: 21–27 phút. Nếu chỉ có 15–18 phút, nói ngắn slide 8, 13,
15, 24 và 27; không cần xóa chúng vì các slide này hữu ích khi phản biện.

## Slide 1 — Knowledge Graph: Nền tảng lý thuyết

**Mục tiêu:** giới thiệu phạm vi bài nói.

**Có thể nói gần như nguyên văn:**

> Kính thưa thầy, đề tài của em tập trung vào nền tảng Knowledge Graph theo mô
> hình Property Graph. Em sẽ lần lượt trình bày thực thể, quan hệ, schema,
> identity, traversal, truy vấn và suy diễn. Movie Knowledge Graph được dùng như
> một nghiên cứu tình huống xuyên suốt để cho thấy các khái niệm đó được mô hình
> hóa và kiểm chứng. Chi tiết source code, API và vận hành nằm trong báo cáo;
> trên slide em tập trung vào khái niệm và bằng chứng.

**Cần chỉ vào:** tiêu đề và sơ đồ Movie Knowledge Graph.

**Chuyển ý:** “Trước hết, khi nào dữ liệu trở thành tri thức?”

## Slide 2 — Từ dữ liệu đến tri thức

**Mục tiêu:** phân biệt data, information, knowledge và inference.

**Có thể nói gần như nguyên văn:**

> Dữ liệu là các giá trị rời rạc như 2010, Inception và Nolan. Khi thêm ngữ
> cảnh, ta có thông tin: Inception phát hành năm 2010. Khi nối các thực thể bằng
> quan hệ có nghĩa, ta có tri thức: Nolan đạo diễn Inception. Khi có schema và
> quy tắc, hệ thống có thể suy ra fact mới. Suy luận ở đây không phải tự hiểu vô
> hạn; mọi kết luận đều phụ thuộc vào fact và luật đã khai báo.

**Cần chỉ vào:** bốn bậc từ trái sang phải.

**Chuyển ý:** “Một Knowledge Graph cụ thể được cấu tạo như thế nào?”

## Slide 3 — Knowledge Graph là gì?

**Mục tiêu:** giải thích entity, relationship, property và identifier.

**Có thể nói gần như nguyên văn:**

> Trong phạm vi dự án, Knowledge Graph là một đồ thị gồm các thực thể có định
> danh, các quan hệ mang ngữ nghĩa và schema để máy diễn giải. Ví dụ Nolan và
> Inception là hai entity; DIRECTED là relationship. Property bổ sung mô tả như
> tên, ngày phát hành hoặc rating. Identifier khác name: tên dùng để hiển thị,
> còn identifier dùng để xác định identity. Hai người có thể trùng tên và một
> phim có thể có nhiều cách viết.

**Cần chỉ vào:** Nolan → DIRECTED → Inception và ba khối bên phải.

**Chuyển ý:** “Để fact không được tạo tùy ý, ta cần schema.”

## Slide 4 — Schema và instance

**Mục tiêu:** phân biệt lớp khái niệm và dữ liệu cụ thể.

**Có thể nói gần như nguyên văn:**

> Schema, hay TBox theo cách gọi khái niệm, mô tả các lớp và loại quan hệ được
> phép: Person có thể DIRECTED một Movie. Instance, hay ABox, chứa các cá thể và
> fact cụ thể: Nolan là Person, Inception là Movie và Nolan DIRECTED Inception.
> Schema trả lời dữ liệu có hình dạng nào; instance trả lời fact nào đang tồn
> tại. Dự án không chạy hai hệ TBox/ABox riêng, đây là cách phân biệt mức mô
> hình và mức dữ liệu.

**Cần chỉ vào:** schema bên trái, instance bên phải.

**Chuyển ý:** “Project hiện thực hóa hai lớp này bằng Property Graph.”

## Slide 5 — Property Graph

**Mục tiêu:** giải thích mô hình graph duy nhất của dự án.

**Có thể nói gần như nguyên văn:**

> Neo4j Property Graph gồm node có label và property, relationship có loại,
> hướng và cũng có property. Ví dụ ACTED_IN nối Person tới Movie và giữ
> character, cast_order. Các thuộc tính này mô tả lần tham gia cụ thể nên đặt
> trên cạnh hợp lý hơn đặt trên Person hoặc Movie. Project chỉ triển khai
> Property Graph, không có nhánh RDF hay một graph engine thứ hai.

**Cần chỉ vào:** hai node và property trên cạnh ACTED_IN.

**Chuyển ý:** “Từ node và cạnh, ta hình thành các cấu trúc lớn hơn.”

## Slide 6 — Neighborhood, path và subgraph

**Mục tiêu:** giới thiệu ba đơn vị cấu trúc của tư duy đồ thị.

**Có thể nói gần như nguyên văn:**

> Neighborhood là tập node lân cận một node qua các quan hệ được chọn. Path là
> dãy node và cạnh nối hai thực thể; độ dài path được đo bằng số cạnh. Subgraph
> là phần đồ thị liên quan được lấy ra theo một phạm vi nhất định. Trong dự án,
> neighborhood hỗ trợ tìm phim tương tự, path hỗ trợ truy vấn nhiều bước và
> subgraph giúp giữ đúng ngữ cảnh dùng làm evidence hoặc snapshot đánh giá.

**Cần chỉ vào:** ba khối Neighborhood, Path, Subgraph.

**Chuyển ý:** “Nhưng có graph chưa đủ để gọi là Knowledge Graph hữu dụng.”

## Slide 7 — Bốn điều kiện của Knowledge Graph hữu dụng

**Mục tiêu:** trình bày identity, schema, provenance và competency questions.

**Có thể nói gần như nguyên văn:**

> Một Knowledge Graph hữu dụng cần ít nhất bốn yếu tố. Identity giúp biết chính
> xác đang nói về thực thể nào. Schema tạo ngôn ngữ chung cho fact. Provenance
> cho biết fact đến từ nguồn hoặc luật nào. Competency question xác định graph
> phải trả lời được câu hỏi gì. Nếu thiếu identity thì node dễ bị gộp sai; thiếu
> schema thì quan hệ thiếu nhất quán; thiếu provenance thì không kiểm chứng
> được; thiếu competency question thì có thể xây rất nhiều dữ liệu nhưng không
> phục vụ mục tiêu.

**Cần chỉ vào:** lần lượt bốn thẻ.

**Chuyển ý:** “Một phần schema được bảo đảm trực tiếp bằng constraint và index.”

## Slide 8 — Constraint, validation và index

**Mục tiêu:** phân biệt ràng buộc đúng đắn với cơ chế tăng tốc.

**Có thể nói gần như nguyên văn:**

> Uniqueness constraint bảo đảm một stable ID không xuất hiện hai lần trong
> cùng label. Validation kiểm tra các quy tắc rộng hơn như orphan Movie, thiếu
> property hoặc cạnh sai đầu mút. Index tăng tốc lookup theo property; full-text
> index tạo candidate theo tên cho entity linking. Điểm quan trọng là index
> không làm graph đúng hơn và không thay đổi ngữ nghĩa; nó chỉ giúp tìm điểm bắt
> đầu nhanh hơn. Constraint trong Neo4j và quality gate trong pipeline bổ sung
> cho nhau.

**Cần chỉ vào:** ba thẻ Uniqueness, Validation, Index.

**Chuyển ý:** “Ngôn ngữ dùng để mô tả pattern và luật là Cypher.”

## Slide 9 — Cypher cho truy vấn và suy diễn

**Mục tiêu:** giải thích hai vai trò của Cypher.

**Có thể nói gần như nguyên văn:**

> Cypher biểu diễn truy vấn bằng pattern gần với hình dạng graph. Query bên trái
> tìm Person nối tới Movie qua DIRECTED; tên được truyền bằng parameter. Khối
> bên phải vật chất hóa luật: nếu hai Person cùng ACTED_IN một Movie thì tạo
> CO_STARRED_WITH. Project không dùng reasoner tách biệt; Cypher vừa thực hiện
> traversal, aggregation, vừa tạo derived relationship có evidence.

**Cần chỉ vào:** MATCH–RETURN và MATCH–MERGE.

**Chuyển ý:** “Để đọc các query này, ta cần một số thuật ngữ traversal.”

## Slide 10 — Hop, degree, common neighbor và shortest path

**Mục tiêu:** giải thích từ vựng duyệt đồ thị.

**Có thể nói gần như nguyên văn:**

> Hop là một lần đi qua cạnh. Degree là số cạnh kề một node. Common neighbor là
> node được hai node cùng chia sẻ, ví dụ hai Person cùng nối tới một Movie.
> Shortest path là đường có số cạnh nhỏ nhất trong phạm vi cho phép. Phim chung,
> co-star và recommendation đều dựa vào neighborhood hoặc common neighbor.
> Cũng cần lưu ý đường ít cạnh nhất chưa chắc có ý nghĩa nhất, nên kết quả phải
> giữ cả loại relationship làm evidence.

**Cần chỉ vào:** bốn khái niệm và dòng liên hệ với project.

**Chuyển ý:** “Đây là lý do mô hình đồ thị phù hợp với miền phim.”

## Slide 11 — Vì sao chọn Neo4j?

**Mục tiêu:** nêu lợi ích đúng mức.

**Có thể nói gần như nguyên văn:**

> Miền phim có nhiều quan hệ nhiều–nhiều. Mô hình quan hệ vẫn biểu diễn được
> bằng bảng nối và JOIN, nhưng Property Graph làm quan hệ trở thành cạnh trực
> tiếp và cho phép cạnh mang property. Điều này thuận tiện cho traversal nhiều
> bước và đường đi bằng chứng. Neo4j được chọn vì độ phù hợp mô hình và Cypher,
> không phải vì graph luôn nhanh hơn SQL. Phần benchmark sau cho thấy SQLite
> nhanh hơn trong các phép đo đã thực hiện.

**Cần chỉ vào:** bảng so sánh và “Property-rich relationships”.

**Chuyển ý:** “Tiếp theo là cách các khái niệm này đi vào kiến trúc dự án.”

## Slide 12 — Kiến trúc đầu cuối

**Mục tiêu:** giải thích các lớp của hệ thống.

**Có thể nói gần như nguyên văn:**

> Dữ liệu đi từ TMDB và IMDb vào raw cache bất biến, qua processing để làm sạch,
> ghép ID và chuẩn hóa thành bảng node–edge. Neo4j tạo constraint, import và
> reasoning. FastAPI cung cấp dịch vụ, Web UI hiển thị kết quả. Manifest và
> checksum bao quanh pipeline để hỗ trợ tái lập; entity link, graph path và
> shared feature tạo lớp explainability. Sau khi import, demo không phụ thuộc
> Internet.

**Cần chỉ vào:** sáu lớp từ trái sang phải.

**Chuyển ý:** “Trong hai nguồn, IMDb được tích hợp theo một phạm vi rất hẹp.”

## Slide 13 — Tích hợp TMDB–IMDb

**Mục tiêu:** giải thích exact join và streaming.

**Có thể nói gần như nguyên văn:**

> TMDB là nguồn graph chính. IMDb chỉ bổ sung rating và vote. Hệ thống đọc trực
> tiếp file ratings đang nén, chỉ giữ các dòng khớp tập IMDb ID của Movie. Phép
> nối dùng exact `imdb_id = tconst`, không ghép theo title. Có 4.558 Movie mang
> IMDb ID và 4.351 Movie ghép được rating, tương đương 95,5 phần trăm. Rating
> TMDB và IMDb được giữ riêng để không làm mất ngữ nghĩa nguồn.

**Cần chỉ vào:** exact ID và ba con số.

**Chuyển ý:** “Dữ liệu sau tích hợp được tổ chức theo schema sau.”

## Slide 14 — Schema Movie Knowledge Graph

**Mục tiêu:** giải thích node, edge và stable ID.

**Có thể nói gần như nguyên văn:**

> Schema có năm node chính: Movie, Person, Genre, Keyword và Studio; cùng năm
> quan hệ gốc. Chỉ dùng một label Person vì một người có thể vừa diễn xuất vừa
> đạo diễn; vai trò được biểu diễn bằng ACTED_IN hoặc DIRECTED. Stable source ID
> là khóa, tên không phải khóa. ACTED_IN giữ character, cast_order và source
> ngay trên cạnh.

**Cần chỉ vào:** Person, Movie và năm quan hệ.

**Chuyển ý:** “Schema này được tạo bởi pipeline có thể chạy lại.”

## Slide 15 — Pipeline dữ liệu

**Mục tiêu:** giải thích reproducibility và idempotency.

**Có thể nói gần như nguyên văn:**

> Pipeline gồm collect, cache, clean, IMDb join, normalize, Neo4j load, reason
> và validate. Raw cache bất biến cho phép xử lý lại cùng snapshot. Manifest ghi
> checksum, số lượng và quality metrics. Import tạo node trước edge và dùng
> MERGE theo stable ID, nên chạy lặp không nhân bản dữ liệu. Runtime chỉ import
> lại khi checksum processed hoặc số Movie trong graph thay đổi.

**Cần chỉ vào:** tám bước và bốn khối Cache–Manifest–MERGE–Gate.

**Chuyển ý:** “Trước khi ứng dụng sử dụng graph, dữ liệu phải vượt quality gate.”

## Slide 16 — Chất lượng graph

**Mục tiêu:** trình bày quy mô và phạm vi của quality claim.

**Có thể nói gần như nguyên văn:**

> Từ 5.000 record đầu vào, một Movie không có quan hệ bị loại, còn 4.999 Movie
> hợp lệ. Graph có 76.612 node và 846.309 relationship. Quality gate không phát
> hiện orphan Movie, stable ID trùng, thiếu property bắt buộc hoặc cạnh sai
> kiểu. Đây là bằng chứng về tính toàn vẹn cấu trúc theo quy tắc công bố, không
> có nghĩa dữ liệu ngoài đời hoàn hảo về mọi khía cạnh.

**Cần chỉ vào:** “0 vi phạm cấu trúc”.

**Chuyển ý:** “Một bài toán trung tâm khi tích hợp là phân giải thực thể.”

## Slide 17 — Entity resolution

**Mục tiêu:** giải thích exact, fuzzy, threshold và abstention.

**Có thể nói gần như nguyên văn:**

> Entity resolution quyết định hai record có mô tả cùng một thực thể hay không.
> Project ưu tiên exact source ID; fuzzy chỉ là fallback có confidence và log.
> Khi candidate mơ hồ hoặc dưới threshold, hệ thống abstain thay vì nối đoán.
> Trên 100 cặp silver, precision là 1, recall 0,933 và F1 0,966. Năm false
> negative là các trường hợp từ chối bảo thủ; tập này không có false positive.

**Cần chỉ vào:** flow exact → fuzzy → abstain và ba metric.

**Chuyển ý:** “Entity linking liên quan đến identity nhưng xảy ra ở thời điểm khác.”

## Slide 18 — Entity resolution và entity linking

**Mục tiêu:** phân biệt hai bài toán dễ bị gọi lẫn.

**Có thể nói gần như nguyên văn:**

> Entity resolution diễn ra lúc xây graph: nó hợp nhất hoặc giữ tách các record
> nguồn và ảnh hưởng dữ liệu lâu dài. Entity linking diễn ra khi người dùng đặt
> câu hỏi: nó nối chuỗi như “Cristopher Nolan” tới node canonical đã tồn tại.
> Linker xác định loại slot, tìm candidate bằng full-text, fuzzy rerank rồi trả
> stable ID, canonical name và confidence. Query sau đó dùng ID; không mở rộng
> lại bằng so khớp tên.

**Cần chỉ vào:** hai cột và thời điểm xử lý.

**Chuyển ý:** “Khi entity đã được liên kết, catalog chạy pattern Cypher.”

## Slide 19 — Cypher và pattern nhiều bước

**Mục tiêu:** đọc query và giải thích parameterization.

**Có thể nói gần như nguyên văn:**

> Query ví dụ đi từ Person qua DIRECTED tới Movie, rồi qua HAS_GENRE tới Genre,
> sau đó đếm Movie. Đây là traversal hai bước kết hợp aggregation. `$genre` và
> `$limit` là parameter, nên dữ liệu người dùng không thay đổi cấu trúc Cypher.
> Catalog gồm lookup, multi-hop, aggregation, shortest path và similarity. Việc
> cố định cấu trúc query giúp execution surface nhỏ và có thể kiểm thử.

**Cần chỉ vào:** pattern và hai parameter.

**Chuyển ý:** “Ngoài đọc cạnh gốc, hệ thống còn tạo cạnh suy ra.”

## Slide 20 — Suy diễn CO_STARRED_WITH

**Mục tiêu:** phân biệt asserted và derived fact.

**Có thể nói gần như nguyên văn:**

> ACTED_IN là asserted fact lấy từ credits TMDB. Khi hai Person cùng ACTED_IN
> một Movie, luật tạo CO_STARRED_WITH. Cạnh suy ra lưu `movie_count`,
> `evidence_movie_ids` và `derived=true`, nên có thể lần ngược về supporting
> movies. Đây là suy diễn rule-based minh bạch, không phải kết luận do mô hình
> ngôn ngữ tự tạo.

**Cần chỉ vào:** hai ACTED_IN và cạnh CO_STARRED_WITH.

**Chuyển ý:** “Để kiểm chứng đầy đủ, cần phân biệt ba lớp truy vết.”

## Slide 21 — Provenance, lineage và evidence

**Mục tiêu:** phân biệt ba khái niệm truy vết.

**Có thể nói gần như nguyên văn:**

> Provenance trả lời fact đến từ nguồn nào, ví dụ `source=tmdb` hoặc checksum
> IMDb. Lineage trả lời fact đã đi qua chuỗi biến đổi nào, từ raw cache qua
> clean, CSV, import và rule. Evidence trả lời một kết quả cụ thể dựa trên node,
> edge hoặc feature nào. Asserted fact cần provenance; derived fact cần cả luật
> và supporting facts; kết quả giải thích được cần evidence đủ để kiểm tra
> ngược.

**Cần chỉ vào:** ba hàng trong bảng và ba thẻ cuối.

**Chuyển ý:** “Các graph pattern được đưa tới người dùng qua hai ứng dụng.”

## Slide 22 — Hỏi–đáp an toàn

**Mục tiêu:** giải thích QA không sinh Cypher tự do.

**Có thể nói gần như nguyên văn:**

> Câu hỏi tiếng Việt được parser ánh xạ vào một trong chín intent và trích slot.
> Entity linker nối slot tới stable ID. Catalog chọn template Cypher cố định có
> parameter; Neo4j thực hiện traversal. Response giữ intent, entity confidence,
> graph row hoặc path và latency. Vì vậy lớp hội thoại chỉ điều phối quy trình
> xác định; nó không tự sinh arbitrary Cypher và không thay Neo4j.

**Cần chỉ vào:** Web UI → parser → linker → catalog → Neo4j.

**Chuyển ý:** “Ứng dụng thứ hai dùng neighborhood để xếp hạng.”

## Slide 23 — Gợi ý phim có giải thích

**Mục tiêu:** giải thích weighted graph similarity và IDF.

**Có thể nói gần như nguyên văn:**

> Candidate là các Movie chia sẻ director, actor, keyword, genre hoặc studio với
> phim nguồn. Mỗi shared feature đóng góp `type_weight` nhân với một thành phần
> IDF. Feature phổ biến có document frequency lớn nên đóng góp thấp hơn; feature
> hiếm có khả năng phân biệt tốt hơn. Tổng contribution tạo điểm. Explanation
> trả lại chính các shared feature, nên lời giải thích gắn trực tiếp với cách
> tính điểm.

**Cần chỉ vào:** công thức, trọng số và shared feature.

**Chuyển ý:** “Để đọc kết quả đánh giá, cần hiểu từng metric đo điều gì.”

## Slide 24 — Các metric đánh giá

**Mục tiêu:** phân biệt P, R, F1, P@K và NDCG@K.

**Có thể nói gần như nguyên văn:**

> Precision hỏi trong các kết quả hệ thống chấp nhận, bao nhiêu là đúng. Recall
> hỏi trong các trường hợp đúng cần tìm, hệ thống tìm được bao nhiêu. F1 là
> trung bình điều hòa của hai giá trị. Với recommendation, Precision@K đo tỷ lệ
> mục liên quan trong Top-K nhưng không quan tâm thứ tự. NDCG@K giảm trọng số ở
> vị trí thấp, nên phản ánh chất lượng ranking. Metric chỉ có ý nghĩa khi đọc
> cùng corpus, rubric và protocol.

**Cần chỉ vào:** ba công thức và hai khối ranking.

**Chuyển ý:** “Vì vậy mỗi claim trong dự án có một phép đánh giá riêng.”

## Slide 25 — Thiết kế evaluation

**Mục tiêu:** nối claim với dataset và metric.

**Có thể nói gần như nguyên văn:**

> Chất lượng dữ liệu dùng toàn corpus và các tỷ lệ lỗi. Entity resolution dùng
> 100 cặp silver với precision, recall, F1. Suy diễn dùng 50 fact co-star. QA
> dùng 20 câu smoke có evidence. Recommendation dùng 20 case với P@10 và
> NDCG@10. Hiệu năng dùng bốn query trên bốn quy mô. Silver corpus có protocol
> và provenance nhưng không phải ground truth độc lập từ người dùng.

**Cần chỉ vào:** từng hàng của bảng.

**Chuyển ý:** “Kết quả chính trên snapshot hiện tại như sau.”

## Slide 26 — Kết quả chính

**Mục tiêu:** trình bày metric và giới hạn diễn giải.

**Có thể nói gần như nguyên văn:**

> QA smoke pass 20 trên 20; entity resolution F1 0,966; co-star precision 1;
> recommendation đạt P@10 0,635 và NDCG@10 0,672. Entity precision cao một phần
> nhờ abstention bảo thủ. Các metric recommendation thuộc 20 case silver, chưa
> thay thế đánh giá người dùng. Điểm mạnh nhất là mọi kết quả QA và
> recommendation đều có evidence.

**Cần chỉ vào:** năm metric và khối “Cách đọc thận trọng”.

**Chuyển ý:** “Phần benchmark cũng cần được đọc với cùng mức thận trọng.”

## Slide 27 — Neo4j–SQLite và trade-off

**Mục tiêu:** diễn giải benchmark không thiên lệch.

**Có thể nói gần như nguyên văn:**

> Trên cùng snapshot, máy, warm-up và 100 lần chạy, SQLite nhanh hơn ở toàn bộ
> cặp query–quy mô đã đo. Vì vậy dự án không dùng tốc độ tuyệt đối để biện minh
> cho Neo4j. Lợi ích của Neo4j là biểu diễn relationship, traversal và evidence
> trực tiếp. Benchmark chưa đo concurrency, cold cache, tài nguyên khác nhau hay
> quy mô lớn hơn, nên không được khái quát thành xếp hạng hai engine.

**Cần chỉ vào:** hai đường latency và phần giới hạn.

**Chuyển ý:** “Quay lại câu hỏi thiết kế: schema phải bắt đầu từ nhu cầu trả lời.”

## Slide 28 — Competency question

**Mục tiêu:** cho thấy câu hỏi dẫn dắt schema và query.

**Có thể nói gần như nguyên văn:**

> Câu hỏi “hai diễn viên có phim nào cùng tham gia” xác định ba thành phần tối
> thiểu: Person, Movie và ACTED_IN. Nó ánh xạ thành shared-neighbor pattern
> Person → Movie ← Person. Từ một competency question, ta kiểm tra ba điều:
> schema có đủ khái niệm, query có trả lời được và kết quả có evidence hay
> không. Đây là cách nối yêu cầu nghiệp vụ với thiết kế graph.

**Cần chỉ vào:** câu hỏi, pattern và ba tiêu chí cuối.

**Chuyển ý:** “Demo sau minh họa toàn bộ phép ánh xạ này.”

## Slide 29 — Demo tổng hợp

**Mục tiêu:** minh họa question → link → query → evidence.

**Có thể nói gần như nguyên văn:**

> Em dùng câu hỏi về phim chung của Christian Bale và Tom Hardy. Parser chọn
> intent `common_movies`. Entity linker trả stable ID của hai Person. Catalog
> chạy pattern có parameter và Neo4j trả Movie chung. Evidence path là
> Christian Bale → The Dark Knight Rises ← Tom Hardy. Điều cần quan sát không
> phải giao diện, mà là mỗi bước từ ngôn ngữ đến kết quả đều có một biểu diễn
> xác định và có thể kiểm tra.

**Cần chỉ vào:** intent, entity IDs, Cypher và evidence path.

**Chuyển ý:** “Dù đạt mục tiêu, nghiên cứu vẫn có những giới hạn rõ ràng.”

## Slide 30 — Giới hạn và hướng phát triển

**Mục tiêu:** nêu phạm vi hiệu lực của kết luận.

**Có thể nói gần như nguyên văn:**

> QA hiện chỉ có chín intent, chưa phải open-domain. Corpus chủ yếu là silver và
> chưa có đánh giá người dùng độc lập. Snapshot tối đa 4.999 Movie, chưa đo
> concurrent load hay cold cache. Credits chỉ lấy top-20 cast và IMDb mới enrich
> Movie. Hướng tiếp theo là thu thập câu hỏi thật, đánh giá nhiều người chấm,
> benchmark tải đồng thời, mở rộng credits và liên kết thêm nguồn như Wikidata.

**Cần chỉ vào:** từng cặp giới hạn → hướng phát triển.

**Chuyển ý:** “Em xin kết luận bằng ba giá trị chính.”

## Slide 31 — Kết luận

**Mục tiêu:** khép lại bằng thông điệp lý thuyết.

**Có thể nói gần như nguyên văn:**

> Dự án cho thấy một Knowledge Graph có giá trị khi ba điều cùng tồn tại. Thứ
> nhất, dữ liệu được tích hợp đúng bằng stable identity, schema và provenance.
> Thứ hai, graph trả lời được competency questions qua traversal và derived fact
> có bằng chứng. Thứ ba, lớp ứng dụng giữ được đường đi hoặc feature giải thích
> thay vì chỉ trả một kết quả không thể kiểm tra. Em xin cảm ơn thầy và xin lắng
> nghe câu hỏi, phản biện.

**Cần chỉ vào:** ba kết luận Tích hợp đúng – Truy vấn được – Giải thích được.

## Quy tắc dùng tài liệu khi thuyết trình

- Không đọc toàn bộ chữ trên slide; dùng đoạn nói để diễn giải quan hệ giữa các
  khối.
- Khi bị giới hạn thời gian, nói một câu định nghĩa và một câu liên hệ dự án cho
  mỗi slide khái niệm.
- Không gọi entity linking và entity resolution là cùng một bước.
- Không nói constraint và index có cùng chức năng.
- Không nói Neo4j luôn nhanh hơn SQL.
- Không khái quát metric silver thành độ chính xác production.
- Khi được hỏi chi tiết implementation, dẫn sang Chương 4–5 và phụ lục tái lập
  trong báo cáo.
