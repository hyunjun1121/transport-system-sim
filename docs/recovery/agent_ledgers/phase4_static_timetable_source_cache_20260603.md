# Phase 4 Static Timetable Source Cache Ledger - 2026-06-03

## Scope

This ledger records a Phase 4 rail-source evidence-acquisition step. It retained
an official Seoul static timetable CSV source candidate and normalized a
headway-only cache for reviewer inspection.

This ledger is not rail-service evidence, not a rail timing acceptance record,
not publication readiness, not final-study readiness, and not formal acceptance.

## Artifacts

- Retained static source: `data/rail/pilot_rail_timetable_static_source.csv`
- Normalized cache: `data/rail/pilot_rail_timetable_cache.csv`
- Normalization manifest: `data/rail/pilot_rail_timetable_cache_manifest.json`
- Updated readiness packet: `data/rail/rail_fetch_readiness_packet.csv`
- Updated priority packet: `data/rail/rail_evidence_priority_packet.csv`
- Updated source-decision packet: `data/rail/rail_source_decision_packet.csv`
- Updated recommendation packet: `data/rail/rail_source_decision_recommendation_packet.csv`
- Updated stress-profile packet: `data/rail/rail_transit_stress_profile_packet.csv`
- Updated bounded-treatment audit: `data/rail/rail_bounded_treatment_audit.json`

## Source And Hash Evidence

- Source page inspected during this phase:
  `https://data.seoul.go.kr/dataList/OA-22522/F/1/datasetView.do`
- Static source SHA256:
  `46B6D9E2C2E1E23632FA72208A3CA5DC6AEBA9013C403EE6F52747FEC2B9A9E2`
- Normalized cache SHA256:
  `9785314A46C9AA5393040448FF2917591E5158F759C57FF93C6FCCCE05F091E8`
- Static source header:
  `"ROWNUM","LINE","SI_ID","STATION_NM","WEEKTAG","INOUTTAG","GUBHANG","TRAIN_NO","STT","EDT","ST_STT_NM","ED_STT_NM"`
- Normalized cache rows: 241
- Manifest scope:
  `static timetable normalization cache only; not rail evidence, not operational service validation, and not formal acceptance`

## Normalization Selection

- Access station: Olympic Park, station code `4136`
- Egress station: none in this cache
- Filters: `LINE=9`, `WEEKTAG=DAY`, `INOUTTAG=UP`
- Source columns:
  `TRAIN_NO`, `STATION_NM`, `SI_ID`, `STT`, `EDT`, `INOUTTAG`, `WEEKTAG`

The source inspection found no same `TRAIN_NO` sequence connecting the selected
Olympic Park and Jamsil records in the retained static file. Therefore this
cache may support a headway-review path only. It must be paired with
shortest-path, GTFS, operator, or other reviewed travel-time evidence before any
rail travel-time or rail-service calibration claim.

## Commands Run

```powershell
.\.venv\Scripts\python scripts\normalize_rail_timetable_cache.py --input data\rail\pilot_rail_timetable_static_source.csv --output data\rail\pilot_rail_timetable_cache.csv --manifest-output data\rail\pilot_rail_timetable_cache_manifest.json --trip-id-column TRAIN_NO --station-name-column STATION_NM --station-code-column SI_ID --arrival-time-column STT --departure-time-column EDT --direction-column INOUTTAG --service-day-column WEEKTAG --access-station-name 올림픽공원 --access-station-code 4136 --filter LINE=9 --filter WEEKTAG=DAY --filter INOUTTAG=UP
.\.venv\Scripts\python scripts\write_rail_fetch_readiness_packet.py
.\.venv\Scripts\python scripts\write_rail_evidence_priority_packet.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python scripts\write_rail_source_decision_action_ledger_template.py
.\.venv\Scripts\python scripts\write_rail_source_decision_recommendation_packet.py
.\.venv\Scripts\python scripts\write_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python scripts\audit_rail_bounded_treatments.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
.\.venv\Scripts\python scripts\run_acceptance_audit.py
```

## Tests Run

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_timetable_static.py
.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence_priority_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_action_ledger_template.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_recommendation_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python tests\test_realworld_acceptance_orchestration.py
.\.venv\Scripts\python tests\test_realworld_formal_acceptance_pre_review.py
.\.venv\Scripts\python tests\test_realworld_goal_completion_audit.py
```

All listed tests passed in the current worktree.

## Current Status After This Step

- `rail_fetch_readiness_manifest.json` now has `blocking_request_count=3`.
- `rail_evidence_priority_manifest.json` now has `blocking_priority_count=3`.
- `rail_source_decision_manifest.json` now has `blocking_decision_count=3`
  and `human_review_decision_count=3`.
- `publication_readiness_audit.json` remains `publication_ready=false`.
- `audit_final_study_readiness.py` remains `final_study_ready=false`.
- `audit_plan_artifacts.py` remains
  `verdict=executable_quasi_real_scaffold_not_final_calibrated_study`.

## Remaining Blockers

- Reviewed shortest-path, GTFS, operator, or equivalent rail travel-time
  evidence is still absent.
- Reviewed rail capacity and availability treatments are still pending.
- Formal rail evidence, parameter evidence, publication, final-study, and
  acceptance gates remain blocked.
