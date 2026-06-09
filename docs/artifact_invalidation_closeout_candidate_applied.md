# Artifact Invalidation Closeout Template

Artifact invalidation matrix for Phase 9 preflight review only; not an artifact regeneration record, not evidence-quality validation, not publication readiness, not final-study approval, and not formal acceptance.

## Summary

- Phase 9 promotion ready: `false`
- Can mark complete: `false`
- Rows: 51
- Closed rows: 5
- Pending or invalid rows: 46
- Reviewer evidence status counts: `{'current_reviewer_evidence': 5, 'missing_reviewer_id': 46}`

## Closeout Rows

| Row Key | Required Disposition | Actual Disposition | Audit Result | Test Result | Reviewer Signoff | Reviewer Evidence | Claim Effect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| region_boundary->road_snapshots | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| region_boundary->connector_audits | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| region_boundary->benchmarks | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| region_boundary->compact_outputs | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| region_boundary->full_outputs | mark_non_evidence | marked_non_evidence | pass | pass | signed_off_for_invalidation_closeout_only | current_reviewer_evidence | non_evidence_only |
| region_boundary->figures | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| region_boundary->reports | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| road_snapshot_or_evidence->route_exposure | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| road_snapshot_or_evidence->graph_scale_diagnostics | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| road_snapshot_or_evidence->benchmarks | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| road_snapshot_or_evidence->compact_outputs | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| road_snapshot_or_evidence->full_outputs | mark_non_evidence | marked_non_evidence | pass | pass | signed_off_for_invalidation_closeout_only | current_reviewer_evidence | non_evidence_only |
| road_snapshot_or_evidence->figures | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| road_snapshot_or_evidence->reports | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| rail_source_or_timing->multimodal_benchmarks | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| rail_source_or_timing->rail_stress_profiles | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| rail_source_or_timing->compact_outputs | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| rail_source_or_timing->full_outputs | mark_non_evidence | marked_non_evidence | pass | pass | signed_off_for_invalidation_closeout_only | current_reviewer_evidence | non_evidence_only |
| rail_source_or_timing->figures | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| rail_source_or_timing->reports | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch->compact_outputs | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch->full_outputs | mark_non_evidence | marked_non_evidence | pass | pass | signed_off_for_invalidation_closeout_only | current_reviewer_evidence | non_evidence_only |
| demand_fleet_behavior_transfer_dispatch->statistics | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch->sensitivity | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch->ml_labels | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch->ml_outputs | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch->figures | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch->reports | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| disruption_library_or_exposure->compact_outputs | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| disruption_library_or_exposure->full_outputs | mark_non_evidence | marked_non_evidence | pass | pass | signed_off_for_invalidation_closeout_only | current_reviewer_evidence | non_evidence_only |
| disruption_library_or_exposure->sensitivity | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| disruption_library_or_exposure->ml_labels | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| disruption_library_or_exposure->ml_outputs | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| disruption_library_or_exposure->figures | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| disruption_library_or_exposure->reports | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| benchmark_cache_or_threshold->benchmark_review_packets | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| benchmark_cache_or_threshold->claim_boundaries | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| benchmark_cache_or_threshold->figures | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| benchmark_cache_or_threshold->reports | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| result_csv_or_manifest->statistics | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| result_csv_or_manifest->sensitivity | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| result_csv_or_manifest->ml_outputs | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| result_csv_or_manifest->figures | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| result_csv_or_manifest->reports | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| result_csv_or_manifest->review_packages | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| claim_boundary_or_readiness_logic->publication_readiness | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| claim_boundary_or_readiness_logic->final_study_readiness | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| claim_boundary_or_readiness_logic->formal_guard | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| claim_boundary_or_readiness_logic->review_package_text | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| claim_boundary_or_readiness_logic->review_packages | mark_non_evidence | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |
| claim_boundary_or_readiness_logic->reports | regenerate | pending | not_run | not_run | unsigned | missing_reviewer_id | blocks_claim_support |

## Use

This file is a reviewer worksheet. A row should only be treated as closed after the required disposition is recorded, affected paths or exclusion scope are listed, rerun or audit evidence is retained, and a non-acceptance reviewer signoff is recorded. The template does not grant publication readiness, final-study readiness, formal acceptance, or operational use.
