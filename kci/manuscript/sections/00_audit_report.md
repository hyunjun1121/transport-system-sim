# KCI Submission Cross-Reference Audit Report

**Audit date:** 2026-05-11
**Auditor:** Cross-reference audit agent
**Inputs:** `manuscript/figures/`, `manuscript/tables/`, `manuscript/sections/`, `kci/submission_format.md`, `kci/results/sensitivity/morris_summary.csv`
**Scope:** Internal consistency, KCI asset-budget compliance, and parallel-drafted Morris top-3 reconciliation.

---

## 1. Asset Count

| Class | Count | Items |
|---|---|---|
| Figures (PNG) | **4** | figure1_concept, figure3_breakeven_heatmap, figure4_success_vs_disruption, figure5_origin_robustness |
| Tables (.md) | **5** | table1_doe_design, table2_phase1_means_ci, table3_phase2_policy_pareto, table4_origin_robustness, table5_morris_mu_star |
| **TOTAL** | **9** | within KCI ~10 budget |

**Asset budget status:** PASS (9 ≤ 10).

**Note:** `figure2_*` is **absent** on disk. Plan referenced 5 figures; only figures 1, 3, 4, 5 are present. This is reported as a FAIL item below (whether intentional renumbering or missing asset is unclear).

---

## 2. PASS Items

| # | Item | Evidence |
|---|---|---|
| P1 | Figure 1 PNG exists, > 5 KB | 1,102,619 B |
| P2 | Figure 3 PNG exists, > 5 KB | 159,089 B |
| P3 | Figure 4 PNG exists, > 5 KB | 361,501 B |
| P4 | Figure 5 PNG exists, > 5 KB | 167,200 B |
| P5 | Table 1 structure correct | Korean title (`**<표 1> 실험 설계 격자 …**`), header row, pipe-separator row, data rows, `*주.*` note row |
| P6 | Table 2 structure correct | Korean title, header, separator, data, `*주.*` note |
| P7 | Table 3 structure correct | Korean title, header, separator, data, `*주.*` note |
| P8 | Table 4 structure correct | Korean title, header, separator, data, `*주.*` note (with Origin D footnote ²) |
| P9 | Table 5 structure correct | Korean title, header, separator, data, `*주.*` note |
| P10 | Origin D "출처 미확인" caveat in Figure 5 caption | `figure5_caption_ko.md` line 7 ("Origin D 주의(중요)… 출처 미확인 가정") |
| P11 | Origin D caveat in Table 4 | footnote ²: "원점 D 미검증 경고… smoke 검증… 참고용" |
| P12 | Origin D caveat in Methods §3.2 | row D: "출처 미확인 가정 변형" |
| P13 | Origin D caveat in Methods §3.5 | "Origin D(잠실종합운동장)의 결과는 출처 미확인 가정 변형으로 표기" |
| P14 | Origin D caveat in Methods §3.9 | item 2: "Origin D 출처 미확인" |
| P15 | Origin D caveat in Results §4.4 | "Origin D (출처 미확인 가정 변형)" |
| P16 | R=30→10 honesty statement in Methods §3.5 | "본 연구의 계획 단계… $R = 30$ paired CRN 반복을 명시하였다. 그러나… $R = 30$ 대신 **$R = 10$**으로 축소하여…" |
| P17 | R=30→10 honesty statement in Table 1 footnote | "¹ 계획된 R=30 → 실행 R=10 (메인 실험), R=5 (강건성 실험); Morris 궤적 200 → 50으로 축소." |
| P18 | Introduction has no specific result numbers | §1 only states research scope, no Δ/μ\* values |
| P19 | Methods has no specific result numbers (apart from design constants) | §3 only states design grid (R, σ, p ranges), no outcome values |
| P20 | All 5 tables include `*주.*` (note) row | Confirmed in head-of-file Reads |

---

## 3. FAIL Items

| # | Item | Severity | Evidence |
|---|---|---|---|
| F1 | **Figure 2 missing** | HIGH | No `figure2_*.png` exists in `manuscript/figures/`. Figures are numbered 1, 3, 4, 5 — gap at 2. Either rename/renumber or supply figure2. |
| F2 | **CRITICAL Morris top-3 disagreement** | **CRITICAL** | See §4 below. Three drafts each pick different top-3 subsets. |
| F3 | Abstract uses "feeder fleet size, passenger volume, rail headway" but no document supports this as the top-3 penalized-makespan ranking | HIGH | Abstract `00_abstract_en.md` line 5; results §4.5 and conclusion §5.1 disagree. |
| F4 | Origin descriptions inconsistent in Figure 5 caption vs. Introduction/Methods | MEDIUM | `figure5_caption_ko.md` line 5 calls origins A="잠실역", B="한강 르네상스/코엑스", C="잠실대교 남단", D="잠실종합운동장". `01_introduction_ko.md` and `03_methods_ko.md` define A=송파구청 일자리센터, B=삼전동 구민회관, C=장지역 4번 출구, D=잠실종합운동장. Origin names for A/B/C are **inconsistent**. |
| F5 | Conclusion §5.1 reports Phase 1 Origin-A baseline cells but contradicts §4.1 paired-delta numbers | MEDIUM | §5.1 cites `$\bar{\delta} = -29.999$분` at `s=1.0, p=0.5` and `-96{,}080`분 at `s=1.0, p=1.0`. Table 2 / §4.1 report `-41.75`분 and `-1.44e+05`분 for same cells. Numbers do not match each other. |
| F6 | Abstract reports Phase 1 baseline "**140** cells" but the DoE has 35 cells × 4 origins ≠ 140; could be 35 × R=10/something | LOW | Both English & Korean abstracts state "Phase 1 baseline 140 cells" — does not match §3.5 (35 cells × R=10 = 350 runs, not 140). Likely arithmetic drift. |
| F7 | Abstract reports completion 0.967 vs 0.900 at `s=2.0, p=3.0, blocked` | MEDIUM | §4.2 reports completion `0.20` (bus) vs `0.10` (multi) at `p=3.0`. Abstract numbers (0.967, 0.900) do not appear anywhere in `04_results_ko.md` or tables. |
| F8 | Table 5 lists 14 parameters; Methods §3.7 design table lists only 9 | LOW | Methods §3.7 says "9개 핵심 매개변수 (전체 14개 중 본 회랑 시나리오에 적용 가능한 부분집합)" — table 5 then presents all 14. Reconcile language. |
| F9 | Conclusion §5.1 cites references [1]–[15] but `references_apa.md` only has 25 entries that follow §2 numbering — re-keying needed | MEDIUM | §5 introduces references not present in §2/§3 (e.g., [10] 보안성 검토 절차, [13] KORAIL GTFS). Final numbering pass required. |
| F10 | Methods §3.5 mentions `(전체 14개 중)` for Morris, but Morris CSV claim_scope text says `750` samples = `(k+1)·T = 15·50` — so k=14 is correct on disk; Methods §3.7 design table only lists 9. Internal mismatch with Table 5. | LOW | Tied to F8. |

---

## 4. CRITICAL — Morris Top-3 Disagreement Matrix

The four documents below were drafted in parallel and each picked **different** top-3 subsets of `results/sensitivity/morris_summary.csv`. The CSV contains four (policy × scenario) blocks for `penalized_makespan`; sub-agents averaged or selected differently.

### 4.1 Per-document top-3 claims for penalized_makespan

| Source | Rank 1 (μ*) | Rank 2 (μ*) | Rank 3 (μ*) | Notes |
|---|---|---|---|---|
| **00_abstract_en.md** (line 5) | feeder_fleet_size | passenger_volume | rail_headway | English: "feeder fleet size, passenger volume, and rail headway"; Korean parallel uses 피더 차량 수, 인원 수, 철도 헤드웨이. **No μ\* values supplied.** |
| **04_results_ko.md** §4.5 | passenger_volume (μ\* = 1.46×10²) | direct_bus_fleet_size (μ\* = 9.71×10) | dispatch_interval (μ\* = 7.54×10) | Cites `bus_only` averaged scenario. |
| **05_conclusion_ko.md** §5.1 | last_mile_fleet_size (μ\* ≈ 42.62) | passenger_volume (μ\* ≈ 35.85) | turnaround_time (μ\* ≈ 29.13) | Numbers correspond exactly to the `baseline_multimodal` row of the CSV. |
| **table5_morris_mu_star.md** | passenger_volume (μ\* avg = 47.27) | direct_bus_fleet_size (μ\* avg = 29.43) | dispatch_interval (μ\* avg = 20.44) | Reports averaged across 7 metrics × 2 policies × 2 scenarios. |

### 4.2 Ground truth from `results/sensitivity/morris_summary.csv`

For `penalized_makespan` only:

| Policy × Scenario block | Rank 1 (μ\*) | Rank 2 (μ\*) | Rank 3 (μ\*) |
|---|---|---|---|
| `baseline_multimodal` × `songpa_last_mile_station_to_destination` | last_mile_fleet_size (42.62) | passenger_volume (35.85) | turnaround_time (29.13) |
| `baseline_multimodal` × `songpa_random_capacity_reduction` | last_mile_fleet_size (42.35) | passenger_volume (35.64) | turnaround_time (29.21) |
| `bus_only` × `songpa_last_mile_station_to_destination` | passenger_volume (255.72) | direct_bus_fleet_size (194.30) | dispatch_interval (126.54) |
| `bus_only` × `songpa_random_capacity_reduction` | passenger_volume (255.69) | direct_bus_fleet_size (194.13) | dispatch_interval (126.48) |

### 4.3 Diagnosis

- **Conclusion** correctly reports the `baseline_multimodal` block.
- **Results** correctly reports the `bus_only` block but at slightly different absolute values (146 vs 255; check whether results agent re-averaged or sampled a sub-block).
- **Table 5** correctly reports a **multi-metric average** (μ\* aggregated over 7 outputs × 2 policies × 2 scenarios), n=28 records — a legitimate aggregation strategy.
- **Abstract** mentions `feeder_fleet_size` and `rail_headway` which do **not appear** in any top-3 of the CSV for `penalized_makespan`. `feeder_fleet_size` ranks 7th and `rail_headway` ranks 6th in the Table 5 aggregate (μ\* = 4.43 and 6.62 respectively). The abstract appears to **fabricate** a ranking not supported by any block. **CRITICAL.**

### 4.4 Recommended reconciliation policy (for integration agent)

Pick **one** canonical aggregation rule and apply it across all four documents:

**Option A (recommended):** Use the **Table 5 multi-metric average** (passenger_volume, direct_bus_fleet_size, dispatch_interval) as the canonical top-3 because (i) it is the most defensible aggregation under the §3.7 "screen ranking" framing, and (ii) it already appears in the table the abstract should mirror.

**Option B:** Use a single (policy × scenario) cell, but then specify *which* in every document. The conclusion's `baseline_multimodal` ranking (last_mile_fleet_size, passenger_volume, turnaround_time) is also a coherent choice but would invalidate the abstract.

Whatever option is chosen, **rewrite abstract, §4.5, §5.1, and the table 5 note to use identical wording and identical μ\* values**.

---

## 5. Other Inconsistencies

| # | Issue | Affected files | Suggested fix |
|---|---|---|---|
| O1 | Phase 1 baseline "140 cells" in abstract | `00_abstract_en.md` | Replace with "35 cells × R = 10 = 350 paired runs" (matches §3.5). |
| O2 | Completion rates 0.967 / 0.900 in abstract not derived from any table | `00_abstract_en.md` | Re-pull from `04_results_ko.md` §4.2 or supporting CSV; current values appear to be from an outdated draft. |
| O3 | Origin names (A/B/C) inconsistent: Figure 5 caption vs. Introduction/Methods | `figure5_caption_ko.md` | Replace caption origins with §3.2 names (송파구청 일자리센터 / 삼전동 / 장지역 4번 출구). |
| O4 | Conclusion §5.1 numbers `-29.999` and `-96,080` minutes do not match Table 2 / §4.1 (`-41.75`, `-1.44e+05`) | `05_conclusion_ko.md` | Re-pull from authoritative Phase 1 CSV; align with Table 2. |
| O5 | Delta column naming differs: Table 2 uses "Mean Δ (분)", Table 4 uses "Mean Δ (A, R=10)" etc., Table 3 uses "Mean Δ 페널라이즈드 메이크스팬 (분)" | tables 2–4 | Standardize on "Mean Δ penalized_makespan (분)" or define short form once and reuse. |
| O6 | Citation numbering re-keying needed | `05_conclusion_ko.md` (cites [1]–[15]); `04_results_ko.md` (notes "no new citations"); `references_apa.md` only has 25 entries that follow §2 numbering | Run a final renumbering pass across §1–§5 against `references_apa.md`. |
| O7 | Terminology drift: "복합수단" vs "다중수단" vs "multimodal" | §4 uses 단일/복합수단; tables use "다중-수단"; figure 3 caption says "다중수단 통합" | Pick one Korean term (suggest **"복합수단"** matching §1/§3) and replace globally. |
| O8 | Figure 3 caption says "n=0 양수 셀" (no positive cells), but Table 2 also shows all-negative — consistent; however §4.1 mentions paired delta becomes "대규모 음의 값" while figure 3 caption frames the **multimodal** as better — opposite sign convention | `figure3_caption_ko.md` line 1 ("음수 셀 … 다중수단 통합이 단일 버스보다 우수") vs. §4.1 ("Δ = bus − multi, 음수 = bus 빠름") | **Sign convention mismatch.** Figure 3 caption inverts the interpretation. Fix figure 3 caption. |
| O9 | Methods §3.7 lists 9 Morris parameters; Table 5 and the CSV (k=14) list 14 | `03_methods_ko.md`, `table5` | Reconcile: either extend §3.7 design table to 14 rows, or add a note that 5 parameters are "extension set". |
| O10 | Reproducibility CSV cited as `figure5_origin_robustness.csv` exists on disk; not cross-referenced in §4.4 text | `04_results_ko.md` §4.4 | Add inline reference to the CSV for transparency. |
| O11 | "smoke 검증" (`results/smoke_D.json`) referenced in Table 4 footnote — verify file exists | `table4_origin_robustness.md` | Confirm `results/smoke_D.json` actually exists before submission. |

---

## 6. Prioritized Action List for Integration Agent

| Priority | Action | Owner-suggested |
|---|---|---|
| **P0** | Resolve Morris top-3 disagreement (§4 above). Pick canonical aggregation, rewrite abstract + §4.5 + §5.1 + Table 5 note with identical top-3 and matching μ\* values. | Lead integration agent |
| **P0** | Decide on figure2: either renumber figures 3→2, 4→3, 5→4 (becoming 4 figures total) or produce the missing figure2 asset. Update all in-text references (§4 uses 〈그림 3〉/〈그림 4〉/〈그림 5〉). | Lead integration agent |
| **P1** | Reconcile abstract numbers (140 cells, 0.967/0.900 completion) with results §4.2 and Table 2 — current numbers cannot be sourced from any artifact on disk. | Abstract author |
| **P1** | Fix Figure 5 caption origin names to match §3.2 (A = 송파구청 일자리센터, B = 삼전동, C = 장지역). | Figure 5 author |
| **P1** | Fix Figure 3 caption sign convention so the meaning of "음수 셀" agrees with §4.1's Δ = bus − multi. | Figure 3 author |
| **P1** | Re-pull Conclusion §5.1 numbers (`-29.999`, `-96,080`) to match Table 2 / §4.1 values. | Conclusion author |
| **P2** | Standardize Δ column naming across Tables 2/3/4. | Tables author |
| **P2** | Pick one Korean term for multimodal (복합수단 vs 다중수단 vs 다중-수단) and apply globally. | Integration agent |
| **P2** | Renumber citations across §1–§5 against `references_apa.md`; ensure all bracketed numbers resolve. | Integration agent |
| **P2** | Reconcile Methods §3.7 Morris parameter count (9 vs 14) with Table 5. | Methods author |
| **P3** | Confirm `results/smoke_D.json` exists (referenced by Table 4 footnote). | Robustness author |
| **P3** | Decide whether to keep `figure5_origin_robustness.csv` as supplementary asset (it exists on disk). | Integration agent |

---

## 7. Summary

- **Total assets:** 9 (4 figures + 5 tables) — within KCI ≤ 10 budget.
- **Critical issues:** **1** (Morris top-3 disagreement across 4 docs).
- **Total FAIL items:** **10** (F1–F10).
- **Other inconsistencies:** **11** (O1–O11).
- **Top 3 issues to resolve first:**
  1. Morris top-3 inconsistency (abstract cites parameters not in CSV top-3 of any block).
  2. Missing figure2 (figure numbering 1, 3, 4, 5 — gap needs explanation or new asset).
  3. Abstract numbers (140 cells, 0.967/0.900) not sourced from any table or results section.
