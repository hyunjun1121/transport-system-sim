# 전시 예비군 수송 연구 — 프레임 문서

> **버전**: 2026-09-21 최종 확정
> **용도**: 연구 전체의 큰 틀과 세부 내용을 하나의 문서로 통합
> **지위**: `agents.md`와 동등한 프로젝트 원칙 문서

---

## 1. 연구 개요

### 1.1 배경

2019년「수송체계 분평단」보고서는 전시 예비군 수송의 운용계획을 제시했으나, 실시설 좌표·내부 데이터에 기반했기 때문에 현재 프로젝트에서 직접 재현할 수 없다. 그러나 그 **문제 구조**(수단 선택·자원 배분·위험 대응·결정 논리)와 **방법론 체계**는 계승 가능하며, 현재는 공공데이터와 시뮬레이션으로 대체된다.

### 1.2 연구 목적

> **조건부 전력증식 의사결정 지원**: 장거리 육로 피해가 어느 수준을 넘으면 철도혼합 수송이 유리해지는가? 이 임계점이 얼마나 강건한가?

2019이 "운용계획"이었다면, 이 연구는 **결정 트리**를 제공한다. "어떤 조건에서 대안을 바꿔야 하는가"를 정량적으로 답한다.

### 1.3 핵심 RQ (단 하나)

> **"S→R 장거리 육로의 travel_time_multiplier가 어느 수준을 넘으면, bus_only 대비 baseline_multimodal이 makespan과 completion_rate에서 우위를 점하는가?"**

모든 부연 질문(위협 유형, 철도 상태, 수요 수준 등)은 이 RQ의 **강건성 검증**으로 귀결된다.

---

## 2. 설계 원칙

### 2.1 층별 분리

| 층 | 역할 | 처리 | 예시 |
|---|---|---|---|
| **불변** | 물리적 현실 | 고정, provenance만 명시 | 표준노드링크 도로망 형상, 역 좌표 |
| **보정** | 공급측 파라미터 | 1회 보정 후 고정 | 자유류속도, 차로당 용량, V/C 곡선 |
| **가정** | 전시 scope 조건 | 고정 + 명시 | A1–A4 (저배경교통, 고정함대 등) |
| **스트레스** | 실험변수 | **여기서만 가변** | 위협 유형, 철도 상태, 자원 프레임, 수요 수준 |
| **판단** | 출력 | 결정자 언어 | 완성률 → makespan → break-even |

### 2.2 고정의 정당화

어떤 변수를 고정하든 **Morris elementary effects screening**이 영향도를 증명한다. 영향 없는 변수를 고정하는 것은恣意가 아니라 절차.

### 2.3 주장 규율 (비협상)

- `final_study_ready=false` — 공식 수용 0/12
- "공공데이터 기반 조건부 시나리오 시뮬레이션" — never "운용", "forecast", "validated", "optimal"
- 한국어 "검증"은 reserved tripwire
- `scripts/audit_claim_language.py` 강제 적용

---

## 3. 규모 설계

### 3.1 실제 동원 규모 (공개 데이터)

| 항목 | 수치 | 출처 |
|---|---|---|
| 연간 병력동원훈련 대상 | **45만여 명** | 병무청 2025 보도자료 |
| 집단수송 대상 | **약 10만 명** | 병무청 FAQ |
| M+1~13일 분산 배치 | 일일 약 **6,000여 명** (8.1만/13일) | 2019 보고서 + 병무청 |
| 2024 비상계엄 수송 실적 | 107대 차량 + 헬기 12대, ~1,500명 | 국방부→국회 제출 (경향신문·YTN) |
| 동원훈련 교통비 | 연료=거리×1,486÷13.3km/L, 통행료=900+44.3원/km | 병무청 2026 지급 기준 |

### 3.2 시뮬레이션 규모 결정

| 규모 | 장점 | 단점 | 판단 |
|---|---|---|---|
| 1,000 | 코드 가벼움 | congestion 미미, 실전과 거리 | **부적절** |
| 2,000–3,000 | 코드 가능, 일부 congestion | 여전히 과소 | **보조 실험용** |
| **5,000–8,000** | **congestion 실전 유사, 하루 배치 규모 반영** | 코드 수정 필요 | **메인 실험** |
| 450,000 | 완전 현실 | 비현실적, 불가능 | **불가** |

**결정**: 메인 실험 = **5,000–8,000명**, 보조 = 2,000명 (scale sensitivity용). 1,000명은 사용하지 않는다.

### 3.3 규모 근거

- 45만/년 ÷ 13일 ≈ 3.5만/일, 그러나 한 소집지에 집중되지 않음
- 실제 집단수송 10만 명이 수소 집결지를 거쳐 분산 배치 → **한 시점에 수천 명**
- 5,000–8,000명이면 23대×45명 = 1,035 수송력 → 5-8회 왕복/일, **큐잉·교통체증이 실전과 유사**
- BPR congestion 효과가 본격적으로 발현되는 수준

---

## 4. 공개 데이터 기반 (public-cited)

### 4.1 교통·도로

| 항목 | 출처 | 용도 |
|---|---|---|
| 한국 표준노드링크 (360,556 node / 971,680 edge) | 국토교통부, data.go.kr | 기본 도로망 |
| top-10 corridor (9,089 / 18,602) | 표준노드링크 필터링 | 분석 그래프 |
| VDS 5분 소통통계 | data.go.kr 15103521, bigdata-transportation.kr | BPR 보정 |
| 자동차 등록 통계 (2024년말 26,298천대) | 국토교통부 통계누리 | 차량 현황 |
| 국방부_육군 무기체계 현황 (1,867행 CSV) | data.go.kr | 군용차량 유형 |

### 4.2 철도

| 항목 | 출처 | 용도 |
|---|---|---|
| KORAIL 운행계획/운행정보 OpenAPI | data.go.kr 15125762 | S→R 서비스 파라미터 |
| KTDB GTFS 2023-03 | ktdb.go.kr | 환승역 구조, 확장 여지 |
| 국군수송사령부 조직 (3철도수송지원대 + TMO) | 국방부 조직도, 위키 | 철도 조직 실체 |
| "군용철도 이용 개별입영 체계 개선" | 병무청, 2022 정책뉴스 | 철도 활용 공식 확인 |

### 4.3 군수·동원

| 항목 | 출처 | 용도 |
|---|---|---|
| 병력동원소집 절차, 집단수송 체계 | 병무청 공식 FAQ, 규정 | 동원 절차 실체 |
| 2024 비상계엄 수송 실적 (107대, 1,500명) | 국방부→국회 제출, 경향신문·YTN | 실제 배치 패턴 |
| 중형표준차량 사업 (9,802대, 총 1조 7,061억원) | 2024 국정감사 부록 | 차량 보유 추이 |
| 방위사업 통계연보 2024 | 방위사업청 | 전체 차량 정수 |
| 국군수송사령부 + Kakao모빌리티 MaaS 논의 | 디지털투데이 2023-11 | 민군 협력 실태 |

### 4.4 학술 인용 (KCI 등재)

| 논문 | 저자/연도 | 기여 |
|---|---|---|
| 호송작전이 지상전에 미치는 중요성 연구 | 신현섭, 2020 (한국국방연구원) | 가상 전투모의로 호송 실패 시 전투력 현저히 저하 증명 |
| 시뮬레이션 모델을 활용한 군지여단 적정 전시 부대편성 | 백병호 | M&S 모델로 전시 부대편성 정량 분석 |
| 동원전력사령부 창설이 지상전에 미치는 함의 연구 | 홍민혁·구원근, 2020 | 동원사단+보충대대 구조의 전장 효과 |
| 미래 한국군 예비전력 정책발전 방안 연구 | 이웅·정민섭·박상혁, 2021 | STEPPER 변수로 예비전력 전망 |
| 예비군 자원감소에 대비한 한국 예비전력정책 연구 | 강용구, 2021 | 2040년 적정예비군 105.3만 명 |

### 4.5 방법론 선행연구

| 방법 | 출처 | repo 적용 |
|---|---|---|
| 최단경로 요격 (shortest-path interdiction) | Israeli & Wood 2002; Smith & Song EJOR 2019 | 위협 생성 model |
| 2단계 확률계획 (recoverable robust) | TR-B 2024; IEEE TEM 2025 | 적응정책 framing |
| SUMO 미시교차 점검 | Chen et al. 2020 | BPR external consistency check (literature cross-check only; not calibrated validation, not formal acceptance) |
| 우크라이나 Flee 3 철도 ABM | Springer 2026, khg.kname 2024 | 철도망 토폴로지 중요성 |

---

## 5. 실험 설계

### 5.1 메인 실험: Break-even 탐색

| 파라미터 | 설정 |
|---|---|
| **규모** | 5,000–8,000명 (메인), 2,000명 (sensitivity) |
| **변수** | S→R road_travel_time_multiplier: 1.0, 1.1, 1.2, ..., 3.0 (0.1 단위) |
| **고정** | 위협 유형 = fixed random baseline, 철도 상태 = available 1.0, 자원 프레임 = configured_bundle |
| **CRN** | 30 arrival seeds × multiplier 단계 |
| **출력** | mean Δ (bus − multimodal), paired t 95% CI, completion_rate |

**기대 결과**: multiplier 1.742 근처에서 Δ의 부호가 전환 (기존 결과와 일치하되 congestion 반영로 조정 가능)

### 5.2 강건성 실험: 위협 유형 교차

| 위협 유형 | 설명 |
|---|---|
| hash-random baseline | 기존 random 위협 (대조군) |
| path-interdiction | 예산-k 최단경로 요격 (Israeli & Wood) |
| segment-damage | A→S / S→R / R→D 기능적 세그먼트 타겟 |
| mixed | 위협 유형 혼합 (실전 유사) |

각 위협 유형 × 5.1의 multiplier ladder → break-even 이동량 측정

### 5.3 철도 상태 실험

| 철도 상태 | multiplier |
|---|---|
| available | 1.0 |
| degraded-1 | 1.25 |
| degraded-2 | 1.5 |
| degraded-3 | 2.0 |
| unavailable | 100 (실질적 비운항) |

각 상태 × 5.2 위협 유형 → "철도가 안 좋을 때 break-even이 어떻게 이동하는가"

### 5.4 자원 프레임 실험

| 프레임 | 구성 |
|---|---|
| configured_bundle | bus 23대 vs multimodal 23+23+rail |
| matched_road_fleet | bus 23대 vs 12 feeder + 11 last-mile + rail |

### 5.5 규모 Sensitivity 실험

| 에이전트 수 | 목적 |
|---|---|
| 2,000 | 낮은 congestion baseline |
| 5,000 | 메인 실험 |
| 8,000 | 높은 congestion |
| 12,000 | 극단적 congestion |

→ break-even이 규모에 의해 이동하는지 양적 확인

### 5.6 Morris Screening

5.2–5.5 모든 결과를 기반으로 elementary effects 계산 → 영향 인자 ranking. "이 인자만 바꾸면 답이 바뀐다"는 선언.

---

## 6. 논문 구조

| 장 | 내용 | 실험 | 인용 |
|---|---|---|---|
| **1. 서론** | 분평단 맥락, RQ 제기, 연구 기여 | — | 2019 보고서, 신현섭(2020) |
| **2. 방법론** | 시뮬레이터, 시나리오, 데이터, public-cited 근거 | — | 표준노드링크, 병무청, KORAIL |
| **3. 기준선** | 버스 vs 혼합, 두 프레임, paired Δ + CI | 5.1 (fixed threat) | repo 결과 |
| **4. 뒤집힘점** | S→R damage ladder → break-even + CI | 5.1 fine-grained | — |
| **5. 강건성** | 위협 유형·철도 상태·규모에서 break-even 생존 여부 | 5.2–5.6 | Morris, bootstrap |
| **6. 논의** | 규모 효과, 결정자 함의, 한계 | 종합 | 우크라이나 Flee 3, KakaoMobility |
| **7. 결론** | 조건부 판단, `final_study_ready=false` 명시 | — | — |

---

## 7. 데이터플로우

```
data/regions/goseong_mobilization.yaml
     + data/cache/goseong_nodelink_road.graphml
     + data/parameters/road_class_overrides.csv (public-cited)
     + data/scenarios/demand_profiles.csv (5,000–8,000 pax)
     + data/scenarios/fleet_profiles.csv (23 vehicles × roles)
     + data/scenarios/goseong_disruption_scenarios.csv (multiplier ladder + threats)
     + data/scenarios/policy_alternatives.csv (strict/adaptive)
     + data/parameters/rail_assumptions.csv (KORAIL cited)
→ src/realworld/adapter.build_simulator_graph()
→ src/scenario.run_scenario(G, config, policy, seed)
→ KPI dict → separated CSV
→ scripts/analyze_paper_revision_results.py
→ paired t, bootstrap CI, Morris, break-even interpolation
```

---

## 8. repo 수정 계획

### 8.1 즉시 수정

| 파일 | 변경 |
|---|---|
| `data/scenarios/demand_profiles.csv` | 1,000 → 5,000–8,000 pax (batch), arrival distribution 재조정 |
| `data/manifests/paper_revision_experiment_design.json` | 5.1–5.6 캠페인 추가 |
| `data/parameters/rail_assumptions.csv` | public-cited 출처 표기 추가 |
| `data/scenarios/goseong_disruption_scenarios.csv` | path-interdiction 행 추가 |
| `scripts/run_paper_revision_experiments.py` | 5.1 fine-grained multiplier ladder 지원 |
| `scripts/analyze_paper_revision_results.py` | scale sensitivity, Morris screening 출력 추가 |

### 8.2 이후 수정

| 파일 | 변경 |
|---|---|
| `src/models.py` | 8,000 agent 처리 최적화 |
| `src/traffic.py` | congestion 발현 수준 조정 |
| `src/disruptions.py` | path-interdiction 시나리오 모듈 |
| `data/parameters/fleet_profiles.csv` | actual 45인승 버스 비용 반영 |

---

## 9. 제약 사항 (논문에 반드시 명시)

1. **규모**: 5,000–8,000명은 하루 분산 배치의 한 소집지 집중 추정치. 실제 45만/년 중 동시다발적 배치는 아님. 결과는 비례적으로 해석.
2. **도로망**: top-10 corridor (9,089/18,602)로 제한. 전체 그래프(360,556)와의 차이가 extreme multiplier에서 영향 가능.
3. **평시 교통**: VDS 통계는 공급측 보정에만 사용. 수요측 배경교통은 A2(저배경 가정) 유지.
4. **좌표**: 공공 행정중심좌표만 사용. 실시설 좌표 불가.
5. **시나리오**: damage는 시뮬레이션 입력이며 실제 관측이 아님. "조건부" 표현 유지.
6. **조직**: 국군수송사령부+병무청 조직 반영하지만, 실제 동원 절차의 모든 예외·변칙은 미포함.
7. **final_study_ready=false**: 공식 수용 전. 연구는 "조건부 판단지원"이며 "운용계획"이 아님.

---

## 10. 일정

| 단계 | 내용 | 선행 |
|---|---|---|
| **1** | manifest·scenarios·profiles 수정 (5,000–8,000, path-interdiction) | — |
| **2** | 5.1 메인 실험 실행 (break-even fine-grained) | 1 |
| **3** | 5.2–5.4 강건성 실험 실행 | 2 |
| **4** | 5.5 scale sensitivity, 5.6 Morris | 3 |
| **5** | 분석 + 논문 초안 | 4 |
| **6** | claim language audit, oracle byte-identity 확인 | 5 |

---

## 11. 참고: 2019 보고서에서 상속한 것 (비교표)

| 2019 요소 | 2026 대응 | 비고 |
|---|---|---|
| 실시설 좌표 (A, S, R, D) | 공공 행정중심좌표 | **차이**: 좌표 정밀도 |
| 8.1만명 / 477소 / M+1~13일 | 5,000–8,000명 / 소집지 1개 / M+1일 | **차이**: 규모 축소, 조직 반영 |
| 내부 수요·가용 자료 | public-cited (병무청, KORAIL, data.go.kr) | **개선**: 투명성 |
| 운용계획 출력 | 조건부 판단 출력 | **변화**: RQ 재정의 |
| 내부 위협 시나리오 | hash-random + path-interdiction + segment-damage | **개선**: 원리 기반 |
| 미지정 방법론 | CRN + paired t + bootstrap + Morris | **계승**: 통계적 엄밀성 |

---

## 12. 부록: 주요 출처 URL

- 병무청: https://www.mma.go.kr
- 국방부 국방백서: https://www.mnd.go.kr (2022 백서 PDF)
- 표준노드링크 캐시: data/cache/goseong_nodelink_road.graphml
- 국방통계연보: http://dl.nanet.go.kr (방위사업청)
- 공공데이터포털: https://www.data.go.kr
- 국군수송사령부: https://ko.wikipedia.org/wiki/국군수송사령부
- KCI 학술지: https://www.kci.go.kr
- 조달엔 (나라장터): https://jodaln.com
- 병력동원훈련 계약공고: https://jodaln.com/bid/R26BK01308190/000

---

> 이 문서는 `agents.md`의 내용을 기반으로, 공개 데이터 수색 결과와 실험 설계 논의를 통합하여 작성하였다. 프로젝트의 모든 참여자는 이 문서를 기준으로 연구를 수행한다.
