# Pilot Accessibility-Loss Diagnostic Summary

Region ID: `songpa_public_demo`

Evidence class: scaffold route-fragility diagnostic. This is not
calibrated real-world accessibility evidence and is not an operational
routing recommendation.

## Current Scaffold Boundary

- Final-study ready: `false`.
- Final-study gate status: `3/15` ready and `12/15` blocked.
- Formal acceptance ready: `0/12`; no formal approval artifacts are present.
- Validation and graph-scale strategy readiness packets are implemented as review aids only.
- This diagnostic is scaffold evidence only; it is not a calibrated real-world result.

## Inputs

- Region spec: `data/regions/pilot_region.yaml`
- Cached road graph: `data/cache/pilot_region_road.graphml`
- Diagnostic helper: `src/realworld/accessibility.py`
- Accessibility-loss table: `data/validation/accessibility_loss.csv`

## Current Snapshot Results

- Adapted graph nodes: 4608
- Adapted graph edges: 9148
- Diagnostic rows: 127
- Routes checked: 3
- Route IDs: bus_direct, last_mile, rail_access
- Disconnected edge-removal cases: 22

Criticality counts:

- `disconnected`: 22
- `high_time_loss`: 17
- `low_time_loss`: 50
- `moderate_time_loss`: 38

## Interpretation Boundary

- Each row removes one directed edge from the baseline shortest-time road
  path and recomputes the road route.
- The diagnostic identifies where the current adapted graph is fragile to
  local link removal.
- It does not assign outage probabilities, traffic reassignment behavior,
  emergency control behavior, or real accessibility loss.
- Final manuscript claims still require accepted graph-scale, road-input,
  validation, and experiment gates.

## Review Items

- treat edge-removal impacts as scaffold route-fragility diagnostics, not calibrated outage probabilities
- review whether directed edge removal, bidirectional road-link removal, or corridor-level disruption matches the final study design
- combine these diagnostics with accepted graph-scale, road evidence, and validation gates before manuscript claims
