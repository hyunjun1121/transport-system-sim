# Phase 11 Formal Package Claim-Boundary Sprint - 2026-06-04

## Scope

This ledger covers claim-language cleanup for the generated formal package intake artifacts:

- `data/manifests/formal_acceptance_package_audit.json`
- `docs/formal_acceptance_package_audit.md`
- `src/realworld/formal_acceptance_package.py`
- `tests/test_realworld_formal_acceptance_package.py`

The change narrows display labels and package wording only. It does not create formal decision artifacts, approve gates, certify evidence, close study gates, or promote any generated output to release evidence.

## Preflight Evidence

- `rg` located the package generator, integration path, and tests:
  - `src/realworld/formal_acceptance_package.py`
  - `scripts/validate_formal_acceptance_package.py`
  - `scripts/run_acceptance_audit.py`
  - `tests/test_realworld_formal_acceptance_package.py`
- Full guard before this sprint showed:
  - `data/manifests/formal_acceptance_package_audit.json`: 14 release blockers
  - `docs/formal_acceptance_package_audit.md`: 4 release blockers
- Guard rows showed the blockers were mostly package title, gate labels, cross-check heading, and the Use paragraph, not newly accepted evidence.

## Changes Made

- Reworded the claim boundary from acceptance-artifact/calibrated wording to reviewer-supplied formal decision artifact wording.
- Renamed the Markdown title from `Formal Acceptance Package Audit` to `Formal Decision Package Intake Audit`.
- Replaced gate labels such as `Pilot Region Acceptance`, `Validation Acceptance`, and `Final Audit Acceptance` with decision or closeout labels.
- Changed the Markdown cross-check heading and verdict display from final-study language to study-closeout language.
- Reworded the Use paragraph so it describes reviewer-checked decision evidence rather than acceptance evidence.
- Updated the package test title assertion to match the new Markdown title.

## Commands Run

```powershell
.\.venv\Scripts\python .\tests\test_realworld_formal_acceptance_package.py
.\.venv\Scripts\python .\scripts\validate_formal_acceptance_package.py 2>&1
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\data\manifests\formal_acceptance_package_audit.json --scan-path .\docs\formal_acceptance_package_audit.md --output .\.tmp_formal_package_guard.csv --manifest .\.tmp_formal_package_guard.json --doc .\.tmp_formal_package_guard.md
Remove-Item -LiteralPath .\.tmp_formal_package_guard.csv, .\.tmp_formal_package_guard.json, .\.tmp_formal_package_guard.md -ErrorAction SilentlyContinue
.\.venv\Scripts\python .\scripts\run_acceptance_audit.py 2>&1
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_formal_acceptance_package.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\src\realworld\formal_acceptance_package.py .\tests\test_realworld_formal_acceptance_package.py .\data\manifests\formal_acceptance_package_audit.json .\docs\formal_acceptance_package_audit.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md
```

## Observed Results

- The first package test run failed only because it still expected the previous Markdown title.
- After updating the assertion, `tests/test_realworld_formal_acceptance_package.py` passed.
- `scripts/validate_formal_acceptance_package.py` exited 0 and emitted:
  - `gate_count: 12`
  - `ready_gate_count: 0`
  - `blocked_gate_count: 12`
  - `invalid_gate_count: 0`
  - `formal_acceptance_ready: false`
  - `final_study_ready: false`
  - `can_mark_complete: false`
- Focused guard for the package JSON and Markdown reported:
  - `blocking_finding_count: 0`
  - `release_blocked: false`
  - `claim_language_guard_ready: true`
- `scripts/run_acceptance_audit.py` exited 0 and regenerated integrated review artifacts.
- Full claim-language guard after this sprint reported:
  - `blocking_finding_count: 332`
  - `release_blocked: true`
  - `claim_language_guard_ready: false`
- CSV check confirmed:
  - `data/manifests/formal_acceptance_package_audit.json` release blockers: 0
  - `docs/formal_acceptance_package_audit.md` release blockers: 0
- Remaining top blocker sources after this sprint included:
  - `docs/graph_scale_diagnostics.md`: 14
  - `docs/human_acceptance_runbook.md`: 13
  - `docs/graph_scale_manifest_audit.md`: 13
  - `docs/analysis_corridor_method_note.md`: 12
- `tests/test_realworld_claim_language_guard.py` passed.
- `tests/test_realworld_plan_audit.py` passed.
- `git diff --check` exited 0 with LF-to-CRLF warnings only.
- Dirty worktree classification reported 414 classified paths and 0 unclassified paths.

## Residual Risk

This sprint clears the formal package intake artifacts only. The package still reports zero ready gates and remains non-approval intake. The repository remains release-blocked by other unbounded claim-language findings.
