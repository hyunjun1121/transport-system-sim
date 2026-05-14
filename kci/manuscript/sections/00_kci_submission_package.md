# T7.0 KCI 한국군사학논집 제출 패키지 — Audit-of-record

**Date.** 2026-05-14
**Branch.** main @ HEAD
**Verdict.** **READY** (single follow-up required from author — see §6).

## 1. 제출 산출물 (Submission artifacts)

| File | Purpose |
|---|---|
| `manuscript/manuscript_submission_draft.md` | Single source-of-truth markdown (Korean body + English title/keywords/abstract + APA-format references; tables and figures all English-labeled) |
| `manuscript/manuscript_submission.hwpx` | HWPX version generated via md2hwpx.py (report template) |
| `manuscript/manuscript_submission.docx` | DOCX version generated via pandoc + reference_kci.docx |
| `manuscript/manuscript_submission.pdf` | PDF version generated via LibreOffice (page-count proxy: **18 pages** under 30-page cap) |
| `manuscript/pdf_pages/page_NN.png` | Per-page PNG renders for visual verification |
| `manuscript/table_images/tableN.png` | Matplotlib-rendered tables (replaces markdown pipe tables for layout robustness) |
| `manuscript/reference_kci.docx` | Reference docx with Pretendard 9.5pt, A4, 1.8cm margins (mirrors KCI editorial template) |

## 2. KCI 편집 규정 정합성 체크

| # | 규정 | 본 패키지 상태 | OK |
|---|---|---|---|
| 1 | 30페이지 이내 | 18 페이지 (PDF 렌더링) | ✓ |
| 2 | 한글파일(.hwp) 제출 | `.hwpx` 제공 — JAMS 업로드 시 한컴 한글에서 1회 열어 `.hwp`로 다시 저장 권장 | △ |
| 3 | 표·그림·초록·참고문헌 모두 영문(APA) | Tables 2/3/4/5/6 모두 영문 / Figures 1/2/3/4/6 영문 캡션 + 영문 라벨 / Abstract 영문 169 words / References APA | ✓ |
| 4 | 본문 글꼴 Pretandard | reference_kci.docx에 Pretendard ascii + Malgun Gothic CJK 적용 | ✓ |
| 5 | 영문 초록 ≤ 200 단어, 필요성·결과·의의 포함 | 169 단어 | ✓ |
| 6 | 한글 논문 → 영문 제목 추가 | Page 1 상단에 English title + English keywords 명시 | ✓ |
| 7 | 저자정보 삭제 | 본문 내 저자명·소속 부재 (anonymous) | ✓ |
| 8 | KCI 문헌유사도 < 10% | 미검사 — 저자가 JAMS에서 수행 필요 | △ |
| 9 | 군 관련 기관 저자 → 보안성 검토 | 육사 소속(ax_01@kma.ac.kr) — 별도 절차 필요 | △ |
| 10 | 저작권 이양 동의서 자필서명 | 양식 보존 `학회_관련_정보/저작권 이양 동의서(양식).hwp` | — |
| 11 | 분야 적합성 (첨단 과학기술의 군사적 응용) | 본 연구 해당 | ✓ |

## 3. 내용 정합성 체크 (G1–G5)

| Gate | 기준 | 결과 |
|---|---|---|
| G1 | Phase-1a R = 30 paired CRN | `results/phase1a_origin_A.csv` 30 reps × 8 levels = 240 rows ✓ |
| G2 | Phase-3 grid 3×3×3×3 × R_phase3=15 | 81 cells × 15 = 1,215 rows ✓ |
| G3 | Sign convention `Δ = bus_only − multimodal` | 10/0 (correct/wrong) ✓ |
| G4 | ≤ 10 main assets | 5 figures (1, 2, 3, 4, 6) + 5 tables (2, 3, 4, 5, 6) = 10 ✓ |
| G5 | KOR body ≥ 6,000 chars | 11,920 ✓ |

## 4. 헤드라인 수치 검증 (Canonical ledger)

| # | Claim | Value | Source |
|---|---|---|---|
| 1 | Phase 1a Δ penalized_makespan @ p=0.0 | −58.5 min | `phase1a_origin_A.csv` mean (R=30) |
| 2 | Phase 1a Δ P(complete ≤ 1500) @ p=2.0 | +0.433 [+0.245, +0.622] | `phase1a_origin_A.csv` (R=30) |
| 3 | Phase 3 multi_dominant cells | **0 of 81** (54 bus_dominant / 27 inconclusive) | `table6_lever_conditions_summary.json` |
| 4 | Phase 3 narrowest-gap cell | rail_headway=3, lastmile=23, rail_cap=500, p=0.5 → Δ=−39.3 [−50.7, −28.0] | summary.json::narrowest_gap_cell |
| 5 | Morris top-3 μ* | passenger_volume 44.5, direct_bus_fleet_size 27.4, dispatch_interval 20.8 | `canonical_morris_top3.md`, `morris_summary.csv` |

## 5. 참고문헌 정합성

- Citations 1–25: 모두 본문에서 인용됨 ✓
- References definitions: 모두 25개 정의 ✓
- APA 스타일 적용 ✓

## 6. 저자 후속 조치 (Author follow-ups before JAMS submission)

1. **`.hwpx` → `.hwp` 변환** — JAMS는 `.hwp` 권장. 한컴 한글에서 `manuscript_submission.hwpx`를 열어 "다른 이름으로 저장" → `.hwp` 형식 선택. 또는 한글 2024 이상에서는 `.hwpx`도 직접 업로드 가능.
2. **KCI 문헌유사도 검사** — KCI 사이트의 문헌유사도 검사 서비스에서 본 원고 제출 → 결과 PDF 첨부 (10% 이내).
3. **보안성 검토** — 화랑대연구소 별도 절차 없음. 소속 부대(육사) 보안담당관에 별도 의뢰 후 검토필 문서 첨부.
4. **저작권 이양 동의서** — `학회_관련_정보/저작권 이양 동의서(양식).hwp` 작성 후 자필 서명, 스캔 → `저작권 이양 동의서(저자명).jpg` 로 저장.
5. **JAMS 투고** — https://kjmac.jams.or.kr 로그인 후 (i) 원본 파일 (저자명 삭제 확인), (ii) 동의서 jpg, (iii) 유사도 결과, (iv) 보안성 검토 문서 업로드.

## 7. 분량 검증 방법

`manuscript/_render_pdf.py`는 다음 파이프라인으로 분량을 정확히 측정한다:

1. `pandoc manuscript_submission_draft.md → manuscript_submission.docx` (참조 docx: `reference_kci.docx`, 1-col Pretandard 9.5pt 1.8cm 여백)
2. `_widen_tables.py`: docx 내 표를 100% 폭으로 강제 적용
3. `soffice --headless --convert-to pdf`: docx → PDF
4. `PyMuPDF`: 페이지 수 측정 및 페이지별 PNG 출력

현재 결과: **18 pages** (vs. KCI 30-page cap → PASS, 12-page margin).

## 8. 검증된 페이지 구성

| Page | Content |
|---|---|
| 1 | 제목 (한·영), 키워드 (한·영), 한글 초록 |
| 2–3 | §1 서론 (배경, RQ, 기여, 범위, 구성) |
| 3–4 | §2 문헌 검토 (4단락 통합) |
| 5–8 | §3 방법론 (시뮬레이터, 회랑, 도로 신뢰성, DoE, CRN, Morris, 재현성, 한계) |
| 8–11 | §4 결과 (Phase 1a/1b/2/3 + Morris) |
| 9 | Figure 3 (Phase 1a 강건성 곡선) + Figure 4 (분위·완료 확률) |
| 10 | Table 2 (Phase 1a) |
| 11–12 | Table 4 (원점 강건성), Table 3 (Phase 2) |
| 13 | Figure 6 (Phase 3 lever sweep heatmap) |
| 14 | Table 6 (반사실 셀), Morris top-3 |
| 14 | Table 5 (Morris ranking) |
| 15–16 | §5 결론 (주요 발견, 함의, 한계, 향후 연구) |
| 16–18 | References (APA, 25 entries) + Appendix (보충자료 안내) |

---

**Verdict: READY for JAMS submission after author follow-ups in §6.**
