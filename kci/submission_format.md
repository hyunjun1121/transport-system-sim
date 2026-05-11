# KCI Submission Format Specification — 한국군사학논집

**Source documents:** `kci/학회_관련_정보/` (학회논문투고 규정.txt, 한국군사학논집 논문접수 첨부서류 안내.txt, 한국군사학논집 논문투고 수시 변경안내.txt, 한국군사학논집 논문편집양식.hwp, 논문_투고시_제출정보.txt).
**Extraction method:** HWP→HWPX conversion via `hwpx` skill (Workflow H), then text + structural analysis (Workflow E + analyze_template).
**Last updated:** 2026-05-11.
**Document role:** Authoritative format reference for the KCI submission. Bind every layout / typography / submission decision in `plan.md` against this file.

---

## 1. Submission process (one-page summary)

| Item | Spec |
|---|---|
| Journal | 한국군사학논집 (Korean Journal of Military Arts and Science, KJMAS) |
| Publisher | 화랑대연구소 (육군사관학교) |
| KCI status | KCI 등재지, Open Access |
| APC | **None** (no submission, review, or publication fee) |
| Submission portal | JAMS — `https://kjmac.jams.or.kr` |
| Inquiries | `kjmas@kma.ac.kr` (email only, no phone) |
| Publication dates | **Feb 28, Jun 30, Oct 31** (3 issues / year) |
| Submission deadline | **Rolling** (수시 접수). Reviewed submissions assigned to the next nearest issue by `received` date. |
| File format | **HWP only** (`.hwp`, edited via 한컴오피스 한글) |
| Paper length | **≤ 30 pages** (per 투고규정 §2-마-3), in the official 편집양식 |
| Manuscript language | Korean **or** English. If Korean, English title required; if English, Korean title required. |
| English abstract | **≤ 200 words**, must include necessity / results / significance |
| Tables, figures, abstract, references | **All in English**, APA Style citations |
| Body font | **Pretendard** (download: see §6) — using a different font is grounds for desk reject ("양식 불일치") |
| Similarity | KCI 문헌유사도 < 10 % (own-citation overrun adjudicated by editor) |
| Author qualification | First / corresponding author must hold ≥ Master's in field, or Bachelor's + ≥ 3 yrs related experience |
| Resubmission after reject | **Locked for 6 months** ("게재불가 → 6개월 내 재투고 불가") |

### Required attachments (uploaded on JAMS)

1. **Manuscript** (`.hwp`) — anonymized: author identifying info **must** be removed from filename and document body. Filename pattern: `논문 제목.hwp` (no author).
2. **저작권 이양 동의서** (`.jpg`) — handwritten signature, scanned, named `저작권 양도 및 활용 동의서(저자명).jpg`. Includes Open Access + CCL consent.
3. **KCI 문헌유사도 결과** — must be < 10 %. Use the KCI similarity service.
4. **보안성 검토완료 문서** — **REQUIRED for authors at military-affiliated institutions**. The 화랑대연구소 does **not** perform its own security review; if not attached, the submission is rejected at intake. **Important for this study: `ax_01@kma.ac.kr` is a KMA address, so this is mandatory.**
5. ~~논문투고 신청서~~ — **no longer required** (per 변경안내). Author info is entered directly into JAMS.

### Pre-upload self-check (per JAMS instructions)

- Tables, figures, abstract, and references all in English (APA).
- Author name removed from filename and document body.
- Handwritten-signed 저작권 이양 동의서 attached as JPG.
- Co-author info entered in JAMS author section.
- 보안성 검토완료 attached if author is at a military institution.
- Similarity report attached (< 10 %).

---

## 2. Page setup (extracted from 편집양식.hwp `secPr`)

| Item | Value (HWPUNIT) | Value (mm or pt) |
|---|---|---|
| Page size | width 59528 × height 84186 | **A4 portrait (210 × 297 mm)** |
| Top margin | 11338 | **40 mm** |
| Bottom margin | 8503 | **30 mm** |
| Left margin | 8504 | **30 mm** |
| Right margin | 8504 | **30 mm** |
| Header margin | 4252 | 15 mm |
| Footer margin | 4252 | 15 mm |
| Gutter | 2834 | 10 mm (left only) |
| Orientation | portrait | LANDSCAPE=WIDELY (한글 attribute) |
| Page numbering | starts page=0 (i.e., starts at 1 on first content page); BOTH sides |
| Visibility | first-header / footer / page-num / empty-line all shown |
| Grid | none (lineGrid=0, charGrid=0) |

> **Action for `plan.md`:** Use the official `한국군사학논집 논문편집양식.hwp` as the working template (Workflow F: clone-form). Do **not** rebuild the layout from scratch.

---

## 3. Typography (extracted from 편집양식.hwp `charPr` + `paraPr`)

### Fonts present in the template

| Slot | Font name | Use |
|---|---|---|
| `hangul:0` | 본명조R (regular) | (legacy slot, retained for fallback) |
| `hangul:1` | 본명조M (medium) | (legacy slot) |
| `hangul:2` | **Pretendard** | **Primary body + heading font (per 변경안내)** |
| `hangul:3` | 한양태고딕 | (limited) |
| `hangul:4` | 산돌고딕 L | (limited) |
| `hangul:5` | 휴먼명조 | (limited) |
| `hangul:6` | 헤드라인특 | (limited) |

> **Pretendard download:** `https://drive.google.com/file/d/1CZH4j-7-PxfBwi_rpwoJlmwrajt9fzyP/view?usp=drive_link`. If the link fails, request from the editor (kjmas@kma.ac.kr).
>
> **Why Pretendard matters:** the 변경안내 explicitly states *"본문 내용 등 기본 글씨체 Pretendard 준수"*. Submitting in 본명조 or any other font triggers desk reject ("양식 불일치").

### Character styles (Pretendard set, distilled from `charPr` IDs)

| Size | Use observed in template |
|---|---|
| **10 pt** | Body text (Pretendard, black) — dominant size |
| 9 pt | Footnote, table caption, table cell text |
| 11 pt | Sub-heading body, callout |
| 12 pt | (occasional) heading, key terms |
| 13 pt | Sub-section heading; abstract title (#808080 grey variant exists) |
| 14 pt | Section heading variant |
| **15 pt** | Major section title |
| **16 pt** | Top-level chapter title (also rendered as #2E74B5 blue in 본명조M slot for cover-style emphasis) |

### Paragraph styles (`paraPr`)

| Style | Spec |
|---|---|
| **Body** | JUSTIFY, line spacing **160 %** |
| **Body indented** | JUSTIFY, 160 %, left indent 1500 HWPUNIT (≈ 5 mm) |
| **Heading levels** | OUTLINE level 0..7, JUSTIFY 160 %, progressive left indent +1000 HWPUNIT per level (≈ 3.5 mm) |
| Centered (titles, abstract heading) | CENTER, 130–160 % |
| Left (tables, captions) | LEFT, 130–160 %, sometimes with `prev`/`next` spacing |
| Right (e-mail / corresp.) | RIGHT, 110 % (compact) |
| References list | JUSTIFY, 160 %, hanging indent (intent=−1310) |

### Recommended bindings for the manuscript (consolidated)

| Element | Font · Size · Spacing |
|---|---|
| Korean title | Pretendard 16 pt centered, single-line |
| English title | Pretendard 14 pt centered |
| Authors | Pretendard 11 pt centered, Korean(English) format with footnote markers |
| Affiliation | Pretendard 9 pt centered, numbered list |
| Key Words | Pretendard 9 pt, "Key Words" label + comma-separated terms |
| ABSTRACT (English) | Pretendard 10 pt justified, ≤ 200 words |
| Section heading (1, 2, 3...) | Pretendard 13 pt bold-equivalent, OUTLINE level 0 |
| Sub-section (1.1, 1.2...) | Pretendard 12 pt, OUTLINE level 1 |
| Sub-sub-section (1.1.1) | Pretendard 11 pt, OUTLINE level 2 |
| Body text | Pretendard 10 pt JUSTIFY 160 % |
| Footnote | Pretendard 9 pt JUSTIFY |
| Table cell | Pretendard 9 pt or 10 pt LEFT |
| Table caption | Pretendard 9 pt CENTER (English) |
| References | Pretendard 10 pt hanging indent, English / APA |
| Running header | "韓國軍事學論集" (the template uses the Hanja form) |

---

## 4. Document structure (per the template's section0.xml)

The reference manuscript in 편집양식.hwp follows this exact section sequence:

```
[Header bar] 韓國軍事學論集 제00집 제0호 0000년 00월 / DOI: 10.31066/kjmas.0000.00.0.000

[Cover block — first page]
  韓國軍事學論集 제00집 제0호 0000년 00월
  DOI: 10.31066/kjmas.0000.00.0.000
  한국군사학논집  /  Received:  Accepted:  Published:
  Korean Journal of Military Arts and Science

[Title block]
  Korean title
  English title
  Authors:  홍길동(Gildong Hong)¹, 장길산(Gilsan Jang)²*
    1. Affiliation A
    2. Affiliation B
  Key Words
    [English keywords] (5 ± terms, comma-separated)
    [Korean keywords]

[Footnote area — first page bottom]
  * 교신저자: kmajc@kma.ac.kr
  ** 본 연구는 [funding statement] 의 지원을 받아 작성된 논문임.

[ABSTRACT block]
  ABSTRACT
  [English abstract text — ≤ 200 words]

[Body — Korean section structure]
  1. 서론
    1.1. 연구배경 및 목적
    1.2. ...
  2. 선행연구 고찰
    2.1. ...
  3. 연구방법
    3.1. 표본선정 및 자료수집
    3.2. ...
  4. 결과 및 분석
    4.1. ...
  5. 결론
    5.1. 결론
    5.2. 시사점 및 한계

[References section]
  <References>
  1. Author, A. A., & Author, B. B. (Year). Title of the article. Name of the Periodical, volume(issue). #-#. https://doi.org/xxxx
  2. ...

[APA citation guidance block]
  ※ 내주 및 인용 표기(APA Style)
   가. ...
   나. ...
   다. ...
   라. ...
   마. 일반원칙
     1) ... 5)
   라. 세부표기 방법
     1) 본문의 문장 가운데에 인용할 경우(저자를 강조하여 삽입)
     2) 본문의 문장 끝에 인용할 경우(삽입문 마지막에 삽입)
```

> **Action for `plan.md`:** mirror this section sequence. The Korean section headings (`1. 서론`, `1.1. 연구배경 및 목적`, etc.) are mandatory; do not invent alternative numbering.

---

## 5. Author block conventions (verbatim from template)

- **Author line:** `홍길동(Gildong Hong)¹, 장길산(Gilsan Jang)²*` — Korean name + parenthesized English Romanization, superscript affiliation number, asterisk for corresponding author.
- **Affiliation line:** numbered `1.` `2.` etc., one per line, Korean institution name + department.
- **Corresponding author footnote:** `* 교신저자: <email>`.
- **Funding footnote:** `** 본 연구는 [funder] [program-code]의 지원을 받아 작성된 논문임.`. The template example uses *"화랑대연구소 국고학술과제 26-A1234-01"*.
- **Anonymization for submission:** the JAMS pre-upload check requires removing all author identifying info from both filename and document body. The author block above is for the camera-ready / accepted version. **For initial submission**, replace author fields with placeholders or omit, and remove `kjmas@kma.ac.kr`-style identifying signatures.

---

## 6. Citation and reference style (APA, with KJMAS-specific rules)

### Reference list (`<References>`) — entry templates

| Source type | Template (verbatim from 편집양식.hwp) |
|---|---|
| Journal article | `Author, A. A., & Author, B. B. (Year). Title of the article. Name of the Periodical, volume(issue). #-#. https://doi.org/xxxx` |
| Book | `Author, A. A., & Author, B. B. (Copyright Year). Title of the book(7th ed.). Publisher. DOI or URL` |
| Multi-author article | `Author, A. A., Author, B. B., & Author, C. C. (Year). Title of article. Title of Periodical, volume number(issue number), pages. DOI or URL` |
| Online periodical | `Author, A. A., & Author, B. B. (Date of publication). Title of article. Title of Online Periodical, volume number(issue number if available). DOI or URL` |
| Report | `Author, A. A. (Date of publication). Title of work (Report No. xxx). Publisher. DOI or URL` |
| Dissertation / thesis | `Author, A. A. (Year of publication). Title of dissertation [Doctoral dissertation or Master's thesis, Name of Institution Awarding the Degree]. Database Name. URL` |

> **Critical rule (KJMAS-specific):** *"참고문헌 이용 시 인터넷 검색 가능한 자료 및 영문으로 표기 가능한 자료로 인용한다."* — references must be **internet-searchable** and **available in English** wherever possible. Korean-only items and inaccessible theses are discouraged because the journal verifies references during intake.

### In-text citations (APA author-date)

#### A. Author count rules

| Author count | Inline (저자 강조) | End-of-sentence (삽입문 마지막) |
|---|---|---|
| 1 | `Kim(2021)은 ...` | `... (Kim, 2021)` |
| 2 | `Kang & Jeon(2024)는 ...` | `... (Kang & Jeon, 2024)` |
| 3+ | `Park 외(2024)는 ...` (Korean) / `Park, et al.(2024)는 ...` (Western) | `... (Park et al., 2024)` |
| Group / institution | `육군사관학교(2000)는 ...` | `... (Korea Military Academy, 2000)` |

#### B. Page numbers

- For direct quotation or borrowed text, use abbreviation `pp.` and include page numbers: `(Williams, 2000, pp. 145-148)`.

#### C. Translated works

- Cite both original and translated year, with translation page numbers: `(Milton, 2000/2009, pp. 77-80)`.

#### D. Same author multiple works

- Author named once; years comma-separated in chronological order: `(Hong, 2010, 2012)` / `(Hill & Allen, 2009, 2011)`.

#### E. Same year disambiguation

- Append `a`, `b`, `c` in alphabetical order of title: `(Hong, 2010a, 2010b)`.

#### F. Multiple sources in one citation

- Alphabetical order of first author, semicolons between: `(Hong, 2011; Lee, 2009a, 2009b; Park, 2010)`.

#### G. Secondary citation (재인용)

- Original year + colon + secondary source year + "에서 재인용":
  - Inline: `Hong(2009: Heo, 2011에서 재인용)은`
  - End: `(Woolf, 2009: White, 2012에서 재인용)`

---

## 7. Tables and figures

- **All table content (cell labels, captions, headers) must be in English.**
- Table caption observed in template: `Category | Context | Data Collection | concept of sampling` — example column headers in English.
- Table border styling in the template uses thin (0.12 mm) solid borders; outermost-row bottoms are emphasized with 0.4 mm borders. Light-grey shading (`#D9D9D9`) is used for header rows.
- Figure captions in English; if Korean is needed for explanation, place after the English caption in parentheses.
- Numbering: `Table 1`, `Table 2`, `Figure 1`, `Figure 2` (English ordinals; the body text may refer in Korean as 「표 1」, 「그림 1」 if needed).

---

## 8. Submission topic eligibility (per 투고규정 §2-나)

The KCI study fits into category 5 most cleanly:

| # | Category | KCI study fit |
|---|---|---|
| 1 | 국방·군사 정책·제도 | weak — simulation, not policy |
| 2 | 군사전략·군사사상·군사사 | weak |
| 3 | 무기체계 및 장비 | no |
| 4 | 국방·안보 정치·외교 | no |
| 5 | **첨단 과학기술의 군사적 응용** | **strong — IE methodology applied to mobilization transport** |
| 6 | 그 밖의 군사학 관련 분야 | fallback |

> **Recommended positioning sentence** for the cover letter / abstract: *"본 연구는 첨단 산업공학·시뮬레이션 기법(통제실험 설계, censoring-aware metric, Morris 민감도)을 예비군 동원수송체계 평가에 적용한 사례로, 한국군사학논집 §2-나-5의 '첨단 과학기술의 군사적 응용' 분야에 해당한다."*

---

## 9. Constraints derived for `plan.md`

The implementation plan must meet **all** of the following:

1. Manuscript final form is `.hwp` produced from the official 편집양식 template using the `hwpx` skill **Workflow F (clone-form)** — never Workflow A or D for this submission, which would lose the template's tables, table-of-contents structure, font slots, and outline levels.
2. Body font is Pretendard 10 pt, line spacing 160 %, JUSTIFY. Section heading is Pretendard 13 pt OUTLINE level 0.
3. Section headings follow the Korean numbering: `1. 서론 → 1.1. → 1.1.1.` etc.
4. Tables, figures, abstract, references **must be in English** (APA Style).
5. English abstract ≤ 200 words; includes necessity / results / significance.
6. References are internet-searchable, English-titled where possible.
7. Total pages ≤ 30 in the final layout.
8. KCI similarity check must show < 10 %.
9. **Author block, filename, and any identifying string must be removed from the submitted file** (anonymous review).
10. **A 보안성 검토완료 문서 must be obtained from the author's institution before JAMS upload** (mandatory because the corresponding author email `ax_01@kma.ac.kr` is at KMA, a military institution).
11. The 저작권 이양 동의서 must be signed by hand, scanned to JPG, and named per the convention: `저작권 양도 및 활용 동의서(저자명).jpg`.
12. Topic positioning paragraph in the cover letter explicitly invokes 투고규정 §2-나-5.

> **Workflow integration:** When `plan.md` schedules the manuscript-build step, it should reference this file (§2 page setup, §3 typography, §4 structure, §5 author block, §6 citations, §7 tables, §9 constraints) rather than re-deriving the rules. Bind the `hwpx` skill's `clone_form.py` against `kci/학회_관련_정보/한국군사학논집 논문편집양식.hwp` (the original `.hwp`, not the converted `.hwpx`, since the journal accepts `.hwp` only).

---

## 10. Open items not resolved by the format documents

These need separate resolution before submission and are tracked in `kci/agents.md` §8:

- **Author and affiliation fields** (decision #12). The template's example reads `홍길동(Gildong Hong) — 한국국방연구원` and `장길산(Gilsan Jang) — 육군사관학교 경제법학과`. The actual author / affiliation for this submission must be confirmed by the user.
- **Funding statement** (the `**` footnote). The template example *"화랑대연구소 국고학술과제 26-A1234-01"* is illustrative; the real funding statement (or "본 연구는 별도 외부지원을 받지 않은 저자 자체연구임") must be provided by the user.
- **DOI block** (`DOI: 10.31066/kjmas.0000.00.0.000`) is filled by the editor at acceptance — leave the placeholder in the submitted file.
- **Korean and English titles** — finalize both at draft freeze using the working titles in `kci/research_plan.md` §1.
- **Keyword sets** — 5 English + 5 Korean keywords, finalized at draft freeze.
- **English abstract** — produced from the Korean abstract, ≤ 200 words, must include necessity / results / significance per 투고규정 §2-마-2.

---

## 11. References to other `kci/` documents

| Question | Document |
|---|---|
| Why this study? What is the research question? | `kci/research_plan.md` §3 |
| Which upstream files do we reuse? | `kci/repo_assets_audit.md` |
| What are the binding constraints (military framing, virtual corridor, IE positioning)? | `kci/agents.md` §2, §6 |
| What decisions are already locked? | `kci/agents.md` §7 |
| What is still open? | `kci/agents.md` §8 + this file §10 |
| How will the implementation actually run? | `kci/plan.md` (to be authored next) |
