# Rail Source Decision Packet

Rail source-decision packet only; not rail timing evidence, not GTFS validation, not rail-service calibration, not emergency rail availability evidence, not sensitivity-only rail approval, and not rail evidence gate closure, not publication gate evidence, not study-closeout evidence, and not a formal decision record. It cannot create data/parameters/rail_service_evidence.csv.

## Verdict

- Publication gate supported: `false`
- Study-closeout gate supported: `false`
- Can mark complete: `false`
- Can support publication gate: `false`
- Can support study-closeout gate: `false`
- Can support rail evidence gate: `false`
- Can support acceptance gate: `false`
- Formal acceptance evidence: `false`
- Completed action ledger is acceptance: `false`
- Proxy/scaffold rail-service artifact present for inspection: `true`
- Source-backed rail-service evidence approved: `false`
- Artifact presence is not rail evidence acceptance or gate closure.
- Decision rows: 6
- Blocking decisions: 3
- Human-review decisions: 3
- Timing-source decisions: 4
- Completed non-formal source decisions: 0
- Action decision status counts: `{'pending_action_decision': 6}`
- Acquisition / exclusion / sensitivity-only / scenario-only decisions: 0 / 0 / 0 / 0

## Decision Rows

| Request | Fields | Status | Source | Cache | Options | Required Action |
| --- | --- | --- | --- | --- | --- | --- |
| rail_shortest_path_travel_time_request | travel_time | blocked_missing_rail_source_decision | data.go.kr Seoul Metro shortest-path API; https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do | absent: data/rail/pilot_rail_shortest_path_cache.csv; raw absent: data/rail/pilot_rail_shortest_path_raw.json | provide_reviewed_cached_api_payload; run_reviewed_live_api_fetch_and_cache_raw_payload; use_reviewed_gtfs_or_alternate_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_release_scope_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from study-closeout interpretation. |
| rail_static_gtfs_timing_request | headway;travel_time | blocked_missing_rail_source_decision | KTDB public transport GTFS dataset candidate; https://www.ktdb.go.kr/www/selectBbsNttView.do?bbsNo=2&key=45&nttNo=3785; https://www.ktdb.go.kr/www/selectPbldataChargerWebList.do?key=12&searchClStepCode=106 | absent: data/rail/pilot_gtfs.zip; data/rail/pilot_gtfs_validator_report.json; raw present: data/rail/ktdb_gtfs_source_extract.csv; data/rail/ktdb_gtfs_notice_raw.html; data/rail/ktdb_gtfs_dataset_list_raw.html | provide_reviewed_static_gtfs_feed; pair_reviewed_timetable_headway_with_shortest_path_travel_time; use_other_reviewed_transit_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_release_scope_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from study-closeout interpretation. |
| rail_timetable_headway_request | headway | blocked_missing_rail_source_decision | data.go.kr Seoul Subway train schedule API; https://www.data.go.kr/en/data/15143847/openapi.do | absent: data/rail/pilot_rail_timetable_api_cache.csv; raw absent: data/rail/pilot_rail_timetable_api_raw.json | provide_reviewed_cached_api_payload; run_reviewed_live_api_fetch_and_cache_raw_payload; use_reviewed_gtfs_or_alternate_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_release_scope_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from study-closeout interpretation. |
| rail_availability_scenario_request | availability;delay;partial_unavailability | needs_human_review_rail_source_decision | Rail delay, unavailability, and station-access scenario evidence; data/scenarios/disruption_scenarios.csv; docs/rail_evidence.md | present: data/scenarios/disruption_scenarios.csv | replace_with_public_disruption_or_incident_source; record_scenario_only_availability_scope; retain_availability_as_sensitivity_only; exclude_availability_dependent_release_scope_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from study-closeout interpretation. |
| rail_capacity_treatment_request | capacity | needs_human_review_rail_source_decision | Line capacity source context or explicit sensitivity-only treatment; https://www.metro9.co.kr/eng/sub03_02_01.do; data/parameters/rail_assumptions.csv | present: data/parameters/rail_assumptions.csv; data/rail/metro9_capacity_source_extract.csv; raw present: data/rail/metro9_capacity_source_raw.html | replace_with_operator_or_literature_capacity_source; retain_capacity_as_sensitivity_only_with_bounds; exclude_capacity_dependent_release_scope_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from study-closeout interpretation. |
| rail_static_timetable_csv_headway_request | headway | needs_human_review_ready_rail_source_decision | Seoul Open Data Plaza Seoul Metro train timetable file; https://data.seoul.go.kr/dataList/OA-22522/F/1/datasetView.do | present: data/rail/pilot_rail_static_timetable_cache.csv; raw present: data/rail/pilot_rail_timetable_static_source.csv; data/rail/pilot_rail_static_timetable_cache_manifest.json | provide_reviewed_static_timetable_csv_and_mapping; pair_reviewed_static_timetable_headway_with_shortest_path_travel_time; use_reviewed_gtfs_or_alternate_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_release_scope_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from study-closeout interpretation. |

## Boundary

- This packet is a reviewer worksheet, not a formal decision record.
- Action-ledger fields are non-formal source-review metadata and do not by themselves close rail evidence, parameter, provenance, publication, study-closeout, or formal decision gates.
- Source-backed acquisition action rows are incomplete unless every listed local source/cache/raw artifact exists and matches the supplied SHA256.
- It does not fetch data, derive `rail_service_evidence.csv`, accept GTFS, or certify rail service availability.
- Keep rail evidence claims blocked until source-backed changes or formal acceptance exist.
