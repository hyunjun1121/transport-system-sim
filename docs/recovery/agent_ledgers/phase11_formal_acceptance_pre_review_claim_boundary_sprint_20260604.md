# Phase 11 Formal Pre-Review Claim-Boundary Sprint - 2026-06-04

## Scope

This ledger covers the claim-language cleanup for `docs/formal_acceptance_pre_review.md` and its generator, `src/realworld/formal_acceptance_pre_review.py`.

The change is limited to Markdown display wording and the pre-review instruction copy. It does not create formal decision artifacts, approve gates, certify sources, close study gates, or promote any generated output to release evidence.

## Preflight Evidence

- `rg` located the generator, writer, test, and integration path:
  - `src/realworld/formal_acceptance_pre_review.py`
  - `scripts/write_formal_acceptance_pre_review.py`
  - `tests/test_realworld_formal_acceptance_pre_review.py`
  - `scripts/run_acceptance_audit.py`
- The focused guard initially reported 14 release-blocking unbounded findings for `docs/formal_acceptance_pre_review.md`.
- The document is generated output; edits were made in the generator rather than manually rewriting the rendered document.

## Changes Made

- Added a Markdown-only display guard in `src/realworld/formal_acceptance_pre_review.py`.
- Applied guarded display wording to list items, compacted blocker items, and record labels.
- Reworded the "Use" paragraph from approval/path language to reviewer decision/path language.
- Preserved underlying draft JSON record contents; the guard only changes rendered Markdown display text.

## Commands Run

```powershell
.\.venv\Scripts\python .\tests\test_realworld_formal_acceptance_pre_review.py
.\.venv\Scripts\python .\scripts\write_formal_acceptance_pre_review.py
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\formal_acceptance_pre_review.md --output .\.tmp_formal_pre_review_guard.csv --manifest .\.tmp_formal_pre_review_guard.json --doc .\.tmp_formal_pre_review_guard.md
Remove-Item -LiteralPath .\.tmp_formal_pre_review_guard.csv, .\.tmp_formal_pre_review_guard.json, .\.tmp_formal_pre_review_guard.md -ErrorAction SilentlyContinue
.\.venv\Scripts\python .\scripts\run_acceptance_audit.py 2>&1
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_formal_acceptance_pre_review.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\src\realworld\formal_acceptance_pre_review.py .\tests\test_realworld_formal_acceptance_pre_review.py .\data\manifests\draft_acceptance\formal_acceptance_pre_review_manifest.json .\docs\formal_acceptance_pre_review.md .\data\manifests\acceptance_orchestration_manifest.json .\docs\review_packets\acceptance_review_index.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md
```

## Observed Results

- `tests/test_realworld_formal_acceptance_pre_review.py` passed.
- `scripts/write_formal_acceptance_pre_review.py` emitted:
  - `record_count: 12`
  - `human_decision_required_count: 12`
  - `formal_approval: false`
  - `formal_acceptance_ready: false`
  - `final_study_ready: false`
  - `can_mark_complete: false`
  - `recommendation_counts.blocked_missing_evidence: 8`
  - `recommendation_counts.blocked_requires_human_decision: 4`
- Focused guard for `docs/formal_acceptance_pre_review.md` reported:
  - `blocking_finding_count: 0`
  - `release_blocked: false`
  - `claim_language_guard_ready: true`
- A first parallel `run_acceptance_audit.py` attempt exited 1 without output; the immediate standalone rerun exited 0 and regenerated integrated artifacts.
- Full claim-language guard after this sprint reported:
  - `blocking_finding_count: 350`
  - `release_blocked: true`
  - `claim_language_guard_ready: false`
- CSV check confirmed:
  - `docs/formal_acceptance_pre_review.md` release blockers: 0
- Remaining top blocker sources after this sprint included:
  - `data/manifests/formal_acceptance_package_audit.json`: 14
  - `docs/graph_scale_diagnostics.md`: 14
  - `docs/graph_scale_manifest_audit.md`: 13
  - `docs/human_acceptance_runbook.md`: 13
- `tests/test_realworld_claim_language_guard.py` passed.
- `tests/test_realworld_plan_audit.py` passed.
- `git diff --check` exited 0 with LF-to-CRLF warnings only.
- Dirty worktree classification reported 411 classified paths and 0 unclassified paths.

## Residual Risk

This sprint only resolves one generated Markdown surface. The repository remains release-blocked by other unbounded claim-language findings. The formal pre-review remains draft-only and requires human reviewer decisions before any formal gate can close.
