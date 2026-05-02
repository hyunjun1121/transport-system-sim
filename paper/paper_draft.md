# A Region-Reusable Decision Framework for Disrupted Mobilization Transport Resilience

## Draft Status

This is a working paper draft. It is written as a research design and manuscript
scaffold for developing the current transport simulation project into a
publishable study.

The current implemented simulator already supports queue-based passenger
dispatch, finite fleets, rail-bus multimodal movement, road congestion,
structured disruptions, censoring-aware metrics, and paired experiments.
However, the current result set is based on a representative abstract network.
This draft therefore separates:

- what is already implemented,
- what can be reported as preliminary baseline evidence,
- what must be added before making real-world or SCI-grade claims.

The intended high-level framing is:

> An open-data, region-reusable decision framework for evaluating when
> multimodal mobilization transport becomes resilient or fragile under disrupted
> regional networks and constrained fleet operations.

## Working Title

**A Region-Reusable Decision Framework for Disrupted Mobilization Transport
Resilience under Network Degradation and Constrained Fleet Operations**

Alternative titles:

- **Evaluating Multimodal Mobilization Transport Resilience under Regional
  Network Disruption**
- **Open-Data Micro-Simulation of Disrupted Regional Personnel Movement with
  Constrained Road and Rail Resources**
- **When Does Rail-Bus Multimodal Transport Improve Mobilization Resilience? A
  Network Disruption Simulation Framework**

## Target Paper Type

Recommended paper type:

- applied transportation resilience study
- simulation-based decision framework
- disrupted logistics and emergency mobilization planning paper

The paper should not be framed as:

- a purely military operations report,
- a one-region case study with operational predictions,
- a claim that the current abstract network proves real-world modal superiority.

The strongest framing is a reusable methodology with a guarded regional case
demonstration.

## Abstract Draft

Large-scale personnel movement during regional disruption depends on the joint
availability of road corridors, transit access, fleet resources, transfer
capacity, and dispatch policy. Although multimodal transport can reduce direct
road-vehicle requirements, its performance may collapse when access roads,
transfer points, or last-mile services become bottlenecks. This study develops
a region-reusable micro-simulation framework for evaluating mobilization
transport resilience under network degradation and constrained fleet
operations. The framework compares bus-only and rail-bus multimodal strategies
using queue-based passenger dispatch, finite vehicle fleets, fixed-headway rail
service, transfer delays, dynamic road travel time, and disruption states
including blockage and capacity reduction. Resilience is assessed using
completion probability, censored personnel, penalized makespan,
resource-efficiency measures, tail arrival times, and bottleneck attribution.
The current implementation is first demonstrated on a representative abstract
network, with common-random-number paired experiments across disruption and
policy scenarios. The proposed full research design extends this baseline with
OpenStreetMap-derived regional road networks, GTFS-based transit validation,
spatially structured hazard overlays, critical-link analysis, and formal global
sensitivity analysis. The expected contribution is not a universal ranking of
transport modes, but a decision framework that identifies the disruption and
resource regimes in which multimodal mobilization transport is robust,
competitive, or fragile.

## Keywords

- transport resilience
- disrupted logistics
- mobilization transport
- multimodal simulation
- road-rail integration
- network degradation
- finite fleet dispatch
- critical-link analysis
- sensitivity analysis
- OpenStreetMap

## 1. Introduction

### 1.1 Problem Context

Regional mobilization and emergency personnel movement require moving a large
number of people within a constrained time window. In normal conditions, direct
road transport can appear operationally simple because passengers are loaded
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
operationally fragile if any connector segment becomes a bottleneck.

This motivates a resilience question rather than a simple speed-comparison
question.

### 1.2 Research Gap

Existing transport simulation tools can model road traffic, public transit,
evacuation, routing, or fleet operations. However, a decision maker evaluating
regional mobilization transport under disruption needs an integrated view of:

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
policy logic of mobilization transport. Conversely, small abstract simulations
are easy to interpret but can be criticized as insufficiently realistic. This
paper addresses that gap by proposing a staged framework: a transparent
micro-simulation core, surrounded by open-data network input, validation,
hazard-overlay, and sensitivity-analysis layers.

### 1.3 Research Questions

Primary research question:

> Under which network-disruption and resource-constraint regimes does rail-bus
> multimodal mobilization transport outperform bus-only transport?

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
4. **A path from abstract simulation to open-data validation.** The framework
   specifies how to move from a representative network to OSM-derived roads,
   GTFS-based rail validation, hazard overlays, critical-link metrics, and
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
with calibrated assumptions and validation checks. Public maps alone do not
make a simulation operationally valid.

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
7. **Validation and sensitivity layer.** Checks plausibility against public
   data, routing benchmarks, source tables, and global sensitivity analysis.

### 3.2 Core Design Principle

The core simulator remains intentionally transparent. External tools are added
around it for data ingestion, validation, benchmarking, optimization, and
reporting. This prevents the research from becoming a black-box integration of
a large traffic simulator.

### 3.3 Recommended Open-Source Stack

Core stack for the SCI-grade extension:

- `NetworkX`: graph representation and criticality metrics.
- `OSMnx`: real regional road network extraction.
- `GeoPandas` and `Shapely`: spatial clipping, joins, and zone abstraction.
- `snail`: raster hazard or exposure overlay onto road and rail edges.
- `gtfs-validator` and `gtfs_kit`: public transit feed validation and headway
  extraction.
- `SALib`: global sensitivity analysis.
- `Frictionless`: result-schema and benchmark-package validation.

Benchmark or optional stack:

- `r5py`, `R5`, `OpenTripPlanner`, `Valhalla`, and `OSRM` for travel-time and
  accessibility plausibility checks.
- `UXsim` for Python-native mesoscopic congestion benchmarking.
- `SUMO` and `MATSim` for high-cost external validation experiments.
- `OR-Tools` or `PyVRP` for candidate fleet allocation and contingency routing
  policies.
- `Papermill`, `Quarto`, and `Streamlit` for reproducible analysis and
  decision-support reporting.

## 4. Study Context and Data Design

### 4.1 Application Context

The motivating application is regional mobilization transport from an urban
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
- transit feed source and validation metadata,
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

For the SCI-grade extension, rail assumptions must be validated or
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
should be presented as a controlled approximation and validated against
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
- Common-random-number pairing between bus-only and multimodal scenarios.
- Scenario sweeps over policies, disruption scaling, and selected network
  variants.
- CSV outputs and plots.

These outputs are useful as baseline evidence, but they should be described as
representative-network results rather than real-world calibrated findings.

### 7.2 Required SCI-Grade Extension

The full paper should add:

1. OSM-derived real or quasi-real road network for a pilot region.
2. Zone-based origin and destination representation.
3. GTFS-based rail schedule validation or a documented rail assumption set.
4. Public-data or literature-supported parameter-source table.
5. Spatially structured disruption scenarios.
6. Critical-link and accessibility-loss analysis.
7. Formal sensitivity analysis.
8. Independent routing or transit benchmark checks.
9. Policy alternatives beyond bus-only and baseline rail-bus.

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

Formal sensitivity analysis should be added using a tool such as SALib.

Recommended outputs:

- first-order sensitivity indices,
- total-order sensitivity indices,
- Morris screening if the full Sobol design is too expensive,
- ranked parameter influence on completion rate,
- ranked parameter influence on censored passengers,
- ranked parameter influence on penalized makespan,
- ranked parameter influence on resource efficiency.

Expected high-impact insight:

The most valuable result is not just which alternative wins, but which uncertain
parameters determine the winning regime.

## 8. Validation and Plausibility Checks

### 8.1 Internal Validation

Internal validation checks:

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

## 9. Preliminary Baseline Interpretation

The current representative-network experiments support a cautious preliminary
interpretation:

> Under the current representative network and operating assumptions, bus-only
> transport tends to be faster, while rail-bus multimodal transport can show
> resource-efficiency advantages but is sensitive to rail access, transfer, and
> last-mile bottlenecks.

This should not be written as:

> Bus-only transport is always superior in the real world.

Nor should it be written as:

> Multimodal transport is inherently more resilient.

The defensible claim is conditional:

> The relative value of multimodal transport depends on disruption location,
> last-mile redundancy, fleet availability, transfer handling, and rail service
> assumptions.

## 10. Expected Results Section Structure

The results section should be organized around decision logic.

### 10.1 Baseline Comparison

Compare bus-only and multimodal transport under the no-disruption or low
disruption baseline.

Report:

- penalized makespan,
- completion rate,
- censored passengers,
- road vehicle-minutes,
- train-minutes,
- resource efficiency.

### 10.2 Disruption Severity

Show how performance changes as disruption severity increases.

Expected figure:

- completion rate and censored passengers by disruption severity.

### 10.3 Bottleneck Attribution

Identify whether failures are driven by:

- origin access,
- feeder road,
- rail access,
- rail trunk,
- transfer node,
- last-mile road,
- destination access.

### 10.4 Policy Alternatives

Evaluate:

- redundant last-mile fleet,
- staggered dispatch,
- adaptive routing,
- feeder capacity expansion,
- rail-delay scenario,
- fleet shortage scenario.

### 10.5 Sensitivity Results

Report which parameters dominate:

- completion probability,
- censored personnel,
- tail arrival time,
- resource efficiency.

### 10.6 Cross-Region Demonstration

If time permits, demonstrate the same pipeline on a second non-sensitive region.
This would strongly support the region-reusable claim.

## 11. Discussion

### 11.1 Main Interpretation

The expected discussion should emphasize regimes, thresholds, and bottlenecks.

Potential final claims:

- Bus-only transport is attractive when direct road access is reliable and fleet
  availability is sufficient.
- Rail-bus multimodal transport becomes more attractive when long road movement
  is constrained but rail access and last-mile redundancy remain functional.
- Multimodal transport can become fragile when transfer handling, rail access,
  or last-mile fleet capacity becomes the limiting segment.
- Completion probability and censored personnel are more decision-relevant than
  average completion time under severe disruption.
- A region-reusable framework is more valuable than a one-off route plan because
  it can identify which assumptions change the preferred policy.

### 11.2 Scientific Contribution

The paper should argue that the contribution is a framework and evidence
structure:

- open-data regional input,
- transparent micro-simulation,
- disruption-aware policy comparison,
- censoring-aware resilience metrics,
- validation and sensitivity workflow.

### 11.3 Practical Contribution

The practical contribution is a way to ask better planning questions:

- Which corridors must remain available?
- Which last-mile links create the largest multimodal fragility?
- How many vehicles are needed before bus-only performance stabilizes?
- When does rail reduce road-fleet burden?
- Which assumptions must be validated before operational conclusions are made?

## 12. Limitations

The paper must be explicit about limitations.

Current limitations:

- The current full outputs are based on an abstract representative network.
- Road capacities and background traffic are not yet fully calibrated.
- Disruption probabilities are scenario assumptions.
- Rail availability is simplified.
- Transfer and station-processing capacity need stronger evidence.
- Vehicle and driver availability are not yet field-validated.
- The current model does not perform full microscopic traffic simulation.
- Public OSM and GTFS data cannot represent all emergency or mobilization
  operating constraints.

For a strong paper, limitations should be framed as model boundaries rather
than hidden weaknesses.

## 13. Reproducibility Plan

The final paper should include a reproducibility package with:

- code version,
- scenario table,
- random seeds,
- region metadata,
- OSM data snapshot metadata,
- GTFS feed metadata,
- parameter-source table,
- result schemas,
- generated figures,
- validation summaries,
- sensitivity design,
- limitations and privacy handling notes.

Use Frictionless-style schema validation for public CSV packages if result
tables become part of the submission artifact.

## 14. Figure Plan

Recommended figures:

1. **Framework pipeline.** Region input, network construction, disruption
   overlay, simulation, metrics, validation, and decision output.
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

## 15. Table Plan

Recommended tables:

1. **Model component table.** Passenger, vehicle, road, rail, transfer,
   disruption, and metric modules.
2. **Parameter-source table.** Data source category for every major parameter.
3. **Scenario design table.** Experimental axes and tested ranges.
4. **Policy alternatives table.** Bus-only, multimodal, redundant last-mile,
   staggered dispatch, adaptive routing, and fleet-shortage settings.
5. **Validation table.** Internal checks, public-data checks, and benchmark
   checks.
6. **Main result table.** Completion, censoring, penalized makespan, resource
   efficiency.
7. **Sensitivity table.** Ranked influential parameters.
8. **Limitations table.** Claim boundary and mitigation strategy.

## 16. Manuscript Claim Guardrails

Use this type of language:

> The framework identifies conditions under which multimodal transport becomes
> resilient or fragile.

> The current representative-network baseline suggests that multimodal
> performance is highly sensitive to access and last-mile bottlenecks.

> Real-world operational claims require calibrated regional networks,
> documented parameters, and validation checks.

Avoid this type of language:

> The model proves that bus-only transport is superior.

> The model proves that rail-bus transport is superior.

> The simulation is already a real-world operational forecast.

> Public map data alone validates the model.

## 17. Draft Conclusion

This paper proposes a region-reusable decision framework for evaluating
mobilization transport resilience under disrupted regional networks and
constrained fleet operations. The framework compares direct bus-only movement
with rail-bus multimodal movement using a transparent micro-simulation model
that captures passenger arrival uncertainty, queue-based dispatch, finite road
fleets, fixed-headway rail service, transfer delay, dynamic road congestion, and
blocked or capacity-reduced links. The evaluation emphasizes completion
probability, censored personnel, penalized makespan, resource efficiency, tail
arrival time, and bottleneck attribution.

The current implementation provides a meaningful baseline on a representative
network, but it should not be interpreted as a calibrated operational forecast.
The proposed SCI-grade extension adds OSM-derived regional networks,
GTFS-based transit validation, spatially structured disruption overlays,
critical-link and accessibility-loss metrics, and formal sensitivity analysis.
Under this framing, the central finding is not that one mode is universally
better. The expected contribution is a method for identifying the disruption and
resource regimes in which multimodal mobilization transport is robust,
competitive, or fragile.

## 18. Immediate Author TODOs

1. Add a real or quasi-real OSM-derived pilot network.
2. Define zone-based origin and destination inputs.
3. Create the parameter-source table.
4. Validate GTFS or documented rail assumptions.
5. Add spatially structured disruption scenarios.
6. Add critical-link and accessibility-loss metrics.
7. Add SALib-based global sensitivity analysis.
8. Add at least two policy alternatives beyond bus-only and baseline
   multimodal.
9. Decide whether to include an external benchmark using r5py, OSRM, Valhalla,
   UXsim, or SUMO.
10. Rewrite the results section after the calibrated or quasi-real experiment
    outputs are generated.

## 19. Suggested Manuscript Outline

1. Introduction
2. Literature Review
3. Framework Architecture
4. Regional Network and Scenario Design
5. Micro-Simulation Model
6. Resilience Metrics and Experimental Design
7. Validation and Sensitivity Analysis
8. Results
9. Discussion
10. Limitations
11. Conclusion

## 20. One-Sentence Paper Thesis

Rail-bus multimodal mobilization transport should be evaluated as a conditional
resilience strategy whose value depends on the joint reliability of access
roads, rail service, transfer handling, last-mile capacity, and fleet
availability under regional network disruption.
