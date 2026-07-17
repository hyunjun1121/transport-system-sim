# FOLLOWUP — 후속 작업 권장 목록

> 2026-07-09 기준. wartime-BPR + damage-lever + segment-targeting fix 커밋(`ba158fb3`, branch `wartime-bpr-targeting-fix`) 이후 정리된 후속 권장.
> 모든 항목은 **의사결정지원·준실험(quasi-real)·민감도** 범위의 작업이며, 정식 인수 증거가 아님(`final_study_ready=false`, 인수 0/12 설계상 유지).

---

## A. 즉시 정정 (quick fixes, 저비용)

### A1. CLAUDE.md stale Vercel URL 정정
- **현상:** `CLAUDE.md`에 `mobilization-transport-ai.vercel.app` 기재. web_demo 실제 배포 = `defense-ai-mobility-demo.vercel.app`(`web_demo/README.md`, `web_demo/demo_map_spec.md`에서 확인).
- **방법:** `CLAUDE.md`에서 `mobilization-transport-ai.vercel.app` → `defense-ai-mobility-demo.vercel.app` 치환.
- **비고:** overview workflow의 deliverables verifier가 포착. 단순 텍스트 정정.

### A2. 전체 정리본(overview)을 문서로 저장
- **현상:** 본 세션에서 작성한 "전시 동원예비군 수송 마이크로 시뮬레이션 — 전체 정리" 개요가 채팅에만 존재.
- **방법:** `PROJECT_OVERVIEW.md`(루트) 또는 `docs/project_overview.md`로 저장. accuracy/claim 검증 반영본(17,250 nodelink 정준, "(검증됨)" 제거, URL 확정) 사용.
- **비고:** claim-disciplined 표기 유지. 연구상태 문서 범주.

---

## B. 재분석 (re-run, 현 결과 대상)

### B1. ML/AI 층을 17,250행 nodelink 결과로 재실행 ★
- **현상:** 현 ML 지표(test accuracy 81.9%, macro-F1 0.685, 라벨 정상7,819/주의976/위험823/실패위험2,802)는 **이전 12,420행 nodelink run**(targeting fix 이전) 기반 → 17,250행 현 결과 대비 stale.
- **방법:**
  ```powershell
  .\.venv\Scripts\python scripts\run_ml_analysis.py `
    --input results/realworld_pilot_nodelink/pilot_full_results.csv
  ```
- **비고:** 신규 damage 7행(access/last-mile/long-haul)이 특성으로 들어가면 상위 gain 특성 분포 변동 가능. 라벨 규칙 정상/주의/위험/실패위험은 completion 분포에 의존해 클래스 수 가변. 산출 경로 갱신 필요 시 `results/realworld_pilot_nodelink/analysis/` 등으로 분리.

### B2. 깨끗한 slowdown 곡선용 milder multiplier 보조 행 (선택)
- **현상:** 고강도 손상(last-mile severe 3.0 / extreme 8.0, long-haul severe 3.0)에서 completion collapse → makespan censored. 깨끗한 단조 slowdown 곡선이 안 보임.
- **방법:** long-haul(S→R, 641 edge)에 mult 1.2~1.5 단일 행 추가, 또는 access/last-mile에 더 잔잔한 단계 추가. 재실험 + truth table 재동결 동반.
- **비고:** access 사다리(mild~extreme, cr 0.93~1.0 유지)는 이미 깨끗한 decomposition 증거이므로, long-haul 보조만으로 충분할 수 있음. planning sensitivity 가정 표기 유지.

---

## C. 방법론 보강 (methodology / provenance)

### C1. `mark_scenario_edges` annotation 대칭 (nit)
- **현상:** `disruption_capacity_factor`는 edge attr로 기록되나 `disruption_travel_time_multiplier`는 누락(`SCENARIO_EDGE_ATTRS`, `disruption_scenarios.py:541-547`).
- **방법:** `SCENARIO_EDGE_ATTRS`에 `disruption_travel_time_multiplier` 추가 + `mark_scenario_edges`에서 기록.
- **비고:** 본 targeting 결함과 무결하게 미구현 nit. annotation 일관성.

### C2. silent scenario-skip → manifest에 `skipped_scenarios` 기록 (provenance minor)
- **현상:** 5개 spatial(bbox) 시나리오가 skip되나 pilot manifest에 명시 기록 안 됨. 결과 행 수(25 ran)와 설계(30) 차이 추적이 manifest만으로 불명.
- **방법:** `pilot_full_manifest.json`에 `skipped_scenarios` 배열 + 사유 추가.
- **비고:** 17,250행 = 23 pol × 25 ran scen × 30 seed. provenance 투명성.

### C3. L1 nodelink 5개 공간(bbox) 시나리오 복원
- **현상:** bbox_midpoint 선택이 nodelink graph에서 no candidate edges → 5개 skip(Tancheon corridor, feeder east, lastmile west, assembly egress, combo tancheon).
- **방법:** bbox → link_id/노드 직접 매핑으로 복원. 별도 작업(BPR/targeting과 무관한 커버리지 문제).
- **비고:** 시나리오 커버리지 25→30 ran으로 회복. 재실험 동반.

---

## D. 산출물 성숙 (deliverables)

### D1. 영문 논문 `paper/paper_draft.md`(1,990행, 스캐폴드) → 본문 초안
- **비고:** 현재 scaffold. wartime BPR no-op·segment-decomposition·empirical bite를 방법론 섹션으로 반영 필요.

### D2. 웹 데모 `web_demo/` dist 빌드 + 배포 갱신
- **현상:** 소스만 존재, `dist` 미빌드. URL `defense-ai-mobility-demo.vercel.app`.
- **방법:** `cd web_demo; npm run build` → Vercel 배포. 신규 결과(17,250행) 데모 데이터 갱신 검토.

### D3. KCI 재설계 `kci_redesign/`(4종 종합, 미구현) → 구현
- **비고:** 5 redesign 축(집결지/복합운송 4수단/위협사다리 L1-4/코리더 5/KPI) 중 sea/air+디젤전환 미구현 격차 존속. Phase R1-6 로드맵.

### D4. 한국어 보고서 `report_draft.md`→`report.docx`에 신규 finding 반영
- **비고:** segment-decomposition·empirical bite·ML 갱신(B1 후) 반영 후 `generate_report.py` 재생성.

---

## E. 구조 / 로드맵 (structural / long-term)

### E1. branch `wartime-bpr-targeting-fix` → main 병합
- **현상:** 커밋 `ba158fb3`(310 files)이 branch에 있고 main은 `c132b72f` 유지.
- **방법:** 리뷰 후 `git checkout main; git merge wartime-bpr-targeting-fix` (또는 PR). 사용자 명시 시만.

### E2. pre-existing 96건 claim-audit blocker 정리 (별도)
- **현상:** `audit_claim_language.py --fail-on-blockers` exit 1 = release_blocking_unbounded 96건. **전부** plan.md·paper 초안·status.md·results 테이블 등 사전 구현 연구문서에 한정. `src/`·`data/scenarios/`엔 없음.
- **비고:** 본 targeting 작업 regression 아님. 어휘 tripwire라 구조상 never-ready. 정리는 연구문서 전면 claim-discipline 개조(대공사).

### E3. 장기 로드맵 (`high_level_plan.md`)
- FTA/FM/FA 결함수 차단 모델링 · 다중 코리더 앙상블 · 현장 검증 벤치마크 · GPU 몬테카를로 · RL 배차 정책.
- Phase-1 입력 재조정(도로 속도/용량·철도 시각표·집결 지연·차대) — 참고 목표.

---

## 우선순위 가이드

| 순위 | 항목 | 이유 |
|---|---|---|
| 즉시 | A1 (CLAUDE.md URL) | 1줄 정정, 문서 정확성 |
| 즉시 | A2 (overview 저장) | 현재 세션 산물 보존 |
| 단기 | B1 (ML 재실행) | ML 지표 stale, 논문/보고서 신뢰성 |
| 단기 | C2 (skipped_scenarios manifest) | provenance 투명성, 저비용 |
| 중기 | B2 (milder multiplier) | 깨끗한 slowdown 곡선, 논문 figure |
| 중기 | C1 (annotation 대칭) | 일관성 nit |
| 중기 | D1/D4 (논문·보고서) | 경연/논문 딜리버블 |
| 별도 | C3 (bbox 복원), D2/D3 (web/KCI), E1-E3 | 독립 대공사 |

---

*본 목록은 작업 권장이며, 어떤 항목도 정식 인수/출판 증거가 아님. `final_study_ready=false` 유지.*
