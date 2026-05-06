# Acceptance Decision Templates

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


TEMPLATE ONLY: this is not approval, not calibrated real-world validation, and not operational routing. Keep accepted false until a reviewer replaces all placeholders and records a source-backed decision.

These files are copy/edit starting points for human reviewers. They are not formal acceptance artifacts and do not close final-study gates.

- Final-study ready at generation: `false`
- JSON templates: 9
- Parameter acceptance template rows: 25
- Formal acceptance ready: 0 / 12
- Formal acceptance artifacts present: 0 / 12
- Can mark complete: `false`

## JSON Templates

| Gate | Template | Formal Target | Current Status |
| --- | --- | --- | --- |
| `pilot_region_accepted` | `data/manifests/acceptance_templates/pilot_acceptance_template.json` | `data/manifests/pilot_acceptance.json` | `blocked` |
| `graph_scale_strategy` | `data/manifests/acceptance_templates/graph_scale_acceptance_template.json` | `data/manifests/graph_scale_acceptance.json` | `blocked` |
| `data_provenance` | `data/manifests/acceptance_templates/provenance_acceptance_template.json` | `data/manifests/provenance_acceptance.json` | `blocked` |
| `validation_package` | `data/manifests/acceptance_templates/validation_acceptance_template.json` | `data/manifests/validation_acceptance.json` | `blocked` |
| `sensitivity_analysis` | `data/manifests/acceptance_templates/sensitivity_acceptance_template.json` | `data/manifests/sensitivity_acceptance.json` | `blocked` |
| `full_experiment_output` | `data/manifests/acceptance_templates/experiment_acceptance_template.json` | `data/manifests/experiment_acceptance.json` | `blocked` |
| `manuscript_report_alignment` | `data/manifests/acceptance_templates/manuscript_acceptance_template.json` | `data/manifests/manuscript_acceptance.json` | `blocked` |
| `reproducibility` | `data/manifests/acceptance_templates/reproducibility_acceptance_template.json` | `data/manifests/reproducibility_acceptance.json` | `blocked` |
| `final_audit` | `data/manifests/acceptance_templates/final_audit_acceptance_template.json` | `data/manifests/final_audit_acceptance.json` | `blocked` |

## Parameter Template

- Template: `data/parameters/parameter_acceptance_template.csv`
- Formal target: `data/parameters/parameter_acceptance.csv`
- Keep `accepted=false` until weak assumptions are reviewed and retained inside a conservative claim boundary.

## Required Use

- Review the corresponding packet in `docs/review_packets/` first.
- Replace every `REVIEW_REQUIRED` placeholder with a real source-backed decision.
- Copy a template to the formal target path only after review.
- Treat `docs/graph_scale_strategy_readiness_packet.md` and
  `docs/validation_strategy_readiness_packet.md` as current blocker-detail
  inputs, not approval records.
- Re-run `scripts/audit_final_study_readiness.py --fail-on-blockers` after formal records are created.
