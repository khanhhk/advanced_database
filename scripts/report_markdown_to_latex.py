"""Convert the maintained report manuscript into the repository LaTeX template.

This intentionally supports only the Markdown constructs used by REPORT_DRAFT.md
so the generated chapter files remain predictable and easy to review.
"""
from __future__ import annotations

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
    (5, "Các lớp và định danh"): ("ontology_diagram.pdf", "Sơ đồ lớp của ontology miền phim", "fig:ontology-diagram"),
    (5, "Relationship"): ("property_graph_schema.pdf", "Lược đồ node và relationship trong Neo4j", "fig:property-graph-schema"),
    (6, "Kiến trúc tổng thể"): ("system_architecture.pdf", "Kiến trúc tổng thể của hệ thống", "fig:system-architecture"),
    (6, "Thuật toán pipeline"): ("etl_pipeline.pdf", "Luồng xử lý dữ liệu từ nguồn đến các graph", "fig:etl-pipeline"),
    (6, "Cleaning và entity resolution"): ("entity_resolution_flow.pdf", "Quy trình cleaning và phân giải thực thể", "fig:entity-resolution"),
    (7, "Suy diễn `CO_STARRED_WITH`"): ("costar_reasoning.pdf", "Suy diễn quan hệ đồng diễn và đường bằng chứng", "fig:costar-reasoning"),
    (7, "Semantic entailment"): ("semantic_reasoning.pdf", "Luồng materialization và kiểm tra ngữ nghĩa", "fig:semantic-reasoning"),
    (8, "Hỏi–đáp"): ("qa_sequence.pdf", "Luồng xử lý một yêu cầu hỏi--đáp", "fig:qa-sequence"),
    (8, "Recommendation"): ("recommendation_explanation.pdf", "Luồng xếp hạng và tạo giải thích gợi ý phim", "fig:recommendation-flow"),
    (8, "API và UI"): ("web_ui.pdf", "Giao diện hỏi--đáp và gợi ý phim", "fig:web-ui"),
    (9, "Dataset và graph"): ("quality_metrics.pdf", "Tổng hợp chỉ số chất lượng dữ liệu và graph", "fig:quality-metrics"),
    (9, "Hiệu năng"): ("query_latency.pdf", "Phân bố độ trễ truy vấn Neo4j", "fig:query-latency"),
    (9, "Recommendation"): ("recommendation_ablation.pdf", "So sánh kết quả các phương pháp xếp hạng", "fig:recommendation-ablation"),
}


def escape(value: str) -> str:
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%",
                    "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{",
                    "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(char, char) for char in value)


def inline(value: str) -> str:
    tokens: list[str] = []
    def stash(rendered: str) -> str:
        tokens.append(rendered); return f"@@TOKEN{len(tokens)-1}@@"
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


def render_table(lines: list[str], caption: str, label: str) -> list[str]:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows = [rows[0], *rows[2:]]  # remove Markdown alignment row
    columns = len(rows[0]); width = max(0.12, 0.88 / columns)
    spec = "|" + "|".join(f">{{\\raggedright\\arraybackslash}}p{{{width:.2f}\\textwidth}}" for _ in range(columns)) + "|"
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
            out.extend(render_table(table, f"Tổng hợp {current_heading.lower()}{suffix}",
                                    f"tab:{label_prefix}-{table_count}")); continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
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


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    # Exclude the Markdown bibliography; LaTeX uses ref.bib.
    body = text.split("# Tài liệu tham khảo sơ bộ", 1)[0]
    chapters = list(re.finditer(r"(?m)^# Chương (\d+)\.\s+(.+)$", body))
    front_text = body[:chapters[0].start()]
    # The title page owns the document title and administrative fields. Start
    # the generated front matter at the introduction instead of relying on a fixed
    # line offset that changes whenever those fields are edited.
    front = ("## Lời mở đầu" + front_text.split("## Lời mở đầu", 1)[1]).splitlines()
    (OUT / "00_frontmatter.tex").write_text(convert(front, None), encoding="utf-8")
    for offset, match in enumerate(chapters):
        start = match.start(); end = chapters[offset + 1].start() if offset + 1 < len(chapters) else len(body)
        number = int(match.group(1)); content = body[start:end].splitlines()
        (OUT / f"{number:02d}_chapter.tex").write_text(convert(content, number), encoding="utf-8")

    appendices = text.split("# Phụ lục A.", 1)
    if len(appendices) == 2:
        appendix_source = "# Phụ lục A." + appendices[1]
        (OUT / "appendices.tex").write_text(convert(appendix_source.splitlines(), None), encoding="utf-8")


if __name__ == "__main__":
    main()
