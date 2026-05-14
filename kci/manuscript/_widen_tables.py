"""Widen pandoc-generated docx tables to fit page width.

Pandoc emits tables with auto-width and narrow grid widths; LibreOffice then
renders them with extreme cell wrapping. Force each table to span 100% of
the printable width and balance column widths.
"""
import sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm

DOCX = Path(sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\User\Downloads\transport-system-sim\kci\manuscript\manuscript_submission.docx')

doc = Document(str(DOCX))
section = doc.sections[0]
# printable width in twips: page_width - left_margin - right_margin
page_w_emu = section.page_width
left_m_emu = section.left_margin
right_m_emu = section.right_margin
print_w_emu = page_w_emu - left_m_emu - right_m_emu
# Convert EMU to twips (1 inch = 914400 EMU = 1440 twips, so 1 twip = 635 EMU)
print_w_twips = int(print_w_emu / 635)
print(f'Page printable width: {print_w_twips} twips ({print_w_twips/567:.1f} cm)')

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

for i, tbl in enumerate(doc.tables):
    n_cols = len(tbl.columns)
    table_xml = tbl._tbl
    # 1. tblW: set to fixed 100% of printable width
    tblPr = table_xml.find(f'{W}tblPr')
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        table_xml.insert(0, tblPr)
    tblW = tblPr.find(f'{W}tblW')
    if tblW is None:
        tblW = OxmlElement('w:tblW')
        tblPr.append(tblW)
    tblW.set(qn('w:type'), 'dxa')
    tblW.set(qn('w:w'), str(print_w_twips))

    # 2. tblLayout: fixed
    tblLayout = tblPr.find(f'{W}tblLayout')
    if tblLayout is None:
        tblLayout = OxmlElement('w:tblLayout')
        tblPr.append(tblLayout)
    tblLayout.set(qn('w:type'), 'fixed')

    # 3. tblGrid: distribute evenly across columns
    col_w = print_w_twips // n_cols
    tblGrid = table_xml.find(f'{W}tblGrid')
    if tblGrid is not None:
        for elem in list(tblGrid):
            tblGrid.remove(elem)
        for _ in range(n_cols):
            g = OxmlElement('w:gridCol')
            g.set(qn('w:w'), str(col_w))
            tblGrid.append(g)

    # 4. Set each cell width explicitly
    for row in table_xml.findall(f'{W}tr'):
        for cell in row.findall(f'{W}tc'):
            tcPr = cell.find(f'{W}tcPr')
            if tcPr is None:
                tcPr = OxmlElement('w:tcPr')
                cell.insert(0, tcPr)
            tcW = tcPr.find(f'{W}tcW')
            if tcW is None:
                tcW = OxmlElement('w:tcW')
                tcPr.append(tcW)
            tcW.set(qn('w:type'), 'dxa')
            tcW.set(qn('w:w'), str(col_w))

    print(f'Table {i}: cols={n_cols}, per-col={col_w} twips ({col_w/567:.2f}cm)')

doc.save(str(DOCX))
print(f'Saved: {DOCX}')
