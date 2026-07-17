# Analysis Corridor Method Note

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


Date: 2026-05-06

## Purpose

This note explains how the current real-world pilot scaffold uses a reduced
analysis corridor derived from the cached OSM road graph.

It does not certify the corridor as a final publication method. It records the
current method boundary so that generated results are interpreted correctly.

## Current Graph Levels

The current pilot input has three graph levels:

| Level | Nodes | Edges | Role |
| --- | ---: | ---: | --- |
| Raw cached OSM snapshot | 13,268 | 28,947 | Source snapshot loaded from the managed GraphML cache. |
| Bus-practical simulator graph | 4,608 | 9,148 | OSM-derived graph after filtering non-bus-practical geometries and adding connector nodes. |
| Reduced analysis corridor | 118 | 174 | Route-corridor subgraph used by current sample, staged, full, figure, and sensitivity scaffold outputs. |

The reduced analysis corridor keeps the current experiment loop tractable while
preserving the required origin-destination, access, rail-egress, and last-mile
routes for the pilot scaffold.

## Current Interpretation

The reduced corridor should be treated as a scaffold method, not as a calibrated
regional network model.

Allowed interpretation:

- The simulator can consume an OSM-derived regional road graph.
- The experiment runner can build a routeable corridor from that graph and run
  paired bus-only, multimodal, disruption, policy, and sensitivity scenarios.
- The manifests correctly record both source graph scale and analysis graph
  scale.

Not allowed:

- claiming that the 118-node corridor represents all relevant regional route
  choice, traffic assignment, spillback, or disruption exposure;
- treating corridor outputs as calibrated real-world performance estimates;
- using corridor results as operational routing advice.

## Final-Study Decision Options

Before the project can make final real-world or quasi-real study claims, one of
the following decisions is required.

### Option A: Accept Corridor Abstraction

Use the reduced corridor as an intentional zone-corridor study design.

Required evidence:

- clear explanation that the study models strategic corridors, not full road
  assignment;
- documented corridor-selection rule;
- route plausibility checks for every retained corridor;
- sensitivity check showing whether reasonable alternate corridor choices
  materially change the strategy ranking;
- manuscript language that calls the case quasi-real corridor-based, not full
  regional traffic simulation.

### Option B: Move To Full Graph Runtime

Keep the full bus-practical simulator graph in the experiment loop.

Required evidence:

- performance-safe shortest-path or precomputed-path strategy;
- successful staged/full runs on the 4,608-node / 9,148-edge graph;
- updated manifests and figures generated from the full graph;
- validation that route choice remains stable and runtime is reproducible.

### Option C: Use Multi-Corridor Ensemble

Run multiple route-corridor variants as uncertainty scenarios.

Required evidence:

- deterministic generation of alternate corridor sets;
- policy and disruption scenarios repeated across corridor variants;
- result tables that separate corridor uncertainty from operational parameter
  uncertainty;
- conservative claims about strategy robustness across corridor definitions.

## Current Decision

The current repository keeps the reduced analysis corridor as a scaffold and
performance abstraction. It is acceptable for smoke tests, implementation
verification, and preliminary figure/table generation. It is not yet accepted
as final paper evidence.

Current feasibility evidence:

- A tiny bus-only and baseline multimodal smoke can run on the 4,608-node /
  9,148-edge bus-practical graph without corridor reduction through
  `scripts/run_full_graph_smoke.py`.
- The full-vs-reduced route parity diagnostic in
  `data/validation/graph_scale_route_comparison.csv` currently has 3 pass
  rows for the canonical baseline road legs `A -> D`, `A -> S`, and `R -> D`.
  This means the reduced corridor preserves the full-graph shortest-time paths
  for those legs in the current scaffold.
- The alternate-route diagnostic in
  `data/validation/graph_scale_alternate_routes.csv` currently has 9 rows:
  3 rank-1 paths pass, while 6 alternate full-graph route candidates warn
  because they are not exactly preserved in the reduced corridor.
- A candidate multi-corridor graph that preserves the top 3 full-graph
  shortest-time route candidates for each canonical leg has 164 nodes and 246
  edges. Its diagnostic table,
  `data/validation/graph_scale_multi_corridor_routes.csv`, currently has 9
  pass rows and no warning rows.
- The separated `multi_corridor_candidate` profile now runs that candidate
  graph and writes `pilot_multi_corridor_results.csv`,
  `pilot_multi_corridor_summary.csv`, and
  `pilot_multi_corridor_manifest.json` as review evidence only.
- The separated `multi_corridor_full_candidate` profile runs the same
  164-node / 246-edge candidate graph with the current full pilot matrix and
  writes `pilot_multi_corridor_full_results.csv`,
  `pilot_multi_corridor_full_summary.csv`, and
  `pilot_multi_corridor_full_manifest.json` as stronger graph-scale review
  evidence only.
- `data/validation/graph_scale_result_comparison.csv` compares the current
  full pilot summary against that full-profile candidate in 819 metric-level
  rows so graph-choice effects are visible before any acceptance decision.
- The companion summary still reports that not all full shortest-distance
  paths are preserved, so the diagnostic is route-parity scaffold evidence
  rather than final graph-scale acceptance.

This proves that the full graph can execute at smoke scale. It does not prove
that the full staged/full policy-scenario-seed experiment is runtime-safe or
methodologically accepted. The alternate-route warning rows make
corridor-abstraction uncertainty explicit, and the multi-corridor candidate is
a concrete upgrade path with both smoke-scale and full-profile candidate
outputs. Neither option reviews traffic assignment, spillback, hazard routing,
or operational detours without a separate graph-scale acceptance decision and
downstream regeneration under the accepted graph-scale method.

The next accepted-study step is to choose Option A, B, or C and regenerate the
pilot outputs under that decision.
