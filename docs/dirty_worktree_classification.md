# Dirty Worktree Classification

This ledger classifies current dirty and untracked worktree paths for sprint-safety planning. It does not commit files, clean the worktree, approve reproducibility, permit generated-output promotion, or close final-study gates.

## Summary

- Dirty paths: 8
- Classified paths: 8
- Unclassified paths: 0
- New generated output allowed: `false`
- Destructive cleanup allowed: `false`
- Can mark complete: `false`

## Classified Paths

| Status | Owner | Phase | Evidence Status | Path | Allowed Next Action |
| --- | --- | --- | --- | --- | --- |
| M | artifact_lineage_owner_required | evidence_or_manifest_phase_requires_source_review | changed_generated_or_evidence_artifact_requires_manifest_review | `data/manifests/pilot_experiment_design.json` | Verify source lineage, row counts, hashes, and invalidation status. |
| M | main_thread_owner_required | phase0_baseline_and_worktree_safety | changed_path_requires_main_thread_review | `high_level_plan.md` | Inspect and assign owner before cleanup or new generated-output work. |
| M | implementation_owner_required | implementation_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `scripts/run_pilot_experiments.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| M | implementation_owner_required | implementation_phase_requires_scope_assignment | changed_code_or_test_requires_diff_and_test_review | `src/realworld/pilot_experiments.py` | Inspect diff, run narrow tests, and record owner before broader work. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/pilot_full_graph_manifest.json` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/pilot_full_graph_output_lock_receipt.json` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/pilot_full_graph_results.csv` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/pilot_full_graph_summary.csv` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |

## Use

Run this before new multi-agent sprints, generated-output work, compact/full experiments, or cleanup. A row means the path is known and classified, not that it is accepted, safe to delete, or ready for release. The default generated-output decision is fail-closed until the relevant owner and phase evidence explicitly allow the next action.
