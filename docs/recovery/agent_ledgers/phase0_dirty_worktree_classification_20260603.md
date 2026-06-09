# Phase 0 Dirty Worktree Classification Ledger - 2026-06-03

## Objective

Implement the `plan.md` hard guardrail requiring a machine-readable dirty and
untracked path classification ledger before new generated-output work, compact
runs, full runs, or cleanup.

## Scope

Edited files:

- `src/realworld/tracked_artifact_audit.py`
- `src/realworld/__init__.py`
- `scripts/write_dirty_worktree_classification.py`
- `scripts/audit_plan_artifacts.py`
- `tests/test_realworld_tracked_artifact_audit.py`
- `tests/test_realworld_plan_audit.py`
- `plan.md`
- `status.md`

Generated outputs:

- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`
- refreshed `data/validation/tracked_artifact_audit.csv`
- refreshed `data/validation/tracked_artifact_audit_manifest.json`
- refreshed `docs/tracked_artifact_audit.md`

## Implementation Summary

- Added a dirty-worktree classification ledger that uses
  `git status --short -uall` so untracked directories are expanded to files.
- Preserved leading-dot paths such as `.tmp_phase4_source_probe/...`.
- Made git-status failure produce a fail-closed classification row.
- Kept the ledger non-acceptance with `can_mark_complete=false`,
  `final_study_ready=false`, and `new_generated_output_allowed=false` whenever
  dirty paths exist.
- Added `scripts/write_dirty_worktree_classification.py` with
  `--fail-on-blockers`.
- Surfaced the ledger through `scripts/audit_plan_artifacts.py`.
- Added freshness verification that compares the saved CSV path set against the
  current `git status --short -uall` path set, not only row counts.

## Sub-Agent Review

Reviewer:

- GPT-5.5 xhigh frozen-diff reviewer `019e8db2-4b00-7511-904f-14c3f7a33d49`

Initial findings:

- ledger used collapsed untracked directories;
- leading-dot paths were normalized incorrectly;
- git-status failure was not fail-closed;
- plan audit surfaced the manifest but did not verify freshness or coverage.

Self-refine actions:

- switched dirty classification to `git status --short -uall`;
- fixed leading-dot path normalization;
- added fail-closed git-status failure rows;
- added saved/current path-set comparison in plan audit;
- added tests for same-count but different-path stale CSVs.

Final reviewer result:

- no blocker/high/medium findings;
- residual risk limited to not running the full repository-wide test suite.

## Commands Run

- `.\.venv\Scripts\python -m py_compile .\src\realworld\tracked_artifact_audit.py .\src\realworld\__init__.py .\scripts\write_dirty_worktree_classification.py .\scripts\audit_plan_artifacts.py .\tests\test_realworld_tracked_artifact_audit.py .\tests\test_realworld_plan_audit.py`
- `.\.venv\Scripts\python .\tests\test_realworld_tracked_artifact_audit.py`
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py --fail-on-blockers`
- `.\.venv\Scripts\python .\scripts\audit_tracked_artifacts.py`
- `.\.venv\Scripts\python .\scripts\audit_plan_artifacts.py`
- `git diff --check -- .\plan.md .\AGENTS.md .\agents.md .\status.md .\src\realworld\tracked_artifact_audit.py .\src\realworld\__init__.py .\scripts\write_dirty_worktree_classification.py .\scripts\audit_plan_artifacts.py .\tests\test_realworld_tracked_artifact_audit.py .\tests\test_realworld_plan_audit.py`

## Current Gate Result

The dirty worktree is classified, but generated-output promotion remains
blocked:

- the dirty classification ledger is fail-closed;
- `--fail-on-blockers` exits 1 while dirty paths remain;
- `audit_plan_artifacts.py` exits 0 only when the saved dirty ledger matches the
  current path set;
- Phase 9 remains blocked by artifact invalidation closeout rows.

This work does not close final-study, publication, clean-checkout
reproducibility, or formal acceptance gates.
