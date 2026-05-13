# 5. 결론 및 향후 연구

본 장은 §4의 4단계 실험(Phase 1a 기준 강건성, Phase 1b 원점 강건성, Phase 2 단일수단 튜닝, Phase 3 반사실 레버 스윕)과 Morris 전역 민감도 결과를 §1.3의 연구질문 및 §3.9의 조건도(condition map) 경계 안에서 종합한다. 본 결론의 모든 정량 진술은 §3.6의 paired-CRN 절차로 산출된 차이 Δ에 한하며, 부호 규약은 `Δ = bus_only − multimodal` (음수 = 직행버스 우위)로 일관 적용된다.

## 5.1 주요 발견 (Main finding)

> **송파 → 72사단(부곡리) 회랑에서 검토된 인프라/매개변수 공간 내에서 multimodal 적용 조건(applicability condition)은 발견되지 않는다. 직행버스는 모든 관측 disruption 강도(`p_fail_scale ∈ [0, 2]`), 4개 후보 원점, 단일수단 fleet/dispatch 튜닝 5×3 격자, 그리고 9개 반사실 인프라 레버 조합(`rail_headway × lastmile_fleet × rail_capacity`) 81셀에서 페어드 CRN 기준 통계적으로 더 우수하거나 동등하다.**

이 진술은 다음 네 가지 정량 근거로 뒷받침된다(상세 수치는 §4 및 표 2·3·4·6 참조).

1. Phase 1a (Origin A, R = 30): `p_fail_scale = 0.0`에서 Δ penalized_makespan = **−58.5분** (95% CI [−58.5, −58.5])로 무장애 영역에서도 구조적 환승 페널티가 직행버스 우위로 작용한다. `p_fail_scale = 2.0`에서 Δ P(완료 ≤ 1500분) = **+0.433** (95% CI [+0.245, +0.622])로 고압박 영역에서 직행버스가 마감 내 완료 확률 측면에서 43.3 포인트 우위를 확보한다.
2. Phase 2 (R = 20): 가장 공격적인 단일수단 튜닝(`bus_fleet_size = 80`, `dispatch_min = 3`, `p_fail_scale = 2.0`)에서 Δ = **−576,348분** (95% CI excludes 0)로 단일수단 fleet/dispatch 한계 튜닝이 부호 반전을 일으키지 못한다.
3. Phase 3 (R = 15, 81 cell): `multi_dominant` 분류 셀은 **0 / 81**이며 `bus_dominant` 54 cell, `inconclusive` 27 cell이다. 부호 반전에 가장 근접한 cell(narrowest gap)은 `rail_headway = 3분, lastmile_fleet = 23, rail_capacity = 500, p_fail_scale = 0.5`에서 Δ = **−39.3분** [−50.7, −28.0]로 여전히 `bus_dominant`로 분류된다(표 6).
4. Morris 전역 민감도 (k = 14, T = 100): 정전 평균 μ* 상위 3개는 `passenger_volume` (**44.5**), `direct_bus_fleet_size` (**27.4**), `dispatch_interval` (**20.8**)로 모두 공급측 자원 모수이며 모드 선택 매개변수는 상위에 없다(canonical_morris_top3.md, 표 5).

**v0.6 → v0.7 재포지셔닝의 의미.** 위 결과의 v0.6 → v0.7 재포지셔닝 의미는 "break-even 탐색"이 아닌 "**적용 조건 식별(applicability-condition identification)**"이다. 검토된 격자 안에서 multimodal이 직행버스를 앞서는 조건은 존재하지 않으며, 이는 본 회랑이 multimodal 도입에 (현재 가용 인프라 레버 범위 내에서) 부적합함을 의미하는 정의된 negative result이다. 본 연구의 산출물은 단일 권고가 아니라 *조건 지도(condition map)*이며, multimodal 우위의 부재는 가설이 아닌 통계적으로 검정된 결론이다.

## 5.2 학술적·실무적 함의 (Implications)

**학술적 함의.**

1. **부정적 결과의 정량적 정의.** 본 연구는 multimodal 우위가 부재하다는 단순 진술을 넘어, R = 30 paired-CRN, censoring-aware penalized makespan, 분위 도착 KPI, 그리고 Morris 전역 민감도를 결합하여 **검토 공간 내 비-적용성**을 통계적으로 정량화한다. 산업공학·운영연구 출판 관행에서 "uplift 없음"은 흔히 보고에서 누락되지만, 본 연구는 페어드 CRN과 분류 규칙(`bus_dominant` / `inconclusive` / `multi_dominant`)을 결합하여 비-적용성을 검증 가능한 진술로 격상시킨다.
2. **회랑 기하학(geometry)의 결정성.** 송파 ↔ 부곡리 회랑은 multimodal 경로가 두 도로 구간(A → S 약 12 km, R → D 약 30 km)을 노출하는 반면 직행버스는 한 구간만 노출하므로, 철도는 **중복(redundancy)이 아닌 추가 위험(added risk)**으로 작용한다. 이 기하학적 비대칭이 검토된 인프라 레버 모두(rail_headway 3분, lastmile_fleet 100대, rail_capacity 2000 pax/train)를 무효화한다.

**실무적 함의.**

3. **정책 권고.** 본 회랑에 대한 예비군 동원수송 계획은 단일수단(직행버스) 운용에 집중하는 것이 censoring-aware 보정 makespan 기준 통계적으로 우월하다. Phase 2의 결과는 본 회랑에서 운영 가용한 자원 모수의 한계 효과가 multimodal 도입보다 크다는 점을 보인다.
4. **Morris 결과의 운영적 함의.** 가장 큰 민감도는 `passenger_volume`과 `direct_bus_fleet_size`에 있다 — 즉 수요 규모 추정과 직행버스 가용 차량 수가 가장 중요한 운영 변수이며, 모드 선택(multimodal vs single)은 본 회랑에서 부차적이다. 후속 보정 단계의 자원 배분은 이 두 매개변수의 실측·시나리오 검증에 집중하는 것이 한계비용 대비 효과가 가장 크다.
5. **일반화 가능성.** 본 결과는 회랑별 기하학(특히 multimodal 경로가 노출하는 도로 구간 수)에 강하게 의존한다. 다른 회랑 — 특히 multimodal 경로가 직행 경로보다 *적은* 도로 구간을 노출하는 경우, 또는 직행 도로 경로가 극도로 장거리·혼잡 노출이 큰 경우 — 에서는 결과가 반전될 수 있다. 본 연구의 비-적용성 결론은 회랑 특이적이며, 다른 회랑으로의 외삽은 동일 분석 골격의 재실행을 전제로 한다.

## 5.3 한계 (Limitations)

본 연구의 한계는 §3.9에서 일차로 선언하였으며, 결론 해석에 직접 영향을 미치는 다섯 가지 항목을 본 절에서 다시 정리한다.

- **반복 회수.** R = 30 (Phase 1a) / R = 20 (Phase 1b, Phase 2) / R = 15 (Phase 3)의 페어드 표본을 사용하였다. Phase 3의 R = 15는 81셀 × 15rep = 1,215 paired runs로 wall-clock 제약 하의 정직한 trade-off이며, 27개 `inconclusive` 셀의 일부는 R 확대로 분류 안정화될 가능성이 있다(점추정 부호는 모두 음).
- **단일 회랑 보정.** 본 연구는 송파 → 양주 부곡리 단일 회랑에 한정되며, 모드 선택에 대한 결론은 회랑 특이적이다. §5.2의 함의 5에서 명시한 바와 같이 다른 회랑으로의 일반화는 보장되지 않는다.
- **Origin D의 비검증 (unverified).** Origin D(잠실종합운동장)는 공개 자료로 출처 검증이 통과되지 않은 후보로 분류되며(표 4 D† 각주; 보충자료 그림 S1 빗금/링; §4.2 caveat 박스), 본문 결론에서 비교 참고용으로만 인용된다. 본 §5.1의 주요 발견은 검증된 Origin A·B·C 기준으로도 단독 성립한다.
- **Morris의 claim_scope.** Morris 결과는 파일럿 스케일 fixture demand 위의 screening이며 calibrated 운영-환경 민감도 추정치 아니다(`morris_summary.csv::claim_scope`). 본 §5.1·§5.2의 인용은 μ* 절대값보다는 *상대 순위*에 한정한다.
- **Phase 3 레버 범위.** 본 연구의 반사실 레버 범위는 `rail_headway ∈ [3, 15]분`, `lastmile_fleet ∈ [23, 100]대`, `rail_capacity ∈ [500, 2000] pax/train`이다. 이 범위 외부(예: 1분 headway, 200대 fleet, 5,000 pax/train)는 검토되지 않았으며, 본 §5.1의 비-적용성 진술은 검토 범위 내에 한정된다.

## 5.4 향후 연구 (Future work)

본 연구의 결론을 보정 단계로 확장하기 위한 후속 연구 방향은 다음 네 가지로 정리된다.

1. **다른 동원훈련장 회랑 비교 연구.** 산악·도서·다른 지방 부대를 포함하는 회랑 후보군을 대상으로 동일 분석 골격을 이식하여 회랑별 기하학에 따른 modal preference 반전 조건을 일반화한다. 본 연구의 비-적용성 결론은 회랑 특이적이며, 회랑 기하학(노출 도로 구간 수, 직행 거리, 환승 위치)을 covariate로 한 cross-corridor 메타 분석이 modal selection rule의 일반 형태를 식별할 수 있다.
2. **장애 모델의 확장.** 본 연구는 도로 고장 모델(BPR + capacity reduction)을 단일 disruption 채널로 사용하였다. 후속 연구는 traffic incident(point-event 모델), 기상 시나리오(권역별 capacity 감소), 철도 신호 장애 등을 추가하여 disruption portfolio를 다양화할 수 있다. 본 연구의 paired-CRN 골격은 이러한 다채널 disruption을 그대로 흡수한다.
3. **회랑별 비용-편익 분석.** 본 §5.1의 Δ penalized_makespan 절대값(예: `p_fail_scale = 2.0`에서 −576,348분)을 화폐 단위로 환산하기 위한 inventory-cost·delay-cost 모델 결합이 필요하다. 본 연구는 운영 KPI 차이를 정량화하였으나, 정책 결정자의 효용함수에 대응하는 화폐 가치는 추가 보정 입력을 요구한다.
4. **R 한도 확장 재현.** 본 연구의 Phase 3 R = 15는 wall-clock 제약 하의 trade-off이다. R = 50 이상으로 재현하면 27개 inconclusive 셀의 분산이 감소하여 분류 안정화가 가능하며, 이는 본 §5.1의 비-적용성 진술의 power를 강화한다. 본 연구의 재현성 패키지(deterministic seed, 매니페스트, 청정 체크아웃 스모크)는 이러한 R 확장을 직접 지원하도록 설계되었다.

본 연구의 결론을 한 문장으로 요약하면 다음과 같다. **검토된 인프라·매개변수 공간 내에서 송파 → 72사단(부곡리) 회랑은 multimodal 적용 조건이 부재하며, 이 비-적용성은 R = 30 paired-CRN과 81셀 반사실 레버 스윕으로 통계적으로 검정된 정의된 negative result이다.** 이 진술은 §3.9의 조건도 경계 안에서만 유효하며, 운용 의사결정 적용은 §5.3의 다섯 가지 한계를 동시에 해소하는 보정 후속 연구를 전제로 한다.
