"""Render manuscript_submission.md → docx → PDF (via pandoc + LibreOffice)
and then PDF → PNG (via PyMuPDF). Reports page count."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PANDOC = r'C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\JohnMacFarlane.Pandoc_Microsoft.Winget.Source_8wekyb3d8bbwe\pandoc-3.9.0.2\pandoc.exe'
SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.com'
ROOT = Path(r'C:\Users\User\Downloads\transport-system-sim\kci')
MD = ROOT / 'manuscript' / 'manuscript_submission_draft.md'
DOCX = ROOT / 'manuscript' / 'manuscript_submission.docx'
ODT = ROOT / 'manuscript' / 'manuscript_submission.odt'
PDF = ROOT / 'manuscript' / 'manuscript_submission.pdf'
PNG_DIR = ROOT / 'manuscript' / 'pdf_pages'

env = os.environ.copy()
env.pop('PYTHONHOME', None)
env.pop('PYTHONPATH', None)


def run(cmd, **kw):
    print('CMD:', ' '.join(repr(c) if ' ' in str(c) else str(c) for c in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=600, **kw)
    print(f'  exit={r.returncode}')
    if r.stdout: print(f'  STDOUT: {r.stdout[:400]}')
    if r.stderr: print(f'  STDERR: {r.stderr[:400]}')
    return r


# Step 1: pandoc md → docx with A4 page size and Korean-aware defaults
print('=== Step 1: pandoc md → docx ===')
REF_DOCX = ROOT / 'manuscript' / 'reference_kci.docx'
r1 = run([
    PANDOC,
    str(MD),
    '-o', str(DOCX),
    '--from=markdown+pipe_tables-implicit_figures',
    '--to=docx',
    f'--reference-doc={REF_DOCX}',
    f'--resource-path={ROOT / "manuscript"}',
])
if not DOCX.exists():
    print('ERROR: docx not produced'); sys.exit(1)
print(f'  DOCX: {DOCX.stat().st_size:,} bytes')

# Widen tables before PDF conversion
print('\n=== Step 1b: widen tables ===')
import subprocess as _sp
_sp.run([sys.executable, str(ROOT / 'manuscript' / '_widen_tables.py'), str(DOCX)], check=True)

# Step 2: LibreOffice docx → PDF
print('\n=== Step 2: soffice docx → PDF ===')
profile = tempfile.mkdtemp(prefix='loprofile_')
profile_uri = 'file:///' + profile.replace('\\', '/')
r2 = run([
    SOFFICE,
    '--headless', '--norestore', '--nologo', '--nodefault', '--nolockcheck',
    f'-env:UserInstallation={profile_uri}',
    '--convert-to', 'pdf',
    '--outdir', str(ROOT / 'manuscript'),
    str(DOCX),
])
if not PDF.exists():
    print('ERROR: PDF not produced'); sys.exit(2)
print(f'  PDF: {PDF.stat().st_size:,} bytes')

# Step 3: PyMuPDF page count & PNG export
print('\n=== Step 3: PDF page count + PNG export ===')
import fitz
doc = fitz.open(str(PDF))
print(f'  PAGES: {doc.page_count}')
PNG_DIR.mkdir(parents=True, exist_ok=True)
# Clear old pngs
for old in PNG_DIR.glob('*.png'): old.unlink()
for i, page in enumerate(doc, start=1):
    pix = page.get_pixmap(dpi=200)
    out = PNG_DIR / f'page_{i:02d}.png'
    pix.save(str(out))
print(f'  Wrote {doc.page_count} PNGs to {PNG_DIR}')

# Step 4: page-by-page byte sizes (proxy for content density)
print('\n=== Step 4: PNG sizes by page ===')
for png in sorted(PNG_DIR.glob('*.png')):
    print(f'  {png.name}: {png.stat().st_size:,} bytes')

print(f'\n=== RESULT: manuscript renders to {doc.page_count} pages ===')
print(f'KCI rule: <= 30 pages. Status: {"PASS" if doc.page_count <= 30 else "FAIL - must trim"}')
