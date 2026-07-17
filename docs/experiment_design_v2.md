# 전시 동원예비군 수송 실험설계 v3 (wartime-assumption-driven)

> 의사결정지원·준실험(quasi-real)·민감도 범위. `final_study_ready=false`, 정식 인수 0/12(설계상).
> 출품 목표: **한국경영공학회(KIIE)** — 전시 수송 시뮬레이션 + 시나리오 기반 의사결정분석.
> AI/ML 층은 본 설계에서 **제외**(경연 track은 별도 보존).
> 최종 갱신: 2026-07-09. 기준 branch: `wartime-bpr-targeting-fix`.

---

## 0. 설계 철학 — 전시 프레임 = 가정-도구

전시라는 특수성은 "다 리얼월드 관측데이터로 환원"하려는 압력을 **해소**하는 도구다. 시스템을 3층으로 나누고,
가정-처리 가능한 것은 **전시 교리 가정으로 명시**하며, real-data로 구축해야 할 것만 실데이터로
다룬다.

| 층 | 내용 | 처우 |
|---|---|---|
| **A. 가정-처리** | 철도 장거리 신뢰성, 민간 배경교통 | 전시 교리 가정으로 명시 (시뮬·실측 안 함) |
| **B. real-data 핵심** | 도로망 geometry, 등급별 자유속도 | 공공데이터로 구축 |
| **C. 비교 무대(arena)** | access A→S, last-mile R→D, bus_only A→D 전-도로 | 여기서 bus vs multimodal 진짜 갈림 |

## 1. 기여 정의 (경영공학회 맞춤)

1. **공식 도로망 기반 재현가능 전시 수송 시뮬레이션** — 표준노드링크(972k edge) 위
   discrete-event 통행·배차 모델.
2. **구조화된 전시-시나리오 분류체계** — 교리근거 9개 family(access/last-mile/long-haul/
   임계링크/확률/공간/철도불가/감속민감도/다중위험).
3. **CRN 쌍대설계 bus vs multimodal 비교** — 동일 위협·동일 seed로 구조적 차이 분리.
4. **전시-가정 기반 모델 단순화의 방어가능 근거** — BPR no-op·철도 신뢰를 물리적 기제
   (방향 비대칭)로 정당화.

## 2. 전시 가정 (명시·교리근거·결과)

| # | 가정 | 전시 근거 | 모델링 결과 |
|---|---|---|---|
| A1 | 철도 = 최대속도·무정지·신뢰 | 전시 군사수송 우선운영 (예비군 동원 = 우선 군사이동) | S→R rail leg = disruption-면역 **by assumption**. sim이 이미 그렇게 작동(`traffic.py` rail branch). "측정된 robustness" 아님 → circularity 제거 |
| A2 | 군사축 민간교통 ≈ 0 | **방향 비대칭**: 병력 ↑ 북상 / 민간 ↓ 남하. 반대축 → 안 겹침 + 전시 교통 붕괴 | BPR 체적-지연항 no-op(<2%, 수치확인). 통행시간 = 거리/자유속도. 민간 교통량 데이터 불필요 |
| A3 | 차량 = 군 배정 고정 | 군 징발/배정, 시장변수 아님 | fleet 수 = 정책 입력(policy alternative) |
| A4 | disruption = 교리 시나리오 입력(민감도 래더) | 파손정도 불확실 → 가정-래더로 sensitivity | multiplier 사다리 = "planning sensitivity". 정확값 주장 X, **±50% 순위안정성**으로 답 |

**핵심 규칙:** 가정 자체는 문제 아님. **숨겨서 "발견"처럼 팔 때** 문제. 모든 가정은 본 문서에
명시하며, 철도-면역은 "측정 결과"가 아닌 **scope 조건**으로 보고.

## 3. real-data 핵심 (B층)

- 도로망: 표준노드링크(972k edge, 공식 국토도로망). geometry = real.
- 등급별 자유속도: maxspeed + `data/parameters/road_class_overrides.csv`.
- 철도 거리/시간: 공식(KTX-Eum 114분, 600객, 30분 배차).
- 좌표: 공공 행정중심점만(보안 제약 — 실 부대 좌표·OOB·이동일정 일절 無).

## 4. 시나리오 분류체계 (본 연구 핵심)

`data/scenarios/goseong_disruption_scenarios.csv` — 24행(전시 가정 정합화 후). 모두
`force_deterministic=True`, `evidence_class=scenario_based`, `observed_disaster_data=false`.

| 코드 | family | 전시 동기 | 비교 효과 |
|---|---|---|---|
| S1 | 접근로 access A→S 감속 사다리 | multimodal 셔틀 leg 파손 | **multimodal 전용** 취약 (bus A→D 안 씀) |
| S2 | 종단 last-mile R→D 감속 사다리 | D 접근 유일도로 파손 | **공유 병목, 양쪽 타격** |
| S3 | 장거리 도로 S→R / bus A→D 파손 | 버스 장거리 도로 노출 | bus 타격, multimodal rail-면역(가정 A1) |
| S4 | 임계 링크 차단(edge betweenness top-k) | 구조적 병목 식별 | 양안 차등 |
| S5 | 확률적 무작위 차단/용량감소(p_fail 래더) | 분산적 위협 | 일반 robustness |
| S6 | 공간 위험 bbox 오버레이(코리더별) | 지역별 위험집중 | 코리더 노출 매핑 |
| S7 | 철도 운행불가(이진, mult=100) | 가정 A1 실패-edge(노선 파괴/전력상실) | 가정 스트레스 |
| S8 | 감속 multiplier 사다리 + **±50% rug** | A4 민감도 | 순위안정성 증거 |
| S9 | 다중위험 조합 | 복합 스트레스 | worst-case 매핑 (현재 road+rail 콤보는 A1으로 제거; road+road 콤보는 schema 확장 필요 → deferred) |
| — | **정책 축** (fleet 강화/혼잡응력/배차적응/transfer·lastmile 용량) | 의사결정 레버 | 매트릭스 한 축 (23 policy) |

**v3 변경(대비 이전):** 철도 점진 열화 래더(delay/capacity/combined mild~severe 7행) +
rail-콤보 2행 = **9행 삭제** (가정 A1과 모순). `rail_unavailable` 1행만 보존. access·last-mile
**±50% stability rug 2행 추가**(severe 3.0 → 4.5; −50%인 1.5는 기존 mild로 이미 존재).

## 5. 대안 + 비교 무대

- `bus_only`: A→D 전-도로.
- `multimodal`: A→S 셔틀 → S→R **rail(가정-면역)** → R→D last-mile.
- **arena**: access(S1, multimodal 전용) / last-mile(S2, 공유) / bus 장거리(S3). rail은
  가정-면역 → 비교 무대 아님.

**핵심 질문(정직):** *전시 철도-신뢰 가정 하에, 버스(전-도로 노출) vs 복합운송(단거리
access+last-mile 노출) 중 어느 도로-노출 profile이 disruption에 더 강한가, 그리고 fleet/dispatch
정책이 completion을 어떻게 조절하는가.*

→ "rail-substitution robustness 측정" 주장 **폐기**. "rail-신뢰 가정 위에서 도로-노출 profile
비교 + 가정 실패-edge(rail_unavailable) 스트레스"로 대체.

## 6. 메트릭 (정직)

- **1차**: `completion_rate`(censored tail 강건), `penalized_makespan`.
- 2차: `makespan`(completion 유지 구간만).
- 자원: vehicle-min, pax-min, train-min.
- **금지**: censored cell에서 raw makespan을 점추정처럼 보고.

## 7. 통계 설계

- **CRN 쌍대설계** 유지(강점): `seed_stream_id`(sha256 of 4 stream seeds)로 결과 CSV만으로
  쌍대 seed-동일성 감사가능.
- **n=30 seed**, `analysis.py` CI = **t-임계치**(Cornish-Fisher, df=29 → 2.0452; 정규 z=1.96 대체).
- seed가 전파하는 것 = **arrival-지연 + fleet/turnaround 노이즈** (명시). disruption은 결정론
  입력 → seed는 시나리오 불확실성 아님. 완전결정론 cell(426/621 historically)은 점추정 보고.
- **검정력 근거(단락):** CRN 쌍대설계로 within-pair 분산이 작으므로, pilot σ_delta 대비
  n=30은 80% power로 탐지가능한 최소 쌍대-차이 Δ_min = t·σ_delta/√30. 재실험 후 실측 σ_delta로
  Δ_min 산출하여 본 문서에 수치 보충 예정.

## 8. ML/AI 층 — 제외

본 설계(v3)에서 ML/AI 판단지원 층은 **실험 cascade에서 제외**. 이유: label = sim 자체
completion 출력의 임계치 → 분류기 아닌 압축 lookup; split `index%5` 비그룹 → CRN-상행 누출로
과장. `src/realworld/ml_analysis.py`·`scripts/run_ml_analysis.py`는 경연(국방AI) track을 위해
코드 보존, 학회(경영공학회) 논문에서는 **사용·인용 안 함**.

## 9. 방어가능 주장

> "전시 군사우선 철도운영·방향별 민간대피 가정(A1-A2) 하에, 공식 표준노드링크 상에서 CRN
> 쌍대설계로 버스-단독 vs 철도-버스 복합운송을 비교하는 **전시 수송 시뮬레이션**. 9개 교리근거
> 시나리오 family × 23 정책축 교차로 **도로-노출 profile의 차등 취약성**을 분석. 철도 장거리
> 우위는 전시 가정; 가정으로 치울 수 없는 도로 leg(access·last-mile)가 어디서 의사결정을
> 갈라놓는지, 정책이 completion을 어떻게 조절하는지가 본 연구의 기여. BPR 무의미성은 방향
> 비대칭으로 기계적 정당화."

- **방어가능**: 시뮬레이션 방법론, 시나리오 분류체계, CRN 쌍대설계, access/last-mile 분해,
  BPR-no-op 물리적 정당화(방향 비대칭), 재현성(byte-identity oracle/truth-table).
- **주장 X (범위 밖)**: rail-substitution을 측정 robustness로 제시, 미래 수요 예측, 평시 보정 수치, 단일 최적경로 지정, 실 운용계획 수립.

## 10. 실행 매트릭스 (full_pilot profile)

- 25 시나리오(no_disruption + 24 CSV) × 23 정책 × 30 seed = **17,250 nominal rows**.
- 공간 bbox 4개 skip 예상(tancheon/feeder_east/lastmile_west/transfer_point) → ≈ 21 ran ×
  23 × 30 ≈ **14,490 executed rows** (재실험 후 확정).
- oracle은 영향 없음(byte-identical; CSV targeting·seed block과 독립).

## 11. 재실행 cascade

1. CSV 정비 ✓ (24행, rail_unavailable만, ±50% rug).
2. design JSON 동기화 ✓ (full_pilot 25 scen / full_graph 14 scen).
3. `analysis.py` z→t ✓.
4. ML cascade 분리 ✓.
5. 재실험 `scripts/run_pilot_experiments.py --engineering-only --full` (진행 중).
6. truth 재동결 `scripts/regenerate_truth_table.py`.
7. 본 문서 + `docs/project_overview.md` 수치 갱신.

## 12. 알려진 한계 (정직 공개)

- 단일 코리더(Goseong; 병행 KTX-Eum 있어 특수) → 모든 주장 코리더-조건부.
- 차량-단위 물리(junction queue·LTM·car-following) 無 → 본 모델은 "결정론적 네트워크-가용성
  + 차량 스케줄링 분석"에 가까움. ~1000-pax 종단 단일 spur의 종단 병목 붕괴는 구조상 미표현.
- disruption multiplier = 교리 가정(미확인); ±50% 안정성으로 순위만 주장.
- rerouting 기본 비활성(도구는 존재, 본 cascade에서는 off).

---

*본 문서는 연구상태 설계 정리이며 정식 인수/출판 증거가 아님. `final_study_ready=false` 유지.*
