# Phase 8 Compact Engineering Probe Ledger

Date: 2026-06-03

Objective: execute the smallest bounded Phase 8 compact probe allowed by the
current evidence state, while preventing the output from being overread as
publication, final-study, Phase 9 promotion, operational, or formal acceptance
evidence.

## Gate Status

Decision: engineering-only compact probe completed.

This does not close Phase 8 as promotion evidence. Phase 9 promotion remains
blocked because rail source decisions remain pending and artifact invalidation
closeout remains unresolved.

## Files Inspected

- `plan.md`
- `src/realworld/pilot_experiments.py`
- `scripts/run_pilot_experiments.py`
- `tests/test_realworld_pilot_experiments.py`
- `tests/test_realworld_phase8_precompact_tables.py`
- `tests/test_realworld_reproducibility_smoke.py`
- `tests/test_realworld_experiment_strategy_readiness_packet.py`
- `data/manifests/pilot_experiment_design.json`
- `data/rail/rail_source_decision_manifest.json`
- `data/validation/artifact_invalidation_matrix_manifest.json`
- `data/validation/artifact_invalidation_closeout_manifest.json`
- `docs/recovery/agent_ledgers/phase8_experiment_preflight_guard_20260603.md`
- `docs/recovery/agent_ledgers/phase8_precompact_tables_20260603.md`

## Files Edited

- `src/realworld/pilot_experiments.py`
- `tests/test_realworld_pilot_experiments.py`
- `docs/recovery/runtime_preflight/phase8_compact_engineering_20260603.md`
- `docs/recovery/agent_ledgers/phase8_compact_engineering_probe_20260603.md`

## Generated Outputs

- `results/realworld_pilot/phase8_compact_engineering_20260603/pilot_staged_results.csv`
- `results/realworld_pilot/phase8_compact_engineering_20260603/pilot_staged_summary.csv`
- `results/realworld_pilot/phase8_compact_engineering_20260603/pilot_staged_manifest.json`
- `results/realworld_pilot/phase8_compact_engineering_20260603/pilot_staged_output_lock_receipt.json`

The compact probe generated 27 result rows and 9 summary rows:

- policies:
  `bus_only`, `baseline_multimodal`, `multimodal_lastmile_redundancy`;
- scenarios:
  `no_disruption`, `songpa_critical_link_blockage`,
  `songpa_last_mile_station_to_destination`;
- seeds: `8201`, `8202`, `8203`.

## Sub-Agent Review

Agents used:

- `019e8d51-3f24-7de0-a672-2671cc126ad6`, GPT-5.5 xhigh read-only Phase 8
  compact-run preflight reviewer.
- `019e8d51-7d37-7e33-a4fa-26dbedf1a33a`, GPT-5.5 xhigh read-only
  runner-manifest auditor.
- `019e8d51-c603-73d3-b2af-94bf75762366`, GPT-5.5 xhigh read-only
  validation/test planner.

Accepted findings:

- A non-sample compact/staged/full run cannot proceed as gate or promotion
  evidence while rail source decisions and artifact invalidation closeout remain
  unresolved.
- Any current compact probe must use `--engineering-only`, a fresh deterministic
  output directory, and explicit non-publication/non-acceptance/non-operational
  claim scope.
- The runner manifest needed stronger runtime evidence, actual worker count,
  output lock evidence, output inventory, explicit output directory, executed
  command with overrides, and config/input hashes.
- The verification ladder should start with narrow runner tests, then Phase 8
  table tests, core scenario/analysis tests, pilot smoke, reproducibility smoke,
  experiment strategy readiness, and tracked-artifact audit.

Self-refine actions:

- Added serial runtime metadata to pilot manifests:
  `actual_worker_count=1`, no tested worker controller, CPU simulation engine,
  RAM before/after, wall time, and no GPU simulation use.
- Added atomic output lock and retained output-lock receipt.
- Added explicit `output_dir`, `executed_command`, output inventory, input
  hashes, and config hashes.
- Added tests for runtime metadata, executed overrides, output lock receipt,
  output inventory, and config hashes.
- Wrote the runtime preflight note before executing the compact probe.

## Commands Run

Preflight and narrow implementation checks:

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\pilot_experiments.py .\scripts\run_pilot_experiments.py .\tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python .\tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python .\scripts\run_pilot_experiments.py --help
```

Compact probe:

```powershell
.\.venv\Scripts\python .\scripts\run_pilot_experiments.py --staged --output-dir .\results\realworld_pilot\phase8_compact_engineering_20260603 --seeds 8201,8202,8203 --policy-ids bus_only,baseline_multimodal,multimodal_lastmile_redundancy --scenario-ids no_disruption,songpa_critical_link_blockage,songpa_last_mile_station_to_destination --engineering-only
```

Post-run verification:

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\pilot_experiments.py .\scripts\run_pilot_experiments.py .\src\realworld\phase8_precompact_tables.py .\scripts\write_phase8_precompact_tables.py .\src\realworld\reproducibility_smoke.py .\src\realworld\tracked_artifact_audit.py
.\.venv\Scripts\python .\tests\test_realworld_phase8_precompact_tables.py
.\.venv\Scripts\python .\tests\test_scenario.py
.\.venv\Scripts\python .\tests\test_analysis.py
.\.venv\Scripts\python .\tests\test_realworld_pilot_smoke.py
.\.venv\Scripts\python .\tests\test_realworld_reproducibility_smoke.py
.\.venv\Scripts\python .\tests\test_realworld_experiment_strategy_readiness_packet.py
.\.venv\Scripts\python .\scripts\audit_tracked_artifacts.py
.\.venv\Scripts\python .\scripts\run_reproducibility_smoke.py --profile clean-checkout-minimal
```

Observed results:

- Python compile checks passed.
- `tests/test_realworld_pilot_experiments.py` passed.
- `tests/test_realworld_phase8_precompact_tables.py` passed.
- `tests/test_scenario.py` passed.
- `tests/test_analysis.py` passed.
- `tests/test_realworld_pilot_smoke.py` passed.
- `tests/test_realworld_reproducibility_smoke.py` passed.
- `tests/test_realworld_experiment_strategy_readiness_packet.py` passed.
- `scripts/run_reproducibility_smoke.py --profile clean-checkout-minimal`
  passed all 9 current-worktree smoke commands but reported
  `acceptance_ready=false`, `can_mark_complete=false`, and
  `clean_checkout_test_performed=false`.
- `scripts/audit_tracked_artifacts.py` completed and reported
  `clean_checkout_reproducibility_ready=false`,
  `blocking_change_count=248`, `modified_or_staged_count=135`, and
  `untracked_count=113`.

Additional manifest inspection:

- manifest `engineering_only=true`;
- manifest `phase8_preflight.status=engineering_only_bypass`;
- manifest `publication_ready=false`;
- manifest `final_study_ready=false`;
- manifest `formal_acceptance_evidence=false`;
- manifest `operational_use_allowed=false`;
- manifest `runtime.actual_worker_count=1`;
- manifest `runtime.gpu_used_for_simulation=false`;
- manifest `output_lock_release.release_status=released`;
- result CSV row count is 27 and summary CSV row count is 9;
- row-level and summary-level `claim_scope` both match manifest `result_scope`.

`git diff --check` on the touched runner/test/preflight paths reported no
whitespace errors, only CRLF conversion warnings for the Python files.

## Residual Risks And Blockers

- This compact output is engineering-only and cannot support Phase 9 promotion.
- Rail source-decision evidence remains pending.
- Artifact invalidation closeout remains unresolved.
- The worktree remains dirty and untracked-heavy; clean-checkout
  reproducibility is not ready.
- Formal acceptance artifacts are still absent.
- The simulation runner remains serial for compact/full profiles until a tested
  worker-count controller exists.
- GPU was not used for simulation and must not be claimed.

## Next Action

Do not start Phase 9 as promotion evidence. Continue with artifact
invalidation closeout, rail source-decision evidence, and clean-checkout
reproducibility blockers before any full-run promotion.
