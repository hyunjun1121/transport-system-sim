"""Render each markdown table block as a PNG via matplotlib.

This bypasses LibreOffice's table-rendering issues with our docx.
"""
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Korean font
preferred = ['Malgun Gothic', 'NanumGothic', 'Pretendard', 'AppleGothic']
installed = {f.name for f in fm.fontManager.ttflist}
chosen = next((c for c in preferred if c in installed), 'DejaVu Sans')
matplotlib.rcParams['font.family'] = chosen
matplotlib.rcParams['axes.unicode_minus'] = False
print(f'Font: {chosen}', file=sys.stderr)

ROOT = Path(r'C:\Users\User\Downloads\transport-system-sim\kci')
MD = ROOT / 'manuscript' / 'manuscript_submission_draft.md'
OUT_DIR = ROOT / 'manuscript' / 'table_images'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_pipe_table(block: str):
    lines = [l for l in block.strip().split('\n') if l.strip().startswith('|')]
    if len(lines) < 2:
        return None, None
    def split_row(s):
        # strip trailing/leading whitespace and pipes
        s = s.strip()
        if s.startswith('|'): s = s[1:]
        if s.endswith('|'): s = s[:-1]
        return [c.strip() for c in s.split('|')]
    header = split_row(lines[0])
    # lines[1] is divider — skip
    data = [split_row(l) for l in lines[2:]]
    # Pad data rows to header length
    n = len(header)
    data = [[(r[i] if i < len(r) else '') for i in range(n)] for r in data]
    return header, data


def render_table(header, data, out_path, title=None):
    n_rows = len(data) + 1
    n_cols = len(header)
    # Compute column widths proportional to max cell length
    max_w = [max(len(str(c)) for c in [header[i]] + [r[i] for r in data]) for i in range(n_cols)]
    total_w = sum(max_w)
    col_ratio = [w / max(1, total_w) for w in max_w]

    fig_w = max(7.0, min(13.0, total_w * 0.10))
    row_h = 0.32
    fig_h = max(1.5, n_rows * row_h + 0.6)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis('off')

    # Replace U+2212 (minus sign) and U+2014 (em-dash) with ASCII for font compat
    def _sanitize(s):
        return str(s).replace('−', '-').replace('—', '--').replace('–', '-')
    cell_text = [[_sanitize(c) for c in row] for row in [header] + data]
    table = ax.table(cellText=cell_text, colWidths=col_ratio, cellLoc='center', loc='upper left')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.2)

    # Style header row
    for j in range(n_cols):
        cell = table[0, j]
        cell.set_facecolor('#e8e8e8')
        cell.set_text_props(weight='bold', fontsize=8)
    # Tighten borders
    for (r, c), cell in table.get_celld().items():
        cell.set_linewidth(0.4)
        cell.set_edgecolor('#444444')

    if title:
        ax.set_title(title, fontsize=9, weight='bold', pad=8, loc='left', wrap=True)

    plt.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'  Wrote {out_path.name} ({out_path.stat().st_size:,} bytes)', file=sys.stderr)


def main():
    text = MD.read_text(encoding='utf-8')

    # Find tables labeled with **Table N.** preceded by 한국 table header
    # Pattern: **Table N.** caption\n\n| ... |\n|---|\n|...|
    pattern = re.compile(
        r'\*\*Table\s+(\d+)\.\s*\*\*\s*([^\n]+)\n+(\|[^\n]+\|\n\|[\-\|\s:]+\|\n(?:\|[^\n]*\|\n?)+)',
        re.MULTILINE,
    )

    replacements = []
    for m in pattern.finditer(text):
        n = int(m.group(1))
        caption = m.group(2).strip()
        table_md = m.group(3)
        header, data = parse_pipe_table(table_md)
        if header is None:
            continue
        out_path = OUT_DIR / f'table{n}.png'
        render_table(header, data, out_path, title=None)
        # Replacement: keep caption, replace table-md with image markdown
        rel = f'table_images/table{n}.png'
        new_block = f'**Table {n}.** {caption}\n\n![Table {n}]({rel})\n'
        replacements.append((m.start(), m.end(), new_block))

    # Apply replacements in reverse order
    new_text = text
    for start, end, new in reversed(replacements):
        new_text = new_text[:start] + new + new_text[end:]

    out_md = ROOT / 'manuscript' / 'manuscript_submission_draft.md'
    out_md.write_text(new_text, encoding='utf-8')
    print(f'Replaced {len(replacements)} tables in {out_md}', file=sys.stderr)
    print(f'New length: {len(new_text)} chars', file=sys.stderr)


if __name__ == '__main__':
    main()
