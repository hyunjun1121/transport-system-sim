#!/usr/bin/env python3
"""
Generate a professionally formatted .docx file from a markdown-like input file.
Uses only Python standard library (zipfile, xml, re, os) -- no python-docx.
Designed for Android Termux.
"""

import zipfile
import re
import os
import sys
import xml.etree.ElementTree as ET

# ── Configuration ──────────────────────────────────────────────────────
INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_draft.md")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.docx")

# OOXML namespaces
NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"

# CM to TWIPs conversion (1 cm = 567 twips)
CM_TO_TWIPS = 567


# ── XML helpers ────────────────────────────────────────────────────────
def _w(tag):
    """Return a namespaced tag for wordprocessingml."""
    return f"{{{NS_W}}}{tag}"


def _r(tag):
    """Return a namespaced tag for relationships."""
    return f"{{{NS_R}}}{tag}"


def make_element(tag, attribs=None, text=None):
    """Create an Element with optional attributes and text."""
    el = ET.Element(tag, attribs or {})
    if text is not None:
        el.text = text
    return el


def make_sub(parent, tag, attribs=None, text=None):
    """Create a sub-element with optional attributes and text."""
    el = ET.SubElement(parent, tag, attribs or {})
    if text is not None:
        el.text = text
    return el


# ── OOXML content generators ──────────────────────────────────────────
def build_content_types():
    """Build [Content_Types].xml."""
    root = make_element(f"{{{NS_CT}}}Types")
    make_sub(root, f"{{{NS_CT}}}Default",
             {"Extension": "rels",
              "ContentType": "application/vnd.openxmlformats-package.relationships+xml"})
    make_sub(root, f"{{{NS_CT}}}Default",
             {"Extension": "xml",
              "ContentType": "application/xml"})
    make_sub(root, f"{{{NS_CT}}}Override",
             {"PartName": "/word/document.xml",
              "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"})
    make_sub(root, f"{{{NS_CT}}}Override",
             {"PartName": "/word/styles.xml",
              "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"})
    return root


def build_rels():
    """Build _rels/.rels."""
    root = make_element(f"{{{NS_REL}}}Relationships")
    make_sub(root, f"{{{NS_REL}}}Relationship",
             {"Id": "rId1",
              "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument",
              "Target": "word/document.xml"})
    return root


def build_document_rels():
    """Build word/_rels/document.xml.rels."""
    root = make_element(f"{{{NS_REL}}}Relationships")
    make_sub(root, f"{{{NS_REL}}}Relationship",
             {"Id": "rId1",
              "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles",
              "Target": "styles.xml"})
    return root


# ── Run (text segment) builder ────────────────────────────────────────
def make_run(text, bold=False, font_size=None, color=None, font_name="Malgun Gothic"):
    """Create a <w:r> element with optional formatting."""
    run = make_element(_w("r"))
    rpr = make_sub(run, _w("rPr"))

    if font_name:
        rfonts = make_sub(rpr, _w("rFonts"),
                          {"ascii": font_name,
                           "hAnsi": font_name,
                           "eastAsia": font_name,
                           "cs": font_name})
    if bold:
        make_sub(rpr, _w("b"))
        make_sub(rpr, _w("bCs"))
    if font_size:
        make_sub(rpr, _w("sz"), {"val": str(font_size * 2)})       # half-points
        make_sub(rpr, _w("szCs"), {"val": str(font_size * 2)})
    if color:
        make_sub(rpr, _w("color"), {"val": color})

    t = make_sub(run, _w("t"))
    t.text = text
    if text and (text[0] == " " or text[-1] == " "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return run


# ── Paragraph builder ─────────────────────────────────────────────────
def make_paragraph(runs, style=None, ppr_extra=None):
    """Create a <w:p> element from a list of runs."""
    p = make_element(_w("p"))
    if style or ppr_extra:
        ppr = make_sub(p, _w("pPr"))
        if style:
            make_sub(ppr, _w("pStyle"), {"val": style})
        if ppr_extra:
            ppr.extend(ppr_extra)
    for run in runs:
        p.append(run)
    return p


# ── Inline bold parser ────────────────────────────────────────────────
def parse_inline_bold(text, font_size=None, color=None):
    """Parse **bold** segments within text, returning a list of runs."""
    runs = []
    pattern = re.compile(r"\*\*(.+?)\*\*")
    last = 0
    for m in pattern.finditer(text):
        if m.start() > last:
            runs.append(make_run(text[last:m.start()],
                                 font_size=font_size, color=color))
        runs.append(make_run(m.group(1), bold=True,
                             font_size=font_size, color=color))
        last = m.end()
    if last < len(text):
        runs.append(make_run(text[last:], font_size=font_size, color=color))
    return runs


# ── Table builder ─────────────────────────────────────────────────────
def make_table(rows):
    """Build a <w:tbl> from a list of row-lists (first row = header)."""
    tbl = make_element(_w("tbl"))

    # Table properties
    tblpr = make_sub(tbl, _w("tblPr"))
    make_sub(tblpr, _w("tblStyle"), {"val": "TableGrid"})
    make_sub(tblpr, _w("tblW"), {"w": "0", "type": "auto"})

    # Table borders
    tblborders = make_sub(tblpr, _w("tblBorders"))
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        make_sub(tblborders, _w(edge),
                 {"val": "single", "sz": "4", "space": "0", "color": "999999"})

    # Table grid (column definitions) -- equal width columns
    ncols = max(len(r) for r in rows) if rows else 0
    tblgrid = make_sub(tbl, _w("tblGrid"))
    for _ in range(ncols):
        make_sub(tblgrid, _w("gridCol"), {"w": "2400"})

    for i, row in enumerate(rows):
        tr = make_sub(tbl, _w("tr"))

        # Header row shading
        if i == 0:
            trpr = make_sub(tr, _w("trPr"))
            make_sub(trpr, _w("tblHeader"))

        for cell_text in row:
            tc = make_sub(tr, _w("tc"))

            # Header cell shading
            if i == 0:
                tcpr = make_sub(tc, _w("tcPr"))
                shd = make_sub(tcpr, _w("shd"),
                               {"val": "clear", "color": "auto",
                                "fill": "1F3864"})
                # White text for header
                cell_runs = parse_inline_bold(cell_text.strip(), color="FFFFFF")
                # Force bold for header
                for cr in cell_runs:
                    rpr = cr.find(_w("rPr"))
                    if rpr is None:
                        rpr = make_sub(cr, _w("rPr"))
                        cr.insert(0, rpr)
                    make_sub(rpr, _w("b"))
                    make_sub(rpr, _w("bCs"))
                    # Also set color in case not set
                    existing_color = rpr.find(_w("color"))
                    if existing_color is None:
                        make_sub(rpr, _w("color"), {"val": "FFFFFF"})
                p = make_paragraph(cell_runs)
                ppr = p.find(_w("pPr"))
                if ppr is None:
                    ppr = make_sub(p, _w("pPr"))
                    p.insert(0, ppr)
                jc = make_sub(ppr, _w("jc"), {"val": "center"})
            else:
                cell_runs = parse_inline_bold(cell_text.strip())
                p = make_paragraph(cell_runs)

            tc.append(p)

    return tbl


# ── Styles builder ────────────────────────────────────────────────────
def build_styles():
    """Build word/styles.xml with heading and body styles."""
    root = make_element(_w("styles"))

    # ── Default paragraph style ──
    docdefault = make_sub(root, _w("docDefaults"))
    rprdefault = make_sub(docdefault, _w("rPrDefault"))
    rpr = make_sub(rprdefault, _w("rPr"))
    rfonts = make_sub(rpr, _w("rFonts"),
                      {"ascii": "Malgun Gothic",
                       "hAnsi": "Malgun Gothic",
                       "eastAsia": "Malgun Gothic",
                       "cs": "Batang",
                       "asciiTheme": "minorHAnsi",
                       "eastAsiaTheme": "minorEastAsia"})
    make_sub(rpr, _w("sz"), {"val": "22"})  # 11pt in half-points
    make_sub(rpr, _w("szCs"), {"val": "22"})
    lang = make_sub(rpr, _w("lang"),
                    {"val": "ko-KR", "eastAsia": "ko-KR", "bidi": "ko-KR"})

    pprdefault = make_sub(docdefault, _w("pPrDefault"))
    ppr2 = make_sub(pprdefault, _w("pPr"))
    spacing = make_sub(ppr2, _w("spacing"),
                       {"after": "200", "line": "276", "lineRule": "auto"})

    # ── Normal style ──
    normal = make_sub(root, _w("style"),
                      {"type": "paragraph", "styleId": "Normal"})
    make_sub(normal, _w("name"), {"val": "Normal"})
    make_sub(normal, _w("qFormat"))
    npr = make_sub(normal, _w("pPr"))
    make_sub(npr, _w("spacing"),
             {"after": "160", "line": "276", "lineRule": "auto"})
    nrpr = make_sub(normal, _w("rPr"))
    make_sub(nrpr, _w("sz"), {"val": "22"})
    make_sub(nrpr, _w("szCs"), {"val": "22"})

    # ── Heading 1 ──
    h1 = make_sub(root, _w("style"),
                  {"type": "paragraph", "styleId": "Heading1"})
    make_sub(h1, _w("name"), {"val": "heading 1"})
    make_sub(h1, _w("basedOn"), {"val": "Normal"})
    make_sub(h1, _w("next"), {"val": "Normal"})
    make_sub(h1, _w("qFormat"))
    h1ppr = make_sub(h1, _w("pPr"))
    make_sub(h1ppr, _w("keepNext"), {})
    make_sub(h1ppr, _w("keepLines"), {})
    make_sub(h1ppr, _w("spacing"),
             {"before": "480", "after": "200"})
    h1rpr = make_sub(h1, _w("rPr"))
    make_sub(h1rpr, _w("rFonts"),
             {"ascii": "Malgun Gothic", "hAnsi": "Malgun Gothic",
              "eastAsia": "Malgun Gothic", "cs": "Batang"})
    make_sub(h1rpr, _w("b"))
    make_sub(h1rpr, _w("bCs"))
    make_sub(h1rpr, _w("color"), {"val": "1F3864"})
    make_sub(h1rpr, _w("sz"), {"val": "36"})   # 18pt
    make_sub(h1rpr, _w("szCs"), {"val": "36"})

    # ── Heading 2 ──
    h2 = make_sub(root, _w("style"),
                  {"type": "paragraph", "styleId": "Heading2"})
    make_sub(h2, _w("name"), {"val": "heading 2"})
    make_sub(h2, _w("basedOn"), {"val": "Normal"})
    make_sub(h2, _w("next"), {"val": "Normal"})
    make_sub(h2, _w("qFormat"))
    h2ppr = make_sub(h2, _w("pPr"))
    make_sub(h2ppr, _w("keepNext"))
    make_sub(h2ppr, _w("keepLines"))
    make_sub(h2ppr, _w("spacing"),
             {"before": "360", "after": "160"})
    h2rpr = make_sub(h2, _w("rPr"))
    make_sub(h2rpr, _w("rFonts"),
             {"ascii": "Malgun Gothic", "hAnsi": "Malgun Gothic",
              "eastAsia": "Malgun Gothic", "cs": "Batang"})
    make_sub(h2rpr, _w("b"))
    make_sub(h2rpr, _w("bCs"))
    make_sub(h2rpr, _w("color"), {"val": "2E5090"})
    make_sub(h2rpr, _w("sz"), {"val": "28"})   # 14pt
    make_sub(h2rpr, _w("szCs"), {"val": "28"})

    # ── Heading 3 ──
    h3 = make_sub(root, _w("style"),
                  {"type": "paragraph", "styleId": "Heading3"})
    make_sub(h3, _w("name"), {"val": "heading 3"})
    make_sub(h3, _w("basedOn"), {"val": "Normal"})
    make_sub(h3, _w("next"), {"val": "Normal"})
    make_sub(h3, _w("qFormat"))
    h3ppr = make_sub(h3, _w("pPr"))
    make_sub(h3ppr, _w("keepNext"))
    make_sub(h3ppr, _w("keepLines"))
    make_sub(h3ppr, _w("spacing"),
             {"before": "240", "after": "120"})
    h3rpr = make_sub(h3, _w("rPr"))
    make_sub(h3rpr, _w("rFonts"),
             {"ascii": "Malgun Gothic", "hAnsi": "Malgun Gothic",
              "eastAsia": "Malgun Gothic", "cs": "Batang"})
    make_sub(h3rpr, _w("b"))
    make_sub(h3rpr, _w("bCs"))
    make_sub(h3rpr, _w("sz"), {"val": "24"})   # 12pt
    make_sub(h3rpr, _w("szCs"), {"val": "24"})

    # ── ListParagraph style (for bullet points) ──
    lp = make_sub(root, _w("style"),
                  {"type": "paragraph", "styleId": "ListParagraph"})
    make_sub(lp, _w("name"), {"val": "List Paragraph"})
    make_sub(lp, _w("basedOn"), {"val": "Normal"})
    make_sub(lp, _w("qFormat"))
    lpppr = make_sub(lp, _w("pPr"))
    make_sub(lpppr, _w("ind"), {"left": "720", "hanging": "360"})

    return root


# ── Document builder ──────────────────────────────────────────────────
def build_document(blocks):
    """Build word/document.xml from parsed content blocks."""
    doc = make_element(_w("document"))
    body = make_sub(doc, _w("body"))

    # ── Page setup (sectPr in body) ──
    # We'll add sectPr at the end

    for block in blocks:
        btype = block["type"]

        if btype == "heading":
            level = block["level"]
            style = f"Heading{level}"
            color_map = {1: "1F3864", 2: "2E5090", 3: "000000"}
            size_map = {1: 18, 2: 14, 3: 12}
            runs = parse_inline_bold(
                block["text"],
                font_size=size_map.get(level),
                color=color_map.get(level)
            )
            body.append(make_paragraph(runs, style=style))

        elif btype == "paragraph":
            runs = parse_inline_bold(block["text"])
            body.append(make_paragraph(runs))

        elif btype == "bullet":
            ppr_extra = []
            ind = make_element(_w("ind"),
                               {"left": "720", "hanging": "360"})
            ppr_extra.append(ind)
            # Bullet character as a run
            bullet_run = make_run("\u2022 ", font_size=11)
            runs = [bullet_run] + parse_inline_bold(block["text"])
            body.append(make_paragraph(runs, ppr_extra=ppr_extra))

        elif btype == "table":
            body.append(make_table(block["rows"]))

        elif btype == "blank":
            body.append(make_paragraph([make_run("")]))

    # Section properties
    sectpr = make_sub(body, _w("sectPr"))
    pgmar = make_sub(sectpr, _w("pgMar"),
                     {"top": str(int(2.54 * CM_TO_TWIPS)),
                      "right": str(int(2.54 * CM_TO_TWIPS)),
                      "bottom": str(int(2.54 * CM_TO_TWIPS)),
                      "left": str(int(2.54 * CM_TO_TWIPS)),
                      "header": "720",
                      "footer": "720",
                      "gutter": "0"})
    pgsz = make_sub(sectpr, _w("pgSz"),
                    {"w": str(int(21.0 * CM_TO_TWIPS)),
                     "h": str(int(29.7 * CM_TO_TWIPS))})  # A4

    return doc


# ── Markdown parser ───────────────────────────────────────────────────
def parse_markdown(text):
    """Parse markdown text into structured blocks."""
    blocks = []
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Blank line
        if not stripped:
            blocks.append({"type": "blank"})
            i += 1
            continue

        # Heading
        hmatch = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if hmatch:
            level = len(hmatch.group(1))
            if level > 3:
                level = 3
            blocks.append({"type": "heading", "level": level,
                           "text": hmatch.group(2)})
            i += 1
            continue

        # Table
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            # Parse table rows, skip separator row
            rows = []
            for tl in table_lines:
                cells = [c.strip() for c in tl.split("|")[1:-1]]
                # Detect separator row (all dashes/colons)
                if all(re.match(r"^[-:]+$", c) for c in cells):
                    continue
                rows.append(cells)
            if rows:
                blocks.append({"type": "table", "rows": rows})
            continue

        # Bullet point
        if re.match(r"^[-*+]\s+", stripped):
            bullet_text = re.sub(r"^[-*+]\s+", "", stripped)
            blocks.append({"type": "bullet", "text": bullet_text})
            i += 1
            continue

        # Regular paragraph -- collect consecutive non-special lines
        para_lines = []
        while i < len(lines):
            ln = lines[i].strip()
            if not ln or ln.startswith("#") or ln.startswith("|") or re.match(r"^[-*+]\s+", ln):
                break
            para_lines.append(ln)
            i += 1
        if para_lines:
            blocks.append({"type": "paragraph", "text": " ".join(para_lines)})

    return blocks


# ── XML serialization helper ──────────────────────────────────────────
def xml_to_bytes(root):
    """Serialize an ElementTree element to a UTF-8 XML byte string."""
    ET.register_namespace("w", NS_W)
    ET.register_namespace("r", NS_R)
    ET.register_namespace("", NS_REL)
    ET.register_namespace("", NS_CT)
    tree = ET.ElementTree(root)
    import io
    buf = io.BytesIO()
    tree.write(buf, encoding="UTF-8", xml_declaration=True)
    return buf.getvalue()


# ── Main ──────────────────────────────────────────────────────────────
def main():
    # Check input file
    if not os.path.exists(INPUT_FILE):
        print(f"Warning: Input file not found: {INPUT_FILE}")
        print("Creating a sample report_draft.md for testing...")
        sample = """# 교통 시스템 시뮬레이션 보고서

## 1. 서론

본 보고서는 **교통 시스템 시뮬레이션** 프로젝트의 결과를 정리한 문서입니다.

### 1.1 목적

시뮬레이션 모델의 **정확성**과 **실효성**을 검증합니다.

## 2. 시뮬레이션 결과

| 항목 | 값 | 단위 |
|------|------|------|
| 평균 속도 | 45.2 | km/h |
| 지연 시간 | 12.3 | 분 |
| 통행량 | 1,500 | 대/시 |

### 2.1 주요 발견사항

- 대중교통 이용률이 15% 증가했습니다
- **혼잡도**가 출퇴근 시간에 최대에 도달합니다
- 신호등 최적화로 **평균 대기시간**이 20% 감소했습니다

## 3. 결론

시뮬레이션 결과는 실제 교통 패턴과 **높은 상관관계**를 보였습니다.
"""
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            f.write(sample)
        print(f"Created sample: {INPUT_FILE}")

    # Read input
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        md_text = f.read()

    print(f"Parsing markdown from: {INPUT_FILE}")
    blocks = parse_markdown(md_text)
    print(f"  Found {len(blocks)} content blocks")

    # Build OOXML parts
    content_types = build_content_types()
    rels = build_rels()
    doc_rels = build_document_rels()
    styles = build_styles()
    document = build_document(blocks)

    # Write .docx (ZIP)
    print(f"Writing: {OUTPUT_FILE}")
    with zipfile.ZipFile(OUTPUT_FILE, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", xml_to_bytes(content_types))
        zf.writestr("_rels/.rels", xml_to_bytes(rels))
        zf.writestr("word/_rels/document.xml.rels", xml_to_bytes(doc_rels))
        zf.writestr("word/styles.xml", xml_to_bytes(styles))
        zf.writestr("word/document.xml", xml_to_bytes(document))

    fsize = os.path.getsize(OUTPUT_FILE)
    print(f"Done! Generated {OUTPUT_FILE} ({fsize:,} bytes)")


if __name__ == "__main__":
    main()
