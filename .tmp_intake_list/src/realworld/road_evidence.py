"""Audit cached OSM road-input evidence for final-study readiness.

This module distinguishes OSM-derived fields such as geometry, length,
highway class, and optional maxspeed tags from simulator proxies such as road
capacity and disruption probabilities. Passing the audit means the cache is
readable and diagnosable, not that the road model is calibrated.
"""

from __future__ import annotations

from collections import Counter
import math
from pathlib import Path
from typing import Any

import networkx as nx

from src.realworld.attributes import (
    is_routeable_vehicle_highway,
    map_osm_edge_attributes,
    normalize_highway,
    parse_length_m,
    parse_positive_float,
    parse_speed_kph,
)
from src.realworld.osm_network import load_graphml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_GRAPH_PATH = PROJECT_ROOT / "data" / "cache" / "pilot_region_road.graphml"


def audit_cached_road_evidence(
    path: str | Path = DEFAULT_ROAD_GRAPH_PATH,
) -> dict[str, object]:
    """Load a cached GraphML road graph and return its evidence audit."""

    graph_path = Path(path)
    graph = load_graphml(graph_path, normalize=True)
    summary = audit_road_graph_evidence(graph)
    summary["path"] = _display_path(graph_path)
    return summary


def audit_road_graph_evidence(graph: nx.Graph) -> dict[str, object]:
    """Return source/proxy coverage for an OSM-style road graph."""

    edge_count = 0
    routeable_edge_count = 0
    highway_known_count = 0
    highway_defaulted_count = 0
    length_parseable_count = 0
    maxspeed_parseable_count = 0
    capacity_explicit_count = 0
    base_disruption_explicit_count = 0
    mapped_edge_count = 0
    highway_counts: Counter[str] = Counter()
    assumption_counts: Counter[str] = Counter()

    for _, _, data in _iter_edge_data(graph):
        edge_count += 1
        highway, defaulted = normalize_highway(data.get("highway"))
        highway_counts[highway] += 1
        if defaulted:
            highway_defaulted_count += 1
        else:
            highway_known_count += 1

        if is_routeable_vehicle_highway(data.get("highway")):
            routeable_edge_count += 1
        if parse_length_m(data.get("length_m", data.get("length"))) is not None:
            length_parseable_count += 1
        if parse_speed_kph(data.get("maxspeed")) is not None:
            maxspeed_parseable_count += 1
        if parse_positive_float(data.get("capacity")) is not None:
            capacity_explicit_count += 1
        if _has_explicit_base_disruption_probability(data):
            base_disruption_explicit_count += 1

        mapped = map_osm_edge_attributes(data)
        mapped_edge_count += 1
        for assumption in mapped.get("attribute_assumptions", ()):
            assumption_counts[str(assumption)] += 1

    capacity_proxy_count = edge_count - capacity_explicit_count
    disruption_proxy_count = edge_count - base_disruption_explicit_count
    maxspeed_fallback_count = edge_count - maxspeed_parseable_count

    return {
        "publication_ready": (
            edge_count > 0
            and maxspeed_fallback_count == 0
            and capacity_proxy_count == 0
            and disruption_proxy_count == 0
        ),
        "claim_boundary": (
            "This audit checks cached road-input evidence coverage. It does not "
            "calibrate traffic assignment, road capacity, background demand, or "
            "disruption probability."
        ),
        "node_count": graph.number_of_nodes(),
        "edge_count": edge_count,
        "mapped_edge_count": mapped_edge_count,
        "routeable_edge_count": routeable_edge_count,
        "highway_known_count": highway_known_count,
        "highway_defaulted_count": highway_defaulted_count,
        "highway_default_rate": _rate(highway_defaulted_count, edge_count),
        "length_parseable_count": length_parseable_count,
        "length_fallback_count": edge_count - length_parseable_count,
        "maxspeed_parseable_count": maxspeed_parseable_count,
        "maxspeed_fallback_count": maxspeed_fallback_count,
        "maxspeed_parseable_rate": _rate(maxspeed_parseable_count, edge_count),
        "capacity_explicit_count": capacity_explicit_count,
        "capacity_proxy_count": capacity_proxy_count,
        "capacity_explicit_rate": _rate(capacity_explicit_count, edge_count),
        "base_disruption_explicit_count": base_disruption_explicit_count,
        "base_disruption_proxy_count": disruption_proxy_count,
        "attribute_assumption_counts": dict(sorted(assumption_counts.items())),
        "top_highway_classes": [
            {"highway": highway, "count": count}
            for highway, count in highway_counts.most_common(10)
        ],
        "remaining_blockers": _road_blockers(
            maxspeed_fallback_count=maxspeed_fallback_count,
            capacity_proxy_count=capacity_proxy_count,
            disruption_proxy_count=disruption_proxy_count,
            routeable_edge_count=routeable_edge_count,
        ),
    }


def _iter_edge_data(graph: nx.Graph):
    if graph.is_multigraph():
        for u, v, _, data in graph.edges(keys=True, data=True):
            yield u, v, data
        return
    for u, v, data in graph.edges(data=True):
        yield u, v, data


def _has_explicit_base_disruption_probability(data: dict[str, Any]) -> bool:
    return _is_probability(data.get("base_p_fail")) or _is_probability(data.get("p_fail"))


def _is_probability(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(parsed) and 0.0 <= parsed <= 1.0


def _rate(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(count / total, 6)


def _road_blockers(
    *,
    maxspeed_fallback_count: int,
    capacity_proxy_count: int,
    disruption_proxy_count: int,
    routeable_edge_count: int,
) -> list[str]:
    blockers: list[str] = []
    if maxspeed_fallback_count:
        blockers.append(
            "review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration"
        )
    if capacity_proxy_count:
        blockers.append(
            "replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values"
        )
    if disruption_proxy_count:
        blockers.append(
            "replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence"
        )
    if routeable_edge_count == 0:
        blockers.append("road graph has no bus-practical routeable edges")
    blockers.append(
        "treat this as road-input evidence only; route plausibility and traffic validation remain separate gates"
    )
    return blockers


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "DEFAULT_ROAD_GRAPH_PATH",
    "audit_cached_road_evidence",
    "audit_road_graph_evidence",
]
