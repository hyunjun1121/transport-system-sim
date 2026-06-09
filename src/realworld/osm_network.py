"""Optional OSM road-network extraction and GraphML cache helpers.

This module deliberately keeps OSMnx behind a lazy import boundary. Offline
callers can save, load, and normalize NetworkX graphs without installing OSMnx
or contacting live OSM/Overpass services.
"""

from __future__ import annotations

import importlib
import inspect
import math
from pathlib import Path
from typing import Any

import networkx as nx


OSMNX_INSTALL_HINT = (
    "Live OSM extraction requires the optional 'osmnx' package. Install it in "
    "the project environment, for example: .\\.venv\\Scripts\\python -m pip "
    "install osmnx. For offline runs, use load_graphml(...) with a cached graph."
)


def save_graphml(graph: nx.Graph, path: str | Path) -> Path:
    """Save a NetworkX graph as GraphML without requiring OSMnx.

    GraphML does not support arbitrary Python objects, so non-scalar attribute
    values are stringified in a copied graph before writing. The input graph is
    not mutated.
    """

    filepath = Path(path)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(_graphml_safe_copy(graph), filepath, encoding="utf-8")
    return filepath


def load_graphml(
    path: str | Path,
    *,
    node_type: type | None = None,
    force_multigraph: bool = True,
    normalize: bool = False,
) -> nx.Graph:
    """Load a GraphML cache with NetworkX and optionally normalize it.

    Parameters
    ----------
    path
        GraphML file path.
    node_type
        Optional node-id converter such as ``int`` for OSMnx-style node IDs.
        NetworkX defaults to string node IDs when this is omitted.
    force_multigraph
        If true, return a MultiGraph/MultiDiGraph-compatible object even when
        the file has no parallel edges.
    normalize
        If true, return ``normalize_osm_graph(...)`` of the loaded graph.
    """

    kwargs: dict[str, Any] = {"force_multigraph": force_multigraph}
    if node_type is not None:
        kwargs["node_type"] = node_type

    graph = nx.read_graphml(Path(path), **kwargs)
    graph = _coerce_common_graphml_types(graph)
    if normalize:
        return normalize_osm_graph(graph)
    return graph


def extract_bbox_graph(
    *,
    north: float,
    south: float,
    east: float,
    west: float,
    network_type: str = "drive",
    simplify: bool = True,
    retain_all: bool = False,
    truncate_by_edge: bool = False,
    custom_filter: str | list[str] | None = None,
    cache_path: str | Path | None = None,
    normalize: bool = True,
) -> nx.Graph:
    """Extract a live OSM graph for a bounding box via OSMnx.

    OSMnx is imported only inside this function. If it is unavailable, a clear
    ``RuntimeError`` is raised here rather than during module import.
    """

    _validate_bbox(north=north, south=south, east=east, west=west)
    osmnx = _import_osmnx()
    raw_graph = _call_osmnx_graph_from_bbox(
        osmnx,
        north=north,
        south=south,
        east=east,
        west=west,
        network_type=network_type,
        simplify=simplify,
        retain_all=retain_all,
        truncate_by_edge=truncate_by_edge,
        custom_filter=custom_filter,
    )
    graph = normalize_osm_graph(raw_graph) if normalize else raw_graph
    if cache_path is not None:
        save_graphml(graph, cache_path)
    return graph


def load_or_extract_bbox_graph(
    cache_path: str | Path,
    *,
    north: float,
    south: float,
    east: float,
    west: float,
    network_type: str = "drive",
    simplify: bool = True,
    retain_all: bool = False,
    truncate_by_edge: bool = False,
    custom_filter: str | list[str] | None = None,
    overwrite: bool = False,
    node_type: type | None = None,
    normalize: bool = True,
) -> nx.Graph:
    """Load an existing GraphML cache or extract and cache a live OSM graph."""

    filepath = Path(cache_path)
    if filepath.exists() and not overwrite:
        return load_graphml(filepath, node_type=node_type, normalize=normalize)

    return extract_bbox_graph(
        north=north,
        south=south,
        east=east,
        west=west,
        network_type=network_type,
        simplify=simplify,
        retain_all=retain_all,
        truncate_by_edge=truncate_by_edge,
        custom_filter=custom_filter,
        cache_path=filepath,
        normalize=normalize,
    )


def normalize_osm_graph(graph: nx.Graph) -> nx.MultiDiGraph:
    """Return a normalized OSM-like road graph copy.

    This is intentionally limited to OSM/cache boundary metadata. It does not
    assign simulator fields such as ``t0`` or ``capacity`` because those belong
    to the attribute-mapping and adapter layers.
    """

    normalized = nx.MultiDiGraph()
    normalized.graph.update(graph.graph)
    normalized.graph.setdefault("source", "osm")
    normalized.graph["normalized_by"] = "src.realworld.osm_network"

    for node, data in graph.nodes(data=True):
        normalized.add_node(node, **_normalize_node_attrs(data))

    for u, v, key, data in _iter_edges_with_keys(graph):
        edge_data = _normalize_edge_attrs(u, v, key, data)
        normalized.add_edge(u, v, key=key, **edge_data)

    return normalized


def _import_osmnx() -> Any:
    try:
        return importlib.import_module("osmnx")
    except ModuleNotFoundError as exc:
        if exc.name == "osmnx":
            raise RuntimeError(OSMNX_INSTALL_HINT) from exc
        raise


def _call_osmnx_graph_from_bbox(
    osmnx: Any,
    *,
    north: float,
    south: float,
    east: float,
    west: float,
    network_type: str,
    simplify: bool,
    retain_all: bool,
    truncate_by_edge: bool,
    custom_filter: str | list[str] | None,
) -> nx.Graph:
    graph_from_bbox = getattr(osmnx, "graph_from_bbox", None)
    if graph_from_bbox is None:
        graph_module = getattr(osmnx, "graph", None)
        graph_from_bbox = getattr(graph_module, "graph_from_bbox", None)
    if graph_from_bbox is None:
        raise RuntimeError("The installed osmnx package does not expose graph_from_bbox.")

    kwargs = {
        "network_type": network_type,
        "simplify": simplify,
        "retain_all": retain_all,
        "truncate_by_edge": truncate_by_edge,
        "custom_filter": custom_filter,
    }

    try:
        parameters = inspect.signature(graph_from_bbox).parameters
    except (TypeError, ValueError):
        parameters = {}

    if "bbox" in parameters:
        bbox = (west, south, east, north)
        return graph_from_bbox(bbox, **kwargs)
    return graph_from_bbox(north, south, east, west, **kwargs)


def _validate_bbox(*, north: float, south: float, east: float, west: float) -> None:
    values = {"north": north, "south": south, "east": east, "west": west}
    for name, value in values.items():
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"Bounding-box coordinate {name!r} must be finite.")
    if north <= south:
        raise ValueError("Bounding-box north must be greater than south.")
    if east <= west:
        raise ValueError("Bounding-box east must be greater than west.")


def _iter_edges_with_keys(graph: nx.Graph):
    if graph.is_multigraph():
        yield from graph.edges(keys=True, data=True)
        return
    for u, v, data in graph.edges(data=True):
        yield u, v, 0, data


def _normalize_node_attrs(data: dict[str, Any]) -> dict[str, Any]:
    attrs = dict(data)
    for key in ("x", "y"):
        if key in attrs:
            attrs[key] = _coerce_float(attrs[key], attrs[key])
    attrs.setdefault("source", "osm")
    return attrs


def _normalize_edge_attrs(u: Any, v: Any, key: Any, data: dict[str, Any]) -> dict[str, Any]:
    attrs = dict(data)
    attrs["mode"] = attrs.get("mode", "road")
    attrs["source"] = attrs.get("source", "osm")

    if "length_m" not in attrs and "length" in attrs:
        attrs["length_m"] = _coerce_float(attrs["length"], attrs["length"])
    elif "length_m" in attrs:
        attrs["length_m"] = _coerce_float(attrs["length_m"], attrs["length_m"])

    if "highway" in attrs:
        attrs["highway"] = _first_attr_value(attrs["highway"])

    if "realworld_edge_id" not in attrs:
        osmid = attrs.get("osmid")
        source_id = _first_attr_value(osmid) if osmid is not None else f"{u}-{v}-{key}"
        attrs["realworld_edge_id"] = f"osm:{source_id}"

    return attrs


def _graphml_safe_copy(graph: nx.Graph) -> nx.Graph:
    copied = graph.copy()
    for attr, value in list(copied.graph.items()):
        if attr in {"node_default", "edge_default"}:
            if not isinstance(value, dict):
                del copied.graph[attr]
            else:
                safe_default = dict(value)
                _replace_with_graphml_safe_values(safe_default)
                copied.graph[attr] = safe_default
            continue
        converted = _graphml_safe_value(value)
        if converted is None:
            del copied.graph[attr]
        else:
            copied.graph[attr] = converted
    for _, data in copied.nodes(data=True):
        _replace_with_graphml_safe_values(data)
    if copied.is_multigraph():
        edge_iter = copied.edges(keys=True, data=True)
        for _, _, _, data in edge_iter:
            _replace_with_graphml_safe_values(data)
    else:
        for _, _, data in copied.edges(data=True):
            _replace_with_graphml_safe_values(data)
    return copied


def _replace_with_graphml_safe_values(data: dict[str, Any]) -> None:
    for attr, value in list(data.items()):
        converted = _graphml_safe_value(value)
        if converted is None:
            del data[attr]
        else:
            data[attr] = converted


def _graphml_safe_value(value: Any) -> str | int | float | bool | None:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _coerce_common_graphml_types(graph: nx.Graph) -> nx.Graph:
    for _, data in graph.nodes(data=True):
        for attr in ("x", "y"):
            if attr in data:
                data[attr] = _coerce_float(data[attr], data[attr])
    edge_iter = graph.edges(keys=True, data=True) if graph.is_multigraph() else graph.edges(data=True)
    for edge in edge_iter:
        data = edge[-1]
        for attr in (
            "length",
            "length_m",
            "speed_kph",
            "travel_time",
            "t0",
            "capacity",
            "base_p_fail",
        ):
            if attr in data:
                data[attr] = _coerce_float(data[attr], data[attr])
    return graph


def _coerce_float(value: Any, default: Any) -> Any:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _first_attr_value(value: Any) -> Any:
    if isinstance(value, (list, tuple, set)):
        return next(iter(value), "")
    return value
