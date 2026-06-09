# Phase 7 External Benchmark Cache Guard Ledger - 2026-06-03

## Scope

Implemented a bounded external route benchmark guard for the current pilot
validation layer. This work keeps OSRM and fallback rows as plausibility
comparators only. It does not create validation acceptance, publication
readiness, or operational route guidance.

## Sub-Agent Review Inputs

- Road-route benchmark reviewer found stale raw-cache risk, split threshold
  logic, missing CSV-to-raw row binding, and OSRM waypoint snap-distance
  exposure.
- Multimodal benchmark reviewer found that R5/r5py/GTFS/OpenTripPlanner
  execution is not currently supportable from accepted cached evidence.
- Provenance reviewer found validation-acceptance bypass risk, missing raw
  payload binding, missing threshold hash governance, and incomplete route
  geometry/version provenance.

## Changes Made

- Updated `src/realworld/plausibility.py` so external benchmark route
  comparison defaults match the Phase 7 threshold table:
  road distance pass within 10 percent and warn within 25 percent; road
  free-flow duration pass within 20 percent and warn within 40 percent.
- Updated `scripts/run_osrm_route_benchmark.py` so the CLI defaults to replaying
  retained raw OSRM payloads from `data/validation/osrm_route_raw/` instead of
  making live OSRM requests. Live refresh remains explicit through
  `--refresh-live`.
- Updated `src/realworld/osrm_snapshot_manifest.py` to bind every OSRM CSV row
  to retained raw payload path, payload SHA256, query URL, reference version,
  benchmark distance, benchmark duration, and waypoint snap-distance status.
- Updated validation review, validation strategy-readiness, and validation
  benchmark-readiness packets to surface raw-payload mismatches, missing raw
  payload rows, OSRM snap-distance warnings, and source-pinning status.
- Regenerated route plausibility, external benchmark, OSRM manifest, validation
  review, validation strategy-readiness, validation benchmark-readiness,
  validation benchmark-decision, Phase 8 precompact threshold, final-study
  readiness, and publication-readiness outputs.

## Current Benchmark State

- Fallback benchmark rows under the stricter threshold bands: pass 1, warn 1,
  fail 1. The failing fallback row reinforces that fallback detour-speed rows
  are placeholders/review aids, not accepted route validation.
- Cached OSRM benchmark rows: pass 3 under route distance/time threshold bands.
- OSRM raw payload binding: 3 rows matched, 0 missing, 0 mismatched.
- OSRM waypoint snap status: pass 1, warn 2, max snap distance 265.494619 m.
  These rows require human review before route-comparison wording is relied on.

## Commands Run

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\plausibility.py .\src\realworld\osrm_snapshot_manifest.py .\scripts\run_osrm_route_benchmark.py .\tests\test_realworld_plausibility.py .\tests\test_realworld_osrm_snapshot_manifest.py
.\.venv\Scripts\python -m py_compile .\src\realworld\validation_review_packet.py .\src\realworld\validation_benchmark_readiness_packet.py
.\.venv\Scripts\python .\scripts\run_plausibility_validation.py
.\.venv\Scripts\python .\scripts\run_osrm_route_benchmark.py
.\.venv\Scripts\python .\scripts\write_validation_review_packet.py
.\.venv\Scripts\python .\scripts\write_osrm_snapshot_manifest.py
.\.venv\Scripts\python .\scripts\write_validation_benchmark_readiness_packet.py
.\.venv\Scripts\python .\scripts\write_validation_strategy_readiness_packet.py
.\.venv\Scripts\python .\scripts\write_validation_benchmark_decision_packet.py
.\.venv\Scripts\python .\scripts\write_phase8_precompact_tables.py
.\.venv\Scripts\python .\tests\test_realworld_plausibility.py
.\.venv\Scripts\python .\tests\test_realworld_osrm_snapshot_manifest.py
.\.venv\Scripts\python .\tests\test_realworld_validation_review_packet.py
.\.venv\Scripts\python .\tests\test_realworld_validation_benchmark_readiness_packet.py
.\.venv\Scripts\python .\tests\test_realworld_validation_strategy_readiness_packet.py
.\.venv\Scripts\python .\tests\test_realworld_validation_benchmark_decision_packet.py
.\.venv\Scripts\python .\tests\test_realworld_phase8_precompact_tables.py
.\.venv\Scripts\python .\scripts\audit_final_study_readiness.py
.\.venv\Scripts\python .\scripts\audit_publication_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_publication_readiness.py
git diff --check
```

`git diff --check` exited successfully with line-ending warnings only.

## Residual Limits

- The OSRM snapshot has no route geometry or external engine/map-data version
  in the retained payloads; it remains a review aid only.
- Full multimodal route-engine benchmarking is blocked until reviewed GTFS,
  timetable, shortest-path, or R5/OpenTripPlanner snapshots exist with source
  hashes and validator evidence.
- Formal validation remains blocked by missing
  `data/manifests/validation_acceptance.json`, scaffold validation-summary
  scope, and weak route-level road-evidence exposure.
- Publication and final-study readiness remain false.
