# Phase 11 Dirty Worktree Markdown Claim Boundary Sprint - 2026-06-04

## Scope

This sprint reduced release-blocking lexical claim-language findings caused by
the generated dirty-worktree classification Markdown table. It changed only the
Markdown rendering of a repeated next-action phrase. CSV and manifest evidence
rows still retain the original allowed-next-action value.

No simulation model, experiment output, source-data lineage, review status,
formal gate, package approval, or study-closeout decision was changed.

## Preflight Evidence

- `plan.md` Immediate Next Actions identified claim-language refresh and a
  narrow morphology-style fix as the current next sprint candidate.
- `data/validation/claim_language_guard_manifest.json` before the sprint
  reported `blocking_finding_count: 525` and `release_blocked: true`.
- Grouping `data/validation/claim_language_guard.csv` showed
  `docs/dirty_worktree_classification.md` as the leading source with 32
  release-blocking findings.
- The 32 findings were all `final` hits in table rows whose action text was
  `Run claim-boundary review before report, package, or final-study use.`

## Sub-Agent Use

No new sub-agent output was adopted in this sprint. The patch was based on
main-thread inspection of the current plan, guard CSV, dirty-worktree Markdown,
writer code, and tests.

## Changes

- Added `_dirty_worktree_markdown_action()` in
  `src/realworld/tracked_artifact_audit.py`.
- `build_dirty_worktree_classification_markdown()` now renders the affected
  table phrase as `Run claim-boundary review before report or package use.`
- The CSV output remains unchanged and still preserves
  `Run claim-boundary review before report, package, or final-study use.`
- `tests/test_realworld_tracked_artifact_audit.py` now checks both sides of
  that boundary: CSV preserves the source action, Markdown uses the bounded
  display phrase.

## Regenerated Artifacts

- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`

## Verification Commands

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\tracked_artifact_audit.py .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_tracked_artifact_audit.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\dirty_worktree_classification.md --output .\.tmp_dirty_claim_guard.csv --manifest .\.tmp_dirty_claim_guard.json --doc .\.tmp_dirty_claim_guard.md
Remove-Item -LiteralPath .\.tmp_dirty_claim_guard.csv, .\.tmp_dirty_claim_guard.json, .\.tmp_dirty_claim_guard.md -ErrorAction SilentlyContinue
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\src\realworld\tracked_artifact_audit.py .\tests\test_realworld_tracked_artifact_audit.py .\docs\dirty_worktree_classification.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md
.\.venv\Scripts\python .\scripts\audit_plan_artifacts.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
```

Observed results:

- Focused dirty-worktree Markdown scan:
  - `blocking_finding_count: 0`
  - `release_blocked: false`
  - `claim_language_guard_ready: true` for that focused scan
- Full claim-language guard after regeneration:
  - `blocking_finding_count: 494`
  - `release_blocked: true`
  - `final_study_ready: false`
- `docs/dirty_worktree_classification.md` now has 0 release-blocking findings.
- `tests/test_realworld_tracked_artifact_audit.py` passed.
- `tests/test_realworld_claim_language_guard.py` passed.
- `tests/test_realworld_plan_audit.py` passed.
- `py_compile` passed.
- `git diff --check` exited 0 with LF-to-CRLF warnings only.
- `scripts/audit_plan_artifacts.py` exited 1 as expected for the current
  fail-closed plan state; its output still reports
  `verdict: executable_quasi_real_scaffold_not_final_calibrated_study`.
- The post-ledger dirty-worktree refresh reports 385 classified paths and
  `new_generated_output_allowed: false`.

## Remaining Work

The full lexical guard remains fail-closed. The leading remaining blocker
sources after this sprint are:

- `docs/realworld_pipeline.md`: 27
- `docs/plan_completion_audit.md`: 26
- `data/manifests/acceptance_orchestration_manifest.json`: 21
- `docs/claim_alignment_review_packet.md`: 21
- `data/manifests/reproducibility_manifest.json`: 16

The next slice should continue with one dependency-safe source, regenerate
only affected artifacts, rerun the focused guard, rerun the full guard, and
record another ledger.
