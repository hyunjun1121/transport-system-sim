# Phase 5 Demand, Fleet, And Behavior Profiles Ledger

Date: 2026-06-03

Scope:

- Implement Phase 5 profile review artifacts for demand, finite fleet, and
  behavior assumptions.
- Keep outputs as bounded scenario-review contracts only.
- Do not change pilot experiment runtime semantics.
- Do not create parameter acceptance, publication readiness, final-study
  readiness, operational planning evidence, or formal acceptance evidence.

Main-thread preflight evidence:

- `git status --short --branch` inspected before implementation.
- `.\.venv\Scripts\python --version`: Python 3.12.10.
- `.\.venv\Scripts\python -m pip check`: no broken requirements found.
- CPU/RAM/GPU command output recorded in the working session:
  AMD Ryzen 7 5800X3D, 8 cores / 16 logical processors; RAM about 31.9 GiB;
  NVIDIA GeForce RTX 3090, 24576 MiB, driver 610.47.
- GPU was not used for this Phase 5 work.

Sub-agent wave:

- `019e8cfa-4795-7720-8f8b-dafc863388e0` / Kuhn the 2nd:
  GPT-5.5 xhigh read-only implementation/test explorer.
  Finding accepted: Phase 5 module existed but lacked CLI writer, shipped
  outputs, plan-audit registration, dedicated tests, and had a blank pilot
  sigma risk.
- `019e8cfa-915c-7000-bd93-1b64bb20b59e` / Hooke the 2nd:
  GPT-5.5 xhigh read-only claim/provenance explorer.
  Finding accepted: Phase 5 rows cannot support parameter evidence, formal
  acceptance, publication readiness, or final-study readiness.
- `019e8cfa-f25d-7d42-bba4-34dcccb00e61` / Galileo the 2nd:
  GPT-5.5 xhigh read-only validation/audit explorer.
  Finding accepted: register `demand_profiles.csv`, `fleet_profiles.csv`,
  `behavior_profiles.csv`, the Phase 5 manifest, and the Markdown doc in
  `scripts/audit_plan_artifacts.py` and `tests/test_realworld_plan_audit.py`.

Implementation changes:

- Added `scripts/write_demand_fleet_behavior_profiles.py`.
- Added `tests/test_realworld_demand_fleet_behavior_profiles.py`.
- Strengthened `src/realworld/demand_fleet_behavior_profiles.py` by:
  - adding local cited-source inputs to the manifest hash list;
  - filling pilot demand sigma from `lateness.sigma_levels` when no scalar
    `lateness.sigma` exists;
  - validating fleet rows and behavior rows;
  - recording that profile CSVs are not yet consumed as runtime inputs by
    `pilot_experiments.py`.
- Registered Phase 5 CSV/JSON/doc artifacts in
  `scripts/audit_plan_artifacts.py`.
- Added plan-audit assertions for the Phase 5 artifacts in
  `tests/test_realworld_plan_audit.py`.
- Updated `plan.md`, `README.md`, `src/realworld/README.md`, `agents.md`, and
  `status.md` to list the Phase 5 writer and conservative claim boundary.
- Updated `tests/test_realworld_parameter_source_decision_packet.py` to match
  the current generated parameter source-decision manifest, where all seven
  parameter source-decision rows remain `needs_human_review`.

Generated Phase 5 artifacts:

- `data/scenarios/demand_profiles.csv`: 2 rows.
- `data/scenarios/fleet_profiles.csv`: 6 rows.
- `data/scenarios/behavior_profiles.csv`: 6 rows.
- `data/scenarios/demand_fleet_behavior_profile_manifest.json`.
- `docs/demand_fleet_behavior_profiles.md`.

Validation commands run:

- `.\.venv\Scripts\python -m py_compile .\src\realworld\demand_fleet_behavior_profiles.py .\scripts\write_demand_fleet_behavior_profiles.py .\scripts\audit_plan_artifacts.py .\tests\test_realworld_demand_fleet_behavior_profiles.py .\tests\test_realworld_plan_audit.py`
- `.\.venv\Scripts\python tests\test_dispatch.py`
- `.\.venv\Scripts\python tests\test_fleet.py`
- `.\.venv\Scripts\python tests\test_metrics.py`
- `.\.venv\Scripts\python tests\test_scenario.py`
- `.\.venv\Scripts\python scripts\write_demand_fleet_behavior_profiles.py`
- `.\.venv\Scripts\python tests\test_realworld_demand_fleet_behavior_profiles.py`
- `.\.venv\Scripts\python scripts\audit_plan_artifacts.py`
- `.\.venv\Scripts\python tests\test_realworld_plan_audit.py`
- `.\.venv\Scripts\python scripts\audit_parameter_evidence.py`
- `.\.venv\Scripts\python scripts\audit_publication_readiness.py`
- `.\.venv\Scripts\python scripts\audit_final_study_readiness.py`
- `.\.venv\Scripts\python tests\test_realworld_parameter_source_decision_packet.py`
- `git diff --check`

Observed validation results:

- Phase 5 dedicated tests passed.
- Dispatch, fleet, metrics, and scenario baseline tests passed.
- Plan artifact audit passed with `all_required_artifacts_present=true`.
- Parameter source-decision test passed after updating expectations to the
  current human-review-only generated packet.
- Parameter evidence audit remained blocked for final claims:
  `publication_ready=false`, 25 weak core parameters.
- Publication readiness audit remained blocked:
  `publication_ready=false`, 1 ready gate and 9 blocked gates.
- Final-study readiness audit remained blocked:
  `final_study_ready=false`, 12 blocked gate IDs.
- `git diff --check` returned no whitespace errors; it reported CRLF
  conversion warnings only.

Residual blockers:

- Demand profiles are not calibrated OD demand.
- Fleet profiles are not agency fleet rosters or operating timetables.
- Partial non-arrival and no-show denominator semantics are not implemented in
  the scenario engine.
- Profile CSVs currently document assumptions but are not runtime inputs for
  `pilot_experiments.py`.
- Formal parameter acceptance remains absent.
- This phase does not close publication, final-study, validation, experiment,
  or formal acceptance gates.

Gate decision:

- Phase 5 profile-packet artifact generation and registration may proceed as a
  bounded review-support step.
- Final real-world study status remains blocked pending upstream source,
  calibration, validation, graph-scale, experiment, reporting, reproducibility,
  and formal acceptance gates.
