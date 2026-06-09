# Phase 8 Micro-Probe Profile Input Verification Ledger - 2026-06-08

## Scope

Verified the Phase 8 executable micro-probe after Phase 5 demand and fleet
profiles were connected to the pilot runtime.

This ledger records execution evidence only. It does not close compact,
publication, formal acceptance, or final-study gates.

## Current Evidence

- `results/realworld_pilot/phase8_micro_probe/phase8_micro_probe_manifest.json`
  records `micro_probe_execution_ready=true`.
- The manifest records two result rows and two summary rows:
  - two policies;
  - one scenario;
  - one seed;
  - one worker.
- Deterministic rerun hashes match:
  - results SHA256:
    `6275e1cda9981d30b1083d33b476f603e539045222781bed007df29770035eba`;
  - summary SHA256:
    `c7725973bb2d8424c1d55b7ab5ee51c94f6f5cc3d580e6f21613e0c6dc79a4f3`.
- Phase 5 runtime profile inputs were consumed in both primary and rerun
  manifests:
  - demand profile ID: `pilot_default_demand`;
  - fleet profile ID: `pilot_default_fleet`;
  - demand profile SHA256:
    `976f0e60c90928d5eaeaf6a242b577af8d61f120f2a75e33bb6748090b617cf0`;
  - fleet profile SHA256:
    `c358554d54c3b879e720bced56ee3325337f5f7f32a71954ddc99cc3ca722991`.
- Runtime preflight was present and ready for `execution_scope=micro_probe`.

## Verification Commands

- `.\.venv\Scripts\python tests\test_realworld_phase8_micro_probe.py`
  - passed.
- `.\.venv\Scripts\python tests\test_realworld_runtime_preflight.py`
  - passed.
- `.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py`
  - passed.
- `.\.venv\Scripts\python tests\test_realworld_demand_fleet_behavior_profiles.py`
  - passed.
- `.\.venv\Scripts\python scripts\audit_claim_language.py --fail-on-blockers`
  - passed with `blocking_finding_count=0`.
- `.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py`
  - passed as an audit command, but reported `formal_acceptance_ready=false`,
    `ready_gate_count=0`, and `blocked_gate_count=12`.
- `.\.venv\Scripts\python scripts\audit_final_study_readiness.py`
  - passed as an audit command, but reported `final_study_ready=false`, three
    ready gates, and twelve blocked gates.
- `.\.venv\Scripts\python scripts\write_dirty_worktree_classification.py`
  - passed and refreshed dirty-worktree classification to 775 classified dirty
    paths, zero unclassified paths, and `final_study_ready=false`.
- `.\.venv\Scripts\python tests\test_realworld_plan_audit.py`
  - first run failed because the dirty-worktree classification manifest was
    stale after generated audit outputs changed;
  - after refreshing dirty classification, the test passed.

## Residual Blockers

- The micro-probe remains execution evidence only and cannot promote compact or
  full outputs.
- Formal acceptance artifacts remain absent for all twelve formal gates.
- Final-study readiness remains false.
- Rail source decisions remain pending.
- Artifact invalidation still blocks Phase 9 promotion.
- Profile rows remain bounded engineering assumptions, not calibration
  evidence.

## Follow-Up Phase-Gate Ledger Update

After the micro-probe evidence was verified, the Phase 8 phase-gate ledger was
updated from a generated `blocked` template to `ready_for_review`.

Updated file:

- `data/manifests/phase_gates/phase8_compact_experiment_gate.json`

The update is intentionally not a closure:

- `status=ready_for_review`;
- `gate_decision=ready_for_review`;
- `can_mark_complete=false`;
- `final_study_ready=false`.

Additional verification:

- `.\.venv\Scripts\python -c "from src.realworld.phase_gate_ledger import load_phase_gate_ledger; ..."`
  - passed and reported `ready_for_review`, eight command records, and three
    artifact hashes.
- `.\.venv\Scripts\python tests\test_realworld_phase_gate_ledger.py`
  - passed.
- `.\.venv\Scripts\python scripts\write_phase_gate_ledgers.py`
  - passed and preserved the Phase 8 `ready_for_review` ledger.
  - audit status counts became `blocked: 12`, `ready_for_review: 1`.
- `.\.venv\Scripts\python tests\test_realworld_plan_audit.py`
  - passed.
