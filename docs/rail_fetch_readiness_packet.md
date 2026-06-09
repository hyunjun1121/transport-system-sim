# Rail Fetch Review Packet

Rail fetch review packet only; not rail timing evidence, not GTFS validation, not rail-service calibration, and not operational rail availability evidence. This packet cannot close rail evidence or provenance gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Region IDs: `['songpa_public_demo']`
- Request rows: 6
- Blocking requests: 3
- Status counts: `{'blocked_missing_data_go_kr_key': 2, 'blocked_missing_reviewed_gtfs_file': 1, 'needs_human_review_availability_scenario': 1, 'needs_human_review_capacity_treatment': 1, 'ready_reviewed_static_timetable_cache_for_derivation_review': 1}`

## Review Rows

| Request | Source | Source Type | Status | Cache | Required Input | Required Action |
| --- | --- | --- | --- | --- | --- | --- |
| rail_timetable_headway_request | data.go.kr Seoul Subway train schedule API<br>https://www.data.go.kr/en/data/15143847/openapi.do | public_api_key_required | blocked_missing_data_go_kr_key | absent | DATA_GO_KR_KEY; reviewed line, direction, service-day, station-code, and service-window choices | provide DATA_GO_KR_KEY or a reviewed cached API payload before derivation |
| rail_static_timetable_csv_headway_request | Seoul Open Data Plaza Seoul Metro train timetable file<br>https://data.seoul.go.kr/dataList/OA-22522/F/1/datasetView.do | reviewed_static_timetable_csv_required | ready_reviewed_static_timetable_cache_for_derivation_review | present | reviewed static timetable CSV; explicit source-column mappings; reviewed line, direction, service-day, station-selector, and service-window choices; normalization manifest | review static timetable source, normalization manifest, and run the listed derive command |
| rail_shortest_path_travel_time_request | data.go.kr Seoul Metro shortest-path API<br>https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do | public_api_key_required | blocked_missing_data_go_kr_key | absent | DATA_GO_KR_KEY; reviewed station names, station codes, search datetime, and route type | provide DATA_GO_KR_KEY or a reviewed cached API payload before derivation |
| rail_static_gtfs_timing_request | KTDB public transport GTFS dataset candidate<br>https://www.ktdb.go.kr/www/selectBbsNttView.do?bbsNo=2&key=45&nttNo=3785; https://www.ktdb.go.kr/www/selectPbldataChargerWebList.do?key=12&searchClStepCode=106 | reviewed_static_gtfs_file_required | blocked_missing_reviewed_gtfs_file | absent | reviewed KTDB or equivalent GTFS zip or directory; access_stop_id; egress_stop_id; route_id; service window; reviewed GTFS Validator report | provide a reviewed GTFS zip or directory and validator report before derivation |
| rail_capacity_treatment_request | Line capacity source context or explicit sensitivity-only treatment<br>https://www.metro9.co.kr/eng/sub03_02_01.do; data/parameters/rail_assumptions.csv | operator_or_literature_or_sensitivity_decision | needs_human_review_capacity_treatment | present | review Metro9 capacity extract, source terms, and current rail assumptions; then record a source-backed capacity update or reviewer-scoped sensitivity-only treatment | record reviewer-scoped sensitivity-only capacity bounds or replace them with source-backed capacity evidence |
| rail_availability_scenario_request | Rail delay, unavailability, and station-access scenario evidence<br>data/scenarios/disruption_scenarios.csv; docs/rail_evidence.md | scenario_or_public_disruption_source_required | needs_human_review_availability_scenario | present | reviewed scenario rules for rail delay, station access degradation, and partial service unavailability | record reviewer-scoped scenario-only rail availability bounds or replace them with source-backed disruption evidence |

## Required Reviewer Actions

- Provide a reviewed API key, GTFS file, or explicit assumption decision where rows are blocked.
- Preserve raw payloads and cache files before deriving rail timing evidence.
- Re-run rail evidence and study-scope review audits after evidence changes.
- Capacity and availability bounded treatments are reviewer-scoped decisions, not formal acceptance.
- Do not create formal acceptance artifacts from this readiness packet alone.
