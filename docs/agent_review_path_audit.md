# Agent Review Path Audit

This audit checks sub-agent review-record path hygiene only. It does not approve evidence quality, licenses, calibration, reviewer decisions, or final-study readiness.

## Summary

- Agent review paths ready: `true`
- Can mark complete: `false`
- Review records: 12
- Path references: 571
- Present paths: 535
- Missing required paths: 0
- Missing formal targets: 36

## Missing Formal Targets

These are expected to remain absent until reviewed acceptance decisions are supplied.

| Gate | Field | Path | Record |
| --- | --- | --- | --- |
| cached_osm_input | source_paths | `data/parameters/road_class_overrides.csv` | `data/manifests/agent_reviews/cached_osm_input__road_rail_parameter_evidence_agent.json` |
| cached_osm_input | source_paths | `data/parameters/parameter_acceptance.csv` | `data/manifests/agent_reviews/cached_osm_input__road_rail_parameter_evidence_agent.json` |
| data_provenance | evidence | `data/manifests/provenance_acceptance.json` | `data/manifests/agent_reviews/data_provenance__osm_source_license_provenance_review_agent.json` |
| data_provenance | source_paths | `data/manifests/provenance_acceptance.json` | `data/manifests/agent_reviews/data_provenance__osm_source_license_provenance_review_agent.json` |
| data_provenance | reviewed_inputs | `data/manifests/provenance_acceptance.json` | `data/manifests/agent_reviews/data_provenance__osm_source_license_provenance_review_agent.json` |
| final_audit | evidence | `docs/final_study_audit.md` | `data/manifests/agent_reviews/final_audit__final_independent_audit_agent.json` |
| final_audit | evidence | `data/manifests/final_audit_acceptance.json` | `data/manifests/agent_reviews/final_audit__final_independent_audit_agent.json` |
| final_audit | source_paths | `docs/final_study_audit.md` | `data/manifests/agent_reviews/final_audit__final_independent_audit_agent.json` |
| final_audit | source_paths | `data/manifests/final_audit_acceptance.json` | `data/manifests/agent_reviews/final_audit__final_independent_audit_agent.json` |
| final_audit | reviewed_inputs | `docs/final_study_audit.md` | `data/manifests/agent_reviews/final_audit__final_independent_audit_agent.json` |
| final_audit | reviewed_inputs | `data/manifests/final_audit_acceptance.json` | `data/manifests/agent_reviews/final_audit__final_independent_audit_agent.json` |
| full_experiment_output | evidence | `data/manifests/experiment_acceptance.json` | `data/manifests/agent_reviews/full_experiment_output__full_experiment_package_agent.json` |
| full_experiment_output | source_paths | `data/manifests/experiment_acceptance.json` | `data/manifests/agent_reviews/full_experiment_output__full_experiment_package_agent.json` |
| full_experiment_output | reviewed_inputs | `data/manifests/experiment_acceptance.json` | `data/manifests/agent_reviews/full_experiment_output__full_experiment_package_agent.json` |
| graph_scale_strategy | evidence | `data/manifests/graph_scale_acceptance.json` | `data/manifests/agent_reviews/graph_scale_strategy__graph_scale_method_review_agent.json` |
| graph_scale_strategy | source_paths | `data/manifests/graph_scale_acceptance.json` | `data/manifests/agent_reviews/graph_scale_strategy__graph_scale_method_review_agent.json` |
| graph_scale_strategy | reviewed_inputs | `data/manifests/graph_scale_acceptance.json` | `data/manifests/agent_reviews/graph_scale_strategy__graph_scale_method_review_agent.json` |
| manuscript_report_alignment | evidence | `data/manifests/manuscript_acceptance.json` | `data/manifests/agent_reviews/manuscript_report_alignment__paper_report_claim_alignment_agent.json` |
| manuscript_report_alignment | source_paths | `data/manifests/manuscript_acceptance.json` | `data/manifests/agent_reviews/manuscript_report_alignment__paper_report_claim_alignment_agent.json` |
| manuscript_report_alignment | reviewed_inputs | `data/manifests/manuscript_acceptance.json` | `data/manifests/agent_reviews/manuscript_report_alignment__paper_report_claim_alignment_agent.json` |
| parameter_evidence | source_paths | `data/parameters/road_class_overrides.csv` | `data/manifests/agent_reviews/parameter_evidence__road_rail_parameter_evidence_agent.json` |
| parameter_evidence | source_paths | `data/parameters/parameter_acceptance.csv` | `data/manifests/agent_reviews/parameter_evidence__road_rail_parameter_evidence_agent.json` |
| pilot_region_accepted | evidence | `data/manifests/pilot_acceptance.json` | `data/manifests/agent_reviews/pilot_region_accepted__pilot_region_privacy_review_agent.json` |
| pilot_region_accepted | source_paths | `data/manifests/pilot_acceptance.json` | `data/manifests/agent_reviews/pilot_region_accepted__pilot_region_privacy_review_agent.json` |
| pilot_region_accepted | reviewed_inputs | `data/manifests/pilot_acceptance.json` | `data/manifests/agent_reviews/pilot_region_accepted__pilot_region_privacy_review_agent.json` |
| rail_evidence | source_paths | `data/parameters/road_class_overrides.csv` | `data/manifests/agent_reviews/rail_evidence__road_rail_parameter_evidence_agent.json` |
| rail_evidence | source_paths | `data/parameters/parameter_acceptance.csv` | `data/manifests/agent_reviews/rail_evidence__road_rail_parameter_evidence_agent.json` |
| reproducibility | evidence | `data/manifests/reproducibility_acceptance.json` | `data/manifests/agent_reviews/reproducibility__clean_checkout_reproducibility_agent.json` |
| reproducibility | source_paths | `data/manifests/reproducibility_acceptance.json` | `data/manifests/agent_reviews/reproducibility__clean_checkout_reproducibility_agent.json` |
| reproducibility | reviewed_inputs | `data/manifests/reproducibility_acceptance.json` | `data/manifests/agent_reviews/reproducibility__clean_checkout_reproducibility_agent.json` |
| sensitivity_analysis | evidence | `data/manifests/sensitivity_acceptance.json` | `data/manifests/agent_reviews/sensitivity_analysis__sensitivity_analysis_review_agent.json` |
| sensitivity_analysis | source_paths | `data/manifests/sensitivity_acceptance.json` | `data/manifests/agent_reviews/sensitivity_analysis__sensitivity_analysis_review_agent.json` |
| sensitivity_analysis | reviewed_inputs | `data/manifests/sensitivity_acceptance.json` | `data/manifests/agent_reviews/sensitivity_analysis__sensitivity_analysis_review_agent.json` |
| validation_package | evidence | `data/manifests/validation_acceptance.json` | `data/manifests/agent_reviews/validation_package__validation_benchmark_strategy_agent.json` |
| validation_package | source_paths | `data/manifests/validation_acceptance.json` | `data/manifests/agent_reviews/validation_package__validation_benchmark_strategy_agent.json` |
| validation_package | reviewed_inputs | `data/manifests/validation_acceptance.json` | `data/manifests/agent_reviews/validation_package__validation_benchmark_strategy_agent.json` |

## Remaining Blockers

- None for path hygiene. This still does not approve any gate.
