# Rail Evidence Priority Packet

This packet prioritizes rail evidence closure paths. It does not fetch API data, provide GTFS files, derive rail_service_evidence.csv, or close rail, parameter, provenance, validation, or final-study gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Priority rows: 6
- Blocking priorities: 3
- Human-review priorities: 2
- Timing closure candidates: 1
- Status counts: `{'blocked_missing_data_go_kr_key': 2, 'blocked_missing_reviewed_gtfs_file': 1, 'needs_human_review_availability_scenario': 1, 'needs_human_review_capacity_treatment': 1, 'prerequisite_ready_not_timing_evidence': 1}`

## Priority Rows

| Priority | Fields | Status | Source | Cache | Timing Closure | Required Action |
| --- | --- | --- | --- | --- | --- | --- |
| rail_shortest_path_travel_time_request | travel_time | blocked_missing_data_go_kr_key | data.go.kr Seoul Metro shortest-path API | absent: data/rail/pilot_rail_shortest_path_cache.csv; raw: data/rail/pilot_rail_shortest_path_raw.json |  | provide DATA_GO_KR_KEY or a reviewed cached API payload before derivation |
| rail_static_gtfs_timing_request | headway;travel_time | blocked_missing_reviewed_gtfs_file | KTDB public transport GTFS dataset candidate | absent: data/rail/pilot_gtfs.zip; raw: data/rail/ktdb_gtfs_source_extract.csv; data/rail/ktdb_gtfs_notice_raw.html; data/rail/ktdb_gtfs_dataset_list_raw.html | headway;travel_time | provide a reviewed GTFS zip or directory before derivation |
| rail_timetable_headway_request | headway | blocked_missing_data_go_kr_key | data.go.kr Seoul Subway train schedule API | absent: data/rail/pilot_rail_timetable_cache.csv; raw: data/rail/pilot_rail_timetable_raw.json |  | provide DATA_GO_KR_KEY or a reviewed cached API payload before derivation |
| rail_availability_scenario_request | availability;delay;partial_unavailability | needs_human_review_availability_scenario | Rail delay, unavailability, and station-access scenario evidence | present: data/scenarios/disruption_scenarios.csv |  | accept scenario-only rail availability bounds or replace them with source-backed disruption evidence |
| rail_capacity_treatment_request | capacity | needs_human_review_capacity_treatment | Line capacity source context or explicit sensitivity-only treatment | present: data/parameters/rail_assumptions.csv; data/rail/metro9_capacity_source_extract.csv; raw: data/rail/metro9_capacity_source_raw.html |  | accept sensitivity-only capacity bounds or replace them with source-backed capacity evidence |
| station_binding_prerequisite | station_binding | prerequisite_ready_not_timing_evidence | cached official station-name binding extract | present: data/parameters/rail_station_bindings.csv; raw: data/rail/pilot_station_binding_cache.csv |  | keep station binding separate from timing, capacity, and availability evidence |

## Boundary

- This packet is rail-evidence prioritization support only.
- It does not fetch live data, validate GTFS, derive rail service evidence, or certify rail availability.
- It cannot create or replace `data/parameters/rail_service_evidence.csv`.
