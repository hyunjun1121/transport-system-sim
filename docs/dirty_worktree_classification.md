# Dirty Worktree Classification

This ledger classifies current dirty and untracked worktree paths for sprint-safety planning. It does not commit files, clean the worktree, approve reproducibility, permit generated-output promotion, or close final-study gates.

## Summary

- Dirty paths: 15
- Classified paths: 15
- Unclassified paths: 0
- New generated output allowed: `false`
- Destructive cleanup allowed: `false`
- Can mark complete: `false`

## Classified Paths

| Status | Owner | Phase | Evidence Status | Path | Allowed Next Action |
| --- | --- | --- | --- | --- | --- |
| M | main_thread_owner_required | phase0_baseline_and_worktree_safety | changed_path_requires_main_thread_review | `agents.md` | Inspect and assign owner before cleanup or new generated-output work. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/source_context_hash_audit.json` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/validation/claim_language_guard.csv` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/validation/claim_language_guard_manifest.json` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | phase0_dirty_worktree_classification | self_generated_classification_output | `data/validation/dirty_worktree_classification.csv` | Regenerate only through the dirty-worktree classification writer; do not treat as acceptance evidence. |
| M | artifact_lineage_owner_required | phase0_dirty_worktree_classification | self_generated_classification_output | `data/validation/dirty_worktree_classification_manifest.json` | Regenerate only through the dirty-worktree classification writer; do not treat as acceptance evidence. |
| M | claim_document_owner_required | phase11_claim_and_package_review | changed_claim_text_requires_claim_boundary_review | `docs/claim_language_guard.md` | Run claim-boundary review before report or package use. |
| M | claim_document_owner_required | phase11_claim_and_package_review | self_generated_classification_output | `docs/dirty_worktree_classification.md` | Regenerate only through the dirty-worktree classification writer; do not treat as acceptance evidence. |
| M | main_thread_owner_required | phase0_baseline_and_worktree_safety | changed_path_requires_main_thread_review | `high_level_plan.md` | Inspect and assign owner before cleanup or new generated-output work. |
| M | main_thread_owner_required | phase0_baseline_and_worktree_safety | changed_path_requires_main_thread_review | `plan.md` | Inspect and assign owner before cleanup or new generated-output work. |
| M | main_thread_owner_required | phase0_baseline_and_worktree_safety | changed_path_requires_main_thread_review | `status.md` | Inspect and assign owner before cleanup or new generated-output work. |
| ?? | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | untracked_requires_owner_and_package_decision | `data/rail/gtfs_derivation_attempt_manifest.json` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | implementation_owner_required | implementation_phase_requires_scope_assignment | untracked_requires_owner_and_package_decision | `scripts/record_gtfs_derivation_attempt.py` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | main_thread_owner_required | verification_phase_requires_scope_assignment | untracked_requires_owner_and_package_decision | `tests/feed.zip` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | implementation_owner_required | verification_phase_requires_scope_assignment | untracked_requires_owner_and_package_decision | `tests/test_realworld_gtfs_derivation_attempt.py` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |

## Use

Run this before new multi-agent sprints, generated-output work, compact/full experiments, or cleanup. A row means the path is known and classified, not that it is accepted, safe to delete, or ready for release. The default generated-output decision is fail-closed until the relevant owner and phase evidence explicitly allow the next action.
