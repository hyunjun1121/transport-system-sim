# Experiment Output Acceptance Schema

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


## Purpose

`data/manifests/experiment_acceptance.json` is the explicit review record that
can close the final-study full-experiment-output gate.

Generated pilot rows are reproducible scaffold outputs by default. They become
final-study evidence only after graph scope, input validation, scenario-policy
design, common-random-number pairing, row counts, and claim boundaries are
reviewed together.

Do not create this file to make audits pass. Create it only after a real review
accepts the experiment package for a quasi-real decision-support study.

## Location

```text
data/manifests/experiment_acceptance.json
```

The current scaffold intentionally does not include this file.

## Required Fields

| Field | Type | Requirement |
| --- | --- | --- |
| `region_id` | string | Non-empty pilot region identifier. |
| `accepted` | boolean | Must be `true` only after review. |
| `accepted_by` | string | Reviewer, group, or decision record identifier. |
| `accepted_date` | string | Review date in `YYYY-MM-DD` form where possible. |
| `run_profile` | string | One of `staged_pilot`, `full_pilot`, or `multi_corridor_full_pilot`. |
| `expected_row_count` | integer | Positive raw output row count accepted for the run profile. |
| `expected_summary_row_count` | integer | Positive grouped summary row count accepted for the run profile. |
| `policy_count` | integer | Positive number of accepted policy alternatives. |
| `scenario_count` | integer | Positive number of accepted disruption scenarios. |
| `seed_count` | integer | Positive number of accepted common-random-number seeds. |
| `graph_scope_accepted` | boolean | Must be `true` after graph-scale review. |
| `input_validation_accepted` | boolean | Must be `true` after input and validation package review. |
| `scenario_policy_seed_design_reviewed` | boolean | Must be `true` after design review. |
| `common_random_numbers_reviewed` | boolean | Must be `true` after CRN pairing review. |
| `claim_boundary` | string | Must include `not operational`. |
| `evidence_paths` | array of strings | Non-empty list of result manifests, CSVs, tables, and review notes. |

## Example Shape

```json
{
  "region_id": "songpa_public_demo",
  "accepted": true,
  "accepted_by": "review record id",
  "accepted_date": "2026-05-04",
  "run_profile": "full_pilot",
  "expected_row_count": 1890,
  "expected_summary_row_count": 63,
  "policy_count": 7,
  "scenario_count": 9,
  "seed_count": 30,
  "graph_scope_accepted": true,
  "input_validation_accepted": true,
  "scenario_policy_seed_design_reviewed": true,
  "common_random_numbers_reviewed": true,
  "claim_boundary": "Accepted for quasi-real decision-support analysis; not operational routing.",
  "evidence_paths": [
    "results/realworld_pilot/pilot_full_results.csv",
    "results/realworld_pilot/pilot_full_summary.csv",
    "results/realworld_pilot/pilot_full_manifest.json",
    "docs/final_study_audit.md"
  ]
}
```

This example is a schema illustration only. It is not evidence that the current
pilot outputs are calibrated or accepted.

## Validation

The schema is enforced by:

```powershell
.\.venv\Scripts\python tests\test_realworld_experiment_acceptance.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

The final-study readiness audit also checks that accepted counts match the
current pilot full manifest. A stale or mismatched acceptance record must keep
the full-experiment-output gate blocked.
