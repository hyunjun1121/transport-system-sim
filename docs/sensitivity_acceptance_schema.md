# Sensitivity Acceptance Schema

Final-study claims require an explicit sensitivity-analysis decision before
Morris, Sobol, or deterministic screening outputs can be treated as accepted
evidence. The current repository intentionally does not commit this record, so
`scripts/audit_final_study_readiness.py` remains blocked.

Expected path:

```text
data/manifests/sensitivity_acceptance.json
```

## Required Fields

| Field | Meaning |
| --- | --- |
| `region_id` | Pilot region identifier matching the accepted region spec. |
| `accepted` | JSON boolean. Must be `true` for final-study readiness. |
| `accepted_by` | Reviewer or team that accepted the sensitivity package. |
| `accepted_date` | Review date. |
| `sensitivity_method` | One of `deterministic_oat_screening`, `salib_morris`, `salib_sobol`, or `morris_plus_sobol`. |
| `result_scope` | Scope of the sensitivity outputs accepted for the study. |
| `expected_row_count` / `expected_summary_row_count` | Positive counts that must match the sensitivity manifest. |
| `graph_scope_accepted` | JSON boolean confirming the sensitivity outputs use the accepted graph scope. |
| `parameter_ranges_reviewed` | JSON boolean confirming uncertain parameter ranges were reviewed. |
| `salib_output_reviewed` | JSON boolean confirming the SALib output was reviewed. |
| `nan_or_masked_values_reviewed` | JSON boolean confirming NaN, masked values, or degenerate indices were reviewed. |
| `sobol_requirement_decision` | One of `not_required`, `completed`, or `required_pending`; `required_pending` blocks final readiness. |
| `claim_boundary` | Must state that outputs are not operational routing guidance. |
| `evidence_paths` | Non-empty list of sensitivity outputs, manifests, scripts, or review notes. |

## Example

```json
{
  "region_id": "songpa_public_demo",
  "accepted": true,
  "accepted_by": "reviewer-name-or-team",
  "accepted_date": "2026-05-04",
  "sensitivity_method": "salib_morris",
  "result_scope": "Accepted quasi-real sensitivity output for the final pilot graph and evidence scope.",
  "expected_row_count": 4320,
  "expected_summary_row_count": 7056,
  "graph_scope_accepted": true,
  "parameter_ranges_reviewed": true,
  "salib_output_reviewed": true,
  "nan_or_masked_values_reviewed": true,
  "sobol_requirement_decision": "not_required",
  "claim_boundary": "Accepted for quasi-real decision-support study; not operational routing.",
  "evidence_paths": [
    "results/realworld_pilot/morris_results.csv",
    "results/realworld_pilot/morris_summary.csv",
    "results/realworld_pilot/morris_manifest.json"
  ]
}
```

## Validation

```powershell
.\.venv\Scripts\python tests\test_realworld_sensitivity_acceptance.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

The final readiness audit should remain blocked until this file exists, the
sensitivity manifest is revised out of scaffold/not-calibrated scope after
review, and the other final-study evidence gates are also closed.
