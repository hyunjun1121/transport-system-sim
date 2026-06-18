# Dirty Worktree Classification

This ledger classifies current dirty and untracked worktree paths for sprint-safety planning. It does not commit files, clean the worktree, approve reproducibility, permit generated-output promotion, or close final-study gates.

## Summary

- Dirty paths: 16
- Classified paths: 16
- Unclassified paths: 0
- New generated output allowed: `false`
- Destructive cleanup allowed: `false`
- Can mark complete: `false`

## Classified Paths

| Status | Owner | Phase | Evidence Status | Path | Allowed Next Action |
| --- | --- | --- | --- | --- | --- |
| M | main_thread_owner_required | phase0_baseline_and_worktree_safety | changed_path_requires_main_thread_review | `high_level_plan.md` | Inspect and assign owner before cleanup or new generated-output work. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_figures/bottleneck_attribution.png` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_figures/censored_by_disruption.png` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_figures/completion_by_disruption.png` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_figures/policy_regime_map.png` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_figures/policy_resource_tradeoff.png` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_figures/sensitivity_ranking.png` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_tables/bottleneck_attribution_table.csv` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_tables/claim_boundary_table.csv` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_tables/figure_table_manifest.json` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_tables/main_result_table.csv` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_tables/policy_regime_table.csv` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/full_graph_tables/sensitivity_result_table.csv` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/pilot_full_graph_metric_ci.csv` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/pilot_full_graph_paired_delta_ci.csv` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |
| ?? | artifact_lineage_owner_required | experiment_output_phase_requires_manifest_review | untracked_requires_owner_and_package_decision | `results/realworld_pilot/pilot_full_graph_statistics_manifest.json` | Assign owner and phase, then add, package, or explicitly exclude before generated-output promotion. |

## Use

Run this before new multi-agent sprints, generated-output work, compact/full experiments, or cleanup. A row means the path is known and classified, not that it is accepted, safe to delete, or ready for release. The default generated-output decision is fail-closed until the relevant owner and phase evidence explicitly allow the next action.
