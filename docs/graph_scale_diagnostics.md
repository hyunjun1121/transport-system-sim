# Graph-Scale Route Diagnostics

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


Date: 2026-05-06

## Purpose

This note documents the current full-graph versus reduced-corridor route
parity and alternate-route diagnostics for the `songpa_public_demo` pilot
scaffold.

The diagnostic supports graph-scale review. It does not accept the reduced
analysis corridor as the final study method, and it does not create calibrated
real-world validation.

## Current Diagnostic

The route-parity diagnostic compares canonical baseline road legs on two graph
levels:

| Graph Level | Nodes | Edges | Role |
| --- | ---: | ---: | --- |
| Full bus-practical simulator graph | 4,608 | 9,148 | OSM-derived graph after bus-practical filtering and connector creation. |
| Reduced analysis corridor | 118 | 174 | Current scaffold graph used by sample, staged, full, figure, and sensitivity outputs. |

Current comparison output:

| Artifact | Role |
| --- | --- |
| `data/validation/graph_scale_route_comparison.csv` | Stable CSV table with one row per canonical road leg. |
| `data/validation/graph_scale_route_comparison_summary.md` | Generated summary with graph counts, status counts, and interpretation boundary. |
| `data/validation/graph_scale_alternate_routes.csv` | Stable CSV table comparing the top full-graph route candidates against the reduced corridor. |
| `data/validation/graph_scale_alternate_routes_summary.md` | Generated alternate-route summary with pass/warn/fail counts and claim boundary. |
| `data/validation/graph_scale_multi_corridor_routes.csv` | Stable CSV table comparing the same top full-graph route candidates against a candidate multi-corridor graph. |
| `data/validation/graph_scale_multi_corridor_routes_summary.md` | Generated multi-corridor candidate summary with pass/warn/fail counts and claim boundary. |
| `scripts/run_graph_scale_diagnostics.py` | Regenerates the CSV and summary from the cached pilot inputs. |
| `src/realworld/graph_scale_diagnostics.py` | Implements route comparison, status classification, and CSV row generation. |

The current generated table has 3 rows:

| Route | Status | Interpretation |
| --- | --- | --- |
| `A -> D` bus direct road leg | pass | The reduced corridor preserves the full-graph baseline shortest-time path. |
| `A -> S` rail-access road leg | pass | The reduced corridor preserves the full-graph baseline shortest-time path. |
| `R -> D` last-mile road leg | pass | The reduced corridor preserves the full-graph baseline shortest-time path. |

The summary reports:

- all routes available: true
- all full shortest-time paths preserved: true
- all full shortest-distance paths preserved: false

## Alternate-Route Sensitivity Diagnostic

The alternate-route diagnostic compares the top 3 full-graph shortest-time
route candidates for each canonical road leg against the reduced analysis
corridor. It is a sensitivity scaffold for graph-scale review, not final
acceptance.

The current generated alternate-route table has 9 rows:

| Route Set | Rank-1 Status | Alternate-Route Status |
| --- | --- | --- |
| `A -> D` bus direct road leg | pass | rank 2 and rank 3 warn |
| `A -> S` rail-access road leg | pass | rank 2 and rank 3 warn |
| `R -> D` last-mile road leg | pass | rank 2 and rank 3 warn |

The alternate-route summary reports:

- pass: 3
- warn: 6
- fail: 0
- rank-1 paths preserved: 3 / 3
- alternate paths preserved: 0 / 6
- minimum edge coverage in analysis graph: 0.314286

This means the reduced corridor currently preserves each canonical
shortest-time path, but it omits the next-best full-graph route candidates.
That is useful review evidence because it makes corridor-abstraction
uncertainty visible. It is not evidence that the omitted alternates are
operationally irrelevant.

## Multi-Corridor Candidate Diagnostic

The same run now builds a candidate multi-corridor graph by preserving the top
3 full-graph shortest-time route candidates for each canonical road leg. This
candidate graph has 164 nodes and 246 edges, compared with 118 nodes and 174
edges in the current reduced analysis corridor.

The current generated multi-corridor table has 9 rows:

| Route Set | Rank-1 Status | Alternate-Route Status |
| --- | --- | --- |
| `A -> D` bus direct road leg | pass | rank 2 and rank 3 pass |
| `A -> S` rail-access road leg | pass | rank 2 and rank 3 pass |
| `R -> D` last-mile road leg | pass | rank 2 and rank 3 pass |

This candidate graph removes the current alternate-route warnings for the top
3 route candidates. A separated `pilot_multi_corridor` experiment profile runs
this graph and writes 32 raw rows plus 16 summary rows for smoke-scale review.
A second `multi_corridor_full_candidate` profile now runs the same candidate
graph on the full 7-policy, 9-scenario, 30-seed matrix and writes 1,890 raw
rows plus 63 summary rows for graph-scale review. Both outputs are still
review support only: accepting this as the final graph-scale method would
require a documented corridor-selection rule, reviewed comparison against the
current reduced-corridor full pilot, review of the 819-row
`graph_scale_result_comparison.csv` delta table, review of the latest
`docs/graph_scale_strategy_readiness_packet.md`, regenerated downstream
sensitivity or figure/table outputs as needed, and a reviewed
`data/manifests/graph_scale_acceptance.json` record.

## Interpretation Boundary

Allowed interpretation:

- the current reduced corridor preserves the baseline full-graph shortest-time
  paths for the three canonical road legs used by the current scaffold;
- the diagnostic is useful evidence for reviewing whether a corridor
  abstraction is defensible;
- the diagnostic should be rerun after any OSM cache, connector, road-class
  override, or graph-reduction change.

Not allowed:

- claiming that the reduced 118-node corridor represents all relevant regional
  route choice;
- claiming that alternate corridors, congestion spillback, traffic assignment,
  hazard exposure, or operational detours have been reviewed;
- treating the 3 pass rows as final graph-scale acceptance;
- treating the 6 alternate-route warning rows as calibrated failure or
  detour-probability evidence;
- treating the 9 multi-corridor pass rows or the 1,890-row full-profile
  multi-corridor candidate output as final method acceptance before the graph
  choice is reviewed;
- using this diagnostic as calibrated real-world or operational route evidence.

## Remaining Review Items

Before the graph-scale strategy gate can close, reviewers must choose one final
method:

- accepted corridor abstraction,
- full-graph runtime,
- multi-corridor ensemble.

If the current corridor abstraction is retained, reviewers must decide whether
the alternate-route warning rows are acceptable under a documented
corridor-selection rule. The new multi-corridor candidate provides one concrete
upgrade path, but staged/full experiments and figures would need to be
regenerated under that graph before result claims can use it. If the study
moves to full-graph runtime, staged and full experiments must be regenerated on
the full bus-practical graph. If a multi-corridor ensemble is selected,
corridor uncertainty must be separated from operational parameter uncertainty
in the results.

Final graph-scale claims still require a reviewed
`data/manifests/graph_scale_acceptance.json` record. That record is
intentionally absent in the current scaffold.

Current final-study status remains blocked: only 3 / 15 plan gates are ready,
12 / 15 are blocked, and formal acceptance is 0 / 12 ready with required
formal artifacts absent.
