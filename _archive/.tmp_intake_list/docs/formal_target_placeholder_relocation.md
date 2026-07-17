# Formal Target Placeholder Relocation

Date: 2026-05-10

This note records a formal-artifact hygiene action. Placeholder or blocker-state
files that had occupied final acceptance target paths were moved to draft
storage so final target paths cannot be mistaken for reviewed approvals.

Moved JSON placeholders:

- `data/manifests/pilot_acceptance.json` -> `data/manifests/draft_acceptance/formal_target_placeholders_20260510/pilot_acceptance.placeholder.json`
- `data/manifests/graph_scale_acceptance.json` -> `data/manifests/draft_acceptance/formal_target_placeholders_20260510/graph_scale_acceptance.placeholder.json`
- `data/manifests/provenance_acceptance.json` -> `data/manifests/draft_acceptance/formal_target_placeholders_20260510/provenance_acceptance.placeholder.json`
- `data/manifests/validation_acceptance.json` -> `data/manifests/draft_acceptance/formal_target_placeholders_20260510/validation_acceptance.placeholder.json`
- `data/manifests/sensitivity_acceptance.json` -> `data/manifests/draft_acceptance/formal_target_placeholders_20260510/sensitivity_acceptance.placeholder.json`
- `data/manifests/experiment_acceptance.json` -> `data/manifests/draft_acceptance/formal_target_placeholders_20260510/experiment_acceptance.placeholder.json`
- `data/manifests/manuscript_acceptance.json` -> `data/manifests/draft_acceptance/formal_target_placeholders_20260510/manuscript_acceptance.placeholder.json`
- `data/manifests/reproducibility_acceptance.json` -> `data/manifests/draft_acceptance/formal_target_placeholders_20260510/reproducibility_acceptance.placeholder.json`
- `data/manifests/final_audit_acceptance.json` -> `data/manifests/draft_acceptance/formal_target_placeholders_20260510/final_audit_acceptance.placeholder.json`

Moved CSV and Markdown placeholders:

- `data/parameters/parameter_acceptance.csv` -> `data/parameters/draft_acceptance/parameter_acceptance.placeholder.csv`
- `data/parameters/road_class_overrides.csv` -> `data/parameters/draft_acceptance/road_class_overrides.placeholder.csv`
- `docs/final_study_audit.md` -> `docs/draft_acceptance/final_study_audit.placeholder.md`

The moved files remain draft/reference material only. They are not formal
acceptance records, reviewed road overrides, accepted parameter records, or a
final-study audit.

After relocation, `scripts/audit_formal_acceptance_artifacts.py` reports:

- formal target files present: 0 / 12
- missing formal target files: 12
- template or placeholder artifacts detected in formal paths: 0
- formal acceptance ready: false

The missing target files should be recreated only when reviewers provide real
source-backed decisions with evidence paths, reviewer identity/date, accepted
scope, and no unresolved placeholder fields.
