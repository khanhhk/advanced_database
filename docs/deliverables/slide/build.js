const pptxgen = require("pptxgenjs");
const path = require("path");
const { imageSize } = require("image-size");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Hoàng Kim Khánh";
pptx.subject = "Cơ sở lý thuyết Knowledge Graph và nghiên cứu tình huống phim";
pptx.title = "Knowledge Graph: Nền tảng lý thuyết và nghiên cứu tình huống phim";
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
    { text: { text: "KNOWLEDGE GRAPH", options: { x: 0.58, y: 0.18, w: 4.3, h: 0.22, fontFace: "Arial", fontSize: 9, bold: true, color: "337B80", charSpacing: 1.5, margin: 0 } } },
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
  s.addText("Knowledge Graph\nNền tảng lý thuyết", { x: 0.72, y: 1.22, w: 7.2, h: 1.55, fontFace: "Calibri", fontSize: 34, bold: true, color: C.white, margin: 0, breakLine: false, fit: "shrink" });
  s.addText("Từ định danh và schema đến truy vấn, suy diễn và khả năng giải thích\nNghiên cứu tình huống: đồ thị tri thức phim đa nguồn", { x: 0.75, y: 3.02, w: 6.45, h: 0.82, fontFace: "Calibri", fontSize: 15.5, color: "D6E3ED", margin: 0, fit: "shrink" });
  addImageContain(s, A("movie_kg_overview"), 7.55, 1.15, 5.15, 3.95, false);
  s.addText("Học viên", { x: 0.75, y: 5.35, w: 1.1, h: 0.24, fontFace: "Arial", fontSize: 9, bold: true, color: "8FD0CC", margin: 0 });
  s.addText("Hoàng Kim Khánh · 20252307M", { x: 0.75, y: 5.68, w: 4.4, h: 0.34, fontFace: "Calibri", fontSize: 15, bold: true, color: C.white, margin: 0 });
  s.addText("Giảng viên hướng dẫn", { x: 6.8, y: 5.35, w: 1.8, h: 0.24, fontFace: "Arial", fontSize: 9, bold: true, color: "8FD0CC", margin: 0 });
  s.addText("TS. Trần Ngọc Thăng", { x: 6.8, y: 5.68, w: 3.4, h: 0.34, fontFace: "Calibri", fontSize: 15, bold: true, color: C.white, margin: 0 });
  s.addText("ĐẠI HỌC BÁCH KHOA HÀ NỘI · KHOA TOÁN – TIN · 07/2026", { x: 0.75, y: 6.92, w: 8, h: 0.2, fontFace: "Arial", fontSize: 8.5, color: "9FB2C3", margin: 0 });
  notes(s, "Kính thưa thầy, bài trình bày tập trung vào nền tảng Knowledge Graph theo mô hình Property Graph: thực thể, quan hệ, schema, identity, truy vấn và suy diễn. Movie Knowledge Graph chỉ đóng vai trò nghiên cứu tình huống để kiểm chứng các nguyên lý. Chi tiết triển khai ứng dụng được trình bày trong báo cáo.");
}

// 2 — From data to knowledge
{
  const s = lightSlide("Từ dữ liệu đến tri thức có thể sử dụng", "Knowledge Graph không chỉ lưu giá trị; nó đặt giá trị vào ngữ cảnh, quan hệ và ngữ nghĩa.", "Nền tảng");
  const levels = [
    ["DỮ LIỆU", "“2010”, “Inception”, “Nolan”", C.muted, C.pale],
    ["THÔNG TIN", "Inception là một phim phát hành năm 2010.", C.teal, "EAF2F8"],
    ["TRI THỨC", "Christopher Nolan đạo diễn Inception.", C.purple, C.purpleBg],
    ["SUY LUẬN", "Nolan là đạo diễn của một phim khoa học viễn tưởng.", C.green, C.greenBg],
  ];
  levels.forEach((d, i) => {
    const x = 0.72 + i * 3.12;
    const y = 4.9 - i * 0.78;
    s.addShape(pptx.ShapeType.roundRect, { x, y, w: 2.62, h: 1.42 + i * 0.78, rectRadius: 0.05, fill: { color: d[3] }, line: { color: d[2], width: 1.3 }, shadow: shadow() });
    s.addText(d[0], { x: x + 0.2, y: y + 0.22, w: 2.2, h: 0.25, fontFace: "Arial", fontSize: 10, bold: true, color: d[2], charSpacing: 1.1, margin: 0 });
    s.addText(d[1], { x: x + 0.2, y: y + 0.7, w: 2.18, h: 0.72, fontFace: "Calibri", fontSize: 13, bold: i > 1, color: C.ink, margin: 0, fit: "shrink" });
    if (i < 3) s.addShape(pptx.ShapeType.line, { x: x + 2.66, y: y + 0.7, w: 0.38, h: -0.25, line: { color: C.muted, width: 1.4, endArrowType: "triangle" } });
  });
  s.addText("Ngữ cảnh + quan hệ + quy tắc làm cho dữ liệu trở thành tri thức có thể truy vấn và suy luận.", { x: 1.4, y: 6.48, w: 10.5, h: 0.34, fontFace: "Calibri", fontSize: 15, bold: true, color: C.navy, align: "center", margin: 0 });
  notes(s, "Ta phân biệt bốn mức. Dữ liệu là các ký hiệu rời rạc. Thông tin thêm ngữ cảnh. Tri thức nối các thực thể bằng một quan hệ có nghĩa. Khi có schema và quy tắc, hệ thống còn có thể suy ra sự kiện mới. Knowledge Graph chủ yếu hoạt động ở hai tầng cuối.");
}

// 3 — Definition and anatomy
{
  const s = lightSlide("Knowledge Graph là gì?", "Một mô hình tri thức dạng đồ thị, trong đó thực thể và quan hệ mang ngữ nghĩa có thể đọc bởi cả người và máy.", "Nền tảng");
  s.addShape(pptx.ShapeType.ellipse, { x: 1.0, y: 2.35, w: 2.0, h: 2.0, fill: { color: C.purpleBg }, line: { color: C.purple, width: 2 }, shadow: shadow() });
  s.addText("Christopher\nNolan", { x: 1.25, y: 2.95, w: 1.5, h: 0.55, fontFace: "Calibri", fontSize: 18, bold: true, color: C.purple, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.ellipse, { x: 5.6, y: 2.35, w: 2.0, h: 2.0, fill: { color: "EAF2F8" }, line: { color: C.teal, width: 2 }, shadow: shadow() });
  s.addText("Inception", { x: 5.85, y: 3.08, w: 1.5, h: 0.28, fontFace: "Calibri", fontSize: 18, bold: true, color: C.teal, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.line, { x: 3.05, y: 3.33, w: 2.48, h: 0, line: { color: C.green, width: 2.5, endArrowType: "triangle" } });
  s.addText("DIRECTED", { x: 3.52, y: 2.88, w: 1.55, h: 0.25, fontFace: "Arial", fontSize: 10, bold: true, color: C.green, align: "center", margin: 0 });
  card(s, 8.25, 1.95, 4.35, 1.25, "Thực thể (entity)", "Đối tượng có định danh: người, phim, địa điểm, tổ chức…", { badge: "N", badgeColor: C.purple, fill: C.purpleBg, stroke: "D9CFE8" });
  card(s, 8.25, 3.48, 4.35, 1.25, "Quan hệ (relationship)", "Liên kết có nghĩa và có hướng giữa các thực thể.", { badge: "E", badgeColor: C.green, fill: C.greenBg, stroke: "C4E2D1" });
  card(s, 8.25, 5.01, 4.35, 1.25, "Thuộc tính và định danh", "Thuộc tính mô tả thực thể; định danh ổn định cho biết chính xác thực thể nào đang được nói tới.", { badge: "P", badgeColor: C.teal, fill: "EAF2F8", stroke: "BDD4E5", bodySize: 10.8 });
  s.addText("subject", { x: 1.55, y: 4.58, w: 0.9, h: 0.22, fontFace: "Arial", fontSize: 9, color: C.muted, align: "center", margin: 0 });
  s.addText("predicate", { x: 3.72, y: 3.62, w: 1.1, h: 0.22, fontFace: "Arial", fontSize: 9, color: C.muted, align: "center", margin: 0 });
  s.addText("object", { x: 6.15, y: 4.58, w: 0.9, h: 0.22, fontFace: "Arial", fontSize: 9, color: C.muted, align: "center", margin: 0 });
  notes(s, "Không có một định nghĩa duy nhất được mọi tài liệu dùng giống hệt nhau. Trong phạm vi này, Knowledge Graph là mô hình đồ thị của các thực thể có định danh, các quan hệ có ngữ nghĩa và schema đủ để máy diễn giải. Mệnh đề cơ bản có thể đọc theo subject–predicate–object.");
}

// 4 — Schema and instance
{
  const s = lightSlide("Schema nói điều gì được phép; instance nói điều gì đang đúng", "Tách lớp khái niệm khỏi dữ liệu cụ thể giúp kiểm tra tính nhất quán và tái sử dụng mô hình.", "Nền tảng");
  s.addText("LỚP KHÁI NIỆM · TBOX / SCHEMA", { x: 0.75, y: 1.92, w: 4.2, h: 0.25, fontFace: "Arial", fontSize: 10, bold: true, color: C.purple, charSpacing: 1.1, margin: 0 });
  card(s, 0.75, 2.35, 2.3, 1.25, "Person", "Một lớp thực thể", { fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple });
  card(s, 4.0, 2.35, 2.3, 1.25, "Movie", "Một lớp thực thể", { fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal });
  s.addShape(pptx.ShapeType.line, { x: 3.08, y: 2.98, w: 0.87, h: 0, line: { color: C.green, width: 2, endArrowType: "triangle" } });
  s.addText("directed", { x: 3.08, y: 2.58, w: 0.87, h: 0.2, fontFace: "Arial", fontSize: 9, bold: true, color: C.green, align: "center", margin: 0 });
  s.addText("Domain: Person · Range: Movie", { x: 1.55, y: 3.92, w: 3.9, h: 0.28, fontFace: "Calibri", fontSize: 13, bold: true, color: C.navy, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.chevron, { x: 6.65, y: 2.25, w: 1.0, h: 2.05, fill: { color: C.amberBg }, line: { color: C.amber } });
  s.addText("thể hiện", { x: 6.7, y: 3.02, w: 0.7, h: 0.25, fontFace: "Arial", fontSize: 9, bold: true, color: C.amber, align: "center", margin: 0, rotate: 90 });
  s.addText("LỚP SỰ KIỆN · ABOX / INSTANCE", { x: 8.05, y: 1.92, w: 4.2, h: 0.25, fontFace: "Arial", fontSize: 10, bold: true, color: C.teal, charSpacing: 1.1, margin: 0 });
  card(s, 8.05, 2.35, 2.05, 1.25, "Nolan", "instanceOf Person", { fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple });
  card(s, 10.95, 2.35, 1.7, 1.25, "Inception", "instanceOf Movie", { fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal, titleSize: 15 });
  s.addShape(pptx.ShapeType.line, { x: 10.12, y: 2.98, w: 0.8, h: 0, line: { color: C.green, width: 2, endArrowType: "triangle" } });
  s.addText("directed", { x: 10.12, y: 2.58, w: 0.8, h: 0.2, fontFace: "Arial", fontSize: 9, bold: true, color: C.green, align: "center", margin: 0 });
  card(s, 1.1, 5.12, 3.35, 1.05, "Schema của đồ thị", "Quy định dữ liệu được phép có những lớp, quan hệ và ràng buộc nào.", { badge: "1", shadow: false, bodySize: 9.5 });
  card(s, 5.0, 5.12, 3.35, 1.05, "Cơ sở tri thức", "Kết hợp schema với tập thực thể và sự kiện đang được lưu.", { badge: "2", badgeColor: C.purple, shadow: false, fill: C.purpleBg, bodySize: 9.5 });
  card(s, 8.9, 5.12, 3.35, 1.05, "Đồ thị tri thức", "Tổ chức cơ sở tri thức thành các đường liên kết có thể truy vấn và kiểm chứng.", { badge: "3", badgeColor: C.green, shadow: false, fill: C.greenBg, bodySize: 9.5 });
  notes(s, "Schema mô tả label, loại quan hệ, thuộc tính và constraint chung. Instance chứa các node, edge và fact cụ thể, ví dụ Nolan DIRECTED Inception. Knowledge Graph kết hợp mô hình và dữ liệu thực tế để truy vấn.");
}

// 5 — Property Graph
{
  const s = lightSlide("Property Graph biểu diễn trực tiếp node, cạnh và thuộc tính", "Đây là mô hình đồ thị duy nhất được triển khai trong dự án.", "Mô hình biểu diễn");
  s.addShape(pptx.ShapeType.roundRect, { x: 0.68, y: 1.92, w: 7.72, h: 4.7, rectRadius: 0.05, fill: { color: C.white }, line: { color: C.line }, shadow: shadow() });
  s.addText("VÍ DỤ KHÁI NIỆM", { x: 0.98, y: 2.2, w: 2.2, h: 0.24, fontFace: "Arial", fontSize: 9.5, bold: true, color: C.teal, charSpacing: 1.1, margin: 0 });
  s.addShape(pptx.ShapeType.ellipse, { x: 1.08, y: 3.0, w: 1.65, h: 1.65, fill: { color: C.purpleBg }, line: { color: C.purple, width: 2 }, shadow: shadow() });
  s.addText(":Person", { x: 1.33, y: 3.55, w: 1.15, h: 0.3, fontFace: "Calibri", fontSize: 18, bold: true, color: C.purple, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.ellipse, { x: 5.92, y: 3.0, w: 1.65, h: 1.65, fill: { color: "EAF2F8" }, line: { color: C.teal, width: 2 }, shadow: shadow() });
  s.addText(":Movie", { x: 6.17, y: 3.55, w: 1.15, h: 0.3, fontFace: "Calibri", fontSize: 18, bold: true, color: C.teal, align: "center", margin: 0 });
  s.addShape(pptx.ShapeType.line, { x: 2.78, y: 3.82, w: 3.08, h: 0, line: { color: C.green, width: 2.5, endArrowType: "triangle" } });
  s.addText(":ACTED_IN", { x: 3.52, y: 3.32, w: 1.65, h: 0.26, fontFace: "Arial", fontSize: 11, bold: true, color: C.green, align: "center", margin: 0 });
  card(s, 0.98, 5.12, 2.25, 1.05, "Thuộc tính Person", "`name`, `birthday` mô tả người.", { shadow: false, titleSize: 12.5, bodySize: 9.2, fill: C.purpleBg, stroke: "D9CFE8" });
  card(s, 3.28, 5.12, 2.5, 1.05, "Thuộc tính ACTED_IN", "`character`, `cast_order` mô tả lần tham gia.", { shadow: false, titleSize: 12.5, bodySize: 9.2, fill: C.greenBg, stroke: "C4E2D1" });
  card(s, 5.83, 5.12, 2.25, 1.05, "Thuộc tính Movie", "`title`, `release_date` mô tả phim.", { shadow: false, titleSize: 12.5, bodySize: 9.2, fill: "EAF2F8", stroke: "BDD4E5" });
  card(s, 8.72, 1.96, 3.9, 1.2, "Node biểu diễn thực thể", "Mỗi node có nhãn lớp, định danh ổn định và các thuộc tính mô tả.", { badge: "N", fill: "EAF2F8", stroke: "BDD4E5", bodySize: 10.5 });
  card(s, 8.72, 3.44, 3.9, 1.2, "Cạnh biểu diễn quan hệ", "Mỗi cạnh có loại và hướng, nhờ đó liên kết mang ý nghĩa thay vì chỉ nối hai điểm.", { badge: "E", badgeColor: C.green, fill: C.greenBg, stroke: "C4E2D1", bodySize: 10.5 });
  card(s, 8.72, 4.92, 3.9, 1.2, "Thuộc tính giữ ngữ cảnh", "Thuộc tính có thể nằm trên node hoặc cạnh, tùy đối tượng mà nó thực sự mô tả.", { badge: "P", badgeColor: C.purple, fill: C.purpleBg, stroke: "D9CFE8", bodySize: 10.5 });
  notes(s, "Slide này chỉ minh họa cấu trúc chung của Property Graph: node có label và property, relationship có loại, hướng và cũng có property. Ví dụ ACTED_IN cho thấy character và cast_order mô tả chính lần một Person tham gia một Movie, nên chúng thuộc cạnh. Schema Movie Knowledge Graph đầy đủ sẽ được trình bày riêng ở slide 10.");
}

// 6 — Graph structures
{
  const s = lightSlide("Neighborhood, path và subgraph là đơn vị của tư duy đồ thị", "Các truy vấn graph không chỉ lọc bản ghi; chúng khám phá cấu trúc liên kết quanh thực thể.", "Cấu trúc đồ thị");
  card(s, 0.68, 1.95, 3.75, 4.45, "Lân cận (neighborhood)", "Là tập thực thể nối trực tiếp hoặc trong một số bước nhất định quanh một thực thể trung tâm.\n\nTrong dự án, lân cận của một Movie gồm diễn viên, đạo diễn, thể loại, từ khóa và hãng phim; đây là dữ liệu đầu vào của phép gợi ý tương tự.", { badge: "1", fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal, titleSize: 19, bodySize: 13 });
  card(s, 4.79, 1.95, 3.75, 4.45, "Đường đi (path)", "Là một dãy node và cạnh liên tiếp nối hai thực thể. Độ dài đường đi được tính bằng số cạnh.\n\nTruy vấn nhiều bước và shortest path không chỉ trả kết quả, mà còn cho biết kết quả được nối qua những quan hệ nào.", { badge: "2", badgeColor: C.purple, fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple, titleSize: 19, bodySize: 13 });
  card(s, 8.9, 1.95, 3.75, 4.45, "Đồ thị con (subgraph)", "Là phần graph chỉ gồm các node và cạnh liên quan đến một mục tiêu cụ thể.\n\nDự án dùng đồ thị con để giới hạn ngữ cảnh giải thích và tạo các snapshot có cùng phạm vi khi đánh giá.", { badge: "3", badgeColor: C.green, fill: C.greenBg, stroke: "C4E2D1", titleColor: C.green, titleSize: 19, bodySize: 13 });
  s.addShape(pptx.ShapeType.line, { x: 3.02, y: 5.15, w: 2.15, h: 0, line: { color: C.muted, width: 1.5, endArrowType: "triangle" } });
  s.addShape(pptx.ShapeType.line, { x: 7.14, y: 5.15, w: 2.15, h: 0, line: { color: C.muted, width: 1.5, endArrowType: "triangle" } });
  s.addText("mở rộng nhiều bước", { x: 3.28, y: 4.78, w: 1.62, h: 0.22, fontFace: "Arial", fontSize: 8.5, bold: true, color: C.muted, align: "center", margin: 0 });
  s.addText("giữ phần liên quan", { x: 7.4, y: 4.78, w: 1.62, h: 0.22, fontFace: "Arial", fontSize: 8.5, bold: true, color: C.muted, align: "center", margin: 0 });
  notes(s, "Ba khái niệm cấu trúc này đứng sau các năng lực chính của graph. Neighborhood hỗ trợ similarity và common neighbor; path hỗ trợ multi-hop và shortest path; subgraph gom đúng phần ngữ cảnh cần để giải thích hoặc đánh giá. Đây là khác biệt quan trọng so với cách chỉ nhìn từng bản ghi riêng lẻ.");
}

// 7 — Knowledge Graph design principles
{
  const s = lightSlide("Bốn điều kiện để một graph trở thành Knowledge Graph hữu dụng", "Node và cạnh chỉ tạo ra cấu trúc; bốn nguyên tắc dưới đây mới làm cấu trúc đó có nghĩa và có mục đích.", "Nguyên tắc thiết kế");
  card(s, 0.68, 1.92, 5.85, 2.15, "1 · Định danh — biết đang nói về thực thể nào", "Mỗi thực thể cần một ID ổn định, độc lập với cách viết tên. Dự án ưu tiên ID nguồn của TMDB/IMDb; tên chỉ phục vụ hiển thị và tìm kiếm. Nhờ vậy, hai người trùng tên không bị gộp và một phim có nhiều cách viết không bị tách sai.", { fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal, titleSize: 18, bodySize: 12.2 });
  card(s, 6.8, 1.92, 5.85, 2.15, "2 · Schema — biết sự kiện có hình dạng nào", "Schema quy định lớp thực thể, loại quan hệ, thuộc tính bắt buộc và miền giá trị. Nó tạo ngôn ngữ chung để dữ liệu từ nhiều nguồn đi vào cùng một mô hình và để truy vấn dựa trên cấu trúc nhất quán.", { fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple, titleSize: 18, bodySize: 12.2 });
  card(s, 0.68, 4.38, 5.85, 2.15, "3 · Nguồn gốc — biết sự kiện đến từ đâu", "Sự kiện nhập trực tiếp phải chỉ ra nguồn; sự kiện suy ra phải giữ luật và các sự kiện hỗ trợ. Nhờ đó, người dùng có thể kiểm tra và tái tạo kết quả thay vì phải tin vào một hộp đen.", { fill: C.greenBg, stroke: "C4E2D1", titleColor: C.green, titleSize: 18, bodySize: 12.2 });
  card(s, 6.8, 4.38, 5.85, 2.15, "4 · Câu hỏi năng lực — biết graph được xây để làm gì", "Câu hỏi năng lực xác định tri thức tối thiểu cần biểu diễn. Nếu schema không trả lời được các câu hỏi đã công bố, việc có nhiều node và cạnh vẫn chưa tạo ra giá trị cho bài toán.", { fill: C.amberBg, stroke: "F1D5AA", titleColor: C.amber, titleSize: 18, bodySize: 12.2 });
  notes(s, "Bốn nguyên tắc này là tiêu chí xuyên suốt của project. Identity tránh nhập nhằng; schema tạo ngữ nghĩa chung; provenance cho phép kiểm chứng; competency questions bảo đảm mô hình phục vụ mục tiêu. Đây cũng là lý do Knowledge Graph không nên được định nghĩa đơn giản là một mạng node và edge.");
}

// 8 — Constraints and indexes
{
  const s = lightSlide("Constraint bảo vệ tính đúng đắn; index phục vụ tốc độ tra cứu", "Hai cơ chế thường được tạo cùng lúc nhưng giải quyết hai vấn đề khác nhau và không thể thay thế cho nhau.", "Ràng buộc dữ liệu");
  card(s, 0.68, 1.95, 3.75, 4.5, "Ràng buộc duy nhất", "Bảo đảm một khóa ổn định không xuất hiện hai lần trong cùng một nhãn.\n\nVí dụ:\nMovie.tmdb_id\nPerson.person_id\nGenre.genre_id\n\nNhờ đó, dữ liệu trùng bị chặn ngay tại tầng lưu trữ và lệnh MERGE luôn xác định đúng node cần dùng.", { badge: "U", fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple, titleSize: 19, bodySize: 12.5 });
  card(s, 4.79, 1.95, 3.75, 4.5, "Kiểm tra tính hợp lệ", "ID và tên bắt buộc được kiểm tra trước hoặc sau khi nhập. Dự án còn phát hiện Movie không có quan hệ, cạnh nối sai loại node và sự kiện suy ra không có bằng chứng.\n\nRàng buộc trong Neo4j và cổng chất lượng của pipeline bổ sung cho nhau.", { badge: "V", badgeColor: C.green, fill: C.greenBg, stroke: "C4E2D1", titleColor: C.green, titleSize: 19, bodySize: 12.2 });
  card(s, 8.9, 1.95, 3.75, 4.5, "Index và chỉ mục toàn văn", "Index tăng tốc tra cứu chính xác theo thuộc tính; chỉ mục toàn văn tạo danh sách ứng viên khi tên người dùng nhập không hoàn toàn trùng khớp.\n\nIndex không chứng minh dữ liệu đúng. Nó chỉ giúp tìm node bắt đầu nhanh hơn trước khi duyệt tiếp các quan hệ.", { badge: "I", badgeColor: C.teal, fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal, titleSize: 19, bodySize: 12.7 });
  notes(s, "Schema khái niệm cần được nối với cơ chế bảo đảm vận hành. Uniqueness constraint bảo vệ identity; pipeline validation kiểm tra các quy tắc phức tạp hơn; index và full-text index hỗ trợ tìm điểm bắt đầu. Index chỉ tối ưu lookup, còn traversal vẫn dựa trên cấu trúc relationship.");
}

// 6 — Reasoning and Cypher
{
  const s = lightSlide("Cypher vừa truy vấn mẫu đường đi, vừa vật chất hóa luật nghiệp vụ", "Một ngôn ngữ thống nhất cho constraint, traversal, aggregation và derived relationship.", "Truy vấn và suy diễn");
  card(s, 0.72, 1.95, 5.8, 4.55, "Truy vấn bằng pattern", "MATCH (p:Person)-[:DIRECTED]->(m:Movie)\nWHERE p.name = $name\nRETURN m.title\n\nPattern thể hiện trực tiếp node và cạnh cần tìm; giá trị người dùng được truyền bằng parameter.", { fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal, titleSize: 21, bodySize: 15 });
  card(s, 6.82, 1.95, 5.8, 4.55, "Suy diễn bằng rule", "MATCH (a)-[:ACTED_IN]->(m)<-[:ACTED_IN]-(b)\nMERGE (a)-[:CO_STARRED_WITH]->(b)\n\nFact suy ra lưu movie_count, evidence_movie_ids và derived=true để kiểm chứng.", { fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple, titleSize: 21, bodySize: 15 });
  s.addText("Không có reasoner riêng: luật nghiệp vụ được khai báo và thực thi trực tiếp trong Neo4j.", { x: 1.3, y: 6.7, w: 10.7, h: 0.28, fontFace: "Calibri", fontSize: 13.5, bold: true, color: C.navy, align: "center", margin: 0 });
  notes(s, "Cypher phục vụ cả truy vấn và materialization. Query catalog dùng pattern có parameter. Luật CO_STARRED_WITH được chạy sau import và lưu evidence. Đây là cơ chế suy diễn duy nhất của hệ thống.");
}

// 10 — Traversal vocabulary
{
  const s = lightSlide("Bốn khái niệm giúp mô tả cách duyệt đồ thị", "Mỗi khái niệm trả lời một câu hỏi khác nhau về khoảng cách, mức kết nối hoặc cấu trúc chung giữa các thực thể.", "Duyệt đồ thị");
  const concepts = [
    ["Bước đi (hop)", "Một hop là một lần đi qua cạnh. Person → Movie dài 1 hop; Person → Movie → Genre dài 2 hop. Số hop cho biết truy vấn phải đi qua bao nhiêu lớp quan hệ.", C.teal, "EAF2F8"],
    ["Bậc của node (degree)", "Degree là số cạnh kề một node. Degree cao có thể cho biết thực thể phổ biến, nhưng cũng có thể làm các đặc trưng phổ biến lấn át kết quả xếp hạng.", C.purple, C.purpleBg],
    ["Láng giềng chung", "Common neighbor là node được hai node cùng kết nối. Hai Person có thể chung một Movie; hai Movie có thể chung diễn viên, thể loại hoặc từ khóa.", C.green, C.greenBg],
    ["Đường đi ngắn nhất", "Shortest path là đường có ít cạnh nhất trong phạm vi quan hệ cho phép. Muốn hiểu kết quả, phải đọc cả loại cạnh trên đường đi chứ không chỉ danh sách node.", C.amber, C.amberBg],
  ];
  concepts.forEach((d, i) => {
    const x = 0.68 + (i % 2) * 6.12;
    const y = 1.95 + Math.floor(i / 2) * 2.35;
    card(s, x, y, 5.85, 2.02, d[0], d[1], { badge: String(i + 1), badgeColor: d[2], fill: d[3], stroke: d[2], titleColor: d[2], titleSize: 19, bodySize: 13 });
  });
  s.addText("Trong dự án: phim chung dựa trên láng giềng chung; quan hệ đồng diễn vật chất hóa cấu trúc đó; gợi ý so sánh lân cận có trọng số; truy vấn đường đi được giới hạn tối đa 8 cạnh.", { x: 1.05, y: 6.48, w: 11.2, h: 0.38, fontFace: "Calibri", fontSize: 13.5, bold: true, color: C.navy, align: "center", margin: 0, fit: "shrink" });
  notes(s, "Hop đo số bước, degree mô tả mức kết nối, common neighbor là nền tảng của phim chung và similarity, shortest path tìm liên hệ ngắn nhất. Cần lưu ý đường ngắn nhất về số cạnh chưa chắc là quan hệ có ý nghĩa nhất, vì vậy evidence phải giữ cả loại relationship.");
}

// 6 — Why graph
{
  const s = lightSlide("Neo4j được chọn vì phù hợp với quan hệ và traversal", "Giá trị của đồ thị nằm ở mô hình quan hệ và đường đi bằng chứng — không phải luôn nhanh hơn SQL.", "Lựa chọn công nghệ");
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
  s.addText("Quan hệ có thể mang thuộc tính", { x: 8.65, y: 4.45, w: 3.7, h: 0.35, fontFace: "Calibri", fontSize: 20, bold: true, color: C.purple, margin: 0 });
  s.addText("Cạnh ACTED_IN và CO_STARRED_WITH mang thuộc tính và bằng chứng trực tiếp.", { x: 8.65, y: 4.96, w: 3.45, h: 0.52, fontFace: "Calibri", fontSize: 13, color: C.ink, margin: 0, fit: "shrink" });
  notes(s, "Neo4j là kho graph duy nhất vì thuận tiện cho traversal, relationship có property và ứng dụng. SQLite chỉ là mốc so sánh được kiểm soát. Em không kết luận đồ thị luôn nhanh hơn quan hệ; giá trị chính là mô hình và bằng chứng.");
}

// 7 — Architecture
{
  const s = lightSlide("Kiến trúc đầu cuối: từ nguồn đến bằng chứng", "Sau khi import, đường chạy trình diễn không phụ thuộc Internet.", "Thiết kế hệ thống");
  const layers = [
    ["TMDB + IMDb", "Cung cấp dữ liệu nguồn", C.teal, "EAF2F8"],
    ["Raw cache", "Giữ nguyên JSON và GZIP", C.amber, C.amberBg],
    ["Xử lý", "Làm sạch, nối ID, chuẩn hóa", C.green, C.greenBg],
    ["Neo4j", "Bảo vệ, nhập và suy diễn", C.purple, C.purpleBg],
    ["FastAPI", "Điều phối hỏi–đáp và gợi ý", C.red, C.redBg],
    ["Giao diện", "Trình bày kết quả và bằng chứng", C.navy2, C.pale],
  ];
  layers.forEach((d, i) => {
    const x = 0.55 + i * 2.12;
    s.addShape(pptx.ShapeType.roundRect, { x, y: 2.35, w: 1.72, h: 2.25, rectRadius: 0.05, fill: { color: d[3] }, line: { color: d[2], width: 1.5 }, shadow: shadow() });
    s.addText(d[0], { x: x + 0.18, y: 2.72, w: 1.36, h: 0.42, fontFace: "Calibri", fontSize: 17, bold: true, color: d[2], align: "center", margin: 0, fit: "shrink" });
    s.addText(d[1], { x: x + 0.18, y: 3.5, w: 1.36, h: 0.58, fontFace: "Calibri", fontSize: 12, color: C.ink, align: "center", margin: 0, fit: "shrink" });
    if (i < layers.length - 1) s.addShape(pptx.ShapeType.line, { x: x + 1.74, y: 3.48, w: 0.34, h: 0, line: { color: C.muted, width: 1.7, endArrowType: "triangle" } });
  });
  card(s, 2.1, 5.25, 3.65, 0.92, "Khả năng tái lập", "Checksum và manifest xác định rõ khi nào phải nhập lại dữ liệu.", { shadow: false, titleSize: 13, bodySize: 9.5, fill: C.amberBg });
  card(s, 7.55, 5.25, 3.65, 0.92, "Khả năng giải thích", "Kết quả giữ thực thể đã liên kết, đường đi và đặc trưng tạo điểm.", { shadow: false, titleSize: 13, bodySize: 9.5, fill: C.greenBg });
  notes(s, "Luồng chính đi từ TMDB và IMDb qua cache bất biến, xử lý và chuẩn hóa sang Neo4j. FastAPI cung cấp QA và recommendation. Manifest, checksum và các phép kiểm tra bao quanh toàn bộ quy trình.");
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
  card(s, 9.1, 1.92, 3.55, 1.2, "Tên không quyết định danh tính", "`Person.person_id = tmdb:<id>` là khóa ổn định; `name` chỉ dùng để hiển thị và tìm kiếm.", { fill: "EAF2F8", stroke: "BDD4E5", titleSize: 14.5, bodySize: 10.3 });
  card(s, 9.1, 3.38, 3.55, 1.2, "Vai trò được đặt trên quan hệ", "`ACTED_IN` cho biết một Person tham gia Movie nào và lưu nhân vật, thứ tự diễn viên, nguồn dữ liệu.", { fill: C.greenBg, stroke: "C4E2D1", titleSize: 14.5, bodySize: 10 });
  card(s, 9.1, 4.84, 3.55, 1.2, "Schema được bảo vệ trước khi nhập", "Constraint ngăn trùng khóa; index giúp tìm node theo khóa hoặc tên.", { fill: C.purpleBg, stroke: "D9CFE8", titleSize: 14.5, bodySize: 10.3 });
  addSource(s, "Nguồn chỉnh sửa: report_latex/images/sources/property_graph_schema.drawio");
  notes(s, "Mô hình có năm loại nút và năm quan hệ gốc. Person chỉ dùng một label vì cùng một người có thể có nhiều vai trò. Stable source ID là khóa; ACTED_IN giữ metadata trên cạnh. Constraint và index được tạo trước khi nạp.");
}

// 10 — ETL
{
  const s = lightSlide("Quy trình dữ liệu có thể chạy lại và kiểm tra", "Raw cache bất biến → dữ liệu chuẩn hóa tất định → import idempotent → validation.", "Quy trình xử lý");
  const steps = ["Thu thập", "Lưu nguồn", "Làm sạch", "Nối IMDb", "Chuẩn hóa", "Nhập Neo4j", "Suy diễn", "Kiểm tra"];
  steps.forEach((label, i) => {
    const x = 0.5 + i * 1.57;
    const color = i < 2 ? C.teal : (i < 5 ? C.amber : (i < 7 ? C.purple : C.green));
    s.addShape(pptx.ShapeType.roundRect, { x, y: 2.4, w: 1.25, h: 1.0, rectRadius: 0.04, fill: { color: i % 2 ? C.white : C.pale }, line: { color, width: 1.4 }, shadow: shadow() });
    s.addText(label, { x: x + 0.1, y: 2.74, w: 1.05, h: 0.28, fontFace: "Calibri", fontSize: 13, bold: true, color, align: "center", margin: 0, fit: "shrink" });
    if (i < steps.length - 1) s.addShape(pptx.ShapeType.line, { x: x + 1.27, y: 2.9, w: 0.26, h: 0, line: { color: C.muted, width: 1.4, endArrowType: "triangle" } });
  });
  const captions = [
    ["Bộ nhớ đệm nguồn", "Giữ nguyên dữ liệu gốc để có thể xử lý lại cùng một snapshot."],
    ["Manifest thực nghiệm", "Ghi số lượng, checksum và kết quả kiểm tra của mỗi lần chạy."],
    ["Nhập idempotent", "`MERGE` theo stable ID giúp chạy lại mà không nhân bản node và cạnh."],
    ["Cổng chất lượng", "Chặn dữ liệu mồ côi, thiếu khóa hoặc có cạnh không hợp lệ."],
  ];
  captions.forEach((d, i) => card(s, 0.68 + i * 3.03, 5.42, 2.72, 1.28, d[0], d[1], { shadow: false, titleSize: 11.5, bodySize: 8.7, fill: i % 2 ? "F0F6F8" : C.white }));
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

// Entity resolution versus entity linking
{
  const s = lightSlide("Entity resolution và entity linking giải quyết hai thời điểm khác nhau", "Cả hai đều xử lý identity, nhưng một bước hợp nhất dữ liệu khi xây graph; bước còn lại nối đầu vào người dùng vào graph đã có.", "Định danh thực thể");
  card(s, 0.68, 1.95, 5.85, 4.65, "Entity resolution · lúc tích hợp dữ liệu", "Mục tiêu: quyết định hai record từ cùng hoặc khác nguồn có mô tả cùng một thực thể hay không.\n\nTín hiệu ưu tiên trong project:\n1. Exact source ID TMDB/IMDb.\n2. Thuộc tính hỗ trợ khi ID thiếu.\n3. Fuzzy matching chỉ là fallback có confidence và log.\n\nSai false positive làm ô nhiễm graph lâu dài, nên hệ thống ưu tiên precision và có thể abstain.", { fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple, titleSize: 20, bodySize: 13.5 });
  card(s, 6.8, 1.95, 5.85, 4.65, "Entity linking · lúc xử lý câu hỏi", "Mục tiêu: nối chuỗi người dùng nhập, ví dụ “Cristopher Nolan”, tới node canonical đã tồn tại.\n\nQuy trình trong project:\n1. Xác định loại slot: Movie/Person/Genre.\n2. Full-text search tạo candidate.\n3. Fuzzy reranking và threshold.\n4. Trả stable ID + canonical name + confidence.\n\nQuery sau đó dùng ID, không mở rộng lại theo tên.", { fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal, titleSize: 20, bodySize: 13.5 });
  notes(s, "Entity resolution diễn ra trong pipeline tích hợp và ảnh hưởng cấu trúc graph lâu dài. Entity linking diễn ra ở request time để nối câu hỏi vào node canonical. Hai bước dùng kỹ thuật giống nhau nhưng khác đầu vào, thời điểm và hậu quả. Project ưu tiên stable ID ở cả hai ranh giới.");
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
  card(s, 8.05, 5.48, 4.55, 1.0, "An toàn", "Không nối chuỗi đầu vào vào Cypher.", { badge: "✓", badgeColor: C.green, shadow: false, titleSize: 13, bodySize: 10, fill: C.greenBg });
  notes(s, "Hệ thống có danh mục truy vấn tham số hóa gồm lookup, aggregation, multi-hop, shortest path và similarity. Ví dụ này đi từ director qua movie sang genre. Giá trị genre và limit là tham số; người dùng không thể thay đổi cấu trúc Cypher.");
}

// 14 — reasoning
{
  const s = lightSlide("CO_STARRED_WITH là fact suy ra có thể kiểm chứng", "Đây là phép vật chất hóa luật nghiệp vụ bằng Cypher.", "Suy diễn");
  addImageContain(s, A("costar_reasoning"), 0.65, 1.92, 8.0, 4.7);
  card(s, 8.98, 1.95, 3.7, 1.18, "Sự kiện được khẳng định", "Cạnh ACTED_IN được nhập trực tiếp từ danh sách vai diễn của TMDB.", { fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal, bodySize: 10.8 });
  card(s, 8.98, 3.43, 3.7, 1.18, "Sự kiện được suy ra", "Nếu hai Person cùng ACTED_IN một Movie, hệ thống tạo quan hệ CO_STARRED_WITH.", { fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple, bodySize: 10.5 });
  card(s, 8.98, 4.91, 3.7, 1.4, "Vì sao kết quả kiểm chứng được?", "Cạnh suy ra lưu số phim chung, ID các phim làm bằng chứng và cờ `derived=true`.", { fill: C.greenBg, stroke: "C4E2D1", titleColor: C.green, bodySize: 10.5 });
  addSource(s, "Nguồn chỉnh sửa: report_latex/images/sources/costar_reasoning.drawio");
  notes(s, "Từ hai cạnh ACTED_IN cùng đi vào một Movie, hệ thống vật chất hóa CO_STARRED_WITH. Cạnh suy ra lưu số phim chung và danh sách Movie hỗ trợ, nên có thể lần ngược. Đây là cơ chế suy diễn duy nhất của hệ thống.");
}

// Provenance and evidence
{
  const s = lightSlide("Nguồn gốc, lịch sử biến đổi và bằng chứng trả lời ba câu hỏi khác nhau", "Phân biệt rõ ba lớp truy vết giúp giải thích được cả dữ liệu gốc, dữ liệu suy ra và kết quả ứng dụng.", "Khả năng giải thích");
  const rows = [
    ["Khái niệm", "Câu hỏi trả lời", "Biểu hiện trong project"],
    ["Nguồn gốc (provenance)", "Sự kiện đến từ nguồn nào?", "`source=tmdb`; checksum IMDb; ID của nguồn"],
    ["Lịch sử biến đổi (lineage)", "Sự kiện đã đi qua các bước nào?", "dữ liệu gốc → làm sạch → CSV → nhập → luật"],
    ["Bằng chứng (evidence)", "Kết quả này dựa trên node và cạnh nào?", "thực thể đã nối; bản ghi/đường đi; đặc trưng chung"],
  ];
  s.addTable(rows, { x: 0.68, y: 1.95, w: 12.0, h: 2.85, border: { type: "solid", color: C.line, pt: 1 }, fill: C.white, color: C.ink, fontFace: "Calibri", fontSize: 13, margin: 0.1, rowH: 0.66, valign: "mid", colW: [2.15, 4.05, 5.8], autoFit: false });
  card(s, 0.68, 5.08, 3.75, 1.48, "Sự kiện được khẳng định", "Được lấy trực tiếp từ nguồn, ví dụ Person ACTED_IN Movie; cần giữ nguồn và ID gốc.", { badge: "A", badgeColor: C.teal, fill: "EAF2F8", stroke: "BDD4E5", titleSize: 16, bodySize: 11.2 });
  card(s, 4.79, 5.08, 3.75, 1.48, "Sự kiện được suy ra", "Được sinh bởi luật, ví dụ CO_STARRED_WITH; cần giữ luật và các phim làm căn cứ.", { badge: "D", badgeColor: C.purple, fill: C.purpleBg, stroke: "D9CFE8", titleSize: 16, bodySize: 11.2 });
  card(s, 8.9, 5.08, 3.75, 1.48, "Kết quả giải thích được", "Kèm đường đi hoặc đặc trưng đóng góp đủ để người dùng kiểm tra ngược cách tạo kết quả.", { badge: "E", badgeColor: C.green, fill: C.greenBg, stroke: "C4E2D1", titleSize: 16, bodySize: 11.2 });
  notes(s, "Provenance chỉ nguồn gốc, lineage chỉ chuỗi biến đổi, evidence chỉ các fact hỗ trợ một kết quả cụ thể. Project dùng cả ba: source và checksum cho provenance, pipeline manifest cho lineage, graph row/path và shared feature cho evidence.");
}

// 15 — QA
{
  const s = lightSlide("Giá trị của chatbot nằm ở việc điều phối Cypher an toàn", "Ngôn ngữ tự nhiên chọn ý định và thực thể; Neo4j thực hiện traversal và trả bằng chứng.", "Ứng dụng hỏi–đáp");
  addImageContain(s, A("qa_sequence"), 0.62, 1.92, 8.25, 4.7);
  card(s, 9.18, 1.94, 3.48, 1.15, "Giới hạn ở chín loại câu hỏi", "Mỗi intent ánh xạ tới một mẫu Cypher cố định; câu ngoài phạm vi được trả về là chưa hỗ trợ.", { fill: "EAF2F8", stroke: "BDD4E5", titleSize: 14.2, bodySize: 9.7 });
  card(s, 9.18, 3.37, 3.48, 1.15, "Tên gọi được nối tới node chuẩn", "Ví dụ “Cristopher Nolan” được liên kết tới Christopher Nolan cùng stable ID và độ tin cậy.", { fill: C.amberBg, stroke: "F1D5AA", titleSize: 14.2, bodySize: 9.7 });
  card(s, 9.18, 4.8, 3.48, 1.15, "Câu trả lời đi kèm căn cứ", "Phản hồi giữ intent, thực thể đã liên kết và bản ghi hoặc đường đi dùng để tạo câu trả lời.", { fill: C.greenBg, stroke: "C4E2D1", titleSize: 14.2, bodySize: 9.7 });
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
  card(s, 8.72, 5.62, 3.9, 1.02, "Mỗi điểm số đều có lời giải thích", "Neo4j trả cả tổng điểm và các đặc trưng chung đã đóng góp vào điểm đó.", { shadow: false, titleSize: 12, bodySize: 9.2, fill: C.greenBg, stroke: "C4E2D1" });
  addSource(s, "Nguồn chỉnh sửa: report_latex/images/sources/recommendation_explanation.drawio");
  notes(s, "Ranker dùng IDF-weighted graph similarity. Đặc trưng chung hiếm đóng góp nhiều hơn đặc trưng phổ biến. Trọng số ưu tiên director và actor. Điểm và explanation đều được tính từ traversal trong Neo4j, không tải toàn graph về Python.");
}

// Evaluation metrics
{
  const s = lightSlide("Các metric đo những loại sai khác nhau", "Không có một con số duy nhất đánh giá toàn bộ Knowledge Graph; metric phải khớp với claim.", "Khái niệm đánh giá");
  card(s, 0.68, 1.92, 3.75, 2.18, "Precision · độ chính xác dương", "Trong các liên kết/fact hệ thống chấp nhận, bao nhiêu là đúng?\n\nPrecision = TP / (TP + FP)\n\nQuan trọng khi một phép nối sai có thể làm ô nhiễm nhiều đường đi.", { fill: "EAF2F8", stroke: "BDD4E5", titleColor: C.teal, titleSize: 17, bodySize: 12 });
  card(s, 4.79, 1.92, 3.75, 2.18, "Recall · độ bao phủ dương", "Trong các liên kết/fact đúng cần tìm, hệ thống tìm được bao nhiêu?\n\nRecall = TP / (TP + FN)\n\nAbstention bảo thủ thường tăng precision nhưng làm giảm recall.", { fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple, titleSize: 17, bodySize: 12 });
  card(s, 8.9, 1.92, 3.75, 2.18, "F1 · cân bằng P và R", "Trung bình điều hòa của precision và recall.\n\nF1 = 2PR / (P + R)\n\nF1 hữu ích khi cần một số tổng hợp nhưng vẫn phải đọc kèm confusion counts.", { fill: C.greenBg, stroke: "C4E2D1", titleColor: C.green, titleSize: 17, bodySize: 12 });
  card(s, 0.68, 4.42, 5.85, 2.12, "Precision@K · mức liên quan trong Top-K", "Tỷ lệ mục liên quan trong K gợi ý đầu tiên. Metric coi các vị trí trong Top-K như nhau, nên chưa phản ánh việc mục tốt nằm ở đầu hay cuối danh sách.", { badge: "K", badgeColor: C.amber, fill: C.amberBg, stroke: "F1D5AA", titleColor: C.amber, titleSize: 17, bodySize: 12 });
  card(s, 6.8, 4.42, 5.85, 2.12, "NDCG@K · chất lượng thứ tự xếp hạng", "Discounted Cumulative Gain giảm trọng số ở vị trí thấp; chuẩn hóa bởi thứ tự lý tưởng. NDCG phù hợp khi relevance có mức độ và vị trí đầu danh sách quan trọng hơn.", { badge: "N", badgeColor: C.red, fill: C.redBg, stroke: "E9C3C6", titleColor: C.red, titleSize: 17, bodySize: 12 });
  notes(s, "Precision, recall và F1 dùng cho entity resolution; precision dùng cho fact suy ra; Precision@K và NDCG@K dùng cho recommendation. NDCG quan tâm thứ tự, còn Precision@K chỉ quan tâm có bao nhiêu mục liên quan trong Top-K. Mọi metric chỉ có ý nghĩa cùng protocol và corpus.");
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
  card(s, 8.4, 3.82, 4.25, 2.48, "Ý nghĩa đúng của các con số", "QA 20/20 chứng minh luồng đã định hoạt động trên tập smoke test. Entity precision cao nhờ hệ thống chấp nhận bỏ sót khi mơ hồ. Chỉ số gợi ý đo trên corpus silver, vì vậy chưa thể thay cho đánh giá độc lập của người dùng.", { fill: C.white, stroke: C.line, titleSize: 17, bodySize: 12.2 });
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
  card(s, 0.75, 5.5, 5.95, 1.05, "Kết luận hiệu năng", "Đo warm-cache, 100 lần/query, không đo concurrency hoặc cold cache.", { shadow: false, titleSize: 13, bodySize: 10, fill: C.amberBg, stroke: "F1D5AA" });
  card(s, 7.15, 5.5, 5.48, 1.05, "Kết luận gợi ý", "Các mốc cũ là lịch sử thiết kế, không phải lựa chọn runtime.", { shadow: false, titleSize: 13, bodySize: 10, fill: C.purpleBg, stroke: "D9CFE8" });
  addSource(s, "Nguồn: multiscale_benchmark.csv · recommendation_ablation.json · recommendation.json");
  notes(s, "SQLite nhanh hơn trên tất cả query và quy mô đã đo. Điều đó cho thấy không nên bán đồ thị bằng tốc độ tuyệt đối; lợi ích là biểu diễn và bằng chứng traversal. Với recommendation, các phương pháp cũ chỉ là lịch sử thiết kế; runtime hiện dùng IDF-weighted graph.");
}

// 21 — Competency questions
{
  const s = lightSlide("Competency question dẫn dắt schema và truy vấn", "Mỗi câu hỏi nghiệp vụ phải ánh xạ được thành một graph pattern có thể kiểm chứng.", "Từ lý thuyết đến mô hình");
  card(s, 0.68, 1.95, 4.0, 3.65, "Câu hỏi năng lực", "Phim nào có hai diễn viên cùng tham gia?\n\nKhái niệm cần có:\nPerson · Movie · ACTED_IN\n\nRàng buộc:\nhai Person khác nhau cùng nối tới một Movie.", { fill: C.purpleBg, stroke: "D9CFE8", titleColor: C.purple, titleSize: 18, bodySize: 15 });
  s.addShape(pptx.ShapeType.roundRect, { x: 4.98, y: 1.95, w: 7.67, h: 3.65, rectRadius: 0.04, fill: { color: C.navy }, line: { color: C.navy }, shadow: shadow() });
  s.addText("GRAPH PATTERN TƯƠNG ỨNG", { x: 5.25, y: 2.2, w: 4.6, h: 0.28, fontFace: "Arial", fontSize: 10, bold: true, color: "8FD0CC", charSpacing: 1.1, margin: 0 });
  s.addText([
    "MATCH (a:Person)-[:ACTED_IN]->(m:Movie)\n",
    "      <-[:ACTED_IN]-(b:Person)\n",
    "WHERE a.person_id = $person1_id\n",
    "  AND b.person_id = $person2_id\n",
    "  AND a <> b\n",
    "RETURN DISTINCT m.title AS common_movie;"
  ].join(""), { x: 5.25, y: 2.68, w: 6.95, h: 2.52, fontFace: "Courier New", fontSize: 13, color: "D9E8F2", margin: 0, fit: "shrink" });
  card(s, 0.68, 5.62, 3.68, 1.04, "Schema coverage", "Có đủ lớp và quan hệ để biểu diễn?", { shadow: false, titleSize: 12, bodySize: 10.5, fill: "EAF2F8" });
  card(s, 4.82, 5.62, 3.68, 1.04, "Query answerability", "Pattern có trả lời được câu hỏi?", { shadow: false, titleSize: 12, bodySize: 10.5, fill: C.amberBg });
  card(s, 8.96, 5.62, 3.68, 1.04, "Evidence", "Kết quả có lần ngược được đường đi?", { shadow: false, titleSize: 12, bodySize: 10.5, fill: C.greenBg });
  notes(s, "Competency question không chỉ dùng để demo. Nó là công cụ thiết kế schema: xác định loại thực thể, quan hệ và thuộc tính tối thiểu; sau đó kiểm tra bằng một graph pattern. Ví dụ phim chung ánh xạ trực tiếp thành shared-neighbor Person–Movie–Person.");
}

// 22 — Consolidated demonstration
{
  const s = lightSlide("Demo tổng hợp · từ câu hỏi đến đường đi bằng chứng", "Ứng dụng chỉ là bề mặt minh họa; trọng tâm là phép ánh xạ từ ngôn ngữ sang graph pattern.", "Minh họa nguyên lý");
  card(s, 0.62, 1.85, 3.45, 4.72, "① Câu hỏi tự nhiên", "“Christian Bale và Tom Hardy cùng đóng phim nào?”\n\nTừ câu hỏi, hệ thống phải xác định:\n• hai thực thể thuộc lớp Person;\n• quan hệ cần duyệt là ACTED_IN;\n• Movie chung là node cần trả về;\n• đường Person → Movie ← Person là bằng chứng.", { fill: C.greenBg, stroke: "C4E2D1", titleColor: C.green, titleSize: 17, bodySize: 13.2 });
  s.addShape(pptx.ShapeType.roundRect, { x: 4.32, y: 1.85, w: 8.38, h: 4.72, rectRadius: 0.04, fill: { color: C.navy }, line: { color: C.navy }, shadow: shadow() });
  s.addText("② ÁNH XẠ AN TOÀN VÀ KIỂM CHỨNG", { x: 4.58, y: 2.08, w: 5.8, h: 0.25, fontFace: "Arial", fontSize: 9.5, bold: true, color: "8FD0CC", charSpacing: 0.9, margin: 0 });
  const demoQuery = [
    "Intent: common_movies\n",
    "Entity links: tmdb:3894 · tmdb:2524\n\n",
    "MATCH (a:Person)-[:ACTED_IN]->(m:Movie)\n",
    "      <-[:ACTED_IN]-(b:Person)\n",
    "WHERE a.person_id = $person1_id\n",
    "  AND b.person_id = $person2_id\n",
    "RETURN m.title, m.tmdb_id;\n\n",
    "Evidence path:\n",
    "Christian Bale → The Dark Knight Rises ← Tom Hardy"
  ].join("");
  s.addText(demoQuery, { x: 4.58, y: 2.5, w: 7.72, h: 3.45, fontFace: "Courier New", fontSize: 12.2, color: "D9E8F2", margin: 0, fit: "shrink" });
  s.addText("Chi tiết parser, API response và giao diện: xem Chương 4–5 của báo cáo.", { x: 4.58, y: 6.08, w: 7.72, h: 0.28, fontFace: "Calibri", fontSize: 10.5, bold: true, color: "8FD0CC", margin: 0, fit: "shrink" });
  notes(s, "Demo chỉ minh họa ba bước lý thuyết: xác định intent và thực thể, chọn graph pattern có tham số, rồi đối chiếu đường đi bằng chứng. Em không đi sâu giao diện hay cấu trúc API trên slide; các chi tiết đó nằm trong chương triển khai của báo cáo.");
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

// 24–25 — Conclusion and Q&A
{
  const s = darkSlide();
  s.addText("KẾT LUẬN", { x: 0.75, y: 0.68, w: 2.5, h: 0.28, fontFace: "Arial", fontSize: 10, bold: true, color: "8FD0CC", charSpacing: 1.7, margin: 0 });
  s.addText("Đồ thị tri thức tạo giá trị khi\nmỗi quan hệ đều có thể được kiểm chứng", { x: 0.75, y: 1.18, w: 9.2, h: 1.25, fontFace: "Calibri", fontSize: 31, bold: true, color: C.white, margin: 0, fit: "shrink" });
  const conclusions = [
    ["01", "Tích hợp nhất quán", "TMDB và IMDb được nối bằng ID ổn định, giữ nguồn gốc và có thể tái lập."],
    ["02", "Khai thác quan hệ", "Cypher duyệt nhiều bước và tạo sự kiện suy ra kèm căn cứ."],
    ["03", "Kiểm chứng kết quả", "Hỏi–đáp và gợi ý trả cả thực thể, đường đi và đặc trưng đóng góp."],
  ];
  conclusions.forEach((d, i) => {
    const x = 0.78 + i * 4.06;
    s.addText(d[0], { x, y: 3.55, w: 0.45, h: 0.28, fontFace: "Arial", fontSize: 12, bold: true, color: "8FD0CC", margin: 0 });
    s.addText(d[1], { x, y: 4.03, w: 3.35, h: 0.35, fontFace: "Calibri", fontSize: 20, bold: true, color: C.white, margin: 0 });
    s.addText(d[2], { x, y: 4.58, w: 3.25, h: 0.82, fontFace: "Calibri", fontSize: 13.5, color: "C9D8E4", margin: 0, fit: "shrink" });
  });
  s.addText("Xin cảm ơn thầy. Em xin lắng nghe câu hỏi và phản biện.", { x: 0.78, y: 6.5, w: 8.5, h: 0.4, fontFace: "Calibri", fontSize: 16, bold: true, color: "8FD0CC", margin: 0 });
  notes(s, "Tóm lại, đề tài đã xây dựng được một quy trình tích hợp đa nguồn có stable identity và provenance; Neo4j hỗ trợ traversal và suy diễn bằng Cypher; hai ứng dụng trả kết quả kèm bằng chứng. Em xin cảm ơn thầy và xin lắng nghe phản biện.");
}

pptx.writeFile({ fileName: OUT });
