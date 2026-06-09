# Rail Transit Stress Profile Packet

Rail/transit stress-profile review packet only; scenario and sensitivity coverage documentation, not rail-service calibration, not emergency rail availability evidence, not operational service planning, not publication readiness, not final-study readiness, and not formal acceptance. It can document stress coverage but cannot close rail evidence, parameter, validation, publication, final-study, or formal acceptance gates.

## Verdict

- Publication ready: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- Can support publication gate: `false`
- Can support final-study gate: `false`
- Can support rail evidence gate: `false`
- Can support acceptance gate: `false`
- Formal acceptance evidence: `false`
- Stress-profile rows populated for coverage taxonomy only: `true`
- Rows: 6

## Stress Profiles

| Profile | Class | Treatment | Runtime Hook | Artifact | Status |
| --- | --- | --- | --- | --- | --- |
| rail_normal_service_assumption | normal_service_assumption | documented_assumption_proxy | fixed_headway_rail_assumption | data/parameters/rail_service_evidence.csv#songpa_public_demo_rail_proxy_v1 | assumption_proxy_not_accepted |
| rail_increased_headway_stress | increased_headway | scenario_only | policy_multiplier | data/scenarios/policy_alternatives.csv#rail_delay_or_partial_unavailability | scenario_stress_not_availability_evidence |
| rail_partial_capacity_reduction_stress | partial_capacity_reduction | sensitivity_only | policy_multiplier | data/scenarios/policy_alternatives.csv#rail_delay_or_partial_unavailability | sensitivity_only_not_capacity_evidence |
| rail_access_egress_road_degradation | rail_access_egress_degradation | scenario_only | road_connector_degradation | data/scenarios/disruption_scenarios.csv#songpa_rail_station_access | scenario_only_station_access_road_stress |
| rail_station_processing_delay_proxy | station_processing_delay_proxy | sensitivity_only_proxy | transfer_delay_parameter | data/scenarios/sensitivity_design.csv#transfer_fixed_delay;transfer_per_passenger_delay | proxy_only_not_station_processing_evidence |
| rail_partial_unavailability_or_delay | partial_unavailability_or_delay | scenario_only | policy_multiplier | data/scenarios/policy_alternatives.csv#rail_delay_or_partial_unavailability | scenario_stress_not_disruption_evidence |

## Boundary

- This packet documents stress coverage only.
- It does not certify rail timing, capacity, availability, dispatch, or operational service plans.
- Source-backed rail evidence and reviewer decisions are still required before release-scope rail claims.
