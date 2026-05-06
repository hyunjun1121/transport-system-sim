# Formal Acceptance Evidence Matrix

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


Formal acceptance evidence matrix only. Rows connect each required formal artifact to review packets, templates, agents, blockers, and validation commands. They do not approve evidence, certify sources, calibrate results, or close final-study gates.

## Summary

- Matrix rows: 12
- Formal gates: 12
- Ready formal gates: 0
- Blocked formal gates: 12
- Human decisions required: 12
- Formal acceptance artifacts present: 0 / 12
- Formal acceptance artifacts absent: 12 / 12
- Formal acceptance ready: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- CSV: `data/manifests/formal_acceptance_evidence_matrix.csv`

## Matrix

| Gate | Agent | Formal Target | Status | Template Or Worksheet | Review Packets | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| pilot_region_accepted | Pilot Region & Privacy Review Agent | `data/manifests/pilot_acceptance.json` | `blocked` | `data/manifests/acceptance_templates/pilot_acceptance_template.json` | docs/review_packets/pilot_region_accepted.md | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| graph_scale_strategy | Graph Scale Method Review Agent | `data/manifests/graph_scale_acceptance.json` | `blocked` | `data/manifests/acceptance_templates/graph_scale_acceptance_template.json` | docs/review_packets/graph_scale_strategy.md<br>docs/graph_scale_strategy_readiness_packet.md<br>data/validation/graph_scale_review_packet.csv<br>data/validation/graph_scale_strategy_readiness_packet.csv | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| data_provenance | OSM / Source / License / Provenance Review Agent | `data/manifests/provenance_acceptance.json` | `blocked` | `data/manifests/acceptance_templates/provenance_acceptance_template.json` | docs/review_packets/data_provenance.md | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| parameter_acceptance | Road / Rail / Parameter Evidence Agent | `data/parameters/parameter_acceptance.csv` | `blocked` | `data/parameters/parameter_acceptance_template.csv` | docs/review_packets/parameter_evidence.md<br>data/parameters/parameter_evidence_review_packet.csv<br>+4 more | .\.venv\Scripts\python tests\test_realworld_parameter_acceptance.py<br>.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| road_class_overrides | Road / Rail / Parameter Evidence Agent | `data/parameters/road_class_overrides.csv` | `blocked` | `data/parameters/road_class_overrides_draft.csv` | docs/review_packets/cached_osm_input.md<br>data/parameters/parameter_evidence_review_packet.csv<br>+4 more | .\.venv\Scripts\python scripts\audit_road_overrides.py<br>.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| validation_package | Validation Benchmark Strategy Agent | `data/manifests/validation_acceptance.json` | `blocked` | `data/manifests/acceptance_templates/validation_acceptance_template.json` | docs/review_packets/validation_package.md<br>docs/validation_strategy_readiness_packet.md<br>data/validation/validation_review_packet.csv<br>data/validation/validation_strategy_readiness_packet.csv | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| sensitivity_analysis | Sensitivity Analysis Review Agent | `data/manifests/sensitivity_acceptance.json` | `blocked` | `data/manifests/acceptance_templates/sensitivity_acceptance_template.json` | docs/review_packets/sensitivity_analysis.md<br>data/validation/sensitivity_review_packet.csv | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| full_experiment_output | Full Experiment Package Agent | `data/manifests/experiment_acceptance.json` | `blocked` | `data/manifests/acceptance_templates/experiment_acceptance_template.json` | docs/review_packets/full_experiment_output.md | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| manuscript_report_alignment | Paper / Report Claim Alignment Agent | `data/manifests/manuscript_acceptance.json` | `blocked` | `data/manifests/acceptance_templates/manuscript_acceptance_template.json` | docs/review_packets/manuscript_report_alignment.md | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| reproducibility | Clean-Checkout Reproducibility Agent | `data/manifests/reproducibility_acceptance.json` | `blocked` | `data/manifests/acceptance_templates/reproducibility_acceptance_template.json` | docs/review_packets/reproducibility.md<br>data/validation/reproducibility_review_packet.csv | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| final_audit_document | Final Independent Audit Agent | `docs/final_study_audit.md` | `blocked` | `docs/human_acceptance_runbook.md` | docs/review_packets/final_audit.md | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |
| final_audit | Final Independent Audit Agent | `data/manifests/final_audit_acceptance.json` | `blocked` | `data/manifests/acceptance_templates/final_audit_acceptance_template.json` | docs/review_packets/final_audit.md | .\.venv\Scripts\python scripts\validate_formal_acceptance_package.py |

## Use

Use this matrix as the reviewer intake index. The matrix tells reviewers which packets, templates, paths, and commands belong to each formal target. It must not be copied into a formal acceptance path and cannot make the active goal complete.

The graph-scale and validation strategy-readiness packets listed above are
latest blocker-detail inputs. They do not close
`data/manifests/graph_scale_acceptance.json` or
`data/manifests/validation_acceptance.json`.
