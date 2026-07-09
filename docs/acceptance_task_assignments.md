# Reviewer Task Assignments

Sub-agent task assignments only. These rows assign review work; they do not approve evidence, certify licenses, validate calibration, or close final-study gates.

## Summary

- Tasks: 2
- Assigned agents: 2
- Formal decision ready: `false`
- Study-closeout ready: `false`
- Can mark complete: `false`
- CSV: `data/manifests/acceptance_task_assignments.csv`

## Assignments

| Task | Gate | Agent | Action Type | Formal Target | Required Output |
| --- | --- | --- | --- | --- | --- |
| acceptance_task_001 | road_class_overrides | Road / Rail / Parameter Evidence Agent | apply_reviewed_input_and_regenerate | `data/parameters/road_class_overrides.csv` | reviewed CSV rows with source-backed or explicitly retained values |
| acceptance_task_002 | final_audit_document | Independent Audit Review Agent | resolve_blocker | `docs/final_study_audit.md` | independent closeout audit document after all prerequisite gates close |

## Use

Use this file to assign human/source-backed review work to the deterministic sub-agent roles. If a task cannot be resolved with evidence, keep the formal target absent or explicitly blocked and rerun the audit.
