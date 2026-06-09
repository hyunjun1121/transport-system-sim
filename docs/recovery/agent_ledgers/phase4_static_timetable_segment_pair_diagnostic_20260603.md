# Phase 4 Static Timetable Segment-Pair Diagnostic - 2026-06-03

## Objective

Add a bounded rail timetable diagnostic from the retained static timetable
source while preserving the rail-evidence, transfer-evidence, publication,
final-study, and formal-acceptance blockers.

This work intentionally does not write `data/parameters/rail_service_evidence.csv`.

## Sub-Agent Review Wave

The review wave used three GPT-5.5 xhigh sub-agents before the main-thread
self-refine patch:

- Method-realism reviewer: treat the static timetable source as a diagnostic
  only. Use same-line segment timings for Line 9 Olympic Park to Seokchon and
  Line 8 Seokchon to Jamsil; do not claim observed transfer calibration.
- Source/provenance reviewer: retain source path, schema, size, and SHA256, but
  do not treat the source as accepted provenance, license, or final evidence.
- Adversarial reviewer: split API timetable and static timetable cache paths,
  add explicit non-evidence flags to manifests, avoid the phrase
  "transfer-route travel-time candidate", and update stale plan/status command
  inventories.

Main-thread decision:

- Accepted: a separate diagnostic artifact with explicit false readiness flags.
- Accepted: path split between API timetable cache and static timetable cache.
- Accepted: normalizer manifest flags that keep publication, final-study, and
  formal-acceptance support false.
- Rejected: any upgrade from diagnostic rows to rail service evidence,
  transfer evidence, or final-study readiness.

## Implementation

Added:

- `src/realworld/rail_static_timetable_segment_pair_diagnostic.py`
- `scripts/write_rail_static_timetable_segment_pair_diagnostic.py`
- `tests/test_realworld_rail_static_timetable_segment_pair_diagnostic.py`

Updated:

- `src/realworld/rail_timetable_static.py`
- `scripts/normalize_rail_timetable_cache.py`
- `src/realworld/rail_timing_request_packet.py`
- `tests/test_realworld_rail_timetable_static.py`
- `tests/test_realworld_rail_timing_request_packet.py`
- `plan.md`
- `README.md`
- `agents.md`
- `status.md`
- `docs/recovery/agent_ledgers/phase4_post_cache_rail_evidence_synthesis_20260603.md`

Generated:

- `data/rail/pilot_rail_static_timetable_cache.csv`
- `data/rail/pilot_rail_static_timetable_cache_manifest.json`
- `data/rail/pilot_rail_timetable_cache.csv`
- `data/rail/pilot_rail_timetable_cache_manifest.json`
- `data/rail/pilot_rail_static_timetable_segment_pair_diagnostic.csv`
- `data/rail/pilot_rail_static_timetable_segment_pair_diagnostic_manifest.json`
- `docs/rail_static_timetable_segment_pair_diagnostic.md`
- regenerated rail timing request, fetch-readiness, evidence-priority, and
  source-decision packets.

## Diagnostic Results

The diagnostic manifest records:

- source path: `data/rail/pilot_rail_timetable_static_source.csv`
- source SHA256:
  `46b6d9e2c2e1e23632fa72208a3ca5dc6aeba9013c403ee6f52747fec2b9a9e2`
- Line 9 Olympic Park to Seokchon matched rows: 241
- Line 8 Seokchon to Jamsil matched rows: 160
- feasible segment-pair connection count: 240
- assumed transfer buffer: 5.0 minutes
- median total diagnostic time: 16.25 minutes
- p90 total diagnostic time: 21.333 minutes

Manifest guard flags:

- `diagnostic_only=true`
- `publication_ready=false`
- `final_study_ready=false`
- `formal_acceptance_evidence=false`
- `can_mark_complete=false`
- `can_support_rail_evidence_gate=false`
- `can_support_transfer_evidence_gate=false`

## Verification

Passed:

- `.\.venv\Scripts\python -m py_compile src\realworld\rail_timing_request_packet.py src\realworld\rail_timetable_static.py src\realworld\rail_static_timetable_segment_pair_diagnostic.py scripts\write_rail_static_timetable_segment_pair_diagnostic.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_timing_request_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_timetable_static.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_static_timetable_segment_pair_diagnostic.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_evidence_priority_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_evidence.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_timetable.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_derivation_scripts.py`
- `.\.venv\Scripts\python tests\test_realworld_transfer_evidence_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_formal_acceptance_package.py`
- `.\.venv\Scripts\python tests\test_realworld_publication_readiness.py`
- `.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py`
- `.\.venv\Scripts\python tests\test_realworld_plan_audit.py`
- `.\.venv\Scripts\python scripts\audit_rail_evidence.py`
- `.\.venv\Scripts\python scripts\audit_plan_artifacts.py`
- `.\.venv\Scripts\python scripts\audit_publication_readiness.py`
- `.\.venv\Scripts\python scripts\audit_final_study_readiness.py`

Expected blocked state:

- rail service evidence remains blocked;
- publication readiness remains false;
- final-study readiness remains false;
- formal acceptance remains absent.

## Remaining Blockers

- Reviewed GTFS input and matching GTFS Validator report are absent.
- API timetable and shortest-path paths still require `DATA_GO_KR_KEY` or
  reviewed retained payloads.
- Rail source decisions remain pending for timing, capacity, and availability.
- Transfer walking/circulation/crowding calibration is not source-backed.
- Static timetable source provenance and license review are not formal
  acceptance.
- `rail_evidence_review_packet` was regenerated to expose the static cache and
  segment-pair diagnostic as review-only non-evidence rows, but it remains a
  review aid and cannot close any rail-evidence gate.
