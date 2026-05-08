# Acceptance Review Index

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Final-study ready: `false`
- Record count: 12
- Can-mark-complete records: 0

| Gate | Agent | Status | Can Mark Complete | Required Action Count |
| --- | --- | --- | --- | --- |
| `pilot_region_accepted` | Pilot Region & Privacy Review Agent | `needs_human_review` | `false` | 2 |
| `data_provenance` | OSM / Source / License / Provenance Review Agent | `blocked` | `false` | 4 |
| `graph_scale_strategy` | Graph Scale Method Review Agent | `needs_human_review` | `false` | 9 |
| `cached_osm_input` | Road / Rail / Parameter Evidence Agent | `blocked` | `false` | 12 |
| `parameter_evidence` | Road / Rail / Parameter Evidence Agent | `blocked` | `false` | 15 |
| `rail_evidence` | Road / Rail / Parameter Evidence Agent | `blocked` | `false` | 10 |
| `validation_package` | Validation Benchmark Strategy Agent | `needs_human_review` | `false` | 8 |
| `sensitivity_analysis` | Sensitivity Analysis Review Agent | `blocked` | `false` | 10 |
| `full_experiment_output` | Full Experiment Package Agent | `blocked` | `false` | 11 |
| `manuscript_report_alignment` | Paper / Report Claim Alignment Agent | `blocked` | `false` | 9 |
| `reproducibility` | Clean-Checkout Reproducibility Agent | `blocked` | `false` | 4 |
| `final_audit` | Final Independent Audit Agent | `blocked` | `false` | 5 |

## Remaining Blockers

- pilot_region_accepted: Record an explicit pilot acceptance decision with reviewer, scope, privacy review, evidence paths, and not-operational claim boundary.
- pilot_region_accepted: create an explicit pilot acceptance record after privacy and case-scope review
- data_provenance: Review source URLs, licenses, attribution, local snapshots, privacy abstraction, and reproducibility scope.
- data_provenance: Create data/manifests/provenance_acceptance.json only after source-backed review.
- data_provenance: create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- data_provenance: replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance
- graph_scale_strategy: Choose and document reduced-corridor, multi-corridor, or full-graph strategy.
- graph_scale_strategy: Create graph_scale_acceptance.json with matching graph counts and evidence paths.
- graph_scale_strategy: create an explicit graph-scale acceptance record after source-vs-analysis graph review
- graph_scale_strategy: resolve graph-scale strategy-readiness blockers before graph-scale acceptance
- graph_scale_strategy: graph-scale strategy readiness: graph_scale_acceptance.json is absent
- graph_scale_strategy: graph-scale strategy readiness: current reduced-corridor output has alternate-route warnings
- graph_scale_strategy: graph-scale strategy readiness: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- graph_scale_strategy: graph-scale strategy readiness: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- graph_scale_strategy: review graph-scale strategy-readiness human-decision items before graph-scale acceptance
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
- validation_package: Review validation thresholds, benchmark scope, snapshot pinning, and failure cases.
- validation_package: Create validation_acceptance.json after benchmark-strategy review.
- validation_package: create an explicit validation acceptance record after benchmark-strategy review
- validation_package: resolve validation strategy-readiness blockers before validation acceptance
- validation_package: validation strategy readiness: validation_acceptance.json is absent
- validation_package: validation strategy readiness: route-level road evidence exposure remains weak until road evidence gates close
- validation_package: review validation strategy-readiness human-decision items before validation acceptance
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
- full_experiment_output: accept or regenerate full pilot outputs after input validation and graph-scale decision
- full_experiment_output: review experiment-package rows before formal experiment acceptance
- manuscript_report_alignment: Revise or hold claims until all supporting evidence gates are accepted.
- manuscript_report_alignment: Create manuscript_acceptance.json after claim-by-claim review.
- manuscript_report_alignment: close evidence gates before final paper/report claims
- manuscript_report_alignment: create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- manuscript_report_alignment: revise figure/table claim boundary from scaffold to accepted study scope
- manuscript_report_alignment: review or revise claim-alignment overclaim candidates before manuscript acceptance
- manuscript_report_alignment: claim alignment: formal manuscript/report acceptance record is absent
- manuscript_report_alignment: claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- manuscript_report_alignment: claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims
- reproducibility: Run or document clean-checkout validation with command log and artifact regeneration evidence.
- reproducibility: Create reproducibility_acceptance.json only after accepted reproduction scope is complete.
- reproducibility: create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- reproducibility: replace scaffold-only manifest with clean-checkout final reproduction package
- final_audit: After all pre-final gates are ready, write the independent prompt-to-artifact final audit.
- final_audit: Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
- final_audit: create docs/final_study_audit.md after all other gates close
- final_audit: create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- final_audit: all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- Pilot Region Accepted: create an explicit pilot acceptance record after privacy and case-scope review
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
- Graph-Scale Strategy: create an explicit graph-scale acceptance record after source-vs-analysis graph review
- Graph-Scale Strategy: resolve graph-scale strategy-readiness blockers before graph-scale acceptance
- Graph-Scale Strategy: graph-scale strategy readiness: graph_scale_acceptance.json is absent
- Graph-Scale Strategy: graph-scale strategy readiness: current reduced-corridor output has alternate-route warnings
- Graph-Scale Strategy: graph-scale strategy readiness: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- Graph-Scale Strategy: graph-scale strategy readiness: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- Graph-Scale Strategy: review graph-scale strategy-readiness human-decision items before graph-scale acceptance
- Data Provenance: create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- Data Provenance: replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance
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
- Rail Evidence: rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- Rail Evidence: rail service evidence: derive headway and travel time from the cached records
- Rail Evidence: rail fetch readiness: rail timing cache files are absent unless source_cache_present is true
- Rail Evidence: rail fetch readiness: API-key and reviewed-GTFS rows require external reviewer-provided inputs
- Rail Evidence: rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- Rail Evidence: rail evidence priority: rail timing cache files are absent
- Rail Evidence: rail evidence priority: DATA_GO_KR_KEY or reviewed GTFS input is absent
- Rail Evidence: rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- Validation Package: create an explicit validation acceptance record after benchmark-strategy review
- Validation Package: resolve validation strategy-readiness blockers before validation acceptance
- Validation Package: validation strategy readiness: validation_acceptance.json is absent
- Validation Package: validation strategy readiness: route-level road evidence exposure remains weak until road evidence gates close
- Validation Package: review validation strategy-readiness human-decision items before validation acceptance
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
- Full Experiment Output: accept or regenerate full pilot outputs after input validation and graph-scale decision
- Full Experiment Output: review experiment-package rows before formal experiment acceptance
- Manuscript Report Alignment: close evidence gates before final paper/report claims
- Manuscript Report Alignment: create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- Manuscript Report Alignment: revise figure/table claim boundary from scaffold to accepted study scope
- Manuscript Report Alignment: review or revise claim-alignment overclaim candidates before manuscript acceptance
- Manuscript Report Alignment: claim alignment: formal manuscript/report acceptance record is absent
- Manuscript Report Alignment: claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- Manuscript Report Alignment: claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims
- Reproducibility: create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- Reproducibility: replace scaffold-only manifest with clean-checkout final reproduction package
- Final Audit: create docs/final_study_audit.md after all other gates close
- Final Audit: create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- Final Audit: all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
