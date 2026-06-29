# Implementation Plan — Phase 1: 결점 전부 근본 해결 (defect-free base)

> Phase 0 완료(7게이트 진단). Phase 1 = 식별된 4개 결점군 전부 근본 해결.
> 사용자 위임("전부 근본 해결만 가능하면 전부 해결해") + audit 추천값으로 판단.
> `docs/feasibility_ruling_2026-06-29.md` = 결점별 verdict/결정 근거. 산출 = 준실험 의사결정지원.

## 단계 순서

| 순 | 결점 | 작업 | 오프라인 | 상태 |
|---|---|---|---|---|
| 1.1 | D-PARAM | α0.36/μ2.45σ0.75/noise0/correction knob 구현 + doc 정합 + fleet0.75 철회 | yes | 진행 |
| 1.2 | D-CLAIM | gate hardening + 3/15→2/15 doc + #5 ruling | yes | 대기 |
| 1.3 | D-ML | CLAUDE.md 정정 + KMeans/SHAP/NL 구현 + shap dep | yes | 대기 |
| 1.4 | D-GOSEONG | corridor-tiled Overpass 실추출 + connector floor + plausibility 재검증 | **live(opt-in)** | 대기 |
| 1.5 | — | 직실행 테스트 전수 + 결과 stale 처리 + plan/memory 갱신 | yes | 대기 |

---

## 1.1 D-PARAM — 입력 파라미터 단일 출처화

**편집**:
1. `src/realworld/pilot_experiments.py:1154` `bpr.alpha` 0.50 → **0.36** (한국 보정 방향값)
2. `pilot_experiments.py:1159` `lateness.mu` 1.2 → **2.45**; `:1160` `sigma_levels` [0.25] → **[0.75]** (진학은 2022)
3. `pilot_experiments.py:1167-1169` `stochastic` road_noise_sigma/turnaround_noise_lambda 0.05/0.2 → **0.0/0.0** (canonical deterministic baseline)
4. **1.67× 보정 knob 구현**: `lateness` 블록에 `correction_factor: 1.0`(default OFF) 추가 + `src/scenario.py` arrival-delay 샘플 후 `delays *= correction_factor`. 출처 주석(진학은 40% 과소평가 역산 1.67, 조합 미검증으로 default 1.0).
5. **fleet 0.75 철회**: `high_level_plan.md` G4 8-scalar list + `docs/kci_param_snapshot_v1.md`에서 "fleet 가용률 0.75" 제거/재기표 ("finite-fleet + turnaround 재사용으로 가용성 모델링, flat 스칼라 아님").
6. `docs/kci_param_snapshot_v1.md` 갱신: run α=0.36 / library default α=0.15(FHWA) / 0.50 shadow 제거 명시, lateness 2.45/0.75, noise deterministic, correction knob 설명.

**테스트**: `tests/test_*.py` 직실행 (lateness/BPR/metrics 관련). 결과 CSV stale 표시.

---

## 1.2 D-CLAIM — gate 정직 + ledger 권위

**편집**:
1. `src/realworld/final_study_readiness.py:848-864` `_real_input_smoke_gate()` hardening: 그래프가 plausibility 통과(or stub 임계 초과 edge 수) 요구 추가 → stub에서 false-green 불가.
2. `status.md:15-16` + `agents.md:58-60/136-139` "3/15" → **"2/15 (real_input_smoke re-blocked until real Goseong extraction)"**.
3. `docs/g7_claim_and_gate_ledger.md` §3 #5 ruling 확정(15-gate = 권위, 12-artifact = human signoff 층).

**테스트**: `tests/test_realworld_final_study_readiness.py` + `test_realworld_goal_completion_audit.py`.

---

## 1.3 D-ML — AI layer 정직 + 컴포넌트 실구현

**편집**:
1. `CLAUDE.md:52,130-132` ML 기재 정정: 현행 = XGBoost 4급 라벨규칙(정의됨) + gain feature_importance only; KMeans/SHAP/NL = Phase-1 구현(또는 planned). kci_redesign/02 정정 상태와 정합.
2. `src/realworld/ml_analysis.py`:
   - **KMeans** 상황군집 추가(sklearn.cluster.KMeans, feature matrix에 fit → cluster_id/centroid summary). ~80-120줄.
   - **SHAP** TreeExplainer wrap(`requirements-ml.txt`에 shap 추가, try/except guard + gain-FI fallback). ~60-100줄.
   - **NL 판단요약** templated generator(metrics + top feature + cluster → claim-guard 통과 한국어 brief). hallucination guard.
   - stratified split 고려(index%5 → StratifiedKFold for imbalanced).
3. `tests/test_realworld_ml_analysis.py` KMeans/SHAP/NL 단정 추가.

**의존**: 의미있는 4급 재baseline은 1.4(D-GOSEONG) 이후. 코드는 현 CSV(stub)로 pipeline 검증, 산출은 stub-caveat 유지.

---

## 1.4 D-GOSEONG — 실제 Goseong 그래프 (live opt-in)

**작업**:
1. `scripts/build_goseong_cache.py` 신규: `build_pilot_cache.py`의 Overpass 템플릿 일반화. **코리더 버퍼 타일링** 전략 — waypoint 구간별(Songpa→Cheongnyangni→…→Goseong) 4km buffer bbox, `way["highway"~"motorway|trunk|primary|secondary"]` 필터, 타일 stitch(node/edge dedup). 단일 100×176km bbox timeout 회피.
2. `--source overpass` 1회 live 실행 → `data/cache/goseong_corridor_road.graphml` 교체 + reviewer manifest(`source=live_overpass_osm_snapshot`, sha256, node/edge 수, claim_limit).
3. `src/realworld/zones.py:20` `MIN_CONNECTOR_T0_MIN` 0.01 → **0.1** (최소 feeder 시간 안전망; 실거리는 real 그래프 snapping이 담당).
4. `scripts/run_plausibility_validation.py` Goseong 재실행 → A→D/A→S/R→D 실거리 band 통과 단정.
5. `data/scenarios/goseong_disruption_scenarios.csv` betweenness 타겟 edge가 real 위상에서 존재하는지 재검증(깨지면 재태깅).
6. `scripts/build_goseong_corridor.py`(synthetic)는 `--source fixture` 전용으로 relabel, 실 cache 덮어쓰기 차단.

**보안**: 전 좌표 공개 행정중심/공용 교통망(`coordinate_class=public`). 실제 부대 좌표 無.

---

## 1.5 마무리 — 테스트 + provenance + 문서

1. `Get-ChildItem tests\test_*.py` 전수 직실행 → green.
2. `main.py --test/--quick` + `run_pilot_experiments.py --sample` Goseong 재생성(stale CSV 교체).
3. ML 재baseline(신 Goseong CSV, 4급 populate 확인).
4. `high_level_plan.md` Phase-1 게이트 ✅, `docs/integrity_baseline` 갱신.
5. memory 영속화.
6. results provenance: 신 sha256 ledger, goseong_pilot 교체 정당화(신 그래프 산물).

## 완료 기준 (Phase 1 exit)

- D-PARAM: 단일 출처, doc=code 일치, 테스트 green
- D-CLAIM: real_input_smoke honestly red(or real graph로 정당 green), #5 ruling
- D-ML: KMeans/SHAP/NL 실구현 + CLAUDE.md 정정 + 테스트
- D-GOSEONG: 실제 OSM Goseong 그래프 + plausibility 통과 + connector 정상
- 직실행 테스트 전수 green
- → Phase 2(mode 확장) IMPLEMENTATION_PLAN으로 이행

---

## Phase 1.5 — 잔여 결점 전부 근본 해결 (사용자 2차 위임 "전부 해결해")

> Phase 1(4결점) 완료 후 보고된 6 잔여 중 4개 근본 해결. #5(OSRM, 오프라인 불가→deferred), #6(acceptance-audit gotcha, 학습 보존)은 비코드.

### 1.5.1 #4 sensitivity_strategy_readiness — 부정직 manifest + 게이트 coupling (근본 결함)
**진단**: committed manifest가 `publication_ready=true`/가짜 `reviewer_accepted`/`blocking=0,human=0`로 **거짓**. `_sensitivity_gate.ready`가 `strategy_blocking_count==0 AND strategy_human_review_count==0` 요구하지만, 정직 generator는 항상 ≥1 human-review 행 산출(classifier에 resolved 분기 없음). → 게이트 green 유지 유일 방법 = 거짓 manifest. 두 테스트 충돌.
**근본 해결(decouple)**: review-packet triage 항목은 review aid → gate `ready`에서 2조건 제거, details만 기록. 게이트 ready = acceptance-record + scope + count-match + artifacts. 거짓 manifest 없이 정직 manifest + gate green 동시 가능.
1. `final_study_readiness.py` `_sensitivity_gate`(L2737-2746): `ready`에서 `strategy_blocking_count==0 and strategy_human_review_count==0` 제거. blockers 리스트 로직은 `not ready` 시에만 노출되므로 유지 가능.
2. `write_sensitivity_strategy_readiness_packet`로 committed CSV/manifest/doc 정직 재생성(publication_ready=False, 정직 status_counts).
3. 검증: `test_realworld_sensitivity_strategy_readiness_packet.py` PASS + `test_realworld_final_study_readiness.py` 여전 PASS.

### 1.5.2 #3 test_realworld_plan_audit — plan.md 섹션 누락
**진단**: commit `afd8bfbf`가 plan.md 재작성 시 Mission/Claim Boundary/Stop Conditions/Sub-Agent 섹션 제거 → 테스트 L822 실패.
**해결**: plan.md에 5 섹션(Mission/Claim Boundary/Stop Conditions/decision-support/Sub-Agent) 정직·claim-disciplined 추가. 테스트 재실행으로 downstream assertion 추가 실패 유무 확인.

### 1.5.3 #1 success_deadline ladder — multimodal censor 블로커
**진단**: sample horizon(~200min)이 multimodal 전원 censor, bus도 60-75%만 완료 → 공정 bus-vs-multimodal delta 불가.
**해결**: `success_deadline_min` ladder(5/6/7/8/10/12h) profile 추가 → smoke 재실행 → multimodal completion 정상화 확인. (high_level_plan Phase 5 ladder를 앞당겨 적용)

### 1.5.4 #2 ML re-baseline — 실제 그래프
**진단**: `ml_baseline_v1.json`(macro-F1 0.887) = stub-era. 실제 그래프 결과로 re-baseline 필요.
**해결**(1.5.3 후): 실제 그래프에서 충분 행 수 profile 실행 → ML 재산출 → baseline 갱신. 4급 클래스 다양성 확보 필요(성공사다리로 completion 분포 생성).

### 검증
- 핵심 직실행 테스트 + #3/#4 테스트 PASS. #1 smoke multimodal completion>0. #2 ML baseline 재생성.
