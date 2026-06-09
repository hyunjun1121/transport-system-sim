# Phase 4 Static Timetable Source-Request Refinement - 2026-06-03

## Objective

Refine the Phase 4 rail static timetable source-request path so the worksheet
names a concrete official source candidate while preserving the blocker that no
reviewed static timetable CSV, explicit mapping, or normalization manifest has
been retained yet.

## Baseline Evidence

- Inspected `src/realworld/rail_timetable_static.py`.
- Inspected `scripts/normalize_rail_timetable_cache.py`.
- Inspected `tests/test_realworld_rail_timetable_static.py`.
- Inspected `src/realworld/rail_timetable.py`.
- Inspected `tests/test_realworld_rail_timetable.py`.
- Inspected `data/rail/rail_source_decision_packet.csv`.
- Inspected generated rail timing, fetch-readiness, priority, and source
  decision documents.
- Checked `data/rail/` inventory. The reviewed static timetable source CSV,
  normalized timetable cache, and normalization manifest were absent from the
  listed artifacts.
- Fetched the official Seoul Open Data page
  `https://data.seoul.go.kr/dataList/OA-22522/F/1/datasetView.do` with
  `Invoke-WebRequest`; the response status was 200 and the page text contained
  `서울교통공사_서울 도시철도 열차운행시각표`, `호선`, `역사코드`,
  `도착시간`, and `출발시간`.

## Write Scope

Approved edits:

- `src/realworld/rail_timing_request_packet.py`
- `tests/test_realworld_rail_timing_request_packet.py`
- `tests/test_realworld_rail_fetch_readiness_packet.py`
- generated rail request/readiness/priority/source-decision/recommendation
  CSV, JSON, and Markdown outputs derived from the rail timing request packet.

Forbidden edits:

- formal acceptance artifacts;
- `data/parameters/rail_service_evidence.csv`;
- broad cleanup, directory moves, or deletion.

## Implementation

- Added `STATIC_TIMETABLE_SOURCE_NAME` and
  `STATIC_TIMETABLE_SOURCE_CITATION` constants for the Seoul Open Data Plaza
  train timetable file candidate.
- Updated the static timetable timing request row to cite that official source
  candidate instead of the placeholder `reviewed source citation required`
  text.
- Updated the suggested derive command to carry the same source citation.
- Updated tests to assert the official source name and citation propagate into
  timing request and fetch-readiness rows.
- Added the static timetable request to the rail evidence priority packet so
  the same blocker is visible in the timing request, fetch-readiness, priority,
  source-decision, and recommendation packet chain.
- Renamed the fetch-readiness manifest count semantics so
  `required_external_input_present_count` counts only non-blocked rows with
  required-input text, while
  `required_external_input_text_present_count` preserves the count of rows that
  specify required external input text.
- Added the GTFS Validator report requirement to the static-GTFS timing request
  documentation and generated command surfaces.
- Updated the plan artifact audit expected row count for
  `rail_evidence_priority_packet.csv` from 6 to 7.
- Regenerated:
  - `data/rail/rail_timing_source_request_packet.csv`
  - `data/rail/rail_timing_source_request_manifest.json`
  - `data/rail/rail_fetch_readiness_packet.csv`
  - `data/rail/rail_fetch_readiness_manifest.json`
  - `docs/rail_fetch_readiness_packet.md`
  - `data/rail/rail_evidence_priority_packet.csv`
  - `data/rail/rail_evidence_priority_manifest.json`
  - `docs/rail_evidence_priority_packet.md`
  - `data/rail/rail_source_decision_packet.csv`
  - `data/rail/rail_source_decision_manifest.json`
  - `docs/rail_source_decision_packet.md`
  - `data/rail/rail_source_decision_recommendation_packet.csv`
  - `data/rail/rail_source_decision_recommendation_manifest.json`
  - `docs/rail_source_decision_recommendation_packet.md`

## Verification Run So Far

- `.\.venv\Scripts\python -m py_compile .\src\realworld\rail_timing_request_packet.py .\tests\test_realworld_rail_timing_request_packet.py`
- `.\.venv\Scripts\python .\tests\test_realworld_rail_timing_request_packet.py`
- `.\.venv\Scripts\python .\scripts\write_rail_timing_source_request_packet.py`
- `.\.venv\Scripts\python .\scripts\write_rail_fetch_readiness_packet.py`
- `.\.venv\Scripts\python .\scripts\write_rail_evidence_priority_packet.py`
- `.\.venv\Scripts\python .\scripts\write_rail_source_decision_packet.py`
- `.\.venv\Scripts\python .\scripts\write_rail_source_decision_recommendation_packet.py`
- `.\.venv\Scripts\python .\tests\test_realworld_rail_timing_request_packet.py`
- `.\.venv\Scripts\python .\tests\test_realworld_rail_fetch_readiness_packet.py`
- `.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_packet.py`
- `.\.venv\Scripts\python .\tests\test_realworld_rail_evidence_priority_packet.py`
- `.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_recommendation_packet.py`
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
- `.\.venv\Scripts\python .\scripts\audit_publication_readiness.py`
- `.\.venv\Scripts\python .\scripts\audit_final_study_readiness.py`

## Sub-Agent Review Findings

- Implementation/test reviewer found one blocker: the static timetable request
  had not been propagated into `rail_evidence_priority_packet.csv`. This was
  fixed by adding the row and updating tests and the plan artifact audit
  expectation to 7 rows.
- Implementation/test reviewer found one medium issue: the static-GTFS
  documentation omitted the GTFS Validator report requirement. This was fixed
  in the request documentation and command/test surfaces.
- Implementation/test reviewer found one low issue: static timetable constants
  were not exported through module `__all__`. This was fixed.
- Rail methodology/overclaim reviewer found one medium issue: the old
  `required_external_input_present_count` name was misleading because it counted
  specified text, not non-blocked present input. This was fixed by adding
  separate specified/text-present counts and narrowing the present count.
- Rail methodology/overclaim reviewer confirmed the official static timetable
  source is still only a candidate request path and must not be treated as
  accepted rail evidence.

## Final Verification

- `data/rail/rail_evidence_priority_packet.csv` now has 7 rows.
- `rail_static_timetable_csv_headway_request` appears in the priority packet
  with `readiness_status=blocked_missing_reviewed_static_timetable_csv` and
  `can_close_timing_fields_after_review=false`.
- `data/rail/rail_fetch_readiness_manifest.json` now reports
  `required_external_input_specified_count=6`,
  `required_external_input_text_present_count=6`, and
  `required_external_input_present_count=2`.
- `scripts/audit_plan_artifacts.py` now reports
  `all_required_artifacts_present=true` and keeps the scaffold verdict:
  `executable_quasi_real_scaffold_not_final_calibrated_study`.
- `git diff --check` on touched files reported only CRLF normalization
  warnings.

## Gate Status

This refinement does not create rail evidence. The reviewed static timetable
CSV, normalized cache, and manifest are still absent; rail evidence,
publication readiness, final-study readiness, and formal acceptance remain
blocked.
