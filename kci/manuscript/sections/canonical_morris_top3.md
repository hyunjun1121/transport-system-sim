# Canonical Morris top-3 (단일 출처 / Single source of truth)

## 정전 집계 규칙 (Canonical aggregation rule)

각 파라미터의 정전 평균 μ*는, `results/sensitivity/morris_summary.csv`에 수록된 모든 (policy_id × scenario_id × metric) 블록에 대해 μ*를 다중-지표 평균(multi-metric mean)으로 평균하여 산출한다 (`plan.md` §3.7 / §10; 표 5와 동일 규칙). 14개 파라미터 × 28 블록(= 7 metric × 2 policy × 2 scenario) = 392행을 입력으로 한다.

## Canonical Morris top-3

1. `passenger_volume` — 정전 평균 μ* = **44.5** (28 블록 집계).
2. `direct_bus_fleet_size` — 정전 평균 μ* = **27.4** (28 블록 집계).
3. `dispatch_interval` — 정전 평균 μ* = **20.8** (28 블록 집계).

(유효숫자 3자리. 14개 전 파라미터의 순위는 `manuscript/tables/table5_morris_mu_star.md` 참조.)

## 사용 규약 (Usage contract)

본 문서는 본문 §4.5 (Results — Morris 민감도), §5.1 (Conclusion — main finding), 그리고 초록(abstract)에 인용되는 Morris top-3에 대한 **단일 출처(single source of truth)** 이다. §4.5, §5.1, 초록을 작성하는 모든 하위 에이전트는 본 파일을 **있는 그대로(verbatim) 소비해야 하며**, `results/sensitivity/morris_results.csv` 또는 `results/sensitivity/morris_summary.csv` 를 **독립적으로 재집계해서는 안 된다** (THEY MUST NOT re-aggregate `morris_results.csv` or `morris_summary.csv` independently). 정전 평균 μ* 수치 또는 순위에 변경이 필요할 경우, 표 5와 본 파일을 동시에 갱신한 뒤에야 본문 인용을 수정할 수 있다.

## 출처 / 산출 추적성

- 입력 데이터: `kci/results/sensitivity/morris_summary.csv` (392행, SALib Morris 집계)
- 집계 스크립트 의미: groupby(`parameter_id`, `metric`) → mean(`mu_star`); groupby(`parameter_id`) → mean(직전 결과) → 내림차순 정렬.
- 방법 파라미터: SALib Morris elementary-effects, k = 14, T = 100 궤적, L = 4 수준, 총 (k + 1) × T = 1,500 모델 평가.
- claim_scope: 파일럿 스캐폴드(보정된 운영-환경 민감도 추정치 아님).
