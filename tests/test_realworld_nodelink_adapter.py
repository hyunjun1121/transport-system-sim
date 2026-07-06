"""Direct-execution integration tests: 표준노드링크 graph -> simulator adapter.

These prove the OSM-named adapter/mapper are genuinely source-agnostic for the
Korean official source: a MultiDiGraph shaped like ``load_nodelink_graph`` output
flows through ``build_simulator_graph`` and ``assert_graph_ready`` unchanged, the
VDS override fragment applies to motorway edges only, and the OSM normalizer
preserves the ``korean_nodelink`` source label (the fact that makes the runner
source-agnostic without code changes).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import networkx as nx
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.adapter import build_simulator_graph  # noqa: E402
from src.realworld.attributes import HIGHWAY_DEFAULTS  # noqa: E402
from src.realworld.nodelink_network import NODELINK_SOURCE_LABEL  # noqa: E402
from src.realworld.osm_network import load_graphml, save_graphml  # noqa: E402
from src.realworld.road_overrides import build_highway_defaults_with_overrides  # noqa: E402
from src.realworld.validation import assert_graph_ready, REQUIRED_EDGE_FIELDS  # noqa: E402
from src.realworld.vds_calibration import (  # noqa: E402
    aggregate_vds_by_class,
    vds_observations_to_override_rows,
)
from src.realworld.road_overrides import load_road_class_overrides, build_road_class_override_metadata  # noqa: E402


FIXTURE_REGION = (
    Path(__file__).resolve().parent / "fixtures" / "synthetic_region_fixture.yaml"
)


def _region_mapping() -> dict:
    return yaml.safe_load(FIXTURE_REGION.read_text(encoding="utf-8"))


def _grid_road_graph() -> nx.MultiDiGraph:
    """A connected WGS84 grid in the synthetic-fixture bbox, shaped like nodelink output."""

    graph = nx.MultiDiGraph()
    graph.graph["source"] = NODELINK_SOURCE_LABEL
    lons = [127.005, 127.015, 127.025, 127.035]
    lats = [37.005, 37.020, 37.030]
    nodes = {}
    for lat in lats:
        for lon in lons:
            node_id = f"{lon:.3f}_{lat:.3f}"
            nodes[(lon, lat)] = node_id
            graph.add_node(
                node_id,
                x=float(lon),
                y=float(lat),
                node_id=node_id,
                source=NODELINK_SOURCE_LABEL,
            )

    edge_index = 0

    def _link(a, b):
        nonlocal edge_index
        edge_index += 1
        attrs = {
            "highway": "primary",
            "mode": "road",
            "source": NODELINK_SOURCE_LABEL,
            "realworld_edge_id": f"kn:{edge_index}",
            "length": 1000.0,
            "length_m": 1000.0,
        }
        graph.add_edge(a, b, **attrs)
        graph.add_edge(b, a, **{**attrs, "realworld_edge_id": f"kn:{edge_index}r"})

    for r, lat in enumerate(lats):
        for c, lon in enumerate(lons):
            if c + 1 < len(lons):
                _link(nodes[(lon, lat)], nodes[(lons[c + 1], lat)])
            if r + 1 < len(lats):
                _link(nodes[(lon, lat)], nodes[(lon, lats[r + 1])])
    return graph


def test_build_simulator_graph_consumes_nodelink_multidigraph() -> None:
    """A nodelink-shaped graph maps to simulator edges and connects the required routes."""

    simulator = build_simulator_graph(_grid_road_graph(), _region_mapping())
    for _, _, data in simulator.edges(data=True):
        for field in REQUIRED_EDGE_FIELDS:
            assert field in data, (field, data)
    for source, target in (("A", "D"), ("A", "S"), ("R", "D")):
        assert nx.has_path(simulator, source, target), (source, target)
    assert simulator.graph["source"] == NODELINK_SOURCE_LABEL
    print("PASS: build_simulator_graph consumes a nodelink MultiDiGraph")


def test_assert_graph_ready_passes_on_nodelink_simulator_graph() -> None:
    """The nodelink-derived simulator graph passes the readiness guard."""

    simulator = build_simulator_graph(_grid_road_graph(), _region_mapping())
    assert_graph_ready(
        simulator,
        required_nodes=("A", "D", "S", "R"),
        required_routes=(("A", "D"), ("A", "S"), ("R", "D")),
    )
    print("PASS: assert_graph_ready passes on the nodelink simulator graph")


def test_vds_override_fragment_applies_to_motorway_edges_only() -> None:
    """VDS-derived motorway defaults override motorway edges and leave others untouched."""

    rows = aggregate_vds_by_class(
        [{"노선번호": "0500", "도로명": "영동선", "VDS_ID": "A", "교통량": 100, "평균속도": 95.0}]
    )
    override_rows = vds_observations_to_override_rows(rows)
    with TemporaryDirectory() as tmp:
        fragment = Path(tmp) / "vds.csv"
        from src.realworld.vds_calibration import write_vds_override_csv

        write_vds_override_csv(override_rows, fragment)
        overrides = load_road_class_overrides(fragment)
    merged = build_highway_defaults_with_overrides(overrides)
    metadata = build_road_class_override_metadata(overrides)

    graph = nx.MultiDiGraph()
    graph.graph["source"] = NODELINK_SOURCE_LABEL
    for node_id, lon, lat in (("m1", 127.010, 37.010), ("m2", 127.020, 37.010),
                              ("r1", 127.010, 37.020), ("r2", 127.020, 37.020)):
        graph.add_node(node_id, x=lon, y=lat, node_id=node_id, source=NODELINK_SOURCE_LABEL)
    graph.add_edge("m1", "m2", highway="motorway", mode="road", source=NODELINK_SOURCE_LABEL,
                   realworld_edge_id="kn:m", length=1000.0, length_m=1000.0)
    graph.add_edge("r1", "r2", highway="residential", mode="road", source=NODELINK_SOURCE_LABEL,
                   realworld_edge_id="kn:r", length=500.0, length_m=500.0)

    simulator = build_simulator_graph(
        graph, _region_mapping(), highway_defaults=merged,
        road_class_override_metadata=metadata, validate_routes=False,
    )

    motorway_edges = [
        data for _, _, data in simulator.edges(data=True) if data.get("highway") == "motorway"
    ]
    residential_edges = [
        data for _, _, data in simulator.edges(data=True) if data.get("highway") == "residential"
    ]
    assert motorway_edges and all(edge["speed_kph"] == 95.0 for edge in motorway_edges)
    assert residential_edges
    assert all(
        edge["speed_kph"] == HIGHWAY_DEFAULTS["residential"].speed_kph
        for edge in residential_edges
    )
    assert all(edge.get("road_class_override_applied") for edge in motorway_edges)
    assert all(not edge.get("road_class_override_applied") for edge in residential_edges)
    print("PASS: VDS override fragment applies to motorway edges only")


def test_osm_normalize_preserves_nodelink_source() -> None:
    """load_graphml(normalize=True) preserves a pre-existing korean_nodelink source."""

    graph = nx.MultiDiGraph()
    graph.graph["source"] = NODELINK_SOURCE_LABEL
    graph.add_node("n1", x=127.01, y=37.01, source=NODELINK_SOURCE_LABEL)
    graph.add_edge(
        "n1", "n2", key=0, highway="trunk", mode="road", source=NODELINK_SOURCE_LABEL,
        realworld_edge_id="kn:1", length=1000.0, length_m=1000.0,
    )
    graph.add_node("n2", x=127.02, y=37.01, source=NODELINK_SOURCE_LABEL)

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "cache.graphml"
        save_graphml(graph, path)
        loaded = load_graphml(path, normalize=True)

    assert loaded.graph["source"] == NODELINK_SOURCE_LABEL
    assert loaded.nodes["n1"]["source"] == NODELINK_SOURCE_LABEL
    edge = loaded.get_edge_data("n1", "n2")[0]
    assert edge["source"] == NODELINK_SOURCE_LABEL
    assert edge["realworld_edge_id"] == "kn:1"
    print("PASS: OSM normalizer preserves the korean_nodelink source label")


if __name__ == "__main__":
    test_build_simulator_graph_consumes_nodelink_multidigraph()
    test_assert_graph_ready_passes_on_nodelink_simulator_graph()
    test_vds_override_fragment_applies_to_motorway_edges_only()
    test_osm_normalize_preserves_nodelink_source()
    print("\n=== NODELINK ADAPTER INTEGRATION TESTS PASSED ===")
