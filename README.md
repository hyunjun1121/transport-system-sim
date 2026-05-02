# Transport System Simulation

Disrupted regional personnel-transport micro-simulation comparing **bus-only**
and **rail-bus multimodal** movement for approximately 1,000 people.

The implemented baseline was originally developed for a reserve-force transport
case. The active research direction is now broader: evolve the model into an
open-data, region-reusable, real-world or quasi-real transport-resilience study
for emergency personnel movement, disrupted regional mobility, and
public-sector contingency transport planning.

The implemented scenarios are:

- `bus_only`: passengers assemble at `A` and travel by road to `D`.
- `multimodal`: passengers shuttle from `A` to `S`, ride rail from `S` to `R`,
  then complete the last mile by road to `D`.

The current generated results are conditional findings under a representative
abstract network. They should not be interpreted as calibrated operational
forecasts.

## Windows Setup

Use Windows PowerShell from the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

If `py -3.11` is unavailable, install Python 3.11+ for Windows and enable the
Python Launcher during installation.

## Run

```powershell
.\.venv\Scripts\python main.py --test       # Single paired scenario debug run
.\.venv\Scripts\python main.py --quick      # Reduced smoke run, writes results/
.\.venv\Scripts\python main.py --phase 1    # Phase 1 only
.\.venv\Scripts\python main.py --phase 2    # Phase 2 only
.\.venv\Scripts\python main.py              # Full experiment
```

`--quick` reduces replications and grid sizes, but it still writes CSV and PNG
artifacts under `results/`.

## Tests

Each test file is directly executable; the project does not require pytest.

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

To run the direct-execution tests as a batch in PowerShell:

```powershell
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
```

## Current Architecture

```text
main.py                    # CLI entry: --quick, --test, --phase 1|2
config.yaml                # Network, stochastic model, dispatch, DoE, KPI config
requirements.txt           # Python dependencies for Windows venv setup
generate_report.py         # Builds report.docx from report_draft.md
report_draft.md            # Korean report source
report.docx                # Generated Word report
src/
  sim_types.py             # Passenger, VehicleTrip, EdgeDisruption records
  network.py               # NetworkX DiGraph builder from config
  models.py                # BPR, arrival delay, legacy failure/travel helpers
  policies.py              # StrictPolicy and GracePolicy(W, theta)
  dispatch.py              # Queue-based dispatch manifest planning
  fleet.py                 # Fleet availability and turnaround assignment
  traffic.py               # Rolling-window dynamic road volume and BPR traversal
  disruptions.py           # Blocked/degraded edge disruption sampling
  rail.py                  # Fixed-headway rail service helpers
  transfers.py             # Fixed plus per-passenger transfer delay helpers
  metrics.py               # Makespan, completion, censoring, resource KPIs
  scenario.py              # Scenario orchestrator: run_scenario(...) -> dict
  experiment/
    doe.py                 # Phase 1 and Phase 2 grids
    runner.py              # CRN paired experiment execution
    analysis.py            # CI, break-even, Phase 1 summaries
  visualize/
    plots.py               # Heatmaps, success-rate plots, Pareto, break-even
tests/                     # Direct-execution regression and unit tests
results/                   # Generated CSV and PNG experiment outputs
paper/                     # English paper/manuscript scaffold
cloned_repo/               # Public repo source snapshots for reference
```

## Research And Planning Documents

The current research context is distributed across these Markdown files:

| File | Purpose |
| --- | --- |
| `status.md` | Current project context, generated outputs, limitations, research direction, and clone state |
| `plan.md` | Remaining work plan for implementation and validation |
| `IMPLEMENTATION_PLAN.md` | Implemented system notes and module contracts |
| `realistic_simulation_requirements.md` | Korean realism requirements for real-world or quasi-real simulation |
| `public_github_repo_research.md` | Public repository research for realistic regional simulation |
| `disrupted_mobilization_resilience_repo_research.md` | Public repository research for disrupted regional resilience framing |
| `real_world_simulation_implementation_blueprint.md` | Extracted implementation ideas from public repos and phased real-world upgrade plan |
| `cloned_repo_manifest.md` | Manifest of local shallow clones in ignored `cloned_repo/` |
| `paper/paper_draft.md` | English manuscript scaffold for a journal-style paper |

`cloned_repo/` contains public repository source snapshots with nested `.git`
metadata removed. These snapshots are references for studying implementation
patterns, not production modules imported by the simulator.

## Config Semantics

`config.yaml` keeps the legacy experiment keys and adds operational namespaces
used by the current scenario runner.

- `network.road_links`: `[from, to, t0_min, capacity_veh_per_hr, base_p_fail]`.
- `network.rail_link`: `[from, to, t0_min, headway_min, capacity_pax_per_train]`.
- `personnel.total`: total passengers in each scenario.
- `personnel.group_size`: vehicle capacity and scheduled batch target.
- `personnel.assembly_time`: absolute assembly time in minutes from midnight.
- `bus.first_departure_min`, `bus.dispatch_interval_min`, `bus.fleet_size`,
  `bus.turnaround_min`: bus-only schedule anchor, dispatch cadence, fleet size,
  and fleet reuse.
- `multimodal.shuttle_first_departure_min`,
  `multimodal.shuttle_dispatch_interval_min`, `multimodal.shuttle_fleet_size`:
  shuttle schedule anchor, dispatch cadence, and fleet size.
- `multimodal.transfer_time_min` and `transfer_per_passenger_min`: transfer
  delay as `base + per_passenger * passenger_count`.
- `multimodal.rail_first_departure_min`: optional first train departure time;
  `null` keeps the default fixed-headway convention.
- `multimodal.lastmile_first_departure_min`,
  `multimodal.lastmile_dispatch_interval_min`,
  `multimodal.lastmile_fleet_size`, `multimodal.lastmile_turnaround_min`, and
  `multimodal.lastmile_vehicle_capacity`: schedule anchor, cadence, finite
  fleet size, reuse time, and vehicle capacity for the road last-mile leg after
  rail arrival.
- `traffic.volume_window_min`: rolling window used to convert simulated vehicle
  entries into hourly BPR volume.
- `traffic.background_volume`: baseline vehicles/hour added to dynamic volume.
- `failure.mode`: `blocked` or `capacity_reduction`.
- `failure.capacity_reduction_factor`: effective capacity multiplier for
  degraded road links, with `0 < factor <= 1`.
- `metrics.late_penalty_min`: per-censored-passenger penalty used by
  `penalized_makespan`.

The configuration includes explicit first-departure fields, finite last-mile
fleet controls, network variant selection, and expanded failure-sensitivity
controls.

`failure_rate.levels` are `p_fail_scale` multipliers, not absolute failure
probabilities. For each road link, sampled probability is:

```text
min(edge_base_p_fail * p_fail_scale, 1.0)
```

Rail links are immune to sampled failures by default.

## Implemented Behavior

- STRICT and GRACE operate on passenger queues. STRICT departs at the scheduled
  time with arrived passengers only; GRACE waits until max wait, threshold, or
  vehicle capacity.
- The GRACE denominator is the scheduled batch target, capped by remaining
  queued demand. The default target is `personnel.group_size`.
- Bus-only, multimodal shuttle, and multimodal last-mile road dispatch use
  configurable finite fleet controls where applicable.
- Rail uses fixed headway; later train departures are not serialized behind
  earlier train travel.
- Bus, shuttle, rail, and last-mile services use explicit first-departure
  semantics where configured. Rail uses
  `multimodal.rail_first_departure_min`.
- Road travel chooses a shortest path at vehicle departure and evaluates BPR at
  each edge entry using current rolling-window traffic volume.
- Failures are structured per-edge states and support both full blockage and
  capacity reduction.
- Multimodal transfers include fixed and crowd-dependent delay.
- Metrics expose censoring through `censored_count`, `completion_rate`, and
  `penalized_makespan` in addition to legacy makespan and success-rate fields.
- Phase 1 and Phase 2 use common random numbers by running paired bus-only and
  multimodal scenarios with the same seed.

## Implemented Model Alignment

- Last-mile movement uses a finite fleet, turnaround, and vehicle capacity model.
- Dispatch schedules use explicit first-departure semantics for bus, shuttle,
  and last-mile services where applicable.
- Resource accounting is split into unit-consistent KPIs such as road
  vehicle-minutes, train-minutes, passenger-minutes, and passengers per service
  minute. The legacy `resource_efficiency` column is documented as an alias.
- Named network variants allow route redundancy to be compared fairly.
- Failure sensitivity spans disruption mode, capacity-reduction factor,
  `p_fail_scale`, and network variant.
- The default Phase 1 sweep uses `baseline` and `matched_redundancy`.
  `multimodal_redundant_lastmile` and `bus_single_corridor` are declared
  selectable sensitivity variants, not part of the current default full result
  set.

## Outputs And Report

Experiment runs write CSV files and plots under `results/`. The current full
result set has 8,400 Phase 1 rows and 840 Phase 2 rows. The Word report is
generated from the Korean Markdown source:

```powershell
.\.venv\Scripts\python generate_report.py
```

After model code changes pass, refresh outputs in this order:

```powershell
.\.venv\Scripts\python -m compileall main.py src tests generate_report.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
.\.venv\Scripts\python main.py --test
.\.venv\Scripts\python main.py --quick
.\.venv\Scripts\python main.py --phase 1
.\.venv\Scripts\python main.py --phase 2
.\.venv\Scripts\python generate_report.py
```

Edit `report_draft.md` for Korean narrative changes, then regenerate
`report.docx`. Do not edit `report.docx` manually unless deliberately accepting
Word-only formatting changes. If model semantics change again, rerun Phase 1/2
before reusing CSV/PNG conclusions.

## Remaining Limitations

- The transport network is abstract and intentionally small; it is not an OSM
  or calibrated Seoul network.
- Dynamic road traffic uses a rolling-window approximation, not full traffic
  assignment, spillback, signal timing, or lane-level simulation.
- Rail is failure-immune by default and uses a single fixed-headway service.
- Operational parameters are uncalibrated scenario assumptions, not field
  estimates.
- The real-world upgrade pipeline has been designed and reference repositories
  have been cloned locally, but those tools are not yet integrated into
  production code.
- Existing generated outputs should be reviewed as stale whenever schedule,
  fleet, KPI, network, or failure experiment semantics change.

## Real-World Upgrade Direction

The next major implementation target is to replace manually defined toy links
with a reusable open-data regional pipeline:

- OSMnx/Pyrosm road-network extraction
- GeoPandas/Shapely region clipping and zone handling
- H3 or administrative-grid sensitive-location abstraction
- GTFS or documented rail timetable assumptions
- spatial hazard/exposure overlays and critical-link disruptions
- routing-engine plausibility checks with tools such as OSRM, Valhalla, r5py,
  routingpy, or UXsim
- SALib-based global sensitivity analysis

The intended paper thesis is:

> Rail-bus multimodal transport is a conditional resilience strategy whose
> performance depends on the joint reliability of access roads, rail service,
> transfer handling, last-mile capacity, and finite fleet availability under
> regional network disruption.
