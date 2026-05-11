"""Tests for dynamic road traffic accounting."""

import math
import os
import sys

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import bpr_travel_time
from src.sim_types import EdgeDisruption
from src.traffic import DynamicRoadTraffic


def make_graph() -> nx.DiGraph:
    """Build a small road graph for traffic tests."""
    graph = nx.DiGraph()
    graph.add_edge("A", "B", t0=10.0, capacity=100.0, p_fail=0.0, mode="road")
    graph.add_edge("B", "C", t0=20.0, capacity=100.0, p_fail=0.0, mode="road")
    graph.add_edge("C", "D", t0=30.0, capacity=100.0, p_fail=0.0, mode="rail")
    return graph


def assert_close(actual: float, expected: float, tolerance: float = 1e-9) -> None:
    assert abs(actual - expected) <= tolerance, (
        f"expected {expected}, got {actual}"
    )


def test_edge_entries_feed_rolling_volume() -> None:
    """Road travel time should use background plus recent edge entries."""
    graph = make_graph()
    traffic = DynamicRoadTraffic(
        graph,
        volume_window_min=60.0,
        background_volume=100.0,
        alpha=1.0,
        beta=1.0,
    )

    first = traffic.enter_edge(("A", "B"), 0.0)
    second = traffic.enter_edge(("A", "B"), 30.0)
    third = traffic.enter_edge(("A", "B"), 61.0)

    assert_close(first.effective_volume, 101.0)
    assert_close(second.effective_volume, 102.0)
    assert_close(third.effective_volume, 102.0)
    assert traffic.entry_count(("A", "B"), 61.0) == 2
    assert_close(
        first.travel_time,
        bpr_travel_time(
            t0=10.0,
            volume=101.0,
            capacity=100.0,
            alpha=1.0,
            beta=1.0,
        ),
    )
    print("PASS: rolling traffic volume feeds BPR")


def test_route_traversal_uses_edge_exit_as_next_entry() -> None:
    """A route should be traversed edge-by-edge with updated entry times."""
    graph = make_graph()
    traffic = DynamicRoadTraffic(
        graph,
        volume_window_min=60.0,
        background_volume=0.0,
        alpha=0.0,
    )

    total_time, traversals = traffic.traverse_route(["A", "B", "C"], 5.0)

    assert_close(total_time, 30.0)
    assert [traversal.edge for traversal in traversals] == [
        ("A", "B"),
        ("B", "C"),
    ]
    assert_close(traversals[0].entry_time, 5.0)
    assert_close(traversals[0].exit_time, 15.0)
    assert_close(traversals[1].entry_time, 15.0)
    assert_close(traversals[1].exit_time, 35.0)
    print("PASS: route traversal advances entry times edge-by-edge")


def test_degraded_disruption_reduces_bpr_capacity() -> None:
    """A degraded edge should apply its capacity factor before BPR."""
    graph = make_graph()
    traffic = DynamicRoadTraffic(
        graph,
        volume_window_min=60.0,
        background_volume=50.0,
        alpha=1.0,
        beta=1.0,
        disruptions={
            ("A", "B"): EdgeDisruption(status="degraded", capacity_factor=0.5),
        },
    )

    traversal = traffic.enter_edge(("A", "B"), 0.0)

    assert_close(traversal.effective_capacity, 50.0)
    assert_close(traversal.effective_volume, 51.0)
    assert_close(
        traversal.travel_time,
        bpr_travel_time(
            t0=10.0,
            volume=51.0,
            capacity=50.0,
            alpha=1.0,
            beta=1.0,
        ),
    )
    print("PASS: degraded disruption reduces road capacity")


def test_congestion_scale_monotonically_increases_travel_time() -> None:
    """Higher BPR scale should not reduce dynamic road travel time."""
    graph = make_graph()
    normal = DynamicRoadTraffic(
        graph,
        volume_window_min=60.0,
        background_volume=100.0,
        alpha=0.15,
        beta=4.0,
        scale=1.0,
    )
    wartime = DynamicRoadTraffic(
        graph,
        volume_window_min=60.0,
        background_volume=100.0,
        alpha=0.15,
        beta=4.0,
        scale=2.0,
    )

    normal_traversal = normal.enter_edge(("A", "B"), 0.0)
    wartime_traversal = wartime.enter_edge(("A", "B"), 0.0)

    assert wartime_traversal.travel_time >= normal_traversal.travel_time
    print("PASS: congestion scale monotonically increases travel time")


def test_blocked_disruption_stops_route_without_recording_entry() -> None:
    """A blocked edge should make the route unreachable and not add traffic."""
    graph = make_graph()
    traffic = DynamicRoadTraffic(
        graph,
        volume_window_min=60.0,
        background_volume=0.0,
        disruptions={
            ("A", "B"): EdgeDisruption(status="blocked", capacity_factor=0.0),
        },
    )

    total_time, traversals = traffic.traverse_route(["A", "B", "C"], 0.0)

    assert total_time == math.inf
    assert len(traversals) == 1
    assert traversals[0].travel_time == math.inf
    assert traffic.entry_count(("A", "B"), 0.0) == 0
    print("PASS: blocked disruption stops route")


def test_non_road_edges_use_t0_without_dynamic_bpr() -> None:
    """Route traversal can pass through non-road edges without road volume BPR."""
    graph = make_graph()
    traffic = DynamicRoadTraffic(
        graph,
        volume_window_min=60.0,
        background_volume=1000.0,
        alpha=1.0,
        beta=1.0,
    )

    traversal = traffic.enter_edge(("C", "D"), 12.0)

    assert_close(traversal.travel_time, 30.0)
    assert_close(traversal.exit_time, 42.0)
    assert traffic.entry_count(("C", "D"), 12.0) == 0
    print("PASS: non-road edges use free-flow t0")


def test_traffic_validation_rejects_invalid_times_and_routes() -> None:
    """Traffic helpers should reject non-finite times and malformed routes."""
    graph = make_graph()

    try:
        DynamicRoadTraffic(graph, volume_window_min=float("nan"))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid volume_window_min should raise ValueError")

    traffic = DynamicRoadTraffic(graph, volume_window_min=60.0)
    invalid_calls = [
        lambda: traffic.enter_edge(("A", "B"), float("nan")),
        lambda: traffic.traverse_route("ABC", 0.0),
        lambda: traffic.traverse_route([("A", "B"), ("B",)], 0.0),
    ]

    for call in invalid_calls:
        try:
            call()
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError("invalid traffic input should raise")
    print("PASS: traffic validation rejects invalid inputs")


TESTS = [
    test_edge_entries_feed_rolling_volume,
    test_route_traversal_uses_edge_exit_as_next_entry,
    test_degraded_disruption_reduces_bpr_capacity,
    test_congestion_scale_monotonically_increases_travel_time,
    test_blocked_disruption_stops_route_without_recording_entry,
    test_non_road_edges_use_t0_without_dynamic_bpr,
    test_traffic_validation_rejects_invalid_times_and_routes,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== TRAFFIC TESTS PASSED ===")
