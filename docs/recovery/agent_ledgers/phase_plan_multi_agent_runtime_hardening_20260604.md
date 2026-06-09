# Plan Multi-Agent Runtime Hardening Sprint - 2026-06-04

## Scope

This sprint hardened `plan.md` as the active implementation workflow. The
changes focused on dependency-aware GPT-5.5 xhigh sub-agent orchestration,
fail-closed runtime evidence, RTX 3090 claim boundaries, micro-probe evidence,
and sprint ledger requirements.

No study-closeout, publication, reproducibility, calibration, field-use,
artifact-promotion, or formal human-review gate was closed.

## Preflight Evidence

Inspected files and commands:

- `git status --short --branch`
- `plan.md`
- `tests/test_realworld_plan_audit.py`
- `scripts/check_gpu_ml_runtime.py`
- `scripts/run_full_graph_smoke.py`
- `scripts/run_pilot_smoke.py`
- existing sprint ledgers under `docs/recovery/agent_ledgers/`
- `data/validation/dirty_worktree_classification_manifest.json`

The worktree was already broadly dirty before this sprint. This sprint's
intended edit scope was limited to `plan.md` and this ledger.

## Agent Wave

Two GPT-5.5 xhigh read-only reviewers were used.

| Agent | Role | Scope | Result |
| --- | --- | --- | --- |
| `019e8ec9-e74a-75d3-926e-8150aa4feb2a` | orchestration reviewer | `plan.md`, `tests/test_realworld_plan_audit.py` | Recommended adding wave/order and barrier evidence fields to sub-agent prompt templates, and clarifying that phase rosters are not execution order. |
| `019e8eca-acdf-7ab2-8d1b-2952effcc792` | runtime/GPU rigor reviewer | `plan.md`, GPU/runtime scripts found with `rg` | Recommended fail-closed GPU runtime wording, runtime manifest evidence fields, micro-probe boundaries for `run_pilot_smoke.py`, and non-substitutive wording for readiness/decision packets. |

Both agents were read-only. Both were closed after their findings were
integrated.

## Changes

`plan.md` now states that:

- phase sub-agent rosters are planning inventories, not execution order;
- every listed phase agent must be mapped in the phase ledger to F1 scout, F3
  builder, or F5 reviewer roles;
- each agent task needs explicit parallel group, prerequisite barrier,
  sequential-after task IDs when applicable, re-check cadence, and released
  write locks;
- standard sub-agent prompt templates include `Wave/order` and
  `Barrier evidence required before start`;
- `scripts\run_pilot_smoke.py` is cached-input development smoke only, not F7
  micro-probe or compact-gate evidence unless wrapped with deterministic rerun,
  one disruption case, CRN pairing, runtime, memory, hashes, row counts, and
  claim boundary;
- full experiment promotion needs runtime smoke manifests with
  `preflight_manifest_path`, `worker_count`, peak memory, wall time,
  input/output hashes, row counts, and claim boundary;
- RTX 3090 / CUDA wording requires `scripts\check_gpu_ml_runtime.py` with
  `--requirements requirements-ml.txt --require-gpu --fail-on-blockers`;
- readiness and decision packets are summaries only, and promotion still
  requires underlying command logs, source manifests, hashes, row counts, and
  pass/fail criteria;
- the audit command reference now includes
  `scripts\check_gpu_ml_runtime.py --package xgboost --requested-device cuda --requirements requirements-ml.txt --require-gpu --fail-on-blockers`.

## Verification Commands

```powershell
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\plan.md
git diff --stat -- .\plan.md
git diff -- .\plan.md
```

Observed results:

- `tests\test_realworld_plan_audit.py` passed.
- `git diff --check -- .\plan.md` exited 0.
- Git emitted an LF-to-CRLF working-copy warning for `plan.md`; no whitespace
  error was reported.

## Residual Risk

This sprint changed the plan, not the implementation scripts. Reviewer findings
about `run_full_graph_smoke.py`, `run_pilot_smoke.py`, and GPU runtime evidence
were captured as workflow requirements in `plan.md`; implementing those script
manifest improvements remains a future dependency-safe slice.

The broader worktree remains dirty and untracked in many paths. Dirty-worktree
classification must be refreshed after this ledger and before any generated
output promotion or cleanup.
