# Tracked Artifact Audit

This audit checks whether current changed artifacts would be present in a clean checkout of the current Git HEAD. It does not commit files, approve reproducibility, validate evidence quality, or close final-study gates.

## Summary

- Clean-checkout reproducibility ready: `false`
- Can mark complete: `false`
- Changed reproducibility artifacts: 538
- Blocking changed artifacts: 538
- Untracked artifacts: 165
- Modified or staged artifacts: 373

## Changed Artifacts

| Status | Category | Path | Required Action |
| --- | --- | --- | --- |
| M | root_document_or_config | `README.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `agents.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | agent_definition | `agents/acceptance_review_agents.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_orchestration_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_task_assignments.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_task_assignments_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_review_path_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/cached_osm_input__road_rail_parameter_evidence_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/final_audit__final_independent_audit_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/manuscript_report_alignment__paper_report_claim_alignment_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/parameter_evidence__road_rail_parameter_evidence_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/rail_evidence__road_rail_parameter_evidence_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/validation_package__validation_benchmark_strategy_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/claim_alignment_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/claim_alignment_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/crn_pairing_audit.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/crn_pairing_audit_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/current_goal_completion_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/deterministic_rerun_audit.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/deterministic_rerun_audit_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/data_provenance_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/final_audit_document_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/final_audit_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
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
| M | data_or_manifest | `data/manifests/experiment_statistical_analysis_plan.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/experiment_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/experiment_strategy_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/figure_table_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/figure_table_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/final_audit_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_blocker_queue.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_blocker_queue_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_evidence_matrix.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_evidence_matrix_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_package_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_evidence_path_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/manuscript_report_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/manuscript_report_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/pilot_experiment_design.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/pilot_region_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/pilot_region_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/publication_readiness_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/replication_adequacy_audit.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/replication_adequacy_audit_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/reproducibility_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/seed_stream_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_context_cache_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_context_cache_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_context_cache_request_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_context_cache_request_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_license_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_license_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_priority_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_priority_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_remediation_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_remediation_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_evidence_priority_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_evidence_priority_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_source_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_source_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_source_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_source_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/rail_evidence_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/rail_evidence_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/road_evidence_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/road_evidence_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/transfer_evidence_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/transfer_evidence_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/ktdb_gtfs_source_extract.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/metro9_capacity_source_extract.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_evidence_priority_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_evidence_priority_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_fetch_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_fetch_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_source_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_source_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_timing_source_request_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_timing_source_request_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/regions/pilot_region.yaml` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_evidence_source_request_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_evidence_source_request_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/scenarios/disruption_scenarios.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/clean_checkout_reproducibility_smoke_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/external_route_benchmarks.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/external_route_benchmarks_osrm.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/full_graph_runtime_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/full_graph_runtime_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/full_graph_smoke_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_alternate_routes_summary.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_manifest_audit.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_manifest_audit_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_method_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_method_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_multi_corridor_routes_summary.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_route_comparison_summary.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_strategy_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/integrated_evidence_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/integrated_evidence_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/osm_graph_snapshot_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/osrm_route_benchmark_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/osrm_route_benchmark_summary.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_smoke_log.jsonl` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_smoke_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/sensitivity_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/sensitivity_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/sensitivity_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/sensitivity_strategy_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_benchmark_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_benchmark_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_benchmark_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_benchmark_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_strategy_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_summary.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/acceptance_decision_templates.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/acceptance_task_assignments.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/accessibility_loss_analysis.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/agent_review_path_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/agents/acceptance_review_agents.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/analysis_corridor_method_note.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/claim_alignment_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/clean_checkout_reproducibility_smoke.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/crn_pairing_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/current_goal_completion_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/deterministic_rerun_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/experiment_design_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/experiment_package_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/experiment_statistical_analysis_plan.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/experiment_strategy_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/figure_table_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/final_audit_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_artifact_guard.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_blocker_queue.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_evidence_matrix.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_package_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_pre_review.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_evidence_path_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_target_placeholder_relocation.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/full_graph_runtime_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/full_graph_smoke.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_diagnostics.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_manifest_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_method_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_strategy_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/human_acceptance_runbook.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/integrated_evidence_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/manuscript_report_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/osrm_route_benchmark_manifest.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_evidence_priority_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_evidence_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_evidence_source_request_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_source_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_source_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/pilot_region_data_card.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/pilot_region_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/plan_completion_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/publication_readiness_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_evidence.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_evidence_priority_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_evidence_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_fetch_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_source_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_timing_source_request_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/realworld_pipeline.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/region_reuse_checklist.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/replication_adequacy_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/reproducibility_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/reproducibility_package.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/reproducibility_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/reproducibility_smoke.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/acceptance_review_index.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/cached_osm_input.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/final_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/manuscript_report_alignment.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/parameter_evidence.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/rail_evidence.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/reproducibility.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/validation_package.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_evidence_diagnostics.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_evidence_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_evidence_source_request_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_source_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_source_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/route_road_evidence_exposure.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/schemas/rail_gtfs_cache_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/schemas/rail_timetable_cache_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/seed_stream_manifest.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/sensitivity_diagnostics.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/sensitivity_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/sensitivity_strategy_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_context_cache_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_context_cache_request_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_license_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_provenance_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_provenance_manifest.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_url_remediation_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_url_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/transfer_evidence_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/validation_benchmark_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/validation_benchmark_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/validation_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/validation_strategy_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | paper | `paper/paper_draft.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `plan.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/audit_plan_artifacts.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/derive_rail_gtfs_evidence.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/run_full_graph_smoke.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/run_osrm_route_benchmark.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/run_pilot_experiments.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_experiment_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_full_graph_runtime_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_graph_scale_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_parameter_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_rail_evidence_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_rail_source_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_road_source_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_road_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_validation_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/README.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/__init__.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/acceptance_blocker_queue.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/acceptance_decision_templates.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/acceptance_orchestration.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/acceptance_task_assignments.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/attributes.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/claim_alignment_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/clean_checkout_smoke.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/crn_pairing_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/deterministic_rerun_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/disruption_scenarios.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/experiment_design_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/experiment_package_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/experiment_statistical_plan.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/experiment_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/figure_table_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/final_audit_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/final_study_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/formal_acceptance_evidence_matrix.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/formal_acceptance_package.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/formal_acceptance_pre_review.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/formal_evidence_path_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/full_graph_runtime_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/goal_completion_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/graph_scale_manifest_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/graph_scale_method_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/graph_scale_review.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/graph_scale_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/integrated_evidence_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/ktdb_gtfs_source.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/manuscript_report_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/metro9_capacity_source.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/osm_network.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/osrm_snapshot_manifest.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/parameter_evidence_priority_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/parameter_source_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/parameter_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/pilot_experiments.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/pilot_region_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/plausibility.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/publication_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_evidence.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_evidence_priority_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_evidence_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_fetch_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_gtfs.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_shortest_path.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_source_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_timetable.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_timing_request_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/replication_adequacy_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/reproducibility_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/reproducibility_smoke.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/road_evidence_request_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/road_evidence_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/road_source_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/road_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/seed_stream_manifest.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/sensitivity_diagnostics.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/sensitivity_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/sensitivity_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_context_cache_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_context_cache_request_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_license_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_provenance.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_provenance_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_provenance_priority_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_url_remediation_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_url_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/tracked_artifact_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/transfer_evidence_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/types.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/validation_benchmark_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/validation_benchmark_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/validation_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/validation_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `status.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_acceptance_orchestration.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_claim_alignment_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_disruption_scenarios.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_experiment_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_figure_table_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_final_audit_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_final_study_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_formal_acceptance_evidence_matrix.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_formal_acceptance_package.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_formal_acceptance_pre_review.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_full_graph_runtime_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_goal_completion_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_graph_scale_manifest_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_graph_scale_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_integrated_evidence_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_ktdb_gtfs_source.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_metro9_capacity_source.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_osm_network.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_osrm_snapshot_manifest.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_parameter_evidence_priority_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_parameter_source_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_parameter_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_pilot_experiments.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_plan_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_plausibility.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_publication_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_evidence_priority_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_evidence_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_fetch_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_gtfs.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_shortest_path.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_source_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_timetable.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_timing_request_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_reproducibility_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_road_evidence_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_road_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_sensitivity_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_sensitivity_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_source_context_cache_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_source_provenance.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_source_url_remediation_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_tracked_artifact_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_types.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_validation_benchmark_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_validation_benchmark_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_validation_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_validation_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| ?? | data_or_manifest | `data/manifests/phase_gate_ledger_audit.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/manifests/phase_gates/` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/manifests/source_context_hash_audit.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/parameters/road_attribute_evidence_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/parameters/road_attribute_evidence_table.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/pilot_rail_static_timetable_cache.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/pilot_rail_static_timetable_cache_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/pilot_rail_static_timetable_segment_pair_diagnostic.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/pilot_rail_static_timetable_segment_pair_diagnostic_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/pilot_rail_timetable_cache.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/pilot_rail_timetable_cache_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/pilot_rail_timetable_static_source.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/rail_bounded_treatment_audit.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/rail_source_decision_action_ledger_template.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/rail_source_decision_action_ledger_template_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/rail_source_decision_recommendation_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/rail_source_decision_recommendation_packet.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/rail_transit_stress_profile_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/rail/rail_transit_stress_profile_packet.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/road/snapshots/` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/scenarios/behavior_profiles.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/scenarios/demand_fleet_behavior_profile_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/scenarios/demand_profiles.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/scenarios/disruption_scenarios_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/scenarios/fleet_profiles.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_action_batch_inspection.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_action_batch_inspection_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_closeout_action_queue.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_closeout_action_queue_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_closeout_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_closeout_readiness_audit.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_closeout_readiness_audit_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_closeout_template.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_matrix.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_matrix_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_claim_reference_remediation_packet.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_claim_reference_remediation_packet_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_closeout_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_closeout_prefill.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_closeout_prefill_gap_audit.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_closeout_prefill_gap_audit_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_closeout_prefill_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_closeout_template.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_main_closeout_copy_audit.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_main_closeout_copy_audit_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_main_closeout_draft_overlay.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_main_closeout_draft_overlay_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_non_evidence_index.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_non_evidence_index_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_non_evidence_transfer_packet.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_non_evidence_transfer_packet_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_reference_triage.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_reference_triage_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_scope_audit.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_quarantine_scope_audit_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_upstream_lineage_review_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/artifact_invalidation_upstream_lineage_review_packet.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/benchmark_threshold_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/benchmark_threshold_table.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/claim_language_guard.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/claim_language_guard_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/gpu_ml_runtime_log.jsonl` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/gpu_ml_runtime_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/policy_feasibility_fairness_manifest.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/policy_feasibility_fairness_table.csv` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | data_or_manifest | `data/validation/runtime_preflight/` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_action_batch_inspection.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_closeout_action_queue.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_closeout_readiness_audit.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_closeout_template.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_matrix.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_quarantine_claim_reference_remediation_packet.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_quarantine_closeout_prefill.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_quarantine_closeout_prefill_gap_audit.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_quarantine_closeout_template.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_quarantine_main_closeout_copy_audit.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_quarantine_main_closeout_draft_overlay.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_quarantine_non_evidence_index.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_quarantine_non_evidence_transfer_packet.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_quarantine_reference_triage.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_quarantine_scope_audit.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/artifact_invalidation_upstream_lineage_review_packet.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/benchmark_threshold_table.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/claim_language_guard.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/demand_fleet_behavior_profiles.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/disruption_scenarios.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/gpu_ml_runtime_check.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/phase_gate_ledger_audit.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/policy_feasibility_fairness_table.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/rail_bounded_treatment_audit.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/rail_source_decision_action_ledger_template.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/rail_source_decision_recommendation_packet.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/rail_static_timetable_segment_pair_diagnostic.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/rail_transit_stress_profile_packet.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/recovery/agent_ledgers/` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/recovery/phase0_forward_baseline_results_20260602.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/recovery/phase1_registry_schema_results_20260602.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/recovery/phase2_road_snapshot_results_20260602.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/recovery/phase3_road_attribute_evidence_results_20260602.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/recovery/phase4_rail_gtfs_validation_guard_results_20260602.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/recovery/phase4_rail_source_decision_refinement_20260603.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/recovery/phase4_rail_transit_stress_profile_results_20260602.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/recovery/runtime_preflight/` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/road_attribute_evidence.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/runtime_preflight/` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | documentation | `docs/source_context_hash_audit.md` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | generated_result | `results/realworld_pilot/phase8_compact_engineering_20260603/` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | generated_result | `results/realworld_pilot/phase8_compact_scoped_20260605/` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | generated_result | `results/realworld_pilot/phase8_compact_scoped_probe_20260605/` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | schema | `schemas/phase_gate_ledger.schema.json` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/audit_claim_language.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/audit_rail_bounded_treatments.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/audit_source_context_hashes.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/check_gpu_ml_runtime.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/normalize_rail_timetable_cache.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_artifact_invalidation_matrix.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_demand_fleet_behavior_profiles.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_dirty_worktree_classification.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_disruption_scenario_manifest.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_phase8_precompact_tables.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_phase_gate_ledgers.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_rail_source_decision_action_ledger_template.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_rail_source_decision_recommendation_packet.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_rail_static_timetable_segment_pair_diagnostic.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_rail_transit_stress_profile_packet.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_road_attribute_evidence.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_road_snapshot.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_runtime_preflight_manifest.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | script | `scripts/write_upstream_lineage_review_packet.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/artifact_invalidation_matrix.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/claim_language_guard.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/demand_fleet_behavior_profiles.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/gpu_ml_runtime.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/phase8_precompact_tables.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/phase_gate_ledger.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/rail_bounded_treatment_audit.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/rail_source_decision_recommendation_packet.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/rail_static_timetable_segment_pair_diagnostic.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/rail_timetable_static.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/rail_transit_stress_profile_packet.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/road_attribute_evidence.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/road_snapshot.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/runtime_preflight.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/source_artifacts.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/source_context_hash_audit.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | realworld_code | `src/realworld/upstream_lineage_review_packet.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_artifact_invalidation_matrix.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_claim_language_guard.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_demand_fleet_behavior_profiles.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_gpu_ml_runtime.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_phase8_precompact_tables.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_phase_gate_ledger.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_rail_bounded_treatment_audit.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_rail_derivation_scripts.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_rail_source_decision_action_ledger_template.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_rail_source_decision_recommendation_packet.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_rail_static_timetable_segment_pair_diagnostic.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_rail_timetable_static.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_rail_transit_stress_profile_packet.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_road_attribute_evidence.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_road_snapshot.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_runtime_preflight.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_source_artifacts.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_source_context_hash_audit.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |
| ?? | test | `tests/test_realworld_upstream_lineage_review_packet.py` | Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope. |

## Use

Run this before clean-checkout reproducibility review. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly marked outside the reviewer-bounded reproduction scope. The audit excludes its own generated CSV, manifest, and Markdown outputs from candidate rows so reruns do not create self-blockers. It also excludes review-package build, inventory, and path-audit sidecars because those are generated after ZIP assembly for external handoff and are outside reproduction-scope inputs.
