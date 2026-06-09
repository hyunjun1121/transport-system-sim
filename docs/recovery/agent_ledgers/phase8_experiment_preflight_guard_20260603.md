# Phase 8 Experiment Preflight Guard Ledger

Date: 2026-06-03

Objective: prevent staged, compact, full, and multi-corridor pilot experiment
profiles from being mistaken for publication, acceptance, final-study, or
operational evidence while rail source decisions remain unresolved.

## Baseline

- Current scope: Phase 8 compact/full experiment preparation.
- Formal acceptance status: unchanged; no formal acceptance artifact was
  created.
- Claim boundary: non-sample runs may proceed only as explicitly
  engineering-only method checks when rail source decisions remain pending.

## Files Inspected

- `plan.md`
- `src/realworld/pilot_experiments.py`
- `scripts/run_pilot_experiments.py`
- `tests/test_realworld_pilot_experiments.py`
- `data/rail/rail_source_decision_manifest.json`

## Files Edited

- `plan.md`
- `src/realworld/pilot_experiments.py`
- `scripts/run_pilot_experiments.py`
- `tests/test_realworld_pilot_experiments.py`
- `docs/recovery/agent_ledgers/phase8_experiment_preflight_guard_20260603.md`

## Sub-Agent Review

Reviewer wave: GPT-5.5 xhigh read-only reviewers before the implementation
patch.

Findings accepted:

- The guard must live in the output-producing experiment API, not only in CLI
  wrappers or documentation.
- Non-sample profiles must block while rail source decisions are pending unless
  an explicit engineering-only bypass is supplied.
- Engineering-only bypasses must label rows and manifests as non-publication,
  non-acceptance, non-operational, non-final-study, and non-formal-acceptance.
- Manifest metadata must separate profile-design dimensions from executed
  dimensions so small override runs cannot look like full profile execution.
- Summary generation must reject mixed claim scopes inside one summary group.

Self-refine actions:

- Added `PilotExperimentPreflightError` and an API-level
  `assert_pilot_experiment_preflight()` barrier.
- Added `--engineering-only` and `--rail-source-decision-manifest-path` to the
  CLI runner.
- Added manifest flags for `publication_ready`, `final_study_ready`,
  `operational_use_allowed`, `formal_acceptance_evidence`,
  `profile_design_complete`, and `engineering_override_run`.
- Added design-vs-executed policy, scenario, seed, and row counts.
- Added SHA-bound rail source-decision manifest metadata to experiment
  manifests.
- Preserved scenario-level `p_fail_scale` during disruption-case conversion.
- Added explicit `disruption_mode` output and summary fields.
- Updated `plan.md` Immediate Next Actions so the Phase 8 guard is recorded as
  implemented review support rather than a still-pending implementation task.

## Verification

Commands run:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\pilot_experiments.py scripts\run_pilot_experiments.py tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python tests\test_realworld_pilot_smoke.py
.\.venv\Scripts\python tests\test_realworld_experiment_strategy_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python tests\test_realworld_pilot_statistics.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python scripts\run_pilot_experiments.py --help
```

Observed result: all commands above passed. The final repeated plan-audit run
was after the `plan.md` status update. The CLI help command showed the new
`--engineering-only` and `--rail-source-decision-manifest-path` options.

Additional search:

```powershell
rg -n "run_pilot_experiments\(" tests src scripts
rg -n "DEFAULT_STAGED_PROFILE_ID|run_profile=.*staged|pilot_staged|multi_corridor" tests src scripts
```

Observed result: direct API calls are concentrated in
`tests/test_realworld_pilot_experiments.py` and the CLI wrapper
`scripts/run_pilot_experiments.py`.

## Gate Decision

Proceed with Phase 8 engineering-only preparation. This closes the experiment
preflight guard implementation gap only. It does not close rail evidence,
experiment acceptance, final-study readiness, publication readiness, or formal
acceptance gates.
