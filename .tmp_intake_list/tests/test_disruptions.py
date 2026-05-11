"""Tests for structured disruption sampling."""

import os
import sys

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.disruptions import (
    blocked_edges,
    edge_effective_capacity,
    effective_capacity,
    is_blocked,
    is_edge_blocked,
    sample_edge_disruptions,
    sample_disruptions,
    scaled_failure_probability,
)
from src.models import sample_link_failures
from src.sim_types import EdgeDisruption


def make_graph() -> nx.DiGraph:
    """Build a small graph with road and rail edges."""
    G = nx.DiGraph()
    G.add_edge("A", "B", capacity=500.0, p_fail=1.0, mode="road")
    G.add_edge("B", "C", capacity=300.0, p_fail=0.0, mode="road")
    G.add_edge("S", "R", capacity=1000.0, p_fail=1.0, mode="rail")
    return G


def assert_raises_value_error(func):
    """Assert that a zero-argument function raises ValueError."""
    try:
        func()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_blocked_mode_samples_structured_states():
    """Blocked mode should mark sampled road edges as blocked."""
    rng = np.random.default_rng(7)
    disruptions = sample_edge_disruptions(
        make_graph(),
        p_fail_scale=1.0,
        rng=rng,
        mode="blocked",
    )

    assert isinstance(disruptions[("A", "B")], EdgeDisruption)
    assert is_edge_blocked(disruptions, ("A", "B"))
    assert is_blocked(disruptions[("A", "B")])
    assert is_blocked(disruptions, ("A", "B"))
    assert disruptions[("A", "B")].capacity_factor == 0.0
    assert not is_edge_blocked(disruptions, ("B", "C"))
    assert not is_edge_blocked(disruptions, ("S", "R"))
    assert blocked_edges(disruptions) == [("A", "B")]
    print("PASS: blocked mode samples structured states")


def test_capacity_reduction_mode_degrades_capacity_without_blocking():
    """Capacity-reduction mode should keep sampled edges usable."""
    G = make_graph()
    rng = np.random.default_rng(7)
    disruptions = sample_edge_disruptions(
        G,
        p_fail_scale=1.0,
        rng=rng,
        mode="capacity_reduction",
        capacity_reduction_factor=0.4,
    )

    disruption = disruptions[("A", "B")]
    assert disruption.status == "degraded"
    assert disruption.capacity_factor == 0.4
    assert not disruption.is_blocked
    assert blocked_edges(disruptions) == []
    assert effective_capacity(500.0, disruption) == 200.0
    assert edge_effective_capacity(G, disruptions, ("A", "B")) == 200.0
    assert edge_effective_capacity(G, disruptions, ("S", "R")) == 1000.0
    print("PASS: capacity reduction degrades capacity without blocking")


def test_rail_is_immune_by_default_but_can_be_enabled():
    """Rail edges should remain normal unless rail immunity is disabled."""
    G = make_graph()

    immune = sample_edge_disruptions(
        G,
        p_fail_scale=1.0,
        rng=np.random.default_rng(1),
        mode="blocked",
    )
    assert not immune[("S", "R")].is_blocked

    enabled = sample_edge_disruptions(
        G,
        p_fail_scale=1.0,
        rng=np.random.default_rng(1),
        mode="blocked",
        rail_immune=False,
    )
    assert enabled[("S", "R")].is_blocked
    print("PASS: rail immunity defaults on and can be disabled")


def test_same_seed_produces_same_disruption_state():
    """Two generators with the same seed should produce equal states."""
    G = nx.DiGraph()
    G.add_edge("A", "B", capacity=500.0, p_fail=0.2, mode="road")
    G.add_edge("B", "C", capacity=500.0, p_fail=0.4, mode="road")
    G.add_edge("C", "D", capacity=500.0, p_fail=0.8, mode="road")

    first = sample_disruptions(
        G,
        p_fail_scale=0.75,
        rng=np.random.default_rng(123),
        mode="capacity_reduction",
        capacity_reduction_factor=0.5,
    )
    second = sample_disruptions(
        G,
        p_fail_scale=0.75,
        rng=np.random.default_rng(123),
        mode="capacity_reduction",
        capacity_reduction_factor=0.5,
    )

    assert first == second
    print("PASS: same seed produces the same disruption state")


def test_failure_probability_uses_multiplier_semantics():
    """p_fail_scale should multiply base p_fail and clip at one."""
    assert scaled_failure_probability({"p_fail": 0.25}, 0.0) == 0.0
    assert scaled_failure_probability({"p_fail": 0.25}, 2.0) == 0.5
    assert scaled_failure_probability({"p_fail": 0.75}, 2.0) == 1.0

    disruptions = sample_edge_disruptions(
        make_graph(),
        p_fail_scale=0.0,
        rng=np.random.default_rng(7),
    )
    assert blocked_edges(disruptions) == []
    print("PASS: p_fail_scale multiplier semantics are explicit")


def test_legacy_sample_link_failures_returns_blocked_edges_only():
    """The models wrapper should preserve the old list-of-failed-edges API."""
    G = make_graph()
    blocked = sample_link_failures(G, 1.0, np.random.default_rng(7))
    degraded = sample_link_failures(
        G,
        1.0,
        np.random.default_rng(7),
        mode="capacity_reduction",
        capacity_reduction_factor=0.4,
    )

    assert blocked == [("A", "B")]
    assert degraded == []
    print("PASS: legacy sample_link_failures returns blocked edges only")


def test_invalid_disruption_parameters_raise_value_error():
    """Invalid disruption controls should fail early."""
    G = make_graph()
    rng = np.random.default_rng(7)

    assert_raises_value_error(
        lambda: sample_edge_disruptions(G, 1.0, rng, mode="detour")
    )
    assert_raises_value_error(lambda: sample_edge_disruptions(G, -1.0, rng))
    assert_raises_value_error(lambda: sample_edge_disruptions(G, float("nan"), rng))
    assert_raises_value_error(lambda: scaled_failure_probability({"p_fail": -0.1}, 1.0))
    assert_raises_value_error(lambda: EdgeDisruption(status="offline"))
    assert_raises_value_error(lambda: EdgeDisruption(status="degraded", capacity_factor=1.1))
    assert_raises_value_error(
        lambda: sample_edge_disruptions(
            G,
            1.0,
            rng,
            mode="capacity_reduction",
            capacity_reduction_factor=0.0,
        )
    )
    print("PASS: invalid disruption parameters raise ValueError")


TESTS = [
    test_blocked_mode_samples_structured_states,
    test_capacity_reduction_mode_degrades_capacity_without_blocking,
    test_rail_is_immune_by_default_but_can_be_enabled,
    test_same_seed_produces_same_disruption_state,
    test_failure_probability_uses_multiplier_semantics,
    test_legacy_sample_link_failures_returns_blocked_edges_only,
    test_invalid_disruption_parameters_raise_value_error,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== DISRUPTION TESTS PASSED ===")
