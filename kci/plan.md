# KCI Implementation Plan v0.7 — Repositioned Study: Counterfactual Multimodal Applicability

**Document role:** HOW. Step-by-step plan that executes a *re-experiment* and full manuscript rewrite. Replaces v0.6 (which was executed but produced methodologically degenerate findings).
**Last updated:** 2026-05-11 (v0.7 — Option A reposition: counterfactual sweep + quantile KPIs + aggressive sub-agent parallelism).
**Status:** Ready to execute.
**Working directory:** `C:\Users\User\Downloads\transport-system-sim\kci` (use `../` for upstream assets).
**Time budget:** Unlimited. Experiments run to completion in background; loop continues.

---

## 0. v0.6 → v0.7 Reframing Rationale

| v0.6 finding | Root cause | v0.7 response |
|---|---|---|
| Phase 1 `s` axis inert (5/35 cells contained all the signal) | Censoring penalty (1440 min × ~hundreds censored) dominates the metric; BPR congestion effect (minutes) is invisible | Drop `s` axis; replace with single-mode parametric sweep (fleet × dispatch × p_fail) |
| Phase 2 policies indistinguishable (Δ within 0.9 min across 7 policies) | Grace period cannot rescue people who physically cannot arrive given road blockage; censoring tail dominates | Replace policy sweep with *counterfactual lever sweep*: rail_headway, lastmile_fleet, rail_capacity |
| Multimodal always loses (Δ < 0 in all 35 cells) | Corridor geography: multimodal exposes *two* road segments (A→S and R→D~30 km) while bus exposes one (A→D); rail = added risk, not redundancy | Reframe the research question from "find break-even" to "identify conditions under which multimodal becomes viable" — negative result is the discovery |
| Morris top-3 disagreement across parallel sub-agents | CSV has multiple (policy × scenario × metric) blocks; agents picked different subsets and one fabricated values | Canonicalize aggregation rule in Methods §3.7 BEFORE drafting; integration agent checks against single ground-truth CSV |

**Reframed research question:** *Under what infrastructure / parameter conditions does rail-bus multimodal become competitive with direct bus for the Songpa → 72nd Division (Bugok-ri) reserve-mobilization corridor?*

**Contribution (positive framing of negative empirical result):** A condition-map identifying the rail-headway / last-mile-fleet / rail-capacity thresholds that flip the corridor's modal preference, using a paired-CRN + censoring-aware + Morris + counterfactual-DoE pipeline.

---

## 1. Reuse vs Rewrite Matrix

Legend: ✅ keep verbatim · 🔧 small patches · 🔄 full rewrite · 🆕 new

### 1.1 Code

| File | v0.7 status | Notes |
|---|---|---|
| `kci/src/*.py` (network, scenario, dispatch, disruptions, fleet, models, policies, rail, sim_types, traffic, transfers) | ✅ | No simulator-core change |
| `kci/src/realworld/{adapter,attributes,osm_network,regions,types,validation,zones}.py` | ✅ | Major-arterial filter already applied |
| `kci/src/realworld/{disruption_scenarios,sensitivity,pilot_experiments,policy_alternatives,road_overrides,parameters}.py` | ✅ | Used by Morris pipeline |
| `kci/src/realworld/__init__.py` (slim) | ✅ | |
| `kci/src/kci_runtime.py` | 🔧 | Add `--quantile-kpi` pass-through, `apply_phase3_lever_override(...)` helper |
| `kci/src/experiment/doe.py` | 🔧 | Add `phase3_grid()` for counterfactual sweep; widen `Phase1Point` if needed |
| `kci/src/experiment/runner.py` | 🔧 | Add `run_phase3(config, G, lever_grid)`; emit quantile KPIs from each scenario |
| `kci/src/metrics.py` | 🔧 | Add `quantile_arrival_time(arrivals, q)`, `prob_completion_within(arrivals, deadline)`; expose as scenario outputs |
| `kci/main.py` | 🔧 | Add `--phase 3`, `--lever {rail_headway,lastmile_fleet,rail_capacity}` CLI; route to `run_phase3_pipeline` |
| `kci/scripts/run_pilot_smoke.py` | ✅ | |
| `kci/scripts/run_sensitivity.py` | ✅ | |
| `kci/scripts/run_accessibility_loss_analysis.py` | ✅ | |
| `kci/scripts/extract_corridor_graph.py` | ✅ | |
| `kci/scripts/make_figure{2..5}.py` | 🔄 | Replot against v0.7 result CSVs |
| `kci/scripts/build_kci_tables.py` | 🔄 | Rebuild against v0.7 result CSVs and new lever-sweep CSVs |
| `kci/scripts/make_figure_phase3.py` | 🆕 | Counterfactual lever-sweep figure |

### 1.2 Configuration / Data

| File | v0.7 status | Notes |
|---|---|---|
| `kci/config.yaml` | 🔄 | Drop `congestion_scale.levels` (keep at single value s=1.2); add `phase3_levers`; bump `experiment.R` to 30; add `quantile_kpi: {q: [0.5,0.9,0.95], deadline_min: 1500}` |
| `kci/data/regions/songpa_yangju_corridor.yaml` | ✅ | |
| `kci/data/regions/origin_candidates.json` | ✅ | |
| `kci/data/cache/songpa_yangju_corridor.graphml` | ✅ | 18,213 nodes (post-arterial-filter view) — reuse |
| `kci/data/scenarios/disruption_scenarios.csv` | ✅ | region_id already remapped |
| `kci/data/scenarios/policy_alternatives.csv` | ✅ | Used by Morris |
| `kci/data/scenarios/sensitivity_design.csv` | 🔧 | Add 4 new rows for Phase 3 levers + dispatch_interval if Morris should screen them too |
| `kci/data/validation/accessibility_loss*.csv` | ✅ | |

### 1.3 Results (regenerate all)

| Path | v0.7 status |
|---|---|
| `kci/results/phase1a_origin_A.csv` | 🆕 / replaces `phase1_origin_A.csv` (R=30, s=1.2 single, p_fail × 8 cells) |
| `kci/results/phase1b_origin_{B,C,D}.csv` | 🆕 / replaces `phase1_origin_{B,C,D}.csv` (R=20, 1D sweep) |
| `kci/results/phase2_singlemode.csv` | 🆕 / replaces `phase2_origin_A.csv` (single-mode fleet × dispatch × p_fail, R=20) |
| `kci/results/phase3_lever_sweep.csv` | 🆕 (counterfactual: rail_headway × lastmile_fleet × rail_capacity × p_fail) |
| `kci/results/sensitivity/morris_v07_*.csv` | 🔄 re-run with extended k=18 parameter set including Phase 3 levers |
| `kci/v0_6_archive/` | 🆕 | Snapshot of v0.6 results + manuscript for postmortem reference |

### 1.4 Manuscript

| File | v0.7 status | Notes |
|---|---|---|
| `kci/manuscript/figures/figure1_concept.png` | ✅ | |
| `kci/manuscript/figures/figure2_corridor_map.png` (+ caption) | ✅ | Geography unchanged |
| `kci/manuscript/figures/figure3_*.png` (break-even heatmap) | 🔄 | Becomes "robustness curve" 1D line plot |
| `kci/manuscript/figures/figure4_*.png` (success vs disruption) | 🔄 | Replot with v0.7 CSVs + 95% CIs (R=30 is statistically meaningful) |
| `kci/manuscript/figures/figure5_*.png` (origin robustness) | 🔄 | Replot with v0.7 origin sweep |
| `kci/manuscript/figures/figure6_phase3_lever.png` | 🆕 | Counterfactual lever heatmap — *the headline figure* |
| `kci/manuscript/tables/table{1..5}*.md` | 🔄 | Rebuild |
| `kci/manuscript/tables/table6_lever_conditions.md` | 🆕 | "Conditions under which multimodal becomes competitive" |
| `kci/manuscript/sections/00_abstract_en.md` (en + ko) | 🔄 | Reframed contribution; new headline numbers |
| `kci/manuscript/sections/01_introduction_ko.md` | 🔧 | Replace §1.3 (research objectives) — pivot from "break-even identification" to "applicability-condition identification" |
| `kci/manuscript/sections/02_literature_ko.md` | ✅ | Keep 25-ref list; integration may reorder |
| `kci/manuscript/sections/03_methods_ko.md` | 🔧 | (a) Drop `s`-axis defense; document why; (b) Define quantile KPIs in §3.6; (c) Add §3.5.4 "counterfactual lever sweep" subsection; (d) Reconcile Morris parameter count to 18 |
| `kci/manuscript/sections/04_results_ko.md` | 🔄 | Full rewrite around 4.1 baseline, 4.2 origin, 4.3 single-mode parametric, 4.4 counterfactual (headline), 4.5 Morris, 4.6 synthesis |
| `kci/manuscript/sections/05_conclusion_ko.md` | 🔄 | New thesis: "multimodal viability requires X+Y+Z; absent those, single-mode bus dominates" |
| `kci/manuscript/sections/references_apa.md` | 🔧 | Re-index after manuscript rewrite |
| `kci/manuscript/sections/00_audit_report.md` | 🔄 | Regenerate at v0.7 QA stage |
| `kci/manuscript/manuscript_ko.md` | 🔄 | Regenerate via integration agent |

---

## 2. Agent-Team Architecture

### Team Alpha — Code Surgery (3 parallel sub-agents, one turn)
- **A1 — DoE & Runner Patcher**: edits `doe.py`, `runner.py`, `main.py` to add Phase 3 grid + lever-injection scaffolding. Verifies imports.
- **A2 — Metrics & Quantile KPI Engineer**: edits `metrics.py` (and `scenario.py` where KPIs surface) to compute `arrival_time_q50/q90/q95`, `prob_completion_within_window`, and propagate them through `runner.py`'s `_paired_result_row`.
- **A3 — Config & Lever-Override Builder**: rewrites `config.yaml`; extends `kci_runtime.py` with `apply_phase3_lever_override(config, lever_name, value)` so each lever-cell run injects a fresh scenario config without mutating shared state.

Deliverables written directly to disk; agents return ≤200-word summaries. Team Alpha runs in **one parallel turn**.

### Team Bravo — Experiment Streams (no sub-agents; 5 background Bash streams)
Background `python` processes managed via `Bash run_in_background` + a long-lived Monitor. Coordinator (lead session) waits via `ScheduleWakeup` + Monitor events. Time budget unlimited; streams retry on failure.

### Team Charlie — Analysis & Figures (6 parallel sub-agents)
- **C1** Figure 3 — robustness curve (1D)
- **C2** Figure 4 — success-rate / quantile arrival curves
- **C3** Figure 5 — origin robustness (4-origin overlay)
- **C4** Figure 6 — Phase 3 counterfactual lever heatmap (**headline**)
- **C5** Tables 1–6 (full rebuild against v0.7 CSVs)
- **C6** Cross-reference audit (must run AFTER C1–C5 complete; arrives in second wave)

C1–C5 fire in one parallel turn. C6 fires after they all return.

### Team Delta — Manuscript Drafting (6 parallel sub-agents)
- **D1** §1 Introduction (patch §1.3 only; rest reuse)
- **D2** §3 Methods (patch §3.5 / §3.6 / §3.7 only; §3.1–§3.4 reuse)
- **D3** §4 Results (full rewrite)
- **D4** §5 Conclusion (full rewrite)
- **D5** Abstract en/ko (full rewrite)
- **D6** §2 Literature (light re-index + Morris-aggregation-rule footnote)

D1, D2, D6 can start while Team Bravo runs (do not require result numbers). D3, D4, D5 must wait for Team Charlie's table/figure outputs.

### Team Echo — Integration & QA (2 sequential agents)
- **E1** Integration agent: merge all sections + tables + figures into `manuscript_ko.md`; canonicalize Morris top-3 against `morris_v07_summary.csv`; verify cross-ref consistency; enforce asset-budget cap.
- **E2** Final QA agent: re-read `manuscript_ko.md` end-to-end; produce final pass/fail report.

---

## 3. Task DAG with Explicit Dependencies

Notation: `Tn.m [owner] description — needs: {prereqs}`. **Bold** tasks gate downstream phases.

### Layer 0 — Pre-work (lead session)
- **T0.1** [Lead] Write `plan.md` v0.7 — needs: ∅  *(this document)*
- **T0.2** [Lead] Snapshot v0.6 manuscript & results into `kci/v0_6_archive/` for postmortem reuse — needs: ∅

### Layer 1 — Code Surgery (Team Alpha, parallel)
- **T1.1** [A1] Patch `doe.py` (add `Phase3Point` NamedTuple + `phase3_grid()`); patch `runner.py` to add `run_phase3()`; patch `main.py` argparse (`--phase 3`, `--lever`, `--quantile-kpi`) and dispatch — needs: T0.1
- **T1.2** [A2] Implement quantile KPIs in `metrics.py`; thread through `scenario.run_scenario` outputs; ensure `_paired_result_row` carries the new columns — needs: T0.1
- **T1.3** [A3] Rewrite `config.yaml` (drop `congestion_scale.levels` sweep — pin `s=1.2`; declare `phase3_levers` block; set `experiment.R: 30`; add `quantile_kpi` block); add `kci/src/kci_runtime.py::apply_phase3_lever_override(...)` — needs: T0.1
- **T1.4** [Lead] Smoke validate Team Alpha output: `python main.py --quick --phase 1 --origin A --output results/v07_smoke_phase1.csv` and `python main.py --phase 3 --lever rail_headway --quick --output results/v07_smoke_phase3.csv` — needs: T1.1, T1.2, T1.3 (all green)

### Layer 2 — Experiments (Team Bravo, background, parallel)
- **T2.1** [Bravo-S1] Phase 1a (baseline robustness, origin A, R=30, s=1.2, p_fail × 8 levels = 8 cells × 30 = 240 paired runs) → `results/phase1a_origin_A.csv`. **GATING for T3.1, T3.2.** — needs: T1.4
- **T2.2** [Bravo-S2] Phase 1b (origin robustness, origins B/C/D, R=20, focused p_fail × 4 levels = 4 × 3 × 20 = 240) → `results/phase1b_origin_{B,C,D}.csv`. **GATING for T3.3.** — needs: T1.4
- **T2.3** [Bravo-S3] Phase 2 single-mode parametric (bus_fleet × dispatch_interval × p_fail = 5×3×3 = 45 cells × R=20 = 900) → `results/phase2_singlemode.csv`. **GATING for T3.5 (Table 3).** — needs: T1.4
- **T2.4** [Bravo-S4] Phase 3 counterfactual (rail_headway × lastmile_fleet × rail_capacity × p_fail = 3×3×3×3 = 81 cells × R=15 = 1215) → `results/phase3_lever_sweep.csv`. **GATING for T3.4 (headline figure).** — needs: T1.4
- **T2.5** [Bravo-S5] Morris (k=18 parameters incl. Phase 3 levers, 100 trajectories, 4 levels = ~1900 model evaluations) → `results/sensitivity/morris_v07_*.csv`. **GATING for T3.5 (Table 5) and T4.5 (Results §4.5).** — needs: T1.4
- **T2.M** [Lead + Monitor] Single Monitor armed on master log filtering for `Phase * complete|V07_PHASE4_DONE|Traceback|Error:|FAILED|Results saved`; `ScheduleWakeup` cadence 1800 s as safety net — needs: T2.1–T2.5 launched

**Bravo backpressure plan (time budget unlimited):**
- If any stream errors at startup → fix-in-place loop: lead session reads log tail, edits offending file, relaunches just that stream.
- If runtime exceeds 12 h → no action; wait.
- Logs at `kci/logs/v07_*.log`. Master sentinel: `kci/logs/v07_master.log` writes `V07_PHASE4_DONE` when streams 1–4 finish.
- Morris (T2.5) is independent of the sentinel — it has its own completion grep (`results: .*morris_v07`).

### Layer 3 — Analysis & Figures (Team Charlie)
Two waves. Wave 1 (T3.1–T3.5) is parallel; Wave 2 (T3.6) is sequential audit.

- **T3.1** [C1] Figure 3 — robustness curve: Δ penalized_makespan vs p_fail_scale, 1D line with 95% CI band (R=30) — needs: T2.1
- **T3.2** [C2] Figure 4 — quantile arrival curves: P(arrival ≤ deadline) and q90 arrival vs p_fail_scale (uses new quantile KPIs) — needs: T2.1
- **T3.3** [C3] Figure 5 — origin robustness: 4-origin overlay of robustness curves, Origin D hatched + caveat — needs: T2.1, T2.2
- **T3.4** [C4] **Figure 6 — counterfactual lever heatmap (HEADLINE)**: cells = (rail_headway, lastmile_fleet); panels = rail_capacity; color = mean Δ penalized_makespan at p_fail_scale=1.5; cross-marker where Δ flips sign — needs: T2.4
- **T3.5** [C5] Tables 1–6 (rebuild + Table 6 new) — needs: T2.1, T2.2, T2.3, T2.4, T2.5
- **T3.6** [C6] Cross-reference audit — re-runs the v0.6 audit checks PLUS verifies the Morris top-3 in every drafted section against `results/sensitivity/morris_v07_summary.csv` (Phase 3 levers included) using the canonical Table 5 multi-metric mean aggregation — needs: T3.1–T3.5

### Layer 4 — Manuscript Drafting (Team Delta)
Parallel within the layer. Two cohorts based on data dependency.

Cohort α (does NOT need result numbers — starts during Layer 2):
- **T4.1** [D1] §1 introduction patch — needs: T0.1
- **T4.2** [D2] §3 methods patch — needs: T1.1, T1.2, T1.3 (must reflect what was actually built)
- **T4.6** [D6] §2 literature re-index — needs: T0.1

Cohort β (needs Layer 3 outputs):
- **T4.3** [D3] §4 results full rewrite — needs: T3.1, T3.2, T3.3, T3.4, T3.5
- **T4.4** [D4] §5 conclusion rewrite — needs: T3.1–T3.5, T4.3 (consistency)
- **T4.5** [D5] Abstract en/ko rewrite — needs: T4.3, T4.4 (so abstract numbers are sourced)

### Layer 5 — Integration & QA (Team Echo)
- **T5.1** [E1] Integration agent: assemble `manuscript_ko.md` v0.7; renumber citations; canonicalize Morris top-3; check Origin D caveat threading; verify quantile-KPI definitions appear consistently; enforce asset cap ≤10 — needs: T4.1–T4.6 complete, T3.6 audit report
- **T5.2** [E2] Final QA agent: read `manuscript_ko.md` cover-to-cover; flag inconsistencies; produce go/no-go report at `manuscript/sections/00_qa_final.md` — needs: T5.1
- **T5.3** [Lead] Address T5.2 findings (iterative; each issue → either direct Edit or spawn targeted Agent) — needs: T5.2

### Layer 6 — Delivery
- **T6.1** [Lead] git pull --rebase / add / commit / push v0.7 — needs: T5.3 green

---

## 4. New Experimental Design — Detail

### 4.1 Phase 1a — Baseline Robustness (origin A only)

| Knob | Value |
|---|---|
| Origin | A (송파구청 일자리센터) |
| `s` (congestion) | **fixed at 1.2** (no sweep — documented as informed by v0.6 inertness check) |
| `p_fail_scale` | 0.0, 0.10, 0.25, 0.50, 0.75, 1.0, 1.5, 2.0 (8 levels) |
| Failure mode | blocked |
| Network variant | baseline |
| R (paired reps) | **30** |
| Total runs | 8 × 30 = 240 paired = 480 scenarios |
| Estimated wall time | 480 × ~8.5 s = ~70 min |

### 4.2 Phase 1b — Origin Robustness

| Knob | Value |
|---|---|
| Origins | B, C, D (D = unverified variant) |
| `p_fail_scale` | 0.0, 0.5, 1.0, 1.5 (4 focused levels) |
| R | **20** |
| Total | 3 × 4 × 20 = 240 paired = 480 scenarios |
| Estimated wall time | ~70 min (sequential across origins inside one stream) |

### 4.3 Phase 2 — Single-Mode Parametric (replaces v0.6 Phase 2)

Goal: how much can single-mode robustness be recovered by fleet / dispatch tuning?

| Knob | Levels |
|---|---|
| `bus.fleet_size` | 15, 23 (baseline), 35, 50, 80 |
| `bus.dispatch_interval_min` | 3, 5, 10 |
| `p_fail_scale` | 0.5, 1.0, 2.0 |
| R | **20** |
| Total | 5 × 3 × 3 × 20 = 900 paired = 1800 scenarios |
| Estimated wall time | ~4.3 h |

### 4.4 Phase 3 — Counterfactual Lever Sweep (NEW, **headline**)

Goal: identify (rail_headway, lastmile_fleet, rail_capacity) regions where multimodal Δ flips sign.

| Lever | Levels |
|---|---|
| `multimodal.rail.headway_min` | 15 (baseline), 7.5, 3 |
| `multimodal.lastmile_fleet_size` | 23 (baseline), 50, 100 |
| `multimodal.rail.capacity_pax_per_train` | 500 (baseline), 1000, 2000 |
| `p_fail_scale` | 0.0, 0.5, 1.5 |
| R | **15** |
| Total | 3 × 3 × 3 × 3 × 15 = 1215 paired = 2430 scenarios |
| Estimated wall time | ~5.7 h |

Each cell uses `apply_phase3_lever_override(config, lever, value)` (T1.3 deliverable) so cell parameters are baked into the run config exactly once per cell.

### 4.5 Phase 4 — Morris (extended)

| Knob | Value |
|---|---|
| Parameters | 18 (= original 14 + 4 Phase 3 levers: rail_headway, lastmile_fleet, rail_capacity, dispatch_interval) |
| Trajectories | 100 |
| Levels | 4 |
| Method | `salib_morris` |
| Total model evaluations | (18 + 1) × 100 = 1900 |
| Estimated wall time | ~1.5 h (Morris uses fixture-scale demand → cheap) |

### 4.6 Quantile KPIs (T1.2 deliverable)

Per scenario output, add:
- `arrival_q50_min` — median arrival time
- `arrival_q90_min` — 90th percentile arrival time
- `arrival_q95_min` — 95th percentile arrival time
- `prob_completion_within_window` — fraction arriving by `deadline_min` (config-default 1500 min ≈ 25 h, matches reserve-training day-1 cutoff)

Delta columns added by `_paired_result_row` automatically: `delta_arrival_q90_min`, `delta_prob_completion_within_window`, etc.

Rationale: quantile metrics are insensitive to the censoring penalty's magnitude and respond to distribution shape; they are the primary metric for §4.4 (counterfactual) and a secondary metric for §4.1 / §4.3.

---

## 5. Background-Execution Strategy

Goal: time budget unlimited → no shortcut; experiments run to completion regardless of duration.

1. **Single `bash -c` launches all 5 streams in background.** Each stream redirects to its own log under `kci/logs/v07_*.log`. Master `wait` writes `V07_PHASE4_DONE` to `kci/logs/v07_master.log`.
2. **One Monitor armed** with grep alternation: `Phase * complete|V07_PHASE4_DONE|results: .*morris_v07|Traceback|Error:|FAILED|Results saved to`.
3. **ScheduleWakeup safety net at 1800 s.** Resets each turn the loop fires.
4. **Stream failure response:** lead session reads `tail -50 logs/v07_<stream>.log`, identifies fault, edits file, relaunches *only that stream* in background. Do not abort the others.
5. **No reduction policy.** Plan v0.6 fell back R=30→R=10; v0.7 holds the line. If wall time exceeds expectations, accept it.
6. **Disk-pressure check:** `du -sh logs/` after each wakeup; rotate logs >100 MB.
7. **Process-leak check:** at each wakeup, if no growth in any log for >20 min, treat that stream as wedged → re-launch.
8. **Stdout-buffering mitigation:** launch Python with `-u` (unbuffered) so progress prints flush immediately, making Monitor events fire on schedule.

---

## 6. Manuscript Rewrite Plan — Per-Section Surgery

### 6.1 Title
- Old: 산업공학 도구를 적용한 예비군 동원수송체계의 단일수단·복합수단 회복력 비교
- New (canonical for v0.7): **예비군 동원수송 회랑에서 복합수단 적용 조건 식별 — 송파↔양주 부곡리 사례를 중심으로**
  - En sub: *Identifying the Conditions for Multimodal Applicability in Reserve-Force Mobilization Corridors — A Songpa-to-Yangju Bugok-ri Case Study*

### 6.2 §1 Introduction
- §1.1 background — ✅ reuse
- §1.2 problem statement — ✅ reuse
- **§1.3 research question** — 🔄 rewrite. Replace "break-even identification" with "applicability-condition identification". Add explicit hypothesis: *baseline rail-bus multimodal is dominated by direct bus; the contribution is identifying the (headway, last-mile fleet, rail capacity) thresholds that reverse the ordering.*
- §1.4 contribution — 🔧 patch. Emphasize the *condition map* as the deliverable.
- §1.5 scope — ✅ reuse
- §1.6 paper structure — 🔧 patch. List new §3.5.4 (counterfactual sweep), Figure 6, Table 6.

### 6.3 §2 Literature
✅ Keep 25-ref list. T4.6 (D6) adds a Morris-aggregation note acknowledging that the integration agent enforces a single canonical aggregation rule.

### 6.4 §3 Methods
- §3.1–§3.4 — ✅ reuse
- **§3.5 DoE** — 🔄 rewrite:
  - §3.5.1 Phase 1a (baseline robustness)
  - §3.5.2 Phase 1b (origin robustness)
  - §3.5.3 Phase 2 (single-mode parametric)
  - **§3.5.4 Phase 3 (counterfactual lever sweep) — new**
  - §3.5.5 "Why the s-axis was dropped" paragraph (cite v0.6 inertness finding)
  - §3.5.6 R-honesty paragraph (R=30 main, R=20 origin / Phase 2, R=15 Phase 3)
- **§3.6 censoring-aware + quantile KPIs** — 🔧 patch. Add quantile definitions and `deadline_min=1500` rationale.
- **§3.7 Morris** — 🔧 patch. List 18 parameters explicitly; canonical aggregation = multi-metric mean over (policy × scenario) blocks.
- §3.8 reproducibility — ✅ reuse
- §3.9 limitations — ✅ reuse + small note: counterfactual sweep does not imply implementability.

### 6.5 §4 Results — 🔄 full rewrite
- §4.1 Phase 1a baseline robustness (cite Fig 3, Table 2)
- §4.2 origin robustness (cite Fig 5, Table 4; Origin D caveat)
- §4.3 Phase 2 single-mode parametric (cite Table 3)
- **§4.4 Phase 3 counterfactual sweep (headline) — cite Fig 6, Table 6**
- §4.5 Morris ranking with Phase 3 levers (cite Table 5)
- §4.6 synthesis: condition map summary

### 6.6 §5 Conclusion — 🔄 full rewrite
- §5.1 main finding: *for the Songpa↔Bugok-ri corridor, multimodal viability requires {rail_headway ≤ X min} ∧ {lastmile_fleet ≥ Y} ∧ {rail_capacity ≥ Z}; baseline parameters meet 0/3*
- §5.2 academic + practical implications
- §5.3 limitations (R, calibration, single corridor, Origin D)
- §5.4 future work

### 6.7 Abstract en/ko — 🔄 rewrite
- 2 quantitative anchors: (a) baseline result direction (bus dominates without intervention); (b) condition-map threshold values for one or two Phase 3 levers.
- Keywords: counterfactual analysis · rail-bus multimodal · reserve mobilization · paired CRN · quantile arrival KPI.

### 6.8 References — 🔧 re-index after §1–§5 cite order finalized by E1

---

## 7. Quality Gates

| Gate | Owner | Pass criterion |
|---|---|---|
| G1 (Layer 1 exit) | Lead | T1.4 smoke `--phase 1` and `--phase 3` both write CSVs and the new quantile columns appear non-NaN; no Python error |
| G2 (Layer 2 exit) | Lead via Monitor | All 5 v0.7 CSVs exist; row counts match design (240/240/900/1215 paired + ~1900 Morris model-evals) |
| G3 (Layer 3 exit) | C6 audit report | All figures + tables present; Morris top-3 cited identically across abstract / §4.5 / §5.1 / Table 5 against `morris_v07_summary.csv` canonical aggregation |
| G4 (Layer 5 exit) | E2 QA report | `manuscript_ko.md`: Origin D caveat at first mention in §1.1 / §3.2 / §4.4 + Fig 5 caption + Table 4 footnote; no orphan citations; total assets ≤ 10 |
| G5 (Delivery) | Lead | git push succeeds; manuscript_ko.md Korean character count ≥ 6000 |

**G4 asset budget note**: 6 figures + 6 tables = 12 > 10 KCI cap. Resolution options (E1 decides):
- Demote Figure 5 (origin robustness) to a supplementary table.
- Collapse Table 1 (DoE design) into a methods paragraph; promote Table 6 to its slot.
- Merge Tables 2 + 4 (Phase 1a + origin robustness) into a single tall table.

---

## 8. Rollback / Risk

| Risk | Probability | Mitigation |
|---|---|---|
| Phase 3 sweep also produces a flat surface (no Δ sign flip anywhere) | medium | Even a flat surface is a defensible finding: "no realistic infrastructure intervention rescues multimodal on this corridor." Manuscript framing accommodates. |
| Quantile KPI implementation buggy | medium | T1.2 includes unit-level smoke (`--quick`); T1.4 gates Layer 2 launch on the quantile columns being non-NaN |
| Morris CSV again produces multi-block readings | high | T3.6 audit explicitly checks; E1 canonicalizes against `morris_v07_summary.csv` multi-metric mean; D3 / D4 / D5 receive the canonical top-3 *as an input fact* in their prompts (do not let them re-aggregate) |
| Manuscript exceeds 25-page Pretendard limit | medium | E1 trim pass; collapse §1.1 + §1.2 if needed; §3.1–§3.4 are reusable but long — candidate for compression |
| Bash background streams die silently on Windows | low (didn't recur in v0.6) | Monitor grep alternation includes `Traceback\|Error:`; lead session relaunches wedged streams |
| Git push fails on upstream divergence (happened twice in v0.6) | high | T6.1 always does `git pull --rebase` before push |
| Sub-agent fabricates numbers (happened in v0.6 abstract) | high | Each Cohort β agent prompt embeds the canonical Morris top-3 + canonical headline numbers; integration agent re-checks against CSVs |

---

## 9. Execution Order — Lead Session Choreography

Concretely, the lead session's turn-by-turn loop:

1. **Turn 1**: T0.2 (archive v0.6) → spawn Team Alpha A1, A2, A3 in one parallel Agent batch. Wait for all three to return.
2. **Turn 2**: Run T1.4 smoke (Bash, foreground). On green, launch Team Bravo via `bash -c` background; arm Monitor; `ScheduleWakeup 1800 s`. Also spawn Team Delta cohort α (D1, D2, D6) in parallel — they draft while experiments run.
3. **Turns 3..N**: Monitor events arrive; safety wakeups fire. Lead reads master log; if a stream errored, edit + relaunch. Otherwise reset safety net and continue.
4. **Turn (G2 reached)**: Spawn Team Charlie wave 1 (C1, C2, C3, C4, C5) in parallel. `ScheduleWakeup 600 s`.
5. **Turn (wave 1 done)**: Spawn C6 audit + Team Delta cohort β (D3, D4, D5) in parallel.
6. **Turn (G3 + cohort β done)**: Spawn E1 integration agent.
7. **Turn (E1 done)**: Spawn E2 final QA.
8. **Turn (E2 issues)**: Either resolve directly (Edit) or spawn targeted Agent. Iterate ≤ 3 cycles, then commit anyway with residual items called out in the commit message.
9. **Turn (G5 done)**: git pull --rebase, git add, git commit, git push.

Estimated lead-session turns: 8–14. Estimated active token usage: comparable to v0.6 plus the Phase 3 + abstract / §4 / §5 rewrites.

---

## 10. TL;DR

1. **Pivot**: stop searching for a break-even, start identifying the *conditions* under which multimodal becomes viable.
2. **Code surgery (Team Alpha, 3 parallel agents)**: Phase 3 grid + lever override, quantile KPIs, config rewrite.
3. **Experiments (Team Bravo, 5 background streams, R = 30/20/20/15)**: ~12–14 h wall-clock, run unattended. Monitor + ScheduleWakeup. No reductions.
4. **Analysis (Team Charlie, 6 parallel agents → 1 audit)**: rebuild all figures/tables; new Figure 6 + Table 6 carry the headline.
5. **Drafting (Team Delta, 6 parallel agents)**: cohort α drafts during experiments, cohort β drafts after.
6. **Integration & QA (Team Echo, 2 agents)**: canonicalize Morris top-3; enforce asset cap; produce final manuscript_ko.md.
7. **Commit & push** with v0.7 reframing called out in the commit message.
8. **Reuse aggressively**: simulator core, OSM graph cache, §2 literature, §3.1–§3.4 methods, Figures 1–2.
9. **Rewrite aggressively**: §4, §5, abstract, Figures 3–5, all tables, plus new Figure 6 + Table 6.
10. **Quality gate G4 forces an asset-cap decision**: 12 → ≤10 by demoting Fig 5 to supplementary or merging tables.

End of v0.7 plan.
