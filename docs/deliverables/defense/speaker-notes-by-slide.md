# Nội dung thuyết trình theo từng slide

Tài liệu này bám theo `movie_knowledge_graph_defense.pptx` gồm **28 slide,
không có phụ lục**. Phần **Có thể nói gần như nguyên văn** là kịch bản chính;
**Cần chỉ vào** và **Chuyển ý** hỗ trợ thao tác trình bày.

Nội dung nói không đọc lại nguyên văn các thẻ trên slide. Mỗi đoạn cần làm rõ
ba ý theo đúng thứ tự: khái niệm là gì, vì sao dự án cần nó, và ví dụ nào trong
Movie Knowledge Graph chứng minh vai trò đó.

Mỗi slide được trình bày theo một mạch thống nhất:

1. Nhắc lại kết luận của slide trước để người nghe biết vì sao chuyển sang nội
   dung hiện tại.
2. Đặt câu hỏi mà slide hiện tại cần trả lời.
3. Giải thích lần lượt mọi khối nội dung đang xuất hiện trên slide, theo hướng
   từ trái sang phải hoặc từ trên xuống dưới.
4. Kết luận bằng một câu nêu điều người nghe cần ghi nhớ.
5. Dùng câu chuyển ý để mở ra câu hỏi của slide tiếp theo.

Tổng thời gian gợi ý: 20–25 phút. Nếu chỉ có 15–18 phút, nói ngắn slide 7 và
21; không cần xóa chúng vì các slide này hữu ích khi phản biện.

## Slide 1 — Knowledge Graph: Nền tảng lý thuyết

**Mục tiêu:** giới thiệu phạm vi bài nói.

**Có thể nói gần như nguyên văn:**

> Kính thưa thầy, đề tài của em tập trung vào nền tảng Knowledge Graph theo mô
> hình Property Graph. Mô hình này được gọi là “Property Graph” vì không chỉ
> node mà cả relationship đều có thể mang các thuộc tính dạng khóa–giá trị.
> Chẳng hạn, node Movie có các thuộc tính như title và release_date, còn cạnh
> ACTED_IN có thể lưu character và cast_order. Nhờ đó, thông tin mô tả một lần
> tham gia phim được đặt đúng trên quan hệ giữa Person và Movie, thay vì phải
> gắn miễn cưỡng vào một trong hai node.
>
> Trong các khái niệm được trình bày, identity là định danh thực thể, tức là cơ
> chế giúp hệ thống biết một node đang đại diện chính xác cho ai hoặc cho đối
> tượng nào. Identity phải dựa trên một ID ổn định thay vì chỉ dựa vào tên, vì
> nhiều người có thể trùng tên và một bộ phim có thể có nhiều cách viết tên.
> Trong dự án, Person được phân biệt bằng ID nguồn như `tmdb:<id>`, còn tên chủ
> yếu phục vụ hiển thị và tìm kiếm.
>
> Traversal là quá trình duyệt từ một node sang các node khác thông qua những
> relationship trong graph. Ví dụ, đường
> `Person → ACTED_IN → Movie → HAS_GENRE → Genre` cho phép tìm thể loại của các
> phim mà một người đã tham gia. Như vậy, identity giúp xác định đúng điểm bắt
> đầu, còn traversal giúp khai thác các mối liên hệ xuất phát từ điểm đó.
>
> Em sẽ lần lượt trình bày thực thể, quan hệ, schema, identity, traversal, truy
> vấn và suy diễn. Movie Knowledge Graph được dùng như một nghiên cứu tình
> huống xuyên suốt để cho thấy các khái niệm đó được mô hình hóa và kiểm chứng.
> Chi tiết source code, API và vận hành nằm trong báo cáo; trên slide em tập
> trung vào khái niệm và bằng chứng.

**Cần chỉ vào:** tiêu đề và sơ đồ Movie Knowledge Graph.

**Chuyển ý:** “Trước hết, khi nào dữ liệu trở thành tri thức?”

## Slide 2 — Từ dữ liệu đến tri thức

**Mục tiêu:** phân biệt data, information, knowledge và inference.

**Có thể nói gần như nguyên văn:**

> Dữ liệu là các giá trị rời rạc như 2010, Inception và Nolan. Khi thêm ngữ
> cảnh, ta có thông tin: Inception phát hành năm 2010. Khi nối các thực thể bằng
> quan hệ có nghĩa, ta có tri thức: Nolan đạo diễn Inception. Khi có schema và
> quy tắc, hệ thống có thể tạo ra tri thức mới từ những sự kiện đã biết. Quá
> trình đó được gọi là suy luận.
>
> Ví dụ, dữ liệu nguồn chỉ khẳng định rằng Christian Bale ACTED_IN một Movie và
> Tom Hardy cũng ACTED_IN chính Movie đó. Từ hai sự kiện đã được lưu, hệ thống
> áp dụng luật “hai người cùng tham gia ít nhất một phim thì họ từng đồng diễn”
> để suy ra quan hệ CO_STARRED_WITH giữa hai Person. Quan hệ mới không được nhập
> trực tiếp từ TMDB mà được tạo bởi một quy tắc có thể kiểm tra.
>
> Vì vậy, cần phân biệt tri thức được khẳng định và tri thức được suy ra. Tri
> thức được khẳng định đến trực tiếp từ nguồn dữ liệu; tri thức được suy ra là
> kết quả của việc áp dụng luật lên các sự kiện đã có. Trong dự án, mỗi quan hệ
> suy ra còn giữ số phim chung và ID của các phim làm bằng chứng. Suy luận ở đây
> không có nghĩa hệ thống tự hiểu hoặc tự sáng tạo kết luận; nó chỉ tạo ra những
> sự kiện thỏa mãn đúng luật đã khai báo.

**Cần chỉ vào:** bốn bậc từ trái sang phải.

**Chuyển ý:** “Một Knowledge Graph cụ thể được cấu tạo như thế nào?”

## Slide 3 — Knowledge Graph là gì?

**Mục tiêu:** giải thích entity, relationship, property và identifier.

**Có thể nói gần như nguyên văn:**

> Trong phạm vi dự án, Knowledge Graph là một đồ thị gồm các thực thể có định
> danh, các quan hệ mang ngữ nghĩa và một schema giúp máy hiểu cấu trúc dữ liệu.
> Như vậy, sau khi slide trước cho thấy dữ liệu chỉ trở thành tri thức khi có
> ngữ cảnh và quan hệ, slide này trả lời câu hỏi: một sự kiện trong Knowledge
> Graph được cấu tạo từ những thành phần nào?
>
> Trên hình, Christopher Nolan là chủ thể, Inception là đối tượng và DIRECTED là
> quan hệ có hướng nối hai thực thể. Cả Nolan và Inception đều là entity, tức là
> những đối tượng có thể được nhận diện độc lập trong miền tri thức.
> Relationship biểu diễn ý nghĩa giữa hai entity; ở đây nó cho biết Nolan giữ
> vai trò đạo diễn đối với Inception, chứ không chỉ nói rằng hai node có liên
> quan.
>
> Bên cạnh đó, property bổ sung thông tin mô tả. Person có thể có tên và ngày
> sinh; Movie có thể có ngày phát hành và rating; relationship cũng có thể mang
> thuộc tính riêng. Cuối cùng, identifier phải được phân biệt với name. Tên dùng
> để con người đọc và tìm kiếm, còn identifier dùng để xác định duy nhất
> identity, bởi hai người có thể trùng tên và một bộ phim có thể có nhiều cách
> viết tên.
>
> Điều cần nhớ ở slide này là một Knowledge Graph không chỉ có node và cạnh:
> node phải đại diện cho thực thể có định danh, còn cạnh phải biểu diễn một quan
> hệ có ý nghĩa.
>
> Khối phía dưới phân biệt ngắn gọn schema với instance. Schema
> `Person -[DIRECTED]-> Movie` quy định hình dạng quan hệ được phép, còn
> `Nolan -[DIRECTED]-> Inception` là một sự kiện cụ thể tuân theo schema đó.
> Nói cách khác, schema trả lời “dữ liệu được phép có hình dạng nào”, còn
> instance trả lời “sự kiện cụ thể nào đang tồn tại”. Dự án không vận hành TBox
> và ABox như hai hệ thống riêng nên em không đưa hai thuật ngữ đó vào mạch
> trình bày chính.

**Cần chỉ vào:** Nolan → DIRECTED → Inception, ba khối bên phải và khối
“Schema và instance” phía dưới.

**Chuyển ý:** “Các thành phần này được hiện thực hóa trong Neo4j bằng mô hình
Property Graph.”

## Slide 4 — Property Graph

**Mục tiêu:** giải thích mô hình graph duy nhất của dự án.

**Có thể nói gần như nguyên văn:**

> Neo4j Property Graph gồm node có label và property, relationship có loại,
> hướng và cũng có property. Slide trước mới mô tả schema và instance ở mức
> khái niệm; slide này cho thấy dự án hiện thực hóa chúng trong Neo4j như thế
> nào.
>
> Node bên trái mang label Person và có các property như name, birthday. Node
> bên phải mang label Movie và có title, release_date. Label cho biết node thuộc
> lớp nào, identifier xác định node nào, còn property cung cấp thông tin mô tả.
>
> Cạnh ACTED_IN nối Person tới Movie, có loại và có hướng. Quan trọng hơn, cạnh
> này còn giữ character và cast_order. Hai thuộc tính đó không mô tả riêng
> Person, cũng không mô tả riêng Movie; chúng mô tả chính lần một người tham gia
> một bộ phim. Vì vậy, đặt chúng trên relationship phản ánh đúng ngữ nghĩa của
> dữ liệu.
>
> Đây cũng là lý do mô hình được gọi là Property Graph: cả node và relationship
> đều có thể mang các cặp thuộc tính khóa–giá trị. Dự án chỉ triển khai mô hình
> này trong Neo4j, không đồng thời vận hành RDF hoặc một graph engine thứ hai.

**Cần chỉ vào:** hai node và property trên cạnh ACTED_IN.

**Chuyển ý:** “Từ node và cạnh, ta hình thành các cấu trúc lớn hơn.”

## Slide 5 — Neighborhood, path và subgraph

**Mục tiêu:** giới thiệu ba đơn vị cấu trúc của tư duy đồ thị.

**Có thể nói gần như nguyên văn:**

> Sau khi có node và cạnh, ta không chỉ đọc từng sự kiện riêng lẻ mà bắt đầu
> khai thác cấu trúc được hình thành bởi nhiều liên kết. Slide này trình bày ba
> cấu trúc cơ bản theo mức độ mở rộng dần.
>
> Trước hết, neighborhood là vùng lân cận quanh một node qua các loại quan hệ đã
> chọn. Với một Movie, vùng lân cận có thể gồm diễn viên, đạo diễn, thể loại, từ
> khóa và hãng phim. Dự án dùng cấu trúc này để tìm những phim có đặc trưng
> chung.
>
> Tiếp theo, path là một dãy node và cạnh liên tiếp nối hai thực thể. Độ dài của
> path được đo bằng số cạnh. Path cho phép trả lời câu hỏi nhiều bước, đồng thời
> cho người dùng nhìn thấy kết quả được nối qua những quan hệ nào.
>
> Cuối cùng, subgraph là phần đồ thị chỉ giữ các node và cạnh liên quan tới một
> mục tiêu cụ thể. Dự án dùng subgraph để giới hạn ngữ cảnh giải thích và tạo
> snapshot đánh giá có phạm vi nhất quán.
>
> Điều cần nhớ là neighborhood mô tả vùng quanh một thực thể, path mô tả cách
> nối giữa các thực thể, còn subgraph giữ lại phần ngữ cảnh cần thiết cho một
> nhiệm vụ.

**Cần chỉ vào:** ba khối Neighborhood, Path, Subgraph.

**Chuyển ý:** “Nhưng có graph chưa đủ để gọi là Knowledge Graph hữu dụng.”

## Slide 6 — Bốn điều kiện của Knowledge Graph hữu dụng

**Mục tiêu:** trình bày identity, schema, provenance và competency questions.

**Có thể nói gần như nguyên văn:**

> Một Knowledge Graph hữu dụng cần ít nhất bốn yếu tố. Identity giúp biết chính
> xác đang nói về thực thể nào. Đây là điều kiện đầu tiên vì mọi quan hệ đều sai
> nếu hai đầu mút bị nhận diện nhầm. Trong dự án, source ID được dùng làm khóa;
> tên chỉ phục vụ hiển thị và tìm kiếm.
>
> Điều kiện thứ hai là schema. Schema tạo ngôn ngữ chung cho các sự kiện: loại
> node nào tồn tại, quan hệ nào được phép và thuộc tính nào cần có. Nhờ đó, dữ
> liệu từ TMDB và IMDb có thể đi vào cùng một mô hình nhất quán.
>
> Điều kiện thứ ba là provenance, hay nguồn gốc dữ liệu. Một sự kiện nhập trực
> tiếp cần chỉ ra nguồn; một sự kiện suy ra cần giữ luật và các sự kiện hỗ trợ.
> Nếu thiếu provenance, người dùng không thể kiểm tra kết quả hoặc tái tạo quá
> trình hình thành graph.
>
> Điều kiện cuối cùng là competency question, tức là câu hỏi năng lực mà graph
> phải trả lời được. Nó giữ cho schema tập trung vào mục tiêu của bài toán, thay
> vì thu thập rất nhiều node và cạnh nhưng không phục vụ nhu cầu nào.
>
> Bốn yếu tố này trả lời bốn câu hỏi liên tiếp: đang nói về thực thể nào, sự kiện
> có hình dạng gì, sự kiện đến từ đâu và graph được xây để trả lời điều gì.

**Cần chỉ vào:** lần lượt bốn thẻ.

**Chuyển ý:** “Ngôn ngữ dùng để mô tả pattern và luật là Cypher.”

## Slide 7 — Cypher cho truy vấn và suy diễn

**Mục tiêu:** giải thích hai vai trò của Cypher.

**Có thể nói gần như nguyên văn:**

> Cypher biểu diễn truy vấn bằng pattern gần với hình dạng graph. Query bên trái
> tìm một Person nối tới Movie qua quan hệ DIRECTED. Cấu trúc
> `(p:Person)-[:DIRECTED]->(m:Movie)` gần như mô tả trực tiếp hình dạng cần tìm
> trên graph. Giá trị tên được truyền bằng parameter, nên dữ liệu người dùng
> không làm thay đổi cấu trúc truy vấn.
>
> Khối bên phải sử dụng cùng ngôn ngữ nhưng cho mục đích suy diễn. Pattern đầu
> tiên tìm hai Person cùng ACTED_IN một Movie; lệnh MERGE sau đó vật chất hóa
> quan hệ CO_STARRED_WITH. Quan hệ suy ra giữ số phim chung, ID phim làm bằng
> chứng và cờ `derived=true`.
>
> Như vậy, Cypher có hai vai trò trong dự án: đọc các pattern đã tồn tại và tạo
> thêm quan hệ khi một luật nghiệp vụ được thỏa mãn. Dự án không dùng reasoner
> tách biệt; traversal, aggregation và suy diễn đều được khai báo rõ trong
> Neo4j.

**Cần chỉ vào:** MATCH–RETURN và MATCH–MERGE.

**Chuyển ý:** “Để đọc các query này, ta cần một số thuật ngữ traversal.”

## Slide 9 — Vì sao chọn Neo4j?

**Mục tiêu:** nêu lợi ích đúng mức.

**Có thể nói gần như nguyên văn:**

> Miền phim có nhiều quan hệ nhiều–nhiều. Mô hình quan hệ vẫn biểu diễn được
> bằng bảng nối và JOIN. Vì vậy, câu hỏi ở slide này không phải là “mô hình bảng
> có làm được hay không”, mà là mô hình nào thể hiện tự nhiên hơn các thao tác
> trọng tâm của dự án.
>
> Trong mô hình bảng, quan hệ nhiều–nhiều cần bảng nối và truy vấn nhiều bước
> cần chuỗi JOIN. Trong Property Graph, quan hệ trở thành cạnh trực tiếp và
> pattern nhiều bước được viết theo đường đi. Cạnh còn có thể mang property:
> ACTED_IN giữ thông tin vai diễn, còn CO_STARRED_WITH giữ số phim chung và bằng
> chứng.
>
> Lợi ích quan trọng nhất là kết quả có thể đi kèm chính đường liên kết đã tạo ra
> nó. Neo4j được chọn vì sự phù hợp giữa mô hình miền phim, traversal và Cypher,
> không dựa trên một tuyên bố rằng graph luôn nhanh hơn SQL.

**Cần chỉ vào:** bảng so sánh và “Property-rich relationships”.

**Chuyển ý:** “Tiếp theo là cách các khái niệm này đi vào kiến trúc dự án.”

## Slide 10 — Kiến trúc đầu cuối

**Mục tiêu:** giải thích các lớp của hệ thống.

**Có thể nói gần như nguyên văn:**

> Dữ liệu đi từ TMDB và IMDb vào raw cache bất biến, qua processing để làm sạch,
> Sau khi đã giải thích vì sao chọn Neo4j, slide này đặt công nghệ đó vào toàn
> bộ luồng hệ thống, từ nguồn dữ liệu tới câu trả lời mà người dùng nhìn thấy.
>
> Bắt đầu từ trái sang phải, TMDB cung cấp dữ liệu chính của graph, còn IMDb bổ
> sung rating và số lượt đánh giá. Dữ liệu gốc được lưu vào raw cache bất biến,
> nhờ đó các lần xử lý lại sử dụng cùng một snapshot thay vì gọi nguồn mới.
>
> Tầng processing làm sạch, ghép ID và chuẩn hóa dữ liệu thành các bảng node và
> edge. Neo4j tạo constraint, nhập node trước cạnh, sau đó chạy luật suy diễn và
> validation. FastAPI điều phối hai chức năng hỏi–đáp và gợi ý; Web UI trình bày
> câu trả lời cùng bằng chứng.
>
> Hai khối phía dưới mô tả hai yêu cầu xuyên suốt. Checksum và manifest giúp tái
> lập quá trình nhập dữ liệu. Entity link, graph path và các đặc trưng chung giúp
> giải thích kết quả. Sau khi graph đã được nhập, đường chạy trình diễn không
> phụ thuộc Internet.

**Cần chỉ vào:** sáu lớp từ trái sang phải.

**Chuyển ý:** “Sau kiến trúc tổng thể, em đi vào schema dùng để tổ chức các
thực thể và quan hệ trong Neo4j.”

## Slide 11 — Schema Movie Knowledge Graph

**Mục tiêu:** giải thích node, edge và stable ID.

**Có thể nói gần như nguyên văn:**

> Trong kiến trúc vừa trình bày, Neo4j là lớp tổ chức và khai thác tri thức.
> Slide này cho thấy schema cụ thể được dùng trong lớp đó. Movie là node trung
> tâm; Person nối tới Movie qua ACTED_IN hoặc DIRECTED; Movie nối tới Genre,
> Keyword và Studio qua HAS_GENRE, HAS_KEYWORD và PRODUCED_BY.
>
> Dự án chỉ dùng một label Person vì cùng một người có thể vừa là diễn viên vừa
> là đạo diễn. Vai trò không phải bản chất cố định của người đó mà được thể hiện
> bằng loại quan hệ họ có với từng Movie.
>
> Mỗi loại node sử dụng stable source ID làm khóa; tên không phải khóa vì có thể
> trùng hoặc thay đổi cách viết. ACTED_IN giữ character, cast_order và source
> ngay trên cạnh, bởi các thuộc tính này mô tả lần tham gia cụ thể.
>
> Ba quyết định cần nhớ là: Movie làm trung tâm liên kết, vai trò nằm trên quan
> hệ và identity dựa trên ID ổn định.

**Cần chỉ vào:** Person, Movie và năm quan hệ.

**Chuyển ý:** “Sau khi xác định schema, em kiểm tra dữ liệu thực tế có tuân thủ
mô hình đó hay không.”

## Slide 12 — Chất lượng graph

**Mục tiêu:** trình bày quy mô và phạm vi của quality claim.

**Có thể nói gần như nguyên văn:**

> Từ 5.000 record đầu vào, một Movie không có quan hệ bị loại, còn 4.999 Movie
> hợp lệ. Graph cuối có 76.612 node và 846.309 relationship; các con số phía
> trên cho thấy quy mô của từng nhóm thực thể lớn như Person, Keyword và Studio.
>
> Phần quan trọng hơn nằm ở số 0 phía dưới. Quality gate không phát hiện Movie
> mồ côi, stable ID trùng, thuộc tính bắt buộc bị thiếu hoặc cạnh nối sai loại
> node. Một Movie không có bất kỳ quan hệ nào đã bị loại trước khi nhập, nên
> không bị che khuất trong thống kê cuối.
>
> Tuy nhiên, “0 vi phạm cấu trúc” chỉ có nghĩa graph thỏa các quy tắc đã công bố.
> Nó không chứng minh dữ liệu ngoài đời hoàn hảo, không có thiếu sót nội dung,
> hoặc mọi nguồn đều đúng. Đây là ranh giới cần giữ khi diễn giải kết quả chất
> lượng.

**Cần chỉ vào:** “0 vi phạm cấu trúc”.

**Chuyển ý:** “Một bài toán trung tâm khi tích hợp là phân giải thực thể.”

## Slide 15 — Cypher và pattern nhiều bước

**Mục tiêu:** đọc query và giải thích parameterization.

**Có thể nói gần như nguyên văn:**

> Sau khi entity linking đã trả đúng stable ID hoặc slot cần thiết, catalog mới
> thực thi pattern tương ứng.
>
> Dòng MATCH mô tả đường Person → DIRECTED → Movie → HAS_GENRE → Genre. Đây là
> traversal hai bước. Điều kiện WHERE chọn thể loại cần xét; RETURN nhóm theo
> đạo diễn và đếm số Movie; ORDER BY sắp xếp giảm dần; LIMIT giữ số kết quả đầu.
>
> `$genre` và `$limit` là parameter. Giá trị người dùng được truyền tách khỏi
> cấu trúc query, nên đầu vào không thể chèn thêm Cypher. Các thẻ bên phải cho
> thấy catalog bao phủ tra cứu, multi-hop, aggregation, shortest path và
> similarity.
>
> Ý cần nhớ là graph pattern được cố định và kiểm thử trước; người dùng chỉ cung
> cấp giá trị tham số, không tạo cấu trúc truy vấn mới.

**Cần chỉ vào:** pattern và hai parameter.

**Chuyển ý:** “Ngoài đọc cạnh gốc, hệ thống còn tạo cạnh suy ra.”

## Slide 16 — Suy diễn CO_STARRED_WITH

**Mục tiêu:** phân biệt asserted và derived fact.

**Có thể nói gần như nguyên văn:**

> ACTED_IN là asserted fact lấy từ credits TMDB. Khi hai Person cùng ACTED_IN
> một Movie, luật tạo CO_STARRED_WITH. Hai cạnh ACTED_IN trên hình là những sự
> kiện được khẳng định trực tiếp từ nguồn; cạnh CO_STARRED_WITH là sự kiện mới
> được suy ra từ pattern chung Movie.
>
> Việc vật chất hóa cạnh giúp những truy vấn đồng diễn phía sau không phải tính
> lại toàn bộ pattern mỗi lần. Tuy nhiên, cạnh mới không được coi như dữ liệu
> nguồn: nó được đánh dấu `derived=true`, lưu `movie_count` và
> `evidence_movie_ids`.
>
> Nhờ các thuộc tính này, hệ thống có thể trả lời không chỉ “hai người có từng
> đồng diễn không” mà còn “họ cùng tham gia bao nhiêu phim và đó là những phim
> nào”. Đây là suy diễn dựa trên luật minh bạch, không phải kết luận do mô hình
> ngôn ngữ tự tạo.

**Cần chỉ vào:** hai ACTED_IN và cạnh CO_STARRED_WITH.

**Chuyển ý:** “Để kiểm chứng đầy đủ, cần phân biệt ba lớp truy vết.”

## Slide 18 — Hỏi–đáp an toàn

**Mục tiêu:** giải thích QA không sinh Cypher tự do.

**Có thể nói gần như nguyên văn:**

> Câu hỏi tiếng Việt được parser ánh xạ vào một trong chín intent và trích slot.
> Đây là bước đầu tiên trong chuỗi xử lý trên hình. Nếu câu hỏi nằm ngoài chín
> intent đã hỗ trợ, hệ thống trả về trạng thái chưa biết thay vì tự tạo truy vấn.
>
> Tiếp theo, entity linker nối các slot như tên người hoặc tên phim tới stable ID
> của node canonical. Catalog dùng intent để chọn một template Cypher cố định và
> truyền các ID dưới dạng parameter. Neo4j mới là thành phần thực hiện traversal
> và trả kết quả.
>
> Response không chỉ có câu trả lời mà còn giữ intent, confidence của entity
> link, graph row hoặc path và latency. Ba thẻ bên phải tóm tắt ba lớp kiểm
> soát: phạm vi câu hỏi đóng, thực thể được chuẩn hóa và kết quả có bằng chứng.
>
> Vì vậy, chatbot chỉ điều phối một quy trình xác định; nó không sinh Cypher tự
> do và không thay thế cơ sở dữ liệu đồ thị.

**Cần chỉ vào:** Web UI → parser → linker → catalog → Neo4j.

**Chuyển ý:** “Ứng dụng thứ hai dùng neighborhood để xếp hạng.”

## Slide 19 — Gợi ý phim có giải thích

**Mục tiêu:** trình bày đầy đủ các bước của thuật toán IDF-weighted graph
similarity đang chạy trong Neo4j.

**Có thể nói gần như nguyên văn:**

> Thuật toán nhận đầu vào là một phim nguồn và số lượng kết quả Top-K. Bước đầu
> tiên, Neo4j duyệt vùng lân cận của phim nguồn qua năm loại quan hệ: đạo diễn,
> diễn viên, keyword, thể loại và studio. Một Movie khác trở thành candidate nếu
> chia sẻ ít nhất một trong năm loại đặc trưng này. Phim nguồn bị loại khỏi tập
> candidate.
>
> Bước thứ hai là tính đóng góp của từng đặc trưng chung. Công thức trên slide
> là `type_weight × (1 + ln((N + 1) / (df + 1)))`. Trong đó, `N` là tổng số
> Movie trong graph; `df` là số Movie được nối với đặc trưng đang xét. Hai số
> cộng một giúp công thức ổn định khi tính toán. Nếu một đặc trưng xuất hiện ở
> rất nhiều phim, tỷ số tiến gần một và phần IDF nhỏ. Nếu đặc trưng hiếm, tỷ số
> lớn hơn nên contribution tăng. Vì vậy, cùng thể loại Drama thường cung cấp ít
> sức phân biệt hơn cùng một đạo diễn hoặc keyword hiếm.
>
> Trọng số loại phản ánh mức ưu tiên được khai báo trong thuật toán: đạo diễn
> là `3,0`, diễn viên `2,0`, keyword `1,5`, thể loại `1,0` và studio `0,75`.
> Đây là các trọng số cố định của runtime; chúng không được học từ hành vi người
> dùng.
>
> Bước thứ ba, điểm của một candidate bằng tổng contribution của tất cả đặc
> trưng mà candidate chia sẻ với phim nguồn. Do đó, một phim có thể được điểm từ
> nhiều diễn viên, nhiều keyword và nhiều loại quan hệ cùng lúc. Hệ thống không
> dùng rating hay popularity để cộng thêm vào điểm.
>
> Cuối cùng, Neo4j sắp xếp candidate theo điểm giảm dần; nếu bằng điểm thì sắp
> theo title, rồi lấy Top-K. Đồng thời query trả lại chính các shared feature đã
> tạo điểm. Phần explanation được dựng từ danh sách này, nên lời giải thích phản
> ánh trực tiếp cơ chế xếp hạng chứ không phải một câu được thêm vào sau.
>
> Tóm lại, đây là content-based recommendation trên cấu trúc graph có trọng số
> IDF. Nó không phải collaborative filtering và cũng không sử dụng embedding.

**Cần chỉ vào:** năm loại đặc trưng, công thức với `N` và `df`, năm trọng số,
rồi khối “Tổng điểm → Top-K → giải thích”.

**Chuyển ý:** “Để đọc kết quả đánh giá, cần hiểu từng metric đo điều gì.”


## Slide 24 — Demo 1: Tra cứu diễn viên

**Mục tiêu:** thực hiện bước 1–2 trong `defense-script.md`.

**Có thể nói gần như nguyên văn:**

> Trước tiên, em kiểm tra một fact một bước. Ở bước 1, em hỏi trên Web UI:
> “Diễn viên nào đóng trong phim Inception?”. Khi kết quả xuất hiện, em chỉ vào
> Movie đã được entity linking, danh sách Person và thông tin vai diễn lấy từ
> cạnh ACTED_IN.
>
> Ở bước 2, em copy nguyên câu Cypher bên phải slide vào Neo4j Browser và chạy.
> Query tìm các cạnh ACTED_IN đi vào Movie có title là Inception, sau đó trả tên
> diễn viên và nhân vật theo `cast_order`. Em đối chiếu hai cột `actor` và
> `character` với Web UI. Hai giao diện sử dụng hai đường truy cập khác nhau:
> Web UI đi qua FastAPI, còn Browser truy vấn trực tiếp; nhưng cả hai phải thống
> nhất vì cùng đọc một graph Neo4j.

**Cần chỉ vào:** câu hỏi, toàn bộ query bên phải, hai cột `actor` và
`character`.

**Chuyển ý:** “Sau fact một bước, em chuyển sang một truy vấn nhiều bước có
đường đi bằng chứng.”

## Slide 25 — Demo 2: Phim chung

**Mục tiêu:** thực hiện bước 3–4 trong `defense-script.md`.

**Có thể nói gần như nguyên văn:**

> Ở bước 3, em hỏi trên Web UI: “Phim chung của Christian Bale và Tom Hardy?”.
> Hệ thống phải liên kết đúng hai Person, chọn intent `common_movies` và trả về
> The Dark Knight Rises.
>
> Ở bước 4, em copy nguyên query bên phải slide vào Neo4j Browser. Hai điều kiện
> WHERE xác định đúng Christian Bale và Tom Hardy; pattern ở dòng MATCH yêu cầu
> cả hai cùng nối tới một Movie qua ACTED_IN. Kết quả bảng phải có
> The Dark Knight Rises. Nếu muốn minh họa trực quan, em đổi dòng RETURN thành
> `RETURN a, m, b` rồi chuyển sang chế độ graph để chỉ ra Movie là láng giềng
> chung của hai Person.

**Cần chỉ vào:** toàn bộ query, kết quả `common_movie` và cách đổi thành
`RETURN a, m, b`.

**Chuyển ý:** “Hai demo đầu kiểm chứng câu trả lời; demo cuối kiểm chứng lời
giải thích của một kết quả xếp hạng.”

## Slide 26 — Demo 3: Gợi ý phim

**Mục tiêu:** thực hiện bước 5–6 trong `defense-script.md`.

**Có thể nói gần như nguyên văn:**

> Ở bước 5, em chọn Inception trên Web UI và yêu cầu Top-5. Với phim đứng đầu,
> em mở phần giải thích để quan sát tổng điểm, các đặc trưng chung và contribution
> của từng đặc trưng.
>
> Ở bước 6, em nhìn dòng `:param candidate_title` ở đầu query. Nếu Top-1 hiện
> tại không phải Interstellar, em thay bằng đúng tên vừa ghi lại. Sau đó em copy
> toàn bộ query bên phải slide vào Neo4j Browser. Các nhánh UNION lần lượt tìm
> đạo diễn, diễn viên, thể loại, từ khóa và hãng phim chung giữa Inception và
> candidate. Hai cột `kind` và `shared_features` phải khớp với explanation trên
> Web UI.
>
> Query trong Browser dùng để kiểm chứng bằng chứng graph. Điểm và thứ hạng vẫn
> do công thức IDF đầy đủ của ứng dụng tính. Vì vậy, demo không thay thế thuật
> toán xếp hạng mà chứng minh lời giải thích xuất phát từ dữ liệu thật trong
> graph.

**Cần chỉ vào:** dòng `:param`, năm nhánh UNION, `kind`, `shared_features` và
phần explanation trên Web UI.

**Chuyển ý:** “Sau sáu bước demo, em quay lại phạm vi hiệu lực và những giới
hạn của kết quả.”

## Slide 27 — Giới hạn và hướng phát triển

**Mục tiêu:** nêu phạm vi hiệu lực của kết luận.

**Có thể nói gần như nguyên văn:**

> Mỗi giới hạn ở cột giữa được nối với một hướng phát triển tương ứng ở cột bên
> phải.
>
> Với QA đóng, bước tiếp theo là thu thập câu hỏi thực tế rồi mở rộng intent theo
> nhu cầu, không mở tùy ý. Với silver corpus, cần bổ sung đánh giá người dùng và
> nhiều người chấm độc lập. Với snapshot tối đa 4.999 Movie, cần benchmark graph
> lớn hơn, concurrent load và cold cache. Với độ phủ top-20 cast và IMDb mới làm
> giàu Movie, cần mở rộng credits và liên kết Person hoặc Wikidata.
>
> Các hướng phát triển này xuất phát trực tiếp từ giới hạn đã quan sát, thay vì
> là danh sách công nghệ bổ sung không gắn với kết quả hiện tại.

**Cần chỉ vào:** từng cặp giới hạn → hướng phát triển.

**Chuyển ý:** “Em xin kết luận bằng ba giá trị chính.”

## Slide 28 — Kết luận

**Mục tiêu:** khép lại bằng thông điệp lý thuyết.

**Có thể nói gần như nguyên văn:**

> Dự án cho thấy một Knowledge Graph có giá trị khi ba điều cùng tồn tại. Thứ
> nhất, dữ liệu phải được tích hợp nhất quán bằng stable identity, schema,
> provenance và một pipeline có thể tái lập.
>
> Thứ hai, graph phải khai thác được các quan hệ đó. Trong dự án, Cypher hỗ trợ
> traversal nhiều bước và luật CO_STARRED_WITH tạo derived fact có bằng chứng.
>
> Thứ ba, giá trị của graph phải đến được lớp ứng dụng. QA giữ intent, entity
> link và graph path; recommendation giữ các feature đã đóng góp vào điểm. Vì
> vậy, hệ thống không chỉ trả kết quả mà còn cho phép kiểm tra vì sao có kết quả
> đó.
>
> Thông điệp cuối cùng là: đồ thị tri thức tạo ra giá trị khi mỗi thực thể được
> nhận diện đúng, mỗi quan hệ có ngữ nghĩa và mỗi kết quả đều có thể lần ngược
> về bằng chứng. Em xin cảm ơn thầy và xin lắng nghe câu hỏi, phản biện.

**Cần chỉ vào:** ba kết luận Tích hợp đúng – Truy vấn được – Giải thích được.

## Quy tắc dùng tài liệu khi thuyết trình

- Không đọc toàn bộ chữ trên slide; dùng đoạn nói để diễn giải quan hệ giữa các
  khối.
- Khi bị giới hạn thời gian, nói một câu định nghĩa và một câu liên hệ dự án cho
  mỗi slide khái niệm.
- Không gọi entity linking và entity resolution là cùng một bước.
- Không nói constraint và index có cùng chức năng.
- Không khái quát metric silver thành độ chính xác production.
- Khi được hỏi chi tiết implementation, dẫn sang Chương 4–5 và phụ lục tái lập
  trong báo cáo.
