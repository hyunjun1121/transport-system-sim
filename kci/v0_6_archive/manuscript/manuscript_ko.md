# 산업공학 도구를 적용한 예비군 동원수송체계의 단일수단·복합수단 회복력 비교: 송파-부곡리 가상 회랑 사례

*Comparative Resilience of Single-Mode versus Multimodal Reserve-Force Mobilization Transport via Industrial-Engineering Tools: A Songpa-Bugok-ri Virtual Corridor Case Study*

---

## 국문초록

상비전력과 예비전력의 통합 운용을 전제로 하는 동원수송체계의 회복력은 평시 도로망 취약성과 결합되어 정량적 평가가 어렵다. 본 연구는 산업공학의 짝지은 공통난수(paired CRN), 검열 인식(censoring-aware) 지표, Morris 기초효과 민감도, 2단계 실험설계(DoE)를 결합한 통합 프레임워크를 송파↔양주 부곡리 가상 회랑(OSMnx 기반)에 적용하여 단일수단(버스)과 복합수단(철도-버스)의 회복력을 비교한다. SimPy 이산사건 시뮬레이터를 활용해 도로 장애 격자 35셀(Phase 1, 셀당 R=10, 총 350회 짝지은 실행)과 정책 격자 28셀(Phase 2, 셀당 R=10), 그리고 원점 강건성 보조 격자(R=5)를 평가하였다. 미보정 계획 프록시 조건에서 단일수단은 Phase 1의 35개 셀 전부에서 페널라이즈드 메이크스팬이 더 낮았으며(예: s=1.0, p_fail_scale=0.5에서 $\bar{\delta}=-41.75$분; s=1.0, p_fail_scale=1.0에서 $\bar{\delta}\approx-1.44\times10^5$분), $p_{\mathrm{fail,scale}}\geq 1.0$ 영역에서는 두 모드의 raw 완료율이 비대칭적으로 갈려 단일수단이 0.1~0.2 포인트 더 높았다(예: $s=1.0$, $p=2.0$에서 단일수단 0.30 대 복합수단 0.10). Morris 분석은 14개 매개변수에 대한 다지표 평균 μ* 기준으로 **passenger_volume, direct_bus_fleet_size, dispatch_interval**을 페널라이즈드 메이크스팬의 상위 3개 인자로 식별하였다(〈표 5〉). 결과는 운용 권고가 아닌 조건부 break-even 지도(condition map)로 보고되며, 모든 매개변수는 미보정 계획 프록시 상태이다.

**핵심어:** 이산사건 시뮬레이션; 예비군 동원수송; 짝지은 공통난수; 검열 인식 지표; Morris 민감도 분석

---

## English Abstract

Korean reserve-force mobilization transport must move large cohorts to designated training sites within a fixed time window, yet operational data are restricted and the relative resilience of single-mode (direct bus) versus multimodal (rail-bus) systems remains unverified for external researchers. This study applies four industrial-engineering tools — paired Common Random Numbers (CRN), censoring-aware performance metrics, Morris elementary-effects sensitivity, and a two-phase Design of Experiments — to a virtual Songpa-to-72nd-Division corridor abstracted from OpenStreetMap. A SimPy-based discrete-event simulator is exercised over a Phase 1 5×7 disruption grid (35 cells × R = 10 = 350 paired runs) and a Phase 2 4×7 policy grid (28 cells × R = 10), with paired CRN seeds equalising road-failure draws, arrival times, and background traffic across modes. Under the planning-proxy parameterisation, the direct-bus mode showed a lower penalized makespan than the multimodal mode in all 35 Phase 1 baseline cells (e.g., $\bar{\delta}=-41.75$ min at $s=1.0$, $p_{\mathrm{fail,scale}}=0.5$; $\bar{\delta}\approx-1.44\times 10^{5}$ min at $s=1.0$, $p_{\mathrm{fail,scale}}=1.0$); under heavier pressure ($p_{\mathrm{fail,scale}}\geq 1.0$) the bus completion rate exceeded the multimodal rate by 0.10–0.20 points (e.g., 0.30 vs 0.10 at $s=1.0$, $p=2.0$). Morris screening, averaged across seven outputs × two policies × two scenarios, ranked **passenger_volume, direct_bus_fleet_size, and dispatch_interval** as the leading drivers of penalized makespan (Table 5). Results are reported as a conditional break-even map, not an operational recommendation; all parameters remain uncalibrated planning proxies pending follow-up validation.

**Keywords:** discrete-event simulation; reserve-force mobilization transport; paired common random numbers; censoring-aware metric; Morris sensitivity analysis

---

## 1. 서론

### 1.1. 연구 배경

대한민국의 국방태세는 상비전력과 예비전력의 통합 운용을 전제로 한다. 「병역법」 및 「예비군법」에 따라 편성되는 예비군은 전시·사변·국가비상사태 시 신속히 동원되어 전방 보충 및 후방 방어 임무를 수행하는 핵심 인적자원이다 [1]. 병무청 공개 자료에 따르면 동원지정 인력은 「병력동원소집통지서」를 통해 개별 통지된 시각·장소에 입영하며, 72보병사단 부곡리 동원훈련장(경기 양주 장흥 부곡리 산 6-17)을 비롯한 전국의 동원사단 훈련장이 그 입영 거점으로 운용된다 [1]. 동원훈련은 2박 3일 일정이며 12시 정시 입영을 기준으로 1시간의 지연입소 허용 시한이 공시되어 있다 [1].

이러한 동원 절차의 실효성은 평상시 행정 동원 단계에서뿐 아니라 전시 도로망이 부분적으로 손상되거나 통제되는 상황에서 더욱 중요하게 부각된다. 수도권 남동부에서 경기 북부 동원훈련장으로 연결되는 회랑은 올림픽대로, 강변북로, 서울외곽순환고속도로 등 소수의 주요 간선도로에 의존한다. 이 간선도로 망은 평시에도 출퇴근 시간 정체와 사고로 인한 단발성 통행 차단에 취약하며, 전시 또는 대규모 재난 시에는 그 취약성이 더욱 증폭될 수 있다 [3, 4]. 〈그림 1〉은 본 연구가 가정하는 전시 예비군 수송체계의 개념도로, 도시 집결지(송파구 내 가상 출발지)에서 동원훈련장(72보병사단 부곡리)까지의 단일수단 버스 직송과 철도-버스 복합수단 환승의 두 가지 대안적 수송체계를 도식화한다.

본 연구는 송파구 내 네 개 가상 집결지로부터 양주시 장흥면 부곡리에 위치한 72보병사단 동원훈련장에 이르는 약 40~50 km의 주요 간선도로 회랑을 분석 대상으로 한다. 집결지(Origin) A·B·C는 각각 송파구청 일자리센터 앞(37.5147 N, 127.1057 E), 삼전동 구민회관 앞(37.5036 N, 127.0857 E), 장지역 4번 출구 앞(37.4784 N, 127.1262 E)으로 송파구 조례 및 보도자료에서 공개적으로 확인되는 예비군 수송버스 집결지이다 [2]. 단, 해당 집결지들은 평시 예비군훈련용으로 지정된 지점이며 동원훈련 집결지 지정 여부는 공개 자료로 확인되지 않으므로, 본 연구에서는 이를 동원훈련 수송 시나리오에 가상으로 적용한다. 추가로 (D) 잠실종합운동장(37.5159 N, 127.0727 E)은 도시계획상의 대규모 집결 가능 공간으로서 비교 시나리오에 포함하되, 「병력동원 집결지」로서의 공식 지정 여부가 공개 자료에서 확인되지 않으므로 본 논문에서는 **출처 미확인 가정 변형(unverified illustrative variant)**으로 명시한다.

〈그림 1〉 부근의 전시 예비군 수송체계 개념도는 본문 마지막 〈그림 1〉에 표시한다.

**〈그림 1〉** 전시 예비군 수송체계 시뮬레이션 개념도. 송파구 가상 집결지(A·B·C·D)에서 출발하는 단일수단 버스 직송과 철도-버스 복합수단 환승의 두 대안적 수송체계를, 72보병사단 부곡리 동원훈련장까지의 주요 간선도로 회랑 위에서 도식화한다. (자료원: 본 연구 자체 작성, `figure1_concept.png`)

### 1.2. 문제 인식

동원수송체계의 회복력(resilience)을 정량적으로 평가하려면 (i) 평시 운용 실적 자료, (ii) 도로망의 시간대별 용량·자유속도, (iii) 철도·버스 환승 시각표, (iv) 동원지정 자원의 행정구역별 배정 정보가 모두 확보되어야 한다. 그러나 한국에서 이들 자료 중 다수는 보안상의 사유로 공개 범위가 제한되어 있다. 특히 동원지정 자원의 행정구역별 배정은 「병력동원소집통지서」로 개별 고지되며 공개 자료로 검증할 수 없고 [1], 사단별 실제 수송 실적·통과 시간 자료 역시 공개되지 않는다. 이러한 정보 비대칭은 군사적 의의가 큰 동원수송 문제임에도 불구하고, 외부 연구자의 정량적 의사결정 지원 분석을 제한하는 구조적 제약이 된다.

또한 도로망 장애 시 단일수단(버스 직송)과 복합수단(철도-버스 연계)의 상대적 신뢰성은 사전 직관에 의해 단정하기 어렵다. 일반적으로 복합수단은 환승 손실과 일정 의존성이라는 비용을 수반하지만, 도로 일부 구간이 차단되었을 때 우회 경로를 제공한다는 장점을 갖는다 [5]. 반대로 단일수단은 환승 손실이 없으나 회랑이 차단되면 전체 시스템이 한꺼번에 영향을 받는다. 두 대안의 비교 우위는 (a) 장애의 강도와 빈도, (b) 가용 차량·열차 자원, (c) 출발 정책(엄격 출발 STRICT 대 유예 출발 GRACE), (d) 집결 지연 분포에 따라 가변적이다. 따라서 어느 한 수단을 일률적으로 권고하기보다는, 어떤 조건에서 어느 수단이 우위에 있는가를 보여 주는 조건 지도(condition map)가 의사결정자에게 더 유용한 산출물이 된다 [6, 7].

이 같은 문제의식 위에서, 본 연구는 산업공학 방법론을 적용하여 실 데이터 보정 없이도 회복력 평가의 정량적 기반을 제시하고자 한다. 구체적으로 (i) 통제실험 설계(controlled experiment design)를 통해 모형 외 잡음의 영향을 제거하고, (ii) censoring-aware 지표 체계를 통해 시한 내 미도착 인원을 일급(first-class) 결과로 다루며, (iii) 민감도 분석을 통해 결과의 강건성과 주요 인자를 식별한다. 본 연구가 사용하는 도로 용량·자유속도·차량 수·헤드웨이·환승 시간 등의 모수는 모두 공개된 계획 가정에 근거한 값이며, 실세계 보정은 후속 연구의 과제로 명시적으로 유보한다.

### 1.3. 연구 목적

본 연구의 목적은 다음과 같다.

**목적 1 (방법론 적용).** 산업공학 분야에서 정립된 네 가지 도구 — 짝지은 공통난수(paired CRN), censoring-aware 성과 지표, Morris 기본효과(elementary effects) 민감도 분석, 2단계 실험설계(two-phase DoE) — 를 군 동원수송체계 평가 문제에 적용한 통합 프레임워크를 구축한다. paired CRN은 동일 장애 실현과 동일 도착 시각에 대해 두 수단을 짝지어 비교함으로써 무작위 변동의 영향을 제거하며, censoring-aware 지표는 시한(병무청 12시 입영 + 1시간 지연입소 허용) 내 미도착 인원을 결과 변수로 명시적으로 추적한다 [8, 9].

**목적 2 (정량 비교).** 송파구 가상 집결지 A·B·C·D에서 72보병사단 부곡리 동원훈련장에 이르는 주요 간선도로 가상 회랑에서, 단일수단(버스 전용)과 복합수단(철도-버스)의 회복력을 도로 장애 강도 sweep(Phase 1)와 출발 정책·집결 지연 분포 sweep(Phase 2)에 걸쳐 비교한다. 결과는 (a) 두 수단 간 완료 시간 차이, (b) 미도착률, (c) 페널티 완료 시간(penalized makespan), (d) 인원당 차량·자원 시간으로 보고한다.

**목적 3 (조건 지도).** 단일수단과 복합수단의 상대적 우위가 뒤집히는 break-even 곡선을 도로 장애 강도 축 위에서 식별하고, 출발 정책(STRICT/GRACE) 및 집결 지연 분포와의 상호작용을 정량화한다. 이를 통해 어떤 조건에서 어느 수단이 우위에 있는가를 보여 주는 정책 trade-off 지도를 산출한다.

**목적 4 (재현 가능한 공개 프레임워크).** 결정적 난수 시드(deterministic seeds), 매니페스트, 청정 체크아웃 스모크(clean-checkout smoke) 등을 포함한 재현성 패키지를 제공하여, 향후 실 데이터 보정을 통한 후속 연구가 동일한 분석 골격을 재사용할 수 있도록 한다.

### 1.4. 연구 의의 및 기여

본 연구의 기여는 군사학과 산업공학의 학제간 위치 위에서 다음과 같이 정리된다.

**첫째, 학제간 의의.** 군 동원수송 문제는 전통적으로 군사 운용 분석(Operations Analysis)의 영역에 속하였으나, 그 분석 자료의 공개 제약이 외부 연구자의 정량적 검증을 제한하여 왔다. 본 연구는 실 데이터 보정 없이도 산업공학의 통제실험 설계와 시뮬레이션 방법론을 통해 의사결정 지원의 정량적 기반을 마련할 수 있음을 보인다. 이는 군사학 연구에 산업공학적 엄밀성을 도입하는 동시에, 산업공학 연구에 국방 도메인의 실질적 문제 영역을 제공하는 양방향 기여를 갖는다.

**둘째, 시뮬레이션 기반 의사결정지원 프레임워크.** 본 연구가 제시하는 paired CRN + censoring-aware 지표 + Morris + 2단계 DoE 결합 프레임워크는 특정 회랑이나 특정 사단에 국한되지 않고, 다른 군사 수송 문제(전시 후송, 장비 후속 수송, 민·관·군 협동 작전 등)에 재적용 가능한 일반 구조를 갖는다. 단일 권고가 아닌 조건 지도를 산출한다는 점이 의사결정자에게 유연성을 제공한다.

**셋째, 공개 자료 기반 분석 원칙.** 본 연구는 병무청이 공식적으로 공개한 동원훈련장 주소·규정, 송파구 조례·보도자료를 통해 확인되는 집결지 정보, OpenStreetMap에서 추출한 도로망 위상(topology)만을 입력으로 사용한다. 군사 시설의 내부 배치, 부대 정원, 동원지정 자원의 행정구역별 배정 등 비공개 정보는 분석 대상에서 의도적으로 배제한다. 이러한 공개 자료 기반 원칙은 군 기관의 보안성 검토 절차와 양립 가능하며, 학술 커뮤니티의 검증 가능성을 보장한다.

**넷째, 후속 보정 연구의 기반.** 본 연구의 가상 회랑 결과는 단일 권고가 아닌 조건 지도이므로, 향후 실 도로 용량, 실 철도 시각표, 실 동원지정 자원 배정 자료가 보정 단계에서 확보될 경우, 동일한 실험 골격 위에서 결과를 갱신하고 정밀화할 수 있다.

### 1.5. 연구 범위 및 한정 사항

연구 범위와 한정 사항은 5장(결론 및 향후연구)에서 다시 정리하되, 다음 사항은 서론에서 미리 명시한다. 첫째, 본 연구가 분석하는 송파↔부곡리 회랑은 가상 사례이다. 실제 송파구 거주 동원 자원이 72보병사단으로 배정되는지의 여부는 공개 자료로 검증할 수 없으며, 본 연구는 이를 예시적(illustrative) 회랑으로 다룬다. 둘째, 도로 용량·자유속도·차량 수·헤드웨이·환승 시간·철도 시각표는 모두 공개된 계획 가정이며, 실 측정값으로 보정되지 않았다. 셋째, 본 연구의 산출물은 운용 경로 계획이나 부대 운용 지침이 아니라, 산업공학 방법론을 통해 도출된 조건 지도이다.

### 1.6. 논문의 구성

본 논문은 다음과 같이 구성된다. 2장에서는 동원·재난 수송과 복합수단 회복력 평가에 관한 선행연구를 검토한다. 3장에서는 연구 방법으로 (i) 시뮬레이터 구조, (ii) 송파↔양주 부곡리 가상 회랑의 네트워크 구성, (iii) 2단계 paired CRN 실험설계, (iv) censoring-aware 성과 지표 체계, (v) Morris 민감도 분석을 설명한다. 4장에서는 Phase 1(도로 장애 sweep), Phase 2(정책·집결 지연 sweep), 원점 강건성, Morris 분석 결과를 차례로 제시한다. 5장에서는 결과의 군사적 함의, 의사결정 시사점, 본 연구의 한계, 그리고 실 데이터 보정을 향한 후속 연구의 방향을 논의한다.

---

## 2. 선행연구

본 절은 (1) 군 동원 및 인적자원 수송, (2) 재난·복구 시 도로망 신뢰성, (3) 이산사건 시뮬레이션 기반 수송체계 분석, (4) 짝지은 공통난수(paired CRN), (5) 검열(censoring)을 반영한 수송 성과지표, (6) Morris 기초효과 민감도, (7) OSMnx 기반 도로망 추출, (8) 운영연구에서의 손익분기 분석을 차례로 검토한다.

### 2.1 군 동원 및 인적자원 수송

군 동원(mobilization) 수송은 평시 대중교통 분석과 다르게 (i) 짧은 시간창(time window) 안에 대규모 인원을 정해진 집결지로 이동시켜야 하며, (ii) 미도착 인원의 비용이 평균 도착시간 증가보다 비대칭적으로 크고, (iii) 도로·철도 일부 구간의 사용 가능성이 평시와 다르다는 특성을 갖는다. 국내 예비군 동원체계의 운영 골격(2박 3일 동원훈련, 12:00 입영 및 1시간 지연입소 허용 등)은 병무청이 공개하고 있으며 [1], 송파구를 비롯한 자치구는 「예비군 수송버스 운행 조례」를 통해 집결지·차량 운영의 행정 절차를 규정한다 [2]. 다만 행정구역별 동원지정 자원 배치는 「병력동원소집통지서」로 개별 고지되어 공개 자료로는 검증할 수 없는 한계가 있다.

국제적으로는 군 동원과 직접 비교 가능한 사례가 제한적이어서, 본 연구는 인접 문헌인 대규모 대피·소개(evacuation) 연구를 보조적으로 참고한다. Murray-Tuite & Wolshon [3]은 도시 대피 모형의 수송수단·시간·정책 차원을 종합적으로 정리하였고, Liu et al. [4]은 시간창 제약 하의 단계적 대피(staged evacuation)를 시뮬레이션으로 평가하였다. 두 문헌 모두 (i) 도착시간 평균만으로는 미도착 위험을 평가할 수 없고, (ii) 정책 변경(시간창, 출발 규칙)이 수송수단 선택보다 큰 효과를 낼 수 있음을 보고한다는 점에서 본 연구의 검열 인식 지표 및 STRICT/GRACE 정책 비교와 동일한 문제의식을 공유한다.

### 2.2 재난·복구 시 도로망 신뢰성 및 우선순위화

도로망의 신뢰성·취약성(reliability/vulnerability) 연구는 단일 간선의 차단 또는 용량 저하가 망 전체의 통행시간과 접근성에 미치는 영향을 정량화하는 분야로 발전해 왔다. Berdica [5]는 도로망 취약성을 "사회적 사용성(serviceability)의 변화 가능성"으로 정의하면서, 평시 신뢰성 측정과 비상시 취약성 평가를 구분할 것을 제안하였다. Jenelius et al. [6]은 단일 링크 제거 후의 일반화 통행비용 증가를 중요도(importance) 지표로 활용하여, 적은 수의 간선이 망 전체 비용에 비대칭적으로 큰 영향을 미친다는 사실을 보였다. Taylor [7]는 접근성 손실(accessibility loss) 기반 지표가 단순 거리 기반 지표보다 사회·경제적 영향을 더 직접적으로 반영한다고 주장하였다.

군사·재난 맥락에서는 망 전체의 일반 통행이 아니라 특정 OD 쌍의 시간 내 도달 가능성이 결정적이다. Mattsson & Jenelius [10]는 신뢰성·취약성 문헌을 종합하면서, 정책 결정에 사용 가능한 지표 집합으로 ① 우회 통행시간, ② 단절된 OD 쌍 비율, ③ 잔여 용량 기반 V/C, ④ 대안 경로 가용성을 제시한다.

### 2.3 이산사건 시뮬레이션 기반 수송체계 분석

이산사건 시뮬레이션(discrete-event simulation, DES)은 차량·승객·정류장·환승점을 명시적인 자원(resource)과 사건(event)으로 모형화하는 데 적합한 패러다임이다. Law [8]는 DES 기반 운영 연구의 입력 모형, 출력 분석, 분산 감소 기법을 표준적으로 정리하였으며, Banks et al. [11]은 시스템 사용·자원 경합·대기열 길이를 핵심 출력으로 다루는 DES 설계 원칙을 제시하였다.

Python 생태계에서는 SimPy [12]가 가장 널리 사용되는 프로세스 기반 DES 프레임워크로 자리잡았다. SimPy는 차량 함대(fleet)를 `Resource`로, 승객을 `Process`로 표현하여 유한 자원·대기·환승·재시도와 같은 본 연구의 핵심 동학을 직접 표현할 수 있게 한다. Boeing & Wang [13]은 도로망 그래프를 NetworkX로 표현한 뒤 SimPy 등 외부 시뮬레이터와 결합해 도시 수송 시나리오를 평가하는 워크플로우의 실용성을 보였다. 본 연구는 이러한 결합(OSMnx → NetworkX → SimPy-스타일 도메인 모형)을 그대로 차용하되, 군 동원 맥락에 맞도록 마감시각(time horizon) 제약과 검열 인식 지표를 추가한다.

### 2.4 짝지은 공통난수(Paired Common Random Numbers)

분산 감소(variance reduction)는 시뮬레이션 출력의 신뢰구간을 좁히기 위한 표준 기법군이며, 그 중 공통난수(CRN)는 서로 다른 시스템 구성(여기서는 버스 단일수단 대 철도-버스 복합수단)을 같은 외생 확률 표본(arrival 시간, 도로 차단 표본, 배경 교통량 등)에 대해 동시에 평가함으로써 비교의 분산을 줄이는 방법이다. Glasserman & Yao [14]는 CRN이 양(positive)의 효과를 보장받기 위한 충분 조건(단조성·동일성)을 형식화하였고, Law [8]는 짝지은 비교(paired-t) 신뢰구간을 CRN 적용의 표준 출력 분석으로 권고한다. Nakayama [15]는 추정량 단조성이 깨질 수 있는 시나리오에서 CRN의 효과 검정 방법을 정리한다.

### 2.5 검열을 반영한 수송 성과지표

평균 또는 중위 완료시간만으로 수송체계를 평가할 경우, 시간창 내에 도착하지 못한 인원(미도착·검열된 관측치)이 평균 계산에서 묵시적으로 제거되어 빠르지만 누락이 큰 시스템이 과대평가되는 편향이 발생한다. 이러한 우편 검열(right-censoring) 문제는 본래 생존분석(survival analysis)에서 정밀하게 다루어진 주제이다. Kaplan & Meier [9]의 생존함수 추정량은 검열된 관측치를 명시적으로 반영하여 사건 발생률을 추정하며, Klein & Moeschberger [16]는 검열 메커니즘이 생략될 때의 편향을 체계적으로 정리한다.

운영연구·일정관리 문헌에서는 동일한 문제의식이 벌점 메이크스팬(penalized makespan) 또는 마감시각 위반 비용 형태로 등장한다. Pinedo [17]는 마감시각 제약 하의 작업 일정 모형에서 makespan과 누적 지연(total tardiness)을 분리해 보고할 것을 권고하며, Hall & Posner [18]는 마감시각 위반이 평균 통계에 미치는 비대칭 효과를 분석한다.

### 2.6 Morris 기초효과 민감도 분석

다인자 시뮬레이션의 매개변수가 결과에 미치는 영향을 체계적으로 평가하기 위해서는 정식 민감도 분석이 필요하다. Sobol' 지수 [19]가 분산 분해 기반의 정량적 영향력을 제공하지만 계산 비용이 크기 때문에, 사전 선별(screening) 단계에서는 Morris의 기초효과 설계 [20]가 표준이다. Campolongo et al. [21]은 원래의 Morris 설계를 개선한 균등분포 기반 trajectory 생성 및 $\mu^*$ 지표를 제안하였다. Python에서는 SALib [22]가 Morris·Sobol'·FAST·PAWN 등 주요 민감도 방법을 모듈화한 라이브러리로 자리잡았다.

### 2.7 OSMnx 기반 도로망 추출

도로망 기반 분석을 위해서는 노드·간선·속성이 표준화된 그래프 추출 도구가 필요하다. Boeing [23]의 OSMnx는 OpenStreetMap(OSM)에서 임의 영역의 도로망을 추출·단순화·NetworkX 그래프로 변환하는 오픈소스 도구로서, 자유속도·통행시간·도로 등급 등 속성 부여를 자동화한다. OSMnx는 학계에서 도시·지역 수송망 분석의 사실상 표준 추출 도구로 정착하였으며 [13], 본 연구도 송파↔양주 회랑의 주요 간선 부분망 추출에 OSMnx를 사용한다. 다만 OSM 데이터 자체는 (i) 신뢰할 수 있는 통행량·용량 정보를 제공하지 않고, (ii) 군사 관련 도로 정보가 제한적이며, (iii) Overpass API의 가용성과 라이선스 의무를 고려해야 한다는 한계가 있어, 본 연구는 OSMnx 추출 결과를 교통 모형이 아닌 가상 회랑 추상화로 위치 짓는다.

### 2.8 운영연구·산업공학에서의 손익분기 분석

손익분기(break-even) 분석은 두 대안의 성과 지표 곡선이 교차하는 지점을 찾아 어느 조건에서 어느 대안이 우월한지를 시각화하는 고전적 방법이다. Hillier & Lieberman [24]은 운영연구 입문 교재에서 손익분기 분석을 비용 구조 비교의 표준 도구로 제시하며, Sullivan et al. [25]의 공학경제학 교재는 다인자 시뮬레이션 결과를 정책 의사결정에 연결할 때 손익분기 곡선이 가지는 해석상의 장점을 강조한다.

### 2.9 종합 및 본 연구의 기여 위치

종합하면, 본 연구는 (a) 군 동원·대피 수송의 시간창 제약 인식 [1]–[4], (b) 도로망 취약성 평가의 OD 중심 시각 [5]–[7, 10], (c) DES 기반 자원·대기열 표현 [8, 11–13], (d) CRN 분산 감소 [14, 15] 및 검열 인식 지표 [9, 16]–[18], (e) Morris 민감도 [19]–[22], (f) OSMnx 도로망 추출 [13, 23], (g) 손익분기 기반 조건 지도 [24, 25]의 갈래를 결합한다. 각 갈래의 개별 기법은 새로운 것이 아니며, 본 연구의 방법론적 기여는 이들을 예비군 동원수송 회복력 평가라는 단일 군사 물류 문제에 정합적으로 적용한 통제실험 IE 프레임워크에 있다. 국문 학술 문헌에서 검열 인식 지표·짝지은 CRN·Morris 민감도를 모두 결합한 군 수송 사례 연구는 현재까지 확인되지 않는다.

---

## 3. 연구방법

본 장은 송파구–양주 부곡리 회랑 위에서 단일수단(버스 전용)과 복합수단(철도–버스)의 회복력을 통제실험으로 비교하기 위해 구축한 시뮬레이션·실험·민감도 분석 체계를 기술한다. 방법론 골격은 (i) SimPy 기반 이산사건 시뮬레이터, (ii) OSMnx로 추출한 주요 간선 가상 회랑, (iii) Paired CRN 기반 두 단계 DoE, (iv) Morris elementary-effects 민감도 분석의 네 축으로 구성된다. 모든 매개변수 값은 미보정 계획 프록시(planning proxy)이다.

### 3.1 시뮬레이터 구조

본 시뮬레이터는 Python 3.11 환경에서 SimPy [12]의 이산사건 패러다임을 채택하여, 인원 도착·차량 디스패치·도로 통행·환승·열차 운행을 모두 명시적 사건 단위로 처리한다. 시뮬레이터는 추상 네트워크 `H/A/S/R/D` 노드 계약(H: 출발 허브, A: 집결지, S: 철도 승차역, R: 철도 하차역, D: 최종 목적지)을 따른다. 본 KCI 연구에서 `A`는 송파구 집결지 후보(§3.2), `D`는 72사단 부곡리 동원훈련장, `S/R`는 잠실역·의정부역에 각각 스냅된다.

**동적 교통 모형(BPR-at-departure).** 도로 통행시간은 출발시각 기준 BPR 함수로 결정된다.

$$
t(v) = t_0 \cdot \left[ 1 + \alpha \left( \frac{v}{C} \right)^{\beta} \right]
$$

여기서 $t_0$는 자유 통행시간(분), $v$는 배경 교통량(rolling 60분 윈도), $C$는 directional capacity(veh/h), $(\alpha, \beta) = (0.15, 4.0)$은 표준 미국연방도로국(FHWA) 권장값을 따른다. 차량은 배차 시각에 한 번 통행시간을 산정하고, 도중 재산정은 하지 않는다(*static-at-dispatch*).

**Fleet / Dispatch / Rail / Last-mile 모듈.** 차량 운용은 `fleet.py`(유한 차량 가용성), `dispatch.py`(대기열 기반 승객 디스패치), `rail.py`(고정 헤드웨이 철도), `transfers.py`(환승 지연 산정)의 네 모듈로 분리된다. 단일수단 시나리오는 `A→D` 직행 버스 단일 회로를 사용하고, 복합수단 시나리오는 `A→S` 셔틀 → `S→R` 열차 → `R→D` last-mile 버스의 3단 회로를 직렬 연결한다.

**Censoring-aware 지표.** 총 인원 $N$이 시간 제한 $T_{\max} = 1440$분 내에 모두 도착하지 못할 수 있으므로 단일 makespan만으로는 빠르지만 누락이 많은 시나리오가 호도된다. 따라서 본 연구는 다음을 1차 지표로 채택한다.

- **censored_count**: $T_{\max}$ 내에 $D$에 도착하지 못한 인원 수.
- **penalized_makespan**:

$$
M_{\mathrm{pen}} = \max(M_{\mathrm{obs}}, T_{\max}) + n_c \cdot \pi
$$

여기서 $M_{\mathrm{obs}}$는 관측된 마지막 도착시각, $n_c$는 censored_count, $\pi = 1440$분(`late_penalty_min`)은 누락 1인당 부과 페널티이다. $n_c = 0$이면 $M_{\mathrm{pen}} = M_{\mathrm{obs}}$로 환원된다. 부가 지표로 95퍼센타일 도착시각, 도로 차량-분(road vehicle-minutes), 1인당 총 서비스 분(passengers per total service minute) 등이 계산된다.

### 3.2 가상 송파-부곡리 회랑

**OSMnx bbox 추출.** 도로망은 OSMnx [23]를 사용하여 위도 37.46–37.78°N, 경도 126.85–127.20°E 범위에서 추출하였다. 이 bbox는 송파구의 네 집결지 후보를 모두 남단에 포함하고, 양주 장흥 부곡리 동원훈련장(약 37.74 N / 126.95 E)을 북단에 포함하며, 사이를 잇는 올림픽대로·강변북로·서울외곽순환·1번 국도 연결구간을 충분히 포함하도록 설정되었다. 추출 결과는 `data/cache/songpa_yangju_corridor.graphml`에 GraphML 형식으로 캐시되어 모든 후속 실험이 동일한 그래프 스냅숏을 재사용하도록 보장한다. 〈그림 2〉는 본 회랑의 지리적 구성을 표시한다.

**주요 간선 필터링.** `src/realworld/adapter.py`의 `ROUTEABLE_HIGHWAY_CLASSES` 집합을 `{motorway, motorway_link, trunk, trunk_link, primary, primary_link, secondary, secondary_link}`로 제한하였다. 이는 본 연구가 주요 간선 회랑 추상화에 명시적으로 한정됨을 의미하며, 보행·자전거·생활도로 등 비차량 OSM 지오메트리가 버스 경로로 침투하는 것을 방지한다. 평행 도로 엣지는 결정론적 규칙(① $t_0$ 최소, ② capacity 최대, ③ `base_p_fail` 최소, ④ 안정적 edge ID)으로 1개만 선택된다. 어댑터 결과 본 회랑은 18,213개 노드 / 29,542개 directed 엣지로 구성된다.

**정규 노드 매핑.** 어댑터는 region YAML에서 정의된 지리적 좌표를 가장 가까운 routeable OSM 노드에 스냅하고 양방향 connector 엣지(기본 connector_speed_kph = 30, connector_capacity = 600)를 추가한다. 정규 노드(`A`, `S`, `R`, `D`)는 `_validate_required_routes`에 의해 `A→D`, `A→S`, `R→D` 경로가 모두 가능함을 확인한 뒤에야 시뮬레이션에 투입된다.

**Origin 4개 후보.** 집결지는 다음 네 위치(`data/regions/origin_candidates.json`)에 대해 검증된다.

| ID | 명칭 | 위도 | 경도 | 검증 |
|----|------|------|------|------|
| A | 송파구청 일자리센터 | 37.5147 | 127.1057 | 검증 (송파구 조례 2023-09-14, 한국경제 2024-02-29 보도) |
| B | 삼전동 구민회관 | 37.5036 | 127.0857 | 검증 (송파구 조례 2023-09-14, 한국경제 2024-02-29 보도) |
| C | 장지역 4번 출구 | 37.4784 | 127.1262 | 검증 (송파구 조례 2023-09-14, 한국경제 2024-02-29 보도) |
| D | 잠실종합운동장 | 37.5159 | 127.0727 | **출처 미확인 가정 변형** |

A·B·C는 송파구 조례 및 보도자료 [2]에 명시된 예비군 수송버스 집결지이며 본 연구에서는 동원훈련장 수송에 유추 적용된다(역할 차이는 §3.9에서 언급). 후보 D(잠실종합운동장)는 어떠한 공개 자료에서도 병력동원 집결지로 확인되지 않았으며, 본 연구에서는 robustness 가정 변형으로만 사용된다. 목적지는 병무청이 공개적으로 게시한 72사단 부곡리 동원훈련장 단일 지점이다 [1].

**〈그림 2〉** 송파-부곡리 예비군 동원 회랑(가상 간선도로 회랑)의 지리적 구성. OSM 기반 캐시 그래프에서 간선도로(motorway·trunk·primary·secondary 및 _link)만 강조하여 표시하고, 송파 측 4개 후보 기점 A(송파구청 일자리센터)·B(삼전동 구민회관)·C(장지역 4번 출구)·D(잠실종합운동장, **출처 미확인 가정**)과 캐노니컬 종점 D'(72사단 부곡리 동원훈련장, ≈37.74°N 126.95°E), 그리고 철도 접근/이탈 노드 S(잠실역)·R(의정부역, ≈37.738°N 127.046°E)를 함께 표시하였다. (자료원: `figure2_corridor_map.png`)

### 3.3 도로 신뢰성 모델

**HIGHWAY_DEFAULTS.** OSM의 `maxspeed`, `length`, `capacity` 태그는 결손·불일치가 흔하므로 어댑터는 클래스별 결정론적 기본값을 적용한다. 본 회랑에 실제로 등장하는 routeable 클래스에 대한 값은 다음과 같다.

| Highway class | speed_kph | capacity (veh/h, dir.) | base_p_fail |
|---------------|-----------|------------------------|-------------|
| motorway      | 100.0     | 2,200                  | 0.010       |
| trunk         | 80.0      | 1,800                  | 0.015       |
| primary       | 60.0      | 1,400                  | 0.020       |
| secondary     | 50.0      | 1,000                  | 0.025       |
| motorway_link | 60.0      | 1,200                  | 0.020       |
| trunk_link    | 50.0      | 1,000                  | 0.025       |
| primary_link  | 45.0      | 800                    | 0.030       |
| secondary_link| 40.0      | 700                    | 0.035       |

자유 통행시간 $t_0 = L/(v \cdot 1000/60)$($L$: 엣지 길이 m, $v$: speed_kph). **이 값들은 한국 도로 데이터로 보정된 값이 아니라 OR/IE 연구용 결정론적 계획 프록시**이며, §3.9에서 정직하게 언급한다.

**장애 모드.** 본 시뮬레이터의 장애 모형은 두 가지 모드를 지원한다. (i) **blocked**: 선택된 엣지의 통행시간을 $+\infty$로 만들어 라우팅에서 제외. (ii) **capacity_reduction**: 선택된 엣지의 capacity를 $C \leftarrow C \cdot \kappa$로 축소($\kappa = $ `capacity_reduction_factor` $\in [0, 1)$). 장애 발생 확률은 엣지별 `base_p_fail`에 시나리오 스칼라 `p_fail_scale`을 곱하여 결정된다.

$$
p_{\mathrm{fail}}(e) = \min\bigl(1,\, p_{\mathrm{fail,scale}} \cdot p_{\mathrm{base}}(e)\bigr)
$$

본 연구에서 `p_fail_scale = 0`은 결정론적 baseline(장애 없음), 3.0은 가장 강한 압박 조건이다(§3.5).

### 3.4 시나리오 정의

장애 시나리오는 `data/scenarios/disruption_scenarios.csv`에 8개 family로 정의된다. 각 family는 결정론적 선택규칙(hash rank, edge betweenness, shortest-path, station_access, bbox)에 따라 그래프에서 영향 엣지를 식별하므로 동일 seed에서 재현된다. `evidence_class`는 모든 행에서 `scenario_based`이며 어떤 시나리오도 실제 관측 재해 데이터를 표현하지 않는다.

### 3.5 두 단계 DoE 설계

**반복 횟수에 대한 정직한 보고.** 본 연구의 계획 단계(`kci/research_plan.md` §7)는 cell당 $R = 30$ paired CRN 반복을 명시하였다. 그러나 §3.2에서 보인 바와 같이 실제 어댑터 결과 회랑은 18,213 노드 / 29,542 엣지로 본 시뮬레이터의 종전 추상 베이스라인(약 8개 노드)에 비해 현저히 크다. 본 회랑의 cell당 비용이 budget을 초과하므로, 본 연구의 주 스트림은 $R = 30$ 대신 **$R = 10$**으로 축소하여 실험 시간을 budget 내에 수렴시켰다. Morris 민감도 또한 계획상 **200 trajectories 대신 50 trajectories**로 축소하였다(§3.7). origin robustness 보조 스트림은 더 작은 grid에 대해 $R = 5$를 사용한다. paired CRN의 페어링 구조 자체는 보존되므로 단일 cell 내 분산 추정은 비파괴적으로 영향을 받는다. 본 축소는 〈표 1〉의 주석¹로 표기된다.

**Phase 1 — Disruption 격자.**
- 요인 1: 혼잡 스케일 $s$ (배경 교통량 배수): $s \in \{0.8, 1.0, 1.2, 1.5, 2.0\}$, 5수준.
- 요인 2: 장애 강도 $p_{\mathrm{fail,scale}}$: $\{0.0, 0.25, 0.50, 1.00, 1.50, 2.00, 3.00\}$, 7수준.
- 격자 크기: $5 \times 7 = 35$ cell.
- cell당 반복: $R = 10$ paired CRN seed (origin A 주 스트림). 총 35 × 10 = 350회 짝지은 실행.

**Phase 2 — Policy 격자.**
- 요인 1: 집결 지연 스케일 $\sigma$ (lognormal $\sigma$, $\mu = 2.0$ 고정): $\sigma \in \{0.3, 0.5, 0.7, 1.0\}$, 4수준.
- 요인 2: 출발 정책: STRICT 1개 + GRACE($W \in \{15, 30, 60\}$분 × $\theta \in \{0.8, 0.9\}$ 점유율 임계값) → 총 7개 policy.
- 격자 크기: $4 \times 7 = 28$ cell. cell당 $R = 10$ paired CRN.

**Robustness — Origins B/C/D.** 집결지 효과의 강건성을 확인하기 위해, B·C·D 각 origin에 대해 Phase 1 격자를 $2 \times 3$ focused subset($s \in \{1.0, 1.5\}$, $p_{\mathrm{fail,scale}} \in \{0.0, 1.0, 2.0\}$)으로 축소하고 cell당 $R = 5$로 실행한다. **Origin D(잠실종합운동장)의 결과는 출처 미확인 가정 변형으로 표기되며 §3.9의 한계와 함께 보고한다.**

**〈표 1〉** 본 연구의 두 단계 DoE와 Morris 민감도 설계 격자를 다음과 같이 정리한다.

| 단계 (Phase) | 요인 (Factor) | 수준 (Levels) | 수준 수 (k) | 셀 수 (Cells) | R per cell | 총 실행 |
|---|---|---|---|---|---|---|
| Phase 1 (main) | $s$ (수요 배수) | 0.8, 1.0, 1.2, 1.5, 2.0 | 5 | — | — | — |
| Phase 1 (main) | $p_{\mathrm{fail,scale}}$ | 0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0 | 7 | 35 | 10¹ | 350 |
| Phase 2 (main) | $\sigma$ (수요 불확실성) | 0.3, 0.5, 0.7, 1.0 | 4 | — | — | — |
| Phase 2 (main) | 정책 (policy) | STRICT, GRACE_W{15,30,60}_T{0.8,0.9} | 7 | 28 | 10¹ | 280 |
| 강건성 (Robustness) | 원점 × $s$ × $p$ | B,C,D × {1.0,1.5} × {0.0,1.0,2.0} | 6 cells × 3 origins | 18 | 5¹ | 90 |
| Morris 민감도 | 파라미터 수 ($k$) | 14 | 14 | — | — | — |
| Morris 민감도 | 궤적 × 수준 | 50 × 4¹ | — | — | — | 750¹ |

*주.* ¹ 계획된 R=30 → 실행 R=10 (메인 실험), R=5 (강건성 실험); Morris 궤적 200 → 50으로 축소. 축소 사유: 송파 회랑 약 18,000 노드 규모로 인한 단위 시뮬레이션 실행 시간 제약. Morris는 $(k+1) \times T = (14+1) \times 50 = 750$ 표본/구성을 평가.

### 3.6 Paired CRN과 신뢰구간

각 cell의 paired 비교 통계량은 다음과 같다. seed $r \in \{1, \ldots, R\}$에 대하여

$$
\delta_r = \mathrm{pm}^{\mathrm{bus}}_r - \mathrm{pm}^{\mathrm{multi}}_r
$$

여기서 $\mathrm{pm}_r$은 seed $r$에서의 penalized_makespan이다. $\delta_r$의 표본평균과 표본분산을 각각 $\bar{\delta}$, $s_\delta^2$이라 할 때, paired $t$-기반 95% 신뢰구간은

$$
\bar{\delta} \pm t_{0.975,\,R-1} \cdot \frac{s_\delta}{\sqrt{R}}
$$

이다. $\bar{\delta} < 0$이면 단일수단(버스)이 복합수단 대비 빠르다고 해석한다(부호 규약: Δ = bus − multi). $R = 10$에서 $t_{0.975,\,9} = 2.262$로 산출된다. Censoring 페널티는 모든 seed·모드에 동일하게 $\pi = 1440$분이 적용되어 페어링을 깨지 않는다.

### 3.7 Morris elementary-effects 민감도 분석

매개변수의 1차 효과와 비선형성을 선별하기 위해 Morris elementary-effects 방법 [20]을 SALib [22]의 `morris.sample` / `morris.analyze`로 적용하였다. 본 연구의 설계는 `data/scenarios/sensitivity_design.csv`에 명시되며, 본 회랑 시나리오에 적용 가능한 9개 핵심 매개변수에 더해 회랑 외부 시나리오(랭킹 검증용)까지 포함한 **총 14개 매개변수**($k=14$)에 대해 분석된다.

| 매개변수 | 베이스라인 | 하한 | 상한 |
|---------|-----------|-----|------|
| passenger_arrival_variability ($\sigma$) | 0.25 | 0.15 | 0.50 |
| direct_bus_fleet_size | 3 | 1 | 5 |
| feeder_fleet_size | 3 | 1 | 5 |
| last_mile_fleet_size | 2 | 1 | 4 |
| dispatch_interval | 5 | 2.5 | 10 |
| road_background_traffic_multiplier | 1.0 | 0.8 | 2.0 |
| capacity_reduction_factor | 0.50 | 0.25 | 0.75 |
| rail_headway | 10 | 5 | 20 |
| transfer_fixed_delay | 3 | 0 | 10 |
| (보조 5개: turnaround_time, rail_capacity, passenger_volume, transfer_per_passenger_delay, last_mile_access_disruption_probability) | — | — | — |

설계 파라미터는 `num_trajectories = 50`(계획상 200에서 축소; §3.5), `num_levels = 4`, paired CRN seed = 1로 고정한다. Morris 평가지표는 매개변수 $i$의

- $\mu^*_i = T^{-1}\sum_{t=1}^{T} |EE_{i,t}|$: 절대 평균 효과(영향력 순위),
- $\sigma_i$: elementary effect의 표준편차(비선형·상호작용 진단)

이며, $(\mu^*, \sigma)$ 산점도로 선별한다. 본 연구는 14개 매개변수 × 7개 출력 지표 × 2개 정책(`baseline_multimodal`, `bus_only`) × 2개 시나리오의 다지표 평균 $\mu^*$를 정식 canonical 순위로 채택하며, 이는 〈표 5〉의 집계와 일치한다.

### 3.8 재현성

본 연구의 모든 실험은 다음 재현성 장치를 갖추고 있다. (i) `main.py` 상단에서 `PROJECT_ROOT`를 고정하여 `kci/`가 self-contained 실행 루트로 동작한다. (ii) `kci/requirements.txt`에 simpy, networkx, numpy, pandas, PyYAML, matplotlib, seaborn, SALib, osmnx의 정확한 버전 핀이 기록된다. (iii) OSMnx 추출 결과는 단 한 번 GraphML로 캐시되며 동반 매니페스트가 ETag·노드 수·엣지 수·추출일을 기록한다. (iv) `experiment.seed_base = 1`을 기점으로 cell-내 paired seed는 단조 증가하며, 선택 규칙이 결정론적이므로 동일 seed에서 정확한 재현이 보장된다. (v) `scripts/run_reproducibility_smoke.py` 및 `scripts/run_clean_checkout_smoke.py`가 동일 환경에서 두 번 실행했을 때 페어드 평균이 부동소수점 허용오차 내에서 일치함을 확인한다.

### 3.9 방법론 한계

본 연구는 IE/OR 방법론 조건 지도(condition map)로 위치되며, 운영 가이드가 아니다. 다음 한계를 본 절에서 미리 선언한다.

1. **미보정 capacity / p_fail.** §3.3의 `HIGHWAY_DEFAULTS`는 한국 도로 데이터로 보정된 값이 아니라 결정론적 계획 프록시이다. 따라서 본 연구의 mode 비교 결과는 동일 그래프·동일 가정 하에서의 두 모드 차이에 한정되며, 절대 통행시간의 외부 타당성을 주장하지 않는다.
2. **Origin D 출처 미확인.** 잠실종합운동장이 병력동원 집결지로 사용되었음을 확인할 공개 자료는 없다. 본 연구는 사용자의 명시적 지시에 따라 robustness 가정 변형으로만 D를 다루며, 본 origin의 결과는 모든 표·그림에서 별도로 표기된다(§3.5).
3. **A·B·C 역할 차이.** 송파구 조례 2023-09-14 및 한국경제 2024-02-29 보도가 명시하는 세 집결지는 예비군훈련(2박 3일 동원훈련이 아님) 수송버스 집결지로 가동되는 사례이다. 본 연구는 이를 동원훈련장 수송에 유추 적용하며, 정확한 1:1 대응이 아님을 밝힌다.
4. **가상 회랑.** 본 회랑은 OSM의 주요 간선 부분집합에서 추출된 가상 추상 네트워크이며 한국 교통량·신호·차로 폭·우회로 가용성에 대한 보정을 거치지 않았다. 송파→72사단 동원지정 자원 catchment는 공개 자료로 검증할 수 없으므로 본 라우팅은 예시적(illustrative)이며 운영 배정의 주장이 아니다.
5. **추상 철도 leg.** 잠실↔의정부 구간에는 직행 고빈도 노선이 없다. 본 연구의 철도 leg(`S→R`)는 60분 통행시간, 15분 헤드웨이, 1열차당 500인 용량의 추상 장거리 프록시이며, 실제 1호선·7호선·환승 경로의 동적 운행 데이터를 사용하지 않는다.
6. **외부 검증 부재.** OSRM·KTDB·GTFS 등 외부 라우팅 벤치마크와의 통행시간 일치 여부는 본 연구에서 검증하지 않는다. 이는 후속 보정 연구의 과제이다.

---

## 4. 결과

본 장은 §3의 두 단계 실험 설계와 Morris 민감도 분석의 결과를 차례로 제시한다. 모든 수치는 §3.6의 paired CRN 절차에 따라 cell당 동일 seed로 두 모드를 짝지어 산출한 paired delta와 그 95% 신뢰구간을 함께 보고하며, 본 절의 모든 정량적 비교는 §3.9에서 선언된 조건 지도의 해석 경계 내에 한정된다.

### 4.1 Phase 1 break-even 분석 (Origin A)

Phase 1 격자는 $s \in \{0.8, 1.0, 1.2, 1.5, 2.0\}$ × $p_{\mathrm{fail,scale}} \in \{0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0\}$의 5×7 = 35 cell, cell당 $R = 10$ paired CRN seed로 구성된다. 〈그림 3〉은 paired delta penalized makespan $\bar{\delta}_{\mathrm{pm}} = \bar{M}^{\mathrm{bus}}_{\mathrm{pen}} - \bar{M}^{\mathrm{multi}}_{\mathrm{pen}}$의 ($s$, $p$) 격자 위 히트맵이며, 〈표 2〉는 동일 데이터의 paired $t$ 기반 95% CI를 셀별로 정리한다.

**무장애 영역.** $p_{\mathrm{fail,scale}} = 0$의 모든 $s$ 수준에서 단일수단(버스)이 복합수단(철도-버스)보다 약 58분 빠르게 완수된다. $s = 1.0$, $p = 0.0$ cell에서 $\bar{\delta}_{\mathrm{pm}} = -58.51$분이며 paired delta 표본분산이 0에 가깝다. 이 값은 환승 고정지연 + 복합수단 경로의 추가 거리 비용을 반영하는 구조적 환승 페널티로 해석된다.

**중간 압박 영역 ($p \in \{0.25, 0.50\}$).** 양 모드 모두에서 censored_count가 점진적으로 증가하나 두 모드의 censoring이 동일 수준으로 페어드되어 paired delta는 여전히 음의 부호를 유지한다. $s = 1.0$, $p = 0.25$에서 $\bar{\delta}_{\mathrm{pm}} = -53.97$분(95% CI $[-65.81, -42.14]$); $p = 0.50$에서 $\bar{\delta}_{\mathrm{pm}} = -41.75$분(95% CI $[-59.65, -23.85]$)로 단일수단 우위가 통계적으로 유의하다.

**고압박 영역 ($p \geq 1.0$): censoring-driven break-even.** $p_{\mathrm{fail,scale}} \geq 1.0$ 영역에서는 두 모드의 미도착률이 비대칭적으로 갈리면서 paired delta가 대규모 음의 값으로 떨어진다. $s = 1.0$, $p = 1.0$ cell에서 $\bar{\delta}_{\mathrm{pm}} \approx -1.44 \times 10^5$분(95% CI $[-4.27 \times 10^5, +1.38 \times 10^5]$)으로 신뢰구간이 0을 포함한다. 페널티 $\pi = 1440$분이 100명 차이에 곱해진 결과($100 \times 1440 = 144{,}000$분)가 delta의 평균을 지배하지만, seed 간 압박 실현의 변동성이 커서 통계적 유의성은 $R = 10$에서 확보되지 않는다. $p = 2.0$, $s = 1.0$에서는 censoring 격차가 200명으로 확대되어 $\bar{\delta}_{\mathrm{pm}} \approx -2.88 \times 10^5$분(95% CI $[-6.65 \times 10^5, +8.84 \times 10^4]$)이다. 종합하면 본 회랑의 실용적 break-even은 paired makespan 부호가 아니라 **censoring 격차의 부호** 위에서 정의되며, 이 격차는 $p_{\mathrm{fail,scale}} \approx 1.0$ 부근에서 처음 0.1 이상의 양의 값을 띤다(복합수단이 더 많이 미도착, §4.2).

**혼잡 축의 둔감성.** 동일 $p$에 대한 다섯 개 $s$ 수준의 paired delta 차이는 1분 미만으로, 본 회랑에서는 BPR 자유 통행시간 항이 도로 차단 페널티에 비해 1차적으로 무시할 수 있는 규모임을 시사한다. 따라서 〈그림 3〉의 히트맵은 본질적으로 $p$축에 평행한 줄무늬 패턴을 보인다.

**〈표 2〉** Phase 1 원점-A 페널라이즈드 메이크스팬 차이의 평균 및 95% 페어드 신뢰구간(부분 발췌, 전체 35셀은 같은 패턴을 따름).

| $s$ | $p_{\mathrm{fail,scale}}$ | Mean Δ penalized_makespan (분) | 95% CI 하한 | 95% CI 상한 | 유의성 |
|---|---|---|---|---|---|
| 0.8 | 0.00 | -58.51 | -58.51 | -58.51 | 버스 우위 |
| 0.8 | 0.25 | -53.97 | -65.81 | -42.14 | 버스 우위 |
| 0.8 | 0.50 | -41.75 | -59.65 | -23.85 | 버스 우위 |
| 0.8 | 1.00 | -1.44e+05 | -4.27e+05 | +1.38e+05 | 구분 불가 |
| 0.8 | 2.00 | -2.88e+05 | -6.65e+05 | +8.84e+04 | 구분 불가 |
| 1.0 | 0.00 | -58.51 | -58.51 | -58.51 | 버스 우위 |
| 1.0 | 0.50 | -41.75 | -59.65 | -23.85 | 버스 우위 |
| 1.0 | 1.00 | -1.44e+05 | -4.27e+05 | +1.38e+05 | 구분 불가 |
| 1.0 | 2.00 | -2.88e+05 | -6.65e+05 | +8.84e+04 | 구분 불가 |
| 2.0 | 0.50 | -41.75 | -59.64 | -23.85 | 버스 우위 |
| 2.0 | 1.00 | -1.44e+05 | -4.27e+05 | +1.38e+05 | 구분 불가 |
| 2.0 | 2.00 | -2.88e+05 | -6.65e+05 | +8.84e+04 | 구분 불가 |

*주.* Δ = 버스 단독 페널라이즈드 메이크스팬 − 복합수단 페널라이즈드 메이크스팬(분). 음수 = 단일수단(버스)이 더 빠름. 35개 전체 셀이 음의 부호이며, 본 표는 모든 $s$ 수준의 대표 셀만 발췌한다. $p_{\mathrm{fail,scale}}=0$ 셀은 결정론적이므로 신뢰구간 폭이 0이다.

**〈그림 3〉** Phase 1 도로 장애 강도($p_{\mathrm{fail,scale}}$, 7수준)와 교통 혼잡 배수($s$, 5수준)의 35개 셀에 대한 평균 Δ penalized_makespan (Δ = bus − multi) 히트맵. 음수 셀(파란색, n=35)은 **단일수단(버스 단독)이 복합수단보다 페널라이즈드 메이크스팬 측면에서 우수**함을, 양수 셀(붉은색, n=0)은 그 반대를 의미하며, 검은 점선은 두 모드의 성과가 같아지는 손익분기 등고선(Δ=0)을 나타낸다. 본 실험 범위 전체에서 평균 Δ는 음의 값으로 관측되었고(35/35 셀이 음수), 가장 큰 단일수단 우위는 $s=0.8$, $p_{\mathrm{fail,scale}}=2.0$에서 Δ ≈ −288,167분으로 관측되어, 도로 장애 강도가 커질수록 복합수단의 censoring 페널티가 비선형적으로 누적되며 두 모드 간 격차가 확대되는 양상이 뚜렷하다. (자료원: `figure3_breakeven_heatmap.png`)

### 4.2 Phase 1 완수율 곡선

페널티 합산 지표만으로는 censoring 규모가 makespan을 압도하므로, 본 절은 §3.1에서 정의한 raw completion rate를 별도로 보고한다. 〈그림 4〉는 $s \in \{0.8, 1.2, 2.0\}$의 세 단면을 $p_{\mathrm{fail,scale}}$의 함수로 표시한 모드별 완수율 곡선이다.

**완수율 단조 감소.** 두 모드 모두 $p$가 0에서 3.0으로 증가함에 따라 완수율이 단조적으로 감소한다. 단일수단(버스)의 경우 $s=1.0$에서 $1.00 \to 0.90 \to 0.70 \to 0.60 \to 0.40 \to 0.30 \to 0.20$, 복합수단의 경우 $1.00 \to 0.90 \to 0.70 \to 0.50 \to 0.30 \to 0.10 \to 0.10$이다. $p \leq 0.50$에서 두 모드의 완수율은 격자상 0.01의 분해능 내에서 동일하다.

**Bus advantage 발현 구간.** $p_{\mathrm{fail,scale}} \geq 1.0$ 영역에서 단일수단이 복합수단을 0.10~0.20 포인트 차이로 일관되게 앞선다. 격차의 정점은 $p = 2.0$ 부근에서 발생하며 (예: $s=1.0$, $p=2.0$에서 버스 완수율 0.30 대 복합수단 0.10) paired 95% CI는 $R = 10$에서 분산이 큰 이항형 지표라 0을 포함하나, 점추정의 일관된 부호는 5개 $s$ 수준 모두에서 동일하다.

**해석: 환승 노드 의존성.** 본 회랑에서 복합수단이 더 빨리 무너지는 메커니즘은 §3.4의 `rail_station_access` 시나리오 패밀리에서 명시적으로 모형화되어 있다. 잠실역·의정부역 진출입로의 capacity 감소는 셔틀 leg(A→S)와 last-mile leg(R→D)를 동시에 압박하므로, 단일수단의 단일 경로 차단보다 시스템 차원의 손실이 누적되기 쉽다. 즉 본 결과는 철도 leg의 추상 프록시 가정 하에서도 환승 노드의 도로 접근성이 복합수단 회복력의 1차적 병목임을 시사한다.

**〈그림 4〉** Phase 1 도로 장애 강도별 완수율 비교(Bus vs Multimodal). 도로 링크의 장애 강도($p_{\mathrm{fail,scale}}$, 0.0~3.0)를 증가시키며 버스 단일 정책(점선·원형 마커)과 복합수단 정책(실선·사각형 마커)의 임무 완수율을 비교한다. 혼잡 강도($s$)는 가독성을 위해 세 가지 기준값만 표시한다(저혼잡 $s=0.8$, 기준 $s=1.2$, 고혼잡 $s=2.0$). 음영대는 동일 시드 쌍을 공유하는 10회 반복에 대한 95% 신뢰구간이다. $p_{\mathrm{fail,scale}}=0$에서는 두 정책 모두 1.0의 완수율을 보이지만, 장애 강도가 증가할수록 복합수단의 완수율 하락 폭이 단일수단보다 더 크게 나타나며($s=1.2$, $p_{\mathrm{fail,scale}}=2.0$에서 Bus 0.30 vs Multimodal 0.10), 본 시나리오 하에서 복합수단 경로의 도로 의존 구간이 장애에 더 민감함을 시사한다. (자료원: `results/phase1_origin_A.csv`, `figure4_success_vs_disruption.png`)

### 4.3 Phase 2 정책 trade-off

Phase 2 격자는 집결 지연 $\sigma \in \{0.3, 0.5, 0.7, 1.0\}$ × 7개 출발 정책(STRICT + GRACE $W \times \theta$)의 4 × 7 = 28 cell, cell당 $R = 10$ paired CRN seed로 구성된다(고정 압박점 $s = 1.2$, $p_{\mathrm{fail,scale}} = 1.0$). 〈표 3〉은 sigma × policy 격자의 paired delta penalized makespan과 자원효율 차이를 정리한다.

**정책 무차별성 영역.** $\sigma \in \{0.3, 0.5, 0.7\}$ 세 수준에서 7개 정책 간 paired delta penalized makespan은 거의 동일하다($\bar{\delta}_{\mathrm{pm}} \approx -1.44 \times 10^5$분이 7개 정책 모두에서 일치). 이는 본 시뮬레이터의 lognormal($\mu = 2.0$, $\sigma \leq 0.7$) 집결 분포 하에서 99분위 도착이 GRACE의 가장 좁은 유예 윈도 $W = 15$분 안에 모두 흡수되므로 정책 간 행동이 동일해지기 때문이다.

**고분산 영역 ($\sigma = 1.0$).** 집결 분포의 꼬리가 더 두꺼워지면 GRACE의 유예 종료시각과 STRICT의 정시 출발이 분기한다. 자원효율 측면에서 STRICT(Δ ≈ 0.140~0.147)가 GRACE 군(Δ ≈ 0.130~0.144)을 0.005 포인트 내외로 앞서는 패턴이 관찰되며, 페널라이즈드 메이크스팬 측면에서 두 군의 차이는 약 0.9분에 불과하다. 즉 본 회랑·본 압박점에서 정책 효과는 1차 censoring 페널티에 비해 두 자릿수 작은 규모이며, Pareto 전선 위 정책 선택은 makespan보다 운용·승객 편의 관점에서 결정되어야 한다.

**Pareto 비지배 정책.** paired delta penalized makespan 단일 축에서 모든 7개 정책은 사실상 동일점에 위치하므로 일차 Pareto 비교는 사실상 의미가 없다. 보조 축으로 raw 완수율을 함께 고려해도 모든 정책이 비지배 집합에 속한다. 본 격자에서 정책 trade-off가 출현하지 않는다는 결과 자체가 §5의 논의에서 "본 회랑·본 압박점에서는 출발 정책 미세 조정의 효용이 도로 신뢰성 개선 대비 매우 작다"라는 함의로 해석된다.

**〈표 3〉** Phase 2 정책 trade-off: $\sigma$ × 정책별 Δ penalized_makespan 및 Δ 자원효율(부분 발췌).

| $\sigma$ | 정책 | Mean Δ penalized_makespan (분) | SD | Mean Δ 자원효율 | SD | $n$ |
|---|---|---|---|---|---|---|
| 0.3 | STRICT | -1.44e+05 | 4.56e+05 | 0.147 | 0.305 | 10 |
| 0.3 | GRACE_W30_T0.9 | -1.44e+05 | 4.56e+05 | 0.121 | 0.312 | 10 |
| 0.7 | STRICT | -1.44e+05 | 4.56e+05 | 0.147 | 0.305 | 10 |
| 0.7 | GRACE_W60_T0.9 | -1.44e+05 | 4.56e+05 | 0.121 | 0.312 | 10 |
| 1.0 | STRICT | -1.44e+05 | 4.56e+05 | 0.140 | 0.260 | 10 |
| 1.0 | GRACE_W15_T0.8 | -1.44e+05 | 4.56e+05 | 0.130 | 0.260 | 10 |
| 1.0 | GRACE_W60_T0.9 | -1.44e+05 | 4.56e+05 | 0.144 | 0.293 | 10 |

*주.* Phase 2는 $s = 1.2$, $p_{\mathrm{fail,scale}} = 1.0$의 단일 셀에서 $\sigma$ × 정책 (7수준)을 $R=10$회 반복. Δ penalized_makespan = bus − multi(분, 음수 = 단일수단 우위). Δ 자원효율 = multi − bus(양수 = 복합수단 우위). 정책 표기 GRACE_W{w}_T{θ}: 그레이스 윈도 $w$분 + 임계치 $\theta$. ±4.6×10⁵ 수준의 큰 표준편차는 censored 페널티가 결과를 지배하는 셀에서 관찰된다.

### 4.4 Origin 강건성

Phase 1의 주 스트림을 Origin A로 고정한 결과가 집결지 선택에 얼마나 강건한지를 확인하기 위해, B(삼전동 구민회관), C(장지역 4번 출구), D(잠실종합운동장, **출처 미확인 가정 변형**)에 대해 $s \in \{1.0, 1.5\}$ × $p_{\mathrm{fail,scale}} \in \{0.0, 1.0, 2.0\}$의 focused 2 × 3 격자, cell당 $R = 5$로 robustness 보조 스트림을 실행하였다(§3.5; 데이터: `figure5_origin_robustness.csv`). 〈그림 5〉는 네 origin의 paired delta penalized makespan을 동일 cell 위에서 비교하며, 〈표 4〉는 cell별 평균과 origin A 대비 절대 격차를 정리한다.

**Origin A vs. B (검증된 인근 집결지).** $s = 1.0$, $p = 1.0$의 대표 cell에서 Origin A는 $\bar{\delta}_{\mathrm{pm}} \approx -1.44 \times 10^5$분, Origin B는 $\bar{\delta}_{\mathrm{pm}} \approx -2.88 \times 10^5$분으로 약 $1.4 \times 10^5$분 더 음의 방향이다. B는 A보다 약 1 km 서쪽에 위치한 지리적 변형이 결과를 부호 단위에서는 변동시키지 않음을 시사한다.

**Origin A vs. C (검증된 남단 집결지).** Origin C(장지역)는 회랑 남단·동측에 위치한 검증된 집결지로, $s = 1.0$, $p = 1.0$ cell에서 $\bar{\delta}_{\mathrm{pm}} \approx -38.15$분이다. C에서는 $p = 1.0$에서 두 모드의 censoring이 정확히 같아 paired delta가 무장애 영역과 유사한 −38 ~ −60분 범위에 머문다. C의 잠실역 진입 경로가 A·B보다 짧아 환승 노드 의존성이 약화되는 점이 본 격차의 원인으로 해석된다.

**Origin D (출처 미확인 가정 변형).** Origin D(잠실종합운동장)는 §3.2·§3.9에서 명시한 바와 같이 **출처 미확인 가정 변형으로 본 결과는 robustness 시험용에 한정한다**. D는 $s = 1.0$, $p = 1.0$ cell에서 $\bar{\delta}_{\mathrm{pm}} \approx -5.76 \times 10^5$분, $p = 2.0$에서 $\bar{\delta}_{\mathrm{pm}} \approx -1.15 \times 10^6$분으로 다른 origin 대비 약 4배 더 큰 페널티를 기록한다. 본 D의 결과는 공식 집결지 지정 여부가 공개 자료에서 확인되지 않은 가상 변형이므로 본 절은 단지 결과 부호의 안정성만을 시사 수준에서 보고하고, 운용 함의는 §5에서 도출하지 않는다.

**종합.** 네 origin 모두에서 paired delta penalized makespan의 부호는 음(단일수단 우위)을 유지하며, 평균 격차의 절대값은 origin 위치에 따라 약 $4 \times 10^4$분 ~ $1.15 \times 10^6$분 범위로 변동한다. 본 부호 강건성은 §4.1·§4.2의 일차 결론이 origin 선택에 1차적으로 의존하지 않음을 보인다.

**〈표 4〉** 원점 강건성: B/C/D 대(對) A의 평균 Δ penalized_makespan (공통 셀).

| $s$ | $p_{\mathrm{fail,scale}}$ | Mean Δ penalized_makespan (A, R=10) | (B, R=5) | (C, R=5) | (D, R=5)² |
|---|---|---|---|---|---|
| 1.0 | 0.00 | -58.51 | -57.16 | -60.90 | -66.68 |
| 1.0 | 1.00 | -1.44e+05 | -2.88e+05 | -38.15 | -5.76e+05 |
| 1.0 | 2.00 | -2.88e+05 | -8.65e+05 | -2.88e+05 | -1.15e+06 |
| 1.5 | 0.00 | -58.51 | -57.16 | -60.90 | -66.68 |
| 1.5 | 1.00 | -1.44e+05 | -2.88e+05 | -38.15 | -5.76e+05 |
| 1.5 | 2.00 | -2.88e+05 | -8.65e+05 | -2.88e+05 | -1.15e+06 |

*주.* Δ = bus − multi (분, 음수 = 단일수단 우위). 공통 셀: $s \in \{1.0, 1.5\}$ × $p_{\mathrm{fail,scale}} \in \{0.0, 1.0, 2.0\}$. 원점 A는 송파 메인 시나리오, B·C·D는 동일 회랑 재실행. ² **원점 D 미검증 경고(출처 미확인 가정 변형)**: smoke 검증(`results/smoke_D.json`)에서 censored 페널티가 다른 원점 대비 약 4배 폭증하며, 본 표의 D 열은 *참고용*으로 차후 데이터 보정 전까지 정량 결론에는 포함하지 않는다.

**〈그림 5〉** Origin robustness — Δ penalized_makespan by origin candidate. 본 그림은 출발지 후보 4종(A: **송파구청 일자리센터** — 본문 기준, $R=10$; B: **삼전동 구민회관**, $R=5$; C: **장지역 4번 출구**, $R=5$; D: **잠실종합운동장**, $R=5$, **출처 미확인 가정**)에 대해 공통 그리드 셀($s \in \{1.0, 1.5\}$ × $p \in \{0.0, 1.0, 2.0\}$)에서의 Δ penalized_makespan 평균과 95% 신뢰구간(정규 근사)을 비교한다. 동일 셀에서 네 후보가 거의 같은 부호와 크기를 보이면, 본문 결과가 출발지 선택에 강건함을 시사한다. **Origin D 주의:** 잠실종합운동장은 공개 자료에서 병력동원 집결지로 확인되지 않은 가정치이며, 본문 분석에는 사용하지 않았다. 그림에서는 빨간 테두리·해치(///)·연한 채움 색으로 시각적으로 분리해 표시하였고, 범례 또한 "D — 출처 미확인 가정"으로 표기한다. 부호 규약은 Δ = bus − multi(음수 = 단일수단 우위). (자료원: `figure5_origin_robustness.png`, `figure5_origin_robustness.csv`)

### 4.5 Morris 민감도 분석

Morris elementary-effects 분석은 §3.7의 14개 매개변수(passenger_volume·direct_bus_fleet_size·dispatch_interval·turnaround_time·last_mile_fleet_size·rail_headway·feeder_fleet_size·rail_capacity·transfer_fixed_delay·passenger_arrival_variability·capacity_reduction_factor·road_background_traffic_multiplier·last_mile_access_disruption_probability·transfer_per_passenger_delay)에 대해 trajectory 수 50, level 수 4의 설계로 실행되었다(`results/sensitivity/morris_summary.csv`). 본 절은 두 정책(`baseline_multimodal`, `bus_only`)과 두 시나리오(`songpa_random_capacity_reduction`, `songpa_last_mile_station_to_destination`)를 통합한 **다지표 평균 μ\*** 기준으로 penalized_makespan 영향력 순위를 보고한다(〈표 5〉).

**Penalized makespan 영향력 순위 (다지표 평균 μ*, 상위 3개).**

1. **passenger_volume** ($\mu^*$ 평균 = 47.27, $\mu^*$ 최대 = 255.7, $\sigma$ 평균 = 71.09, $n$ = 28). 본 모형의 입력 인원 $N$이 가장 큰 1차 효과를 보인다. censoring 페널티가 $n_c \cdot \pi$의 곱 형태이므로 $N$의 변동이 미도착자 수의 절대값을 직접 변동시키는 구조적 결과이다.
2. **direct_bus_fleet_size** ($\mu^*$ 평균 = 29.43, $\mu^*$ 최대 = 194.3, $\sigma$ 평균 = 46.75, $n$ = 28). 단일수단 회로의 차량 수는 일정 시한 내 사이클 회수를 결정하므로 makespan에 강한 비선형 영향을 미친다. $\sigma$가 $\mu^*$를 상회하여 상호작용·임계점 효과가 있음을 시사한다.
3. **dispatch_interval** ($\mu^*$ 평균 = 20.44, $\mu^*$ 최대 = 126.5, $\sigma$ 평균 = 48.17, $n$ = 28). 배차 간격이 좁아질수록 차량 회전이 가속되어 makespan이 단조 감소하나, 차량 가용성 제약과의 상호작용에 따라 비선형 효과가 강하다.

이상의 상위 3개 매개변수는 모두 공급측 자원 모수(인원·차량 수·배차)이며, 도로 신뢰성 매개변수(`capacity_reduction_factor`, `road_background_traffic_multiplier`)는 다지표 평균 $\mu^* < 1.0$로 1~2 자릿수 작다(〈표 5〉 11–12위). 이는 §4.1의 혼잡 축 둔감성 관찰과 정합적이다. 다만 본 Morris 결과는 §3.5의 50 trajectory 축소 설계 위에서 산출되었으므로 $\mu^*$ 절대값의 외부 타당성보다는 상대 순위만 일관되게 해석한다.

**개별 정책 × 시나리오 블록의 참고 순위.** 14개 매개변수 중 한 정책 블록(`baseline_multimodal`)만으로 본 회랑에 한정하면 (1) last_mile_fleet_size ($\mu^* \approx 42.62$), (2) passenger_volume ($\approx 35.85$), (3) turnaround_time ($\approx 29.13$)이 상위 3개를 점한다. 한편 `bus_only` 단일 블록에서는 (1) passenger_volume ($\approx 255.72$), (2) direct_bus_fleet_size ($\approx 194.30$), (3) dispatch_interval ($\approx 126.54$)이 상위 3개이다. 두 정책 × 두 시나리오의 4개 블록을 통합한 〈표 5〉의 다지표 평균이 본 연구의 canonical 순위이며, 본 절 위의 abstract·결론에서도 동일한 기준을 인용한다.

**〈표 5〉** Morris 전역 민감도: 파라미터별 μ* 및 σ (상위 순위, penalized_makespan; 다지표 평균).

| 순위 | 파라미터 | $\mu^*$ 평균 | $\mu^*$ 최대 | $\sigma$ 평균 | $\mu^*$ 95% CI 폭 평균 | $n$ |
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
| 13 | last_mile_access_disruption_probability | 0.330 | 2.102 | 0.796 | 0.223 | 28 |
| 14 | transfer_per_passenger_delay | 0.114 | 0.690 | 0.540 | 0.149 | 28 |

*주.* SALib Morris elementary-effects, trajectories = 50, levels = 4, 14개 파라미터에 대해 $(k+1) \times T = 750$ 표본/구성으로 평가. $\mu^*$ = |elementary effect|의 평균(영향력 크기), $\sigma$ = elementary effects의 표준편차(비선형·상호작용 강도). 본 표의 값은 7개 출력 지표(완료율, censored 인원, 페널라이즈드 메이크스팬, p80·p95 도착시간, 총 운영분, 단위 운영분당 수송 인원) × 2개 정책(`baseline_multimodal`, `bus_only`) × 2개 시나리오(`songpa_last_mile_station_to_destination`, `songpa_random_capacity_reduction`)에 대한 평균. Morris 결과는 파일럿 스캐폴드로 보정된 운영-환경 민감도 추정치는 아니다.

### 4.6 결과 종합

본 장의 결과는 다음과 같이 종합된다. (i) 무장애 영역에서 단일수단이 약 58분 우위이며 이는 본 회랑의 환승 고정지연·추가 거리에 기인하는 구조적 환승 페널티이다. (ii) 고압박 영역($p_{\mathrm{fail,scale}} \geq 1.0$)에서 복합수단의 미도착률이 단일수단보다 0.10~0.20 포인트 높아 단일수단의 우위가 censoring 측면에서 확장되며, 본 분기는 paired makespan의 부호가 아니라 censoring 격차의 부호 위에서 정의되는 실용적 break-even이다. (iii) 출발 정책(STRICT/GRACE) 미세 조정의 효용은 censoring 페널티에 비해 두 자릿수 작아 본 회랑·본 압박점에서는 정책 trade-off가 사실상 평탄하다. (iv) origin 선택은 paired delta의 부호를 변동시키지 않으나 절대 격차의 규모는 $4 \times 10^4$분 ~ $1.15 \times 10^6$분 범위로 변동하며, Origin D는 **출처 미확인 가정 변형**으로 robustness 시험용에만 한정 해석된다. (v) Morris 분석은 다지표 평균 μ* 기준으로 passenger_volume, direct_bus_fleet_size, dispatch_interval을 상위 3개 인자로 식별하며, 도로 신뢰성 매개변수의 효과는 1–2 자릿수 작다.

---

## 5. 결론 및 향후연구

### 5.1 결론

본 연구는 송파구 가상 집결지(A·B·C·D)에서 72보병사단 부곡리 동원훈련장에 이르는 약 40~50 km의 OSM 주요 간선 회랑 위에서, 단일수단(버스 직송)과 복합수단(철도-버스)의 회복력을 paired CRN 기반 2단계 통제실험으로 비교하였다. Phase 1(혼잡 스케일 $s \in \{0.8, 1.0, 1.2, 1.5, 2.0\}$ × 장애 강도 $p_{\mathrm{fail,scale}} \in \{0.0, \ldots, 3.0\}$, cell당 $R=10$, 〈표 1〉)와 Phase 2(집결 지연 스케일 $\sigma$ × 출발 정책 STRICT/GRACE, cell당 $R=10$), 그리고 origin B·C·D 강건성 보조 격자($R=5$)의 세 스트림을 동일한 시드 베이스에서 실행하였다.

**Phase 1.** 35개 셀 전체에서 paired delta penalized makespan은 음의 부호를 유지하였다. 무장애·저압박 영역($p_{\mathrm{fail,scale}} \leq 0.5$)에서 두 수단의 페어드 차이는 환승 손실분에 고정되며(예: $s=1.0$, $p=0.5$, baseline×blocked: $\bar{\delta} = -41.75$분, 95% CI $[-59.65, -23.85]$), 복합수단의 환승 고정지연과 추가 거리가 그대로 격차로 남는다. 압박이 커질수록($p_{\mathrm{fail,scale}} \geq 1.0$, blocked 모드) 베이스라인 네트워크의 페어드 평균이 $-58 \sim -42$분에서 $-1.44 \times 10^5$분 수준으로 급격히 발산하며(예: $s=1.0$, $p=1.0$: $\bar{\delta} = -1.44 \times 10^5$분), 이는 복합수단이 인당 $\pi = 1440$분의 censoring 페널티를 단일수단보다 100명가량 더 누적하기 때문이다(〈표 2〉, 〈그림 3〉). 즉 본 회랑에서 두 수단 간 break-even은 paired makespan의 부호가 아니라 **censoring 격차의 부호** 위에서 정의된다.

**Phase 2.** STRICT/GRACE 출발 정책과 집결 지연 스케일 $\sigma$ 사이의 정책 trade-off는 본 압박점($s = 1.2$, $p_{\mathrm{fail,scale}} = 1.0$)에서 1차 censoring 페널티에 비해 두 자릿수 작은 규모이다. 자원효율 축에서 STRICT가 GRACE를 0.005 포인트 내외로 앞서는 패턴이 $\sigma$ 전 구간에서 일관되게 관찰되나, 페널라이즈드 메이크스팬 축에서는 7개 정책이 사실상 동일점에 위치하여 Pareto 비교가 평탄하다(〈표 3〉).

**Origin 강건성.** 네 origin 모두에서 paired delta의 부호는 음(단일수단 우위)을 유지하나 절대 격차의 규모는 origin 위치에 따라 $4 \times 10^4$분 ~ $1.15 \times 10^6$분 범위로 변동한다(〈표 4〉, 〈그림 5〉). 단, **origin D(잠실종합운동장)는 공개 자료에서 병력동원 집결지로 확인되지 않은 출처 미확인 가정 변형**이며, 따라서 본 결론의 일반화 범위에 포함되지 않는다(§3.5, §5.3).

**Morris 민감도.** 50 trajectories × 4 levels × 14 parameters Morris 분석은 페널라이즈드 메이크스팬의 다지표 평균 μ* 상위 3개 인자로 **passenger_volume($\mu^* = 47.27$), direct_bus_fleet_size($\mu^* = 29.43$), dispatch_interval($\mu^* = 20.44$)**을 식별하였으며, 이들 세 매개변수가 본 회랑의 결과 변동성을 1차적으로 설명한다(〈표 5〉). 도로 측 매개변수(`capacity_reduction_factor`, `road_background_traffic_multiplier`)는 다지표 평균 μ* < 1로 1~2 자릿수 작아 §4.1의 혼잡 축 둔감성과 정합적이다.

### 5.2 학술적·실무적 시사점

**학술적 시사점.** 본 연구는 산업공학·운영연구 분야에서 정립된 네 가지 도구 — paired CRN, censoring-aware 지표 체계, Morris 기본효과 민감도, 2단계 paired DoE — 를 군 동원수송체계라는 비공개 자료 의존도가 큰 도메인에 학제적으로 결합하였다는 점에서 방법론적 기여를 갖는다. 특히 censoring-aware 지표는 "빠르지만 누락이 큰" 시스템이 단일 makespan 보고에서 호도되는 문제를 직접적으로 보정하며, 본 연구의 가장 핵심적 정량 결과(고압박 영역에서 페어드 차이가 4~5 자릿수로 발산하는 양상)는 단일 makespan 보고만으로는 드러나지 않는다. Morris screening은 산업공학 출판 관행과 군사 도메인 사이의 의사소통 비용을 낮추는 도구로 활용될 수 있음을 보이며, Sobol' [19] 등 정량 분해 기반 후속 분석으로의 자연스러운 경로를 제시한다.

**실무적 시사점(강한 한정 하).** 본 연구의 조건 지도는 동원수송 계획자에게 (i) 단일 회랑 의존도가 높은 구간에서는 도로 신뢰성 매개변수보다 공급측 자원 매개변수(인원·차량·배차)가 결과 변동의 1차 동인이라는 정성적 가설(Morris 다지표 평균 결과), (ii) 집결 지연 분포가 큰 표본에 대해서도 출발 정책 미세 조정의 효용이 도로 신뢰성 개선 대비 작다는 가설, (iii) 검증된 세 집결지(A·B·C) 간 부호 강건성을 제공한다. 단, **본 결과는 가상 회랑·미보정 매개변수 하의 paired CRN 비교 차이일 뿐, 실 도로 용량·실 철도 시각표·실 동원지정 자원 배정 자료로 보정되지 않았다**. 따라서 본 결과는 운용 가이드가 아니라 보정 후속 연구의 우선순위 설계 입력으로만 활용되어야 하며, 군 기관의 어떠한 운영적 확장도 「국방연구분야 보안성 검토 절차」를 비롯한 보안성 검토 절차의 사전 통과를 필수 전제로 한다.

### 5.3 한계

본 연구의 한계는 §3.9에서 일차로 선언하였으며, 결과 해석에 직접 영향을 미치는 다섯 가지 핵심 한계를 본 절에서 다시 정리한다.

첫째, **catchment 추정의 한계.** 송파구 거주 동원 자원이 72보병사단으로 배정되는지의 여부는 공개 자료로 검증할 수 없다. 「병력동원소집통지서」는 개별 고지되며 행정구역별 배정표는 공개되지 않으므로, 본 연구의 송파↔부곡리 라우팅은 예시적(illustrative) 회랑에 한정되며 운영 배정의 주장이 아니다.

둘째, **OSM 주요 간선 필터의 외부 영향.** 본 연구의 회랑은 `motorway`·`trunk`·`primary`·`secondary`(및 link 변형)로 필터된 18,213 노드 / 29,542 directed 엣지 부분망이다. 이 필터는 보행·자전거·생활도로의 침투를 방지하는 효과를 갖지만, 동시에 우회 가용성을 과소 평가할 가능성이 있다. 또한 OSM 태그의 결손·불일치를 `HIGHWAY_DEFAULTS` 결정론적 프록시로 채웠으므로, 한국 도로의 실측 capacity·자유속도와의 일치는 보장되지 않는다.

셋째, **반복 회수 축소($R = 10$ / Morris 50).** 본 회랑의 계산 비용으로 인해 계획상 $R = 30$(Morris 200 trajectories)을 주 스트림 $R = 10$(Morris 50 trajectories), 보조 origin 스트림 $R = 5$로 축소하였다. paired CRN의 페어링 구조 자체는 보존되므로 단일 cell 내 분산 추정은 비파괴적으로 영향을 받으나, $t_{0.975,\,9} = 2.262$로 다소 넓은 신뢰구간을 산출한다는 점은 결과 해석에서 명시적으로 고려되어야 한다.

넷째, **Origin D의 출처 미확인.** 잠실종합운동장이 병력동원 집결지로 사용되었음을 확인할 공개 자료는 없다. 본 연구는 사용자의 명시적 지시에 따라 D를 robustness 가정 변형으로만 다루며, 본 origin의 결과는 모든 표·그림에서 별도로 표기되고 본 연구의 일반 결론에 포함되지 않는다.

다섯째, **공개 자료만 사용.** 본 연구는 병무청 공식 게시 정보, 송파구 조례·보도자료, OSM 도로망 위상, 공개 매개변수 가정만을 입력으로 사용하였다. 군사 시설 내부 배치, 부대 정원, 동원지정 자원의 행정구역별 배정 등 비공개 정보는 분석 대상에서 의도적으로 배제하였다. 군 기관의 어떠한 운영적 확장도 사전에 보안성 검토 절차를 거쳐야 함을 함의한다.

### 5.4 향후 연구

본 연구의 산출물을 보정 단계로 확장하기 위한 후속 연구 방향은 다음 다섯 가지로 정리된다.

첫째, **실 데이터 보정.** 본 연구의 가상 회랑 결과를 운용 의사결정 지원 수준으로 강화하려면 (i) 한국 도로의 실측 capacity·자유속도, (ii) 실제 철도 시각표(KORAIL·Seoul Metro GTFS 또는 station-event timetable), (iii) 동원지정 자원의 실 배정 분포(보안 검토 후 익명·집계 형태)가 보정 입력으로 확보되어야 한다. 본 연구의 paired CRN + censoring + Morris 골격은 이러한 보정 입력을 그대로 흡수하도록 설계되어 있다.

둘째, **KTDB 도로 capacity 보정.** 국가교통DB는 한국 도로의 시간대별 통행량·자유속도·용량 추정치를 제공한다. 본 연구의 `HIGHWAY_DEFAULTS` 결정론적 프록시를 KTDB 기반 보정값으로 대체하면, BPR 함수의 절대 통행시간 외부 타당성이 크게 강화되며 break-even 영역의 위치가 정밀화될 수 있다.

셋째, **부곡리 실제 access route 측정.** 본 연구의 목적지는 72보병사단 부곡리 동원훈련장의 공개 좌표에 스냅된 routeable OSM 노드이며, 실제 동원훈련장 접근로의 차로 폭·신호·집결지 내부 동선은 측정되지 않았다. 보안성 검토를 통과한 범위 내에서 last-mile access의 실측 통행시간을 측정하면 본 연구의 영향력 있는 매개변수의 보정이 가능하다.

넷째, **Morris 상위 매개변수의 우선순위 calibration.** Morris 다지표 평균 결과(§5.1)는 passenger_volume·direct_bus_fleet_size·dispatch_interval을 상위 3개 매개변수로 식별하였다. 후속 보정 단계의 자원 배분은 이 우선순위에 따라 (i) 동원 인원 규모, (ii) 단일수단 함대 크기, (iii) 배차 간격의 실측·시나리오 검증에 집중하는 것이 가장 큰 한계비용 대비 효과를 보인다. 후속 분석에서는 Sobol' 분해 [19]를 결합하여 상호작용 항까지 분리할 수 있다.

다섯째, **단일 corridor → 멀티 corridor 확장.** 본 연구는 송파↔부곡리 단일 회랑에 한정된다. 동일 분석 골격을 (i) 서울 동남부 → 경기 북부 다른 동원사단, (ii) 수도권 외 권역의 동원 회랑으로 이식하면, 회랑 이중화 효과의 일반성과 정책 효과의 권역별 이질성을 검증할 수 있다. 본 연구의 재현성 패키지(deterministic seed, 매니페스트, 청정 체크아웃 스모크)는 이러한 멀티 corridor 이식을 직접 지원하도록 설계되었다.

본 연구의 결론을 한 문장으로 요약하면 다음과 같다. **송파↔부곡리 가상 주요 간선 회랑 위에서, 단일수단의 회복력 우위는 도로 장애 강도가 커질수록 censoring-aware 페널라이즈드 메이크스팬 측면에서 확장되며, 그 1차 동인은 도로 신뢰성보다 공급측 자원 매개변수(인원·차량·배차)에 있다.** 이 진술은 본 연구가 사용한 공개 자료·가상 매개변수 범위 안에서만 유효하며, 운용 의사결정 적용은 추가 보정과 보안성 검토를 전제로 한다.

---

## 참고문헌

(APA 7판. 본문 인용 [1]–[25]는 등장 순서로 번호가 부여되었다.)

[1] 병무청. (2024). *동원훈련 안내: 입영시간 및 지연입소 규정* [Mobilization training guide: Entry time and grace-period rules]. 병무청. https://www.mma.go.kr

[2] 송파구청. (2023). *송파구 예비군 수송버스 운행 조례* (조례 제1486호, 2023-09-14) [Songpa-gu reserve-force transport-bus operation ordinance (No. 1486, 2023-09-14)]. 송파구.

[3] Murray-Tuite, P., & Wolshon, B. (2013). Evacuation transportation modeling: An overview of research, development, and practice. *Transportation Research Part C: Emerging Technologies, 27*, 25–45. https://doi.org/10.1016/j.trc.2012.11.005

[4] Liu, Y., Lai, X., & Chang, G.-L. (2006). Two-level integrated optimization system for planning of emergency evacuation. *Journal of Transportation Engineering, 132*(10), 800–807. https://doi.org/10.1061/(ASCE)0733-947X(2006)132:10(800)

[5] Berdica, K. (2002). An introduction to road vulnerability: What has been done, is done and should be done. *Transport Policy, 9*(2), 117–127. https://doi.org/10.1016/S0967-070X(02)00011-2

[6] Jenelius, E., Petersen, T., & Mattsson, L.-G. (2006). Importance and exposure in road network vulnerability analysis. *Transportation Research Part A: Policy and Practice, 40*(7), 537–560. https://doi.org/10.1016/j.tra.2005.11.003

[7] Taylor, M. A. P. (2008). Critical transport infrastructure in urban areas: Impacts of traffic incidents assessed using accessibility-based network vulnerability analysis. *Growth and Change, 39*(4), 593–616. https://doi.org/10.1111/j.1468-2257.2008.00448.x

[8] Law, A. M. (2015). *Simulation modeling and analysis* (5th ed.). McGraw-Hill.

[9] Kaplan, E. L., & Meier, P. (1958). Nonparametric estimation from incomplete observations. *Journal of the American Statistical Association, 53*(282), 457–481. https://doi.org/10.1080/01621459.1958.10501452

[10] Mattsson, L.-G., & Jenelius, E. (2015). Vulnerability and resilience of transport systems: A discussion of recent research. *Transportation Research Part A: Policy and Practice, 81*, 16–34. https://doi.org/10.1016/j.tra.2015.06.002

[11] Banks, J., Carson, J. S., Nelson, B. L., & Nicol, D. M. (2014). *Discrete-event system simulation* (5th ed.). Pearson.

[12] Matloff, N. (2008). *Introduction to discrete-event simulation and the SimPy language*. University of California, Davis. https://simpy.readthedocs.io

[13] Boeing, G., & Wang, S. (2024). Urban street network analysis with computational notebooks: An OSMnx-based reproducible workflow. *Computers, Environment and Urban Systems, 107*, 102045. https://doi.org/10.1016/j.compenvurbsys.2023.102045

[14] Glasserman, P., & Yao, D. D. (1992). Some guidelines and guarantees for common random numbers. *Management Science, 38*(6), 884–908. https://doi.org/10.1287/mnsc.38.6.884

[15] Nakayama, M. K. (2008). Statistical analysis of simulation output. In S. G. Henderson & B. L. Nelson (Eds.), *Handbooks in operations research and management science: Simulation* (Vol. 13, pp. 207–249). Elsevier. https://doi.org/10.1016/S0927-0507(06)13007-7

[16] Klein, J. P., & Moeschberger, M. L. (2003). *Survival analysis: Techniques for censored and truncated data* (2nd ed.). Springer. https://doi.org/10.1007/b97377

[17] Pinedo, M. L. (2016). *Scheduling: Theory, algorithms, and systems* (5th ed.). Springer. https://doi.org/10.1007/978-3-319-26580-3

[18] Hall, N. G., & Posner, M. E. (1991). Earliness–tardiness scheduling problems, I: Weighted deviation of completion times about a common due date. *Operations Research, 39*(5), 836–846. https://doi.org/10.1287/opre.39.5.836

[19] Sobol', I. M. (2001). Global sensitivity indices for nonlinear mathematical models and their Monte Carlo estimates. *Mathematics and Computers in Simulation, 55*(1–3), 271–280. https://doi.org/10.1016/S0378-4754(00)00270-6

[20] Morris, M. D. (1991). Factorial sampling plans for preliminary computational experiments. *Technometrics, 33*(2), 161–174. https://doi.org/10.1080/00401706.1991.10484804

[21] Campolongo, F., Cariboni, J., & Saltelli, A. (2007). An effective screening design for sensitivity analysis of large models. *Environmental Modelling & Software, 22*(10), 1509–1518. https://doi.org/10.1016/j.envsoft.2006.10.004

[22] Herman, J., & Usher, W. (2017). SALib: An open-source Python library for sensitivity analysis. *Journal of Open Source Software, 2*(9), 97. https://doi.org/10.21105/joss.00097

[23] Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. *Computers, Environment and Urban Systems, 65*, 126–139. https://doi.org/10.1016/j.compenvurbsys.2017.05.004

[24] Hillier, F. S., & Lieberman, G. J. (2015). *Introduction to operations research* (10th ed.). McGraw-Hill.

[25] Sullivan, W. G., Wicks, E. M., & Koelling, C. P. (2019). *Engineering economy* (17th ed.). Pearson.
