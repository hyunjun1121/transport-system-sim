# Formal Decision Package Intake Audit

This package checks reviewer-supplied formal decision artifacts. It does not create approvals, invent evidence, or convert scaffold outputs into field-fit findings.

## Verdict

- Formal acceptance ready: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- Ready formal gates: 11 / 12
- Invalid formal gates: 0

## Gate Intake

| Gate | Status | Artifact | Blockers |
| --- | --- | --- | --- |
| Pilot Region Decision | ready | `data/manifests/pilot_acceptance.json` | none |
| Graph-Scale Decision | ready | `data/manifests/graph_scale_acceptance.json` | none |
| Source/License/Provenance Decision | ready | `data/manifests/provenance_acceptance.json` | none |
| Weak-Parameter Decision | ready | `data/parameters/parameter_acceptance.csv` | none |
| Road-Class Override Decision | ready | `data/parameters/road_class_overrides.csv` | verify graph-adapter runs apply the reviewed override table before using road-calibration claims |
| Benchmark Decision | ready | `data/manifests/validation_acceptance.json` | none |
| Sensitivity Analysis Decision | ready | `data/manifests/sensitivity_acceptance.json` | none |
| Experiment Output Decision | ready | `data/manifests/experiment_acceptance.json` | none |
| Manuscript/Report Alignment Decision | ready | `data/manifests/manuscript_acceptance.json` | none |
| Reproducibility Decision | ready | `data/manifests/reproducibility_acceptance.json` | none |
| Study-Closeout Audit Document | blocked | `docs/final_study_audit.md` | final study audit document does not state final_study_ready true |
| Closeout Audit Decision | ready | `data/manifests/final_audit_acceptance.json` | none |

## Guard Summary

- Formal artifacts present: 12 / 12
- Missing formal artifacts: 0
- Template or placeholder artifacts detected: 0
- Guard can mark complete: `false`

## Evidence Path Summary

- Evidence items: 110
- Missing local evidence: 0
- Placeholder evidence values: 0
- Empty evidence records: 1
- Evidence-path audit can mark complete: `false`

## Study-Closeout Cross-Check

- Study-closeout verdict: `study_closeout_blocked`
- Ready plan gates: 9 / 15
- Blocked plan gates: 6 / 15

## Use

Run this audit after a reviewer adds or edits any formal decision artifact. A `ready` package only means the repository has reviewer-checked decision evidence; it still must agree with the study-closeout readiness audit before the active goal can be marked complete.
