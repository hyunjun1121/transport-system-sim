**<표 5> Morris 전역 민감도: 정전 집계 규칙(canonical aggregation)에 따른 파라미터별 평균 μ* 순위 (전 14개 파라미터)**

| 순위 (Rank) | 파라미터 (Parameter ID) | 정전 평균 μ* (Canonical mean μ*) | 집계 블록 수 (Blocks aggregated) |
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

*주.* **정전 집계 규칙 (canonical aggregation rule, `plan.md` §3.7 / §10).** 각 파라미터에 대해 (1) `(parameter_id, metric)`별로 `(policy_id × scenario_id)` 블록(2 × 2 = 4 블록) 평균 μ*를 산출하고, (2) 다시 7개 metric (`completion_rate`, `censored_count`, `penalized_makespan`, `p80_arrival_time`, `p95_arrival_time`, `total_service_minutes`, `passengers_per_total_service_minute`)에 대해 평균하여 정전 평균 μ*를 얻는다. 따라서 집계 블록 수 = 7 metric × 2 policy × 2 scenario = 28 블록/파라미터. 출처: `results/sensitivity/morris_summary.csv` (392행, 14 파라미터 × 28 블록). 방법: SALib Morris elementary-effects, T = 100 궤적, L = 4 수준, k = 14 파라미터, 총 (k + 1) × T = 1,500 모델 평가. μ*는 elementary-effects 절댓값 평균(영향력 크기). 값은 유효숫자 3자리로 반올림했다. 본 표가 본문 §4.5 / §5.1 / 초록의 Morris top-3 인용에 대한 단일 출처(single source of truth)이며, 정전 top-3는 `manuscript/sections/canonical_morris_top3.md`에 별도 명기되어 있다. claim_scope: 본 결과는 파일럿 스캐폴드(`morris_summary.csv`의 `claim_scope` 필드 참고)로, 보정된 운영-환경 민감도 추정치는 아니다.
