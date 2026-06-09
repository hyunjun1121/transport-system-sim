# Formal Decision Package Intake Audit

This package checks reviewer-supplied formal decision artifacts. It does not create approvals, invent evidence, or convert scaffold outputs into field-fit findings.

## Verdict

- Formal acceptance ready: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- Ready formal gates: 0 / 12
- Invalid formal gates: 0

## Gate Intake

| Gate | Status | Artifact | Blockers |
| --- | --- | --- | --- |
| Pilot Region Decision | blocked | `data/manifests/pilot_acceptance.json` | create an explicit pilot acceptance record after privacy and case-scope review |
| Graph-Scale Decision | blocked | `data/manifests/graph_scale_acceptance.json` | create an explicit graph-scale acceptance record after source-vs-analysis graph review |
| Source/License/Provenance Decision | blocked | `data/manifests/provenance_acceptance.json` | create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review |
| Weak-Parameter Decision | blocked | `data/parameters/parameter_acceptance.csv` | create reviewed parameter acceptance records only for weak assumptions retained in final claims<br>parameter_acceptance.csv is missing |
| Road-Class Override Decision | blocked | `data/parameters/road_class_overrides.csv` | replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence<br>apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs<br>reviewed road-class override table is absent |
| Benchmark Decision | blocked | `data/manifests/validation_acceptance.json` | create an explicit validation acceptance record after benchmark-strategy review |
| Sensitivity Analysis Decision | blocked | `data/manifests/sensitivity_acceptance.json` | create an explicit sensitivity acceptance record after SALib output and Sobol-decision review |
| Experiment Output Decision | blocked | `data/manifests/experiment_acceptance.json` | create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review |
| Manuscript/Report Alignment Decision | blocked | `data/manifests/manuscript_acceptance.json` | create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed |
| Reproducibility Decision | blocked | `data/manifests/reproducibility_acceptance.json` | create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks |
| Study-Closeout Audit Document | blocked | `docs/final_study_audit.md` | create docs/final_study_audit.md after all other gates close |
| Closeout Audit Decision | blocked | `data/manifests/final_audit_acceptance.json` | create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed |

## Guard Summary

- Formal artifacts present: 0 / 12
- Missing formal artifacts: 12
- Template or placeholder artifacts detected: 0
- Guard can mark complete: `false`

## Evidence Path Summary

- Evidence items: 0
- Missing local evidence: 0
- Placeholder evidence values: 0
- Empty evidence records: 0
- Evidence-path audit can mark complete: `false`

## Study-Closeout Cross-Check

- Study-closeout verdict: `study_closeout_blocked`
- Ready plan gates: 3 / 15
- Blocked plan gates: 12 / 15

## Use

Run this audit after a reviewer adds or edits any formal decision artifact. A `ready` package only means the repository has reviewer-checked decision evidence; it still must agree with the study-closeout readiness audit before the active goal can be marked complete.
