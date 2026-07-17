# Optional OSRM Route Benchmark Summary

Region ID: `songpa_public_demo`

Evidence class: optional external-router plausibility evidence. This is not
ground truth and does not calibrate emergency operations.

## Inputs

- Cached road graph: `data/cache/pilot_region_road.graphml`
- OSRM base URL: `https://router.project-osrm.org`
- Output table: `data/validation/external_route_benchmarks_osrm.csv`

## Current Snapshot Results

- Adapted graph nodes: 4608
- Adapted graph edges: 9148
- Benchmark checks: 3
- Pass: 3
- Warn: 0
- Fail: 0

The adapted graph filters pedestrian, cycling, platform, construction, track,
living-street, and service-only OSM geometries out of bus-practical simulator
routes before the OSRM comparison is built.

## Warn/Fail Rows

- No warn/fail benchmark rows in this snapshot.

## Claim Boundary

The OSRM public demo service is an external routing reference for route-distance
and travel-time plausibility only. It is not a calibrated local traffic model,
not a public-agency forecast, and not an operational route plan. Keep the
offline fallback benchmark as the default deterministic validation layer.

Any warn or fail row should be treated as a reason to limit claims, inspect the
adapted graph route, or revise the accepted analysis corridor before publishing
route-realism conclusions.
