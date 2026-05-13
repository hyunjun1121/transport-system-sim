# T3.6 Cross-Reference Audit — v0.7 (G3 gate)

Auditor: C6. Convention: `Δ = bus_only − multimodal` (code `_safe_delta(left=bus, right=multi)`; negative ⇒ bus advantage).

## A. Sign convention (10/10 PASS)

| Artifact | Verdict |
|---|---|
| `figure3_caption_ko.md` L1: "Δ … (직행버스 - 다중수단 통합)" + "Δ<0 … 직행버스가 모든 관측 disruption 강도에서 우위" | PASS |
| `figure4_caption_ko.md`: per-mode curves, no Δ formula | PASS (n/a) |
| `figure5_caption_ko.md` L5: "Δ … (= bus-only − multimodal)" + "음(−) … bus-only가 유리" | PASS |
| `figure6_caption_ko.md` L5: "Δ … (= bus − multi)" + "청색(Δ<0) 직행버스 우위, 적색(Δ>0) multimodal 우위" | PASS |
| `table1_doe_design.md`: design table, no Δ | PASS (n/a) |
| `table2_phase1_means_ci.md` L14: "Δ = bus_only − multimodal … 음수 = 직행버스 우위" | PASS |
| `table3_phase2_policy_pareto.md` L53: "Δ = bus_only − multimodal … 음수 = 직행버스 우위" | PASS |
| `table4_origin_robustness.md` L22: "Δ = bus_only − multimodal …" + D† footnote | PASS |
| `table5_morris_mu_star.md`: μ* only, no Δ | PASS (n/a) |
| `table6_lever_conditions.md` L17: "Δ = bus − multi (음수 = 직행버스 우위)" | PASS |

## B. Morris top-3 cross-check (PASS)

Independent re-aggregation of `morris_summary.csv` (392 rows, 14 params) via `groupby(parameter_id, metric).mu_star.mean()` → `groupby(parameter_id).mean()` desc:

1. passenger_volume = **44.50**
2. direct_bus_fleet_size = **27.41**
3. dispatch_interval = **20.77**

Canonical file: 44.5 / 27.4 / 20.8. Table 5 rows 1–3: identical. Independent ↔ canonical ↔ Table 5 agree to 3 sig figs.

## C. Origin D caveat coverage

| File | Present | Marker |
|---|---|---|
| `figure5_caption_ko.md` L9 | YES | "비검증 후보 — 결과는 참고용" + ring/hatch/dashed |
| `table4_origin_robustness.md` L17–L22 | YES | `D†` rows + "**† Origin D는 비검증(unverified) 변형…**" |
| `table1_doe_design.md` L6, L11 | YES | "D = 비검증" inline |
| `04_results_ko.md` §4.4 L45 | YES (phrasing only) | Caveat correct; surrounding §4 prose is stale v0.6 (R=10, 9 Morris params, μ*=1.46×10²) — D3 must rewrite §4 (out-of-scope here). |

Verdict: PASS for figure/table; §4 prose flagged for D3.

## D. Asset budget (G4)

6 figures + 6 tables = **12 > G4 cap 10**. Demote 2.

**Recommendation:** demote **Table 1 (DoE design)** AND **Figure 5 (origin robustness)** → supplementary. Rationale: Table 1 is design metadata (foldable into §3 methods prose); Figure 5 carries the Origin D unverified caveat that weakens headline-figure impact, and Table 4 already conveys the same numbers. Result: 5 + 5 = 10, meets G4 exactly.

## E. Headline numbers ledger (canonical)

| # | Quantity | Value | Source |
|---|---|---|---|
| 1 | Phase 1a Δ penalized_makespan @ p_fail=0.0 | **−58.5 min**, 95% CI [−58.5, −58.5] (R=30, deterministic) | Table 2 row 1 |
| 2 | Phase 1a Δ P(완료 ≤ 1500min) @ p_fail=2.0 | **+0.433**, 95% CI [+0.245, +0.622] | Table 2 row 8 |
| 3 | Phase 3 multi-dominant cells | **0 of 81** (54 bus_dominant, 27 inconclusive) | `table6_lever_conditions_summary.json` |
| 4 | Phase 3 narrowest-gap cell | rail_headway=3, lastmile_fleet=23, rail_capacity=500, p_fail=0.5 → Δ = **−39.3 min** [−50.7, −28.0]; bus_dominant (closest to 0) | `table6_…_summary.json::narrowest_gap_cell` |
| 5 | Morris top-3 (canonical μ*) | passenger_volume **44.5**, direct_bus_fleet_size **27.4**, dispatch_interval **20.8** | `canonical_morris_top3.md` |
| 6 | Morris parameter count v0.7 | **k = 14** (not 18; `sensitivity_design.csv` covered Phase 3 levers; plan §4.5 extension deferred) | `morris_summary.csv` |

Downstream (E1 abstract / D3 §4 / D5 §5) must cite verbatim and not re-aggregate `morris_summary.csv`.

## G3 verdict — PASS (conditional)

Wave-1 artifacts are internally consistent and consistent with canonical sources on all four axes (A, B, C, E). Conditional items for E1/D3 (not blocking G3, must resolve before G4):

1. Demote Table 1 + Figure 5 → supplementary (per §D) for G4 ≤ 10.
2. D3 must rewrite §4 with v0.7 numbers; only Origin D caveat phrasing in §4.4 L45 is reusable.
3. `figure6_caption_ko.md` L9 contains a `TODO` for headline numbers (multi_dominant count, narrowest-cell tuple) — integration agent must inject items 3 + 4 from §E.
