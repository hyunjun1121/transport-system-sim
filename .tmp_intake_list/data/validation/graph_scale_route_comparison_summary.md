# Graph-Scale Route Comparison Summary

Region ID: `songpa_public_demo`

Evidence class: graph-scale scaffold diagnostic. This compares baseline
shortest road routes on the full bus-practical graph and the reduced
analysis corridor. It is not graph-scale acceptance and not calibrated
real-world validation.

## Current Scaffold Boundary

- Final-study ready: `false`.
- Final-study gate status: `3/15` ready and `12/15` blocked.
- Formal acceptance ready: `0/12`; no formal approval artifacts are present.
- Graph-scale strategy readiness is implemented in `data/validation/graph_scale_strategy_readiness_packet.csv`, but it is review support only.
- This diagnostic is scaffold evidence only; it is not a calibrated real-world result.

## Inputs

- Region spec: `data/regions/pilot_region.yaml`
- Cached road graph: `data/cache/pilot_region_road.graphml`
- Diagnostic helper: `src/realworld/graph_scale_diagnostics.py`
- Route comparison table: `data/validation/graph_scale_route_comparison.csv`

## Current Snapshot Results

- Full bus-practical graph nodes: 4608
- Full bus-practical graph edges: 9148
- Reduced analysis corridor nodes: 118
- Reduced analysis corridor edges: 174
- Route comparison rows: 3
- Pass: 3
- Warn: 0
- Fail: 0
- All routes available: true
- All full shortest-time paths preserved: true
- All full shortest-distance paths preserved: false

## Interpretation Boundary

- A pass means the reduced corridor preserves the current full-graph
  baseline shortest-time route for a canonical road leg.
- This diagnostic does not evaluate all alternate corridors, traffic
  assignment, spillback, hazard exposure, or operational detours.
- Final graph-scale claims still require
  `data/manifests/graph_scale_acceptance.json` after review.

## Review Items

- confirm whether baseline shortest-route parity is sufficient for a corridor abstraction
- review alternate corridor sensitivity before graph-scale acceptance
- rerun this diagnostic after any OSM cache, connector, or road-class override change
- do not use this diagnostic as final graph-scale acceptance by itself
