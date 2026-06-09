# Phase 8 Pre-Compact Tables Ledger

Date: 2026-06-03

Objective: add pre-compact policy feasibility/fairness and external benchmark
threshold tables before staged, compact, multi-corridor, or full experiment
promotion.

## Baseline

- Current scope: Phase 8 compact-experiment preparation.
- Formal acceptance status: unchanged; no formal acceptance artifact was
  created.
- Claim boundary: the tables are review support only. They are not policy
  acceptance, validation acceptance, calibrated real-world evidence,
  final-study approval, or operational routing/dispatch guidance.

## Files Inspected

- `plan.md`
- `data/scenarios/policy_alternatives.csv`
- `data/manifests/pilot_experiment_design.json`
- `data/regions/pilot_region.yaml`
- `data/validation/external_route_benchmarks.csv`
- `data/validation/external_route_benchmarks_osrm.csv`
- `data/validation/osrm_route_benchmark_manifest.json`
- `src/realworld/pilot_experiments.py`
- `src/realworld/policy_alternatives.py`
- `src/realworld/plausibility.py`
- `src/realworld/validation_benchmark_decision_packet.py`
- `tests/test_realworld_policy_alternatives.py`
- `tests/test_realworld_pilot_experiments.py`
- `tests/test_realworld_validation_benchmark_decision_packet.py`

## Files Edited

- `plan.md`
- `src/realworld/phase8_precompact_tables.py`
- `scripts/write_phase8_precompact_tables.py`
- `tests/test_realworld_phase8_precompact_tables.py`
- `data/validation/policy_feasibility_fairness_table.csv`
- `data/validation/policy_feasibility_fairness_manifest.json`
- `docs/policy_feasibility_fairness_table.md`
- `data/validation/benchmark_threshold_table.csv`
- `data/validation/benchmark_threshold_manifest.json`
- `docs/benchmark_threshold_table.md`
- `docs/recovery/agent_ledgers/phase8_precompact_tables_20260603.md`

## Sub-Agent Review

Reviewer wave: two GPT-5.5 xhigh read-only reviewers before self-refinement.

Accepted policy feasibility findings:

- Use one row per policy and compare each row against the same-mode baseline:
  `bus_only` or `baseline_multimodal`.
- Include vehicle/fleet assumptions, service-minute budget status, route legs,
  route-check IDs, transfer burden, rerouting authority, dispatch/routing
  adaptation, feasibility status, fairness status, and claim-boundary fields.
- `staggered_or_adaptive_dispatch` is a deterministic dispatch variant only,
  not adaptive route optimization.
- `bus_corridor_redundancy` remains excluded until a documented redundant
  corridor graph variant is reviewed.
- `fleet_shortage_stress` is currently a no-effect policy under the pilot base
  config because 0.75 multipliers round the shuttle fleet 3 back to 3 and
  last-mile fleet 2 back to 2.

Accepted benchmark threshold findings:

- Predeclare road duration and distance thresholds before compact execution.
- Include rail/transit travel-time, headway, and itinerary thresholds even
  while rail source decisions remain pending.
- Include transfer fixed-delay, per-passenger-delay, and boarding/station
  process-coverage thresholds.
- Include source-pinning, post-hoc-change, and downstream claim-boundary
  thresholds.
- OSRM rows are cached external-router snapshots with raw payloads and zero
  unpinned rows, but remain review-only. Fallback rows remain documented
  executable fallbacks, not ground truth.

Self-refine actions:

- Added `src/realworld/phase8_precompact_tables.py`.
- Added `scripts/write_phase8_precompact_tables.py`.
- Added `tests/test_realworld_phase8_precompact_tables.py`.
- Generated the two CSV tables, manifests, and Markdown docs.
- Revised bus-only rows so multimodal-only and rail-only fields use
  `not_applicable`.
- Updated `plan.md` Immediate Next Actions to record this work as implemented
  review support, not a still-pending task.

## Verification

Commands run:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\phase8_precompact_tables.py scripts\write_phase8_precompact_tables.py tests\test_realworld_phase8_precompact_tables.py
.\.venv\Scripts\python scripts\write_phase8_precompact_tables.py
.\.venv\Scripts\python tests\test_realworld_phase8_precompact_tables.py
.\.venv\Scripts\python tests\test_realworld_validation_benchmark_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_policy_alternatives.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python scripts\write_phase8_precompact_tables.py --help
.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py
```

Observed result: all commands above passed.

## Gate Decision

Proceed with Phase 8 engineering-only preparation only. These tables satisfy
the pre-compact review-table requirement, but they do not close road evidence,
rail evidence, validation acceptance, experiment acceptance, publication
readiness, final-study readiness, or formal acceptance gates.
