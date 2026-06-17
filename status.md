# Project Status

## Current Date And Workspace

- Date: 2026-06-09
- Workspace: `C:\project\transport-system-sim`
- Platform: Windows PowerShell
- Git branch: `main`
- Remote: `https://github.com/hyunjun1121/transport-system-sim.git`

## Latest Audit Snapshot

- `final_study_ready=false`
- Gate count: 15
- Ready gates: 3/15: `real_input_smoke`, `structured_disruptions`, `policy_alternatives`
- Blocked gates: 12/15: `pilot_region_accepted`, `cached_osm_input`, `graph_scale_strategy`, `data_provenance`, `parameter_evidence`, `rail_evidence`, `validation_package`, `sensitivity_analysis`, `full_experiment_output`, `manuscript_report_alignment`, `reproducibility`, `final_audit`
- Formal acceptance: 0/12 (all 12 formal artifacts intentionally absent until reviewer signoff)
- `publication_ready=false`
- `formal_acceptance_evidence=false`
- Claim-language guard: `blocking_finding_count=0`, `release_blocked=false`
- Dirty worktree: 616 uncommitted paths

## Key Metrics

- Phase gate ledgers: 13/13 present, 0 closed
- Artifact invalidation: 51 rows, 31 closed, 20 pending
- Review package ZIP: rebuilt 2026-06-09, 1319 files, mirror synced
- Pilot result files: 88
- Codebase: src 167 files, tests 163 files, scripts 135 files, docs 128 files
- No stub or empty source/test/script files

## Known Limitations

- Road speed: OSM `maxspeed` coverage sparse (5/10 classes have observed tags)
- Road capacity: OSM `lanes` tags absent (0/10 classes observed)
- Rail timing: headway/travel time are assumption proxies, not derived from GTFS/timetable
- Reproducibility: `clean_checkout_test_performed=false` (current-worktree smoke only)
- Critical-link blockage: reduced corridor multimodal fails 100% vs multi-corridor 0%
  in `songpa_critical_link_blockage` scenario (alternate-route gap documented in
  graph-scale decision packet)

## Review Package State

- `required_deliverables.zip`: expert-review handoff ZIP, rebuilt 2026-06-09
- `review_packages/expert_review_package.zip`: mirror copy, SHA256 matching
- `review_packages/expert_review_handoff_20260510.json`: sidecar with checksum and
  non-acceptance cover note, regenerated 2026-06-09
- `docs/review_package_build.md`: build manifest with file list and SHA256

## Study Scope

This is a decision-support simulation framework. It is not:
- an "operational" route plan (not claimed)
- a real-world "forecast" (not claimed)
- "calibrated" field "validation" (not claimed)
- publication-"ready" (not claimed)
- "final"-study-"ready" (not claimed)

Allowed framing: decision-support simulation, quasi-real input pipeline, stochastic
scenario comparison, resilience/sensitivity analysis, ML-assisted post-simulation
risk classification when runtime evidence supports the specific claim.

## Scripts

audit_agent_review_paths.py, audit_analysis_outputs.py, audit_claim_language.py,
audit_compact_scoped_outputs.py, audit_crn_pairing.py, audit_deterministic_rerun.py,
audit_final_study_readiness.py, audit_formal_acceptance_artifacts.py,
audit_formal_evidence_paths.py, audit_graph_scale_manifests.py,
audit_parameter_evidence.py, audit_plan_artifacts.py, audit_publication_readiness.py,
audit_rail_bounded_treatments.py, audit_rail_evidence.py,
audit_rail_station_bindings.py, audit_replication_adequacy.py,
audit_review_package_paths.py, audit_road_evidence.py,
audit_road_evidence_diagnostics.py, audit_road_overrides.py,
audit_sensitivity_diagnostics.py, audit_source_context_hashes.py,
audit_source_provenance.py, audit_tracked_artifacts.py, build_pilot_cache.py,
build_review_package.py, cache_ktdb_gtfs_source.py, cache_metro9_capacity_source.py,
check_gpu_ml_runtime.py, derive_rail_gtfs_evidence.py,
derive_rail_headway_evidence.py, derive_rail_service_evidence.py,
derive_rail_shortest_path_evidence.py, derive_rail_station_bindings.py,
fetch_rail_shortest_path_cache.py, fetch_rail_timetable_cache.py,
make_pilot_figures.py, make_pilot_statistics.py, normalize_rail_timetable_cache.py,
run_acceptance_audit.py, run_accessibility_loss_analysis.py,
run_clean_checkout_smoke.py, run_full_graph_smoke.py,
run_graph_scale_diagnostics.py, run_ml_analysis.py, run_osrm_route_benchmark.py,
run_phase8_micro_probe.py, run_pilot_experiments.py, run_pilot_smoke.py,
run_plausibility_validation.py, run_reproducibility_smoke.py, run_sensitivity.py,
run_variance_diagnostic.py, regenerate_truth_table.py,
validate_formal_acceptance_package.py, write_acceptance_blocker_queue.py,
write_acceptance_decision_templates.py, write_acceptance_task_assignments.py,
write_artifact_invalidation_matrix.py, write_claim_alignment_review_packet.py,
write_demand_fleet_behavior_profiles.py, write_dirty_worktree_classification.py,
write_disruption_scenario_manifest.py, write_experiment_design_decision_packet.py,
write_experiment_package_review_packet.py, write_experiment_statistical_plan.py,
write_experiment_strategy_readiness_packet.py, write_expert_review_handoff.py,
write_figure_table_review_packet.py, write_final_audit_decision_packet.py,
write_formal_acceptance_blocker_queue.py, write_formal_acceptance_evidence_matrix.py,
write_formal_acceptance_pre_review.py, write_full_graph_runtime_readiness_packet.py,
write_goal_completion_audit.py, write_graph_scale_method_decision_packet.py,
write_graph_scale_result_comparison.py, write_graph_scale_review_packet.py,
write_graph_scale_strategy_readiness_packet.py,
write_integrated_evidence_review_packet.py,
write_manuscript_report_decision_packet.py,
write_osm_graph_snapshot_review_packet.py, write_osrm_snapshot_manifest.py,
write_parameter_evidence_priority_packet.py,
write_parameter_evidence_source_request_packet.py, write_parameter_review_packet.py,
write_parameter_source_decision_packet.py, write_parameter_source_readiness_packet.py,
write_phase_gate_ledgers.py, write_phase8_precompact_tables.py,
write_pilot_privacy_review_packet.py, write_pilot_region_decision_packet.py,
write_rail_evidence_priority_packet.py, write_rail_evidence_review_packet.py,
write_rail_fetch_readiness_packet.py, write_rail_service_static_candidate.py,
write_rail_source_decision_action_ledger_template.py,
write_rail_source_decision_packet.py,
write_rail_source_decision_recommendation_packet.py,
write_rail_static_timetable_segment_pair_diagnostic.py,
write_rail_timing_source_request_packet.py, write_rail_transit_stress_profile_packet.py,
write_reproducibility_decision_packet.py, write_reproducibility_review_packet.py,
write_review_package_inventory.py, write_road_attribute_evidence.py,
write_road_capacity_evidence.py, write_road_class_override_source_candidate.py,
write_road_class_override_template.py, write_road_evidence_priority_packet.py,
write_road_evidence_review_packet.py, write_road_evidence_source_request_packet.py,
write_road_snapshot.py, write_road_source_decision_packet.py,
write_road_source_readiness_packet.py, write_road_speed_evidence.py,
write_route_road_evidence_exposure.py, write_runtime_preflight_manifest.py,
write_seed_stream_manifest.py, write_sensitivity_index_review_packet.py,
write_sensitivity_method_decision_packet.py, write_sensitivity_review_packet.py,
write_sensitivity_strategy_readiness_packet.py,
write_source_context_cache_decision_packet.py,
write_source_context_cache_request_packet.py, write_source_license_review_packet.py,
write_source_provenance_decision_packet.py, write_source_provenance_priority_packet.py,
write_source_url_remediation_packet.py, write_source_url_review_packet.py,
write_transfer_evidence_review_packet.py, write_upstream_lineage_review_packet.py,
write_validation_benchmark_decision_packet.py,
write_validation_benchmark_readiness_packet.py, write_validation_review_packet.py,
write_validation_strategy_readiness_packet.py

## Detailed Records

Detailed implementation notes, artifact lists, and per-phase status are in:
- `AGENTS.md`: repository structure and conventions
- `plan.md`: remaining work guide
- `docs/plan_completion_audit.md`: gate-by-gate audit snapshot
- `docs/current_goal_completion_audit.md`: goal completion audit
- `docs/publication_readiness_audit.md`: publication readiness (not claimed) audit
- `docs/phase_gate_ledger_audit.md`: phase gate ledger audit
- `docs/artifact_invalidation_matrix.md`: stale artifact disposition
