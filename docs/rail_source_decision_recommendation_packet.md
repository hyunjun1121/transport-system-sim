# Rail Source Decision Recommendation Packet

This packet is reviewer guidance only. It is not an action ledger, not rail timing evidence, not GTFS validation, not rail-service calibration, not emergency rail availability evidence, not publication readiness, not final-study readiness, and not formal acceptance.

- Row count: 6
- Blocked source-artifact rows: 3
- Reviewer-owned rows: 6
- Action ledger created: false
- Rail source decision recorded: false
- Can support rail evidence gate: false
- Can support acceptance gate: false

## Recommendations

| request_id | recommended_treatment | reviewer_action_prompt | recommended_reviewer_choice | fallback_reviewer_choice | reason |
|---|---|---|---|---|---|
| rail_shortest_path_travel_time_request | key_or_cache_gated_timing_acquisition | Provide retained API cache/raw payload evidence, run a reviewed live fetch, or explicitly bound/exclude timing-dependent claims. | provide_reviewed_cached_api_payload | retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_final_claims | API-backed timing remains blocked until a DATA_GO_KR_KEY live fetch or reviewed cached payload is retained. |
| rail_timetable_headway_request | key_or_cache_gated_timing_acquisition | Provide retained API cache/raw payload evidence, run a reviewed live fetch, or explicitly bound/exclude timing-dependent claims. | provide_reviewed_cached_api_payload | retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_final_claims | API-backed timing remains blocked until a DATA_GO_KR_KEY live fetch or reviewed cached payload is retained. |
| rail_static_gtfs_timing_request | source_backed_acquisition_candidate | Retain and review the GTFS feed and same-feed Validator report, or explicitly keep/exclude timing-dependent claims. | provide_reviewed_static_gtfs_feed | retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_final_claims | Static GTFS can support timing only after the retained feed and same-feed Validator report are reviewed and hashable. |
| rail_static_timetable_csv_headway_request | review_static_timetable_headway_cache | Review the retained timetable CSV, explicit mapping, normalization manifest, filters, and station binding. Pair the derived headway with travel-time evidence before using timing-dependent claims. | provide_reviewed_static_timetable_csv_and_mapping | use_reviewed_gtfs_or_alternate_timing_source; exclude_timing_dependent_final_claims | A static timetable cache is present for headway review, but it does not close travel-time evidence or rail-service calibration by itself. |
| rail_availability_scenario_request | scenario_only_now | Record reviewed scenario-only availability scope, or replace it with retained public disruption/incident evidence. | record_scenario_only_availability_scope | replace_with_public_disruption_or_incident_source; exclude_availability_dependent_final_claims | Current availability treatment is a stress scenario and should not be framed as observed emergency service availability. |
| rail_capacity_treatment_request | sensitivity_only_now | Record reviewed sensitivity-only capacity bounds and excluded claim scope, or replace the proxy with source-backed capacity evidence. | retain_capacity_as_sensitivity_only_with_bounds | replace_with_operator_or_literature_capacity_source; exclude_capacity_dependent_final_claims | Cached capacity context is not enough to treat rail capacity as source-backed calibration. |

## Required Boundary

- Do not copy these recommendations into an action ledger without human reviewer ownership.
- Do not treat source acquisition recommendations as retained local artifacts.
- Do not treat sensitivity-only or scenario-only recommendations as source-backed calibration.
- Keep completed source-decision action ledgers separate from this packet.
