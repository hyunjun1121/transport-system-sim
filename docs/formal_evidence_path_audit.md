# Formal Evidence Path Audit

This audit checks whether formal target artifacts point to concrete local evidence files or explicit external references. It does not approve the evidence, check license sufficiency, certify calibration, or close final-study gates.

## Verdict

- Formal evidence paths ready: `false`
- Can mark complete: `false`
- Formal artifacts present: 0 / 11
- Evidence items: 0
- Missing local evidence: 0
- Placeholder evidence values: 0

## Artifact Summary

| Artifact | Present | Evidence Items | Blockers |
| --- | --- | --- | --- |
| `data/manifests/pilot_acceptance.json` | false | 0 | none |
| `data/manifests/graph_scale_acceptance.json` | false | 0 | none |
| `data/manifests/provenance_acceptance.json` | false | 0 | none |
| `data/parameters/parameter_acceptance.csv` | false | 0 | none |
| `data/parameters/road_class_overrides.csv` | false | 0 | none |
| `data/manifests/validation_acceptance.json` | false | 0 | none |
| `data/manifests/sensitivity_acceptance.json` | false | 0 | none |
| `data/manifests/experiment_acceptance.json` | false | 0 | none |
| `data/manifests/manuscript_acceptance.json` | false | 0 | none |
| `data/manifests/reproducibility_acceptance.json` | false | 0 | none |
| `data/manifests/final_audit_acceptance.json` | false | 0 | none |

## Use

Run this audit after a reviewer adds or edits formal acceptance artifacts. A clean evidence-path audit is necessary but not sufficient for final study acceptance.
