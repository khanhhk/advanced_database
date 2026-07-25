# Hiểu Movie Knowledge Graph từ con số 0

Tài liệu này dành cho người mới mở repository lần đầu, chưa biết đồ thị tri thức,
Neo4j, Cypher hay cấu trúc project Python. Sau khi đọc xong, bạn nên trả lời được:

- Project giải quyết bài toán gì?
- Dữ liệu đi từ Internet đến giao diện bằng cách nào?
- Neo4j lưu những gì và tại sao không chỉ dùng bảng SQL?
- Hỏi–đáp và gợi ý phim hoạt động ra sao?
- Muốn chạy, kiểm thử hoặc sửa một chức năng thì bắt đầu ở file nào?

Nếu chỉ có 5 phút, đọc mục 1–4. Nếu cần chạy project, đọc tiếp mục 5. Nếu cần
sửa code hoặc bảo vệ đồ án, đọc toàn bộ tài liệu.

## 1. Project này làm gì?

Đây là một hệ thống **đồ thị tri thức phim** (Movie Knowledge Graph). Nó gom dữ
liệu phim từ TMDB và rating từ IMDb, biến dữ liệu đó thành một mạng lưới các
thực thể có quan hệ, rồi cung cấp hai chức năng chính:

1. Hỏi bằng tiếng Việt về phim và người làm phim.
2. Gợi ý phim tương tự, kèm lý do có thể kiểm tra được.

Ví dụ, thay vì chỉ lưu một dòng:

```text
Inception | 2010 | Science Fiction | Christopher Nolan
```

hệ thống biểu diễn các sự kiện riêng:

```text
(Christopher Nolan) -[DIRECTED]-> (Inception)
(Leonardo DiCaprio) -[ACTED_IN]-> (Inception)
(Inception) -[HAS_GENRE]-> (Science Fiction)
(Inception) -[HAS_KEYWORD]-> (Dream)
```

Nhờ vậy, hệ thống có thể đi qua nhiều quan hệ để trả lời các câu như:

- Christopher Nolan đạo diễn những phim nào?
- Leonardo DiCaprio từng đóng chung với ai?
- Christian Bale và Tom Hardy có phim chung nào?
- Leonardo DiCaprio liên hệ với Christian Bale qua những phim/người nào?
- Phim nào giống Inception và giống vì đạo diễn, diễn viên hay thể loại?

Project không dùng mô hình ngôn ngữ để tự sinh câu Cypher. Nó nhận diện một tập
ý định đã biết, liên kết tên trong câu hỏi với thực thể thật, rồi chạy truy vấn
Cypher cố định có tham số. Đây là lựa chọn có chủ ý để kết quả xác định, an toàn
và dễ kiểm thử.

## 2. Đồ thị tri thức là gì?

### 2.1. Ba khái niệm cần nhớ

Một đồ thị trong project có:

- **Node (nút):** một thực thể, ví dụ phim, người, thể loại.
- **Relationship (quan hệ/cạnh):** kết nối có ý nghĩa giữa hai node.
- **Property (thuộc tính):** dữ liệu mô tả node hoặc relationship.

Ví dụ:

```text
Node Person:
  person_id = "tmdb:525"
  name = "Christopher Nolan"

Relationship DIRECTED:
  Christopher Nolan -> Inception

Node Movie:
  tmdb_id = 27205
  title = "Inception"
  rating = 8.4
```

`person_id` và `tmdb_id` là khóa ổn định. Tên không được dùng làm khóa vì hai
người có thể trùng tên, và tên có thể bị viết sai.

### 2.2. Schema đang dùng

Hệ thống có năm loại node chính:

| Node | Ý nghĩa | Khóa chính |
|---|---|---|
| `Movie` | Phim | `tmdb_id` |
| `Person` | Người, có thể là diễn viên và/hoặc đạo diễn | `person_id` |
| `Genre` | Thể loại | `genre_id` |
| `Keyword` | Từ khóa nội dung | `keyword_id` |
| `Studio` | Công ty sản xuất | `company_id` |

Các quan hệ gốc:

| Relationship | Hướng | Ý nghĩa | Thuộc tính đáng chú ý |
|---|---|---|---|
| `ACTED_IN` | `Person → Movie` | Người đóng trong phim | `character`, `cast_order` |
| `DIRECTED` | `Person → Movie` | Người đạo diễn phim | nguồn dữ liệu |
| `HAS_GENRE` | `Movie → Genre` | Phim thuộc thể loại | nguồn dữ liệu |
| `HAS_KEYWORD` | `Movie → Keyword` | Phim có từ khóa | nguồn dữ liệu |
| `PRODUCED_BY` | `Movie → Studio` | Phim do studio sản xuất | nguồn dữ liệu |

Một quan hệ được suy ra:

| Relationship | Ý nghĩa |
|---|---|
| `CO_STARRED_WITH` | Hai người đã cùng diễn trong ít nhất một phim |

`CO_STARRED_WITH` không đến trực tiếp từ TMDB. Importer suy ra nó từ hai cạnh
`ACTED_IN`, rồi lưu `movie_count`, `evidence_movie_ids` và `derived: true`.
Vì thế có thể giải thích quan hệ bằng chính các phim làm bằng chứng.

### 2.3. Tại sao dùng Neo4j?

Miền phim có rất nhiều quan hệ nhiều-nhiều: một phim có nhiều diễn viên, một
diễn viên đóng nhiều phim, một phim có nhiều thể loại và từ khóa. Các câu hỏi
quan trọng thường phải đi qua nhiều bước.

Neo4j phù hợp vì Cypher diễn đạt trực tiếp mẫu quan hệ:

```cypher
MATCH (person:Person)-[:ACTED_IN]->(movie:Movie)
RETURN person.name, movie.title;
```

Điều này không có nghĩa graph luôn nhanh hơn SQL. Benchmark của project cho thấy
SQLite nhanh hơn ở tất cả các cặp truy vấn/quy mô đã đo. Neo4j được chọn vì mô
hình và traversal dễ diễn đạt, quan hệ có thể mang thuộc tính, và đường bằng
chứng dễ truy lại.

## 3. Bức tranh toàn hệ thống

Hãy coi repository như một dây chuyền gồm bốn tầng:

```text
Nguồn Internet
  TMDB API + IMDb ratings
          |
          v
Chuẩn bị dữ liệu
  raw cache -> làm sạch -> CSV node/edge + manifest
          |
          v
Kho tri thức
  Neo4j Property Graph
          |
          v
Ứng dụng
  FastAPI -> hỏi đáp / gợi ý -> Web UI
```

### 3.1. Tầng dữ liệu

TMDB là nguồn chính cho phim, diễn viên, đạo diễn, thể loại, keyword và studio.
IMDb chỉ bổ sung `imdb_rating` và `imdb_votes`.

Hai loại rating được giữ riêng:

- `rating`: rating của TMDB.
- `imdb_rating`: rating của IMDb.

Dữ liệu tải về được cache ở `data/raw/`. Pipeline không sửa cache này mà sinh
đầu ra mới ở `data/processed/`. Cách tách này giúp chạy lại mà không gọi mạng,
không tốn quota API và truy được dữ liệu đã tạo ra kết quả.

### 3.2. Tầng xử lý

Pipeline:

1. Đọc JSON đã cache từ TMDB.
2. Làm sạch kiểu dữ liệu và trường bắt buộc.
3. Giữ ID nguồn ổn định cho mọi thực thể.
4. Gộp credit trùng của cùng người trong cùng phim.
5. Đọc trực tiếp file IMDb nén và exact-join bằng `imdb_id`.
6. Loại phim không có bất kỳ quan hệ graph nào.
7. Ghi năm bảng node, năm bảng edge và `manifest.json`.

`manifest.json` là “phiếu xuất xưởng” của dataset: checksum, số dòng, độ bao phủ,
số record lỗi và các chỉ số chất lượng.

### 3.3. Tầng lưu trữ

Importer tạo constraint/index, nhập node trước, nhập edge sau, rồi suy ra
`CO_STARRED_WITH`. Nó dùng `MERGE` theo stable ID nên chạy lại không tạo thêm
bản sao.

`make demo` cũng không import lại vô điều kiện. Runtime so checksum của toàn bộ
CSV đã xử lý và số Movie đang có trong Neo4j. Nếu mọi thứ khớp, graph cũ được
tái sử dụng.

### 3.4. Tầng ứng dụng

FastAPI mở:

| Endpoint | Dùng để làm gì |
|---|---|
| `GET /` | Giao diện web |
| `GET /health` | Kiểm tra Neo4j có sẵn sàng không |
| `GET /stats` | Thống kê node/relationship |
| `GET /entities/search` | Tìm thực thể cho autocomplete/linking |
| `POST /ask` | Hỏi đáp tiếng Việt |
| `POST /recommend` | Gợi ý phim có giải thích |

Backend thật luôn là Neo4j. Dữ liệu nhỏ trong `tests/fixtures/` chỉ phục vụ test,
không phải fallback cho demo.

## 4. Hai chức năng chính hoạt động như thế nào?

### 4.1. Hỏi–đáp

Ví dụ đầu vào:

```text
Những phim nào do Christopher Nolan đạo diễn?
```

Luồng xử lý:

```text
Câu hỏi
  -> parser nhận diện intent "movies_by_director"
  -> trích slot "Christopher Nolan"
  -> entity linker tìm Person canonical và person_id
  -> chọn Cypher cố định cho intent
  -> truyền person_id bằng parameter
  -> Neo4j trả các Movie
  -> service tạo câu trả lời + evidence
```

Hệ thống hỗ trợ chín intent:

| Intent trong code | Ví dụ câu hỏi |
|---|---|
| `movies_by_director` | Những phim nào do Christopher Nolan đạo diễn? |
| `movies_by_person` | Tìm phim của Clint Eastwood |
| `actors_in_movie` | Diễn viên nào đóng trong phim Inception? |
| `common_movies` | Phim chung của Christian Bale và Tom Hardy? |
| `movies_by_genre_rating` | Phim action rating trên 8 |
| `co_stars` | Ai đóng chung với Leonardo DiCaprio? |
| `directors_by_genre` | Đạo diễn nào làm thể loại science fiction? |
| `shortest_path` | Đường liên hệ giữa Leonardo DiCaprio và Christian Bale? |
| `similar_movies` | Phim tương tự Inception? |

Câu ngoài các mẫu hỗ trợ trả intent `unknown`; hệ thống không đoán rồi chạy một
truy vấn tự sinh.

Entity linker tồn tại vì người dùng có thể gõ sai như `Cristopher Nolan`, hoặc
hai phim có tên gần giống. Candidate được tìm trong Neo4j, exact/full-text trước,
fuzzy rerank sau. Kết quả linking và confidence được đưa vào evidence.

Các lớp source liên quan:

```text
src/qa/intents.py
  -> src/qa/entity_linker.py
  -> src/qa/neo4j_service.py
  -> src/kg/query_catalog.py
  -> src/kg/repository.py
```

### 4.2. Gợi ý phim

Người dùng chọn một phim, ví dụ Inception (`tmdb_id = 27205`). Neo4j tìm các
phim có chung:

- đạo diễn;
- diễn viên;
- thể loại;
- keyword;
- studio.

Không phải đặc trưng chung nào cũng đáng giá như nhau. Một đặc trưng rất phổ
biến, chẳng hạn thể loại Drama, cung cấp ít thông tin hơn một đạo diễn hoặc
keyword hiếm. Project dùng trọng số IDF:

```text
điểm đặc trưng =
  trọng số loại * (1 + ln((tổng số phim + 1) / (số phim có đặc trưng + 1)))
```

Điểm phim là tổng đóng góp của các đặc trưng chung. API trả cả danh sách đặc
trưng để tạo lời giải thích như “cùng đạo diễn Christopher Nolan, cùng thể loại
Science Fiction”.

Đây là thuật toán duy nhất ở runtime. Các phương pháp cũ trong kết quả lịch sử
chỉ dùng để so sánh thiết kế, không phải tùy chọn cho người dùng.

Các lớp source liên quan:

```text
src/recommendation/neo4j_service.py
  -> src/recommendation/service.py
  -> src/kg/repository.py
```

## 5. Chạy project lần đầu

### 5.1. Cần cài gì?

- Python 3.11 trở lên.
- Docker và Docker Compose.
- `make`.
- Dữ liệu đã xử lý trong `data/processed/`, hoặc TMDB API key để tạo dữ liệu mới.

Kiểm tra nhanh:

```bash
python3 --version
docker --version
docker compose version
make --version
```

### 5.2. Trường hợp A — đã có snapshot xử lý

Đây là đường ngắn nhất:

```bash
make setup
make demo
```

`make setup` tạo `.env`, `.venv` và cài project. Không cần tự activate virtual
environment vì Makefile luôn gọi executable trong `.venv`.

`make demo`:

1. Khởi động Neo4j.
2. Kiểm tra `data/processed/manifest.json`.
3. Import hoặc tái sử dụng graph.
4. Chạy FastAPI/Uvicorn ở foreground.

Mở:

- Web UI: <http://127.0.0.1:8000/>
- Swagger/OpenAPI: <http://127.0.0.1:8000/docs>
- Neo4j Browser: <http://127.0.0.1:7474/>

Đăng nhập Neo4j local:

```text
Username: neo4j
Password: change-me
```

Nhấn `Ctrl+C` để dừng Uvicorn. Sau đó chạy:

```bash
make stop
```

Lệnh này dừng container nhưng giữ volume dữ liệu Neo4j.

### 5.3. Trường hợp B — chưa có snapshot xử lý

Mở `.env`, điền:

```dotenv
TMDB_API_KEY=your-key-here
```

Sau đó:

```bash
make setup
make data DATA_COUNT=2000
make demo
```

`DATA_COUNT` được hỗ trợ trong khoảng 2.000–5.000 phim. Bước `make data` cần
Internet, tải IMDb ratings và gọi TMDB. Không commit `.env` hay raw dataset.

### 5.4. Gọi API không qua giao diện

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Những phim nào do Christopher Nolan đạo diễn?"}'
```

```bash
curl -X POST http://127.0.0.1:8000/recommend \
  -H 'Content-Type: application/json' \
  -d '{"movie_id":27205,"top_k":3}'
```

`movie_id` là TMDB ID, không phải vị trí của phim trong danh sách.

## 6. Bản đồ repository

| Đường dẫn | Vai trò | Khi nào cần đọc? |
|---|---|---|
| `src/ingestion/` | Tải/cache TMDB và IMDb | Sửa nguồn dữ liệu |
| `src/processing/` | Làm sạch, entity resolution, sinh CSV | Sửa schema/quality |
| `src/kg/` | Import Neo4j, repository và CRUD | Sửa lớp lưu trữ/query |
| `src/qa/` | Intent, entity linking, trả lời | Thêm/sửa loại câu hỏi |
| `src/recommendation/` | Chấm điểm và giải thích gợi ý | Sửa thuật toán ranking |
| `src/api/` | FastAPI và web tĩnh | Sửa API/UI |
| `src/runtime/` | Quyết định import hay reuse graph | Sửa startup |
| `cypher/` | Constraint, query mẫu, reasoning | Làm việc trực tiếp với Cypher |
| `tests/` | Unit, API và integration test | Kiểm chứng thay đổi |
| `experiments/` | Corpus, evaluation, benchmark, reporting | Tái lập số liệu |
| `experiments/results/` | Artifact kết quả đã commit | Kiểm tra claim báo cáo |
| `docs/` | Tài liệu kỹ thuật/vận hành/nộp bài | Hiểu và demo project |
| `report_latex/` | Source báo cáo chính thức | Chỉnh báo cáo Overleaf |
| `data/raw/` | Cache nguồn, không commit | Debug ingestion |
| `data/processed/` | CSV graph + manifest, không commit | Debug/import snapshot |

### 6.1. Thư mục `cypher/`: câu lệnh dành cho Neo4j

Cypher là ngôn ngữ truy vấn graph của Neo4j. Nếu SQL thường mô tả bảng và phép
`JOIN`, Cypher mô tả node và mẫu đường đi:

```cypher
MATCH (person:Person)-[:DIRECTED]->(movie:Movie)
RETURN person.name, movie.title;
```

Các file trong thư mục:

| File | Vai trò | Được dùng ở đâu? |
|---|---|---|
| `constraints.cypher` | Tạo unique constraint, index và full-text index | Importer `src/kg/load_neo4j.py` |
| `reasoning.cypher` | Suy ra và materialize `CO_STARRED_WITH` | Importer sau khi nhập node/edge |
| `queries.cypher` | Catalog 10 truy vấn minh họa/competency question | Neo4j Browser, demo, báo cáo |
| `crud.cypher` | Mẫu CRUD hành chính có parameter | Tài liệu, kiểm thử và đối chiếu với `src/kg/crud.py` |

`constraints.cypher` chạy trước khi import. Ví dụ:

```cypher
CREATE CONSTRAINT movie_tmdb_id IF NOT EXISTS
FOR (movie:Movie) REQUIRE movie.tmdb_id IS UNIQUE;
```

Constraint ngăn hai node `Movie` dùng cùng `tmdb_id`. Index trên title/name tăng
tốc lookup; full-text index `entity_names` cung cấp candidate cho entity linker.

`reasoning.cypher` chạy sau khi đã có các cạnh `ACTED_IN`:

```text
Person A -[:ACTED_IN]-> Movie <-[:ACTED_IN]- Person B
                         |
                         v
Person A -[:CO_STARRED_WITH]-> Person B
```

Nó lưu `movie_count`, `evidence_movie_ids` và `derived=true`. Đây là luật nghiệp
vụ materialize trực tiếp trong Neo4j.

`queries.cypher` trả lời các competency question như:

- phim của một đạo diễn;
- diễn viên trong một phim;
- hai diễn viên có phim chung nào;
- đạo diễn nổi bật theo thể loại;
- đường đi ngắn nhất giữa hai người;
- kiểm tra các fact `CO_STARRED_WITH` đã suy ra.

Một chi tiết quan trọng: file `cypher/queries.cypher` là catalog minh họa dùng
trong demo/báo cáo. Request thật của `/ask` dùng các template có parameter và
stable ID trong `src/kg/query_catalog.py`. Việc tách này cho phép catalog public
dễ đọc, trong khi application catalog xử lý entity linking và các fallback cần
thiết cho runtime.

`crud.cypher` không có nghĩa public API cho phép người dùng tùy ý sửa graph.
CRUD chỉ là workflow hành chính được parameter hóa; implementation nằm ở
`src/kg/crud.py` và được kiểm thử nhưng không mở thành endpoint.

#### Cách nhớ nhanh

| Câu hỏi | Nơi cần tìm |
|---|---|
| Neo4j có cho phép trùng ID không? | `cypher/constraints.cypher` |
| Quan hệ đồng diễn được tạo thế nào? | `cypher/reasoning.cypher` |
| Muốn xem query Cypher mẫu? | `cypher/queries.cypher` |
| API `/ask` thật chạy query nào? | `src/kg/query_catalog.py` |
| Ai điều phối Neo4j runtime? | `src/kg/repository.py` |

Các điểm vào (entry point) thường dùng:

| Việc muốn làm | Điểm bắt đầu |
|---|---|
| Chạy ứng dụng | `Makefile` → `src/runtime/prepare.py` → `src/api/main.py` |
| Thu thập TMDB | `src/ingestion/collect_tmdb.py` |
| Biến raw thành CSV | `src/processing/pipeline.py` |
| Import Neo4j | `src/kg/load_neo4j.py` |
| Thêm intent hỏi đáp | `src/qa/intents.py` và `src/kg/query_catalog.py` |
| Sửa recommendation | `src/recommendation/neo4j_service.py` |
| Sửa API contract | `src/models.py` và `src/api/main.py` |
| Sửa giao diện | `src/api/static/` |

## 7. Dữ liệu trên đĩa trông như thế nào?

Sau `make data`, `data/processed/` có:

```text
movies.csv
people.csv
genres.csv
keywords.csv
studios.csv
acted_in.csv
directed.csv
has_genre.csv
has_keyword.csv
produced_by.csv
manifest.json
```

Năm file đầu là node table, năm file tiếp theo là edge table. Ví dụ về mặt khái
niệm:

```csv
# movies.csv
tmdb_id,title,rating
27205,Inception,8.4
```

```csv
# people.csv
person_id,name
tmdb:525,Christopher Nolan
```

```csv
# directed.csv
person_id,tmdb_id,source
tmdb:525,27205,tmdb
```

CSV thật có nhiều cột hơn. Đừng sửa thủ công rồi coi đó là nguồn chuẩn; hãy sửa
pipeline và sinh lại để manifest/checksum phản ánh đúng biến đổi.

## 8. Kiểm thử và đọc kết quả nghiên cứu

Chạy toàn bộ gate:

```bash
make test
```

Lệnh này:

1. Dựng Neo4j test riêng ở Bolt port `7688`.
2. Chạy pytest, gồm integration test có quyền reset graph test.
3. Compile source Python.
4. Kiểm tra checksum của các source/artifact được theo dõi.

Graph demo dùng port `7687` và volume bền vững; graph test dùng port `7688` và
`tmpfs`. Vì vậy test không reset dữ liệu demo.

Kết quả đã đo không nên diễn giải thành độ chính xác production:

- Entity resolution: corpus silver tất định 100 case.
- Reasoning: 50 fact có evidence.
- QA: 20 câu smoke test chạy trên Neo4j.
- Recommendation: 20 case theo rubric đã công bố.
- Benchmark: 4 query, 4 quy mô, cùng snapshot/máy/warm-up policy.

Các con số chỉ hợp lệ trong protocol và snapshot đó. Đọc
`experiments/results/README.md` trước khi trích dẫn.

## 9. Project có dùng bao nhiêu mô hình graph?

Project chỉ dùng một mô hình graph: Neo4j Property Graph. Đây là kho dữ liệu cho
API, UI, hỏi–đáp, suy diễn `CO_STARRED_WITH` và gợi ý. Các constraint, truy vấn
và luật graph đều được viết bằng Cypher.

## 10. Những điều project cố ý không làm

- Không có chatbot LLM sinh Cypher tùy ý.
- Không có GraphRAG, vector search hay embedding trong MVP.
- Không tự động nhập chung những người trùng tên.
- Không tải toàn bộ IMDb dataset vào RAM hay Neo4j.
- Không dùng fixture làm backend dự phòng khi Neo4j/dữ liệu thật bị thiếu.
- Không tuyên bố graph database luôn nhanh hơn relational database.
- Không mở CRUD hành chính qua public API.

Các ranh giới này giúp scope rõ, dữ liệu truy vết được và kết quả dễ tái lập.

## 11. Lỗi thường gặp

### `Missing processed data. Run: make data`

Không có `data/processed/manifest.json`. Cần nhận snapshot từ nhóm hoặc cấu hình
TMDB API key và chạy `make data`.

### `Knowledge graph is unavailable`

Neo4j chưa healthy, sai mật khẩu/URI, hoặc container chưa chạy. Kiểm tra:

```bash
docker compose ps
docker compose logs neo4j
```

Đối chiếu `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` trong `.env`.

### Port `8000`, `7474` hoặc `7687` đã được dùng

Tìm process/container đang dùng port hoặc dừng stack cũ:

```bash
docker compose ps
make stop
```

Có thể đổi API port:

```bash
make demo API_PORT=8001
```

### `TMDB_API_KEY` thiếu hoặc không hợp lệ

Key chỉ cần khi chạy `make data`, không cần khi snapshot đã tồn tại. Điền key vào
`.env`, không ghi trực tiếp vào source và không commit file này.

### Câu hỏi luôn trả `unknown`

Parser chỉ hỗ trợ chín mẫu. Thử một câu trong bảng ở mục 4.1. Nếu muốn hỗ trợ
cách diễn đạt mới, bổ sung pattern và test; nếu muốn thêm năng lực mới, cần cả
intent, slot linking, Cypher catalog, formatter và test.

### Tìm thấy sai phim/người

Kiểm tra evidence liên kết thực thể và confidence. Với tên trùng hoặc gần giống,
nên dùng autocomplete/chọn đúng phim kèm năm. Stable ID mới là identity; tên chỉ
là nhãn hiển thị.

## 12. Lộ trình đọc theo vai trò

### Chỉ muốn hiểu đồ án

1. Tài liệu này.
2. `docs/technical/architecture.md`.
3. `docs/runbooks/demo.md`.
4. `experiments/results/summary/`.

### Muốn phát triển backend

1. `src/api/main.py` và `src/models.py`.
2. `src/kg/repository.py`.
3. `src/qa/` hoặc `src/recommendation/`.
4. Test cùng tên dưới `tests/unit/`.

### Muốn phát triển data/graph

1. `src/processing/pipeline.py`.
2. `src/kg/load_neo4j.py`.
3. `cypher/constraints.cypher` và `cypher/reasoning.cypher`.
4. `tests/unit/test_pipeline.py` và integration test.

### Muốn chạy demo/bảo vệ

1. `docs/runbooks/demo.md`.
2. `docs/deliverables/defense/defense-script.md`.
3. `docs/deliverables/defense/defense-qa.md`.
4. `docs/deliverables/checklist-traceability.md`.

## 13. Tóm tắt trong một câu

Repository này biến dữ liệu phim đa nguồn thành một Neo4j Knowledge Graph có
provenance, dùng các traversal xác định để hỏi–đáp và xếp hạng phim tương tự,
đồng thời giữ bộ thí nghiệm tái lập để đánh giá và giải thích các quyết định kỹ
thuật.
