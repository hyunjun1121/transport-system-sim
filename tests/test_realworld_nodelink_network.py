"""Direct-execution tests for the Korean 표준노드링크 network source."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.attributes import (  # noqa: E402
    DEFAULT_ROUTEABLE_HIGHWAY_CLASSES,
    HIGHWAY_DEFAULTS,
)
from src.realworld.claim_language_guard import RESERVED_TERM_PATTERNS  # noqa: E402
from src.realworld.nodelink_network import (  # noqa: E402
    DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK,
    MISSING_DATA_SENTINELS,
    NODELINK_OFFICIAL_LABEL,
    NODELINK_SOURCE_LABEL,
    NODELINK_SOURCE_WKT,
    ROAD_RANK_TO_HIGHWAY,
    filter_bbox_wgs84,
    is_missing_value,
    load_nodelink_graph,
    normalize_nodelink_graph,
    road_rank_to_highway,
)


def _geodata_available() -> bool:
    try:
        import pyproj  # noqa: F401
        import shapefile  # noqa: F401

        return True
    except ModuleNotFoundError:
        return False


def _skip_if_no_geodata() -> bool:
    if not _geodata_available():
        print("SKIP: pyshp/pyproj not installed (requirements-geodata.txt)")
        return True
    return False


# --- Tier 1: pure-Python contract (no geodata deps) -------------------------


def test_road_rank_to_highway_table_is_total_and_routeable() -> None:
    """Every ROAD_RANK must map to a known, routeable highway class."""

    for code, highway in ROAD_RANK_TO_HIGHWAY.items():
        assert highway in HIGHWAY_DEFAULTS, (code, highway)
        assert highway in DEFAULT_ROUTEABLE_HIGHWAY_CLASSES, (code, highway)
    assert DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK in HIGHWAY_DEFAULTS
    assert DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK in DEFAULT_ROUTEABLE_HIGHWAY_CLASSES

    # Unknown / blank / odd encodings fall back safely.
    assert road_rank_to_highway(999) == DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK
    assert road_rank_to_highway("") == DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK
    assert road_rank_to_highway(None) == DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK
    assert road_rank_to_highway("103") == "trunk"
    assert road_rank_to_highway("0103") == "trunk"
    assert road_rank_to_highway(" 101 ") == "motorway"
    assert road_rank_to_highway(105) == "primary"
    print("PASS: ROAD_RANK -> highway table is total and routeable")


def test_missing_sentinel_constants() -> None:
    """The -1 sentinel set covers the 표준노드링크 missing-data convention."""

    assert -1 in MISSING_DATA_SENTINELS
    assert "-1" in MISSING_DATA_SENTINELS
    assert is_missing_value(-1)
    assert is_missing_value("-1")
    assert is_missing_value("")
    assert is_missing_value(None)
    assert not is_missing_value(80)
    assert not is_missing_value("2")
    print("PASS: missing-data sentinel constants and helper")


def test_graph_source_labels_are_not_claim_terms() -> None:
    """Source labels must contain no reserved claim adjective."""

    for label in (NODELINK_SOURCE_LABEL, NODELINK_OFFICIAL_LABEL):
        for term, pattern in RESERVED_TERM_PATTERNS:
            assert pattern.search(label) is None, (term, label)
    print("PASS: nodelink source labels carry no reserved claim terms")


# --- Tier 2: needs pyshp/pyproj (skip when absent) --------------------------


def _write_node_shp(base: str, nodes: list[tuple[str, float, float]]) -> None:
    import shapefile

    writer = shapefile.Writer(base, shapeType=shapefile.POINT, encoding="cp949")
    writer.encodingErrors = "replace"
    writer.field("NODE_ID", "C", size=10)
    for node_id, easting, northing in nodes:
        writer.point(easting, northing)
        writer.record(NODE_ID=node_id)
    writer.close()


def _write_link_shp(
    base: str,
    links: list[dict],
) -> None:
    import shapefile

    writer = shapefile.Writer(base, shapeType=shapefile.POLYLINE, encoding="cp949")
    writer.encodingErrors = "replace"
    writer.field("LINK_ID", "C", size=10)
    writer.field("F_NODE", "C", size=10)
    writer.field("T_NODE", "C", size=10)
    writer.field("ROAD_RANK", "C", size=3)
    writer.field("MAX_SPD", "N", size=10)
    writer.field("LANES", "N", size=10)
    writer.field("LENGTH", "N", size=18, decimal=12)
    writer.field("ROAD_NO", "C", size=5)
    writer.field("ROAD_NAME", "C", size=30)
    for link in links:
        writer.line([[(link["fx"], link["fy"]), (link["tx"], link["ty"])]])
        writer.record(
            LINK_ID=link["LINK_ID"],
            F_NODE=link["F_NODE"],
            T_NODE=link["T_NODE"],
            ROAD_RANK=str(link["ROAD_RANK"]),
            MAX_SPD=link.get("MAX_SPD", -1),
            LANES=link.get("LANES", -1),
            LENGTH=link.get("LENGTH", 0.0),
            ROAD_NO=link.get("ROAD_NO", ""),
            ROAD_NAME=link.get("ROAD_NAME", ""),
        )
    writer.close()


def test_reprojection_5179_to_4326_known_point() -> None:
    """EPSG:5179 origin (200000, 600000) reprojects to ~ (lon 127, lat 38)."""

    if _skip_if_no_geodata():
        return
    import pyproj

    transformer = pyproj.Transformer.from_crs(
        pyproj.CRS.from_user_input(NODELINK_SOURCE_WKT), 4326, always_xy=True
    )
    lon, lat = transformer.transform(200000.0, 600000.0)
    assert abs(lon - 127.0) < 5e-4, (lon, lat)
    assert abs(lat - 38.0) < 5e-4, (lon, lat)
    print("PASS: 표준노드링크 CRS origin reprojects to (127.0, 38.0)")


def test_load_nodelink_graph_from_synthetic_shp() -> None:
    """A synthetic 1-link/2-node SHP builds a directed graph with the edge contract."""

    if _skip_if_no_geodata():
        return
    with TemporaryDirectory() as tmp:
        node_base = str(Path(tmp) / "MOCT_NODE")
        link_base = str(Path(tmp) / "MOCT_LINK")
        _write_node_shp(
            node_base,
            [
                ("10", 200000.0, 600000.0),
                ("20", 201000.0, 600000.0),
            ],
        )
        _write_link_shp(
            link_base,
            [
                {
                    "LINK_ID": "1",
                    "F_NODE": "10",
                    "T_NODE": "20",
                    "ROAD_RANK": 103,
                    "MAX_SPD": 80,
                    "LANES": 2,
                    "LENGTH": 1234.5,
                    "ROAD_NO": "6",
                    "ROAD_NAME": "테스트국도",
                    "fx": 200000.0, "fy": 600000.0,
                    "tx": 201000.0, "ty": 600000.0,
                }
            ],
        )
        graph = load_nodelink_graph(
            link_shp_path=link_base + ".shp",
            node_shp_path=node_base + ".shp",
        )

    assert graph.number_of_nodes() == 2
    assert graph.has_edge("10", "20")
    assert not graph.has_edge("20", "10")  # directed F_NODE -> T_NODE only
    edge = graph.get_edge_data("10", "20")[0]
    assert edge["highway"] == "trunk"
    assert abs(edge["length_m"] - 1234.5) < 1e-6
    assert abs(edge["length"] - 1234.5) < 1e-6
    assert edge["maxspeed"] == 80
    assert edge["lanes"] == 2
    assert edge["mode"] == "road"
    assert edge["source"] == NODELINK_SOURCE_LABEL
    assert edge["realworld_edge_id"] == "kn:1"
    assert edge["road_name"] == "테스트국도"
    node = graph.nodes["10"]
    assert isinstance(node["x"], float) and isinstance(node["y"], float)
    assert 33.0 <= node["y"] <= 39.0 and 124.0 <= node["x"] <= 132.0
    print("PASS: load_nodelink_graph builds directed graph with edge contract")


def test_load_nodelink_graph_handles_minus_one_sentinels() -> None:
    """MAX_SPD/LANES = -1 must not leak into edge attributes."""

    if _skip_if_no_geodata():
        return
    with TemporaryDirectory() as tmp:
        node_base = str(Path(tmp) / "MOCT_NODE")
        link_base = str(Path(tmp) / "MOCT_LINK")
        _write_node_shp(node_base, [("10", 200000.0, 600000.0), ("20", 201000.0, 600000.0)])
        _write_link_shp(
            link_base,
            [
                {
                    "LINK_ID": "1",
                    "F_NODE": "10",
                    "T_NODE": "20",
                    "ROAD_RANK": 103,
                    "MAX_SPD": -1,
                    "LANES": -1,
                    "LENGTH": 500.0,
                    "fx": 200000.0, "fy": 600000.0,
                    "tx": 201000.0, "ty": 600000.0,
                }
            ],
        )
        graph = load_nodelink_graph(
            link_shp_path=link_base + ".shp", node_shp_path=node_base + ".shp"
        )

    edge = graph.get_edge_data("10", "20")[0]
    assert "maxspeed" not in edge
    assert "lanes" not in edge
    assert edge["length_m"] == 500.0
    print("PASS: load_nodelink_graph drops -1 sentinels from edge attributes")


def test_load_nodelink_graph_bidirectional_adds_reverse() -> None:
    """bidirectional=True adds a T_NODE->F_NODE reverse edge per link."""

    if _skip_if_no_geodata():
        return
    with TemporaryDirectory() as tmp:
        node_base = str(Path(tmp) / "MOCT_NODE")
        link_base = str(Path(tmp) / "MOCT_LINK")
        _write_node_shp(node_base, [("10", 200000.0, 600000.0), ("20", 201000.0, 600000.0)])
        _write_link_shp(
            link_base,
            [
                {"LINK_ID": "1", "F_NODE": "10", "T_NODE": "20", "ROAD_RANK": 103,
                 "LENGTH": 1000.0, "fx": 200000.0, "fy": 600000.0, "tx": 201000.0, "ty": 600000.0}
            ],
        )
        graph = load_nodelink_graph(
            link_shp_path=link_base + ".shp", node_shp_path=node_base + ".shp",
            bidirectional=True,
        )

    assert graph.has_edge("10", "20") and graph.has_edge("20", "10")
    forward = graph.get_edge_data("10", "20")[0]
    reverse = graph.get_edge_data("20", "10")[0]
    assert forward["realworld_edge_id"] == "kn:1"
    assert reverse["realworld_edge_id"] == "kn:1r"
    print("PASS: bidirectional=True adds a reverse edge with a distinct id")


def test_load_nodelink_graph_bbox_filter() -> None:
    """corridor_bbox keeps only the in-envelope link and its two nodes."""

    if _skip_if_no_geodata():
        return
    with TemporaryDirectory() as tmp:
        node_base = str(Path(tmp) / "MOCT_NODE")
        link_base = str(Path(tmp) / "MOCT_LINK")
        # Three widely-spaced node pairs along latitude 38 (~ northing 600000).
        _write_node_shp(
            node_base,
            [
                ("1", 200000.0, 600000.0),  # ~ lon 127.0
                ("2", 201000.0, 600000.0),
                ("3", 300000.0, 600000.0),  # ~ lon 128.x  (middle)
                ("4", 301000.0, 600000.0),
                ("5", 400000.0, 600000.0),  # ~ lon 129.x
                ("6", 401000.0, 600000.0),
            ],
        )
        _write_link_shp(
            link_base,
            [
                {"LINK_ID": "A", "F_NODE": "1", "T_NODE": "2", "ROAD_RANK": 3,
                 "LENGTH": 1000.0, "fx": 200000.0, "fy": 600000.0, "tx": 201000.0, "ty": 600000.0},
                {"LINK_ID": "B", "F_NODE": "3", "T_NODE": "4", "ROAD_RANK": 3,
                 "LENGTH": 1000.0, "fx": 300000.0, "fy": 600000.0, "tx": 301000.0, "ty": 600000.0},
                {"LINK_ID": "C", "F_NODE": "5", "T_NODE": "6", "ROAD_RANK": 3,
                 "LENGTH": 1000.0, "fx": 400000.0, "fy": 600000.0, "tx": 401000.0, "ty": 600000.0},
            ],
        )
        graph = load_nodelink_graph(
            link_shp_path=link_base + ".shp",
            node_shp_path=node_base + ".shp",
            corridor_bbox=(37.9, 128.0, 38.1, 128.5),
        )

    assert graph.number_of_edges() == 1
    assert graph.has_edge("3", "4")
    assert graph.number_of_nodes() == 2
    print("PASS: corridor_bbox filter keeps only the in-envelope link + nodes")


def test_normalize_nodelink_graph_sets_source_metadata() -> None:
    """normalize sets source metadata and coerces x/y/length_m to float."""

    if _skip_if_no_geodata():
        return
    import networkx as nx

    raw = nx.MultiDiGraph()
    raw.add_node("10", x="127.0", y="38.0", source=NODELINK_SOURCE_LABEL)
    raw.add_edge("10", "10", key=0, highway="TRUNK", length_m="1234.5", mode="road")
    normalized = normalize_nodelink_graph(raw)

    assert normalized.graph["source"] == NODELINK_SOURCE_LABEL
    assert normalized.graph["normalized_by"] == "src.realworld.nodelink_network"
    assert isinstance(normalized.nodes["10"]["x"], float)
    edge = normalized.get_edge_data("10", "10")[0]
    assert edge["highway"] == "trunk"
    assert isinstance(edge["length_m"], float)
    print("PASS: normalize_nodelink_graph sets source metadata and coerces types")


def test_filter_bbox_wgs84_induces_subgraph() -> None:
    """filter_bbox_wgs84 keeps only nodes inside the bbox and their internal edges."""

    if _skip_if_no_geodata():
        return
    import networkx as nx

    graph = nx.MultiDiGraph()
    graph.add_node("a", x=127.0, y=38.0)
    graph.add_node("b", x=127.01, y=38.0)
    graph.add_node("c", x=129.0, y=38.0)
    graph.add_edge("a", "b", key=0, mode="road")
    graph.add_edge("b", "c", key=0, mode="road")
    sub = filter_bbox_wgs84(graph, 37.9, 126.9, 38.1, 127.5)

    assert set(sub.nodes()) == {"a", "b"}
    assert sub.has_edge("a", "b")
    assert not sub.has_edge("b", "c")
    print("PASS: filter_bbox_wgs84 induces the in-bbox subgraph")


if __name__ == "__main__":
    test_road_rank_to_highway_table_is_total_and_routeable()
    test_missing_sentinel_constants()
    test_graph_source_labels_are_not_claim_terms()
    test_reprojection_5179_to_4326_known_point()
    test_load_nodelink_graph_from_synthetic_shp()
    test_load_nodelink_graph_handles_minus_one_sentinels()
    test_load_nodelink_graph_bidirectional_adds_reverse()
    test_load_nodelink_graph_bbox_filter()
    test_normalize_nodelink_graph_sets_source_metadata()
    test_filter_bbox_wgs84_induces_subgraph()
    print("\n=== NODELINK NETWORK TESTS PASSED ===")
