# Rail Evidence Notes

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This note documents the current rail assumptions for `songpa_public_demo`.
It does not certify emergency rail availability or a calibrated passenger
itinerary.

## Current Model Values

The simulator still uses the fixed rail fields in
`data/regions/pilot_region.yaml`:

| Field | Current value | Status |
| --- | ---: | --- |
| Access point | `S` near Olympic Park Station | public station-area point |
| Egress point | `R` near Jamsil Station | public station-area point |
| Headway | 10 min | timetable-informed assumption |
| Travel time | 20 min | timetable and shortest-path informed assumption |
| Capacity | 500 pax/train | de-rated sensitivity value |

These values are appropriate for quasi-real decision-support scenarios and
smoke/sample experiments only. They should be replaced by a cached timetable or
GTFS-derived extract before publication-grade service claims.

## Source Review

Checked on 2026-05-04:

- Seoul Data Hub provides line-by-station information for Seoul Metro lines
  1-8 and Line 9 phases 2-3:
  <https://data.seoul.go.kr/bsp/wgs/dataView/data300View/10104.do>.
- Seoul Open Data describes subway station information sources delivered
  through Sheet OpenAPI and File formats:
  <https://data.seoul.go.kr/dataList/32/literacyView.do>.
- Seoul Open Data Plaza provides the station-name subway search API used for
  the cached station-code binding rows:
  <https://data.seoul.go.kr/dataList/OA-121/S/1/datasetView.do>.
- The Korean public data portal lists a Seoul Subway train-schedule REST API
  with station-level operation times, up/down direction fields, train numbers,
  and departure/arrival fields:
  <https://www.data.go.kr/en/data/15143847/openapi.do>.
- Seoul public APIs document station train timetable access:
  <https://data.seoul.go.kr/bsp/wgs/dataView/data300View/527.do> and
  <https://data.seoul.go.kr/bsp/wgs/dataView/data300View/100204.do>.
- Seoul Open Data Plaza documents the Seoul Metro station-to-station
  shortest-path API. The dataset page states that it returns minimum-time,
  shortest-distance, and minimum-transfer paths with section-level station,
  travel-time, distance, and transfer information:
  <https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do>.
- Seoul Metro Line 9 operator pages list Olympic Park as a Line 9 station and
  expose a schedule page:
  <https://www.metro9.co.kr/eng/index.do> and
  <https://www.metro9.co.kr/prog/subwayTm/eng/sub01_02/list.do>.
- Seoul Metro Line 9 rolling-stock material lists six-car train configuration
  and total capacity of 922 passengers:
  <https://www.metro9.co.kr/eng/sub03_02_01.do>.
- Seoul Metropolitan Government reporting identifies Jamsil Station in Seoul
  Metro Line 2 passenger statistics:
  <https://english.seoul.go.kr/jamsil-and-seongsu-crowned-as-seouls-busiest-subway-stations/>.

No live API call or OSM call is part of the default test path. No static GTFS
feed is committed in this repository, but a cached-GTFS derivation path now
exists for future reviewed feeds.

## Offline Evidence Cache

The repository now includes an offline rail evidence cache:

- `data/parameters/rail_service_evidence.csv`

This file is intentionally not treated as calibrated evidence yet. The current
row is marked `documented_assumption_proxy`, which means it records the rail
values used by the model and their source context, but it does not derive them
from a cached GTFS feed, timetable extract, or station-to-station shortest-path
result.

Validation and audit helpers:

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_evidence.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence_review_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_station_binding.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable.py
.\.venv\Scripts\python tests\test_realworld_rail_gtfs.py
.\.venv\Scripts\python tests\test_realworld_rail_shortest_path.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py
.\.venv\Scripts\python scripts\audit_rail_station_bindings.py
```

The audit is expected to report `publication_ready: false` until cached
evidence derives both `headway` and `travel_time`, each derived row points to a
committed or otherwise reproducible source artifact with a matching SHA256
digest, rail capacity is either source-backed or explicitly retained as
sensitivity-only, and the station-binding audit reports official bindings for
the required rail points. Headway and travel time may come from separate
cached sources, for example a timetable extract for headway and a
shortest-path extract for station-to-station travel time.

## Rail Evidence Review Packet

The repository now includes a consolidated rail review packet:

- `src/realworld/rail_evidence_review_packet.py`
- `scripts/write_rail_evidence_review_packet.py`
- `scripts/write_rail_timing_source_request_packet.py`
- `data/parameters/rail_evidence_review_packet.csv`
- `data/parameters/rail_evidence_review_manifest.json`
- `data/rail/rail_timing_source_request_packet.csv`
- `data/rail/rail_timing_source_request_manifest.json`
- `docs/rail_evidence_review_packet.md`
- `docs/rail_timing_source_request_packet.md`

This packet joins station-binding status, current rail-service evidence,
rail assumptions, and available cached-derivation paths. The current generated
packet has 10 rows. It records that station binding is ready for `S` and `R`,
while service timing is not publication-ready because no reviewed cached
timetable, GTFS, or shortest-path artifact has derived both headway and travel
time. The manifest keeps `publication_ready: false`.

This packet is not accepted rail timing evidence. It exists to make the next
review step explicit before any rail-service claim is strengthened.

The source-request packet is even narrower: it lists the exact API-key or
reviewed-file inputs needed to create future cached timing artifacts. It does
not fetch data, derive timing evidence, or close the rail evidence gate.

## Cached Timetable Derivation

The repository now includes a local derivation path:

- `src/realworld/rail_timetable.py`
- `scripts/derive_rail_service_evidence.py`
- `docs/schemas/rail_timetable_cache_schema.md`

This path can convert a reviewed station-event timetable CSV into the
`rail_service_evidence.csv` schema. It derives median access-station headway
and median matched access-to-egress travel time from cached rows sharing a
`trip_id`. Derived evidence rows can also carry optional `derived_fields`,
`source_artifact_path`, and `source_artifact_sha256` columns so field-level
evidence can be audited. A derived row is not counted as ready unless the
artifact path resolves and its SHA256 matches. It does not call live APIs and
does not make the current shipped rail evidence publication-ready by itself.
The derivation command also checks cached timetable station codes against the
official station-binding table so an extract from a different station cannot
silently certify the pilot rail leg.

The current shipped `rail_service_evidence.csv` remains an assumption proxy
because no official timetable, GTFS, shortest-path, or equivalent station-event
extract has been committed for `songpa_public_demo`. Its rail capacity value is
now explicitly marked as sensitivity-only, which narrows the rail-service audit
blocker to missing cached timing evidence rather than implying calibrated train
capacity.

## Cached GTFS Derivation

The repository now includes a local GTFS derivation path:

- `src/realworld/rail_gtfs.py`
- `scripts/derive_rail_gtfs_evidence.py`
- `docs/schemas/rail_gtfs_cache_schema.md`

This path reads a reviewed static GTFS zip or directory and derives scheduled
headway plus access-stop to egress-stop travel time from `stops.txt`,
`trips.txt`, and `stop_times.txt`. The derived row uses
`source_status=cached_gtfs_derived`, records `derived_fields=headway;travel_time`,
and preserves `source_artifact_path` plus `source_artifact_sha256`.

GTFS timing evidence still does not prove emergency rail availability, station
processing capacity, special train operations, or train capacity. Capacity
remains source-backed or sensitivity-only evidence separate from the GTFS
timing derivation.

## Cached Shortest-Path Derivation

The repository now includes a local travel-time derivation path:

- `src/realworld/rail_shortest_path.py`
- `scripts/derive_rail_shortest_path_evidence.py`
- `docs/schemas/rail_shortest_path_cache_schema.md`

This path can convert a reviewed station-to-station shortest-path CSV into a
`cached_shortest_path_derived` rail evidence row. It records `travel_time` as
the derived field, verifies shortest-path station codes against the official
rail-point station-binding table, and stores the source artifact path and
SHA256 digest. It does not derive headway, capacity, rail availability, or
operational route feasibility; those fields must remain separately sourced or
explicitly sensitivity-only.

## Station Binding Cache

The repository now separates rail-service values from station binding evidence:

- `data/parameters/rail_station_bindings.csv`
- `src/realworld/rail_station_binding.py`
- `src/realworld/rail_station_cache.py`
- `scripts/audit_rail_station_bindings.py`
- `scripts/derive_rail_station_bindings.py`
- `docs/schemas/rail_station_cache_schema.md`

The current `S` and `R` rows are official line-specific station-code binding
rows derived from the cached Seoul Open Data Plaza station-name search extract
in `data/rail/pilot_station_binding_cache.csv`. The audit now reports
`binding_ready: true` for station identifiers.

For final-study rail claims, each required rail point must be replaced or
supplemented with `source_status=official_station_code_bound` and a
non-placeholder station code or station ID from a documented public or agency
source. This station-binding requirement is now satisfied for the pilot points,
but it is deliberately separate from rail service evidence.

The repository now includes an offline derivation path for that upgrade. A
reviewed station-source CSV that follows `docs/schemas/rail_station_cache_schema.md`
can be converted into official binding rows with
`scripts/derive_rail_station_bindings.py`.

## Assumption Status

Access and egress are traceable public station-area points from the pilot region
spec, and official line-specific station-code bindings are now tracked by
`data/parameters/rail_station_bindings.csv`. This does not choose or validate a
specific operational subway path.

The 10-minute headway is not yet parsed from a timetable. It is a fixed-headway
proxy supported by the existence of official timetable APIs and should remain in
the 5-20 minute sensitivity range until a cached timetable extract is added.

The 20-minute rail travel time is an abstract Olympic Park Station area to
Jamsil Station area service leg. It includes room for transfer and waiting in
the model and should remain in the 10-40 minute sensitivity range until a
cached shortest-path API result, public timetable extract, or GTFS-like extract
is parsed.

The 500 passenger capacity is deliberately below the Line 9 six-car total
capacity context of 922 passengers. It is a de-rated planning proxy to avoid
claiming full scheduled capacity emergency availability or crush-load capacity.
Sensitivity analysis should vary this value.

Rail availability is modeled as scheduled-service proxy only. The current model
does not guarantee emergency rail operations and does not calibrate rail delay
station closure or special operations.

## Upgrade Path

Before stronger claims are made:

1. Keep the current official station-code bindings reproducible from the cached
   station extract.
2. Cache a timetable, shortest-path, or GTFS-like extract outside default live
   tests.
3. Use `scripts/derive_rail_service_evidence.py` to derive headway from the
   selected service window and direction, or use
   `scripts/derive_rail_gtfs_evidence.py` for a reviewed static GTFS feed.
4. Use `scripts/derive_rail_shortest_path_evidence.py` for station-to-station
   shortest-path travel time, or derive travel time from matched timetable
   trips or reviewed GTFS stop times.
5. Replace the single capacity value with a documented route-leg capacity and
   sensitivity design.
6. Add rail delay or unavailability scenarios instead of assuming rail is
   always usable.
