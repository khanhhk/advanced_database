const pptxgen = require("pptxgenjs");
const path = require("path");
const { imageSize } = require("image-size");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Hoàng Kim Khánh";
pptx.subject = "Báo cáo cuối kỳ Cơ sở dữ liệu nâng cao";
pptx.title = "Xây dựng đồ thị tri thức phim đa nguồn";
pptx.company = "Đại học Bách khoa Hà Nội";
pptx.lang = "vi-VN";
pptx.theme = {
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  lang: "vi-VN",
};
pptx.defineSlideMaster({
  title: "LIGHT",
  background: { color: "F6F8FB" },
  objects: [
    { rect: { x: 0, y: 0, w: 13.333, h: 7.5, line: { color: "F6F8FB", transparency: 100 }, fill: { color: "F6F8FB" } } },
    { text: { text: "MOVIE KNOWLEDGE GRAPH", options: { x: 0.58, y: 0.18, w: 3.3, h: 0.22, fontFace: "Arial", fontSize: 9, bold: true, color: "337B80", charSpacing: 1.5, margin: 0 } } },
    { text: { text: "Đại học Bách khoa Hà Nội · Khoa Toán – Tin", options: { x: 8.75, y: 7.12, w: 3.85, h: 0.18, fontFace: "Arial", fontSize: 8, color: "697586", align: "right", margin: 0 } } },
  ],
  slideNumber: { x: 12.72, y: 7.08, w: 0.25, h: 0.2, fontFace: "Arial", fontSize: 9, color: "697586", align: "right", margin: 0 },
});

const C = {
  navy: "112B46",
  navy2: "183D5D",
  teal: "337B80",
  teal2: "63A6A6",
  green: "3D8B66",
  greenBg: "E8F4EE",
  purple: "725B9B",
  purpleBg: "F0ECF7",
  amber: "D38B36",
  amberBg: "FFF2DF",
  red: "B94D52",
  redBg: "FBEAEC",
  ink: "172B3A",
  muted: "697586",
  line: "D7DEE8",
  pale: "EDF2F7",
  white: "FFFFFF",
};

const A = (name) => path.join(__dirname, "assets", `${name}.png`);
const OUT = path.join(__dirname, "movie_knowledge_graph_defense.pptx");
const shadow = () => ({ type: "outer", color: "26384A", opacity: 0.13, blur: 2, angle: 45, distance: 1 });

function addTitle(slide, title, kicker, section = "") {
  if (section) slide.addText(section.toUpperCase(), { x: 0.58, y: 0.52, w: 2.4, h: 0.24, fontFace: "Arial", fontSize: 9, bold: true, color: C.teal, charSpacing: 1.4, margin: 0 });
  slide.addText(title, { x: 0.58, y: 0.78, w: 11.9, h: 0.55, fontFace: "Calibri", fontSize: 26, bold: true, color: C.navy, margin: 0, breakLine: false, fit: "shrink" });
  if (kicker) slide.addText(kicker, { x: 0.6, y: 1.38, w: 11.65, h: 0.34, fontFace: "Calibri", fontSize: 12.5, color: C.muted, margin: 0, fit: "shrink" });
}

function addSource(slide, text) {
  slide.addText(text, { x: 0.6, y: 6.84, w: 11.75, h: 0.2, fontFace: "Arial", fontSize: 7.5, color: "7C8796", margin: 0, italic: true });
}

function card(slide, x, y, w, h, title, body, opts = {}) {
  const fill = opts.fill || C.white;
  const stroke = opts.stroke || C.line;
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.06, fill: { color: fill }, line: { color: stroke, width: opts.lineWidth || 1 }, shadow: opts.shadow === false ? undefined : shadow() });
  if (opts.badge) {
    slide.addShape(pptx.ShapeType.ellipse, { x: x + 0.22, y: y + 0.22, w: 0.42, h: 0.42, fill: { color: opts.badgeColor || C.teal }, line: { color: opts.badgeColor || C.teal } });
    slide.addText(opts.badge, { x: x + 0.22, y: y + 0.28, w: 0.42, h: 0.16, fontFace: "Arial", fontSize: 10, bold: true, color: C.white, align: "center", margin: 0 });
  }
  slide.addText(title, { x: x + (opts.badge ? 0.78 : 0.25), y: y + 0.2, w: w - (opts.badge ? 1.0 : 0.5), h: 0.33, fontFace: "Calibri", fontSize: opts.titleSize || 16, bold: true, color: opts.titleColor || C.navy, margin: 0, fit: "shrink" });
  if (body) slide.addText(body, { x: x + 0.25, y: y + 0.66, w: w - 0.5, h: h - 0.86, fontFace: "Calibri", fontSize: opts.bodySize || 11.5, color: opts.bodyColor || C.ink, margin: 0, breakLine: false, valign: opts.valign || "top", fit: "shrink", paraSpaceAfterPt: 5 });
}

function metric(slide, x, y, w, value, label, color = C.teal, note = "") {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h: 1.38, rectRadius: 0.06, fill: { color: C.white }, line: { color: C.line }, shadow: shadow() });
  slide.addText(value, { x: x + 0.18, y: y + 0.18, w: w - 0.36, h: 0.5, fontFace: "Arial", fontSize: 28, bold: true, color, margin: 0, fit: "shrink" });
  slide.addText(label, { x: x + 0.2, y: y + 0.74, w: w - 0.4, h: 0.28, fontFace: "Calibri", fontSize: 11, bold: true, color: C.ink, margin: 0, fit: "shrink" });
  if (note) slide.addText(note, { x: x + 0.2, y: y + 1.06, w: w - 0.4, h: 0.18, fontFace: "Arial", fontSize: 7.5, color: C.muted, margin: 0, fit: "shrink" });
}

function addImageContain(slide, imagePath, x, y, w, h, border = true) {
  if (border) slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.04, fill: { color: C.white }, line: { color: C.line }, shadow: shadow() });
  const dimensions = imageSize(imagePath);
  const boxW = w - 0.24;
  const boxH = h - 0.24;
  const scale = Math.min(boxW / dimensions.width, boxH / dimensions.height);
  const imageW = dimensions.width * scale;
  const imageH = dimensions.height * scale;
  slide.addImage({
    path: imagePath,
    x: x + 0.12 + (boxW - imageW) / 2,
    y: y + 0.12 + (boxH - imageH) / 2,
    w: imageW,
    h: imageH,
  });
}

function bullets(slide, items, x, y, w, h, opts = {}) {
  const runs = [];
  items.forEach((item, i) => {
    runs.push({ text: item, options: { bullet: { indent: 16 }, hanging: 4, breakLine: i !== items.length - 1 } });
  });
  slide.addText(runs, { x, y, w, h, fontFace: "Calibri", fontSize: opts.fontSize || 15, color: opts.color || C.ink, margin: 0, breakLine: false, paraSpaceAfterPt: opts.gap || 10, valign: "mid", fit: "shrink" });
}

function notes(slide, text) {
  slide.addNotes(text);
}

function darkSlide() {
  const slide = pptx.addSlide();
  slide.background = { color: C.navy };
  slide.addShape(pptx.ShapeType.ellipse, { x: 10.7, y: -0.7, w: 3.5, h: 3.5, fill: { color: C.teal, transparency: 72 }, line: { color: C.teal, transparency: 100 } });
  slide.addShape(pptx.ShapeType.ellipse, { x: -0.7, y: 5.8, w: 2.3, h: 2.3, fill: { color: C.purple, transparency: 70 }, line: { color: C.purple, transparency: 100 } });
  return slide;
}

function lightSlide(title, kicker, section) {
  const slide = pptx.addSlide("LIGHT");
  addTitle(slide, title, kicker, section);
  return slide;
}

// 1 — Cover
{
  const s = darkSlide();
  s.addText("BÁO CÁO CUỐI KỲ · CƠ SỞ DỮ LIỆU NÂNG CAO", { x: 0.72, y: 0.62, w: 6.5, h: 0.3, fontFace: "Arial", fontSize: 10, bold: true, color: "8FD0CC", charSpacing: 1.7, margin: 0 });
  s.addText("Xây dựng đồ thị tri thức\nphim đa nguồn", { x: 0.72, y: 1.22, w: 7.2, h: 1.55, fontFace: "Calibri", fontSize: 34, bold: true, color: C.white, margin: 0, breakLine: false, fit: "shrink" });
  s.addText("Tích hợp dữ liệu · Truy vấn nhiều bước · Suy diễn · Hỏi–đáp và gợi ý có bằng chứng", { x: 0.75, y: 3.02, w: 6.45, h: 0.62, fontFace: "Calibri", fontSize: 16, color: "D6E3ED", margin: 0, fit: "shrink" });
  addImageContain(s, A("movie_kg_overview"), 7.55, 1.15, 5.15, 3.95, false);
  s.addText("Học viên", { x: 0.75, y: 5.35, w: 1.1, h: 0.24, fontFace: "Arial", fontSize: 9, bold: true, color: "8FD0CC", margin: 0 });
  s.addText("Hoàng Kim Khánh · 20252307M", { x: 0.75, y: 5.68, w: 4.4, h: 0.34, fontFace: "Calibri", fontSize: 15, bold: true, color: C.white, margin: 0 });
  s.addText("Giảng viên hướng dẫn", { x: 6.8, y: 5.35, w: 1.8, h: 0.24, fontFace: "Arial", fontSize: 9, bold: true, color: "8FD0CC", margin: 0 });
  s.addText("TS. Trần Ngọc Thăng", { x: 6.8, y: 5.68, w: 3.4, h: 0.34, fontFace: "Calibri", fontSize: 15, bold: true, color: C.white, margin: 0 });
  s.addText("ĐẠI HỌC BÁCH KHOA HÀ NỘI · KHOA TOÁN – TIN · 07/2026", { x: 0.75, y: 6.92, w: 8, h: 0.2, fontFace: "Arial", fontSize: 8.5, color: "9FB2C3", margin: 0 });
  notes(s, "Kính thưa thầy, em xin trình bày đề tài xây dựng đồ thị tri thức phim đa nguồn. Trọng tâm không chỉ là lưu dữ liệu, mà là tạo một quy trình tích hợp có thể tái lập, hỗ trợ truy vấn nhiều bước, suy diễn và hai ứng dụng có bằng chứng.");
}

// 2 — Motivation
{
  const s = lightSlide("Dữ liệu phim vốn là một mạng quan hệ", "Tra cứu một bảng không đủ khi câu hỏi đi qua nhiều thực thể và nhiều nguồn.", "Bài toán");
  addImageContain(s, A("movie_kg_overview"), 0.62, 1.95, 7.25, 4.55);
  card(s, 8.2, 1.98, 4.42, 1.15, "Quan hệ dày đặc", "Movie kết nối Person, Genre, Keyword và Studio theo cấu trúc nhiều–nhiều.", { badge: "1", fill: "F0F6F8", stroke: "BDDADD" });
  card(s, 8.2, 3.35, 4.42, 1.15, "Nguồn phân tán", "TMDB cung cấp metadata/credits; IMDb cung cấp rating và số lượt đánh giá độc lập.", { badge: "2", badgeColor: C.purple, fill: C.purpleBg, stroke: "D9CFE8" });
  card(s, 8.2, 4.72, 4.42, 1.15, "Cần bằng chứng", "Câu trả lời và gợi ý phải chỉ ra thực thể, quan hệ hoặc đường đi đã tạo nên kết quả.", { badge: "3", badgeColor: C.green, fill: C.greenBg, stroke: "C4E2D1" });
  addSource(s, "Nguồn hình: report_latex/images/sources/movie_kg_overview.drawio");
  notes(s, "Dữ liệu phim là một mạng nhiều–nhiều. Một phim liên hệ với nhiều người, thể loại, từ khóa và hãng; một người lại tham gia nhiều phim với nhiều vai trò. Khi tích hợp TMDB và IMDb, câu hỏi không chỉ là lấy một dòng dữ liệu mà là đi qua mạng quan hệ và giữ được nguồn gốc.");
}

// 3 — Gap
{
  const s = lightSlide("Ba khoảng trống cần giải quyết đồng thời", "Nếu thiếu một trong ba, hệ thống có thể trả lời được nhưng không đáng tin hoặc không giải thích được.", "Bài toán");
  card(s, 0.65, 2.05, 3.78, 3.95, "Định danh đúng", "209 người trùng tên vẫn phải là các thực thể khác nhau.\n\nKhông dùng tên làm khóa chính; ưu tiên định danh nguồn ổn định.", { badge: "ID", badgeColor: C.teal, titleSize: 19, bodySize: 14 });
  card(s, 4.78, 2.05, 3.78, 3.95, "Duyệt nhiều bước", "Bạn diễn, phim chung, đạo diễn–thể loại và đường liên hệ đều cần duyệt đồ thị (traversal) qua nhiều cạnh.\n\nMô hình phải phản ánh trực tiếp các quan hệ.", { badge: "↗", badgeColor: C.amber, titleSize: 19, bodySize: 14, fill: C.amberBg, stroke: "F1D5AA" });
  card(s, 8.91, 2.05, 3.78, 3.95, "Giải thích được", "Kết quả cần gắn với nguồn, thực thể đã liên kết, cạnh hỗ trợ và đóng góp điểm.\n\nKhông chấp nhận suy diễn hộp đen.", { badge: "✓", badgeColor: C.green, titleSize: 19, bodySize: 14, fill: C.greenBg, stroke: "C4E2D1" });
  notes(s, "Đề tài tập trung vào ba khoảng trống. Thứ nhất là identity: trùng tên không đồng nghĩa cùng người. Thứ hai là traversal: nhiều câu hỏi thực chất là mẫu đường đi. Thứ ba là provenance: mỗi kết quả phải lần ngược được về nguồn hoặc phép suy diễn.");
}

// 4 — RQ
{
  const s = darkSlide();
  s.addText("CÂU HỎI NGHIÊN CỨU", { x: 0.75, y: 0.68, w: 3.5, h: 0.25, fontFace: "Arial", fontSize: 10, bold: true, color: "8FD0CC", charSpacing: 1.6, margin: 0 });
  s.addText("Đồ thị tri thức có thể tích hợp dữ liệu phim đa nguồn, hỗ trợ truy vấn nhiều bước và tạo kết quả có bằng chứng như thế nào?", { x: 0.75, y: 1.25, w: 11.4, h: 1.6, fontFace: "Calibri", fontSize: 30, bold: true, color: C.white, margin: 0, fit: "shrink" });
  const goals = [
    ["01", "Quy trình TMDB + IMDb tái lập được"],
    ["02", "Định danh ổn định và ràng buộc dữ liệu"],
    ["03", "Cypher nhiều bước và đường đi ngắn nhất"],
    ["04", "QA 9 ý định + gợi ý có lời giải thích"],
    ["05", "Đánh giá chất lượng, suy diễn và hiệu năng"],
  ];
  goals.forEach((g, i) => {
    const x = 0.75 + i * 2.48;
    s.addText(g[0], { x, y: 4.25, w: 0.42, h: 0.3, fontFace: "Arial", fontSize: 12, bold: true, color: "8FD0CC", margin: 0 });
    s.addText(g[1], { x, y: 4.72, w: 2.14, h: 1.0, fontFace: "Calibri", fontSize: 13.5, bold: true, color: C.white, margin: 0, fit: "shrink" });
  });
  notes(s, "Câu hỏi nghiên cứu được cụ thể hóa thành năm mục tiêu đo được: tích hợp tái lập, mô hình có identity và constraint, truy vấn Cypher nhiều bước, hai ứng dụng có giải thích và một kế hoạch đánh giá có bằng chứng.");
}

// 5 — Scope
{
  const s = lightSlide("Phạm vi được khóa để bảo đảm tính kiểm chứng", "MVP tập trung vào đồ thị phim có thể chạy, đo và trình diễn; không mở rộng sang sinh Cypher tự do.", "Phạm vi");
  metric(s, 0.65, 2.0, 2.35, "4.999", "Phim (Movie) hợp lệ", C.teal, "từ 5.000 bản ghi đầu vào");
  metric(s, 3.25, 2.0, 2.35, "5 + 1", "Quan hệ gốc + suy diễn", C.purple, "CO_STARRED_WITH là cạnh suy ra");
  metric(s, 5.85, 2.0, 2.35, "2 nguồn", "TMDB + IMDb", C.green, "IMDb chỉ enrich rating/votes");
  card(s, 0.65, 3.75, 5.75, 2.2, "Trong phạm vi", "Movie · Person · Genre · Keyword · Studio\nNeo4j/Cypher · RDF/OWL/SPARQL\nQA 9 ý định · gợi ý IDF có bằng chứng", { fill: C.greenBg, stroke: "C4E2D1", titleColor: C.green, bodySize: 14 });
  card(s, 6.75, 3.75, 5.9, 2.2, "Ngoài phạm vi", "Giải thưởng/Wikidata · LLM-to-Cypher tự do\nTìm kiếm véc-tơ · GraphRAG · đa phương thức\nĐánh giá người dùng quy mô lớn", { fill: C.redBg, stroke: "E9C3C6", titleColor: C.red, bodySize: 14 });
  notes(s, "Phạm vi hiện tại là 4.999 phim hợp lệ, năm loại quan hệ gốc và một quan hệ suy diễn. TMDB là nguồn cấu trúc đồ thị; IMDb chỉ bổ sung rating bằng exact ID. Các hướng như LLM-to-Cypher, vector search và GraphRAG được loại khỏi MVP để tránh đánh đổi tính kiểm chứng.");
}

// 6 — Why graph
{
  const s = lightSlide("Neo4j và RDF/OWL đảm nhiệm hai vai trò bổ trợ", "Giá trị của đồ thị nằm ở mô hình quan hệ, đường đi bằng chứng và ngữ nghĩa — không phải luôn nhanh hơn SQL.", "Lựa chọn công nghệ");
  const rows = [
    ["Yêu cầu", "Mô hình bảng", "Đồ thị thuộc tính"],
    ["Quan hệ nhiều–nhiều", "Bảng nối", "Cạnh trực tiếp"],
    ["Truy vấn nhiều bước", "Chuỗi JOIN", "Mẫu đường đi"],
    ["Suy diễn co-star", "Logic vật chất hóa riêng", "Cạnh suy ra có bằng chứng"],
    ["Giải thích", "Dựng lại quan hệ", "Đường đi tự nhiên"],
  ];
  s.addTable(rows, { x: 0.67, y: 2.05, w: 7.25, h: 3.95, border: { type: "solid", color: C.line, pt: 1 }, fill: C.white, color: C.ink, fontFace: "Calibri", fontSize: 12, margin: 0.1, rowH: 0.68, bold: false, valign: "mid", colW: [2.15, 2.25, 2.85], autoFit: false });
  s.addShape(pptx.ShapeType.roundRect, { x: 8.35, y: 2.05, w: 4.3, h: 1.72, rectRadius: 0.06, fill: { color: "EAF2F8" }, line: { color: "B9D3E8" }, shadow: shadow() });
  s.addText("Neo4j / Cypher", { x: 8.65, y: 2.35, w: 3.7, h: 0.35, fontFace: "Calibri", fontSize: 20, bold: true, color: C.navy, margin: 0 });
  s.addText("Kho vận hành cho duyệt đồ thị, hỏi–đáp và gợi ý.", { x: 8.65, y: 2.86, w: 3.45, h: 0.46, fontFace: "Calibri", fontSize: 13, color: C.ink, margin: 0, fit: "shrink" });
  s.addShape(pptx.ShapeType.roundRect, { x: 8.35, y: 4.15, w: 4.3, h: 1.72, rectRadius: 0.06, fill: { color: C.purpleBg }, line: { color: "D5C9E8" }, shadow: shadow() });
  s.addText("RDF / OWL / SPARQL", { x: 8.65, y: 4.45, w: 3.7, h: 0.35, fontFace: "Calibri", fontSize: 20, bold: true, color: C.purple, margin: 0 });
  s.addText("Lớp chuẩn trao đổi, ràng buộc và suy diễn ngữ nghĩa.", { x: 8.65, y: 4.96, w: 3.45, h: 0.46, fontFace: "Calibri", fontSize: 13, color: C.ink, margin: 0, fit: "shrink" });
  notes(s, "Neo4j là kho vận hành vì thuận tiện cho traversal và ứng dụng. RDF/OWL là lớp chuẩn ngữ nghĩa và trao đổi. SQLite chỉ là mốc so sánh được kiểm soát. Em không kết luận đồ thị luôn nhanh hơn quan hệ; giá trị chính là mô hình và bằng chứng.");
}

// 7 — Architecture
{
  const s = lightSlide("Kiến trúc đầu cuối: từ nguồn đến bằng chứng", "Sau khi import, đường chạy trình diễn không phụ thuộc Internet.", "Thiết kế hệ thống");
  addImageContain(s, A("system_architecture"), 0.64, 1.88, 12.03, 4.72);
  addSource(s, "Nguồn chỉnh sửa: report_latex/images/sources/system_architecture.drawio");
  notes(s, "Luồng chính đi từ TMDB và IMDb qua cache bất biến, xử lý và chuẩn hóa sang Neo4j. Một nhánh xuất RDF/Turtle cho suy diễn ngữ nghĩa. FastAPI cung cấp QA và recommendation. Manifest, checksum và các phép kiểm tra bao quanh toàn bộ quy trình.");
}

// 8 — Sources and IMDb
{
  const s = lightSlide("Tích hợp IMDb theo chiến lược tiết kiệm lưu trữ", "Chỉ đọc tuần tự tệp rating nén và ghép chính xác theo IMDb ID; không tải toàn bộ IMDb vào đồ thị.", "Dữ liệu");
  const x0 = 0.75, y0 = 2.0;
  ["TMDB\nexternal_ids", "imdb_id = tconst", "IMDb ratings.gz", "Movie\nenrichment"].forEach((t, i) => {
    const x = x0 + i * 2.85;
    s.addShape(i === 1 ? pptx.ShapeType.chevron : pptx.ShapeType.roundRect, { x, y: y0, w: 2.2, h: 1.2, rectRadius: 0.06, fill: { color: i === 1 ? C.amberBg : (i === 3 ? C.greenBg : "EAF2F8") }, line: { color: i === 1 ? C.amber : (i === 3 ? C.green : C.teal), width: 1.4 } });
    s.addText(t, { x: x + 0.15, y: y0 + 0.32, w: 1.9, h: 0.52, fontFace: "Calibri", fontSize: 14, bold: true, color: C.navy, align: "center", margin: 0, fit: "shrink" });
    if (i < 3) s.addShape(pptx.ShapeType.line, { x: x + 2.22, y: y0 + 0.6, w: 0.55, h: 0, line: { color: C.muted, width: 1.8, beginArrowType: "none", endArrowType: "triangle" } });
  });
  metric(s, 0.75, 4.1, 2.55, "4.558", "Movie có IMDb ID", C.teal);
  metric(s, 3.55, 4.1, 2.55, "4.351", "Rating ghép chính xác", C.green);
  metric(s, 6.35, 4.1, 2.55, "95,5%", "Tỷ lệ ghép trên IMDb ID", C.purple);
  card(s, 9.15, 4.1, 3.45, 1.38, "Không ghi đè", "`rating`, `imdb_rating` và `imdb_votes` được giữ riêng.", { fill: C.amberBg, stroke: "F1D5AA", titleSize: 15, bodySize: 11 });
  notes(s, "Để giữ quy mô lưu trữ hợp lý, hệ thống chỉ tải tệp title.ratings.tsv.gz và đọc streaming. Phép nối là exact ID giữa imdb_id của TMDB và tconst của IMDb. Trong 4.558 phim có IMDb ID, 4.351 phim ghép được rating; hai thang rating được giữ riêng.");
}

// 9 — Model
{
  const s = lightSlide("Mô hình dữ liệu đặt định danh lên trước tên gọi", "Một Person có thể vừa là diễn viên vừa là đạo diễn; vai trò được biểu diễn bằng quan hệ.", "Mô hình tri thức");
  addImageContain(s, A("property_graph_schema"), 0.62, 1.9, 8.15, 4.72);
  card(s, 9.1, 1.92, 3.55, 1.2, "Định danh ổn định", "`Person.person_id = tmdb:<id>`\nTên không phải khóa chính.", { fill: "EAF2F8", stroke: "BDD4E5", titleSize: 15, bodySize: 11 });
  card(s, 9.1, 3.38, 3.55, 1.2, "Vai trò trên cạnh", "`ACTED_IN` giữ character, cast_order và source.", { fill: C.greenBg, stroke: "C4E2D1", titleSize: 15, bodySize: 11 });
  card(s, 9.1, 4.84, 3.55, 1.2, "Ràng buộc", "Ràng buộc (constraint) và chỉ mục được tạo trước khi nhập dữ liệu.", { fill: C.purpleBg, stroke: "D9CFE8", titleSize: 15, bodySize: 11 });
  addSource(s, "Nguồn chỉnh sửa: report_latex/images/sources/property_graph_schema.drawio");
  notes(s, "Mô hình có năm loại nút và năm quan hệ gốc. Person chỉ dùng một label vì cùng một người có thể có nhiều vai trò. Stable source ID là khóa; ACTED_IN giữ metadata trên cạnh. Constraint và index được tạo trước khi nạp.");
}

// 10 — ETL
{
  const s = lightSlide("Quy trình dữ liệu có thể chạy lại và kiểm tra", "Raw cache bất biến → dữ liệu chuẩn hóa tất định → import idempotent → validation.", "Quy trình xử lý");
  addImageContain(s, A("etl_pipeline"), 0.62, 1.92, 12.02, 3.9);
  const captions = [
    ["Cache", "Không tải lại nguồn khi xử lý lại"],
    ["Manifest", "Count + checksum + chất lượng"],
    ["MERGE", "Import lặp không nhân bản"],
    ["Gate", "Phát hiện orphan và khóa lỗi"],
  ];
  captions.forEach((d, i) => card(s, 0.68 + i * 3.03, 5.98, 2.72, 0.72, d[0], d[1], { shadow: false, titleSize: 12, bodySize: 9.5, fill: i % 2 ? "F0F6F8" : C.white }));
  addSource(s, "Nguồn chỉnh sửa: report_latex/images/sources/etl_pipeline.drawio");
  notes(s, "Quy trình gồm collect, cache, clean, exact-ID enrich, normalize, load, reason và validate. Raw cache là bất biến; manifest ghi checksum và số lượng. Import dùng batch và MERGE nên có thể chạy lặp. Runtime chỉ import lại khi checksum processed hoặc số Movie thay đổi.");
}

// 11 — Quality
{
  const s = lightSlide("Đồ thị cuối cùng vượt qua toàn bộ quality gate", "Một bản ghi Movie không có quan hệ bị loại; ảnh chụp hợp lệ còn 4.999 phim.", "Chất lượng dữ liệu");
  metric(s, 0.65, 1.98, 2.2, "76.612", "Tổng số nút", C.teal);
  metric(s, 3.05, 1.98, 2.2, "846.309", "Tổng số quan hệ", C.purple);
  metric(s, 5.45, 1.98, 2.2, "53.555", "Person", C.green);
  metric(s, 7.85, 1.98, 2.2, "12.509", "Keyword", C.amber);
  metric(s, 10.25, 1.98, 2.2, "5.530", "Studio", C.navy2);
  s.addText("0", { x: 0.75, y: 4.0, w: 2.1, h: 0.75, fontFace: "Arial", fontSize: 48, bold: true, color: C.green, margin: 0, align: "center" });
  s.addText("vi phạm cấu trúc", { x: 0.75, y: 4.78, w: 2.1, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: C.ink, margin: 0, align: "center" });
  const gates = ["Orphan Movie", "Stable ID trùng", "Thiếu thuộc tính bắt buộc", "Cạnh sai kiểu/đầu mút"];
  gates.forEach((g, i) => {
    const x = 3.4 + (i % 2) * 4.35, y = 3.95 + Math.floor(i / 2) * 1.08;
    s.addShape(pptx.ShapeType.ellipse, { x, y, w: 0.42, h: 0.42, fill: { color: C.green }, line: { color: C.green } });
    s.addText("✓", { x, y: y + 0.05, w: 0.42, h: 0.2, fontFace: "Arial", fontSize: 12, bold: true, color: C.white, align: "center", margin: 0 });
    s.addText(g, { x: x + 0.62, y: y + 0.03, w: 3.4, h: 0.28, fontFace: "Calibri", fontSize: 13, bold: true, color: C.ink, margin: 0, fit: "shrink" });
  });
  addSource(s, "Nguồn số liệu: experiments/results/quality/{knowledge_quality_audit,neo4j_validation}.json");
  notes(s, "Ảnh chụp cuối có 76.612 nút và 846.309 quan hệ. Không có orphan Movie, stable ID trùng, thuộc tính bắt buộc bị thiếu hay cạnh sai kiểu. Một Movie không có quan hệ đã bị loại ở bước kiểm tra trước khi nạp.");
}

// 12 — ER
{
  const s = lightSlide("Phân giải thực thể: exact trước, fuzzy có kiểm soát", "Mục tiêu là tránh false positive; trường hợp mơ hồ có thể từ chối thay vì nối sai.", "Định danh và provenance");
  addImageContain(s, A("entity_resolution_flow"), 0.63, 1.94, 8.1, 4.66);
  metric(s, 9.05, 1.98, 3.55, "1,000", "Precision", C.green, "100 cặp silver");
  metric(s, 9.05, 3.58, 3.55, "0,933", "Recall", C.amber, "5 trường hợp abstain");
  metric(s, 9.05, 5.18, 3.55, "0,966", "F1", C.purple, "nearest-name hard negatives");
  addSource(s, "Nguồn: entity_resolution.json · sơ đồ: report_latex/images/sources/entity_resolution_flow.drawio");
  notes(s, "Phép nối TMDB–IMDb dùng exact imdb_id với confidence 1.0. Entity linker ưu tiên exact và full-text candidate trước fuzzy reranking. Trên 100 cặp silver, precision 1.0, recall 0.933 và F1 0.966. Năm lỗi là abstention bảo thủ, không có false positive.");
}

// 13 — Cypher
{
  const s = lightSlide("Cypher biến câu hỏi quan hệ thành mẫu đường đi", "Tham số người dùng được truyền riêng; cấu trúc truy vấn lấy từ danh mục cố định.", "Truy vấn");
  s.addShape(pptx.ShapeType.roundRect, { x: 0.68, y: 1.92, w: 7.0, h: 4.5, rectRadius: 0.05, fill: { color: "10283D" }, line: { color: "10283D" }, shadow: shadow() });
  const code = [
    "MATCH (d:Person)-[:DIRECTED]->(m:Movie)",
    "      -[:HAS_GENRE]->(g:Genre)",
    "WHERE g.name = $genre",
    "RETURN d.name, count(m) AS movie_count",
    "ORDER BY movie_count DESC",
    "LIMIT $limit",
  ].join("\n");
  s.addText(code, { x: 1.02, y: 2.28, w: 6.35, h: 2.95, fontFace: "Courier New", fontSize: 15, color: "D9E8F2", margin: 0.05, breakLine: false, fit: "shrink" });
  s.addText("$genre · $limit", { x: 1.02, y: 5.62, w: 2.6, h: 0.36, fontFace: "Courier New", fontSize: 13, bold: true, color: "8FD0CC", margin: 0 });
  card(s, 8.05, 1.95, 4.55, 1.05, "Tra cứu", "Phim theo đạo diễn · diễn viên theo phim", { badge: "1", shadow: false, bodySize: 11 });
  card(s, 8.05, 3.18, 4.55, 1.05, "Nhiều bước (multi-hop)", "Phim chung · đạo diễn → phim → thể loại", { badge: "2", badgeColor: C.amber, shadow: false, bodySize: 11, fill: C.amberBg });
  card(s, 8.05, 4.41, 4.55, 1.05, "Đường đi và suy diễn", "shortestPath([*..8]) · CO_STARRED_WITH", { badge: "3", badgeColor: C.purple, shadow: false, bodySize: 11, fill: C.purpleBg });
  card(s, 8.05, 5.64, 4.55, 0.78, "An toàn", "Không nối chuỗi đầu vào vào Cypher.", { badge: "✓", badgeColor: C.green, shadow: false, titleSize: 13, bodySize: 10, fill: C.greenBg });
  notes(s, "Hệ thống có danh mục truy vấn tham số hóa gồm lookup, aggregation, multi-hop, shortest path và similarity. Ví dụ này đi từ director qua movie sang genre. Giá trị genre và limit là tham số; người dùng không thể thay đổi cấu trúc Cypher.");
}

// 14 — reasoning
{
  const s = lightSlide("CO_STARRED_WITH là fact suy ra có thể kiểm chứng", "Không gọi đây là OWL reasoning: đây là phép vật chất hóa luật nghiệp vụ bằng Cypher.", "Suy diễn");
  addImageContain(s, A("costar_reasoning"), 0.65, 1.92, 8.0, 4.7);
  card(s, 8.98, 1.95, 3.7, 1.18, "Sự kiện được khẳng định", "ACTED_IN đến từ danh sách vai diễn của TMDB.", { fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal });
  card(s, 8.98, 3.43, 3.7, 1.18, "Sự kiện suy ra", "CO_STARRED_WITH được tạo từ phim chung.", { fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple });
  card(s, 8.98, 4.91, 3.7, 1.4, "Bằng chứng", "movie_count · evidence_movie_ids · derived=true", { fill: C.greenBg, stroke: "C4E2D1", titleColor: C.green, bodySize: 12 });
  addSource(s, "Nguồn chỉnh sửa: report_latex/images/sources/costar_reasoning.drawio");
  notes(s, "Từ hai cạnh ACTED_IN cùng đi vào một Movie, hệ thống vật chất hóa CO_STARRED_WITH. Cạnh suy ra lưu số phim chung và danh sách Movie hỗ trợ, nên có thể lần ngược. Đây là rule-based materialization bằng Cypher, tách biệt với OWL entailment.");
}

// 15 — QA
{
  const s = lightSlide("Giá trị của chatbot nằm ở việc điều phối Cypher an toàn", "Ngôn ngữ tự nhiên chọn ý định và thực thể; Neo4j thực hiện traversal và trả bằng chứng.", "Ứng dụng hỏi–đáp");
  addImageContain(s, A("qa_sequence"), 0.62, 1.92, 8.25, 4.7);
  card(s, 9.18, 1.94, 3.48, 1.15, "9 ý định cố định", "Tra cứu · tổng hợp · nhiều bước · đường đi ngắn nhất", { fill: "EAF2F8", stroke: "BDD4E5", titleSize: 15, bodySize: 10.5 });
  card(s, 9.18, 3.37, 3.48, 1.15, "Liên kết thực thể", "“Cristopher Nolan” → Christopher Nolan + độ tin cậy", { fill: C.amberBg, stroke: "F1D5AA", titleSize: 15, bodySize: 10.5 });
  card(s, 9.18, 4.8, 3.48, 1.15, "Bằng chứng đồ thị", "Ý định · thực thể · bản ghi/đường đi · độ trễ", { fill: C.greenBg, stroke: "C4E2D1", titleSize: 15, bodySize: 10.5 });
  addSource(s, "Nguồn chỉnh sửa: report_latex/images/sources/qa_sequence.drawio");
  notes(s, "Chatbot không thay Neo4j và không sinh Cypher tự do. Parser chỉ nhận diện một trong chín ý định và trích slot. Entity linker chuẩn hóa thực thể; catalog chọn mẫu Cypher cố định; Neo4j thực hiện traversal. Response trả cả intent, confidence, evidence và latency.");
}

// 16 — Recommendation
{
  const s = lightSlide("Gợi ý giải thích được bằng đóng góp trên đồ thị", "IDF giảm ảnh hưởng của đặc trưng quá phổ biến; mỗi đề xuất kèm các đặc trưng chung tạo điểm.", "Ứng dụng gợi ý");
  addImageContain(s, A("recommendation_explanation"), 0.63, 1.92, 7.78, 4.7);
  s.addText("contribution = type_weight × (1 + ln((N+1)/(df+1)))", { x: 8.72, y: 2.02, w: 3.9, h: 0.62, fontFace: "Courier New", fontSize: 12.5, bold: true, color: C.navy, margin: 0, fit: "shrink" });
  const weights = [["Đạo diễn", "3,0", C.purple], ["Diễn viên", "2,0", C.teal], ["Thể loại", "1,5", C.green], ["Từ khóa", "1,0", C.amber]];
  weights.forEach((d, i) => {
    const y = 2.95 + i * 0.72;
    s.addText(d[0], { x: 8.75, y, w: 1.25, h: 0.24, fontFace: "Calibri", fontSize: 12, bold: true, color: C.ink, margin: 0 });
    s.addShape(pptx.ShapeType.rect, { x: 10.08, y: y + 0.03, w: Number(d[1].replace(",", ".")) * 0.56, h: 0.18, fill: { color: d[2] }, line: { color: d[2] } });
    s.addText(d[1], { x: 11.9, y, w: 0.5, h: 0.24, fontFace: "Arial", fontSize: 11, bold: true, color: d[2], align: "right", margin: 0 });
  });
  card(s, 8.72, 5.92, 3.9, 0.72, "Điểm được tính trong Neo4j", "Không tải toàn bộ graph về Python.", { shadow: false, titleSize: 12, bodySize: 9.5, fill: C.greenBg, stroke: "C4E2D1" });
  addSource(s, "Nguồn chỉnh sửa: report_latex/images/sources/recommendation_explanation.drawio");
  notes(s, "Ranker dùng IDF-weighted graph similarity. Đặc trưng chung hiếm đóng góp nhiều hơn đặc trưng phổ biến. Trọng số ưu tiên director và actor. Điểm và explanation đều được tính từ traversal trong Neo4j, không tải toàn graph về Python.");
}

// 17 — Semantic layer
{
  const s = lightSlide("RDF/OWL bổ sung lớp chuẩn ngữ nghĩa", "Cùng ảnh chụp dữ liệu được xuất sang Turtle với URI ổn định và truy vấn bằng SPARQL.", "Ngữ nghĩa");
  addImageContain(s, A("ontology_diagram"), 0.62, 1.92, 7.75, 4.68);
  card(s, 8.72, 1.94, 3.92, 1.1, "Khả năng liên thông", "URI ổn định và từ vựng chuẩn hóa.", { badge: "1", shadow: false, fill: C.purpleBg, stroke: "D9CFE8" });
  card(s, 8.72, 3.28, 3.92, 1.1, "Ràng buộc", "Functional property · disjoint class · required title.", { badge: "2", badgeColor: C.purple, shadow: false, fill: C.purpleBg, stroke: "D9CFE8" });
  card(s, 8.72, 4.62, 3.92, 1.1, "Suy diễn ngữ nghĩa", "miền/phạm vi · inverseOf · quan hệ đối xứng.", { badge: "3", badgeColor: C.purple, shadow: false, fill: C.purpleBg, stroke: "D9CFE8" });
  card(s, 8.72, 5.96, 3.92, 0.65, "10/10 SPARQL", "RDFLib và Jena/Fuseki.", { shadow: false, titleSize: 12, bodySize: 9.5, fill: C.greenBg, stroke: "C4E2D1" });
  addSource(s, "Nguồn chỉnh sửa: report_latex/images/sources/ontology_diagram.drawio");
  notes(s, "RDF/OWL không thay Neo4j trong đường chạy ứng dụng. Nó cung cấp URI ổn định, vocabulary, ràng buộc và entailment. Cùng tập dữ liệu được kiểm tra bằng RDFLib và Jena/Fuseki; cả mười truy vấn SPARQL đều chạy thành công.");
}

// 18 — Semantic result
{
  const s = lightSlide("Suy diễn ngữ nghĩa đã chạy trên toàn ảnh chụp", "Kết quả chỉ đại diện cho RDFS/OWL-RL subset đã khai báo, không phải full OWL 2 DL.", "Ngữ nghĩa");
  addImageContain(s, A("semantic_reasoning"), 0.65, 1.92, 7.25, 4.7);
  metric(s, 8.25, 2.0, 2.05, "342.683", "Triple trước", C.teal);
  metric(s, 10.55, 2.0, 2.05, "429.192", "Triple sau", C.purple);
  metric(s, 8.25, 3.7, 2.05, "+86.509", "Triple suy ra", C.amber);
  metric(s, 10.55, 3.7, 2.05, "0", "Vi phạm ngữ nghĩa", C.green);
  card(s, 8.25, 5.45, 4.35, 1.0, "Hai loại suy diễn", "OWL entailment cho semantics; Cypher rule cho CO_STARRED_WITH.", { fill: C.purpleBg, stroke: "D9CFE8", titleSize: 14, bodySize: 10.5 });
  addSource(s, "Nguồn: experiments/results/semantic/semantic_reasoning.json");
  notes(s, "Materialization tăng từ 342.683 lên 429.192 triple, tức 86.509 triple suy ra và không có vi phạm trong tập luật khai báo. Em phân biệt rõ OWL entailment với luật nghiệp vụ CO_STARRED_WITH bằng Cypher.");
}

// 19 — Evaluation design
{
  const s = lightSlide("Đánh giá được thiết kế theo từng tuyên bố", "Mỗi metric gắn với dataset, protocol và giới hạn diễn giải cụ thể.", "Thực nghiệm");
  const rows = [
    ["Hạng mục", "Tập đánh giá", "Metric"],
    ["Chất lượng dữ liệu", "Toàn corpus", "missing · duplicate · orphan"],
    ["Phân giải thực thể", "100 cặp silver", "P · R · F1"],
    ["Suy diễn co-star", "50 fact silver", "precision"],
    ["Hỏi–đáp", "20 câu smoke", "accuracy + evidence"],
    ["Gợi ý", "20 case silver", "P@10 · NDCG@10"],
    ["Hiệu năng", "4 quy mô × 4 query", "median · p95 · 100 lần"],
  ];
  s.addTable(rows, { x: 0.67, y: 1.94, w: 8.2, h: 4.75, border: { type: "solid", color: C.line, pt: 1 }, fill: C.white, color: C.ink, fontFace: "Calibri", fontSize: 11.2, margin: 0.08, rowH: 0.6, valign: "mid", colW: [2.3, 2.6, 3.3], autoFit: false });
  card(s, 9.22, 1.96, 3.42, 1.25, "Silver ≠ ground truth độc lập", "Corpus được sinh tất định, có provenance và rubric công bố.", { fill: C.amberBg, stroke: "F1D5AA", titleColor: C.amber, titleSize: 14, bodySize: 10.5 });
  card(s, 9.22, 3.54, 3.42, 1.25, "So sánh công bằng", "Neo4j và SQLite dùng cùng snapshot, máy, warm-up và số lần chạy.", { fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal, titleSize: 14, bodySize: 10.5 });
  card(s, 9.22, 5.12, 3.42, 1.25, "Không vượt quá bằng chứng", "Không suy rộng sang concurrency, cold cache hay production scale.", { fill: C.redBg, stroke: "E9C3C6", titleColor: C.red, titleSize: 14, bodySize: 10.5 });
  notes(s, "Mỗi tuyên bố có một tập đánh giá riêng. Entity resolution và recommendation dùng silver corpus có provenance. QA là smoke test 20 câu. Benchmark chạy cùng snapshot, máy, warm-up và 100 iterations. Vì vậy em không suy rộng kết quả thành độ chính xác sản xuất hoặc scalability tổng quát.");
}

// 20 — Results
{
  const s = lightSlide("Kết quả chính: đúng cấu trúc, có bằng chứng, còn dư địa cải thiện", "Các con số dưới đây đều thuộc lần chạy 5.000 đầu vào ngày 24/07/2026.", "Kết quả");
  metric(s, 0.65, 1.95, 2.25, "20/20", "QA smoke", C.green, "Neo4j + evidence");
  metric(s, 3.1, 1.95, 2.25, "0,966", "Entity F1", C.teal, "100 cặp silver");
  metric(s, 5.55, 1.95, 2.25, "1,00", "Co-star precision", C.purple, "50 fact silver");
  metric(s, 8.0, 1.95, 2.25, "0,635", "Recommendation P@10", C.amber, "20 case silver");
  metric(s, 10.45, 1.95, 2.25, "0,672", "NDCG@10", C.red, "20 case silver");
  s.addChart(pptx.ChartType.bar, [
    { name: "Giá trị", labels: ["QA", "ER F1", "Co-star", "P@10", "NDCG@10"], values: [1.0, 0.966, 1.0, 0.635, 0.672] },
  ], {
    x: 0.8, y: 3.75, w: 7.2, h: 2.62,
    catAxisLabelFontFace: "Arial", catAxisLabelFontSize: 10,
    valAxisLabelFontFace: "Arial", valAxisLabelFontSize: 9,
    valAxisMinVal: 0, valAxisMaxVal: 1, valAxisMajorUnit: 0.2,
    showLegend: false, showTitle: false, showValue: true, dataLabelPosition: "outEnd",
    chartColors: [C.teal], showCatName: false, showValAxisTitle: false,
    valGridLine: { color: "D7DEE8", width: 1 }, catGridLine: { style: "none" },
    border: { color: "D7DEE8", pt: 1 }, showBorder: false,
  });
  card(s, 8.4, 3.82, 4.25, 2.48, "Cách đọc thận trọng", "• QA là smoke corpus được quản lý.\n• Entity precision cao nhờ abstention bảo thủ.\n• Recommendation là metric silver, chưa phải đánh giá người dùng.\n• Mọi output gợi ý đều có đường giải thích.", { fill: C.white, stroke: C.line, titleSize: 17, bodySize: 12.5 });
  addSource(s, "Nguồn: experiments/results/summary/quality_metrics.csv");
  notes(s, "QA smoke đạt 20/20; entity resolution F1 0.966; co-star precision 1.0; recommendation đạt P@10 0.635 và NDCG@10 0.672. Các metric silver phản ánh protocol đã công bố, chưa thay thế đánh giá người dùng độc lập.");
}

// 21 — Benchmark and ablation
{
  const s = lightSlide("Phép đo so sánh cho thấy sự đánh đổi", "SQLite nhanh hơn ở toàn bộ cặp truy vấn/quy mô; Neo4j đổi lại mô hình duyệt đồ thị và bằng chứng trực tiếp.", "Phân tích");
  s.addChart(pptx.ChartType.line, [
    { name: "Neo4j · common_movies", labels: ["500", "1.000", "2.000", "4.999"], values: [15.16, 16.90, 25.67, 44.31] },
    { name: "SQLite · common_movies", labels: ["500", "1.000", "2.000", "4.999"], values: [2.77, 7.31, 14.19, 40.00] },
  ], {
    x: 0.65, y: 1.96, w: 6.2, h: 3.55,
    showTitle: true, title: "Median latency · common_movies (ms)",
    titleFontFace: "Calibri", titleFontSize: 14, titleColor: C.navy,
    catAxisLabelFontFace: "Arial", catAxisLabelFontSize: 9,
    valAxisLabelFontFace: "Arial", valAxisLabelFontSize: 9,
    showLegend: true, legendPos: "b", legendFontSize: 9,
    chartColors: [C.teal, C.amber], showValue: false,
    valGridLine: { color: "D7DEE8", width: 1 }, catGridLine: { style: "none" },
    showBorder: false,
  });
  s.addChart(pptx.ChartType.bar, [
    { name: "P@10", labels: ["Overlap", "Weighted Jaccard", "Hybrid", "IDF production"], values: [0.67, 0.64, 0.59, 0.635] },
    { name: "NDCG@10", labels: ["Overlap", "Weighted Jaccard", "Hybrid", "IDF production"], values: [0.723, 0.699, 0.657, 0.672] },
  ], {
    x: 7.15, y: 1.96, w: 5.5, h: 3.55,
    showTitle: true, title: "Lịch sử thiết kế ranker · 20 case",
    titleFontFace: "Calibri", titleFontSize: 14, titleColor: C.navy,
    catAxisLabelFontFace: "Arial", catAxisLabelFontSize: 8.5,
    valAxisLabelFontFace: "Arial", valAxisLabelFontSize: 9,
    valAxisMinVal: 0, valAxisMaxVal: 0.8, valAxisMajorUnit: 0.2,
    showLegend: true, legendPos: "b", legendFontSize: 9,
    chartColors: [C.teal, C.purple], showValue: false,
    valGridLine: { color: "D7DEE8", width: 1 }, catGridLine: { style: "none" },
    showBorder: false,
  });
  card(s, 0.75, 5.75, 5.95, 0.78, "Kết luận hiệu năng", "Đo warm-cache, 100 lần/query, không đo concurrency hoặc cold cache.", { shadow: false, titleSize: 13, bodySize: 10, fill: C.amberBg, stroke: "F1D5AA" });
  card(s, 7.15, 5.75, 5.48, 0.78, "Kết luận gợi ý", "Các mốc cũ là lịch sử thiết kế, không phải lựa chọn runtime.", { shadow: false, titleSize: 13, bodySize: 10, fill: C.purpleBg, stroke: "D9CFE8" });
  addSource(s, "Nguồn: multiscale_benchmark.csv · recommendation_ablation.json · recommendation.json");
  notes(s, "SQLite nhanh hơn trên tất cả query và quy mô đã đo. Điều đó cho thấy không nên bán đồ thị bằng tốc độ tuyệt đối; lợi ích là biểu diễn và bằng chứng traversal. Với recommendation, các phương pháp cũ chỉ là lịch sử thiết kế; runtime hiện dùng IDF-weighted graph.");
}

// 22 — Demo
{
  const s = darkSlide();
  s.addText("TRÌNH DIỄN END-TO-END", { x: 0.75, y: 0.65, w: 4.2, h: 0.3, fontFace: "Arial", fontSize: 10, bold: true, color: "8FD0CC", charSpacing: 1.7, margin: 0 });
  s.addText("Từ câu hỏi tự nhiên đến đường đi bằng chứng", { x: 0.75, y: 1.18, w: 8.6, h: 0.75, fontFace: "Calibri", fontSize: 30, bold: true, color: C.white, margin: 0, fit: "shrink" });
  const demo = [
    ["01", "/stats", "Xác nhận graph thật đang chạy"],
    ["02", "QA có typo", "Entity linking + fixed Cypher"],
    ["03", "Multi-hop", "Shortest path / co-star evidence"],
    ["04", "Recommend", "Shared features + contribution"],
    ["05", "Neo4j", "Mở subgraph và query catalog"],
  ];
  demo.forEach((d, i) => {
    const x = 0.75 + i * 2.45;
    s.addShape(pptx.ShapeType.ellipse, { x, y: 3.25, w: 0.56, h: 0.56, fill: { color: i === 4 ? C.purple : C.teal }, line: { color: i === 4 ? C.purple : C.teal } });
    s.addText(d[0], { x, y: 3.39, w: 0.56, h: 0.18, fontFace: "Arial", fontSize: 10, bold: true, color: C.white, align: "center", margin: 0 });
    s.addText(d[1], { x, y: 4.05, w: 1.95, h: 0.34, fontFace: "Calibri", fontSize: 16, bold: true, color: C.white, margin: 0 });
    s.addText(d[2], { x, y: 4.55, w: 1.95, h: 0.72, fontFace: "Calibri", fontSize: 12, color: "C9D8E4", margin: 0, fit: "shrink" });
    if (i < 4) s.addShape(pptx.ShapeType.line, { x: x + 0.75, y: 3.53, w: 1.45, h: 0, line: { color: "7893A8", width: 1.3, endArrowType: "triangle" } });
  });
  s.addText("Dữ liệu đã import · Không phụ thuộc Internet · Swagger là phương án dự phòng", { x: 0.75, y: 6.43, w: 9.2, h: 0.3, fontFace: "Arial", fontSize: 10, color: "8FD0CC", margin: 0 });
  notes(s, "Em xin chuyển sang phần trình diễn. Em sẽ xác nhận graph qua stats, hỏi một câu có typo, một câu multi-hop, mở recommendation explanation và nếu còn thời gian xem subgraph trong Neo4j Browser. Toàn bộ dữ liệu đã import và không phụ thuộc Internet.");
}

// 23 — Limits
{
  const s = lightSlide("Giới hạn được xem là một phần của kết quả", "Các kết luận chỉ có giá trị trong ảnh chụp dữ liệu và protocol đã công bố.", "Giới hạn và hướng phát triển");
  const limits = [
    ["QA đóng", "Chín ý định; chưa phải open-domain QA.", "Mở rộng intent dựa trên câu hỏi thực tế."],
    ["Silver corpus", "Tất định và có provenance nhưng chưa có người chấm độc lập.", "Bổ sung đánh giá người dùng và inter-rater review."],
    ["Quy mô", "Tối đa 4.999 phim; chưa đo concurrent/cold-cache.", "Thử nghiệm graph lớn hơn và tải đồng thời."],
    ["Độ phủ", "Top-20 cast; IMDb mới enrich Movie.", "Mở rộng credits và liên kết Person/Wikidata."],
  ];
  limits.forEach((d, i) => {
    const y = 1.9 + i * 1.22;
    s.addShape(pptx.ShapeType.roundRect, { x: 0.68, y, w: 2.2, h: 0.9, rectRadius: 0.04, fill: { color: C.redBg }, line: { color: "E9C3C6" } });
    s.addText(d[0], { x: 0.92, y: y + 0.26, w: 1.7, h: 0.28, fontFace: "Calibri", fontSize: 15, bold: true, color: C.red, align: "center", margin: 0 });
    s.addText(d[1], { x: 3.2, y: y + 0.1, w: 4.25, h: 0.68, fontFace: "Calibri", fontSize: 12.2, color: C.ink, margin: 0, valign: "mid", fit: "shrink" });
    s.addShape(pptx.ShapeType.line, { x: 7.62, y: y + 0.45, w: 0.75, h: 0, line: { color: C.muted, width: 1.4, endArrowType: "triangle" } });
    s.addText(d[2], { x: 8.58, y: y + 0.1, w: 3.95, h: 0.68, fontFace: "Calibri", fontSize: 12.2, bold: true, color: C.green, margin: 0, valign: "mid", fit: "shrink" });
  });
  s.addText("GIỚI HẠN HIỆN TẠI", { x: 3.2, y: 6.72, w: 2.5, h: 0.22, fontFace: "Arial", fontSize: 8.5, bold: true, color: C.red, charSpacing: 1.2, margin: 0 });
  s.addText("HƯỚNG PHÁT TRIỂN", { x: 8.58, y: 6.72, w: 2.5, h: 0.22, fontFace: "Arial", fontSize: 8.5, bold: true, color: C.green, charSpacing: 1.2, margin: 0 });
  notes(s, "Hạn chế chính là QA chỉ có chín ý định, corpus đánh giá chủ yếu là silver, quy mô tối đa 4.999 phim và top-20 cast. Hướng tiếp theo là thu thập câu hỏi thật, đánh giá người dùng, benchmark tải đồng thời và mở rộng liên kết sang Person/Wikidata.");
}

// 24 — Conclusion
{
  const s = darkSlide();
  s.addText("KẾT LUẬN", { x: 0.75, y: 0.68, w: 2.5, h: 0.28, fontFace: "Arial", fontSize: 10, bold: true, color: "8FD0CC", charSpacing: 1.7, margin: 0 });
  s.addText("Đồ thị tri thức tạo giá trị khi\nmỗi quan hệ đều có thể được kiểm chứng", { x: 0.75, y: 1.18, w: 9.2, h: 1.25, fontFace: "Calibri", fontSize: 31, bold: true, color: C.white, margin: 0, fit: "shrink" });
  const conclusions = [
    ["01", "Tích hợp đúng", "TMDB + IMDb, stable ID, provenance và quy trình tái lập."],
    ["02", "Truy vấn được", "Cypher multi-hop, derived fact và semantic entailment."],
    ["03", "Giải thích được", "QA và gợi ý trả cả thực thể, path và đóng góp điểm."],
  ];
  conclusions.forEach((d, i) => {
    const x = 0.78 + i * 4.06;
    s.addText(d[0], { x, y: 3.55, w: 0.45, h: 0.28, fontFace: "Arial", fontSize: 12, bold: true, color: "8FD0CC", margin: 0 });
    s.addText(d[1], { x, y: 4.03, w: 3.35, h: 0.35, fontFace: "Calibri", fontSize: 20, bold: true, color: C.white, margin: 0 });
    s.addText(d[2], { x, y: 4.58, w: 3.25, h: 0.82, fontFace: "Calibri", fontSize: 13.5, color: "C9D8E4", margin: 0, fit: "shrink" });
  });
  s.addText("Xin cảm ơn thầy. Em xin lắng nghe câu hỏi và phản biện.", { x: 0.78, y: 6.5, w: 8.5, h: 0.4, fontFace: "Calibri", fontSize: 16, bold: true, color: "8FD0CC", margin: 0 });
  notes(s, "Tóm lại, đề tài đã xây dựng được một quy trình tích hợp đa nguồn có stable identity và provenance; đồ thị hỗ trợ traversal, suy diễn và semantic validation; hai ứng dụng trả kết quả kèm bằng chứng. Em xin cảm ơn thầy và xin lắng nghe phản biện.");
}

// Appendix 1
{
  const s = lightSlide("Phụ lục · Chín ý định và nhóm Cypher", "Chỉ mở khi giảng viên hỏi sâu về phạm vi chatbot.", "Phản biện");
  const intents = [
    ["movies_by_director", "Lookup 1–2 hop"],
    ["actors_in_movie", "Lookup 1 hop"],
    ["common_movies", "Shared neighbor"],
    ["movies_by_genre_rating", "Filter + traversal"],
    ["co_stars", "Derived edge"],
    ["directors_by_genre", "Aggregation 2 hop"],
    ["shortest_path", "shortestPath([*..8])"],
    ["similar_movies", "Graph similarity"],
    ["movie_details", "Canonical lookup"],
  ];
  intents.forEach((d, i) => {
    const col = i % 3, row = Math.floor(i / 3), x = 0.68 + col * 4.16, y = 1.95 + row * 1.43;
    card(s, x, y, 3.82, 1.08, d[0], d[1], { badge: String(i + 1), shadow: false, titleSize: 13, bodySize: 10.5, fill: col === 2 ? C.purpleBg : C.white, stroke: col === 2 ? "D9CFE8" : C.line });
  });
  card(s, 0.68, 6.35, 12.02, 0.55, "Ranh giới an toàn", "Parser chỉ chọn intent và tham số; cấu trúc Cypher luôn lấy từ catalog cố định.", { shadow: false, titleSize: 11.5, bodySize: 9.5, fill: C.greenBg, stroke: "C4E2D1" });
  notes(s, "Phụ lục này ánh xạ chín ý định sang nhóm truy vấn. Điểm cần nhấn mạnh là parser không viết Cypher; nó chỉ chọn intent và tham số cho catalog cố định.");
}

// Appendix 2
{
  const s = lightSlide("Phụ lục · Hai lớp suy diễn không bị đánh đồng", "OWL entailment phục vụ ngữ nghĩa; Cypher materialization phục vụ luật nghiệp vụ.", "Phản biện");
  card(s, 0.72, 1.95, 5.75, 4.45, "RDFS / OWL-RL subset", "domain / range → suy ra kiểu\ninverseOf → actedIn ⇄ hasActor\nsymmetric property\nfunctional/disjoint validation\n\n342.683 → 429.192 triple\n+86.509 inferred · 0 violation", { fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple, titleSize: 20, bodySize: 15 });
  card(s, 6.85, 1.95, 5.75, 4.45, "Cypher rule nghiệp vụ", "Person A → Movie ← Person B\n\nVật chất hóa CO_STARRED_WITH\nmovie_count\nevidence_movie_ids\nderived=true\n\nPrecision silver: 1,00 / 50 fact", { fill: C.greenBg, stroke: "C4E2D1", titleColor: C.green, titleSize: 20, bodySize: 15 });
  addSource(s, "Nguồn: semantic_reasoning.json · reasoning.json · costar_reasoning.drawio");
  notes(s, "Nếu được hỏi về reasoning, cần phân biệt hai lớp. RDFS/OWL-RL subset suy ra các fact ngữ nghĩa theo ontology. CO_STARRED_WITH là luật nghiệp vụ được vật chất hóa bằng Cypher và lưu evidence.");
}

pptx.writeFile({ fileName: OUT });
