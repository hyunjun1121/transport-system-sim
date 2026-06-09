# Road Override Source Candidate - 2026-06-08

## Scope

Created a non-formal road-class override source-candidate packet from the
current draft road override worksheet. This work supports reviewer triage only.
It does not create reviewed road-class overrides, publication readiness,
final-study readiness, formal acceptance evidence, or operational routing
evidence.

## Sub-Agent Reviews

- `019ea5f2-5c9a-7d71-af8f-63e1bbbfa35c`
  - Role: evidence/provenance reviewer.
  - Inspected `plan.md`, `docs/schemas/road_class_override_schema.md`,
    `src/realworld/road_overrides.py`,
    `src/realworld/road_override_audit.py`,
    `scripts/write_road_class_override_template.py`,
    `tests/test_realworld_road_override_audit.py`, and
    `data/parameters/road_class_overrides_draft.csv`.
  - Recommendation: a separate source-candidate packet is dependency-safe only
    if it is not written to `data/parameters/road_class_overrides.csv`, not used
    as accepted pilot input, and keeps official row/field source classes weak
    until review.
- `019ea5f2-8f31-7a30-a94f-32675b0c437c`
  - Role: adversarial claim-boundary reviewer.
  - Inspected `plan.md`, `status.md`,
    `docs/schemas/road_class_override_schema.md`,
    `src/realworld/road_override_audit.py`,
    `data/parameters/road_class_overrides_draft.csv`,
    `src/realworld/publication_readiness.py`,
    publication/final/formal readiness docs, and formal acceptance guard docs.
  - Recommendation: do not write formal target paths during this step,
    especially `data/parameters/road_class_overrides.csv`,
    `data/parameters/parameter_acceptance.csv`,
    acceptance JSON files, or `docs/final_study_audit.md`.

## External Sources Consulted

- Korean road speed-limit bounds:
  - `https://www.law.go.kr/LSW/lsPdfPrint.do?ancYnChk=0&bylChaChk=N&efGubun=Y&efYd=20220420&joAllCheck=Y&joEfOutPutYn=on&lsiSeq=241893&mokChaChk=N`
  - `https://www.easylaw.go.kr/CSP/IssueQaRetrieve.laf?issueqaSeq=110&targetRow=221&topMenu=openUl7`
- FHWA/HCM-derived roadway capacity proxy references:
  - `https://www.fhwa.dot.gov/ohim/hpmsmanl/appn1.cfm`
  - `https://www.fhwa.dot.gov/ohim/hpmsmanl/appn7.cfm`

These sources are candidate constraints only. The packet does not claim Korean
road-class calibration, observed traffic calibration, or accepted disruption
probability evidence.

## Files Added

- `src/realworld/road_override_source_candidate.py`
- `scripts/write_road_class_override_source_candidate.py`
- `tests/test_realworld_road_override_source_candidate.py`
- `data/parameters/road_class_override_source_candidate.csv`
- `data/parameters/road_class_override_source_candidate_manifest.json`
- `docs/road_class_override_source_candidate.md`

## Generated Manifest

`data/parameters/road_class_override_source_candidate_manifest.json` reports:

- `row_count=10`
- `candidate_table_present=true`
- `reviewed_override_table_present=false`
- `formal_target_path=data/parameters/road_class_overrides.csv`
- `formal_target_written=false`
- `formal_acceptance_evidence=false`
- `publication_ready=false`
- `final_study_ready=false`
- `can_support_road_evidence_gate=false`
- `can_support_road_application_gate=false`
- `road_class_overrides_applied=false`
- `graph_source_records_override=false`

Field-level candidate source counts:

- speed candidate: `public-data-derived=10`
- capacity candidate: `literature-derived=10`
- base disruption candidate: `sensitivity-only=10`

Official row/field source values from the draft remain weak and are preserved
as traceability fields.

## Commands Run

```powershell
.\.venv\Scripts\python scripts\write_road_class_override_source_candidate.py
Test-Path data\parameters\road_class_overrides.csv
Test-Path data\parameters\parameter_acceptance.csv
Test-Path data\manifests\pilot_acceptance.json
Test-Path docs\final_study_audit.md
.\.venv\Scripts\python tests\test_realworld_road_override_source_candidate.py
.\.venv\Scripts\python tests\test_realworld_road_override_audit.py
.\.venv\Scripts\python tests\test_realworld_road_overrides.py
.\.venv\Scripts\python tests\test_realworld_road_source_readiness_packet.py
.\.venv\Scripts\python scripts\audit_road_overrides.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

Results:

- All four targeted test files passed.
- The four checked formal target paths returned `False`.
- Road override audit still reports `publication_ready=false`.
- Publication audit still reports `publication_ready=false`, `1/10` ready gates.
- Final-study audit still reports `final_study_ready=false`, with 12 blocked
  gates.

## Gate Impact

- Promoted phases: none.
- Closed gates: none.
- New evidence: source-candidate triage packet for road override review.
- Remaining blockers:
  - reviewed `data/parameters/road_class_overrides.csv` is absent;
  - road capacity needs Korean agency, traffic-count, or benchmark-calibrated
    evidence where final claims require calibration;
  - base disruption probabilities remain sensitivity-only;
  - accepted pilot/full outputs still do not record override application by
    path, SHA256, and `road_class_overrides_applied=true`;
  - publication, final-study, and formal acceptance gates remain blocked.

## Next Dependency-Safe Work

The highest-value next step is to resolve a different upstream evidence gap
without touching formal targets: rail timing/source evidence or parameter-source
decision triage. Do not rerun Phase 9 full experiments until upstream road,
rail, parameter, provenance, validation, and graph-scale blockers are resolved.
