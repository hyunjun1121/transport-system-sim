# Phase 9 Action-Batch Row Guidance Ledger - 2026-06-04

## Scope

This ledger records a narrow Phase 9 support update for the artifact
invalidation action-batch inspection. It is row-level closeout guidance only.
It is not closeout evidence, not reviewer signoff, not artifact regeneration
evidence, not publication readiness, not final-study approval, and not formal
acceptance.

## Objective

Make each pending invalidation row show the next dependency-safe closeout
focus, prerequisite batch, minimum evidence package, and allowed next operation
before any Phase 9 regeneration or promotion work is attempted.

## Edits

- Added row-level action-batch inspection fields:
  - `next_closeout_focus`
  - `blocking_prerequisite_batch`
  - `blocking_prerequisite_status`
  - `minimum_evidence_package_json`
  - `allowed_next_operation`
- Added batch rollup fields for blocking prerequisite batches and allowed next
  operations.
- Added validation that every action-batch inspection row has a non-empty next
  focus, prerequisite status, allowed operation, and JSON evidence package.
- Changed action-batch inspection CSV writing to content-aware output and added
  `csv_sha256` to its manifest.
- Updated Markdown output to show row-level focus, prerequisite, and evidence
  package fields.
- Added regression tests for row-level guidance, prerequisite ordering, minimum
  package contents, manifest CSV hash, and unchanged CSV rewrite behavior.

## Evidence Commands

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-action-batch-inspection
.\.venv\Scripts\python scripts\audit_claim_language.py --fail-on-blockers
.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
git diff --check -- src\realworld\artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py data\validation\artifact_invalidation_action_batch_inspection.csv data\validation\artifact_invalidation_action_batch_inspection_manifest.json docs\artifact_invalidation_action_batch_inspection.md
```

## Results

- Artifact invalidation tests passed.
- Claim-language guard passed with `blocking_finding_count=0`.
- Plan audit test passed.
- `git diff --check` returned no whitespace findings for the touched paths.
- Regenerated action-batch inspection output:
  - rows: 51
  - pending or blocked rows: 51
  - regeneration candidates: 45
  - exclusion or non-evidence candidates: 6
  - CSV SHA256:
    `5d96905c1d24add7e46d98214ad5ef428c0fee1e6fe3b1aba00b46a785479456`

## Remaining Blockers

- All 51 action-batch inspection rows still require main closeout evidence.
- The first dependency-safe batch remains the six-row
  `quarantine_non_evidence` batch.
- Later batches remain blocked behind their prerequisite batches:
  `upstream_evidence_and_benchmarks`, `compact_outputs`, `analysis_outputs`,
  then `claims_and_packages`.
- `phase9_promotion_ready=false`, `publication_ready=false`,
  `final_study_ready=false`, and `formal_acceptance_evidence=false` remain
  unchanged.
