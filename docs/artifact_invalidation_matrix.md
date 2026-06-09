# Artifact Invalidation Matrix

Artifact invalidation matrix for Phase 9 preflight review only; not an artifact regeneration record, not evidence-quality validation, not publication readiness, not final-study approval, and not formal acceptance.

## Summary

- Phase 9 promotion ready: `false`
- Can mark complete: `false`
- Rows: 51
- Blocking rows: 51
- Required upstream groups covered: `true`
- Required Phase 9 downstream groups covered: `true`

## Matrix

| Upstream Group | Stale Downstream Group | Required Disposition | Status | Claim Effect |
| --- | --- | --- | --- | --- |
| region_boundary | road_snapshots | regenerate | stale_pending_disposition | blocks_claim_support |
| region_boundary | connector_audits | regenerate | stale_pending_disposition | blocks_claim_support |
| region_boundary | benchmarks | regenerate | stale_pending_disposition | blocks_claim_support |
| region_boundary | compact_outputs | regenerate | stale_pending_disposition | blocks_claim_support |
| region_boundary | full_outputs | mark_non_evidence | stale_pending_disposition | blocks_claim_support |
| region_boundary | figures | regenerate | stale_pending_disposition | blocks_claim_support |
| region_boundary | reports | regenerate | stale_pending_disposition | blocks_claim_support |
| road_snapshot_or_evidence | route_exposure | regenerate | stale_pending_disposition | blocks_claim_support |
| road_snapshot_or_evidence | graph_scale_diagnostics | regenerate | stale_pending_disposition | blocks_claim_support |
| road_snapshot_or_evidence | benchmarks | regenerate | stale_pending_disposition | blocks_claim_support |
| road_snapshot_or_evidence | compact_outputs | regenerate | stale_pending_disposition | blocks_claim_support |
| road_snapshot_or_evidence | full_outputs | mark_non_evidence | stale_pending_disposition | blocks_claim_support |
| road_snapshot_or_evidence | figures | regenerate | stale_pending_disposition | blocks_claim_support |
| road_snapshot_or_evidence | reports | regenerate | stale_pending_disposition | blocks_claim_support |
| rail_source_or_timing | multimodal_benchmarks | regenerate | stale_pending_disposition | blocks_claim_support |
| rail_source_or_timing | rail_stress_profiles | regenerate | stale_pending_disposition | blocks_claim_support |
| rail_source_or_timing | compact_outputs | regenerate | stale_pending_disposition | blocks_claim_support |
| rail_source_or_timing | full_outputs | mark_non_evidence | stale_pending_disposition | blocks_claim_support |
| rail_source_or_timing | figures | regenerate | stale_pending_disposition | blocks_claim_support |
| rail_source_or_timing | reports | regenerate | stale_pending_disposition | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch | compact_outputs | regenerate | stale_pending_disposition | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch | full_outputs | mark_non_evidence | stale_pending_disposition | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch | statistics | regenerate | stale_pending_disposition | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch | sensitivity | regenerate | stale_pending_disposition | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch | ml_labels | regenerate | stale_pending_disposition | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch | ml_outputs | regenerate | stale_pending_disposition | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch | figures | regenerate | stale_pending_disposition | blocks_claim_support |
| demand_fleet_behavior_transfer_dispatch | reports | regenerate | stale_pending_disposition | blocks_claim_support |
| disruption_library_or_exposure | compact_outputs | regenerate | stale_pending_disposition | blocks_claim_support |
| disruption_library_or_exposure | full_outputs | mark_non_evidence | stale_pending_disposition | blocks_claim_support |
| disruption_library_or_exposure | sensitivity | regenerate | stale_pending_disposition | blocks_claim_support |
| disruption_library_or_exposure | ml_labels | regenerate | stale_pending_disposition | blocks_claim_support |
| disruption_library_or_exposure | ml_outputs | regenerate | stale_pending_disposition | blocks_claim_support |
| disruption_library_or_exposure | figures | regenerate | stale_pending_disposition | blocks_claim_support |
| disruption_library_or_exposure | reports | regenerate | stale_pending_disposition | blocks_claim_support |
| benchmark_cache_or_threshold | benchmark_review_packets | regenerate | stale_pending_disposition | blocks_claim_support |
| benchmark_cache_or_threshold | claim_boundaries | regenerate | stale_pending_disposition | blocks_claim_support |
| benchmark_cache_or_threshold | figures | regenerate | stale_pending_disposition | blocks_claim_support |
| benchmark_cache_or_threshold | reports | regenerate | stale_pending_disposition | blocks_claim_support |
| result_csv_or_manifest | statistics | regenerate | stale_pending_disposition | blocks_claim_support |
| result_csv_or_manifest | sensitivity | regenerate | stale_pending_disposition | blocks_claim_support |
| result_csv_or_manifest | ml_outputs | regenerate | stale_pending_disposition | blocks_claim_support |
| result_csv_or_manifest | figures | regenerate | stale_pending_disposition | blocks_claim_support |
| result_csv_or_manifest | reports | regenerate | stale_pending_disposition | blocks_claim_support |
| result_csv_or_manifest | review_packages | regenerate | stale_pending_disposition | blocks_claim_support |
| claim_boundary_or_readiness_logic | publication_readiness | regenerate | stale_pending_disposition | blocks_claim_support |
| claim_boundary_or_readiness_logic | final_study_readiness | regenerate | stale_pending_disposition | blocks_claim_support |
| claim_boundary_or_readiness_logic | formal_guard | regenerate | stale_pending_disposition | blocks_claim_support |
| claim_boundary_or_readiness_logic | review_package_text | regenerate | stale_pending_disposition | blocks_claim_support |
| claim_boundary_or_readiness_logic | review_packages | mark_non_evidence | stale_pending_disposition | blocks_claim_support |
| claim_boundary_or_readiness_logic | reports | regenerate | stale_pending_disposition | blocks_claim_support |

## Use

Before Phase 9, every blocking row must be regenerated, explicitly excluded, or marked non-evidence and then re-audited. `excluded` or `non-evidence` dispositions clear claim use only after text, figures, manifests, and package notes no longer cite the stale artifact.
