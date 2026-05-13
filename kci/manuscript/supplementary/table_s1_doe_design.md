**<표 S1> 실험 설계 격자 (Experimental Design Grid, v0.7) — 보충 자료**

| 단계 (Phase) | 원점 (Origin) | 스윕 차원 (Sweep dimensions) | 수준 (Levels) | R (반복) | 페어드 실행 수 (Total paired runs) | 추정 벽시계 (Estimated wall-clock) |
|---|---|---|---|---|---|---|
| Phase 1a (베이스라인 강건성) | A (송파구청 일자리센터) | `p_fail_scale` | 0.0, 0.10, 0.25, 0.50, 0.75, 1.0, 1.5, 2.0 (8) | 30 | 8 × 30 = 240 | ≈70 분 |
| Phase 1b (원점 강건성) | B, C, D (D = 비검증) | `p_fail_scale` × origin | {0.0, 0.5, 1.0, 1.5} × {B, C, D} (4 × 3 = 12) | 20 | 12 × 20 = 240 | ≈70 분 |
| Phase 2 (단일모드 파라메트릭) | A | `bus.fleet_size` × `bus.dispatch_interval_min` × `p_fail_scale` | {15, 23, 35, 50, 80} × {3, 5, 10} × {0.5, 1.0, 2.0} (5 × 3 × 3 = 45) | 20 | 45 × 20 = 900 | ≈4.3 시간 |
| Phase 3 (반사실적 레버 스윕, 헤드라인) | A | `rail.headway_min` × `lastmile_fleet_size` × `rail.capacity_pax_per_train` × `p_fail_scale` | {15, 7.5, 3} × {23, 50, 100} × {500, 1000, 2000} × {0.0, 0.5, 1.5} (3⁴ = 81) | 15 | 81 × 15 = 1,215 | ≈5.7 시간 |
| Morris (전역 민감도) | A | 파라미터 14개 × 궤적(trajectories) × 수준(levels) | k = 14, T = 100, L = 4 | — | (14 + 1) × 100 = 1,500 모델 평가 | ≈1.5 시간 |

*주.* `s` (수요 배수)축은 v0.6 inertness 검증 결과에 따라 v0.7에서 제거되었고, Phase 1a는 `s = 1.2`로 고정한다 (`plan.md` §4.1). Phase 1b의 origin D는 비검증(unverified) 변형이므로 본문 강건성 결론에서 부각하지 않는다. Morris 단계의 파라미터 수는 `plan.md` §4.5의 확장 목표(18 = 14 + Phase 3 레버 4)와 달리 v0.7 실행에서 원본 14개 파라미터로 수행되었으며, 향후 확장은 후속 작업으로 남는다. R은 페어드 CRN(common random numbers) 반복 수, 페어드 실행 수는 multimodal/bus_only 쌍을 1개의 페어드 행으로 집계한 단위이다 (실제 시나리오 호출 수는 페어드 실행 수 × 2). 추정 벽시계는 `plan.md` §4의 설계 단계 추산치이며, 실제 실행시간과 차이가 있을 수 있다.
