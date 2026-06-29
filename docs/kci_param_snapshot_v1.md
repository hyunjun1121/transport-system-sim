# kci_param_snapshot — Phase-1 입력 파라미터 (2026-06-29 갱신, Phase-1 해결 반영)

> 결점-checklist **G4(param 근거)** 산출물. Phase 0에서 현행 코드 실제값을 file:line과
> 함께 동결하고 공개출처에 근거부여. **Phase 1(D-PARAM)**에서 식별된 불일치(α/lateness/
> noise/fleet)를 전부 단일 출처로 해결 — 본 문서는 해결 후 상태.
> 모든 값은 가정/추정치 — calibrated 아님. "준실험적 의사결정지원".

## A. 도로 자유통행속도 t0 / 용량 / 기본고장확률

소스: `src/realworld/attributes.py:40-55` (`ROAD_CLASS_DEFAULTS`, OSM highway class → t0/capacity).
t0 = length/speed_kph (`travel_time_min`, attributes.py:125). speed_kph는 OSM `maxspeed` 우선,
없으면 class default (attributes.py:104-106).

| highway class | speed_kph | capacity(veh/h) | base_p_fail |
|---|---|---|---|
| motorway | 100 | 2100 | 0.010 |
| trunk | 60 | 1700 | 0.015 |
| primary | 50 | 1300 | 0.020 |
| secondary | 40 | 1000 | 0.025 |
| tertiary | 30 | 750 | 0.030 |
| unclassified | 30 | 500 | 0.040 |
| residential | 30 | 400 | 0.040 |

**공개출처** (attributes.py:32-35 주석 인용): 도로교통법 시행령 제19조(법정 속도제한) /
Korea HCM 2004 도로용량편람(용량) / 국토부 도로설계기준(설계속도) / Suh et al. 1990
(서울 현장 용량) / Kim & Jung 2021 (서울 도시 속도제한 연구).

## B. BPR 링크저항함수 α/β — **Phase-1 해결 (단일 출처)**

| 위치 | α | β | 역할 |
|---|---|---|---|
| `src/models.py:19` (함수 기본값) | 0.15 | 4.0 | 라이브러리 fallback(미 FHWA) — config 미지정 시 |
| `src/realworld/pilot_experiments.py:1157` (**실행값**) | **0.36** | 4.0 | 단일 run 권위 — Goseong/pilot run에 적용 |

**해결**: Phase 0의 3종 충돌(default 0.15 / CLAUDE.md 0.36 / 실행 0.50) 중 **실행 shadow
0.50은 폐기**, 실행값을 문서=코드 단일값 **0.36**(한국 보정 방향값)으로 통일. 함수 기본값
0.15(FHWA)은 라이브러리 fallback으로 잔류(역할 분리, 문서화). CLAUDE.md 0.36 기재 = 코드와
일치(더 이상 stale 아님).

**근거**: 0.36 = 한국 교통 보정 방향성 추정치(KOTI 계열). calibrated 값 아님 — sensitivity
해석. 미 FHWA 0.15와 한국 현장이 중간~상향 보정된다는 방향성 반영.

## C. 철도 (KTX-Eum)

소스: `data/regions/goseong_mobilization.yaml:56-58`.

| param | 값 | 출처 |
|---|---|---|
| travel_time_min | 114 | KORAIL 공개 시각표(강릉선, 2022 정렬) |
| headway_min | 30 | KORAIL(peak 30 / off-peak 60 → 동원 시나리오는 30) |
| capacity_pax_per_train | 600 | KTX-Eum 6량 입석 환산(추정) |

operational_claim: `scheduled_service_proxy_not_emergency_availability` (평시 시각표 proxy,
비상 가용성 아님). Phase 2(rail 디젤폴백)에서 전시 헤드웨이 25-35min·순항속도 50% 반영 예정.

## D. 집결지연(lateness) 분포 — **Phase-1 해결 (anchor 적용)**

단일 출처 체인: `make_pilot_base_config`(mu2.45/sigma_levels[0.75]) →
`build_phase5_profile_rows` → `data/scenarios/demand_profiles.csv`
(`pilot_default_demand` arrival_param_mu=2.45/sigma=0.75) →
`apply_pilot_demand_fleet_profiles` runtime 적용.

| param | 값 | 출처 |
|---|---|---|
| distribution | lognormal_sample_fixture | — |
| mu | **2.45** | 진학은 et al. (2022) KCI anchor |
| sigma_levels | **[0.75]** | 진학은 et al. (2022) KCI anchor |
| correction_factor | **1.0** (default OFF) | 진학은 40% 과소평가 역산 1.67× — opt-in stress knob |

**해결**: Phase 0의 μ1.2/σ0.25(과소)를 anchor μ2.45/σ0.75로 통일. 단일 출처(demand profile)
권위화. **1.67× 보정**: 진학은(2022)이 ~40% 과소평가 보고 → 역산 1.67×. 단 2.45/0.75와의
**조합(composition)이 출처에서 검증되지 않았으므로 default 1.0(raw anchor)**, 1.67은
`lateness.correction_factor` opt-in stress로만(`scenario.py` 샘플 후 `delays *= factor`).
과잉 composite 산출 회피. CRN 보존(동일 seed → 동일 raw sample → scale).

`sensitivity_design.csv` `passenger_arrival_variability` sweep도 baseline 0.75(low 0.50 /
high 1.00)로 anchor centering — drift 제거.

## E. 시뮬레이션 horizon / 패널티 / 노이즈 — **Phase-1 해결 (#1 결정)**

소스: `pilot_experiments.py`.

| param | 값 | 의미 |
|---|---|---|
| `metrics.late_penalty_min` | 300.0 | penalized_makespan 전용 가중 — censored/completion 무관(G2) |
| `experiment.time_limit` | 200.0 | **censored_count 구동 노브**(=3.3h horizon). success_deadline_min ladder는 Phase 5 분리 |
| `stochastic.road_noise_sigma` | **0.0** | canonical deterministic baseline(Phase-1 결정 #1) |
| `stochastic.turnaround_noise_lambda` | **0.0** | canonical deterministic baseline(Phase-1 결정 #1) |
| `traffic.background_volume` | 300.0 | 배경 교통량 |
| `traffic.volume_window_min` | 60.0 | rolling window |

**해결 (#1)**: canonical baseline = **deterministic(0/0)** 으로 정합 — 재현성·claim 경계 확보.
0.05/0.2는 opt-in 탐색(Morris/sensitivity profile) 값으로 잔류. CRN은 noise level 무관 유효
(동일 seed 짝, `scenario.py:64-65`는 >0 일때만 스트림 생성 → 0이면 deterministic).

## F. 멀티모달 운영 param

소스: `pilot_experiments.py`.

- shuttle: fleet 3, dispatch 5min, turnaround 8min
- transfer: base 3.0min + per-pax 0.02min
- rail_first_departure 0.0
- lastmile: fleet 2, dispatch 5min, turnaround 8min, vehicle_capacity 8

연구권장(prompts-outputs/04) 환승비용: bus→rail 45-60min(대대급). **현행 transfer 3min은
과소** — Phase 1(환승비용 table 도입) 후속에서 보정 예정.

## G. fleet 가용률 — **Phase-1 해결 (문서 주장 철회)**

**해결**: "fleet 가용률 0.75" 스칼라는 **코드에 모델링되지 않음**이 확인됨. 시뮬레이터는
`FleetAvailability`(`src/fleet.py`)의 **finite fleet_size + turnaround 재사용**으로 가용성을
구조적으로 모델링 — flat 0.75 스칼라보다 현실적. 따라서 연구권장 "0.75 가동률"은 **문서
주장에서 철회**(high_level_plan G4 8-scalar list에서 제거). fleet_size/turnaround가 동원
시나리오 가용성을 담당함을 명시. 0.75를 별도 파라미터로 도입하지 않음(근거 없는 스칼라
추가 회피).

## Phase-1 해결 요약

| 항목 | Phase 0 상태 | Phase 1 해결 |
|---|---|---|
| BPR α | 3종 충돌(0.15/0.36/0.50) | 실행 0.36 단일화, 0.50 폐기 |
| lateness μ/σ | 1.2/0.25(과소) | 2.45/0.75(진학은 anchor), demand profile 권위화 |
| 1.67× 보정 | 문서 전용(미적용) | opt-in knob 구현(default OFF, 조합 미검증 명시) |
| noise #1 | 0.05/0.2(비영) vs "default 0" | canonical deterministic(0/0), 0.05/0.2 = opt-in |
| fleet 0.75 | 문서 주장(코드 無) | 주장 철회, finite-fleet+turnaround 구조 모델 명시 |

## claim 경계

- 모든 speed/capacity/headway/lateness는 공개 자료/학술 anchor 기반 **proxy/추정치**. 현장 검증 아님.
- α=0.36, μ=2.45/σ0.75는 **방향성 anchor** — calibrated 아님, "sensitivity" 표기.
- `final_study_ready=false` 유지.
