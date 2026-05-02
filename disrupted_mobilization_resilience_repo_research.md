# Public Repository Research for a Disrupted Regional Mobilization Transport Resilience Framework

## Purpose

This document summarizes additional public GitHub repositories that can help
reframe this project as a:

> disrupted regional mobilization transport resilience framework

The research was split across six GPT-5.5 high subagents, each responsible for
one feature area:

1. Transport network resilience metrics and critical-link analysis.
2. Disruption scenario generation and hazard-overlay modeling.
3. Emergency evacuation, mass movement, and multimodal simulation engines.
4. Constrained fleet logistics and contingency routing.
5. Public-data validation and calibration.
6. Resilience visualization, reproducibility, and decision-support reporting.

The goal is not to replace the current simulation with a large external
platform. The goal is to identify which repositories should become practical
dependencies, which should be used as benchmark engines, and which should only
inform model design.

## Executive Recommendation

Keep the current Python micro-simulation as the core scenario engine. It already
models finite fleets, dispatch policies, rail headways, transfers, disruptions,
BPR congestion, censoring, and paired experiments. The next research upgrade
should add external repositories as surrounding evidence layers:

1. Use `NetworkX` and `OSMnx` as the core graph and real-road-network layer.
2. Use `snail` to overlay raster hazard or disruption intensity fields onto
   road and rail edge geometries.
3. Add a local degradation mapper that converts exposure values into current
   `blocked` and `capacity_reduction` disruption states.
4. Add critical-link and accessibility-loss metrics using `NetworkX`, with
   `transcrit`, `GOSTnets`, and `pysal/access` as metric references.
5. Use `gtfs-validator`, `gtfs_kit`, and optionally `r5py` for public transit
   feed validation and multimodal travel-time benchmarking.
6. Use `OR-Tools` or `PyVRP` only as an optional planning layer for optimized
   fleet assignment or contingency routing, not as the main simulation engine.
7. Use `UXsim`, `SUMO`, `MATSim`, `R5`, `OpenTripPlanner`, `Valhalla`, and
   `AequilibraE` as external benchmarks or high-cost extensions.
8. Use `Streamlit`, `Papermill`, `Frictionless`, and `Quarto` to turn results
   into a reusable decision-support and reproducible research package.

The minimum credible stack for the next stage is:

```text
networkx
osmnx
geopandas
shapely
snail
gtfs-validator
gtfs_kit
SALib
frictionless
```

Optional next-stage additions:

```text
r5py
routingpy
OR-Tools or PyVRP
UXsim
Streamlit
Papermill
Quarto
```

## Architecture Recommendation

### Layer 1: Region-Reusable Network Input

Use `OSMnx` as the first real-network implementation path. It already exports
road networks to `NetworkX`, which matches the current in-repo architecture.

Recommended use:

- Extract a pilot regional road network from OSM.
- Simplify and clean the graph.
- Add edge length, speed, travel time, highway class, and estimated capacity.
- Persist a reproducible network snapshot.
- Keep sensitive destinations as zones or synthetic nodes rather than exact
  coordinates.

Use `Pyrosm` later if repeated multi-region runs require pinned OSM PBF
snapshots instead of live Overpass queries.

### Layer 2: Disruption And Hazard Overlay

Use `snail` as the most practical disruption-overlay dependency. It can split
vector road and rail geometries by raster cells and attach raster values such as
flood depth, hazard intensity, or abstract exposure scores.

Recommended use:

- Convert OSM edges to line geometries.
- Overlay hazard or disruption rasters onto edges.
- Compute edge-level exposure values.
- Apply a local degradation rule:
  - low exposure: no disruption
  - medium exposure: capacity reduction
  - high exposure: blockage
- Feed those edge states into the existing `disruptions.py` and `traffic.py`
  semantics.

Use `open-gira`, `pyincore`, `CLIMADA`, `oq-engine`, and NOAA flood mapping as
methodological references or external benchmarks. They are too heavy for the
first integration pass.

### Layer 3: Resilience Metrics

Keep `NetworkX` as the first implementation tool for criticality and robustness
metrics.

Recommended metrics:

- shortest-path travel-time increase after edge degradation
- disconnected OD pairs
- completion-rate loss
- censored-passenger increase
- edge betweenness or OD-flow-weighted betweenness
- min-cut or bridge-like vulnerability
- accessibility loss to rail heads, staging zones, and destination zones
- alternative-route availability
- bottleneck contribution to penalized makespan

Use `transcrit` as a metric-design reference because it collects transport
criticality measures such as accessibility loss, efficiency loss, link
betweenness, min-cut, OD k-connectivity, V/C, and unsatisfied demand. Treat it
as conceptual reference code, not as a packaged dependency.

Use `pysal/access` if the paper needs formal spatial accessibility indicators,
and use `Networkit` only if OSM-scale criticality sweeps become too slow in
plain `NetworkX`.

### Layer 4: Transport And Evacuation Benchmarks

Do not replace the current simulator with SUMO or MATSim in the next pass. They
are valuable, but adopting them would turn the project into a new traffic
platform integration effort.

Recommended use:

- `UXsim`: optional Python-native mesoscopic road-congestion benchmark if the
  rolling-window BPR model becomes insufficient.
- `r5py`: optional multimodal accessibility and travel-time matrix benchmark
  using OSM and GTFS.
- `SUMO`: external microscopic road-evacuation benchmark for a small pilot
  corridor.
- `MATSim`: methodological benchmark for large-scale agent-based transport,
  not a direct dependency.
- `OpenTripPlanner`, `R5`, and `Valhalla`: routing and multimodal benchmark
  engines, not the core scenario model.

The paper can benefit from one benchmark comparison, but the core contribution
should remain a controlled resilience decision framework rather than a claim
that the project is a full traffic simulator.

### Layer 5: Fleet Optimization And Contingency Routing

The current simulator dispatches finite fleets according to scenario policies.
That should remain the execution model. Optimization tools should generate
candidate policies or benchmark plans.

Recommended use:

- `OR-Tools`: first choice for assignment, min-cost flow, vehicle routing, and
  capacity-constrained dispatch experiments.
- `PyVRP`: strong alternative for high-performance VRP with heterogeneous
  fleets, time windows, multi-depot settings, and multi-trip/reloading.
- `VROOM` or `pyvroom`: optional route optimizer if a service-oriented routing
  stack is accepted.
- `Pyomo`: later-stage modeling tool for robust or stochastic resource
  allocation, not a first-pass dependency.
- `VRPLIB` and `PyVRP/Instances`: external benchmarks for reporting that the
  optimization layer behaves sensibly on standard logistics instances.

Recommended project pattern:

1. The optimizer proposes dispatch intervals, vehicle assignments, station
   choices, or last-mile capacity expansion.
2. The in-repo simulator evaluates those policies under stochastic arrivals,
   disruptions, congestion, and censoring.
3. Results are compared using completion probability, censored personnel,
   95th-percentile arrival time, resource efficiency, and bottleneck
   attribution.

### Layer 6: Validation And Calibration

Use public-data validation tools to prevent the research from looking like an
arbitrary simulation case.

Recommended use:

- `gtfs-validator`: validate any static GTFS feed before using it.
- `gtfs_kit`: extract route, service, stop, trip, and headway summaries in
  Python.
- `Mobility Database catalogs` and `Transitland Atlas`: discover and record
  feed sources, with feed-specific license checks.
- `routingpy`: compare travel-time estimates across OSRM, Valhalla, OTP,
  GraphHopper, or other routing services.
- `OSRM` or `Valhalla`: independent road-routing and matrix benchmarks.
- `r5py`: independent multimodal travel-time and accessibility benchmark.

Validation should not claim that routing-engine outputs are ground truth. They
should be used as plausibility checks:

- Are OSM-derived road travel times in a realistic range?
- Are rail headways and station-to-station times plausible?
- Does multimodal access time roughly match an independent routing engine?
- Do disrupted-route travel times move in the expected direction?
- Are bottleneck rankings stable across reasonable speed assumptions?

### Layer 7: Reproducibility, Dashboarding, And Report Packaging

Use lightweight tools around the existing CSV and PNG workflow.

Recommended use:

- `Frictionless`: define schemas for result CSVs, scenario tables, and public
  benchmark packages.
- `Papermill`: parameterize notebooks for repeatable scenario summaries and
  figure generation.
- `Quarto`: produce publication-style HTML/PDF/DOCX reports when the evidence
  package becomes heavier than the current `generate_report.py`.
- `Streamlit`: create an internal decision-support dashboard for scenario
  comparison, filters, KPI tables, and plots.
- `Great Tables`: optional polished decision tables for paper/report outputs.
- `Snakemake` or `DVC`: only after experiment artifacts become large enough to
  justify workflow management overhead.

## Repository Shortlist

| Repo | URL | License | Recommended role | Project use |
|---|---|---:|---|---|
| NetworkX | https://github.com/networkx/networkx | BSD-3 | Core dependency | Criticality, connectivity, shortest paths, robustness metrics |
| OSMnx | https://github.com/gboeing/osmnx | MIT | Core dependency | Real regional road graph extraction into NetworkX |
| Pyrosm | https://github.com/pyrosm/pyrosm | MIT | Optional module | Reproducible OSM PBF ingestion |
| snail | https://github.com/nismod/snail | MIT | Core dependency | Raster hazard overlay onto road and rail edges |
| open-gira | https://github.com/nismod/open-gira | MIT | External benchmark | Reproducible infrastructure risk workflow reference |
| GOSTnets | https://github.com/worldbank/GOSTnets | MIT | Optional module | Accessibility and travel-time loss workflows |
| transcrit | https://github.com/bramkaarga/transcrit | BSD-3 | Conceptual reference | Transport criticality metric design |
| pysal/access | https://github.com/pysal/access | BSD-3 | Optional module | Spatial accessibility loss indicators |
| Networkit | https://github.com/networkit/networkit | MIT | Optional module | Faster graph centrality and connectivity on large networks |
| r5py | https://github.com/r5py/r5py | GPL-3-or-MIT | External benchmark | Multimodal travel-time and accessibility matrices |
| R5 | https://github.com/conveyal/r5 | MIT | External benchmark | OSM and GTFS multimodal routing engine |
| OpenTripPlanner | https://github.com/opentripplanner/OpenTripPlanner | LGPL-3 | External benchmark | End-to-end multimodal routing plausibility |
| Valhalla | https://github.com/valhalla/valhalla | MIT | External benchmark | Road and multimodal routing, matrices, map matching |
| OSRM | https://github.com/Project-OSRM/osrm-backend | BSD-2 | External benchmark | Road routing, matrices, map matching |
| routingpy | https://github.com/mthh/routingpy | Apache-2 | Optional module | Python wrapper for multiple routing engines |
| SUMO | https://github.com/eclipse-sumo/sumo | EPL-2 | External benchmark | Microscopic traffic or evacuation comparison |
| UXsim | https://github.com/toruseo/UXsim | MIT | Optional module | Python-native mesoscopic road traffic benchmark |
| MATSim | https://github.com/matsim-org/matsim-libs | GPL-2 | External benchmark | Large-scale agent-based transport reference |
| FleetPy | https://github.com/TUM-VT/FleetPy | MIT | Optional module | Fleet simulation design reference |
| OR-Tools | https://github.com/google/or-tools | Apache-2 | Optional core layer | Dispatch optimization, VRP, min-cost flow, assignment |
| PyVRP | https://github.com/PyVRP/PyVRP | MIT | Optional core layer | High-performance VRP policy generation |
| VROOM | https://github.com/VROOM-Project/vroom | BSD-2 | Optional module | Fast route optimization with duration matrices |
| pyvroom | https://github.com/VROOM-Project/pyvroom | BSD-2 | Optional module | Python access to VROOM |
| Pyomo | https://github.com/Pyomo/pyomo | BSD | Optional module | Later robust or stochastic optimization models |
| mpi-sppy | https://github.com/Pyomo/mpi-sppy | Mixed visible | Optional module | Scenario-based stochastic programming experiments |
| VRPLIB | https://github.com/PyVRP/VRPLIB | MIT | External benchmark | Standard VRP benchmark instance support |
| gtfs-validator | https://github.com/MobilityData/gtfs-validator | Apache-2 | Core dependency | Static GTFS feed validation |
| gtfs-realtime-validator | https://github.com/MobilityData/gtfs-realtime-validator | Apache-2 | Optional module | GTFS-RT quality checks |
| gtfs_kit | https://github.com/araichev/gtfs_kit | MIT | Core dependency | Python GTFS analysis and headway summaries |
| Mobility Database catalogs | https://github.com/MobilityData/mobility-database-catalogs | Apache-2 | Optional module | GTFS feed discovery and metadata |
| Transitland Atlas | https://github.com/transitland/transitland-atlas | CC-BY-4 | Optional module | Cross-check GTFS feed registry |
| AequilibraE | https://github.com/AequilibraE/aequilibrae | MIT plus attribution clause | External benchmark | Traffic assignment, skims, OD matrix workflows |
| Path4GMNS | https://github.com/jdlph/Path4GMNS | Apache-2 | External benchmark | GMNS assignment, ODME, accessibility |
| Frictionless | https://github.com/frictionlessdata/frictionless-py | MIT | Core dependency | CSV schema and benchmark data package validation |
| Papermill | https://github.com/nteract/papermill | BSD-3 | Core dependency | Parameterized reproducible notebooks |
| Quarto | https://github.com/quarto-dev/quarto-cli | MIT | Core dependency | Publication-style reports from notebooks and Markdown |
| Streamlit | https://github.com/streamlit/streamlit | Apache-2 | Optional core layer | Scenario dashboard and decision support |
| Great Tables | https://github.com/posit-dev/great-tables | MIT | Optional module | Polished result and decision tables |
| Snakemake | https://github.com/snakemake/snakemake | MIT | Optional module | Reproducible experiment pipeline |
| DVC | https://github.com/iterative/dvc | Apache-2 | Optional module | Data and artifact versioning |

## Recommended Adopt, Evaluate, Benchmark, Reference Split

### Adopt Now

These fit the current architecture and directly strengthen the resilience
framing:

- `NetworkX`
- `OSMnx`
- `GeoPandas`
- `Shapely`
- `snail`
- `gtfs-validator`
- `gtfs_kit`
- `SALib`
- `Frictionless`

### Evaluate Next

These are useful but should be integrated only after the first real-network and
hazard-overlay prototype works:

- `Pyrosm`
- `GOSTnets`
- `pysal/access`
- `r5py`
- `routingpy`
- `OR-Tools`
- `PyVRP`
- `UXsim`
- `Streamlit`
- `Papermill`
- `Quarto`

### Benchmark Only

These are strong tools, but they are too heavy to be first-pass dependencies:

- `SUMO`
- `MATSim`
- `OpenTripPlanner`
- `R5`
- `Valhalla`
- `OSRM`
- `AequilibraE`
- `Path4GMNS`
- `open-gira`

### Reference Only

These are valuable for concepts, metric vocabulary, or architecture patterns,
but should not be copied into the codebase:

- `transcrit`
- `RNDS`
- `disrupt-sc`
- `pyincore`
- `CLIMADA`
- `oq-engine`
- `NOAA-OWP/inundation-mapping`
- `WNTR`
- `fmdtools`
- `infra-risk-vis`
- `DAFNI-NIRD`

## How These Repositories Support the New Research Frame

### Research Need: Real Regional Network

Use:

- `OSMnx` for road extraction.
- `Pyrosm` for reproducible PBF-based extraction.
- `GeoPandas` and `Shapely` for region boundaries, clipping, joins, and zone
  abstraction.

Output:

- A reusable region input pipeline that can run on Songpa-gu and later on other
  regions with the same schema.

### Research Need: Disrupted Network States

Use:

- `snail` for hazard overlay.
- Local rules for converting exposure into `blocked` or
  `capacity_reduction`.
- `open-gira` as a benchmark for reproducible risk workflows.

Output:

- Scenario tables where disruption is tied to explicit spatial exposure or
  structured degradation assumptions rather than arbitrary random failure only.

### Research Need: Resilience Metrics

Use:

- `NetworkX` for graph metrics.
- `transcrit` as a metric menu.
- `pysal/access` for accessibility loss.
- `Networkit` only when graph size demands it.

Output:

- Critical-link rankings.
- Accessibility-loss maps.
- OD completion vulnerability.
- Bottleneck attribution for penalized makespan and censored personnel.

### Research Need: Multimodal Plausibility

Use:

- `gtfs-validator` and `gtfs_kit` for feed validation and schedule summaries.
- `r5py`, `R5`, or `OpenTripPlanner` for travel-time matrix checks.
- `Valhalla` or `OSRM` for road travel-time plausibility.

Output:

- Evidence that rail headways, access times, last-mile paths, and road travel
  times are within defensible public-data ranges.

### Research Need: Policy Alternatives

Use:

- `OR-Tools` or `PyVRP` to generate candidate fleet allocation and contingency
  routing policies.
- Current simulator to evaluate those policies under stochastic disruption and
  queueing.

Output:

- Policy scenarios beyond bus-only vs rail-bus:
  - last-mile redundancy
  - feeder capacity expansion
  - staggered dispatch
  - rail delay or partial unavailability
  - fleet shortage
  - adaptive rerouting

### Research Need: Reproducible Paper Package

Use:

- `Frictionless` for result schema validation.
- `Papermill` for parameterized analysis notebooks.
- `Quarto` for publication-style reports.
- `Streamlit` for stakeholder dashboard prototypes.

Output:

- A reproducible evidence package with input metadata, scenario definitions,
  result schemas, figures, and sensitivity summaries.

## Implementation Roadmap

### Phase 0: Guardrails

Do this before adding dependencies:

- Keep the current simulator as the authoritative scenario evaluator.
- Define exact interfaces for external data:
  - regional road graph
  - transit feed summary
  - OD zones
  - disruption edge states
  - scenario policy table
  - validation metrics
- Keep sensitive destinations zone-based or synthetic.
- Record license and attribution obligations for every data and code source.

### Phase 1: Real Network And Criticality Prototype

Target repositories:

- `OSMnx`
- `GeoPandas`
- `Shapely`
- `NetworkX`

Deliverables:

- `region_id` input schema.
- OSM-derived road graph for one pilot region.
- Edge attribute mapping into current simulation fields.
- Connectivity and shortest-path sanity checks.
- Initial critical-link ranking.

### Phase 2: Hazard Overlay And Disruption Scenarios

Target repositories:

- `snail`
- `open-gira` as reference

Deliverables:

- Edge exposure table.
- Exposure-to-degradation rule.
- Scenarios for full blockage and capacity reduction.
- Comparison between random disruption and spatially structured disruption.

### Phase 3: Multimodal Validation

Target repositories:

- `gtfs-validator`
- `gtfs_kit`
- `r5py`
- `routingpy`

Deliverables:

- Validated public transit feed metadata.
- Rail headway and station travel-time summaries.
- Road and multimodal travel-time plausibility checks.
- Documented differences between routing-engine estimates and simulator
  outputs.

### Phase 4: Resilience Metrics And Policy Experiments

Target repositories:

- `NetworkX`
- `pysal/access`
- `OR-Tools` or `PyVRP`
- `SALib`

Deliverables:

- Accessibility-loss metrics.
- Critical-link and bottleneck attribution.
- Sensitivity analysis over disruption, fleet, transfer, and rail assumptions.
- Optimizer-generated policy alternatives evaluated by the simulator.

### Phase 5: Reproducible Research Package

Target repositories:

- `Frictionless`
- `Papermill`
- `Quarto`
- `Streamlit`

Deliverables:

- CSV schemas.
- Scenario metadata package.
- Parameterized analysis notebooks.
- Publication-ready report build.
- Internal dashboard for scenario exploration.

## Main Risks

### License Risk

GPL, LGPL, AGPL, or custom attribution clauses may limit direct dependency use
or require additional review. Keep GPL-heavy tools as external benchmarks unless
the licensing path is explicitly accepted.

High-attention examples:

- `MATSim`: GPL-2
- `CLIMADA`: GPL-3
- `OSM2GMNS`: GPL-3
- `oq-engine`: AGPL-3
- `OpenTripPlanner`: LGPL-3
- `AequilibraE`: MIT plus attribution clause

### Overengineering Risk

SUMO, MATSim, OTP, Valhalla, and AequilibraE can consume the project. They
should be used only when they answer a specific validation or benchmark question.

### Data Realism Risk

OSM and GTFS do not automatically make the model real. They provide network and
schedule structure, but the paper still needs:

- capacity assumptions
- traffic-volume assumptions
- station access assumptions
- transfer processing assumptions
- disruption-fragility assumptions
- validation against public or literature ranges

### Security And Sensitivity Risk

Do not publish exact sensitive destination coordinates or operationally specific
mobilization details. Use:

- zone centroids
- synthetic destination nodes
- H3 or administrative zones
- aggregated OD counts
- scenario abstractions

## Final Position

The strongest repository strategy is a layered strategy:

- Keep the current simulator.
- Add OSM-based regional network input.
- Add spatially structured disruption overlays.
- Add resilience and accessibility metrics.
- Add public-data validation.
- Add optional optimization-generated policies.
- Package outputs reproducibly.

This supports a stronger paper claim:

> An open-data, region-reusable decision framework can identify when multimodal
> mobilization transport is resilient or fragile under disrupted regional
> networks and constrained fleet operations.

That claim is more defensible than claiming that the current simulator directly
predicts real wartime transport performance.
