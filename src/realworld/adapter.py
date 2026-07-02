"""Adapter from normalized OSM-like road graphs to simulator DiGraphs."""

from __future__ import annotations

from math import isfinite
from typing import Any, Iterable, Mapping, Sequence

import networkx as nx

from .attributes import (
    DEFAULT_ROUTEABLE_HIGHWAY_CLASSES,
    RoadClassDefaults,
    is_routeable_vehicle_highway,
    map_edge_attributes,
)
from .regions import load_region_spec
from .types import RegionSpec
from .zones import (
    DEFAULT_CONNECTOR_CAPACITY,
    DEFAULT_CONNECTOR_SPEED_KPH,
    MIN_CONNECTOR_T0_MIN,
    add_connector_edges,
    snap_region_points,
)


REQUIRED_EDGE_FIELDS = ("t0", "capacity", "base_p_fail", "p_fail", "mode")
REQUIRED_ROUTES = (
    ("A", "D"),
    ("A", "S"),
    ("R", "D"),
)
# Edge modes the simulator graph may carry. ``road`` and ``rail`` are the
# Phase-1 2-mode contract; ``sea`` / ``air`` are added by the multi-service
# widening (Phase 2) and exercised once sea/air RegionServiceSpec entries and
# their graph edges exist (Phase 3 mode leaves).
ALLOWED_EDGE_MODES = frozenset({"road", "rail", "sea", "air"})


def build_simulator_graph(
    road_graph: nx.Graph,
    region: Mapping[str, Any] | RegionSpec,
    *,
    connector_speed_kph: float = DEFAULT_CONNECTOR_SPEED_KPH,
    connector_capacity: float = DEFAULT_CONNECTOR_CAPACITY,
    min_connector_t0_min: float = MIN_CONNECTOR_T0_MIN,
    routeable_highway_classes: Sequence[str] | None = tuple(
        sorted(DEFAULT_ROUTEABLE_HIGHWAY_CLASSES)
    ),
    highway_defaults: Mapping[str, RoadClassDefaults] | None = None,
    road_class_override_metadata: Mapping[str, Mapping[str, Any]] | None = None,
    validate_routes: bool = True,
) -> nx.DiGraph:
    """Convert an OSM-like road graph plus region spec to a simulator graph.

    Parallel road edges are collapsed deterministically by choosing the lowest
    free-flow time, then higher capacity, lower failure probability, and finally
    a stable source edge identifier.
    """

    region_spec = load_region_spec(region)
    _ensure_canonical_ids(region_spec)
    routeable_graph = _routeable_road_graph(
        road_graph,
        routeable_highway_classes=routeable_highway_classes,
    )

    simulator = nx.DiGraph()
    simulator.graph.update(road_graph.graph)
    simulator.graph["source"] = simulator.graph.get("source", "realworld")
    simulator.graph["adapted_by"] = "src.realworld.adapter"
    simulator.graph["region_id"] = region_spec.region_id
    simulator.graph["source_node_count"] = road_graph.number_of_nodes()
    simulator.graph["source_edge_count"] = road_graph.number_of_edges()
    simulator.graph["routeable_source_node_count"] = routeable_graph.number_of_nodes()
    simulator.graph["routeable_source_edge_count"] = routeable_graph.number_of_edges()
    simulator.graph["routeable_highway_classes"] = tuple(
        sorted(routeable_highway_classes or ())
    )
    simulator.graph["road_class_overrides_applied"] = highway_defaults is not None
    simulator.graph["road_class_override_metadata_applied"] = (
        road_class_override_metadata is not None
    )
    simulator.graph["road_class_override_highway_count"] = len(
        road_class_override_metadata or {}
    )
    simulator.graph["road_class_override_highways"] = tuple(
        sorted((road_class_override_metadata or {}).keys())
    )

    for node, data in routeable_graph.nodes(data=True):
        if node in region_spec.canonical_ids:
            raise ValueError(
                f"Road node {node!r} conflicts with a canonical simulator node ID."
            )
        simulator.add_node(node, **dict(data))

    for edge in _select_simulator_edges(
        routeable_graph,
        highway_defaults=highway_defaults,
        road_class_override_metadata=road_class_override_metadata,
    ):
        u, v, attrs = edge
        simulator.add_edge(u, v, **attrs)

    snaps = snap_region_points(routeable_graph, region_spec)
    add_connector_edges(
        simulator,
        snaps,
        speed_kph=connector_speed_kph,
        capacity=connector_capacity,
        min_t0_min=min_connector_t0_min,
    )

    _add_rail_metadata(simulator, region_spec)
    _validate_required_edge_fields(simulator)
    if validate_routes:
        _validate_required_routes(simulator, region_spec)
    return simulator


def _routeable_road_graph(
    road_graph: nx.Graph,
    *,
    routeable_highway_classes: Sequence[str] | None,
) -> nx.MultiDiGraph:
    """Return the bus-practical OSM edge subset used by simulator routes."""

    routeable = nx.MultiDiGraph()
    routeable.graph.update(road_graph.graph)
    routeable.graph["filtered_by"] = "src.realworld.adapter._routeable_road_graph"

    selected_edges: list[tuple[Any, Any, Any, dict[str, Any]]] = []
    for u, v, key, data in _iter_directed_edges_with_keys(road_graph):
        if routeable_highway_classes is not None and not is_routeable_vehicle_highway(
            data.get("highway"),
            allowed_classes=routeable_highway_classes,
        ):
            continue
        selected_edges.append((u, v, key, dict(data)))

    if not selected_edges:
        raise ValueError("Road graph has no routeable vehicle-road edges after filtering.")

    routeable_nodes = {u for u, _, _, _ in selected_edges} | {
        v for _, v, _, _ in selected_edges
    }
    for node in sorted(routeable_nodes, key=repr):
        routeable.add_node(node, **dict(road_graph.nodes[node]))
    for u, v, key, data in selected_edges:
        routeable.add_edge(u, v, key=key, **data)
    return routeable


def realworld_network_config(region: Mapping[str, Any] | RegionSpec) -> dict[str, Any]:
    """Return config-compatible network metadata for the region's services.

    Emits ``service_links`` (one tuple per RegionServiceSpec: mode, access,
    egress, travel_time, headway, capacity) for the composable multi-service
    pipeline, plus a backward-compatible ``rail_link`` derived from the first
    rail service so legacy single-rail callers keep working.
    """

    region_spec = load_region_spec(region)
    nodes = list(region_spec.canonical_ids)
    service_links = [
        (
            svc.mode,
            svc.access.id,
            svc.egress.id,
            svc.travel_time_min,
            svc.headway_min,
            svc.capacity_pax_per_unit,
        )
        for svc in region_spec.region_services
    ]
    rail_services = region_spec.services_by_mode("rail")
    rail_link: list[tuple] = []
    if rail_services:
        rail = rail_services[0]
        rail_link = [
            (
                rail.access.id,
                rail.egress.id,
                rail.travel_time_min,
                rail.headway_min,
                rail.capacity_pax_per_unit,
            )
        ]
    return {
        "nodes": nodes,
        "service_links": service_links,
        "rail_link": rail_link,
    }


def _select_simulator_edges(
    road_graph: nx.Graph,
    *,
    highway_defaults: Mapping[str, RoadClassDefaults] | None = None,
    road_class_override_metadata: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[tuple[Any, Any, dict[str, Any]]]:
    selected: dict[tuple[Any, Any], dict[str, Any]] = {}
    for u, v, key, data in _iter_directed_edges_with_keys(road_graph):
        attrs = map_edge_attributes(
            data,
            edge_id=_edge_id(u, v, key, data),
            highway_defaults=highway_defaults,
        )
        _apply_road_class_override_metadata(
            attrs,
            road_class_override_metadata=road_class_override_metadata,
        )
        _validate_edge_attrs(attrs)
        edge = (u, v)
        current = selected.get(edge)
        if current is None or _edge_choice_key(attrs) < _edge_choice_key(current):
            selected[edge] = attrs

    edges = [(u, v, attrs) for (u, v), attrs in selected.items()]
    return sorted(edges, key=lambda item: (repr(item[0]), repr(item[1])))


def _apply_road_class_override_metadata(
    attrs: dict[str, Any],
    *,
    road_class_override_metadata: Mapping[str, Mapping[str, Any]] | None,
) -> None:
    if not road_class_override_metadata:
        return
    highway = str(attrs.get("highway", "")).strip().lower()
    metadata = road_class_override_metadata.get(highway)
    if not metadata:
        return
    assumptions = {
        str(item)
        for item in attrs.get("attribute_assumptions", ())
        if str(item) in {"speed_kph", "capacity", "base_p_fail"}
    }
    if not assumptions:
        return

    attrs["road_class_override_applied"] = True
    attrs["road_class_override_highway"] = highway
    attrs["road_class_override_fields"] = tuple(sorted(assumptions))
    attrs["road_class_override_source_class"] = str(
        metadata.get("source_class", "")
    )
    attrs["road_class_override_source_name"] = str(metadata.get("source_name", ""))
    attrs["road_class_override_source_url_or_citation"] = str(
        metadata.get("source_url_or_citation", "")
    )
    attrs["road_class_override_notes"] = str(metadata.get("notes", ""))


def _iter_directed_edges_with_keys(road_graph: nx.Graph) -> Iterable[tuple[Any, Any, Any, dict]]:
    if road_graph.is_multigraph():
        for u, v, key, data in road_graph.edges(keys=True, data=True):
            yield u, v, key, dict(data)
            if not road_graph.is_directed():
                yield v, u, key, dict(data)
        return

    for u, v, data in road_graph.edges(data=True):
        yield u, v, 0, dict(data)
        if not road_graph.is_directed():
            yield v, u, 0, dict(data)


def _edge_id(u: Any, v: Any, key: Any, data: Mapping[str, Any]) -> str:
    if "realworld_edge_id" in data:
        return str(data["realworld_edge_id"])
    if "osmid" in data:
        osmid = data["osmid"]
        if isinstance(osmid, (list, tuple)):
            return ",".join(str(item) for item in osmid)
        if isinstance(osmid, (set, frozenset)):
            return ",".join(sorted(str(item) for item in osmid))
        return str(osmid)
    return f"{u!r}->{v!r}:{key!r}"


def _edge_choice_key(attrs: Mapping[str, Any]) -> tuple[float, float, float, str]:
    return (
        float(attrs["t0"]),
        -float(attrs["capacity"]),
        float(attrs["base_p_fail"]),
        str(attrs.get("realworld_edge_id", "")),
    )


def _add_service_metadata(graph: nx.DiGraph, region: RegionSpec) -> None:
    config = realworld_network_config(region)
    graph.graph["rail_link"] = config["rail_link"]
    graph.graph["service_links"] = config["service_links"]


# Backward-compatible alias; callers that attach rail metadata now also attach
# the full multi-service link set.
_add_rail_metadata = _add_service_metadata


def _ensure_canonical_ids(region: RegionSpec) -> None:
    """Validate the canonical-id structure for single- and multi-service regions.

    A single-rail region yields exactly ``("A","D","S","R")`` (unchanged legacy
    contract). A multi-service region appends extra ``<access,egress>`` pairs.
    The rail service, when present, must be declared first so the legacy rail
    alias and the first service pair stay stable.
    """

    ids = region.canonical_ids
    if len(ids) < 4 or len(ids) % 2 != 0:
        raise ValueError(
            "canonical_ids must be (assembly, destination, <access,egress> "
            f"pairs); got {ids!r}"
        )
    services = region.region_services
    has_rail = any(svc.mode == "rail" for svc in services)
    if has_rail and services[0].mode != "rail":
        raise ValueError(
            "rail service must be declared first in region_services "
            "(legacy rail alias requires it)"
        )


def required_routes_for(region: RegionSpec) -> tuple[tuple[str, str], ...]:
    """Return the required road routes for a region's services.

    Always includes ``assembly -> destination``; each service adds
    ``assembly -> service.access`` and ``service.egress -> destination``. A
    single-rail region yields exactly ``[(A,D),(A,S),(R,D)]`` (identical to the
    legacy ``REQUIRED_ROUTES``).
    """

    assembly = region.primary_assembly_id
    destination = region.primary_destination_id
    routes: list[tuple[str, str]] = [(assembly, destination)]
    for svc in region.region_services:
        routes.append((assembly, svc.access.id))
        routes.append((svc.egress.id, destination))
    return tuple(routes)


def _validate_required_edge_fields(graph: nx.DiGraph) -> None:
    for u, v, data in graph.edges(data=True):
        missing = [field for field in REQUIRED_EDGE_FIELDS if field not in data]
        if missing:
            raise ValueError(f"Edge {u!r}->{v!r} is missing fields: {', '.join(missing)}")
        _validate_edge_attrs(data)


def _validate_edge_attrs(attrs: Mapping[str, Any]) -> None:
    for field in ("t0", "capacity"):
        try:
            value = float(attrs[field])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be a positive finite edge attribute") from exc
        if not isfinite(value) or value <= 0.0:
            raise ValueError(f"{field} must be a positive finite edge attribute")

    for field in ("base_p_fail", "p_fail"):
        try:
            probability = float(attrs[field])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be a finite probability") from exc
        if not isfinite(probability) or not 0.0 <= probability <= 1.0:
            raise ValueError(f"{field} must satisfy 0 <= p <= 1")

    if attrs.get("mode") not in ALLOWED_EDGE_MODES:
        raise ValueError(
            f"mode must be routeable by the simulator (one of "
            f"{sorted(ALLOWED_EDGE_MODES)}), got {attrs.get('mode')!r}"
        )


def _validate_required_routes(graph: nx.DiGraph, region: RegionSpec) -> None:
    for source, target in required_routes_for(region):
        try:
            if not nx.has_path(graph, source, target):
                raise ValueError(f"Simulator graph has no route {source} -> {target}.")
        except nx.NodeNotFound as exc:
            raise ValueError(f"Simulator graph is missing node for route {source} -> {target}.") from exc


osm_graph_to_simulator_graph = build_simulator_graph
to_simulator_graph = build_simulator_graph


__all__ = [
    "REQUIRED_EDGE_FIELDS",
    "REQUIRED_ROUTES",
    "build_simulator_graph",
    "osm_graph_to_simulator_graph",
    "realworld_network_config",
    "to_simulator_graph",
]
