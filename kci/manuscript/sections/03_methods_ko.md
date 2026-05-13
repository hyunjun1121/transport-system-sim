# 3. 연구 방법

본 장은 송파구–양주 부곡리 회랑 위에서 단일수단(버스 전용)과 복합수단(철도–버스)의 회복력을 통제실험으로 비교하기 위해 구축한 시뮬레이션·실험·민감도 분석 체계를 기술한다. 방법론 골격은 (i) SimPy 기반 이산사건 시뮬레이터, (ii) OSMnx로 추출한 주요 간선 가상 회랑, (iii) Paired CRN 기반 두 단계 DoE, (iv) Morris elementary-effects 민감도 분석의 네 축으로 구성된다. 모든 매개변수 값은 미보정 계획 프록시(planning proxy)임을 본 절 전반에 걸쳐 명시한다.

## 3.1 시뮬레이터 구조

본 시뮬레이터는 Python 3.11 환경에서 `SimPy` [1]의 이산사건(discrete-event) 패러다임을 채택하여, 인원 도착·차량 디스패치·도로 통행·환승·열차 운행을 모두 명시적 사건 단위로 처리한다. 시뮬레이터는 추상 네트워크 `H/A/S/R/D` 노드 계약(canonical node contract; H: 출발 허브, A: 집결지, S: 철도 승차역, R: 철도 하차역, D: 최종 목적지)을 따른다. 본 KCI 연구에서는 `A`는 송파구 집결지 후보(§3.2), `D`는 72사단 부곡리 동원훈련장, `S/R`는 잠실역·의정부역에 각각 스냅된다.

### 동적 교통 모형 (BPR-at-departure)

도로 통행시간은 출발시각(BPR-at-departure-time) 기준 BPR 함수로 결정된다.

$$
t(v) = t_0 \cdot \left[ 1 + \alpha \left( \frac{v}{C} \right)^{\beta} \right]
$$

여기서 $t_0$는 자유 통행시간(분), $v$는 배경 교통량(rolling 60분 윈도), $C$는 directional capacity(veh/h), $(\alpha, \beta) = (0.15, 4.0)$은 표준 미국연방도로국(FHWA) 권장값을 따른다. 차량은 배차 시각에 한 번 통행시간을 산정하고, 도중 재산정은 하지 않는다(*static-at-dispatch* 가정).

### Fleet / Dispatch / Rail / Last-mile 모듈

차량 운용은 `fleet.py`(유한 차량 가용성), `dispatch.py`(대기열 기반 승객 디스패치), `rail.py`(고정 헤드웨이 철도), `transfers.py`(환승 지연 산정)의 4개 sibling 모듈로 분리된다. 단일수단 시나리오는 `A→D` 직행 버스 단일 회로를 사용하고, 복합수단 시나리오는 `A→S` 셔틀 → `S→R` 열차 → `R→D` last-mile 버스의 3단 회로를 직렬 연결한다.

### Censoring-aware 지표 정의

총 인원 $N$이 시간 제한 $T_{\max} = 1440$분 내에 모두 도착하지 못할 수 있으므로 단일 makespan만으로는 *"빠르지만 누락이 많은"* 시나리오가 호도된다 [본 연구]. 따라서 본 연구는 다음을 1차 지표로 채택한다.

- **censored_count**: $T_{\max}$ 내에 $D$에 도착하지 못한 인원 수.
- **penalized_makespan**:

$$
M_{\mathrm{pen}} = \max(M_{\mathrm{obs}}, T_{\max}) + n_c \cdot \pi
$$

여기서 $M_{\mathrm{obs}}$는 관측된 마지막 도착시각, $n_c$는 censored_count, $\pi = 1440$분(`late_penalty_min`)은 누락 1인당 부과 페널티이다. $n_c = 0$이면 $M_{\mathrm{pen}} = M_{\mathrm{obs}}$로 환원된다.

부가 지표로 95퍼센타일 도착시각, 도로 차량-분(road vehicle-minutes), 1인당 총 서비스 분(passengers per total service minute, 자원 효율) 등이 계산된다.

## 3.2 가상 송파-부곡리 회랑

### OSMnx bbox 추출

도로망은 OSMnx [2]를 사용하여 위도 37.46–37.78°N, 경도 126.85–127.20°E 범위에서 추출하였다. 이 bbox는 송파구의 네 집결지 후보를 모두 남단에 포함하고, 양주 장흥 부곡리 동원훈련장(약 37.74 N / 126.95 E)을 북단에 포함하며, 사이를 잇는 올림픽대로·강변북로·서울외곽순환·1번 국도 연결구간을 충분히 포함하도록 설정되었다. 추출 결과는 `data/cache/songpa_yangju_corridor.graphml`에 GraphML 형식으로 캐시되어 모든 후속 실험이 동일한 그래프 스냅숏을 재사용하도록 보장한다.

### 주요 간선 필터링

`src/realworld/adapter.py`의 `ROUTEABLE_HIGHWAY_CLASSES` 집합을 다음으로 제한하였다.

```
{motorway, motorway_link, trunk, trunk_link,
 primary, primary_link, secondary, secondary_link}
```

이는 본 연구가 *주요 간선 회랑 추상화*(major-arterial corridor abstraction)에 명시적으로 한정됨을 의미하며, 보행·자전거·생활도로 등 비차량 OSM 지오메트리가 버스 경로로 침투하는 것을 방지한다. 평행 도로 엣지는 결정론적 규칙으로 1개만 선택된다: ① $t_0$ 최소, ② capacity 최대, ③ `base_p_fail` 최소, ④ 안정적 edge ID. 어댑터 결과 본 회랑은 18,213개 노드 / 29,542개 directed 엣지로 구성된다(`data/validation/accessibility_loss_summary.csv`). 이는 본 시뮬레이터의 종전 추상 베이스라인보다 한 자릿수 이상 큰 규모이며, §3.5의 반복 회수(R) 결정에 직접적 영향을 미친다.

### 정규 노드 매핑

어댑터는 region YAML에서 정의된 지리적 좌표를 가장 가까운 routeable OSM 노드에 스냅하고 양방향 connector 엣지(기본 connector_speed_kph = 30, connector_capacity = 600)를 추가한다. 정규 노드(`A`, `S`, `R`, `D`)는 `_validate_required_routes`에 의해 `A→D`, `A→S`, `R→D` 경로가 모두 가능함을 확인한 뒤에야 시뮬레이션에 투입된다.

### Origin 4개 후보

집결지는 네 개의 후보 위치(`data/regions/origin_candidates.json`)에 대해 검증된다.

| ID | 명칭 | 위도 | 경도 | 검증 |
|----|------|------|------|------|
| A | 송파구청 일자리센터 | 37.5147 | 127.1057 | 검증 (Hankyung 2024-02-29, 송파구 조례 2023-09-14) |
| B | 삼전동 구민회관 | 37.5036 | 127.0857 | 검증 (Hankyung 2024-02-29, 송파구 조례 2023-09-14) |
| C | 장지역 4번 출구 | 37.4784 | 127.1262 | 검증 (Hankyung 2024-02-29, 송파구 조례 2023-09-14) |
| D | 잠실종합운동장 | 37.5159 | 127.0727 | **출처 미확인 가정 변형** |

A·B·C는 송파구 조례 2023-09-14 및 한국경제 2024-02-29 보도에 명시된 예비군 수송버스 집결지이며 본 연구에서는 동원훈련장 수송에 유추 적용된다(역할 차이는 §3.9에서 언급). 후보 D(잠실종합운동장)는 어떠한 공개 자료에서도 병력동원 집결지로 확인되지 않았으며, 사용자 지정에 따라 *robustness 가정 변형*으로만 사용된다. 목적지는 병무청이 공개적으로 게시한 72사단 부곡리 동원훈련장(경기 양주 장흥 부곡리 산 6-17, 약 37.74 N / 126.95 E) 단일 지점이다.

## 3.3 도로 신뢰성 모델

### HIGHWAY_DEFAULTS

OSM의 `maxspeed`, `length`, `capacity` 태그는 결손·불일치가 흔하므로 어댑터는 클래스별 결정론적 기본값을 적용한다(`src/realworld/attributes.py`). 본 회랑에 실제로 등장하는 4개 routeable 클래스에 대한 값은 다음과 같다.

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

자유 통행시간 $t_0$ 는 $t_0 = L/(v \cdot 1000/60)$ 로 산정한다($L$: 엣지 길이 m, $v$: speed_kph). **이 값들은 한국 도로 데이터로 보정된 값이 아니라 OR/IE 연구용 결정론적 계획 프록시**이며, §3.9에서 정직하게 언급한다. OSM 엣지에 명시적 `maxspeed`·`capacity`가 있을 경우 그 값이 우선 적용된다.

### 장애 모드

본 시뮬레이터의 장애 모형(`src/disruptions.py`)은 두 가지 모드를 지원한다.

- **blocked**: 선택된 엣지의 통행시간을 $+\infty$로 만들어 라우팅에서 제외.
- **capacity_reduction**: 선택된 엣지의 capacity를 $C \leftarrow C \cdot \kappa$로 축소($\kappa$ = `capacity_reduction_factor` ∈ [0, 1)).

장애 발생 확률은 엣지별 `base_p_fail`에 시나리오 스칼라 `p_fail_scale`을 곱하여 결정된다.

$$
p_{\mathrm{fail}}(e) = \min\bigl(1, p_{\mathrm{fail,scale}} \cdot p_{\mathrm{base}}(e)\bigr)
$$

본 연구에서 `p_fail_scale` 0은 결정론적 baseline(장애 없음), 3.0은 가장 강한 압박 조건이다(§3.5).

## 3.4 시나리오 정의

장애 시나리오는 `data/scenarios/disruption_scenarios.csv`에 8개 family로 정의된다. 각 family는 결정론적 선택규칙(hash rank, edge betweenness, shortest-path, station_access, bbox)에 따라 그래프에서 영향 엣지를 식별하므로 동일 seed에서 재현된다.

| family | label | 선택 규칙 | mode | $\kappa$ / max_edges |
|--------|-------|----------|------|--------------------|
| random | 결정론적 무작위 capacity 감소 | hash_rank | capacity_reduction | 0.50 / 4 |
| random | 결정론적 무작위 완전 차단 | hash_rank | blocked | — / 2 |
| critical_link | 도로 betweenness 상위 차단 | edge_betweenness | blocked | — / 3 |
| access_road | A→S 진입로 감소 | shortest_path | capacity_reduction | 0.40 |
| access_road | A→D 직행 감소 | shortest_path | capacity_reduction | 0.40 |
| last_mile | R→D 종단부 감소 | shortest_path | capacity_reduction | 0.40 |
| rail_station_access | 역 진입·진출 도로 감소 | station_access | capacity_reduction | 0.50 / 6 |
| spatial_hazard_overlay | 탄천 회랑 노출 bbox | bbox_midpoint | capacity_reduction | 0.35 / 6 |

`evidence_class` 필드는 모든 행에서 `scenario_based`이며 `observed_disaster_data`는 `false`이다. 즉 어떤 시나리오도 실제 관측 재해 데이터를 표현하지 않는다.

## 3.5 DoE 설계

v0.7 실험 설계는 네 개의 DoE 스트림(Phase 1a/1b/2/3)과 한 개의 민감도 스트림(§3.7 Morris)으로 구성되며, 모든 스트림은 §3.6의 paired CRN을 공유한다. cell 정의·반복 횟수·grid 크기는 `kci/config.yaml`이 단일 출처로 보유한다.

### 3.5.1 Phase 1a — 기저 강건성

origin A(송파구청 일자리센터)에서 장애 강도만 변화시키는 1차원 sweep으로 기저 강건성 곡선을 산출한다. 요인 $p_{\mathrm{fail,scale}}$ 8수준 $\{0.0, 0.10, 0.25, 0.50, 0.75, 1.0, 1.5, 2.0\}$, 혼잡 스케일 $s = 1.2$ 고정(§3.5.5), 장애 모드 blocked, 네트워크 변형 baseline, **cell당 $R = 30$**; **격자 8 cell × R = 240 paired = 480 실행**. 출력 `results/phase1a_origin_A.csv`.

### 3.5.2 Phase 1b — 원점 강건성

origin A의 강건성 곡선이 다른 송파구 집결지 후보에 대해 부호·크기가 유지되는지 확인한다. 원점 B(삼전동 구민회관), C(장지역 4번 출구), D(잠실종합운동장; *출처 미확인 가정 변형*); $p_{\mathrm{fail,scale}}$ 4수준 $\{0.0, 0.5, 1.0, 1.5\}$; **cell당 $R = 20$**; **3 × 4 × R = 240 paired = 480 실행**. Origin D는 §3.9에 따라 모든 표·그림에서 별도 표기.

### 3.5.3 Phase 2 — 단일수단 매개변수 스윕

baseline 단일수단 구성에서 fleet·dispatch·장애 강도의 1차 효과를 분리해 *단일수단 회복력의 매개변수 조정 한계*를 평가한다. `bus.fleet_size` 5수준 $\{15, 23, 35, 50, 80\}$ (23 baseline) × `bus.dispatch_interval_min` 3수준 $\{3, 5, 10\}$ × $p_{\mathrm{fail,scale}}$ 3수준 $\{0.5, 1.0, 2.0\}$; **cell당 $R = 20$**; **45 cell × R = 900 paired = 1{,}800 실행**.

### 3.5.4 Phase 3 — 반사실 레버 스윕 (헤드라인)

baseline에서 복합수단이 단일수단에 의해 지배되는 결과를 *어떤 인프라 개입이 역전시킬 수 있는가*를 식별하는 헤드라인 격자. `multimodal.rail_headway_min` $\{15, 7.5, 3\}$ (15 baseline) × `multimodal.lastmile_fleet_size` $\{23, 50, 100\}$ (23 baseline) × `multimodal.rail_capacity_pax_per_train` $\{500, 1000, 2000\}$ (500 baseline) × 외생 $p_{\mathrm{fail,scale}}$ $\{0.0, 0.5, 1.5\}$; **cell당 $R = 15$**; **$3^4 = 81$ cell × R = 1{,}215 paired = 2{,}430 실행**.

격자 정의는 `src/experiment/doe.py::Phase3Point`/`phase3_grid(config)`가 단일 출처로 보유한다. cell 단위 레버 주입은 `src/experiment/phase3_runner.py::run_phase3`가 `src/kci_runtime.py::apply_phase3_lever_override(config, point)`를 호출해 수행하며, 후자는 입력 config를 **deepcopy** 한 뒤 `multimodal` 블록과 `network.rail_link[0]`을 함께 재기록하여 cell 간 레버 누출을 코드 계약 수준에서 차단한다.

### 3.5.5 s축 제거 사유

선행 버전(v0.6)은 혼잡 스케일 $s \in \{0.8, 1.0, 1.2, 1.5, 2.0\}$ 5수준을 Phase 1의 두 번째 요인으로 포함했으나 실행 결과 s축은 통계적으로 *불활성(inert)* 으로 판명되었다: 본 회랑에서 BPR 혼잡 효과는 수 분 규모인 반면 censoring 페널티(1{,}440분 × 수백 명)는 약 *세 자릿수* 큰 페널티로 penalized_makespan을 지배한다. 5개 s 수준 간 paired delta가 모두 CI 폭 내에 머물러 s축은 어떠한 신호도 운반하지 못하였고, v0.7은 이를 반영해 s를 단일 대표값 $s = 1.2$로 고정하고 절약된 budget을 §3.5.4의 반사실 격자에 재배분한다.

### 3.5.6 R 정직성 (R-honesty)

주(main) 분석은 cell당 $R = 30$ paired CRN을 Phase 1a에 적용한다. Phase 1b·Phase 2는 $R = 20$, Phase 3은 $R = 15$로 비대칭 배정한다 — Phase 3 격자는 Phase 1a의 약 10배 cell 수를 가지므로 wall-clock 관리상 R 축소가 불가피하며, cell 내 paired CRN 페어링이 보존되므로 cell당 분산 추정은 비파괴적이다. 본 trade-off는 §4의 모든 표가 cell당 CI 폭을 함께 보고하여 투명하게 노출된다 — 더 좁은 R은 더 넓은 CI로 직접 가시화된다.

## 3.6 Censoring-aware 지표·분위수 KPI·Paired CRN 신뢰구간

§3.1의 `penalized_makespan`은 1차 비교 지표로 유지된다. v0.7은 censoring 페널티에 가려진 분포 형태 정보를 복원하기 위해 분위수 기반 KPI를 추가한다.

**분위수 도착시각 (population-padded).** 각 실행에서 인원 총수 $N$ = `personnel.total` 의 모집단 벡터는 (i) $D$에 도착한 $N - n_c$명의 실제 도착시각 + (ii) censored된 $n_c$명에 대한 sentinel `time_limit` = 1{,}440분으로 구성된다. 이 길이-$N$ 벡터에 선형 보간 q-분위수를 적용해 `arrival_q50_min`, `arrival_q90_min`, `arrival_q95_min`을 정의한다. 본 규칙은 *성공자 분위수*가 아니라 *모집단 분위수* 이므로 censored 인원이 sentinel 값으로 꼬리에 보존되어 censoring 신호가 사라지지 않는다. 구현은 `src/metrics.py::MetricsCollector._quantile_over_population`.

**마감 시한 내 완료 확률.** $\mathrm{prob\_completion\_within\_window} = \#\{i : t_i \le \text{deadline\_min}\} / N$, `deadline_min` = `config.quantile_kpi.deadline_min` = **1{,}500분** ($\approx$ 25시간, 동원훈련 1일차 집결 cutoff 부합). [0, 1] 범위의 페널티 스케일 무관 완료율 지표.

**Paired delta 컬럼.** 위 KPI는 `src/scenario.py::run_scenario` 출력에 포함되고, `src/experiment/runner.py::_paired_result_row(base, bus, multi)`가 모든 단계 결과 행에 `delta_arrival_q{50,90,95}_min`, `delta_prob_completion_within_window` 컬럼을 자동 추가한다(양수 = 복합수단 우월).

**Paired CRN 신뢰구간.** seed $r \in \{1, \ldots, R\}$에 대하여 $\delta_r = \mathrm{pm}^{\mathrm{bus}}_r - \mathrm{pm}^{\mathrm{multi}}_r$, 표본평균 $\bar{\delta}$, 표본분산 $s_\delta^2$의 paired $t$-기반 95% CI는 $\bar{\delta} \pm t_{0.975, R-1} \cdot s_\delta/\sqrt{R}$. censoring 페널티 $\pi = 1{,}440$분이 모든 seed·모드에 동일 적용되어 페어링을 보존하며, paired CRN은 매 seed가 두 모드에 동일한 도로 장애 추첨·승객 도착시각·BPR 시계열을 부여해 구조적 차이를 외생 노이즈로부터 분리한다 [Kelton & Law 2014].

## 3.7 Morris elementary-effects 민감도 분석

매개변수의 1차 효과와 비선형성을 선별하기 위해 Morris elementary-effects 방법 [3]을 SALib [4]의 `morris.sample` / `morris.analyze`로 적용하였다. 설계 매트릭스 `data/scenarios/sensitivity_design.csv`는 다음 **14개** 매개변수를 보유한다(괄호 안은 베이스라인 / 하한 / 상한): passenger_volume (24 / 16 / 32 pax), passenger_arrival_variability (0.25 / 0.15 / 0.50), direct_bus_fleet_size (3 / 1 / 5), feeder_fleet_size (3 / 1 / 5), last_mile_fleet_size (2 / 1 / 4), dispatch_interval (5 / 2.5 / 10 min), road_background_traffic_multiplier (1.0 / 0.8 / 2.0), capacity_reduction_factor (0.50 / 0.25 / 0.75), rail_headway (10 / 5 / 20 min), rail_capacity (16 / 8 / 32 pax/train), transfer_fixed_delay (3 / 0 / 10 min), transfer_per_passenger_delay (0.02 / 0 / 0.10 min/pax), turnaround_time (8 / 4 / 20 min), last_mile_access_disruption_probability (1.0 / 0.0 / 1.0).

이 14개 매개변수는 **Phase 3 레버 네 가지(rail_headway, last_mile_fleet_size, rail_capacity, dispatch_interval)를 이미 포함**하므로 v0.7 reframing은 Morris 설계 확장을 요구하지 않았고, 본 설계는 그대로 재사용되었다.

설계 파라미터는 $k = 14$, $T = 100$ trajectories, `num_levels = 4`, paired CRN seed=1로 고정하며, 총 모델 평가 수는 $(k + 1) \times T = 1{,}500$ 회이다. Morris 지표는 $\mu^*_i = T^{-1}\sum_t |EE_{i,t}|$ (절대 평균 효과, 영향력 순위)와 $\sigma_i$ (EE 표준편차, 비선형·상호작용 진단)이며 $(\mu^*, \sigma)$ 산점도로 선별한다.

### 표준 집계 규칙 (canonical aggregation rule)

원시 `results/sensitivity/morris_results.csv`는 (policy × scenario × metric) 다중 블록을 포함하므로 본문이 인용하는 *μ\* 상위 매개변수* 는 다음 단일 규칙으로만 도출된다 — **각 매개변수에 대해 μ\* 는 (policy × scenario × metric) 블록에 걸쳐 산술 평균하며 metric 차원은 Table 5 build pipeline의 *multi-metric mean* 으로 통합되고, 본 평균은 `scripts/build_kci_tables.py::build_table5_morris_mu_star`(또는 동등 진입점)가 단독 산출한다.** 본 규칙은 §4·§5·초록의 Morris 인용에 대해 *유일한 권한 출처(single source of truth)* 로 작동하며, 다운스트림 작성·검증에서 raw 블록 재집계로 다른 순위를 산출하는 것은 허용되지 않는다(v0.6에서 관측된 fabrication 방지를 위한 통제).

## 3.8 재현성

본 연구의 모든 실험은 다음 재현성 장치를 갖추고 있다.

- **PROJECT_ROOT 고정**: `main.py` 상단에서 `PROJECT_ROOT = Path(__file__).resolve().parent`로 정의되며, `kci/`가 self-contained 실행 루트로 동작한다.
- **의존성 명시**: `kci/requirements.txt`에 simpy, networkx, numpy, pandas, PyYAML, matplotlib, seaborn, SALib, osmnx의 정확한 버전 핀이 기록된다.
- **GraphML 캐시 매니페스트**: OSMnx 추출 결과는 단 한 번 `data/cache/songpa_yangju_corridor.graphml`로 캐시되며 동반 매니페스트가 ETag·노드 수·엣지 수·추출일을 기록한다. 후속 모든 실험은 이 캐시를 *읽기 전용*으로 사용한다.
- **결정론적 seed 베이스**: `experiment.seed_base = 1`을 기점으로 cell-내 paired seed는 $1, 2, \ldots, R$로 단조 증가하며, `disruption_scenarios.csv`의 선택 규칙(hash_rank, edge_betweenness 등)이 결정론적이므로 동일 seed에서 정확한 재현이 보장된다.
- **재현성 smoke**: `scripts/run_reproducibility_smoke.py` 및 `scripts/run_clean_checkout_smoke.py`가 동일 환경에서 두 번 실행했을 때 페어드 평균이 부동소수점 허용오차 내에서 일치함을 확인한다.

## 3.9 방법론 한계

본 연구는 IE/OR 방법론 *조건도(condition map)*로 위치되며, 운영 가이드가 아니다. 다음 한계를 본 절에서 미리 선언함으로써 결과 해석의 경계를 설정한다.

1. **미보정 capacity / p_fail.** §3.3의 `HIGHWAY_DEFAULTS`는 한국 도로 데이터로 보정된 값이 아니라 결정론적 계획 프록시이다. 따라서 본 연구의 mode 비교 결과는 *동일 그래프·동일 가정 하에서의 두 모드 차이*에 한정되며, 절대 통행시간의 외부 타당성을 주장하지 않는다.
2. **Origin D 출처 미확인.** 잠실종합운동장이 병력동원 집결지로 사용되었음을 확인할 공개 자료는 없다. 본 연구는 사용자의 명시적 지시에 따라 *robustness 가정 변형*으로만 D를 다루며, 본 origin의 결과는 모든 표·그림에서 별도로 표기된다(§3.5).
3. **A·B·C 역할 차이.** 송파구 조례 2023-09-14 및 한국경제 2024-02-29 보도가 명시하는 세 집결지는 *예비군훈련*(2박3일 동원훈련이 아님) 수송버스 집결지로 가동되는 사례이다. 본 연구는 이를 동원훈련장 수송에 유추 적용하며, 정확한 1:1 대응이 아님을 밝힌다.
4. **가상 회랑.** 본 회랑은 OSM의 주요 간선 부분집합에서 추출된 *가상 추상 네트워크*이며 한국 교통량·신호·차로 폭·우회로 가용성에 대한 보정을 거치지 않았다. 또한 송파→72사단 동원지정 자원 catchment는 *공개 자료로 검증할 수 없다*: 병무청은 동원지정을 개별 병력동원소집통지서로 통지하며 행정구역별 배정표를 공개하지 않는다. 따라서 본 라우팅은 *예시적(illustrative)*이며 운영 배정의 주장이 아니다.
5. **추상 철도 leg.** 잠실↔의정부 구간에는 직행 고빈도 노선이 없다. 본 연구의 철도 leg(`S→R`)는 60분 통행시간, 15분 헤드웨이, 1열차당 500인 용량의 *추상 장거리 프록시*이며, 실제 1호선·7호선·환승 경로의 동적 운행 데이터를 사용하지 않는다.
6. **외부 검증 부재.** OSRM·KTDB·GTFS 등 외부 라우팅 벤치마크와의 통행시간 일치 여부를 본 연구에서는 검증하지 않는다. 이는 후속 보정 연구의 과제이다.

이상의 한계 선언은 §4(결과) 및 §5(논의)의 *조건도* 해석에 일관되게 반영되며, 본 연구의 기여를 *방법론적 framework + 조건부 비교 지도*로 한정한다.

---

### 인용

[1] N. Matloff and the SimPy contributors, *SimPy Discrete-Event Simulation for Python (Documentation)*. https://simpy.readthedocs.io/.
[2] G. Boeing, "OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks," *Computers, Environment and Urban Systems*, vol. 65, pp. 126–139, 2017. doi:10.1016/j.compenvurbsys.2017.05.004.
[3] M. D. Morris, "Factorial sampling plans for preliminary computational experiments," *Technometrics*, vol. 33, no. 2, pp. 161–174, 1991.
[4] J. D. Herman and W. Usher, "SALib: An open-source Python library for sensitivity analysis," *Journal of Open Source Software*, vol. 2, no. 9, p. 97, 2017. doi:10.21105/joss.00097.
