# Road Attribute Evidence Table

`src/realworld/road_attribute_evidence.py` creates an edge-level review table
for road attributes used by the quasi-real simulation pipeline.

The table is a review aid only. It is not reviewed road calibration, traffic
assignment validation, graph-scale acceptance, or operational routing evidence.
It must not be copied into `data/parameters/road_class_overrides.csv` or any
formal acceptance path without source-backed human review.

## Purpose

The table separates:

- OSM-derived geometry and tags;
- explicit graph fields with source markers;
- mapper fallback proxies;
- lane-based capacity candidates;
- optional routing-engine benchmark fields;
- sensitivity-only disruption probabilities.

This prevents mapper defaults from being mistaken for reviewed road evidence.
In particular, observed OSM lane tags produce a candidate capacity field, but
they do not make the simulator's currently used capacity proxy calibrated or
final-claim-ready.

## Command

```powershell
.\.venv\Scripts\python scripts\write_road_attribute_evidence.py
```

Optional benchmark fields can be supplied only with traceability metadata:

```powershell
.\.venv\Scripts\python scripts\write_road_attribute_evidence.py `
  --benchmark-times-csv data\validation\example_benchmark_times.csv `
  --benchmark-source-label osrm_snapshot `
  --benchmark-snapshot-path data\cache\osrm\example_snapshot.json
```

## Outputs

Default outputs:

- `data/parameters/road_attribute_evidence_table.csv`
- `data/parameters/road_attribute_evidence_manifest.json`

The manifest is intentionally conservative:

- `publication_ready=false`
- `formal_acceptance_created=false`
- `can_mark_complete=false`

## Required Tests

```powershell
.\.venv\Scripts\python tests\test_realworld_attributes.py
.\.venv\Scripts\python tests\test_realworld_road_attribute_evidence.py
.\.venv\Scripts\python tests\test_realworld_road_capacity_evidence.py
.\.venv\Scripts\python tests\test_realworld_road_speed_evidence.py
```

## Claim Boundary

Rows marked `weak_for_final_claim=true` must not support final road claims.
Rows marked `review_ready_candidate` are candidates for human/source review, not
evidence records. Release-scope road claims still require reviewed overrides and
the existing formal review gates.
