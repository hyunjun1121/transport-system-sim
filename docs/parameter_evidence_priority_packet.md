# Parameter Evidence Priority Packet

This packet prioritizes existing parameter evidence gaps. It does not create accepted parameter values, does not certify source sufficiency, and does not close parameter, validation, provenance, or study-closeout gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Priority rows: 7
- Weak parameters: 23
- Blocking priority rows: 0
- Human-review priority rows: 7
- Priority status counts: `{'needs_human_review_high_priority_parameter_source': 3, 'needs_human_review_medium_priority_parameter_source': 4}`

## Priority Rows

| Request | Group | Status | High | Medium | Required Action |
| --- | --- | --- | --- | --- | --- |
| disruption_scenario_assumption_source_request | disruption | needs_human_review_high_priority_parameter_source | 4 | 0 | review scenario-only disruption rules or replace them with hazard/incident evidence |
| rail_service_parameter_source_request | rail | needs_human_review_high_priority_parameter_source | 3 | 0 | review rail timing evidence and capacity treatment before release-scope rail parameter claims |
| background_traffic_bpr_calibration_source_request | road | needs_human_review_high_priority_parameter_source | 2 | 0 | review route benchmark, traffic-volume window, and BPR default treatment |
| demand_arrival_horizon_censoring_source_request | demand_time_censoring | needs_human_review_medium_priority_parameter_source | 0 | 5 | review demand scale, arrival process, time horizon, and censoring penalty rationale |
| fleet_vehicle_capacity_source_request | fleet | needs_human_review_medium_priority_parameter_source | 0 | 5 | review vehicle capacities and finite fleet counts as source-backed or scenario-bounded |
| dispatch_turnaround_source_request | fleet | needs_human_review_medium_priority_parameter_source | 0 | 2 | review dispatch interval and turnaround treatment as policy scenario assumptions |
| transfer_delay_source_request | transfer | needs_human_review_medium_priority_parameter_source | 0 | 2 | review transfer geometry or pedestrian-flow evidence before release-scope transfer claims |

## Boundary

- This packet is parameter-evidence prioritization support only.
- It does not create source evidence, calibrated values, or weak-parameter acceptance.
- It cannot create or replace `data/parameters/parameter_acceptance.csv`.
