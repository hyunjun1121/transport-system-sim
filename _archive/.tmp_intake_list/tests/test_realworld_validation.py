"""Offline tests for real-world graph readiness validation."""

import os
import sys

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.adapter import build_simulator_graph
from src.realworld.validation import assert_graph_ready, validate_graph_readiness


def minimal_region_dict() -> dict:
    """Return a canonical simulator-compatible region spec."""

    return {
        "region_id": "validation_fixture",
        "name": "Validation Fixture",
        "boundary": {
            "type": "bbox",
            "north": 37.53,
            "south": 37.49,
            "east": 127.14,
            "west": 127.08,
        },
        "assembly_zones": [{"id": "A", "lat": 37.5001, "lon": 127.1001}],
        "destination_zones": [{"id": "D", "lat": 37.5201, "lon": 127.1301}],
        "rail": {
            "access": {"id": "S", "lat": 37.5051, "lon": 127.1101},
            "egress": {"id": "R", "lat": 37.5151, "lon": 127.1201},
            "travel_time_min": 40,
            "headway_min": 10,
            "capacity_pax_per_train": 500,
        },
    }


def synthetic_osm_like_graph() -> nx.MultiDiGraph:
    """Build a routeable directed OSM-like road graph."""

    graph = nx.MultiDiGraph()
    graph.add_node(1, x=127.1000, y=37.5000)
    graph.add_node(2, x=127.1100, y=37.5050)
    graph.add_node(3, x=127.1200, y=37.5150)
    graph.add_node(4, x=127.1300, y=37.5200)

    graph.add_edge(1, 2, key=0, osmid="12", highway="primary", maxspeed=60, length=1_000)
    graph.add_edge(2, 3, key=0, osmid="23", highway="secondary", maxspeed=50, length=1_500)
    graph.add_edge(3, 4, key=0, osmid="34", highway="secondary", maxspeed=50, length=1_500)
    graph.add_edge(4, 3, key=0, osmid="43", highway="secondary", maxspeed=50, length=1_500)
    return graph


def simulator_graph() -> nx.DiGraph:
    """Return a validated synthetic simulator graph."""

    return build_simulator_graph(synthetic_osm_like_graph(), minimal_region_dict())


def assert_error_contains(report, expected: str) -> None:
    """Assert that a readiness report includes an actionable fragment."""

    message = "\n".join(report.errors)
    assert expected in message, f"expected {expected!r} in {message!r}"


def test_valid_adapter_output_is_graph_ready() -> None:
    """Adapter output should satisfy the scenario-readiness contract."""

    graph = simulator_graph()
    report = validate_graph_readiness(graph)

    assert report.ok
    assert report.errors == ()
    assert report.required_nodes == {
        "assembly": "A",
        "destination": "D",
        "rail_access": "S",
        "rail_egress": "R",
    }
    assert ("bus-only", "A", "D") in report.checked_routes
    assert_graph_ready(graph)

    print("PASS: valid adapter output is graph-ready")


def test_missing_required_nodes_are_reported_clearly() -> None:
    """Missing canonical nodes should be named by role and ID."""

    graph = simulator_graph()
    graph.remove_node("A")

    report = validate_graph_readiness(graph)

    assert not report.ok
    assert_error_contains(report, "Missing required nodes: assembly='A'")
    assert_error_contains(report, "missing node(s) 'A'")

    print("PASS: missing required nodes are reported clearly")


def test_missing_edge_fields_are_reported_clearly() -> None:
    """Edges missing simulator fields should name the edge and fields."""

    graph = simulator_graph()
    del graph.edges[1, 2]["t0"]
    del graph.edges[1, 2]["base_p_fail"]

    report = validate_graph_readiness(graph)

    assert not report.ok
    assert_error_contains(report, "Edge 1->2 missing required fields: t0, base_p_fail")

    print("PASS: missing edge fields are reported clearly")


def test_invalid_edge_values_are_reported_clearly() -> None:
    """Invalid numeric edge values should be rejected before scenario runs."""

    graph = simulator_graph()
    graph.edges[1, 2]["t0"] = 0.0
    graph.edges[2, 3]["capacity"] = float("inf")
    graph.edges[3, 4]["p_fail"] = 1.5
    graph.edges[4, 3]["mode"] = ""

    report = validate_graph_readiness(graph)

    assert not report.ok
    assert_error_contains(report, "Edge 1->2 has invalid t0")
    assert_error_contains(report, "Edge 2->3 has invalid capacity")
    assert_error_contains(report, "Edge 3->4 has invalid p_fail")
    assert_error_contains(report, "Edge 4->3 has invalid mode")

    print("PASS: invalid edge values are reported clearly")


def test_disconnected_required_road_segments_are_reported_clearly() -> None:
    """Road-mode routeability should catch disconnected bus and access legs."""

    graph = simulator_graph()
    graph.edges[2, 3]["mode"] = "rail"

    report = validate_graph_readiness(graph)

    assert not report.ok
    assert_error_contains(report, "Disconnected road-mode segment for bus-only")
    assert_error_contains(report, "no route 'A' -> 'D'")

    print("PASS: disconnected road segments are reported clearly")


def test_required_node_overrides_are_supported() -> None:
    """Validation can be reused for noncanonical node IDs when needed."""

    graph = nx.DiGraph()
    graph.add_edge("O", "X", t0=1.0, capacity=100.0, p_fail=0.0, base_p_fail=0.0, mode="road")
    graph.add_edge("X", "Z", t0=1.0, capacity=100.0, p_fail=0.0, base_p_fail=0.0, mode="road")
    graph.add_edge("O", "TS", t0=1.0, capacity=100.0, p_fail=0.0, base_p_fail=0.0, mode="road")
    graph.add_edge("TR", "Z", t0=1.0, capacity=100.0, p_fail=0.0, base_p_fail=0.0, mode="road")

    report = validate_graph_readiness(
        graph,
        required_nodes={
            "assembly": "O",
            "destination": "Z",
            "rail_access": "TS",
            "rail_egress": "TR",
        },
    )

    assert report.ok

    print("PASS: required node overrides are supported")


if __name__ == "__main__":
    test_valid_adapter_output_is_graph_ready()
    test_missing_required_nodes_are_reported_clearly()
    test_missing_edge_fields_are_reported_clearly()
    test_invalid_edge_values_are_reported_clearly()
    test_disconnected_required_road_segments_are_reported_clearly()
    test_required_node_overrides_are_supported()
    print("\n=== REALWORLD VALIDATION TESTS PASSED ===")
