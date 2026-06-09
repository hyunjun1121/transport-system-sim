# Rail Evidence Reviewer Wave - 2026-06-08

## Scope

This ledger records a read-only rail-evidence review. It does not modify
`data/parameters/rail_service_evidence.csv` and does not close rail evidence,
publication, or final-study gates.

## Reviewer Evidence

- `019ea5a9-8bff-7e52-ad11-b27c4972a38c`: rejected replacing the current
  `documented_assumption_proxy` rail-service row with derived timing evidence.

## Evidence Checked

- `data/parameters/rail_service_evidence.csv`
- `data/parameters/rail_evidence_review_manifest.json`
- `data/rail/rail_fetch_readiness_manifest.json`
- `data/rail/rail_source_decision_manifest.json`
- `data/rail/pilot_rail_static_timetable_cache_manifest.json`
- `data/rail/pilot_rail_static_timetable_segment_pair_diagnostic_manifest.json`
- `src/realworld/rail_evidence.py`
- `src/realworld/rail_timetable.py`

## Commands Run

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_evidence.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
```

The tests passed. The audit reports station binding ready but rail timing
evidence blocked:

- `current_source_statuses=["documented_assumption_proxy"]`
- `derived_record_count=0`
- `timing_evidence_ready=false`
- `publication_ready=false`

## Decision

Keep `data/parameters/rail_service_evidence.csv` unchanged. The retained static
timetable cache can support headway review only; it has no egress events and
cannot derive station-to-station travel time. The segment-pair diagnostic remains
diagnostic-only and must not be promoted to rail-service evidence without a
separate source/provenance and timing review.

## Remaining Blockers

- Obtain or review a rail source that supports travel-time evidence, such as a
  cached shortest-path response, reviewed GTFS plus validator report, or a
  timetable cache with matched access and egress events.
- Keep capacity source-backed or explicitly sensitivity-only.
- Record source artifact paths and SHA256 digests before any derived rail row is
  used.
- Rerun rail, publication, and final-study readiness audits after any rail
  evidence changes.
