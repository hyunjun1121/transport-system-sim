# Transport System Simulation - Implementation Plan

## 1. 프로젝트 본질 요약

**목적**: "어떤 조건에서 복합수송이 버스 단독보다 유리한가?"를 답하는 **통제된 비교 실험**
**대상**: 추상 네트워크 (노드 5개: H→A→S→R→D, 도로 링크 3~6개, 철도 1개)
**방법**: SimPy DES + CRN 페어 실험 + DoE 그리드 탐색

## 2. 참고 레포에서 차용할 패턴

| 출처 | 차용할 것 | 적용 방식 |
|------|----------|----------|
| **inventory-simulation** | `run(params) → dict` 단일 실행 패턴, `run_experiments(grid, R)` 그리드 탐색 | `run_scenario(params, scenario, seed) → KPI dict` 함수 구조 |
| **HSR_Simulation_SimPy** | SimPy generator로 열차 이동 모델링, 정차시간 변동성, 블록 자원 관리 | 철도 구간 SimPy 프로세스, 열차 capacity를 SimPy Resource로 관리 |
| **Traffic_Assignment_Tutorial** | BPR 함수 구현 (`t = t0 * (1 + α*(v/C)^β)`) | `models.py`에 BPR 함수 1개 구현. assignment 알고리즘 불필요 |
| **nxsim** | `NetworkEnvironment(simpy.Environment + nx.Graph)` 패턴 | `network.py`에서 추상 그래프 생성. SimPy Environment에 그래프 참조 연결 |

## 3. 프로젝트 구조

```
transport-system-sim/
├── config.yaml                  # 모든 파라미터 정의
├── src/
│   ├── __init__.py
│   ├── network.py               # 추상 네트워크 그래프 생성
│   ├── models.py                # BPR, Bernoulli 파손, LogNormal 지각
│   ├── scenario.py              # 시나리오 실행 (SimPy 프로세스)
│   ├── policies.py              # STRICT, GRACE 출발 정책
│   ├── metrics.py               # KPI 수집기
│   ├── experiment/
│   │   ├── __init__.py
│   │   ├── doe.py               # 실험 그리드 생성 (pyDOE3)
│   │   ├── runner.py            # CRN 페어 실행 + CSV 저장
│   │   └── analysis.py          # CI, break-even 보간
│   └── visualize/
│       ├── __init__.py
│       └── plots.py             # 히트맵, 파레토, 등고선
├── main.py                      # CLI 진입점
├── results/                     # 실험 결과 CSV 출력
└── tests/
    ├── test_models.py           # BPR, 분포 단위테스트
    └── test_scenario.py         # 시나리오 통합테스트
```

## 4. 모듈별 상세 설계

### 4.1 config.yaml

```yaml
network:
  nodes: [H, A, S, R, D]
  road_links:  # from, to, t0(min), capacity(veh/hr), p_fail
    - [A, D_1, 30, 500, 0.05]   # 고속도로 구간1
    - [A, D_2, 45, 300, 0.08]   # 일반도로 구간2
    - [D_1, D, 20, 400, 0.03]   # 고속도로 구간3
    - [D_2, D, 35, 250, 0.10]   # 우회도로
    - [A, S, 15, 200, 0.02]     # 셔틀 구간 (A→S 허브)
    - [R, D, 10, 300, 0.02]     # 라스트마일 (R→D)
  rail_link:  # from, to, t0(min), headway(min), capacity(pax/train)
    - [S, R, 40, 10, 500]

personnel:
  total: 1000           # 총 예비군 인원
  group_size: 45        # 버스당 탑승인원
  arrival_time: 480     # 집결 기준시간 (08:00 = 480min)

bpr:
  alpha: 0.15
  beta: 4.0

congestion_scale:       # s values for Phase 1
  levels: [0.8, 1.0, 1.2, 1.5, 2.0]

failure_rate:           # p_fail multiplier for Phase 1
  levels: [0.0, 0.02, 0.05, 0.10, 0.15]

lateness:
  distribution: lognormal
  mu: 2.0               # LogNormal μ (분)
  sigma_levels: [0.3, 0.5, 0.7, 1.0]  # Phase 2

policies:
  STRICT:
    type: strict
  GRACE:
    type: grace
    W: [15, 30, 60]      # 최대 대기시간(분)
    theta: [0.8, 0.9]    # 도착률 임계

experiment:
  R: 30                  # 반복수
  seed_base: 42
```

### 4.2 network.py — 추상 네트워크

**참고**: nxsim의 `NetworkEnvironment` 패턴 단순화

```python
import networkx as nx

def build_network(config) -> nx.DiGraph:
    """config.yaml에서 추상 네트워크 생성"""
    G = nx.DiGraph()
    for node in config['network']['nodes']:
        G.add_node(node)
    for link in config['network']['road_links']:
        G.add_edge(link[0], link[1],
                   t0=link[2], capacity=link[3],
                   p_fail=link[4], mode='road')
    rail = config['network']['rail_link'][0]
    G.add_edge(rail[0], rail[1],
               t0=rail[2], headway=rail[3],
               capacity=rail[4], mode='rail')
    return G
```

**from nxsim**: 그래프를 SimPy에 직접 연결하지 않고 참조만 전달 (단순화)

### 4.3 models.py — 확률/물리 모델

**참고**: Traffic_Assignment_Tutorial에서 BPR 공식만 추출

```python
import numpy as np

def bpr_travel_time(t0, volume, capacity, alpha=0.15, beta=4.0, scale=1.0):
    """BPR 여행시간 함수 + 전시 혼잡 스케일링"""
    vc = scale * volume / capacity if capacity > 0 else 0
    return t0 * (1 + alpha * vc ** beta)

def sample_link_failure(p_fail, rng):
    """Bernoulli 링크 파손"""
    return rng.random() < p_fail

def sample_arrival_delay(mu, sigma, rng):
    """LogNormal 지각 (분 단위)"""
    return rng.lognormal(mu, sigma)

def compute_reroute_cost(G, failed_edges, source, target):
    """파손 링크 제거 후 최단경로 비용 증분"""
    G_temp = G.copy()
    G_temp.remove_edges_from(failed_edges)
    if nx.has_path(G_temp, source, target):
        return nx.shortest_path_length(G_temp, source, target, weight='t0')
    return float('inf')  # 완전 단절
```

**from Traffic_Assignment_Tutorial**: BPR 공식 1줄 (assignment 알고리즘 제외)
**자체 구현**: Bernoulli 파손, LogNormal 지각, 우회비용 (새로 작성)

### 4.4 policies.py — 출발 정책

**참고**: buskit의 holding 전략 개념, 제안서의 STRICT/GRACE 정의

```python
from abc import ABC, abstractmethod

class DeparturePolicy(ABC):
    @abstractmethod
    def should_depart(self, elapsed_wait, arrived_count, total_expected, bus_capacity):
        ...

class StrictPolicy(DeparturePolicy):
    """정시 출발. 미도착자는 후속 수송."""
    def should_depart(self, elapsed_wait, arrived_count, total_expected, bus_capacity):
        return elapsed_wait >= 0  # 즉시 출발

class GracePolicy(DeparturePolicy):
    """최대 W분 대기 또는 θ% 도착 시 출발."""
    def __init__(self, W, theta):
        self.W = W
        self.theta = theta

    def should_depart(self, elapsed_wait, arrived_count, total_expected, bus_capacity):
        if elapsed_wait >= self.W:
            return True
        if arrived_count / total_expected >= self.theta:
            return True
        if arrived_count >= bus_capacity:
            return True
        return False
```

### 4.5 scenario.py — SimPy 시나리오 실행

**참고**:
- inventory-simulation의 `run(params) → dict` 패턴
- HSR_Simulation_SimPy의 SimPy generator 패턴 (열차 이동, 정차, 자원)

```python
import simpy
import numpy as np

def run_scenario(G, config, scenario_type, policy, params, seed) -> dict:
    """
    단일 시나리오 실행. inventory-simulation의 run() 패턴.

    Args:
        G: NetworkX 그래프
        config: YAML 설정
        scenario_type: 'bus_only' | 'multimodal'
        policy: DeparturePolicy 인스턴스
        params: {s, p_fail_scale, sigma}
        seed: 난수 시드 (CRN용)

    Returns:
        {'makespan': ..., 'success_rate': ..., 'resource_efficiency': ..., ...}
    """
    rng = np.random.default_rng(seed)
    env = simpy.Environment()

    # 1. 병력 생성: 각 병력은 도착지연(지각)을 가짐
    personnel = generate_personnel(config, params, rng)

    # 2. 도로 파손 샘플링
    failed_edges = sample_network_failures(G, params, rng)

    # 3. BPR 여행시간 사전 계산 (파손 반영)
    travel_times = compute_travel_times(G, params, failed_edges)

    # 4. 시나리오별 SimPy 프로세스 실행
    if scenario_type == 'bus_only':
        metrics = run_bus_only(env, G, config, personnel, travel_times, policy, rng)
    else:
        metrics = run_multimodal(env, G, config, personnel, travel_times, policy, rng)

    env.run()

    return metrics.as_dict()

def run_bus_only(env, G, config, personnel, travel_times, policy, rng):
    """Scenario 1: H→A→(버스)→도로망→D"""
    metrics = MetricsCollector()
    bus_cap = config['personnel']['group_size']

    # 집결 프로세스: 병력이 A에 도착 (지각 반영)
    # 배차 프로세스: policy.should_depart()로 출발 결정
    # 이동 프로세스: BPR 여행시간으로 timeout
    # 도착 프로세스: D 도착 시각 기록 → makespan 갱신
    ...

def run_multimodal(env, G, config, personnel, travel_times, policy, rng):
    """Scenario 2: H→A→(셔틀)→S→(철도)→R→(라스트마일)→D"""
    metrics = MetricsCollector()

    # 집결 + 셔틀: A→S
    # 철도: SimPy Resource로 열차 용량 관리 (HSR_Simulation_SimPy 패턴)
    #   - headway 간격으로 열차 출발
    #   - capacity 제한으로 대기 발생
    # 라스트마일: R→D 버스
    ...
```

**from inventory-simulation**: `run() → dict` 단일 실행 + `env.run()` 패턴
**from HSR_Simulation_SimPy**: 열차를 SimPy Resource로 관리, headway timeout

### 4.6 experiment/ — DoE + CRN 러너

**참고**: inventory-simulation의 `run_experiments()` 패턴, pyDOE3

```python
# doe.py
from itertools import product

def phase1_grid(config):
    """s × p_fail 완전요인 그리드"""
    s_levels = config['congestion_scale']['levels']
    p_levels = config['failure_rate']['levels']
    return list(product(s_levels, p_levels))

def phase2_grid(config):
    """σ × 정책 그리드"""
    sigma_levels = config['lateness']['sigma_levels']
    policies = build_policies(config)
    return list(product(sigma_levels, policies))

# runner.py
def run_paired_experiment(grid, config, R):
    """
    CRN 페어 실행: 각 (s, p_fail)마다 같은 seed로 Scenario 1 & 2 실행
    inventory-simulation의 run_experiments() 패턴
    """
    results = []
    for s, p_fail in grid:
        for r in range(R):
            seed = config['experiment']['seed_base'] + r
            params = {'s': s, 'p_fail_scale': p_fail, 'sigma': config['lateness']['mu']}

            bus_result = run_scenario(G, config, 'bus_only', policy, params, seed)
            multi_result = run_scenario(G, config, 'multimodal', policy, params, seed)

            results.append({
                's': s, 'p_fail': p_fail, 'rep': r, 'seed': seed,
                'bus_makespan': bus_result['makespan'],
                'multi_makespan': multi_result['makespan'],
                'delta_makespan': bus_result['makespan'] - multi_result['makespan'],
                ...
            })
    return pd.DataFrame(results)

# analysis.py
def compute_ci(df, metric, group_cols):
    """95% 신뢰구간"""
    grouped = df.groupby(group_cols)[metric]
    return grouped.agg(['mean', 'std', 'count']).assign(
        ci_lower=lambda x: x['mean'] - 1.96 * x['std'] / np.sqrt(x['count']),
        ci_upper=lambda x: x['mean'] + 1.96 * x['std'] / np.sqrt(x['count'])
    )

def find_breakeven(df, s_value):
    """Δ=0이 되는 p_fail* 보간 추정"""
    ...
```

### 4.7 visualize/plots.py

```python
import seaborn as sns

def plot_delta_heatmap(df):
    """Δ(s, p_fail) = bus_makespan - multi_makespan 히트맵"""
    pivot = df.pivot_table(index='p_fail', columns='s', values='delta_makespan', aggfunc='mean')
    sns.heatmap(pivot, annot=True, cmap='RdBu_r', center=0)

def plot_success_rate_surface(df):
    """SuccessRate 곡면"""
    ...

def plot_policy_pareto(df):
    """정책별 파레토 (시간 vs 미수송)"""
    ...
```

## 5. main.py — 전체 파이프라인

```python
import yaml
from src.network import build_network
from src.experiment.doe import phase1_grid, phase2_grid
from src.experiment.runner import run_paired_experiment
from src.experiment.analysis import compute_ci, find_breakeven
from src.visualize.plots import plot_delta_heatmap, plot_policy_pareto

# 1. 설정 로드
config = yaml.safe_load(open('config.yaml'))
G = build_network(config)

# 2. Phase 1: s × p_fail break-even 탐색
grid1 = phase1_grid(config)
df1 = run_paired_experiment(grid1, config, R=config['experiment']['R'])
df1.to_csv('results/phase1_results.csv', index=False)

ci1 = compute_ci(df1, 'delta_makespan', ['s', 'p_fail'])
plot_delta_heatmap(df1)

# 3. Phase 2: σ × 정책 파레토 분석
grid2 = phase2_grid(config)
df2 = run_paired_experiment(grid2, config, R=config['experiment']['R'])
df2.to_csv('results/phase2_results.csv', index=False)

plot_policy_pareto(df2)

# 4. Break-even 추정
for s in config['congestion_scale']['levels']:
    p_star = find_breakeven(df1, s)
    print(f"s={s}: break-even p_fail* = {p_star:.4f}")
```

## 6. 구현 순서 (Step-by-step)

| Step | 파일 | 내용 | 참고 레포 |
|------|------|------|----------|
| 1 | `config.yaml` | 전체 파라미터 정의 | 제안서 §6 |
| 2 | `src/network.py` | 추상 그래프 생성 | nxsim 패턴 |
| 3 | `src/models.py` | BPR, 파손, 지각, 우회 | Traffic_Assignment_Tutorial BPR |
| 4 | `src/policies.py` | STRICT, GRACE 정책 | 제안서 §3.3 |
| 5 | `src/metrics.py` | KPI 수집기 | 자체 설계 |
| 6 | `src/scenario.py` | SimPy 시나리오 (버스 단독 먼저) | HSR_SimPy 패턴 + inventory-sim run() |
| 7 | `src/scenario.py` | SimPy 시나리오 (복합 추가) | HSR_SimPy 열차 Resource |
| 8 | `tests/` | 단위테스트 | - |
| 9 | `src/experiment/doe.py` | 실험 그리드 | pyDOE3 |
| 10 | `src/experiment/runner.py` | CRN 페어 실행 | inventory-sim run_experiments() |
| 11 | `src/experiment/analysis.py` | CI, break-even | scipy.stats |
| 12 | `src/visualize/plots.py` | 시각화 | matplotlib/seaborn |
| 13 | `main.py` | 전체 파이프라인 연결 | - |
| 14 | 검증 | 인원 보존, 극단 케이스 확인 | 제안서 §7 Step 8 |
