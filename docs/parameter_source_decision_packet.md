# Parameter Source Decision Packet

Parameter source-decision packet only; not source evidence, not approved parameter fitting, not weak-parameter decision evidence, not parameter evidence gate closure, and not publication gate approval. It cannot create data/parameters/parameter_acceptance.csv.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Parameter acceptance present: `false`
- Decision rows: 7
- Weak parameters covered: 21
- Blocking decisions: 0
- Human-review decisions: 7

## Decision Rows

| Request | Group | Status | Options | Required Action |
| --- | --- | --- | --- | --- |
| background_traffic_bpr_calibration_source_request | road | needs_human_review_parameter_source_decision | replace_with_source_backed_parameter_values; retain_as_bounded_scenario_assumption; retain_as_sensitivity_only; exclude_from_release_scope_claims | Choose whether to replace with source-backed values, retain as a bounded scenario assumption, retain as sensitivity-only, or exclude the affected claim from release-scope interpretation. |
| demand_arrival_horizon_censoring_source_request | demand_time_censoring | needs_human_review_parameter_source_decision | replace_with_source_backed_parameter_values; retain_as_bounded_scenario_assumption; retain_as_sensitivity_only; exclude_from_release_scope_claims | Choose whether to replace with source-backed values, retain as a bounded scenario assumption, retain as sensitivity-only, or exclude the affected claim from release-scope interpretation. |
| dispatch_turnaround_source_request | fleet | needs_human_review_parameter_source_decision | replace_with_source_backed_parameter_values; retain_as_bounded_scenario_assumption; retain_as_sensitivity_only; exclude_from_release_scope_claims | Choose whether to replace with source-backed values, retain as a bounded scenario assumption, retain as sensitivity-only, or exclude the affected claim from release-scope interpretation. |
| disruption_scenario_assumption_source_request | disruption | needs_human_review_parameter_source_decision | replace_with_source_backed_parameter_values; retain_as_bounded_scenario_assumption; retain_as_sensitivity_only; exclude_from_release_scope_claims | Choose whether to replace with source-backed values, retain as a bounded scenario assumption, retain as sensitivity-only, or exclude the affected claim from release-scope interpretation. |
| fleet_vehicle_capacity_source_request | fleet | needs_human_review_parameter_source_decision | replace_with_source_backed_parameter_values; retain_as_bounded_scenario_assumption; retain_as_sensitivity_only; exclude_from_release_scope_claims | Choose whether to replace with source-backed values, retain as a bounded scenario assumption, retain as sensitivity-only, or exclude the affected claim from release-scope interpretation. |
| rail_service_parameter_source_request | rail | needs_human_review_parameter_source_decision | replace_with_source_backed_parameter_values; use_rail_timing_or_gtfs_source_decision_packet; retain_as_bounded_scenario_assumption; retain_as_sensitivity_only; exclude_from_release_scope_claims | Choose whether to replace with source-backed values, retain as a bounded scenario assumption, retain as sensitivity-only, or exclude the affected claim from release-scope interpretation. |
| transfer_delay_source_request | transfer | needs_human_review_parameter_source_decision | replace_with_source_backed_parameter_values; supply_transfer_layout_or_pedestrian_flow_source; retain_as_bounded_scenario_assumption; retain_as_sensitivity_only; exclude_from_release_scope_claims | Choose whether to replace with source-backed values, retain as a bounded scenario assumption, retain as sensitivity-only, or exclude the affected claim from release-scope interpretation. |

## Boundary

- This packet is a reviewer worksheet, not a formal decision record.
- It does not update parameter tables or accept weak assumptions.
- Keep release-scope parameter claims blocked until source-backed changes or formal weak-parameter decisions exist.
