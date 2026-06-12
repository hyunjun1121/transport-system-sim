# Reviewer Task Assignments

Sub-agent task assignments only. These rows assign review work; they do not approve evidence, certify licenses, validate calibration, or close final-study gates.

## Summary

- Tasks: 18
- Assigned agents: 10
- Formal decision ready: `false`
- Study-closeout ready: `false`
- Can mark complete: `false`
- CSV: `data/manifests/acceptance_task_assignments.csv`

## Assignments

| Task | Gate | Agent | Action Type | Formal Target | Required Output |
| --- | --- | --- | --- | --- | --- |
| acceptance_task_001 | pilot_region_accepted | Pilot Region & Privacy Review Agent | create_or_supply_formal_evidence | `data/manifests/pilot_acceptance.json` | reviewed JSON decision record with real evidence paths |
| acceptance_task_002 | graph_scale_strategy | Graph Scale Method Review Agent | create_or_supply_formal_evidence | `data/manifests/graph_scale_acceptance.json` | reviewed JSON decision record with real evidence paths |
| acceptance_task_003 | data_provenance | OSM / Source / License / Provenance Review Agent | create_or_supply_formal_evidence | `data/manifests/provenance_acceptance.json` | reviewed JSON decision record with real evidence paths |
| acceptance_task_004 | parameter_acceptance | Road / Rail / Parameter Evidence Agent | create_or_supply_formal_evidence | `data/parameters/parameter_acceptance.csv` | reviewed CSV rows with source-backed or explicitly retained values |
| acceptance_task_005 | parameter_acceptance | Road / Rail / Parameter Evidence Agent | create_or_supply_formal_evidence | `data/parameters/parameter_acceptance.csv` | reviewed CSV rows with source-backed or explicitly retained values |
| acceptance_task_006 | road_class_overrides | Road / Rail / Parameter Evidence Agent | replace_weak_or_scaffold_evidence | `data/parameters/road_class_overrides.csv` | reviewed CSV rows with source-backed or explicitly retained values |
| acceptance_task_007 | road_class_overrides | Road / Rail / Parameter Evidence Agent | apply_reviewed_input_and_regenerate | `data/parameters/road_class_overrides.csv` | reviewed CSV rows with source-backed or explicitly retained values |
| acceptance_task_008 | road_class_overrides | Road / Rail / Parameter Evidence Agent | resolve_blocker | `data/parameters/road_class_overrides.csv` | reviewed CSV rows with source-backed or explicitly retained values |
| acceptance_task_009 | road_class_overrides | Road / Rail / Parameter Evidence Agent | resolve_blocker | `data/parameters/road_class_overrides.csv` | reviewed CSV rows with source-backed or explicitly retained values |
| acceptance_task_010 | road_class_overrides | Road / Rail / Parameter Evidence Agent | resolve_blocker | `data/parameters/road_class_overrides.csv` | reviewed CSV rows with source-backed or explicitly retained values |
| acceptance_task_011 | road_class_overrides | Road / Rail / Parameter Evidence Agent | resolve_blocker | `data/parameters/road_class_overrides.csv` | reviewed CSV rows with source-backed or explicitly retained values |
| acceptance_task_012 | validation_package | Benchmark Strategy Review Agent | create_or_supply_formal_evidence | `data/manifests/validation_acceptance.json` | reviewed JSON decision record with real evidence paths |
| acceptance_task_013 | sensitivity_analysis | Sensitivity Analysis Review Agent | create_or_supply_formal_evidence | `data/manifests/sensitivity_acceptance.json` | reviewed JSON decision record with real evidence paths |
| acceptance_task_014 | full_experiment_output | Full Experiment Package Agent | create_or_supply_formal_evidence | `data/manifests/experiment_acceptance.json` | reviewed JSON decision record with real evidence paths |
| acceptance_task_015 | manuscript_report_alignment | Paper / Report Claim Alignment Agent | create_or_supply_formal_evidence | `data/manifests/manuscript_acceptance.json` | reviewed JSON decision record with real evidence paths |
| acceptance_task_016 | reproducibility | Clean-Checkout Reproducibility Agent | create_or_supply_formal_evidence | `data/manifests/reproducibility_acceptance.json` | reviewed JSON decision record with real evidence paths |
| acceptance_task_017 | final_audit_document | Independent Audit Review Agent | create_or_supply_formal_evidence | `docs/final_study_audit.md` | independent closeout audit document after all prerequisite gates close |
| acceptance_task_018 | final_audit | Independent Audit Review Agent | create_or_supply_formal_evidence | `data/manifests/final_audit_acceptance.json` | reviewed JSON decision record with real evidence paths |

## Use

Use this file to assign human/source-backed review work to the deterministic sub-agent roles. If a task cannot be resolved with evidence, keep the formal target absent or explicitly blocked and rerun the audit.
