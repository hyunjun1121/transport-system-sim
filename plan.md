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

- Replace the abstract graph with an OSM/calibrated Seoul road and rail network,
  or explicitly retain the current graph as a controlled toy network.
- Calibrate road capacities, background volumes, and BPR parameters.
- Calibrate link disruption probabilities and realistic capacity-reduction
  factors.
- Calibrate bus, shuttle, and last-mile fleet sizes against realistic vehicle
  availability.
- Calibrate transfer times for platform movement, loading, staging, and command
  procedures.
- Decide whether rail should remain failure-immune or receive a rail disruption
  model.

Acceptance criteria:

- Every completed calibration item cites a data source or records a deliberate
  assumption.
- If calibration remains incomplete, report conclusions remain conditional and
  do not read as operational forecasts.

## Priority 2: Result Interpretation Guardrails

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

## Priority 3: Variant Coverage Decision

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
