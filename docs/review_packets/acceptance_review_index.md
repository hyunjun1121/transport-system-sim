# Acceptance Review Index

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Final-study ready: `false`
- Record count: 12
- Can-mark-complete records: 0

| Gate | Agent | Status | Can Mark Complete | Required Action Count |
| --- | --- | --- | --- | --- |
| `pilot_region_accepted` | Pilot Region & Privacy Review Agent | `needs_human_review` | `false` | 7 |
| `data_provenance` | OSM / Source / License / Provenance Review Agent | `blocked` | `false` | 23 |
| `graph_scale_strategy` | Graph Scale Method Review Agent | `needs_human_review` | `false` | 15 |
| `cached_osm_input` | Road / Rail / Parameter Evidence Agent | `blocked` | `false` | 18 |
| `parameter_evidence` | Road / Rail / Parameter Evidence Agent | `blocked` | `false` | 19 |
| `rail_evidence` | Road / Rail / Parameter Evidence Agent | `blocked` | `false` | 37 |
| `validation_package` | Benchmark Strategy Review Agent | `needs_human_review` | `false` | 13 |
| `sensitivity_analysis` | Sensitivity Analysis Review Agent | `blocked` | `false` | 10 |
| `full_experiment_output` | Full Experiment Package Agent | `blocked` | `false` | 17 |
| `manuscript_report_alignment` | Paper / Report Claim Alignment Agent | `blocked` | `false` | 20 |
| `reproducibility` | Clean-Checkout Reproducibility Agent | `blocked` | `false` | 8 |
| `final_audit` | Independent Audit Review Agent | `blocked` | `false` | 11 |

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

- Review-only source note: provide reviewed target payloads, retain context-source rows as sensitivity/context-only evidence, or explicitly exclude them before final claims
- Review-only source note: review cached public snapshots for license, attribution, snapshot, and reproducibility suitability
- Review-only source note: confirm project-owned local citations and privacy abstraction for repository inputs
- Review-only source note: resolve alternate URL issues before provenance acceptance
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
| `Source Provenance Decision` | 7 | 3 | 4 | 0 | `false` | blocked_missing_context_cache_retention_or_exclusion_decisions=1; blocked_missing_provenance_acceptance_record=1; blocked_scaffold_reproducibility_manifest_scope=1; +4 more |
| `Source/License Review` | 11 | 2 | 11 | 0 | `false` | cached_snapshot_pending_review=5; context_only_not_cached=2; repository_input_pending_review=4 |
| `Source URL Review` | 17 | 1 | 17 | 0 | `false` | network_error=1; no_url_detected=4; reachable=12 |
| `Source URL Remediation` | 17 | 0 | 0 | 0 | `false` | alternate_reachable_url_needs_review=1; local_citation_needs_review=4; reachable_needs_license_review=12 |
| `Pilot Region Decision` | 6 | 3 | 3 | 0 | `false` | blocked_missing_graph_scale_acceptance_record=1; blocked_missing_pilot_acceptance_record=1; blocked_missing_provenance_acceptance_record=1; +3 more |
| `Graph-Scale Method Review` | 4 | 0 | 0 | 0 | `false` |  |
| `Full-Graph Runtime Review` | 4 | 2 | 2 | 0 | `false` | blocked_missing_downstream_full_graph_regeneration_decision=1; blocked_missing_full_graph_full_profile_outputs=1; needs_human_review_full_graph_runtime_scope_decision=1; +1 more |
| `Graph-Scale Strategy Review` | 5 | 2 | 3 | 0 | `false` | blocked_missing_full_graph_experiment_outputs=1; blocked_missing_graph_scale_acceptance_record=1; needs_human_review_multi_corridor_result_deltas=1; +2 more |
| `Graph-Scale Method Decision` | 7 | 3 | 4 | 0 | `false` | blocked_missing_downstream_regeneration_decision=1; blocked_missing_full_graph_full_profile_outputs=1; blocked_missing_graph_scale_acceptance_record=1; +4 more |
| `Graph-Scale Manifest Audit` | 13 | 0 | 0 | 0 | `false` | complete_reduced_analysis_graph_recorded=13 |
| `Graph-Scale Result Comparison` | 819 | 0 | 0 | 0 | `false` | candidate_improves=24; candidate_worsens=24; nonfinite_difference=30; +1 more |
| `Road Evidence Priority` | 11 | 5 | 2 | 0 | `false` | blocked_exposed_connector_assumption=1; blocked_exposed_high_priority_road_evidence_gap=4; needs_review_exposed_medium_priority_road_evidence_gap=2; +1 more |
| `OSM Graph Snapshot Review` | 6 | 5 | 1 | 0 | `false` | blocked_graph_scale_acceptance_missing=1; blocked_osm_snapshot_claim_boundary=1; blocked_osm_source_provenance_pending=1; +3 more |
| `Road Source Review` | 5 | 2 | 3 | 0 | `false` | blocked_missing_capacity_source=1; blocked_missing_reviewed_road_class_overrides=1; needs_human_review_benchmark_strategy=1; +2 more |
| `Road Source Decisions` | 5 | 2 | 3 | 0 | `false` | blocked_missing_road_source_decision=2; needs_human_review_road_source_decision=3 |
| `Parameter Evidence Priority` | 7 | 0 | 7 | 0 | `false` | needs_human_review_demand_scenario=1; needs_human_review_dispatch_policy=1; needs_human_review_disruption_parameter_scenario=1; +4 more |
| `Parameter Source Review` | 7 | 0 | 7 | 0 | `false` | needs_human_review_demand_scenario=1; needs_human_review_dispatch_policy=1; needs_human_review_disruption_parameter_scenario=1; +4 more |
| `Parameter Source Decisions` | 7 | 0 | 7 | 0 | `false` | needs_human_review_parameter_source_decision=7 |
| `Transfer Evidence Review` | 5 | 1 | 4 | 0 | `false` | documented_parameter_proxy=1; missing_station_layout_or_observed_transfer_source=1; public_station_context_present=2; +1 more |
| `Rail Evidence Priority` | 7 | 3 | 2 | 0 | `false` | blocked_missing_data_go_kr_key=2; blocked_missing_reviewed_gtfs_file=1; needs_human_review_availability_scenario=1; +3 more |
| `Rail Fetch Review` | 6 | 3 | 2 | 0 | `false` | blocked_missing_data_go_kr_key=2; blocked_missing_reviewed_gtfs_file=1; needs_human_review_availability_scenario=1; +2 more |
| `Rail Source Decisions` | 6 | 3 | 3 | 0 | `false` | blocked_missing_rail_source_decision=3; needs_human_review_rail_source_decision=2; needs_human_review_ready_rail_source_decision=1 |
| `Benchmark Evidence Review` | 4 | 1 | 3 | 0 | `false` | blocked_missing_validation_acceptance_record=1; needs_human_review_alternative_benchmark_decision=1; needs_human_review_fallback_warn_rows=1; +1 more |
| `Benchmark Evidence Decision` | 6 | 3 | 3 | 0 | `false` | blocked_missing_validation_acceptance_record=1; blocked_scaffold_validation_scope=1; blocked_weak_route_road_evidence_dependency=1; +3 more |
| `Benchmark Strategy Review` | 7 | 3 | 4 | 0 | `false` | blocked_fallback_benchmark_failures=1; blocked_missing_validation_acceptance_record=1; blocked_weak_route_road_evidence_exposure=1; +4 more |
| `Sensitivity Method Decision` | 7 | 4 | 3 | 0 | `false` | blocked_missing_morris_vs_sobol_decision=1; blocked_missing_sensitivity_acceptance_record=1; blocked_reduced_graph_scope_dependency=1; +4 more |
| `Sensitivity Index Review` | 7 | 0 | 7 | 0 | `false` | needs_human_review_unavailable_indices=2; needs_human_review_zero_mu_star_rows=5 |
| `Sensitivity Strategy Review` | 7 | 4 | 3 | 0 | `false` | blocked_missing_morris_vs_sobol_decision=1; blocked_missing_sensitivity_acceptance_record=1; blocked_reduced_graph_scope_for_sensitivity_claims=1; +4 more |
| `Experiment Strategy Review` | 9 | 4 | 5 | 0 | `false` | blocked_graph_scale_dependency=1; blocked_input_evidence_dependency=1; blocked_missing_experiment_acceptance_record=1; +5 more |
| `Experiment Design Decision` | 8 | 4 | 4 | 0 | `false` | blocked_graph_scale_dependency=1; blocked_input_evidence_dependency=1; blocked_missing_experiment_acceptance_record=1; +5 more |
| `Integrated E2/E3/E5 Evidence Review` | 5 | 5 | 14 | 0 | `false` | blocked_experiment_design_dependencies=1; blocked_integrated_claim_boundary=1; blocked_rail_source_decisions_pending=1; +2 more |
| `Figure/Table Review` | 8 | 3 | 5 | 0 | `false` | blocked_missing_manuscript_acceptance_record=1; blocked_reduced_graph_scope_dependency=1; blocked_upstream_evidence_dependency=1; +5 more |
| `Manuscript/Report Decision` | 7 | 4 | 3 | 0 | `false` | blocked_claim_alignment_review_dependency=1; blocked_figure_table_review_dependency=1; blocked_missing_manuscript_acceptance_record=1; +4 more |
| `Reproducibility Review` | 8 | 5 | 0 | 0 | `false` | blocked_dirty_worktree=1; blocked_full_clean_checkout_not_run=1; blocked_no_reproducibility_acceptance_record=1; +5 more |
| `Reproducibility Decision` | 7 | 2 | 5 | 0 | `false` | blocked_missing_reproducibility_acceptance_record=1; blocked_scaffold_reproducibility_manifest_scope=1; needs_human_review_artifact_regeneration=1; +4 more |
| `Independent Audit Decision` | 7 | 4 | 3 | 0 | `false` | blocked_missing_final_audit_acceptance_record=1; blocked_missing_final_study_audit_document=1; blocked_missing_formal_acceptance_artifacts=1; +4 more |
| `Review Decision Templates` | 9 | 0 | 0 | 0 | `false` |  |
| `Formal Acceptance Blocker Queue` | 15 | 15 | 15 | 0 | `false` | blocked=15 |
| `Review Task Assignments` | 15 | 0 | 15 | 0 | `false` | apply_reviewed_input_and_regenerate=1; create_or_supply_formal_evidence=13; replace_weak_or_scaffold_evidence=1 |
| `Formal Evidence Matrix` | 12 | 12 | 12 | 0 | `false` | blocked=12 |
| `Formal Pre-Review` | 12 | 12 | 12 | 0 | `false` | blocked_missing_evidence=8; blocked_requires_human_decision=4 |
| `Formal Package Audit` | 12 | 12 | 0 | 0 | `false` |  |
| `Formal Evidence Path Audit` | 11 | 0 | 0 | 0 | `false` |  |
| `Agent Review Path Audit` | 12 | 0 | 0 | 0 | `false` | missing_formal_target=36; present=817 |
| `Tracked Artifact Audit` | 334 | 334 | 0 | 0 | `false` | agent_definition=1; data_or_manifest=130; documentation=74; +7 more |
| `Current Goal Completion Audit` | 15 | 12 | 0 | 0 | `false` | blocked=12; missing_acceptance_artifact=12; ready=3 |
| `Publication Blocker Audit` | 10 | 9 | 0 | 0 | `false` | blocked=9; ready=1 |

Priority blockers by packet:

- `Source Provenance Priority`: Blocked non-approval source note: formal provenance acceptance record is absent (+4 more)
- `Source Context Cache Requests`: Blocked non-approval source note: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions (+2 more)
- `Source Context Cache Decisions`: Blocked non-approval source note: formal provenance acceptance record is absent (+5 more)
- `Source Provenance Decision`: Blocked non-approval source note: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions (+2 more)
- `Source/License Review`: Blocked non-approval source note: formal provenance acceptance record is absent (+2 more)
- `Source URL Review`: Blocked non-approval source note: formal provenance acceptance record is absent (+3 more)
- `Source URL Remediation`: Blocked non-approval source note: formal provenance acceptance record is absent (+3 more)
- `Pilot Region Decision`: Blocked non-approval source note: data/manifests/graph_scale_acceptance.json is absent (+2 more)
- `Full-Graph Runtime Review`: Blocked non-approval source note: full-graph full-profile outputs are absent (+2 more)
- `Graph-Scale Strategy Review`: Blocked non-approval source note: full bus-practical graph has smoke evidence only (+4 more)
- `Graph-Scale Method Decision`: Blocked non-approval source note: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output (+2 more)
- `Road Evidence Priority`: Blocked non-approval source note: reviewed road_class_overrides.csv is still absent (+2 more)
- `OSM Graph Snapshot Review`: Blocked non-approval source note: OSM source snapshot remains pending review or provenance acceptance is absent (+4 more)
- `Road Source Review`: Blocked non-approval source note: cached lane-count evidence has no parseable observed lane rows (+3 more)
- `Road Source Decisions`: Blocked non-approval source note: reviewed road_class_overrides.csv is absent (+4 more)
- `Parameter Evidence Priority`: Blocked non-approval source note: transfer-delay evidence still requires human review and source-backed or accepted-assumption treatment (+4 more)
- `Parameter Source Review`: Blocked non-approval source note: all rows require human review or external source decisions before final claims (+2 more)
- `Parameter Source Decisions`: Blocked non-approval source note: formal parameter acceptance table is absent (+2 more)
- `Transfer Evidence Review`: Blocked non-approval source note: station-layout, observed transfer, or pedestrian-flow source artifact is still absent (+2 more)
- `Rail Evidence Priority`: Blocked non-approval source note: source-backed rail timing evidence remains incomplete until API/GTFS/travel-time source paths are reviewed and retained (+2 more)
- `Rail Fetch Review`: Blocked non-approval source note: source-backed rail timing evidence remains incomplete until every required timing source is reviewed and retained (+5 more)
- `Rail Source Decisions`: Blocked non-approval source note: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests (+6 more)
- `Benchmark Evidence Review`: Blocked non-approval source note: validation_acceptance_record: data/manifests/validation_acceptance.json is absent
- `Benchmark Evidence Decision`: Blocked non-approval source note: validation summary still declares scaffold or sanity scope (+2 more)
- `Benchmark Strategy Review`: Blocked non-approval source note: validation_acceptance.json is absent (+1 more)
- `Sensitivity Method Decision`: Blocked non-approval source note: Morris-vs-Sobol method decision is not recorded in formal acceptance (+3 more)
- `Sensitivity Index Review`: Blocked non-approval source note: metric-level index handling still requires human review (+1 more)
- `Sensitivity Strategy Review`: Blocked non-approval source note: sensitivity outputs use a reduced analysis graph (+3 more)
- `Experiment Strategy Review`: Blocked non-approval source note: current full-pilot result scope is scaffold or not calibrated (+3 more)
- `Experiment Design Decision`: Blocked non-approval source note: experiment outputs depend on a graph method that is not accepted (+3 more)
- `Integrated E2/E3/E5 Evidence Review`: Blocked non-approval source note: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests (+4 more)
- `Figure/Table Review`: Blocked non-approval source note: figure/table outputs depend on reduced analysis graph scope (+2 more)
- `Manuscript/Report Decision`: Blocked non-approval source note: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent (+3 more)
- `Reproducibility Decision`: Blocked non-approval source note: reproducibility manifest remains scaffold-only (+1 more)
- `Independent Audit Decision`: Blocked non-approval source note: pre-final gates remain blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility (+3 more)
- `Formal Package Audit`: Blocked non-approval source note: pilot_region_accepted: create an explicit pilot acceptance record after privacy and case-scope review (+27 more)
- `Tracked Artifact Audit`: Blocked non-approval source note: README.md: Commit, stash, or document this change before clean-checkout reproduction. (+50 more)
- `Publication Blocker Audit`: Blocked non-approval source note: parameter evidence: justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence (+40 more)

## Remaining Blockers

- Blocked non-approval action: pilot_region_accepted: Record an explicit pilot acceptance decision with reviewer, scope, privacy review, evidence paths, and not-operational claim boundary.
- Blocked non-approval action: pilot_region_accepted: create an explicit pilot acceptance record after privacy and case-scope review
- Blocked non-approval action: pilot_region_accepted: resolve pilot-region decision blockers before pilot acceptance
- Blocked non-approval action: pilot_region_accepted: pilot-region decision: data/manifests/graph_scale_acceptance.json is absent
- Blocked non-approval action: pilot_region_accepted: pilot-region decision: data/manifests/provenance_acceptance.json is absent
- Blocked non-approval action: pilot_region_accepted: pilot-region decision: data/manifests/pilot_acceptance.json is absent
- Blocked non-approval action: pilot_region_accepted: review pilot-region decision human-decision items before pilot acceptance
- Blocked non-approval action: data_provenance: Review source URLs, licenses, attribution, local snapshots, privacy abstraction, and reproducibility scope.
- Blocked non-approval action: data_provenance: Create data/manifests/provenance_acceptance.json only after source-backed review.
- Blocked non-approval action: data_provenance: create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- Blocked non-approval action: data_provenance: replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance
- Blocked non-approval action: data_provenance: source provenance priority: formal provenance acceptance record is absent
- Blocked non-approval action: data_provenance: source provenance priority: context-source target artifacts still need reviewed payloads, sensitivity/context-only retention decisions, or exclusion decisions
- Blocked non-approval action: data_provenance: source provenance priority: cached public snapshots still require license, attribution, snapshot, and reproducibility review
- Blocked non-approval action: data_provenance: source provenance priority: repository inputs still require human scope/privacy/reproducibility review
- Blocked non-approval action: data_provenance: source provenance priority: URL remediation rows still require reviewer confirmation
- Blocked non-approval action: data_provenance: source context cache request: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- Blocked non-approval action: data_provenance: source context cache request: license, attribution, snapshot, and reproducibility review are still required for retained public sources
- Blocked non-approval action: data_provenance: source context cache request: formal provenance acceptance record is absent
- Blocked non-approval action: data_provenance: source context cache decision: formal provenance acceptance record is absent
- Blocked non-approval action: data_provenance: source context cache decision: target cache/retention/exclusion decisions are pending for context-source rows
- Blocked non-approval action: data_provenance: source context cache decision: retained context sources still require license, attribution, snapshot, and reproducibility review
- Blocked non-approval action: data_provenance: source context cache decision: ktdb_public_transport_gtfs_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- Blocked non-approval action: data_provenance: source context cache decision: seoul_shortest_path_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- Blocked non-approval action: data_provenance: source context cache decision: seoul_timetable_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- Blocked non-approval action: data_provenance: resolve source-provenance decision blockers before provenance acceptance
- Blocked non-approval action: data_provenance: source provenance decision: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- Blocked non-approval action: data_provenance: source provenance decision: reproducibility manifest remains scaffold-only
- Blocked non-approval action: data_provenance: source provenance decision: data/manifests/provenance_acceptance.json is absent
- Blocked non-approval action: data_provenance: review source-provenance decision human-decision items before provenance acceptance
- Blocked non-approval action: graph_scale_strategy: Choose and document reduced-corridor, multi-corridor, or full-graph strategy.
- Blocked non-approval action: graph_scale_strategy: Create graph_scale_acceptance.json with matching graph counts and evidence paths.
- Blocked non-approval action: graph_scale_strategy: create an explicit graph-scale acceptance record after source-vs-analysis graph review
- Blocked non-approval action: graph_scale_strategy: resolve graph-scale strategy-readiness blockers before graph-scale acceptance
- Blocked non-approval action: graph_scale_strategy: graph-scale strategy readiness: full bus-practical graph has smoke evidence only
- Blocked non-approval action: graph_scale_strategy: graph-scale strategy readiness: data/manifests/graph_scale_acceptance.json is absent
- Blocked non-approval action: graph_scale_strategy: graph-scale strategy readiness: current reduced-corridor output has alternate-route warnings
- Blocked non-approval action: graph_scale_strategy: graph-scale strategy readiness: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- Blocked non-approval action: graph_scale_strategy: graph-scale strategy readiness: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- Blocked non-approval action: graph_scale_strategy: review graph-scale strategy-readiness human-decision items before graph-scale acceptance
- Blocked non-approval action: graph_scale_strategy: resolve graph-scale method-decision blockers before graph-scale acceptance
- Blocked non-approval action: graph_scale_strategy: graph-scale method decision: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- Blocked non-approval action: graph_scale_strategy: graph-scale method decision: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- Blocked non-approval action: graph_scale_strategy: graph-scale method decision: data/manifests/graph_scale_acceptance.json is absent
- Blocked non-approval action: graph_scale_strategy: review graph-scale method-decision human-decision items before graph-scale acceptance
- Blocked non-approval action: cached_osm_input: Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Blocked non-approval action: cached_osm_input: Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- Blocked non-approval action: cached_osm_input: road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- Blocked non-approval action: cached_osm_input: road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- Blocked non-approval action: cached_osm_input: road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- Blocked non-approval action: cached_osm_input: road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- Blocked non-approval action: cached_osm_input: road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- Blocked non-approval action: cached_osm_input: road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- Blocked non-approval action: cached_osm_input: road override application: reviewed road-class override table is absent
- Blocked non-approval action: cached_osm_input: road source readiness: cached lane-count evidence has no parseable observed lane rows
- Blocked non-approval action: cached_osm_input: road source readiness: data/parameters/road_class_overrides.csv is absent
- Blocked non-approval action: cached_osm_input: road source readiness: capacity and disruption evidence still require external source or formal assumption decisions
- Blocked non-approval action: cached_osm_input: road source readiness: this packet is readiness evidence only and cannot create road-class overrides
- Blocked non-approval action: cached_osm_input: road source decision: reviewed road_class_overrides.csv is absent
- Blocked non-approval action: cached_osm_input: road source decision: road source decisions are pending for speed, capacity, disruption, benchmark, and override-application requests
- Blocked non-approval action: cached_osm_input: road source decision: retained road assumptions require source-backed updates, sensitivity-only limits, benchmark-only limits, or explicit acceptance
- Blocked non-approval action: cached_osm_input: road source decision: reviewed_road_class_override_application_request: data/parameters/road_class_overrides.csv is absent
- Blocked non-approval action: cached_osm_input: road source decision: road_capacity_lane_count_source_request: cached lane-count evidence has no parseable observed lane rows
- Blocked non-approval action: parameter_evidence: Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Blocked non-approval action: parameter_evidence: Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- Blocked non-approval action: parameter_evidence: justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- Blocked non-approval action: parameter_evidence: replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- Blocked non-approval action: parameter_evidence: replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- Blocked non-approval action: parameter_evidence: derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- Blocked non-approval action: parameter_evidence: strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- Blocked non-approval action: parameter_evidence: support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- Blocked non-approval action: parameter_evidence: parameter source readiness: all rows require human review or external source decisions before final claims
- Blocked non-approval action: parameter_evidence: parameter source readiness: this packet is readiness evidence only and cannot create accepted parameter values
- Blocked non-approval action: parameter_evidence: parameter source readiness: parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions
- Blocked non-approval action: parameter_evidence: parameter evidence priority: transfer-delay evidence still requires human review and source-backed or accepted-assumption treatment
- Blocked non-approval action: parameter_evidence: parameter evidence priority: rail timing/source-decision evidence is incomplete
- Blocked non-approval action: parameter_evidence: parameter evidence priority: high-priority disruption and traffic/BPR rows still require human/source-backed decisions
- Blocked non-approval action: parameter_evidence: parameter evidence priority: medium-priority demand, fleet, dispatch, and transfer rows remain scenario assumptions
- Blocked non-approval action: parameter_evidence: parameter evidence priority: parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions
- Blocked non-approval action: parameter_evidence: parameter source decision: formal parameter acceptance table is absent
- Blocked non-approval action: parameter_evidence: parameter source decision: parameter source decisions are pending for weak parameter groups
- Blocked non-approval action: parameter_evidence: parameter source decision: retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance
- Blocked non-approval action: rail_evidence: Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Blocked non-approval action: rail_evidence: Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- Blocked non-approval action: rail_evidence: rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- Blocked non-approval action: rail_evidence: rail service evidence: derive headway and travel time from the cached records
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
- Blocked non-approval action: rail_evidence: rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates
- Blocked non-approval action: rail_evidence: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval action: rail_evidence: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- Blocked non-approval action: rail_evidence: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval action: rail_evidence: record reviewed rail source decisions for every row with zero blocking and human-review rows
- Blocked non-approval action: rail_evidence: non-formal rail source-decision action ledger cannot close rail evidence gate
- Blocked non-approval action: rail_evidence: rail source-decision action ledger is not formal acceptance evidence
- Blocked non-approval action: rail_evidence: rail transit stress profile cannot support rail evidence gate
- Blocked non-approval action: rail_evidence: rail transit stress profile is not publication-ready evidence
- Blocked non-approval action: rail_evidence: rail transit stress profile cannot mark complete
- Blocked non-approval action: rail_evidence: rail transit stress profile: rail transit stress profiles are scenario/sensitivity review support only
- Blocked non-approval action: rail_evidence: rail transit stress profile: capacity and availability profiles require reviewer decisions before final claims
- Blocked non-approval action: rail_evidence: rail transit stress profile: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- Blocked non-approval action: rail_evidence: rail transit stress profile: rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- Blocked non-approval action: rail_evidence: rail transit stress profile: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- Blocked non-approval action: rail_evidence: rail transit stress profile: rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates
- Blocked non-approval action: rail_evidence: rail transit stress profile: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval action: rail_evidence: rail transit stress profile: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- Blocked non-approval action: rail_evidence: rail transit stress profile: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval action: rail_evidence: 4 rail bounded-treatment warnings remain
- Blocked non-approval action: rail_evidence: 2 rail bounded-treatment source decisions remain pending
- Blocked non-approval action: validation_package: Review validation thresholds, benchmark scope, snapshot pinning, and failure cases.
- Blocked non-approval action: validation_package: Create validation_acceptance.json after benchmark-strategy review.
- Blocked non-approval action: validation_package: create an explicit validation acceptance record after benchmark-strategy review
- Blocked non-approval action: validation_package: resolve validation strategy-readiness blockers before validation acceptance
- Blocked non-approval action: validation_package: validation strategy readiness: validation_acceptance.json is absent
- Blocked non-approval action: validation_package: validation strategy readiness: route-level road evidence exposure remains weak until road evidence gates close
- Blocked non-approval action: validation_package: review validation strategy-readiness human-decision items before validation acceptance
- Blocked non-approval action: validation_package: resolve validation benchmark-decision blockers before validation acceptance
- Blocked non-approval action: validation_package: validation benchmark decision: validation summary still declares scaffold or sanity scope
- Blocked non-approval action: validation_package: validation benchmark decision: route-level road evidence exposure remains weak until road evidence gates close
- Blocked non-approval action: validation_package: validation benchmark decision: data/manifests/validation_acceptance.json is absent
- Blocked non-approval action: validation_package: review validation benchmark-decision human-decision items before validation acceptance
- Blocked non-approval action: validation_package: revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review
- Blocked non-approval action: sensitivity_analysis: Review parameter ranges and decide whether Morris is enough or Sobol is required.
- Blocked non-approval action: sensitivity_analysis: Create sensitivity_acceptance.json after final input and graph scope are accepted.
- Blocked non-approval action: sensitivity_analysis: create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
- Blocked non-approval action: sensitivity_analysis: resolve sensitivity strategy-readiness blockers before sensitivity acceptance
- Blocked non-approval action: sensitivity_analysis: sensitivity strategy readiness: sensitivity outputs use a reduced analysis graph
- Blocked non-approval action: sensitivity_analysis: sensitivity strategy readiness: current sensitivity result scope is scaffold or not calibrated
- Blocked non-approval action: sensitivity_analysis: sensitivity strategy readiness: Morris-vs-Sobol method decision is not recorded in formal acceptance
- Blocked non-approval action: sensitivity_analysis: sensitivity strategy readiness: data/manifests/sensitivity_acceptance.json is absent
- Blocked non-approval action: sensitivity_analysis: review sensitivity strategy-readiness human-decision items before sensitivity acceptance
- Blocked non-approval action: sensitivity_analysis: accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level
- Blocked non-approval action: full_experiment_output: Regenerate or accept full outputs after input, graph-scale, and validation gates close.
- Blocked non-approval action: full_experiment_output: Create experiment_acceptance.json with matching run profile and row counts.
- Blocked non-approval action: full_experiment_output: create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review
- Blocked non-approval action: full_experiment_output: resolve experiment strategy-readiness blockers before experiment acceptance
- Blocked non-approval action: full_experiment_output: experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- Blocked non-approval action: full_experiment_output: experiment strategy readiness: full-pilot outputs depend on a graph method that is not accepted
- Blocked non-approval action: full_experiment_output: experiment strategy readiness: upstream input, road override, parameter, validation, or provenance gates are not accepted
- Blocked non-approval action: full_experiment_output: experiment strategy readiness: data/manifests/experiment_acceptance.json is absent
- Blocked non-approval action: full_experiment_output: review experiment strategy-readiness human-decision items before experiment acceptance
- Blocked non-approval action: full_experiment_output: resolve experiment design-decision blockers before experiment acceptance
- Blocked non-approval action: full_experiment_output: experiment design decision: experiment outputs depend on a graph method that is not accepted
- Blocked non-approval action: full_experiment_output: experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not accepted
- Blocked non-approval action: full_experiment_output: experiment design decision: current full-pilot result scope is scaffold or not calibrated
- Blocked non-approval action: full_experiment_output: experiment design decision: data/manifests/experiment_acceptance.json is absent
- Blocked non-approval action: full_experiment_output: review experiment design-decision human-decision items before experiment acceptance
- Blocked non-approval action: full_experiment_output: accept or regenerate full pilot outputs after input validation and graph-scale decision
- Blocked non-approval action: full_experiment_output: review experiment-package rows before formal experiment acceptance
- Blocked non-approval action: manuscript_report_alignment: Revise or hold claims until all supporting evidence gates are accepted.
- Blocked non-approval action: manuscript_report_alignment: Create manuscript_acceptance.json after claim-by-claim review.
- Blocked non-approval action: manuscript_report_alignment: close evidence gates before final paper/report claims
- Blocked non-approval action: manuscript_report_alignment: create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- Blocked non-approval action: manuscript_report_alignment: revise figure/table claim boundary from scaffold to accepted study scope
- Blocked non-approval action: manuscript_report_alignment: resolve figure/table review blockers before manuscript acceptance
- Blocked non-approval action: manuscript_report_alignment: figure/table review: figure/table outputs depend on reduced analysis graph scope
- Blocked non-approval action: manuscript_report_alignment: figure/table review: figure/table source outputs remain scaffold or not calibrated
- Blocked non-approval action: manuscript_report_alignment: figure/table review: data/manifests/manuscript_acceptance.json is absent
- Blocked non-approval action: manuscript_report_alignment: review figure/table human-review rows before manuscript acceptance
- Blocked non-approval action: manuscript_report_alignment: review or revise claim-alignment overclaim candidates before manuscript acceptance
- Blocked non-approval action: manuscript_report_alignment: claim alignment: formal manuscript/report review record is absent
- Blocked non-approval action: manuscript_report_alignment: claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- Blocked non-approval action: manuscript_report_alignment: claim alignment: evidence gates remain blocked, so result claims cannot be treated as target-study claims
- Blocked non-approval action: manuscript_report_alignment: resolve manuscript/report decision blockers before manuscript acceptance
- Blocked non-approval action: manuscript_report_alignment: manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent
- Blocked non-approval action: manuscript_report_alignment: manuscript/report decision: claim-alignment packet has 42 rows requiring revision or acceptance
- Blocked non-approval action: manuscript_report_alignment: manuscript/report decision: upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output
- Blocked non-approval action: manuscript_report_alignment: manuscript/report decision: data/manifests/manuscript_acceptance.json is absent
- Blocked non-approval action: manuscript_report_alignment: review manuscript/report human-decision rows before manuscript acceptance
- Blocked non-approval action: reproducibility: Run or document clean-checkout validation with command log and artifact regeneration evidence.
- Blocked non-approval action: reproducibility: Create reproducibility_acceptance.json only after accepted reproduction scope is complete.
- Blocked non-approval action: reproducibility: create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- Blocked non-approval action: reproducibility: replace scaffold-only manifest with clean-checkout final reproduction package
- Blocked non-approval action: reproducibility: resolve reproducibility decision blockers before reproducibility acceptance
- Blocked non-approval action: reproducibility: reproducibility decision: reproducibility manifest remains scaffold-only
- Blocked non-approval action: reproducibility: reproducibility decision: data/manifests/reproducibility_acceptance.json is absent
- Blocked non-approval action: reproducibility: review reproducibility human-decision rows before reproducibility acceptance
- Blocked non-approval action: final_audit: After all pre-final gates are ready, write the independent prompt-to-artifact final audit.
- Blocked non-approval action: final_audit: Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
- Blocked non-approval action: final_audit: create docs/final_study_audit.md after all other gates close
- Blocked non-approval action: final_audit: create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- Blocked non-approval action: final_audit: resolve final-audit decision blockers before final-audit acceptance
- Blocked non-approval action: final_audit: final-audit decision: pre-final gates remain blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- Blocked non-approval action: final_audit: final-audit decision: required formal acceptance artifacts are absent: data/manifests/pilot_acceptance.json, data/manifests/graph_scale_acceptance.json, data/manifests/provenance_acceptance.json, data/parameters/parameter_acceptance.csv, data/parameters/road_class_overrides.csv, data/manifests/validation_acceptance.json, data/manifests/sensitivity_acceptance.json, data/manifests/experiment_acceptance.json, data/manifests/manuscript_acceptance.json, data/manifests/reproducibility_acceptance.json, docs/final_study_audit.md, data/manifests/final_audit_acceptance.json
- Blocked non-approval action: final_audit: final-audit decision: docs/final_study_audit.md is absent
- Blocked non-approval action: final_audit: final-audit decision: data/manifests/final_audit_acceptance.json is absent
- Blocked non-approval action: final_audit: review final-audit human-decision rows before final-audit acceptance
- Blocked non-approval action: final_audit: all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- Blocked non-approval audit item: Pilot Region Accepted: create an explicit pilot acceptance record after privacy and case-scope review
- Blocked non-approval audit item: Pilot Region Accepted: resolve pilot-region decision blockers before pilot acceptance
- Blocked non-approval audit item: Pilot Region Accepted: pilot-region decision: data/manifests/graph_scale_acceptance.json is absent
- Blocked non-approval audit item: Pilot Region Accepted: pilot-region decision: data/manifests/provenance_acceptance.json is absent
- Blocked non-approval audit item: Pilot Region Accepted: pilot-region decision: data/manifests/pilot_acceptance.json is absent
- Blocked non-approval audit item: Pilot Region Accepted: review pilot-region decision human-decision items before pilot acceptance
- Blocked non-approval audit item: Cached OSM Input: road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- Blocked non-approval audit item: Cached OSM Input: road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- Blocked non-approval audit item: Cached OSM Input: road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- Blocked non-approval audit item: Cached OSM Input: road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- Blocked non-approval audit item: Cached OSM Input: road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- Blocked non-approval audit item: Cached OSM Input: road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- Blocked non-approval audit item: Cached OSM Input: road override application: reviewed road-class override table is absent
- Blocked non-approval audit item: Cached OSM Input: road source readiness: cached lane-count evidence has no parseable observed lane rows
- Blocked non-approval audit item: Cached OSM Input: road source readiness: data/parameters/road_class_overrides.csv is absent
- Blocked non-approval audit item: Cached OSM Input: road source readiness: capacity and disruption evidence still require external source or formal assumption decisions
- Blocked non-approval audit item: Cached OSM Input: road source readiness: this packet is readiness evidence only and cannot create road-class overrides
- Blocked non-approval audit item: Cached OSM Input: road source decision: reviewed road_class_overrides.csv is absent
- Blocked non-approval audit item: Cached OSM Input: road source decision: road source decisions are pending for speed, capacity, disruption, benchmark, and override-application requests
- Blocked non-approval audit item: Cached OSM Input: road source decision: retained road assumptions require source-backed updates, sensitivity-only limits, benchmark-only limits, or explicit acceptance
- Blocked non-approval audit item: Cached OSM Input: road source decision: reviewed_road_class_override_application_request: data/parameters/road_class_overrides.csv is absent
- Blocked non-approval audit item: Cached OSM Input: road source decision: road_capacity_lane_count_source_request: cached lane-count evidence has no parseable observed lane rows
- Blocked non-approval audit item: Graph-Scale Strategy: create an explicit graph-scale acceptance record after source-vs-analysis graph review
- Blocked non-approval audit item: Graph-Scale Strategy: resolve graph-scale strategy-readiness blockers before graph-scale acceptance
- Blocked non-approval audit item: Graph-Scale Strategy: graph-scale strategy readiness: full bus-practical graph has smoke evidence only
- Blocked non-approval audit item: Graph-Scale Strategy: graph-scale strategy readiness: data/manifests/graph_scale_acceptance.json is absent
- Blocked non-approval audit item: Graph-Scale Strategy: graph-scale strategy readiness: current reduced-corridor output has alternate-route warnings
- Blocked non-approval audit item: Graph-Scale Strategy: graph-scale strategy readiness: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- Blocked non-approval audit item: Graph-Scale Strategy: graph-scale strategy readiness: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- Blocked non-approval audit item: Graph-Scale Strategy: review graph-scale strategy-readiness human-decision items before graph-scale acceptance
- Blocked non-approval audit item: Graph-Scale Strategy: resolve graph-scale method-decision blockers before graph-scale acceptance
- Blocked non-approval audit item: Graph-Scale Strategy: graph-scale method decision: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- Blocked non-approval audit item: Graph-Scale Strategy: graph-scale method decision: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- Blocked non-approval audit item: Graph-Scale Strategy: graph-scale method decision: data/manifests/graph_scale_acceptance.json is absent
- Blocked non-approval audit item: Graph-Scale Strategy: review graph-scale method-decision human-decision items before graph-scale acceptance
- Blocked non-approval audit item: Data Provenance: create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- Blocked non-approval audit item: Data Provenance: replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance
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
- Blocked non-approval audit item: Data Provenance: resolve source-provenance decision blockers before provenance acceptance
- Blocked non-approval audit item: Data Provenance: source provenance decision: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- Blocked non-approval audit item: Data Provenance: source provenance decision: reproducibility manifest remains scaffold-only
- Blocked non-approval audit item: Data Provenance: source provenance decision: data/manifests/provenance_acceptance.json is absent
- Blocked non-approval audit item: Data Provenance: review source-provenance decision human-decision items before provenance acceptance
- Blocked non-approval audit item: Parameter Evidence: justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- Blocked non-approval audit item: Parameter Evidence: replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- Blocked non-approval audit item: Parameter Evidence: replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- Blocked non-approval audit item: Parameter Evidence: derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- Blocked non-approval audit item: Parameter Evidence: strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- Blocked non-approval audit item: Parameter Evidence: support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- Blocked non-approval audit item: Parameter Evidence: parameter source readiness: all rows require human review or external source decisions before final claims
- Blocked non-approval audit item: Parameter Evidence: parameter source readiness: this packet is readiness evidence only and cannot create accepted parameter values
- Blocked non-approval audit item: Parameter Evidence: parameter source readiness: parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions
- Blocked non-approval audit item: Parameter Evidence: parameter evidence priority: transfer-delay evidence still requires human review and source-backed or accepted-assumption treatment
- Blocked non-approval audit item: Parameter Evidence: parameter evidence priority: rail timing/source-decision evidence is incomplete
- Blocked non-approval audit item: Parameter Evidence: parameter evidence priority: high-priority disruption and traffic/BPR rows still require human/source-backed decisions
- Blocked non-approval audit item: Parameter Evidence: parameter evidence priority: medium-priority demand, fleet, dispatch, and transfer rows remain scenario assumptions
- Blocked non-approval audit item: Parameter Evidence: parameter evidence priority: parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions
- Blocked non-approval audit item: Parameter Evidence: parameter source decision: formal parameter acceptance table is absent
- Blocked non-approval audit item: Parameter Evidence: parameter source decision: parameter source decisions are pending for weak parameter groups
- Blocked non-approval audit item: Parameter Evidence: parameter source decision: retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance
- Blocked non-approval audit item: Rail Evidence: rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- Blocked non-approval audit item: Rail Evidence: rail service evidence: derive headway and travel time from the cached records
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
- Blocked non-approval audit item: Rail Evidence: rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates
- Blocked non-approval audit item: Rail Evidence: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval audit item: Rail Evidence: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- Blocked non-approval audit item: Rail Evidence: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval audit item: Rail Evidence: record reviewed rail source decisions for every row with zero blocking and human-review rows
- Blocked non-approval audit item: Rail Evidence: non-formal rail source-decision action ledger cannot close rail evidence gate
- Blocked non-approval audit item: Rail Evidence: rail source-decision action ledger is not formal acceptance evidence
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile cannot support rail evidence gate
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile is not publication-ready evidence
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile cannot mark complete
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile: rail transit stress profiles are scenario/sensitivity review support only
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile: capacity and availability profiles require reviewer decisions before final claims
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile: rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile: rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- Blocked non-approval audit item: Rail Evidence: rail transit stress profile: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval audit item: Rail Evidence: 4 rail bounded-treatment warnings remain
- Blocked non-approval audit item: Rail Evidence: 2 rail bounded-treatment source decisions remain pending
- Blocked non-approval audit item: Validation Package: create an explicit validation acceptance record after benchmark-strategy review
- Blocked non-approval audit item: Validation Package: resolve validation strategy-readiness blockers before validation acceptance
- Blocked non-approval audit item: Validation Package: validation strategy readiness: validation_acceptance.json is absent
- Blocked non-approval audit item: Validation Package: validation strategy readiness: route-level road evidence exposure remains weak until road evidence gates close
- Blocked non-approval audit item: Validation Package: review validation strategy-readiness human-decision items before validation acceptance
- Blocked non-approval audit item: Validation Package: resolve validation benchmark-decision blockers before validation acceptance
- Blocked non-approval audit item: Validation Package: validation benchmark decision: validation summary still declares scaffold or sanity scope
- Blocked non-approval audit item: Validation Package: validation benchmark decision: route-level road evidence exposure remains weak until road evidence gates close
- Blocked non-approval audit item: Validation Package: validation benchmark decision: data/manifests/validation_acceptance.json is absent
- Blocked non-approval audit item: Validation Package: review validation benchmark-decision human-decision items before validation acceptance
- Blocked non-approval audit item: Validation Package: revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review
- Blocked non-approval audit item: Sensitivity Analysis: create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
- Blocked non-approval audit item: Sensitivity Analysis: resolve sensitivity strategy-readiness blockers before sensitivity acceptance
- Blocked non-approval audit item: Sensitivity Analysis: sensitivity strategy readiness: sensitivity outputs use a reduced analysis graph
- Blocked non-approval audit item: Sensitivity Analysis: sensitivity strategy readiness: current sensitivity result scope is scaffold or not calibrated
- Blocked non-approval audit item: Sensitivity Analysis: sensitivity strategy readiness: Morris-vs-Sobol method decision is not recorded in formal acceptance
- Blocked non-approval audit item: Sensitivity Analysis: sensitivity strategy readiness: data/manifests/sensitivity_acceptance.json is absent
- Blocked non-approval audit item: Sensitivity Analysis: review sensitivity strategy-readiness human-decision items before sensitivity acceptance
- Blocked non-approval audit item: Sensitivity Analysis: accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level
- Blocked non-approval audit item: Full Experiment Output: create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review
- Blocked non-approval audit item: Full Experiment Output: resolve experiment strategy-readiness blockers before experiment acceptance
- Blocked non-approval audit item: Full Experiment Output: experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- Blocked non-approval audit item: Full Experiment Output: experiment strategy readiness: full-pilot outputs depend on a graph method that is not accepted
- Blocked non-approval audit item: Full Experiment Output: experiment strategy readiness: upstream input, road override, parameter, validation, or provenance gates are not accepted
- Blocked non-approval audit item: Full Experiment Output: experiment strategy readiness: data/manifests/experiment_acceptance.json is absent
- Blocked non-approval audit item: Full Experiment Output: review experiment strategy-readiness human-decision items before experiment acceptance
- Blocked non-approval audit item: Full Experiment Output: resolve experiment design-decision blockers before experiment acceptance
- Blocked non-approval audit item: Full Experiment Output: experiment design decision: experiment outputs depend on a graph method that is not accepted
- Blocked non-approval audit item: Full Experiment Output: experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not accepted
- Blocked non-approval audit item: Full Experiment Output: experiment design decision: current full-pilot result scope is scaffold or not calibrated
- Blocked non-approval audit item: Full Experiment Output: experiment design decision: data/manifests/experiment_acceptance.json is absent
- Blocked non-approval audit item: Full Experiment Output: review experiment design-decision human-decision items before experiment acceptance
- Blocked non-approval audit item: Full Experiment Output: accept or regenerate full pilot outputs after input validation and graph-scale decision
- Blocked non-approval audit item: Full Experiment Output: review experiment-package rows before formal experiment acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: close evidence gates before final paper/report claims
- Blocked non-approval audit item: Manuscript Report Alignment: create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- Blocked non-approval audit item: Manuscript Report Alignment: revise figure/table claim boundary from scaffold to accepted study scope
- Blocked non-approval audit item: Manuscript Report Alignment: resolve figure/table review blockers before manuscript acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: figure/table review: figure/table outputs depend on reduced analysis graph scope
- Blocked non-approval audit item: Manuscript Report Alignment: figure/table review: figure/table source outputs remain scaffold or not calibrated
- Blocked non-approval audit item: Manuscript Report Alignment: figure/table review: data/manifests/manuscript_acceptance.json is absent
- Blocked non-approval audit item: Manuscript Report Alignment: review figure/table human-review rows before manuscript acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: review or revise claim-alignment overclaim candidates before manuscript acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: claim alignment: formal manuscript/report review record is absent
- Blocked non-approval audit item: Manuscript Report Alignment: claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- Blocked non-approval audit item: Manuscript Report Alignment: claim alignment: evidence gates remain blocked, so result claims cannot be treated as target-study claims
- Blocked non-approval audit item: Manuscript Report Alignment: resolve manuscript/report decision blockers before manuscript acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent
- Blocked non-approval audit item: Manuscript Report Alignment: manuscript/report decision: claim-alignment packet has 42 rows requiring revision or acceptance
- Blocked non-approval audit item: Manuscript Report Alignment: manuscript/report decision: upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output
- Blocked non-approval audit item: Manuscript Report Alignment: manuscript/report decision: data/manifests/manuscript_acceptance.json is absent
- Blocked non-approval audit item: Manuscript Report Alignment: review manuscript/report human-decision rows before manuscript acceptance
- Blocked non-approval audit item: Reproducibility: create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- Blocked non-approval audit item: Reproducibility: replace scaffold-only manifest with clean-checkout final reproduction package
- Blocked non-approval audit item: Reproducibility: resolve reproducibility decision blockers before reproducibility acceptance
- Blocked non-approval audit item: Reproducibility: reproducibility decision: reproducibility manifest remains scaffold-only
- Blocked non-approval audit item: Reproducibility: reproducibility decision: data/manifests/reproducibility_acceptance.json is absent
- Blocked non-approval audit item: Reproducibility: review reproducibility human-decision rows before reproducibility acceptance
- Blocked non-approval audit item: Final Audit: create docs/final_study_audit.md after all other gates close
- Blocked non-approval audit item: Final Audit: create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- Blocked non-approval audit item: Final Audit: resolve final-audit decision blockers before final-audit acceptance
- Blocked non-approval audit item: Final Audit: final-audit decision: pre-final gates remain blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- Blocked non-approval audit item: Final Audit: final-audit decision: required formal acceptance artifacts are absent: data/manifests/pilot_acceptance.json, data/manifests/graph_scale_acceptance.json, data/manifests/provenance_acceptance.json, data/parameters/parameter_acceptance.csv, data/parameters/road_class_overrides.csv, data/manifests/validation_acceptance.json, data/manifests/sensitivity_acceptance.json, data/manifests/experiment_acceptance.json, data/manifests/manuscript_acceptance.json, data/manifests/reproducibility_acceptance.json, docs/final_study_audit.md, data/manifests/final_audit_acceptance.json
- Blocked non-approval audit item: Final Audit: final-audit decision: docs/final_study_audit.md is absent
- Blocked non-approval audit item: Final Audit: final-audit decision: data/manifests/final_audit_acceptance.json is absent
- Blocked non-approval audit item: Final Audit: review final-audit human-decision rows before final-audit acceptance
- Blocked non-approval audit item: Final Audit: all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
