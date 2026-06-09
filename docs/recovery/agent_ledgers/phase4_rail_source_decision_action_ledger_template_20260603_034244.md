# Phase 4 Rail Source-Decision Action Ledger Template

Timestamp: 2026-06-03 03:42:44 KST

## Objective

Continue Phase 4 rail/transit evidence work under `plan.md` by adding a
separate reviewer worksheet generator for rail source-decision action ledgers.

This change supports reviewer workflow only. It does not create rail timing
evidence, GTFS validation, rail service calibration, emergency rail
availability evidence, publication readiness, final-study readiness, or formal
acceptance.

## Agent Review

Three read-only GPT-5.5 xhigh agents reviewed the next-step choice before
implementation:

- `019e8993-c68e-7543-873b-0f5ae75f773d` reviewed rail timing and GTFS evidence
  context. Recommendation: the direct evidence path remains reviewed GTFS,
  timetable, or shortest-path intake; a worksheet template is acceptable only as
  workflow support while those evidence inputs remain absent.
- `019e8994-221c-7901-ad08-4ff307259736` reviewed source-decision and capacity
  workflow. Recommendation: generate a template that exposes only action-ledger
  columns, keeps all decisions pending by default, and cannot be interpreted as
  evidence or acceptance.
- `019e8994-8061-79b3-87ff-e49a0abdb12c` reviewed artifact-hygiene risk.
  Recommendation: write the template to paths separate from the source-decision
  packet, exclude protected generated fields, add round-trip tests through the
  existing action-ledger merge path, and keep all gate flags false.

Accepted scope: implement the non-formal template generator and tests.
Rejected scope: do not fabricate GTFS, timetable, shortest-path, capacity, or
availability evidence; do not create formal acceptance targets.

## Write Scope

Approved write scope:

- `src/realworld/rail_source_decision_packet.py`
- `src/realworld/__init__.py`
- `scripts/write_rail_source_decision_action_ledger_template.py`
- `tests/test_realworld_rail_source_decision_action_ledger_template.py`
- `agents.md`
- `status.md`
- `plan.md`
- generated template, rail source-decision, publication-readiness, and
  goal-completion audit artifacts
- this ledger

No formal acceptance target files were created.

## Implementation

- Added default output paths for
  `data/rail/rail_source_decision_action_ledger_template.csv`,
  `data/rail/rail_source_decision_action_ledger_template_manifest.json`, and
  `docs/rail_source_decision_action_ledger_template.md`.
- Added `build_rail_source_decision_action_ledger_template_rows()` so templates
  contain exactly `RAIL_SOURCE_DECISION_ACTION_COLUMNS`.
- Prefilled only `request_id` and `decision_choice=pending_reviewer_decision`;
  all reviewer, evidence, rationale, and claim-boundary cells stay blank.
- Added manifest and Markdown generation that explicitly mark the artifact as a
  non-acceptance, non-evidence, non-publication, non-final-study worksheet.
- Added `scripts/write_rail_source_decision_action_ledger_template.py`.
- Exported the template helper and default paths from `src.realworld`.
- Added tests for safe columns, protected-field exclusion, writer outputs,
  blank-template round-trip behavior, and CLI custom-output behavior.
- Updated `agents.md`, `status.md`, and `plan.md` to document the command and
  its non-formal boundary.

## Verification Commands

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\rail_source_decision_packet.py src\realworld\__init__.py scripts\write_rail_source_decision_action_ledger_template.py scripts\write_rail_source_decision_packet.py tests\test_realworld_rail_source_decision_action_ledger_template.py tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_action_ledger_template.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python scripts\write_rail_source_decision_action_ledger_template.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
```

Observed results:

- Python compile checks passed.
- Rail source-decision action-ledger template tests passed.
- Rail source-decision action-ledger tests passed.
- Plan audit tests passed.
- Default template generation wrote the template CSV, manifest, and Markdown
  with `template_only=true`, `ledger_compatible=true`, `publication_ready=false`,
  `can_mark_complete=false`, and 5 pending template rows.
- Default source-decision packet generation still reports 5 pending action
  decisions, 3 blocking decisions, 2 human-review decisions, and
  `rail_source_decision_recorded=false`.
- Publication readiness tests passed and still require completed rail
  source-decision rows.
- Final-study readiness tests passed and still block the rail gate on incomplete
  source decisions and missing evidence.
- Publication readiness audit still reports `publication_ready=false` with 7
  blocked gates.
- Current goal completion audit still reports `final_study_ready=False` with 12
  blocked gates.

## Remaining Blockers

- Reviewed static GTFS feed and validator report are still absent.
- Reviewed timetable and shortest-path cache payloads are still absent.
- `DATA_GO_KR_KEY` is absent for current public API timing requests.
- Capacity and availability rows still require source-backed, sensitivity-only,
  scenario-only, or exclusion decisions.
- The action-ledger template cannot close rail evidence, publication,
  final-study, or formal acceptance gates.
