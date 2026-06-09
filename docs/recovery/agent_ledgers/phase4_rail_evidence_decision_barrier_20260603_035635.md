# Phase 4 Rail Evidence-Decision Barrier

Timestamp: 2026-06-03 03:56:35 KST

## Objective

Continue `plan.md` Phase 4 by stopping before any rail builder work and
recording the current evidence-decision barrier for rail/transit inputs.

This ledger is a synthesis and guardrail record only. It does not create rail
timing evidence, GTFS validation, rail service calibration, rail capacity
acceptance, emergency rail availability evidence, publication readiness,
final-study readiness, or formal acceptance.

## Read-Only Agent Wave

Three GPT-5.5 xhigh read-only agents reviewed the current Phase 4 rail state:

- `019e89ab-24ad-74a2-896f-339eb4971740`: rail timing, GTFS, timetable, and
  shortest-path evidence availability.
- `019e89ab-7dbb-7272-9ac2-db391dca20d3`: rail capacity and availability
  treatment status.
- `019e89ab-f353-76e0-903e-c895e7f3498e`: adversarial overclaim and false
  readiness review.

Accepted synthesis:

- No current artifact supports source-backed rail timing claims.
- `data/rail/ktdb_gtfs_source_extract.csv` and retained KTDB raw HTML are source
  context only, not a GTFS feed and not GTFS validation.
- `data/rail/metro9_capacity_source_extract.csv` is capacity source context
  only, pending human review, and does not make the modeled 500 pax/train value
  source-backed.
- Rail station bindings are present, but station binding is not rail headway,
  travel-time, capacity, or availability evidence.
- Rail capacity is currently sensitivity-only unless a reviewer records a
  source-backed or exclusion decision.
- Rail availability is currently scenario-only unless a reviewer records a
  source-backed, sensitivity-only, or exclusion decision.
- The next implementation should not add another review-support packet. It
  should first harden false-readiness guards so completed non-formal
  source-decision ledgers cannot be mistaken for publication-ready rail
  evidence.

## Current Evidence Availability

Present local context files:

- `data/rail/ktdb_gtfs_source_extract.csv`
- `data/rail/ktdb_gtfs_notice_raw.html`
- `data/rail/ktdb_gtfs_dataset_list_raw.html`
- `data/rail/metro9_capacity_source_extract.csv`
- `data/rail/metro9_capacity_source_raw.html`
- `data/rail/pilot_station_binding_cache.csv`
- `data/parameters/rail_station_bindings.csv`
- `data/parameters/rail_service_evidence.csv`

Missing rail timing inputs:

- `data/rail/pilot_gtfs.zip`
- `data/rail/pilot_gtfs_validator_report.json`
- `data/rail/pilot_rail_timetable_cache.csv`
- `data/rail/pilot_rail_timetable_raw.json`
- `data/rail/pilot_rail_shortest_path_cache.csv`
- `data/rail/pilot_rail_shortest_path_raw.json`
- `DATA_GO_KR_KEY` in the current shell

Current `data/rail/rail_source_decision_manifest.json` reports:

- `row_count=5`
- `completed_source_decision_count=0`
- `blocking_decision_count=3`
- `human_review_decision_count=2`
- `rail_source_decision_recorded=false`
- `publication_ready=false`
- `can_mark_complete=false`

Current `data/manifests/publication_readiness_audit.json` reports:

- `publication_ready=false`
- `blocked_gate_count=7`
- `rail_source_decision_ready=false`
- `rail_service_evidence_ready=false`

## Row Classification

| request_id | Current classification | Reason |
| --- | --- | --- |
| `rail_static_gtfs_timing_request` | Pending/blocked; not source-backed | Reviewed GTFS feed and GTFS Validator report are absent. |
| `rail_timetable_headway_request` | Pending/blocked; not source-backed | `DATA_GO_KR_KEY`, timetable cache, and raw payload are absent. |
| `rail_shortest_path_travel_time_request` | Pending/blocked; not source-backed | `DATA_GO_KR_KEY`, shortest-path cache, and raw payload are absent. |
| `rail_capacity_treatment_request` | Pending; current treatment sensitivity-only | Metro9 source context exists but remains pending review and does not validate current model capacity. |
| `rail_availability_scenario_request` | Pending; current treatment scenario-only | Stress profiles cover scenario behavior only and are not availability evidence. |

## Accepted Next Implementation Scope

Implement a narrow false-readiness guard:

- `src/realworld/publication_readiness.py` must not mark rail source decisions
  ready when the source-decision manifest itself has `publication_ready=false`
  or `can_mark_complete=false`, even if non-formal action-ledger rows are all
  completed.
- Add a regression test proving a complete non-formal source-decision manifest
  remains not publication-ready.
- `src/realworld/rail_source_decision_packet.py` must not mark source-backed
  acquisition action rows complete unless every retained `source_cache_path` and
  `raw_payload_path` file exists locally and matches a 64-hex SHA256 entry in
  `artifact_sha256s`.
- Add a regression test proving fake hashes and missing reviewed files keep
  acquisition rows incomplete.

Rejected scope:

- Do not create or synthesize GTFS, timetable, shortest-path, capacity, or
  availability evidence.
- Do not create formal acceptance targets.
- Do not make stress-profile or bounded-treatment artifacts support rail
  evidence gates.

## Required Verification

After the guard patch, run:

```powershell
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
```

Expected result:

- Publication readiness remains false.
- Final-study readiness remains false.
- The false-readiness guard blocks complete non-formal source-decision manifests
  unless the source-decision manifest is itself publication-ready and
  mark-complete capable.
- Source-backed acquisition choices remain incomplete unless all local
  source/cache/raw artifacts exist and match `path=64hex_sha256` values.

## Observed Verification

Commands run after the guard patch:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\publication_readiness.py tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python scripts\write_rail_source_decision_action_ledger_template.py
```

Observed results:

- Python compile checks passed.
- Publication readiness tests passed, including the regression that rejects a
  complete non-formal rail source-decision manifest with
  `publication_ready=false` and `can_mark_complete=false`.
- Rail source-decision packet tests passed.
- Rail source-decision packet tests passed, including the regression that fake
  or missing source-backed acquisition artifacts remain incomplete and real
  retained local source/cache/raw artifacts require matching 64-hex SHA256
  values.
- Rail source-decision packet and action-ledger template artifacts were
  regenerated with the `path=64hex_sha256` instruction.
- Rail bounded-treatment audit tests passed.
- Final-study readiness tests passed.
- Publication readiness audit reports `publication_ready=false`, 1 ready gate,
  7 blocked gates, and `rail_source_decision_ready=false`.
- Current goal completion audit reports `final_study_ready=False` and 12
  blocked gates.
- Plan audit tests passed.
- Formal acceptance artifact guard reports 0 formal target files present, 12
  missing, 0 placeholders/templates in formal paths, and
  `formal_acceptance_ready=false`.
- Formal acceptance package validation reports 0/12 ready gates and
  `final_study_ready=false`.
