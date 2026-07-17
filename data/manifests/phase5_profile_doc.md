# Demand, Fleet, And Behavior Profiles

Phase 5 demand/fleet/behavior profile packet only; bounded scenario inputs for decision-support simulation, not calibrated OD demand, not an agency fleet roster, not observed no-show behavior, not an operational transport plan, not a public-agency forecast, not publication readiness, not final-study readiness, and not formal acceptance.

## Verdict

- Publication ready: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- Row counts: `{'demand': 2, 'fleet': 6, 'behavior': 6}`
- Profile IDs: `{'demand': ['config_default_demand', 'pilot_default_demand'], 'fleet': ['config_default_fleet', 'pilot_default_fleet'], 'behavior': ['pilot_default_behavior']}`

## Demand Profiles

- `pilot_default_demand` origin `A`: 1000 pax, distribution `lognormal_sample_fixture`, evidence `bounded_scenario_assumption_not_calibration`.
- `config_default_demand` origin `A`: 1000 pax, distribution `lognormal`, evidence `review_required_scenario_assumption`.

## Fleet Profiles

- `pilot_default_fleet` role `direct_bus`: fleet 23, capacity 45, dispatch 5.0 min, turnaround 8.0 min.
- `pilot_default_fleet` role `feeder_shuttle`: fleet 23, capacity 45, dispatch 5.0 min, turnaround 8.0 min.
- `pilot_default_fleet` role `last_mile`: fleet 23, capacity 45, dispatch 5.0 min, turnaround 8.0 min.
- `config_default_fleet` role `direct_bus`: fleet 23, capacity 45, dispatch 5.0 min, turnaround 5.0 min.
- `config_default_fleet` role `feeder_shuttle`: fleet 23, capacity 45, dispatch 5.0 min, turnaround 5.0 min.
- `config_default_fleet` role `last_mile`: fleet 23, capacity 45, dispatch 5.0 min, turnaround 5.0 min.

## Behavior Profiles

- `concentrated_arrival`: `represented_by_lognormal_sigma_sensitivity`; denominator `total_scenario_demand`.
- `staggered_arrival`: `represented_by_policy_alternative`; denominator `total_scenario_demand`.
- `heavy_tailed_lateness`: `represented_by_lognormal_sigma_sensitivity`; denominator `total_scenario_demand`.
- `partial_non_arrival`: `not_implemented_contract_pending`; denominator `not separated; all passengers are instantiated and non-completion is metric censoring`.
- `boarding_delay`: `represented_by_transfer_delay_sensitivity`; denominator `total_scenario_demand`.
- `volume_stress`: `represented_by_sensitivity_design`; denominator `total_scenario_demand`.

## Remaining Blockers

- demand profiles are not calibrated OD demand
- fleet profiles are not agency fleet rosters or operating timetables
- partial non-arrival semantics are not implemented in the scenario engine
- formal parameter acceptance remains absent
