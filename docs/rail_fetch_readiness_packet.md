# Rail Fetch Readiness Packet

Rail fetch-readiness packet only; not rail timing evidence, not GTFS validation, not rail-service calibration, and not operational rail availability evidence. This packet cannot close rail evidence or provenance gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Request rows: 5
- Blocking requests: 3
- Status counts: `{'blocked_missing_data_go_kr_key': 2, 'blocked_missing_reviewed_gtfs_file': 1, 'needs_human_review_availability_scenario': 1, 'needs_human_review_capacity_treatment': 1}`

## Readiness Rows

| Request | Source Type | Status | Cache | Required Action |
| --- | --- | --- | --- | --- |
| rail_timetable_headway_request | public_api_key_required | blocked_missing_data_go_kr_key | absent | provide DATA_GO_KR_KEY or a reviewed cached API payload before derivation |
| rail_shortest_path_travel_time_request | public_api_key_required | blocked_missing_data_go_kr_key | absent | provide DATA_GO_KR_KEY or a reviewed cached API payload before derivation |
| rail_static_gtfs_timing_request | reviewed_static_gtfs_file_required | blocked_missing_reviewed_gtfs_file | absent | provide a reviewed GTFS zip or directory before derivation |
| rail_capacity_treatment_request | operator_or_literature_or_sensitivity_decision | needs_human_review_capacity_treatment | present | accept sensitivity-only capacity bounds or replace them with source-backed capacity evidence |
| rail_availability_scenario_request | scenario_or_public_disruption_source_required | needs_human_review_availability_scenario | present | accept scenario-only rail availability bounds or replace them with source-backed disruption evidence |

## Required Reviewer Actions

- Provide a reviewed API key, GTFS file, or explicit assumption decision where rows are blocked.
- Preserve raw payloads and cache files before deriving rail timing evidence.
- Re-run rail evidence and final-study readiness audits after evidence changes.
- Do not create formal acceptance artifacts from this readiness packet alone.
