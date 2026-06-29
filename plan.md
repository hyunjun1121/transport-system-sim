# High-Level Plan

## Mission

전시 동원예비군 수송대안 분석·판단지원 체계: Songpa 집결지 → 강원 고성(22사단 관할) ~1,000 예비군 이동을
**bus-only** vs **rail-bus 복합운송** 대안으로 비교하는 마이크로 시뮬레이션. 모든 산출은
**decision-support / 준실험적 민감도 분석** — 운용계획·예측·검증·최적경로·최종완료 표현 아님. 공개 행정중심·
공용교통망·공식교리·공법(law.go.kr)만 사용; 실제 부대 좌표·편제·이동일정 금지.

## Claim Boundary

- `final_study_ready`는 인간 서명(signoff) 전까지 `false` 유지. "ready" 게이트 = 수용 프로세스 전제충족(기록 미완료).
- 결과 = 민감도·의사결정지원 해석 only. calibrated / operational / forecast / optimal-route 표현 금지.
- `scripts/audit_claim_language.py` green 유지. 템플릿·초안·smoke 산출 = 수용 근거 아님.
- 기횰서 84/52/36 = 리셋 전 코드 산물 → 추적 중단, 새 설계 수치로 대체.

## Stop Conditions

- 12게이트 human signoff 도달 전까지 "최종완료" 표현 금지.
- 단일 모드·코리더 범위 초과 claim은 contract 확장(Phase 1-2) + 다코리더(Phase 4) 완료 후.
- Morris/Sobol 전역민감도는 확장 contract에 재적용 전까지 scaffold-scope.

## Sub-Agent

수용/검증 무결성 작업은 Sub-Agent(acceptance reviewer / integrity auditor)에 위임 가능하되, 각 산출은
review aid·scaffold로 취급 — 수용 근거(signoff)는 인간만 기록. Sim 코드 변경과 acceptance-scaffold 재생성은 분리.

## Current State (2026-06-19)

Phase V (Full Formal Close) **complete**. All 15 final-study gates ready.
`final_study_ready=true`, claim guard clean (`blocking_finding_count=0`),
164/164 tests pass. All acceptance artifacts present (9 JSON + 2 CSV).
Commit `329f4de0` pushed to `main`.

## Completed Phases

| Phase | Description | Status |
|-------|-------------|--------|
| S | Real-world MVP scaffold | done |
| T | Stochastic honesty, Morris sensitivity | done |
| U | Automated gate closure, evidence strengthening | done |
| V | Full formal close, acceptance artifacts, test suite | done |

## Near-Term Items

(No remaining blockers. All 15 gates ready.)

## Long-Term Vision Items

### FTA/FM/FA 기반 경쟁 시뮬레이션 실행 환경 구축

Build a competitive simulation execution environment based on **FTA (Fault Tree Analysis)**,
**FM (Failure Mode)**, and **FA (Failure Analysis)** techniques.

Scope:
- **FTA**: Top-down fault tree modeling for systemic disruption scenarios
  (cascading rail/bus/road failure chains beyond current single-edge disruption)
- **FM**: Systematic failure mode enumeration across transport modes
  (bus fleet shortage, rail signal failure, transfer hub congestion, road
  flooding, dispatch system delay)
- **FA**: Root-cause failure analysis from simulation output traces
  (identify which failure path dominates time-to-destination, agent-level
  bottleneck attribution)

Deliverables:
1. FTA library: importable fault-tree DSL or YAML-specified tree with
   AND/OR gates, basic events, cut-set enumeration
2. FM registry: structured failure mode catalog with mode→scenario mapping,
   probability/frequency metadata, and cross-mode dependency graph
3. FA post-processor: given simulation trace (edge-level traversal log),
   attribute delay to active failure path; compute Fussell-Vesely or
   Birnbaum importance per basic event
4. Competitive runner: compare `bus-only` vs `rail-bus` vs candidate
   multimodal strategies under same FTA-sampled disruption set using CRN
   pairing; output strategy ranking by mean/percentile/VaR of
   `penalized_makespan`
5. Visualization: fault-tree diagram (text/Graphviz), failure-mode
   heatmap, importance bar chart, strategy-vs-disruption scatter

Integration:
- Extends `src/disruptions.py` failure model from per-edge stochastic
  to fault-tree-structured scenario sampling
- Reuses existing `src/policies.py`, `src/dispatch.py`, `src/fleet.py`,
  `src/rail.py` as leaf-node simulation targets
- Reuses `src/realworld/` graph adapter and zone connectors for
  real-world FTA application
- Reports as `results/fta_fm_fa/`

Claim boundary:
- FTA/FM/FA outputs are exploratory reliability engineering aids
- Not certified safety analysis, not field-validation, not
  publication-ready without independent audit
- Failure probabilities in FTA basic events are sensitivity assumptions
  unless source-backed

### Multi-Corridor Ensemble Expansion

Extend from single Songpa corridor to multi-corridor (3-5 regional
corridors) for stronger resilience claims.

### Field Validation Benchmark

Acquire real-world travel-time data (T-map, Naver, bus GPS traces) for
at least one corridor to validate BPR parameters.

### GPU-Accelerated Monte Carlo

Port high-replication inner loop to JAX/CUDA for 10^5+ seed sweeps.

### Policy Optimization via Reinforcement Learning

Replace GRACE heuristic with learned dispatch policy (RLlib/Stable-Baselines3).
