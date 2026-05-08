# Tracked Artifact Audit

This audit checks whether current changed artifacts would be present in a clean checkout of the current Git HEAD. It does not commit files, approve reproducibility, validate evidence quality, or close final-study gates.

## Summary

- Clean-checkout reproducibility ready: `false`
- Can mark complete: `false`
- Changed reproducibility artifacts: 199
- Blocking changed artifacts: 199
- Untracked artifacts: 9
- Modified or staged artifacts: 190

## Changed Artifacts

| Status | Category | Path | Required Action |
| --- | --- | --- | --- |
| M | root_document_or_config | `README.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/cache/pilot_region_road_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_decision_template_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_orchestration_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_task_assignments_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_templates/graph_scale_acceptance_template.json` | Commit, stash, or document this change before clean-checkout reproduction. |
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
| M | data_or_manifest | `data/manifests/formal_acceptance_blocker_queue_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_evidence_matrix_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_license_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_license_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_remediation_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_remediation_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_source_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/parameters/parameter_source_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_fetch_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_fetch_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/rail/rail_timing_source_request_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/external_route_benchmarks_osrm.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_strategy_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/osrm_route_benchmark_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/osrm_route_benchmark_summary.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_smoke_log.jsonl` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_smoke_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/sensitivity_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/sensitivity_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/sensitivity_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/sensitivity_strategy_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/tracked_artifact_audit.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/tracked_artifact_audit_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/validation_strategy_readiness_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/accessibility_loss_analysis.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/agent_review_path_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/analysis_corridor_method_note.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/clean_checkout_reproducibility_smoke.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/current_goal_completion_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/experiment_acceptance_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/final_audit_acceptance_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_artifact_guard.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_pre_review.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_acceptance_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_diagnostics.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_result_comparison.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/graph_scale_strategy_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/manuscript_acceptance_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/osrm_route_benchmark_manifest.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_acceptance_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_evidence_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_evidence_source_request_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/parameter_source_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/pilot_acceptance_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/pilot_region_data_card.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/plan_completion_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/provenance_acceptance_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_evidence.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_evidence_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_fetch_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_gtfs_cache_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_shortest_path_cache_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_station_cache_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_timetable_cache_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/rail_timing_source_request_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/realworld_pipeline.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/reproducibility_acceptance_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/reproducibility_package.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/reproducibility_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/reproducibility_smoke.md` | Commit, stash, or document this change before clean-checkout reproduction. |
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
| M | documentation | `docs/road_class_override_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_evidence_diagnostics.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_evidence_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_evidence_source_request_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/road_source_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/route_road_evidence_exposure.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/sensitivity_acceptance_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/sensitivity_diagnostics.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/sensitivity_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/sensitivity_strategy_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_license_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_provenance_manifest.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_url_remediation_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_url_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/third_party_adaptations.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/tracked_artifact_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/validation_acceptance_schema.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/validation_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/validation_strategy_readiness_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | paper | `paper/paper_draft.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `plan.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `report.docx` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `report_draft.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/morris_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/morris_results.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/morris_summary.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/audit_plan_artifacts.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/build_pilot_cache.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/run_full_graph_smoke.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/run_osrm_route_benchmark.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_graph_scale_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_graph_scale_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/write_osrm_snapshot_manifest.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/README.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/__init__.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/final_study_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/goal_completion_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/graph_scale_review.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/graph_scale_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/osrm_snapshot_manifest.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/parameter_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/plausibility.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_fetch_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/rail_timing_request_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/road_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/sensitivity.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/sensitivity_diagnostics.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/sensitivity_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/sensitivity_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_url_remediation_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_url_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/tracked_artifact_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/validation_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/validation_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `status.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_final_study_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_osrm_snapshot_manifest.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_parameter_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_pilot_smoke.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_plan_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_plausibility.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_rail_fetch_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_road_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_sensitivity_diagnostics.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_sensitivity_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_sensitivity_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_source_url_remediation_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_source_url_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_tracked_artifact_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_validation_review_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_validation_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_scenario.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| ?? | data_or_manifest | `data/validation/full_graph_runtime_readiness_manifest.json` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/validation/full_graph_runtime_readiness_packet.csv` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/validation/full_graph_smoke_manifest.json` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/validation/osrm_route_raw/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/full_graph_runtime_readiness_packet.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/full_graph_smoke.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/write_full_graph_runtime_readiness_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/full_graph_runtime_readiness_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_full_graph_runtime_readiness_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |

## Use

Run this before clean-checkout reproducibility acceptance. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly excluded from the accepted reproduction scope.
