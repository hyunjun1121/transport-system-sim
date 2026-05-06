# Parameter Source Readiness Packet

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


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

| Request | Group | Status | Source Cache | Target | Required Action |
| --- | --- | --- | --- | --- | --- |
| demand_arrival_horizon_censoring_source_request | demand_time_censoring | needs_human_review_demand_scenario | present | present | review demand scale, arrival process, time horizon, and censoring penalty rationale |
| fleet_vehicle_capacity_source_request | fleet | needs_human_review_fleet_package | present | present | review vehicle capacities and finite fleet counts as source-backed or scenario-bounded |
| dispatch_turnaround_source_request | fleet | needs_human_review_dispatch_policy | present | present | review dispatch interval and turnaround treatment as policy scenario assumptions |
| transfer_delay_source_request | transfer | blocked_missing_transfer_source | present | present | supply transfer path, walking/crowding, field-observation, or literature evidence |
| disruption_scenario_assumption_source_request | disruption | needs_human_review_disruption_parameter_scenario | present | present | review scenario-only disruption rules or replace them with hazard/incident evidence |
| background_traffic_bpr_calibration_source_request | road | needs_human_review_traffic_bpr_with_benchmark_snapshot | present | present | review route benchmark, traffic-volume window, and BPR default treatment |

## Required Reviewer Actions

- Supply reviewed sources or explicit bounded-scenario decisions for every row.
- Update parameter tables only after source review.
- Use formal weak-parameter acceptance separately when assumptions remain weak.
- Do not create formal acceptance artifacts from this readiness packet alone.
