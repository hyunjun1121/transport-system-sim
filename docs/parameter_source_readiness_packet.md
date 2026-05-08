# Parameter Source Readiness Packet

Parameter source-readiness packet only; not source evidence, not accepted parameter calibration, not weak-parameter acceptance, not evidence-gate closure, and not publication-readiness approval. This packet cannot close parameter evidence or formal acceptance gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Request rows: 6
- Weak parameters covered: 20
- Blocking requests: 1
- Human-review requests: 5
- Status counts: `{'blocked_missing_transfer_source': 1, 'needs_human_review_demand_scenario': 1, 'needs_human_review_dispatch_policy': 1, 'needs_human_review_disruption_parameter_scenario': 1, 'needs_human_review_fleet_package': 1, 'needs_human_review_traffic_bpr_with_benchmark_snapshot': 1}`

## Readiness Rows

| Request | Source | Group | Status | Source Cache | Target | Required Input | Required Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| demand_arrival_horizon_censoring_source_request | Reviewed demand planning scenario, arrival-process evidence, exercise design, or literature values<br>data/parameters/parameter_sources.csv; data/scenarios/sensitivity_design.csv | demand_time_censoring | needs_human_review_demand_scenario | present | present | reviewed passenger-volume basis, arrival process or assembly window, simulation horizon, and KPI penalty rationale or explicit sensitivity-only treatment | review demand scale, arrival process, time horizon, and censoring penalty rationale |
| fleet_vehicle_capacity_source_request | Reviewed agency fleet roster, vehicle-capacity source, exercise fleet package, or transport-planning literature<br>data/parameters/fleet_assumptions.csv | fleet | needs_human_review_fleet_package | present | present | reviewed vehicle capacities, feasible load factors, available fleet counts by role, or explicit scenario-fleet assumption | review vehicle capacities and finite fleet counts as source-backed or scenario-bounded |
| dispatch_turnaround_source_request | Reviewed dispatch schedule, staging rule, depot/layover basis, or policy scenario rule<br>data/parameters/fleet_assumptions.csv; data/scenarios/policy_alternatives.csv | fleet | needs_human_review_dispatch_policy | present | present | reviewed dispatch interval, turnaround or layover time, first departure anchor, or explicit policy-sensitivity treatment | review dispatch interval and turnaround treatment as policy scenario assumptions |
| transfer_delay_source_request | Reviewed station-transfer geometry, walking/crowding evidence, observed transfer range, or pedestrian-flow literature<br>data/parameters/parameter_sources.csv; data/regions/pilot_region.yaml | transfer | blocked_missing_transfer_source | present | present | reviewed transfer path length, walking speed, vertical-circulation or crowding assumptions, and per-passenger delay treatment | supply transfer path, walking/crowding, field-observation, or literature evidence |
| disruption_scenario_assumption_source_request | Reviewed hazard, incident, exposure, accessibility-loss, or scenario-rule source<br>data/scenarios/disruption_scenarios.csv; data/validation/accessibility_loss.csv | disruption | needs_human_review_disruption_parameter_scenario | present | present | public hazard or incident data, reviewed scenario-family rules, capacity-loss literature, or explicit sensitivity-only treatment | review scenario-only disruption rules or replace them with hazard/incident evidence |
| background_traffic_bpr_calibration_source_request | Reviewed route-time benchmark, observed traffic counts/speeds, or BPR calibration literature<br>data/validation/external_route_benchmarks.csv; data/validation/external_route_benchmarks_osrm.csv; Bureau of Public Roads 1964 Traffic Assignment Manual | road | needs_human_review_traffic_bpr_with_benchmark_snapshot | present | present | reviewed route-time benchmarks, traffic counts or speed profiles, rolling-window justification, and local BPR calibration decision | review route benchmark, traffic-volume window, and BPR default treatment |

## Required Reviewer Actions

- Supply reviewed sources or explicit bounded-scenario decisions for every row.
- Update parameter tables only after source review.
- Use formal weak-parameter acceptance separately when assumptions remain weak.
- Do not create formal acceptance artifacts from this readiness packet alone.
