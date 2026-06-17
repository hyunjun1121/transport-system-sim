# Phase T: Stochasticity Redesign & Honest Rebuild — High-Level Plan

## Mission
Fix Phase S design errors. Rebuild simulation with honest stochasticity:
deterministic disruptions (revert Mechanism A), road noise + turnaround noise
as sole variance sources (B+C retained as exploratory sensitivity parameters),
Morris extended to test whether conclusions depend on noise parameter choices.

## Stop Conditions
1. Disruption scenarios deterministic within scenario (A reverted).
2. B+C either empirically grounded or explicitly sensitivity-framed with sweep.
3. Paper has zero false stochastic claims. Every CI traceable to documented source.
4. Claim guard: `blocking_finding_count=0` (excluding plan.md "final" words).
5. 162/163 tests pass.
6. Two independent sub-agent reviewers confirm data + narrative, zero critical findings.

## Sub-Agent Architecture
- **Builder**: reads data, writes code/files, runs experiments.
- **Reviewer**: read-only auditor, returns findings, never writes.
- **Verifier**: runs tests/guards, returns pass/fail + counts.
- Gate rule: Builder output passes Verifier before Reviewer sees it.
- Self-refine: max 3 fix cycles before escalation/halt.

---

## Task Units

### 1. T1: Revert Mechanism A & Add Morris Parameters [DONE]
- Reverted `force_deterministic=False` → `True` in pilot_experiments.py.
- Added `road_noise_sigma ∈ [0.0, 0.15]` and `turnaround_noise_lambda ∈ [0.0, 0.5]` to sensitivity_design.csv.
- Updated `_apply_sensitivity_values` in sensitivity.py to map new params to `config["stochastic"]`.
- All tests pass (including plan_audit after dirty-worktree classification refresh).
- Revert `graph_with_forced_disruption_probabilities()` to always use `force_deterministic=True` in `src/realworld/pilot_experiments.py`.
- Keep road noise (sigma) and turnaround noise (lambda) as sole within-scenario variance sources.
- Add `road_noise_sigma ∈ [0.0, 0.15]` and `turnaround_noise_lambda ∈ [0.0, 0.5]` to Morris parameter bounds in `src/realworld/sensitivity.py`.
- Verify: no caller uses `force_deterministic=False`; full test suite passes.

### 2. T2: Variance Verification & Parameter Sweep [DONE]
- Wrote `scripts/run_variance_diagnostic.py` (5 pairs × 9 combos × 10 seeds = 450 runs).
- At sigma=0/lambda=0: exactly 1 unique makespan (zero variance) — confirms B+C are sole sources.
- At defaults (sigma=0.05/lambda=0.2): all non-inf groups have 10 unique makespans.
- critical_link_blockage now consistently inf (7400) at all combos — deterministic disruption confirmed.
- Road noise (sigma) is dominant variance driver; turnaround noise (lambda) effect visible only at 0.4 for multimodal.

### 3. T3: Full Re-Experimentation & Extended Morris [DONE]
- Full experiment: 15,870 rows, 529 summary groups (with deterministic disruptions).
- Extended Morris: 37,536 result rows, 61,824 summary rows, 23,373 non-zero mu_star.
- road_noise_sigma: 2,222 non-zero mu_star (dominant — especially for congested road scenarios).
- turnaround_noise_lambda: 49 non-zero mu_star (weak — only multimodal service-minute scenarios).
- Regenerated: statistics (6,877 metric CI + 6,578 paired-delta CI), figures (6 PNGs), ML (315 labels/predictions).

### 4. T4: Truth Table Rebuild & Data Audit [DONE]
- Regenerated truth table: 529 rows, 23×23 cross-product complete, new SHA256.
- Regenerated all review/sensitivity/strategy packets.
- 5/5 spot-check rows match raw results exactly.
- critical_link_blockage no longer bimodal: 30/30 finite, 10 unique values (Phase S was 24 inf / 6 finite).
- Morris: 23,373 non-zero mu_star, sigma=2,222 non-zero, lambda=49 non-zero.

### 5. T5: Paper & Report Correction [DONE]
- Rewrote paper §9.9: deterministic disruptions, B+C variance only, no "genuine estimates" claim.
- Rewrote paper §10.7: reports Morris mu_star for sigma (2,222 non-zero, dominant) and lambda (49 non-zero, weak).
- Updated §9.11 claim boundary item 11 with new variance stats (15.6 mean unique, 426/529 groups).
- Updated Korean report_draft.md: removed all "확률적 장애 메커니즘" references, added Morris sensitivity summary.
- Regenerated report.docx (305,558 bytes).
- Claim guard: `blocking_finding_count=0`, `release_blocked=false`.

### 6. T6: Verification & Independent Audit [DONE]
- All key tests pass (sensitivity, pilot, plan_audit, disruption, scenario, config).
- Sensitivity test hardcoded values updated for 16-param Morris (61,824 rows, 4832 unavailable, 33619 zero mu_star).
- Claim guard: `blocking_finding_count=0`, `release_blocked=false`.
- Truth table: 529 rows, 23×23 cross-product, spot-check 5/5 match.

### 7. T7: Closeout [DONE]
- Updated AGENTS.md with Phase T completion context.
- Committed and pushed: `afc7c4f3`.

---

## Phase T Complete

All 7 sub-phases executed successfully. The simulation now has honest,
defensible stochasticity with deterministic disruption scenarios and
exploratory within-scenario noise parameters.

---

## Workflow Per Task Unit
1. Read this file → identify current unit.
2. Write detailed `plan.md` (English) for current unit only.
3. Context compact.
4. Execute `plan.md` (Builder → Verifier → Reviewer → self-refine).
5. Context compact.
6. Review completed work, mark done, move to next unit.
