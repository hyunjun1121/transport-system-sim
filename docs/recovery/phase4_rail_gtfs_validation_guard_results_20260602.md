# Phase 4 Rail GTFS Validation Guard Results - 2026-06-02

## Scope

This phase strengthens the rail/transit evidence path by requiring a retained
GTFS Validator report for any `cached_gtfs_derived` rail timing evidence row.
The work is a guardrail and review-support improvement only. It does not create
reviewed GTFS evidence, rail-service calibration, rail availability evidence,
formal acceptance artifacts, or operational rail routing claims.

## Files Added Or Updated

Updated:

- `src/realworld/rail_evidence.py`
- `src/realworld/rail_gtfs.py`
- `src/realworld/rail_timetable.py`
- `src/realworld/rail_shortest_path.py`
- `src/realworld/publication_readiness.py`
- `src/realworld/rail_timing_request_packet.py`
- `src/realworld/rail_fetch_readiness_packet.py`
- `scripts/derive_rail_gtfs_evidence.py`
- `tests/test_realworld_rail_gtfs.py`
- `tests/test_realworld_rail_evidence.py`
- `tests/test_realworld_rail_timing_request_packet.py`
- `tests/test_realworld_rail_fetch_readiness_packet.py`
- `tests/test_realworld_publication_readiness.py`
- `tests/test_realworld_acceptance_orchestration.py`
- `docs/schemas/rail_gtfs_cache_schema.md`
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
- `data/manifests/publication_readiness_audit.json`
- `docs/publication_readiness_audit.md`

## Implementation Notes

- `RailServiceEvidence` now supports optional
  `gtfs_validator_report_path` and `gtfs_validator_report_sha256` fields.
- `cached_gtfs_derived` rows require both validator report fields.
- `summarize_rail_service_evidence()` now reports:
  - `gtfs_validation_required_count`
  - `gtfs_validation_ready`
- GTFS-derived timing can be publication-ready only when:
  - cached source artifact path exists;
  - cached source artifact SHA256 matches;
  - GTFS Validator report path exists;
  - GTFS Validator report SHA256 matches;
  - headway and travel time are derived;
  - capacity is source-backed or explicitly sensitivity-only.
- `scripts/derive_rail_gtfs_evidence.py` now requires
  `--gtfs-validator-report` and records the report path and SHA256.
- The GTFS source-request row now requires both `pilot_gtfs.zip` and
  `pilot_gtfs_validator_report.json` before derivation review.
- `publication_readiness.py` now includes `rail_source_decision_ready` so
  timing evidence alone cannot bypass unresolved capacity, availability, or
  source-decision blockers.

## Generated Evidence Summary

Regenerated rail packets in dependency order:

```powershell
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py
.\.venv\Scripts\python scripts\write_rail_fetch_readiness_packet.py
.\.venv\Scripts\python scripts\write_rail_evidence_priority_packet.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
```

Observed rail-source decision summary:

- `row_count`: 5
- `blocking_decision_count`: 3
- `human_review_decision_count`: 2
- `rail_source_decision_recorded`: `false`
- `publication_ready`: `false`
- `can_mark_complete`: `false`
- GTFS blocker now states that the reviewed GTFS file or GTFS Validator report
  is absent.

Observed publication readiness summary:

- `gate_count`: 8
- `ready_gate_count`: 1
- `blocked_gate_count`: 7
- `rail_station_binding_ready`: `true`
- `rail_service_evidence_ready`: `false`
- `rail_source_decision_ready`: `false`
- `rail_evidence_ready`: `false`
- `publication_ready`: `false`

Observed rail evidence audit summary:

- `row_count`: 1
- `current_source_statuses`: `documented_assumption_proxy`
- `gtfs_validation_required_count`: 0
- `gtfs_validation_ready`: `true`
- `timing_evidence_ready`: `false`
- `service_publication_ready`: `false`
- `station_binding_ready`: `true`

## Tests And Checks Run

Passed:

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_gtfs.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_rail_timing_request_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence_priority_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_acceptance_orchestration.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
```

Observed final-study readiness remains blocked:

- `final_study_ready`: `false`
- `verdict`: `final_real_world_study_blocked`
- blocked gates remain 12 of 15.

## Remaining Risks

- No reviewed GTFS feed is currently present for the pilot rail leg.
- No GTFS Validator report is currently present for a reviewed pilot GTFS feed.
- Current rail service evidence remains a documented assumption proxy.
- Rail capacity and rail availability remain source-decision or human-review
  items, not accepted evidence.
- This phase prevents future overclaiming but does not itself improve rail
  calibration.
