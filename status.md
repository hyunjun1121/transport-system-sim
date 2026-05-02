# Project Status

## Current Date And Workspace

- Date: 2026-05-03
- Workspace: `C:\project\transport-system-sim`
- Platform in use: Windows PowerShell
- Git branch: `main`
- Remote: `https://github.com/hyunjun1121/transport-system-sim.git`

## Project Goal

This project is a disrupted regional personnel-transport micro-simulation. The
implemented baseline compares:

- Bus-only transport
- Rail-bus multimodal transport

The baseline scenario moves about 1,000 people from an assembly context toward
a destination zone. The original use case was reserve-force transport, but the
current research direction is broader and more publishable:

> open-data, region-reusable, real-world or quasi-real simulation of emergency
> personnel movement, disrupted regional mobility, and public-sector
> contingency transport planning.

The goal is to make the simulator as close as practical to a real-world
disrupted regional transport scenario while keeping claims conservative.

## Current Implementation State

The codebase currently includes:

- Queue-based passenger dispatch
- STRICT and GRACE departure policies
- Finite fleet availability and turnaround
- Bus-only road transport
- Multimodal shuttle, rail, and last-mile transport
- Fixed-headway rail service
- Transfer delay modeling
- Rolling-window dynamic BPR road traffic
- Road disruption modes:
  - Full blockage
  - Capacity reduction
- Completion, censoring, penalized makespan, and resource-efficiency metrics
- Common-random-number paired experiments
- Phase 1 and Phase 2 experiment runners
- CSV output and PNG plot generation
- Korean narrative report generation to Word

## Current Full Experiment Outputs

The current full output set already exists under `results/`.

Verified row counts:

- Phase 1: 8,400 paired comparison rows
- Phase 2: 840 paired comparison rows

Current generated result artifacts include:

- `results/phase1_results.csv`
- `results/phase1_summary.csv`
- `results/phase1_ci.csv`
- `results/phase2_results.csv`
- `results/phase2_ci.csv`
- `results/delta_heatmap.png`
- `results/success_rate_comparison.png`
- `results/breakeven_line.png`
- `results/policy_pareto.png`

Important interpretation:

The experiments have been run, but the most recent work did not rerun the full simulations. The recent work updated documentation, report narrative, figures, and planning documents using the existing result outputs.

## Report State

The report has been simplified into a readable Korean narrative. It intentionally avoids code, command, file-path, and configuration-key details in the report body.

The Word report currently includes:

- A first-page pipeline overview figure generated externally by the user
- Existing result-based figures:
  - Time and resource efficiency comparison
  - Undelivered personnel under disruption severity
  - Executive decision lens summary

The current Word report is:

- `report.docx`

The Korean source is:

- `report_draft.md`

Report generation script:

- `generate_report.py`

Report-specific generated figures:

- `results/report_figures/figure0_pipeline_overview.png`
- `results/report_figures/figure1_time_efficiency_summary.png`
- `results/report_figures/figure2_undelivered_risk.png`
- `results/report_figures/figure3_decision_lens.png`

## Recent Commits

Recent completed commits and pushes:

- `1ba6519 Simplify report narrative`
- `c2d0a38 Add report figures`
- `7aed7a6 Add pipeline overview figure to report`
- `d742cb1 Document realistic simulation roadmap`

The pipeline overview figure was inserted into `report.docx` and pushed in commit `7aed7a6`.
The realistic simulation roadmap, public GitHub repository research, and this status document were added in commit `d742cb1`.

## Current Git Working Tree Notes

After commit `d742cb1`, a documentation and research-context update was made.
The update includes:

- `.gitignore` entry for ignored local `cloned_repo/` references
- `disrupted_mobilization_resilience_repo_research.md`
- `paper/paper_draft.md`
- `real_world_simulation_implementation_blueprint.md`
- `cloned_repo_manifest.md`
- updates to `agents.md`, `README.md`, `plan.md`, `IMPLEMENTATION_PLAN.md`,
  `repo_survey_results.md`, and this status file

If this file is being read after additional edits, run `git status --short`
before committing.

A Word temporary file was observed earlier:

- `~$report.docx`

This is a Word lock/temp file and should not be committed.

## Important Conceptual Status

The current simulation is not yet ready to be claimed as an SCI-grade real-world calibrated experiment.

Best current description:

> A meaningful baseline micro-simulation with realistic transport elements, but still based on an abstract representative network and scenario assumptions.

It includes realistic features such as fleet limits, dispatch, rail headways, disruption, traffic congestion, transfer time, and censored arrivals. However, it is not yet calibrated with actual road networks, actual traffic volumes, actual rail operation constraints, or validated wartime transport assumptions.

## Current Scientific Position

The current result should be interpreted as:

> Under the current representative network and operating assumptions, bus-only transport tends to be faster, while multimodal transport can show resource-efficiency advantages but is sensitive to road access and last-mile bottlenecks.

It should not be interpreted as:

> Bus-only transport is always faster in the real Seoul-to-forward-area setting.

## Main Limitations

Current limitations:

- The network is abstract and small.
- It is not a real OSM/Seoul calibrated network.
- Road link times and capacities are representative assumptions.
- Failure probabilities and capacity reductions are sensitivity assumptions.
- Rail is simplified and mostly treated as operationally available.
- Actual station access, platform operations, and large-scale transfer handling are not fully calibrated.
- Vehicle availability and driver constraints are not validated against real mobilization conditions.
- Current results are conditional comparative outputs, not operational forecasts.

## Realism Upgrade Direction

A new planning document was added:

- `realistic_simulation_requirements.md`

It summarizes what is needed to move toward a realistic simulation:

- Real or quasi-real road/rail network
- Reusable regional pipeline for locations beyond Songpa-gu
- Public map and open-source data pipeline
- Calibrated vehicle, road, rail, transfer, and disruption assumptions
- Sensitive-location abstraction
- Zone-level OD modeling
- Sensitivity analysis
- Reproducibility package
- SCI-level minimum criteria

Key idea:

> Public map data helps create a reusable and more realistic starting point, but public maps alone do not make the simulation real. Realism comes from adding calibrated assumptions, constraints, validation, and uncertainty analysis on top of public networks.

## Public GitHub Repository Research

A new research synthesis document was added:

- `public_github_repo_research.md`

This was produced after running multiple GPT-5.5 xhigh subagents in parallel, each responsible for one feature area.

Feature areas researched:

1. Road network extraction and reusable regional pipeline
2. Traffic assignment, calibration, and routing
3. Rail, GTFS, and multimodal routing
4. Fleet dispatch, queueing, and discrete-event modeling
5. Scenario management, sensitivity, and reproducibility
6. Geospatial anonymization, regional inputs, and OD generation

## Disrupted Resilience Repository Research

A second repository research document was added:

- `disrupted_mobilization_resilience_repo_research.md`

This document focuses specifically on the reframed research direction:

> disrupted regional mobilization transport resilience framework

It was produced with six GPT-5.5 high subagents in parallel. The subagents
searched public GitHub repositories for:

1. Transport network resilience metrics and critical-link analysis
2. Disruption scenario generation and hazard-overlay modeling
3. Emergency evacuation, mass movement, and multimodal simulation engines
4. Constrained fleet logistics and contingency routing
5. Public-data validation and calibration
6. Resilience visualization, reproducibility, and decision-support reporting

Main conclusion:

> Keep the current Python micro-simulation as the core evaluator, and add
> external repositories as data, validation, benchmark, optimization, and
> reporting layers around it.

Recommended immediate additions for this new framing:

- `NetworkX` and `OSMnx` for real road networks and critical-link metrics
- `snail` for hazard or disruption raster overlay onto transport edges
- `gtfs-validator` and `gtfs_kit` for public transit feed validation
- `Frictionless` for result and benchmark data package validation

Recommended evaluation targets:

- `r5py` for multimodal accessibility benchmarking
- `routingpy` with OSRM or Valhalla for road travel-time plausibility checks
- `OR-Tools` or `PyVRP` for optimizer-generated fleet and contingency policies
- `UXsim` for a Python-native road-congestion benchmark
- `Streamlit`, `Papermill`, and `Quarto` for decision-support and reproducible
  paper packaging

Recommended benchmark/reference-only tools:

- SUMO
- MATSim
- OpenTripPlanner
- R5
- Valhalla
- AequilibraE
- Path4GMNS
- open-gira
- transcrit
- pyincore
- CLIMADA

## Recommended Open-Source Stack

Recommended first-stage stack:

- OSMnx
- GeoPandas
- Shapely
- H3 / h3-py
- Pyrosm
- partridge or gtfs_kit
- SALib

Recommended later-stage candidates:

- Path4GMNS
- AequilibraE
- routingpy + Valhalla
- r5py
- scikit-mobility
- Ciw

Useful as design references:

- OpenMines
- FleetPy
- peartree
- street-network-models

Defer as first-pass core dependencies:

- SUMO
- MATSim
- OpenTripPlanner
- MOTIS
- DTALite
- OSM2GMNS
- eFLIPS tools

## Recommended Technical Roadmap

Stage 1: Build a reusable regional network prototype.

- Use OSMnx, GeoPandas, Shapely, and NetworkX.
- Define a region registry.
- Extract one pilot region road network.
- Store GraphML/GPKG outputs.
- Validate graph connectivity and required edge attributes.

Stage 2: Add regional reproducibility and sensitive-location abstraction.

- Use Pyrosm and pinned South Korea OSM PBF snapshots.
- Use H3 or zone aggregation.
- Store zone IDs and OD counts rather than exact sensitive coordinates.

Stage 3: Add real rail/GTFS inputs.

- Use partridge or gtfs_kit.
- Extract stations, stop times, trips, frequencies, and headways.
- Optionally prototype peartree for GTFS-to-NetworkX conversion.
- Use r5py only as an external benchmark path.

Stage 4: Add assignment and calibration.

- Add a NetworkX-to-GMNS adapter.
- Use Path4GMNS for assignment/ODME experiments.
- Keep AequilibraE as a mature alternative for larger traffic assignment needs.

Stage 5: Add formal sensitivity analysis.

- Use SALib.
- Analyze completion time, completion rate, censored personnel, and resource efficiency.

Stage 6: Improve fleet and queue semantics.

- Use Ciw, OpenMines, and FleetPy as references.
- Add passenger state logs, per-vehicle task logs, queue wait accounting, boarding/alighting service times, and driver/fleet shortage scenarios.

## SCI-Level Research Development Requirements

To develop this into an SCI-grade paper, the project needs:

- A sharply defined research question
- Real or quasi-real regional road and rail network
- Defensible input-parameter table
- Public-data, literature, or expert-judgment basis for key assumptions
- Multiple network and disruption scenarios
- Formal sensitivity analysis
- Confidence intervals or comparable uncertainty summaries
- Tail-risk and censored-arrival interpretation
- Reproducibility package
- Clear separation between operational claims and conditional simulation findings

Potential research question framing:

- Under what network disruption and resource constraints does rail-bus multimodal transport outperform bus-only transport?
- Which bottlenecks most reduce multimodal transport resilience?
- How do last-mile redundancy, transfer delay, and fleet shortage affect completion probability?
- Can a region-reusable open-map pipeline support robust reserve-force transport planning under uncertainty?

## High-IF SCI Framing Assessment

The idea can become a research paper, but the current version should not be framed as ready for a high-impact SCI journal. The current strongest assessment is:

> The project has a promising research seed and a non-trivial simulator, but the claim structure is still weaker than the evidence standard expected by high-impact transportation, logistics, reliability, or system-safety journals.

The main weakness is not the number of simulation runs. The main weakness is real-world alignment:

- The current network is representative and abstract.
- Major parameters are not yet supported by a source table.
- Rail availability, station access, transfer capacity, and last-mile reliability are not calibrated.
- Validation is not yet strong enough for operational or policy claims.
- The contribution is currently mixed between simulator, case result, and methodology.

The best high-impact framing is not:

> A wartime reserve-force transport simulator proves which mode is better.

The better framing is:

> An open-data, region-reusable decision framework that combines geospatial networks and discrete-event micro-simulation to identify when rail-bus multimodal mobilization transport becomes resilient or fragile under network degradation and constrained fleet operations.

This framing reduces military specificity, improves generalizability, and aligns the work with resilience, disrupted logistics, emergency mobilization, and multimodal network reliability.

## Strongest Paper Claim Direction

The most promising research question is:

> Under which disruption and resource constraints does rail-bus multimodal transport outperform bus-only mobilization transport?

A strong paper should produce conditional decision rules, such as:

- Multimodal transport becomes competitive only when rail access and last-mile redundancy remain available.
- Bus-only transport can dominate travel time under direct-road access but becomes vulnerable under fleet shortage or major corridor disruption.
- Transfer delay and last-mile bottlenecks can erase the theoretical capacity benefit of rail.
- Completion probability, censored personnel, and tail-risk are more decision-relevant than raw mean makespan.

The final claim should be about regimes, thresholds, and bottlenecks, not absolute superiority.

## Three-Month Research Upgrade Plan

Month 1: Realistic network prototype.

- Build an OSMnx-based road network prototype for one non-sensitive pilot region.
- Represent sensitive destinations as zones or synthetic nodes.
- Add a minimum rail/GTFS input path using partridge or gtfs_kit.
- Define the region input schema and network persistence format.

Month 2: Calibration and parameter evidence.

- Run the existing simulator on the new quasi-real network.
- Create a parameter-source table.
- Classify each value as public-data, literature, expert-assumption, or sensitivity-only.
- Add sanity checks for road travel time, rail headway, bus turnaround, transfer time, and queue behavior.

Month 3: Scientific analysis package.

- Add SALib-based global sensitivity analysis.
- Expand policy scenarios: last-mile redundancy, rail delay, feeder capacity expansion, fleet shortage, adaptive routing, and staggered dispatch.
- Report completion probability, censored personnel, 95th-percentile arrival, bottleneck attribution, and resource efficiency.
- Prepare a reproducibility package with input snapshots, seeds, scenario tables, and result-generation steps.

## Immediate Next Steps

Suggested next work:

1. Build a first OSMnx/Pyrosm prototype for one non-sensitive pilot region.
2. Define a reusable region input schema and zone-based OD schema.
3. Define how exact sensitive points will be replaced by administrative zones,
   H3/admin-grid cells, or synthetic centroids.
4. Map OSM edge attributes into simulation fields: length, road class,
   free-flow speed, travel time, capacity proxy, and disruption exposure.
5. Add rail input handling through GTFS where available or a documented
   rail-assumption table where GTFS is incomplete.
6. Create a parameter-source table separating:
   - public-data values
   - literature values
   - agency/timetable values
   - benchmark-calibrated values
   - expert assumptions
   - sensitivity-only assumptions
7. Add spatially structured disruption scenarios:
   - random degradation baseline
   - critical-link disruption
   - hazard/exposure overlay disruption
8. Add validation and plausibility checks for road travel time, rail, fleet,
   transfer, station access, and last-mile assumptions.
9. Add a SALib sensitivity-analysis design.
10. Expand policy alternatives beyond bus-only vs baseline rail-bus multimodal.

## Files Added In Recent Roadmap Work

- `realistic_simulation_requirements.md`
- `public_github_repo_research.md`
- `disrupted_mobilization_resilience_repo_research.md`
- `paper/paper_draft.md`
- `real_world_simulation_implementation_blueprint.md`
- `cloned_repo_manifest.md`
- `status.md`

## Paper Draft State

A paper draft scaffold was added under:

- `paper/paper_draft.md`

The draft is written in English and frames the project as:

> A region-reusable decision framework for disrupted mobilization transport
> resilience under network degradation and constrained fleet operations.

The draft includes:

- working title options
- abstract draft
- research questions
- contribution claims
- related-work plan
- framework architecture
- data and regional reuse design
- simulation model description
- disruption and resilience metrics
- experimental design
- validation and sensitivity plan
- preliminary baseline interpretation guardrails
- figure and table plan
- manuscript claim guardrails
- immediate author TODOs

## Public Repository Clone State

A local reference clone directory was created:

- `cloned_repo/`

It is ignored by git and should be treated as a local reference cache, not as
vendored source code.

The following repositories were shallow-cloned successfully:

- `networkx`
- `osmnx`
- `geopandas`
- `shapely`
- `pyrosm`
- `h3-py`
- `snail`
- `open-gira`
- `gtfs_kit`
- `gtfs-validator`
- `SALib`
- `frictionless-py`
- `GOSTnets`
- `pysal-access`
- `r5py`
- `routingpy`
- `or-tools`
- `PyVRP`
- `UXsim`
- `transcrit`
- `Path4GMNS`
- `aequilibrae`
- `osrm-backend`
- `valhalla`

The clone manifest is tracked separately in:

- `cloned_repo_manifest.md`

Heavy full-platform tools such as SUMO, MATSim, and OpenTripPlanner were not
cloned in this pass because the immediate implementation target is the
open-data real-world pipeline around the current simulator rather than a full
platform migration.

## Caution For Future Work

Do not overstate current experimental results as real-world operational predictions.

Use this language:

> The current results are conditional findings under a representative network and assumptions.

Avoid this language:

> The current model proves that one transport mode is operationally superior in the real world.

Before any publication-style claim, improve network realism, calibrate parameters, and run sensitivity analysis.
