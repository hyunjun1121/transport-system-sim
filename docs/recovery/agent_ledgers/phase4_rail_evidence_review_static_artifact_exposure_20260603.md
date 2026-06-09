# Phase 4 Rail Evidence Review Static Artifact Exposure - 2026-06-03

## Objective

Update the consolidated rail evidence review packet so it reflects the retained
static timetable cache and segment-pair diagnostic created in Phase 4, without
promoting either artifact to rail evidence or transfer evidence.

## Baseline Finding

After the static timetable diagnostic work, `data/parameters/rail_evidence_review_packet.csv`
still had 10 rows and represented timing paths only as derivation code with no
default source cache. That was stale for review workflow purposes because the
retained static cache and diagnostic artifacts existed but were invisible in
the consolidated review packet.

## Implementation

Updated `src/realworld/rail_evidence_review_packet.py` to add two conservative
rows:

- `rail_static_timetable_cache_review`
- `rail_static_timetable_segment_pair_diagnostic`

Both rows are forced to:

- `weak_for_final_claim=true`
- `service_publication_ready=false`
- publication use status ending in `not_evidence`
- artifact status ending in `non_evidence` when the corresponding guarded
  manifest is readable

The writer manifest now lists the static timetable cache and diagnostic
artifacts under `inputs` and keeps `publication_ready=false`.

Updated:

- `tests/test_realworld_rail_evidence_review_packet.py`
- `scripts/audit_plan_artifacts.py`
- `tests/test_realworld_plan_audit.py`
- `agents.md`
- `status.md`
- `docs/rail_evidence_review_packet.md`
- `docs/recovery/agent_ledgers/phase4_static_timetable_segment_pair_diagnostic_20260603.md`

Regenerated:

- `data/parameters/rail_evidence_review_packet.csv`
- `data/parameters/rail_evidence_review_manifest.json`
- `data/rail/rail_evidence_priority_packet.csv`
- `data/rail/rail_evidence_priority_manifest.json`
- `docs/rail_evidence_priority_packet.md`
- `data/rail/rail_source_decision_packet.csv`
- `data/rail/rail_source_decision_manifest.json`
- `docs/rail_source_decision_packet.md`
- `data/rail/rail_source_decision_recommendation_packet.csv`
- `data/rail/rail_source_decision_recommendation_manifest.json`
- `docs/rail_source_decision_recommendation_packet.md`

## Verification

Passed:

- `.\.venv\Scripts\python -m py_compile src\realworld\rail_evidence_review_packet.py tests\test_realworld_rail_evidence_review_packet.py scripts\write_rail_evidence_review_packet.py scripts\audit_plan_artifacts.py tests\test_realworld_plan_audit.py`
- `.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_evidence_review_packet.py`
- `.\.venv\Scripts\python scripts\write_rail_evidence_priority_packet.py`
- `.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py`
- `.\.venv\Scripts\python scripts\write_rail_source_decision_recommendation_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_evidence_priority_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_source_decision_recommendation_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_plan_audit.py`
- `.\.venv\Scripts\python scripts\audit_plan_artifacts.py`
- `.\.venv\Scripts\python scripts\audit_rail_evidence.py`
- `.\.venv\Scripts\python scripts\audit_publication_readiness.py`
- `.\.venv\Scripts\python scripts\audit_final_study_readiness.py`

Current verified packet state:

- `rail_evidence_review_packet.csv` has 12 rows.
- `rail_evidence_review_manifest.json` has `publication_ready=false`.
- Static cache row status is `static_timetable_cache_retained_not_evidence`.
- Diagnostic row status is
  `static_segment_pair_diagnostic_retained_not_evidence`.

## Remaining Blockers

- `rail_service_evidence.csv` still has no derived headway or travel-time rows.
- `rail_evidence` remains blocked in publication and final-study audits.
- GTFS, shortest-path, timetable API, transfer, capacity, and availability
  source decisions remain open.
- No formal acceptance artifact was created.
