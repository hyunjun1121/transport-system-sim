# Validation Acceptance Schema

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


Final-study claims require an explicit validation-package decision before
internal route checks, fallback benchmarks, OSRM snapshots, or other route
engine comparisons can be treated as accepted evidence. The current repository
intentionally does not commit this record, so
`scripts/audit_final_study_readiness.py` remains blocked.

Expected path:

```text
data/manifests/validation_acceptance.json
```

## Required Fields

| Field | Meaning |
| --- | --- |
| `region_id` | Pilot region identifier matching the accepted region spec. |
| `accepted` | JSON boolean. Must be `true` for final-study readiness. |
| `accepted_by` | Reviewer or team that accepted the validation strategy. |
| `accepted_date` | Review date. |
| `validation_scope` | Scope of internal, plausibility, and benchmark checks accepted for the study. |
| `benchmark_strategy` | Accepted benchmark approach. See allowed values below. |
| `internal_validation_reviewed` | JSON boolean confirming internal consistency checks were reviewed. |
| `external_plausibility_reviewed` | JSON boolean confirming external plausibility rows were reviewed. |
| `benchmark_validation_reviewed` | JSON boolean confirming benchmark evidence was reviewed. |
| `benchmark_is_not_ground_truth_acknowledged` | JSON boolean confirming benchmark outputs are plausibility checks, not ground truth. |
| `claim_boundary` | Must state that outputs are not operational routing guidance. |
| `evidence_paths` | Non-empty list of validation tables, summaries, scripts, or benchmark artifacts. |

Allowed `benchmark_strategy` values:

- `cached_osrm_snapshot`
- `cached_valhalla_snapshot`
- `cached_r5_or_otp_snapshot`
- `cached_routingpy_snapshot`
- `documented_fallback_plus_cached_external_snapshot`
- `documented_plausibility_only`
- `uxsim_corridor_benchmark`

## Example

```json
{
  "region_id": "songpa_public_demo",
  "accepted": true,
  "accepted_by": "reviewer-name-or-team",
  "accepted_date": "2026-05-04",
  "validation_scope": "Internal route checks plus cached OSRM plausibility benchmark for the accepted pilot graph.",
  "benchmark_strategy": "cached_osrm_snapshot",
  "internal_validation_reviewed": true,
  "external_plausibility_reviewed": true,
  "benchmark_validation_reviewed": true,
  "benchmark_is_not_ground_truth_acknowledged": true,
  "claim_boundary": "Accepted for quasi-real decision-support study; not operational routing.",
  "evidence_paths": [
    "data/validation/validation_summary.md",
    "data/validation/external_route_benchmarks_osrm.csv",
    "data/validation/osrm_route_benchmark_summary.md"
  ]
}
```

## Validation

```powershell
.\.venv\Scripts\python tests\test_realworld_validation_acceptance.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

The final readiness audit should remain blocked until this file exists, the
validation summary is revised out of scaffold/sanity scope after review, and
the other final-study evidence gates are also closed.
