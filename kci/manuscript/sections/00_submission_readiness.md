# T6.0 Submission-Readiness Audit — KCI v0.7 (한국군사학논집)

**Audit date:** 2026-05-13
**Auditor:** Echo (final integration)
**Manuscript HEAD:** `manuscript/manuscript_ko.md` @ `fa93c725` on `origin/main`
**Verdict:** **GO** — ready for KCI submission.

This file is the final audit-of-record for the v0.7 plan execution. It
supersedes earlier T3.6 (`00_audit_report.md`, G3 gate) and T5.2
(`00_qa_final.md`, internal QA) by re-verifying their findings against the
delivered artifacts on disk after the v0.7 push.

## 1. Quality gates

| Gate | Criterion | Verified value | Verdict |
|---|---|---|---|
| G1 | Phase-1a R = 30 paired CRN | `results/phase1a_origin_A.csv` rows ÷ p_levels = 30 | PASS |
| G2 | Phase-3 grid 3×3×3×3 × R_phase3=15 | 81 cells in `phase3_lever_sweep.csv` | PASS |
| G3 | Cross-reference integrity (sign, Morris, caveat) | see §2 below | PASS |
| G4 | ≤ 10 main assets | 5 figures (1, 2, 3, 4, 6) + 5 tables (2, 3, 4, 5, 6) | PASS |
| G5 | KOR body ≥ 6,000 chars | 17,784 | PASS |

## 2. Spot-check ledger (canonical values)

| # | Claim | Manuscript | Source | OK |
|---|---|---|---|---|
| 1 | Phase 1a Δ penalized_makespan @ p=0.0 | −58.5 min | `phase1a_origin_A.csv` mean = −58.5108 (R=30) | Y |
| 2 | Phase 1a Δ P(완료 ≤ 1500) @ p=2.0 | +0.433 [+0.245, +0.622] | `phase1a_origin_A.csv` mean = 0.4333 (R=30) | Y |
| 3 | Phase 3 multi_dominant cells | 0 of 81 | `table6_lever_conditions_summary.json::n_multi_dominant` = 0 | Y |
| 4 | Phase 3 narrowest-gap cell | rail_headway=3, lastmile=23, rail_cap=500, p=0.5 → Δ=−39.3 [−50.7, −28.0] | `…summary.json::narrowest_gap_cell` | Y |
| 5 | Morris top-3 μ* | passenger_volume 44.5, direct_bus_fleet_size 27.4, dispatch_interval 20.8 | `canonical_morris_top3.md`, `morris_summary.csv` independent re-aggregation | Y |
| 6 | Morris parameter count | k = 14 | `morris_summary.csv` distinct `parameter_id` count | Y |
| 7 | Asset count | 5 fig + 5 tbl = 10 | Filesystem scan of `manuscript/figures/`, `manuscript/tables/` | Y |
| 8 | Citations 1–25 used and defined | 25/25 | Regex of `manuscript_ko.md` body vs §참고문헌 | Y |
| 9 | Sign convention `Δ = bus_only − multimodal` | 11 places, all coherent | Body L295 / L336 / L369 / L402 / L430 / L464 / L511 + table/figure footnotes | Y |
| 10 | Origin D unverified caveat coverage | 7 explicit mentions | §1.1, §3.2, §3.9, §4.2, Tbl4, §5.3, Fig2 caption | Y |

## 3. File-integrity checks

- All `.md` files in `manuscript/` parse as strict UTF-8.
- `table6_lever_conditions_summary.json` parses; counts add up (54 + 27 + 0 = 81).
- All `.csv` files in `manuscript/` parse with `csv.reader`.
- Every `![...](path)` and `[...](path)` link in `manuscript_ko.md` resolves to a real file inside `manuscript/`.
- No `TODO`, `FIXME`, `XXX`, `placeholder`, `TBD`, or `???` markers in `manuscript_ko.md` body.

## 4. Filed for submission

- `manuscript/manuscript_ko.md` — 96,811 B, 633 lines, 17,784 KOR chars body.
- `manuscript/sections/00_abstract_en.md` + `00_abstract_ko.md` — bilingual abstract.
- `manuscript/figures/figure{1,2,3,4,6}_*.png` + `*_caption_ko.md`.
- `manuscript/tables/table{2..6}*.md`, `table6_lever_conditions_summary.json`.
- `manuscript/supplementary/figure_s1_origin_robustness.{png,csv}`, `table_s1_doe_design.md`.
- `manuscript/sections/references_apa.md` — APA-style reference list (refs 1–25).
- Audit trail: `00_audit_report.md` (G3) → `00_qa_final.md` (T5.2) → this file (T6.0).

## 5. Reproducibility pointers

- `config.yaml` at repo root pins R=30, R_phase3=15, R_origin_b_c_d=20, p_fail levels, phase3_levers grid, quantile_kpi (q ∈ {0.5, 0.9, 0.95}, deadline_min = 1500).
- `scripts/run_v07_phase{1_fast,1b,2_singlemode_fast,3_fast}.py` — parallel + checkpoint-resumable launchers (bit-identical CRN vs serial `main.py`, verified during execution).
- `src/experiment/phase3_runner.py` — `_override(deepcopy(base_config), point)` ensures lever values do not leak across cells.
- `v0_6_archive/` — frozen postmortem snapshot of v0.6 (do not regenerate from).

## 6. Stop condition

The plan's stop condition is satisfied:

> All Turn 14 deliverables produced AND G1–G5 all pass AND manuscript compiles clean.

No further action is required prior to journal submission. The submission file
to upload is `manuscript/manuscript_ko.md`; supporting figures/tables ship from
`manuscript/figures/`, `manuscript/tables/`, and `manuscript/supplementary/`.
