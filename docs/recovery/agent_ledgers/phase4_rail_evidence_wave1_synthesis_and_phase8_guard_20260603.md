# Phase 4 Rail Evidence Wave 1 Synthesis and Phase 8 Guard Update

Date: 2026-06-03

Objective: synthesize the Phase 4 GPT-5.5 xhigh rail evidence explorer wave and
patch the Phase 8 experiment preflight guard so completed non-formal rail source
decisions cannot be mistaken for rail evidence, publication readiness,
final-study readiness, or formal acceptance.

## Files Inspected

- `plan.md`
- `src/realworld/pilot_experiments.py`
- `tests/test_realworld_pilot_experiments.py`
- `src/realworld/rail_source_decision_packet.py`
- `scripts/write_rail_source_decision_packet.py`
- `scripts/write_rail_source_decision_action_ledger_template.py`
- `data/rail/rail_source_decision_packet.csv`
- `data/rail/rail_source_decision_manifest.json`
- `data/rail/rail_timing_source_request_packet.csv`
- `data/rail/rail_fetch_readiness_packet.csv`
- `data/rail/rail_evidence_priority_packet.csv`
- `data/rail/rail_transit_stress_profile_packet.csv`
- `data/rail/rail_bounded_treatment_audit.json`
- `data/parameters/rail_evidence_review_packet.csv`
- `data/parameters/rail_service_evidence.csv`
- `data/parameters/rail_assumptions.csv`
- `data/parameters/rail_station_bindings.csv`

## Sub-Agent Wave

Read-only GPT-5.5 xhigh agents were used in the Phase 4 Wave 1 pattern:

- GTFS/timetable evidence explorer
- rail capacity and availability explorer
- adversarial rail overclaim reviewer

Accepted synthesis:

- KTDB GTFS is a realistic official acquisition path, but the current
  repository has only KTDB metadata/raw HTML. It does not have
  `data/rail/pilot_gtfs.zip` or
  `data/rail/pilot_gtfs_validator_report.json`.
- data.go.kr timetable and Seoul shortest-path APIs are plausible timing
  acquisition paths, but `DATA_GO_KR_KEY` is absent and no reviewed raw/cache
  payloads are present.
- Static timetable CSV evidence should be deferred or excluded unless a
  reviewed source CSV, explicit mapping, and normalization manifest are
  supplied.
- Metro9 capacity context supports a sensitivity/proxy boundary only in the
  current state. It must not be used as source-backed emergency capacity.
- Rail availability is scenario-only in the current state. The current stress
  profile and bounded-treatment audit do not create operational or emergency
  rail availability evidence.
- A completed non-formal action ledger should remain reviewer-owned and must
  not be generated autonomously as acceptance, publication, or rail evidence.

## Files Edited

- `src/realworld/pilot_experiments.py`
- `tests/test_realworld_pilot_experiments.py`
- `plan.md`
- `docs/recovery/agent_ledgers/phase4_rail_evidence_wave1_synthesis_and_phase8_guard_20260603.md`

## Guard Update

The Phase 8 preflight now treats a rail source-decision manifest as still
blocking non-sample evidence runs when any of these support flags remain false:

- `publication_ready`
- `can_mark_complete`
- `can_support_rail_evidence_gate`
- `can_support_acceptance_gate`

It also blocks when
`rail_service_evidence_gate_closure_candidate_count` is zero. This prevents a
completed non-formal rail source-decision ledger from bypassing rail evidence
and publication/final/formal gates.

## Verification

Commands run:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\pilot_experiments.py tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py
```

Observed result: both commands passed. The pilot experiment test suite now
includes a fixture where every rail source-decision row is completed
non-formally, but all support flags remain false; that fixture blocks
non-sample profile execution.

## Gate Decision

This closes only the overclaim guard gap identified by the Phase 4 Wave 1
review. It does not create rail timing evidence, GTFS validation, rail-service
calibration, emergency rail availability evidence, publication readiness,
final-study readiness, or formal acceptance.
