# Rail Source Decision Packet

Rail source-decision packet only; not rail timing evidence, not GTFS validation, not rail-service calibration, not emergency rail availability evidence, not sensitivity-only rail acceptance, and not rail evidence gate closure. It cannot create data/parameters/rail_service_evidence.csv.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Rail-service evidence present: `true`
- Decision rows: 5
- Blocking decisions: 3
- Human-review decisions: 2
- Timing-source decisions: 3

## Decision Rows

| Request | Fields | Status | Options | Required Action |
| --- | --- | --- | --- | --- |
| rail_shortest_path_travel_time_request | travel_time | blocked_missing_rail_source_decision | provide_reviewed_cached_api_payload; run_reviewed_live_api_fetch_and_cache_raw_payload; use_reviewed_gtfs_or_alternate_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_final_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from final-study interpretation. |
| rail_static_gtfs_timing_request | headway;travel_time | blocked_missing_rail_source_decision | provide_reviewed_static_gtfs_feed; pair_reviewed_timetable_headway_with_shortest_path_travel_time; use_other_reviewed_transit_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_final_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from final-study interpretation. |
| rail_timetable_headway_request | headway | blocked_missing_rail_source_decision | provide_reviewed_cached_api_payload; run_reviewed_live_api_fetch_and_cache_raw_payload; use_reviewed_gtfs_or_alternate_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_final_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from final-study interpretation. |
| rail_availability_scenario_request | availability;delay;partial_unavailability | needs_human_review_rail_source_decision | replace_with_public_disruption_or_incident_source; accept_scenario_only_availability_with_scope; retain_availability_as_sensitivity_only; exclude_availability_dependent_final_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from final-study interpretation. |
| rail_capacity_treatment_request | capacity | needs_human_review_rail_source_decision | replace_with_operator_or_literature_capacity_source; retain_capacity_as_sensitivity_only_with_bounds; exclude_capacity_dependent_final_claims | Choose whether to provide source-backed rail evidence, retain the item as sensitivity-only or scenario-only within strict claim limits, or exclude the affected claim from final-study interpretation. |

## Boundary

- This packet is a reviewer worksheet, not a formal decision record.
- It does not fetch data, derive `rail_service_evidence.csv`, accept GTFS, or certify rail service availability.
- Keep rail evidence claims blocked until source-backed changes or formal acceptance exist.
