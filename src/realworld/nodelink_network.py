"""Korean official road-network source: 표준노드링크 (Standard Node-Link).

Reads the MOCT_LINK / MOCT_NODE ESRI shapefiles (EPSG:5179, CP949 DBF), reprojects
to WGS84 (EPSG:4326), and builds a directed MultiDiGraph in the same edge contract
the OSM adapter consumes: nodes carry ``x``/``y`` lon/lat; edges carry ``highway`` /
``length`` / ``maxspeed`` / ``mode`` / ``source`` / ``realworld_edge_id``. The
resulting graph feeds ``build_simulator_graph()`` unchanged via the runner's
``--cache-path`` (the OSM normalizer preserves a pre-existing ``source``).

The geodata deps (pyshp, pyproj) are lazily imported inside functions and are
OPTIONAL: importing this module never requires them, and callers without
requirements-geodata.txt get a clear RuntimeError only when they actually read
shapefiles. This is a DECISION-SUPPORT quasi-real source, not a calibrated or
validated network. final_study_ready=false.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx

from src.realworld.attributes import (
    DEFAULT_ROUTEABLE_HIGHWAY_CLASSES,
    HIGHWAY_DEFAULTS,
)


NODELINK_SOURCE_LABEL = "korean_nodelink"
NODELINK_OFFICIAL_LABEL = "korean_nodelink_official"

# Authoritative CRS for the downloaded 표준노드링크 data, taken verbatim from the
# shipped MOCT_LINK/MOCT_NODE .prj (ITRF2000 Central Belt 60: TM, central meridian
# 127, false easting 200000, false northing 600000, lat-of-origin 38). The EPSG
# code 5179 in pyproj does NOT match this .prj (its false-northing differs), so the
# WKT is used directly. The origin (200000, 600000) reprojections to (lon 127.0,
# lat 38.0), which the reprojection test pins.
NODELINK_SOURCE_WKT = (
    'PROJCS["ITRF2000_Central_Belt_60",'
    'GEOGCS["GCS_ITRF_2000",'
    'DATUM["D_ITRF_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],'
    'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],'
    'PROJECTION["Transverse_Mercator"],'
    'PARAMETER["False_Easting",200000.0],'
    'PARAMETER["False_Northing",600000.0],'
    'PARAMETER["Central_Meridian",127.0],'
    'PARAMETER["Scale_Factor",1.0],'
    'PARAMETER["Latitude_Of_Origin",38.0],'
    'UNIT["Meter",1.0]]'
)

# Korean 표준노드링크 ROAD_RANK code -> OSM highway class. Pinned against the
# REAL national DBF (the Goseong build logged codes 101-107 exclusively; the
# single-digit 1-8 form is NOT used by this dataset). Codes per the MOLIT
# 표준노드링크 attribute dictionary:
#   101 고속국도 / 102 도시고속도로 / 103 일반국도 / 104 특별광역시도 /
#   105 지방도 / 106 시군도 / 107 읍면도 / 108 이면도.
ROAD_RANK_TO_HIGHWAY: dict[int, str] = {
    101: "motorway",    # 고속국도 (expressway)
    102: "motorway",    # 도시고속도로 (urban expressway)
    103: "trunk",       # 일반국도 (national route)
    104: "trunk",       # 특별광역시도 (metropolitan special route)
    105: "primary",     # 지방도 (provincial road)
    106: "secondary",   # 시군도 (city/county road)
    107: "tertiary",    # 읍면도 (town road)
    108: "residential", # 이면도 (local street)
}
DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK = "road"

# 표준노드링크 uses -1 for missing numeric attributes (MAX_SPD / LANES).
MISSING_DATA_SENTINELS = (-1, "-1")

# Corridor envelope (WGS84 south, west, north, east) covering Songpa assembly,
# Cheongnyangni rail access, Gangneung rail egress, and Goseong destination.
DEFAULT_CORRIDOR_BBOX = (37.0, 126.6, 38.9, 129.2)


def road_rank_to_highway(rank_value: Any) -> str:
    """Map a 표준노드링크 ROAD_RANK value to an OSM highway class."""

    if rank_value is None:
        return DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK
    text = str(rank_value).strip()
    if text == "":
        return DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK
    try:
        code = int(float(text))
    except ValueError:
        return DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK
    return ROAD_RANK_TO_HIGHWAY.get(code, DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK)


def is_missing_value(value: Any) -> bool:
    """Return true when a 표준노드링크 cell is a -1 sentinel or blank."""

    if value is None:
        return True
    text = str(value).strip()
    if text == "":
        return True
    try:
        return float(text) < 0
    except ValueError:
        return False


def _import_geodata():
    try:
        import shapefile  # type: ignore
        import pyproj  # type: ignore

        return shapefile, pyproj
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Reading 표준노드링크 shapefiles requires the optional geodata deps. "
            "Install them: .\\.venv\\Scripts\\python -m pip install -r "
            "requirements-geodata.txt"
        ) from exc


def _iter_edges(graph: nx.Graph):
    if graph.is_multigraph():
        yield from graph.edges(keys=True, data=True)
        return
    for u, v, data in graph.edges(data=True):
        yield u, v, 0, data


def _in_bbox(lon: Any, lat: Any, south: float, west: float, north: float, east: float) -> bool:
    try:
        x = float(lon)
        y = float(lat)
    except (TypeError, ValueError):
        return False
    return south <= y <= north and west <= x <= east


def _build_edge_attrs(attrs: dict[str, Any], link_id: str, source_label: str) -> dict[str, Any]:
    edge: dict[str, Any] = {
        "mode": "road",
        "source": source_label,
        "realworld_edge_id": f"kn:{link_id}",
        "highway": road_rank_to_highway(attrs.get("ROAD_RANK")),
    }

    length = attrs.get("LENGTH")
    if not is_missing_value(length):
        try:
            edge["length"] = float(length)
            edge["length_m"] = float(length)
        except (TypeError, ValueError):
            pass

    max_spd = attrs.get("MAX_SPD")
    if not is_missing_value(max_spd):
        try:
            edge["maxspeed"] = float(max_spd)
        except (TypeError, ValueError):
            pass

    lanes = attrs.get("LANES")
    if not is_missing_value(lanes):
        try:
            edge["lanes"] = int(float(lanes))
        except (TypeError, ValueError):
            pass

    road_no = attrs.get("ROAD_NO")
    if road_no is not None and str(road_no).strip():
        edge["road_no"] = str(road_no).strip()
    road_name = attrs.get("ROAD_NAME")
    if road_name is not None and str(road_name).strip():
        edge["road_name"] = str(road_name).strip()
    rank = attrs.get("ROAD_RANK")
    if rank is not None and str(rank).strip():
        edge["road_rank"] = str(rank).strip()

    return edge


def load_nodelink_graph(
    *,
    link_shp_path: str | Path,
    node_shp_path: str | Path,
    corridor_bbox: tuple[float, float, float, float] | None = None,
    source_crs: str = NODELINK_SOURCE_WKT,
    target_epsg: int = 4326,
    source_label: str = NODELINK_SOURCE_LABEL,
    bidirectional: bool = False,
) -> nx.MultiDiGraph:
    """Read MOCT_LINK/MOCT_NODE SHP -> directed WGS84 MultiDiGraph.

    ``corridor_bbox`` is ``(south, west, north, east)`` in WGS84. When given, nodes
    whose reprojected coordinate falls outside are dropped and only links whose both
    endpoints survive are kept (filter-while-reading, so the in-memory graph is
    corridor-scale, not national). ``source_crs`` is the 표준노드링크 CRS as WKT
    (the shipped .prj); pass an EPSG code or other WKT to override.

    ``bidirectional``: this export uses one link per physical segment (only ~0.1% of
    links carry a matching reverse link), so pure F_NODE->T_NODE routing is
    unreliable for bidirectional bus traversal. When True, a reverse edge
    T_NODE->F_NODE is added per link (with a distinct realworld_edge_id). The build
    script enables this for routing; the loader default stays False to preserve the
    pure directed semantics the unit tests assert.
    """

    shapefile, pyproj = _import_geodata()
    transformer = pyproj.Transformer.from_crs(
        pyproj.CRS.from_user_input(source_crs), target_epsg, always_xy=True
    )

    south = west = north = east = None
    if corridor_bbox is not None:
        south, west, north, east = corridor_bbox

    graph = nx.MultiDiGraph()
    graph.graph["source"] = source_label
    graph.graph["source_network"] = source_label
    graph.graph["source_crs"] = source_crs
    graph.graph["target_epsg"] = target_epsg

    kept_nodes: dict[str, tuple[float, float]] = {}
    with shapefile.Reader(str(node_shp_path), encoding="cp949") as reader:
        for shape_record in reader.shapeRecords():
            attrs = shape_record.record.as_dict()
            node_id = str(attrs.get("NODE_ID", "")).strip()
            if not node_id:
                continue
            points = shape_record.shape.points
            if not points:
                continue
            easting, northing = points[0]
            lon, lat = transformer.transform(easting, northing)
            if corridor_bbox is not None and not _in_bbox(lon, lat, south, west, north, east):
                continue
            kept_nodes[node_id] = (float(lon), float(lat))
            graph.add_node(
                node_id,
                x=float(lon),
                y=float(lat),
                node_id=node_id,
                source=source_label,
            )

    rank_histogram: dict[str, int] = {}
    with shapefile.Reader(str(link_shp_path), encoding="cp949") as reader:
        for shape_record in reader.shapeRecords():
            attrs = shape_record.record.as_dict()
            link_id = str(attrs.get("LINK_ID", "")).strip()
            f_node = str(attrs.get("F_NODE", "")).strip()
            t_node = str(attrs.get("T_NODE", "")).strip()
            rank_raw = str(attrs.get("ROAD_RANK", "")).strip()
            rank_histogram[rank_raw] = rank_histogram.get(rank_raw, 0) + 1
            if not f_node or not t_node:
                continue
            if f_node not in kept_nodes or t_node not in kept_nodes:
                continue
            edge_attrs = _build_edge_attrs(attrs, link_id, source_label)
            graph.add_edge(f_node, t_node, **edge_attrs)
            if bidirectional:
                reverse_attrs = dict(edge_attrs)
                reverse_attrs["realworld_edge_id"] = edge_attrs["realworld_edge_id"] + "r"
                graph.add_edge(t_node, f_node, **reverse_attrs)

    graph.graph["road_rank_histogram"] = dict(sorted(rank_histogram.items()))
    graph.graph["nodelink_node_count"] = graph.number_of_nodes()
    graph.graph["nodelink_edge_count"] = graph.number_of_edges()
    return graph


def normalize_nodelink_graph(graph: nx.Graph) -> nx.MultiDiGraph:
    """Return a normalized copy: coerced x/y/length_m floats, metadata set."""

    normalized = nx.MultiDiGraph()
    normalized.graph.update(graph.graph)
    normalized.graph.setdefault("source", NODELINK_SOURCE_LABEL)
    normalized.graph["normalized_by"] = "src.realworld.nodelink_network"

    for node, data in graph.nodes(data=True):
        attrs = dict(data)
        for key in ("x", "y"):
            if key in attrs:
                try:
                    attrs[key] = float(attrs[key])
                except (TypeError, ValueError):
                    pass
        normalized.add_node(node, **attrs)

    for u, v, key, data in _iter_edges(graph):
        attrs = dict(data)
        if "length_m" in attrs:
            try:
                attrs["length_m"] = float(attrs["length_m"])
            except (TypeError, ValueError):
                pass
        if isinstance(attrs.get("highway"), str):
            attrs["highway"] = attrs["highway"].lower()
        normalized.add_edge(u, v, key=key, **attrs)

    return normalized


def filter_bbox_wgs84(
    graph: nx.Graph,
    south: float,
    west: float,
    north: float,
    east: float,
) -> nx.MultiDiGraph:
    """Return the subgraph induced by nodes inside the WGS84 bbox."""

    keep = {
        node
        for node, data in graph.nodes(data=True)
        if _in_bbox(data.get("x"), data.get("y"), south, west, north, east)
    }
    sub = nx.MultiDiGraph()
    sub.graph.update(graph.graph)
    for node in keep:
        sub.add_node(node, **graph.nodes[node])
    for u, v, key, data in _iter_edges(graph):
        if u in keep and v in keep:
            sub.add_edge(u, v, key=key, **data)
    return sub


__all__ = [
    "NODELINK_SOURCE_LABEL",
    "NODELINK_OFFICIAL_LABEL",
    "ROAD_RANK_TO_HIGHWAY",
    "DEFAULT_HIGHWAY_FOR_UNKNOWN_RANK",
    "DEFAULT_CORRIDOR_BBOX",
    "MISSING_DATA_SENTINELS",
    "road_rank_to_highway",
    "is_missing_value",
    "load_nodelink_graph",
    "normalize_nodelink_graph",
    "filter_bbox_wgs84",
]
