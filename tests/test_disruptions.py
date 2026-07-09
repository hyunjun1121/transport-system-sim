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
    sample_correlated_failures,
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


def test_edge_disruption_travel_time_multiplier_field():
    """travel_time_multiplier is an orthogonal direct-slowdown lever.

    Under the wartime V~0 frame the BPR volume-delay term is a near-no-op, so a
    capacity_reduction disruption barely slows a damaged road. travel_time_multiplier
    scales free-flow t0 directly (decoupled from BPR) so a damaged road is actually
    slower. Default 1.0 leaves traversal unchanged (baseline non-regression).
    """
    assert EdgeDisruption().travel_time_multiplier == 1.0
    degraded = EdgeDisruption(
        status="degraded", capacity_factor=0.5, travel_time_multiplier=2.0
    )
    assert degraded.travel_time_multiplier == 2.0
    # orthogonal to existing fields
    assert degraded.capacity_factor == 0.5
    assert not degraded.is_blocked
    # strictly positive (0 would zero travel time = teleport)
    assert_raises_value_error(lambda: EdgeDisruption(travel_time_multiplier=0.0))
    assert_raises_value_error(lambda: EdgeDisruption(travel_time_multiplier=-1.0))
    print("PASS: EdgeDisruption.travel_time_multiplier field + validation")


def test_road_travel_time_multiplier_threads_to_disrupted_edges():
    """road_travel_time_multiplier threads from the sampler to disrupted edges only.

    Disrupted (failed) edges carry the multiplier; normal edges stay at the
    default 1.0. This is how a damaged-road scenario reaches the per-edge
    direct-slowdown lever in enter_edge.
    """
    G = make_graph()  # (A,B) p_fail=1.0 (fails), (B,C) p_fail=0.0 (normal)
    disruptions = sample_edge_disruptions(
        G,
        p_fail_scale=1.0,
        rng=np.random.default_rng(7),
        mode="capacity_reduction",
        capacity_reduction_factor=0.5,
        road_travel_time_multiplier=2.0,
    )
    ab = disruptions[("A", "B")]
    assert not ab.is_blocked
    assert ab.capacity_factor == 0.5
    assert ab.travel_time_multiplier == 2.0
    # normal edge keeps the default
    assert disruptions[("B", "C")].travel_time_multiplier == 1.0

    # default (param omitted) -> all edges at 1.0
    disruptions_default = sample_edge_disruptions(
        G,
        1.0,
        np.random.default_rng(7),
        mode="capacity_reduction",
        capacity_reduction_factor=0.5,
    )
    assert disruptions_default[("A", "B")].travel_time_multiplier == 1.0
    print("PASS: road_travel_time_multiplier threads to disrupted edges only")


def test_correlated_zero_radius_matches_independent():
    """Zero correlation radius should produce identical results to independent."""
    G = nx.DiGraph()
    G.add_edge("A", "B", capacity=500.0, p_fail=0.5, mode="road")
    G.add_edge("B", "C", capacity=300.0, p_fail=0.3, mode="road")

    independent = sample_edge_disruptions(
        G, 1.0, np.random.default_rng(42), mode="blocked",
    )
    correlated = sample_correlated_failures(
        G, 1.0, np.random.default_rng(42), mode="blocked",
        correlation_radius_m=0.0,
    )
    assert independent == correlated
    print("PASS: zero correlation radius matches independent sampling")


def test_correlated_nonzero_radius_produces_disruptions():
    """Non-zero radius should sample disruptions without error."""
    G = nx.DiGraph()
    G.add_node("A", x=127.0, y=37.5)
    G.add_node("B", x=127.001, y=37.501)
    G.add_node("C", x=127.002, y=37.502)
    G.add_edge("A", "B", capacity=500.0, p_fail=0.3, mode="road")
    G.add_edge("B", "C", capacity=300.0, p_fail=0.3, mode="road")

    disruptions = sample_correlated_failures(
        G, 1.0, np.random.default_rng(99), mode="blocked",
        correlation_radius_m=500.0, correlation_strength=2.0,
    )
    assert len(disruptions) == 2
    for edge in [("A", "B"), ("B", "C")]:
        assert edge in disruptions
        assert isinstance(disruptions[edge], EdgeDisruption)
    print("PASS: nonzero radius produces disruptions")


def test_correlated_rail_immune_with_coordinates():
    """Rail edges should remain normal even with spatial correlation."""
    G = nx.DiGraph()
    G.add_node("A", x=127.0, y=37.5)
    G.add_node("B", x=127.001, y=37.501)
    G.add_node("S", x=127.002, y=37.502)
    G.add_node("R", x=127.003, y=37.503)
    G.add_edge("A", "B", capacity=500.0, p_fail=0.5, mode="road")
    G.add_edge("S", "R", capacity=1000.0, p_fail=1.0, mode="rail")

    disruptions = sample_correlated_failures(
        G, 1.0, np.random.default_rng(7), mode="blocked",
        correlation_radius_m=1000.0, correlation_strength=2.0,
    )
    assert not disruptions[("S", "R")].is_blocked
    print("PASS: rail immune with spatial correlation")


def test_correlated_no_coordinates_falls_back_gracefully():
    """Edges without node coordinates should still sample via latent field."""
    G = nx.DiGraph()
    G.add_edge("A", "B", capacity=500.0, p_fail=0.5, mode="road")

    disruptions = sample_correlated_failures(
        G, 1.0, np.random.default_rng(7), mode="blocked",
        correlation_radius_m=100.0, correlation_strength=1.0,
    )
    assert isinstance(disruptions[("A", "B")], EdgeDisruption)
    print("PASS: no coordinates falls back gracefully")


def test_correlated_deterministic_with_same_seed():
    """Same seed should produce identical correlated disruptions."""
    G = nx.DiGraph()
    G.add_node("A", x=127.0, y=37.5)
    G.add_node("B", x=127.001, y=37.501)
    G.add_node("C", x=127.005, y=37.505)
    G.add_edge("A", "B", capacity=500.0, p_fail=0.3, mode="road")
    G.add_edge("B", "C", capacity=300.0, p_fail=0.3, mode="road")

    first = sample_correlated_failures(
        G, 1.0, np.random.default_rng(777), mode="blocked",
        correlation_radius_m=500.0, correlation_strength=2.0,
    )
    second = sample_correlated_failures(
        G, 1.0, np.random.default_rng(777), mode="blocked",
        correlation_radius_m=500.0, correlation_strength=2.0,
    )
    assert first == second
    print("PASS: same seed produces identical correlated disruptions")


def test_correlated_nearby_edges_share_latent_field():
    """Nearby edges should fail more often than independent when boosted."""
    G = nx.DiGraph()
    n = 20
    for i in range(n):
        G.add_node(str(i), x=127.0 + i * 0.0001, y=37.5)
    for i in range(n - 1):
        G.add_edge(str(i), str(i + 1), capacity=500.0, p_fail=0.05, mode="road")

    n_replications = 200
    correlated_count = 0
    independent_count = 0

    for seed in range(n_replications):
        rng_c = np.random.default_rng(seed)
        rng_i = np.random.default_rng(seed)
        c = sample_correlated_failures(
            G, 1.0, rng_c, mode="blocked",
            correlation_radius_m=200.0, correlation_strength=3.0,
        )
        i = sample_edge_disruptions(G, 1.0, rng_i, mode="blocked")
        correlated_count += sum(1 for d in c.values() if d.is_blocked)
        independent_count += sum(1 for d in i.values() if d.is_blocked)

    assert correlated_count >= independent_count
    print(
        f"PASS: correlated failures ({correlated_count}) >= "
        f"independent ({independent_count}) over {n_replications} replications"
    )


def test_correlated_invalid_parameters_raise():
    """Invalid correlation parameters should raise ValueError."""
    G = nx.DiGraph()
    G.add_edge("A", "B", capacity=500.0, p_fail=0.5, mode="road")
    rng = np.random.default_rng(1)

    assert_raises_value_error(
        lambda: sample_correlated_failures(
            G, 1.0, rng, correlation_radius_m=-1.0,
        )
    )
    assert_raises_value_error(
        lambda: sample_correlated_failures(
            G, 1.0, rng, correlation_strength=-0.5,
        )
    )
    print("PASS: invalid correlation parameters raise ValueError")


TESTS = [
    test_blocked_mode_samples_structured_states,
    test_capacity_reduction_mode_degrades_capacity_without_blocking,
    test_rail_is_immune_by_default_but_can_be_enabled,
    test_same_seed_produces_same_disruption_state,
    test_failure_probability_uses_multiplier_semantics,
    test_legacy_sample_link_failures_returns_blocked_edges_only,
    test_invalid_disruption_parameters_raise_value_error,
    test_edge_disruption_travel_time_multiplier_field,
    test_road_travel_time_multiplier_threads_to_disrupted_edges,
    test_correlated_zero_radius_matches_independent,
    test_correlated_nonzero_radius_produces_disruptions,
    test_correlated_rail_immune_with_coordinates,
    test_correlated_no_coordinates_falls_back_gracefully,
    test_correlated_deterministic_with_same_seed,
    test_correlated_nearby_edges_share_latent_field,
    test_correlated_invalid_parameters_raise,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== DISRUPTION TESTS PASSED ===")
