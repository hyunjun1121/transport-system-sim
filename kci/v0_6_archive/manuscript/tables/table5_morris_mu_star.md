**<표 5> Morris 전역 민감도: 파라미터별 μ* 및 σ (상위 순위)**
(Morris Global Sensitivity: Parameter μ* and σ, Top-Ranked)

| 순위 (Rank) | 파라미터 (Parameter) | μ* 평균 (Mean μ*) | μ* 최대 (Max μ*) | σ 평균 (Mean σ) | μ* 95% CI 폭 평균 | 집계 레코드 수 (n) |
|---|---|---|---|---|---|---|
| 1 | passenger_volume | 47.27 | 255.7 | 71.09 | 18.38 | 28 |
| 2 | direct_bus_fleet_size | 29.43 | 194.3 | 46.75 | 13.77 | 28 |
| 3 | dispatch_interval | 20.44 | 126.5 | 48.17 | 11.37 | 28 |
| 4 | turnaround_time | 12.70 | 64.50 | 41.59 | 11.34 | 28 |
| 5 | last_mile_fleet_size | 8.757 | 42.62 | 8.472 | 2.160 | 28 |
| 6 | rail_headway | 6.619 | 50.52 | 7.213 | 1.872 | 28 |
| 7 | feeder_fleet_size | 4.434 | 40.48 | 8.862 | 2.565 | 28 |
| 8 | rail_capacity | 3.942 | 43.11 | 6.719 | 1.873 | 28 |
| 9 | transfer_fixed_delay | 3.927 | 23.56 | 5.203 | 1.242 | 28 |
| 10 | passenger_arrival_variability | 2.375 | 11.53 | 8.252 | 2.112 | 28 |
| 11 | capacity_reduction_factor | 0.515 | 2.849 | 1.309 | 0.352 | 28 |
| 12 | road_background_traffic_multiplier | 0.349 | 2.009 | 0.767 | 0.195 | 28 |
| 13 | last_mile_access_disruption_probability | 0.33 | 2.102 | 0.796 | 0.223 | 28 |
| 14 | transfer_per_passenger_delay | 0.114 | 0.69 | 0.54 | 0.149 | 28 |

*주.* SALib Morris elementary-effects 방법, 궤적(trajectories) = 50, 수준(levels) = 4, 14개 파라미터에 대해 (k+1) × T = (14+1) × 50 = 750 표본/구성으로 평가. μ* = |elementary effect|의 평균 (영향력 크기), σ = elementary effects의 표준편차 (비선형/상호작용 강도). 본 표의 값은 7개 출력 지표 (완료율, censored 인원, 페널라이즈드 메이크스팬, p80·p95 도착시간, 총 운영분, 단위 운영분당 수송 인원) × 2개 정책 (`baseline_multimodal`, `bus_only`) × 2개 시나리오 (`songpa_last_mile_station_to_destination`, `songpa_random_capacity_reduction`)에 대한 평균. Morris 결과는 파일럿 스캐폴드 (`results/sensitivity/morris_summary.csv`의 claim_scope 필드 참고)로, 보정된 운영-환경 민감도 추정치는 아님.