# Parameter Acceptance Hardening - 2026-06-08

## Scope

This ledger records a blocker-hardening change for weak-parameter acceptance
records. It does not create `data/parameters/parameter_acceptance.csv` and does
not close parameter evidence, publication, or final-study gates.

## Reviewer Evidence

- `019ea5a4-5bc2-7521-b893-3e054272471a`: rejected creating
  `data/parameters/parameter_acceptance.csv` from current evidence.

The reviewer confirmed that current parameter source/readiness/decision packets
are review aids only and cannot approve retained weak assumptions.

## Edits Made

- `src/realworld/parameter_acceptance.py`
  - `accepted_parameter_count` now counts only rows with `accepted=true`, not
    every row in the table.
  - Ready records now require non-placeholder reviewer fields, ISO-like
    `YYYY-MM-DD` dates, a non-placeholder `not operational` claim boundary, and
    at least one evidence path that is not merely a review/readiness/decision
    packet.
- `tests/test_realworld_parameter_acceptance.py`
  - Added tests for placeholder rows, accepted-count semantics, and
    non-approval evidence paths.

## Commands Run

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\parameter_acceptance.py src\realworld\parameter_audit.py
.\.venv\Scripts\python tests\test_realworld_parameter_acceptance.py
.\.venv\Scripts\python tests\test_realworld_parameter_audit.py
.\.venv\Scripts\python scripts\audit_parameter_evidence.py
```

All listed checks passed. The parameter audit still reports
`publication_ready=false`, `accepted_weak_parameter_count=0`, and
`weak_core_parameter_count=25`.

## Remaining Blockers

- Do not create `data/parameters/parameter_acceptance.csv` from the current
  template.
- Weak road, disruption, fleet, rail, transfer, demand, and censoring
  parameters still require source-backed updates, sensitivity-bound exclusion,
  or explicit reviewed weak-assumption acceptance.
- Review/readiness/decision packets remain insufficient as acceptance evidence.

## Decision

Gate closure remains rejected. The implemented change reduces accidental
acceptance risk.
