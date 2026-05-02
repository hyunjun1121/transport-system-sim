# Real-World Simulation Implementation Blueprint From Public Repository Research

## Goal

The project goal is to extract the strongest implementation ideas from public
transportation, resilience, routing, optimization, and reproducibility
repositories, then use those ideas to move this simulator as close as practical
to a real-world disrupted regional transport scenario.

The target is not to replace the current simulator with a large external
platform. The target is a layered implementation:

> open-data regional input + realistic network preprocessing + structured
> disruption generation + transparent micro-simulation + validation benchmarks
> + sensitivity analysis + reproducible outputs.

## Core Principle

Keep the current simulator as the authoritative scenario evaluator because it
already contains the project-specific strengths:

- queue-based passenger dispatch,
- finite vehicle fleets,
- bus-only and rail-bus multimodal movement,
- fixed-headway rail abstraction,
- transfer delay modeling,
- dynamic BPR-style road congestion,
- blocked and capacity-reduced disruption states,
- censoring-aware metrics,
- common-random-number paired experiments.

Public repositories should be used to improve the inputs, validation,
benchmarks, policy generation, and reproducibility around that simulator.

## Extracted Good Parts By Repository Family

### 1. OSM-Based Regional Road Network

Repos:

- `OSMnx`
- `Pyrosm`
- `GeoPandas`
- `Shapely`
- `h3-py`

Good parts to extract:

- Real road network extraction from OpenStreetMap.
- Graph conversion into a NetworkX-compatible structure.
- Edge geometry, length, road class, speed, and travel-time attributes.
- Region polygon clipping and reusable region registries.
- Local OSM PBF snapshots for repeatable multi-region experiments.
- Zone abstraction through H3 or administrative grids for sensitive locations.

Project implementation target:

- Replace manually defined toy links with OSM-derived road graphs.
- Store road edges with:
  - edge ID,
  - geometry,
  - length,
  - highway class,
  - free-flow speed,
  - travel time,
  - capacity proxy,
  - disruption exposure fields.
- Define assembly and destination inputs as zones or synthetic centroids.

### 2. Spatial Disruption And Hazard Overlay

Repos:

- `snail`
- `open-gira`
- `pyincore`
- `CLIMADA`

Good parts to extract:

- Vector-raster overlay workflow.
- Splitting road and rail geometries by exposure cells.
- Exposure-to-functionality logic.
- Reproducible infrastructure risk pipeline structure.

Project implementation target:

- Create a disruption preprocessing module that maps spatial exposure to edge
  states:
  - normal,
  - capacity reduced,
  - blocked.
- Support three scenario families:
  - random degradation baseline,
  - critical-link disruption,
  - spatial hazard-overlay disruption.
- If no real hazard raster is available, use documented scenario polygons,
  flood-prone buffers, low-lying corridors, or corridor exposure zones and label
  them as scenario-based.

### 3. Network Resilience And Critical-Link Metrics

Repos:

- `NetworkX`
- `GOSTnets`
- `transcrit`
- `pysal/access`
- `Networkit`

Good parts to extract:

- Betweenness and centrality-based criticality.
- Connectivity and min-cut concepts.
- Accessibility loss metrics.
- OD disconnection and alternative-route availability.
- Travel-time and service-reachability loss.

Project implementation target:

- Add metrics that identify why a strategy fails:
  - origin access bottleneck,
  - feeder road bottleneck,
  - rail access bottleneck,
  - rail trunk bottleneck,
  - transfer bottleneck,
  - last-mile bottleneck,
  - destination access bottleneck.
- Add critical-link disruption scenarios using high-betweenness or high-flow
  edges.
- Add accessibility loss from assembly zones to rail access nodes and from rail
  egress nodes to destination zones.

### 4. Transit And Multimodal Validation

Repos:

- `gtfs-validator`
- `gtfs_kit`
- `r5py`
- `R5`
- `OpenTripPlanner`
- `routingpy`
- `OSRM`
- `Valhalla`

Good parts to extract:

- GTFS feed validation before use.
- Station, stop, route, trip, service-window, and headway summaries.
- Independent road and multimodal travel-time matrices.
- Routing-engine plausibility checks.

Project implementation target:

- Build a rail input table from GTFS where available.
- If GTFS is unavailable, build a documented rail-assumption table from public
  timetables or explicit assumptions.
- Compare simulator road and multimodal travel times against at least one
  routing benchmark.
- Treat benchmarks as plausibility checks, not ground truth.

### 5. Traffic And Congestion Benchmarking

Repos:

- `UXsim`
- `SUMO`
- `AequilibraE`
- `Path4GMNS`

Good parts to extract:

- Mesoscopic dynamic network loading ideas.
- Microscopic or corridor-level validation when needed.
- Assignment, skims, and OD matrix concepts.
- BPR and flow-capacity calibration workflows.

Project implementation target:

- Keep rolling-window BPR as the default transparent model.
- Use UXsim or assignment tools only to check whether BPR outputs are plausible
  under selected pilot scenarios.
- Use SUMO only for a small corridor benchmark if the paper needs an external
  high-fidelity comparison.

### 6. Fleet Optimization And Policy Generation

Repos:

- `OR-Tools`
- `PyVRP`
- `VROOM`
- `Pyomo`
- `VRPLIB`

Good parts to extract:

- Capacity-constrained assignment.
- Fleet allocation.
- Vehicle routing with time windows.
- Min-cost flow and dispatch optimization.
- Standard VRP benchmark discipline.

Project implementation target:

- Do not replace simulation with optimization.
- Use optimization to generate candidate policies:
  - increased feeder capacity,
  - redundant last-mile fleet,
  - vehicle allocation by zone,
  - staggered dispatch,
  - contingency routing.
- Evaluate those policies with the current stochastic simulator.

### 7. Sensitivity, Reproducibility, And Reporting

Repos:

- `SALib`
- `Frictionless`
- `Papermill`
- `Quarto`
- `Streamlit`
- `Snakemake`
- `DVC`

Good parts to extract:

- Morris or Sobol global sensitivity analysis.
- CSV schema validation.
- Parameterized notebook execution.
- Reproducible report builds.
- Interactive scenario dashboard.
- Pipeline and artifact versioning when outputs grow.

Project implementation target:

- Add sensitivity analysis for:
  - passenger volume,
  - arrival variability,
  - fleet sizes,
  - dispatch intervals,
  - road traffic multiplier,
  - disruption severity,
  - capacity-reduction factor,
  - rail headway,
  - rail capacity,
  - transfer delay,
  - turnaround time.
- Package result CSVs with schemas and metadata.
- Build figures and tables from reproducible notebooks or scripted workflows.

## Implementation Phases

### Phase 1: Real-World Network Input

Build:

- region registry,
- OSM road graph extractor,
- OSM edge-to-simulation adapter,
- zone-based OD input format,
- graph connectivity checks.

Primary repo ideas:

- OSMnx graph extraction,
- Pyrosm reproducible PBF ingestion,
- GeoPandas/Shapely spatial joins,
- H3-style zone abstraction.

### Phase 2: Realistic Disruption Generation

Build:

- random disruption generator,
- critical-link disruption generator,
- spatial overlay disruption generator,
- exposure-to-disruption rule table.

Primary repo ideas:

- snail vector-raster overlay,
- open-gira risk workflow structure,
- transcrit criticality metrics.

### Phase 3: Multimodal And Routing Validation

Build:

- GTFS validation workflow,
- rail headway/capacity table,
- station access and egress node matching,
- road and multimodal benchmark comparison.

Primary repo ideas:

- gtfs-validator feed QA,
- gtfs_kit schedule summaries,
- r5py multimodal matrices,
- routingpy/OSRM/Valhalla travel-time checks.

### Phase 4: Policy Alternatives

Build:

- direct bus-only,
- baseline rail-bus multimodal,
- multimodal with redundant last-mile fleet,
- multimodal with increased feeder capacity,
- staggered dispatch,
- adaptive rerouting,
- fleet shortage,
- rail delay or partial rail unavailability.

Primary repo ideas:

- OR-Tools assignment and min-cost flow,
- PyVRP fleet routing,
- current simulator for stochastic evaluation.

### Phase 5: Scientific Validation And Sensitivity

Build:

- internal validation tests,
- external plausibility checks,
- benchmark comparison tables,
- SALib Morris or Sobol analysis,
- policy regime map.

Primary repo ideas:

- SALib global sensitivity,
- Frictionless data schemas,
- Papermill/Quarto reproducible analysis,
- Streamlit decision dashboard.

## Near-Term Clone Set

The `cloned_repo/` directory is for local reference clones only. It is ignored
by git. These clones are not vendored dependencies and should not be committed.

Clone priorities:

1. Core implementation references:
   - OSMnx
   - Pyrosm
   - snail
   - gtfs_kit
   - gtfs-validator
   - SALib
   - Frictionless
   - h3-py
2. Next implementation references:
   - GOSTnets
   - pysal/access
   - r5py
   - routingpy
   - OR-Tools
   - PyVRP
   - UXsim
3. Benchmark and metric references:
   - transcrit
   - Path4GMNS
   - AequilibraE
   - OSRM
   - Valhalla

Heavy full-platform tools such as SUMO, MATSim, and OpenTripPlanner should not
be first-pass clones unless a specific benchmark experiment is accepted. They
are too large and would distract from the near-term real-world implementation.
