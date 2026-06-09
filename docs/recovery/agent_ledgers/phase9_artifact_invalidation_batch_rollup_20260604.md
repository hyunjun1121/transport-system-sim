# Phase 9 Artifact Invalidation Batch Rollup - 2026-06-04

## Objective

Improve Phase 9 artifact-invalidation closeout triage by adding a batch-level
rollup to the action-batch inspection outputs, then regenerate the closeout
family from one current matrix basis.

## Scope

Edited files:

- `src/realworld/artifact_invalidation_matrix.py`
- `tests/test_realworld_artifact_invalidation_matrix.py`

Generated or refreshed files:

- `data/validation/artifact_invalidation_matrix.csv`
- `data/validation/artifact_invalidation_matrix_manifest.json`
- `docs/artifact_invalidation_matrix.md`
- `data/validation/artifact_invalidation_closeout_template.csv`
- `data/validation/artifact_invalidation_closeout_manifest.json`
- `docs/artifact_invalidation_closeout_template.md`
- `data/validation/artifact_invalidation_closeout_action_queue.csv`
- `data/validation/artifact_invalidation_closeout_action_queue_manifest.json`
- `docs/artifact_invalidation_closeout_action_queue.md`
- `data/validation/artifact_invalidation_action_batch_inspection.csv`
- `data/validation/artifact_invalidation_action_batch_inspection_manifest.json`
- `docs/artifact_invalidation_action_batch_inspection.md`
- `data/validation/artifact_invalidation_closeout_readiness_audit.csv`
- `data/validation/artifact_invalidation_closeout_readiness_audit_manifest.json`
- `docs/artifact_invalidation_closeout_readiness_audit.md`
- `data/validation/artifact_invalidation_quarantine_closeout_template.csv`
- `data/validation/artifact_invalidation_quarantine_closeout_manifest.json`
- `docs/artifact_invalidation_quarantine_closeout_template.md`
- `data/validation/artifact_invalidation_quarantine_scope_audit.csv`
- `data/validation/artifact_invalidation_quarantine_scope_audit_manifest.json`
- `docs/artifact_invalidation_quarantine_scope_audit.md`
- `data/validation/artifact_invalidation_quarantine_non_evidence_index.csv`
- `data/validation/artifact_invalidation_quarantine_non_evidence_index_manifest.json`
- `docs/artifact_invalidation_quarantine_non_evidence_index.md`
- `data/validation/artifact_invalidation_quarantine_non_evidence_transfer_packet.csv`
- `data/validation/artifact_invalidation_quarantine_non_evidence_transfer_packet_manifest.json`
- `docs/artifact_invalidation_quarantine_non_evidence_transfer_packet.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

## Change Summary

- Added `action_batch_rollup` to the action-batch inspection summary.
- Added per-batch next-focus guidance, pending counts, signoff counts, and
  missing-evidence lists.
- Added a `Batch Rollup` section to the markdown writer.
- Strengthened tests so generated manifest and markdown outputs must include
  the batch rollup.
- Regenerated all closeout-family outputs together after detecting that a stale
  closeout template could misclassify one row as `other`.

## Command Checkpoints

| checkpoint_id | command | result | claim impact |
| --- | --- | --- | --- |
| T1-py-compile | `.\.venv\Scripts\python -m py_compile src\realworld\artifact_invalidation_matrix.py scripts\write_artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py` | Passed. | Syntax check only for artifact-invalidation code paths. |
| T2-focused-tests-before-regeneration | `.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py` | Passed. | Confirms the new rollup behavior is covered by focused tests. |
| T3-partial-generator | `.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-action-batch-inspection` | Completed, but revealed one stale-template row classified as `other`. | Identified generated-output basis drift; not used as closeout evidence. |
| T4-full-generator | `.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-closeout-template --write-closeout-action-queue --write-action-batch-inspection --write-closeout-readiness-audit --write-quarantine-closeout-template --write-quarantine-scope-audit --write-quarantine-non-evidence-index --write-quarantine-non-evidence-transfer-packet` | Passed. | Regenerated the closeout family from the current matrix basis. |
| T5-action-batch-counts | `Import-Csv -LiteralPath data\validation\artifact_invalidation_action_batch_inspection.csv | Group-Object action_batch | Select-Object Name,Count | Format-Table -AutoSize` | Confirmed `analysis_outputs=10`, `claims_and_packages=20`, `compact_outputs=5`, `quarantine_non_evidence=6`, and `upstream_evidence_and_benchmarks=10`; no `other` batch. | Confirms the stale-template mismatch was corrected in generated outputs. |
| T6-focused-tests-after-regeneration | `.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py` | Passed. | Confirms regenerated outputs remain non-acceptance and satisfy focused tests. |
| T7-claim-language | `.\.venv\Scripts\python scripts\audit_claim_language.py` | Passed with `blocking_finding_count=0`. | Confirms the regenerated docs did not add lexical claim-language blockers. |
| T8-claim-guard-tests | `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | Passed. | Confirms claim-language guard behavior after regenerated guard artifacts. |
| T9-plan-audit | `.\.venv\Scripts\python tests\test_realworld_plan_audit.py` | Passed. | Confirms plan-artifact audit still preserves scaffold claim boundaries. |
| T10-diff-check | `git diff --check -- src\realworld\artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py data\validation\artifact_invalidation_action_batch_inspection_manifest.json docs\artifact_invalidation_action_batch_inspection.md data\validation\artifact_invalidation_closeout_template.csv data\validation\artifact_invalidation_closeout_manifest.json docs\artifact_invalidation_closeout_template.md data\validation\artifact_invalidation_closeout_action_queue.csv data\validation\artifact_invalidation_closeout_action_queue_manifest.json docs\artifact_invalidation_closeout_action_queue.md data\validation\artifact_invalidation_closeout_readiness_audit.csv data\validation\artifact_invalidation_closeout_readiness_audit_manifest.json docs\artifact_invalidation_closeout_readiness_audit.md` | Passed. | No whitespace errors detected in the checked changed files. |
| T11-dirty-classification | `.\.venv\Scripts\python scripts\write_dirty_worktree_classification.py` | Passed; manifest reports `dirty_path_count=665`, `unclassified_path_count=0`, and `final_study_ready=false`. | Updates worktree-safety classification only; it does not approve generated-output promotion. |

## Remaining Blockers

The action-batch inspection still reports 51 pending or blocked invalidation
rows, 0 rows that can clear the invalidation gate, and `phase9_promotion_ready`
as false. All rows still require actual disposition, affected scope, rerun
result, audit result, targeted test result, claim-boundary review, reviewer
signoff, and explicit can-clear status before Phase 9 can be promoted.

## Boundary

This ledger records a triage-output improvement and regeneration consistency
check. It does not close the artifact-invalidation record, create formal
acceptance, approve generated-output promotion, or support final-study,
publication, calibrated-validation, or operational-routing claims.
