# Real-World / Quasi-Real Pipeline

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This document records the implemented MVP for feeding open-map-style regional
road data into the existing transport micro-simulator. The pipeline is
decision-support research infrastructure. It is not a calibrated operational
routing model.

## Current Status Boundary

As of the current audit, `final_study_ready` remains `false`. The plan-level
audit reports 3 / 15 ready gates (`real_input_smoke`,
`structured_disruptions`, and `policy_alternatives`) and 12 / 15 blocked gates.
Formal acceptance is not ready: 0 / 12 formal gates are ready, the required
formal acceptance artifacts are absent, and no final approval should be
claimed.

The latest strategy-detail packets exist and are review aids only:

- `docs/graph_scale_strategy_readiness_packet.md` with
  `data/validation/graph_scale_strategy_readiness_manifest.json`
- `docs/validation_strategy_readiness_packet.md` with
  `data/validation/validation_strategy_readiness_manifest.json`
- `docs/sensitivity_strategy_readiness_packet.md` with
  `data/validation/sensitivity_strategy_readiness_manifest.json`
- `docs/experiment_strategy_readiness_packet.md` with
  `data/manifests/experiment_strategy_readiness_manifest.json`

## Implemented Scope

The current vertical slice is:

```text
RegionSpec
-> OSMnx extraction or cached/synthetic GraphML
-> normalized OSM-like road graph
-> deterministic road edge attribute mapping
-> zone and rail-point snapping
-> bidirectional connector edges
-> simulator-compatible NetworkX DiGraph
-> readiness validation
-> run_scenario(...)
```

Implemented modules:

| Module | Role |
| --- | --- |
| `src/realworld/types.py` | Validated records for bbox regions, zones, rail points, and fixed-headway rail inputs |
| `src/realworld/regions.py` | Region spec and registry loading helpers |
| `src/realworld/osm_network.py` | Optional live OSMnx bbox extraction plus offline GraphML load/save and normalization |
| `src/realworld/attributes.py` | OSM-style road fields mapped to simulator `t0`, `capacity`, `p_fail`, `base_p_fail`, routeable-road eligibility, and metadata |
| `src/realworld/zones.py` | Nearest-node snapping using `x`/`y` lon/lat and connector edge creation |
| `src/realworld/adapter.py` | Normalized OSM-like graph conversion into simulator-ready `networkx.DiGraph` |
| `src/realworld/validation.py` | Required node, edge-field, numeric, and route-readiness checks |
| `src/realworld/parameters.py` | Parameter-source, rail-assumption, and fleet-assumption table validation |
| `src/realworld/parameter_evidence_request_packet.py` | Cross-cutting parameter evidence source-request worksheet for demand, fleet, dispatch, transfer, disruption, and traffic/BPR review |
| `src/realworld/plausibility.py` | Offline route, connector, speed, capacity, fallback benchmark checks, and optional OSRM benchmark helpers |
| `src/realworld/osrm_snapshot_manifest.py` | Optional OSRM benchmark checksum/query/raw-payload manifest generation without validation acceptance |
| `src/realworld/validation_review_packet.py` | Validation-package review worksheet for plausibility, fallback/OSRM benchmark, accessibility-loss, route road-evidence exposure, scope, and benchmark-strategy decision support |
| `src/realworld/route_road_evidence_exposure.py` | Route-level road-evidence exposure worksheet linking weak road assumptions to canonical route candidates |
| `src/realworld/graph_scale_diagnostics.py` | Full-vs-reduced route parity and alternate-route checks for current baseline road legs |
| `src/realworld/disruption_scenarios.py` | Deterministic structured disruption scenario definitions and edge mapping |
| `src/realworld/policy_alternatives.py` | Policy-alternative table validation and non-mutating config variants |
| `src/realworld/pilot_experiments.py` | Cached pilot scaffold sample/staged/full experiment runner |
| `src/realworld/sensitivity.py` | Deterministic one-at-a-time and SALib Morris sensitivity scaffold |
| `src/realworld/sensitivity_review_packet.py` | Morris sensitivity diagnostics review worksheet for index handling, zero-effect interpretation, reduced-graph scope, and Morris-vs-Sobol decision support |
| `src/realworld/pilot_figures.py` | Scaffold-only figures, result tables, and claim-boundary table generation |
| `src/realworld/road_capacity_evidence.py` | Cached OSM `lanes` capacity-candidate summaries by routeable road class |
| `src/realworld/road_speed_evidence.py` | Cached OSM `maxspeed` candidate evidence summaries by routeable road class |
| `src/realworld/road_evidence_request_packet.py` | Road evidence source-request worksheet for speed, capacity, background-traffic, disruption, and override-application review |

The adapter currently targets canonical simulator node IDs:

```text
A = primary assembly zone
D = primary destination zone
S = rail access point
R = rail egress point
```

Required road-mode route checks are `A -> D`, `A -> S`, and `R -> D`.

## Current Pilot Artifacts

The repository now includes a first non-sensitive offline pilot scaffold:

| Artifact | Role |
| --- | --- |
| `data/regions/pilot_region.yaml` | `songpa_public_demo` region, zone, rail-point, and rail-service spec |
| `docs/pilot_region_data_card.md` | Privacy/security handling, coordinate classes, reuse notes, and claim limits |
| `data/cache/pilot_region_road.graphml` | Offline cached road graph for repeatable smoke and sample runs |
| `data/cache/pilot_region_road_manifest.json` | Cache metadata and claim-limit statement |
| `scripts/build_pilot_cache.py` | Preserves an existing cache by default; rebuilds the fixture or refreshes Overpass only when explicitly requested |
| `scripts/run_pilot_smoke.py` | Loads the pilot cache and runs `bus_only` and `multimodal` |
| `tests/test_realworld_pilot_smoke.py` | Direct-execution test for the offline pilot path |
| `data/parameters/` | Parameter, rail, and fleet evidence tables |
| `data/parameters/parameter_evidence_source_request_packet.csv` | Cross-cutting parameter source-request worksheet; 6 request rows for demand, fleet, dispatch, transfer, disruption, and traffic/BPR evidence |
| `data/parameters/road_capacity_evidence_candidates.csv` | Cached OSM lane-count capacity candidate evidence; 10 road-class rows, 0 with observed lane tags, not accepted calibration |
| `data/parameters/road_speed_evidence_candidates.csv` | Cached OSM maxspeed candidate evidence; 10 road-class rows, 5 with observed tags, not accepted calibration |
| `data/parameters/road_class_overrides_draft.csv` | Current road-class override review worksheet; 10 expert-assumption rows, not accepted evidence |
| `data/road/road_evidence_source_request_packet.csv` | Road evidence source-request worksheet; 5 request rows for speed, capacity, benchmark, disruption, and reviewed override application |
| `data/validation/` | Current route plausibility checks, fallback benchmark checks, optional OSRM snapshot, optional raw OSRM payload directory, OSRM manifest, and summaries |
| `data/validation/canonical_route_road_evidence_exposure.csv` | Route-level road-evidence exposure worksheet; 76 rows across 18 route candidates, review support only |
| `data/validation/validation_review_packet.csv` | Validation review worksheet; 7 rows for internal plausibility, fallback benchmark, OSRM snapshot, accessibility-loss, route evidence exposure, summary scope, and benchmark-strategy decision review |
| `data/validation/validation_strategy_readiness_packet.csv` | Validation strategy-readiness worksheet; 7 rows with 3 blocking requests and 4 human-review requests; not validation acceptance |
| `data/validation/graph_scale_route_comparison.csv` | Full-vs-reduced route parity diagnostic; 3 current rows, all pass for baseline shortest-time paths |
| `data/validation/graph_scale_route_comparison_summary.md` | Graph-scale diagnostic summary and claim boundary |
| `data/validation/graph_scale_alternate_routes.csv` | Full-vs-reduced alternate-route diagnostic; 9 current rows with 3 pass and 6 warn statuses |
| `data/validation/graph_scale_alternate_routes_summary.md` | Alternate-route diagnostic summary and claim boundary |
| `data/validation/graph_scale_multi_corridor_routes.csv` | Multi-corridor candidate diagnostic; 9 current rows, all pass |
| `data/validation/graph_scale_multi_corridor_routes_summary.md` | Multi-corridor candidate summary and claim boundary |
| `data/validation/full_graph_smoke_manifest.json` | Two-row full bus-practical graph smoke manifest; feasibility evidence only |
| `data/validation/full_graph_runtime_readiness_packet.csv` | Full-graph runtime-readiness worksheet; 4 rows, not graph-scale acceptance |
| `data/validation/graph_scale_strategy_readiness_packet.csv` | Graph-scale strategy-readiness worksheet; 5 rows with 3 blocking requests and 2 human-review requests; not graph-scale acceptance |
| `data/validation/sensitivity_review_packet.csv` | Morris sensitivity review worksheet; 6 rows for structural readiness, index issues, zero `mu_star`, reduced graph scope, result scope, and Sobol-decision review |
| `data/validation/sensitivity_strategy_readiness_packet.csv` | Sensitivity strategy-readiness worksheet; 7 rows with 4 blocking requests and 3 human-review requests; not sensitivity acceptance |
| `data/manifests/experiment_strategy_readiness_packet.csv` | Experiment strategy-readiness worksheet; 9 rows with 4 blocking requests and 5 human-review requests; not experiment acceptance |
| `data/scenarios/` | Structured disruption and policy-alternative scenario tables |
| `data/manifests/reproducibility_manifest.json` | Current scaffold-only reproduction manifest |
| `results/realworld_pilot/` | Separated pilot scaffold sample/staged/full and sensitivity outputs |

The current cache manifest records a `live_overpass_osm_snapshot` source. It
proves that the real-world adapter can feed the existing simulator with a
pilot-shaped OSM-derived input, but it is not yet a reviewed or calibrated
study network. The compact fixture remains available only as a deterministic
fallback for cache-refresh experiments.

The adapter now filters pedestrian, cycling, platform, construction, track,
living-street, and service-only OSM geometries out of bus-practical simulator
routes before snapping `A`, `D`, `S`, and `R` to the road graph. The raw cache
still contains those geometries for provenance, but they are no longer treated
as vehicle roads in the simulator graph.

Current graph scale:

- Raw cached OSM snapshot: 13,268 nodes and 28,947 edges
- Bus-practical simulator graph after filtering: 4,608 nodes and 9,148 edges
- Reduced experiment corridor in current pilot outputs: 118 nodes and 174 edges

## Offline Validation

Default tests use synthetic NetworkX fixtures and must not contact live OSM or
Overpass services.

```powershell
.\.venv\Scripts\python tests\test_realworld_types.py
.\.venv\Scripts\python tests\test_realworld_attributes.py
.\.venv\Scripts\python tests\test_realworld_osm_network.py
.\.venv\Scripts\python tests\test_realworld_adapter.py
.\.venv\Scripts\python tests\test_realworld_validation.py
.\.venv\Scripts\python tests\test_realworld_end_to_end.py
.\.venv\Scripts\python tests\test_realworld_pilot_smoke.py
.\.venv\Scripts\python tests\test_realworld_parameters.py
.\.venv\Scripts\python tests\test_realworld_plausibility.py
.\.venv\Scripts\python tests\test_realworld_disruption_scenarios.py
.\.venv\Scripts\python tests\test_realworld_policy_alternatives.py
.\.venv\Scripts\python tests\test_scenario.py
```

The synthetic end-to-end test builds an OSM-like graph, adapts it, validates it,
and runs both `bus_only` and `multimodal` through `run_scenario(...)`.

Pilot smoke commands:

```powershell
.\.venv\Scripts\python scripts\run_pilot_smoke.py
.\.venv\Scripts\python scripts\run_plausibility_validation.py
.\.venv\Scripts\python scripts\run_accessibility_loss_analysis.py
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py --raw-response-dir data\validation\osrm_route_raw
.\.venv\Scripts\python scripts\write_route_road_evidence_exposure.py
.\.venv\Scripts\python scripts\write_validation_review_packet.py
.\.venv\Scripts\python scripts\run_graph_scale_diagnostics.py
.\.venv\Scripts\python scripts\write_graph_scale_result_comparison.py
.\.venv\Scripts\python scripts\run_pilot_experiments.py --sample
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor-full
.\.venv\Scripts\python scripts\run_sensitivity.py --sample
.\.venv\Scripts\python scripts\write_sensitivity_review_packet.py
.\.venv\Scripts\python scripts\write_sensitivity_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\write_experiment_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\write_road_capacity_evidence.py
.\.venv\Scripts\python scripts\write_road_speed_evidence.py
.\.venv\Scripts\python scripts\make_pilot_statistics.py
.\.venv\Scripts\python scripts\make_pilot_statistics.py --input results\realworld_pilot\pilot_multi_corridor_results.csv --source-manifest results\realworld_pilot\pilot_multi_corridor_manifest.json --output-prefix pilot_multi_corridor
.\.venv\Scripts\python scripts\make_pilot_statistics.py --input results\realworld_pilot\pilot_multi_corridor_full_results.csv --source-manifest results\realworld_pilot\pilot_multi_corridor_full_manifest.json --output-prefix pilot_multi_corridor_full
.\.venv\Scripts\python scripts\make_pilot_figures.py
```

## Optional Live OSM Usage

Live extraction is deliberately isolated behind `src.realworld.osm_network`.
Install `osmnx` only when a manual extraction is needed:

```powershell
.\.venv\Scripts\python -m pip install osmnx
```

Use `extract_bbox_graph(...)` for one-time extraction or
`load_or_extract_bbox_graph(...)` to prefer a cached GraphML file. Keep live OSM
calls out of unit tests and prefer reviewed caches for repeatable experiments.

Example shape:

```python
from src.realworld.osm_network import load_or_extract_bbox_graph

graph = load_or_extract_bbox_graph(
    "data/cache/pilot_region_road.graphml",
    north=37.53,
    south=37.50,
    east=127.14,
    west=127.09,
    network_type="drive",
)
```

The coordinates above match the current public demo region envelope. Do not
treat the cached graph as an accepted publication-grade pilot case until the
snapshot, connectors, parameters, and rail assumptions are reviewed and
validated.

## Quasi-Real Limitations

The MVP makes the network input more realistic, but it does not calibrate the
simulation by itself.

Current limitations:

- OSM road classes, speeds, lengths, and missing values are mapped to coarse
  deterministic planning proxies.
- The cached OSM `maxspeed` candidate table exposes sparse public speed tags
  for 10 routeable road classes. It supports review triage only and does not
  replace a reviewed road-class override table.
- The cached OSM `lanes` capacity-candidate table currently has no parseable
  lane observations for routeable road classes, so capacity remains a fallback
  evidence gap until reviewed traffic counts, design references, or accepted
  proxies are supplied.
- The current road-class override draft is only a review worksheet. It mirrors
  mapper defaults and must be replaced by a reviewed
  `data/parameters/road_class_overrides.csv` before road-calibration claims.
- The road evidence source-request packet names the next speed, capacity,
  background-traffic, disruption, and override-application inputs to collect,
  but it is not itself road evidence and does not close any readiness gate.
- Directional capacities and failure probabilities are proxy assumptions, not
  measured field values.
- Zone connectors use nearest-node snapping and approximate lon/lat distance;
  connector distances must be reviewed for plausibility.
- Rail remains a fixed-headway abstraction in the current shipped pilot row.
  Cached timetable, shortest-path, and static-GTFS derivation paths now exist,
  but no reviewed rail timing feed is committed and rail disruption modeling is
  not calibrated.
- Dynamic traffic still uses rolling-window BPR rather than traffic assignment,
  spillback, signal timing, or microscopic simulation.
- Live OSM availability, Overpass responses, and OSM data quality are external
  dependencies; reproducible studies should use cached input snapshots.
- The current pilot cache is for smoke and scaffold sample testing;
  publication claims require
  parameter-source tables, rail evidence, route plausibility checks, structured
  disruption scenarios, and sensitivity analysis.
- Parameter-source tables, route plausibility checks, fallback route benchmark
  checks, optional OSRM benchmark checks, structured disruption scenarios, and
  policy alternatives now exist for the pilot path. They are study scaffolding
  until the OSM-derived input, reduced analysis corridor, route warnings, and
  assumptions are reviewed for publication use. The current optional OSRM
  snapshot has no warn/fail rows after bus-practical road filtering, and the
  OSRM manifest records 3 cached external-router rows, 0 unpinned rows, 3
  retained raw response files, query URLs, and checksums. The deterministic
  fallback benchmark still warns on `A -> S`.
- The parameter evidence source-request packet names the demand, fleet,
  dispatch, transfer, disruption, and traffic/BPR source packages still needed
  before weak cross-cutting parameters can be strengthened. It is not evidence
  and does not close parameter or acceptance gates.
- Route-level accessibility-loss diagnostics now write
  `data/validation/accessibility_loss.csv` and
  `data/validation/accessibility_loss_summary.md`. The current scaffold has 127
  directed edge-removal rows for `A -> D`, `A -> S`, and `R -> D`, including 22
  disconnected edge-removal cases. This supports critical-link review but is
  not calibrated accessibility evidence.
- Pilot scaffold sample/staged/full experiments now write separated output
  files under `results/realworld_pilot/`. These outputs are separated from the
  abstract `results/` files and remain scaffold-only.
- A small pilot scaffold sample experiment writes
  `results/realworld_pilot/pilot_sample_results.csv`,
  `results/realworld_pilot/pilot_sample_summary.csv`, and
  `results/realworld_pilot/pilot_result_manifest.json`.
- A separated multi-corridor candidate experiment writes
  `results/realworld_pilot/pilot_multi_corridor_results.csv`,
  `results/realworld_pilot/pilot_multi_corridor_summary.csv`, and
  `results/realworld_pilot/pilot_multi_corridor_manifest.json` for graph-scale
  review only.
- A separated full-profile multi-corridor candidate experiment writes
  `results/realworld_pilot/pilot_multi_corridor_full_results.csv`,
  `results/realworld_pilot/pilot_multi_corridor_full_summary.csv`, and
  `results/realworld_pilot/pilot_multi_corridor_full_manifest.json` for
  stronger graph-scale review only. It uses the same 7-policy, 9-scenario,
  30-seed matrix as the current full pilot.
- Deterministic sensitivity screening now writes
  `results/realworld_pilot/sensitivity_results.csv`,
  `results/realworld_pilot/sensitivity_summary.csv`, and
  `results/realworld_pilot/sensitivity_manifest.json`.
- SALib Morris screening now writes `results/realworld_pilot/morris_results.csv`,
  `results/realworld_pilot/morris_summary.csv`, and
  `results/realworld_pilot/morris_manifest.json`. These are formal scaffold
  indices, not calibrated real-world sensitivity evidence or Sobol indices.
- The sensitivity review packet writes
  `data/validation/sensitivity_review_packet.csv` and
  `data/validation/sensitivity_review_manifest.json`. It summarizes Morris
  diagnostic issues and method-review decisions, but it is not sensitivity
  acceptance, not a Sobol waiver, and not calibrated sensitivity evidence.
- The sensitivity strategy-readiness packet writes
  `data/validation/sensitivity_strategy_readiness_packet.csv`,
  `data/validation/sensitivity_strategy_readiness_manifest.json`, and
  `docs/sensitivity_strategy_readiness_packet.md`. It records current Morris
  output, graph-scope, method-decision, and missing-acceptance blockers, but it
  cannot close `data/manifests/sensitivity_acceptance.json`.
- The experiment strategy-readiness packet writes
  `data/manifests/experiment_strategy_readiness_packet.csv`,
  `data/manifests/experiment_strategy_readiness_manifest.json`, and
  `docs/experiment_strategy_readiness_packet.md`. It records current full-pilot
  scope, graph/input dependencies, row-count/checksum, scenario-policy-seed,
  CRN, and missing-acceptance review items, but it cannot close
  `data/manifests/experiment_acceptance.json`.
- The validation review packet writes
  `data/validation/validation_review_packet.csv` and
  `data/validation/validation_review_manifest.json`. It summarizes internal
  route-plausibility warnings, fallback benchmark warnings, optional OSRM
  snapshot/manifest status, raw-response retention counts,
  accessibility-loss coverage, validation-summary scope, and the
  benchmark-strategy decision requirement. It is not validation acceptance and
  does not create `data/manifests/validation_acceptance.json`.
- The validation strategy-readiness packet writes
  `data/validation/validation_strategy_readiness_packet.csv`,
  `data/validation/validation_strategy_readiness_manifest.json`, and
  `docs/validation_strategy_readiness_packet.md`. It records current validation
  blockers and human-review items, but it cannot close
  `data/manifests/validation_acceptance.json`.
- Full-pilot statistics generation now writes
  `results/realworld_pilot/tables/pilot_full_metric_ci.csv`,
  `results/realworld_pilot/tables/pilot_full_paired_delta_ci.csv`, and
  `results/realworld_pilot/tables/pilot_full_statistics_manifest.json`.
- Multi-corridor candidate statistics generation writes the matching
  `pilot_multi_corridor_metric_ci`, `pilot_multi_corridor_paired_delta_ci`, and
  `pilot_multi_corridor_statistics_manifest` artifacts for graph-scale review.
- Full-profile multi-corridor candidate statistics generation writes
  `pilot_multi_corridor_full_metric_ci`,
  `pilot_multi_corridor_full_paired_delta_ci`, and
  `pilot_multi_corridor_full_statistics_manifest` artifacts for graph-scale
  review.
- Current-vs-candidate graph-scale result comparison writes
  `data/validation/graph_scale_result_comparison.csv` and
  `data/validation/graph_scale_result_comparison_manifest.json`. The current
  comparison has 819 metric-level rows and remains review support only.
- The graph-scale strategy-readiness packet writes
  `data/validation/graph_scale_strategy_readiness_packet.csv`,
  `data/validation/graph_scale_strategy_readiness_manifest.json`, and
  `docs/graph_scale_strategy_readiness_packet.md`. It records current
  source-vs-analysis graph blockers and human-review items, but it cannot close
  `data/manifests/graph_scale_acceptance.json`.
- The full-graph smoke writes `data/validation/full_graph_smoke_manifest.json`
  for a two-row unreduced full bus-practical graph feasibility run. The
  full-graph runtime-readiness packet writes
  `data/validation/full_graph_runtime_readiness_packet.csv`,
  `data/validation/full_graph_runtime_readiness_manifest.json`, and
  `docs/full_graph_runtime_readiness_packet.md`; it records smoke scope,
  missing full-profile full-graph outputs, runtime-scope review, and
  downstream regeneration decisions without accepting full-graph execution.
- Pilot, sensitivity, Morris, and figure/table manifests record both the
  bus-practical source graph scale and the reduced analysis graph scale. This
  keeps the current corridor abstraction visible but does not accept it as the
  final study graph-scale method.
- The full-vs-reduced graph-scale route diagnostic now compares `A -> D`,
  `A -> S`, and `R -> D` on the full bus-practical graph and reduced analysis
  corridor. Current route-parity rows all pass for shortest-time path
  preservation. Current alternate-route rows have 3 pass and 6 warn statuses,
  making omitted alternate full-graph candidates visible without accepting the
  reduced corridor as the final graph-scale method.
- A candidate multi-corridor graph preserving the top 3 full-graph route
  candidates per canonical leg has 164 nodes and 246 edges. Its diagnostic has
  9 pass rows. A separated 32-row / 16-summary-row smoke-scale candidate
  experiment and a 1,890-row / 63-summary-row full-profile candidate
  experiment now run on that graph. They are still not accepted final-study
  evidence.
- Scaffold-only figure/table generation now writes PNGs under
  `results/realworld_pilot/figures/` and tables under
  `results/realworld_pilot/tables/`, including bottleneck attribution proxy,
  policy regime-map, and claim-boundary tables that block calibrated,
  operational, and route-plan claims.

Allowed language:

```text
quasi-real decision-support experiment
OSM-derived simulator input
open-map-derived road graph with documented assumptions
```

Avoid:

```text
calibrated real-world result
operational route plan
validated emergency response forecast
```

## Integration Notes

Use `realworld_network_config(region)` to obtain the current rail-link config
shape for `run_scenario(...)`. Use `build_simulator_graph(road_graph, region)`
to create the road graph passed to the scenario runner.

Before any result claim, run `assert_graph_ready(graph)` or inspect
`validate_graph_readiness(graph)`. If readiness fails, fix the input graph or
region spec instead of adding hidden shortcut edges.
