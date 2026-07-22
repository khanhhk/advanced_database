"""Convert the maintained report manuscript into the repository LaTeX template.

This intentionally supports only the Markdown constructs used by REPORT_DRAFT.md
so the generated chapter files remain predictable and easy to review.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "REPORT_DRAFT.md"
OUT = ROOT / "report_latex" / "contents"

CITATIONS = {
    "1": "w3c2014rdf", "2": "w3c2014rdfs", "3": "w3c2012owl",
    "4": "w3c2013sparql", "5": "neo4j2026cypher", "6": "tmdb2026api",
    "7": "imdb2026datasets",
    "8": "guo2023kgsurvey", "9": "caro2023graph", "10": "colas2023knowledge",
    "11": "ren2024explicit", "12": "zhang2023movie", "13": "saat2024enhanced",
    "14": "su2024temporal", "15": "agarwal2024byokg", "16": "hogan2021knowledge",
}

FIGURES = {
    (1, "Bối cảnh"): ("movie_kg_overview.pdf", "Khái quát miền dữ liệu Movie Knowledge Graph", "fig:movie-kg-overview"),
    (3, "Các lớp và định danh"): ("ontology_diagram.pdf", "Sơ đồ lớp của ontology miền phim", "fig:ontology-diagram"),
    (3, "Relationship"): ("property_graph_schema.pdf", "Lược đồ node và relationship trong Neo4j", "fig:property-graph-schema"),
    (3, "Kiến trúc tổng thể"): ("system_architecture.pdf", "Kiến trúc tổng thể của hệ thống", "fig:system-architecture"),
    (3, "Thuật toán pipeline"): ("etl_pipeline.pdf", "Luồng xử lý dữ liệu từ nguồn đến các graph", "fig:etl-pipeline"),
    (3, "Cleaning và entity resolution"): ("entity_resolution_flow.pdf", "Quy trình cleaning và phân giải thực thể", "fig:entity-resolution"),
    (4, "Suy diễn `CO_STARRED_WITH`"): ("costar_reasoning.pdf", "Suy diễn quan hệ đồng diễn và đường bằng chứng", "fig:costar-reasoning"),
    (4, "Semantic entailment"): ("semantic_reasoning.pdf", "Luồng materialization và kiểm tra ngữ nghĩa", "fig:semantic-reasoning"),
    (6, "Hỏi–đáp"): ("qa_sequence.pdf", "Luồng xử lý một yêu cầu hỏi--đáp", "fig:qa-sequence"),
    (6, "Recommendation"): ("recommendation_explanation.pdf", "Luồng xếp hạng và tạo giải thích gợi ý phim", "fig:recommendation-flow"),
    (6, "API và UI"): ("web_ui.pdf", "Giao diện hỏi--đáp và gợi ý phim", "fig:web-ui"),
    (5, "Dataset và graph"): ("quality_metrics.pdf", "Tổng hợp chỉ số chất lượng dữ liệu và graph", "fig:quality-metrics"),
    (5, "Hiệu năng"): ("query_latency.pdf", "Phân bố độ trễ truy vấn Neo4j", "fig:query-latency"),
    (5, "Recommendation"): ("recommendation_ablation.pdf", "So sánh kết quả các phương pháp xếp hạng", "fig:recommendation-ablation"),
}

TABLE_WIDTHS = {
    # Field names and descriptions need substantially more room than the
    # required/source columns. Values sum to 0.82 so tab padding and rules still
    # fit inside the text block.
    (3, "Từ điển dữ liệu và quy tắc miền"): [0.23, 0.14, 0.09, 0.14, 0.22],
    # Artifact descriptions are longer than their paths. Explicit breaks in the
    # path cells keep long monospace filenames from crossing the column border.
    (None, "Cấu trúc dữ liệu và kết quả thực nghiệm"): [0.36, 0.52],
}


# The submission report follows the six rubric groups in ChecklistCSDLNCv2.XLS.
# Source sections keep their descriptive headings as subsections, while the 20
# rubric criteria become the ordered top-level sections that appear in the TOC.
RUBRIC_OUTLINE = [
    ("I. Đặt vấn đề và tổng quan", [
        ("Mô tả bài toán, ngữ cảnh, phạm vi, mục tiêu và lý do lựa chọn công nghệ CSDL",
         [(1, "Bối cảnh"), (1, "Phát biểu bài toán"), (1, "Câu hỏi nghiên cứu"),
          (1, "Mục tiêu"), (1, "Phạm vi")], None),
        ("Khảo sát tổng quan công nghệ và mô hình liên quan",
         [(3, "Phương pháp khảo sát"), (3, "Tổng hợp nghiên cứu"),
          (3, "Khoảng trống và vị trí đề tài"),
          (3, "So sánh có cấu trúc các công trình liên quan"),
          (3, "Liên hệ survey với quyết định thiết kế")], None),
        ("So sánh với mô hình quan hệ truyền thống và giải pháp thay thế",
         [(2, "Property Graph và Neo4j"), (2, "So sánh mô hình")], None),
    ]),
    ("II. Lý thuyết và mô hình dữ liệu", [
        ("Biểu diễn tri thức và ngữ nghĩa",
         [(2, "Tri thức và Knowledge Graph"), (2, "Ontology"),
          (2, "RDF, RDFS, OWL và SPARQL")], None),
        ("Cơ chế suy diễn và lập luận",
         [(7, "Hai loại suy diễn")],
         "Phần này phân biệt suy diễn cấu trúc trong property graph với entailment "
         "ngữ nghĩa trên RDF/OWL; phần cài đặt và bằng chứng được trình bày theo "
         "đúng thứ tự ở tiêu chí 13."),
        ("Chất lượng tri thức: liên kết thực thể, tính nhất quán và tính đầy đủ",
         [(2, "Entity resolution"), (2, "Tính đúng, tính đầy đủ và tính nhất quán"),
          (5, "Provenance")], None),
    ]),
    ("III. Thiết kế và cài đặt hệ thống", [
        ("Lựa chọn, cấu hình và triển khai DBMS/công cụ",
         [(6, "Kiến trúc tổng thể"), (4, "Yêu cầu phi chức năng")], None),
        ("Chuẩn bị bộ dữ liệu thực nghiệm",
         [(6, "Thu thập TMDB"), (6, "Tích hợp IMDb"),
          (6, "Quản trị nguồn, điều khoản sử dụng và đạo đức dữ liệu"),
          (6, "Cleaning và entity resolution"), (6, "Normalized artifacts và manifest"),
          (6, "Thuật toán pipeline"), (6, "Xử lý lỗi"),
          (6, "Tái lập và thay đổi nguồn"), (2, "Idempotency và reproducibility")], None),
        ("Thiết kế và tinh chỉnh ontology hoặc lược đồ Knowledge Graph",
         [(5, "Các lớp và định danh"), (5, "Relationship"), (5, "Ontology RDF/OWL"),
          (5, "Ánh xạ RDF–Neo4j"), (5, "Các quyết định mô hình hóa"),
          (5, "Từ điển dữ liệu và quy tắc miền")], None),
        ("Cài đặt trên Knowledge Graph engine và cấu hình reasoner",
         [(6, "Import và validation Neo4j")],
         "Neo4j là operational Knowledge Graph engine; RDFLib đảm nhiệm export, "
         "materialization và validation cho nhánh RDF/OWL của cùng snapshot."),
    ]),
    ("IV. Truy vấn, xử lý và nghiệp vụ", [
        ("Ngôn ngữ truy vấn và suy diễn đặc thù",
         [(7, "SPARQL"), (7, "An toàn truy vấn")], None),
        ("Bộ truy vấn và thao tác nghiệp vụ từ cơ bản đến nâng cao",
         [(7, "Cypher catalog và CRUD"), (4, "Competency questions"),
          (4, "Ma trận truy vết competency question"), (4, "Acceptance criteria")], None),
        ("Truy vấn có suy luận và tri thức ẩn",
         [(7, "Suy diễn `CO_STARRED_WITH`"), (7, "Semantic entailment")], None),
    ]),
    ("V. Thực nghiệm và đánh giá", [
        ("Tiêu chí đánh giá",
         [(2, "Recommendation dựa trên graph"), (2, "Chỉ số đánh giá"),
          (9, "Cách đọc kết quả")], None),
        ("Kịch bản thực nghiệm, benchmark, bảng biểu và baseline",
         [(9, "Dataset và graph"), (9, "Entity resolution"), (9, "Reasoning"),
          (9, "QA"), (9, "Recommendation"), (9, "Hiệu năng"),
          (9, "Protocol tái chạy thực nghiệm"), (9, "Kiểm thử và quy trình chạy")], None),
        ("Phân tích, bàn luận, hạn chế và hướng cải tiến",
         [(9, "Threats to validity"), (9, "Trả lời câu hỏi nghiên cứu"),
          (9, "Phân tích lỗi và hướng khắc phục")], None),
    ]),
    ("VI. Ứng dụng, báo cáo và trình bày", [
        ("Ứng dụng nghiệp vụ và demo chương trình",
         [(4, "Stakeholder và use case"), (4, "Yêu cầu chức năng"),
          (8, "Hỏi–đáp"), (8, "Recommendation"), (8, "API và UI"),
          (8, "An toàn và vận hành"), (8, "Failure modes"),
          (8, "Tính faithful của explanation")], None),
        ("Chất lượng báo cáo, sơ đồ và tài liệu tham khảo",
         [(1, "Đóng góp"), (1, "Cấu trúc báo cáo")],
         "Báo cáo duy trì một bản thảo nguồn, bộ hình vector có nguồn draw.io và "
         "thư mục tài liệu tham khảo chuẩn hóa để bảo đảm bố cục và khả năng tái tạo."),
        ("Slide và thuyết trình",
         [], "Nội dung thuyết trình được rút từ cùng số liệu đã kiểm chứng trong báo cáo, "
         "tập trung vào kiến trúc, demo, kết quả và giới hạn; thời lượng và checklist "
         "trước bảo vệ được quản lý trong dàn ý slide của dự án."),
        ("Chuẩn bị trả lời phản biện",
         [], "Bộ câu hỏi phản biện tập trung vào lựa chọn mô hình, tính đúng của suy diễn, "
         "độ trung thực của explanation, giới hạn của silver evaluation và điều kiện "
         "để diễn giải benchmark một cách hợp lệ."),
    ]),
]


def escape(value: str) -> str:
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%",
                    "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{",
                    "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(char, char) for char in value)


def inline(value: str) -> str:
    tokens: list[str] = []
    def stash(rendered: str) -> str:
        tokens.append(rendered); return f"@@TOKEN{len(tokens)-1}@@"
    value = re.sub(r"<br\s*/?>", lambda _: stash(r"\linebreak{}"), value, flags=re.IGNORECASE)
    value = re.sub(r"`([^`]+)`", lambda m: stash(r"\texttt{" + escape(m.group(1)) + "}"), value)
    value = re.sub(r"\*\*([^*]+)\*\*", lambda m: stash(r"\textbf{" + escape(m.group(1)) + "}"), value)
    value = re.sub(r"\[([1-9]|1[0-6])\]", lambda m: stash(r"\cite{" + CITATIONS[m.group(1)] + "}"), value)
    value = escape(value)
    for index, token in enumerate(tokens): value = value.replace(f"@@TOKEN{index}@@", token)
    return value


def title_without_number(title: str) -> str:
    title = re.sub(r"^Chương\s+\d+\.\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^Phụ lục\s+[A-Z]\.\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^[A-Z]\.\d+\.\s*", "", title)
    return re.sub(r"^\d+(?:\.\d+)*\.\s*", "", title).strip()


def render_table(lines: list[str], caption: str, label: str,
                 widths: list[float] | None = None) -> list[str]:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows = [rows[0], *rows[2:]]  # remove Markdown alignment row
    columns = len(rows[0])
    if widths is None:
        width = max(0.12, 0.88 / columns)
        widths = [width] * columns
    if len(widths) != columns:
        raise ValueError(f"Expected {columns} table widths, received {len(widths)}")
    spec = "|" + "|".join(
        f">{{\\raggedright\\arraybackslash}}p{{{width:.2f}\\textwidth}}" for width in widths
    ) + "|"
    result = [r"\begin{longtable}{" + spec + "}",
              r"\caption{" + inline(caption) + r"}\label{" + label + r"} \\",
              r"\hline"]
    for index, row in enumerate(rows):
        cells = [inline(cell) for cell in row]
        if index == 0: cells = [r"\textbf{" + cell + "}" for cell in cells]
        result.append(" & ".join(cells) + r" \\ \hline")
        if index == 0: result.append(r"\endfirsthead\hline " + " & ".join(cells) + r" \\ \hline\endhead")
    result.append(r"\end{longtable}")
    return result


def convert(lines: list[str], chapter_number: int | None) -> str:
    out: list[str] = ["% Generated from docs/REPORT_DRAFT.md; edit the manuscript then rerun the converter."]
    index = 0; list_kind = None; in_code = False; emitted_figures: set[str] = set()
    current_heading = "Nội dung tổng hợp"; table_count = 0
    heading_table_counts: dict[str, int] = {}
    while index < len(lines):
        line = lines[index].rstrip()
        if line.startswith("```"):
            if list_kind: out.append(f"\\end{{{list_kind}}}"); list_kind = None
            if in_code: out.append(r"\end{Verbatim}"); in_code = False
            else: out.append(r"\begin{Verbatim}[fontsize=\small,breaklines=true,frame=single]"); in_code = True
            index += 1; continue
        if in_code:
            out.append(line); index += 1; continue
        if line.startswith("|") and index + 1 < len(lines) and re.match(r"^\|[\s:|\-]+\|$", lines[index + 1].strip()):
            if list_kind: out.append(f"\\end{{{list_kind}}}"); list_kind = None
            table = [line, lines[index + 1].rstrip()]; index += 2
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                table.append(lines[index].rstrip()); index += 1
            table_count += 1
            heading_table_counts[current_heading] = heading_table_counts.get(current_heading, 0) + 1
            heading_table_count = heading_table_counts[current_heading]
            suffix = f" ({heading_table_count})" if heading_table_count > 1 else ""
            label_prefix = chapter_number if chapter_number is not None else "app"
            widths = TABLE_WIDTHS.get((chapter_number, current_heading))
            out.extend(render_table(table, f"Tổng hợp {current_heading.lower()}{suffix}",
                                    f"tab:{label_prefix}-{table_count}", widths)); continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            if list_kind: out.append(f"\\end{{{list_kind}}}"); list_kind = None
            level, title = len(heading.group(1)), heading.group(2)
            title = title_without_number(title)
            current_heading = re.sub(r"[`*]", "", title)
            if level == 1: out.append(r"\chapter{" + inline(title) + "}")
            elif level == 2 and chapter_number is None and title == "Lời mở đầu":
                out.append(r"\chapter*{" + inline(title) + "}")
                out.append(r"\addcontentsline{toc}{chapter}{" + inline(title) + "}")
            elif level == 2: out.append(r"\section{" + inline(title) + "}")
            elif level == 3: out.append(r"\subsection{" + inline(title) + "}")
            elif level == 4: out.append(r"\subsubsection{" + inline(title) + "}")
            figure = FIGURES.get((chapter_number, title))
            if figure and figure[2] not in emitted_figures:
                filename, caption, label = figure
                out.append(r"\reportfigure{" + filename + "}{" + inline(caption) + "}{" + label + "}")
                emitted_figures.add(label)
            index += 1; continue
        bullet = re.match(r"^\s*-\s+(.+)$", line)
        numbered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        desired = "itemize" if bullet else "enumerate" if numbered else None
        if desired:
            if list_kind != desired:
                if list_kind: out.append(f"\\end{{{list_kind}}}")
                out.append(f"\\begin{{{desired}}}"); list_kind = desired
            item = (bullet or numbered).group(1)
            index += 1
            # Markdown wraps long list items onto unindented continuation lines.
            while index < len(lines):
                continuation = lines[index].rstrip()
                if not continuation.strip() or re.match(r"^\s*(?:-|\d+\.)\s+", continuation):
                    break
                if continuation.startswith(("#", "```", "|", "> ")):
                    break
                item += " " + continuation.strip()
                index += 1
            out.append(r"\item " + inline(item))
            continue
        if list_kind: out.append(f"\\end{{{list_kind}}}"); list_kind = None
        if line.startswith("> "):
            out.extend([r"\begin{quote}\itshape", inline(line[2:]), r"\end{quote}"])
        elif line == "---": out.append(r"\bigskip\hrule\bigskip")
        elif line.strip(): out.append(inline(line))
        else: out.append("")
        index += 1
    if list_kind: out.append(f"\\end{{{list_kind}}}")
    if in_code: out.append(r"\end{Verbatim}")
    return "\n".join(out).strip() + "\n"


def restructure_for_rubric(body: str) -> str:
    """Reorder the maintained manuscript into the checklist's six groups."""
    chapter_matches = list(re.finditer(r"(?m)^# Chương (\d+)\.\s+(.+)$", body))
    sections: dict[tuple[int, str], list[str]] = {}
    chapter_ten = ""
    for chapter_index, chapter_match in enumerate(chapter_matches):
        number = int(chapter_match.group(1))
        end = (chapter_matches[chapter_index + 1].start()
               if chapter_index + 1 < len(chapter_matches) else len(body))
        chapter_text = body[chapter_match.start():end]
        if number == 10:
            chapter_ten = re.sub(r"^# Chương 10\.", "# Chương 7.", chapter_text, count=1)
            continue
        section_matches = list(re.finditer(r"(?m)^##\s+(.+)$", chapter_text))
        for section_index, section_match in enumerate(section_matches):
            section_end = (section_matches[section_index + 1].start()
                           if section_index + 1 < len(section_matches) else len(chapter_text))
            raw_title = section_match.group(1).strip()
            title = title_without_number(raw_title)
            content = chapter_text[section_match.end():section_end].strip("\n")
            sections[(number, title)] = content.splitlines()

    output: list[str] = []
    used: set[tuple[int, str]] = set()
    for chapter_number, (chapter_title, criteria) in enumerate(RUBRIC_OUTLINE, 1):
        output.extend([f"# Chương {chapter_number}. {chapter_title}", ""])
        for criterion_number, (criterion_title, sources, lead) in enumerate(criteria, 1):
            output.extend([f"## {chapter_number}.{criterion_number}. {criterion_title}", ""])
            if lead:
                output.extend([lead, ""])
            for source in sources:
                if source not in sections:
                    raise ValueError(f"Missing report source section: {source}")
                if source in used:
                    raise ValueError(f"Report source section used twice: {source}")
                used.add(source)
                nested = [re.sub(r"^###\s+", "#### ", line) for line in sections[source]]
                output.extend([f"### {source[1]}", "", *nested, ""])

    available = {key for key in sections if key[0] <= 9}
    omitted = available - used
    if omitted:
        raise ValueError(f"Unmapped report source sections: {sorted(omitted)}")
    if not chapter_ten:
        raise ValueError("Missing conclusion chapter")
    output.extend([chapter_ten.strip(), ""])
    return "\n".join(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rewrite-source",
        action="store_true",
        help="Migrate the legacy ten-chapter manuscript to the six rubric groups",
    )
    args = parser.parse_args()
    text = SOURCE.read_text(encoding="utf-8")
    # Exclude the Markdown bibliography; LaTeX uses ref.bib.
    source_body = text.split("# Tài liệu tham khảo sơ bộ", 1)[0]
    already_restructured = bool(re.search(r"(?m)^# Chương 1\. I\. Đặt vấn đề", source_body))
    body = source_body if already_restructured else restructure_for_rubric(source_body)
    if args.rewrite_source and not already_restructured:
        front_end = re.search(r"(?m)^# Chương 1\.", source_body)
        if not front_end:
            raise ValueError("Missing first report chapter")
        tail = text.split("# Tài liệu tham khảo sơ bộ", 1)
        bibliography = "# Tài liệu tham khảo sơ bộ" + tail[1] if len(tail) == 2 else ""
        rewritten = source_body[:front_end.start()].rstrip() + "\n\n" + body.strip()
        if bibliography:
            rewritten += "\n\n" + bibliography.lstrip()
        SOURCE.write_text(rewritten.rstrip() + "\n", encoding="utf-8")
        text = SOURCE.read_text(encoding="utf-8")
        source_body = text.split("# Tài liệu tham khảo sơ bộ", 1)[0]
    chapters = list(re.finditer(r"(?m)^# Chương (\d+)\.\s+(.+)$", body))
    source_chapters = list(re.finditer(r"(?m)^# Chương (\d+)\.\s+(.+)$", source_body))
    front_text = source_body[:source_chapters[0].start()]
    # The title page owns the document title and administrative fields. Start
    # the generated front matter at the introduction instead of relying on a fixed
    # line offset that changes whenever those fields are edited.
    front = ("## Lời mở đầu" + front_text.split("## Lời mở đầu", 1)[1]).splitlines()
    (OUT / "00_frontmatter.tex").write_text(convert(front, None), encoding="utf-8")
    for offset, match in enumerate(chapters):
        start = match.start(); end = chapters[offset + 1].start() if offset + 1 < len(chapters) else len(body)
        number = int(match.group(1)); content = body[start:end].splitlines()
        (OUT / f"{number:02d}_chapter.tex").write_text(convert(content, number), encoding="utf-8")
    for stale_number in range(len(chapters) + 1, 11):
        stale = OUT / f"{stale_number:02d}_chapter.tex"
        if stale.exists():
            stale.unlink()

    appendices = text.split("# Phụ lục A.", 1)
    if len(appendices) == 2:
        appendix_source = "# Phụ lục A." + appendices[1]
        (OUT / "appendices.tex").write_text(convert(appendix_source.splitlines(), None), encoding="utf-8")


if __name__ == "__main__":
    main()
