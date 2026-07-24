# Trình diễn đồ thị tri thức phim trên DBeaver Community

Tài liệu này hướng dẫn kết nối DBeaver Community tới Neo4j của project, chạy
SQL thông qua cơ chế SQL-to-Cypher và chạy Cypher trực tiếp. Quy trình đã được
kiểm tra với cấu hình hiện tại của repository:

- Neo4j `5.26-community` chạy bằng Docker Compose;
- Bolt tại `localhost:7687`;
- database `neo4j`;
- Neo4j JDBC Driver `6.9.1` full bundle;
- DBeaver Community dùng một Generic JDBC driver tự cấu hình.

## 1. Hiểu đúng giới hạn của DBeaver Community

Connector Neo4j dựng sẵn trong DBeaver chỉ khả dụng ở các bản PRO. Khi chọn
connector đó trên Community, DBeaver hiển thị thông báo `Neo4j driver is not
available in Community version`.

Không chọn connector bị khóa này. DBeaver Community vẫn có thể kết nối qua một
Generic JDBC driver tự tạo. Driver được dùng bên dưới là JDBC driver chính thức
của Neo4j, không phải connector Neo4j dựng sẵn của DBeaver.

Với cách này:

- kết quả truy vấn được hiển thị tốt ở dạng bảng;
- có thể chạy Cypher qua JDBC;
- có thể chạy một tập con SQL được driver dịch sang Cypher;
- không có graph visualization và Cypher-aware UI của connector DBeaver PRO.

## 2. Khởi động Neo4j của project

Từ thư mục gốc repository:

```bash
docker compose up -d neo4j
docker compose ps neo4j
```

Đợi service chuyển sang trạng thái `healthy`. Cấu hình local trình diễn hiện tại:

| Trường | Giá trị |
|---|---|
| Host | `localhost` |
| Bolt port | `7687` |
| HTTP/Neo4j Browser | `http://localhost:7474` |
| Database | `neo4j` |
| Username | `neo4j` |
| Password | `change-me` |

Có thể kiểm tra credential trực tiếp bằng:

```bash
docker compose exec -T neo4j \
  cypher-shell -u neo4j -p change-me "RETURN 1 AS ok"
```

Kết quả đúng là một cột `ok` có giá trị `1`.

> `NEO4J_AUTH` trong `docker-compose.yml` khởi tạo credential của server. Biến
> `NEO4J_PASSWORD` trong `.env` được API sử dụng để kết nối tới server; chỉ sửa
> `.env` không tự đổi mật khẩu đã lưu trong Neo4j volume. Với buổi trình diễn local,
> giữ hai phía đồng bộ với cấu hình repository.

## 3. Tạo Generic JDBC driver

Trong DBeaver:

1. Chọn `Database` → `Driver Manager`.
2. Chọn `New`.
3. Ở tab `Settings` hoặc `Main`, nhập:

| Trường | Giá trị |
|---|---|
| Driver Name | `Neo4j JDBC` |
| Driver Type | `Generic` |
| Class Name | `org.neo4j.jdbc.Neo4jDriver` |
| URL Template | `jdbc:neo4j://{host}:{port}/{database}?enableSQLTranslation=true` |
| Default Port | `7687` |

Không chọn `Embedded` hoặc `No Authentication`.

### Cách A — tải bằng Maven sản phẩm đầu ra

1. Mở tab `Libraries`.
2. Chọn `Add Artifact`.
3. Ở chế độ `Dependency declaration`, nhập:

   ```text
   org.neo4j:neo4j-jdbc-full-bundle:6.9.1
   ```

4. Xác nhận để sản phẩm đầu ra xuất hiện trong danh sách Libraries.
5. Chọn sản phẩm đầu ra rồi nhấn `Download/Update`.
6. Đợi đến khi sản phẩm đầu ra không còn biểu tượng lỗi hoặc màu đỏ.

Phải dùng `neo4j-jdbc-full-bundle`. Gói `neo4j-jdbc-bundle` nhỏ hơn không chứa
default SQL-to-Cypher translator.

### Cách B — thêm file JAR trực tiếp

Dùng cách này nếu DBeaver không tải được Maven sản phẩm đầu ra:

1. Tải
   [`neo4j-jdbc-full-bundle-6.9.1.jar`](https://repo.maven.apache.org/maven2/org/neo4j/neo4j-jdbc-full-bundle/6.9.1/neo4j-jdbc-full-bundle-6.9.1.jar).
2. Tại tab `Libraries`, chọn `Add File`.
3. Chọn file JAR vừa tải.

Full bundle là một JAR đã đóng gói các dependency cần thiết, nên không cần thêm
từng dependency thủ công.

### Kiểm tra driver class

Nút `Find Class` chỉ bật sau khi DBeaver đã tải hoặc nhận diện được file JAR.
Khi nút khả dụng, chọn:

```text
org.neo4j.jdbc.Neo4jDriver
```

Nếu `Find Class` vẫn bị vô hiệu hóa nhưng JAR đã có trong Libraries, có thể bỏ
qua nút này và nhập trực tiếp class name ở tab `Main`. Nhấn `OK` để lưu driver.

## 4. Tạo connection

1. Chọn `Database` → `New Database Connection`.
2. Tìm và chọn custom driver `Neo4j JDBC` vừa tạo.
3. Không chọn connector `Neo4j` có thông báo yêu cầu bản PRO.
4. Ở tab `Main`, chọn `Connect by: Host` và nhập:

   | Trường | Giá trị |
   |---|---|
   | Host | `localhost` |
   | Port | `7687` |
   | Database/Schema | `neo4j` |
   | Username | `neo4j` |
   | Password | `change-me` |

DBeaver sẽ tạo JDBC URL:

```text
jdbc:neo4j://localhost:7687/neo4j?enableSQLTranslation=true
```

Nếu màn hình chỉ có chế độ `URL`, chọn `Connect by: URL` rồi nhập nguyên URL
trên. Username và password vẫn đặt ở phần `Authentication (Database Native)`.

5. Chọn `Test Connection`.
6. Khi DBeaver báo kết nối thành công, chọn `Finish`.

## 5. Kiểm tra bằng SQL

Chuột phải connection → `SQL Editor` → `New SQL Script`, sau đó chạy:

```sql
SELECT
    m.tmdb_id,
    m.title,
    m.rating,
    m.imdb_rating
FROM Movie AS m
WHERE m.rating IS NOT NULL
ORDER BY m.rating DESC
LIMIT 10;
```

Trong câu SQL này, `Movie` được ánh xạ tới node label `Movie`; các cột được ánh
xạ tới node properties. JDBC driver dịch câu lệnh thành Cypher trước khi gửi tới
Neo4j.

Một kiểm tra ngắn hơn:

```sql
SELECT count(*) AS movie_count
FROM Movie AS m;
```

Đây không phải một relational schema thực. SQL translation phù hợp cho trình diễn
truy vấn dạng bảng đơn giản; nó không thay thế Cypher cho traversal graph.

## 6. Chạy Cypher trên cùng connection

Vì connection đang bật `enableSQLTranslation=true`, thêm hint sau vào đầu câu
Cypher để driver không cố dịch nó như SQL:

```cypher
/*+ NEO4J FORCE_CYPHER */
MATCH (n)
UNWIND labels(n) AS label
RETURN label, count(*) AS node_count
ORDER BY node_count DESC;
```

Nếu DBeaver chỉ gạch chân cú pháp vì editor đang dùng SQL dialect nhưng câu lệnh
vẫn chạy thành công, có thể bỏ qua cảnh báo syntax của editor.

## 7. Kịch bản trình diễn đề xuất

### 7.1. Thống kê các loại node

```cypher
/*+ NEO4J FORCE_CYPHER */
MATCH (n)
UNWIND labels(n) AS label
RETURN label, count(*) AS node_count
ORDER BY node_count DESC;
```

Mục đích: giới thiệu năm loại thực thể chính `Movie`, `Person`, `Genre`,
`Keyword` và `Studio`.

### 7.2. Truy vấn phim dạng bảng bằng SQL

```sql
SELECT
    m.title,
    m.release_date,
    m.rating,
    m.imdb_rating
FROM Movie AS m
WHERE m.rating >= 8
ORDER BY m.rating DESC
LIMIT 10;
```

Mục đích: cho thấy công cụ BI/JDBC quen với SQL vẫn đọc được một phần graph qua
lớp dịch SQL-to-Cypher.

### 7.3. Traversal đạo diễn → phim

```cypher
/*+ NEO4J FORCE_CYPHER */
MATCH (director:Person)-[:DIRECTED]->(movie:Movie)
WHERE toLower(director.name) = toLower('Christopher Nolan')
RETURN movie.title, movie.release_date, movie.rating
ORDER BY movie.release_date;
```

Mục đích: minh họa relationship có hướng và truy vấn graph-native.

### 7.4. Diễn viên của một phim bằng stable ID

```cypher
/*+ NEO4J FORCE_CYPHER */
MATCH (actor:Person)-[role:ACTED_IN]->(movie:Movie {tmdb_id: 155})
RETURN actor.name, role.character, role.cast_order
ORDER BY role.cast_order;
```

`tmdb_id=155` là *The Dark Knight*. Stable ID tránh nhầm với phim có tên gần
giống như *The Dark Knight Rises*.

### 7.5. Quan hệ suy diễn đồng diễn

```cypher
/*+ NEO4J FORCE_CYPHER */
MATCH (actor:Person {name: 'Christian Bale'})
      -[collaboration:CO_STARRED_WITH]-(co_star:Person)
RETURN co_star.name,
       collaboration.movie_count,
       collaboration.evidence_movie_ids
ORDER BY collaboration.movie_count DESC, co_star.name
LIMIT 10;
```

Mục đích: trình bày relationship suy diễn và bằng chứng truy vết về phim nguồn.

### 7.6. Đường đi ngắn nhất giữa hai người

```cypher
/*+ NEO4J FORCE_CYPHER */
MATCH path = shortestPath(
    (a:Person {name: 'Christian Bale'})-[*..8]-(b:Person {name: 'Leonardo DiCaprio'})
)
RETURN [node IN nodes(path) | coalesce(node.name, node.title)] AS entities,
       [rel IN relationships(path) | type(rel)] AS relationships;
```

Mục đích: minh họa multi-hop traversal, loại truy vấn khó biểu diễn tự nhiên
bằng SQL translation.

## 8. Xử lý lỗi thường gặp

### `Neo4j driver is not available in Community version`

Đây là connector dựng sẵn của DBeaver PRO. Quay lại `Driver Manager`, tạo custom
Generic JDBC driver theo mục 3 rồi chọn driver `Neo4j JDBC` khi tạo connection.

### `Find Class` không bấm được

JAR chưa được tải hoặc chưa được DBeaver nhận diện:

1. chọn sản phẩm đầu ra trong Libraries;
2. nhấn `Download/Update`;
3. nếu vẫn lỗi, dùng `Add File` với full-bundle JAR;
4. có thể nhập thủ công `org.neo4j.jdbc.Neo4jDriver` mà không dùng `Find Class`.

### `The client is unauthorized due to authentication failure`

Kết nối mạng đã tới được Neo4j nhưng credential không đúng:

1. xóa toàn bộ password đã lưu và nhập lại `change-me`;
2. bảo đảm username là `neo4j`;
3. không nhập dấu nháy hoặc chuỗi `NEO4J_PASSWORD=`;
4. trong tab `Driver properties`, xóa `user`/`password` cũ nếu chúng ghi đè
   credential ở tab `Main`;
5. chạy lệnh `cypher-shell` ở mục 2 để kiểm tra phía server.

### `Connection refused`

Neo4j chưa chạy hoặc cổng chưa mở:

```bash
docker compose up -d neo4j
docker compose ps neo4j
```

Xác nhận dùng Bolt port `7687`, không dùng HTTP port `7474` trong JDBC URL.

### `No SQL translators available`

Driver đang thiếu translator. Xóa bundle hiện tại và cài đúng:

```text
org.neo4j:neo4j-jdbc-full-bundle:6.9.1
```

Đồng thời kiểm tra JDBC URL có `enableSQLTranslation=true`.

### `ClassNotFoundException: org.neo4j.jdbc.Neo4jDriver`

Full-bundle JAR chưa nằm trong Libraries hoặc chưa tải xong. Thêm lại JAR, nhập
đúng class name và mở lại màn hình cấu hình driver. Neo4j JDBC Driver 6.x yêu
cầu Java 17 trở lên ở phía client.

### SQL phức tạp không dịch được

SQL-to-Cypher chỉ hỗ trợ những cấu trúc có ánh xạ hợp lý sang graph. Không dựa
vào lớp dịch cho `OUTER JOIN`, traversal nhiều hop hoặc thuật toán đường đi. Dùng
Cypher với `/*+ NEO4J FORCE_CYPHER */` cho các trường hợp đó.

## 9. Checklist trước buổi trình diễn

- [ ] `docker compose ps neo4j` báo service `healthy`.
- [ ] `cypher-shell` trả về `ok = 1`.
- [ ] Custom driver dùng full bundle `6.9.1`.
- [ ] `Test Connection` trong DBeaver thành công.
- [ ] SQL ở mục 5 trả về dữ liệu.
- [ ] Cypher thống kê node ở mục 7.1 chạy được.
- [ ] Các câu trình diễn cần trình bày đã được mở sẵn trong SQL Editor.
- [ ] Không dùng connector Neo4j PRO trên DBeaver Community.

## 10. Tài liệu tham khảo

- [DBeaver Driver Manager](https://dbeaver.com/docs/dbeaver/Driver-Manager/)
- [DBeaver — thêm Maven artifact cho driver](https://dbeaver.com/docs/dbeaver/How-to-add-additional-artifacts-to-the-driver/)
- [Neo4j JDBC Driver — distribution và full bundle](https://neo4j.com/docs/jdbc-manual/current/distribution/)
- [Neo4j JDBC Driver — cấu hình URL và driver class](https://neo4j.com/docs/jdbc-manual/current/configuration/)
- [Neo4j JDBC Driver — SQL-to-Cypher](https://neo4j.com/docs/jdbc-manual/current/sql2cypher/)
