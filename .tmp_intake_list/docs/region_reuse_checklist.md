# Region Reuse Checklist

> Current project status (2026-05-08): `final_study_ready=false`. This
> checklist is implementation guidance only; it does not create an accepted
> second case study, calibrated evidence, or operational routing authority.

Use this checklist when adding a new public or synthetic region to the
real-world input pipeline.

## Required Region Inputs

Create a new region spec, for example:

```text
data/regions/<region_id>.yaml
```

The spec must include:

- `region_id` that is unique across the package
- bbox `boundary`
- assembly zone `A`
- destination zone `D`
- rail access point `S`
- rail egress point `R`
- fixed rail timing placeholders or reviewed rail evidence values
- coordinate metadata that labels each point as public, synthetic, aggregated,
  or assumption-based

The current adapter uses canonical simulator node IDs `A`, `D`, `S`, and `R`;
use those IDs unless the adapter and scenario contracts are deliberately
changed and revalidated.

## Required Companion Artifacts

Duplicate or create region-specific versions of these artifacts:

- data card under `docs/`
- road graph cache and cache manifest under `data/cache/`
- road evidence review rows and any reviewed road-class overrides
- parameter-source rows for demand, fleet, dispatch, transfer, traffic, BPR,
  disruption, and censoring assumptions
- rail station binding, timetable, GTFS, shortest-path, capacity, or
  sensitivity-only evidence rows
- disruption scenario rows and policy alternative rows with the new
  `region_id`
- validation, graph-scale, experiment, sensitivity, figure/table, and
  reproducibility outputs scoped to the new region

Do not copy formal acceptance artifacts from another region. Pilot,
provenance, graph-scale, parameter, rail, validation, sensitivity, experiment,
manuscript, reproducibility, and final-audit acceptance decisions remain
region- and evidence-specific.

## Current Fixture Coverage

`tests/fixtures/synthetic_region_fixture.yaml` and
`tests/test_realworld_region_reusability.py` provide a second synthetic region
fixture. The test loads the fixture, adapts an independent OSM-like graph,
checks road-mode routeability, and verifies rail metadata mapping without
changing production code.

This proves schema and adapter reusability only. It is not a second accepted
pilot, not source-backed validation, and not publication-grade evidence.

## Validation Commands

Run at minimum:

```powershell
.\.venv\Scripts\python tests\test_realworld_region_reusability.py
.\.venv\Scripts\python tests\test_realworld_types.py
.\.venv\Scripts\python tests\test_realworld_adapter.py
```

The cached smoke CLIs accept explicit region and cache paths:

```powershell
.\.venv\Scripts\python scripts\run_pilot_smoke.py --region data\regions\<region_id>.yaml --cache data\cache\<region_id>_road.graphml
.\.venv\Scripts\python scripts\run_full_graph_smoke.py --region-path data\regions\<region_id>.yaml --cache-path data\cache\<region_id>_road.graphml --no-write
```

Source-request worksheet generators also accept explicit region IDs when
creating region-scoped review aids:

```powershell
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py --region-id <region_id>
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py --region-id <region_id>
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py --cache-prefix <region_id>
```

The downstream parameter, road, and rail source-readiness manifests expose the
`region_ids` found in those request rows. Check those manifest fields before
mixing review packets from multiple regions.

For rail timing, pass `--station-bindings <region_station_bindings.csv>` when
using a non-pilot binding table; the generated headway and shortest-path
derivation commands will reference that same binding file.

For a publication-bound region, also rerun the full validation ladder listed
in `plan.md` and keep formal acceptance artifacts absent until reviewed
source-backed decisions are supplied.
