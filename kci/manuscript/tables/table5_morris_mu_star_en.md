**Table 5.** Morris global sensitivity: canonical-aggregation mean μ* ranking across all 14 parameters.

| Rank | Parameter ID | Canonical mean μ* | Blocks aggregated |
|---|---|---|---|
| 1 | `passenger_volume` | 44.5 | 28 |
| 2 | `direct_bus_fleet_size` | 27.4 | 28 |
| 3 | `dispatch_interval` | 20.8 | 28 |
| 4 | `turnaround_time` | 12.3 | 28 |
| 5 | `last_mile_fleet_size` | 10.2 | 28 |
| 6 | `rail_headway` | 6.26 | 28 |
| 7 | `feeder_fleet_size` | 4.27 | 28 |
| 8 | `rail_capacity` | 3.47 | 28 |
| 9 | `transfer_fixed_delay` | 3.10 | 28 |
| 10 | `passenger_arrival_variability` | 2.29 | 28 |
| 11 | `capacity_reduction_factor` | 1.73 | 28 |
| 12 | `road_background_traffic_multiplier` | 1.65 | 28 |
| 13 | `transfer_per_passenger_delay` | 0.475 | 28 |
| 14 | `last_mile_access_disruption_probability` | 0.265 | 28 |

*Note.* **Canonical aggregation rule** (`plan.md` §3.7 / §10). For each parameter, (1) compute mean μ* over `(policy_id × scenario_id)` blocks (2 × 2 = 4 blocks) for each `(parameter_id, metric)` pair, then (2) average over the seven metrics (`completion_rate`, `censored_count`, `penalized_makespan`, `p80_arrival_time`, `p95_arrival_time`, `total_service_minutes`, `passengers_per_total_service_minute`) to obtain the canonical mean μ*. Hence the aggregation block count = 7 metrics × 2 policies × 2 scenarios = 28 blocks per parameter. Source: `results/sensitivity/morris_summary.csv` (392 rows, 14 parameters × 28 blocks). Method: SALib Morris elementary effects with T = 100 trajectories, L = 4 levels, k = 14 parameters, and (k + 1) × T = 1,500 model evaluations. μ* is the mean absolute elementary effect (magnitude of influence). Values are rounded to three significant digits. This table is the single source of truth for the Morris top-3 citations in §4.5, §5.1, and the abstract; the canonical top-3 is also recorded separately in `manuscript/sections/canonical_morris_top3.md`. *claim_scope.* These results are pilot-scaffold estimates (see the `claim_scope` field in `morris_summary.csv`) and not calibrated operational-environment sensitivity estimates.
