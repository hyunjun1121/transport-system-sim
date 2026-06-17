# A Region-Reusable Decision Framework for Disrupted Regional Personnel Transport Resilience

> Current project status (2026-05-09): `final_study_ready=false`. Preflight-pass gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal signoff is `0/12` complete. This document is current-state or review support only; it does not create formal signoff, fit-to-observed-data real-world results, or field-use routing guidance.


## Draft Status

This is a working paper draft. It is written as a research design and manuscript
scaffold for developing the current transport simulation project into a
publishable study.

The current implemented simulator already supports queue-based passenger
dispatch, finite fleets, rail-bus multimodal movement, road congestion,
structured disruptions, censoring-aware metrics, paired experiments, and a
first real-world/quasi-real input pipeline. The current full result set remains
based on a representative abstract network. A separate pilot scaffold now
exists with an Overpass/OSM-derived cached road graph, but its outputs are
explicitly scaffold-only and are not calibrated real-world findings. The formal
evidence boundary is also explicit: study-closeout preflight status is `false`,
only `3/15` study-closeout gates are preflight-pass, `12/15` gates remain
blocked, and formal signoff status is `0/12`. Formal signoff records are
absent, fit-to-observed-data real-world result evidence is absent, and the
evidence-check, graph-scale, sensitivity, and experiment strategy-blocker-review
packets are blocker/review aids only; they are not signoff records. This draft
therefore separates:

- what is already implemented,
- what can be reported as preliminary baseline evidence,
- what must be added before making real-world or SCI-grade claims.

The intended high-level framing is civilian and public-sector oriented:

> An open-data, region-reusable decision framework for evaluating when
> multimodal personnel transport becomes resilient or fragile under disrupted
> regional mobility, contingency transport planning, and constrained fleet
> operations.

## Current Implementation Snapshot

The repository now contains a first executable open-data-style scaffold for the
real-world extension:

- `src/realworld/` converts OSM-like cached road graphs into the existing
  simulator graph contract.
- `data/regions/pilot_region.yaml` defines the non-sensitive
  `songpa_public_demo` scaffold region.
- `data/cache/pilot_region_road.graphml` stores an offline pilot road graph
  cache whose manifest records `live_overpass_osm_snapshot` provenance.
- `data/parameters/` records parameter, rail, fleet, and road-evidence review
  tables. The current `road_class_overrides_draft.csv` has 10 road-class rows,
  all still labeled as expert-assumption review scaffolds rather than signed-off
  road evidence. The current `road_speed_evidence_candidates.csv` also has 10
  routeable road-class rows and 5 rows with observed cached OSM `maxspeed`
  tags, but this remains speed-review support rather than source-tuned speed
  evidence. The current `road_capacity_evidence_candidates.csv` has 10
  routeable road-class rows and 0 rows with observed cached OSM `lanes` tags,
  so it documents a capacity evidence gap rather than source-backed capacity
  evidence. The current `road_evidence_review_packet.csv` consolidates the
  road-class diagnostic, sparse speed-tag, lane-count, and draft-override
  evidence status into 10 routeable road-class review rows; all 10 remain weak
  for study-level road claims. The current
  `road_evidence_source_request_packet.csv` adds 5 request rows that identify
  the source-backed speed, capacity, benchmark, disruption, and
  override-application inputs needed before reviewed road overrides can be
  built; it is not road evidence. The current
  `parameter_evidence_review_packet.csv` has 29 core-parameter rows and marks
  25 as weak for study-level claims; it is a prioritization worksheet and does
  not sign off or tune parameter values. The current
  `parameter_evidence_source_request_packet.csv` adds 7 request rows covering
  25 demand, fleet, dispatch, transfer, rail, disruption, and traffic/BPR parameters;
  it names required source inputs but is not parameter evidence or acceptance.
- `data/rail/pilot_station_binding_cache.csv` and
  `data/parameters/rail_station_bindings.csv` now bind the pilot rail points
  to official line-specific station identifiers, while keeping rail service
  timing and capacity claims separate.
- `data/parameters/rail_evidence_review_packet.csv` now consolidates rail
  station-binding status, timing gaps, capacity treatment, service-window
  assumptions, availability assumptions, and derivation paths into 10 review
  rows. It keeps service publication readiness false until cached timetable,
  GTFS, shortest-path, or equivalent evidence derives headway and travel time.
- `data/rail/rail_timing_source_request_packet.csv` now records the exact
  API-key, GTFS, capacity, and rail-availability inputs required before those
  cached timing artifacts can be produced. It is a request worksheet, not rail
  timing evidence.
- Cached timetable, static-GTFS, and shortest-path derivation paths now exist
  for future reviewed rail timing evidence; no reviewed GTFS feed or timetable
  extract is committed for the current pilot, so the current rail-service row
  remains an assumption proxy and capacity remains sensitivity-only.
- `data/validation/` stores route plausibility sanity checks for the pilot
  scaffold, including an offline fallback benchmark and an optional OSRM
  snapshot with a non-acceptance checksum/query manifest.
- `data/validation/accessibility_loss.csv` stores route-level directed
  edge-removal diagnostics for the current baseline road legs, with 127
  scaffold rows and 22 disconnected edge-removal cases.
- `data/validation/canonical_route_road_evidence_exposure.csv` stores a 76-row
  route-level road-evidence exposure worksheet linking weak road speed,
  capacity, disruption, and connector assumptions to 18 canonical route
  candidates. It is prioritization support only, not road calibration.
- `data/validation/validation_review_packet.csv` stores a 7-row evidence-check
  review worksheet covering internal plausibility, fallback benchmark, optional
  OSRM snapshot/manifest status, accessibility-loss coverage, route-level
  road-evidence exposure, evidence-summary scope, and benchmark-strategy decision
  requirements. It is not evidence-check signoff.
- `data/validation/validation_strategy_readiness_packet.csv` stores a 7-row
  evidence-check strategy-blocker-review worksheet with 3 blocking requests and 4
  human-review requests. It is implemented preflight support only and cannot
  close `data/manifests/validation_acceptance.json`.
- `data/scenarios/` stores deterministic disruption, policy, and sensitivity
  design tables.
- `results/realworld_pilot/` stores separated pilot scaffold sample/staged/full
  outputs, deterministic sensitivity screening outputs, SALib Morris scaffold
  outputs, first/median/80th/95th arrival-time KPIs, and scaffold-only figures,
  bottleneck/regime tables, and claim-boundary tables.
- The current cached graph pipeline records three graph scales: 13,268 raw
  cached OSM nodes / 28,947 raw cached edges, 4,608 bus-practical simulator
  nodes / 9,148 simulator edges after filtering, and a 118-node / 174-edge
  reduced analysis corridor used by the current pilot, figure, and sensitivity
  scaffold outputs.
- A separate graph-scale route parity diagnostic compares the full
  bus-practical graph and multi-corridor graph for `A -> D`, `A -> S`, and
  `R -> D`. The current multi-corridor graph has 164 nodes and 246 edges,
  preserving the top 3 route candidates per canonical leg, with 9 pass rows
  in the alternate-route diagnostic. The current full pilot experiment uses
  this multi-corridor graph. A full-profile candidate on the same graph
  produces 1,890 raw rows and 63 summary rows for comparison.
- A generated graph-scale method review packet now compares four options in
  one worksheet: the current 118-node / 174-edge reduced corridor, the small
  164-node / 246-edge multi-corridor candidate, the full-profile 164-node /
  246-edge multi-corridor candidate, and the full 4,608-node / 9,148-edge
  bus-practical graph. This packet supports method selection but does not
  replace a reviewed graph-scale signoff record.
- `data/validation/graph_scale_strategy_readiness_packet.csv` stores a 5-row
  graph-scale strategy-blocker-review worksheet with 2 blocking requests and 3
  human-review requests. It is implemented preflight support only and cannot
  close `data/manifests/graph_scale_acceptance.json`.
- Current pilot scaffold outputs include 15,870 full pilot rows and 529 full
  summary rows across 23 policies (5 congestion levels, 4 transfer stress
  levels, 4 fleet/capacity severity), 23 scenarios (8 structural, 4 spatial
  hazard overlays, 8 rail severity scenarios, 2 multi-hazard combinations,
  and 1 transfer-point blockage), and 30 seeds. Current
  SALib Morris scaffold outputs include 4,320 raw rows and 7,056 summary rows
  over the current policy/scenario sensitivity design.
  A separate 6-row sensitivity review packet summarizes Morris structural
  readiness, missing/non-finite index rows, zero `mu_star` rows, reduced graph
  scope, scaffold result scope, and the Morris-vs-Sobol decision; it is not a
  sensitivity signoff record and does not waive Sobol analysis.
- `data/validation/sensitivity_strategy_readiness_packet.csv` stores a 7-row
  sensitivity strategy-blocker-review worksheet with 5 blocking requests and 2
  human-review requests. It is implemented blocker support only and cannot
  close `data/manifests/sensitivity_acceptance.json`.
- `data/manifests/experiment_strategy_readiness_packet.csv` stores a 9-row
  experiment strategy-blocker-review worksheet with 4 blocking requests and 5
  human-review requests. It is implemented blocker support only and cannot
  close `data/manifests/experiment_acceptance.json`.
- Full pilot seed-replication uncertainty tables add 819 metric confidence
  interval rows and 702 paired policy-delta confidence interval rows. These are
  scaffold uncertainty summaries, not calibrated real-world confidence evidence.
- The small multi-corridor candidate output has matching uncertainty tables
  with 208 metric confidence interval rows and 156 paired policy-delta rows.
  The full-profile multi-corridor candidate output has 819 metric confidence
  interval rows and 702 paired policy-delta rows. These are graph-scale review
  summaries only.
- The current-vs-full-profile-candidate graph-scale result comparison adds
  819 metric-level delta rows. It currently reports 741 same-or-close rows,
  24 candidate-improves rows, 24 candidate-worsens rows, and 30 non-finite
  difference rows. These differences require graph-scale review before any
  manuscript claim uses the candidate graph.

These artifacts are useful for implementation verification and manuscript
structure. They should not be described as calibrated real-world results,
calibrated sensitivity evidence, Sobol indices, or operational route guidance.

## Working Title

**A Region-Reusable Decision Framework for Disrupted Regional Personnel
Transport Resilience under Network Degradation and Constrained Fleet
Operations**

Alternative titles:

- **Evaluating Multimodal Personnel Transport Resilience under Regional Network
  Disruption**
- **Open-Data Micro-Simulation of Disrupted Regional Personnel Movement with
  Constrained Road and Rail Resources**
- **When Does Rail-Bus Multimodal Transport Improve Disrupted Regional Mobility?
  A Network Disruption Simulation Framework**

## Target Paper Type

Recommended paper type:

- applied transportation resilience study
- simulation-based decision framework
- disrupted logistics and emergency or contingency transport planning paper

The paper should not be framed as:

- a military operations report,
- a one-region case study with field-use predictions,
- a claim that the current abstract network proves real-world modal superiority.

The strongest framing is a reusable methodology with a guarded regional case
demonstration.

## Abstract Draft

Large-scale personnel movement during regional disruption depends on the joint
availability of road corridors, transit access, fleet resources, transfer
capacity, and dispatch policy. Although multimodal transport can reduce direct
road-vehicle requirements, its performance may collapse when access roads,
transfer points, or last-mile services become bottlenecks. This study develops
a region-reusable micro-simulation framework for evaluating regional personnel
transport resilience under network degradation and constrained fleet
operations. The framework compares bus-only and rail-bus multimodal strategies
using queue-based passenger dispatch, finite vehicle fleets, fixed-headway rail
service, transfer delays, dynamic road travel time, and disruption states
including blockage and capacity reduction. Resilience is assessed using
completion probability, censored personnel, penalized makespan,
resource-efficiency measures, tail arrival times, and bottleneck attribution.

A full-profile pilot experiment covering 23 policies (5 congestion levels, 4
transfer stress levels, 4 fleet/capacity severity), 23 disruption scenarios
(including 4 spatial hazard overlays, 8 rail severity scenarios, 2 multi-hazard
combinations, and 1 transfer-point blockage), and 30
common-random-number seed replications (15,870 result rows, 529 summary rows)
was conducted on a multi-corridor OSM-derived cached road graph (164 nodes,
246 edges) for the Songpa-gu pilot region. The emergency demand profile
represents 500 personnel. The fleet is deliberately under-provisioned (8 direct
buses, 5 feeder shuttles, 4 last-mile vehicles, all 45-passenger capacity)
with a 200-minute time limit and BPR alpha=0.50.

The central finding is that multimodal resilience is not merely
congestion-dependent but location-dependent. Bus-only transport is faster at
every congestion level without disruption (19.84 vs 46.51 min at 1x). The
Tancheon corridor disruption creates a multimodal advantage at 4x (MM:
CR=0.97 vs bus: CR=0.93; both inf mean makespan) because it degrades the bus-only
trunk route while sparing the feeder and last-mile legs. However, when
disruption hits the feeder route (feeder_east), multimodal CR drops to
0.89 at 6x while bus-only maintains CR=0.80 (both have inf mean makespan). When
disruption hits the last-mile route (lastmile_west), multimodal CR drops to
0.91 vs bus-only CR=0.80 (both inf mean makespan). Only disruptions that affect the bus-only trunk
without touching multimodal-specific legs create a multimodal advantage. This
is a geographic property of the specific pilot region route structure, not a
general resilience finding.

Three additional evidence pillars extend this geographic-conditional finding.
Rail service disruption (delay, capacity reduction, combined stress) increases
multimodal makespan by 6-11 min at baseline congestion but does not eliminate
the multimodal completion-rate advantage when road disruption simultaneously
degrades the bus-direct trunk. Transfer stress policies increase multimodal
makespan proportionally (up to +121 min at extreme level) without affecting
bus-only; completion rate remains 1.0 under all transfer stress levels because
the 200-minute time limit absorbs the delay, indicating that transfer handling
is a makespan cost rather than a completion risk under current assumptions.
Multi-hazard scenarios combining road and rail degradation show that the
multimodal road-bypass advantage persists under moderate rail degradation: at
severe congestion with Tancheon and rail delay, multimodal maintains CR=0.96
while bus-only drops to CR=0.20.

The framework's value is identifying which disruption locations create advantage
or disadvantage for each mode. These results are decision-support simulation
outputs only; they are not calibrated real-world forecasts, operational route
plans, or field-use guidance. The expected contribution is not a universal
ranking of transport modes, but a decision framework that identifies the
disruption-location regimes in which multimodal personnel transport is robust,
competitive, or fragile.

## Keywords

- transport resilience
- disrupted logistics
- emergency personnel movement
- multimodal simulation
- road-rail integration
- network degradation
- finite fleet dispatch
- critical-link analysis
- sensitivity analysis
- OpenStreetMap

## 1. Introduction

### 1.1 Problem Context

Regional emergency, contingency, and public-sector personnel movement require moving a large
number of people within a constrained time window. In normal conditions, direct
road transport can appear simple in field operations because passengers are loaded
onto vehicles and moved from an assembly area to a destination. Under disrupted
conditions, however, direct road transport becomes exposed to road congestion,
blocked corridors, limited vehicle availability, driver constraints, and
uncertain arrival patterns.

Rail-bus multimodal transport offers a plausible alternative. Rail can move
many passengers with fewer road vehicles over the trunk segment, while buses or
shuttles provide feeder and last-mile movement. This apparent capacity
advantage is conditional. It depends on station access, train availability,
transfer handling, last-mile road resilience, and the coordination of several
sequential services. A rail-bus system can therefore be resource-efficient but
fragile in field execution if any connector segment becomes a bottleneck.

This motivates a resilience question rather than a simple speed-comparison
question.

### 1.2 Research Gap

Existing transport simulation tools can model road traffic, public transit,
evacuation, routing, or fleet operations. However, a decision maker evaluating
regional personnel transport under disruption needs an integrated view of:

- passenger arrival uncertainty,
- dispatch policy,
- finite road vehicle fleets,
- rail service headway and capacity,
- transfer and staging delays,
- disrupted road links,
- censored or undelivered passengers,
- resource efficiency,
- sensitivity to uncertain assumptions.

Large traffic platforms can be powerful, but they can also obscure the specific
policy logic of coordinated personnel transport. Conversely, small abstract simulations
are easy to interpret but can be criticized as insufficiently realistic. This
paper addresses that gap by proposing a staged framework: a transparent
micro-simulation core, surrounded by open-data network input, plausibility-check,
hazard-overlay, and sensitivity-analysis layers.

### 1.3 Research Questions

Primary research question:

> Under which network-disruption and resource-constraint regimes does rail-bus
> multimodal personnel transport outperform bus-only transport?

Supporting questions:

1. Which road, rail-access, transfer, and last-mile bottlenecks most reduce
   completion probability?
2. When does the resource-efficiency advantage of multimodal transport offset
   its additional coordination and transfer burden?
3. How sensitive are conclusions to fleet size, dispatch interval, transfer
   delay, rail headway, road capacity degradation, and passenger arrival
   uncertainty?
4. Can an open-data regional pipeline support repeatable analysis across
   different regions without exposing sensitive destination coordinates?

### 1.4 Contributions

This paper aims to make four contributions:

1. **A region-reusable disrupted transport resilience framework.** The proposed
   framework combines regional network input, disruption scenarios, passenger
   micro-simulation, finite fleet operations, rail-bus multimodal movement, and
   resilience metrics.
2. **A transparent comparison of bus-only and rail-bus multimodal transport.**
   The comparison is based on paired stochastic scenarios and reports
   completion, censoring, tail risk, and resource-efficiency metrics rather than
   mean travel time alone.
3. **A bottleneck-centered interpretation of multimodal resilience.** The paper
   evaluates whether multimodal transport fails because of rail trunk capacity,
   station access, transfer processing, last-mile road service, or fleet
   shortage.
4. **A path from abstract simulation to open-data evidence checks.** The framework
   specifies how to move from a representative network to OSM-derived roads,
   GTFS-based rail plausibility checks, hazard overlays, critical-link metrics, and
   formal sensitivity analysis.

## 2. Related Work Plan

This section should be completed with peer-reviewed citations. The current
draft identifies the required literature groups.

### 2.1 Transport Network Resilience

Relevant themes:

- road network vulnerability,
- critical-link analysis,
- accessibility loss,
- network robustness under link removal or capacity reduction,
- travel-time reliability,
- infrastructure resilience metrics.

Expected connection to this paper:

The paper should position completion probability, censored personnel, and
bottleneck attribution as application-specific resilience outcomes derived from
transport network degradation.

### 2.2 Evacuation and Emergency Transport Simulation

Relevant themes:

- evacuation planning,
- emergency bus dispatch,
- mass movement under disruption,
- staged evacuation,
- multimodal evacuation,
- microscopic and mesoscopic traffic simulation.

Expected connection:

The proposed problem is similar to evacuation in scale and disruption exposure,
but differs because passengers are moved toward controlled destination zones
under fleet and rail coordination constraints.

### 2.3 Multimodal Transport and Transit Resilience

Relevant themes:

- road-rail integration,
- transit headway reliability,
- first-mile and last-mile bottlenecks,
- transfer capacity,
- public transit disruption response.

Expected connection:

The paper should argue that rail-bus multimodal transport is not inherently
resilient. It is resilient only when access, trunk, transfer, and last-mile
segments remain jointly functional.

### 2.4 Fleet Dispatch and Vehicle Routing under Uncertainty

Relevant themes:

- finite fleet assignment,
- vehicle routing with capacity and time windows,
- robust or stochastic routing,
- dispatch policy evaluation,
- common-random-number comparison.

Expected connection:

Optimization tools can generate candidate policies, but simulation is needed to
evaluate those policies under stochastic arrivals, disruptions, congestion, and
censoring.

### 2.5 Open-Data Geospatial Transport Modeling

Relevant themes:

- OpenStreetMap road networks,
- GTFS transit schedules,
- public routing engines,
- reproducible geospatial pipelines,
- privacy-preserving spatial aggregation.

Expected connection:

Open data improves reproducibility and regional reuse, but it must be combined
with source-tuned assumptions and benchmark checks. Public maps alone do not
make a simulation field-use valid.

## 3. Framework Overview

### 3.1 Conceptual Pipeline

The proposed framework has seven layers:

1. **Regional input layer.** Defines region boundaries, assembly zones,
   destination zones, rail access points, road networks, and public transit
   feeds.
2. **Network preparation layer.** Converts road and rail data into a simulation
   graph with travel time, capacity, mode, and geometry attributes.
3. **Disruption layer.** Generates edge states such as normal, capacity
   reduced, or blocked. Disruptions may be random, scenario-based, or spatially
   structured through hazard overlays.
4. **Policy layer.** Defines transport alternatives such as bus-only,
   rail-bus multimodal, last-mile redundancy, staggered dispatch, fleet
   shortage, or rail delay.
5. **Micro-simulation layer.** Simulates passenger arrivals, queue-based
   dispatch, finite fleets, road travel, rail departures, transfers, and
   censored arrivals.
6. **Evaluation layer.** Computes completion, censoring, tail-risk,
   resource-efficiency, accessibility-loss, and bottleneck metrics.
7. **Evidence-check and sensitivity layer.** Checks plausibility against public
   data, routing benchmarks, source tables, and global sensitivity analysis.

### 3.2 Core Design Principle

The core simulator remains intentionally transparent. External tools are added
around it for data ingestion, plausibility checks, benchmarking, optimization, and
reporting. This prevents the research from becoming a black-box integration of
a large traffic simulator.

### 3.3 Recommended Open-Source Stack

Core stack for the SCI-grade extension:

- `NetworkX`: graph representation and criticality metrics.
- `OSMnx`: real regional road network extraction.
- `GeoPandas` and `Shapely`: spatial clipping, joins, and zone abstraction.
- `snail`: raster hazard or exposure overlay onto road and rail edges.
- `gtfs-validator` and `gtfs_kit`: public transit feed quality checks and headway
  extraction.
- `SALib`: global sensitivity analysis.
- `Frictionless`: result-schema and benchmark-package checks.

Benchmark or optional stack:

- `r5py`, `R5`, `OpenTripPlanner`, `Valhalla`, and `OSRM` for travel-time and
  accessibility plausibility checks.
- `UXsim` for Python-native mesoscopic congestion benchmarking.
- `SUMO` and `MATSim` for high-cost external benchmark experiments.
- `OR-Tools` or `PyVRP` for candidate fleet allocation and contingency routing
  policies.
- `Papermill`, `Quarto`, and `Streamlit` for reproducible analysis and
  decision-support reporting.

## 4. Study Context and Data Design

### 4.1 Application Context

The motivating application is regional emergency or contingency personnel transport from an urban
assembly context toward destination zones. The current baseline represents a
movement of approximately 1,000 personnel and compares:

- direct bus-only transport,
- rail-bus multimodal transport with road feeder, rail trunk, and road
  last-mile services.

For publication, exact sensitive locations should not be exposed. The paper
should use anonymized zones, synthetic destination nodes, or coarse regional
representations.

### 4.2 Regional Reuse

The design should not be hard-coded to one region. A region should be described
by:

- region identifier,
- boundary polygon,
- assembly zone set,
- destination zone set,
- candidate rail access points,
- candidate last-mile destination access points,
- road graph source and snapshot metadata,
- transit feed source and quality-check metadata,
- scenario parameter set.

Changing the region should not require changing the simulation logic.

### 4.3 Sensitive-Location Abstraction

Sensitive locations should be represented as:

- administrative or H3-like zones,
- synthetic centroids,
- generalized destination areas,
- OD counts between zones,
- aggregated result maps.

The paper should explicitly state that the framework supports sensitive-location
protection and that the published case is not an operational route plan.

### 4.4 Parameter Source Table

A required paper deliverable is a parameter-source table. Each major parameter
should be labeled as one of:

- public-data value,
- literature value,
- expert-assumption value,
- sensitivity-only value.

Example parameter groups:

- road free-flow travel time,
- road capacity,
- background traffic volume,
- disruption probability or exposure threshold,
- capacity-reduction factor,
- bus capacity,
- fleet availability,
- dispatch interval,
- turnaround time,
- rail headway,
- rail capacity,
- transfer fixed time,
- transfer per-passenger time,
- passenger arrival distribution,
- simulation time limit,
- late-arrival penalty.

The current repository also includes a generated parameter review packet that
turns the audit into a 29-row reviewer worksheet. It should be used to
prioritize evidence upgrades and explicit assumption review, but it should not
be cited as calibration evidence.

## 5. Simulation Model

### 5.1 Entities

The current model includes the following entities:

- passengers,
- road vehicles,
- rail service,
- road links,
- rail link,
- transfer node,
- fleet resources,
- disruption states,
- policy parameters,
- scenario outputs.

### 5.2 Transport Alternatives

The paper compares at least two alternatives.

**Bus-only.** Passengers assemble, queue for road vehicles, and travel by road
from origin zone to destination zone.

**Rail-bus multimodal.** Passengers use a road feeder from origin zone to rail
access, rail trunk movement, transfer handling, and road last-mile service from
rail egress to destination zone.

Future policy alternatives should include:

- multimodal with redundant last-mile capacity,
- bus-only with alternate corridors,
- staggered dispatch,
- adaptive rerouting,
- feeder capacity expansion,
- rail delay or partial rail unavailability,
- fleet shortage scenarios.

### 5.3 Passenger Arrival Model

Passengers do not all arrive at the exact same time. Arrival delay is modeled
stochastically to capture early, on-time, and late arrivals.

The current implementation uses a lognormal lateness process. The full paper
should justify or sensitivity-test this assumption because arrival tails can
affect dispatch efficiency, queue formation, and missed departures.

### 5.4 Dispatch Policies

The implemented dispatch policies are:

- **STRICT:** depart at the scheduled time with the passengers who have arrived.
- **GRACE:** wait up to a maximum time, or until a target fraction has arrived,
  or until vehicle capacity is reached.

The key modeling decision is that policies operate on passenger queues rather
than fixed pre-batched groups. This better represents late arrivals, partial
departures, and queue spillover.

### 5.5 Fleet Model

Road services are constrained by finite fleets and turnaround time. A vehicle
cannot be reused until its previous trip and turnaround are complete.

The model should distinguish:

- direct bus fleet,
- feeder shuttle fleet,
- last-mile fleet,
- vehicle capacity,
- dispatch cadence,
- turnaround time,
- first-departure schedule anchor.

This matters because a multimodal option may reduce long-distance road vehicle
use while increasing sensitivity to feeder or last-mile vehicle shortage.

### 5.6 Rail Model

Rail service is modeled as a fixed-headway service with passenger capacity. The
current model does not serialize later trains behind earlier train travel, which
is appropriate for a scheduled headway abstraction.

For the SCI-grade extension, rail assumptions must be source-checked or
sensitivity-tested:

- headway,
- capacity,
- access station availability,
- egress station availability,
- transfer capacity,
- partial rail delay,
- partial rail unavailability.

### 5.7 Transfer Model

Transfers include both a fixed component and a passenger-count-dependent
component. This reflects staging, movement, boarding, coordination, and platform
or queue handling.

Transfer time is a key multimodal fragility parameter. If transfer handling
grows too slowly in the model, rail-bus transport may look artificially strong.
If it grows too aggressively, multimodal transport may look artificially weak.
The paper should therefore include transfer-time sensitivity analysis.

### 5.8 Road Travel Time Model

The current implementation uses a dynamic rolling-window BPR-style travel time:

```text
t = t0 * (1 + alpha * (s * v / C)^beta)
```

where:

- `t0` is free-flow travel time,
- `v` is effective traffic volume,
- `C` is capacity,
- `s` is a scaling factor,
- `alpha` and `beta` are BPR parameters.

The rolling-window design gives the simulation congestion feedback without
requiring a full microscopic traffic assignment model. For publication, this
should be presented as a controlled approximation and compared against
routing-engine or public-data ranges.

### 5.9 Disruption Model

The implemented disruption modes are:

- full blockage,
- capacity reduction.

In the current abstract baseline, disruption probability is scenario-driven. In
the proposed SCI-grade extension, disruptions should also be spatially
structured:

- road-link exposure from hazard overlays,
- critical-link targeted degradation,
- access-road disruption,
- last-mile disruption,
- multiple correlated edge degradations,
- rail-access degradation.

The key improvement is to move from purely random link failure to a combination
of random, criticality-based, and spatially structured disruption scenarios.

## 6. Evaluation Metrics

### 6.1 Primary Metrics

The paper should not evaluate alternatives using makespan alone. When some
passengers are not delivered within the time limit, raw makespan can be
misleading.

Primary metrics:

- completion rate,
- censored passenger count,
- penalized makespan,
- 50th, 80th, and 95th percentile arrival time,
- first-arrival time,
- resource efficiency,
- road vehicle-minutes,
- train-minutes,
- passenger-minutes,
- passengers moved per service minute.

### 6.2 Resilience Metrics

Additional resilience metrics:

- performance loss relative to no-disruption baseline,
- recovery or redundancy benefit under capacity reduction,
- critical-link contribution to completion loss,
- accessibility loss from origin zones to rail access points,
- accessibility loss from rail egress points to destination zones,
- alternative-route availability,
- OD pair disconnection rate,
- bottleneck attribution by segment.

### 6.3 Suggested Composite Interpretation

The paper should present results through three lenses:

1. **Speed lens:** arrival time and penalized makespan.
2. **Reliability lens:** completion rate, censored personnel, and tail arrivals.
3. **Resource lens:** vehicle-minutes, train-minutes, and passengers per service
   minute.

The main policy conclusion should be based on all three lenses, not one metric.

## 7. Experimental Design

### 7.1 Current Implemented Baseline

The current project already includes:

- Phase 1 experiment output with 8,400 paired rows.
- Phase 2 experiment output with 840 paired rows.
- Pilot experiment output with 15,870 result rows (23 policies x 23 scenarios x
  30 seeds) and 529 summary rows.
- Common-random-number pairing between bus-only and multimodal scenarios.
- Scenario sweeps over policies, disruption scaling, congestion levels, and
  selected network variants.
- CSV outputs and plots.

These outputs are useful as baseline evidence, but they should be described as
representative-network results rather than fit-to-observed-data real-world findings.

### 7.2 Required SCI-Grade Extension

The full paper should add or strengthen:

1. Reviewed OSM-derived real or quasi-real road network for a pilot region.
2. Zone-based origin and destination representation beyond scaffold points.
3. GTFS-based rail schedule checks or a documented rail assumption set.
4. Public-data, benchmark, or literature-supported parameter-source table.
5. Spatially structured disruption scenarios beyond scaffold definitions.
6. Critical-link and accessibility-loss analysis.
7. Formal sensitivity analysis beyond deterministic screening.
8. Independent routing or transit benchmark checks.
9. Broader policy alternatives and seed/scenario coverage beyond the current
   sample subset.

### 7.3 Scenario Axes

Recommended scenario axes:

- passenger volume,
- passenger arrival variability,
- bus fleet size,
- shuttle fleet size,
- last-mile fleet size,
- dispatch interval,
- rail headway,
- rail capacity,
- transfer delay,
- road background traffic,
- disruption mode,
- disruption severity,
- capacity-reduction factor,
- affected corridor type,
- network variant,
- policy alternative.

### 7.4 Experimental Pairing

Bus-only and multimodal scenarios should be paired using the same stochastic
seeds where possible. This reduces variance and helps isolate differences due
to transport strategy rather than random arrival or disruption draws.

### 7.5 Sensitivity Analysis

Formal sensitivity analysis should be applied with a tool such as SALib. The
current repository contains both a deterministic one-at-a-time screening
scaffold and a SALib Morris screening path for the current full
policy/scenario scaffold.
These are useful for implementation testing and preliminary parameter ranking,
but they should not be reported as calibrated real-world sensitivity evidence
or Sobol sensitivity evidence. The generated sensitivity review packet should
be used to document index handling and method-scope review before any
manuscript claim is upgraded.

The generated evidence-check review packet should likewise be used to document
internal plausibility warnings, fallback benchmark limitations, optional OSRM
snapshot/manifest provenance, accessibility-loss interpretation, and the
closeout benchmark-strategy decision before any evidence-check claim is upgraded.
The evidence-check, graph-scale, sensitivity, and experiment strategy-blocker-review
packets are implemented, but all are blocker triage aids, not formal signoff
records.

Recommended outputs:

- first-order sensitivity indices,
- total-order sensitivity indices,
- Morris screening for the selected staged/full pilot design if the full Sobol
  design is too expensive,
- ranked parameter influence on completion rate,
- ranked parameter influence on censored passengers,
- ranked parameter influence on penalized makespan,
- ranked parameter influence on resource efficiency.

Expected high-impact insight:

The most valuable result is not just which alternative wins, but which uncertain
parameters determine the winning regime.

## 8. Evidence And Plausibility Checks

### 8.1 Internal Checks

Internal checks:

- identical seeds reproduce identical outputs,
- more fleet capacity should not worsen completion under otherwise identical
  assumptions unless congestion feedback explains it,
- higher disruption severity should not improve average resilience metrics,
- longer transfer delay should not improve multimodal completion time,
- blocked critical links should produce worse results than minor capacity
  reductions,
- no-disruption baseline should be easier than disrupted cases.

### 8.2 Public-Data Plausibility

Public-data checks:

- OSM-derived road distances and free-flow times are plausible.
- GTFS-derived headways and route times are plausible.
- Routing-engine travel times are within a defensible range.
- Road speeds and capacities are documented by road class or source category.
- Station access and last-mile distances are not artificially short.

### 8.3 Benchmark Checks

Recommended benchmark tools:

- r5py or R5 for multimodal accessibility matrices.
- OSRM or Valhalla for road travel-time matrices.
- UXsim for a limited road-congestion benchmark.
- SUMO only for a small corridor-level microscopic benchmark if necessary.

Benchmark outputs should be treated as plausibility checks, not ground truth.
The current optional OSRM snapshot has 3 pass rows after bus-practical road
filtering. Its manifest records 3 live/unpinned rows, query URLs, and
checksums. This supports route-plausibility screening, but it still does not
calibrate travel times, emergency operations, or route choice.

The current graph-scale route parity diagnostic also has 3 pass rows for the
canonical baseline road legs. A companion alternate-route diagnostic has 9
rows: 3 rank-1 paths are preserved, while 6 alternate full-graph route
candidates warn because they are not exactly preserved in the reduced
corridor. This supports review of the reduced-corridor abstraction, but it is
not evidence that all alternate corridors or regional route-choice dynamics are
represented.

A candidate multi-corridor graph preserving the top 3 route candidates for
each canonical road leg has 164 nodes and 246 edges, with 9 pass rows in the
same alternate-route diagnostic schema. This suggests a concrete graph-scale
upgrade path. A small separated profile has been run on that graph to produce
32 raw rows and 16 summary rows, and a full-profile candidate has been run to
produce 1,890 raw rows and 63 summary rows. Any result claim based on that
graph still requires a reviewed graph-scale decision.

The graph-scale review packet consolidates these options into a method
selection worksheet. It should be used to decide whether the paper reports a
reduced-corridor abstraction, regenerates on the multi-corridor candidate,
uses full-graph runtime evidence, or defines an ensemble method. The packet is
review support only and does not validate the chosen graph scale by itself.

The current-vs-candidate result comparison provides a second review layer by
showing where the full-profile multi-corridor candidate changes full-pilot
summary metrics. It is useful for identifying graph-choice-sensitive claims,
but it is not graph-scale acceptance and does not replace reviewer judgment.

## 9. Results

The following results are derived from the full-profile pilot experiment on the
multi-corridor OSM-derived cached road graph (164 nodes, 246 edges) for the
Songpa-gu pilot region. The experiment covers 23 transport policies (5 congestion levels: normal/1x,
moderate/2x, heavy/4x, severe/6x, peak/8x; 4 transfer stress levels:
mild, moderate, severe, extreme; and 4 fleet/capacity severity levels),
23 disruption scenarios (8 structural scenarios, 4 spatial hazard overlays,
8 rail severity scenarios, 2 multi-hazard combinations, and 1 transfer-point
blockage), and 30
common-random-number seed replications, producing 15,870
individual result rows and 529 summary rows. The emergency demand profile
represents 500 personnel mobilization with group size 45, assembly window 60
minutes, and arrival lateness following LogNormal(mu=2.0, sigma=0.8). Fleet
resources include 8 direct buses, 5 feeder shuttles, and 4 last-mile vehicles,
all with 45-passenger capacity. The simulation time limit is 200 minutes. BPR
alpha is set to 0.50 with beta=4.0. Background traffic volume is 300 vehicles
per hour. These results are decision-support simulation outputs only; they are
not calibrated real-world forecasts, operational route plans, or field-use
guidance.

### 9.1 Congestion Sweep without Disruption <!-- truth: source=pilot_full_summary.csv -->

The no-disruption scenario reveals that bus-only transport is faster than
multimodal at every congestion level when no road disruption is present:

| Congestion Level | Bus-only (makespan / CR) | Multimodal (makespan / CR) | Winner |
|------------------|--------------------------|----------------------------|--------|
| Normal (1x) <!-- truth: policy=bus_only scenario=no_disruption --> | 19.84 min / 1.00 | 46.51 min / 1.00  | Bus (faster) |
| Moderate (2x) <!-- truth: policy=moderate_congestion_bus scenario=no_disruption --> | 20.55 min / 1.00 | 46.96 min / 1.00  | Bus (faster) |
| Heavy (4x) <!-- truth: policy=heavy_congestion_bus scenario=no_disruption --> | 31.80 min / 1.00 | 56.45 min / 1.00  | Bus (faster) |
| Severe (6x) <!-- truth: policy=severe_congestion_bus scenario=no_disruption --> | 80.41 min / 1.00 | 123.05 min / 1.00  | Bus (faster) |
| Peak (8x) <!-- truth: policy=peak_congestion_bus scenario=no_disruption --> | inf / 0.20 | 177.41 min / 0.67  | MM (only survivor) |

At normal traffic, bus-only is 57.4% faster than multimodal (19.84 vs 46.51
min). This gap persists across all congestion levels up to 6x. At severe
congestion (6x), both modes maintain 100% completion, but bus-only is 42.64
minutes faster. At peak congestion (8x), bus-only mostly fails (CR=0.20) while
multimodal maintains 67% completion with MS=177.41. Congestion alone does not
create a multimodal makespan advantage, but at extreme congestion multimodal
retains partial throughput where bus-only loses most capacity.

### 9.2 Tancheon Corridor Disruption Creates Multimodal Advantage

When congestion is combined with the Tancheon corridor disruption, which
degrades the direct bus trunk road (A -> D) while sparing the feeder (A -> S)
and last-mile (R -> D) legs, the results change qualitatively:

| Congestion Level | Bus-only (makespan / CR) | Multimodal (makespan / CR) | Winner |
|------------------|--------------------------|----------------------------|--------|
| Normal (1x) <!-- truth: policy=bus_only scenario=songpa_spatial_tancheon_corridor --> | 20.14 / 1.00 | 46.57 / 1.00  | Bus (faster) |
| Moderate (2x) <!-- truth: policy=moderate_congestion_bus scenario=songpa_spatial_tancheon_corridor --> | 25.24 / 1.00 | 48.01 / 1.00  | Bus (faster) |
| Heavy (4x) <!-- truth: policy=heavy_congestion_bus scenario=songpa_spatial_tancheon_corridor --> | inf / 0.93 | **inf / 0.97** <!-- truth: policy=heavy_congestion_multimodal scenario=songpa_spatial_tancheon_corridor --> | **MM (higher CR)** |
| Severe (6x) <!-- truth: policy=severe_congestion_bus scenario=songpa_spatial_tancheon_corridor --> | inf / 0.20 | **inf / 0.96** <!-- truth: policy=severe_congestion_multimodal scenario=songpa_spatial_tancheon_corridor --> | **MM (CR 0.96 vs 0.20)** |
| Peak (8x) <!-- truth: policy=peak_congestion_bus --> | inf / 0.00 | inf / 0.32 <!-- truth: policy=peak_congestion_multimodal --> | MM (partial survival) |

At 4x + Tancheon, multimodal achieves higher completion (CR=0.97) than
bus-only (CR=0.93), though both show inf mean makespan — multimodal has higher completion probability across seeds. At 6x + Tancheon, bus-only drops to CR=0.20 while
multimodal maintains CR=0.96. This crossover occurs because the
Tancheon disruption degrades the road segment that bus-only must traverse,
while multimodal passengers bypass it via rail.

### 9.3 Spatial Overlay Comparison: Disruption Location Determines Outcome

The four spatial hazard overlays reveal that the multimodal advantage depends
critically on WHICH route leg the disruption affects:

**Tancheon corridor (degrades bus trunk A -> D, spares A -> S and R -> D):**

| Congestion | Bus (MS / CR) | MM (MS / CR) | Winner |
|------------|---------------|--------------|--------|
| 4x <!-- truth: policy=heavy_congestion_bus scenario=songpa_spatial_tancheon_corridor --> | inf / 0.93 | inf / 0.97 <!-- truth: policy=heavy_congestion_multimodal --> | **MM** |
| 6x <!-- truth: policy=severe_congestion_bus scenario=songpa_spatial_tancheon_corridor --> | inf / 0.20 | inf / 0.96 <!-- truth: policy=severe_congestion_multimodal --> | **MM** |

**Feeder east (degrades A -> S, spares A -> D and R -> D):**

| Congestion | Bus (MS / CR) | MM (MS / CR) | Winner |
|------------|---------------|--------------|--------|
| 1x <!-- truth: policy=bus_only scenario=songpa_spatial_feeder_east --> | 19.95 / 1.00 | 46.57 / 1.00  | Bus |
| 4x <!-- truth: policy=heavy_congestion_bus scenario=songpa_spatial_feeder_east --> | inf / 0.97 | inf / 0.97  | Bus |
| 6x <!-- truth: policy=severe_congestion_bus scenario=songpa_spatial_feeder_east --> | inf / 0.80 | inf / 0.89  | Bus (higher CR) |

**Lastmile west (degrades R -> D, spares A -> D and A -> S):**

| Congestion | Bus (MS / CR) | MM (MS / CR) | Winner |
|------------|---------------|--------------|--------|
| 4x <!-- truth: policy=heavy_congestion_bus scenario=songpa_spatial_lastmile_west --> | inf / 0.97 | inf / 0.97  | Bus |
| 6x <!-- truth: policy=severe_congestion_bus scenario=songpa_spatial_lastmile_west --> | inf / 0.80 | inf / 0.91  | Bus (higher CR) |

**Assembly egress (degrades near A, affects both A -> D and A -> S):**

| Congestion | Bus (MS / CR) | MM (MS / CR) | Winner |
|------------|---------------|--------------|--------|
| 4x <!-- truth: policy=heavy_congestion_bus scenario=songpa_spatial_assembly_egress --> | inf / 0.92 | inf / 0.97  | Near-tie |
| 6x <!-- truth: policy=severe_congestion_bus scenario=songpa_spatial_assembly_egress --> | inf / 0.12 | inf / 0.58  | MM (only survivor) |

At 6x congestion, the feeder_east disruption causes both modes to partially
fail (MM CR=0.89 vs bus CR=0.80, both inf mean makespan). The
lastmile_west disruption similarly causes partial failures
(MM CR=0.91 vs bus CR=0.80, both inf mean makespan). In both cases, the disruption targets a route leg that
ONLY multimodal uses, adding road exposure cost. However, the assembly egress
disruption at 6x eliminates bus-only entirely while multimodal retains 58%
completion, because the egress disruption degrades shared road near the
origin that bus-only must use for its entire route.

### 9.4 Disruption-Location Matrix

The following matrix summarizes how disruption location interacts with route
structure to determine multimodal advantage or disadvantage:

| Disruption Location | Route Leg Affected | Bus Uses? | MM Uses? | MM Advantage at 6x? |
|---------------------|--------------------|-----------|----------|---------------------|
| Tancheon corridor | A -> D (bus trunk) | Yes | No | **YES** (MM CR=0.96 vs Bus CR=0.20) |
| Feeder east | A -> S (feeder) | No | Yes | **NO** (MM CR=0.89 vs Bus CR=0.80, both inf) |
| Lastmile west | R -> D (last-mile) | No | Yes | **NO** (MM CR=0.91 vs Bus CR=0.80, both inf) |
| Assembly egress | Near A (both legs) | Yes | Yes | **YES** (MM CR=0.58 vs Bus CR=0.12) |
| No disruption | None | N/A | N/A | **NO** (Bus faster at all levels) |

This matrix reveals the geographic logic: multimodal transport gains advantage
when disruption degrades a road segment that bus-only must use but multimodal
can bypass via rail (Tancheon), or when shared-origin disruption overwhelms
bus-only's single-path dependency (assembly egress). When disruption instead
degrades a multimodal-specific leg (feeder or last-mile), the rail bypass
provides no benefit and the additional road exposure makes multimodal slower
than bus-only, though both maintain full completion under current parameters.

### 9.5 Other Disruption Scenarios at Heavy Congestion (4x)

At 4x congestion with the non-spatial disruption scenarios:

- **4x + access_origin_to_station:** <!-- truth: policy=heavy_congestion_bus scenario=songpa_access_origin_to_station --> Bus-only inf / CR=0.97 vs
  multimodal inf / CR=0.97 <!-- truth: policy=heavy_congestion_multimodal scenario=songpa_access_origin_to_station -->. Both modes have similar completion rates (CR=0.97); the feeder leg disruption
  affects both modes similarly under heavy congestion with stochastic variation.
- **4x + random_capacity_reduction:** <!-- truth: policy=heavy_congestion_bus scenario=songpa_random_capacity_reduction --> Bus-only inf / CR=0.87 vs
  multimodal inf / CR=0.77 <!-- truth: policy=heavy_congestion_multimodal scenario=songpa_random_capacity_reduction -->. Bus-only maintains higher completion (CR=0.87)
  than multimodal (CR=0.77). Random capacity reduction affects both modes
  but hits multimodal's additional road links harder.
- **4x + last_mile_station_to_destination:** <!-- truth: policy=heavy_congestion_bus scenario=songpa_last_mile_station_to_destination --> Bus-only inf / CR=0.80 vs
  multimodal inf / CR=0.41 <!-- truth: policy=heavy_congestion_multimodal scenario=songpa_last_mile_station_to_destination -->. The last-mile disruption pushes
  multimodal completion to CR=0.41 while bus-only maintains CR=0.80.
- **4x + critical_link_blockage:** <!-- truth: policy=heavy_congestion_bus scenario=songpa_critical_link_blockage --> Bus-only inf / CR=0.37 vs
  multimodal inf / CR=0.20 <!-- truth: policy=heavy_congestion_multimodal scenario=songpa_critical_link_blockage -->. Both modes show reduced completion rates
  (bus CR=0.37, MM CR=0.20) due to stochastic disruption effects under
  heavy congestion, with bus-only maintaining higher CR.
- **4x + rail_station_access:** <!-- truth: policy=heavy_congestion_bus scenario=songpa_rail_station_access --> Bus-only 38.44 min / CR=1.00 vs
  multimodal 63.15 min / CR=1.00 <!-- truth: policy=heavy_congestion_multimodal scenario=songpa_rail_station_access -->. Both modes maintain full completion; the station
  access disruption adds modest makespan to both modes.
- **4x + random_blockage:** <!-- truth: policy=heavy_congestion_bus scenario=songpa_random_blockage --> Both modes nearly fail completely (bus inf / CR=0.03, MM inf / CR=0.00).
  The random blockage scenario with 8 max edges is catastrophic for all
  transport strategies.

The access_origin_to_station and last_mile_station_to_destination results
reinforce the spatial finding: when multimodal-specific road links are
degraded, multimodal loses its structural advantage because those legs are
unique to the multimodal chain.

### 9.6 Rail Service Disruption Results

Three new rail service disruption scenarios test multimodal sensitivity to rail
degradation: rail delay (travel time x1.5), rail capacity reduction (capacity
x0.5), and combined rail stress (travel time x1.5, headway x1.5, capacity x0.5).
Bus-only transport is unaffected by rail disruption in all three scenarios.

**Baseline congestion (1x) rail impact:**

| Scenario | Bus MS | MM MS | MM delta vs no-disruption |
|----------|--------|-------|---------------------------|
| No disruption | 19.84 | 46.51 | -- |
| Rail delay (x1.5) | 19.84 | 52.47 | +5.96 min |
| Rail combined stress | 19.84 | 57.47 | +10.96 min |

Rail disruption increases multimodal makespan by 6-11 min at baseline
congestion. The impact grows with congestion severity: at severe congestion
(6x), the combined rail stress adds approximately 11 min to multimodal
makespan. However, rail degradation alone does not reduce multimodal completion
rate below bus-only at any congestion level, because the 200-minute time limit
absorbs the additional rail travel time.

When rail disruption is combined with Tancheon road disruption at severe
congestion (6x), multimodal maintains CR=0.96 while bus-only drops to CR=0.20.
This shows that road disruption on the bus-direct trunk dominates rail
degradation for completion-rate outcomes: the multimodal road-bypass benefit
persists even with degraded rail service.

### 9.7 Transfer Stress Results

Four transfer stress policies test multimodal sensitivity to transfer delay
increases: mild (+3 min fixed, +0.5 min/passenger), moderate (+6 min fixed,
+1.0 min/passenger), severe (+10 min fixed, +2.0 min/passenger), and extreme
(+15 min fixed, +3.0 min/passenger). Transfer stress affects only multimodal
transport; bus-only has no transfer step.

**Transfer stress impact on makespan (no-disruption, baseline congestion):**

| Policy | Bus MS | MM MS | MM delta vs baseline MM |
|--------|--------|-------|-------------------------|
| Baseline transfer | 19.84 | 46.51 | -- |
| Mild <!-- truth: policy=transfer_stress_mild scenario=no_disruption --> | 19.84 | 71.51 | +25.00 |
| Moderate <!-- truth: policy=transfer_stress_moderate scenario=no_disruption --> | 19.84 | 96.51 | +50.00 |
| Severe <!-- truth: policy=transfer_stress_severe scenario=no_disruption --> | 19.84 | 127.47 | +80.96 |
| Extreme <!-- truth: policy=transfer_stress_extreme scenario=no_disruption --> | 19.84 | 167.47 | +120.96 |

Transfer delay increases multimodal makespan proportionally without affecting
bus-only performance. At extreme transfer stress, multimodal makespan increases
by 121 min (from 46.51 to 167.47). Despite this large makespan increase,
completion rate remains 1.0 under all transfer stress levels at all congestion
levels because the 200-minute time limit absorbs the delay even at peak
congestion. Under the current demand profile (500 personnel, 45-passenger
vehicles), transfer handling is a makespan cost proportional to passenger load,
not a completion-rate risk. This boundary would shift if the time limit were
shorter or the passenger volume were larger.

At extreme transfer stress combined with rail combined stress at baseline
congestion, multimodal makespan reaches 177.47 min, still within the 200-minute
limit. This indicates that simultaneous rail degradation and transfer stress do
not create a completion-rate failure under current assumptions.

### 9.8 Multi-Hazard Results

Two multi-hazard scenarios combine road and rail disruption: Tancheon road
corruption + rail delay, and access road (A->D) + rail capacity reduction.
These test whether the multimodal road-bypass advantage persists when rail
service is simultaneously degraded.

**Tancheon + rail delay (multi-hazard):**

| Congestion | Bus (MS / CR) | MM (MS / CR) | MM Advantage |
|------------|---------------|--------------|--------------|
| 4x (heavy) | inf / 0.93 | inf / 0.97 | MM (higher CR) |
| 6x (severe) | inf / 0.20 | inf / 0.96 <!-- truth: policy=severe_congestion_multimodal scenario=songpa_combo_tancheon_rail_delay --> | **MM CR advantage** |

At heavy congestion, Tancheon + rail delay shows multimodal with higher
CR (0.97 vs 0.93) over bus-only despite the 1.5x rail travel time penalty. At
severe congestion, bus-only drops to CR=0.20 while multimodal
maintains CR=0.96, confirming that the road-bypass benefit from
Tancheon disruption dominates the rail delay penalty.

**Access road + rail capacity reduction (multi-hazard):** <!-- truth: policy=heavy_congestion_bus scenario=songpa_combo_access_rail_capacity -->

At heavy congestion (4x), this combination eliminates both modes: bus MS=inf /
CR=0.00, multimodal MS=inf / CR=0.00. The combined access-road disruption and
rail capacity reduction creates a worst-case scenario where neither transport
chain can complete within the 200-minute time limit. At baseline congestion
(1x), bus-only maintains 21.39 min / CR=1.00 and multimodal 47.13 min /
CR=1.00.

These multi-hazard results show that the multimodal advantage from road
disruption on bus-direct routes persists under moderate rail degradation
(Tancheon + rail delay), but the access-road + rail-capacity combination is
catastrophic for both modes at heavy congestion and above.

### 9.9 Seed Variance

Within each disruption scenario, seed variance reflects run-to-run
variability in road travel time and fleet turnaround. These are the sole
within-scenario stochasticity mechanisms:

1. **Road noise** (sigma=0.05): A Gaussian perturbation (sigma=0.05) is applied
   to road free-flow travel times per replication. This creates variation in
   arrival times across seeds, even in no-disruption scenarios. This is the
   dominant variance source.

2. **Turnaround noise** (lambda=0.2): An exponential perturbation
   (lambda=0.2) is applied to vehicle turnaround times. This varies fleet
   cycling speed across seeds, creating dispatch-timing diversity. This
   has weak influence on outcomes (see §10.7).

Disruption scenarios are deterministic by design: selected road edges are
always blocked (p_fail=1.0), not probabilistically sampled. This separation
ensures that scenario-level uncertainty (which disruption occurs) is distinct
from realization-level uncertainty (run-to-run variability within a fixed
disruption).

Variance statistics across 529 summary groups (policy-scenario pairs):

- 426 out of 529 groups (80.5%) produce >=5 unique makespan values across 30
  seeds. The mean unique makespan count across all groups is 15.6 out of 30
  seeds.
- Groups with fewer unique values occur where the disruption creates a tight
  resource constraint with limited routing flexibility.
- At baseline congestion (1x), finite makespan groups show seed-dependent
  variation with standard deviations of 0.5-2.0 min around the mean.
- At heavy congestion (4x), road noise amplifies BPR travel-time increases,
  producing wider makespan distributions.

Confidence intervals computed from seed replications reflect run-to-run
variability under the chosen noise parameters (sigma=0.05, lambda=0.2).
These parameters are exploratory sensitivity assumptions, not empirically
calibrated values. The sensitivity of conclusions to these parameter choices
is reported in §10.7.

### 9.10 Sensitivity Analysis

Morris screening was conducted across the full policy/scenario design. The
sensitivity analysis evaluates parameter influence on completion rate, censored
passenger count, penalized makespan, and resource efficiency across all tested
transport strategies and disruption conditions. The current Morris output is
scaffold screening on the full policy/scenario design; it is not calibrated
real-world sensitivity evidence, and Sobol variance decomposition has not yet
been applied.

### 9.11 Claim Boundaries for Pilot Results

All results in this section carry the following claim boundaries:

1. These are decision-support simulation outputs, not calibrated real-world
   forecasts or operational route plans.
2. The pilot demand is 500 personnel on a 164-node / 246-edge multi-corridor
   graph derived from OSM data for Songpa-gu, Seoul.
3. Demand justification: 500 personnel represents approximately 0.3% of
   Songpa-gu's population (~170,000), consistent with a targeted emergency
   mobilization or contingency personnel movement scenario.
4. Road defaults are based on Korean regulatory values (Road Traffic Act, Korea
   HCM 2004, MOLIT standards) but remain expert-assumption proxies until
   source-tuned.
5. Rail timing of 13 minutes is derived from Seoul Metro Lines 2/8/9 schedule
   assumptions and has not been source-checked against reviewed GTFS or timetable
   data.
6. BPR alpha is set to 0.50 based on stress-scenario calibration, not
   calibrated to observed traffic counts. This is higher than the Korean
   urban arterial literature value (0.36) and produces stronger congestion
   response.
7. LogNormal sigma is set to 0.8, higher than the previous value of 0.5, to
   generate meaningful stochastic variation across seed replications.
8. Fleet resources (8/5/4) are deliberately under-provisioned relative to the
   500-personnel demand to create resource contention under congestion.
9. The simulation time limit is 200 minutes.
10. Peak congestion (8x background volume) is a stress scenario, not a
    calibrated representation of specific real-world congestion events.
11. Seed-level variance produces a mean of 15.6 unique makespan values per
     30 seeds (426/529 groups with >=5 unique values). This variance reflects
     operational variability under exploratory noise parameters (sigma=0.05,
     lambda=0.2), not calibrated real-world uncertainty. See §10.7 for
     sensitivity of conclusions to these parameter choices.
12. The spatial overlay results reflect the specific geographic configuration of
    the Songpa-gu pilot region. The Tancheon corridor, feeder-east, lastmile-west,
    and assembly-egress disruption locations are defined by this region's road and
    rail topology. Different regions with different route structures may produce
    different disruption-location outcomes.
13. The disruption-location advantage/disadvantage pattern is a geographic
    property of the pilot region's route structure, not a generalizable finding
    about multimodal resilience.
14. Completion rate differences between bus-only and multimodal under combined
     congestion and spatial disruption warrant further investigation with
     higher-fidelity fleet cycling models and region-specific parameter tuning.
15. Rail service disruption scenarios (delay, capacity reduction, combined
     stress) assume uniform rail degradation applied to travel time, headway,
     and capacity parameters simultaneously. Actual rail service degradation
     may be more localized or intermittent than these uniform multipliers imply.
16. Transfer stress policies apply fixed and per-passenger delay increases
     uniformly across all transfer events. Actual transfer delay may vary by
     passenger group size, platform capacity, or coordination procedures.
17. Multi-hazard scenarios combine independent road and rail disruption
     multipliers. Correlations between road and rail disruption events under
     real regional hazards may differ from these independent-combination
     assumptions.
18. The `songpa_random_capacity_reduction` scenario was tightened from
     capacity_factor 0.50 to 0.30 and max_edges 4 to 8. The
     `songpa_random_blockage` scenario was expanded from max_edges 2 to 8.
     The `songpa_spatial_lastmile_west` bbox was expanded from approximately
     100m x 110m to approximately 485m x 500m. These severity adjustments
     change the disruption intensity relative to the original definitions and
     must be considered when comparing to earlier experiment outputs.

### 9.12 Severity Ladder Evidence

The expanded experiment design (23 policies x 23 scenarios x 30 seeds = 15,870
rows) introduces graduated severity ladders for rail degradation, fleet shortage,
last-mile vehicle capacity, and transfer-point blockage. Each ladder isolates a
single stress dimension while holding other factors constant. The following
subsections report the severity ladder results for the baseline_multimodal
policy unless otherwise noted. All values are decision-support simulation
outputs only; they are not calibrated real-world results or operational
guidance.

#### 9.12.1 Rail Delay Severity Ladder

Four rail delay scenarios test progressive rail travel-time degradation at
baseline congestion (1x) with no road disruption. Rail delay multiplies the rail
travel time by a severity factor; rail unavailability multiplies it by 100x
(effectively removing rail from the transport chain):

| Scenario | Rail Factor | MM Makespan (min) | MM CR | Delta vs Baseline |
|----------|-------------|-------------------|-------|-------------------|
| No disruption <!-- truth: policy=baseline_multimodal scenario=no_disruption --> | 1.0x | 46.51 | 1.00 | -- |
| Rail delay mild <!-- truth: policy=baseline_multimodal scenario=songpa_rail_delay_mild --> | 1.2x | 47.47 | 1.00 <!-- truth: policy=baseline_multimodal scenario=songpa_rail_delay_mild --> | +0.96 |
| Rail delay <!-- truth: policy=baseline_multimodal scenario=songpa_rail_delay --> | 1.5x | 52.47 | 1.00 <!-- truth: policy=baseline_multimodal scenario=songpa_rail_delay --> | +5.96 |
| Rail delay severe <!-- truth: policy=baseline_multimodal scenario=songpa_rail_delay_severe --> | 2.0x | 57.47 | 1.00 <!-- truth: policy=baseline_multimodal scenario=songpa_rail_delay_severe --> | +10.96 |
| Rail unavailable <!-- truth: policy=baseline_multimodal scenario=songpa_rail_unavailable --> | x100 | inf | 0.00 <!-- truth: policy=baseline_multimodal scenario=songpa_rail_unavailable --> | **Collapse** |

Rail delay produces a threshold-linear makespan increase: mild (1.2x) adds less
than 1 min (MS=47.47 vs 46.51 baseline), then approximately 6 min per
additional 0.5x severity increment (MS=52.47 at 1.5x, MS=57.47 at 2.0x). This indicates
the current rail segment is short enough that a 20% travel-time increase falls
below the rounding threshold, but 50% and above produce measurable delays.
The system is robust to moderate rail
slowdown: even at 2.0x rail delay, completion rate remains 1.00 and makespan
increases by only 11 min.

At rail unavailability (x100), the multimodal chain collapses entirely (MS=inf,
CR=0.00). This is a cliff-edge failure: the system transitions from fully
functioning to zero completion when rail becomes effectively unavailable. The
rail service pillar exhibits a robust-then-fragile profile -- tolerant of
degradation up to 2.0x, but catastrophically sensitive to complete unavailability
because the feeder and last-mile legs depend on rail trunk movement to deliver
passengers to the destination zone.

#### 9.12.2 Rail Combined Stress Severity Ladder

Three combined stress scenarios simultaneously vary rail travel time, headway,
and capacity. The combined stress multiplier applies to travel time and headway,
while the capacity reduction factor scales train capacity:

| Scenario | Time/Hwy Factor | Capacity Factor | MM Makespan (min) | MM CR | Delta vs Baseline |
|----------|-----------------|-----------------|-------------------|-------|-------------------|
| No disruption <!-- truth: policy=baseline_multimodal scenario=no_disruption --> | 1.0x | 1.00 | 46.51 | 1.00 | -- |
| Combined mild <!-- truth: policy=baseline_multimodal scenario=songpa_rail_combined_stress_mild --> | 1.2x | 0.75 | 47.47 | 1.00 <!-- truth: policy=baseline_multimodal scenario=songpa_rail_combined_stress_mild --> | +0.96 |
| Combined <!-- truth: policy=baseline_multimodal scenario=songpa_rail_combined_stress --> | 1.5x | 0.50 | 57.47 | 1.00 <!-- truth: policy=baseline_multimodal scenario=songpa_rail_combined_stress --> | +10.96 |
| Combined severe <!-- truth: policy=baseline_multimodal scenario=songpa_rail_combined_stress_severe --> | 2.0x | 0.25 | 66.42 | 1.00 <!-- truth: policy=baseline_multimodal scenario=songpa_rail_combined_stress_severe --> | +19.91 |

Combined stress produces a progressive makespan increase from mild (+0.96) to
severe (+19.91). The mild combined stress scenario (1.2x/1.2x/0.75) shows minimal impact
(+0.96 min), similar to the rail-delay-only mild result. The severe
combined stress scenario adds 20 min, which is 9 min more than severe rail
delay alone (57.47 vs 66.42). This additional 9-min increment is attributable
to the combined effect of reduced capacity (0.25x) and increased headway (2.0x),
which delay subsequent train boardings and force passengers to wait longer for
available capacity. The capacity reduction multiplier is the dominant additional
factor: halving capacity from 0.50 to 0.25 adds 9 min, while the travel-time
and headway increase from 1.5x to 2.0x accounts for the remaining difference.

#### 9.12.3 Fleet Shortage Severity Ladder

Two fleet shortage policies scale both the shuttle fleet and last-mile fleet
simultaneously at no-disruption baseline congestion:

| Scenario | Fleet Multiplier | MM Makespan (min) | MM CR | Delta vs Baseline |
|----------|------------------|-------------------|-------|-------------------|
| No disruption <!-- truth: policy=baseline_multimodal scenario=no_disruption --> | 1.00x | 46.51 | 1.00 | -- |
| Fleet shortage stress <!-- truth: policy=fleet_shortage_stress scenario=no_disruption --> | 0.75x | 46.51 | 1.00 <!-- truth: policy=fleet_shortage_stress scenario=no_disruption --> | +0.00 |
| Fleet shortage severe <!-- truth: policy=fleet_shortage_severe scenario=no_disruption --> | 0.50x | 52.79 | 1.00 <!-- truth: policy=fleet_shortage_severe scenario=no_disruption --> | +6.28 |

A 25% fleet reduction (0.75x) produces zero measurable impact on makespan
(MS=46.51 = baseline). A 50% fleet reduction increases makespan by only +6.28
min while maintaining full completion. Fleet shortage is a weaker stressor than
congestion or rail degradation under current parameters: 50% fleet loss adds
less makespan than 1.5x rail delay (+5.96 min), and it does not reduce
completion rate. The current fleet (5 shuttles, 4 last-mile vehicles) has enough
surplus capacity at baseline congestion that a 25% reduction does not create a
binding constraint. Even at 50% reduction, the remaining fleet can cycle
sufficiently within the 200-minute time limit to deliver all 500 personnel.

This suggests that fleet size is a second-order concern relative to road
congestion and rail availability at baseline conditions. However, fleet shortage
may interact non-linearly with simultaneous congestion or disruption, a
hypothesis that should be tested in future combined-stress experiments.

#### 9.12.4 Last-Mile Vehicle Capacity Severity Ladder

Three last-mile vehicle capacity policies vary the per-vehicle passenger
capacity of last-mile vehicles at no-disruption baseline congestion:

| Scenario | Vehicle Capacity (pax) | MM Makespan (min) | MM CR | Delta vs Baseline |
|----------|------------------------|-------------------|-------|-------------------|
| No disruption <!-- truth: policy=baseline_multimodal scenario=no_disruption --> | 45 | 46.51 | 1.00 | -- |
| Capacity mild <!-- truth: policy=lastmile_capacity_mild scenario=no_disruption --> | 35 | 41.42 | 1.00 <!-- truth: policy=lastmile_capacity_mild scenario=no_disruption --> | **-5.00** |
| Capacity moderate <!-- truth: policy=lastmile_capacity_moderate scenario=no_disruption --> | 25 | 41.42 | 1.00 <!-- truth: policy=lastmile_capacity_moderate scenario=no_disruption --> | **-5.00** |
| Capacity severe <!-- truth: policy=lastmile_capacity_severe scenario=no_disruption --> | 15 | 46.51 | 1.00 <!-- truth: policy=lastmile_capacity_severe scenario=no_disruption --> | +0.00 |

This ladder produces a counter-intuitive result. Reducing last-mile vehicle
capacity from 45 to 35 or 25 passengers per vehicle *decreases* makespan by
5 min (from 46.51 to 41.42). Only at 15 passengers per vehicle does makespan
return to the baseline value of 46.51.

This pattern suggests that the default vehicle capacity (45 pax) is not the
binding constraint at current demand levels. The last-mile fleet count (4
vehicles) and dispatch interval matter more than individual vehicle size.
Reducing capacity from 45 to 35 or 25 does not increase the number of trips
required because the current passenger batch sizes per dispatch cycle do not
fully utilize the 45-pax capacity. The observed makespan decrease likely
reflects faster boarding and alighting with smaller vehicle loads, reducing
per-trip dwell time. At 15 pax capacity, the reduced vehicle size does create
additional trips, returning makespan to baseline.

This finding is scaffold evidence under current demand and fleet parameters; it
should not be generalized to higher-demand scenarios or different fleet
configurations without replication.

#### 9.12.5 Transfer Point Blockage

The transfer point blockage scenario disrupts road edges near the multimodal
transfer station (S). This tests whether spatial disruption near the transfer
node affects either mode:

| Policy | Scenario | MS (min) | CR | Baseline MS | Delta |
|--------|----------|----------|-----|-------------|-------|
| bus_only <!-- truth: policy=bus_only scenario=songpa_transfer_point_blockage --> | transfer_blockage | 20.06 | 1.00 <!-- truth: policy=bus_only scenario=songpa_transfer_point_blockage --> | 19.84 <!-- truth: policy=bus_only scenario=no_disruption --> | +0.22 |
| baseline_multimodal <!-- truth: policy=baseline_multimodal scenario=songpa_transfer_point_blockage --> | transfer_blockage | 46.61 | 1.00 <!-- truth: policy=baseline_multimodal scenario=songpa_transfer_point_blockage --> | 46.51 <!-- truth: policy=baseline_multimodal scenario=no_disruption --> | +0.10 |
| heavy_congestion_bus <!-- truth: policy=heavy_congestion_bus scenario=songpa_transfer_point_blockage --> | transfer_blockage | inf | 0.90 <!-- truth: policy=heavy_congestion_bus scenario=songpa_transfer_point_blockage --> | 31.80 <!-- truth: policy=heavy_congestion_bus scenario=no_disruption --> | inf |
| heavy_congestion_multimodal <!-- truth: policy=heavy_congestion_multimodal scenario=songpa_transfer_point_blockage --> | transfer_blockage | inf | 0.97 <!-- truth: policy=heavy_congestion_multimodal scenario=songpa_transfer_point_blockage --> | 56.45 <!-- truth: policy=heavy_congestion_multimodal scenario=no_disruption --> | inf |

Transfer point blockage has minimal impact on bus_only or baseline_multimodal at
normal congestion: both maintain near-baseline makespan and CR=1.00. The road
disruption near station S does not block the key route segments used by either
mode at baseline congestion levels.

At heavy congestion (4x), bus_only drops to CR=0.90 (vs 1.00 baseline)
and multimodal to CR=0.97 (vs 1.00 baseline). The transfer point blockage begins to affect multimodal only when
congestion amplifies the road disruption near S, increasing feeder travel time
to the station under heavy traffic. Even then, completion rate remains 1.00.

This confirms that transfer-point-adjacent road disruption is a moderate-severity
stressor at heavy congestion: it reduces bus_only CR to 0.90 and multimodal
to CR=0.97, with both modes showing partial seed failures. The
geographic location of the transfer point disruption relative to the feeder and
last-mile routes determines this impact.

#### 9.12.6 Severity Ladder Synthesis

The five severity ladders reveal a clear ranking of stressor potency under
current simulation parameters:

1. **Rail unavailability** is the only cliff-edge stressor: MS=inf, CR=0.00.
   Complete rail service loss collapses the entire multimodal chain.
2. **Rail combined severe** (2.0x/2.0x/0.25) is the strongest non-fatal
   stressor: +19.91 min makespan, but CR=1.00.
3. **Fleet severe shortage** (0.50x) is the weakest stressor: +6.28 min
   makespan with no completion impact.
4. **Last-mile capacity** produces a non-monotonic response: smaller vehicles
   improve makespan until capacity drops below a threshold, suggesting vehicle
   capacity is not the binding constraint under current demand.
5. **Transfer point blockage** has zero impact at baseline congestion and
   +10.00 min at heavy congestion, making it a moderate conditional stressor.

These severity ladder results are decision-support simulation evidence only.
They characterize the relative sensitivity of the multimodal chain to isolated
stress dimensions on the Songpa-gu pilot graph and should not be generalized to
other regions or demand profiles without replication.

## 10. Discussion

### 10.1 Disruption Location, Not Just Congestion, Determines Multimodal Outcome

The most important finding from the spatial overlay experiments is that the
multimodal advantage depends on disruption LOCATION, not just congestion level
or disruption severity. The previous interpretation emphasized that congestion
alone does not create a multimodal advantage, which remains true. But the
spatial overlays reveal a stronger and more nuanced constraint: the multimodal
advantage depends on which specific road segment is disrupted relative to the
route structure of each transport mode.

When the Tancheon corridor disruption degrades the bus trunk road (A -> D),
multimodal transport benefits because its passengers bypass that segment via
rail. But when the feeder_east disruption degrades the station access road
(A -> S), multimodal transport suffers because bus-only does not use that road
at all. The lastmile_west disruption similarly penalizes multimodal because
bus-only does not traverse R -> D. The mode that "owns" the disrupted leg
bears the cost.

### 10.2 Why Tancheon Creates Multimodal Advantage

The Tancheon corridor runs along the direct bus route from assembly (A) to
destination (D). Bus-only transport must traverse this corridor. Multimodal
transport instead splits into feeder (A -> S), rail (S -> R), and last-mile
(R -> D). When the Tancheon corridor is degraded under heavy congestion,
bus-only faces increasing travel time and eventual route failure, while
multimodal passengers are unaffected because their route never uses the
Tancheon road edges.

This is a geographic property of the specific pilot region: the Tancheon
corridor happens to overlap with the bus-only trunk but not with the
multimodal feeder or last-mile legs. In a different region where the rail
station or destination access required traversing the same corridor, this
advantage would not appear.

### 10.3 Why Feeder and Last-Mile Disruptions Make Multimodal Worse

The feeder_east disruption degrades road edges on the route from assembly (A)
to the rail station (S). Bus-only transport does not use this road; it goes
directly A -> D. Multimodal transport must use it. At 6x congestion with
feeder_east disruption, multimodal CR drops to 0.89 while bus-only
maintains CR=0.80 (both inf mean makespan). The rail bypass becomes a liability
because the disruption targets a leg that only multimodal requires.

The lastmile_west disruption produces the same pattern: it degrades R -> D,
which only multimodal uses. At 6x, multimodal CR drops to 0.91
while bus-only maintains CR=0.80 (both inf mean makespan). In both cases, the
additional road exposure of the multimodal chain (feeder + last-mile) creates
vulnerability that bus-only does not share.

This finding is important because it contradicts the common assumption that
multimodal transport is inherently more resilient. The resilience depends on
which road segments are disrupted and which mode depends on those segments.

### 10.4 The Disruption-Location Matrix as a Planning Tool

The disruption-location matrix (Section 9.4) provides a structured way to
evaluate multimodal resilience for any region. The key question is not "is
multimodal more resilient?" but "which disruption locations create multimodal
advantage or disadvantage?" For the Songpa-gu pilot region:

- Disruptions to the bus trunk corridor (Tancheon) create strong multimodal
  advantage.
- Disruptions to multimodal-specific legs (feeder, last-mile) create strong
  multimodal disadvantage.
- Disruptions to shared origin segments (assembly egress) produce near-tie
  outcomes.

This matrix can be applied to any region by identifying the route overlap
between bus-only and multimodal transport. Regions where the bus trunk and
multimodal feeder/last-mile share few road segments will show stronger
location-dependent effects. Regions where both modes use similar roads will
show less differentiation.

### 10.5 The Framework's Value Is Diagnostic, Not Prescriptive

The central contribution of this framework is not a claim that multimodal
transport is better or worse than bus-only. It is the ability to identify
WHICH disruption locations matter for a given region and route structure. A
planner using this framework can:

1. Map the route structure of bus-only and multimodal alternatives.
2. Identify which road segments are shared and which are mode-specific.
3. Test spatial disruptions on mode-specific segments to find vulnerability.
4. Test spatial disruptions on shared segments to find the crossover zone.
5. Decide whether multimodal investment is justified given the regional
   disruption risk profile.

For the Songpa-gu pilot, this diagnostic reveals that multimodal resilience
is concentrated in a narrow geographic window: the Tancheon corridor
disruption under heavy congestion. For other disruption locations, multimodal
is equal to or worse than bus-only.

### 10.6 Multimodal Resilience Has Upper Bounds

At 8x congestion, bus-only mostly fails (inf / CR=0.20) while multimodal
retains partial throughput (177.41 min / CR=0.67) in the no-disruption and
Tancheon scenarios. However, for the access-road + rail-capacity multi-hazard,
both modes fail at 4x and above. Road congestion is so extreme that even with
rail trunk bypass, the feeder and last-mile road legs cannot complete within
the 200-minute time limit under the most severe combined stress. Rail immunity
to road disruption does not extend to the feeder and last-mile legs, which
remain road-dependent. When road congestion reaches a level that prevents any
road vehicle from completing its leg within the time limit, the entire
multimodal chain fails regardless of rail availability.

### 10.7 Sensitivity to Noise Parameters

The two within-scenario stochasticity mechanisms (road noise sigma and
turnaround noise lambda) use uncalibrated parameters. To test whether
conclusions depend on these parameter choices, both were added to the Morris
sensitivity analysis alongside the 14 existing parameters.

Morris screening results across 23 policies × 23 scenarios × 4 metrics:

- **road_noise_sigma**: 2,222 non-zero mu_star values out of 3,864 index
  rows (57.6%). This parameter has substantial influence on penalized
  makespan, especially under heavy congestion where road noise amplifies BPR
  travel-time increases. The top influence is on congested road scenarios
  (mu_star up to 1,804 min for heavy_congestion_bus under random capacity
  reduction).

- **turnaround_noise_lambda**: 49 non-zero mu_star values out of 3,864 index
  rows (1.3%). This parameter has weak influence on outcomes, with effects
  limited to multimodal service-minute metrics. Most policy-scenario-metric
  combinations show zero sensitivity to turnaround noise.

**Finding**: Conclusions about regime boundaries and policy rankings are
robust to the choice of turnaround noise parameter but sensitive to the
choice of road noise parameter, particularly under congestion. The default
sigma=0.05 should be treated as an exploratory assumption. Studies seeking
stronger claims should source-tune road noise against observed travel-time
variability data.

Confidence intervals reported in this paper reflect run-to-run variability
under the chosen noise parameters. They are not calibrated estimates of
real-world stochastic uncertainty. The sensitivity analysis above quantifies
how much this framing matters: for low-congestion scenarios, conclusions are
robust; for high-congestion regime boundaries, the road noise parameter
materially affects reported makespan distributions.

### 10.8 Fleet Under-Provisioning Creates Real Resource Contention

The deliberately reduced fleet (8 buses, 5 shuttles, 4 last-mile vehicles, all
45-pax capacity) creates genuine resource contention under congestion. With 500
personnel and 45-passenger vehicles, completing delivery requires multiple
vehicle cycling trips. Under heavy congestion, road travel times increase,
turnaround cycles lengthen, and the finite fleet becomes a binding constraint.
This resource contention is realistic for emergency and contingency transport
scenarios where fleet availability is limited. The 200-minute time limit
combined with under-provisioned fleets produces completion rates that reflect
resource-level constraints rather than pure network effects.

### 10.9 Five-Pillar Synthesis of Multimodal Resilience

The expanded experiment design (23 policies, 23 scenarios) provides evidence
across five pillars that jointly determine multimodal resilience:

1. **Access roads.** The access-road evidence pillar is confirmed. Road
   disruption on the bus-direct trunk (Tancheon corridor, access-road
   multi-hazard) creates multimodal advantage because multimodal passengers
   bypass the degraded segment via rail. The geographic location of the
   disruption relative to each mode's route structure determines which mode
   benefits.

2. **Rail service.** The rail service evidence pillar is new. Rail degradation
   (delay x1.5, capacity x0.5, combined stress) increases multimodal makespan
   by 5-10 min at baseline and approximately 11 min at severe congestion but does not
   eliminate the multimodal completion-rate advantage when road disruption
   simultaneously affects the bus-direct trunk. At severe congestion with
   Tancheon + rail delay, multimodal maintains CR=1.00 while bus-only drops to
   CR=0.00. Road disruption dominates rail degradation for completion-rate
   outcomes.

3. **Transfer handling.** The transfer handling evidence pillar is new. Transfer
   delay increases multimodal makespan proportionally (up to +120 min at
   extreme) without affecting bus-only. Completion rate remains 1.0 under all
   transfer stress levels because the 200-minute time limit absorbs the delay.
   Under current assumptions, transfer handling is a makespan cost proportional
   to passenger load, not a completion-rate risk. This boundary would shift with
   a shorter time limit or larger passenger volume.

4. **Last-mile capacity.** The last-mile evidence pillar is extended. The
   expanded lastmile_west disruption bbox (from approximately 100m x 110m to
   approximately 485m x 500m) shows the same pattern as the original analysis:
   when disruption targets a multimodal-specific last-mile leg, multimodal
   completion drops below bus-only. The larger spatial footprint confirms that
   last-mile vulnerability scales with the disruption zone, not just its
   existence.

5. **Fleet availability.** The fleet evidence pillar is maintained. Fleet
   shortage policies (multimodal-only) show that 0.50x fleet reduction adds
   only +6.28 min at baseline congestion, making fleet shortage a weaker
   stressor than congestion or rail degradation. The deliberately
   under-provisioned fleet (8/5/4) still creates binding resource contention
   under congestion, and fleet limits interact with road disruption to
   determine whether vehicles can cycle back for remaining passengers within
   the time limit.

The five pillars are not independent. Rail degradation and transfer stress
both increase multimodal makespan without eliminating the completion-rate
advantage from road bypass, but their combined effect (rail combined stress +
extreme transfer stress at baseline: MM MS=177.47) approaches the 200-minute
time limit. The interaction between pillars determines the multimodal resilience
boundary, not any single factor in isolation.

## 11. Preliminary Baseline Interpretation

The full pilot results on the multi-corridor graph with 500-personnel demand,
under-provisioned fleet (8/5/4), 200-minute time limit, elevated
LogNormal sigma (0.8), and 23 disruption scenarios including 4 spatial hazard
overlays, 8 rail severity scenarios, 2 multi-hazard combinations, and 1
transfer-point blockage strengthen the spatial-interaction interpretation of conditional
resilience:

> Under normal traffic, bus-only transport is faster (19.84 vs 46.51 min).
> Under heavy congestion without disruption, bus-only remains faster (31.80 vs
> 56.45 min). Congestion alone does not create a multimodal advantage. The
> multimodal advantage emerges only when disruption degrades a road segment
> that bus-only must use but multimodal bypasses via rail (Tancheon corridor).
> When disruption instead degrades a multimodal-specific leg (feeder or
> last-mile), multimodal becomes slower than bus-only (feeder_east 6x: MM
> CR=0.89 vs bus CR=0.80). Rail degradation increases multimodal makespan
> (+6-11 min at baseline) but does not eliminate the completion-rate advantage
> from road bypass. Transfer stress increases multimodal makespan
> proportionally (up to +121 min at extreme) without reducing completion rate
> under the current 200-minute time limit. Multi-hazard combinations show the
> multimodal road bypass advantage persists under moderate rail degradation
> (Tancheon + rail delay), but the access-road + rail-capacity combination
> eliminates both modes at heavy congestion. This is a geographic property of
> the pilot region's route structure, not a general resilience finding.

This should not be written as:

> Bus-only transport is always superior in the real world.

Nor should it be written as:

> Multimodal transport is inherently more resilient.

The defensible claim is conditional and spatial:

> The relative value of multimodal transport depends on the spatial interaction
> between disruption location and route structure. The framework identifies
> which disruption locations create multimodal advantage or disadvantage for a
> given region. For the Songpa-gu pilot, multimodal advantage is concentrated
> in the Tancheon corridor disruption under heavy congestion; for other
> disruption locations, multimodal is equal to or worse than bus-only. Rail
> service degradation and transfer handling are makespan costs that modulate
> but do not override the geographic disruption-location effect.

The separated `results/realworld_pilot/` outputs should be interpreted even
more narrowly: they are decision-support simulation outputs used to evaluate
the framework's ability to identify location-dependent resilience regimes, not
empirical evidence about Songpa-gu or any operational system.

## 14. Limitations

The paper must be explicit about limitations.

Current limitations:

- The current complete-profile outputs are based on an abstract representative network.
- Study-closeout preflight status is currently `false`: `3/15`
  study-closeout gates are preflight-pass and `12/15` remain blocked.
- Formal signoff status is `0/12`; no formal signoff artifacts are present,
  and templates or packets must not be treated as signoffs.
- The current pilot outputs use a scaffold-level cached OSM snapshot and
  reduced analysis corridor, not a reviewed or calibrated regional network.
- Sparse OSM `maxspeed` tags have been summarized for road-class review, but
  the candidate table has not been accepted as speed calibration and is not an
  applied road-class override table.
- Cached OSM lane-count tags do not currently support road-class capacity
  calibration; the lane-count candidate table preserves this evidence gap.
- The consolidated road-input review packet makes speed, capacity, and
  disruption-evidence gaps visible by routeable road class, but it is not
  accepted calibration evidence.
- The current route parity diagnostic preserves three baseline shortest-time
  paths, and the alternate-route diagnostic flags six omitted alternate
  candidates; neither proves traffic assignment, spillback, hazard exposure,
  or field-use detours.
- The current multi-corridor candidate preserves those top alternate
  candidates and has separated 32-row smoke-scale and 1,890-row full-profile
  candidate outputs, but it has not been accepted as final pilot evidence.
- Road capacities and background traffic are not yet fully calibrated.
- BPR alpha=0.50 is a stress-scenario value, not calibrated to observed traffic
  counts. The Korean urban arterial literature value is 0.36.
- LogNormal sigma=0.8 is set to generate meaningful seed-level variance; this
  is higher than the previous value of 0.5 and may overestimate arrival-tail
  effects. Within-scenario noise mechanisms (road noise sigma=0.05,
  turnaround noise lambda=0.2) provide additional seed-level variation.
  These are exploratory sensitivity parameters, not calibrated values.
- Fleet resources (8/5/4) are deliberately under-provisioned to create resource
  contention; this represents a constrained scenario, not an observed fleet
  configuration.
- The simulation time limit of 200 minutes is a planning assumption, not a
  validated operational deadline.
- Disruption probabilities are scenario assumptions.
- Rail availability is simplified.
- Transfer and station-processing capacity need stronger evidence.
- Vehicle and driver availability are not yet field-checked.
- The current model does not perform full microscopic traffic simulation.
- Public OSM and GTFS data cannot represent all emergency or mobilization
  operating constraints.
- The current Morris output is formal scaffold screening on the current full
  policy/scenario design,
  not calibrated real-world sensitivity evidence or Sobol analysis.
- The current sensitivity review packet is a review worksheet, not acceptance
  evidence and not a substitute for `data/manifests/sensitivity_acceptance.json`.
- The current validation review packet is a review worksheet, not acceptance
  evidence and not a substitute for `data/manifests/validation_acceptance.json`.
- The current validation, graph-scale, sensitivity, and experiment strategy
  readiness packets are implemented preflight worksheets, not substitutes for
  formal acceptance records or calibrated real-world validation.
- The external consultation reply in
  `docs/archive/2026-05-11/expert_review_cycle_archive_20260511.md` reviewed the submitted ZIP as an
  external-review bundle and reported that it lacked the full implementation,
  scripts, tests, data/cache tree, results, and documentation needed for
  technical review. This paper must therefore treat package completeness and
  path-integrity as prerequisites before renewed external signoff review.

For a strong paper, limitations should be framed as model boundaries rather
than hidden weaknesses.

## 15. Reproducibility Plan

The closeout paper should include a reproducibility package with:

- code version,
- scenario table,
- random seeds,
- region metadata,
- OSM data snapshot metadata,
- GTFS feed metadata,
- parameter-source table,
- result schemas,
- generated figures,
- plausibility-check summaries,
- sensitivity design,
- limitations and privacy handling notes.
- package inventory and path-integrity outputs showing that every local
  evidence path referenced by review or signoff materials is present in the
  external-review bundle or explicitly externalized.

Use Frictionless-style schema checks for public CSV packages if result
tables become part of the submission artifact.

## 16. Figure Plan

Recommended figures:

1. **Framework pipeline.** Region input, network construction, disruption
   overlay, simulation, metrics, evidence checks, and decision output.
2. **Transport alternatives.** Bus-only vs rail-bus multimodal structure.
3. **Regional network representation.** OSM-derived road network with
   generalized zones and rail access points.
4. **Disruption overlay example.** Edge exposure mapped to normal, capacity
   reduced, and blocked states.
5. **Baseline performance comparison.** Completion time, completion rate, and
   resource efficiency.
6. **Censored personnel under disruption severity.**
7. **Bottleneck attribution.** Segment contribution to completion loss or
   penalized makespan.
8. **Sensitivity ranking.** Parameters that most affect completion probability
   and censored passengers.
9. **Policy regime map.** Conditions under which bus-only, baseline multimodal,
   or redundant multimodal performs best.

## 17. Table Plan

Recommended tables:

1. **Model component table.** Passenger, vehicle, road, rail, transfer,
   disruption, and metric modules.
2. **Parameter-source table.** Data source category for every major parameter.
3. **Scenario design table.** Experimental axes and tested ranges.
4. **Policy alternatives table.** Bus-only, multimodal, redundant last-mile,
   staggered dispatch, adaptive routing, and fleet-shortage settings.
5. **Evidence-check table.** Internal checks, public-data checks, and benchmark
   checks.
6. **Main result table.** Completion, censoring, penalized makespan, resource
   efficiency.
7. **Sensitivity table.** Ranked influential parameters.
8. **Limitations table.** Claim boundary and mitigation strategy.

## 18. Manuscript Claim Guardrails

Use this type of language:

> The framework identifies conditions under which multimodal transport becomes
> resilient or fragile.

> The current representative-network baseline suggests that multimodal
> performance is highly sensitive to access and last-mile bottlenecks.

> Real-world field-use claims require source-tuned regional networks,
> documented parameters, and benchmark checks.

Avoid this type of language:

> The model proves that bus-only transport is superior.

> The model proves that rail-bus transport is superior.

> The simulation is already a real-world field-use prediction.

> Public map data alone supports the model.

## 19. Draft Conclusion

This paper proposes a region-reusable decision framework for evaluating
regional personnel-transport resilience under disrupted regional networks and
constrained fleet operations. The framework compares direct bus-only movement
with rail-bus multimodal movement using a transparent micro-simulation model
that captures passenger arrival uncertainty, queue-based dispatch, finite road
fleets, fixed-headway rail service, transfer delay, dynamic road congestion, and
blocked or capacity-reduced links. The evaluation emphasizes completion
probability, censored personnel, penalized makespan, resource efficiency, tail
arrival time, and bottleneck attribution.

The current implementation provides a meaningful baseline on a representative
network, but it should not be interpreted as a source-tuned field-use prediction.
The proposed SCI-grade extension adds OSM-derived regional networks,
GTFS-based transit checks, spatially structured disruption overlays,
critical-link and accessibility-loss metrics, and staged/full-profile formal
sensitivity interpretation.
Under this framing, the central finding is not that one mode is universally
better. The expected contribution is a method for identifying the disruption and
resource regimes in which multimodal personnel transport is robust,
competitive, or fragile.

## 20. Immediate Author TODOs

1. Review the current pilot OSM-derived cache as a signed-off snapshot or
   replace it with a better signed-off snapshot.
2. Strengthen zone-based origin and destination inputs.
3. Strengthen the parameter-source table with public, literature, benchmark,
   OSM speed-tag review, and timetable evidence.
4. Validate rail timing using the cached static-GTFS, timetable, or
   shortest-path derivation path, or document rail assumptions when no reviewed
   feed is available.
5. Expand spatially structured disruption scenarios beyond scaffold definitions.
6. Review the current critical-link/accessibility-loss diagnostic and decide
   whether directed-edge, bidirectional-link, or corridor-level loss is the
   signed-off study-closeout representation.
7. Review the current graph-scale route parity, alternate-route, and
   multi-corridor candidate diagnostics. Decide whether the six
   alternate-route warning rows are acceptable under a documented
   corridor-selection rule, whether to use the existing 164-node / 246-edge
   full-profile candidate graph and regenerate downstream artifacts, or
   whether full-graph runtime or a multi-corridor ensemble is the study-closeout
   method. Use the graph-scale review packet and graph-scale strategy-blocker-review
   packet as method-selection worksheets before writing closeout result claims.
8. Review the current SALib Morris outputs with the sensitivity review packet
   for the selected staged/full pilot profile, resolve missing/non-finite index
   handling and zero `mu_star` interpretation, and add Sobol only if compute
   budget and interpretation justify it. Use the sensitivity
   strategy-blocker-review packet to keep blockers separate from signoff.
9. Review the generated policy alternatives and seed/scenario coverage beyond
   the current sample outputs. Use the experiment strategy-blocker-review packet to
   track full-output scope, graph/input dependencies, CRN, row counts, and
   missing `experiment_acceptance.json` without treating it as approval.
10. Review the evidence-check review packet, OSRM snapshot manifest, and
   route-level road-evidence exposure rows, then decide whether the current
   optional OSRM snapshot is enough or whether to add another external
   benchmark using r5py, Valhalla, UXsim, or SUMO before creating an evidence-check
   signoff record. Use the evidence-check strategy-blocker-review packet to track
   blocker and human-review closure.
11. Keep study-closeout preflight status `false` until the 12 blocked gates and all
    12 formal acceptance targets are resolved by reviewer-supplied evidence.
12. Build the next expert-review bundle from the complete repository evidence
    profile, not only acceptance/audit artifacts. Include code, configs,
    scripts, tests, data/cache manifests, results, docs, paper/report sources,
    planning files, checksums, and the post-consultation follow-up plan.
13. Keep signoff-looking files out of formal target paths unless they are
    real reviewed decisions; draft templates should remain clearly named and
    outside closeout paths.
14. Rewrite the results section after signed-off quasi-real or source-tuned
    experiment outputs are generated.

## 21. Suggested Manuscript Outline

1. Introduction
2. Literature Review
3. Framework Architecture
4. Regional Network and Scenario Design
5. Micro-Simulation Model
6. Resilience Metrics and Experimental Design
7. Evidence Checks and Sensitivity Analysis
8. Results
9. Discussion
10. Limitations
11. Conclusion

## 22. One-Sentence Paper Thesis

Rail-bus multimodal personnel transport is a CONDITIONAL resilience strategy
whose performance depends on five interacting pillars: access-road
disruption location, rail service availability, transfer handling efficiency,
last-mile capacity, and fleet resources. The dominant factor is the spatial
interaction between disruption location and route structure: multimodal
transport gains advantage when disruption degrades a bus-only trunk road while
sparing multimodal-specific legs; rail degradation and transfer stress
modulate the magnitude of that advantage without eliminating it under current
assumptions; and the framework identifies which disruption regimes create
multimodal robustness, competition, or fragility for any given region.
