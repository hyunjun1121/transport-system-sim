# Phase 4 Post-Cache Rail Evidence Synthesis - 2026-06-03

## Scope

This ledger records the post-cache Phase 4 synthesis after three read-only
GPT-5.5 xhigh explorer agents reviewed the current rail/transit evidence state.

This ledger is not rail evidence, not rail-service calibration, not operational
rail availability evidence, not publication readiness, not final-study
readiness, and not formal acceptance.

## Explorer Wave

- GTFS/timetable/shortest-path explorer:
  confirmed that `data/rail/pilot_gtfs.zip` and
  `data/rail/pilot_gtfs_validator_report.json` are absent, and that the current
  `data/rail/pilot_rail_timetable_cache.csv` has 241 access events and 0
  egress events. The existing cache supports headway review only.
- Capacity/availability explorer:
  classified capacity as sensitivity-only unless separately sourced, and
  availability as scenario-only unless separately sourced or excluded.
- Overclaim/adversarial explorer:
  rejected any builder that would promote the current cache to rail evidence or
  close rail evidence, publication, final-study, or formal acceptance gates.
  A builder may only perform tightly bounded diagnostics or claim-boundary
  hardening after this synthesis.

## Main-Thread Evidence Inspected

- `plan.md`, Phase 4 and Immediate Next Actions
- `data/rail/rail_source_decision_manifest.json`
- `data/rail/rail_timing_source_request_packet.csv`
- `data/rail/rail_source_decision_recommendation_packet.csv`
- `data/rail/pilot_rail_timetable_static_source.csv`
- `data/rail/pilot_rail_timetable_cache.csv`
- `data/rail/pilot_rail_timetable_cache_manifest.json`
- `data/parameters/rail_station_bindings.csv`
- `data/manifests/publication_readiness_audit.json`
- `data/manifests/current_goal_completion_audit.json`

The local environment has `DATA_GO_KR_KEY` absent. Therefore live data.go.kr
rail timetable and shortest-path fetches remain blocked unless a reviewed
cached payload is supplied.

## Current Classification

| Request | Current classification | Reason |
| --- | --- | --- |
| `rail_static_gtfs_timing_request` | pending / missing source artifacts | Reviewed GTFS feed and same-feed Validator report are absent. KTDB context files are metadata only. |
| `rail_timetable_headway_request` | blocked by missing API key/cache | API-backed timetable cache is absent and `DATA_GO_KR_KEY` is absent. |
| `rail_static_timetable_csv_headway_request` | ready for headway review only | Static source and normalized headway cache are retained, but egress event count is 0 in the current cache. |
| `rail_shortest_path_travel_time_request` | blocked by missing API key/cache | Shortest-path cache/raw payloads are absent and `DATA_GO_KR_KEY` is absent. |
| `rail_capacity_treatment_request` | sensitivity-only or excluded | Metro9 context exists, but source/provenance review and reviewer decision are absent. |
| `rail_availability_scenario_request` | scenario-only or excluded | Current stress profile documents scenarios, not observed emergency rail availability. |

## Static Timetable Follow-Up Observation

The retained static timetable source contains station rows for Olympic Park,
Seokchon, and Jamsil. A main-thread probe found physically positive weekday
candidate segments:

- Line 9 DOWN: Olympic Park -> Seokchon, 241 train rows, median 5.917
  minutes.
- Line 8 UP: Seokchon -> Jamsil, 160 train rows, median 1.833 minutes.

This observation does not create rail evidence. It only suggests a possible
non-evidence diagnostic path: derive a static timetable segment-pair diagnostic
from the retained static source and mark it as review support. It must not be
described as transfer evidence because the static train rows do not validate
Seokchon transfer walking time, connection wait, crowding, station circulation,
or calibration.

## Builder Boundary

Allowed next implementation scope:

- add a static-timetable segment-pair diagnostic artifact; or
- harden claim boundaries so current headway cache cannot be overread.

Not allowed in this phase without additional reviewed evidence:

- write a source-backed rail-service evidence row from the diagnostic;
- mark `publication_ready`, `final_study_ready`, or `can_mark_complete` true;
- create or imply formal rail, parameter, provenance, or final-study
  acceptance;
- treat capacity or availability as source-backed.

## Required Verification For Any Follow-Up Edit

Run touched rail tests first, then readiness audits. Minimum expected commands:

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_timetable_static.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable.py
.\.venv\Scripts\python tests\test_realworld_rail_derivation_scripts.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence.py
.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```
