# Acceptance Review Index

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Final-study ready: `false`
- Record count: 12
- Can-mark-complete records: 0

| Gate | Agent | Status | Can Mark Complete | Required Action Count |
| --- | --- | --- | --- | --- |
| `pilot_region_accepted` | Pilot Region & Privacy Review Agent | `needs_human_review` | `false` | 7 |
| `data_provenance` | OSM / Source / License / Provenance Review Agent | `blocked` | `false` | 24 |
| `graph_scale_strategy` | Graph Scale Method Review Agent | `needs_human_review` | `false` | 15 |
| `cached_osm_input` | Road / Rail / Parameter Evidence Agent | `blocked` | `false` | 17 |
| `parameter_evidence` | Road / Rail / Parameter Evidence Agent | `blocked` | `false` | 19 |
| `rail_evidence` | Road / Rail / Parameter Evidence Agent | `blocked` | `false` | 16 |
| `validation_package` | Validation Benchmark Strategy Agent | `needs_human_review` | `false` | 13 |
| `sensitivity_analysis` | Sensitivity Analysis Review Agent | `blocked` | `false` | 10 |
| `full_experiment_output` | Full Experiment Package Agent | `blocked` | `false` | 17 |
| `manuscript_report_alignment` | Paper / Report Claim Alignment Agent | `blocked` | `false` | 20 |
| `reproducibility` | Clean-Checkout Reproducibility Agent | `blocked` | `false` | 10 |
| `final_audit` | Final Independent Audit Agent | `blocked` | `false` | 5 |

## Source Provenance Priority Snapshot

This section summarizes the provenance triage packet for the data-provenance reviewer. It is not source acceptance or license approval.

- Manifest: `data/manifests/source_provenance_priority_manifest.json`
- Packet: `data/manifests/source_provenance_priority_packet.csv`
- Manifest present: `true`
- Source rows: 11
- Blocking context-only sources: 4
- Human-review sources: 7
- Cached public snapshots: 3
- Repository input sources: 4
- Provenance gate closure candidates: 0
- Can mark complete from provenance triage: `false`

Required reviewer actions:

- cache or explicitly exclude context-only public sources before final claims
- review cached public snapshots for license, attribution, snapshot, and reproducibility suitability
- confirm project-owned local citations and privacy abstraction for repository inputs
- resolve alternate URL issues before provenance acceptance
- create data/manifests/provenance_acceptance.json only after source-backed review

Provenance blockers:

- formal provenance acceptance record is absent
- context-only public sources still need cached extracts or exclusion decisions
- cached public snapshots still require license, attribution, snapshot, and reproducibility review
- repository inputs still require human scope/privacy/reproducibility review
- URL remediation rows still require reviewer confirmation

## Review Packet Status Snapshots

These manifest summaries help reviewers triage existing packets. They do not accept any gate or choose a final method.

| Packet | Rows | Blocking | Human Review | Gate Candidates | Can Complete | Key Status Counts |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `Source Provenance Priority` | 11 | 4 | 7 | 0 | `false` | blocked_context_only_source_not_cached=4; needs_human_review_cached_snapshot_source=3; needs_human_review_repository_input_source=4 |
| `Source Context Cache Requests` | 4 | 4 | 0 | 0 | `false` | blocked_missing_context_source_cache=4 |
| `Source Context Cache Decisions` | 4 | 4 | 0 | 0 | `false` | blocked_missing_context_source_cache_or_exclusion_decision=4 |
| `Source Provenance Decision` | 7 | 3 | 4 | 0 | `false` | blocked_missing_context_cache_or_exclusion_decisions=1; blocked_missing_provenance_acceptance_record=1; blocked_scaffold_reproducibility_manifest_scope=1; +4 more |
| `Source/License Review` | 11 | 4 | 11 | 0 | `false` | cached_snapshot_pending_review=3; context_only_not_cached=4; repository_input_pending_review=4 |
| `Source URL Review` | 17 | 1 | 17 | 0 | `false` | network_error=1; no_url_detected=4; reachable=12 |
| `Source URL Remediation` | 17 | 0 | 0 | 0 | `false` | alternate_reachable_url_needs_review=1; local_citation_needs_review=4; reachable_needs_license_review=12 |
| `Pilot Region Decision` | 6 | 3 | 3 | 0 | `false` | blocked_missing_graph_scale_acceptance_record=1; blocked_missing_pilot_acceptance_record=1; blocked_missing_provenance_acceptance_record=1; +3 more |
| `Graph-Scale Method Review` | 4 | 0 | 0 | 0 | `false` |  |
| `Full-Graph Runtime Readiness` | 4 | 2 | 2 | 0 | `false` | blocked_missing_downstream_full_graph_regeneration_decision=1; blocked_missing_full_graph_full_profile_outputs=1; needs_human_review_full_graph_runtime_scope_decision=1; +1 more |
| `Graph-Scale Strategy Readiness` | 5 | 3 | 2 | 0 | `false` | blocked_incomplete_multi_corridor_run_profile=1; blocked_missing_full_graph_experiment_outputs=1; blocked_missing_graph_scale_acceptance_record=1; +2 more |
| `Graph-Scale Method Decision` | 7 | 4 | 3 | 0 | `false` | blocked_incomplete_multi_corridor_run_profile=1; blocked_missing_downstream_regeneration_decision=1; blocked_missing_full_graph_full_profile_outputs=1; +4 more |
| `Graph-Scale Manifest Audit` | 13 | 0 | 0 | 0 | `false` | complete_reduced_analysis_graph_recorded=13 |
| `Graph-Scale Result Comparison` | 819 | 0 | 0 | 0 | `false` | candidate_improves=24; candidate_worsens=24; nonfinite_difference=30; +1 more |
| `Road Evidence Priority` | 11 | 5 | 2 | 0 | `false` | blocked_exposed_connector_assumption=1; blocked_exposed_high_priority_road_evidence_gap=4; needs_review_exposed_medium_priority_road_evidence_gap=2; +1 more |
| `Road Source Readiness` | 5 | 2 | 3 | 0 | `false` | blocked_missing_capacity_source=1; blocked_missing_reviewed_road_class_overrides=1; needs_human_review_benchmark_strategy=1; +2 more |
| `Road Source Decisions` | 5 | 2 | 3 | 0 | `false` | blocked_missing_capacity_source=1; blocked_missing_reviewed_road_class_overrides=1; needs_human_review_benchmark_strategy=1; +2 more |
| `Parameter Evidence Priority` | 6 | 1 | 5 | 0 | `false` | blocked_missing_transfer_source=1; needs_human_review_demand_scenario=1; needs_human_review_dispatch_policy=1; +3 more |
| `Parameter Source Readiness` | 6 | 1 | 5 | 0 | `false` | blocked_missing_transfer_source=1; needs_human_review_demand_scenario=1; needs_human_review_dispatch_policy=1; +3 more |
| `Parameter Source Decisions` | 6 | 1 | 5 | 0 | `false` | blocked_missing_transfer_source=1; needs_human_review_demand_scenario=1; needs_human_review_dispatch_policy=1; +3 more |
| `Rail Evidence Priority` | 6 | 3 | 2 | 0 | `false` | blocked_missing_data_go_kr_key=2; blocked_missing_reviewed_gtfs_file=1; needs_human_review_availability_scenario=1; +2 more |
| `Rail Fetch Readiness` | 5 | 3 | 2 | 0 | `false` | blocked_missing_data_go_kr_key=2; blocked_missing_reviewed_gtfs_file=1; needs_human_review_availability_scenario=1; +1 more |
| `Rail Source Decisions` | 5 | 3 | 2 | 0 | `false` | blocked_missing_data_go_kr_key=2; blocked_missing_reviewed_gtfs_file=1; needs_human_review_availability_scenario=1; +1 more |
| `Validation Benchmark Readiness` | 4 | 1 | 3 | 0 | `false` | blocked_missing_validation_acceptance_record=1; needs_human_review_alternative_benchmark_decision=1; needs_human_review_cached_osrm_snapshot=1; +1 more |
| `Validation Benchmark Decision` | 6 | 3 | 3 | 0 | `false` | blocked_missing_validation_acceptance_record=1; blocked_scaffold_validation_scope=1; blocked_weak_route_road_evidence_dependency=1; +3 more |
| `Validation Strategy Readiness` | 7 | 2 | 5 | 0 | `false` | blocked_missing_validation_acceptance_record=1; blocked_weak_route_road_evidence_exposure=1; needs_human_review_accessibility_disconnections=1; +4 more |
| `Sensitivity Method Decision` | 7 | 4 | 3 | 0 | `false` | blocked_missing_morris_vs_sobol_decision=1; blocked_missing_sensitivity_acceptance_record=1; blocked_reduced_graph_scope_dependency=1; +4 more |
| `Sensitivity Strategy Readiness` | 7 | 4 | 3 | 0 | `false` | blocked_missing_morris_vs_sobol_decision=1; blocked_missing_sensitivity_acceptance_record=1; blocked_reduced_graph_scope_for_sensitivity_claims=1; +4 more |
| `Experiment Strategy Readiness` | 9 | 4 | 5 | 0 | `false` | blocked_graph_scale_dependency=1; blocked_input_evidence_dependency=1; blocked_missing_experiment_acceptance_record=1; +5 more |
| `Experiment Design Decision` | 8 | 4 | 4 | 0 | `false` | blocked_graph_scale_dependency=1; blocked_input_evidence_dependency=1; blocked_missing_experiment_acceptance_record=1; +5 more |
| `Figure/Table Review` | 8 | 3 | 5 | 0 | `false` | blocked_missing_manuscript_acceptance_record=1; blocked_reduced_graph_scope_dependency=1; blocked_upstream_evidence_dependency=1; +5 more |
| `Manuscript/Report Decision` | 7 | 4 | 3 | 0 | `false` | blocked_claim_alignment_review_dependency=1; blocked_figure_table_review_dependency=1; blocked_missing_manuscript_acceptance_record=1; +4 more |
| `Reproducibility Review` | 8 | 5 | 0 | 0 | `false` | blocked_dirty_worktree=1; blocked_full_clean_checkout_not_run=1; blocked_no_reproducibility_acceptance_record=1; +5 more |
| `Reproducibility Decision` | 7 | 4 | 3 | 0 | `false` | blocked_artifact_regeneration_not_tested=1; blocked_bounded_or_stale_clean_checkout_evidence=1; blocked_missing_reproducibility_acceptance_record=1; +4 more |
| `Acceptance Decision Templates` | 9 | 0 | 0 | 0 | `false` |  |
| `Formal Acceptance Blocker Queue` | 15 | 15 | 15 | 0 | `false` | blocked=15 |
| `Acceptance Task Assignments` | 15 | 0 | 15 | 0 | `false` | apply_reviewed_input_and_regenerate=1; create_or_supply_formal_evidence=13; replace_weak_or_scaffold_evidence=1 |
| `Formal Evidence Matrix` | 12 | 12 | 12 | 0 | `false` | blocked=12 |
| `Formal Acceptance Pre-Review` | 12 | 12 | 12 | 0 | `false` | blocked_missing_evidence=8; blocked_requires_human_decision=4 |
| `Formal Package Audit` | 12 | 12 | 0 | 0 | `false` |  |
| `Formal Evidence Path Audit` | 11 | 0 | 0 | 0 | `false` |  |
| `Agent Review Path Audit` | 12 | 0 | 0 | 0 | `false` | missing_formal_target=36; present=768 |
| `Tracked Artifact Audit` | 74 | 74 | 0 | 0 | `false` | agent_definition=1; data_or_manifest=39; documentation=18; +4 more |
| `Current Goal Completion Audit` | 15 | 12 | 0 | 0 | `false` | blocked=12; missing_acceptance_artifact=12; ready=3 |
| `Publication Readiness Audit` | 7 | 6 | 0 | 0 | `false` | blocked=6; ready=1 |

Priority blockers by packet:

- `Source Provenance Priority`: formal provenance acceptance record is absent (+4 more)
- `Source Context Cache Requests`: context-only public sources still lack reviewed cached extracts or explicit exclusion decisions (+2 more)
- `Source Context Cache Decisions`: formal provenance acceptance record is absent (+6 more)
- `Source Provenance Decision`: context-only public sources still lack reviewed cached extracts or explicit exclusion decisions (+2 more)
- `Source/License Review`: formal provenance acceptance record is absent (+2 more)
- `Source URL Review`: formal provenance acceptance record is absent (+3 more)
- `Source URL Remediation`: formal provenance acceptance record is absent (+3 more)
- `Pilot Region Decision`: data/manifests/graph_scale_acceptance.json is absent (+2 more)
- `Full-Graph Runtime Readiness`: full-graph full-profile outputs are absent (+2 more)
- `Graph-Scale Strategy Readiness`: graph_scale_acceptance.json is absent (+3 more)
- `Graph-Scale Method Decision`: multi-corridor candidate has only separated/sample-scale output (+3 more)
- `Road Evidence Priority`: reviewed road_class_overrides.csv is still absent (+2 more)
- `Road Source Readiness`: reviewed road_class_overrides.csv is absent unless target_output_present is true (+2 more)
- `Road Source Decisions`: reviewed road_class_overrides.csv is absent (+4 more)
- `Parameter Evidence Priority`: transfer-delay source evidence is absent (+3 more)
- `Parameter Source Readiness`: all rows require human review or external source decisions before final claims (+2 more)
- `Parameter Source Decisions`: formal parameter acceptance table is absent (+3 more)
- `Rail Evidence Priority`: rail timing cache files are absent (+2 more)
- `Rail Fetch Readiness`: rail timing cache files are absent unless source_cache_present is true (+2 more)
- `Rail Source Decisions`: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests (+5 more)
- `Validation Benchmark Readiness`: validation_acceptance_record: data/manifests/validation_acceptance.json is absent
- `Validation Benchmark Decision`: validation summary still declares scaffold or sanity scope (+2 more)
- `Validation Strategy Readiness`: validation_acceptance.json is absent (+1 more)
- `Sensitivity Method Decision`: Morris-vs-Sobol method decision is not recorded in formal acceptance (+3 more)
- `Sensitivity Strategy Readiness`: sensitivity outputs use a reduced analysis graph (+3 more)
- `Experiment Strategy Readiness`: current full-pilot result scope is scaffold or not calibrated (+3 more)
- `Experiment Design Decision`: experiment outputs depend on a graph method that is not accepted (+3 more)
- `Figure/Table Review`: figure/table outputs depend on reduced analysis graph scope (+2 more)
- `Manuscript/Report Decision`: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent (+3 more)
- `Reproducibility Decision`: reproducibility manifest remains scaffold-only (+3 more)
- `Formal Package Audit`: pilot_region_accepted: create an explicit pilot acceptance record after privacy and case-scope review (+27 more)
- `Tracked Artifact Audit`: agents/acceptance_review_agents.json: Commit, stash, or document this change before clean-checkout reproduction. (+50 more)
- `Publication Readiness Audit`: parameter evidence: justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence (+14 more)

## Remaining Blockers

- pilot_region_accepted: Record an explicit pilot acceptance decision with reviewer, scope, privacy review, evidence paths, and not-operational claim boundary.
- pilot_region_accepted: create an explicit pilot acceptance record after privacy and case-scope review
- pilot_region_accepted: resolve pilot-region decision blockers before pilot acceptance
- pilot_region_accepted: pilot-region decision: data/manifests/graph_scale_acceptance.json is absent
- pilot_region_accepted: pilot-region decision: data/manifests/provenance_acceptance.json is absent
- pilot_region_accepted: pilot-region decision: data/manifests/pilot_acceptance.json is absent
- pilot_region_accepted: review pilot-region decision human-decision items before pilot acceptance
- data_provenance: Review source URLs, licenses, attribution, local snapshots, privacy abstraction, and reproducibility scope.
- data_provenance: Create data/manifests/provenance_acceptance.json only after source-backed review.
- data_provenance: create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- data_provenance: replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance
- data_provenance: source provenance priority: formal provenance acceptance record is absent
- data_provenance: source provenance priority: context-only public sources still need cached extracts or exclusion decisions
- data_provenance: source provenance priority: cached public snapshots still require license, attribution, snapshot, and reproducibility review
- data_provenance: source provenance priority: repository inputs still require human scope/privacy/reproducibility review
- data_provenance: source provenance priority: URL remediation rows still require reviewer confirmation
- data_provenance: source context cache request: context-only public sources still lack reviewed cached extracts or explicit exclusion decisions
- data_provenance: source context cache request: license, attribution, snapshot, and reproducibility review are still required for retained public sources
- data_provenance: source context cache request: formal provenance acceptance record is absent
- data_provenance: source context cache decision: formal provenance acceptance record is absent
- data_provenance: source context cache decision: cache/exclusion decisions are pending for context-only public sources
- data_provenance: source context cache decision: retained context sources still require license, attribution, snapshot, and reproducibility review
- data_provenance: source context cache decision: ktdb_public_transport_gtfs_context: no reviewed cache artifact or explicit exclusion decision is present
- data_provenance: source context cache decision: metro9_capacity_context: no reviewed cache artifact or explicit exclusion decision is present
- data_provenance: source context cache decision: seoul_shortest_path_api_context: no reviewed cache artifact or explicit exclusion decision is present
- data_provenance: source context cache decision: seoul_timetable_api_context: no reviewed cache artifact or explicit exclusion decision is present
- data_provenance: resolve source-provenance decision blockers before provenance acceptance
- data_provenance: source provenance decision: context-only public sources still lack reviewed cached extracts or explicit exclusion decisions
- data_provenance: source provenance decision: reproducibility manifest remains scaffold-only
- data_provenance: source provenance decision: data/manifests/provenance_acceptance.json is absent
- data_provenance: review source-provenance decision human-decision items before provenance acceptance
- graph_scale_strategy: Choose and document reduced-corridor, multi-corridor, or full-graph strategy.
- graph_scale_strategy: Create graph_scale_acceptance.json with matching graph counts and evidence paths.
- graph_scale_strategy: create an explicit graph-scale acceptance record after source-vs-analysis graph review
- graph_scale_strategy: resolve graph-scale strategy-readiness blockers before graph-scale acceptance
- graph_scale_strategy: graph-scale strategy readiness: graph_scale_acceptance.json is absent
- graph_scale_strategy: graph-scale strategy readiness: current reduced-corridor output has alternate-route warnings
- graph_scale_strategy: graph-scale strategy readiness: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- graph_scale_strategy: graph-scale strategy readiness: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- graph_scale_strategy: review graph-scale strategy-readiness human-decision items before graph-scale acceptance
- graph_scale_strategy: resolve graph-scale method-decision blockers before graph-scale acceptance
- graph_scale_strategy: graph-scale method decision: multi-corridor candidate has only separated/sample-scale output
- graph_scale_strategy: graph-scale method decision: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- graph_scale_strategy: graph-scale method decision: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- graph_scale_strategy: graph-scale method decision: data/manifests/graph_scale_acceptance.json is absent
- graph_scale_strategy: review graph-scale method-decision human-decision items before graph-scale acceptance
- cached_osm_input: Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- cached_osm_input: Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- cached_osm_input: road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- cached_osm_input: road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- cached_osm_input: road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- cached_osm_input: road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- cached_osm_input: road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- cached_osm_input: road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- cached_osm_input: road override application: reviewed road-class override table is absent
- cached_osm_input: road source readiness: reviewed road_class_overrides.csv is absent unless target_output_present is true
- cached_osm_input: road source readiness: capacity and disruption evidence still require external source or formal assumption decisions
- cached_osm_input: road source readiness: this packet is readiness evidence only and cannot create road-class overrides
- cached_osm_input: road source decision: reviewed road_class_overrides.csv is absent
- cached_osm_input: road source decision: road source decisions are pending for speed, capacity, disruption, benchmark, and override-application requests
- cached_osm_input: road source decision: retained road assumptions require source-backed updates, sensitivity-only limits, benchmark-only limits, or explicit acceptance
- cached_osm_input: road source decision: reviewed_road_class_override_application_request: data/parameters/road_class_overrides.csv is absent
- cached_osm_input: road source decision: road_capacity_lane_count_source_request: cached lane-count evidence has no parseable observed lane rows
- parameter_evidence: Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- parameter_evidence: Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- parameter_evidence: justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- parameter_evidence: replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- parameter_evidence: replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- parameter_evidence: derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- parameter_evidence: strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- parameter_evidence: support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- parameter_evidence: parameter source readiness: all rows require human review or external source decisions before final claims
- parameter_evidence: parameter source readiness: this packet is readiness evidence only and cannot create accepted parameter values
- parameter_evidence: parameter source readiness: parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions
- parameter_evidence: parameter evidence priority: transfer-delay source evidence is absent
- parameter_evidence: parameter evidence priority: high-priority disruption and traffic/BPR rows still require human/source-backed decisions
- parameter_evidence: parameter evidence priority: medium-priority demand, fleet, and dispatch rows remain scenario assumptions
- parameter_evidence: parameter evidence priority: parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions
- parameter_evidence: parameter source decision: formal parameter acceptance table is absent
- parameter_evidence: parameter source decision: parameter source decisions are pending for weak parameter groups
- parameter_evidence: parameter source decision: retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance
- parameter_evidence: parameter source decision: transfer_delay_source_request: no station-layout, observed transfer, or pedestrian-flow source artifact is present
- rail_evidence: Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- rail_evidence: Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- rail_evidence: rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- rail_evidence: rail service evidence: derive headway and travel time from the cached records
- rail_evidence: rail fetch readiness: rail timing cache files are absent unless source_cache_present is true
- rail_evidence: rail fetch readiness: API-key and reviewed-GTFS rows require external reviewer-provided inputs
- rail_evidence: rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- rail_evidence: rail evidence priority: rail timing cache files are absent
- rail_evidence: rail evidence priority: DATA_GO_KR_KEY or reviewed GTFS input is absent
- rail_evidence: rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- rail_evidence: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- rail_evidence: rail source decision: rail timing cache or reviewed GTFS source files are absent for timing requests
- rail_evidence: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or explicit acceptance
- rail_evidence: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- rail_evidence: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file is absent
- rail_evidence: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- validation_package: Review validation thresholds, benchmark scope, snapshot pinning, and failure cases.
- validation_package: Create validation_acceptance.json after benchmark-strategy review.
- validation_package: create an explicit validation acceptance record after benchmark-strategy review
- validation_package: resolve validation strategy-readiness blockers before validation acceptance
- validation_package: validation strategy readiness: validation_acceptance.json is absent
- validation_package: validation strategy readiness: route-level road evidence exposure remains weak until road evidence gates close
- validation_package: review validation strategy-readiness human-decision items before validation acceptance
- validation_package: resolve validation benchmark-decision blockers before validation acceptance
- validation_package: validation benchmark decision: validation summary still declares scaffold or sanity scope
- validation_package: validation benchmark decision: route-level road evidence exposure remains weak until road evidence gates close
- validation_package: validation benchmark decision: data/manifests/validation_acceptance.json is absent
- validation_package: review validation benchmark-decision human-decision items before validation acceptance
- validation_package: revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review
- sensitivity_analysis: Review parameter ranges and decide whether Morris is enough or Sobol is required.
- sensitivity_analysis: Create sensitivity_acceptance.json after final input and graph scope are accepted.
- sensitivity_analysis: create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
- sensitivity_analysis: resolve sensitivity strategy-readiness blockers before sensitivity acceptance
- sensitivity_analysis: sensitivity strategy readiness: sensitivity outputs use a reduced analysis graph
- sensitivity_analysis: sensitivity strategy readiness: current sensitivity result scope is scaffold or not calibrated
- sensitivity_analysis: sensitivity strategy readiness: Morris-vs-Sobol method decision is not recorded in formal acceptance
- sensitivity_analysis: sensitivity strategy readiness: data/manifests/sensitivity_acceptance.json is absent
- sensitivity_analysis: review sensitivity strategy-readiness human-decision items before sensitivity acceptance
- sensitivity_analysis: accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level
- full_experiment_output: Regenerate or accept full outputs after input, graph-scale, and validation gates close.
- full_experiment_output: Create experiment_acceptance.json with matching run profile and row counts.
- full_experiment_output: create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review
- full_experiment_output: resolve experiment strategy-readiness blockers before experiment acceptance
- full_experiment_output: experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- full_experiment_output: experiment strategy readiness: full-pilot outputs depend on a graph method that is not accepted
- full_experiment_output: experiment strategy readiness: upstream input, road override, parameter, validation, or provenance gates are not accepted
- full_experiment_output: experiment strategy readiness: data/manifests/experiment_acceptance.json is absent
- full_experiment_output: review experiment strategy-readiness human-decision items before experiment acceptance
- full_experiment_output: resolve experiment design-decision blockers before experiment acceptance
- full_experiment_output: experiment design decision: experiment outputs depend on a graph method that is not accepted
- full_experiment_output: experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not accepted
- full_experiment_output: experiment design decision: current full-pilot result scope is scaffold or not calibrated
- full_experiment_output: experiment design decision: data/manifests/experiment_acceptance.json is absent
- full_experiment_output: review experiment design-decision human-decision items before experiment acceptance
- full_experiment_output: accept or regenerate full pilot outputs after input validation and graph-scale decision
- full_experiment_output: review experiment-package rows before formal experiment acceptance
- manuscript_report_alignment: Revise or hold claims until all supporting evidence gates are accepted.
- manuscript_report_alignment: Create manuscript_acceptance.json after claim-by-claim review.
- manuscript_report_alignment: close evidence gates before final paper/report claims
- manuscript_report_alignment: create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- manuscript_report_alignment: revise figure/table claim boundary from scaffold to accepted study scope
- manuscript_report_alignment: resolve figure/table review blockers before manuscript acceptance
- manuscript_report_alignment: figure/table review: figure/table outputs depend on reduced analysis graph scope
- manuscript_report_alignment: figure/table review: figure/table source outputs remain scaffold or not calibrated
- manuscript_report_alignment: figure/table review: data/manifests/manuscript_acceptance.json is absent
- manuscript_report_alignment: review figure/table human-review rows before manuscript acceptance
- manuscript_report_alignment: review or revise claim-alignment overclaim candidates before manuscript acceptance
- manuscript_report_alignment: claim alignment: formal manuscript/report acceptance record is absent
- manuscript_report_alignment: claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- manuscript_report_alignment: claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims
- manuscript_report_alignment: resolve manuscript/report decision blockers before manuscript acceptance
- manuscript_report_alignment: manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent
- manuscript_report_alignment: manuscript/report decision: claim-alignment packet has 108 rows requiring revision or acceptance
- manuscript_report_alignment: manuscript/report decision: upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output
- manuscript_report_alignment: manuscript/report decision: data/manifests/manuscript_acceptance.json is absent
- manuscript_report_alignment: review manuscript/report human-decision rows before manuscript acceptance
- reproducibility: Run or document clean-checkout validation with command log and artifact regeneration evidence.
- reproducibility: Create reproducibility_acceptance.json only after accepted reproduction scope is complete.
- reproducibility: create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- reproducibility: replace scaffold-only manifest with clean-checkout final reproduction package
- reproducibility: resolve reproducibility decision blockers before reproducibility acceptance
- reproducibility: reproducibility decision: reproducibility manifest remains scaffold-only
- reproducibility: reproducibility decision: clean-checkout smoke is bounded, stale, or not a full clean-environment reproduction
- reproducibility: reproducibility decision: clean-checkout artifact regeneration protocol has not been tested
- reproducibility: reproducibility decision: data/manifests/reproducibility_acceptance.json is absent
- reproducibility: review reproducibility human-decision rows before reproducibility acceptance
- final_audit: After all pre-final gates are ready, write the independent prompt-to-artifact final audit.
- final_audit: Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
- final_audit: create docs/final_study_audit.md after all other gates close
- final_audit: create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- final_audit: all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- Pilot Region Accepted: create an explicit pilot acceptance record after privacy and case-scope review
- Pilot Region Accepted: resolve pilot-region decision blockers before pilot acceptance
- Pilot Region Accepted: pilot-region decision: data/manifests/graph_scale_acceptance.json is absent
- Pilot Region Accepted: pilot-region decision: data/manifests/provenance_acceptance.json is absent
- Pilot Region Accepted: pilot-region decision: data/manifests/pilot_acceptance.json is absent
- Pilot Region Accepted: review pilot-region decision human-decision items before pilot acceptance
- Cached OSM Input: road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- Cached OSM Input: road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- Cached OSM Input: road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- Cached OSM Input: road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- Cached OSM Input: road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- Cached OSM Input: road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- Cached OSM Input: road override application: reviewed road-class override table is absent
- Cached OSM Input: road source readiness: reviewed road_class_overrides.csv is absent unless target_output_present is true
- Cached OSM Input: road source readiness: capacity and disruption evidence still require external source or formal assumption decisions
- Cached OSM Input: road source readiness: this packet is readiness evidence only and cannot create road-class overrides
- Cached OSM Input: road source decision: reviewed road_class_overrides.csv is absent
- Cached OSM Input: road source decision: road source decisions are pending for speed, capacity, disruption, benchmark, and override-application requests
- Cached OSM Input: road source decision: retained road assumptions require source-backed updates, sensitivity-only limits, benchmark-only limits, or explicit acceptance
- Cached OSM Input: road source decision: reviewed_road_class_override_application_request: data/parameters/road_class_overrides.csv is absent
- Cached OSM Input: road source decision: road_capacity_lane_count_source_request: cached lane-count evidence has no parseable observed lane rows
- Graph-Scale Strategy: create an explicit graph-scale acceptance record after source-vs-analysis graph review
- Graph-Scale Strategy: resolve graph-scale strategy-readiness blockers before graph-scale acceptance
- Graph-Scale Strategy: graph-scale strategy readiness: graph_scale_acceptance.json is absent
- Graph-Scale Strategy: graph-scale strategy readiness: current reduced-corridor output has alternate-route warnings
- Graph-Scale Strategy: graph-scale strategy readiness: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- Graph-Scale Strategy: graph-scale strategy readiness: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- Graph-Scale Strategy: review graph-scale strategy-readiness human-decision items before graph-scale acceptance
- Graph-Scale Strategy: resolve graph-scale method-decision blockers before graph-scale acceptance
- Graph-Scale Strategy: graph-scale method decision: multi-corridor candidate has only separated/sample-scale output
- Graph-Scale Strategy: graph-scale method decision: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- Graph-Scale Strategy: graph-scale method decision: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- Graph-Scale Strategy: graph-scale method decision: data/manifests/graph_scale_acceptance.json is absent
- Graph-Scale Strategy: review graph-scale method-decision human-decision items before graph-scale acceptance
- Data Provenance: create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- Data Provenance: replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance
- Data Provenance: source provenance priority: formal provenance acceptance record is absent
- Data Provenance: source provenance priority: context-only public sources still need cached extracts or exclusion decisions
- Data Provenance: source provenance priority: cached public snapshots still require license, attribution, snapshot, and reproducibility review
- Data Provenance: source provenance priority: repository inputs still require human scope/privacy/reproducibility review
- Data Provenance: source provenance priority: URL remediation rows still require reviewer confirmation
- Data Provenance: source context cache request: context-only public sources still lack reviewed cached extracts or explicit exclusion decisions
- Data Provenance: source context cache request: license, attribution, snapshot, and reproducibility review are still required for retained public sources
- Data Provenance: source context cache request: formal provenance acceptance record is absent
- Data Provenance: source context cache decision: formal provenance acceptance record is absent
- Data Provenance: source context cache decision: cache/exclusion decisions are pending for context-only public sources
- Data Provenance: source context cache decision: retained context sources still require license, attribution, snapshot, and reproducibility review
- Data Provenance: source context cache decision: ktdb_public_transport_gtfs_context: no reviewed cache artifact or explicit exclusion decision is present
- Data Provenance: source context cache decision: metro9_capacity_context: no reviewed cache artifact or explicit exclusion decision is present
- Data Provenance: source context cache decision: seoul_shortest_path_api_context: no reviewed cache artifact or explicit exclusion decision is present
- Data Provenance: source context cache decision: seoul_timetable_api_context: no reviewed cache artifact or explicit exclusion decision is present
- Data Provenance: resolve source-provenance decision blockers before provenance acceptance
- Data Provenance: source provenance decision: context-only public sources still lack reviewed cached extracts or explicit exclusion decisions
- Data Provenance: source provenance decision: reproducibility manifest remains scaffold-only
- Data Provenance: source provenance decision: data/manifests/provenance_acceptance.json is absent
- Data Provenance: review source-provenance decision human-decision items before provenance acceptance
- Parameter Evidence: justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- Parameter Evidence: replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- Parameter Evidence: replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- Parameter Evidence: derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- Parameter Evidence: strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- Parameter Evidence: support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- Parameter Evidence: parameter source readiness: all rows require human review or external source decisions before final claims
- Parameter Evidence: parameter source readiness: this packet is readiness evidence only and cannot create accepted parameter values
- Parameter Evidence: parameter source readiness: parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions
- Parameter Evidence: parameter evidence priority: transfer-delay source evidence is absent
- Parameter Evidence: parameter evidence priority: high-priority disruption and traffic/BPR rows still require human/source-backed decisions
- Parameter Evidence: parameter evidence priority: medium-priority demand, fleet, and dispatch rows remain scenario assumptions
- Parameter Evidence: parameter evidence priority: parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions
- Parameter Evidence: parameter source decision: formal parameter acceptance table is absent
- Parameter Evidence: parameter source decision: parameter source decisions are pending for weak parameter groups
- Parameter Evidence: parameter source decision: retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance
- Parameter Evidence: parameter source decision: transfer_delay_source_request: no station-layout, observed transfer, or pedestrian-flow source artifact is present
- Rail Evidence: rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- Rail Evidence: rail service evidence: derive headway and travel time from the cached records
- Rail Evidence: rail fetch readiness: rail timing cache files are absent unless source_cache_present is true
- Rail Evidence: rail fetch readiness: API-key and reviewed-GTFS rows require external reviewer-provided inputs
- Rail Evidence: rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- Rail Evidence: rail evidence priority: rail timing cache files are absent
- Rail Evidence: rail evidence priority: DATA_GO_KR_KEY or reviewed GTFS input is absent
- Rail Evidence: rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- Rail Evidence: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- Rail Evidence: rail source decision: rail timing cache or reviewed GTFS source files are absent for timing requests
- Rail Evidence: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or explicit acceptance
- Rail Evidence: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Rail Evidence: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file is absent
- Rail Evidence: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Validation Package: create an explicit validation acceptance record after benchmark-strategy review
- Validation Package: resolve validation strategy-readiness blockers before validation acceptance
- Validation Package: validation strategy readiness: validation_acceptance.json is absent
- Validation Package: validation strategy readiness: route-level road evidence exposure remains weak until road evidence gates close
- Validation Package: review validation strategy-readiness human-decision items before validation acceptance
- Validation Package: resolve validation benchmark-decision blockers before validation acceptance
- Validation Package: validation benchmark decision: validation summary still declares scaffold or sanity scope
- Validation Package: validation benchmark decision: route-level road evidence exposure remains weak until road evidence gates close
- Validation Package: validation benchmark decision: data/manifests/validation_acceptance.json is absent
- Validation Package: review validation benchmark-decision human-decision items before validation acceptance
- Validation Package: revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review
- Sensitivity Analysis: create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
- Sensitivity Analysis: resolve sensitivity strategy-readiness blockers before sensitivity acceptance
- Sensitivity Analysis: sensitivity strategy readiness: sensitivity outputs use a reduced analysis graph
- Sensitivity Analysis: sensitivity strategy readiness: current sensitivity result scope is scaffold or not calibrated
- Sensitivity Analysis: sensitivity strategy readiness: Morris-vs-Sobol method decision is not recorded in formal acceptance
- Sensitivity Analysis: sensitivity strategy readiness: data/manifests/sensitivity_acceptance.json is absent
- Sensitivity Analysis: review sensitivity strategy-readiness human-decision items before sensitivity acceptance
- Sensitivity Analysis: accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level
- Full Experiment Output: create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review
- Full Experiment Output: resolve experiment strategy-readiness blockers before experiment acceptance
- Full Experiment Output: experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- Full Experiment Output: experiment strategy readiness: full-pilot outputs depend on a graph method that is not accepted
- Full Experiment Output: experiment strategy readiness: upstream input, road override, parameter, validation, or provenance gates are not accepted
- Full Experiment Output: experiment strategy readiness: data/manifests/experiment_acceptance.json is absent
- Full Experiment Output: review experiment strategy-readiness human-decision items before experiment acceptance
- Full Experiment Output: resolve experiment design-decision blockers before experiment acceptance
- Full Experiment Output: experiment design decision: experiment outputs depend on a graph method that is not accepted
- Full Experiment Output: experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not accepted
- Full Experiment Output: experiment design decision: current full-pilot result scope is scaffold or not calibrated
- Full Experiment Output: experiment design decision: data/manifests/experiment_acceptance.json is absent
- Full Experiment Output: review experiment design-decision human-decision items before experiment acceptance
- Full Experiment Output: accept or regenerate full pilot outputs after input validation and graph-scale decision
- Full Experiment Output: review experiment-package rows before formal experiment acceptance
- Manuscript Report Alignment: close evidence gates before final paper/report claims
- Manuscript Report Alignment: create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- Manuscript Report Alignment: revise figure/table claim boundary from scaffold to accepted study scope
- Manuscript Report Alignment: resolve figure/table review blockers before manuscript acceptance
- Manuscript Report Alignment: figure/table review: figure/table outputs depend on reduced analysis graph scope
- Manuscript Report Alignment: figure/table review: figure/table source outputs remain scaffold or not calibrated
- Manuscript Report Alignment: figure/table review: data/manifests/manuscript_acceptance.json is absent
- Manuscript Report Alignment: review figure/table human-review rows before manuscript acceptance
- Manuscript Report Alignment: review or revise claim-alignment overclaim candidates before manuscript acceptance
- Manuscript Report Alignment: claim alignment: formal manuscript/report acceptance record is absent
- Manuscript Report Alignment: claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- Manuscript Report Alignment: claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims
- Manuscript Report Alignment: resolve manuscript/report decision blockers before manuscript acceptance
- Manuscript Report Alignment: manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent
- Manuscript Report Alignment: manuscript/report decision: claim-alignment packet has 108 rows requiring revision or acceptance
- Manuscript Report Alignment: manuscript/report decision: upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output
- Manuscript Report Alignment: manuscript/report decision: data/manifests/manuscript_acceptance.json is absent
- Manuscript Report Alignment: review manuscript/report human-decision rows before manuscript acceptance
- Reproducibility: create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- Reproducibility: replace scaffold-only manifest with clean-checkout final reproduction package
- Reproducibility: resolve reproducibility decision blockers before reproducibility acceptance
- Reproducibility: reproducibility decision: reproducibility manifest remains scaffold-only
- Reproducibility: reproducibility decision: clean-checkout smoke is bounded, stale, or not a full clean-environment reproduction
- Reproducibility: reproducibility decision: clean-checkout artifact regeneration protocol has not been tested
- Reproducibility: reproducibility decision: data/manifests/reproducibility_acceptance.json is absent
- Reproducibility: review reproducibility human-decision rows before reproducibility acceptance
- Final Audit: create docs/final_study_audit.md after all other gates close
- Final Audit: create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- Final Audit: all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
