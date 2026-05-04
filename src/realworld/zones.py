"""Zone snapping and connector-edge helpers for real-world road graphs."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, radians, sqrt
from typing import Any, Mapping

import networkx as nx

from .regions import load_region_spec
from .types import RailPointSpec, RegionSpec, ZoneSpec


PointSpec = ZoneSpec | RailPointSpec

EARTH_M_PER_DEG_LAT = 111_320.0
DEFAULT_CONNECTOR_SPEED_KPH = 20.0
DEFAULT_CONNECTOR_CAPACITY = 9_999.0
MIN_CONNECTOR_T0_MIN = 0.01


@dataclass(frozen=True)
class SnappedPoint:
    """A region point snapped to the nearest road-network node."""

    point_id: str
    road_node: Any
    distance_m: float
    lat: float
    lon: float
    road_lat: float
    road_lon: float


def nearest_road_node(graph: nx.Graph, point: PointSpec) -> SnappedPoint:
    """Snap a zone or rail point to the nearest node using lon/lat attributes.

    The MVP intentionally avoids geospatial dependencies. Node attributes are
    expected to use OSMnx-style ``x`` longitude and ``y`` latitude values.
    """

    if graph.number_of_nodes() == 0:
        raise ValueError("Cannot snap zone points because the road graph has no nodes.")

    candidates: list[tuple[float, str, Any, float, float]] = []
    for node, data in graph.nodes(data=True):
        lon = _finite_float(data.get("x"))
        lat = _finite_float(data.get("y"))
        if lon is None or lat is None:
            continue
        distance_m = approximate_distance_m(point.lat, point.lon, lat, lon)
        candidates.append((distance_m, repr(node), node, lat, lon))

    if not candidates:
        raise ValueError("Cannot snap zone points because no road nodes have finite x/y lon/lat.")

    distance_m, _, road_node, road_lat, road_lon = min(candidates)
    return SnappedPoint(
        point_id=point.id,
        road_node=road_node,
        distance_m=distance_m,
        lat=point.lat,
        lon=point.lon,
        road_lat=road_lat,
        road_lon=road_lon,
    )


def snap_region_points(graph: nx.Graph, region: Mapping[str, Any] | RegionSpec) -> dict[str, SnappedPoint]:
    """Snap the simulator-canonical region points to nearest road nodes."""

    region_spec = load_region_spec(region)
    points: tuple[PointSpec, ...] = (
        region_spec.primary_assembly,
        region_spec.primary_destination,
        region_spec.rail.access,
        region_spec.rail.egress,
    )
    return {point.id: nearest_road_node(graph, point) for point in points}


def connector_edge_attributes(
    snapped: SnappedPoint,
    *,
    speed_kph: float = DEFAULT_CONNECTOR_SPEED_KPH,
    capacity: float = DEFAULT_CONNECTOR_CAPACITY,
    min_t0_min: float = MIN_CONNECTOR_T0_MIN,
) -> dict[str, Any]:
    """Return simulator-ready metadata for a zone-to-road connector edge."""

    speed_kph = _require_positive_finite(speed_kph, "connector speed_kph")
    capacity = _require_positive_finite(capacity, "connector capacity")
    min_t0_min = _require_positive_finite(min_t0_min, "connector min_t0_min")
    t0 = max(snapped.distance_m / (speed_kph * 1000.0 / 60.0), min_t0_min)
    return {
        "t0": t0,
        "capacity": capacity,
        "base_p_fail": 0.0,
        "p_fail": 0.0,
        "mode": "road",
        "length_m": snapped.distance_m,
        "speed_kph": speed_kph,
        "highway": "connector",
        "source": "connector",
        "snapped_point_id": snapped.point_id,
        "snapped_road_node": snapped.road_node,
        "connector_distance_m": snapped.distance_m,
    }


def add_connector_edges(
    graph: nx.DiGraph,
    snaps: Mapping[str, SnappedPoint],
    *,
    speed_kph: float = DEFAULT_CONNECTOR_SPEED_KPH,
    capacity: float = DEFAULT_CONNECTOR_CAPACITY,
    min_t0_min: float = MIN_CONNECTOR_T0_MIN,
) -> None:
    """Add bidirectional traversable road connectors to a simulator graph."""

    for point_id in sorted(snaps):
        snapped = snaps[point_id]
        graph.add_node(
            point_id,
            source="region",
            role="simulator_point",
            x=snapped.lon,
            y=snapped.lat,
            snapped_road_node=snapped.road_node,
            connector_distance_m=snapped.distance_m,
        )
        attrs = connector_edge_attributes(
            snapped,
            speed_kph=speed_kph,
            capacity=capacity,
            min_t0_min=min_t0_min,
        )
        graph.add_edge(point_id, snapped.road_node, **attrs)
        graph.add_edge(snapped.road_node, point_id, **attrs)


def approximate_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return an equirectangular lon/lat distance estimate in meters."""

    lat1 = _require_finite(lat1, "lat1")
    lon1 = _require_finite(lon1, "lon1")
    lat2 = _require_finite(lat2, "lat2")
    lon2 = _require_finite(lon2, "lon2")
    mean_lat = radians((lat1 + lat2) / 2.0)
    meters_per_deg_lon = EARTH_M_PER_DEG_LAT * cos(mean_lat)
    dy = (lat2 - lat1) * EARTH_M_PER_DEG_LAT
    dx = (lon2 - lon1) * meters_per_deg_lon
    return sqrt(dx * dx + dy * dy)


def _finite_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(parsed):
        return None
    return parsed


def _require_finite(value: Any, field_name: str) -> float:
    parsed = _finite_float(value)
    if parsed is None:
        raise ValueError(f"{field_name} must be finite")
    return parsed


def _require_positive_finite(value: Any, field_name: str) -> float:
    parsed = _finite_float(value)
    if parsed is None or parsed <= 0.0:
        raise ValueError(f"{field_name} must be positive and finite")
    return parsed


__all__ = [
    "DEFAULT_CONNECTOR_CAPACITY",
    "DEFAULT_CONNECTOR_SPEED_KPH",
    "MIN_CONNECTOR_T0_MIN",
    "SnappedPoint",
    "add_connector_edges",
    "approximate_distance_m",
    "connector_edge_attributes",
    "nearest_road_node",
    "snap_region_points",
]
