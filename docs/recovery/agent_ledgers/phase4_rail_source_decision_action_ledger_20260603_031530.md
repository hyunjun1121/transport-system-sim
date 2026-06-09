# Phase 4 Rail Source-Decision Action Ledger Input

Timestamp: 2026-06-03 03:15:30 KST

## Objective

Continue Phase 4 rail/transit evidence work under `plan.md` by adding a
narrow, non-formal action-ledger input path for rail source-decision rows.

This change supports reviewer workflow only. It does not create rail timing
evidence, GTFS validation, rail service calibration, emergency rail
availability evidence, publication readiness, final-study readiness, or formal
acceptance.

## Agent Review

Read-only GPT-5.5 xhigh agent `019e897c-3c78-7e51-9a33-4d88f634b968`
inspected:

- `plan.md`
- `src/realworld/rail_source_decision_packet.py`
- `scripts/write_rail_source_decision_packet.py`
- `tests/test_realworld_rail_source_decision_packet.py`

Accepted recommendations:

- add an optional `--action-ledger` CLI path;
- merge action rows by exact `request_id`;
- allow only reviewer/action fields to be supplied by the ledger;
- reject unknown or duplicate `request_id` values;
- reject attempts to override generated source, evidence, readiness, path, gate,
  or claim-boundary fields;
- keep `publication_ready=false`, `can_mark_complete=false`, and gate-closure
  candidate counts at zero even when a complete non-formal source-decision
  ledger is recorded.

## Write Scope

Approved write scope:

- `src/realworld/rail_source_decision_packet.py`
- `scripts/write_rail_source_decision_packet.py`
- `tests/test_realworld_rail_source_decision_packet.py`
- `src/realworld/__init__.py`
- `plan.md`
- generated rail source-decision, publication-readiness, and goal-completion
  audit artifacts
- this ledger

No formal acceptance target files were created.

## Implementation

- Added `RAIL_SOURCE_DECISION_ACTION_COLUMNS` for non-formal reviewer action
  input.
- Added `apply_rail_source_decision_action_ledger()` to merge reviewer action
  fields by `request_id`.
- Added `--action-ledger` to `scripts/write_rail_source_decision_packet.py`.
- Updated manifest logic so completed non-formal action decisions are counted
  as effective source-decision status while acceptance and publication gates
  remain closed.
- Updated remaining-blocker wording so complete action-ledger outputs no
  longer say source decisions are pending, while still preserving evidence and
  acceptance blockers.
- Exported the action-ledger helper and action-column tuple from
  `src.realworld`.
- Updated `plan.md` Immediate Next Actions to document the new non-formal
  action-ledger path and its acceptance boundary.

## Verification Commands

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\rail_source_decision_packet.py scripts\write_rail_source_decision_packet.py tests\test_realworld_rail_source_decision_packet.py src\realworld\__init__.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python -c "from src.realworld import RAIL_SOURCE_DECISION_ACTION_COLUMNS, apply_rail_source_decision_action_ledger; print(len(RAIL_SOURCE_DECISION_ACTION_COLUMNS), callable(apply_rail_source_decision_action_ledger))"
```

Observed results:

- Python compile checks passed.
- Rail source-decision tests passed, including merge, protected-field
  rejection, unknown and duplicate ID rejection, CLI temp-file merge, complete
  non-formal ledger status, no-ledger shipped-output parity, and blocker wording.
- Rail bounded-treatment audit tests passed.
- Publication readiness tests passed and still report publication readiness
  blocked.
- Final-study readiness tests passed and still report final-study readiness
  blocked.
- Plan audit tests passed.
- Publication readiness audit still reports `publication_ready=false`.
- Current goal completion audit still reports `final_study_ready=false` with
  12 blocked gates.
- `src.realworld` export smoke printed `9 True`.

## Remaining Blockers

- Reviewed static GTFS feed and validator report are still absent.
- Reviewed timetable and shortest-path cache payloads are still absent.
- `DATA_GO_KR_KEY` is absent for current public API timing requests.
- Capacity and availability rows still require source-backed, sensitivity-only,
  scenario-only, or exclusion decisions.
- Non-formal source-decision rows cannot close rail evidence, publication,
  final-study, or formal acceptance gates.
