# Phase T: Stochasticity Redesign & Honest Rebuild

## Mission

Fix the design errors introduced in Phase S, rebuild the simulation with
scientifically grounded stochasticity, and produce a paper/report that makes
only defensible claims.

## Lessons Learned (Phase S Retrospective)

### What went wrong

1. **Mechanism A (probabilistic edge disruption) damages scenario semantics.**
   Setting `selection_p_fail=0.8` means "songpa_rail_unavailable" has a 20%
   chance of rail working — that is not what the scenario is supposed to test.
   Disruption scenarios are controlled experiments; making them probabilistic
   conflates two sources of uncertainty that should be separated.

2. **Mechanism B & C parameters are arbitrary.** `sigma=0.05` and `lambda=0.2`
   have no empirical basis. The variance they create is not a measurement of
   real uncertainty — it is an artifact of chosen numbers. Presenting CI from
   arbitrary noise as "genuine estimates of stochastic uncertainty" (paper
   §9.9) is worse than honestly reporting a deterministic model.

3. **Process flaw: treated a design change as a bug fix.** Zero variance was
   not necessarily a bug — it was a deterministic model behaving correctly.
   The fix should have started from "what uncertainty sources exist and how
   should we model them?", not "make numbers different."

4. **Paper overclaiming.** §9.9 says "genuine estimates of stochastic
   uncertainty" about variance from uncalibrated parameters. This is an
   unsupported claim.

### What went right

- Severity ladder rankings preserved (qualitative conclusions are robust).
- Claim boundary (§9.11) remains honest about decision-support framing.
- Morris sensitivity now produces non-zero mu_star (19,623 vs previously 0).
- Test suite stays green (162/163; plan_audit is dirty-worktree count only).
- Self-refine protocol caught parameter issues early in Phase S2.

### Core value reminder

> Rail-bus multimodal transport is a **conditional resilience strategy**.
> The simulation compares modal alternatives under controlled disruption
> scenarios. The value is in the **comparison structure** (which conditions
> favor multimodal, which favor bus-only), not in point estimates of travel
> time or CI precision.

## Environment

| Resource | Value |
|----------|-------|
| CPU | Ryzen 7 5800X3D 8C/16T |
| RAM | 64 GB |
| GPU | RTX 3090 24 GB (CUDA 8.6, driver 610.47) |
| Python | 3.12.10 via `.\.venv\Scripts\python` |
| XGBoost | 3.2.0 `tree_method='hist', device='cuda'` (verified) |
| SALib | 1.5.2 |
| NumPy | 2.4.6, SciPy 1.17.1, Pandas 3.0.3, NetworkX 3.6.1 |
| No PyTorch | Only XGBoost CUDA available |

Hardware exploitation:
- RTX 3090: XGBoost GPU training only. Simulator is CPU-bound.
- 16 logical cores: seed-level parallelism feasible.
- 64 GB RAM: 12 parallel workers × ~50 MB graph ≈ 600 MB, trivial.
- `joblib.parallel_backend('threading')` for SALib Morris trajectories.

## Stop Conditions

1. Disruption scenarios are **deterministic within scenario** (Mechanism A
   reverted). Seed variance comes only from passenger arrivals, road noise,
   and turnaround noise.
2. Road noise and turnaround noise are either (a) empirically grounded or
   (b) explicitly framed as sensitivity parameters with a sweep showing how
   conclusions change.
3. Paper contains zero false stochastic claims. Every CI is traceable to an
   explicitly documented uncertainty source.
4. Claim guard: `blocking_finding_count=0` (excluding plan.md "final" words).
5. 162/163 tests pass (plan_audit dirty-worktree exclusion accepted).
6. Two independent sub-agent reviewers confirm data-consistency and narrative
   coherence with zero critical findings.

## Sub-Agent Architecture

```
Builder   — reads data, writes code/files, runs experiments
Reviewer  — read-only auditor, returns findings, never writes
Verifier  — runs tests/guards, returns pass/fail + counts
```

Rules:
- Builder outputs must pass Verifier before any Reviewer sees them.
- Reviewer findings with severity >= critical block downstream phases.
- Self-refine: up to 3 fix cycles before escalation.
- Every phase gate requires Verifier + Reviewer pass.

## Phase Overview (Sequential Gates)

```
T1 ──► T2 ──► T3 ──► T4 ──► T5 ──► T6 ──► T7
^       ^       ^       ^       ^       ^       ^
revert  verify  re-run  truth   paper   final   close
mech A  +param  exper   rebuild update review   out
        sweep
```

---

## Phase T1: Revert Mechanism A & Redesign Stochasticity

### Goal

Restore deterministic disruption scenarios while keeping road noise and
turnaround noise as the two stochasticity mechanisms. Reframe B and C as
sensitivity parameters rather than calibrated defaults.

### Design Decisions

1. **Revert `graph_with_forced_disruption_probabilities`:** Pilot experiments
   always call with `force_deterministic=True`. The `False` mode is kept as
   dead code for potential future use but is not called anywhere.
2. **Keep Mechanisms B and C** (road noise, turnaround noise) as the sole
   sources of within-scenario seed variance.
3. **Add `road_noise_sigma` and `turnaround_noise_lambda` to the Morris
   parameter space** so sensitivity analysis reveals whether these parameters
   affect conclusions. If conclusions are robust across sigma/lambda values,
   that is a finding. If they are sensitive, that is also a finding.
4. **Document the uncertainty model honestly:** The paper must say "within each
   disruption scenario, seed variance reflects operational variability in road
   travel time and fleet turnaround. These parameters are exploratory; see
   sensitivity analysis for their influence on conclusions."

### Implementation Workflow

1. **Builder** reverts `graph_with_forced_disruption_probabilities` call in
   `pilot_experiments.py` to always use `force_deterministic=True`.
2. **Builder** updates `make_pilot_base_config()` to keep stochastic config
   for B and C, but remove any reference to probabilistic edge disruption.
3. **Builder** adds `road_noise_sigma` and `turnaround_noise_lambda` to the
   Morris parameter bounds in `src/realworld/sensitivity.py` (both currently
   fixed; they should become variable parameters with ranges like
   `sigma ∈ [0.0, 0.15]`, `lambda ∈ [0.0, 0.5]`).
4. **Verifier** runs full test suite. All 162/163 must pass.
5. **Self-refine:** If tests fail, Builder fixes and re-verifies (max 3 loops).

### Verification Gate

- `force_deterministic=True` confirmed in all pilot experiment call paths.
- Test suite green.
- Code search confirms no caller uses `force_deterministic=False`.

---

## Phase T2: Variance Verification & Parameter Sweep Design

### Goal

Prove that the two-mechanism stochasticity (B+C only) produces sufficient
variance, and design the parameter sweep that will test sensitivity to those
parameters.

### Sub-Agent Workflow

**Sequential: Builder → Verifier → Reviewer.**

1. **Builder** writes a variance diagnostic script (or extends existing):
   - Run 10 seeds for 5 representative (policy, scenario) pairs:
     `(bus_only, no_disruption)`,
     `(baseline_multimodal, no_disruption)`,
     `(heavy_congestion_bus, songpa_spatial_tancheon_corridor)`,
     `(baseline_multimodal, songpa_critical_link_blockage)`,
     `(severe_congestion_bus, songpa_rail_delay)`.
   - At each of 3 sigma values (0.0, 0.05, 0.10) and 3 lambda values
     (0.0, 0.2, 0.4), i.e. 9 parameter combinations.
   - Report: unique makespan count, makespan range, CI width per combo.
   - This is a 5×9×10 = 450-run grid, estimated <1 minute.

2. **Verifier** checks:
   - At current defaults (sigma=0.05, lambda=0.2), each non-inf group has
     >= 3 unique makespans from 10 seeds.
   - At sigma=0.0, lambda=0.0, verify variance drops to near-zero (confirms
     B and C are the actual variance sources, not some other leak).
   - At sigma=0.10, lambda=0.4, verify variance increases but does not
     produce physically implausible swings (no 10x makespan jumps).

3. **Reviewer** (read-only) inspects diagnostic output and confirms:
   - Variance source attribution is correct (B+C are the drivers).
   - Variance magnitude is physically plausible across the sweep.
   - The parameter ranges are sensible for a sensitivity study.
   - Zero critical findings required.

4. **Self-refine:** If default variance is insufficient, Builder may increase
   sigma or lambda slightly and re-verify. Loop up to 3 times.

---

## Phase T3: Full Re-Experimentation & Extended Morris

### Goal

Re-run the full experiment with reverted Mechanism A, then run an extended
Morris sensitivity that includes sigma and lambda as parameters.

### Execution Strategy

1. **Full experiment re-run:**
   - 23P × 23S × 30 seeds = 15,870 runs.
   - ProcessPoolExecutor with 10-12 workers.
   - Estimated ~15 minutes.

2. **Extended Morris sensitivity:**
   - Add `road_noise_sigma` and `turnaround_noise_lambda` to the Morris
     parameter space alongside existing parameters.
   - Re-run Morris with the extended parameter set.
   - This directly answers: "do conclusions depend on the choice of noise
     parameters?"

3. **Statistics regeneration:**
   - `make_pilot_statistics.py` for CIs and paired deltas.
   - `run_ml_analysis.py` for XGBoost risk classification (GPU-accelerated).
   - `make_pilot_figures.py` for updated plots.

### Sub-Agent Workflow

1. **Builder** runs the full experiment.
2. **Builder** runs extended Morris.
3. **Builder** regenerates all downstream artifacts (statistics, ML, figures).
4. **Verifier** runs:
   - Row count = 15,870 in results CSV.
   - Summary row count = 529.
   - No zero-variance groups where finite makespan is expected.
   - Morris output has non-zero mu_star for sigma/lambda parameters.
   - Full test suite passes.
5. **Self-refine:** If Morris indices for sigma/lambda are unexpectedly zero,
   investigate and potentially widen parameter ranges.

---

## Phase T4: Truth Table Rebuild & Data Audit

### Goal

Regenerate the single source of truth and verify all downstream data artifacts.

### Sub-Agent Workflow

**Sequential: Builder → Verifier → Reviewer.**

1. **Builder** regenerates:
   - `data/validation/summary_truth_table.csv` (529 rows).
   - `data/validation/summary_truth_manifest.json` with new SHA256.
   - All review packets, sensitivity packets, and strategy packets that
     reference counts or statistics.

2. **Verifier** runs structural checks:
   - Truth table row count = 529.
   - 23 policies × 23 scenarios cross-product complete.
   - Spot-check 40 random rows against source CSV.
   - Severity ladder **rankings** preserved (same qualitative ordering).
   - Full test suite (162/163).

3. **Reviewer** (read-only) performs independent data audit:
   - Sample 40 truth-table values, verify against raw results.
   - Inf rows and CR=0 rows internally consistent.
   - CI widths non-zero for all non-inf groups.
   - Spatial overlay rankings preserved.
   - Zero critical findings required.

4. **Self-refine:** If Reviewer finds issues, Builder investigates and fixes.

---

## Phase T5: Paper & Report Correction

### Goal

Update all paper and report prose to honestly describe the stochasticity model,
remove all false claims, and report the sensitivity of conclusions to noise
parameters.

### Changes Required

**Paper (`paper/paper_draft.md`):**

1. **Rewrite §9.9 (Seed Variance):** Replace Mechanism A description. State
   honestly that disruption scenarios are deterministic by design, and within-
   scenario variance comes from road noise (sigma) and turnaround noise
   (lambda). Report actual variance statistics from T3 results. Do NOT claim
   "genuine estimates of stochastic uncertainty" unless the Morris sweep
   proves conclusions are robust across parameter choices.
2. **Rewrite §10.7:** Describe the honest uncertainty model. If Morris shows
   sigma/lambda have low influence on mu_star for key outcomes, state that
   as a finding ("conclusions are robust to noise parameter choice"). If
   they have high influence, state that as a limitation.
3. **Update all truth-commented numerical values** in §9.1–§9.12, §10.9.
4. **Add a paragraph or subsection on stochasticity sensitivity:** Report
   Morris mu_star for sigma and lambda parameters across key metrics.
5. **Update Abstract** if it references specific numbers.
6. **Preserve** all structural findings (spatial overlay, disruption-location
   matrix, conditional resilience thesis).

**Report (`report_draft.md`):**

1. Mirror all paper numerical changes in Korean.
2. Regenerate `report.docx`.

### Sub-Agent Workflow

**Sequential phases within T5:**

1. **Builder** — Paper update:
   - Update all numerical values from new truth table.
   - Rewrite §9.9 and §10.7 with honest stochasticity framing.
   - Add Morris sigma/lambda sensitivity results.
   - Run claim guard.

2. **Builder** — Report update:
   - Update Korean prose.
   - Regenerate report.docx.

3. **Verifier** — Full test suite + claim guard (0 non-plan blockers).

4. **Reviewer #1 (data-truth)** — Verify 40 paper + 40 report numerical
   claims against truth table. Zero tolerance for mismatches.

5. **Reviewer #2 (narrative coherence)** — Full paper read-through:
   - Abstract matches results.
   - No false stochastic claims ("genuine estimates" must be removed or
     qualified with "under the chosen parameter values").
   - Sensitivity results honestly reported.
   - Claim boundary respected.
   - Zero critical findings required.

6. **Self-refine:** If any Reviewer reports >=moderate findings, Builder
   fixes and re-submits (max 3 loops).

---

## Phase T6: Final Verification & Independent Audit

### Goal

Complete independent verification that all stop conditions are met.

### Sub-Agent Workflow

**Parallel Reviewers after sequential Builder+Verifier pass.**

1. **Verifier** runs:
   - Full test suite (162/163 pass).
   - Claim guard (`blocking_finding_count=0` excluding plan.md).
   - Truth table integrity.
   - Report.docx freshness (newer than report_draft.md).
   - Confirm `force_deterministic=True` in all pilot call paths.

2. **Reviewer #1 (simulation integrity)** — Read-only audit:
   - Mechanism A reverted (no probabilistic edge disruption).
   - Mechanisms B and C correctly implemented.
   - Morris includes sigma/lambda as parameters.
   - Backward compatibility for existing tests maintained.

3. **Reviewer #2 (paper completeness)** — Read-only audit:
   - All numbers trace 1:1 to truth table.
   - No false stochastic claims.
   - Sensitivity to noise parameters honestly reported.
   - Severity ladder rankings preserved.
   - Conditional resilience thesis still supported.

4. **Reviewer #3 (report quality)** — Read-only audit:
   - Korean report matches paper findings.
   - No numerical inconsistencies between paper and report.
   - Claim boundary in Korean text respected.

5. All three Reviewers must report **zero critical findings**.
   Moderate findings trigger self-refine (max 3 iterations).

---

## Phase T7: Closeout

### Goal

Finalize all artifacts and update handoff documents.

### Steps

1. **Builder** updates `status.md` with corrected experiment design.
2. **Builder** updates `AGENTS.md` with full current context.
3. **Verifier** runs final full test suite + claim guard.
4. **Verifier** confirms `final_study_ready=false` (structural) and
   `blocking_finding_count=0`.
5. **Reviewer** confirms all stop conditions met.

---

## Self-Refine Protocol

At every Verifier/Reviewer gate, if the check fails:

1. Builder receives the specific failure report.
2. Builder makes the minimum fix.
3. Verifier re-runs the failing check.
4. Repeat up to 3 times.
5. If still failing after 3 iterations, escalate: halt and report blocker.

## Key Design Decisions

1. **Deterministic disruption scenarios:** Scenarios test specific conditions.
   Making them probabilistic conflates scenario uncertainty with realization
   uncertainty. Keep them separate.
2. **Two-mechanism stochasticity (B+C only):** Road noise and turnaround noise
   create operational variability within a controlled scenario. Their
   parameters are exploratory, not calibrated.
3. **Morris includes noise parameters:** The sensitivity analysis itself tests
   whether conclusions depend on noise parameter choices. This is the
   scientifically honest way to handle uncalibrated parameters.
4. **Backward compatibility:** Existing tests use `force_deterministic=True`
   and `sigma=0.0`. Only pilot experiments enable stochasticity.
5. **Truth table as single source:** All paper/report numbers trace to
   `summary_truth_table.csv` via HTML comment annotations.
6. **No human review gates:** Sub-agent Reviewers provide independent audit.
   Their findings are review guidance, not formal acceptance.

## Expected Outcomes

After Phase T completes:
- Simulation has honest, defensible stochasticity (B+C only, A reverted).
- Paper makes zero false claims about variance sources.
- Morris sensitivity quantifies influence of noise parameters on conclusions.
- If conclusions are robust across noise parameter sweep → strong finding.
- If conclusions are sensitive → honest limitation, worth reporting.
- All artifacts internally consistent (truth table → paper → report).
