#!/usr/bin/env python3
"""Generate editable draw.io sources and publication-ready PDF report figures."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from xml.etree import ElementTree as ET

os.environ.setdefault("MPLCONFIGDIR", "/tmp/movie-kg-matplotlib")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report_latex" / "images"
SOURCES = OUT / "sources"

COLORS = {
    "source": (0.86, 0.91, 0.98),
    "process": (1.00, 0.93, 0.78),
    "graph": (0.84, 0.93, 0.83),
    "semantic": (0.90, 0.85, 0.94),
    "app": (0.98, 0.84, 0.84),
    "neutral": (0.93, 0.93, 0.93),
}
STROKES = {
    "source": "#4c78a8", "process": "#d69e2e", "graph": "#59a14f",
    "semantic": "#8064a2", "app": "#e15759", "neutral": "#666666",
}


def diagram(name, title, nodes, edges, note=None):
    """Render one diagram to PDF and an editable native draw.io file."""
    fig, ax = plt.subplots(figsize=(12, 6.8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 6.8); ax.axis("off")
    ax.text(6, 6.48, title, ha="center", va="center", fontsize=16, weight="bold", color="#17365d")
    boxes = {}
    for node_id, label, x, y, w, h, role in nodes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.08",
                             facecolor=COLORS[role], edgecolor=STROKES[role], linewidth=1.6)
        ax.add_patch(box); boxes[node_id] = (x, y, w, h)
        ax.text(x+w/2, y+h/2, label, ha="center", va="center", fontsize=9.2, wrap=True)
    for i, (src, dst, label) in enumerate(edges):
        sx, sy, sw, sh = boxes[src]; tx, ty, tw, th = boxes[dst]
        sc = (sx+sw/2, sy+sh/2); tc = (tx+tw/2, ty+th/2)
        dx, dy = tc[0]-sc[0], tc[1]-sc[1]
        if abs(dx) >= abs(dy):
            start = (sx+sw if dx > 0 else sx, sc[1]); end = (tx if dx > 0 else tx+tw, tc[1])
        else:
            start = (sc[0], sy+sh if dy > 0 else sy); end = (tc[0], ty if dy > 0 else ty+th)
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11,
                                    linewidth=1.15, color="#4a5568", connectionstyle="arc3,rad=0.0"))
        if label:
            ax.text((start[0]+end[0])/2, (start[1]+end[1])/2+0.12, label,
                    fontsize=7.5, ha="center", va="bottom", color="#333333",
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.7, alpha=0.85))
    if note:
        ax.text(0.15, 0.12, note, fontsize=8, color="#555555", va="bottom")
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)

    mxfile = ET.Element("mxfile", host="drawio", version="26.0.0")
    page = ET.SubElement(mxfile, "diagram", name=title, id=name)
    model = ET.SubElement(page, "mxGraphModel", grid="1", gridSize="10", page="1", pageWidth="1200", pageHeight="680")
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0"); ET.SubElement(root, "mxCell", id="1", parent="0")
    for node_id, label, x, y, w, h, role in nodes:
        fill = "#%02x%02x%02x" % tuple(round(c*255) for c in COLORS[role])
        cell = ET.SubElement(root, "mxCell", id=node_id, value=label,
            style=f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={STROKES[role]};strokeWidth=2;",
            vertex="1", parent="1")
        ET.SubElement(cell, "mxGeometry", x=str(round(x*100)), y=str(round((6.1-y-h)*100)),
                      width=str(round(w*100)), height=str(round(h*100)), **{"as":"geometry"})
    for i, (src, dst, label) in enumerate(edges, 1):
        sx, sy, sw, sh = boxes[src]; tx, ty, tw, th = boxes[dst]
        horizontal = abs((tx+tw/2)-(sx+sw/2)) >= abs((ty+th/2)-(sy+sh/2))
        if horizontal:
            ex, ey, enx, eny = ((1, .5, 0, .5) if tx > sx else (0, .5, 1, .5))
        else:
            ex, ey, enx, eny = ((.5, 0, .5, 1) if ty < sy else (.5, 1, .5, 0))
        style = ("edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
                 f"endArrow=block;exitX={ex};exitY={ey};exitDx=0;exitDy=0;entryX={enx};entryY={eny};entryDx=0;entryDy=0;")
        edge = ET.SubElement(root, "mxCell", id=f"e{i}", value=label, style=style,
                             edge="1", parent="1", source=src, target=dst)
        ET.SubElement(edge, "mxGeometry", relative="1", **{"as":"geometry"})
    ET.indent(mxfile)
    ET.ElementTree(mxfile).write(SOURCES / f"{name}.drawio", encoding="utf-8", xml_declaration=True)


def metric_plots():
    with (ROOT/"experiments/results/summary/quality_metrics.csv").open() as f:
        rows = list(csv.DictReader(f))
    labels = [r["metric"].replace("Entity resolution ", "ER ").replace("Recommendation ", "Rec. ") for r in rows]
    values = [float(r["value"]) for r in rows]
    fig, ax = plt.subplots(figsize=(11, 5.8)); y = range(len(rows))
    ax.barh(list(y), values, color="#59a14f"); ax.set_yticks(list(y), labels); ax.invert_yaxis()
    ax.set_xlim(0, 1.08); ax.set_xlabel("Giá trị (0–1)"); ax.set_title("Các chỉ số chất lượng và đánh giá", weight="bold")
    for i, v in enumerate(values): ax.text(v+.012, i, f"{v:.3f}", va="center", fontsize=9)
    ax.grid(axis="x", alpha=.25); fig.tight_layout(); fig.savefig(OUT/"quality_metrics.pdf"); plt.close(fig)

    with (ROOT/"experiments/results/summary/benchmark_comparison.csv").open() as f:
        rows = list(csv.DictReader(f))
    labels = [r["intent"].replace("_", "\n") for r in rows]; x = range(len(rows)); width=.19
    series = [("Neo4j median", "neo4j_median_ms", "#4c78a8"), ("Neo4j p95", "neo4j_p95_ms", "#9ecae9"),
              ("SQLite median", "sqlite_median_ms", "#e15759"), ("SQLite p95", "sqlite_p95_ms", "#f4a3a3")]
    fig, ax = plt.subplots(figsize=(11, 5.8))
    for j,(label,key,color) in enumerate(series): ax.bar([i+(j-1.5)*width for i in x], [float(r[key]) for r in rows], width, label=label, color=color)
    ax.set_xticks(list(x), labels); ax.set_ylabel("Độ trễ (ms, thang log)"); ax.set_yscale("log")
    ax.set_title("Neo4j và SQLite trên cùng snapshot, 100 lần chạy", weight="bold"); ax.legend(ncol=2); ax.grid(axis="y", alpha=.25)
    fig.tight_layout(); fig.savefig(OUT/"query_latency.pdf"); plt.close(fig)

    data=json.loads((ROOT/"experiments/results/recommendation_ablation.json").read_text())["results"]
    production={"method":"idf_weighted (production)","precision_at_k":.715,"ndcg_at_k":.7542484569}
    data=[production]+data; labels=[d["method"].replace("_","\n") for d in data]
    fig,ax=plt.subplots(figsize=(10,5.5)); x=range(len(data)); w=.34
    ax.bar([i-w/2 for i in x],[d["precision_at_k"] for d in data],w,label="P@10",color="#4c78a8")
    ax.bar([i+w/2 for i in x],[d["ndcg_at_k"] for d in data],w,label="NDCG@10",color="#f28e2b")
    ax.set_ylim(0,1); ax.set_xticks(list(x),labels); ax.set_title("So sánh phương pháp xếp hạng (20 ca silver)",weight="bold"); ax.legend(); ax.grid(axis="y",alpha=.25)
    fig.tight_layout(); fig.savefig(OUT/"recommendation_ablation.pdf"); plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True); SOURCES.mkdir(parents=True, exist_ok=True)
    diagrams = [
      ("movie_kg_overview","Khái quát Movie Knowledge Graph",[
       ("movie","Movie",5,2.6,2,1,"graph"),("person","Person",1,4.5,2,1,"source"),("genre","Genre",1,1,2,1,"semantic"),("keyword","Keyword",9,4.5,2,1,"process"),("studio","Studio",9,1,2,1,"app")],
       [("person","movie","ACTED_IN / DIRECTED"),("movie","genre","HAS_GENRE"),("movie","keyword","HAS_KEYWORD"),("movie","studio","PRODUCED_BY")],"Movie là nút trung tâm; mọi fact giữ ID nguồn và provenance."),
      ("ontology_diagram","Ontology miền phim (RDF/OWL)",[
       ("thing","owl:Thing",5,5,2,0.7,"neutral"),("movie","kg:Movie",2,3.3,2,0.8,"graph"),("person","kg:Person",5,3.3,2,0.8,"source"),("genre","kg:Genre",8,3.3,2,0.8,"semantic"),("actor","kg:Actor",3.7,1.5,2,0.8,"source"),("director","kg:Director",6.3,1.5,2,0.8,"source")],
       [("movie","thing","subClassOf"),("person","thing","subClassOf"),("genre","thing","subClassOf"),("actor","person","subClassOf"),("director","person","subClassOf"),("person","movie","actedIn / directed")],"Miền/range, inverse, symmetric và functional constraints được materialize/kiểm tra bằng RDFLib."),
      ("property_graph_schema","Lược đồ Property Graph trong Neo4j",[
       ("movie","Movie\ntmdb_id · title · rating",4.8,2.6,2.4,1,"graph"),("person","Person\ntmdb_id · name",.5,4.6,2.4,1,"source"),("genre","Genre\ngenre_id · name",.5,.7,2.4,1,"semantic"),("keyword","Keyword\nkeyword_id · name",9.1,4.6,2.4,1,"process"),("studio","Studio\ncompany_id · name",9.1,.7,2.4,1,"app")],
       [("person","movie","ACTED_IN {character, cast_order}"),("person","movie","DIRECTED"),("movie","genre","HAS_GENRE"),("movie","keyword","HAS_KEYWORD"),("movie","studio","PRODUCED_BY"),("person","person","CO_STARRED_WITH {count, evidence}")],None),
      ("system_architecture","Kiến trúc tổng thể hệ thống",[
       ("sources","TMDB API + IMDb ratings",.3,4.5,2,1,"source"),("pipeline","Cache → clean → resolve",2.8,4.5,2,1,"process"),("neo","Neo4j 5\nProperty Graph",5.3,4.5,2,1,"graph"),("rdf","RDF/OWL/SPARQL",5.3,2.5,2,1,"semantic"),("qa","QA planner + safe compiler",7.8,4.5,2,1,"process"),("rec","IDF graph recommender",7.8,2.5,2,1,"semantic"),("api","FastAPI",10.2,3.5,1.5,1,"app"),("ui","Web UI",10.2,1.5,1.5,1,"app")],
       [("sources","pipeline","raw cache"),("pipeline","neo","CSV + manifest"),("neo","rdf","export"),("neo","qa","evidence"),("neo","rec","features"),("qa","api","answer"),("rec","api","ranking"),("api","ui","JSON/HTTP")],"Neo4j là backend phục vụ; RDF là nhánh tiêu chuẩn hóa và đối chiếu ngữ nghĩa."),
      ("entity_resolution_flow","Cleaning và phân giải thực thể",[
       ("raw","TMDB raw records",.3,3,1.7,1,"source"),("clean","Chuẩn hóa\nvalidate required fields",2.4,3,2,1,"process"),("id","Exact stable ID\nTMDB ↔ IMDb",4.9,4.2,2,1,"graph"),("fuzzy","Fuzzy fallback\nscore + log",4.9,1.8,2,1,"process"),("decision","Ngưỡng + uniqueness",7.4,3,2,1,"semantic"),("out","Canonical entities\n+ provenance",9.9,3,1.8,1,"app")],
       [("raw","clean",""),("clean","id","ưu tiên"),("clean","fuzzy","khi thiếu ID"),("id","decision",""),("fuzzy","decision",""),("decision","out","accepted / rejected")],"Không dùng tên làm khóa chính; mọi fallback đều có confidence và audit log."),
      ("etl_pipeline","Pipeline dữ liệu tái lập",[
       ("collect","Collect\nTMDB + IMDb",.2,3,1.5,1,"source"),("raw","Immutable raw\nJSON / GZIP",2.1,3,1.6,1,"source"),("process","Clean · normalize\nentity resolution",4.1,3,1.8,1,"process"),("tables","Node/edge CSV\nmanifest",6.3,3,1.6,1,"process"),("neo","Neo4j import\nconstraints + MERGE",8.3,4.2,1.8,1,"graph"),("rdf","RDF export\nmaterialization",8.3,1.8,1.8,1,"semantic"),("eval","Validation +\nexperiments",10.5,3,1.3,1,"app")],
       [("collect","raw","cache"),("raw","process","checksum"),("process","tables",""),("tables","neo","batch"),("tables","rdf","same snapshot"),("neo","eval",""),("rdf","eval","")],"Import lặp lại không tạo bản ghi trùng; manifest và checksum bảo đảm truy vết."),
      ("costar_reasoning","Suy diễn quan hệ CO_STARRED_WITH",[
       ("a","Person A",.7,4,1.7,1,"source"),("m1","Movie M1",4,4.8,1.7,1,"graph"),("m2","Movie M2",4,2.4,1.7,1,"graph"),("b","Person B",7.3,4,1.7,1,"source"),("derived","CO_STARRED_WITH\ncount=2 · evidence=[M1,M2]",9.5,3.7,2.2,1.2,"semantic")],
       [("a","m1","ACTED_IN"),("a","m2","ACTED_IN"),("b","m1","ACTED_IN"),("b","m2","ACTED_IN"),("b","derived","derive"),("a","derived","derive")],"Luật chỉ tạo fact khi có đường bằng chứng; edge mang derived=true, count và evidence."),
      ("semantic_reasoning","Materialization và kiểm tra ngữ nghĩa",[
       ("ttl","RDF asserted\n154,970 triples",.5,3,2,1,"source"),("rules","RDFS/OWL-RL subset\ndomain · range · inverse · symmetric",3.1,3,2.5,1.2,"semantic"),("mat","Materialized graph\n190,389 triples",6.3,3,2,1,"graph"),("validate","Constraint checks\nfunctional · disjoint · title",8.9,3,2.2,1.2,"process"),("result","0 violations\n+35,419 inferred",9.2,.8,1.8,1,"app")],
       [("ttl","rules",""),("rules","mat",""),("mat","validate",""),("validate","result","report")],"Đây là subset thực thi bằng RDFLib, không được trình bày như reasoner OWL 2 DL đầy đủ."),
      ("qa_sequence","Luồng xử lý yêu cầu hỏi–đáp",[
       ("user","Người dùng",.2,3,1.4,1,"source"),("api","POST /ask",2,3,1.4,1,"app"),("planner","LLM planner hoặc\n9-intent fallback",3.9,3,1.9,1,"process"),("link","Entity linker",6.3,3,1.5,1,"process"),("compile","Whitelist compiler\nparameterized Cypher",8.3,3,1.9,1,"semantic"),("neo","Neo4j",10.7,3,1.1,1,"graph"),("answer","Answer + evidence\n+ confidence",8.3,.9,1.9,1,"app")],
       [("user","api","question"),("api","planner",""),("planner","link","QueryPlan"),("link","compile","canonical IDs"),("compile","neo","safe query"),("neo","answer","rows"),("answer","user","JSON response")],"LLM không sinh Cypher và không trả lời từ tri thức nội tại; Neo4j evidence là nguồn chuẩn."),
      ("recommendation_explanation","Xếp hạng và giải thích gợi ý phim",[
       ("seed","Phim đầu vào",.4,3,1.5,1,"source"),("features","Graph features\ngenre · actor · director\nkeyword · studio",2.4,3,2,1.3,"graph"),("idf","IDF weighting\ntype_weight × rarity",5,3,2,1.2,"process"),("rank","Aggregate + rank\nTop-K",7.6,3,1.7,1,"semantic"),("explain","Shared features\n+ graph evidence",9.8,3,1.8,1.2,"app")],
       [("seed","features","traverse"),("features","idf","candidate overlap"),("idf","rank","score"),("rank","explain","ranked movies")],"Trọng số loại: director 3; actor 2; keyword 1.5; genre 1; studio 0.75."),
      ("web_ui","Wireframe giao diện web hai chức năng",[
       ("header","MOVIE KNOWLEDGE GRAPH\nAdvanced Database",.4,5,11.2,.8,"neutral"),("tabs","[ Hỏi đáp ]     [ Gợi ý phim tương tự ]",.8,4.1,10.4,.6,"source"),("history","Trợ lý: Hãy hỏi về phim, diễn viên, đạo diễn…\n\nBạn: Các phim của Christopher Nolan?\n\nTrợ lý: Danh sách kết quả + evidence",.8,1.4,7.2,2.3,"neutral"),("evidence","GRAPH EVIDENCE\nEntity link · Cypher intent\nRows · latency",8.4,2.5,2.8,1.2,"semantic"),("input","Nhập câu hỏi tiếp theo…                         [ Gửi ]",.8,.6,10.4,.55,"app")],
       [("tabs","history","active tab"),("history","evidence","expand")],"Wireframe bám theo src/api/static/index.html; thay bằng screenshot thật trước khi nộp nếu có."),
    ]
    for args in diagrams: diagram(*args)
    metric_plots()


if __name__ == "__main__": main()
