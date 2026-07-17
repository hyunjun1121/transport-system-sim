# Parameter Evidence Priority Packet

This packet prioritizes existing parameter evidence gaps. It does not create accepted parameter values, does not certify source sufficiency, and does not close parameter, validation, provenance, or final-study gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Priority rows: 7
- Weak parameters: 23
- Blocking priority rows: 1
- Human-review priority rows: 6
- Priority status counts: `{'blocked_missing_parameter_source': 1, 'needs_human_review_high_priority_parameter_source': 2, 'needs_human_review_medium_priority_parameter_source': 4}`

## Priority Rows

| Request | Group | Status | High | Medium | Required Action |
| --- | --- | --- | --- | --- | --- |
| rail_service_parameter_source_request | rail | blocked_missing_parameter_source | 3 | 0 | review rail timing/source-decision packets and supply timing cache, GTFS, or explicit sensitivity treatment |
| disruption_scenario_assumption_source_request | disruption | needs_human_review_high_priority_parameter_source | 4 | 0 | review scenario-only disruption rules or replace them with hazard/incident evidence |
| background_traffic_bpr_calibration_source_request | road | needs_human_review_high_priority_parameter_source | 2 | 0 | review route benchmark, traffic-volume window, and BPR default treatment |
| demand_arrival_horizon_censoring_source_request | demand_time_censoring | needs_human_review_medium_priority_parameter_source | 0 | 5 | review demand scale, arrival process, time horizon, and censoring penalty rationale |
| fleet_vehicle_capacity_source_request | fleet | needs_human_review_medium_priority_parameter_source | 0 | 5 | review vehicle capacities and finite fleet counts as source-backed or scenario-bounded |
| dispatch_turnaround_source_request | fleet | needs_human_review_medium_priority_parameter_source | 0 | 2 | review dispatch interval and turnaround treatment as policy scenario assumptions |
| transfer_delay_source_request | transfer | needs_human_review_medium_priority_parameter_source | 0 | 2 | review transfer geometry or pedestrian-flow evidence before final transfer claims |

## Boundary

- This packet is parameter-evidence prioritization support only.
- It does not create source evidence, calibrated values, or weak-parameter acceptance.
- It cannot create or replace `data/parameters/parameter_acceptance.csv`.
