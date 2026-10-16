"""PDF -> 고품질 OCR 보고서 보조 스크립트.

용도: 원본(텍스트 PDF 또는 스캔 PDF)에서
  1) 페이지별 텍스트를 텍스트값으로 추출하고,
  2) 내장 그림/사진을 images/FIG-##.png 로 무손실 추출한다.

사용:
    .\\.venv\\Scripts\\python _workspace\\2026-09-18-pdf1-ocr\\extract_pdf_report.py --pdf <원본PDF> --out _workspace\\2026-09-18-pdf1-ocr

필요 패키지: pymupdf (없으면 `pip install pymupdf` 후 재실행)
스캔 PDF(텍스트층 없음)인 경우: 텍스트 추출량이 0에 가까우면
  Tesseract(`pip install pytesseract` + 한국어 traineddata) 또는
  PaddleOCR 스킬(smart-ocr / ocr-document-processor)로 OCR 후 본 스크립트 재실행.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="PDF 텍스트/그림 추출")
    ap.add_argument("--pdf", required=True, help="원본 PDF 경로")
    ap.add_argument("--out", required=True, help="출력 루트 (images/ 하위 생성)")
    ap.add_argument("--min-text-chars", type=int, default=50,
                    help="페이지당 이 문자 수 미만이면 스캔 PDF로 판정(기본 50)")
    args = ap.parse_args()

    try:
        import fitz  # pymupdf
    except ImportError:
        print("ERROR: pymupdf가 없습니다. `.\\.venv\\Scripts\\python -m pip install pymupdf` 후 재실행하세요.",
              file=sys.stderr)
        return 2

    pdf = Path(args.pdf)
    out = Path(args.out)
    imgdir = out / "images"
    imgdir.mkdir(parents=True, exist_ok=True)
    if not pdf.exists():
        print(f"ERROR: PDF 없음: {pdf}", file=sys.stderr)
        return 2

    doc = fitz.open(pdf)
    text_path = out / (pdf.stem + "_extracted_text.txt")
    fig_count = 0
    scan_pages: list[int] = []
    with open(text_path, "w", encoding="utf-8") as fw:
        for i, page in enumerate(doc):
            t = page.get_text("text") or ""
            fw.write(f"\n===== PAGE {i + 1} =====\n{t}")
            if len(t.strip()) < args.min_text_chars:
                scan_pages.append(i + 1)
            for xref, *_ in page.get_images(full=True):
                fig_count += 1
                pix = fitz.Pixmap(doc, xref)
                name = imgdir / f"FIG-{fig_count:02d}_p{i + 1}.png"
                if pix.n - pix.alpha > 3:  # CMYK 등 변환
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save(name)
    print(f"pages={len(doc)} figures={fig_count} text={text_path}")
    if scan_pages:
        print(f"WARN: 텍스트층이 빈약한 페이지(스캔 추정): {scan_pages}")
        print("-> Tesseract/PaddleOCR로 OCR 후 텍스트값을 확정하세요.")
    else:
        print("OK: 텍스트층 정상. 추출 텍스트를 pdf1_ocr_report.md와 대조하세요.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
