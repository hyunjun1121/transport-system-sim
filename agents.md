# AGENTS.md - Transport System Simulation

## Project Overview

Disrupted regional personnel-transport resilience simulation. The implemented
baseline compares **bus-only** vs **rail-bus multimodal** transport for moving
approximately 1,000 people from an assembly context toward a destination zone.

The current research direction is broader than the original wartime/reserve
framing:

> build an open-data, region-reusable, real-world or quasi-real simulation
> pipeline for emergency personnel movement, disrupted regional mobility, and
> public-sector contingency transport planning.

Do not present the current model as an operational route plan or real-world
forecast. It is a decision-support and resilience-evaluation framework.

**Environment**: Windows PowerShell. Use the Python Launcher (`py`) to create a
local virtual environment, then run project commands through
`.\.venv\Scripts\python`.

## Repository Structure

```text
main.py                    # CLI entry: --quick, --test, --phase 1|2
config.yaml                # Network, BPR, stochastic, dispatch, DoE config
requirements.txt           # Python dependencies for Windows/venv setup
generate_report.py         # Generates report.docx from report_draft.md
report_draft.md            # Korean narrative report source
report.docx                # Generated Word document
microsim_experiment_proposal_v3.docx  # Original proposal
status.md                  # Current project context and limitations
plan.md                    # Remaining work guide
IMPLEMENTATION_PLAN.md     # Implemented system notes
realistic_simulation_requirements.md  # Korean realism requirements
public_github_repo_research.md        # Public repo research synthesis
disrupted_mobilization_resilience_repo_research.md
                           # Disrupted-resilience repo research synthesis
real_world_simulation_implementation_blueprint.md
                           # Implementation blueprint from public repo research
cloned_repo_manifest.md    # Manifest for ignored local reference clones
paper/
  paper_draft.md           # English paper/manuscript scaffold
src/
  sim_types.py             # Shared immutable simulation records
  network.py               # Build NetworkX DiGraph from config
  models.py                # BPR, Bernoulli failures, LogNormal delays
  policies.py              # StrictPolicy, GracePolicy(W, theta)
  dispatch.py              # Passenger queues and dispatch manifests
  fleet.py                 # Fleet availability and turnaround
  traffic.py               # Dynamic road volume and BPR edge traversal
  disruptions.py           # Structured blocked/degraded edge states
  rail.py                  # Fixed-headway rail service helpers
  transfers.py             # Fixed and per-passenger transfer delays
  metrics.py               # MetricsCollector KPIs
  scenario.py              # Scenario orchestrator: run_scenario() -> dict
  experiment/
    doe.py                 # phase1_grid, phase2_grid
    runner.py              # CRN paired execution: run_phase1(), run_phase2()
    analysis.py            # compute_ci(), find_breakeven(), summarize_phase1()
  visualize/
    plots.py               # Heatmaps, Pareto curves, break-even line
tests/
  test_models.py           # Model, network, policy, metrics smoke tests
  test_config.py           # Config namespace/schema smoke tests
  test_dispatch.py         # Queue dispatch behavior tests
  test_fleet.py            # Fleet availability tests
  test_traffic.py          # Dynamic traffic and BPR traversal tests
  test_disruptions.py      # Failure/disruption tests
  test_rail.py             # Fixed-headway rail tests
  test_transfers.py        # Transfer-delay tests
  test_metrics.py          # Censoring KPI tests
  test_analysis.py         # CI and summary tests
  test_scenario.py         # End-to-end scenario regression tests
results/                   # Generated CSV outputs and PNG plots
cloned_repo/               # Ignored local shallow clones of public reference repos
```

`refs/` may be used for local reference clones if needed; keep it out of active
implementation and generated-output changes.

`cloned_repo/` is also a local reference cache and is ignored by git. Do not
vendor code from cloned public repositories into this project. Extract design
patterns and implement project-owned code in `src/` instead.

## Windows Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

If `py -3.11` is unavailable, install Python 3.11+ for Windows and enable the
Python Launcher.

## How to Run

```powershell
.\.venv\Scripts\python main.py --test       # Single paired scenario debug
.\.venv\Scripts\python main.py --quick      # Smoke run, writes results/
.\.venv\Scripts\python main.py --phase 1    # Phase 1 only
.\.venv\Scripts\python main.py --phase 2    # Phase 2 only
.\.venv\Scripts\python main.py              # Full experiment
.\.venv\Scripts\python generate_report.py   # Regenerate report.docx
```

Direct test commands:

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

Batch form:

```powershell
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
```

## Key Models

- **BPR**: `t = t0 * (1 + alpha * (s * v / C)^beta)`; defaults are
  `alpha=0.15`, `beta=4.0`.
- **Dynamic road volume**: `traffic.background_volume` plus rolling-window
  simulated vehicle entries converted to vehicles/hour.
- **Link failure**: road-link probability is
  `min(edge_base_p_fail * p_fail_scale, 1.0)`.
- **Failure modes**: `blocked` gives infinite traversal time; `capacity_reduction`
  multiplies effective road capacity by `failure.capacity_reduction_factor`.
- **Rail failure**: rail is immune by default.
- **Lateness**: `Y ~ LogNormal(mu=2.0, sigma^2)`; sigma controls long-tail
  arrival delay.
- **STRICT policy**: depart immediately at scheduled time with arrived
  passengers only.
- **GRACE policy**: wait until max `W` minutes, `theta` fraction arrived, or
  vehicle capacity reached.
- **CRN pairing**: paired bus-only and multimodal replications use the same
  seed. The scenario runner uses separate arrival and failure RNG streams
  derived from that seed.

## Config Schema Notes

`config.yaml` keeps legacy experiment keys and includes operational namespaces
used by the current scenario runner:

- `bus.first_departure_min`, `bus.dispatch_interval_min`,
  `bus.fleet_size`, `bus.turnaround_min`
- `multimodal.shuttle_first_departure_min`,
  `multimodal.shuttle_dispatch_interval_min`,
  `multimodal.shuttle_fleet_size`, `multimodal.transfer_time_min`,
  `multimodal.transfer_per_passenger_min`,
  `multimodal.rail_first_departure_min`,
  `multimodal.lastmile_first_departure_min`,
  `multimodal.lastmile_dispatch_interval_min`,
  `multimodal.lastmile_fleet_size`,
  `multimodal.lastmile_turnaround_min`,
  `multimodal.lastmile_vehicle_capacity`
- `traffic.volume_window_min`, `traffic.background_volume`
- `failure.mode`, `failure.capacity_reduction_factor`
- `metrics.late_penalty_min`
- `experiment.R`, `experiment.seed_base`, `experiment.time_limit`

`failure_rate.levels` are `p_fail_scale` multipliers, not actual probabilities.
Keep `failure_rate.parameter` and `failure_rate.semantics` aligned with that
behavior unless the model code is deliberately changed.

Config validation guidance:

- Run `.\.venv\Scripts\python tests\test_config.py` after schema edits.
- Keep minute fields non-negative and fleet sizes at least 1.
- Keep `traffic.volume_window_min > 0`.
- Use `failure.mode: blocked` or `failure.mode: capacity_reduction`.
- Keep `0 < failure.capacity_reduction_factor <= 1`.

Config includes finite last-mile fleet controls, explicit first-departure
schedule controls, network variant selection, and expanded failure-sensitivity
dimensions. Keep documentation aligned with the implemented code and tests.

## Implemented Design Fixes

- STRICT and GRACE now operate on passenger queues rather than waiting for the
  last passenger in a pre-batched group.
- Bus-only and multimodal shuttle dispatch use configurable fleet size, dispatch
  interval, and turnaround.
- Multimodal last-mile dispatch uses a finite fleet, vehicle capacity, dispatch
  interval, turnaround, and optional first-departure anchor.
- Rail departures follow fixed headway and are not serialized by earlier train
  travel. `multimodal.rail_first_departure_min` can pin the first scheduled
  train departure when needed.
- Road travel uses dynamic per-link traffic volume with BPR travel time at edge
  entry.
- Failure sampling supports `blocked` and `capacity_reduction` modes.
- Multimodal transfers include configurable fixed and per-passenger delay.
- Metrics include explicit censoring KPIs: `censored_count`, `completion_rate`,
  and `penalized_makespan`.

## Implemented Model Alignment

The implemented model includes finite last-mile fleet modeling, explicit
schedule semantics, unit-consistent resource KPIs, named network variants, and
expanded failure sensitivity. If these semantics change again, rerun Phase 1/2
before updating result conclusions.

Current full generated outputs contain 8,400 Phase 1 rows and 840 Phase 2 rows.
The default Phase 1 sweep includes only `baseline` and `matched_redundancy`;
`multimodal_redundant_lastmile` and `bus_single_corridor` are declared
selectable sensitivity variants outside the current default full result set.

## Current Research Upgrade Direction

The next major implementation goal is to move from a representative abstract
network to a real-world or quasi-real regional case.

Priority implementation layers:

1. **Open-data regional network input** using OSMnx/Pyrosm,
   GeoPandas/Shapely, and zone abstraction such as H3/admin-grid cells.
2. **Spatially structured disruptions** using critical-link scenarios and
   hazard/exposure overlays inspired by `snail` and `open-gira`.
3. **Public transit and rail validation** using GTFS where available, or a
   documented rail-assumption table when GTFS is incomplete.
4. **Plausibility benchmarking** with routing or multimodal tools such as
   OSRM, Valhalla, routingpy, r5py/R5, or UXsim as appropriate.
5. **Policy alternatives** beyond baseline bus-only and baseline multimodal:
   redundant last-mile fleet, increased feeder capacity, staggered dispatch,
   adaptive rerouting, fleet shortage, and rail delay/unavailability.
6. **Formal sensitivity analysis** with SALib over fleet, arrival, disruption,
   transfer, road-traffic, and rail parameters.

The main thesis for the paper direction is:

> Rail-bus multimodal transport is a conditional resilience strategy whose
> performance depends on access roads, rail service, transfer handling,
> last-mile capacity, and finite fleet availability under disruption.

## Report Workflow

`report_draft.md` is the Korean source document. Regenerate the Word document
with:

```powershell
.\.venv\Scripts\python generate_report.py
```

After model code changes pass and refreshed outputs are requested, use this
Windows PowerShell workflow:

```powershell
.\.venv\Scripts\python -m compileall main.py src tests generate_report.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
.\.venv\Scripts\python main.py --test
.\.venv\Scripts\python main.py --quick
.\.venv\Scripts\python main.py --phase 1
.\.venv\Scripts\python main.py --phase 2
.\.venv\Scripts\python generate_report.py
```

Do not edit `report.docx` or `results/` as part of routine code/documentation
changes unless refreshed outputs are explicitly requested. If model semantics
change, rerun full experiments before carrying result conclusions forward.

## Remaining Limitations

- The currently implemented experiment network is abstract and intentionally
  small.
- Dynamic traffic uses rolling-window BPR, not full traffic assignment or
  microscopic road simulation.
- Rail is a single fixed-headway service and is failure-immune by default.
- Operational parameters are uncalibrated scenario assumptions.
- The public repository clone cache exists for reference only; none of those
  tools have yet been integrated into the production simulation pipeline.
- The paper draft and real-world implementation blueprint define the next
  research direction but do not by themselves create calibrated real-world
  results.
- The default Phase 1 sweep covers `baseline` and `matched_redundancy`; the
  additional declared sensitivity variants require an explicit result
  regeneration before they are used in conclusions.
- Report narrative and generated outputs should be reviewed together after a
  new full experiment is accepted.

## Git

- Remote: `https://github.com/hyunjun1121/transport-system-sim.git`
- Branch: `main`
- Configure local commit identity if commits are needed:
  `git config user.name "hyunjun1121"` and
  `git config user.email "hyunjun1121@users.noreply.github.com"`

## Conventions

- All code comments and docstrings in English.
- Report files (`report_draft.md`, `report.docx`) in Korean.
- Keep text files encoded as UTF-8.
- Do not add emojis unless explicitly requested.
- Keep changes minimal; do not refactor beyond what was asked.
- Do not revert edits made by other workers.
