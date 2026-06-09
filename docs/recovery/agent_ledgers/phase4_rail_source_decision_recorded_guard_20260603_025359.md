# Phase 4 Rail Source-Decision Recorded Guard

Timestamp: 2026-06-03 02:53:59 KST

## Objective

Continue Phase 4 rail/transit evidence work under `plan.md` by tightening the
rail source-decision guard. The change prevents a permanent false-negative
state where every non-formal rail source-decision row could be complete while
the aggregate still reported `rail_source_decision_recorded=false`.

This is review-support logic only. It does not create rail timing evidence,
GTFS validation, rail service calibration, emergency rail availability evidence,
publication readiness, final-study readiness, or formal acceptance.

## Baseline Evidence Inspected

- `plan.md` Immediate Next Actions for Phase 4 require every rail
  source-decision row to be classified before implementation proceeds.
- `data/rail/rail_source_decision_manifest.json` currently has:
  - `row_count=5`
  - `completed_source_decision_count=0`
  - `blocking_decision_count=3`
  - `human_review_decision_count=2`
  - `rail_source_decision_recorded=false`
- `src/realworld/rail_source_decision_packet.py` already computed
  `completed_source_decision_count`, but previously hard-coded
  `rail_source_decision_recorded=false`.
- `src/realworld/publication_readiness.py` and
  `src/realworld/final_study_readiness.py` both require the aggregate to be
  recorded, complete, and free of blocking/human-review rows before the rail
  source-decision subgate can be ready.

## Agent Review

Read-only GPT-5.5 xhigh agent `019e8972-6e8e-7623-997b-e7a39866c7b6`
reviewed the rail source-decision logic and recommended not keeping
`rail_source_decision_recorded` hard-coded false. The accepted recommendation
was to compute it from complete non-formal source-decision rows while keeping
all approval and closure fields false or zero.

Accepted finding:

- A complete non-formal source-decision ledger should be recorded as a reviewed
  source-decision aggregate.

Rejected or bounded finding:

- Recording the aggregate is not evidence acceptance. The manifest still keeps
  `publication_ready=false`, `can_mark_complete=false`,
  `rail_service_evidence_gate_closure_candidate_count=0`, and
  `acceptance_gate_closure_candidate_count=0`.

## Write Scope

Approved write scope:

- `src/realworld/rail_source_decision_packet.py`
- `tests/test_realworld_rail_source_decision_packet.py`
- generated rail source-decision packet artifacts
- generated publication/final-study readiness audit artifacts
- this ledger

No formal acceptance target files were created.

## Implementation

- Updated `build_rail_source_decision_manifest()` so
  `rail_source_decision_recorded` is true only when `rows` is non-empty and
  `completed_source_decision_count == row_count`.
- Added a regression test proving that all five complete non-formal decisions
  set `rail_source_decision_recorded=true` while publication, completion, rail
  evidence closure, and acceptance closure remain false or zero.
- Preserved the current shipped-output expectation that the active packet is
  still pending and therefore `rail_source_decision_recorded=false`.
- Regenerated the rail source-decision packet, publication readiness audit, and
  current goal completion audit.

## Verification Commands

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\rail_source_decision_packet.py tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
```

Observed results:

- Rail source-decision tests passed.
- Publication readiness tests passed.
- Final-study readiness tests passed.
- Plan audit tests passed.
- Publication readiness remains `publication_ready=false` with
  `rail_source_decision_ready=false`.
- Current goal completion audit remains `final_study_ready=false` with
  `blocked_gates=12`.

## Remaining Blockers

- No reviewed static GTFS feed and validator report are present.
- No reviewed timetable or shortest-path cache payloads are present.
- `DATA_GO_KR_KEY` is absent for the current public API timing requests.
- Capacity and availability rows still need source-backed, sensitivity-only,
  scenario-only, or exclusion decisions.
- The current packet remains review support only and cannot close rail,
  parameter, provenance, publication, final-study, or formal acceptance gates.
