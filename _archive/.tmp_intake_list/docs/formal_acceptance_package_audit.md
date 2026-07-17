# Formal Acceptance Package Audit

This package validates formal acceptance artifacts supplied by reviewers. It does not create approvals, invent evidence, or convert scaffold outputs into calibrated real-world findings.

## Verdict

- Formal acceptance ready: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- Ready formal gates: 0 / 12
- Invalid formal gates: 0

## Gate Intake

| Gate | Status | Artifact | Blockers |
| --- | --- | --- | --- |
| Pilot Region Acceptance | blocked | `data/manifests/pilot_acceptance.json` | create an explicit pilot acceptance record after privacy and case-scope review |
| Graph-Scale Acceptance | blocked | `data/manifests/graph_scale_acceptance.json` | create an explicit graph-scale acceptance record after source-vs-analysis graph review |
| Source/License/Provenance Acceptance | blocked | `data/manifests/provenance_acceptance.json` | create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review |
| Weak-Parameter Acceptance | blocked | `data/parameters/parameter_acceptance.csv` | create reviewed parameter acceptance records only for weak assumptions retained in final claims<br>parameter_acceptance.csv is missing |
| Road-Class Override Acceptance | blocked | `data/parameters/road_class_overrides.csv` | replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence<br>apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs<br>reviewed road-class override table is absent |
| Validation Acceptance | blocked | `data/manifests/validation_acceptance.json` | create an explicit validation acceptance record after benchmark-strategy review |
| Sensitivity Acceptance | blocked | `data/manifests/sensitivity_acceptance.json` | create an explicit sensitivity acceptance record after SALib output and Sobol-decision review |
| Experiment Acceptance | blocked | `data/manifests/experiment_acceptance.json` | create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review |
| Manuscript/Report Acceptance | blocked | `data/manifests/manuscript_acceptance.json` | create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed |
| Reproducibility Acceptance | blocked | `data/manifests/reproducibility_acceptance.json` | create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks |
| Final Study Audit Document | blocked | `docs/final_study_audit.md` | create docs/final_study_audit.md after all other gates close |
| Final Audit Acceptance | blocked | `data/manifests/final_audit_acceptance.json` | create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed |

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

## Final Readiness Cross-Check

- Final-study verdict: `final_real_world_study_blocked`
- Ready plan gates: 3 / 15
- Blocked plan gates: 12 / 15

## Use

Run this audit after a reviewer adds or edits any formal acceptance artifact. A `ready` package only means the repository has reviewed acceptance evidence; it still must agree with the final-study readiness audit before the active goal can be marked complete.
