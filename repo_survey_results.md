# Transport System Simulation - GitHub Repo Survey Results
> 조사일: 2026-04-30 | 총 9개 에이전트 × Opus로 병렬 조사

---

## 1. SimPy 기반 교통/수송 시뮬레이션

| Repo | URL | 관련성 | 설명 |
|------|-----|--------|------|
| HSR_Simulation_SimPy | https://github.com/dhareshvadalia/HSR_Simulation_SimPy | **매우 높음** | SimPy 기반 고속철도 시뮬레이션. 신호 블록, 정차시간, 처리량 최적화. 철도 모델링에 직접 참고 |
| capacity-python | https://github.com/mesflores/capacity-python | **높음** | SimPy + NetworkX + GTFS 기반 LA Metro Rail 시뮬레이션. 환승역 처리 포함 |
| simulation (mwong009) | https://github.com/mwong009/simulation | **높음** | SimPy DES 교통 시뮬레이션. 차량 단위 통계(통행시간, 대기시간) 추적 |
| TNDP_Evac_Heuristic | https://github.com/Jaiaid/TNDP_Evac_Heuristic | **높음** | SimPy + 대피/수송 시나리오 결합. Vehicle.py 모듈로 대중교통+대피 시뮬레이션 |
| FleetPy | https://github.com/TUM-VT/FleetPy | **보통** | Python 차량 fleet 시뮬레이션 프레임워크 (SimPy 외부 엔진). 아키텍처 참고용 |
| logistics_sim | https://github.com/hamk-uas/logistics_sim | **보통** | SimPy 물류 DES + C++ 최적화. 수거 스케줄링 패턴 참고 |

---

## 2. BPR 함수 / 교통류 모델링

| Repo | URL | 관련성 | 설명 |
|------|-----|--------|------|
| AequilibraE | https://github.com/AequilibraE/aequilibrae | **매우 높음** | Python 교통모델링 패키지. BPR VDF, Frank-Wolfe, 다중클래스 배정. SQLite 기반 네트워크 |
| dyntapy | https://github.com/p-ortmann/dyntapy | **높음** | BPR 정적 배정 + 동적 배정. JOSS 게재. NetworkX 호환 |
| Traffic_Assignment_Tutorial | https://github.com/sguo28/Traffic_Assignment_Tutorial | **높음** | BPR + Frank-Wolfe + MSA + PBA 파이썬 구현. 교육적 참고에 최적 |
| road_network_resilience | https://github.com/qiang-yi/road_network_resilience | **높음** | 재해 상황 도로망 복원력 평가. 링크 단계적 제거 + 복원력 지표. IJGIS 게재 |
| UXsim | https://github.com/toruseo/UXsim | **높음** | 순수 Python 거시/중시 교통류 시뮬레이터. 동적 경로 재배정. JOSS 2025 게재 |
| TAP101 | https://github.com/jdlph/TAP101 | **보통** | Traffic Assignment Problem 알고리즘 컬렉션. BPR 구현 비교 참고 |
| data2SupplyModel | https://github.com/asu-trans-ai-lab/data2SupplyModel | **보통** | BPR 파라미터(α, β) 실데이터 보정 방법론 |

---

## 3. 복합교통 (버스+철도) 시뮬레이션

| Repo | URL | 관련성 | 설명 |
|------|-----|--------|------|
| MATSim | https://github.com/matsim-org/matsim | **매우 높음** | Java 기반 대규모 에이전트 교통 시뮬레이션. 복합모드 선택, 반복 재계획. 업계 표준 |
| SBB Extensions (MATSim) | https://github.com/SchweizerischeBundesBahnen/matsim-sbb-extensions | **매우 높음** | 스위스연방철도(SBB) 제작. 결정론적 철도 + 확률적 버스 모델링. 환승 패널티 포함 |
| SUMO | https://github.com/eclipse/sumo | **높음** | 미시적 교통 시뮬레이션 표준. 복합모드 라우팅, GTFS 연동, Python API(TraCI) |
| BEAM | https://github.com/LBNL-UCB-STI/beam | **높음** | MATSim 확장. 당일 재계획, 실시간 모드 선택, 에너지 모델링 |
| eqasim | https://github.com/eqasim-org/eqasim-java | **높음** | MATSim 래퍼. 보행-접근-환승-도보 체인 모델링. 취리히/파리 사례 |
| A/B Street | https://github.com/a-b-street/abstreet | **보통** | Rust 기반 인터랙티브 교통 시뮬. 시나리오 시각화 프로토타입용 |

---

## 4. 대피 / 군사 수송 시뮬레이션

| Repo | URL | 관련성 | 설명 |
|------|-----|--------|------|
| pyMassEvac | https://github.com/DRDC-RDDC/pyMassEvac | **매우 높음** | 캐나다 국방연구소 제작. 대규모 대피 수송 의사결정 정책 시뮬. STRICT vs GRACE와 직접 유사 |
| MilitaryOperationsResearchRecipes | https://github.com/eidelen/MilitaryOperationsResearchRecipes | **높음** | 군사 OR 레시피 모음. 수송 문제 LP, 공격 하 물류 최적화. 운행시간 스케일링 참고 |
| MesaFireEvacuation | https://github.com/chadsr/MesaFireEvacuation | **높음** | Mesa 기반 화재 대피 ABM. 배치 파라미터 스윕, 시각화 포함 |
| MultiagentEvacuationSimulation | https://github.com/Zerkles/MultiagentEvacuationSimulation | **보통** | Mesa + Q-learning 다중 에이전트 대피. 가이드/피난자 상호작용 |

---

## 5. 네트워크 복원력 / DoE 실험설계

| Repo | URL | 관련성 | 설명 |
|------|-----|--------|------|
| pyDOE3 | https://github.com/relf/pyDOE3 | **매우 높음** | Python 실험계획법 라이브러리. 완전요인, LHS, 중합합성 등. pip install pydoe3 |
| ERIGrid2/toolbox_doe_sa | https://github.com/ERIGrid2/toolbox_doe_sa | **높음** | EU 프로젝트 DoE + 민감도 분석 툴박스. Sobol, eFAST, ANOVA. JSON 설정 기반 |
| network_robustness_simulation | https://github.com/tkEzaki/network_robustness_simulation | **높음** | 물류 네트워크 장애 시뮬. 장애/수요변화 실험 스크립트 구조 참고 |
| Network-Robustness-with-NetworkX | https://github.com/riki95/Network-Robustness-with-NetworkX | **높음** | NetworkX로 노드/엣지 제거 시 복원력 측정. 베르누이 장애 적용 가능 |
| ospf-network-simulation | https://github.com/mozqueda-alejandro/ospf-network-simulation | **보통** | 확률적 링크 장애 + 우회 라우팅 시뮬. 개념적 유사성 높음 |
| doepy | https://github.com/tirthajyoti/Design-of-experiment-Python | **보통** | 시뮬레이션 워크플로우용 DOE 생성기. 간단한 API |

---

## 6. 에이전트 기반 모델링 (Mesa / Hybrid DES+ABM)

| Repo | URL | 관련성 | 설명 |
|------|-----|--------|------|
| Mesa | https://github.com/mesa/mesa | **매우 높음** | Python ABM 표준 프레임워크. v3.5부터 DES 지원. NetworkGrid, StagedActivation |
| ABIDES | https://github.com/abides-sim/abides | **매우 높음** | Hybrid DES+ABM 프레임워크. Kernel 기반 이벤트 루프, 메시지 패싱 에이전트 |
| nxsim | https://github.com/kentwait/nxsim | **매우 높음** | SimPy + NetworkX 결합 네트워크 에이전트 시뮬. 본 프로젝트 아키텍처와 가장 유사 |
| Multi-Level Mesa | https://github.com/tpike3/multilevel_mesa | **높음** | Mesa 계층적 에이전트 확장. 개인→소대→중대 구조 모델링 가능 |
| Mesa-Geo | https://github.com/mesa/mesa-geo | **보통** | Mesa GIS 확장. 실지리 네트워크 필요시 활용 |
| Mesa ABM Tutorial (SFI) | https://github.com/SFIComplexityExplorer/Mesa-ABM-Tutorial | **보통** | 산타페연구소 Mesa 튜토리얼. 학습 참고용 |

---

## 7. 차량 배차 / 출발 정책 / 큐잉

| Repo | URL | 관련성 | 설명 |
|------|-----|--------|------|
| Network-performance-model | https://github.com/mbc96325/Network-performance-model | **매우 높음** | 용량제약 도시철도 이벤트 시뮬. 우선순위 승차배정. Transportation Research Record 게재 |
| buskit | https://github.com/ywnch/buskit | **높음** | 버스 holding 전략 시뮬. 승객 큐, 체류시간, 용량제약. pip install buskit |
| bus_bunching_sim | https://github.com/sarvaniputta/bus_bunching_sim | **높음** | 최소 체류시간 출발 정책. 버스 편대 방지 시뮬 |
| AMoD | https://github.com/Leot6/AMoD | **보통** | 자율주행 수요응답형 시뮬. MaxWait/MaxDelay 파라미터, 용량제약 |
| transit_opt | https://github.com/Hussein-Mahfouz/transit_opt | **보통** | 배차간격(headway) 최적화. PyMOO + GTFS + MATSim 연동 |

---

## 8. 몬테카를로 / CRN / 통계적 실험분석

| Repo | URL | 관련성 | 설명 |
|------|-----|--------|------|
| SALib | https://github.com/SALib/SALib | **매우 높음** | Python 민감도 분석 표준 라이브러리. Sobol, Morris, FAST. ~1300+ stars |
| monaco | https://github.com/scottshambaugh/monaco | **높음** | Monte Carlo 라이브러리. 시드 관리, 병렬 실행, LHS 샘플링 |
| stochastic_systems | https://github.com/health-data-science-OR/stochastic_systems | **높음** | DES 코스 자료. Warm-up, CI, 분산감소, 구성비교 방법론 |
| inventory-simulation | https://github.com/Arthurbdt/inventory-simulation | **높음** | SimPy DES 2D 파라미터 그리드, 다중 반복, CI, 등고선 플롯. 아키텍처 참고 |

---

## 9. 한국 교통 / 국방수송 관련

| Repo | URL | 관련성 | 설명 |
|------|-----|--------|------|
| SeoultrafficABM | https://github.com/dataandcrowd/SeoultrafficABM | **높음** | 서울 중심부 교통 ABM. A* 경로탐색, 시나리오 분석. NetLogo 기반 |
| OSMnx | https://github.com/gboeing/osmnx | **매우 높음** | OSM 도로망 다운로드/분석. 송파구 실도로망 구축에 필수. ~5000+ stars |
| CityFlow | https://github.com/cityflow-project/CityFlow | **보통** | 대규모 다중에이전트 교통 RL 환경. SUMO 대비 20x 빠름 |
| SUMO (Seoul 실험) | https://github.com/eclipse-sumo/sumo | **높음** | AgentSUMO 논문에서 서울 도시망 실험 수행. OSM 임포트 지원 |

---

## 핵심 발견: 본 프로젝트의 독창성

**기존 오픈소스 중 본 프로젝트의 핵심 기능을 모두 갖춘 것은 없습니다:**
- (1) 베르누이 확률적 도로 링크 장애
- (2) 우회 비용 계산
- (3) BPR 혼잡 모델 + 전시 스케일링
- (4) STRICT vs GRACE 출발 정책 비교
- (5) CRN 기반 페어 실험 + DoE 그리드 탐색

이 5가지가 통합된 단일 프레임워크는 존재하지 않습니다.

---

## 추천 기술 스택

| 구성요소 | 추천 도구 | 이유 |
|----------|-----------|------|
| 시뮬레이션 엔진 | **SimPy** + **NetworkX** | nxsim 패턴 참고. DES + 네트워크 그래프 |
| ABM (선택) | **Mesa** | NetworkGrid, StagedActivation. 개별 병력 에이전트 |
| BPR 혼잡 모델 | **AequilibraE** 또는 자체 구현 | Traffic_Assignment_Tutorial 참고 |
| 도로망 데이터 | **OSMnx** | 송파구 실도로망 확보 (고도화 단계) |
| 실험설계 (DoE) | **pyDOE3** | 완전요인 그리드 생성. 가볍고 파이썬 표준 |
| 민감도 분석 | **SALib** | Sobol 지수, Morris 방법 |
| 통계 분석 | **monaco** 또는 numpy/scipy | CRN 시드 관리, CI 계산 |
| 시각화 | **matplotlib** + **seaborn** | 히트맵, 파레토 곡선, 등고선 |
