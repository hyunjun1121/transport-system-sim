# High-Level Plan: 결점 없는 새 설계 빌드 + 전체 실험 재실행

> 2026-06-29 작성. 리셋 전 코드(기횰서 수치 84/52/36 산출)는 폐기. **현재 OSM 기반 2모드
> 시뮬레이션을 새 권위 기반으로 삼고**, 결점-checklist 7종을 통과하는 설계로 재빌드 후
> 전체 실험을 재실행한다. 모든 산출은 "준실험적 의사결정지원" — 운용계획/예측/검증/
> 최적경로/최종완료 표현 금지. `final_study_ready=false` 유지.

## 1. 목표

- 기횰서 수치(리셋 전 산물) 추적/erratum **중단** → 새 설계에서 재생성된 수치가 권위.
- 단일 코리더·2모드(bus vs rail-bus) → **다코리더·복합운송(road/rail/sea/air)·다층 위협사다리**.
- 결점-checklist 7종 **전부 green**인 설계에서 전체 실험 재실행 → 기횰서/report/paper/kci/web_demo 갱신.

## 2. 원칙 (불가양보)

- **CRN 짝실험**: bus-only vs 복합대안 동일 seed → delta를 수송구조 탓으로 귀속.
- **결정론적 within-scenario**: noise는 탐색적 profile에만 (Phase 0에서 기본값 정합).
- **오프라인 기본**: cached OSM GraphML. live 추출 opt-in.
- **보안**: 공개 행정중심/공용 교통망/공식 교리/공법(law.go.kr) only. 실제 부대 좌표·편제·이동일정 금지. 모드 확장 시 `coordinate_class != 'public'` guard 테스트 **선행**.
- **claim 경계**: `scripts/audit_claim_language.py` green 유지.

## 3. 수용 게이트 (결점-checklist 7종) — 설계 통과조건

| # | 게이트 | 통과 조건 | 관련 코드 |
|---|---|---|---|
| G1 | topology | OSM 도로망 결점 무 (현행 OK) | `osm_network.py`/`adapter.py` |
| G2 | deadline/censoring | censored 구동 = `time_limit`/`success_deadline_min` 명시·문서화 (`late_penalty_min`=penalized 전용과 분리) | `metrics.py`, `pilot_experiments.py:1150` |
| G3 | CRN 짝 | bus/multimodal **4스트림**(arrival/failure/road_noise/turnaround) 동일 seed 증명 — 직실행 테스트 + `seed_stream_id` 증명열 | `scenario.py:59-65`, `audit_crn_pairing.py` |
| G4 | param 근거 | 스칼라(속도/용량/BPR α=0.36(Phase-1 단일화)/rail 114·30·600/lognormal μ2.45·σ0.75(진학은2022)/1.67× opt-in knob/censoring 1-5%) 공개출처 인용, file:line 검증. **fleet 0.75 스칼라 철회 — finite-fleet+turnaround가 가용성 구조 모델** | `attributes.py`/`network.py`/`rail.py`/`models.py`/`fleet.py`/`goseong_mobilization.yaml` |
| G5 | validation | OSRM/실거리 sanity 통과 (quasi-real anchor) | `scripts/run_osrm_route_benchmark.py`, `run_plausibility_validation.py` |
| G6 | ML 정직성 | 기재=코드 일치 (XGBoost 4급 + KMeans + SHAP + NL **실제 구현** or 문서 정정) | `ml_analysis.py` |
| G7 | claim | `audit_claim_language.py` green + 게이트 ledger 정합(10 evidence-triage vs 15 acceptance 중 권위 1종 지정) | `scripts/audit_*.py`, `status.md` |

## 4. 단계 로드맵

> 원칙: **새 모드/코리더 추가 전에 현재 2모드 설계를 결점 없게(G2-G7) 만든다** → 그 위에
> contract 확장 → mode/corridor/threat leaf → 전체 재실행 → ML → 산출물 갱신.

### Phase 0 — 무결성 기반 (현재 2모드 시뮬 결점 제거, 06-30 freeze 포함)
- G2 deadline 노브 정합: `time_limit`/`success_deadline_min`/`late_penalty_min` 분리·문서화
- G3 CRN 4스트림 증명 테스트 + noise 기본값(0.05/0.2) 정합 결정 + `seed_stream_id` 증명열
- **G4 Phase-1 입력 freeze** `kci_param_snapshot_v1` (8 스칼라 + 공개출처, 2026-06-30) + tag
- G5 OSRM/플라우지빌리티 벤치마크 실행
- G6 ML 현황 기록(`ml_baseline_v1.json` macro-F1 @15,870행) + kci_redesign/01·02 정정
- G7 claim audit + 게이트 ledger 정합
- results provenance: sha256 증명원장 + INTEGRITY_BASELINE tag + 오해 32행 scaffold 보관 이동

### Phase 1 — contract 확장 (rework multiplier, 1회)
- `types.py`: `RegionSpec.rail` → `region_services: tuple[RegionServiceSpec]` (mode ∈ {rail,sea,air}, access/egress PortPointSpec, fuel_type, fallback). computed `rail:` alias 보존(약 90 scaffolding 호출 호환)
- **`tests/test_public_coordinate_guard.py` 선행** (비공개 좌표 거부)
- `adapter.py`: canonical_ids 데이터 구동, `_validate_edge_attrs` mode-set → {road,rail,sea,air}, REQUIRED_ROUTES region 구동
- `scenario.py`: composable multi-service pipeline (bus_only/multimodal legacy 보존)
- `pilot_experiments.py`: service-list 기반 config build + case-failure 전 서비스 링크 변이
- `transfers.py` + 환승비용 table (bus→rail 45-60min 등, per-leg base+per-pax)
- backward-compat goseong yaml loader + 164 직실행 테스트 green

### Phase 1.5 — contract 확장 hardening (2026-07-01 defect-hunt 전수 감사 + 근본해결)

> Phase 1(composable multi-service) verify 이후 6-lens finder + 3-skeptic adversarial verify
> 워크플로(51 agent, 842 tool-call) + 독립 byte-identity 재현으로 결점 전수 탐색.
> **판정: 시뮬 엔진 자체 CLEAN** — byte-identity·determinism·correctness 3 lens 결점 0.
> oracle 6 runs 정밀 일치(sha `fe963e74`, bus 287.81 / mm 290.68). 결점 전부 =
> defense-in-depth / contract-validation / test-quality 영역(엔진 아님).

**확정 코드 결점 (6건, contract/test 양 lens 중복 1건 병합)**

| ID | 심각 | 위치 | 결점 | 근본해결 |
|---|---|---|---|---|
| C1 | HIGH | `src/realworld/types.py:401,928` | `PortPointSpec.coordinate_class` 미값검사 + `assert_public_coordinate_policy`가 port 레벨 **전혀** 미검사. docstring "non-public port 거부" 약속 위반. `region_services[].access.coordinate_class='military_unit'`이 로드+guard 통과 → **보안경계(실좌표/OOB 차단) 미집행** | (a) `ALLOWED_PORT_COORDINATE_CLASSES={public,synthetic}` PortPointSpec 검사 (b) guard에 `region_services[].access/.egress` 순회 거부 (c) 허용집합 위반 거부 테스트 추가 |
| C2 | HIGH | `tests/test_composable_service_pipeline.py:95` | byte-identity(#1 invariant)를 assert하는 테스트 **0개**. rail-default는 `train_trips>0`+`breakdown=={}`만. `oracle.json` 아무 코드도 안 읽음 → silent KPI drift green 유지 | oracle.json 로드 → 핀 seed(1101-1103) bus_only+multimodal 재실행 → KPI bit-equal(`abs<1e-9`) 단정 신규 테스트 |
| C3 | MED | `src/realworld/types.py:725,920` | 동일 mode 중복 서비스 허용 → `simulator_node_ids` silent collide(첫 port 증발), boundary 에러 라벨 모호. consumer `tests/test_realworld_region_reusability.py:32`→`assert_graph_ready` 우회 가능 | `__post_init__`/`_validate_service_tuple` mode-uniqueness guard + boundary 라벨 인덱스화 |
| C4 | MED | `src/realworld/types.py:928` | guard opt-in/단일호출(`pilot_experiments.py:949`만). `load_region_spec`/`build_simulator_graph` 우회 → restricted region이 공용 API로 시뮬 진입(2 confirmed/1 refuted = carry-vs-enter 설계 주장, 판단 분분) | guard를 `RegionSpec.__post_init__`로 승격 OR 모든 공용 진입점에 추가 + 기존 guard 테스트 패턴 조정 (대안: opt-in 설치로 문서화) |
| C5 | MED | `tests/test_composable_service_pipeline.py:132` | `'service_mode' in str(exc) or 'service' in str(exc)` — 'service' 단어만으로 임의 에러 pass → guard 회귀 감지불가 | 구체 fragment `and` 결합 단정(`multimodal.service_mode` + `requires a multimodal.service`) |
| C6 | LOW | `src/scenario.py:286-304` | `_resolve_service_spec` mode 집합 검사 무 → `service_mode='bus'/'xyz'` 무오류 실행, `service_breakdown['bus']` 작성(2 confirmed/1 refuted = defensive-only) | 비-rail 분기에 `{sea,air}` membership guard + ValueError |

**리포 위생 (커밋 전 정리, 5건)**
- H1 `kci/`→`previous-kci/` rename 정규화(`git mv`, 현재 246파일 D + 신경로 `??`)
- H2 CLAUDE.md `kci/` 참조 → `kci_redesign/`/`previous-kci/` 갱신
- H3 `_te.txt`(0바이트) 삭제
- H4 `results/_shap_install.log`·`results/_phase15_staged.log` gitignore 또는 삭제
- H5 `cloned_repo/osmnx/.../short.graphml` revert(무시대상 참조트리 변조)

**완료 기준 (Phase 1.5 exit)**
- C1–C6 전부 근본해결 + 단정 추가, 169+ 직실행 green, byte-identity 독립재현 유지(oracle 정밀 일치)
- H1–H5 정리
- claim discipline 유지(`final_study_ready=false`), security 경계(C1) 확실히 집행
- 산출 framing = decision-support / quasi-real / sensitivity 유지

**상태: 해결 완료 (2026-07-01)** — C1–C6 + C1/C3/C6 회귀단정 전부 근본해결. 사용자 "전부 근본 해결, 나머지는 판단에 맡김" 위임.

**해결 내역**
- **C4 설계 결정 = Design A (강제 집행)**: 보안경계는 opt-in이 될 수 없음. guard를 `RegionSpec.__post_init__`로 승격 → `load_region_spec`/`load_region_registry`/`get_region_spec`/`build_simulator_graph` 전 공용 진입점이 단일 지점에서 집행. 사전 조사: production/test 어디도 restricted `RegionSpec`을 "carry"하지 않음(privacy_review_packet은 raw dict metadata만 읽음) → carry-vs-enter 구분은 사실상 dead flexibility, 승격이 안전.
- C1: `ALLOWED_PORT_COORDINATE_CLASSES={public,synthetic}` 상수 → `PortPointSpec.__post_init__` 구조 시점 허용집합 검사(non-public port 생성 자체 거부) + guard의 `metadata.coordinate_class` 검사도 동일 허용집합으로 통일. docstring 정정.
- C2: `test_byte_identity_against_oracle` 신규 — `oracle.json` 로드 → base-config sha 단정(`fe963e74`) + 6 runs(bus_only/multimodal × 1101-1103) × 10 KPI bit-equal(`abs<1e-9`). 발견: `_base_config()`의 `time_limit=600` override가 sha drift 원인 → 제거(oracle=480 8h 작전창).
- C3: `_validate_service_tuple` mode-uniqueness guard(동일 mode 중복 → last-wins collide 차단) + `_validate_points_inside_boundary` 라벨 인덱스화(`region_services[i].access`).
- C5: `'service_mode' in str(exc) or 'service'` → `and 'multimodal.service'` 구체 fragment 결합. + 신규 `test_unsupported_service_mode_raises`(C6 회귀단정).
- C6: `scenario.py` `_NON_RAIL_SERVICE_MODES={sea,air}` 로컬 상수(core→realworld 의존 무) + `_resolve_service_spec` 비-rail 분기 membership guard + ValueError.
- 회귀단정: C1 hostile-repro port(`military_unit` 구조 거부) + restricted 구조 시점 거부 / C3 duplicate-mode 거부.

**검증**: types + guard + composable 직실행 green. 느린 전수셋 + adversarial re-hunt 진행 중.

**Adversarial re-hunt round (2026-07-01, workflow 17 agent / 742k tok)** — C1-C6 고친 코드를 6-lens finder + 3-skeptic verify로 재검증. 3 lens CLEAN(contract-validation/byte-identity/regression). C1-C6 자체는 전부 정상(엔진 무결점). 단 C2 oracle **test-quality** + 경량 hardening 영역 6건 추가 발견 → 전부 근본해결:

| ID | 심각 | 결점 | 근본해결 |
|---|---|---|---|
| F2 | HIGH | oracle.json 미추적 → fresh clone FileNotFoundError + 가변(KPI checksum 무) → silent-regeneration 우회 가능(bypass_confirmed=true) | `scripts/generate_phase23_oracle.py` 신규(단일 출처, 결정론적) + oracle 재생성(full 27-key as_dict + `runs_sha256`) + `git add`(공유/불변). test가 `runs_sha256` 검증 → hand-edit 즉시 탐지 |
| F3 | MED | C2가 27 key 중 10개만 pin, docstring "byte-identical" 과장 | oracle을 full `as_dict()` 27-key로 재동결 → 문자 그대로 전-key identity. docstring 정정("full-key rail/bus identity") |
| F4 | MED | oracle 축소(키 삭제) 미감지(단방향 검사) | `set(result.keys()) == set(expected.keys())` 양방향 단정 → shrink/add 모두 탐지 |
| F1 | LOW | legacy `rail:` 경로 `_region_service_from_legacy_rail`이 coordinate_class 미전달 → 'public' silent-normalize(region_services path와 불일치) | raw access/egress mapping에서 coordinate_class 전달 → PortPointSpec 검증 통과. legacy-rail hostile 거부 회귀단정 추가 |
| F5 | LOW | sea test가 `trips>0` 만 → 2x minutes corruption 미탐지(widening 핵심이 least-pinned) | `breakdown['sea']['minutes'] == trips*travel_time` 구조단정 추가 |
| F6 | LOW | `load_pilot_inputs:949` guard가 이제 dead(`__post_init__`에 승격) → 오해 유발 | fail-fast pre-check로 주석 정정(제한 region을 105MB graphml 로드 전 ms 단위로 거부; 권위는 `__post_init__`) |

**최종 검증**: full 직실행 수트 green. claim audit 무변(40 blocker 전부 기존 docs, 편집/신규 파일 0건). `final_study_ready=False` 유지. byte-identity 독립재현 유지(oracle full-key, sha fe963e74/a248663b).

### Phase 2 — mode 확장 (leaf)
- P2a rail electric→diesel fallback (L3 전철마비 시, service-list+fuel_type 소비)
- P2b sea (LST/Ro-Ro, **조건부** default-OFF, 항만 수심/ASW 전제)
- P2c air (CN-235/C-130, **조건부·소수**, 공개 민간 공항 좌표만)

### Phase 3 — 다층 위협사다리 L1-L4
- `disruption_scenarios` 기존 패밀리 → L1(국소)/L2(광역다중)/L3(철도+C2)/L4(총체) 레벨 재태깅
- BPR 링크차단/용량감소/지연 매핑 유지
- L2 다중차단 rerouting 종료 테스트 (32행 scaffold의 inf makespan 회귀 방지)

### Phase 4 — 코리더·집결지 다변화
- 5 region spec: C1 수도권→영동북부고성 / C2 →영서내륙 / C3 →경기북부철원 / C4 영남→동해안 / C5 호남→서해안접경
- 4 집결지: 잠실 / 킨텍스(5t/㎡) / 수원메쎄(수원역 연계) / 인천아시아드
- 치명적링크 태그(대관령 21.7km·인제양양 10.9km·진부령/미시령·임진강/한강교) `evidence_class:scenario_assumption`
- multi-hop 대체코리더 rerouting (단일 edge fallback 대체)
- privacy review packet 다중집결/다중코리더 확장

### Phase 5 — KPI + 실험설계
- KPI 매핑 문서화: makespan(증창설완료)/completion_rate(조기투입)/penalized(대체자산배분)
- `success_deadline_min` ladder 5/6/7/8/10/12h
- Tier 설계 매트릭스 (kci_redesign/03 §8): A 코리더비교 / B 위협사다리심화 / C 모드확장 / D 집결지다변화
- design profile `pilot_experiments.py` 추가

### Phase 6 — 전체 실험 재실행
- CRN 짝실험, deterministic, offline (cached graphml)
- 각 Tier 실행 → results/{tier}/ CSV + sha256 manifest
- paired-delta-CI (within-seed bus−multimodal)

### Phase 7 — ML layer 실제 구현
- XGBoost 4급(정상/주의/위험/실패위험) + 물리 feature(threat_index/mode-mix/fallback/critical-link survival/corridor-id/BPR v·c/환승/fleet)
- KMeans 상황군집 + SHAP TreeExplainer
- 자연어 판단요약(근거 수치만, hallucination guard, claim audit)
- ablation: G1 현행 XGBoost vs G7 물리feature (P1 ml_baseline_v1.json 비교)

### Phase 8 — 산출물 갱신 (새 권위수치로)
- 기횰서/report_draft.md/paper/kci 표·도 갱신 (동일 sha256 baseline 인용)
- web_demo 데이터 바인딩 파이프라인 (stale abstract CSV 교체, results→web_demo/public/data/ sha256 전파, Vercel 동기화)
- 3 manuscript(한국 report / EN paper / kci) claim altitude 정합

### Phase 9 — 검증·게이트·claim 종료
- 전 게이트 재실행, validation_package 산출
- Morris/Sobol 전역 민감도 (확장 contract에 재적용)
- clean-checkout 재현 smoke 테스트
- `final_study_ready=false` 유지, "12게이트 human signoff 대기"로 포지셔닝

## 5. 수용 게이트 추적 (Phase 종료 시 갱신)

| 게이트 | 현재 | 목표 Phase |
|---|---|---|
| G1 topology | ✅ | — |
| G2 deadline | ✅ **Phase-1.5: `success_deadline_min` decouple 구현(metrics.py, backward-compat) + time_limit 200→480(8h)로 multimodal censor 블로커 해결(양 모드 completion=1.0)**; ladder sweep(5/6/7/8/10/12h)은 Phase 5 | Phase 0→5 |
| G3 CRN | ✅ | Phase 0 |
| G4 param 근거 | ✅ Phase-1(α0.36/μ2.45σ0.75/noise deterministic/1.67×knob/fleet0.75철회) | Phase 1 |
| G5 validation | ✅ machinery + ✅ **Phase-1 실제 Goseong OSM 그래프(197,819 nodes/298,012 edges, A→D 189km, plausibility 16/5/0)** | Phase 0→1 |
| G6 ML 정직 | ✅ **Phase-1.5: 실제 그래프 ML re-baseline(staged 280행, `ml_baseline_realgraph_v1.json`); KMeans/SHAP/NL 전 구현·실행 확인; macro_f1=1.0은 bimodal scale artifact로 정직 명시** | Phase 0→7(full 15,870행 ablation은 Phase 6-7) |
| G7 claim | ✅ **Phase-1.5: sensitivity gate coupling 근본 해결(거짓 manifest 폐기 + decouple) + plan audit/mission 섹션 정합** | Phase 0 |

## 6. 미결정사항 (사용자 결정)

1. **noise 기본값** ✅ **Phase-1 해결**: canonical deterministic(0/0), 0.05/0.2 = opt-in 탐색(Morris/sensitivity). CRN은 level 무관 유효.
2. **공모 scope**: Phase 0+1(2모드 de-risk) 출하 vs redesign leaf(P2-P7) 동반 출하? (공모 데드라인 미상)
3. **seed parity**: 축소(10/30 혼합) vs full 30 (5코리더→100k+행)
4. **해상/항공 공개 좌표 소스**: 검증 민간 항만/공항 centroid vs fixture 합성
5. **게이트 ledger 권위**: 10 evidence-triage vs 15 acceptance — KCI 정식은 1종 지정(추천 15 acceptance)

## 7. claim 경계 (재확인)

- 기횰서 84/52/36 = 리셋 전 코드 산물 → **추적 중단**, 새 설계 수치로 대체.
- 모든 수치는 공개출처/교리 기반 가정·추정치. calibrated 아님.
- 결과 = 민감도·의사결정지원 해석 only.
