"""Offline tests for optional OSM extraction and GraphML cache helpers."""

import os
import sys
import tempfile
import types

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld import osm_network


def synthetic_osm_graph():
    """Build a tiny OSM-like graph fixture without live OSM services."""

    graph = nx.MultiDiGraph()
    graph.add_node(1, x=127.10, y=37.50)
    graph.add_node(2, x=127.11, y=37.51)
    graph.add_edge(
        1,
        2,
        key=0,
        osmid=1001,
        length=250.5,
        highway=["primary", "secondary"],
        maxspeed="50",
        geometry=("placeholder", "not", "graphml-native"),
    )
    return graph


def test_module_import_and_offline_helpers_do_not_require_osmnx():
    """OSMnx should only be required for live extraction calls."""

    graph = osm_network.normalize_osm_graph(synthetic_osm_graph())
    assert graph.has_edge(1, 2, 0)
    assert graph.edges[1, 2, 0]["mode"] == "road"

    original_import_module = osm_network.importlib.import_module

    def fake_import_module(name):
        if name == "osmnx":
            raise ModuleNotFoundError("No module named 'osmnx'", name="osmnx")
        return original_import_module(name)

    osm_network.importlib.import_module = fake_import_module
    try:
        try:
            osm_network.extract_bbox_graph(
                north=37.52,
                south=37.50,
                east=127.12,
                west=127.10,
            )
        except RuntimeError as exc:
            assert "optional 'osmnx' package" in str(exc)
            assert "load_graphml" in str(exc)
        else:
            raise AssertionError("Missing OSMnx did not raise RuntimeError")
    finally:
        osm_network.importlib.import_module = original_import_module

    print("PASS: OSMnx import boundary")


def test_graphml_cache_helpers_work_offline_with_networkx():
    """GraphML save/load should work with only NetworkX and a fixture graph."""

    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "road.graphml")
        saved_path = osm_network.save_graphml(synthetic_osm_graph(), path)
        assert os.path.exists(saved_path)

        loaded = osm_network.load_graphml(saved_path, node_type=int)
        assert loaded.has_edge(1, 2, 0)
        assert loaded.nodes[1]["x"] == 127.10
        assert loaded.nodes[2]["y"] == 37.51
        assert loaded.edges[1, 2, 0]["length"] == 250.5

        normalized = osm_network.load_graphml(saved_path, node_type=int, normalize=True)
        data = normalized.edges[1, 2, 0]
        assert data["mode"] == "road"
        assert data["source"] == "osm"
        assert data["length_m"] == 250.5
        assert data["realworld_edge_id"] == "osm:1001"

    print("PASS: GraphML cache helpers")


def test_normalize_osm_graph_preserves_boundary_metadata():
    """Normalization should add metadata without simulator schema side effects."""

    graph = osm_network.normalize_osm_graph(synthetic_osm_graph())

    assert isinstance(graph, nx.MultiDiGraph)
    assert graph.graph["source"] == "osm"
    assert graph.graph["normalized_by"] == "src.realworld.osm_network"
    assert graph.nodes[1]["source"] == "osm"

    data = graph.edges[1, 2, 0]
    assert data["highway"] == "primary"
    assert data["length_m"] == 250.5
    assert data["mode"] == "road"
    assert "t0" not in data
    assert "capacity" not in data
    assert "base_p_fail" not in data

    print("PASS: OSM graph normalization")


def test_live_extraction_uses_lazy_osmnx_import_without_live_service():
    """A fake OSMnx module proves live extraction wiring without network calls."""

    calls = []

    def graph_from_bbox(bbox, **kwargs):
        calls.append((bbox, kwargs))
        return synthetic_osm_graph()

    fake_osmnx = types.SimpleNamespace(graph_from_bbox=graph_from_bbox)
    previous_osmnx = sys.modules.get("osmnx")
    sys.modules["osmnx"] = fake_osmnx
    try:
        graph = osm_network.extract_bbox_graph(
            north=37.52,
            south=37.50,
            east=127.12,
            west=127.10,
            network_type="drive",
            normalize=True,
        )
    finally:
        if previous_osmnx is None:
            sys.modules.pop("osmnx", None)
        else:
            sys.modules["osmnx"] = previous_osmnx

    assert calls
    assert calls[0][0] == (127.10, 37.50, 127.12, 37.52)
    assert calls[0][1]["network_type"] == "drive"
    assert graph.edges[1, 2, 0]["source"] == "osm"

    print("PASS: Lazy live extraction wiring")


def test_invalid_bbox_fails_before_osmnx_import():
    """Invalid live extraction inputs should fail clearly and offline."""

    try:
        osm_network.extract_bbox_graph(
            north=37.50,
            south=37.52,
            east=127.12,
            west=127.10,
        )
    except ValueError as exc:
        assert "north" in str(exc)
    else:
        raise AssertionError("Invalid bbox did not raise ValueError")

    print("PASS: Bbox validation")


if __name__ == "__main__":
    test_module_import_and_offline_helpers_do_not_require_osmnx()
    test_graphml_cache_helpers_work_offline_with_networkx()
    test_normalize_osm_graph_preserves_boundary_metadata()
    test_live_extraction_uses_lazy_osmnx_import_without_live_service()
    test_invalid_bbox_fails_before_osmnx_import()
    print("\n=== REALWORLD OSM NETWORK TESTS PASSED ===")
