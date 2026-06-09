# Rail Service Static Candidate - 2026-06-08

## Scope

Created a non-formal static rail-service candidate packet from the retained
static timetable cache and existing segment-pair diagnostic. This work supports
reviewer triage only. It does not modify
`data/parameters/rail_service_evidence.csv` and does not close rail,
publication, final-study, or formal acceptance gates.

## Sub-Agent Reviews

- `019ea5fb-4bba-7d30-8086-e40bb26c5440`
  - Role: rail evidence/provenance reviewer.
  - Recommendation: a separate `data/rail/rail_service_evidence_static_candidate.csv`
    is dependency-safe only if it stays non-formal, keeps
    `data/parameters/rail_service_evidence.csv` unchanged, and marks the current
    static cache as headway-only. Travel time from the segment-pair diagnostic
    must remain proxy/not-derived because the diagnostic includes an assumed
    transfer buffer.
- `019ea5fb-883b-7673-b0ec-f12cd147527b`
  - Role: adversarial claim-boundary reviewer.
  - Recommendation: do not modify rail/status guard files or formal targets.
    Keep all rail evidence, publication, final-study, acceptance, calibration,
    availability, and operational claims false.

## Files Added

- `src/realworld/rail_service_static_candidate.py`
- `scripts/write_rail_service_static_candidate.py`
- `tests/test_realworld_rail_service_static_candidate.py`
- `data/rail/rail_service_evidence_static_candidate.csv`
- `data/rail/rail_service_evidence_static_candidate_manifest.json`
- `docs/rail_service_evidence_static_candidate.md`

## Generated Manifest

`data/rail/rail_service_evidence_static_candidate_manifest.json` reports:

- `artifact_class=non_formal_static_rail_service_candidate`
- `candidate_only=true`
- `row_count=1`
- `formal_target_path=data/parameters/rail_service_evidence.csv`
- `formal_target_written=false`
- `rail_service_evidence_written=false`
- `writes_default_rail_service_evidence_path=false`
- `replaces_data_parameters_rail_service_evidence=false`
- `publication_ready=false`
- `final_study_ready=false`
- `formal_acceptance_evidence=false`
- `can_support_rail_evidence_gate=false`
- `can_support_publication_gate=false`
- `can_support_final_study_gate=false`
- `can_support_acceptance_gate=false`
- `accepted_source_backed_rail_service_evidence=false`
- `rail_source_decision_recorded=false`
- `source_license_or_provenance_review_status=pending_or_not_recorded`
- `observed_transfer_calibration=false`
- `capacity_source_backed=false`
- `derived_field_counts={headway: 1, travel_time: 0, capacity: 0}`
- `travel_time_value_status=proxy_not_derived`
- `capacity_value_status=sensitivity_only_or_pending`
- `gate_decision_authority=none`

## Commands Run

```powershell
.\.venv\Scripts\python scripts\write_rail_service_static_candidate.py
Get-FileHash -Algorithm SHA256 data\parameters\rail_service_evidence.csv
.\.venv\Scripts\python tests\test_realworld_rail_service_static_candidate.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence.py
.\.venv\Scripts\python tests\test_realworld_rail_static_timetable_segment_pair_diagnostic.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable_static.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

Results:

- All four targeted rail test files passed. The static timetable test required
  a longer command timeout and then passed.
- `data/parameters/rail_service_evidence.csv` hash was checked and the candidate
  writer did not modify the formal rail evidence table.
- Rail evidence audit still reports `publication_ready=false` and
  `timing_evidence_ready=false` because the formal rail evidence table remains a
  documented assumption proxy.
- Publication audit still reports `publication_ready=false`, `1/10` ready gates.
- Final-study audit still reports `final_study_ready=false`.

## Gate Impact

- Promoted phases: none.
- Closed gates: none.
- New evidence: non-formal static timetable rail-service candidate for reviewer
  triage.
- Remaining blockers:
  - `data/parameters/rail_service_evidence.csv` still has no derived records;
  - rail source decisions remain pending;
  - travel time remains proxy/not-derived from the candidate packet;
  - transfer buffer is assumed, not observed or source-backed;
  - rail capacity remains sensitivity-only or pending;
  - source/provenance/license acceptance is absent.

## Next Dependency-Safe Work

The next safe work is to improve parameter-source triage or source-provenance
triage without writing formal acceptance targets. Do not edit
`data/parameters/rail_service_evidence.csv` until source decisions are recorded
and reviewed.
