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
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report_latex" / "images"
SOURCES = OUT / "sources"

COLORS = {
    "source": "#E8F1FB",
    "process": "#FFF3D6",
    "graph": "#E5F3E5",
    "semantic": "#F0E8F7",
    "app": "#FDE8E7",
    "neutral": "#F3F5F7",
}
STROKES = {
    "source": "#3B73A8", "process": "#C58A18", "graph": "#4D8B52",
    "semantic": "#7B5AA6", "app": "#C85452", "neutral": "#5F6B76",
}
INK = "#17365D"
EDGE = "#40536B"


def _port(box, side, fraction=.5):
    x, y, w, h = box
    return {
        "left": (x, y + h * fraction), "right": (x + w, y + h * fraction),
        "top": (x + w * fraction, y + h), "bottom": (x + w * fraction, y),
    }[side]


def _route(boxes, src, dst, lane=0.0, source_fraction=.5, target_fraction=.5,
           waypoints=None):
    """Return an orthogonal route, explicit ports and a label anchor."""
    source, target = boxes[src], boxes[dst]
    if src == dst:
        start = _port(source, "top", .28); end = _port(source, "top", .72)
        high = source[1] + source[3] + .55 + lane
        points = [start, (start[0], high), (end[0], high), end]
        return points, "top", "top"

    sx, sy, sw, sh = source; tx, ty, tw, th = target
    dx = tx + tw / 2 - (sx + sw / 2); dy = ty + th / 2 - (sy + sh / 2)
    if abs(dx) >= abs(dy):
        source_side, target_side = (("right", "left") if dx > 0 else ("left", "right"))
        start = _port(source, source_side, source_fraction)
        end = _port(target, target_side, target_fraction)
        if abs(start[1] - end[1]) < .05:
            points = [start, end]
        else:
            mid = (start[0] + end[0]) / 2 + lane
            points = [start, (mid, start[1]), (mid, end[1]), end]
    else:
        source_side, target_side = (("top", "bottom") if dy > 0 else ("bottom", "top"))
        start = _port(source, source_side, source_fraction)
        end = _port(target, target_side, target_fraction)
        if abs(start[0] - end[0]) < .05:
            points = [start, end]
        else:
            mid = (start[1] + end[1]) / 2 + lane
            points = [start, (start[0], mid), (end[0], mid), end]
    if waypoints:
        points = [start, *waypoints, end]
    return points, source_side, target_side


def _label_anchor(points):
    segments = list(zip(points, points[1:]))
    start, end = max(segments, key=lambda pair: abs(pair[1][0] - pair[0][0]) + abs(pair[1][1] - pair[0][1]))
    horizontal = abs(end[0] - start[0]) >= abs(end[1] - start[1])
    x, y = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
    return (x, y + .13) if horizontal else (x + .13, y)


def _draw_route(ax, points, label):
    xs, ys = zip(*points)
    ax.plot(xs, ys, color="white", linewidth=4.2, solid_capstyle="round", zorder=1)
    ax.plot(xs, ys, color=EDGE, linewidth=1.45, solid_capstyle="round", zorder=2)
    start, end = points[-2], points[-1]
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13,
                                linewidth=1.45, color=EDGE, zorder=3))
    if label:
        x, y = _label_anchor(points)
        ax.text(x, y, label, fontsize=8.8, ha="center", va="center", color="#2F3B4A",
                bbox=dict(boxstyle="round,pad=0.22", facecolor="white", edgecolor="#D7DEE7",
                          linewidth=.6, alpha=.98), zorder=8)


def _draw_node(ax, label, x, y, w, h, role):
    ax.add_patch(FancyBboxPatch((x + .045, y - .055), w, h,
                               boxstyle="round,pad=0.03,rounding_size=0.09",
                               facecolor="#D8DEE6", edgecolor="none", alpha=.55, zorder=4))
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                               boxstyle="round,pad=0.03,rounding_size=0.09",
                               facecolor=COLORS[role], edgecolor=STROKES[role], linewidth=1.65, zorder=5))
    ax.add_patch(Rectangle((x, y + h - .075), w, .075, facecolor=STROKES[role],
                           edgecolor="none", zorder=6))
    lines = label.split("\n")
    if len(lines) == 1:
        ax.text(x + w / 2, y + h / 2, lines[0], ha="center", va="center",
                fontsize=11.5, weight="semibold", color="#1F2937", zorder=7)
    else:
        ax.text(x + w / 2, y + h * .68, lines[0], ha="center", va="center",
                fontsize=10.8, weight="semibold", color="#1F2937", zorder=7)
        ax.text(x + w / 2, y + h * .34, "\n".join(lines[1:]), ha="center", va="center",
                fontsize=9.2, color="#354152", linespacing=1.12, zorder=7)


def diagram(name, title, nodes, edges, note=None):
    """Render a publication-ready PDF and matching editable draw.io source."""
    # Match the physical size used on an A4 report page.  A very wide source
    # canvas would make LaTeX scale 8–10 pt labels down to unreadable text.
    fig, ax = plt.subplots(figsize=(7.4, 4.16))
    fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(0, 6.8); ax.axis("off")
    ax.text(6, 6.48, title, ha="center", va="center", fontsize=16.0,
            weight="bold", color=INK)
    ax.plot([4.7, 7.3], [6.22, 6.22], color="#C9D5E3", linewidth=1.2)
    boxes = {}
    for node_id, label, x, y, w, h, role in nodes:
        boxes[node_id] = (x, y, w, h)
    routes = []
    for item in edges:
        src, dst, label = item[:3]
        lane = item[3] if len(item) > 3 else 0.0
        source_fraction = item[4] if len(item) > 4 else .5
        target_fraction = item[5] if len(item) > 5 else .5
        waypoints = item[6] if len(item) > 6 else None
        points, source_side, target_side = _route(
            boxes, src, dst, lane, source_fraction, target_fraction, waypoints
        )
        routes.append((src, dst, label, points, source_side, target_side,
                       source_fraction, target_fraction))
        _draw_route(ax, points, label)
    for _, label, x, y, w, h, role in nodes:
        _draw_node(ax, label, x, y, w, h, role)
    if note:
        ax.text(6, .19, note, fontsize=9.0, color="#445164", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=.35", facecolor="#F7F9FB", edgecolor="#D7DEE7", linewidth=.7))
    fig.tight_layout(pad=.65)
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", pad_inches=.08)
    plt.close(fig)

    mxfile = ET.Element("mxfile", host="drawio", version="26.0.0")
    page = ET.SubElement(mxfile, "diagram", name=title, id=name)
    model = ET.SubElement(page, "mxGraphModel", grid="1", gridSize="10", page="1", pageWidth="1200", pageHeight="680")
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0"); ET.SubElement(root, "mxCell", id="1", parent="0")
    for node_id, label, x, y, w, h, role in nodes:
        cell = ET.SubElement(root, "mxCell", id=node_id, value=label,
            style=(f"rounded=1;whiteSpace=wrap;html=1;fillColor={COLORS[role]};"
                   f"strokeColor={STROKES[role]};strokeWidth=2;fontSize=15;fontColor=#1F2937;"
                   "fontStyle=1;spacing=8;shadow=1;"),
            vertex="1", parent="1")
        ET.SubElement(cell, "mxGeometry", x=str(round(x*100)), y=str(round((6.1-y-h)*100)),
                      width=str(round(w*100)), height=str(round(h*100)), **{"as":"geometry"})
    def port_values(side, fraction):
        # Matplotlib's y-axis grows upward; draw.io's entryY/exitY grows
        # downward, so vertical fractions on left/right ports must be inverted.
        return {"left": (0, 1 - fraction), "right": (1, 1 - fraction),
                "top": (fraction, 0), "bottom": (fraction, 1)}[side]
    for i, (src, dst, label, points, source_side, target_side,
            source_fraction, target_fraction) in enumerate(routes, 1):
        ex, ey = port_values(source_side, source_fraction)
        enx, eny = port_values(target_side, target_fraction)
        style = ("edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
                 "endArrow=block;endFill=1;strokeColor=#40536B;strokeWidth=2;fontSize=13;"
                 "fontColor=#2F3B4A;labelBackgroundColor=#FFFFFF;spacingBottom=8;"
                 f"exitX={ex};exitY={ey};exitDx=0;exitDy=0;entryX={enx};entryY={eny};entryDx=0;entryDy=0;")
        edge = ET.SubElement(root, "mxCell", id=f"e{i}", value=label, style=style,
                             edge="1", parent="1", source=src, target=dst)
        geometry = ET.SubElement(edge, "mxGeometry", relative="1", y="-12", **{"as":"geometry"})
        if len(points) > 2:
            waypoints = ET.SubElement(geometry, "Array", **{"as": "points"})
            for px, py in points[1:-1]:
                ET.SubElement(waypoints, "mxPoint", x=str(round(px * 100)),
                              y=str(round((6.1 - py) * 100)))
    ET.indent(mxfile)
    ET.ElementTree(mxfile).write(SOURCES / f"{name}.drawio", encoding="utf-8", xml_declaration=True)


def metric_plots():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11.5,
        "axes.titlesize": 15, "axes.titleweight": "bold", "axes.labelcolor": "#354152",
        "axes.edgecolor": "#B9C4D0", "xtick.color": "#354152", "ytick.color": "#354152",
    })
    with (ROOT/"experiments/results/summary/quality_metrics.csv").open() as f:
        rows = list(csv.DictReader(f))
    labels = [r["metric"].replace("Entity resolution ", "ER — ").replace("Recommendation ", "Gợi ý — ")
              .replace("Co-star", "Đồng diễn").replace("QA smoke accuracy", "QA — độ chính xác")
              .replace("Semantic conformance", "RDF — nhất quán ngữ nghĩa")
              .replace("Neo4j structural validity", "Neo4j — hợp lệ cấu trúc") for r in rows]
    values = [float(r["value"]) for r in rows]
    colors = ["#3B73A8"] * 4 + ["#C58A18"] * 2 + ["#7B5AA6", "#4D8B52", "#4D8B52"]
    fig, ax = plt.subplots(figsize=(7.4, 4.8)); y = list(range(len(rows)))
    ax.barh(y, values, height=.62, color=colors, edgecolor="white", linewidth=.7)
    ax.set_yticks(y, labels); ax.invert_yaxis(); ax.set_xlim(0, 1.06)
    ax.set_xlabel("Giá trị chỉ số (0–1)"); ax.set_title("Tổng hợp chất lượng dữ liệu và kết quả đánh giá", color=INK, pad=15)
    for i, v in enumerate(values):
        ax.text(min(v + .012, 1.015), i, f"{v:.3f}", va="center", ha="left",
                fontsize=10.5, weight="semibold", color="#263445")
    ax.grid(axis="x", color="#D7DEE7", linewidth=.7); ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.tight_layout(pad=1.2); fig.savefig(OUT/"quality_metrics.pdf", bbox_inches="tight"); plt.close(fig)

    with (ROOT/"experiments/results/summary/benchmark_comparison.csv").open() as f:
        rows = list(csv.DictReader(f))
    intent_labels = {
        "movies_by_director": "Phim theo đạo diễn", "common_movies": "Phim chung của hai diễn viên",
        "movies_by_genre_rating": "Phim theo thể loại và điểm", "directors_by_genre": "Đạo diễn theo thể loại",
    }
    labels = [intent_labels.get(r["intent"], r["intent"].replace("_", " ")) for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 4.8), sharey=True)
    for ax, statistic, neo_key, sqlite_key in (
        (axes[0], "Median", "neo4j_median_ms", "sqlite_median_ms"),
        (axes[1], "P95", "neo4j_p95_ms", "sqlite_p95_ms"),
    ):
        y = list(range(len(rows))); offset = .18
        neo = [float(r[neo_key]) for r in rows]; sqlite = [float(r[sqlite_key]) for r in rows]
        ax.barh([i - offset for i in y], neo, height=.32, color="#3B73A8", label="Neo4j")
        ax.barh([i + offset for i in y], sqlite, height=.32, color="#C85452", label="SQLite")
        ax.set_xscale("log"); ax.set_title(statistic, color=INK, pad=10); ax.set_xlabel("Độ trễ (ms, thang log)")
        ax.grid(axis="x", color="#D7DEE7", linewidth=.7); ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        for i, value in enumerate(neo): ax.text(value * 1.07, i - offset, f"{value:.2f}", va="center", fontsize=9.2)
        for i, value in enumerate(sqlite): ax.text(value * 1.07, i + offset, f"{value:.2f}", va="center", fontsize=9.2)
    axes[0].set_yticks(list(range(len(rows))), labels); axes[0].invert_yaxis()
    handles, legend_labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="upper center", bbox_to_anchor=(.5, .93), ncol=2, frameon=False)
    fig.suptitle("Độ trễ Neo4j và SQLite trên cùng snapshot (100 lần chạy)", color=INK,
                 fontsize=15.5, weight="bold", y=.995)
    fig.tight_layout(rect=(0, 0, 1, .90), pad=1.2); fig.savefig(OUT/"query_latency.pdf", bbox_inches="tight"); plt.close(fig)

    data=json.loads((ROOT/"experiments/results/recommendation_ablation.json").read_text())["results"]
    production={"method":"idf_weighted (production)","precision_at_k":.715,"ndcg_at_k":.7542484569}
    data=[production]+data
    method_labels = {"idf_weighted (production)": "IDF-weighted\n(đang sử dụng)", "overlap": "Overlap",
                     "weighted_jaccard": "Weighted Jaccard", "hybrid": "Hybrid"}
    labels=[method_labels[d["method"]] for d in data]
    fig,ax=plt.subplots(figsize=(7.2,4.6)); x=list(range(len(data))); w=.31
    ax.axvspan(-.48, .48, color="#E8F3E8", zorder=0)
    bars_p = ax.bar([i-w/2 for i in x],[d["precision_at_k"] for d in data],w,label="P@10",color="#3B73A8")
    bars_n = ax.bar([i+w/2 for i in x],[d["ndcg_at_k"] for d in data],w,label="NDCG@10",color="#C58A18")
    ax.bar_label(bars_p, fmt="%.3f", padding=3, fontsize=10); ax.bar_label(bars_n, fmt="%.3f", padding=3, fontsize=10)
    ax.set_ylim(0, .86); ax.set_xticks(x,labels); ax.set_ylabel("Giá trị chỉ số")
    ax.set_title("So sánh các phương pháp xếp hạng trên 20 trường hợp kiểm thử", color=INK, pad=15)
    ax.legend(frameon=False, ncol=2, loc="upper right"); ax.grid(axis="y", color="#D7DEE7", linewidth=.7)
    ax.set_axisbelow(True); ax.spines[["top", "right", "left"]].set_visible(False)
    fig.tight_layout(pad=1.2); fig.savefig(OUT/"recommendation_ablation.pdf", bbox_inches="tight"); plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True); SOURCES.mkdir(parents=True, exist_ok=True)
    diagrams = [
      ("movie_kg_overview", "Khái quát Movie Knowledge Graph", [
       ("movie", "Movie\nID · tiêu đề · rating", 4.8, 2.75, 2.4, 1.15, "graph"),
       ("person", "Person\ndiễn viên / đạo diễn", .55, 4.35, 2.35, 1.05, "source"),
       ("genre", "Genre\nthể loại", .55, 1.25, 2.35, 1.05, "semantic"),
       ("keyword", "Keyword\nchủ đề", 9.1, 4.35, 2.35, 1.05, "process"),
       ("studio", "Studio\nhãng sản xuất", 9.1, 1.25, 2.35, 1.05, "app")],
       [("person", "movie", "ACTED_IN / DIRECTED", -.22, .5, .72),
        ("movie", "genre", "HAS_GENRE", .22, .28, .5),
        ("movie", "keyword", "HAS_KEYWORD", -.22, .72, .5),
        ("movie", "studio", "PRODUCED_BY", .22, .28, .5)],
       "Movie là nút trung tâm; node và relationship đều giữ định danh nguồn cùng provenance."),

      ("ontology_diagram", "Ontology miền phim (RDF/OWL)", [
       ("movie", "kg:Movie\ntitle · rating · tmdbId", 4.75, 2.85, 2.5, 1.15, "graph"),
       ("person", "kg:Person\nname", .45, 4.35, 2.3, 1.0, "source"),
       ("genre", "kg:Genre\nname", .45, 1.35, 2.3, 1.0, "semantic"),
       ("keyword", "kg:Keyword\nname", 9.25, 4.35, 2.3, 1.0, "process"),
       ("studio", "kg:Studio\nname", 9.25, 1.35, 2.3, 1.0, "app"),
       ("axioms", "OWL axioms\ndomain/range · inverse · symmetric · functional", 4.25, .65, 3.5, .95, "neutral")],
       [("person", "movie", "actedIn / directed", -.22, .5, .72),
        ("movie", "genre", "hasGenre", .22, .28, .5),
        ("movie", "keyword", "hasKeyword", -.22, .72, .5),
        ("movie", "studio", "producedBy", .22, .28, .5),
        ("person", "person", "coStarredWith", -.22),
        ("movie", "axioms", "ràng buộc ngữ nghĩa")],
       "Ontology dùng một lớp Person; vai trò actor/director được biểu diễn bằng object property."),

      ("property_graph_schema", "Lược đồ Property Graph trong Neo4j", [
       ("movie", "Movie\ntmdb_id · title · rating", 4.75, 2.75, 2.5, 1.15, "graph"),
       ("person", "Person\nperson_id · name", .45, 4.35, 2.45, 1.05, "source"),
       ("genre", "Genre\ngenre_id · name", .45, 1.2, 2.45, 1.05, "semantic"),
       ("keyword", "Keyword\nkeyword_id · name", 9.1, 4.35, 2.45, 1.05, "process"),
       ("studio", "Studio\ncompany_id · name", 9.1, 1.2, 2.45, 1.05, "app")],
       [("person", "movie", "ACTED_IN", -.42, .35, .72),
        ("person", "movie", "DIRECTED", -.05, .72, .88),
        ("movie", "genre", "HAS_GENRE", .38, .25, .5),
        ("movie", "keyword", "HAS_KEYWORD", -.22, .75, .5),
        ("movie", "studio", "PRODUCED_BY", .22, .25, .5),
        ("person", "person", "CO_STARRED_WITH {count, evidence}", -.22)],
       "Một Person có thể đồng thời tham gia ACTED_IN và DIRECTED; CO_STARRED_WITH là quan hệ suy diễn."),

      ("system_architecture", "Kiến trúc tổng thể hệ thống", [
       ("sources", "Nguồn\nTMDB · IMDb", .15, 4.35, 1.6, 1.05, "source"),
       ("pipeline", "Xử lý\ncache · clean\nresolve", 2.0, 4.35, 1.7, 1.05, "process"),
       ("artifacts", "Dữ liệu\nCSV · manifest", 3.95, 4.35, 1.65, 1.05, "process"),
       ("neo", "Neo4j 5\nProperty Graph", 5.95, 4.35, 1.65, 1.05, "graph"),
       ("rdf", "RDF / OWL\nSPARQL\nentailment", 5.95, 1.75, 1.65, 1.05, "semantic"),
       ("qa", "Hỏi–đáp\nplanner · linker\ncompiler", 7.95, 4.7, 1.8, 1.05, "process"),
       ("rec", "Gợi ý phim\nIDF graph\nsimilarity", 7.95, 2.15, 1.8, 1.05, "semantic"),
       ("api", "FastAPI\nAPI an toàn", 10.15, 3.55, 1.45, 1.0, "app"),
       ("ui", "Web UI\nQA · gợi ý", 10.15, 1.35, 1.45, 1.0, "app")],
       [("sources", "pipeline", ""), ("pipeline", "artifacts", ""),
        ("artifacts", "neo", ""), ("artifacts", "rdf", "snapshot"),
        ("neo", "qa", "", 0, .7, .5), ("neo", "rec", "", 0, .3, .5),
        ("qa", "api", "", -.22, .65, .7), ("rec", "api", "", .22, .55, .3),
        ("api", "ui", "HTTP")],
       "Neo4j phục vụ ứng dụng; RDF/OWL là nhánh tiêu chuẩn hóa và kiểm tra ngữ nghĩa trên cùng snapshot."),

      ("entity_resolution_flow", "Cleaning và phân giải thực thể", [
       ("raw", "Dữ liệu thô\nTMDB records", .25, 2.9, 1.65, 1.05, "source"),
       ("clean", "Chuẩn hóa\nkiểm tra trường\nbắt buộc", 2.25, 2.9, 1.85, 1.05, "process"),
       ("id", "Đối sánh chính\nexact stable ID", 4.65, 4.25, 2.0, 1.05, "graph"),
       ("fuzzy", "Dự phòng\nfuzzy score · log", 4.65, 1.55, 2.0, 1.05, "process"),
       ("decision", "Quyết định\nngưỡng · duy nhất", 7.25, 2.9, 2.0, 1.05, "semantic"),
       ("out", "Thực thể\nID · provenance\nconfidence", 9.85, 2.9, 1.9, 1.05, "app")],
       [("raw", "clean", ""), ("clean", "id", "exact ID", -.24, .7, .5),
        ("clean", "fuzzy", "fallback", .24, .3, .5), ("id", "decision", "", -.24, .5, .7),
        ("fuzzy", "decision", "", .24, .5, .3), ("decision", "out", "")],
       "Tên không được dùng làm khóa chính; fuzzy fallback luôn có confidence và dấu vết kiểm tra."),

      ("etl_pipeline", "Pipeline dữ liệu có thể chạy lại", [
       ("collect", "Thu thập\nTMDB · IMDb", .15, 2.9, 1.45, 1.05, "source"),
       ("raw", "Raw cache\nJSON · GZIP", 1.9, 2.9, 1.6, 1.05, "source"),
       ("process", "Xử lý\nclean · normalize\nresolve", 3.8, 2.9, 1.85, 1.05, "process"),
       ("tables", "Dữ liệu\nnode/edge CSV\nmanifest", 5.95, 2.9, 1.85, 1.05, "process"),
       ("neo", "Neo4j import\nconstraint · MERGE", 8.2, 4.2, 1.75, 1.05, "graph"),
       ("rdf", "RDF export\nmaterialization", 8.2, 1.6, 1.75, 1.05, "semantic"),
       ("eval", "Kiểm tra\nvalidation\nexperiments", 10.35, 2.9, 1.5, 1.05, "app")],
       [("collect", "raw", ""), ("raw", "process", ""), ("process", "tables", ""),
        ("tables", "neo", "batch", -.24, .72, .5), ("tables", "rdf", "snapshot", .24, .28, .5),
        ("neo", "eval", "", -.24, .5, .7), ("rdf", "eval", "", .24, .5, .3)],
       "Import lặp lại không tạo bản ghi trùng; manifest và checksum cho phép xác định chính xác snapshot."),

      ("costar_reasoning", "Suy diễn quan hệ CO_STARRED_WITH", [
       ("a", "Person A", .45, 3.05, 1.75, 1.05, "source"),
       ("m1", "Movie M1\nbằng chứng 1", 3.55, 4.35, 1.85, 1.05, "graph"),
       ("m2", "Movie M2\nbằng chứng 2", 3.55, 1.75, 1.85, 1.05, "graph"),
       ("b", "Person B", 6.75, 3.05, 1.75, 1.05, "source"),
       ("derived", "Quan hệ mới\nderived · count = 2\nevidence = [M1, M2]", 9.25, 3.0, 2.35, 1.15, "semantic")],
       [("a", "m1", "ACTED_IN", -.24, .75, .5), ("a", "m2", "ACTED_IN", .24, .25, .5),
        ("b", "m1", "ACTED_IN", .24, .75, .5), ("b", "m2", "ACTED_IN", -.24, .25, .5),
        ("b", "derived", "", .18, .5, .5)],
       "Fact chỉ được tạo khi tồn tại shared Movie; edge lưu derived=true, movie_count và evidence_movie_ids."),

      ("semantic_reasoning", "Materialization và kiểm tra ngữ nghĩa", [
       ("ttl", "RDF đầu vào\n154.970 triples", .35, 3.0, 1.8, 1.05, "source"),
       ("rules", "Tập luật\ndomain · range\ninverse · symmetric", 2.55, 3.0, 2.3, 1.05, "semantic"),
       ("mat", "RDF kết quả\n190.389 triples", 5.25, 3.0, 1.95, 1.05, "graph"),
       ("validate", "Kiểm tra\nfunctional · disjoint\nrequired title", 7.6, 3.0, 2.15, 1.05, "process"),
       ("result", "Kết quả\n0 vi phạm\n+35.419 triples", 10.1, 3.0, 1.55, 1.05, "app")],
       [("ttl", "rules", ""), ("rules", "mat", ""),
        ("mat", "validate", ""), ("validate", "result", "")],
       "Workflow dùng RDFLib và một tập con RDFS/OWL-RL; không phải full OWL 2 DL reasoner."),

      ("qa_sequence", "Luồng xử lý yêu cầu hỏi–đáp", [
       ("user", "Người hỏi\ncâu hỏi\ntự nhiên", .15, 4.0, 1.45, 1.05, "source"),
       ("api", "FastAPI\nPOST /ask", 1.9, 4.0, 1.45, 1.05, "app"),
       ("planner", "Planner\nLLM / 9 intents", 3.65, 4.0, 1.85, 1.05, "process"),
       ("link", "Liên kết\ncanonical entity", 5.85, 4.0, 1.7, 1.05, "process"),
       ("compile", "Biên dịch\nCypher whitelist", 7.9, 4.0, 1.75, 1.05, "semantic"),
       ("neo", "Neo4j\nparameterized\nquery", 10.0, 4.0, 1.65, 1.05, "graph"),
       ("answer", "Câu trả lời\nanswer · evidence\nconfidence", 7.75, 1.45, 2.05, 1.05, "app")],
       [("user", "api", ""), ("api", "planner", ""),
        ("planner", "link", ""), ("link", "compile", ""),
        ("compile", "neo", ""), ("neo", "answer", "rows + path"),
        ("answer", "user", "JSON", 0, .5, .5, [(6.7, .95), (.85, .95)])],
       "LLM không sinh Cypher và không tự trả lời; fact cùng evidence luôn được lấy từ Neo4j."),

      ("recommendation_explanation", "Xếp hạng và giải thích gợi ý phim", [
       ("seed", "Phim gốc\nTMDB ID", .35, 3.0, 1.45, 1.05, "source"),
       ("features", "Duyệt graph\ndirector · actor\nkeyword · genre · studio", 2.15, 2.85, 2.35, 1.35, "graph"),
       ("idf", "Đóng góp\ntype weight × IDF", 4.9, 2.95, 2.05, 1.15, "process"),
       ("rank", "Xếp hạng\nsắp xếp Top-K", 7.35, 2.95, 1.8, 1.15, "semantic"),
       ("explain", "Giải thích\nshared features\nscore", 9.55, 2.85, 2.1, 1.35, "app")],
       [("seed", "features", ""), ("features", "idf", ""),
        ("idf", "rank", ""), ("rank", "explain", "")],
       "Trọng số loại: director 3, actor 2, keyword 1,5, genre 1 và studio 0,75."),

      ("web_ui", "Giao diện web: hỏi–đáp và gợi ý phim", [
       ("header", "MOVIE KNOWLEDGE GRAPH\nAdvanced Database", .45, 5.05, 11.1, .75, "neutral"),
       ("tabs", "Điều hướng\nHỏi đáp   |   Gợi ý phim tương tự", .75, 4.0, 10.5, .85, "source"),
       ("history", "Hội thoại hỏi–đáp\nBạn: Phim nào do Christopher Nolan đạo diễn?\nTrợ lý: Danh sách phim và bằng chứng", .75, 1.55, 6.55, 2.15, "neutral"),
       ("evidence", "Bằng chứng graph\nentity link · intent · rows · latency", 7.65, 2.55, 3.6, 1.15, "semantic"),
       ("input", "Ô nhập câu hỏi\nNhập nội dung…                                      Gửi", .75, .55, 10.5, .75, "app")],
       [],
       "Wireframe bám theo giao diện hiện tại: lịch sử hội thoại, evidence và hai tab chức năng."),
    ]
    for args in diagrams: diagram(*args)
    metric_plots()


if __name__ == "__main__": main()
