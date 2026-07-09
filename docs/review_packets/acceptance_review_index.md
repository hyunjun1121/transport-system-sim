# Acceptance Review Index

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Final-study ready: `false`
- Record count: 12
- Can-mark-complete records: 6

| Gate | Agent | Status | Can Mark Complete | Required Action Count |
| --- | --- | --- | --- | --- |
| `pilot_region_accepted` | Pilot Region & Privacy Review Agent | `accepted` | `true` | 0 |
| `data_provenance` | OSM / Source / License / Provenance Review Agent | `accepted` | `true` | 0 |
| `graph_scale_strategy` | Graph Scale Method Review Agent | `needs_human_review` | `false` | 3 |
| `cached_osm_input` | Road / Rail / Parameter Evidence Agent | `accepted` | `true` | 0 |
| `parameter_evidence` | Road / Rail / Parameter Evidence Agent | `accepted` | `true` | 0 |
| `rail_evidence` | Road / Rail / Parameter Evidence Agent | `blocked` | `false` | 21 |
| `validation_package` | Benchmark Strategy Review Agent | `accepted` | `true` | 0 |
| `sensitivity_analysis` | Sensitivity Analysis Review Agent | `accepted` | `true` | 0 |
| `full_experiment_output` | Full Experiment Package Agent | `blocked` | `false` | 15 |
| `manuscript_report_alignment` | Paper / Report Claim Alignment Agent | `blocked` | `false` | 17 |
| `reproducibility` | Clean-Checkout Reproducibility Agent | `blocked` | `false` | 3 |
| `final_audit` | Independent Audit Review Agent | `blocked` | `false` | 8 |

## Source Provenance Priority Snapshot

This section summarizes the provenance triage packet for the data-provenance reviewer. It is not source acceptance or license approval.

- Manifest: `data/manifests/source_provenance_priority_manifest.json`
- Packet: `data/manifests/source_provenance_priority_packet.csv`
- Manifest present: `true`
- Source rows: 11
- Blocking context-source target gaps: 3
- Human-review sources: 9
- Cached public snapshots: 5
- Repository input sources: 4
- Provenance gate closure candidates: 0
- Can mark complete from provenance triage: `false`

Required reviewer actions:

- Review-only source note: provide reviewed target payloads, retain context-source rows as sensitivity/context-only evidence, or explicitly exclude them before release-scope claims
- Review-only source note: review cached public snapshots for license, attribution, snapshot, and reproducibility suitability
- Review-only source note: confirm project-owned local citations and privacy abstraction for repository inputs
- Review-only source note: resolve alternate URL issues before the provenance review record is created
- Review-only source note: create data/manifests/provenance_acceptance.json only after source-backed review

Provenance blockers:

- Blocked non-approval source note: formal provenance acceptance record is absent
- Blocked non-approval source note: context-source target artifacts still need reviewed payloads, sensitivity/context-only retention decisions, or exclusion decisions
- Blocked non-approval source note: cached public snapshots still require license, attribution, snapshot, and reproducibility review
- Blocked non-approval source note: repository inputs still require human scope/privacy/reproducibility review
- Blocked non-approval source note: URL remediation rows still require reviewer confirmation

## Review Packet Status Snapshots

These manifest summaries help reviewers triage existing packets. They do not accept any gate or choose a final method.

| Packet | Rows | Blocking | Human Review | Gate Candidates | Can Complete | Key Status Counts |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `Source Provenance Priority` | 11 | 2 | 9 | 0 | `false` | blocked_context_only_source_not_cached=2; needs_human_review_cached_snapshot_source=5; needs_human_review_repository_input_source=4 |
| `Source Context Cache Requests` | 3 | 3 | 0 | 0 | `false` | blocked_missing_context_source_cache=3 |
| `Source Context Cache Decisions` | 3 | 3 | 0 | 0 | `false` | blocked_missing_context_source_cache_retention_or_exclusion_decision=3 |
| `Source Provenance Decision` | 7 | 1 | 6 | 0 | `false` | blocked_missing_context_cache_retention_or_exclusion_decisions=1; needs_human_review_cached_snapshot_and_repository_scope=1; needs_human_review_existing_provenance_acceptance=1; +4 more |
| `Source/License Review` | 11 | 2 | 11 | 0 | `false` | cached_snapshot_pending_review=5; context_only_not_cached=2; repository_input_pending_review=4 |
| `Source URL Review` | 17 | 1 | 17 | 0 | `false` | network_error=1; no_url_detected=4; reachable=12 |
| `Source URL Remediation` | 17 | 0 | 0 | 0 | `false` | alternate_reachable_url_needs_review=1; local_citation_needs_review=4; reachable_needs_license_review=12 |
| `Pilot Region Decision` | 6 | 0 | 6 | 0 | `false` | needs_human_review_claim_boundary=1; needs_human_review_existing_graph_scale_acceptance=1; needs_human_review_existing_pilot_acceptance=1; +3 more |
| `Graph-Scale Method Review` | 4 | 0 | 0 | 0 | `false` |  |
| `Full-Graph Runtime Review` | 4 | 2 | 2 | 0 | `false` | blocked_missing_downstream_full_graph_regeneration_decision=1; blocked_missing_full_graph_full_profile_outputs=1; needs_human_review_full_graph_runtime_scope_decision=1; +1 more |
| `Graph-Scale Strategy Review` | 5 | 1 | 4 | 0 | `false` | blocked_missing_full_graph_experiment_outputs=1; needs_human_review_graph_scale_acceptance_record=1; needs_human_review_multi_corridor_result_deltas=1; +2 more |
| `Graph-Scale Method Decision` | 7 | 2 | 5 | 0 | `false` | blocked_missing_downstream_regeneration_decision=1; blocked_missing_full_graph_full_profile_outputs=1; needs_human_review_existing_graph_scale_acceptance=1; +4 more |
| `Graph-Scale Manifest Audit` | 13 | 0 | 0 | 0 | `false` | complete_reduced_analysis_graph_recorded=13 |
| `Graph-Scale Result Comparison` | 6877 | 0 | 0 | 0 | `false` | candidate_improves=588; candidate_worsens=27; current_only=6058; +2 more |
| `Road Evidence Priority` | 11 | 1 | 6 | 0 | `false` | blocked_exposed_connector_assumption=1; needs_review_exposed_medium_priority_road_evidence_gap=6; queued_no_current_canonical_route_exposure=4 |
| `OSM Graph Snapshot Review` | 6 | 4 | 2 | 0 | `false` | blocked_missing_or_incomplete_osm_cache_metadata=1; blocked_osm_snapshot_claim_boundary=1; blocked_osm_source_provenance_pending=1; +3 more |
| `Road Source Review` | 5 | 0 | 5 | 0 | `false` | needs_human_review_benchmark_strategy=1; needs_human_review_disruption_scenario=1; needs_human_review_lane_capacity_candidates=1; +2 more |
| `Road Source Decisions` | 5 | 0 | 5 | 0 | `false` | needs_human_review_road_source_decision=5 |
| `Parameter Evidence Priority` | 7 | 0 | 7 | 0 | `false` | needs_human_review_demand_scenario=1; needs_human_review_dispatch_policy=1; needs_human_review_disruption_parameter_scenario=1; +4 more |
| `Parameter Source Review` | 7 | 0 | 7 | 0 | `false` | needs_human_review_demand_scenario=1; needs_human_review_dispatch_policy=1; needs_human_review_disruption_parameter_scenario=1; +4 more |
| `Parameter Source Decisions` | 7 | 0 | 7 | 0 | `false` | needs_human_review_parameter_source_decision=7 |
| `Transfer Evidence Review` | 7 | 1 | 6 | 0 | `false` | documented_component_accounting=2; documented_parameter_proxy=1; missing_station_layout_or_observed_transfer_source=1; +2 more |
| `Rail Evidence Priority` | 7 | 3 | 2 | 0 | `false` | blocked_missing_data_go_kr_key=2; blocked_missing_reviewed_gtfs_file=1; needs_human_review_availability_scenario=1; +3 more |
| `Rail Fetch Review` | 6 | 3 | 2 | 0 | `false` | blocked_missing_data_go_kr_key=2; blocked_missing_reviewed_gtfs_file=1; needs_human_review_availability_scenario=1; +2 more |
| `Rail Source Decisions` | 6 | 3 | 3 | 0 | `false` | blocked_missing_rail_source_decision=3; needs_human_review_rail_source_decision=2; needs_human_review_ready_rail_source_decision=1 |
| `Benchmark Evidence Review` | 4 | 0 | 4 | 0 | `false` | needs_human_review_alternative_benchmark_decision=1; needs_human_review_existing_validation_acceptance=1; needs_human_review_fallback_warn_rows=1; +1 more |
| `Benchmark Evidence Decision` | 6 | 2 | 4 | 0 | `false` | blocked_scaffold_validation_scope=1; blocked_weak_route_road_evidence_dependency=1; needs_human_review_alternative_benchmark_scope=1; +3 more |
| `Benchmark Strategy Review` | 7 | 3 | 4 | 0 | `false` | blocked_fallback_benchmark_failures=1; blocked_missing_validation_acceptance_record=1; blocked_weak_route_road_evidence_exposure=1; +4 more |
| `Sensitivity Method Decision` | 7 | 2 | 5 | 0 | `false` | blocked_missing_morris_vs_sobol_decision=1; blocked_reduced_graph_scope_dependency=1; needs_human_review_defer_or_continue=1; +4 more |
| `Sensitivity Index Review` | 7 | 0 | 7 | 0 | `false` | needs_human_review_unavailable_indices=2; needs_human_review_zero_mu_star_rows=5 |
| `Sensitivity Strategy Review` | 7 | 2 | 5 | 0 | `false` | blocked_missing_morris_vs_sobol_decision=1; blocked_reduced_graph_scope_for_sensitivity_claims=1; needs_human_review_morris_artifact_selection=1; +4 more |
| `Experiment Strategy Review` | 9 | 3 | 6 | 0 | `false` | blocked_graph_scale_dependency=1; blocked_input_evidence_dependency=1; blocked_scaffold_or_not_calibrated_experiment_scope=1; +5 more |
| `Experiment Design Decision` | 8 | 3 | 5 | 0 | `false` | blocked_graph_scale_dependency=1; blocked_input_evidence_dependency=1; blocked_scaffold_or_not_calibrated_experiment_scope=1; +5 more |
| `Integrated E2/E3/E5 Evidence Review` | 5 | 5 | 16 | 0 | `false` | blocked_experiment_design_dependencies=1; blocked_integrated_claim_boundary=1; blocked_rail_source_decisions_pending=1; +2 more |
| `Figure/Table Review` | 8 | 2 | 6 | 0 | `false` | blocked_reduced_graph_scope_dependency=1; blocked_upstream_evidence_dependency=1; needs_human_review_artifact_inventory=1; +5 more |
| `Manuscript/Report Decision` | 7 | 3 | 4 | 0 | `false` | blocked_claim_alignment_review_dependency=1; blocked_figure_table_review_dependency=1; blocked_upstream_evidence_gate_dependency=1; +4 more |
| `Reproducibility Review` | 8 | 3 | 0 | 0 | `false` | blocked_dirty_worktree=1; blocked_full_clean_checkout_not_run=1; blocked_untracked_reproducibility_artifacts=1; +5 more |
| `Reproducibility Decision` | 7 | 0 | 7 | 0 | `false` | needs_human_review_artifact_regeneration=1; needs_human_review_clean_checkout_evidence_scope=1; needs_human_review_command_ladder_scope=1; +4 more |
| `Independent Audit Decision` | 7 | 1 | 6 | 0 | `false` | blocked_pre_final_gates_not_ready=1; needs_human_review_final_packet_handoff=1; needs_human_review_final_study_audit_document=1; +4 more |
| `Review Decision Templates` | 9 | 0 | 0 | 0 | `false` |  |
| `Formal Acceptance Blocker Queue` | 2 | 1 | 2 | 0 | `false` | blocked=1; ready=1 |
| `Review Task Assignments` | 2 | 0 | 2 | 0 | `false` | apply_reviewed_input_and_regenerate=1; resolve_blocker=1 |
| `Formal Evidence Matrix` | 12 | 1 | 1 | 0 | `false` | blocked=1; ready=11 |
| `Formal Pre-Review` | 12 | 1 | 12 | 0 | `false` | blocked_missing_evidence=1; recommended_approve=11 |
| `Formal Package Audit` | 12 | 1 | 0 | 0 | `false` |  |
| `Formal Evidence Path Audit` | 11 | 0 | 0 | 0 | `false` | present_local_evidence=110 |
| `Agent Review Path Audit` | 12 | 0 | 0 | 0 | `false` | missing_formal_target=0; present=853 |
| `Tracked Artifact Audit` | 210 | 210 | 0 | 0 | `false` | data_or_manifest=125; documentation=46; generated_result=27; +4 more |
| `Current Goal Completion Audit` | 15 | 6 | 0 | 0 | `false` | blocked=6; missing_acceptance_artifact=0; ready=9 |
| `Publication Blocker Audit` | 10 | 2 | 0 | 0 | `false` | blocked=2; ready=8 |

Priority blockers by packet:

- `Source Provenance Priority`: Blocked non-approval source note: formal provenance acceptance record is absent (+4 more)
- `Source Context Cache Requests`: Blocked non-approval source note: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions (+2 more)
- `Source Context Cache Decisions`: Blocked non-approval source note: formal provenance acceptance record is absent (+5 more)
- `Source Provenance Decision`: Blocked non-approval source note: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- `Source/License Review`: Blocked non-approval source note: formal provenance acceptance record is absent (+2 more)
- `Source URL Review`: Blocked non-approval source note: formal provenance acceptance record is absent (+3 more)
- `Source URL Remediation`: Blocked non-approval source note: formal provenance acceptance record is absent (+3 more)
- `Full-Graph Runtime Review`: Blocked non-approval source note: full-graph full-profile outputs are absent (+2 more)
- `Graph-Scale Strategy Review`: Blocked non-approval source note: full bus-practical graph has smoke evidence only (+3 more)
- `Graph-Scale Method Decision`: Blocked non-approval source note: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output (+1 more)
- `Road Evidence Priority`: Blocked non-approval source note: reviewed road_class_overrides.csv is still absent (+2 more)
- `OSM Graph Snapshot Review`: Blocked non-approval source note: cache metadata, attribution, counts, or offline-test boundary is incomplete (+3 more)
- `Road Source Review`: Blocked non-approval source note: capacity and disruption evidence still require external source or formal assumption decisions (+1 more)
- `Road Source Decisions`: Blocked non-approval source note: road_class_overrides.csv exists but remains blocked until source-backed review and application are recorded (+2 more)
- `Parameter Evidence Priority`: Blocked non-approval source note: transfer-delay evidence still requires human review and source-backed or accepted-assumption treatment (+4 more)
- `Parameter Source Review`: Blocked non-approval source note: all rows require human review or external source decisions before release-scope claims (+2 more)
- `Parameter Source Decisions`: Blocked non-approval source note: formal parameter acceptance table is absent (+2 more)
- `Transfer Evidence Review`: Blocked non-approval source note: station-layout, observed transfer, or pedestrian-flow source artifact is still absent (+2 more)
- `Rail Evidence Priority`: Blocked non-approval source note: source-backed rail timing evidence remains incomplete until API/GTFS/travel-time source paths are reviewed and retained (+2 more)
- `Rail Fetch Review`: Blocked non-approval source note: source-backed rail timing evidence remains incomplete until every required timing source is reviewed and retained (+5 more)
- `Rail Source Decisions`: Blocked non-approval source note: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests (+6 more)
- `Benchmark Evidence Review`: Blocked non-approval source note: benchmark strategy still requires human review and validation_acceptance.json
- `Benchmark Evidence Decision`: Blocked non-approval source note: validation summary still declares scaffold or sanity scope (+1 more)
- `Benchmark Strategy Review`: Blocked non-approval source note: validation_acceptance.json is absent (+1 more)
- `Sensitivity Method Decision`: Blocked non-approval source note: Morris-vs-Sobol method decision is not recorded in formal acceptance (+1 more)
- `Sensitivity Index Review`: Blocked non-approval source note: metric-level index handling still requires human review (+1 more)
- `Sensitivity Strategy Review`: Blocked non-approval source note: sensitivity outputs use a reduced analysis graph (+1 more)
- `Experiment Strategy Review`: Blocked non-approval source note: current full-pilot result scope is scaffold or not calibrated (+2 more)
- `Experiment Design Decision`: Blocked non-approval source note: experiment outputs depend on a graph method that is not selected by review (+2 more)
- `Integrated E2/E3/E5 Evidence Review`: Blocked non-approval source note: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests (+4 more)
- `Figure/Table Review`: Blocked non-approval source note: figure/table outputs depend on reduced analysis graph scope (+1 more)
- `Manuscript/Report Decision`: Blocked non-approval source note: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated (+2 more)
- `Independent Audit Decision`: Blocked non-approval source note: pre-final gates remain blocked: graph_scale_strategy, rail_evidence, full_experiment_output, manuscript_report_alignment, reproducibility
- `Formal Package Audit`: Blocked non-approval source note: road_class_overrides: verify graph-adapter runs apply the reviewed override table before using road-calibration claims (+4 more)
- `Formal Evidence Path Audit`: Blocked non-approval source note: data/parameters/road_class_overrides.csv: no evidence_paths, source_paths, reviewed_inputs, or data_snapshot_paths found
- `Tracked Artifact Audit`: Blocked non-approval source note: data/cache/pilot_region_road.graphml: Commit, stash, or document this change before clean-checkout reproduction. (+50 more)
- `Publication Blocker Audit`: Blocked non-approval source note: road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates (+13 more)

## Remaining Blockers

- Blocked non-approval action: graph_scale_strategy: Choose and document reduced-corridor, multi-corridor, or full-graph strategy.
- Blocked non-approval action: graph_scale_strategy: Create graph_scale_acceptance.json with matching graph counts and evidence paths.
- Blocked non-approval action: graph_scale_strategy: graph-scale acceptance counts must match the pilot full manifest counts: source_graph_nodes: acceptance=4608, manifest=197823; source_graph_edges: acceptance=9148, manifest=298020; analysis_graph_nodes: acceptance=164, manifest=2850; analysis_graph_edges: acceptance=246, manifest=3002
- Blocked non-approval action: rail_evidence: Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Blocked non-approval action: rail_evidence: Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- Blocked non-approval action: rail_evidence: rail fetch readiness: source-backed rail timing evidence remains incomplete until every required timing source is reviewed and retained
- Blocked non-approval action: rail_evidence: rail fetch readiness: API-key rows require DATA_GO_KR_KEY or reviewed cached API payloads
- Blocked non-approval action: rail_evidence: rail fetch readiness: reviewed-GTFS row requires a reviewed GTFS input and validator report
- Blocked non-approval action: rail_evidence: rail fetch readiness: reviewed-static-timetable cache is retained for headway review only; it does not close rail travel-time evidence
- Blocked non-approval action: rail_evidence: rail fetch readiness: capacity and availability rows still require reviewer-scoped bounded treatment or source-backed evidence
- Blocked non-approval action: rail_evidence: rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- Blocked non-approval action: rail_evidence: rail evidence priority: source-backed rail timing evidence remains incomplete until API/GTFS/travel-time source paths are reviewed and retained
- Blocked non-approval action: rail_evidence: rail evidence priority: DATA_GO_KR_KEY, reviewed GTFS input, or reviewed shortest-path cache is absent
- Blocked non-approval action: rail_evidence: rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- Blocked non-approval action: rail_evidence: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- Blocked non-approval action: rail_evidence: rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- Blocked non-approval action: rail_evidence: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- Blocked non-approval action: rail_evidence: rail source decision: non-formal source decisions do not close rail evidence, publication, study-closeout, or formal decision gates
- Blocked non-approval action: rail_evidence: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval action: rail_evidence: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- Blocked non-approval action: rail_evidence: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval action: rail_evidence: record reviewed rail source decisions for every row with zero blocking and human-review rows
- Blocked non-approval action: rail_evidence: non-formal rail source-decision action ledger cannot close rail evidence gate
- Blocked non-approval action: rail_evidence: rail source-decision action ledger is not formal acceptance evidence
- Blocked non-approval action: full_experiment_output: Regenerate or accept full outputs after input, graph-scale, and validation gates close.
- Blocked non-approval action: full_experiment_output: Create experiment_acceptance.json with matching run profile and row counts.
- Blocked non-approval action: full_experiment_output: resolve experiment strategy-readiness blockers before experiment acceptance
- Blocked non-approval action: full_experiment_output: experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- Blocked non-approval action: full_experiment_output: experiment strategy readiness: full-pilot outputs depend on a graph method that has no graph-scale decision
- Blocked non-approval action: full_experiment_output: experiment strategy readiness: upstream input, road override, parameter, benchmark, or provenance gates are unresolved
- Blocked non-approval action: full_experiment_output: review experiment strategy-readiness human-decision items before experiment acceptance
- Blocked non-approval action: full_experiment_output: resolve experiment design-decision blockers before experiment acceptance
- Blocked non-approval action: full_experiment_output: experiment design decision: experiment outputs depend on a graph method that is not selected by review
- Blocked non-approval action: full_experiment_output: experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not closed
- Blocked non-approval action: full_experiment_output: experiment design decision: current full-pilot result scope is scaffold or not calibrated
- Blocked non-approval action: full_experiment_output: review experiment design-decision human-decision items before experiment acceptance
- Blocked non-approval action: full_experiment_output: accept or regenerate full pilot outputs after input validation and graph-scale decision
- Blocked non-approval action: full_experiment_output: experiment acceptance counts must match the pilot full manifest: row_count: acceptance=15870, manifest=12420; summary_row_count: acceptance=529, manifest=414; scenario_count: acceptance=23, manifest=18
- Blocked non-approval action: full_experiment_output: review experiment-package rows before formal experiment acceptance
- Blocked non-approval action: manuscript_report_alignment: Revise or hold claims until all supporting evidence gates are accepted.
- Blocked non-approval action: manuscript_report_alignment: Create manuscript_acceptance.json after claim-by-claim review.
- Blocked non-approval action: manuscript_report_alignment: close evidence gates before final paper/report claims
- Blocked non-approval action: manuscript_report_alignment: revise figure/table claim boundary from scaffold to accepted study scope
- Blocked non-approval action: manuscript_report_alignment: resolve figure/table review blockers before manuscript acceptance
- Blocked non-approval action: manuscript_report_alignment: figure/table review: figure/table outputs depend on reduced analysis graph scope
- Blocked non-approval action: manuscript_report_alignment: figure/table review: figure/table source outputs remain scaffold or not calibrated
- Blocked non-approval action: manuscript_report_alignment: review figure/table human-review rows before manuscript acceptance
- Blocked non-approval action: manuscript_report_alignment: review or revise claim-alignment overclaim candidates before manuscript acceptance
- Blocked non-approval action: manuscript_report_alignment: claim alignment: formal manuscript/report review record is absent
- Blocked non-approval action: manuscript_report_alignment: claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- Blocked non-approval action: manuscript_report_alignment: claim alignment: evidence gates remain blocked, so result claims cannot be treated as target-study claims
- Blocked non-approval action: manuscript_report_alignment: resolve manuscript/report decision blockers before manuscript acceptance
- Blocked non-approval action: manuscript_report_alignment: manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated
- Blocked non-approval action: manuscript_report_alignment: manuscript/report decision: claim-alignment packet has 55 rows requiring revision or explicit retention
- Blocked non-approval action: manuscript_report_alignment: manuscript/report decision: upstream evidence gates blocked: graph_scale_strategy, rail_evidence, full_experiment_output
- Blocked non-approval action: manuscript_report_alignment: review manuscript/report human-decision rows before manuscript acceptance
- Blocked non-approval action: reproducibility: Run or document clean-checkout validation with command log and artifact regeneration evidence.
- Blocked non-approval action: reproducibility: Create reproducibility_acceptance.json only after accepted reproduction scope is complete.
- Blocked non-approval action: reproducibility: review reproducibility human-decision rows before reproducibility acceptance
- Blocked non-approval action: final_audit: After all pre-final gates are ready, write the independent prompt-to-artifact final audit.
- Blocked non-approval action: final_audit: Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
- Blocked non-approval action: final_audit: resolve final-audit decision blockers before final-audit acceptance
- Blocked non-approval action: final_audit: final-audit decision: pre-final gates remain blocked: graph_scale_strategy, rail_evidence, full_experiment_output, manuscript_report_alignment, reproducibility
- Blocked non-approval action: final_audit: review final-audit human-decision rows before final-audit acceptance
- Blocked non-approval action: final_audit: final-audit ready_gate_ids must match current ready gates
- Blocked non-approval action: final_audit: final-audit blocked_gate_ids must match current blocked gates
- Blocked non-approval action: final_audit: all pre-final gates must be ready before final audit acceptance: graph_scale_strategy, rail_evidence, full_experiment_output, manuscript_report_alignment, reproducibility
- Blocked non-approval audit item: Graph-Scale Strategy: graph-scale acceptance counts must match the pilot full manifest counts: source_graph_nodes: acceptance=4608, manifest=197823; source_graph_edges: acceptance=9148, manifest=298020; analysis_graph_nodes: acceptance=164, manifest=2850; analysis_graph_edges: acceptance=246, manifest=3002
- Blocked non-approval audit item: Data Provenance: source provenance priority: formal provenance acceptance record is absent
- Blocked non-approval audit item: Data Provenance: source provenance priority: context-source target artifacts still need reviewed payloads, sensitivity/context-only retention decisions, or exclusion decisions
- Blocked non-approval audit item: Data Provenance: source provenance priority: cached public snapshots still require license, attribution, snapshot, and reproducibility review
- Blocked non-approval audit item: Data Provenance: source provenance priority: repository inputs still require human scope/privacy/reproducibility review
- Blocked non-approval audit item: Data Provenance: source provenance priority: URL remediation rows still require reviewer confirmation
- Blocked non-approval audit item: Data Provenance: source context cache request: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- Blocked non-approval audit item: Data Provenance: source context cache request: license, attribution, snapshot, and reproducibility review are still required for retained public sources
- Blocked non-approval audit item: Data Provenance: source context cache request: formal provenance acceptance record is absent
- Blocked non-approval audit item: Data Provenance: source context cache decision: formal provenance acceptance record is absent
- Blocked non-approval audit item: Data Provenance: source context cache decision: target cache/retention/exclusion decisions are pending for context-source rows
- Blocked non-approval audit item: Data Provenance: source context cache decision: retained context sources still require license, attribution, snapshot, and reproducibility review
- Blocked non-approval audit item: Data Provenance: source context cache decision: ktdb_public_transport_gtfs_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- Blocked non-approval audit item: Data Provenance: source context cache decision: seoul_shortest_path_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- Blocked non-approval audit item: Data Provenance: source context cache decision: seoul_timetable_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- Blocked non-approval audit item: Rail Evidence: rail fetch readiness: source-backed rail timing evidence remains incomplete until every required timing source is reviewed and retained
- Blocked non-approval audit item: Rail Evidence: rail fetch readiness: API-key rows require DATA_GO_KR_KEY or reviewed cached API payloads
- Blocked non-approval audit item: Rail Evidence: rail fetch readiness: reviewed-GTFS row requires a reviewed GTFS input and validator report
- Blocked non-approval audit item: Rail Evidence: rail fetch readiness: reviewed-static-timetable cache is retained for headway review only; it does not close rail travel-time evidence
- Blocked non-approval audit item: Rail Evidence: rail fetch readiness: capacity and availability rows still require reviewer-scoped bounded treatment or source-backed evidence
- Blocked non-approval audit item: Rail Evidence: rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- Blocked non-approval audit item: Rail Evidence: rail evidence priority: source-backed rail timing evidence remains incomplete until API/GTFS/travel-time source paths are reviewed and retained
- Blocked non-approval audit item: Rail Evidence: rail evidence priority: DATA_GO_KR_KEY, reviewed GTFS input, or reviewed shortest-path cache is absent
- Blocked non-approval audit item: Rail Evidence: rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- Blocked non-approval audit item: Rail Evidence: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- Blocked non-approval audit item: Rail Evidence: rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- Blocked non-approval audit item: Rail Evidence: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- Blocked non-approval audit item: Rail Evidence: rail source decision: non-formal source decisions do not close rail evidence, publication, study-closeout, or formal decision gates
- Blocked non-approval audit item: Rail Evidence: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval audit item: Rail Evidence: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- Blocked non-approval audit item: Rail Evidence: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval audit item: Rail Evidence: record reviewed rail source decisions for every row with zero blocking and human-review rows
- Blocked non-approval audit item: Rail Evidence: non-formal rail source-decision action ledger cannot close rail evidence gate
- Blocked non-approval audit item: Rail Evidence: rail source-decision action ledger is not formal acceptance evidence
- Blocked non-approval audit item: Full Experiment Output: resolve experiment strategy-readiness blockers before experiment acceptance
- Blocked non-approval audit item: Full Experiment Output: experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- Blocked non-approval audit item: Full Experiment Output: experiment strategy readiness: full-pilot outputs depend on a graph method that has no graph-scale decision
- Blocked non-approval audit item: Full Experiment Output: experiment strategy readiness: upstream input, road override, parameter, benchmark, or provenance gates are unresolved
- Blocked non-approval audit item: Full Experiment Output: review experiment strategy-readiness human-decision items before experiment acceptance
- Blocked non-approval audit item: Full Experiment Output: resolve experiment design-decision blockers before experiment acceptance
- Blocked non-approval audit item: Full Experiment Output: experiment design decision: experiment outputs depend on a graph method that is not selected by review
- Blocked non-approval audit item: Full Experiment Output: experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not closed
- Blocked non-approval audit item: Full Experiment Output: experiment design decision: current full-pilot result scope is scaffold or not calibrated
- Blocked non-approval audit item: Full Experiment Output: review experiment design-decision human-decision items before experiment acceptance
- Blocked non-approval audit item: Full Experiment Output: accept or regenerate full pilot outputs after input validation and graph-scale decision
- Blocked non-approval audit item: Full Experiment Output: experiment acceptance counts must match the pilot full manifest: row_count: acceptance=15870, manifest=12420; summary_row_count: acceptance=529, manifest=414; scenario_count: acceptance=23, manifest=18
- Blocked non-approval audit item: Full Experiment Output: review experiment-package rows before formal experiment acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: close evidence gates before final paper/report claims
- Blocked non-approval audit item: Manuscript Report Alignment: revise figure/table claim boundary from scaffold to accepted study scope
- Blocked non-approval audit item: Manuscript Report Alignment: resolve figure/table review blockers before manuscript acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: figure/table review: figure/table outputs depend on reduced analysis graph scope
- Blocked non-approval audit item: Manuscript Report Alignment: figure/table review: figure/table source outputs remain scaffold or not calibrated
- Blocked non-approval audit item: Manuscript Report Alignment: review figure/table human-review rows before manuscript acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: review or revise claim-alignment overclaim candidates before manuscript acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: claim alignment: formal manuscript/report review record is absent
- Blocked non-approval audit item: Manuscript Report Alignment: claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- Blocked non-approval audit item: Manuscript Report Alignment: claim alignment: evidence gates remain blocked, so result claims cannot be treated as target-study claims
- Blocked non-approval audit item: Manuscript Report Alignment: resolve manuscript/report decision blockers before manuscript acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated
- Blocked non-approval audit item: Manuscript Report Alignment: manuscript/report decision: claim-alignment packet has 55 rows requiring revision or explicit retention
- Blocked non-approval audit item: Manuscript Report Alignment: manuscript/report decision: upstream evidence gates blocked: graph_scale_strategy, rail_evidence, full_experiment_output
- Blocked non-approval audit item: Manuscript Report Alignment: review manuscript/report human-decision rows before manuscript acceptance
- Blocked non-approval audit item: Reproducibility: review reproducibility human-decision rows before reproducibility acceptance
- Blocked non-approval audit item: Final Audit: resolve final-audit decision blockers before final-audit acceptance
- Blocked non-approval audit item: Final Audit: final-audit decision: pre-final gates remain blocked: graph_scale_strategy, rail_evidence, full_experiment_output, manuscript_report_alignment, reproducibility
- Blocked non-approval audit item: Final Audit: review final-audit human-decision rows before final-audit acceptance
- Blocked non-approval audit item: Final Audit: final-audit ready_gate_ids must match current ready gates
- Blocked non-approval audit item: Final Audit: final-audit blocked_gate_ids must match current blocked gates
- Blocked non-approval audit item: Final Audit: all pre-final gates must be ready before final audit acceptance: graph_scale_strategy, rail_evidence, full_experiment_output, manuscript_report_alignment, reproducibility
