# Nội dung thuyết trình theo từng slide

Tài liệu này bám theo `movie_knowledge_graph_defense.pptx` gồm **30 slide,
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

Tổng thời gian gợi ý: 20–26 phút. Nếu chỉ có 15–18 phút, nói ngắn slide 8 và
22; không cần xóa chúng vì các slide này hữu ích khi phản biện.

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

**Cần chỉ vào:** Nolan → DIRECTED → Inception và ba khối bên phải.

**Chuyển ý:** “Để fact không được tạo tùy ý, ta cần schema.”

## Slide 4 — Schema và instance

**Mục tiêu:** phân biệt lớp khái niệm và dữ liệu cụ thể.

**Có thể nói gần như nguyên văn:**

> Schema, hay TBox theo cách gọi khái niệm, mô tả các lớp và loại quan hệ được
> phép. Sau khi đã biết một sự kiện gồm entity và relationship, câu hỏi tiếp
> theo là: điều gì ngăn graph tạo ra những quan hệ tùy ý hoặc không nhất quán?
> Câu trả lời là schema.
>
> Ở nửa trái của slide, schema quy định Person và Movie là hai lớp thực thể, còn
> DIRECTED là loại quan hệ đi từ Person tới Movie. Đây là mô tả ở mức khái niệm:
> nó chưa nói đến một người hay một bộ phim cụ thể. Domain là Person và range là
> Movie giúp xác định đúng loại node ở hai đầu quan hệ.
>
> Ở nửa phải, instance là dữ liệu cụ thể tuân theo schema đó: Nolan là một
> instance của Person, Inception là một instance của Movie và sự kiện Nolan
> DIRECTED Inception là một instance của quan hệ đã định nghĩa. Vì vậy, schema
> trả lời “dữ liệu được phép có hình dạng nào”, còn instance trả lời “những sự
> kiện cụ thể nào đang tồn tại”.
>
> Ba khối phía dưới thể hiện quan hệ giữa các khái niệm: graph schema định nghĩa
> cấu trúc; knowledge base kết hợp schema với tập instance; và Knowledge Graph
> tổ chức knowledge base đó thành các liên kết có thể truy vấn. Dự án không vận
> hành TBox và ABox như hai hệ thống tách biệt; hai thuật ngữ này được dùng để
> phân biệt mức mô hình và mức dữ liệu.

**Cần chỉ vào:** schema bên trái, instance bên phải.

**Chuyển ý:** “Project hiện thực hóa hai lớp này bằng Property Graph.”

## Slide 5 — Property Graph

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

## Slide 6 — Neighborhood, path và subgraph

**Mục tiêu:** giới thiệu ba đơn vị cấu trúc của tư duy đồ thị.

**Có thể nói gần như nguyên văn:**

> Neighborhood là tập node lân cận một node qua các quan hệ được chọn. Path là
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

## Slide 7 — Bốn điều kiện của Knowledge Graph hữu dụng

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

**Chuyển ý:** “Một phần schema được bảo đảm trực tiếp bằng constraint và index.”

## Slide 8 — Constraint, validation và index

**Mục tiêu:** phân biệt ràng buộc đúng đắn với cơ chế tăng tốc.

**Có thể nói gần như nguyên văn:**

> Uniqueness constraint bảo đảm một stable ID không xuất hiện hai lần trong
> cùng label. Ví dụ, một `Movie.tmdb_id` chỉ được phép thuộc về một node Movie.
> Constraint bảo vệ identity ngay tại tầng lưu trữ và giúp lệnh MERGE xác định
> đúng node thay vì tạo bản sao.
>
> Tuy nhiên, constraint trong cơ sở dữ liệu không biểu diễn được mọi quy tắc của
> miền. Vì vậy, validation trong pipeline kiểm tra thêm Movie không có quan hệ,
> thuộc tính bắt buộc bị thiếu, cạnh nối sai loại node và sự kiện suy ra không có
> bằng chứng. Hai lớp kiểm tra bổ sung cho nhau: constraint chặn lỗi có thể khai
> báo trong Neo4j, còn validation kiểm tra các quy tắc rộng hơn.
>
> Khối cuối là index. Index thường được tạo cùng constraint nhưng có mục đích
> khác: nó tăng tốc việc tìm node theo thuộc tính. Full-text index còn tạo danh
> sách ứng viên khi tên người dùng nhập không hoàn toàn trùng với tên chuẩn.
> Index không làm dữ liệu đúng hơn và không thay đổi ngữ nghĩa; nó chỉ giúp tìm
> điểm bắt đầu nhanh hơn trước khi traversal.
>
> Vì vậy, cần nhớ: constraint bảo vệ tính đúng đắn, validation kiểm tra quy tắc
> nghiệp vụ, còn index phục vụ hiệu năng tra cứu.

**Cần chỉ vào:** ba thẻ Uniqueness, Validation, Index.

**Chuyển ý:** “Ngôn ngữ dùng để mô tả pattern và luật là Cypher.”

## Slide 9 — Cypher cho truy vấn và suy diễn

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

## Slide 10 — Hop, degree, common neighbor và shortest path

**Mục tiêu:** giải thích từ vựng duyệt đồ thị.

**Có thể nói gần như nguyên văn:**

> Hop là một lần đi qua cạnh. Degree là số cạnh kề một node. Common neighbor là
> Để đọc đúng các pattern Cypher vừa trình bày, ta cần bốn thuật ngữ mô tả cách
> duyệt đồ thị.
>
> Hop là một lần đi qua cạnh. Person → Movie là một hop; Person → Movie → Genre
> là hai hop. Degree là số cạnh kề một node. Node có degree cao thường là thực
> thể phổ biến, nhưng chính sự phổ biến đó có thể gây thiên lệch khi xếp hạng.
>
> Common neighbor là node được hai node cùng chia sẻ. Ví dụ, một Movie là láng
> giềng chung của hai Person cùng tham gia phim đó; một diễn viên hoặc thể loại
> cũng có thể là láng giềng chung của hai Movie. Đây là nền tảng của truy vấn
> phim chung, quan hệ đồng diễn và gợi ý tương tự.
>
> Shortest path là đường có số cạnh nhỏ nhất trong phạm vi quan hệ cho phép.
> Trong dự án, truy vấn này được giới hạn tối đa tám cạnh để kiểm soát phạm vi.
> Tuy nhiên, đường ít cạnh nhất chưa chắc là đường có ý nghĩa nhất; vì vậy kết
> quả phải giữ cả loại relationship để người dùng đọc được ngữ nghĩa.
>
> Tóm lại, hop đo số bước, degree đo mức kết nối, common neighbor đo phần lân cận
> chung và shortest path tìm cách nối ngắn nhất.

**Cần chỉ vào:** bốn khái niệm và dòng liên hệ với project.

**Chuyển ý:** “Đây là lý do mô hình đồ thị phù hợp với miền phim.”

## Slide 11 — Vì sao chọn Neo4j?

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

## Slide 12 — Kiến trúc đầu cuối

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

## Slide 13 — Schema Movie Knowledge Graph

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

## Slide 14 — Chất lượng graph

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

## Slide 15 — Entity resolution

**Mục tiêu:** giải thích exact, fuzzy, threshold và abstention.

**Có thể nói gần như nguyên văn:**

> Entity resolution quyết định hai record có mô tả cùng một thực thể hay không.
> Đây là bước cần thiết trước khi nhập graph, vì nếu hai record của cùng một
> người bị tách thành hai node, quan hệ sẽ bị phân mảnh; ngược lại, nếu hai người
> khác nhau bị gộp, nhiều đường đi phía sau sẽ trở thành sai.
>
> Quy trình trên hình đi từ tín hiệu chắc chắn tới tín hiệu yếu hơn. Trước hết,
> hệ thống ưu tiên exact source ID. Chỉ khi thiếu ID mới dùng fuzzy matching như
> một phương án dự phòng, có confidence và log. Nếu ứng viên mơ hồ hoặc điểm
> dưới threshold, hệ thống abstain, tức là từ chối nối thay vì đoán.
>
> Trên 100 cặp silver, precision đạt 1, recall đạt 0,933 và F1 đạt 0,966. Năm
> false negative là các trường hợp hệ thống từ chối bảo thủ; tập này không có
> false positive. Kết quả thể hiện lựa chọn thiết kế: chấp nhận bỏ sót một số
> liên kết để tránh tạo liên kết sai làm ô nhiễm graph.

**Cần chỉ vào:** flow exact → fuzzy → abstain và ba metric.

**Chuyển ý:** “Entity linking liên quan đến identity nhưng xảy ra ở thời điểm khác.”

## Slide 16 — Entity resolution và entity linking

**Mục tiêu:** phân biệt hai bài toán dễ bị gọi lẫn.

**Có thể nói gần như nguyên văn:**

> Entity resolution diễn ra lúc xây graph: nó hợp nhất hoặc giữ tách các record
> nguồn và ảnh hưởng dữ liệu lâu dài. Đầu vào của bước này là các record dữ liệu;
> đầu ra là các node canonical được nhập vào graph. Vì hậu quả kéo dài qua mọi
> truy vấn, false positive ở bước này đặc biệt nguy hiểm.
>
> Entity linking diễn ra ở thời điểm người dùng đặt câu hỏi. Đầu vào không phải
> record nguồn mà là một chuỗi như “Cristopher Nolan”; mục tiêu là nối chuỗi đó
> tới node Christopher Nolan đã tồn tại.
>
> Linker trước hết xác định loại slot như Person, Movie hoặc Genre; sau đó dùng
> full-text index tạo candidate, fuzzy rerank, áp dụng threshold và trả stable
> ID, canonical name cùng confidence. Query phía sau sử dụng ID đã chọn, không
> mở rộng lại bằng so khớp tên.
>
> Vì vậy, hai bài toán cùng xử lý identity nhưng khác thời điểm và mục tiêu:
> resolution xây identity của graph, còn linking tìm đúng identity khi khai
> thác graph.

**Cần chỉ vào:** hai cột và thời điểm xử lý.

**Chuyển ý:** “Khi entity đã được liên kết, catalog chạy pattern Cypher.”

## Slide 17 — Cypher và pattern nhiều bước

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

## Slide 18 — Suy diễn CO_STARRED_WITH

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

## Slide 19 — Provenance, lineage và evidence

**Mục tiêu:** phân biệt ba khái niệm truy vết.

**Có thể nói gần như nguyên văn:**

> Provenance trả lời fact đến từ nguồn nào, ví dụ `source=tmdb` hoặc checksum
> IMDb. Đây là thông tin về nguồn gốc của sự kiện.
>
> Lineage trả lời một câu hỏi khác: sự kiện đã đi qua chuỗi biến đổi nào, từ raw
> cache, làm sạch, CSV, import cho tới luật suy diễn. Nó mô tả lịch sử xử lý,
> không chỉ nguồn ban đầu.
>
> Evidence lại gắn với một kết quả cụ thể: câu trả lời hoặc gợi ý này dựa trên
> node, edge, path hay shared feature nào. Vì vậy, cùng một dữ liệu có thể có
> provenance và lineage cố định, nhưng mỗi câu trả lời sử dụng một tập evidence
> khác nhau.
>
> Ba thẻ phía dưới cho thấy yêu cầu tương ứng: asserted fact cần provenance;
> derived fact cần luật và supporting facts; explainable result cần đường đi
> hoặc đặc trưng đủ để kiểm tra ngược. Ba lớp này bổ sung cho nhau chứ không phải
> ba cách gọi của cùng một khái niệm.

**Cần chỉ vào:** ba hàng trong bảng và ba thẻ cuối.

**Chuyển ý:** “Các graph pattern được đưa tới người dùng qua hai ứng dụng.”

## Slide 20 — Hỏi–đáp an toàn

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

## Slide 21 — Gợi ý phim có giải thích

**Mục tiêu:** giải thích weighted graph similarity và IDF.

**Có thể nói gần như nguyên văn:**

> Candidate là các Movie chia sẻ director, actor, keyword, genre hoặc studio với
> phim nguồn. Như vậy, ứng dụng bắt đầu từ neighborhood của phim đang xét, lấy
> những phim có ít nhất một đặc trưng chung rồi mới tính điểm.
>
> Mỗi shared feature đóng góp `type_weight` nhân với thành phần IDF. Trọng số
> loại thể hiện ưu tiên của miền: đạo diễn và diễn viên đóng góp nhiều hơn thể
> loại hoặc từ khóa. Thành phần IDF phụ thuộc vào document frequency: đặc trưng
> xuất hiện ở quá nhiều phim có sức phân biệt thấp nên bị giảm ảnh hưởng; đặc
> trưng hiếm đóng góp nhiều hơn.
>
> Tổng các contribution tạo thành điểm cuối. Neo4j trả lại cả điểm và danh sách
> shared feature đã đóng góp. Do lời giải thích được tạo từ đúng các thành phần
> dùng để xếp hạng, nó phản ánh cơ chế tính điểm chứ không phải một câu giải thích
> được thêm vào sau.

**Cần chỉ vào:** công thức, trọng số và shared feature.

**Chuyển ý:** “Để đọc kết quả đánh giá, cần hiểu từng metric đo điều gì.”

## Slide 22 — Các metric đánh giá

**Mục tiêu:** phân biệt P, R, F1, P@K và NDCG@K.

**Có thể nói gần như nguyên văn:**

> Precision hỏi trong các kết quả hệ thống chấp nhận, bao nhiêu là đúng. Recall
> hỏi trong các trường hợp đúng cần tìm, hệ thống tìm được bao nhiêu. Hai metric
> nhìn lỗi từ hai phía: precision phạt false positive, còn recall phạt false
> negative.
>
> F1 là trung bình điều hòa của precision và recall, dùng khi cần một con số cân
> bằng. Tuy nhiên, F1 vẫn phải được đọc cùng số TP, FP và FN để hiểu hệ thống sai
> theo hướng nào.
>
> Với recommendation, Precision@K đo tỷ lệ mục liên quan trong K vị trí đầu,
> nhưng coi các vị trí trong Top-K như nhau. NDCG@K giảm trọng số của kết quả ở
> vị trí thấp và chuẩn hóa theo thứ tự lý tưởng, nên phản ánh cả mức liên quan và
> chất lượng sắp xếp.
>
> Mỗi metric trả lời một câu hỏi khác nhau; không có một con số duy nhất đánh giá
> toàn bộ Knowledge Graph. Mọi giá trị chỉ có nghĩa khi đọc cùng corpus, rubric
> và protocol.

**Cần chỉ vào:** ba công thức và hai khối ranking.

**Chuyển ý:** “Vì vậy mỗi claim trong dự án có một phép đánh giá riêng.”

## Slide 23 — Thiết kế evaluation

**Mục tiêu:** nối claim với dataset và metric.

**Có thể nói gần như nguyên văn:**

> Slide này ánh xạ từng tuyên bố của dự án tới một tập đánh giá và metric cụ thể.
>
> Chất lượng dữ liệu được kiểm tra trên toàn corpus bằng tỷ lệ thiếu, trùng và
> node mồ côi. Entity resolution dùng 100 cặp silver với precision, recall và
> F1. Suy diễn dùng 50 sự kiện co-star để đo precision. QA dùng 20 câu smoke và
> yêu cầu cả câu trả lời lẫn evidence. Recommendation dùng 20 trường hợp với
> P@10 và NDCG@10. Hiệu năng dùng bốn query trên bốn quy mô, báo cáo median và
> p95 sau warm-up.
>
> Ba lưu ý bên phải giới hạn cách diễn giải: silver corpus có provenance và
> protocol nhưng không phải ground truth độc lập; mọi kết quả phải đi kèm
> snapshot và cấu hình đã dùng; kết luận không được vượt ra ngoài những gì thí
> nghiệm đã đo.

**Cần chỉ vào:** từng hàng của bảng.

**Chuyển ý:** “Kết quả chính trên snapshot hiện tại như sau.”

## Slide 24 — Kết quả chính

**Mục tiêu:** trình bày metric và giới hạn diễn giải.

**Có thể nói gần như nguyên văn:**

> QA smoke pass 20 trên 20; entity resolution F1 0,966; co-star precision 1;
> recommendation đạt P@10 0,635 và NDCG@10 0,672. Năm thẻ phía trên tương ứng
> với năm tuyên bố đã nêu ở slide thiết kế đánh giá.
>
> Biểu đồ phía dưới giúp so sánh quy mô tương đối, nhưng các cột không hoàn toàn
> cùng loại metric nên không nên dùng để kết luận tác vụ nào “tốt hơn”. Khối bên
> phải mới là cách đọc cần giữ: QA 20/20 chỉ chứng minh luồng đóng hoạt động trên
> smoke corpus; entity precision cao một phần nhờ abstention bảo thủ;
> recommendation được đo trên 20 case silver và chưa thay thế đánh giá người
> dùng.
>
> Điểm mạnh xuyên suốt không chỉ là giá trị metric, mà là kết quả QA và
> recommendation đều giữ evidence để kiểm tra.

**Cần chỉ vào:** năm metric và khối “Cách đọc thận trọng”.

**Chuyển ý:** “Sau các kết quả, em quay lại nguyên tắc thiết kế: schema phải
bắt đầu từ câu hỏi cần trả lời.”

## Slide 25 — Competency question

**Mục tiêu:** cho thấy câu hỏi dẫn dắt schema và query.

**Có thể nói gần như nguyên văn:**

> Câu hỏi “hai diễn viên có phim nào cùng tham gia” xác định ba thành phần tối
> thiểu: Person, Movie và ACTED_IN. Điều kiện hai Person phải khác nhau cũng xuất
> phát trực tiếp từ ý nghĩa của câu hỏi.
>
> Phần Cypher bên phải chuyển câu hỏi thành shared-neighbor pattern:
> Person → Movie ← Person. Hai ID người được truyền bằng parameter, còn Movie
> chung là kết quả trả về.
>
> Ba thẻ phía dưới tạo thành một phép kiểm tra thiết kế. Schema coverage hỏi mô
> hình có đủ lớp và quan hệ hay không. Query answerability hỏi pattern có thực sự
> trả lời câu hỏi hay không. Evidence hỏi kết quả có lần ngược được đường đi hay
> không.
>
> Như vậy, competency question không chỉ dùng để demo; nó là điểm xuất phát để
> thiết kế và kiểm chứng schema.

**Cần chỉ vào:** câu hỏi, pattern và ba tiêu chí cuối.

**Chuyển ý:** “Ba slide tiếp theo biến nguyên lý này thành sáu bước demo: mỗi
kết quả trên Web UI đều được kiểm chứng ngay trong Neo4j Browser.”

## Slide 26 — Demo 1: Tra cứu diễn viên

**Mục tiêu:** thực hiện bước 1–2 trong `defense-script.md`.

**Có thể nói gần như nguyên văn:**

> Trước tiên, em kiểm tra một fact một bước. Ở bước 1, em hỏi trên Web UI:
> “Diễn viên nào đóng trong phim Inception?”. Khi kết quả xuất hiện, em chỉ vào
> Movie đã được entity linking, danh sách Person và thông tin vai diễn lấy từ
> cạnh ACTED_IN.
>
> Ở bước 2, em chuyển sang Neo4j Browser và chạy pattern
> Person -[ACTED_IN]-> Movie cho Inception. Em đối chiếu tên diễn viên và
> character với Web UI. Hai giao diện sử dụng hai đường truy cập khác nhau:
> Web UI đi qua FastAPI, còn Browser truy vấn trực tiếp; nhưng cả hai phải thống
> nhất vì cùng đọc một graph Neo4j.

**Cần chỉ vào:** câu hỏi, evidence ACTED_IN và hai đường truy cập.

**Chuyển ý:** “Sau fact một bước, em chuyển sang một truy vấn nhiều bước có
đường đi bằng chứng.”

## Slide 27 — Demo 2: Phim chung

**Mục tiêu:** thực hiện bước 3–4 trong `defense-script.md`.

**Có thể nói gần như nguyên văn:**

> Ở bước 3, em hỏi trên Web UI: “Phim chung của Christian Bale và Tom Hardy?”.
> Hệ thống phải liên kết đúng hai Person, chọn intent `common_movies` và trả về
> The Dark Knight Rises.
>
> Ở bước 4, em chạy shared-neighbor pattern trong Neo4j Browser. Trên graph,
> Christian Bale và Tom Hardy cùng nối tới một Movie qua ACTED_IN. Movie chung
> chính là bằng chứng cho câu trả lời. Em chuyển giữa dạng bảng và dạng graph để
> cho thấy kết quả và đường đi là hai cách nhìn của cùng một pattern.

**Cần chỉ vào:** hai Person, Movie chung và pattern Person → Movie ← Person.

**Chuyển ý:** “Hai demo đầu kiểm chứng câu trả lời; demo cuối kiểm chứng lời
giải thích của một kết quả xếp hạng.”

## Slide 28 — Demo 3: Gợi ý phim

**Mục tiêu:** thực hiện bước 5–6 trong `defense-script.md`.

**Có thể nói gần như nguyên văn:**

> Ở bước 5, em chọn Inception trên Web UI và yêu cầu Top-5. Với phim đứng đầu,
> em mở phần giải thích để quan sát tổng điểm, các đặc trưng chung và contribution
> của từng đặc trưng.
>
> Ở bước 6, em dùng đúng tên phim đứng đầu làm candidate trong Neo4j Browser rồi
> truy vấn các đạo diễn, diễn viên, thể loại, từ khóa và hãng phim chung với
> Inception. Các shared feature phải khớp với explanation trên Web UI.
>
> Query trong Browser dùng để kiểm chứng bằng chứng graph. Điểm và thứ hạng vẫn
> do công thức IDF đầy đủ của ứng dụng tính. Vì vậy, demo không thay thế thuật
> toán xếp hạng mà chứng minh lời giải thích xuất phát từ dữ liệu thật trong
> graph.

**Cần chỉ vào:** phim nguồn, phim đứng đầu, contribution và shared features.

**Chuyển ý:** “Sau sáu bước demo, em quay lại phạm vi hiệu lực và những giới
hạn của kết quả.”

## Slide 29 — Giới hạn và hướng phát triển

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

## Slide 30 — Kết luận

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
