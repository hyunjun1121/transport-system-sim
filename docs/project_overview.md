# 프로젝트 전체 정리 — 전시 동원예비군 수송 시뮬레이션 (v3)

> 의사결정지원·준실험(quasi-real)·민감도 범위. `final_study_ready=false`, 정식 인수 0/12(설계상 유지).
> 본 문서는 연구상태 기록이며 운용계획·예측·최적경로가 아님.
> 출품 목표: **한국경영공학회(KIIE)** — 전시 수송 시뮬레이션 + 시나리오 기반 의사결정분석.
> 최종 갱신: 2026-07-09 (v3, wartime-assumption 재설계). 기준 branch: `wartime-bpr-targeting-fix`.

---

## 0. v3 설계 철학 — 전시 프레임 = 가정-도구

전시 특수성은 "다 리얼월드 검증" 압력을 해소. 시스템 3층 분할:

| 층 | 내용 | 처우 |
|---|---|---|
| **A. 가정-처리** | 철도 장거리 신뢰성, 민간 배경교통 | 전시 교리 가정으로 명시 (시뮬·검증 안 함) |
| **B. real-data 핵심** | 도로망 geometry, 등급별 자유속도 | 공공데이터로 구축 |
| **C. 비교 무대(arena)** | access A→S, last-mile R→D, bus_only A→D 전-도로 | bus vs multimodal 진짜 갈림 |

상세 설계는 `docs/experiment_design_v2.md`.

## 1. 무엇을 만드는가

전시 동원예비군 약 1,000명이 **집결지→목적지** 이동 시 **버스 단독(bus_only)** vs
**철도-버스 복합운송(multimodal)** 을 **동일 위협 조건 + 동일 CRN seed**에서 쌍으로 비교하는
**교통망 시뮬레이션**. 활용 사례 = 송파(A, 올림픽공원) → 강원 고성(D, 제22보병사단 인근 토천면 학야리).

**좌표는 공공 행정중심점/공공교통망만 사용** — 실제 부대 좌표·이동일정·OOB 일절 無.

## 2. 두 겹 구조 (편집 전 구분)

1. **시뮬레이터**(본질): `src/` core + `src/realworld/` 실세계 파이프라인 + `src/experiment/` 실험.
2. **수용/검토-무결성 기계**(주의): `src/realworld/*_acceptance.py`, `*_review_packet.py`, `scripts/` 약 90/141.
   형식 게이트 폐쇄·증거 출처·클레임 경계 가드. **시뮬을 구동하지 않음.**

## 3. 전시 가정 (명시)

| # | 가정 | 전시 근거 | 결과 |
|---|---|---|---|
| A1 | 철도 = 최대속도·무정지·신뢰 | 군사수송 우선운영 | S→R rail = disruption-면역 **by assumption** (측정 아님) |
| A2 | 군사축 민간교통 ≈ 0 | **방향 비대칭**(병력↑ 북상 / 민간↓ 남하) | BPR 체적-지연항 no-op(<2%). 통행시간=거리/자유속도 |
| A3 | 차량 = 군 배정 고정 | 군 징발 | fleet 수 = 정책 입력 |
| A4 | disruption = 교리 입력(민감도 래더) | 파손정도 불확실 | multiplier = "planning sensitivity". ±50% 순위안정성으로 답 |

**규칙:** 가정 자체는 OK, **숨겨서 "발견"처럼 팔 때** 문제. 모든 가정 본 문서에 명시.

## 4. 핵심 방법론

### 4.1 전시 BPR 부피-지연 = near-no-op (방향 비대칭으로 정당화)
전시 민간 배경교통량 붕괴 + **병력(북상)/민간(남하) 방향 비대칭** → 군사축 volume≈0 →
BPR 지연항 사실상 항등 (`t≈t0=거리/자유속도`). 정준 설정에서 makespan 지연 = **0.0024%**.
→ 평시 교통량/BPR-α 보정은 **저가치 잔여 응력축** (데이터 불필요).

### 4.2 도로-파손 직접-감속 lever (capacity 경로와 분리)
`capacity_reduction`은 capacity↓→BPR 경로라 전시 V≈0에서 inert. 그래서
`EdgeDisruption.travel_time_multiplier`를 `traffic.enter_edge`에서 `effective_t0 = t0 × multiplier`
로 BPR **이전** 적용(road branch만). "파손 도로가 종단을 실제로 지연" 가능.

### 4.3 시나리오 분류체계 (본 연구 핵심)
9개 교리근거 family: S1 접근로 access A→S / S2 종단 last-mile R→D / S3 장거리 도로 /
S4 임계링크 차단 / S5 확률적 무작위 / S6 공간 bbox / S7 철도불가(이진) / S8 감속 사다리+±50% /
S9 다중위험. 정책축(23 policy)과 교차.

### 4.4 통계 설계
CRN 쌍대설계(bus_only·multimodal 동일 seed) → delta가 구조적 차이. `seed_stream_id`(sha256)로
CSV만으로 감사가능. CI = **t-임계치**(df=29→2.0452, 정규 z=1.96 대체, `analysis.py`).
seed 전파 = arrival-지연+fleet 노이즈 (disruption은 결정론 입력).

## 5. 경험적 결과 (1000-pax 전시 재실험, 14,490행 기준)

1000-pax·24h 창·23-차량 fleets 전시 척도에선 **완료율이 대부분 1.000으로 포화** → 판별 신호는
**makespan(분)** 이다. CR=0.000 cell만 진성 실패모드(censored). bus_only vs baseline_multimodal 평균:

| 시나리오 | bus_only (CR/MS) | multimodal (CR/MS) | 해석 |
|---|---|---|---|
| no_disruption (baseline) | 1.000 / **283** | 1.000 / **364** | **bus가 ~81분 빠름** — 24h 창+23-차량이면 도로 직송이 철도 고정오버헤드(114분 leg+headway+환승)보다 빠름 (24-pax/8h fixture에선 multi가 빨랐던 것과 반전) |
| access A→S mild / severe / extreme / **+50(4.5)** | 1.000 / 285·291·311·296 | 1.000 / 371·394·464·416 | multi 전용 feeder leg → multi 타격 큼; bus는 A 근처 공유 edge만 경미. ±50% 순위안정 |
| last-mile R→D mild / severe / extreme / **+50(4.5)** | 1.000 / 294·329·458·368 | 1.000 / 395·502·**976**·642 | **공유 병목, 양쪽 MS 단조 상승**(multi 압도적, extreme 976분). ±50% 안정 |
| long-haul S→R mild(1.2) / mod(1.5) / severe(3.0) | 1.000 / 317·375·**671** | 1.000 / 364·364·364 | bus 도로 노출 단조 상승; multimodal **가정 A1로 MS 불변**(scope 조건, 측정 아님) = rail-substitution |
| **critical_link_blockage** (betweenness top-3) | **0.000** / inf | 1.000 / 364 | bus 트렁크 붕괴, multi rail bypass 생존 |
| **rail_unavailable** (가정 실패-edge) | 1.000 / 283 | **0.000** / inf | 철도 가정 실패 시 multimodal 완전 붕괴 — 정당·비순환 stress(**헤드라인**) |
| random_blockage (8 간선) | 0.000 / inf | 0.000 / inf | 과도 차단, 양쪽 진성 붕괴 → 단일실패점 식별 우선 |

**핵심 재프레임(24-pax fixture 대비):** 24h 전시 창에선 CR 포화로 **makespan이 척도** (24-pax/8h
fixture는 completion-rate 구동). baseline은 **bus가 더 빠르다**(반전). multimodal 우위는 road-specific
고장을 rail로 우회할 때(critical_link·long-haul)만 발현되고, rail 가정 제거 시 붕괴. 혼잡축은 A2(V≈0)
부합해 양쪽 모두 1.000 포화(makespan 미미 변동). **±50% rug**가 multiplier 순위안정성 증거.

## 6. ML/AI 층 — v3에서 제외

경영공학회 논문에서 ML/AI 판단지원 층 **사용·인용 안 함**. 이유: label = sim 자체 completion
출력의 임계치(압축 lookup), split 비그룹(CRN-상행 누출). 코드(`src/realworld/ml_analysis.py`)는
국방AI 경연 track 위해 보존. **v3 cascade는 ML 미경유.**

## 7. 현 정준 산출 숫자

- 재실험 결과: **14,490행** = 23 정책 × 21 ran 시나리오 × 30 seed (4개 spatial bbox skip).
- truth table: **483행**, 23 정책, 21 시나리오, `cross_product_matches=true`, sha `7ff3711d`.
- 시나리오 CSV: **24 data행**(rail 점진열화 9행 삭제·rail_unavailable 1행 보존·±50% rug 2행 추가).
- design: full_pilot **25 시나리오**(no_disruption+24) × 23 정책 × 30 seed = 17,250 nominal.
- 표준노드링크 캐시 = Goseong 정준 도로망 출처(972k edge, 공식).

## 8. 산출물

- 한국어 기획서: `국방AI_활용_아이디어_경연대회/...공모기획서.md` (경연용; 본 학회 논문과 별도).
- 한국어 보고서: `report_draft.md` → `report.docx`.
- 영문 논문 스캐폴드: `paper/paper_draft.md` (v3 framing 재정렬 필요).
- 웹 데모: `web_demo/` (Vercel: defense-ai-mobility-demo.vercel.app).

## 9. 클레임 규율 (타협 불가)

`final_study_ready=false`, 정식 인수 0/12. 산출 = "의사결정지원·준실험·민감도"로만 기술.
금지어: 운용(operational), 예측(forecast), 보정(calibrated), 검증(validated), 최종완료(final-ready),
최적경로(optimal route). 한국어 "검증" = 예약 트리프와이어. `scripts/audit_claim_language.py`가 시행.

## 10. 알려진 한계 (정직 공개)

- 단일 코리더(Goseong; 병행 KTX-Eum 있어 특수) → 모든 주장 코리더-조건부.
- 차량-단위 물리(junction queue·LTM·car-following) 無 → "결정론적 네트워크-가용성 + 차량 스케줄링 분석"에 가까움.
- disruption multiplier = 교리 가정(비검증); ±50% 안정성으로 순위만 주장.
- rerouting 기본 비활성(도구는 존재, 본 cascade에서 off).
- S9 다중위험: rail-콤보는 A1으로 제거, road+road 콤보는 schema 확장 필요 → deferred.

---

*본 문서는 연구상태 정리이며 정식 인수/출판 증거가 아님. `final_study_ready=false` 유지.*
