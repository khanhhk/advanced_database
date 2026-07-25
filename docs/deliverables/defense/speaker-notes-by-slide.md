# Nội dung thuyết trình theo từng slide

Tài liệu này bám theo bộ slide `movie_knowledge_graph_defense.pptx` gồm **25
slide, không có phụ lục**. Phần trong mục **Có thể nói gần như nguyên văn** là
kịch bản chính. Các mục **Cần chỉ vào** và **Chuyển ý** giúp thao tác tự nhiên,
không phải đọc thành tiếng.

Tổng thời gian gợi ý:

- Slide 1–6, nền tảng Knowledge Graph: khoảng 5 phút.
- Slide 7–13, thiết kế và dữ liệu: khoảng 4–5 phút.
- Slide 14–20, truy vấn, ứng dụng và đánh giá: khoảng 4–5 phút.
- Slide 21–23, demo: khoảng 4 phút.
- Slide 24–25, giới hạn và kết luận: khoảng 1 phút.

## Slide 1 — Knowledge Graph: Từ lý thuyết đến ứng dụng

**Mục tiêu:** giới thiệu đề tài và cấu trúc bài nói.

**Có thể nói gần như nguyên văn:**

> Kính thưa thầy, đề tài của em là Knowledge Graph, hay đồ thị tri thức. Trong
> phần đầu, em sẽ trình bày các kiến thức nền tảng gồm thực thể, quan hệ, schema,
> Property Graph, suy diễn và ngôn ngữ Cypher. Trong phần sau, em sử dụng dữ liệu
> phim như một nghiên cứu tình huống để minh họa cách các khái niệm này được
> triển khai thành một hệ thống hỏi–đáp và gợi ý phim có giải thích. Điểm em muốn
> nhấn mạnh là hệ thống không chỉ trả về kết quả, mà còn cho biết kết quả đó dựa
> trên những thực thể và quan hệ nào trong đồ thị.

**Cần chỉ vào:** tiêu đề, sơ đồ Movie Knowledge Graph bên phải.

**Chuyển ý:** “Trước hết, em xin bắt đầu từ câu hỏi: khi nào dữ liệu trở thành
tri thức?”

## Slide 2 — Từ dữ liệu đến tri thức có thể sử dụng

**Mục tiêu:** phân biệt dữ liệu, thông tin, tri thức và suy luận.

**Có thể nói gần như nguyên văn:**

> Bốn bậc trên slide thể hiện quá trình từ dữ liệu đến tri thức. Ở mức dữ liệu,
> chúng ta chỉ có những giá trị rời rạc như 2010, Inception và Nolan. Khi thêm
> ngữ cảnh, ta có thông tin: Inception là một bộ phim phát hành năm 2010. Khi nối
> các thực thể bằng một quan hệ có nghĩa, ta có tri thức: Christopher Nolan đạo
> diễn Inception. Cuối cùng, khi có thêm schema và quy tắc, hệ thống có thể suy
> ra một phát biểu mới, chẳng hạn Nolan là đạo diễn của một phim khoa học viễn
> tưởng. Vì vậy, Knowledge Graph chủ yếu tạo giá trị ở hai tầng cuối: biểu diễn
> tri thức và hỗ trợ suy luận.

**Cần chỉ vào:** lần lượt bốn bậc từ trái sang phải.

**Lưu ý:** “Suy luận” không có nghĩa hệ thống tự hiểu mọi thứ; kết luận chỉ có
thể được tạo ra từ những fact và quy tắc đã khai báo.

**Chuyển ý:** “Vậy một Knowledge Graph cụ thể được cấu tạo từ những thành phần
nào?”

## Slide 3 — Knowledge Graph là gì?

**Mục tiêu:** giải thích entity, relationship, property và identifier.

**Có thể nói gần như nguyên văn:**

> Trong phạm vi đề tài, em hiểu Knowledge Graph là một mô hình đồ thị gồm các
> thực thể có định danh, các quan hệ có ý nghĩa và một schema để máy có thể diễn
> giải dữ liệu. Ví dụ trên slide có hai thực thể là Christopher Nolan và
> Inception. Quan hệ DIRECTED cho biết Nolan đạo diễn bộ phim này. Ta có thể đọc
> fact đó theo dạng chủ thể, quan hệ, đối tượng: Nolan, DIRECTED, Inception.
> Ngoài node và cạnh, hệ thống còn lưu property như tên, ngày phát hành, rating,
> vai diễn hoặc thứ tự diễn viên. Định danh rất quan trọng vì tên chỉ là thuộc
> tính hiển thị; hai người có thể trùng tên và một phim có thể có nhiều tên gọi.

**Cần chỉ vào:** Nolan → DIRECTED → Inception, sau đó ba khối Entity,
Relationship và Property.

**Chuyển ý:** “Để các fact không được tạo ra tùy ý, Knowledge Graph cần một lớp
mô hình chung gọi là schema.”

## Slide 4 — Schema và instance

**Mục tiêu:** phân biệt mô hình khái niệm với dữ liệu cụ thể.

**Có thể nói gần như nguyên văn:**

> Slide này tách hai lớp. Bên trái là schema, tức lớp khái niệm. Schema quy định
> rằng Person và Movie là hai loại thực thể, và quan hệ DIRECTED đi từ Person
> đến Movie. Bên phải là instance data, tức các sự kiện cụ thể đang tồn tại:
> Nolan là một Person, Inception là một Movie, và Nolan DIRECTED Inception.
> Nói ngắn gọn, schema trả lời “loại dữ liệu và quan hệ nào được phép tồn tại”,
> còn instance trả lời “sự kiện cụ thể nào đang đúng trong tập dữ liệu”. Việc
> tách hai lớp giúp kiểm tra tính nhất quán và tái sử dụng mô hình cho nhiều dữ
> liệu khác nhau.

**Cần chỉ vào:** Schema ở trái, mũi tên “thể hiện”, Instance ở phải.

**Nếu được hỏi TBox/ABox:** TBox là các khái niệm và quan hệ chung; ABox là các
cá thể và fact cụ thể. Đây là cách giải thích khái niệm, không phải hai hệ quản
trị riêng trong project.

**Chuyển ý:** “Project hiện thực hóa hai lớp này bằng mô hình Property Graph.”

## Slide 5 — Property Graph

**Mục tiêu:** giải thích mô hình đồ thị duy nhất được dùng trong project.

**Có thể nói gần như nguyên văn:**

> Project chỉ triển khai một mô hình là Neo4j Property Graph. Trong mô hình này,
> node có label và property; relationship có loại, hướng và cũng có thể mang
> property. Hình trên slide chỉ là một ví dụ khái niệm tối giản gồm Person,
> ACTED_IN và Movie, chưa phải toàn bộ schema của ứng dụng. Điểm hữu ích là
> property có thể đặt ngay trên cạnh. Chẳng hạn character và cast_order mô tả
> lần một Person tham gia một Movie, nên chúng thuộc cạnh ACTED_IN chứ không
> thuộc riêng Person hoặc Movie. Schema Movie Knowledge Graph đầy đủ sẽ được
> trình bày ở slide 10.

**Cần chỉ vào:** một node Movie, một node Person và cạnh ACTED_IN trong sơ đồ.

**Lưu ý:** không nói project dùng thêm một mô hình RDF hay một graph thứ hai.

**Chuyển ý:** “Sau khi đã có mô hình, ta cần một ngôn ngữ để tạo ràng buộc,
truy vấn đường đi và áp dụng luật.”

## Slide 6 — Cypher cho truy vấn và suy diễn

**Mục tiêu:** giải thích hai vai trò của Cypher.

**Có thể nói gần như nguyên văn:**

> Cypher là ngôn ngữ truy vấn của Neo4j. Vai trò thứ nhất là tìm các mẫu đường
> đi trong graph. Ở ví dụ bên trái, query tìm một Person nối với Movie qua quan
> hệ DIRECTED; tên người được truyền bằng parameter. Vai trò thứ hai là vật chất
> hóa một luật nghiệp vụ. Nếu hai Person cùng có cạnh ACTED_IN tới một Movie, hệ
> thống có thể tạo quan hệ CO_STARRED_WITH giữa họ. Cạnh suy ra này lưu số phim
> chung, danh sách phim làm bằng chứng và cờ derived bằng true. Project không có
> một reasoner tách biệt; cả truy vấn và luật suy diễn đều được khai báo bằng
> Cypher và thực thi trong Neo4j.

**Cần chỉ vào:** khối `MATCH...RETURN` bên trái và `MATCH...MERGE` bên phải.

**Chuyển ý:** “Sau phần nền tảng, em chuyển sang nghiên cứu tình huống và giải
thích vì sao bài toán này chọn Neo4j.”

## Slide 7 — Vì sao chọn Neo4j?

**Mục tiêu:** nêu lợi ích đúng mức, không tuyên bố graph luôn nhanh hơn SQL.

**Có thể nói gần như nguyên văn:**

> Dữ liệu phim có nhiều quan hệ nhiều–nhiều: một phim có nhiều diễn viên, một
> diễn viên tham gia nhiều phim, và phim còn nối với đạo diễn, thể loại, từ khóa
> và hãng sản xuất. Mô hình bảng vẫn biểu diễn được bằng bảng nối và JOIN. Tuy
> nhiên, Property Graph biểu diễn các mối quan hệ thành cạnh trực tiếp, nên các
> câu hỏi nhiều bước và đường đi bằng chứng gần với cách mô tả nghiệp vụ hơn.
> Neo4j được chọn vì hỗ trợ traversal và relationship có property thuận tiện.
> Em không kết luận Neo4j luôn nhanh hơn cơ sở dữ liệu quan hệ; SQLite vẫn được
> dùng ở phần đánh giá như một baseline có kiểm soát.

**Cần chỉ vào:** hàng “Truy vấn nhiều bước” và khối “Property-rich
relationships”.

**Chuyển ý:** “Sau đây là luồng đầy đủ từ dữ liệu nguồn đến giao diện người
dùng.”

## Slide 8 — Kiến trúc đầu cuối

**Mục tiêu:** giúp người nghe thấy rõ luồng dữ liệu và luồng chạy ứng dụng.

**Có thể nói gần như nguyên văn:**

> Hệ thống bắt đầu từ TMDB và IMDb. Dữ liệu nguồn được lưu vào raw cache để có
> thể xử lý lại mà không phải gọi Internet. Bước processing làm sạch, ghép dữ
> liệu theo ID và chuẩn hóa thành các bảng node, edge. Sau đó dữ liệu được nạp
> vào Neo4j, tạo constraint và chạy luật CO_STARRED_WITH. FastAPI là lớp dịch vụ
> cho hỏi–đáp và gợi ý; Web UI là giao diện người dùng. Manifest và checksum giúp
> biết dữ liệu nào đã được xử lý và có cần import lại hay không. Sau khi đã nạp
> graph, phần demo có thể chạy offline.

**Cần chỉ vào:** đọc chuỗi sáu khối từ trái sang phải.

**Chuyển ý:** “Trong hai nguồn dữ liệu, TMDB là nguồn graph chính, còn IMDb chỉ
bổ sung rating theo một cách tiết kiệm lưu trữ.”

## Slide 9 — Tích hợp IMDb

**Mục tiêu:** giải thích exact join và chiến lược streaming.

**Có thể nói gần như nguyên văn:**

> TMDB cung cấp phim, credits, thể loại, từ khóa và hãng sản xuất, nên đây là
> nguồn chính tạo graph. IMDb chỉ được dùng để bổ sung `imdb_rating` và
> `imdb_votes`. Hệ thống không tải toàn bộ IMDb vào Neo4j mà chỉ đọc tuần tự tệp
> `title.ratings.tsv.gz` khi nó vẫn đang nén. Phép ghép sử dụng chính xác
> `imdb_id` từ TMDB với `tconst` của IMDb, không ghép theo tên phim. Có 4.558
> Movie mang IMDb ID và 4.351 Movie ghép được rating, tương đương 95,5 phần
> trăm. Rating của TMDB và IMDb được giữ ở hai trường riêng để không làm mất
> nguồn gốc.

**Cần chỉ vào:** luồng exact ID và ba con số 4.558, 4.351, 95,5%.

**Chuyển ý:** “Sau khi tích hợp nguồn, dữ liệu được tổ chức theo schema sau.”

## Slide 10 — Mô hình dữ liệu

**Mục tiêu:** giải thích node, edge, stable ID và vai trò trên cạnh.

**Có thể nói gần như nguyên văn:**

> Schema gồm năm loại node chính: Movie, Person, Genre, Keyword và Studio; cùng
> năm loại quan hệ gốc. Project chỉ dùng một label Person vì một người có thể vừa
> là diễn viên vừa là đạo diễn. Vai trò được thể hiện bằng quan hệ ACTED_IN hoặc
> DIRECTED. Khóa của Person dựa trên stable source ID, ví dụ `tmdb:<id>`, chứ
> không dựa trên tên. Cạnh ACTED_IN lưu character, cast_order và source.
> Constraint và index được tạo trước khi import để chặn trùng ID và hỗ trợ truy
> vấn.

**Cần chỉ vào:** Person, Movie, ACTED_IN và ba khối bên phải.

**Chuyển ý:** “Để tạo được graph này một cách lặp lại, project sử dụng pipeline
gồm tám bước.”

## Slide 11 — Pipeline dữ liệu

**Mục tiêu:** giải thích khả năng tái lập và import idempotent.

**Có thể nói gần như nguyên văn:**

> Pipeline đi từ collect, cache, clean, ghép IMDb, normalize, nạp Neo4j, chạy
> rule và cuối cùng là validate. Raw cache được xem là bất biến, nên có thể tái
> hiện việc xử lý trên cùng một snapshot. Kết quả chuẩn hóa được lưu thành các
> bảng node và edge cùng manifest về số lượng và checksum. Khi import, hệ thống
> tạo node trước, edge sau và sử dụng MERGE theo batch. Vì vậy chạy lại cùng dữ
> liệu không tạo bản ghi trùng; đây là tính idempotent. Runtime chỉ import lại
> khi checksum của dữ liệu processed hoặc số lượng Movie trong graph thay đổi.

**Cần chỉ vào:** tám bước từ Collect đến Validate; bốn khối Cache, Manifest,
MERGE, Gate.

**Chuyển ý:** “Kết quả của pipeline phải vượt qua quality gate trước khi được
dùng cho ứng dụng.”

## Slide 12 — Chất lượng graph

**Mục tiêu:** trình bày quy mô và các kiểm tra cấu trúc.

**Có thể nói gần như nguyên văn:**

> Với 5.000 bản ghi đầu vào, một Movie không có bất kỳ quan hệ nào bị loại và
> graph hợp lệ còn 4.999 Movie. Toàn graph có 76.612 node và 846.309
> relationship. Các quality gate kiểm tra orphan Movie, stable ID trùng, thiếu
> thuộc tính bắt buộc và cạnh sai kiểu hoặc sai đầu mút. Kết quả đều bằng không.
> Điều này chứng minh snapshot đạt tính toàn vẹn cấu trúc theo các quy tắc đã
> công bố; nó không có nghĩa dữ liệu nguồn ngoài đời hoàn hảo về mọi mặt.

**Cần chỉ vào:** “0 vi phạm cấu trúc” và bốn dấu kiểm.

**Chuyển ý:** “Một nguyên nhân quan trọng giúp tránh nối sai thực thể là chiến
lược exact trước, fuzzy sau.”

## Slide 13 — Phân giải thực thể

**Mục tiêu:** giải thích exact match, fuzzy fallback, confidence và abstention.

**Có thể nói gần như nguyên văn:**

> Phân giải thực thể là xác định hai bản ghi hoặc một cụm từ truy vấn đang nói
> đến thực thể nào. Hệ thống ưu tiên exact ID. Với câu hỏi của người dùng, entity
> linker ưu tiên exact và full-text candidate, sau đó mới fuzzy reranking. Nếu
> kết quả không đủ chắc chắn hoặc bị hòa điểm, hệ thống có thể abstain, tức từ
> chối liên kết thay vì đoán. Trên 100 cặp silver, precision đạt 1,000, recall
> 0,933 và F1 0,966. Năm trường hợp bị bỏ sót là các lần abstain bảo thủ; không
> có false positive trong tập đánh giá này.

**Cần chỉ vào:** luồng xử lý và ba metric bên phải.

**Lưu ý:** silver corpus là tập đánh giá được sinh có kiểm soát, không phải
ground truth độc lập từ người dùng.

**Chuyển ý:** “Khi thực thể đã được xác định, câu hỏi quan hệ được chuyển thành
một mẫu Cypher có tham số.”

## Slide 14 — Cypher và pattern nhiều bước

**Mục tiêu:** đọc được query và giải thích parameterization.

**Có thể nói gần như nguyên văn:**

> Query minh họa bắt đầu từ một Person đóng vai trò đạo diễn, đi qua Movie và
> sang Genre. Nó đếm số phim theo từng đạo diễn trong một thể loại, rồi sắp xếp
> giảm dần. Điểm cần chú ý là `$genre` và `$limit` được truyền như parameter;
> chuỗi người dùng không được ghép trực tiếp vào cấu trúc query. Catalog của hệ
> thống có các nhóm lookup, aggregation, multi-hop, shortest path và similarity.
> Vì pattern trong query gần với đường đi trong graph, ta có thể đọc tương đối
> trực tiếp câu hỏi mà query đang trả lời.

**Cần chỉ vào:** pattern `Person → Movie → Genre`, rồi `$genre` và `$limit`.

**Chuyển ý:** “Ngoài việc đọc các cạnh gốc, Cypher còn tạo một loại cạnh suy ra
có thể kiểm chứng.”

## Slide 15 — Suy diễn CO_STARRED_WITH

**Mục tiêu:** phân biệt asserted fact và derived fact.

**Có thể nói gần như nguyên văn:**

> ACTED_IN là asserted fact, tức sự kiện được lấy trực tiếp từ credits của TMDB.
> Nếu hai Person cùng tham gia một Movie, ta áp dụng luật để tạo
> CO_STARRED_WITH; đây là derived fact, tức sự kiện suy ra. Cạnh mới không chỉ
> ghi rằng hai người từng đóng chung, mà còn lưu `movie_count`,
> `evidence_movie_ids` và `derived=true`. Nhờ đó ta có thể lần ngược từ kết luận
> về những bộ phim làm bằng chứng. Đây là suy diễn minh bạch bằng một luật Cypher
> cụ thể, không phải kết luận do mô hình AI tự tạo.

**Cần chỉ vào:** hai cạnh ACTED_IN hội tụ vào Movie, rồi cạnh
CO_STARRED_WITH.

**Chuyển ý:** “Các query và fact này được đưa đến người dùng qua hai ứng dụng;
đầu tiên là hỏi–đáp.”

## Slide 16 — Hệ hỏi–đáp

**Mục tiêu:** giải thích Web UI không tự sinh Cypher.

**Có thể nói gần như nguyên văn:**

> Người dùng nhập câu hỏi tự nhiên trên Web UI. Backend nhận diện một trong chín
> intent cố định và trích các slot như tên phim hoặc tên người. Entity linker
> chuẩn hóa những tên này về đúng node trong graph và trả cả confidence. Sau đó
> query catalog chọn một template Cypher cố định; Neo4j thực hiện traversal và
> trả kết quả. Response gồm câu trả lời cùng intent, thực thể đã liên kết, bằng
> chứng graph và độ trễ. Vì vậy chatbot chỉ điều phối một quy trình xác định; nó
> không sinh Cypher tự do và không thay thế Neo4j.

**Cần chỉ vào:** trình tự Web UI → parser → entity linker → catalog → Neo4j.

**Chuyển ý:** “Ứng dụng thứ hai cũng khai thác các đường nối trong graph, nhưng
để xếp hạng phim tương tự.”

## Slide 17 — Gợi ý phim có giải thích

**Mục tiêu:** giải thích shared feature, type weight và IDF.

**Có thể nói gần như nguyên văn:**

> Hệ gợi ý tìm các phim có đặc trưng chung với phim nguồn qua đạo diễn, diễn
> viên, thể loại, từ khóa và hãng sản xuất. Mỗi đặc trưng chung tạo một
> contribution. `type_weight` cho phép ưu tiên loại quan hệ, ví dụ đạo diễn có
> trọng số 3, diễn viên 2, thể loại 1,5 và từ khóa 1. Thành phần IDF làm giảm ảnh
> hưởng của đặc trưng quá phổ biến và tăng giá trị của đặc trưng hiếm. Tổng các
> contribution tạo thành điểm xếp hạng. Điểm và phần giải thích đều được tính từ
> traversal trong Neo4j; ứng dụng không tải toàn bộ graph về Python.

**Cần chỉ vào:** công thức, bốn trọng số và khối “Điểm được tính trong Neo4j”.

**Nếu được hỏi vì sao dùng IDF:** hai phim cùng một thể loại rất phổ biến chưa
chắc giống nhau nhiều; cùng một đạo diễn hoặc một keyword hiếm thường mang nhiều
thông tin hơn.

**Chuyển ý:** “Để biết các thành phần trên hoạt động đến đâu, mỗi tuyên bố được
gắn với một phép đánh giá riêng.”

## Slide 18 — Thiết kế đánh giá

**Mục tiêu:** giải thích đánh giá theo claim và giới hạn của silver corpus.

**Có thể nói gần như nguyên văn:**

> Project không dùng một con số duy nhất để kết luận toàn hệ thống tốt. Chất
> lượng dữ liệu được đo trên toàn corpus. Entity resolution dùng 100 cặp silver.
> Suy diễn co-star dùng 50 fact silver. QA dùng 20 câu smoke test có evidence.
> Gợi ý dùng 20 case và đo P@10, NDCG@10. Hiệu năng được đo trên bốn quy mô và
> bốn query, với một warm-up và 100 lần chạy. Silver corpus được sinh tất định,
> có provenance và rubric công bố, nhưng không phải ground truth độc lập từ
> người dùng. Vì vậy các kết luận chỉ có giá trị trong snapshot và protocol này.

**Cần chỉ vào:** từng hàng trong bảng, sau đó ba cảnh báo bên phải.

**Chuyển ý:** “Với protocol đó, các kết quả chính như sau.”

## Slide 19 — Kết quả chính

**Mục tiêu:** đọc đúng metric và không suy rộng.

**Có thể nói gần như nguyên văn:**

> QA smoke test đạt 20 trên 20 câu và mọi câu đều có evidence. Entity resolution
> đạt F1 bằng 0,966. Suy diễn co-star đạt precision 1,00 trên 50 fact silver.
> Hệ gợi ý đạt P@10 bằng 0,635 và NDCG@10 bằng 0,672 trên 20 case silver. Các con
> số này cho thấy pipeline và ứng dụng hoạt động nhất quán theo tập kiểm thử đã
> công bố. Tuy nhiên, chúng chưa thay thế đánh giá người dùng độc lập, đặc biệt
> với chất lượng gợi ý. Điểm mạnh quan trọng là mọi output gợi ý đều có đường
> giải thích.

**Cần chỉ vào:** lần lượt 20/20, 0,966, 1,00, 0,635 và 0,672.

**Chuyển ý:** “Kết quả benchmark cũng cho thấy cần trình bày lợi ích của graph
một cách thận trọng.”

## Slide 20 — Benchmark và sự đánh đổi

**Mục tiêu:** nói rõ SQLite nhanh hơn và giá trị thật của graph.

**Có thể nói gần như nguyên văn:**

> Trong phép đo cùng snapshot, cùng máy, cùng warm-up và cùng 100 lần chạy,
> SQLite nhanh hơn Neo4j ở tất cả các cặp query và quy mô đã đo. Biểu đồ bên trái
> minh họa query common movies: khi quy mô tăng, độ trễ của cả hai hệ thống đều
> tăng. Vì vậy, project không dùng tốc độ tuyệt đối làm lý do để chọn graph. Giá
> trị của Neo4j ở đây là mô hình quan hệ, traversal và khả năng trả bằng chứng
> trực tiếp. Biểu đồ bên phải là lịch sử thử các ranker; runtime hiện tại chỉ
> dùng IDF-weighted graph similarity. Benchmark này chưa đo cold cache,
> concurrency hoặc dữ liệu lớn hơn 4.999 phim.

**Cần chỉ vào:** hai đường Neo4j/SQLite và ghi chú giới hạn dưới biểu đồ.

**Chuyển ý:** “Sau phần kết quả, em xin demo đúng luồng người dùng trước và kiểm
chứng trực tiếp trên Neo4j ngay sau đó.”

## Slide 21 — Demo QA lookup

**Mục tiêu:** chạy Web UI trước, Browser sau và đối chiếu cùng fact.

**Nói trước khi thao tác:**

> Ở ví dụ đầu tiên, em dùng Web UI để hỏi bằng ngôn ngữ tự nhiên, sau đó chạy
> Cypher trên Neo4j Browser để kiểm chứng cùng một fact.

**Thao tác và lời nói:**

1. Mở `http://127.0.0.1:8000/`, dán:

   ```text
   Diễn viên nào đóng trong phim Inception?
   ```

2. Khi có kết quả, nói:

   > UI đã liên kết “Inception” với một Movie cụ thể và trả danh sách diễn viên,
   > vai diễn cùng evidence.

3. Mở `http://127.0.0.1:7474/`, dán query trên slide và chạy.
4. Chuyển sang bảng kết quả, nói:

   > Browser truy vấn trực tiếp cùng graph Neo4j. Danh sách tên ở hai giao diện
   > phải thống nhất; Web UI chỉ bổ sung bước hiểu câu hỏi và định dạng câu trả
   > lời.

**Nếu lỗi:** UI lỗi thì dùng Swagger; Browser lỗi thì giữ kết quả UI và nói rõ
backend vẫn đang truy vấn Neo4j thật.

**Chuyển ý:** “Ví dụ tiếp theo đi qua hai cạnh thay vì chỉ tra cứu một quan hệ.”

## Slide 22 — Demo QA multi-hop

**Mục tiêu:** minh họa shared-neighbor pattern.

**Nói trước khi thao tác:**

> Câu hỏi thứ hai yêu cầu tìm một Movie là hàng xóm chung của hai Person, nên đây
> là truy vấn multi-hop.

**Thao tác và lời nói:**

1. Trên Web UI, dán:

   ```text
   Phim chung của Christian Bale và Tom Hardy?
   ```

2. Khi có kết quả, nói:

   > Hệ thống liên kết hai tên người, chọn intent tìm phim chung và trả về The
   > Dark Knight Rises cùng hai cạnh ACTED_IN làm evidence.

3. Chạy query trên slide trong Neo4j Browser.
4. Nếu muốn minh họa bằng graph, thay phần `RETURN` bằng:

   ```cypher
   RETURN a, m, b;
   ```

5. Nói:

   > Pattern cần tìm là Person đi tới Movie và từ Movie đi ngược về Person còn
   > lại. Đây chính là đường Person → Movie ← Person.

**Chuyển ý:** “QA kiểm chứng kết quả trả lời; ví dụ cuối kiểm chứng phần giải
thích của một kết quả gợi ý.”

## Slide 23 — Demo gợi ý và kiểm chứng evidence

**Mục tiêu:** phân biệt kiểm chứng evidence với tái tính toàn bộ ranking.

**Nói trước khi thao tác:**

> Với gợi ý phim, Web UI chịu trách nhiệm chạy query xếp hạng đầy đủ. Browser sẽ
> được dùng để kiểm chứng các shared feature tạo phần giải thích.

**Thao tác và lời nói:**

1. Chuyển sang tab Gợi ý, nhập `Inception`, chọn phim năm 2010 và chạy Top 5.
2. Ghi lại tên phim đứng đầu và mở phần giải thích.
3. Trong Browser, đổi parameter thành đúng tên phim vừa nhận:

   ```cypher
   :param candidate_title => 'Interstellar';
   ```

4. Chạy query kiểm chứng trên slide.
5. Đối chiếu `shared_features` với explanation trên Web UI và nói:

   > Kết quả Browser cho biết hai phim có chung những node nào theo từng loại
   > quan hệ. Các feature này phải xuất hiện trong phần giải thích của UI. Query
   > rút gọn chỉ kiểm chứng evidence; điểm contribution và thứ hạng chính xác do
   > query IDF đầy đủ của ứng dụng tính trong Neo4j.

**Lưu ý:** nếu phim đứng đầu không phải Interstellar, phải thay parameter bằng
đúng tên đang hiển thị trên Web UI.

**Chuyển ý:** “Ba ví dụ vừa rồi cũng cho thấy ranh giới hiện tại của hệ thống.”

## Slide 24 — Giới hạn và hướng phát triển

**Mục tiêu:** chủ động nêu giới hạn và hướng xử lý tương ứng.

**Có thể nói gần như nguyên văn:**

> Project có bốn giới hạn chính. Thứ nhất, QA chỉ hỗ trợ chín intent, chưa phải
> open-domain QA; hướng phát triển là thu thập câu hỏi thực tế rồi mở rộng intent
> theo nhu cầu. Thứ hai, phần lớn corpus đánh giá là silver, nên cần đánh giá
> người dùng và người chấm độc lập. Thứ ba, quy mô hiện tại tối đa 4.999 Movie và
> benchmark chưa đo concurrent hoặc cold cache; cần thử graph lớn hơn và tải
> đồng thời. Thứ tư, dữ liệu credits chỉ lấy top 20 cast và IMDb mới enrich
> Movie; tương lai có thể mở rộng credits và liên kết thêm nguồn cho Person.

**Cần chỉ vào:** mỗi giới hạn bên trái và hướng phát triển tương ứng bên phải.

**Chuyển ý:** “Từ phạm vi và bằng chứng hiện có, em rút ra ba kết luận.”

## Slide 25 — Kết luận

**Mục tiêu:** trả lời ngắn gọn đề tài đã làm được gì.

**Có thể nói gần như nguyên văn:**

> Tóm lại, đề tài đạt ba kết quả chính. Thứ nhất, hệ thống tích hợp TMDB và IMDb
> bằng stable ID, giữ provenance và có quy trình chạy lại được. Thứ hai, dữ liệu
> được mô hình hóa bằng Neo4j Property Graph, hỗ trợ Cypher multi-hop và fact suy
> ra có bằng chứng. Thứ ba, hai ứng dụng hỏi–đáp và gợi ý đều trả kết quả kèm
> thực thể, đường đi hoặc đóng góp điểm để người dùng kiểm chứng. Thông điệp cuối
> cùng của đề tài là: đồ thị tri thức tạo giá trị không chỉ vì kết nối được dữ
> liệu, mà vì mỗi kết luận có thể lần ngược về quan hệ và bằng chứng đã tạo ra
> nó. Em xin cảm ơn thầy và xin lắng nghe câu hỏi, phản biện.

**Cần chỉ vào:** ba kết luận Tích hợp đúng, Truy vấn được, Giải thích được.

## Cách sử dụng tài liệu khi thuyết trình

- In hai mặt và đánh dấu màu các câu chuyển ý.
- Không đọc tiêu đề slide rồi mới đọc lại toàn bộ chữ trên slide.
- Với slide 13, 14, 19, 20 và 21, đọc đúng phạm vi của metric; không bỏ câu giới
  hạn.
- Với slide 21–23, mở sẵn Web UI và Neo4j Browser trước khi bắt đầu trình bày.
- Nếu thiếu thời gian, rút ngắn slide 10–16, nhưng giữ phần lý thuyết 2–7, ba
  slide demo và kết luận.
- Trước ngày bảo vệ, kiểm tra lại các con số trong `experiments/results/` nếu
  pipeline được chạy lại.
