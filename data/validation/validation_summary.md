# Pilot Route Plausibility Validation Summary

Region ID: `songpa_public_demo`

Evidence class: scaffold/sanity evidence for the committed offline pilot graph.
This is not calibrated real-world validation and is not ground truth for
emergency operations or public transport service.

## Current Scaffold Boundary

- Final-study ready: `false`.
- Final-study gate status: `3/15` ready (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`) and `12/15` blocked.
- Formal acceptance ready: `0/12`; no formal approval artifacts are present.
- Validation strategy readiness is implemented in `data/validation/validation_strategy_readiness_packet.csv`, but it is review support only and cannot close `data/manifests/validation_acceptance.json`.
- Graph-scale strategy readiness is implemented in `data/validation/graph_scale_strategy_readiness_packet.csv`, but it is review support only and cannot close `data/manifests/graph_scale_acceptance.json`.
- Current validation outputs are scaffold checks; no calibrated real-world result or operational route plan is accepted.

## Inputs

- Region spec: `data/regions/pilot_region.yaml`
- Cached road graph: `data/cache/pilot_region_road.graphml`
- Validation helper: `src/realworld/plausibility.py`
- Internal route plausibility table: `data/validation/route_plausibility.csv`
- External/fallback benchmark table: `data/validation/external_route_benchmarks.csv`

The adapted simulator graph filters pedestrian, cycling, platform,
construction, track, living-street, and service-only OSM geometries before
zone/rail-point snapping and route checks. These filtered geometries remain in
the raw cache for provenance, but they are not treated as bus-practical vehicle
routes.

The checks load the cached GraphML and adapted simulator graph only. They do not
call live OSM, OSRM, Valhalla, routingpy, R5, OpenTripPlanner, UXsim, or other
web/external routing services. The current benchmark layer uses an executable
documented fallback: endpoint-coordinate straight-line distance multiplied by a
route-class detour factor, then converted to time using coarse urban speed
assumptions. Cached OSRM/Valhalla/routingpy/R5/OpenTripPlanner/UXsim outputs
can replace the fallback later, but any such value remains a plausibility
benchmark and not ground truth.

## Current Snapshot Results

- Adapted graph nodes: 4608
- Adapted graph edges: 9148
- Internal checks: 21
- Pass: 19
- Warn: 2
- Fail: 0
- Benchmark checks: 3
- Benchmark pass: 2
- Benchmark warn: 1
- Benchmark fail: 0

## Assumptions

- Route distance checks compare adapted graph path length with a straight-line
  coordinate lower bound from the public or synthetic scaffold points.
- Free-flow time checks use simulator `t0` values from the adapter and do not
  include congestion, dispatch waiting, transfer handling, or disruption.
- Implied speed checks use broad urban-road sanity ranges, not calibration.
- Connector checks use `connector_distance_m` metadata from the zone snapping
  layer.
- Road speed and capacity checks inspect non-connector road edges only and use
  coarse planning ranges.
- The benchmark table currently uses a documented executable fallback because
  no reviewed OSRM, Valhalla, routingpy, R5, OpenTripPlanner, or UXsim cache is
  committed. This gives Workstream 6 an explicit external-benchmark interface
  and reproducible comparison method without adding a live-service dependency.

## Residual Risks

- The current GraphML is an offline pilot snapshot for smoke and sanity testing.
  It still requires review before publication-grade claims.
- Road capacities, free-flow speeds, and disruption probabilities remain proxy
  assumptions until parameter-source tables and benchmarking are completed.
- The fallback benchmark is independent of adapted graph routing, but it is
  still an assumption-based comparator. It should be replaced or supplemented
  with cached third-party route-engine outputs before calibrated route-realism
  claims are made.
- Rail travel time, headway, and capacity remain documented assumptions for the
  pilot scaffold.
- Passing these checks means the adapted snapshot is internally plausible enough
  for scaffold testing. It does not justify operational route planning claims
  or calibrated real-world accuracy claims.
