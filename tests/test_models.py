"""Unit tests for models and network."""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import bpr_travel_time, sample_link_failures, sample_arrival_delays
from src.network import build_network
from src.policies import StrictPolicy, GracePolicy, build_policies
from src.metrics import MetricsCollector


def test_bpr_free_flow():
    """BPR at zero volume should return free-flow time."""
    assert bpr_travel_time(30, 0, 500) == 30.0
    assert bpr_travel_time(45, 0, 300) == 45.0
    print("PASS: BPR free-flow")


def test_bpr_congestion():
    """BPR with congestion should increase travel time."""
    t_free = bpr_travel_time(30, 0, 500)
    t_cong = bpr_travel_time(30, 400, 500)
    assert t_cong > t_free
    print(f"PASS: BPR congestion ({t_free:.1f} -> {t_cong:.1f})")


def test_bpr_scale():
    """Wartime scaling should increase congestion effect."""
    t_normal = bpr_travel_time(30, 100, 500, scale=1.0)
    t_war = bpr_travel_time(30, 100, 500, scale=2.0)
    assert t_war >= t_normal
    print(f"PASS: BPR scale ({t_normal:.1f} -> {t_war:.1f})")


def test_bpr_zero_capacity():
    """Zero capacity should return inf."""
    assert bpr_travel_time(30, 100, 0) == float("inf")
    print("PASS: BPR zero capacity")


def test_link_failures():
    """Link failures should be stochastic but respect probability."""
    import networkx as nx
    G = nx.DiGraph()
    G.add_edge("A", "B", t0=30, capacity=500, p_fail=0.5, mode="road")
    G.add_edge("B", "C", t0=20, capacity=300, p_fail=0.0, mode="road")
    G.add_edge("S", "R", t0=40, capacity=500, p_fail=0.0, mode="rail")

    rng = np.random.default_rng(42)
    fails = sample_link_failures(G, 1.0, rng)
    # A->B should fail ~50% of runs over many trials
    # B->C should never fail (p=0)
    # S->R should never fail (rail)
    for f in fails:
        assert f != ("B", "C"), "Zero-probability link should not fail"
        assert f != ("S", "R"), "Rail should not fail"
    print(f"PASS: Link failures (this run: {len(fails)} failures)")


def test_arrival_delays():
    """Arrival delays should be non-negative (LogNormal)."""
    rng = np.random.default_rng(42)
    delays = sample_arrival_delays(100, mu=2.0, sigma=0.5, rng=rng)
    assert len(delays) == 100
    assert all(d >= 0 for d in delays), "LogNormal delays should be non-negative"
    assert np.mean(delays) > 0
    print(f"PASS: Arrival delays (mean={np.mean(delays):.2f} min)")


def test_build_network():
    """Network should have correct structure."""
    config = {
        "network": {
            "nodes": ["H", "A", "S", "R", "D"],
            "road_links": [["A", "D", 30, 500, 0.05]],
            "rail_link": [["S", "R", 40, 10, 500]],
        }
    }
    G = build_network(config)
    assert G.has_edge("A", "D")
    assert G.has_edge("S", "R")
    assert G.edges["A", "D"]["mode"] == "road"
    assert G.edges["S", "R"]["mode"] == "rail"
    print("PASS: Build network")


def test_strict_policy():
    """Strict policy should always depart."""
    p = StrictPolicy()
    assert p.should_depart(0, 0, 100, 45) is True
    assert p.should_depart(100, 10, 100, 45) is True
    assert p.name() == "STRICT"
    print("PASS: Strict policy")


def test_grace_policy():
    """Grace policy should wait for conditions."""
    p = GracePolicy(W=30, theta=0.9)
    # Not enough arrived, not enough time
    assert p.should_depart(0, 5, 100, 45) is False
    # Max wait reached
    assert p.should_depart(30, 5, 100, 45) is True
    # Enough arrived
    assert p.should_depart(10, 90, 100, 45) is True
    # Vehicle full
    assert p.should_depart(5, 45, 100, 45) is True
    print("PASS: Grace policy")


def test_metrics():
    """Metrics should compute KPIs correctly."""
    m = MetricsCollector(total_personnel=100, time_limit=1440)
    m.record_arrival(0, 500)
    m.record_arrival(1, 600)
    m.record_arrival(2, 700)
    m.bus_trips = 3
    m.bus_minutes = 90.0

    assert m.makespan == 700
    assert m.success_count == 3
    assert m.success_rate == 0.03
    d = m.as_dict()
    assert d["makespan"] == 700
    assert d["success_rate"] == 0.03
    print("PASS: Metrics")


def test_build_policies():
    """Policy builder should create correct policies."""
    config = {
        "policies": {
            "STRICT": {"type": "strict"},
            "GRACE": {"type": "grace", "W": [30], "theta": [0.9]},
        }
    }
    policies = build_policies(config)
    assert len(policies) == 2
    names = [p.name() for p in policies]
    assert "STRICT" in names
    assert "GRACE_W30_T0.9" in names
    print("PASS: Build policies")


if __name__ == "__main__":
    test_bpr_free_flow()
    test_bpr_congestion()
    test_bpr_scale()
    test_bpr_zero_capacity()
    test_link_failures()
    test_arrival_delays()
    test_build_network()
    test_strict_policy()
    test_grace_policy()
    test_metrics()
    test_build_policies()
    print("\n=== ALL TESTS PASSED ===")
