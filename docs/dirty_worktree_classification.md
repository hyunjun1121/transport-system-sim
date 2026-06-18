# Dirty Worktree Classification

This ledger classifies current dirty and untracked worktree paths for sprint-safety planning. It does not commit files, clean the worktree, approve reproducibility, permit generated-output promotion, or close final-study gates.

## Summary

- Dirty paths: 9
- Classified paths: 9
- Unclassified paths: 0
- New generated output allowed: `false`
- Destructive cleanup allowed: `false`
- Can mark complete: `false`

## Classified Paths

| Status | Owner | Phase | Evidence Status | Path | Allowed Next Action |
| --- | --- | --- | --- | --- | --- |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/parameters/road_class_overrides_draft.csv` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | artifact_lineage_owner_required | phase0_dirty_worktree_classification | self_generated_classification_output | `data/validation/dirty_worktree_classification.csv` | Regenerate only through the dirty-worktree classification writer; do not treat as acceptance evidence. |
| M | artifact_lineage_owner_required | phase0_dirty_worktree_classification | self_generated_classification_output | `data/validation/dirty_worktree_classification_manifest.json` | Regenerate only through the dirty-worktree classification writer; do not treat as acceptance evidence. |
| M | claim_document_owner_required | phase11_claim_and_package_review | self_generated_classification_output | `docs/dirty_worktree_classification.md` | Regenerate only through the dirty-worktree classification writer; do not treat as acceptance evidence. |
| M | main_thread_owner_required | phase0_baseline_and_worktree_safety | changed_path_requires_main_thread_review | `high_level_plan.md` | Inspect and assign owner before cleanup or new generated-output work. |
| M | main_thread_owner_required | phase0_baseline_and_worktree_safety | changed_path_requires_main_thread_review | `plan.md` | Inspect and assign owner before cleanup or new generated-output work. |
| M | implementation_owner_required | implementation_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `scripts/write_road_class_override_template.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| M | implementation_owner_required | implementation_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `src/realworld/road_override_template.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| M | implementation_owner_required | implementation_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `src/realworld/road_speed_evidence.py` | Inspect diff, run narrow tests, and record owner before broader work. |

## Use

Run this before new multi-agent sprints, generated-output work, compact/full experiments, or cleanup. A row means the path is known and classified, not that it is accepted, safe to delete, or ready for release. The default generated-output decision is fail-closed until the relevant owner and phase evidence explicitly allow the next action.
