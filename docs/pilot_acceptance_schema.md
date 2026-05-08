# Pilot Acceptance Schema

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


The final study must not treat the existence of `pilot_region.yaml` and the
pilot data card as human acceptance of the case design. If the pilot case is
accepted for final-study claims, record that decision in:

```text
data/manifests/pilot_acceptance.json
```

This file is intentionally absent in the current scaffold. Its absence keeps
`scripts/audit_final_study_readiness.py` blocked.

## Required Fields

| Field | Meaning |
| --- | --- |
| `region_id` | Region ID, for example `songpa_public_demo`. |
| `accepted` | Boolean; must be `true` only after human review. |
| `accepted_by` | Reviewer, team, or role that accepted the pilot scope. |
| `accepted_date` | Acceptance date in ISO-style date text. |
| `acceptance_scope` | What is accepted: region, privacy treatment, graph scale, evidence boundary, and result-use scope. |
| `privacy_review_complete` | Boolean confirming exact sensitive destinations are public, synthetic, aggregated, or otherwise approved. |
| `graph_scale_decision` | One of `corridor_abstraction`, `full_graph_runtime`, or `multi_corridor_ensemble`. |
| `claim_boundary` | Must explicitly state that the accepted case is not operational routing. |
| `evidence_paths` | List of files that support the acceptance decision. |

## Example Shape

```json
{
  "region_id": "songpa_public_demo",
  "accepted": true,
  "accepted_by": "reviewer role or team",
  "accepted_date": "2026-05-04",
  "acceptance_scope": "Accepted as a quasi-real corridor-based decision-support pilot after privacy and graph-scale review.",
  "privacy_review_complete": true,
  "graph_scale_decision": "corridor_abstraction",
  "claim_boundary": "Accepted for research decision support; not operational routing.",
  "evidence_paths": [
    "data/regions/pilot_region.yaml",
    "docs/pilot_region_data_card.md",
    "docs/analysis_corridor_method_note.md"
  ]
}
```

Do not add this file with placeholder approval. A passing acceptance record
should represent an actual review decision, not a way to satisfy tests.

## Validation

```powershell
.\.venv\Scripts\python tests\test_realworld_pilot_acceptance.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```
