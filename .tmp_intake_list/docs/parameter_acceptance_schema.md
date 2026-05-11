# Parameter Acceptance Schema

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


The parameter-source tables may retain expert assumptions or sensitivity-only
values when stronger public, literature, agency, timetable, or benchmark
evidence is unavailable. Those weak rows should not support final claims unless
they are either replaced by stronger evidence or explicitly accepted within a
conservative claim boundary.

If reviewers decide to retain weak assumptions in the final study, record that
decision in:

```text
data/parameters/parameter_acceptance.csv
```

This file is intentionally absent in the current scaffold. Its absence keeps
the parameter evidence gate blocked.

## Required Columns

| Column | Meaning |
| --- | --- |
| `parameter` | Parameter name from the source tables. |
| `accepted` | `true` only after review. |
| `accepted_by` | Reviewer, team, or role that accepted the weak parameter. |
| `accepted_date` | Acceptance date. |
| `acceptance_scope` | Why the weak assumption is acceptable for the bounded study. |
| `claim_boundary` | Must explicitly state that the parameter is not accepted for operational routing. |
| `sensitivity_reviewed` | `true` only if uncertainty or sensitivity coverage was reviewed. |
| `evidence_paths` | Semicolon-separated files supporting the acceptance decision. |
| `notes` | Additional caveats or transformation notes. |

## Example Shape

```csv
parameter,accepted,accepted_by,accepted_date,acceptance_scope,claim_boundary,sensitivity_reviewed,evidence_paths,notes
road_capacity_proxy,true,reviewer role,2026-05-04,Accepted for bounded corridor sensitivity only,Accepted for decision-support sensitivity analysis; not operational routing.,true,data/parameters/parameter_sources.csv;docs/analysis_corridor_method_note.md,Example only; replace with real review before final claims.
```

Do not add this file with placeholder approvals. A passing acceptance record
should represent a real review decision.

## Validation

```powershell
.\.venv\Scripts\python tests\test_realworld_parameter_acceptance.py
.\.venv\Scripts\python scripts\audit_parameter_evidence.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```
