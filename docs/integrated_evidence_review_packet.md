# Integrated Evidence Review Packet

Integrated evidence review packet only; not rail evidence acceptance, not validation acceptance, not experiment acceptance, not calibrated real-world evidence, and not operational routing evidence. It cannot create formal acceptance artifacts.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Review rows: 5
- Blocking rows: 5
- Human-review rows: 0
- Underlying human-review decisions: 14
- Status counts: `{'blocked_experiment_design_dependencies': 1, 'blocked_integrated_claim_boundary': 1, 'blocked_rail_source_decisions_pending': 1, 'blocked_validation_benchmark_decisions_pending': 1, 'blocked_validation_strategy_dependencies': 1}`

## Review Rows

| Review | Status | Evidence | Required Action |
| --- | --- | --- | --- |
| e2_rail_timing_capacity_dependency | blocked_rail_source_decisions_pending | row_count=6; blocking_count=3; human_review_count=3; status_counts={"blocked_missing_rail_source_decision": 3, "needs_human_review_rail_source_decision": 2, "needs_human_review_ready_rail_source_decision": 1}; rail_service_evidence_artifact_present=true; accepted_source_backed_rail_service_evidence=false; source_cache_present_count=3 | Choose reviewed timetable, shortest-path, GTFS, capacity, and availability treatment before rail-dependent claims are retained. |
| e3_external_benchmark_dependency | blocked_validation_benchmark_decisions_pending | row_count=6; blocking_count=3; human_review_count=3; status_counts={"blocked_missing_validation_acceptance_record": 1, "blocked_scaffold_validation_scope": 1, "blocked_weak_route_road_evidence_dependency": 1, "needs_human_review_alternative_benchmark_scope": 1, "needs_human_review_cached_osrm_scope_policy": 1, "needs_human_review_fallback_warn_or_fail_policy": 1}; alternative_benchmark_decision_recorded=false; validation_gate_closure_candidate_count=0 | Decide whether fallback rows, cached OSRM, or another route engine can be used only as plausibility evidence. |
| validation_strategy_dependency | blocked_validation_strategy_dependencies | row_count=7; blocking_count=3; human_review_count=4; status_counts={"blocked_fallback_benchmark_failures": 1, "blocked_missing_validation_acceptance_record": 1, "blocked_weak_route_road_evidence_exposure": 1, "needs_human_review_accessibility_disconnections": 1, "needs_human_review_external_route_snap_distances": 1, "needs_human_review_internal_plausibility_warnings": 1, "needs_human_review_validation_summary_scope": 1}; validation_gate_closure_candidate_count=0 | Resolve weak route-road evidence exposure and validation-scope limitations before release-scope validation claims. |
| e5_experiment_profile_dependency | blocked_experiment_design_dependencies | row_count=8; blocking_count=4; human_review_count=4; status_counts={"blocked_graph_scale_dependency": 1, "blocked_input_evidence_dependency": 1, "blocked_missing_experiment_acceptance_record": 1, "blocked_scaffold_or_not_calibrated_experiment_scope": 1, "needs_human_review_current_full_profile_scope": 1, "needs_human_review_multi_corridor_profile_scope": 1, "needs_human_review_regenerate_or_retain_outputs": 1, "needs_human_review_scenario_policy_seed_design": 1}; selected_run_profile_recorded=false; scenario_policy_seed_decision_recorded=false | Choose retained or regenerated experiment outputs only after graph-scale and upstream input dependencies are resolved. |
| integrated_claim_boundary | blocked_integrated_claim_boundary | row_count=4; blocking_count=13; human_review_count=14; status_counts={"benchmark_blocking": 3, "experiment_blocking": 4, "rail_blocking": 3, "validation_blocking": 3}; formal_gate_closure_candidate_count=0; publication_ready=false | Keep fallback and OSRM rows labeled as plausibility checks and keep pilot outputs scaffold-scoped until the formal evidence and acceptance records are reviewed. |

## Boundary

- This packet is a reviewer worksheet, not an acceptance record.
- It does not make fallback or OSRM benchmarks ground truth.
- It does not certify rail timing, rail capacity, or pilot experiment outputs.
- Keep final-study claims blocked until the relevant formal acceptance artifacts are reviewed.
