# Road Class Override Schema

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This schema defines the optional reviewed CSV expected by
`src/realworld/road_overrides.py`. The file is intentionally not committed in
the current scaffold because no reviewed road speed, capacity, or
base-disruption evidence package has been accepted yet.

If final-study claims require calibrated or source-backed road inputs, create:

```text
data/parameters/road_class_overrides.csv
```

Then rerun:

```powershell
.\.venv\Scripts\python scripts\audit_road_overrides.py
.\.venv\Scripts\python scripts\audit_road_evidence.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
```

The override table only proves that reviewed fallback values exist. It does
not prove that a result graph was built with those values. Any experiment that
uses the table must record the applied override path and source digest in its
manifest before final road-calibration claims are made.
The road override audit now checks both parts: source strength of the override
rows and whether the accepted pilot manifest records that the same table was
applied with a matching SHA256 digest.

To prepare a non-acceptance draft from the current cached-road diagnostics,
run:

```powershell
.\.venv\Scripts\python scripts\write_road_class_override_template.py --output data\parameters\road_class_overrides_draft.csv --overwrite
```

This draft intentionally mirrors the current mapper defaults and marks rows as
`expert assumption`. It is a review worksheet only. Do not rename it to
`road_class_overrides.csv` or apply it to final results until reviewers replace
the values and source fields with public, literature, agency, benchmark, or
accepted scenario evidence.

To apply a reviewed table to a pilot experiment run, pass it explicitly:

```powershell
.\.venv\Scripts\python scripts\run_pilot_experiments.py --sample --road-class-overrides-path data\parameters\road_class_overrides.csv
```

The pilot manifest records `road_class_overrides_applied: true`,
`inputs.road_class_overrides_path`,
`inputs.road_class_overrides_sha256`, and a `graph_source` suffix when the
table is supplied. Default scaffold runs still do not apply an override table.

## Required Columns

| Column | Meaning |
| --- | --- |
| `highway` | OSM highway class known to `src/realworld/attributes.py`, for example `primary`, `secondary`, `tertiary`, or `residential`. |
| `speed_kph` | Reviewed free-flow speed in kilometers per hour. |
| `capacity_veh_per_hr` | Reviewed directional capacity proxy in vehicles per hour for BPR-style mesoscopic modeling. |
| `base_p_fail` | Reviewed or accepted scenario base disruption probability, between 0 and 1. |
| `source_class` | One of the project source classes: `public-data-derived`, `literature-derived`, `agency/timetable-derived`, `benchmark-calibrated`, `expert assumption`, or `sensitivity-only`. |
| `source_name` | Human-readable source name. |
| `source_url_or_citation` | Public URL, document citation, or accepted internal evidence note. |
| `notes` | Transformation notes, assumptions, and claim limits. |

Rows with `expert assumption` or `sensitivity-only` remain weak for final
claims. They can be useful for scenario sweeps, but they should not be used to
claim calibrated road performance.

## Example Shape

```csv
highway,speed_kph,capacity_veh_per_hr,base_p_fail,source_class,source_name,source_url_or_citation,notes
primary,50,1800,0.01,benchmark-calibrated,accepted benchmark calibration,docs/source_note.md,Example only; replace with reviewed evidence before use.
```

Do not copy this example into `data/parameters/road_class_overrides.csv` as
evidence. It is a schema illustration, not a reviewed source.
