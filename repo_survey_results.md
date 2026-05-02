# Transport System Simulation - Reference Survey

## Status

This file is a historical research reference, not the active implementation
plan or setup guide. Current setup, commands, architecture, and limitations are
documented in `README.md`, `agents.md`, `IMPLEMENTATION_PLAN.md`, and
`plan.md`.

Newer research and implementation-planning context is documented in:

- `public_github_repo_research.md`
- `disrupted_mobilization_resilience_repo_research.md`
- `real_world_simulation_implementation_blueprint.md`
- `cloned_repo_manifest.md`
- `paper/paper_draft.md`

Current implementation status:

- Windows PowerShell and `.\.venv\Scripts\python` are the active local workflow.
- Queue-based STRICT and GRACE dispatch are implemented.
- Bus-only, multimodal shuttle, and multimodal last-mile services use finite
  fleet controls where applicable.
- Rail uses fixed-headway scheduling and supports
  `multimodal.rail_first_departure_min`.
- Road movement uses rolling-window dynamic BPR traffic.
- Road disruption states support `blocked` and `capacity_reduction` modes.
- Transfers, censoring-aware KPIs, and unit-consistent resource KPIs are
  implemented.
- Current full outputs contain 8,400 paired Phase 1 rows and 840 paired Phase 2
  rows.
- The default Phase 1 sweep covers `baseline` and `matched_redundancy`; the
  `multimodal_redundant_lastmile` and `bus_single_corridor` variants are
  selectable sensitivity cases outside the current default result set.

External-data and calibration work remains open. This survey does not imply
that OSM/GTFS calibration, real Seoul network replacement, empirical traffic
calibration, or empirical disruption-probability calibration has been completed.

As of the latest context update, public reference repositories have been cloned
locally under ignored `cloned_repo/` for study only. They are not vendored
dependencies and are not yet integrated into the production simulator.

## Survey Takeaways

The original repository survey was used to choose a conservative local design:
a small Python simulation stack built around NetworkX-style graph modeling,
discrete-event dispatch logic, BPR travel time, common-random-number paired
experiments, and CSV/plot/report generation.

The reviewed reference categories were:

- SimPy and discrete-event simulation examples for transport and logistics.
- NetworkX and graph-based traffic/resilience examples.
- BPR and traffic-assignment references.
- Multimodal transport simulation frameworks such as MATSim and SUMO.
- Evacuation and military-transport decision simulation references.
- Design-of-experiments, Monte Carlo, and sensitivity-analysis tools.
- Seoul or OSM-oriented network data tools for future calibration.

## References Worth Revisiting

These references remain useful if the project moves beyond the current abstract
network:

| Area | Reference | Use |
| --- | --- | --- |
| Road network data | OSMnx | Candidate tool for replacing the abstract graph with OSM-derived roads. |
| Microscopic traffic | SUMO | Candidate for richer traffic assignment, signals, and spillback modeling. |
| Agent-based transport | MATSim | Candidate reference for large-scale multimodal transport experiments. |
| Python ABM | Mesa | Candidate if individual behavior or command-agent logic is added. |
| BPR / assignment | AequilibraE | Candidate source for calibrated traffic assignment workflows. |
| Sensitivity analysis | SALib | Candidate tool for Sobol/Morris sensitivity analysis. |
| Experiment design | pyDOE3 | Candidate tool if factorial grids become too large or need LHS designs. |
| Fleet simulation | FleetPy | Candidate reference for richer vehicle fleet availability and dispatch. |

## Current Decision

The project deliberately remains a controlled micro-simulation rather than a
full operational transport model. The present codebase should continue to use
the local modular implementation unless a future task explicitly adopts a
larger external framework or calibrated data source.
