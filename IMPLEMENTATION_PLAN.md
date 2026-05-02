# Implemented System Notes

This document records the current implemented system. It is an implementation
record, not a worker launch schedule.

## Implemented Scope

The current codebase implements the design fixes that replaced the original
early assumptions:

- STRICT and GRACE dispatch policies operate on passenger queues.
- Bus-only, multimodal shuttle, and multimodal last-mile road movement use
  finite fleet controls where applicable.
- Rail movement uses fixed-headway departures; train travel does not block later
  departures.
- Road movement uses dynamic rolling-window link volumes and BPR travel time at
  edge entry.
- Link disruptions are structured as normal, degraded, or blocked edge states.
- Failure sampling supports both `blocked` and `capacity_reduction` modes.
- Multimodal transfers use configurable fixed and per-passenger delay.
- Metrics include completion and censoring KPIs so incomplete runs are visible.
- Phase runners preserve common-random-number paired comparisons.

## Implemented Alignment

The current implementation preserves the modular structure while applying five
model-semantics changes:

- Replaced multimodal last-mile service slots with a finite fleet, turnaround,
  queue, and capacity model.
- Added explicit first-departure schedule semantics so STRICT and GRACE decisions
  are evaluated against a timetable rather than implicit first-arrival timing.
- Split resource accounting into unit-consistent KPIs. Road vehicle-minutes,
  train-minutes, and passenger-minutes are not summed into an ambiguous resource
  field; legacy `resource_efficiency` is an alias for passengers per total
  service minute.
- Added named network variants for fair route-redundancy comparisons.
- Expanded failure sensitivity to include disruption mode, capacity-reduction
  factor, `p_fail_scale`, and network variant in result rows and summaries.

## Module Contracts

- `src/sim_types.py` defines immutable records shared across modules:
  `Passenger`, `VehicleTrip`, `EdgeDisruption`, `EdgeTraversal`, and
  `StationBatch`.
- `src/network.py` builds the abstract `NetworkX` directed graph from
  `config.yaml`.
- `src/models.py` contains BPR travel time, arrival delay sampling, and legacy
  wrappers for failure and static travel-time helpers.
- `src/policies.py` defines `StrictPolicy`, `GracePolicy(W, theta)`, and
  `build_policies(config)`.
- `src/dispatch.py` converts passenger arrivals into scheduled vehicle
  manifests using the selected departure policy.
- `src/fleet.py` applies finite fleet availability and turnaround to requested
  trips.
- `src/disruptions.py` samples per-edge disruption state and computes effective
  capacity.
- `src/traffic.py` records edge entries, computes rolling hourly volume, and
  traverses routes edge-by-edge with BPR.
- `src/rail.py` provides fixed-headway rail service helpers and independent
  train-trip completion.
- `src/transfers.py` computes fixed plus crowd-dependent transfer delay.
- `src/metrics.py` collects makespan, success, completion, censoring, and
  resource-efficiency KPIs.
- `src/scenario.py` orchestrates bus-only and multimodal scenarios through
  `run_scenario(...)`.
- `src/experiment/runner.py` runs Phase 1 and Phase 2 paired experiments.
- `src/experiment/analysis.py` computes finite-value CIs, break-even estimates,
  and Phase 1 summaries.
- `src/visualize/plots.py` writes heatmaps, success-rate comparisons, policy
  Pareto plots, and break-even plots with the non-interactive `Agg` backend.

## Scenario Flow

`run_scenario(G, config, scenario_type, policy, params, seed)` performs these
steps:

1. Sample passenger arrival delays with a seed-derived arrival RNG.
2. Sample road disruptions with a separate seed-derived failure RNG.
3. Create a `MetricsCollector` with total personnel, time limit, and late
   penalty config.
4. Create `DynamicRoadTraffic` from BPR, traffic, congestion-scale, and
   disruption config.
5. Dispatch either the bus-only flow or the multimodal flow.
6. Set leftover personnel and return the KPI dictionary.

Bus-only flow:

1. Plan passenger-queue dispatches from `A`.
2. Apply finite bus fleet availability and turnaround.
3. Pick a dynamic shortest road path from `A` to `D` at vehicle departure.
4. Traverse road edges with dynamic BPR and record destination arrivals.

Multimodal flow:

1. Plan passenger-queue shuttle dispatches from `A` to `S`.
2. Apply finite shuttle fleet availability and turnaround.
3. Apply transfer delay at the station.
4. Board fixed-headway rail service from `S` to `R`.
5. Dispatch finite-fleet last-mile road service from `R` to `D`.
6. Record arrivals that complete within the simulation time limit.

## Config Semantics

Important current semantics:

- `failure_rate.levels` are `p_fail_scale` multipliers, not absolute
  probabilities.
- Road failure probability is
  `min(edge_base_p_fail * p_fail_scale, 1.0)`.
- Rail links are failure-immune by default.
- `bus.first_departure_min` pins the first bus-only departure schedule.
- `multimodal.shuttle_first_departure_min` pins the first shuttle departure
  schedule.
- `multimodal.rail_first_departure_min` can pin the first fixed-headway rail
  departure; `null` keeps the default headway convention.
- `multimodal.lastmile_first_departure_min` optionally pins the last-mile
  schedule anchor. `multimodal.lastmile_fleet_size`,
  `multimodal.lastmile_turnaround_min`, and
  `multimodal.lastmile_vehicle_capacity` control the finite last-mile fleet.
- `failure.mode: blocked` makes a disrupted edge unusable.
- `failure.mode: capacity_reduction` keeps a disrupted road edge usable with
  capacity multiplied by `failure.capacity_reduction_factor`.
- `traffic.background_volume` is vehicles/hour.
- `traffic.volume_window_min` controls the rolling window for simulated edge
  entries; entries are converted to vehicles/hour before calling BPR.
- `personnel.group_size` is both vehicle capacity and the default scheduled
  batch target for dispatch policy evaluation.
- GRACE threshold uses the scheduled batch target capped by remaining demand.
- `metrics.late_penalty_min` is applied per censored passenger in
  `penalized_makespan`.

## Experiment Pipeline

`main.py` exposes the implemented CLI:

```powershell
.\.venv\Scripts\python main.py --test
.\.venv\Scripts\python main.py --quick
.\.venv\Scripts\python main.py --phase 1
.\.venv\Scripts\python main.py --phase 2
.\.venv\Scripts\python main.py
```

Phase 1 runs a grid over congestion scale `s`, `p_fail_scale`, default network
variants, and failure semantics with STRICT policy. The current full Phase 1
result set has 8,400 rows and includes `baseline` and `matched_redundancy`
only; `multimodal_redundant_lastmile` and `bus_single_corridor` are selectable
sensitivity variants outside the default full result set.

Phase 2 runs a grid over lateness severity `sigma` and dispatch policies using
representative Phase 1 values. The current full Phase 2 result set has 840
rows.

Experiment result rows include legacy fields and newer completion-aware fields:

- `bus_makespan`, `multi_makespan`, `delta_makespan`
- `bus_penalized_makespan`, `multi_penalized_makespan`,
  `delta_penalized_makespan`
- `bus_success_rate`, `multi_success_rate`
- `bus_completion_rate`, `multi_completion_rate`
- `bus_leftover`, `multi_leftover`
- `bus_censored_count`, `multi_censored_count`
- resource-efficiency columns where available

## Verification

The direct-execution test suite covers the implemented module split:

```powershell
.\.venv\Scripts\python tests\test_models.py
.\.venv\Scripts\python tests\test_config.py
.\.venv\Scripts\python tests\test_dispatch.py
.\.venv\Scripts\python tests\test_fleet.py
.\.venv\Scripts\python tests\test_traffic.py
.\.venv\Scripts\python tests\test_disruptions.py
.\.venv\Scripts\python tests\test_rail.py
.\.venv\Scripts\python tests\test_transfers.py
.\.venv\Scripts\python tests\test_metrics.py
.\.venv\Scripts\python tests\test_analysis.py
.\.venv\Scripts\python tests\test_scenario.py
```

Use `main.py --test` for a single scenario sanity check and `main.py --quick`
for a reduced end-to-end experiment smoke run.

## Report Regeneration

`report_draft.md` is the Korean Markdown source. Regenerate the Word report
with:

```powershell
.\.venv\Scripts\python generate_report.py
```

After model changes are integrated, use this order before treating results as
current:

```powershell
.\.venv\Scripts\python -m compileall main.py src tests generate_report.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
.\.venv\Scripts\python main.py --test
.\.venv\Scripts\python main.py --quick
.\.venv\Scripts\python main.py --phase 1
.\.venv\Scripts\python main.py --phase 2
.\.venv\Scripts\python generate_report.py
```

Regenerating the report overwrites `report.docx`. Keep report narrative updates
separate from code changes unless the task explicitly includes report work. If
model semantics change again, rerun Phase 1/2 before copying CSV/PNG
interpretations forward.

## Remaining Limitations

- The graph is an abstract, small network rather than a calibrated road and rail
  network.
- Dynamic traffic is a rolling-window BPR approximation, not full traffic
  assignment or microscopic simulation.
- Rail is represented as a single fixed-headway service and remains failure
  immune unless model code changes.
- Operational parameters are uncalibrated scenario assumptions, not validated
  field estimates.
- The default Phase 1 sweep uses `baseline` and `matched_redundancy`; declared
  variants such as `multimodal_redundant_lastmile` and `bus_single_corridor`
  require deliberate result regeneration before they support conclusions.
- Generated experiment outputs and the Korean report need to be reviewed
  together before drawing final narrative conclusions.

## Current Research Extension Direction

The implemented system remains the core scenario evaluator. The next research
extension is to surround it with real-world or quasi-real data and validation
layers rather than replacing it with a large external traffic platform.

Planned extension layers:

- OSMnx/Pyrosm road-network extraction and graph adaptation.
- GeoPandas/Shapely/H3-style regional and sensitive-zone preprocessing.
- GTFS or documented rail schedule assumptions.
- Spatially structured disruptions from critical-link analysis and
  hazard/exposure overlays.
- Routing or multimodal plausibility checks with tools such as OSRM, Valhalla,
  routingpy, r5py/R5, UXsim, or limited SUMO benchmarks.
- SALib sensitivity analysis.
- Result-schema and reproducibility checks using tools such as Frictionless and
  scripted analysis workflows.

The local `cloned_repo/` directory contains ignored shallow clones of public
repositories for reference. It is not part of the implemented source tree.
