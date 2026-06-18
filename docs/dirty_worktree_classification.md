# Dirty Worktree Classification

This ledger classifies current dirty and untracked worktree paths for sprint-safety planning. It does not commit files, clean the worktree, approve reproducibility, permit generated-output promotion, or close final-study gates.

## Summary

- Dirty paths: 30
- Classified paths: 30
- Unclassified paths: 0
- New generated output allowed: `false`
- Destructive cleanup allowed: `false`
- Can mark complete: `false`

## Classified Paths

| Status | Owner | Phase | Evidence Status | Path | Allowed Next Action |
| --- | --- | --- | --- | --- | --- |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/acceptance_task_assignments.csv` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/acceptance_task_assignments_manifest.json` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/current_goal_completion_audit.json` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/final_audit_decision_manifest.json` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/final_audit_decision_packet.csv` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/formal_acceptance_blocker_queue.csv` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/formal_acceptance_blocker_queue_manifest.json` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/formal_acceptance_evidence_matrix.csv` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/formal_evidence_path_audit.json` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/source_context_hash_audit.json` | Verify source lineage, row counts, hashes, and invalidation status. |
| D | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/parameters/road_class_overrides.csv` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | phase0_dirty_worktree_classification | self_generated_classification_output | `data/validation/dirty_worktree_classification.csv` | Regenerate only through the dirty-worktree classification writer; do not treat as acceptance evidence. |
| M | artifact_lineage_owner_required | phase0_dirty_worktree_classification | self_generated_classification_output | `data/validation/dirty_worktree_classification_manifest.json` | Regenerate only through the dirty-worktree classification writer; do not treat as acceptance evidence. |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/validation/osm_graph_snapshot_review_packet.csv` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | claim_document_owner_required | phase11_claim_and_package_review | changed_claim_text_requires_claim_boundary_review | `docs/acceptance_task_assignments.md` | Run claim-boundary review before report or package use. |
| M | claim_document_owner_required | phase11_claim_and_package_review | changed_claim_text_requires_claim_boundary_review | `docs/current_goal_completion_audit.md` | Run claim-boundary review before report or package use. |
| M | claim_document_owner_required | phase11_claim_and_package_review | self_generated_classification_output | `docs/dirty_worktree_classification.md` | Regenerate only through the dirty-worktree classification writer; do not treat as acceptance evidence. |
| M | claim_document_owner_required | phase11_claim_and_package_review | changed_claim_text_requires_claim_boundary_review | `docs/final_audit_decision_packet.md` | Run claim-boundary review before report or package use. |
| M | claim_document_owner_required | phase11_claim_and_package_review | changed_claim_text_requires_claim_boundary_review | `docs/formal_acceptance_blocker_queue.md` | Run claim-boundary review before report or package use. |
| M | claim_document_owner_required | phase11_claim_and_package_review | changed_claim_text_requires_claim_boundary_review | `docs/formal_evidence_path_audit.md` | Run claim-boundary review before report or package use. |
| M | claim_document_owner_required | phase11_claim_and_package_review | changed_claim_text_requires_claim_boundary_review | `docs/osm_graph_snapshot_review_packet.md` | Run claim-boundary review before report or package use. |
| M | main_thread_owner_required | phase0_baseline_and_worktree_safety | changed_path_requires_main_thread_review | `high_level_plan.md` | Inspect and assign owner before cleanup or new generated-output work. |
| M | implementation_owner_required | verification_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `tests/test_realworld_acceptance_blocker_queue.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| M | implementation_owner_required | verification_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `tests/test_realworld_acceptance_task_assignments.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| M | implementation_owner_required | verification_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `tests/test_realworld_final_audit_decision_packet.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| M | implementation_owner_required | verification_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `tests/test_realworld_formal_acceptance_guard.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| M | implementation_owner_required | verification_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `tests/test_realworld_goal_completion_audit.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| M | implementation_owner_required | verification_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `tests/test_realworld_plan_audit.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| M | implementation_owner_required | verification_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `tests/test_realworld_road_override_audit.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| M | implementation_owner_required | verification_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `tests/test_realworld_road_override_source_candidate.py` | Inspect diff, run narrow tests, and record owner before broader work. |

## Use

Run this before new multi-agent sprints, generated-output work, compact/full experiments, or cleanup. A row means the path is known and classified, not that it is accepted, safe to delete, or ready for release. The default generated-output decision is fail-closed until the relevant owner and phase evidence explicitly allow the next action.
