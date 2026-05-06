# Acceptance Task Assignments

Sub-agent task assignments only. These rows assign review work; they do not approve evidence, certify licenses, validate calibration, or close final-study gates.

## Summary

- Tasks: 15
- Assigned agents: 10
- Formal acceptance ready: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- CSV: `data/manifests/acceptance_task_assignments.csv`

## Assignments

| Task | Gate | Agent | Action Type | Formal Target | Required Output |
| --- | --- | --- | --- | --- | --- |
| acceptance_task_001 | pilot_region_accepted | Pilot Region & Privacy Review Agent | create_or_supply_formal_evidence | `data/manifests/pilot_acceptance.json` | reviewed JSON acceptance record with real evidence paths |
| acceptance_task_002 | graph_scale_strategy | Graph Scale Method Review Agent | create_or_supply_formal_evidence | `data/manifests/graph_scale_acceptance.json` | reviewed JSON acceptance record with real evidence paths |
| acceptance_task_003 | data_provenance | OSM / Source / License / Provenance Review Agent | create_or_supply_formal_evidence | `data/manifests/provenance_acceptance.json` | reviewed JSON acceptance record with real evidence paths |
| acceptance_task_004 | parameter_acceptance | Road / Rail / Parameter Evidence Agent | create_or_supply_formal_evidence | `data/parameters/parameter_acceptance.csv` | reviewed CSV rows with source-backed or explicitly accepted values |
| acceptance_task_005 | parameter_acceptance | Road / Rail / Parameter Evidence Agent | create_or_supply_formal_evidence | `data/parameters/parameter_acceptance.csv` | reviewed CSV rows with source-backed or explicitly accepted values |
| acceptance_task_006 | road_class_overrides | Road / Rail / Parameter Evidence Agent | replace_weak_or_scaffold_evidence | `data/parameters/road_class_overrides.csv` | reviewed CSV rows with source-backed or explicitly accepted values |
| acceptance_task_007 | road_class_overrides | Road / Rail / Parameter Evidence Agent | apply_reviewed_input_and_regenerate | `data/parameters/road_class_overrides.csv` | reviewed CSV rows with source-backed or explicitly accepted values |
| acceptance_task_008 | road_class_overrides | Road / Rail / Parameter Evidence Agent | create_or_supply_formal_evidence | `data/parameters/road_class_overrides.csv` | reviewed CSV rows with source-backed or explicitly accepted values |
| acceptance_task_009 | validation_package | Validation Benchmark Strategy Agent | create_or_supply_formal_evidence | `data/manifests/validation_acceptance.json` | reviewed JSON acceptance record with real evidence paths |
| acceptance_task_010 | sensitivity_analysis | Sensitivity Analysis Review Agent | create_or_supply_formal_evidence | `data/manifests/sensitivity_acceptance.json` | reviewed JSON acceptance record with real evidence paths |
| acceptance_task_011 | full_experiment_output | Full Experiment Package Agent | create_or_supply_formal_evidence | `data/manifests/experiment_acceptance.json` | reviewed JSON acceptance record with real evidence paths |
| acceptance_task_012 | manuscript_report_alignment | Paper / Report Claim Alignment Agent | create_or_supply_formal_evidence | `data/manifests/manuscript_acceptance.json` | reviewed JSON acceptance record with real evidence paths |
| acceptance_task_013 | reproducibility | Clean-Checkout Reproducibility Agent | create_or_supply_formal_evidence | `data/manifests/reproducibility_acceptance.json` | reviewed JSON acceptance record with real evidence paths |
| acceptance_task_014 | final_audit_document | Final Independent Audit Agent | create_or_supply_formal_evidence | `docs/final_study_audit.md` | independent final audit document after all pre-final gates close |
| acceptance_task_015 | final_audit | Final Independent Audit Agent | create_or_supply_formal_evidence | `data/manifests/final_audit_acceptance.json` | reviewed JSON acceptance record with real evidence paths |

## Use

Use this file to assign human/source-backed review work to the deterministic sub-agent roles. If a task cannot be resolved with evidence, keep the formal target absent or explicitly blocked and rerun the audit.
