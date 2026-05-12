# 4. 결과

본 장은 §3에서 기술한 두 단계 실험 설계와 Morris 민감도 분석의 결과를 차례로 제시한다. 모든 수치는 §3.6의 paired CRN 절차에 따라 cell당 동일 seed로 두 모드를 짝지어 산출한 paired delta와 그 95% 신뢰구간을 함께 보고하며, 본 절의 모든 정량적 비교는 §3.9에서 선언된 *조건도(condition map)*의 해석 경계 내에 한정된다. 특히 §3.3의 `HIGHWAY_DEFAULTS`가 미보정 계획 프록시라는 사실, §3.5의 반복 회수 축소($R=10$), 그리고 Origin D의 출처 미확인 가정 변형 지위는 본 절 전반에 걸쳐 반복적으로 환기된다.

## 4.1 Phase 1 break-even 분석 (Origin A)

Phase 1 격자는 혼잡 스케일 $s \in \{0.8, 1.0, 1.2, 1.5, 2.0\}$ × 장애 강도 $p_{\mathrm{fail,scale}} \in \{0.0, 0.25, 0.50, 1.0, 1.5, 2.0, 3.0\}$의 5×7 = 35 cell, cell당 $R = 10$ paired CRN seed로 구성된다. 〈그림 3〉은 paired delta penalized makespan $\bar{\delta}_{\mathrm{pm}} = \bar{M}^{\mathrm{bus}}_{\mathrm{pen}} - \bar{M}^{\mathrm{multi}}_{\mathrm{pen}}$의 (s, p) 격자 위 히트맵이며, 〈표 2〉는 동일 데이터의 paired $t$ 기반 95% CI를 셀별로 정리한다.

**무장애 영역 (장애 없음).** $p_{\mathrm{fail,scale}} = 0$의 모든 $s$ 수준에서 단일수단(버스)이 복합수단(철도-버스)보다 약 58분 빠르게 완수된다. $s = 1.0$, $p = 0.0$ cell에서 $\bar{\delta}_{\mathrm{pm}} = -58.5$분이며 paired delta 표본분산이 0에 가깝다(모든 seed에서 결정론적 BPR 자유 통행 + 환승 손실 약 60분이 그대로 페어 차로 잡힌다). 이 값은 §3.3의 환승 고정지연($t_{\mathrm{transfer}} = 3$분/인) + 복합수단 경로의 추가 거리 비용을 반영하는 *구조적 환승 페널티*로 해석된다.

**중간 압박 영역 ($p \in \{0.25, 0.50\}$).** 양 모드 모두에서 censored_count가 점진적으로 증가하나(버스 100 → 300명, 복합수단 100 → 300명) 두 모드의 censoring이 동일 수준으로 페어드되어 paired delta는 여전히 음의 부호를 유지한다. $s = 1.0$, $p = 0.25$에서 $\bar{\delta}_{\mathrm{pm}} = -54.0$분, 95% CI $[-65.8, -42.1]$; $p = 0.50$에서 $\bar{\delta}_{\mathrm{pm}} = -41.7$분, 95% CI $[-59.6, -23.9]$로 단일수단 우위가 통계적으로 유의하다.

**고압박 영역 ($p \geq 1.0$): censoring-driven break-even.** $p_{\mathrm{fail,scale}} \geq 1.0$ 영역에서는 두 모드의 미도착률이 비대칭적으로 갈리면서 paired delta가 대규모 음의 값으로 떨어진다. $s = 1.0$, $p = 1.0$ cell에서 버스 censored 평균 400명·복합수단 censored 평균 500명, $\bar{\delta}_{\mathrm{pm}} \approx -1.44 \times 10^5$분, paired 95% CI $[-4.70 \times 10^5, +1.82 \times 10^5]$분으로 신뢰구간이 0을 포함한다. 즉 페널티 $\pi = 1440$분이 100명 차이에 곱해진 결과($100 \times 1440 = 144{,}000$분)가 delta의 평균을 지배하지만, seed 간 압박 실현의 변동성이 커서 통계적 유의성은 R = 10에서 확보되지 않는다. $p = 2.0$, $s = 1.0$에서는 censoring 격차가 200명으로 확대되어 $\bar{\delta}_{\mathrm{pm}} \approx -2.88 \times 10^5$분, 95% CI $[-7.23 \times 10^5, +1.46 \times 10^5]$분이다. 종합하면 본 회랑의 *실용적 break-even*은 paired makespan 부호가 아니라 **censoring 격차의 부호** 위에서 정의되며, 이 격차는 $p_{\mathrm{fail,scale}} \approx 1.0$ 부근에서 처음 0.1 이상의 양의 값을 띤다(즉 multimodal이 더 많이 미도착, §4.2 참조).

**혼잡 축의 둔감성.** 동일 $p$에 대한 다섯 개 $s$ 수준의 paired delta 차이는 1분 미만으로 본 회랑에서는 BPR 자유 통행시간 항이 도로 차단 페널티에 비해 1차적으로 무시할 수 있는 규모임을 시사한다. 이는 §3.3의 미보정 capacity 가정 하에서 본 회랑 거리(약 40-50 km) × BPR 곡선이 $s \in [0.8, 2.0]$ 범위에서 자유 통행시간을 수십 분 단위로만 변동시키는 반면, censoring 페널티는 인당 1440분이라는 두 자릿수 큰 단위라는 점에서 기인한다. 따라서 〈그림 3〉의 히트맵은 본질적으로 $p$축에 평행한 줄무늬 패턴을 보인다.

## 4.2 Phase 1 완수율 곡선

페널티 합산 지표만으로는 censoring 규모가 makespan을 압도하므로, 본 절은 §3.1에서 정의한 *raw completion rate*를 별도로 보고한다. 〈그림 4〉는 $s \in \{0.8, 1.2, 2.0\}$의 세 단면을 $p_{\mathrm{fail,scale}}$의 함수로 표시한 모드별 완수율 곡선이다.

**완수율 단조 감소.** 두 모드 모두 $p$가 0에서 3.0으로 증가함에 따라 완수율이 단조적으로 감소한다. 단일수단의 경우 1.00 → 0.90 → 0.70 → 0.60 → 0.40 → 0.30 → 0.20, 복합수단의 경우 1.00 → 0.90 → 0.70 → 0.50 → 0.30 → 0.10 → 0.10이다. $p \leq 0.50$에서 두 모드의 완수율은 격자상 0.01의 분해능 내에서 동일하다(*"낮은 압박 평형 영역"*).

**Bus advantage 발현 구간.** $p_{\mathrm{fail,scale}} \geq 1.0$ 영역에서 단일수단이 복합수단을 0.1-0.2 포인트 차이로 일관되게 앞선다. 격차의 정점은 $p = 2.0$에서 발생하며 모든 $s$ 수준에서 $\bar{\Delta}_{\mathrm{cr}} = +0.20$, paired 95% CI $[-0.10, +0.50]$이다(R = 10에서 분산이 큰 이항형 지표라 CI는 0을 포함하나 점추정의 일관된 부호는 5개 $s$ 수준 모두에서 동일하다).

**해석: 환승 노드 의존성.** 본 회랑에서 복합수단이 더 빨리 무너지는 메커니즘은 §3.4의 `rail_station_access` 시나리오 패밀리에서 명시적으로 모형화되어 있다. 잠실역·의정부역 진출입로의 capacity 감소는 셔틀 leg(A→S)와 last-mile leg(R→D)를 동시에 압박하므로, 단일수단의 단일 경로 차단보다 시스템 차원의 손실이 누적되기 쉽다. 즉 본 결과는 *철도 leg의 추상 프록시 가정* 하에서도 환승 노드의 도로 접근성이 복합수단 회복력의 1차적 병목임을 시사하며, §5.2의 의사결정 논의에서 더 자세히 다룬다.

## 4.3 Phase 2 정책 trade-off

Phase 2 격자는 집결 지연 $\sigma \in \{0.3, 0.5, 0.7, 1.0\}$ × 7개 출발 정책(STRICT 1개 + GRACE $W \in \{15, 30, 60\}$분 × $\theta \in \{0.8, 0.9\}$의 6개 조합)의 4 × 7 = 28 cell, cell당 $R = 10$ paired CRN seed로 구성된다(고정 압박점 $s = 1.2$, $p_{\mathrm{fail,scale}} = 1.0$). 〈표 3〉은 sigma × policy 격자의 paired delta penalized makespan과 두 모드 raw 완수율을 정리한다.

**정책 무차별성 영역.** $\sigma \in \{0.3, 0.5, 0.7\}$ 세 수준에서 7개 정책 간 paired delta penalized makespan은 0.5분 이내로 사실상 구별되지 않는다($\bar{\delta}_{\mathrm{pm}} \approx -1.44 \times 10^5$분이 7개 정책 모두에서 일치). 이는 본 시뮬레이터의 lognormal($\mu = 2.0$, $\sigma \leq 0.7$) 집결 분포 하에서 99분위 도착이 GRACE의 가장 좁은 유예 윈도 $W = 15$분 안에 모두 흡수되므로 정책 간 행동이 동일해지기 때문이다. STRICT와 GRACE의 makespan 차는 0.5분 수준에 머문다.

**고분산 영역 ($\sigma = 1.0$).** 집결 분포의 꼬리가 더 두꺼워지면 GRACE의 유예 종료시각과 STRICT의 정시 출발이 비로소 분기한다. $\sigma = 1.0$에서 GRACE 정책군의 $\bar{\delta}_{\mathrm{pm}} \approx -1.4410 \times 10^5$분, STRICT의 $\bar{\delta}_{\mathrm{pm}} \approx -1.4410 \times 10^5$분으로 두 군의 차이는 약 0.9분에 불과하다. 즉 본 회랑·본 압박점에서 *정책 효과는 1차 censoring 페널티에 비해 두 자릿수 작은 규모이며*, Pareto 전선 위 정책 선택은 makespan보다 운용·승객 편의 관점에서 결정되어야 한다.

**Pareto 비지배 정책.** paired delta penalized makespan 단일 축에서 모든 7개 정책은 사실상 동일점에 위치하므로 일차 Pareto 비교는 사실상 의미가 없다. 보조 축으로 raw 완수율(7개 정책 모두 버스 0.60, 복합수단 0.50)을 함께 고려해도 모든 정책이 비지배 집합에 속한다. 본 격자에서 정책 trade-off가 출현하지 않는다는 결과 자체가 §5의 논의에서 *"본 회랑·본 압박점에서는 출발 정책 미세 조정의 효용이 도로 신뢰성 개선 대비 매우 작다"*라는 함의로 해석된다.

## 4.4 Origin 강건성

Phase 1의 주 스트림을 Origin A로 고정한 결과가 집결지 선택에 얼마나 강건한지를 확인하기 위해, B(삼전동 구민회관), C(장지역 4번 출구), D(잠실종합운동장)에 대해 $s \in \{1.0, 1.5\}$ × $p_{\mathrm{fail,scale}} \in \{0.0, 1.0, 2.0\}$의 focused 2 × 3 격자, cell당 $R = 5$로 robustness 보조 스트림을 실행하였다(§3.5). 〈그림 5〉는 네 origin의 paired delta penalized makespan을 동일 cell 위에서 비교한 box plot이며, 〈표 4〉는 cell별 평균과 origin A 대비 절대 격차를 정리한다.

**Origin A vs. B (검증된 인근 집결지).** $s = 1.0$, $p = 1.0$의 대표 cell에서 Origin A의 $\bar{\delta}_{\mathrm{pm}} \approx -1.44 \times 10^5$분 대비 Origin B는 $\bar{\delta}_{\mathrm{pm}} \approx -2.88 \times 10^5$분으로 약 1.4 × $10^5$분 더 음의 방향이다. 다만 B의 raw 완수율은 버스 1.00·복합수단 0.80으로 A보다 모두 높아, 절대 페널티 합산 차이의 부호 변동은 censoring 분포의 비대칭에서 기인한다. B는 송파구 조례 2023-09-14 및 한국경제 2024-02-29 보도에 명시된 *검증된 예비군 수송버스 집결지*이며, A 대비 약 1 km 서쪽에 위치한 지리적 변형이 결과를 *부호 단위에서는* 변동시키지 않음을 시사한다.

**Origin A vs. C (검증된 남단 집결지).** Origin C(장지역)는 회랑의 남단·동측에 위치한 검증된 집결지로, $s = 1.0$, $p = 1.0$ cell에서 $\bar{\delta}_{\mathrm{pm}} \approx -38.1$분, raw 완수율 버스 0.60·복합수단 0.60이다. 흥미롭게도 C에서는 $p = 1.0$에서 두 모드의 censoring이 정확히 같아 paired delta가 무장애 영역과 유사한 -38 ~ -60분 범위에 머문다. C의 잠실역 진입 경로가 A·B보다 짧아 환승 노드 의존성이 약화되는 점이 본 격차의 원인으로 해석된다.

**Origin D (출처 미확인 가정 변형).** Origin D(잠실종합운동장)는 §3.2·§3.9에서 명시한 바와 같이 **출처 미확인 가정 변형으로 본 결과는 robustness 시험용에 한정한다**. D는 $s = 1.0$, $p = 1.0$ cell에서 $\bar{\delta}_{\mathrm{pm}} \approx -5.76 \times 10^5$분, raw 완수율 버스 1.00·복합수단 0.60이다. 즉 D의 단일수단 0.60→1.00 향상은 잠실역에서 매우 가까운 D의 지리적 위치가 셔틀 leg(A→S)의 도로 차단 노출을 *증가*시키는 반면(복합수단 완수율 하락), 직행 버스 경로의 회랑 진입을 *단축*시켜(버스 완수율 향상) 두 효과의 합으로 paired delta가 강한 음의 방향으로 이동한 것이다. 본 D의 결과는 *공식 집결지 지정 여부가 공개 자료에서 확인되지 않은 가상 변형*이므로 본 절은 단지 *결과 부호의 안정성*만을 시사 수준에서 보고하고, 운용 함의는 §5에서 도출하지 않는다.

**종합.** 네 origin 모두에서 paired delta penalized makespan의 부호는 음(단일수단 우위)을 유지하며, 평균 격차의 절대값은 origin 위치에 따라 약 $4 \times 10^4$분 ~ $6 \times 10^5$분 범위로 변동한다. 본 부호 강건성은 §4.1·§4.2의 일차 결론(*"고압박 영역에서 단일수단이 censoring 측면에서 우위"*)이 origin 선택에 1차적으로 의존하지 않음을 보인다.

## 4.5 Morris 민감도 분석

Morris elementary-effects 분석은 §3.7의 9개 핵심 매개변수(passenger_volume·direct_bus_fleet_size·dispatch_interval·turnaround_time·last_mile_fleet_size·rail_headway·rail_capacity·feeder_fleet_size·transfer_fixed_delay 등 총 14개 SALib 인자)에 대해 trajectory 수 50, level 수 4의 설계로 실행되었다(`results/sensitivity/morris_summary.csv`). 본 절은 두 핵심 지표 *penalized_makespan*과 *completion_rate*에 대한 $\mu^*$ 순위를 보고한다. 〈표 5〉는 두 정책(`baseline_multimodal`, `bus_only`)과 두 시나리오(`songpa_random_capacity_reduction`, `songpa_last_mile_station_to_destination`) 평균의 매개변수 순위를 정리한다.

**Penalized makespan 영향력 순위 (상위 3개).**

1. **passenger_volume** ($\mu^* = 1.46 \times 10^2$분, $\sigma = 3.88 \times 10^2$분). 본 모형의 입력 인원 $N$이 가장 큰 1차 효과를 보인다. censoring 페널티가 $n_c \cdot \pi$의 곱 형태이므로 $N$의 변동이 미도착자 수의 절대값을 직접 변동시키는 구조적 결과이다.
2. **direct_bus_fleet_size** ($\mu^* = 9.71 \times 10$분, $\sigma = 2.65 \times 10^2$분). 단일수단 회로의 차량 수는 일정 시한 내 사이클 회수를 결정하므로 makespan에 강한 비선형 영향을 미친다. $\sigma$가 $\mu^*$를 상회하므로 상호작용·임계점 효과가 있음을 시사한다.
3. **dispatch_interval** ($\mu^* = 7.54 \times 10$분, $\sigma = 2.56 \times 10^2$분). 배차 간격이 좁아질수록 차량 회전이 가속되어 makespan이 단조 감소하나, 차량 가용성 제약과의 상호작용에 따라 비선형 효과가 강하다.

**Completion rate 영향력 순위 (상위 3개).** 완수율(0 ~ 1 스케일) 기준으로는 (1) passenger_volume ($\mu^* = 1.10 \times 10^{-2}$), (2) dispatch_interval ($\mu^* = 6.06 \times 10^{-3}$), (3) direct_bus_fleet_size ($\mu^* = 3.75 \times 10^{-3}$) 순으로 동일한 3개 매개변수가 상위를 점유한다. 즉 본 회랑에서 censoring과 makespan은 사실상 동일한 1차 매개변수 집합에 의해 구동된다.

**해석 시드.** 상위 3개 매개변수는 모두 *공급측 자원 모수*(인원·차량 수·배차)이며, 도로 신뢰성 매개변수(capacity_reduction_factor, road_background_traffic_multiplier)는 $\mu^* < 1.0$분으로 1-2 자릿수 작다. 이는 §4.1의 *혼잡 축 둔감성* 관찰과 정합적이며, §5.3의 의사결정 시사점(*"자원 보강이 회랑 신뢰성 보강보다 비용 효율적 가능성이 크다"*)의 정량적 근거를 제공한다. 다만 본 Morris 결과는 §3.5에 명시된 50 trajectory 축소 설계 위에서 산출되었으므로 $\mu^*$ 절대값의 외부 타당성보다는 *상대 순위*만 일관되게 해석한다.

## 4.6 결과 종합

본 장의 네 갈래 결과는 다음과 같이 종합된다.

첫째, **무장애 영역에서 단일수단이 약 58분 우위**이며 이는 본 회랑의 환승 고정지연·추가 거리에 기인하는 *구조적 환승 페널티*이다. 둘째, **고압박 영역($p_{\mathrm{fail,scale}} \geq 1.0$)에서 복합수단의 미도착률이 단일수단보다 0.1-0.2 포인트 높아** 단일수단의 우위가 censoring 측면에서 확장된다. 본 분기는 paired makespan의 부호가 아니라 *censoring 격차의 부호* 위에서 정의되는 *실용적 break-even*이다. 셋째, **출발 정책(STRICT/GRACE) 미세 조정의 효용은 censoring 페널티에 비해 두 자릿수 작아** 본 회랑·본 압박점에서는 정책 trade-off가 사실상 평탄하다. 넷째, **origin 선택은 paired delta의 부호를 변동시키지 않으나** 절대 격차의 규모는 $4 \times 10^4$분 ~ $6 \times 10^5$분 범위로 변동하며, Origin D는 출처 미확인 가정 변형으로서 robustness 시험용에만 한정 해석된다. 다섯째, **Morris 분석은 makespan·완수율의 1차 변동이 인원·차량·배차의 공급측 자원에 집중됨을 시사**하며, 도로 신뢰성 매개변수의 효과는 1-2 자릿수 작다.

이상의 다섯 결과는 §3.9에서 선언한 미보정 capacity·미보정 p_fail·추상 철도 leg·검증 부재의 조건도 경계 내에서만 유효하며, 본 연구는 단일 정책 권고가 아닌 *조건부 비교 지도*로 위치한다. 본 결과의 군사적·운용적 함의와 후속 보정 연구의 방향은 §5에서 논의한다.

---

### 인용

(본 절은 §3에서 도입된 인용 [1]-[4]를 이어 사용하며, 본 절에서 새로 도입한 인용은 없다.)
