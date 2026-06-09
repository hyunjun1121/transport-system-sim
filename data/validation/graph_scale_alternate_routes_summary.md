# Graph-Scale Alternate Route Summary

Region ID: `songpa_public_demo`

Evidence class: graph-scale alternate-route sensitivity diagnostic.
This table compares top full-graph shortest-time route candidates with
the reduced analysis corridor. It is not graph-scale acceptance and not calibrated
real-world validation.

## Inputs

- Region spec: `data/regions/pilot_region.yaml`
- Cached road graph: `data/cache/pilot_region_road.graphml`
- Diagnostic helper: `src/realworld/graph_scale_diagnostics.py`
- Alternate-route table: `data/validation/graph_scale_alternate_routes.csv`

## Current Snapshot Results

- Full bus-practical graph nodes: 4608
- Full bus-practical graph edges: 9148
- Reduced analysis corridor nodes: 118
- Reduced analysis corridor edges: 174
- Requested paths per route: 3
- Alternate-route rows: 9
- Pass: 3
- Warn: 6
- Fail: 0
- Rank-1 paths preserved: 3 / 3
- Alternate paths preserved: 0 / 6
- Minimum edge coverage in reduced analysis corridor: 0.314286
- All analysis routes available: true
- All rank-1 paths preserved: true
- All alternate paths preserved: false

## Interpretation Boundary

- A pass means a full-graph candidate path is exactly present in the
  reduced analysis corridor.
- A warn for rank greater than 1 means an alternate full-graph path is
  omitted by the reduced analysis corridor and should be treated as graph-scale
  uncertainty.
- This diagnostic does not perform dynamic traffic assignment, spillback,
  hazard routing, or operational detour validation.
- Final graph-scale claims still require
  `data/manifests/graph_scale_acceptance.json` after review.

## Review Items

- use this table to decide whether the reduced corridor omits important alternate routes
- treat missing alternate paths as graph-scale uncertainty, not operational failure evidence
- add full-graph runtime or multi-corridor experiments if omitted alternates affect claims
- do not use this diagnostic as final graph-scale acceptance by itself
