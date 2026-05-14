"""Build a reference.docx for pandoc with KCI-template-like layout:
- A4 page size
- Narrow margins (20mm)
- 10pt body
- 2-column body (typical Korean academic journal)
- Pretendard or Malgun Gothic CJK fallback
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
section = doc.sections[0]
section.page_height = Cm(29.7)
section.page_width = Cm(21.0)
section.top_margin = Cm(1.8)
section.bottom_margin = Cm(1.8)
section.left_margin = Cm(1.8)
section.right_margin = Cm(1.8)

# 1-column layout — tables need full width
# Set default body font 9.5pt with CJK fallback
styles = doc.styles
normal = styles['Normal']
normal.font.name = 'Pretendard'
normal.font.size = Pt(9.5)

# Add East Asia font fallback
rpr = normal.element.get_or_add_rPr()
rfonts = rpr.find(qn('w:rFonts'))
if rfonts is None:
    rfonts = OxmlElement('w:rFonts')
    rpr.append(rfonts)
rfonts.set(qn('w:ascii'), 'Pretendard')
rfonts.set(qn('w:hAnsi'), 'Pretendard')
rfonts.set(qn('w:eastAsia'), 'Malgun Gothic')

# Set paragraph spacing tight
pPr = normal.element.get_or_add_pPr()
spacing = pPr.find(qn('w:spacing'))
if spacing is None:
    spacing = OxmlElement('w:spacing')
    pPr.append(spacing)
spacing.set(qn('w:before'), '20')   # 1pt before
spacing.set(qn('w:after'), '20')    # 1pt after
spacing.set(qn('w:line'), '240')    # 1.0x line
spacing.set(qn('w:lineRule'), 'auto')

# Smaller heading sizes
for name, size_pt in [('Heading 1', 13), ('Heading 2', 11), ('Heading 3', 10), ('Heading 4', 9.5)]:
    s = styles[name]
    s.font.name = 'Pretendard'
    s.font.size = Pt(size_pt)
    rpr2 = s.element.get_or_add_rPr()
    rf = rpr2.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rpr2.append(rf)
    rf.set(qn('w:ascii'), 'Pretendard')
    rf.set(qn('w:hAnsi'), 'Pretendard')
    rf.set(qn('w:eastAsia'), 'Malgun Gothic')

# Save - need to add at least one paragraph for valid docx
doc.add_paragraph(' ')

import os
out = r'C:\Users\User\Downloads\transport-system-sim\kci\manuscript\reference_kci.docx'
doc.save(out)
print(f'Wrote {out} ({os.path.getsize(out):,} bytes)')
