# Graph-Scale Multi-Corridor Candidate Summary

Region ID: `songpa_public_demo`

Evidence class: graph-scale multi-corridor candidate diagnostic.
This table compares top full-graph shortest-time route candidates with
the multi-corridor candidate graph. It is not graph-scale acceptance and not calibrated
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
- Alternate-route table: `data/validation/graph_scale_multi_corridor_routes.csv`

## Current Snapshot Results

- Full bus-practical graph nodes: 4608
- Full bus-practical graph edges: 9148
- Multi-corridor candidate graph nodes: 164
- Multi-corridor candidate graph edges: 246
- Requested paths per route: 3
- Alternate-route rows: 9
- Pass: 9
- Warn: 0
- Fail: 0
- Rank-1 paths preserved: 3 / 3
- Alternate paths preserved: 6 / 6
- Minimum edge coverage in multi-corridor candidate graph: 1.000000
- All analysis routes available: true
- All rank-1 paths preserved: true
- All alternate paths preserved: true

## Interpretation Boundary

- A pass means a full-graph candidate path is exactly present in the
  multi-corridor candidate graph.
- A warn for rank greater than 1 means an alternate full-graph path is
  omitted by the multi-corridor candidate graph and should be treated as graph-scale
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
