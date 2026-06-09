# Road Override Field-Source Hardening - 2026-06-08

## Scope

This ledger records a blocker-hardening change for road-class override evidence.
It does not close road evidence, cached OSM input, publication, or final-study
gates.

## Reviewer Wave

- `019ea59b-5ad7-7191-8959-2c1338c9e167`: rejected creation of
  `data/parameters/road_class_overrides.csv` from current evidence.
- `019ea59b-9cd6-7cd1-92e8-9c64e81a94f9`: rejected source-backed treatment for
  current road speed, capacity, and base-disruption values.

Both reviewers identified the same blocker: current speed, capacity, and
base-disruption values are still draft, proxy, or sensitivity/scenario values.

## Edits Made

- `src/realworld/road_overrides.py`
  - Added optional field-level source columns for speed, capacity, and
    base-disruption values.
  - Preserved backward compatibility: old tables without these columns inherit
    the row-level source fields.
- `src/realworld/road_override_audit.py`
  - Added field-level source-class counts.
  - Blocks publication readiness when any speed, capacity, or base-disruption
    field remains `expert assumption` or `sensitivity-only`, even if the row
    source class is strong.
  - Exposes draft field-source counts and weak-field count.
- `src/realworld/road_override_template.py`
  - Added field-level source columns to future draft override templates.
  - Marks draft base-disruption values as `sensitivity-only`.
- `tests/test_realworld_road_override_audit.py`
  - Added a regression test proving a strong row source cannot hide a weak
    field-level `base_p_fail` source.
- `data/parameters/road_class_overrides_draft.csv`
  - Regenerated as a draft worksheet with field-level source columns.

## Commands Run

```powershell
.\.venv\Scripts\python tests\test_realworld_road_overrides.py
.\.venv\Scripts\python tests\test_realworld_road_override_template.py
.\.venv\Scripts\python tests\test_realworld_road_override_audit.py
.\.venv\Scripts\python scripts\audit_road_overrides.py
.\.venv\Scripts\python scripts\write_road_class_override_template.py --output data\parameters\road_class_overrides_draft.csv --overwrite
```

All listed tests passed. The audit still reports `publication_ready=false`
because the reviewed canonical `data/parameters/road_class_overrides.csv` is
absent and no accepted pilot manifest records override application.

## Remaining Blockers

- Do not create `data/parameters/road_class_overrides.csv` from the current
  draft worksheet.
- Source-backed or benchmark-calibrated evidence is still needed for road speed
  and capacity if those values are to support final claims.
- Base-disruption probabilities need hazard, incident, literature, or formal
  scenario-only treatment. Until then, they remain sensitivity/scenario inputs.
- Even after a reviewed override table exists, a pilot/full result manifest must
  prove the table was applied by recording path, SHA256, and
  `road_class_overrides_applied=true`.

## Decision

Gate closure remains rejected. The implemented change reduces overclaim risk and
makes future review more granular.
