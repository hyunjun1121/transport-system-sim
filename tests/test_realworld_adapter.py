"""Offline tests for zone connectors and the real-world graph adapter."""

import os
import sys

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.adapter import build_simulator_graph, realworld_network_config
from src.realworld.attributes import RoadClassDefaults
from src.realworld.regions import load_region_spec
from src.realworld.zones import nearest_road_node, snap_region_points


def minimal_region_dict() -> dict:
    """Return a canonical simulator-compatible region spec."""

    return {
        "region_id": "adapter_fixture",
        "name": "Adapter Fixture",
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
    """Build a tiny directed road graph with one parallel-edge choice."""

    graph = nx.MultiDiGraph()
    graph.add_node(1, x=127.1000, y=37.5000)
    graph.add_node(2, x=127.1100, y=37.5050)
    graph.add_node(3, x=127.1200, y=37.5150)
    graph.add_node(4, x=127.1300, y=37.5200)

    graph.add_edge(1, 2, key="slow", osmid="12-slow", highway="primary", maxspeed=30, length=1_000)
    graph.add_edge(1, 2, key="fast", osmid="12-fast", highway="primary", maxspeed=60, length=1_000)
    graph.add_edge(2, 3, key=0, osmid="23", highway="secondary", maxspeed=50, length=1_500)
    graph.add_edge(3, 4, key=0, osmid="34", highway="secondary", maxspeed=50, length=1_500)
    graph.add_edge(4, 3, key=0, osmid="43", highway="secondary", maxspeed=50, length=1_500)
    return graph


def synthetic_osm_like_graph_with_footway() -> nx.MultiDiGraph:
    """Return the base fixture plus a closer non-routeable pedestrian edge."""

    graph = synthetic_osm_like_graph()
    graph.add_node("walk_a", x=127.1001, y=37.5001)
    graph.add_node("walk_b", x=127.1101, y=37.5051)
    graph.add_edge("walk_a", "walk_b", key=0, osmid="walk", highway="footway", maxspeed=5, length=10)
    return graph


def assert_required_edge_fields(graph: nx.DiGraph) -> None:
    """All simulator edges must carry the fields used by scenario/traffic."""

    for u, v, data in graph.edges(data=True):
        for field in ("t0", "capacity", "p_fail", "base_p_fail", "mode"):
            assert field in data, f"{u!r}->{v!r} missing {field}"
        assert data["t0"] > 0
        assert data["capacity"] > 0
        assert 0 <= data["p_fail"] <= 1
        assert 0 <= data["base_p_fail"] <= 1


def test_snaps_region_points_to_nearest_road_nodes() -> None:
    """Zone and rail points should snap by finite node x/y lon/lat values."""

    graph = synthetic_osm_like_graph()
    snaps = snap_region_points(graph, minimal_region_dict())

    assert snaps["A"].road_node == 1
    assert snaps["S"].road_node == 2
    assert snaps["R"].road_node == 3
    assert snaps["D"].road_node == 4
    assert snaps["A"].distance_m < 20

    nearest = nearest_road_node(graph, load_region_spec(minimal_region_dict()).primary_destination)
    assert nearest.road_node == 4

    print("PASS: region points snap to nearest road nodes")


def test_adapter_builds_routeable_simulator_digraph() -> None:
    """Converted graph should route the simulator's required road legs."""

    graph = build_simulator_graph(synthetic_osm_like_graph_with_footway(), minimal_region_dict())

    assert isinstance(graph, nx.DiGraph)
    assert not graph.is_multigraph()
    assert nx.has_path(graph, "A", "D")
    assert nx.has_path(graph, "A", "S")
    assert nx.has_path(graph, "R", "D")
    assert_required_edge_fields(graph)

    assert graph.edges[1, 2]["realworld_edge_id"] == "12-fast"
    assert "walk_a" not in graph
    assert "walk_b" not in graph
    assert graph.edges["A", 1]["mode"] == "road"
    assert graph.edges["A", 1]["source"] == "connector"
    assert graph.edges[1, "A"]["source"] == "connector"
    assert graph.nodes["A"]["snapped_road_node"] == 1
    assert graph.graph["source_edge_count"] == 6
    assert graph.graph["routeable_source_edge_count"] == 5

    print("PASS: adapter builds routeable simulator DiGraph")


def test_adapter_applies_reviewed_highway_defaults_when_supplied() -> None:
    """Reviewed road defaults should flow through graph adaptation explicitly."""

    graph = build_simulator_graph(
        synthetic_osm_like_graph(),
        minimal_region_dict(),
        highway_defaults={
            "primary": RoadClassDefaults(
                speed_kph=42.0,
                capacity=1234.0,
                base_p_fail=0.012,
            )
        },
    )

    assert graph.graph["road_class_overrides_applied"] is True
    # The fixture edge has maxspeed, so speed comes from OSM. Capacity and
    # base_p_fail use the reviewed fallback defaults.
    assert graph.edges[1, 2]["speed_kph"] == 60.0
    assert graph.edges[1, 2]["capacity"] == 1234.0
    assert graph.edges[1, 2]["base_p_fail"] == 0.012

    print("PASS: adapter applies supplied highway defaults")


def test_connector_edges_are_traversable_by_road_mode_filter() -> None:
    """Connector edges must use mode='road' for current run_scenario filters."""

    graph = build_simulator_graph(synthetic_osm_like_graph(), minimal_region_dict())
    road_only = nx.subgraph_view(
        graph,
        filter_edge=lambda u, v: graph.edges[u, v].get("mode") == "road",
    )

    assert nx.has_path(road_only, "A", "D")
    assert nx.has_path(road_only, "A", "S")
    assert nx.has_path(road_only, "R", "D")
    assert graph.edges["S", 2]["source"] == "connector"
    assert graph.edges["R", 3]["source"] == "connector"

    print("PASS: connector edges are road-routeable")


def test_adapter_generates_config_compatible_rail_metadata() -> None:
    """Region rail fields should map to current config rail_link shape."""

    config = realworld_network_config(minimal_region_dict())
    assert config["nodes"] == ["A", "D", "S", "R"]
    assert config["rail_link"] == [("S", "R", 40.0, 10.0, 500)]

    graph = build_simulator_graph(synthetic_osm_like_graph(), minimal_region_dict())
    assert graph.graph["rail_link"] == [("S", "R", 40.0, 10.0, 500)]

    print("PASS: rail metadata is config-compatible")


def test_disconnected_required_route_fails_clearly() -> None:
    """Disconnected road graphs should fail instead of adding hidden shortcuts."""

    graph = synthetic_osm_like_graph()
    graph.remove_edge(2, 3, 0)

    try:
        build_simulator_graph(graph, minimal_region_dict())
    except ValueError as exc:
        assert "no route A -> D" in str(exc)
    else:
        raise AssertionError("Disconnected graph did not raise ValueError")

    print("PASS: disconnected required route fails clearly")


if __name__ == "__main__":
    test_snaps_region_points_to_nearest_road_nodes()
    test_adapter_builds_routeable_simulator_digraph()
    test_adapter_applies_reviewed_highway_defaults_when_supplied()
    test_connector_edges_are_traversable_by_road_mode_filter()
    test_adapter_generates_config_compatible_rail_metadata()
    test_disconnected_required_route_fails_clearly()
    print("\n=== REALWORLD ADAPTER TESTS PASSED ===")
