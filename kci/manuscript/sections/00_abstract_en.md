# Abstract

## English Abstract

Korean reserve-force mobilization transport must move large cohorts to designated training sites within a fixed time window, yet operational data are restricted and the relative resilience of single-mode (direct bus) versus multimodal (rail-bus) systems remains unverified for external researchers. This study applies four industrial-engineering tools — paired Common Random Numbers (CRN), censoring-aware performance metrics, Morris elementary-effects sensitivity, and a two-phase Design of Experiments — to a virtual Songpa-to-72nd-Division corridor abstracted from OpenStreetMap. A SimPy-based discrete-event simulator is exercised over a 5x7 disruption grid (35 cells) and a 4x7 policy grid (28 cells), with paired CRN seeds equalising road-failure draws, arrival times, and background traffic across modes. Under the planning-proxy parameterisation, the direct-bus mode showed a lower penalised makespan than the multimodal mode in all 140 Phase 1 baseline cells; under the heaviest pressure (congestion x2.0, road-failure scale 3.0, blocked links) bus completion was 0.967 versus multimodal 0.900. Morris screening ranked feeder fleet size, passenger volume, and rail headway as the leading drivers of penalised makespan. Results are reported as a conditional break-even map, not an operational recommendation; all parameters remain uncalibrated planning proxies pending follow-up validation.

**Keywords:** discrete-event simulation; reserve-force mobilization transport; paired common random numbers; censoring-aware metric; Morris sensitivity analysis

---

## 국문초록

상비전력과 예비전력의 통합 운용을 전제로 하는 동원 수송체계의 회복력은 평시 도로망 취약성과 결합되어 정량적 평가가 어렵다. 본 연구는 산업공학의 짝지은 공통난수(paired CRN), 검열 인식(censoring-aware) 지표, Morris 기초효과 민감도, 2단계 실험설계(DoE)를 결합한 통합 프레임워크를 송파↔양주 부곡리 가상 회랑(OSMnx 기반)에 적용하여 단일수단(버스)과 복합수단(철도-버스)의 회복력을 비교한다. SimPy 이산사건 시뮬레이터를 활용해 도로 장애 격자 35셀(Phase 1)과 정책 격자 28셀(Phase 2)을 평가하였다. 미보정 계획 프록시 조건에서 단일수단은 Phase 1 베이스라인 140셀 모두에서 벌점 메이크스팬이 더 낮았으며, 최고 압박 조건(혼잡 2.0배, 장애 강도 3.0, 차단 모드)에서도 단일수단 완료율 0.967, 복합수단 0.900이었다. Morris 분석은 피더 차량 수, 인원 수, 철도 헤드웨이를 주요 인자로 식별하였다. 결과는 운용 권고가 아닌 조건부 break-even 지도로 보고된다.

**핵심어:** 이산사건 시뮬레이션; 예비군 동원수송; 짝지은 공통난수; 검열 인식 지표; Morris 민감도 분석
