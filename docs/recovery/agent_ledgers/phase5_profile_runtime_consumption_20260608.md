# Phase 5 Profile Runtime Consumption Ledger - 2026-06-08

## Scope

Implemented bounded runtime consumption for Phase 5 demand and fleet profile
CSVs in `src/realworld/pilot_experiments.py`.

This ledger does not close parameter, publication, acceptance, or final-study
gates. The profile rows remain bounded scenario assumptions.

## Changes

- Restored `_output_file_manifest()` so it returns output path metadata,
  including the legacy sample manifest path when requested.
- Added `apply_pilot_demand_fleet_profiles()` runtime validation helpers for:
  - one-origin demand profile rows;
  - total demand, group size, assembly time, arrival distribution, and sigma
    levels;
  - direct bus, feeder shuttle, and last-mile finite-fleet profile rows;
  - fail-closed unsupported semantics such as non-zero no-show fractions and
    `after_rail_arrival` runtime departure markers.
- Connected the first configured demand-profile sigma level to the
  `run_scenario(..., params={"sigma": ...})` call.
- Added manifest traceability for demand/fleet profile paths and hashes.
- Updated Phase 5 demand/fleet/behavior profile manifest wording from
  "not yet consumed" to bounded runtime consumption.

## Verification

- `.\.venv\Scripts\python -m py_compile src\realworld\pilot_experiments.py`
  - passed.
- `.\.venv\Scripts\python -m py_compile src\realworld\pilot_experiments.py src\realworld\demand_fleet_behavior_profiles.py tests\test_realworld_pilot_experiments.py tests\test_realworld_demand_fleet_behavior_profiles.py`
  - passed.
- `.\.venv\Scripts\python scripts\write_demand_fleet_behavior_profiles.py`
  - passed and regenerated Phase 5 CSV/manifest/Markdown artifacts.
- `.\.venv\Scripts\python tests\test_realworld_demand_fleet_behavior_profiles.py`
  - passed.
- `.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py`
  - passed.

## Residual Blockers

- Demand profiles are not calibrated OD demand.
- Fleet profiles are not agency fleet rosters or operating timetables.
- Partial non-arrival semantics remain unimplemented in the scenario engine.
- Formal parameter acceptance remains absent.
- The human-review approval mentioned in chat has not been converted into a
  gate-specific formal acceptance artifact because the approved gate scope and
  evidence bundle were not specified.

## Follow-Up Phase-Gate Ledger Update

The Phase 5 phase-gate ledger was updated from a generated `blocked` template
to `ready_for_review` after bounded runtime profile-consumption evidence was
verified.

Updated file:

- `data/manifests/phase_gates/phase5_demand_fleet_behavior_profiles.json`

The update is intentionally not a closure:

- `status=ready_for_review`;
- `gate_decision=ready_for_review`;
- `can_mark_complete=false`;
- `final_study_ready=false`.

Additional verification:

- `.\.venv\Scripts\python -c "from src.realworld.phase_gate_ledger import load_phase_gate_ledger; ..."`
  - passed and reported `ready_for_review`, four command records, and six
    artifact hashes.
- `.\.venv\Scripts\python tests\test_realworld_demand_fleet_behavior_profiles.py`
  - passed.
- `.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py`
  - passed.
- `.\.venv\Scripts\python tests\test_realworld_phase_gate_ledger.py`
  - passed.
- `.\.venv\Scripts\python scripts\write_phase_gate_ledgers.py`
  - passed and preserved the Phase 5 `ready_for_review` ledger.
  - audit status counts became `blocked: 11`, `ready_for_review: 2`.
