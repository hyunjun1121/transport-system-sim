# Rail Fetch Readiness Packet

Rail fetch-readiness packet only; not rail timing evidence, not GTFS validation, not rail-service calibration, and not operational rail availability evidence. This packet cannot close rail evidence or provenance gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Request rows: 5
- Blocking requests: 3
- Status counts: `{'blocked_missing_data_go_kr_key': 2, 'blocked_missing_reviewed_gtfs_file': 1, 'needs_human_review_availability_scenario': 1, 'needs_human_review_capacity_treatment': 1}`

## Readiness Rows

| Request | Source | Source Type | Status | Cache | Required Input | Required Action |
| --- | --- | --- | --- | --- | --- | --- |
| rail_timetable_headway_request | data.go.kr Seoul Subway train schedule API<br>https://www.data.go.kr/en/data/15143847/openapi.do | public_api_key_required | blocked_missing_data_go_kr_key | absent | DATA_GO_KR_KEY; reviewed line, direction, service-day, station-code, and service-window choices | provide DATA_GO_KR_KEY or a reviewed cached API payload before derivation |
| rail_shortest_path_travel_time_request | data.go.kr Seoul Metro shortest-path API<br>https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do | public_api_key_required | blocked_missing_data_go_kr_key | absent | DATA_GO_KR_KEY; reviewed station names, station codes, search datetime, and route type | provide DATA_GO_KR_KEY or a reviewed cached API payload before derivation |
| rail_static_gtfs_timing_request | KTDB public transport GTFS dataset candidate<br>https://www.ktdb.go.kr/www/selectPbldataChargerWebList.do?key=12&searchClStepCode=106; https://www.ktdb.go.kr/www/selectBbsNttView.do?bbsNo=2&key=45&nttNo=3772 | reviewed_static_gtfs_file_required | blocked_missing_reviewed_gtfs_file | absent | reviewed KTDB or equivalent GTFS zip or directory; access_stop_id; egress_stop_id; route_id; service window | provide a reviewed GTFS zip or directory before derivation |
| rail_capacity_treatment_request | Line capacity source or explicit sensitivity-only treatment<br>data/parameters/rail_assumptions.csv | operator_or_literature_or_sensitivity_decision | needs_human_review_capacity_treatment | present | reviewed train capacity source or explicit final sensitivity-only acceptance | accept sensitivity-only capacity bounds or replace them with source-backed capacity evidence |
| rail_availability_scenario_request | Rail delay, unavailability, and station-access scenario evidence<br>data/scenarios/disruption_scenarios.csv; docs/rail_evidence.md | scenario_or_public_disruption_source_required | needs_human_review_availability_scenario | present | reviewed scenario rules for rail delay, station access degradation, and partial service unavailability | accept scenario-only rail availability bounds or replace them with source-backed disruption evidence |

## Required Reviewer Actions

- Provide a reviewed API key, GTFS file, or explicit assumption decision where rows are blocked.
- Preserve raw payloads and cache files before deriving rail timing evidence.
- Re-run rail evidence and final-study readiness audits after evidence changes.
- Do not create formal acceptance artifacts from this readiness packet alone.
