# Phase 4 Rail Source Artifact Integrity Guard Ledger

Date: 2026-06-03

Objective: apply one consistent source-artifact integrity guard to cached rail
GTFS, timetable, headway-only timetable, and shortest-path derivation paths.

## Baseline

- Current scope: Phase 4 rail/transit evidence guard work.
- Formal acceptance status: unchanged; no formal acceptance artifact was
  created.
- Claim boundary: review support only. These guards do not prove rail service
  calibration, emergency availability, operational routing, publication
  readiness, final-study readiness, or formal acceptance.

## Files Inspected

- `src/realworld/rail_gtfs.py`
- `src/realworld/rail_timetable.py`
- `src/realworld/rail_shortest_path.py`
- `src/realworld/source_artifacts.py`
- `tests/test_realworld_rail_gtfs.py`
- `tests/test_realworld_rail_timetable.py`
- `tests/test_realworld_rail_shortest_path.py`
- `tests/test_realworld_rail_derivation_scripts.py`
- `plan.md`

## Files Edited

- `src/realworld/source_artifacts.py`
- `src/realworld/__init__.py`
- `src/realworld/rail_gtfs.py`
- `src/realworld/rail_timetable.py`
- `src/realworld/rail_shortest_path.py`
- `tests/test_realworld_source_artifacts.py`
- `tests/test_realworld_rail_gtfs.py`
- `tests/test_realworld_rail_timetable.py`
- `tests/test_realworld_rail_shortest_path.py`
- `tests/test_realworld_rail_derivation_scripts.py`
- `plan.md`

## Sub-Agent Review

Reviewer: GPT-5.5 xhigh read-only reviewer.

Findings accepted:

- Shortest-path derivation lacked the source-artifact SHA guard.
- Timetable and shortest-path derivations did not prove that the loaded
  records came from the same artifact named in the metadata.
- GTFS derivation had a `CachedGtfsFeed.source_path`, but the derive path did
  not compare it to `source_artifact_path`.
- The missing-egress timetable test needed a valid artifact path/hash so it
  continued to test egress matching rather than artifact validation.
- The shared helper needed direct tests for malformed SHA, mismatch, and path
  mismatch behavior.

Self-refine actions:

- Added `src/realworld/source_artifacts.py` as a shared file/SHA/path-integrity
  helper.
- Added loaded-source-to-metadata path matching for GTFS feeds, cached
  timetable events, headway-only timetable events, and cached shortest-path
  records.
- Added source-path carrying sequence wrappers for timetable and shortest-path
  loaders.
- Added direct source-artifact helper tests.
- Added regression tests for source SHA mismatch and loaded-source metadata
  mismatch across GTFS, timetable, headway-only timetable, and shortest-path
  evidence derivation.
- Added CLI smoke tests that execute the four cached rail derivation scripts
  through `subprocess` with relative retained-source paths and production
  schema reload.
- Exposed the shared source-artifact helpers through the `src.realworld`
  package surface with explicit `source_artifact_*` names so callers do not
  confuse them with module-local `file_sha256` compatibility helpers.

## Verification

Commands run:

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\source_artifacts.py .\src\realworld\rail_gtfs.py .\src\realworld\rail_timetable.py .\src\realworld\rail_shortest_path.py .\tests\test_realworld_source_artifacts.py .\tests\test_realworld_rail_gtfs.py .\tests\test_realworld_rail_timetable.py .\tests\test_realworld_rail_shortest_path.py
.\.venv\Scripts\python .\tests\test_realworld_source_artifacts.py
.\.venv\Scripts\python .\tests\test_realworld_rail_gtfs.py
.\.venv\Scripts\python .\tests\test_realworld_rail_timetable.py
.\.venv\Scripts\python .\tests\test_realworld_rail_shortest_path.py
.\.venv\Scripts\python .\tests\test_realworld_rail_derivation_scripts.py
.\.venv\Scripts\python .\tests\test_realworld_rail_timetable_api.py
.\.venv\Scripts\python .\tests\test_realworld_rail_shortest_path_api.py
.\.venv\Scripts\python .\tests\test_realworld_rail_evidence.py
.\.venv\Scripts\python .\tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python -m py_compile .\src\realworld\__init__.py .\src\realworld\source_artifacts.py .\tests\test_realworld_source_artifacts.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
```

Observed result: all commands above passed.

## Gate Decision

Proceed within Phase 4 guard work. The cached rail derivation paths now require
source-artifact path/hash consistency and loaded-source path binding. This does
not close rail evidence or final-study gates because reviewed timetable,
shortest-path, GTFS, capacity, and availability evidence decisions remain open.
