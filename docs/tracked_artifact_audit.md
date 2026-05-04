# Tracked Artifact Audit

This audit checks whether current changed artifacts would be present in a clean checkout of the current Git HEAD. It does not commit files, approve reproducibility, validate evidence quality, or close final-study gates.

## Summary

- Clean-checkout reproducibility ready: `false`
- Can mark complete: `false`
- Changed reproducibility artifacts: 96
- Blocking changed artifacts: 96
- Untracked artifacts: 88
- Modified or staged artifacts: 8

## Changed Artifacts

| Status | Category | Path | Required Action |
| --- | --- | --- | --- |
| M | root_document_or_config | `README.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `agents.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | paper | `paper/paper_draft.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `plan.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `report.docx` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `report_draft.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `requirements.txt` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `status.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| ?? | agent_definition | `agents/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | generated_result | `results/realworld_pilot/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | schema | `schemas/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_acceptance_blocker_queue.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_acceptance_decision_templates.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_acceptance_orchestration.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_acceptance_records.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_acceptance_task_assignments.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_accessibility.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_adapter.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_agent_review_path_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_attributes.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_claim_alignment_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_disruption_scenarios.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_end_to_end.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_experiment_acceptance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_experiment_package_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_final_audit_acceptance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_final_study_readiness.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_formal_acceptance_evidence_matrix.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_formal_acceptance_guard.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_formal_acceptance_package.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_formal_acceptance_pre_review.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_formal_evidence_path_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_full_graph_smoke.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_goal_completion_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_graph_scale_acceptance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_graph_scale_diagnostics.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_graph_scale_result_comparison.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_graph_scale_review.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_manuscript_acceptance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_osm_network.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_osrm_snapshot_manifest.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_parameter_acceptance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_parameter_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_parameter_evidence_request_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_parameter_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_parameters.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_pilot_acceptance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_pilot_experiments.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_pilot_figures.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_pilot_privacy_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_pilot_smoke.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_pilot_statistics.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_plan_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_plausibility.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_policy_alternatives.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_provenance_acceptance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_publication_readiness.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_rail_evidence.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_rail_evidence_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_rail_gtfs.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_rail_shortest_path.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_rail_shortest_path_api.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_rail_station_binding.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_rail_station_cache.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_rail_timetable.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_rail_timetable_api.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_rail_timing_request_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_reproducibility_acceptance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_reproducibility_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_reproducibility_smoke.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_road_capacity_evidence.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_road_evidence.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_road_evidence_diagnostics.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_road_evidence_request_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_road_evidence_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_road_override_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_road_override_template.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_road_overrides.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_road_speed_evidence.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_route_road_evidence_exposure.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_sensitivity.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_sensitivity_acceptance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_sensitivity_diagnostics.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_sensitivity_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_source_license_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_source_provenance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_source_url_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_tracked_artifact_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_types.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_validation.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_validation_acceptance.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_validation_review_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |

## Use

Run this before clean-checkout reproducibility acceptance. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly excluded from the accepted reproduction scope.
