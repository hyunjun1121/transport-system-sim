# Project Status

## Current Date And Workspace

- Date: 2026-05-01
- Workspace: `C:\project\transport-system-sim`
- Platform in use: Windows PowerShell
- Git branch: `main`
- Remote: `https://github.com/hyunjun1121/transport-system-sim.git`

## Project Goal

This project is a wartime reserve-force transport micro-simulation. It compares:

- Bus-only transport
- Rail-bus multimodal transport

The baseline scenario moves about 1,000 reservists from a Seoul Songpa-gu assembly context toward a forward-area destination. The long-term goal is to evolve this from an abstract comparative simulator into a more realistic, reusable, region-extensible simulation framework that could support a high-quality research paper.

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

The pipeline overview figure was inserted into `report.docx` and pushed in commit `7aed7a6`.

## Current Git Working Tree Notes

At the time this status file is being written, there are uncommitted changes:

- `report.docx` is modified
- `realistic_simulation_requirements.md` is newly added
- `public_github_repo_research.md` is newly added
- `status.md` is newly added

The `report.docx` modification may be due to local Word/temp or regeneration state. Check before committing.

There was also a Word temporary file observed earlier:

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

## Immediate Next Steps

Suggested next work:

1. Decide whether to commit the newly added planning documents.
2. Clean or ignore Word temp files if present.
3. Decide whether `report.docx` should be committed again or left unchanged.
4. Build a first OSMnx prototype for one non-sensitive pilot region.
5. Define a region input schema.
6. Define how exact sensitive points will be replaced by zones.
7. Create a parameter-source table separating:
   - public-data values
   - literature values
   - expert assumptions
   - sensitivity-only assumptions
8. Add a SALib experiment design plan.

## Files Added In Current Uncommitted Work

- `realistic_simulation_requirements.md`
- `public_github_repo_research.md`
- `status.md`

## Caution For Future Work

Do not overstate current experimental results as real-world operational predictions.

Use this language:

> The current results are conditional findings under a representative network and assumptions.

Avoid this language:

> The current model proves that one transport mode is operationally superior in the real world.

Before any publication-style claim, improve network realism, calibrate parameters, and run sensitivity analysis.
