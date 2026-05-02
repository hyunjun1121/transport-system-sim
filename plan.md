# Remaining Work Plan

This document is the planning guide for the next work on the transport
simulation. It should describe only work that still needs action. Completed
local implementation and documentation cleanup should stay in the status section
so future passes do not reopen closed items by accident.

## Current State

The project is a Windows PowerShell Python workflow. Run project commands from
the repository root through `.\.venv\Scripts\python`.

Implemented local model and documentation items:

- Queue-based STRICT and GRACE passenger dispatch.
- Finite fleet availability and turnaround for bus-only service, multimodal
  shuttle service, and multimodal last-mile service.
- Rolling-window dynamic BPR road traffic.
- Road disruption modes for `blocked` and `capacity_reduction` states.
- Fixed and per-passenger multimodal transfer delay.
- Completion, censoring, penalized makespan, and unit-consistent resource KPIs.
- Fixed-headway rail service with `multimodal.rail_first_departure_min`
  integration completed in the current pass.
- Planning and historical documentation cleanup completed in the current pass.

Current generated full-output context:

- Phase 1 output: 8,400 paired rows.
- Phase 2 output: 840 paired rows.
- Default Phase 1 sweep: `baseline` and `matched_redundancy` only.

The declared network variants also include
`multimodal_redundant_lastmile` and `bus_single_corridor`, but those are
selectable sensitivity cases, not part of the current default Phase 1 sweep.

Recent planning and research assets now exist:

- `paper/paper_draft.md`: English manuscript scaffold.
- `disrupted_mobilization_resilience_repo_research.md`: public repo research
  for the disrupted regional resilience framing.
- `real_world_simulation_implementation_blueprint.md`: implementation blueprint
  focused on extracting the best practical ideas from public repos.
- `cloned_repo_manifest.md`: manifest of public repository source snapshots
  under `cloned_repo/`.

The active target is no longer just documenting the abstract simulator. The next
implementation objective is:

> make the simulation as close as practical to a real-world or quasi-real
> regional disrupted transport scenario while keeping claims conservative.

## Standing Rules

- Keep code comments and docstrings in English.
- Keep report narrative files in Korean.
- Do not add Termux, Android, or `pkg` setup instructions as active guidance.
- Do not describe implemented local behavior as future work.
- Treat `results/` and `report.docx` as generated artifacts. Refresh them only
  when explicitly requested or when a model/result-semantics change requires it.
- Preserve the public scenario API unless a deliberate API change is accepted:
  `run_scenario(G, config, scenario_type, policy, params, seed) -> dict`.

## Priority 1: Calibration And External Data

These items require external data, subject-matter assumptions, or an explicit
scenario-design decision. They are not complete and should not be marked done
until the input source or assumption set is recorded.

- Build an OSMnx/Pyrosm regional road-network extractor.
- Define a region registry and zone-based OD schema.
- Replace exact sensitive points with administrative zones, synthetic centroids,
  or H3/admin-grid cells.
- Map OSM road attributes to simulation attributes: length, road class,
  free-flow speed, capacity proxy, and travel time.
- Add candidate rail access and egress nodes.
- Create a GTFS-derived or documented rail-assumption table.
- Calibrate or source road capacities, background volumes, and BPR parameters.
- Add spatially structured disruption scenarios:
  - random degradation baseline,
  - critical-link disruption,
  - hazard/exposure overlay disruption.
- Calibrate or source bus, shuttle, and last-mile fleet sizes against plausible
  vehicle availability.
- Calibrate or source transfer times for platform movement, loading, staging,
  and coordination procedures.
- Decide whether rail remains failure-immune or receives rail delay, capacity
  reduction, access disruption, or partial unavailability scenarios.

Acceptance criteria:

- Every completed calibration item cites a data source or records a deliberate
  assumption.
- Regional input artifacts record data snapshot metadata.
- Sensitive destination handling is documented before any map or OD output is
  published.
- If calibration remains incomplete, report conclusions remain conditional and
  do not read as operational forecasts.

## Priority 2: Validation And Benchmarking

Before claiming a real-world or quasi-real result, add validation layers:

- Internal validation:
  - identical seeds reproduce identical outputs,
  - more fleet capacity should not worsen completion unless congestion feedback
    explains it,
  - greater disruption severity should generally worsen resilience outcomes,
  - longer transfer delay should not improve multimodal travel time,
  - blocked critical links should be more damaging than minor capacity
    reductions,
  - no-disruption scenarios should outperform disrupted scenarios.
- External plausibility validation:
  - compare OSM-derived road distance and free-flow time to public map or
    routing-engine estimates,
  - compare GTFS-derived headways and rail travel times to public schedules,
  - verify access and last-mile distances are plausible,
  - check road speed and capacity assumptions by road class.
- Benchmark validation:
  - use at least one of OSRM, Valhalla, routingpy, r5py/R5, UXsim, or a
    limited SUMO corridor experiment.

Acceptance criteria:

- Validation outputs are stored or summarized before manuscript claims are
  strengthened.
- Benchmark outputs are described as plausibility checks, not ground truth.

## Priority 3: Sensitivity And Policy Expansion

Add formal sensitivity and policy-regime analysis:

- Use SALib for Morris screening or Sobol first-order and total-order indices.
- Analyze completion rate, censored personnel, penalized makespan, tail arrival
  times, vehicle-minutes, passenger-minutes, and passengers per service minute.
- Vary passenger volume, arrival variability, fleet sizes, dispatch interval,
  background traffic, disruption severity, capacity reduction, rail headway,
  rail capacity, transfer delay, turnaround time, and access disruption.
- Expand policy alternatives beyond baseline bus-only and baseline multimodal:
  - multimodal with redundant last-mile fleet,
  - multimodal with increased feeder capacity,
  - staggered dispatch,
  - adaptive rerouting,
  - bus-only with alternate corridors,
  - fleet shortage,
  - rail delay or partial unavailability.

Acceptance criteria:

- Results report which uncertain parameters determine the winning regime rather
  than only reporting which mode wins.
- Policy alternatives are evaluated through speed, reliability, resource, and
  bottleneck lenses.

## Priority 4: Result Interpretation Guardrails

The current model is useful for controlled comparison, not calibrated
forecasting. Keep future writeups explicit about the assumptions behind any
performance claim.

- Keep conclusions tied to `delta_penalized_makespan`, completion rate, and
  censoring when failures can prevent delivery.
- Avoid relying on raw makespan alone when `censored_count > 0`.
- Keep `failure_rate.levels` described as `p_fail_scale` multipliers, not
  absolute disruption probabilities.
- When outputs are regenerated, record Phase 1/2 row counts, swept axes, active
  network variants, failure mode, and plot context.

Acceptance criteria:

- Documentation does not overstate operational validity.
- Readers can tell which variants were swept and which were only declared as
  selectable sensitivity cases.

## Priority 5: Variant Coverage Decision

The default Phase 1 sweep currently covers only `baseline` and
`matched_redundancy`. Keep that default unless a full four-variant regeneration
is deliberately requested.

Remaining decision:

- Decide whether future published results should keep the two-variant default
  or expand to include `multimodal_redundant_lastmile` and
  `bus_single_corridor`.

Acceptance criteria if expanded:

- Run a full result regeneration.
- Update result row counts and all narrative references to the swept variants.
- Regenerate plots and report artifacts only as part of the accepted output
  refresh.

## Verification For Future Model Changes

Use these commands before accepting future code or config changes:

```powershell
.\.venv\Scripts\python -m compileall main.py src tests generate_report.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
.\.venv\Scripts\python main.py --test
.\.venv\Scripts\python main.py --quick
```

Use these only after an accepted result-changing model update or an explicit
output-refresh request:

```powershell
.\.venv\Scripts\python main.py --phase 1
.\.venv\Scripts\python main.py --phase 2
.\.venv\Scripts\python generate_report.py
```
