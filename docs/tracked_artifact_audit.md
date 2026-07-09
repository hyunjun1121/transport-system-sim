# Tracked Artifact Audit

This audit checks whether current changed artifacts would be present in a clean checkout of the current Git HEAD. It does not commit files, approve reproducibility, validate evidence quality, or close final-study gates.

## Summary

- Clean-checkout reproducibility ready: `false`
- Can mark complete: `false`
- Changed reproducibility artifacts: 210
- Blocking changed artifacts: 210
- Untracked artifacts: 4
- Modified or staged artifacts: 206

## Changed Artifacts

| Status | Category | Path | Required Action |
| --- | --- | --- | --- |
| M | data_or_manifest | `data/cache/pilot_region_road.graphml` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/cache/pilot_region_road.raw.graphml` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_decision_template_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_orchestration_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_task_assignments.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_task_assignments_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_templates/experiment_acceptance_template.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_templates/final_audit_acceptance_template.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_templates/graph_scale_acceptance_template.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_templates/sensitivity_acceptance_template.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_review_path_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/cached_osm_input__road_rail_parameter_evidence_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/data_provenance__osm_source_license_provenance_review_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/final_audit__final_independent_audit_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/full_experiment_output__full_experiment_package_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/graph_scale_strategy__graph_scale_method_review_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/manuscript_report_alignment__paper_report_claim_alignment_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/parameter_evidence__road_rail_parameter_evidence_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/pilot_region_accepted__pilot_region_privacy_review_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/rail_evidence__road_rail_parameter_evidence_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/reproducibility__clean_checkout_reproducibility_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/sensitivity_analysis__sensitivity_analysis_review_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/validation_package__validation_benchmark_strategy_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/claim_alignment_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/claim_alignment_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/current_goal_completion_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/data_provenance_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/final_audit_document_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/final_audit_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/formal_acceptance_pre_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/full_experiment_output_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/graph_scale_strategy_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/manuscript_report_alignment_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/parameter_acceptance_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/pilot_region_accepted_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/reproducibility_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/road_class_overrides_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/sensitivity_analysis_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/validation_package_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/experiment_design_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/experiment_design_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/experiment_package_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/experiment_package_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/experiment_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/experiment_strategy_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/figure_table_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/figure_table_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/final_audit_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/final_audit_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_blocker_queue.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_blocker_queue_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_evidence_matrix.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_evidence_matrix_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_package_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/manuscript_report_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/manuscript_report_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/pilot_region_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/publication_readiness_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_context_cache_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_context_hash_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_license_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_priority_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_remediation_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_acceptance_template.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_evidence_priority_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_evidence_priority_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_evidence_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_evidence_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_evidence_source_request_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_evidence_source_request_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_source_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_source_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_source_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_source_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/rail_evidence_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/rail_evidence_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/rail_service_evidence.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/road_capacity_evidence_candidates.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/road_capacity_evidence_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/road_class_overrides.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/road_evidence_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/road_evidence_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/road_speed_evidence_candidates.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/road_speed_evidence_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_evidence_priority_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_fetch_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_source_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_source_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/regions/goseong_mobilization.yaml` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_evidence_priority_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_evidence_priority_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_evidence_source_request_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/snapshots/songpa_public_demo_phase9_upstream_20260605T000000Z/road.graphml` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/artifact_invalidation_matrix.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/artifact_invalidation_matrix_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/canonical_route_road_evidence_exposure.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_manifest_audit.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_manifest_audit_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_method_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_method_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_strategy_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/integrated_evidence_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/integrated_evidence_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/osm_graph_snapshot_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/osm_graph_snapshot_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/sensitivity_method_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/summary_truth_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/summary_truth_table.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_benchmark_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_benchmark_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_benchmark_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_strategy_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/acceptance_decision_templates.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/acceptance_task_assignments.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/agent_review_path_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/current_goal_completion_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/experiment_design_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/experiment_package_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/experiment_strategy_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/figure_table_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/final_audit_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_blocker_queue.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_evidence_matrix.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_package_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_pre_review.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_manifest_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_method_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_strategy_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/integrated_evidence_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/manuscript_report_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/osm_graph_snapshot_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_evidence_priority_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_source_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_source_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/pilot_region_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/publication_readiness_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_source_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/reproducibility_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/acceptance_review_index.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/cached_osm_input.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/data_provenance.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/final_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/full_experiment_output.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/graph_scale_strategy.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/manuscript_report_alignment.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/parameter_evidence.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/pilot_region_accepted.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/rail_evidence.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/reproducibility.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/sensitivity_analysis.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/validation_package.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_evidence_priority_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_source_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_source_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_provenance_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_url_remediation_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/validation_benchmark_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/validation_strategy_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/figures/bottleneck_attribution.png` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/figures/censored_by_disruption.png` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/figures/completion_by_disruption.png` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/figures/policy_regime_map.png` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/figures/policy_resource_tradeoff.png` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/phase8_compact_scoped_20260605/analysis/pilot_staged_scoped_ml_analysis.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/phase8_compact_scoped_20260605/analysis/pilot_staged_scoped_ml_feature_importance.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/phase8_compact_scoped_20260605/analysis/pilot_staged_scoped_ml_labels.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/phase8_compact_scoped_20260605/analysis/pilot_staged_scoped_ml_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/phase8_compact_scoped_20260605/analysis/pilot_staged_scoped_ml_metrics.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/phase8_compact_scoped_20260605/analysis/pilot_staged_scoped_ml_predictions.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/pilot_full_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/pilot_full_output_lock_receipt.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/pilot_full_results.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/pilot_full_summary.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/bottleneck_attribution_table.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/claim_boundary_table.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/figure_table_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/main_result_table.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/pilot_full_metric_ci.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/pilot_full_paired_delta_ci.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/pilot_full_statistics_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/policy_regime_table.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/generate_phase23_oracle.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/parameters.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/pilot_experiments.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_evidence.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_evidence_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/road_capacity_evidence.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/road_override_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `status.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_composable_service_pipeline.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_evidence.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_evidence_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_road_capacity_evidence.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| ?? | generated_result | `results/realworld_pilot/analysis/` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | generated_result | `results/realworld_pilot/phase8_compact_scoped_20260605/analysis/pilot_staged_scoped_ml_clusters.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | generated_result | `results/realworld_pilot/phase8_compact_scoped_20260605/analysis/pilot_staged_scoped_ml_shap_importance.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | generated_result | `results/realworld_pilot/pilot_full_graph.output.lock` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |

## Use

Run this before clean-checkout reproducibility review. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly marked outside the reviewer-bounded reproduction scope. The audit excludes its own generated CSV, manifest, and Markdown outputs from candidate rows so reruns do not create self-blockers. It also excludes review-package build, inventory, and path-audit sidecars because those are generated after ZIP assembly for external handoff and are outside reproduction-scope inputs.
