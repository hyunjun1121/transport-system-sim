# Formal Review Evidence Matrix

Formal review evidence matrix only. Rows connect each required review artifact to review packets, templates, agents, blockers, and check commands. They do not approve evidence, certify sources, calibrate results, or close final-study gates.

## Summary

- Matrix rows: 12
- Formal gates: 12
- Ready formal gates: 11
- Blocked formal gates: 1
- Human decisions required: 1
- Formal acceptance ready: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- CSV: `data/manifests/formal_acceptance_evidence_matrix.csv`

## Matrix

| Gate | Agent | Formal Target | Status | Template Or Worksheet | Review Packets | Check Commands |
| --- | --- | --- | --- | --- | --- | --- |
| pilot_region_accepted | Pilot Region & Privacy Review Agent | `data/manifests/pilot_acceptance.json` | `ready` | `` | data/manifests/pilot_privacy_review_packet.csv<br>data/manifests/pilot_region_decision_packet.csv<br>+1 more | none |
| graph_scale_strategy | Graph Scale Method Review Agent | `data/manifests/graph_scale_acceptance.json` | `ready` | `` | data/validation/graph_scale_review_packet.csv<br>data/validation/full_graph_runtime_readiness_packet.csv<br>+4 more | none |
| data_provenance | OSM / Source / License / Provenance Review Agent | `data/manifests/provenance_acceptance.json` | `ready` | `` | data/manifests/source_license_review_packet.csv<br>data/manifests/source_url_review_packet.csv<br>+6 more | none |
| parameter_acceptance | Road / Rail / Parameter Evidence Agent | `data/parameters/parameter_acceptance.csv` | `ready` | `` | data/parameters/parameter_evidence_review_packet.csv<br>data/parameters/parameter_source_readiness_packet.csv<br>+14 more | none |
| road_class_overrides | Road / Rail / Parameter Evidence Agent | `data/parameters/road_class_overrides.csv` | `ready` | `data/parameters/road_class_overrides_draft.csv` | docs/review_packets/cached_osm_input.md<br>data/parameters/parameter_evidence_review_packet.csv<br>+14 more | .\.venv\Scripts\python scripts\audit_road_overrides.py<br>.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| validation_package | Benchmark Strategy Review Agent | `data/manifests/validation_acceptance.json` | `ready` | `` | data/validation/validation_review_packet.csv<br>data/validation/validation_strategy_readiness_packet.csv<br>+3 more | none |
| sensitivity_analysis | Sensitivity Analysis Review Agent | `data/manifests/sensitivity_acceptance.json` | `ready` | `` | data/validation/sensitivity_review_packet.csv<br>data/validation/sensitivity_index_review_packet.csv<br>+3 more | none |
| full_experiment_output | Full Experiment Package Agent | `data/manifests/experiment_acceptance.json` | `ready` | `` | data/manifests/experiment_package_review_packet.csv<br>data/manifests/experiment_strategy_readiness_packet.csv<br>+2 more | none |
| manuscript_report_alignment | Paper / Report Claim Alignment Agent | `data/manifests/manuscript_acceptance.json` | `ready` | `` | data/manifests/claim_alignment_review_packet.csv<br>data/manifests/figure_table_review_packet.csv<br>+2 more | none |
| reproducibility | Clean-Checkout Reproducibility Agent | `data/manifests/reproducibility_acceptance.json` | `ready` | `` | data/validation/reproducibility_review_packet.csv<br>data/validation/reproducibility_decision_packet.csv<br>+2 more | none |
| final_audit_document | Independent Audit Review Agent | `docs/final_study_audit.md` | `blocked` | `docs/human_acceptance_runbook.md` | docs/review_packets/final_audit.md<br>data/manifests/final_audit_decision_packet.csv | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| final_audit | Independent Audit Review Agent | `data/manifests/final_audit_acceptance.json` | `ready` | `` | data/manifests/final_audit_decision_packet.csv<br>docs/review_packets/final_audit.md | none |

## Use

Use this matrix as the reviewer intake index. The matrix tells reviewers which packets, templates, paths, and commands belong to each formal target. It must not be copied into a formal acceptance path and cannot make the active goal complete.
