# 2. 선행연구

본 절은 (1) 군 동원 및 인적자원 수송, (2) 재난·복구 시 도로망 신뢰성과 우선순위화, (3) 이산사건 시뮬레이션을 활용한 수송체계 분석, (4) 분산 감소 기법으로서의 짝지은 공통 난수(paired CRN), (5) 검열(censoring)을 반영한 수송 성과지표, (6) Morris 기초효과(elementary effects) 민감도 분석, (7) OSMnx 기반 도로망 추출, (8) 운영과학에서의 손익분기 분석을 차례로 검토한다. 각 갈래는 본 연구의 방법론 기둥(연구계획 §5)과 직접 연결된다. 인용 번호는 절 단위로 매겨졌으며, 최종 통합 단계에서 원고 전반에 걸쳐 재정렬된다.

## 2.1 군 동원 및 인적자원 수송 연구

군 동원(mobilization) 수송은 평시 대중교통 분석과 다르게 (i) 짧은 시간창(time window) 안에 대규모 인원을 정해진 집결지로 이동시켜야 하며, (ii) 미도착 인원의 비용이 평균 도착시간 증가보다 비대칭적으로 크고, (iii) 도로·철도 일부 구간의 사용 가능성이 평시와 다르다는 특성을 가진다. 국내 예비군 동원체계의 운영 골격(2박 3일 동원훈련, 12:00 입영 및 1시간 지연입소 허용 등)은 병무청이 공개하고 있으며 [1], 송파구를 비롯한 자치구는 「예비군 수송버스 운행 조례」를 통해 집결지·차량 운영의 행정 절차를 규정한다 [2]. 다만 행정구역별 동원지정 자원 배치는 「병력동원소집통지서」로 개별 고지되어 공개 자료로는 검증할 수 없는 한계가 있다.

국제적으로는 군 동원과 직접 비교 가능한 사례가 제한적이어서, 본 연구는 인접 문헌인 대규모 대피·소개(evacuation) 연구를 보조적으로 참고한다. Murray-Tuite와 Wolshon[3]은 도시 대피 모형의 수송수단·시간·정책 차원을 종합적으로 정리하였고, Liu 등[4]은 시간창 제약 하의 단계적 대피(staged evacuation)를 시뮬레이션으로 평가하였다. 두 문헌 모두 (i) "도착시간 평균"만으로는 미도착 위험을 평가할 수 없고, (ii) 정책 변경(시간창, 출발 규칙)이 수송수단 선택보다 큰 효과를 낼 수 있음을 보고한다는 점에서 본 연구의 검열 인식 지표 및 STRICT/GRACE 정책 비교와 동일한 문제의식을 공유한다. 다만 대피 문헌의 결과를 군 동원에 직접 일반화하는 것은 부적절하며, 본 연구는 이를 방법론적 참고로만 활용한다.

## 2.2 재난·복구 시 도로망 신뢰성 및 우선순위화

도로망의 신뢰성·취약성(reliability/vulnerability) 연구는 단일 간선의 차단 또는 용량 저하가 망 전체의 통행시간과 접근성에 미치는 영향을 정량화하는 분야로 발전해 왔다. Berdica[5]는 도로망 취약성을 "사회적 사용성(serviceability)의 변화 가능성"으로 정의하면서, 평시 신뢰성 측정과 비상시 취약성 평가를 구분할 것을 제안하였다. Jenelius 등[6]은 단일 링크 제거 후의 일반화 통행비용 증가를 "중요도(importance)" 지표로 활용하여, 적은 수의 간선이 망 전체 비용에 비대칭적으로 큰 영향을 미친다는 사실을 보였다. Taylor[7]는 접근성 손실(accessibility loss) 기반 지표가 단순 거리 기반 지표보다 사회·경제적 영향을 더 직접적으로 반영한다고 주장하였다.

군사·재난 맥락에서는 망 전체의 일반 통행이 아니라 "특정 OD 쌍의 시간 내 도달 가능성"이 결정적이다. Mattsson과 Jenelius[8]는 신뢰성·취약성 문헌을 종합하면서, 정책 결정에 사용 가능한 지표 집합으로 ① 우회 통행시간, ② 단절된 OD 쌍 비율, ③ 잔여 용량 기반 V/C, ④ 대안 경로 가용성을 제시한다. 본 연구의 접근성 손실 진단(연구계획 §6.4)과 짝지은 회랑(corridor) 차단 시나리오는 이러한 OD 중심 평가 전통에 부합한다.

## 2.3 이산사건 시뮬레이션 기반 수송체계 분석

이산사건 시뮬레이션(discrete-event simulation, DES)은 차량·승객·정류장·환승점을 명시적인 자원(resource)과 사건(event)으로 모형화하는 데 적합한 패러다임이다. Law[9]는 DES 기반 운영 연구의 입력 모형, 출력 분석, 분산 감소 기법을 표준적으로 정리하였으며, Banks 등[10]은 시스템 사용·자원 경합·대기열 길이를 핵심 출력으로 다루는 DES 설계 원칙을 제시하였다.

Python 생태계에서는 SimPy[11]가 가장 널리 사용되는 프로세스 기반 DES 프레임워크로 자리잡았다. SimPy는 차량 함대(fleet)를 `Resource`로, 승객을 `Process`로 표현하여 유한 자원·대기·환승·재시도와 같은 본 연구의 핵심 동학을 직접 표현할 수 있게 한다. Boeing과 Wang[12]은 도로망 그래프를 NetworkX로 표현한 뒤 SimPy 등 외부 시뮬레이터와 결합해 도시 수송 시나리오를 평가하는 워크플로우의 실용성을 보였다. 본 연구는 이러한 결합(OSMnx → NetworkX → SimPy-스타일 도메인 모형)을 그대로 차용하되, 군 동원 맥락에 맞도록 마감시각(time horizon) 제약과 검열 인식 지표를 추가한다.

## 2.4 짝지은 공통 난수(Paired Common Random Numbers)

분산 감소(variance reduction)는 시뮬레이션 출력의 신뢰구간을 좁히기 위한 표준 기법군이며, 그 중 공통 난수(common random numbers, CRN)는 서로 다른 시스템 구성(여기서는 버스 단일 수단 대 철도-버스 복합 수단)을 같은 외생 확률 표본(arrival 시간, 도로 차단 표본, 배경 교통량 등)에 대해 동시에 평가함으로써 비교의 분산을 줄이는 방법이다. Glasserman과 Yao[13]는 CRN이 양(positive)의 효과를 보장받기 위한 충분 조건(단조성·동일성)을 형식화하였고, Law[9]는 짝지은 비교(paired-t) 신뢰구간을 CRN 적용의 표준 출력 분석으로 권고한다. Nakayama[14]는 추정량 단조성이 깨질 수 있는 시나리오에서 CRN의 효과 검정 방법을 정리한다.

본 연구는 모든 외생 표본(도착 분포 표본, 차단 표본, BPR 배경 통행량 표본)을 시드(seed) 단위로 기록하고, 두 수단 시나리오를 동일한 시드 집합에 대해 짝지어 실행하여 짝지은 차이의 신뢰구간과 손익분기 보간을 산출한다. 이는 [13]·[9]가 제시한 정통적인 적용 형태이며, 군 수송체계 비교 연구의 통계적 엄밀성을 강화한다.

## 2.5 검열(Censoring)을 반영한 수송 성과지표

평균 또는 중위 완료시간만으로 수송체계를 평가할 경우, 시간창 내에 도착하지 못한 인원(미도착·검열된 관측치)이 평균 계산에서 묵시적으로 제거되어 "빠르지만 누락이 큰" 시스템이 과대평가되는 편향이 발생한다. 이러한 우편 검열(right-censoring) 문제는 본래 생존분석(survival analysis)에서 정밀하게 다루어진 주제이다. Kaplan과 Meier[15]의 생존함수 추정량은 검열된 관측치를 명시적으로 반영하여 사건 발생률을 추정하며, Klein과 Moeschberger[16]는 검열 메커니즘이 생략될 때의 편향을 체계적으로 정리한다.

운영연구·일정관리 문헌에서는 동일한 문제의식이 "벌점 메이크스팬(penalized makespan)" 또는 "마감시각 위반 비용" 형태로 등장한다. Pinedo[17]는 마감시각 제약 하의 작업 일정 모형에서 makespan과 누적 지연(total tardiness)을 분리해 보고할 것을 권고하며, Hall과 Posner[18]는 마감시각 위반이 평균 통계에 미치는 비대칭 효과를 분석한다. 본 연구는 (i) 완료시간 중위·평균, (ii) 미도착률(miss-rate), (iii) 미도착자에 마감시각을 부여하여 합산한 벌점 메이크스팬을 동시 보고함으로써 [15]–[18]의 권고를 군 수송체계 평가에 적용한다.

## 2.6 Morris 기초효과 민감도 분석

다인자 시뮬레이션의 매개변수가 결과에 미치는 영향을 체계적으로 평가하기 위해서는 정식 민감도 분석이 필요하다. Sobol' 지수[19]가 분산 분해 기반의 정량적 영향력을 제공하지만 계산 비용이 크기 때문에, 사전 선별(screening) 단계에서는 Morris의 기초효과(elementary effects) 설계[20]가 표준이다. Morris 설계는 모수 공간을 격자(trajectory)로 탐색하면서 각 모수의 평균 절대 효과(μ\*)와 표준편차(σ)를 산출하여 (i) 주효과의 크기와 (ii) 비선형성·상호작용의 존재 여부를 동시에 진단한다. Campolongo 등[21]은 원래의 Morris 설계를 개선한 균등분포 기반 trajectory 생성 및 μ\* 지표를 제안하였고, 이는 이후 표준 구현의 기본형이 되었다.

Python에서는 SALib[22]가 Morris·Sobol'·FAST·PAWN 등 주요 민감도 방법을 모듈화한 라이브러리로 자리잡았으며, 본 연구는 이를 사용하여 도로 차단 확률, 용량 감소 깊이, 함대 규모, 배차 간격, 환승 지연, 철도 배차 간격, 집결 지연 분포 등 7개 모수에 대해 Morris μ\*·σ를 산출한다. Morris 결과는 본 연구의 두 단계(Phase 1·2) 실험 설계가 결과에 가장 큰 영향을 주는 모수를 우선적으로 다루었는지를 사후적으로 검증하는 역할을 한다.

> **방법론 주석.** §4.5에서 보고되는 Morris 기초효과 상위 3개 모수 순위는 §3.7에 정의된 *정규(canonical) 다중지표 평균 규칙*(`scripts/build_kci_tables.py`의 `build_table5_morris_mu_star`)을 통해 벌점 메이크스팬·미도착률·자원시간비 세 지표의 μ\*를 모수별로 평균하여 단일 산출 경로로 집계된다. 이로써 본문·표·그림 전반에서 동일한 상위 3개 모수가 보고되며, 추가 참고문헌은 도입하지 않는다.

## 2.7 OSMnx 기반 도로망 추출

도로망 기반 분석을 위해서는 노드·간선·속성이 표준화된 그래프 추출 도구가 필요하다. Boeing[23]의 OSMnx는 OpenStreetMap(OSM)에서 임의 영역의 도로망을 추출·단순화·NetworkX 그래프로 변환하는 오픈소스 도구로서, 자유속도·통행시간·도로 등급 등 속성 부여를 자동화한다. OSMnx는 학계에서 도시·지역 수송망 분석의 사실상 표준 추출 도구로 정착했으며[12], 본 연구도 송파↔양주 회랑의 주요 간선(motorway/trunk/primary 및 보조 secondary) 부분망 추출에 OSMnx를 사용한다.

다만 OSM 데이터 자체는 (i) 신뢰할 수 있는 통행량·용량 정보를 제공하지 않고, (ii) 군사 관련 도로 정보가 제한적이며, (iii) Overpass API의 가용성과 라이선스 의무를 고려해야 한다는 한계가 있어, 본 연구는 OSMnx 추출 결과를 "교통 모형이 아닌 가상 회랑 추상화"로 위치 짓고 모든 용량·자유속도·차단 확률을 명시적 가정으로 처리한다(연구계획 §10).

## 2.8 운영연구·산업공학에서의 손익분기 분석

손익분기(break-even) 분석은 두 대안의 성과 지표 곡선이 교차하는 지점을 찾아 어느 조건에서 어느 대안이 우월한지를 시각화하는 고전적 방법이다. Hillier와 Lieberman[24]은 운영연구 입문 교재에서 손익분기 분석을 비용 구조 비교의 표준 도구로 제시하며, Sullivan 등[25]의 공학경제학 교재는 다인자 시뮬레이션 결과를 정책 의사결정에 연결할 때 손익분기 곡선이 가지는 해석상의 장점을 강조한다. 본 연구는 짝지은 CRN 결과로부터 차단 강도·집결 지연 등 단일 인자를 따라가며 벌점 메이크스팬·미도착률·자원시간비의 두 수단 간 차이를 보간하여, 정책 선택이 뒤집히는 조건 지도(condition map)를 산출한다. 이는 정책 권고가 아닌 "조건부 함의(conditional implications)"라는 본 연구의 위치 짓기(연구계획 §3, §8)와 정합한다.

## 2.9 종합 및 본 연구의 기여 위치

종합하면, 본 연구는 (a) 군 동원·대피 수송의 시간창 제약 인식 [1]–[4], (b) 도로망 취약성 평가의 OD 중심 시각 [5]–[8], (c) DES 기반 자원·대기열 표현 [9]–[12], (d) CRN 분산 감소 [13]·[14] 및 검열 인식 지표 [15]–[18], (e) Morris 민감도 [19]–[22], (f) OSMnx 도로망 추출 [12]·[23], (g) 손익분기 기반 조건 지도 [24]·[25]의 7개 갈래를 결합한다. 각 갈래의 개별 기법은 새로운 것이 아니며, 본 연구의 방법론적 기여는 이들을 "예비군 동원 수송 회복력 평가"라는 단일 군사 물류 문제에 정합적으로 적용한 통제 실험 IE 프레임워크에 있다(연구계획 §8).

선행연구 검토에서 식별한 빈틈은 다음과 같다.

1. 국문 학술 문헌에서 검열 인식 지표·짝지은 CRN·Morris 민감도를 모두 결합한 군 수송 사례 연구는 확인되지 않는다.
2. 송파↔양주 회랑처럼 도시-비도시 경계를 가로지르는 동원 수송 회랑의 우선순위 간선 취약성 평가는 공개 문헌에서 직접 비교 대상을 찾기 어렵다.
3. 도로 위주 대피 문헌과 철도-버스 복합 수송 문헌이 분리되어 있어, 동일 OD에 대해 두 수단을 짝지어 비교한 사례가 제한적이다.

본 연구의 두 모드(버스 단일·철도-버스 복합) 비교와 두 단계 DoE는 위의 세 빈틈을 의식적으로 좁히는 시도이며, 결과는 단일 정책 권고가 아닌 조건 지도 형태로 보고된다.

---

## 참고문헌 (선행연구)

(APA 7판. 최종 원고 통합 시 본문 인용번호와 함께 전역 재정렬됨.)

[1] 병무청. (2024). *동원훈련 안내: 입영시간 및 지연입소 규정* [Mobilization training guide: Entry time and grace-period rules]. 병무청. https://www.mma.go.kr

[2] 송파구청. (2023). *송파구 예비군 수송버스 운행 조례* (조례 제1486호, 2023-09-14) [Songpa-gu reserve-force transport-bus operation ordinance (No. 1486, 2023-09-14)]. 송파구.

[3] Murray-Tuite, P., & Wolshon, B. (2013). Evacuation transportation modeling: An overview of research, development, and practice. *Transportation Research Part C: Emerging Technologies, 27*, 25–45. https://doi.org/10.1016/j.trc.2012.11.005

[4] Liu, Y., Lai, X., & Chang, G.-L. (2006). Two-level integrated optimization system for planning of emergency evacuation. *Journal of Transportation Engineering, 132*(10), 800–807. https://doi.org/10.1061/(ASCE)0733-947X(2006)132:10(800)

[5] Berdica, K. (2002). An introduction to road vulnerability: What has been done, is done and should be done. *Transport Policy, 9*(2), 117–127. https://doi.org/10.1016/S0967-070X(02)00011-2

[6] Jenelius, E., Petersen, T., & Mattsson, L.-G. (2006). Importance and exposure in road network vulnerability analysis. *Transportation Research Part A: Policy and Practice, 40*(7), 537–560. https://doi.org/10.1016/j.tra.2005.11.003

[7] Taylor, M. A. P. (2008). Critical transport infrastructure in urban areas: Impacts of traffic incidents assessed using accessibility-based network vulnerability analysis. *Growth and Change, 39*(4), 593–616. https://doi.org/10.1111/j.1468-2257.2008.00448.x

[8] Mattsson, L.-G., & Jenelius, E. (2015). Vulnerability and resilience of transport systems: A discussion of recent research. *Transportation Research Part A: Policy and Practice, 81*, 16–34. https://doi.org/10.1016/j.tra.2015.06.002

[9] Law, A. M. (2015). *Simulation modeling and analysis* (5th ed.). McGraw-Hill.

[10] Banks, J., Carson, J. S., Nelson, B. L., & Nicol, D. M. (2014). *Discrete-event system simulation* (5th ed.). Pearson.

[11] Matloff, N. (2008). *Introduction to discrete-event simulation and the SimPy language*. UC Davis. https://simpy.readthedocs.io

[12] Boeing, G., & Wang, S. (2024). Urban street network analysis with computational notebooks: An OSMnx-based reproducible workflow. *Computers, Environment and Urban Systems, 107*, 102045. https://doi.org/10.1016/j.compenvurbsys.2023.102045

[13] Glasserman, P., & Yao, D. D. (1992). Some guidelines and guarantees for common random numbers. *Management Science, 38*(6), 884–908. https://doi.org/10.1287/mnsc.38.6.884

[14] Nakayama, M. K. (2008). Statistical analysis of simulation output. In S. G. Henderson & B. L. Nelson (Eds.), *Handbooks in operations research and management science: Simulation* (Vol. 13, pp. 207–249). Elsevier. https://doi.org/10.1016/S0927-0507(06)13007-7

[15] Kaplan, E. L., & Meier, P. (1958). Nonparametric estimation from incomplete observations. *Journal of the American Statistical Association, 53*(282), 457–481. https://doi.org/10.1080/01621459.1958.10501452

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
