# Phase 11 Graph-Scale Manifest Audit Claim-Boundary Sprint - 2026-06-04

## Scope

This ledger covers claim-language cleanup for the generated graph-scale manifest audit artifacts:

- `src/realworld/graph_scale_manifest_audit.py`
- `tests/test_realworld_graph_scale_manifest_audit.py`
- `data/validation/graph_scale_manifest_audit.csv`
- `data/validation/graph_scale_manifest_audit_manifest.json`
- `docs/graph_scale_manifest_audit.md`

The change narrows graph-scale method wording only. It does not change source graph counts, analysis graph counts, coverage status rows, experiment outputs, or formal graph-scale gate status.

## Preflight Evidence

- `rg` located the generator, writer script, tests, and integration references:
  - `src/realworld/graph_scale_manifest_audit.py`
  - `scripts/audit_graph_scale_manifests.py`
  - `tests/test_realworld_graph_scale_manifest_audit.py`
  - `scripts/run_acceptance_audit.py`
- Full guard before this sprint reported 13 release-blocking unbounded findings for `docs/graph_scale_manifest_audit.md`.
- Guard rows showed the blockers were repeated `required_reviewer_action` table values using graph-scale acceptance wording.

## Changes Made

- Reworded the manifest claim boundary from accept/validate/calibrate/final-study wording to select/confirm/tune/study-gate wording.
- Reworded review items:
  - final method -> selected method
  - accepted graph-scale method -> selected graph-scale method
  - accepted graph-scale decision -> selected graph-scale decision
- Reworded Markdown boundary text from accepted final method to selected method.
- Reworded `_required_action(...)` outputs:
  - graph-scale acceptance -> graph-scale decision record
  - acceptance -> graph-scale decision record
- Updated the test claim-boundary assertion to match the new wording.

## Commands Run

```powershell
.\.venv\Scripts\python .\tests\test_realworld_graph_scale_manifest_audit.py
.\.venv\Scripts\python .\scripts\audit_graph_scale_manifests.py 2>&1
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\graph_scale_manifest_audit.md --scan-path .\data\validation\graph_scale_manifest_audit_manifest.json --scan-path .\data\validation\graph_scale_manifest_audit.csv --output .\.tmp_graph_manifest_guard.csv --manifest .\.tmp_graph_manifest_guard.json --doc .\.tmp_graph_manifest_guard.md
Remove-Item -LiteralPath .\.tmp_graph_manifest_guard.csv, .\.tmp_graph_manifest_guard.json, .\.tmp_graph_manifest_guard.md -ErrorAction SilentlyContinue
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\graph_scale_manifest_audit.md --scan-path .\data\validation\graph_scale_manifest_audit_manifest.json --output .\.tmp_graph_manifest_guard.csv --manifest .\.tmp_graph_manifest_guard.json --doc .\.tmp_graph_manifest_guard.md
Remove-Item -LiteralPath .\.tmp_graph_manifest_guard.csv, .\.tmp_graph_manifest_guard.json, .\.tmp_graph_manifest_guard.md -ErrorAction SilentlyContinue
.\.venv\Scripts\python .\scripts\run_acceptance_audit.py 2>&1
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_graph_scale_manifest_audit.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\src\realworld\graph_scale_manifest_audit.py .\tests\test_realworld_graph_scale_manifest_audit.py .\data\validation\graph_scale_manifest_audit.csv .\data\validation\graph_scale_manifest_audit_manifest.json .\docs\graph_scale_manifest_audit.md .\data\manifests\acceptance_orchestration_manifest.json .\docs\review_packets\acceptance_review_index.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md
```

## Observed Results

- `tests/test_realworld_graph_scale_manifest_audit.py` passed.
- `scripts/audit_graph_scale_manifests.py` exited 0 and emitted:
  - `row_count: 13`
  - `audited_manifest_count: 12`
  - `missing_or_incomplete_row_count: 0`
  - `complete_graph_scale_row_count: 13`
  - `source_graph_node_counts: [4608]`
  - `analysis_graph_node_counts: [118, 164]`
  - `publication_ready: false`
  - `can_mark_complete: false`
- The first focused guard included the CSV path and reported one unsupported scan target for `.csv`; this was a guard-target selection issue, not a generated text blocker.
- Focused guard rerun on Markdown and manifest JSON reported:
  - `blocking_finding_count: 0`
  - `release_blocked: false`
  - `claim_language_guard_ready: true`
- `scripts/run_acceptance_audit.py` exited 0 and regenerated integrated review artifacts.
- Full claim-language guard after this sprint reported:
  - `blocking_finding_count: 305`
  - `release_blocked: true`
  - `claim_language_guard_ready: false`
- CSV check confirmed:
  - `docs/graph_scale_manifest_audit.md` release blockers: 0
  - `data/validation/graph_scale_manifest_audit_manifest.json` release blockers: 0
- Remaining top blocker sources after this sprint included:
  - `docs/human_acceptance_runbook.md`: 13
  - `docs/analysis_corridor_method_note.md`: 12
  - `docs/acceptance_task_assignments.md`: 11
  - `docs/validation_review_packet.md`: 10
- `tests/test_realworld_claim_language_guard.py` passed.
- `tests/test_realworld_plan_audit.py` passed.
- `git diff --check` exited 0 with LF-to-CRLF warnings only.
- Dirty worktree classification reported 422 classified paths and 0 unclassified paths.

## Residual Risk

This sprint clears the graph-scale manifest audit surfaces only. The manifest audit remains visibility evidence and cannot select a graph-scale method or close the graph-scale gate.
