# Figure 6 — Phase 3 반사실 레버 스윕 (헤드라인 그림)

**제목.** Phase 3 반사실 레버 스윕 — Δ penalized_makespan at p_fail_scale=1.5.

**패널 구성.** 본 그림은 Phase 3 반사실 그리드(3×3×3×3 = 81 셀, 셀당 R=15 페어드 CRN 반복)의 disruption 스트레스 수준 `p_fail_scale=1.5`에 대한 평균 Δ penalized_makespan(= bus − multi)을 3개 패널로 분할한 발산형(diverging) 히트맵이다. 패널은 `rail_capacity_pax_per_train ∈ {500, 1000, 2000}` 세 수준을 좌→우로 배치하고, 각 패널 내부에서 Y축은 `rail_headway_min (분) ∈ {15, 7.5, 3}`(상→하), X축은 `lastmile_fleet_size (대) ∈ {23, 50, 100}`(좌→우)이다. 셀 색상은 `RdBu_r` 컬러맵으로 0에서 발산하며, 청색(Δ<0)은 직행버스 우위, 적색(Δ>0)은 multimodal 우위를 나타낸다.

**헤드라인 해석.** 기저 (rail_headway=15분, lastmile=23, rail_capacity=500)에서는 Δ < 0 (직행버스 우위). 어느 셀에서 Δ ≥ 0 (multimodal 우위)으로 부호 반전이 일어나는가가 본 그림의 핵심이다. `✕` 마커는 95% paired-t CI가 0을 가로지르는 셀(부호 반전 후보)을 표시한다.

**핵심 수치.** 81셀 전체 분류는 bus_dominant 54셀, inconclusive 27셀, multi_dominant 0셀로, 검토된 인프라 레버 공간 내에서 multimodal 우위 셀은 발견되지 않았다. 부호 반전에 가장 근접한 셀은 `rail_headway = 3분, lastmile_fleet = 23, rail_capacity = 500, p_fail_scale = 0.5`로 평균 Δ penalized_makespan = **−39.3분** (95% CI [−50.7, −28.0])이며, 여전히 bus_dominant로 분류된다.

**기타 주.** 사이드카 통계 (셀별 평균·95% CI·분류 라벨)는 `manuscript/tables/table6_lever_conditions.md`와 `manuscript/tables/table6_lever_conditions_summary.json` 참조. CI는 paired-t (df = R−1 = 14) 기반이며, 비유한값(±inf)은 평균·CI 계산 전 제거했다.
