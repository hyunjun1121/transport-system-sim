# Seed Stream Manifest

This seed-stream manifest documents current scenario-runner stochastic streams and deterministic dispatch components. It does not prove statistical power, accept CRN design, validate stochastic assumptions, or close final-study gates.

## Verdict

- Seed-stream manifest ready: `true`
- Acceptance ready: `false`
- Can mark complete: `false`
- Blocking checks: 0
- Run profile: `full_pilot`
- Seed count: 30

## Streams

| Stream | Seed Rule | Consumer | Shared Across Policies | Evidence | Review Note |
| --- | --- | --- | --- | --- | --- |
| demand_arrival_lateness | np.random.default_rng(seed) | sample_arrival_delays(..., rng=rng_arrival) | True | src/scenario.py; src/models.py | same scenario/seed rows across policies share the demand stream by construction |
| road_disruption_sampling | np.random.default_rng(seed + 10_000) | _sample_disruptions(..., rng_failure) | True | src/scenario.py; src/disruptions.py | same scenario/seed rows across policies share the disruption stream by construction |
| dispatch_and_fleet_ordering | not_applicable | plan_dispatches, FleetAvailability, rail headway, transfers, dynamic traffic | not_random | src/scenario.py; src/dispatch.py; src/fleet.py; src/rail.py; src/transfers.py; src/traffic.py | no current random tie-breaking stream is present; add a named stream if stochastic dispatch logic is introduced |

## Marker Checks

| Check | Status | Review Action |
| --- | --- | --- |
| arrival_rng_seed_rule | pass | Restore or document the demand-stream seed rule. |
| failure_rng_seed_rule | pass | Restore or document the disruption-stream seed rule. |
| arrival_rng_consumed_by_lognormal | pass | Review demand sampling implementation before CRN design signoff. |
| disruption_rng_consumed_by_edge_draws | pass | Review disruption sampling implementation before CRN design signoff. |
| dispatch_has_no_rng_marker | pass | Add a named dispatch stream before stochastic dispatch is introduced. |
| fleet_rail_transfer_traffic_have_no_rng_marker | pass | Add named streams before stochastic fleet, rail, transfer, or traffic logic is introduced. |

## Use

Use this manifest with `docs/crn_pairing_audit.md` and the paired delta statistics tables before any formal experiment decision review. If stochastic dispatch tie-breaking, random routing, or additional sampling is added, update this manifest before interpreting policy differences.
