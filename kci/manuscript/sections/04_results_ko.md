# 4. 결과

본 장은 §3의 4단계 실험 설계(Phase 1a 기준 강건성, Phase 1b 원점 강건성, Phase 2 단일수단 매개변수 스윕, Phase 3 반사실 레버 스윕)와 Morris 전역 민감도 분석의 결과를 차례로 제시한다. 모든 정량값은 §3.6의 paired-CRN 절차에 따라 cell당 동일 seed로 두 모드를 페어드한 결과의 평균과 paired-t 95% 신뢰구간(이하 CI)을 함께 보고하며, 본 절의 모든 비교는 §3.9에서 선언된 *조건도(condition map)*의 해석 경계 내에 한정된다. Δ는 일관되게 `Δ = bus_only − multimodal`로 정의되어 음수는 직행버스 우위, 양수는 multimodal 우위를 의미한다(코드 `_safe_delta(left=bus, right=multi)`).

## 4.1 Phase 1a 기준 강건성 (Origin A, R = 30)

Phase 1a는 송파구청 일자리센터(Origin A)에서 출발하여 `p_fail_scale ∈ {0.0, 0.10, 0.25, 0.50, 0.75, 1.0, 1.5, 2.0}`의 8개 수준에 대해 cell당 R = 30회 페어드 CRN 반복을 수행하였다(〈표 2〉, 〈그림 3〉, 〈그림 4〉).

**무장애 영역에서의 구조적 페널티.** `p_fail_scale = 0.0`에서 Δ penalized_makespan = **−58.5분** (95% CI [−58.5, −58.5])이며 CRN 하 30회 반복이 결정적 동일 출력으로 수렴하여 CI 폭이 0이다. 즉 어떤 장애도 발생하지 않은 조건에서도 직행버스가 약 58분 빠르게 완수되며, 이는 multimodal 경로의 환승 고정지연과 추가 거리에 기인하는 *구조적 환승 페널티*로 해석된다.

**Disruption 강도에 따른 단조 악화.** `p_fail_scale`이 증가함에 따라 Δ q90 도착시간은 −58.5분(p=0.0)에서 −124.8분(p=0.5), −263.5분(p=1.5)을 거쳐 **−358.1분** (95% CI [−508.9, −207.3], p=2.0)으로 단조적으로 음의 방향으로 깊어진다. Δ P(완료 ≤ 1500분)는 0.000(p=0.0)에서 +0.133(p=1.0), +0.300(p=1.5)을 거쳐 **+0.433** (95% CI [+0.245, +0.622], p=2.0)으로 증가하여, 고압박 영역에서 직행버스가 마감 내 완료 확률 측면에서 약 43.3 포인트 우위를 확보한다.

**통계적 분리.** `p_fail_scale ≥ 0.75`의 모든 cell에서 Δ penalized_makespan의 95% CI가 0을 제외하여(〈표 2〉) paired-CRN 기준 두 모드가 통계적으로 유의하게 분리된다. 〈그림 3〉의 강건성 곡선은 8개 관측 점 모두에서 Δ < 0의 부호를 유지하며 어떤 disruption 강도에서도 break-even 교차가 관측되지 않는다.

## 4.2 Phase 1b 원점 강건성

Origin A의 결론이 집결지 선택에 강건한지 확인하기 위해 검증된 후보 B(삼전동), C(장지역), 그리고 비검증 후보 D†(비검증, 부록 보충자료)를 `p_fail_scale ∈ {0.0, 0.5, 1.0, 1.5}`의 4개 수준 × cell당 R = 20 (Origin A는 R = 30의 부분집합)으로 비교하였다(〈표 4〉; 시각화는 보충자료 〈그림 S1〉).

**부호 강건성.** 4개 원점 × 4개 `p_fail_scale` 수준 = 16 cell 모두에서 Δ penalized_makespan의 평균이 음의 부호를 유지한다. 무장애 영역에서 A는 −58.5분, B는 −57.2분, C는 −60.9분, D†는 −66.7분으로 4개 원점 간 격차는 약 10분 이내이다. 고압박 영역(`p_fail_scale = 1.5`)에서는 B = −720,413분, D† = −720,410분, A = −432,259분, C = −504,291분으로 절대 크기는 원점 위치에 따라 변동하나 모든 셀의 95% CI가 0 미만에 머문다.

**원점 간 격차 폭.** `p_fail_scale = 1.5`에서 4개 원점의 평균 Δ 분포 폭은 약 **288,154분**으로(보충자료 〈그림 S1〉) `p_fail_scale ≤ 1.0` 구간에서는 95% CI가 서로 크게 겹쳐 본문 결론이 출발지 선택에 robust함을 시사한다.

**Origin D 비검증 caveat (caveat 박스).** Origin D(잠실종합운동장)는 공개 자료에서 출처 검증을 통과하지 못한 비검증(unverified) 후보이므로(〈표 4〉 D† 각주, 보충자료 〈그림 S1〉 빗금/링 표시) 본 절의 결론 문장은 검증된 Origin A·B·C에 한정하며 D는 robustness 점검용 참고 자료로만 보고한다. 이 caveat은 §1.1, §3.5.2, §3.9 항목 2, §5.3에서 일관되게 명시된다.

## 4.3 Phase 2 단일수단 매개변수 스윕 (R = 20)

단일수단 튜닝만으로 §4.1의 격차를 해소할 수 있는지 검정하기 위해 `bus_fleet_size ∈ {15, 23, 35, 50, 80}` × `dispatch_min ∈ {3, 5, 10}` × `p_fail_scale ∈ {0.5, 1.0, 2.0}`의 5 × 3 × 3 = 45 cell, cell당 R = 20 페어드 CRN 반복을 수행하였다(〈표 3〉).

**격차 해소 부재 (헤드라인).** 가장 공격적인 단일수단 튜닝(`bus_fleet_size = 80`, `dispatch_min = 3`)에서도 `p_fail_scale = 2.0`의 Δ penalized_makespan = **−576,347.8분** (95% CI [−915,281.0, −237,414.5])으로 95% CI가 0을 제외한 채 강한 음의 부호를 유지한다. 즉 본 회랑에서 단일수단 fleet 증설·배차 단축의 한계 효과는 §4.1·§4.2의 multimodal 대비 격차를 부호 단위에서 변동시키지 못한다.

**중간 신뢰성 영역의 불확정성.** `p_fail_scale = 0.5` 및 `1.0`의 모든 튜닝셀에서 Δ의 95% CI가 0을 포함한다(예: `p_fail = 0.5`, fleet=80, dispatch=3에서 Δ = −72,118.8분 [−222,896.6, +78,659.0]). 이는 R = 20의 검정력 한계 하에서 단일수단과 multimodal이 중간 신뢰성 영역에서는 통계적으로 구별되지 않음을 의미하며, 부호 점추정은 여전히 일관되게 음이다.

**실용적 함의.** 단일수단 fleet/dispatch 튜닝은 §4.4의 multimodal 인프라 보강이 본 회랑에서 가용한 대안일 경우에만 비교 의의를 가진다. 그러나 §4.4가 보이듯 검토된 multimodal 인프라 공간 내에서도 부호 반전 cell은 발견되지 않아, 본 회랑의 결정 변수는 *모드 선택*이 아닌 *공급측 자원 모수*(passenger_volume, direct_bus_fleet_size, dispatch_interval; §4.5 참조)임이 시사된다.

## 4.4 Phase 3 반사실 레버 스윕 (헤드라인)

multimodal 인프라 보강 공간 내에서 mode-switch가 가능한 cell이 존재하는지 확인하기 위해 `rail_headway_min ∈ {3, 7.5, 15}` × `lastmile_fleet_size ∈ {23, 50, 100}` × `rail_capacity_pax_per_train ∈ {500, 1000, 2000}` × `p_fail_scale ∈ {0.5, 1.0, 1.5}`의 3⁴ = **81 cell**, cell당 R = 15 페어드 CRN 반복으로 반사실 레버 스윕을 실행하였다(〈그림 6〉, 〈표 6〉, `table6_lever_conditions_summary.json`).

**헤드라인 — multi_dominant cell의 부재.** 81 cell 중 **0 cell**이 `multi_dominant` (Δ의 95% CI 하한 > 0)로 분류된다. 분류 분포는 `bus_dominant` 54 cell, `inconclusive` 27 cell, `multi_dominant` 0 cell이다. 즉 본 연구가 검토한 인프라 레버 공간 내에서 multimodal을 직행버스보다 통계적으로 유의하게 우월하게 만드는 조건은 발견되지 않는다.

**부호 반전에 가장 근접한 cell.** 평균 Δ의 절대값이 가장 작은 cell은 `rail_headway = 3분, lastmile_fleet = 23, rail_capacity = 500, p_fail_scale = 0.5`로 Δ penalized_makespan = **−39.3분** (95% CI [−50.7, −28.0])이며, 분류는 여전히 `bus_dominant`이다(`narrowest_gap_cell`, R = 15). 본 cell은 검토된 가장 공격적인 철도 배차(3분 headway)와 함께 가장 낮은 disruption 수준(p_fail = 0.5)을 결합하였음에도 직행버스 우위가 유지됨을 보인다.

**`p_fail = 1.5`에서의 inconclusive 영역.** 〈표 6〉이 보고하는 5개 inconclusive cell은 모두 `rail_headway = 3분, p_fail_scale = 1.5`에 위치하며 평균 Δ = −192,127.9분 (95% CI [−472,873.2, +88,617.4])로 95% CI가 0을 포함한다. 점추정 부호는 여전히 음이며, R = 15의 검정력 한계가 통계적 비유의의 직접 원인으로 추정된다.

**v0.7의 핵심 기여.** 〈그림 6〉의 3 패널 발산형 히트맵은 (rail_headway × lastmile_fleet) 단면을 rail_capacity 수준별로 보임으로써, 검토된 가장 공격적인 인프라 개입(3분 headway × 4배 last-mile fleet × 4배 철도 용량)에서도 multimodal 우위 cell이 발견되지 않는다는 *조건부 부재(conditional null)* 를 명시한다.

## 4.5 Morris 전역 민감도 분석

Morris elementary-effects 분석은 §3.7의 14개 매개변수에 대해 T = 100 궤적, L = 4 수준 설계로 (k + 1) × T = **1,500 모델 평가**를 수행하였다. 본 절의 인용 수치는 `manuscript/sections/canonical_morris_top3.md` (단일 출처)와 〈표 5〉에서 그대로 가져왔으며, `morris_summary.csv`의 독립 재집계를 수행하지 않는다.

**정전 평균 μ* 상위 3개.** 7개 metric × 2 policy × 2 scenario = 28 블록을 평균한 정전(canonical) μ* 순위는 다음과 같다.

1. `passenger_volume` — μ* = **44.5**
2. `direct_bus_fleet_size` — μ* = **27.4**
3. `dispatch_interval` — μ* = **20.8**

(전 14개 파라미터 순위는 〈표 5〉 참조.)

**해석.** 상위 3개 매개변수는 모두 *공급측 자원 모수*(승객 인원·직행버스 차량 수·배차 간격)이며, 도로 신뢰성 매개변수(capacity_reduction_factor μ* = 1.73, road_background_traffic_multiplier μ* = 1.65)와 환승 매개변수(transfer_fixed_delay μ* = 3.10, transfer_per_passenger_delay μ* = 0.475)는 1–2 자릿수 작다. 이는 §4.3의 단일수단 fleet/dispatch 튜닝이 본 회랑에서 1차적 결정 변수임을 정량적으로 뒷받침한다. 다만 본 Morris 결과는 파일럿 스케일 fixture demand 위에서 산출되었으므로 μ* 절대값보다는 *상대 순위*만 일관되게 해석한다(`morris_summary.csv::claim_scope`).

## 4.6 종합: 적용 조건 진술

§4.1–§4.5의 결과는 다음의 단일 적용 조건 진술로 종합된다.

> **본 회랑(송파 ↔ 양주 부곡리)에서 본 연구가 검토한 인프라·매개변수 공간 내에서는 multimodal 적용 조건이 발견되지 않는다.** 직행버스는 (1) Phase 1a의 8개 관측 disruption 강도 전 구간(`p_fail_scale = 0.0 ~ 2.0`, Δ q90 = −58.5 ~ −358.1분), (2) Phase 1b의 4개 후보 원점(A 검증, B/C 검증, D 비검증), (3) Phase 2의 단일수단 fleet × dispatch × p_fail 5×3×3 = 45 cell, (4) Phase 3의 반사실 인프라 레버 81 cell 모두에서 paired-CRN 기준 통계적으로 더 우수하거나 (R = 15/20의 검정력 한계 하에서) 동등하다.

이 진술은 §3.9에 명시된 미보정 capacity 가정·미보정 p_fail 사다리·추상 철도 leg·Origin D 비검증의 조건도 경계 내에서만 유효하다. §4.5의 Morris 결과는 본 결론의 메커니즘 근거를 제공한다 — 본 회랑의 makespan과 censoring을 지배하는 1차 매개변수는 *공급측 자원 모수*(passenger_volume·direct_bus_fleet_size·dispatch_interval)이며, 모드 선택은 이 자원 모수의 직행버스 측 최적화가 multimodal의 환승·last-mile 손실을 흡수하기에 충분한 구조이다. §5는 본 적용 조건 진술의 군사·운용적 함의와 후속 보정 연구의 방향을 논의한다.

---

### 인용

(본 절은 §3에서 도입된 인용 [1]–[4]를 이어 사용하며, 본 절에서 새로 도입한 인용은 없다.)
