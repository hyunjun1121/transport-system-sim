# Formal Acceptance Pre-Review

Draft pre-review recommendations only. These records classify remaining formal acceptance gates for human reviewers; they do not create formal approval, certify evidence, validate licenses, calibrate results, or mark the final study complete.

## Summary

- Draft records: 12
- Recommendation counts: `{'blocked_requires_human_decision': 4, 'blocked_missing_evidence': 8}`
- Human decisions required: 12
- Formal approval made: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- Draft directory: `data/manifests/draft_acceptance`

## Gate Recommendations

| Gate | Current Status | Recommendation | Formal Target | Missing Evidence | Human Action |
| --- | --- | --- | --- | --- | --- |
| pilot_region_accepted | `blocked` | `blocked_requires_human_decision` | `data/manifests/pilot_acceptance.json` | create an explicit pilot acceptance record after privacy and case-scope review<br>data/manifests/pilot_acceptance.json is absent | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| graph_scale_strategy | `blocked` | `blocked_requires_human_decision` | `data/manifests/graph_scale_acceptance.json` | create an explicit graph-scale acceptance record after source-vs-analysis graph review<br>data/manifests/graph_scale_acceptance.json is absent | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| data_provenance | `blocked` | `blocked_requires_human_decision` | `data/manifests/provenance_acceptance.json` | create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review<br>replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance<br>+1 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| parameter_acceptance | `blocked` | `blocked_missing_evidence` | `data/parameters/parameter_acceptance.csv` | create reviewed parameter acceptance records only for weak assumptions retained in final claims<br>parameter_acceptance.csv is missing<br>+9 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| road_class_overrides | `blocked` | `blocked_missing_evidence` | `data/parameters/road_class_overrides.csv` | replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence<br>apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs<br>+9 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| validation_package | `blocked` | `blocked_requires_human_decision` | `data/manifests/validation_acceptance.json` | create an explicit validation acceptance record after benchmark-strategy review<br>revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review<br>+1 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| sensitivity_analysis | `blocked` | `blocked_missing_evidence` | `data/manifests/sensitivity_acceptance.json` | create an explicit sensitivity acceptance record after SALib output and Sobol-decision review<br>accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level<br>+1 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| full_experiment_output | `blocked` | `blocked_missing_evidence` | `data/manifests/experiment_acceptance.json` | create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review<br>accept or regenerate full pilot outputs after input validation and graph-scale decision<br>+2 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| manuscript_report_alignment | `blocked` | `blocked_missing_evidence` | `data/manifests/manuscript_acceptance.json` | create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed<br>close evidence gates before final paper/report claims<br>+3 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| reproducibility | `blocked` | `blocked_missing_evidence` | `data/manifests/reproducibility_acceptance.json` | create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks<br>replace scaffold-only manifest with clean-checkout final reproduction package<br>+1 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| final_audit_document | `blocked` | `blocked_missing_evidence` | `docs/final_study_audit.md` | create docs/final_study_audit.md after all other gates close<br>create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed<br>+2 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+5 more |
| final_audit | `blocked` | `blocked_missing_evidence` | `data/manifests/final_audit_acceptance.json` | create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed<br>create docs/final_study_audit.md after all other gates close<br>+2 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+5 more |

## Gate Details

### pilot_region_accepted

- Label: Pilot Region Acceptance
- Related plan gates: `pilot_region_accepted`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/pilot_acceptance.json`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `data/regions/pilot_region.yaml`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/pilot_region_data_card.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/pilot_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/pilot_region_accepted.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/current_goal_completion_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/pilot_privacy_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/pilot_privacy_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/pilot_privacy_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create an explicit pilot acceptance record after privacy and case-scope review
- data/manifests/pilot_acceptance.json is absent

Residual risks:
- Record an explicit pilot acceptance decision with reviewer, scope, privacy review, evidence paths, and not-operational claim boundary.
- create an explicit pilot acceptance record after privacy and case-scope review
- data/manifests/pilot_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Approve, reject, or keep blocked based on the existing review packet evidence.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/pilot_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/pilot_acceptance.json

### graph_scale_strategy

- Label: Graph-Scale Acceptance
- Related plan gates: `graph_scale_strategy`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/graph_scale_acceptance.json`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `results/realworld_pilot/pilot_full_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_route_comparison.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_alternate_routes.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_multi_corridor_routes.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/graph_scale_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/graph_scale_strategy.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/analysis_corridor_method_note.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/graph_scale_diagnostics.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_result_comparison.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_route_comparison_summary.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_alternate_routes_summary.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_multi_corridor_routes_summary.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_result_comparison_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_graph_scale_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_graph_scale_result_comparison.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_graph_scale_diagnostics.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_results.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_summary.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_full_results.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_full_summary.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_full_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create an explicit graph-scale acceptance record after source-vs-analysis graph review
- data/manifests/graph_scale_acceptance.json is absent

Residual risks:
- Choose and document reduced-corridor, multi-corridor, or full-graph strategy.
- Create graph_scale_acceptance.json with matching graph counts and evidence paths.
- create an explicit graph-scale acceptance record after source-vs-analysis graph review
- data/manifests/graph_scale_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Approve, reject, or keep blocked based on the existing review packet evidence.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/graph_scale_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/graph_scale_acceptance.json

### data_provenance

- Label: Source/License/Provenance Acceptance
- Related plan gates: `data_provenance`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/provenance_acceptance.json`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `data/manifests/source_provenance_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/reproducibility_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/cache/pilot_region_road_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `cloned_repo_manifest.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/provenance_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/data_provenance.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/reproducibility_package.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_license_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_license_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_url_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_url_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_url_remediation_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_url_remediation_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/source_license_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/source_url_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/source_url_remediation_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/pilot_region_data_card.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_source_provenance.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_source_license_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_source_url_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_source_url_remediation_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance
- data/manifests/provenance_acceptance.json is absent

Residual risks:
- Review source URLs, licenses, attribution, local snapshots, privacy abstraction, and reproducibility scope.
- Create data/manifests/provenance_acceptance.json only after source-backed review.
- create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance
- data/manifests/provenance_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Approve, reject, or keep blocked based on the existing review packet evidence.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/provenance_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/provenance_acceptance.json

### parameter_acceptance

- Label: Weak-Parameter Acceptance
- Related plan gates: `parameter_evidence`, `rail_evidence`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/parameters/parameter_acceptance.csv`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `data/parameters/parameter_sources.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_class_overrides_draft.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_service_evidence.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_station_bindings.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_acceptance.csv`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/parameter_evidence.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/review_packets/cached_osm_input.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/review_packets/rail_evidence.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_timing_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_source_request_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_source_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_source_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/parameter_source_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_parameter_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_parameter_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_parameter_evidence_source_request_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_parameter_source_readiness_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_evidence_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_timing_source_request_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_fetch_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_fetch_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/rail_fetch_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_rail_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_rail_evidence_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_rail_timing_source_request_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_rail_fetch_readiness_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/fetch_rail_timetable_cache.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/derive_rail_headway_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/derive_rail_service_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/derive_rail_gtfs_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/rail_gtfs_cache_schema.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/fetch_rail_shortest_path_cache.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/derive_rail_shortest_path_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create reviewed parameter acceptance records only for weak assumptions retained in final claims
- parameter_acceptance.csv is missing
- justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- rail service evidence: derive headway and travel time from the cached records
- data/parameters/parameter_acceptance.csv is absent

Residual risks:
- Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- create reviewed parameter acceptance records only for weak assumptions retained in final claims
- parameter_acceptance.csv is missing
- justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- rail service evidence: derive headway and travel time from the cached records
- data/parameters/parameter_acceptance.csv is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/parameters/parameter_acceptance.csv.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/parameters/parameter_acceptance.csv

### road_class_overrides

- Label: Road-Class Override Acceptance
- Related plan gates: `cached_osm_input`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/parameters/road_class_overrides.csv`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `data/parameters/parameter_sources.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_class_overrides_draft.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_service_evidence.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_station_bindings.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_class_overrides.csv`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/cached_osm_input.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/review_packets/parameter_evidence.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/review_packets/rail_evidence.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_timing_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/cache/pilot_region_road.graphml`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/cache/pilot_region_road_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_road_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_road_evidence_diagnostics.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_speed_evidence_candidates.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_capacity_evidence_candidates.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_evidence_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_evidence_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_evidence_source_request_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_source_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_source_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/road_source_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_speed_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_capacity_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_evidence_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_evidence_source_request_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_source_readiness_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_class_override_template.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_road_overrides.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- reviewed road-class override table is absent
- road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- road override application: reviewed road-class override table is absent
- data/parameters/road_class_overrides.csv is absent

Residual risks:
- Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- reviewed road-class override table is absent
- road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- road override application: reviewed road-class override table is absent
- data/parameters/road_class_overrides.csv is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/parameters/road_class_overrides.csv.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/parameters/road_class_overrides.csv
- results/realworld_pilot/pilot_full_manifest.json
- results/realworld_pilot/pilot_full_results.csv
- data/manifests/experiment_acceptance.json

### validation_package

- Label: Validation Acceptance
- Related plan gates: `validation_package`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/validation_acceptance.json`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `data/validation/validation_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/osrm_route_benchmark_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/canonical_route_road_evidence_exposure.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/validation_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/validation_package.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/validation_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/osrm_route_benchmark_manifest.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/validation_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/validation_summary.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/external_route_benchmarks.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/external_route_benchmarks_osrm.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/accessibility_loss.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/accessibility_loss_summary.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/canonical_route_road_evidence_exposure_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_plausibility_validation.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_accessibility_loss_analysis.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_route_road_evidence_exposure.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_osrm_route_benchmark.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_osrm_snapshot_manifest.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_validation_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create an explicit validation acceptance record after benchmark-strategy review
- revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review
- data/manifests/validation_acceptance.json is absent

Residual risks:
- Review validation thresholds, benchmark scope, snapshot pinning, and failure cases.
- Create validation_acceptance.json after benchmark-strategy review.
- create an explicit validation acceptance record after benchmark-strategy review
- revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review
- data/manifests/validation_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Approve, reject, or keep blocked based on the existing review packet evidence.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/validation_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/validation_acceptance.json

### sensitivity_analysis

- Label: Sensitivity Acceptance
- Related plan gates: `sensitivity_analysis`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/manifests/sensitivity_acceptance.json`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `results/realworld_pilot/morris_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/morris_results.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/morris_summary.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/sensitivity_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/sensitivity_analysis.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/sensitivity_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/sensitivity_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_sensitivity.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_sensitivity_diagnostics.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_sensitivity_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
- accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level
- data/manifests/sensitivity_acceptance.json is absent

Residual risks:
- Review parameter ranges and decide whether Morris is enough or Sobol is required.
- Create sensitivity_acceptance.json after final input and graph scope are accepted.
- create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
- accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level
- data/manifests/sensitivity_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/sensitivity_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/sensitivity_acceptance.json

### full_experiment_output

- Label: Experiment Acceptance
- Related plan gates: `full_experiment_output`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/manifests/experiment_acceptance.json`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `results/realworld_pilot/pilot_full_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_full_results.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_full_summary.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/experiment_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/full_experiment_output.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_pilot_experiments.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/scenarios/disruption_scenarios.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/scenarios/policy_alternatives.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/experiment_package_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/experiment_package_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/experiment_package_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review
- accept or regenerate full pilot outputs after input validation and graph-scale decision
- review experiment-package rows before formal experiment acceptance
- data/manifests/experiment_acceptance.json is absent

Residual risks:
- Regenerate or accept full outputs after input, graph-scale, and validation gates close.
- Create experiment_acceptance.json with matching run profile and row counts.
- create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review
- accept or regenerate full pilot outputs after input validation and graph-scale decision
- review experiment-package rows before formal experiment acceptance
- data/manifests/experiment_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/experiment_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/experiment_acceptance.json

### manuscript_report_alignment

- Label: Manuscript/Report Acceptance
- Related plan gates: `manuscript_report_alignment`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/manifests/manuscript_acceptance.json`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `paper/paper_draft.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `report_draft.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `report.docx`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/tables/figure_table_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/manuscript_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/manuscript_report_alignment.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_publication_readiness.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/current_goal_completion_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/claim_alignment_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/claim_alignment_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/claim_alignment_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- close evidence gates before final paper/report claims
- revise figure/table claim boundary from scaffold to accepted study scope
- review or revise claim-alignment overclaim candidates before manuscript acceptance
- data/manifests/manuscript_acceptance.json is absent

Residual risks:
- Revise or hold claims until all supporting evidence gates are accepted.
- Create manuscript_acceptance.json after claim-by-claim review.
- create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- close evidence gates before final paper/report claims
- revise figure/table claim boundary from scaffold to accepted study scope
- review or revise claim-alignment overclaim candidates before manuscript acceptance
- data/manifests/manuscript_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/manuscript_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/manuscript_acceptance.json

### reproducibility

- Label: Reproducibility Acceptance
- Related plan gates: `reproducibility`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/manifests/reproducibility_acceptance.json`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `data/manifests/reproducibility_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/reproducibility_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/reproducibility_package.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `requirements.txt`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/reproducibility_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/reproducibility.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/reproducibility_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_plan_artifacts.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/reproducibility_smoke_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/reproducibility_smoke.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/clean_checkout_reproducibility_smoke_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/clean_checkout_reproducibility_smoke.md`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- replace scaffold-only manifest with clean-checkout final reproduction package
- data/manifests/reproducibility_acceptance.json is absent

Residual risks:
- Run or document clean-checkout validation with command log and artifact regeneration evidence.
- Create reproducibility_acceptance.json only after accepted reproduction scope is complete.
- create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- replace scaffold-only manifest with clean-checkout final reproduction package
- data/manifests/reproducibility_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/reproducibility_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/reproducibility_acceptance.json

### final_audit_document

- Label: Final Study Audit Document
- Related plan gates: `final_audit`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `docs/final_study_audit.md`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `docs/current_goal_completion_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/acceptance_orchestration_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/final_study_audit.md`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/final_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_final_study_readiness.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/final_audit_acceptance.json`: absent; local supporting artifact absent

Missing evidence:
- create docs/final_study_audit.md after all other gates close
- create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- docs/final_study_audit.md is absent

Residual risks:
- After all pre-final gates are ready, write the independent prompt-to-artifact final audit.
- Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
- create docs/final_study_audit.md after all other gates close
- create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- docs/final_study_audit.md is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Wait until every pre-final formal gate is accepted before creating final-audit artifacts.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update docs/final_study_audit.md.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- docs/final_study_audit.md
- data/manifests/final_audit_acceptance.json

### final_audit

- Label: Final Audit Acceptance
- Related plan gates: `final_audit`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/manifests/final_audit_acceptance.json`
- Formal approval: `false`
- Human decision required: `true`

Evidence inspected:
- `docs/current_goal_completion_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/acceptance_orchestration_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/final_audit_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/final_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_final_study_readiness.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/final_study_audit.md`: absent; local supporting artifact absent

Missing evidence:
- create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- create docs/final_study_audit.md after all other gates close
- all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- data/manifests/final_audit_acceptance.json is absent

Residual risks:
- After all pre-final gates are ready, write the independent prompt-to-artifact final audit.
- Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
- create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- create docs/final_study_audit.md after all other gates close
- all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- data/manifests/final_audit_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Wait until every pre-final formal gate is accepted before creating final-audit artifacts.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/final_audit_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/final_audit_acceptance.json
- docs/final_study_audit.md

## Use

Use these draft records to decide whether a human reviewer should approve, reject, or keep each gate blocked. Do not move any draft JSON into a formal acceptance path unless a reviewer replaces the draft fields with source-backed acceptance evidence and then reruns the formal package validators.
