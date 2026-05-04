"""Road-class diagnostics for cached OSM/GraphML road evidence.

This module expands the coarse road-evidence audit into a review packet by
normalized highway class. It is intentionally diagnostic: it identifies which
road classes drive the current cache and where final-study calibration still
depends on speed, capacity, or disruption-probability proxies.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import math
from pathlib import Path
from typing import Any

import networkx as nx

from src.realworld.attributes import (
    is_routeable_vehicle_highway,
    normalize_highway,
    parse_length_m,
    parse_positive_float,
    parse_speed_kph,
)
from src.realworld.osm_network import load_graphml
from src.realworld.road_evidence import DEFAULT_ROAD_GRAPH_PATH


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_COVERAGE_THRESHOLD = 0.95


@dataclass
class RoadClassCounters:
    """Mutable evidence counters for one normalized highway class."""

    highway: str
    edge_count: int = 0
    routeable_edge_count: int = 0
    highway_defaulted_count: int = 0
    length_parseable_count: int = 0
    length_m: float = 0.0
    routeable_length_m: float = 0.0
    maxspeed_parseable_count: int = 0
    capacity_explicit_count: int = 0
    base_disruption_explicit_count: int = 0
    source_counts: Counter[str] = field(default_factory=Counter)

    def add(self, data: dict[str, Any]) -> None:
        """Add one OSM-style edge to this class counter."""

        self.edge_count += 1
        _, highway_defaulted = normalize_highway(data.get("highway"))
        if highway_defaulted:
            self.highway_defaulted_count += 1
        routeable = is_routeable_vehicle_highway(data.get("highway"))
        if routeable:
            self.routeable_edge_count += 1

        length = parse_length_m(data.get("length_m", data.get("length")))
        if length is not None:
            self.length_parseable_count += 1
            self.length_m += length
            if routeable:
                self.routeable_length_m += length
        if parse_speed_kph(data.get("maxspeed")) is not None:
            self.maxspeed_parseable_count += 1
        if parse_positive_float(data.get("capacity")) is not None:
            self.capacity_explicit_count += 1
        if _has_explicit_base_disruption_probability(data):
            self.base_disruption_explicit_count += 1
        self.source_counts[str(data.get("source", "unknown") or "unknown")] += 1

    def to_row(self, total_length_m: float, total_routeable_length_m: float) -> dict[str, object]:
        """Return a JSON-serializable evidence row."""

        length_share = self.length_m / total_length_m if total_length_m > 0.0 else 0.0
        routeable_length_share = (
            self.routeable_length_m / total_routeable_length_m
            if total_routeable_length_m > 0.0
            else 0.0
        )
        return {
            "highway": self.highway,
            "edge_count": self.edge_count,
            "routeable_edge_count": self.routeable_edge_count,
            "highway_defaulted_count": self.highway_defaulted_count,
            "length_parseable_count": self.length_parseable_count,
            "length_parseable_rate": _rate(self.length_parseable_count, self.edge_count),
            "length_km": round(self.length_m / 1000.0, 6),
            "length_share": round(length_share, 6),
            "routeable_length_km": round(self.routeable_length_m / 1000.0, 6),
            "routeable_length_share": round(routeable_length_share, 6),
            "maxspeed_parseable_count": self.maxspeed_parseable_count,
            "maxspeed_parseable_rate": _rate(
                self.maxspeed_parseable_count,
                self.edge_count,
            ),
            "speed_proxy_edge_count": self.edge_count - self.maxspeed_parseable_count,
            "capacity_explicit_count": self.capacity_explicit_count,
            "capacity_explicit_rate": _rate(self.capacity_explicit_count, self.edge_count),
            "capacity_proxy_edge_count": self.edge_count - self.capacity_explicit_count,
            "base_disruption_explicit_count": self.base_disruption_explicit_count,
            "base_disruption_explicit_rate": _rate(
                self.base_disruption_explicit_count,
                self.edge_count,
            ),
            "base_disruption_proxy_edge_count": (
                self.edge_count - self.base_disruption_explicit_count
            ),
            "dominant_source": _dominant_source(self.source_counts),
            "review_priority": _review_priority(
                routeable_edge_count=self.routeable_edge_count,
                routeable_length_share=routeable_length_share,
                maxspeed_rate=_raw_rate(self.maxspeed_parseable_count, self.edge_count),
                capacity_rate=_raw_rate(self.capacity_explicit_count, self.edge_count),
                disruption_rate=_raw_rate(
                    self.base_disruption_explicit_count,
                    self.edge_count,
                ),
            ),
        }


def audit_cached_road_evidence_diagnostics(
    path: str | Path = DEFAULT_ROAD_GRAPH_PATH,
) -> dict[str, object]:
    """Return road-class evidence diagnostics for a cached GraphML path."""

    graph_path = Path(path)
    if not graph_path.exists():
        return {
            "diagnostics_ready": False,
            "path": _display_path(graph_path),
            "node_count": 0,
            "edge_count": 0,
            "road_class_rows": [],
            "top_review_candidates": [],
            "claim_boundary": _claim_boundary(),
            "remaining_blockers": [f"cached road graph is missing: {_display_path(graph_path)}"],
            "review_items": [],
        }

    graph = load_graphml(graph_path, normalize=True)
    summary = audit_road_graph_evidence_diagnostics(graph)
    summary["path"] = _display_path(graph_path)
    return summary


def audit_road_graph_evidence_diagnostics(graph: nx.Graph) -> dict[str, object]:
    """Summarize cached-road evidence by normalized highway class."""

    class_counters: dict[str, RoadClassCounters] = {}
    edge_count = 0
    routeable_edge_count = 0
    highway_defaulted_count = 0
    length_parseable_count = 0
    total_length_m = 0.0
    total_routeable_length_m = 0.0
    maxspeed_parseable_count = 0
    capacity_explicit_count = 0
    base_disruption_explicit_count = 0
    source_counts: Counter[str] = Counter()
    raw_highway_counts: Counter[str] = Counter()

    for _, _, data in _iter_edge_data(graph):
        edge_count += 1
        highway, highway_defaulted = normalize_highway(data.get("highway"))
        counter = class_counters.setdefault(highway, RoadClassCounters(highway))
        counter.add(data)

        raw_highway_counts[str(data.get("highway", "missing") or "missing")] += 1
        if highway_defaulted:
            highway_defaulted_count += 1
        routeable = is_routeable_vehicle_highway(data.get("highway"))
        if routeable:
            routeable_edge_count += 1
        length = parse_length_m(data.get("length_m", data.get("length")))
        if length is not None:
            length_parseable_count += 1
            total_length_m += length
            if routeable:
                total_routeable_length_m += length
        if parse_speed_kph(data.get("maxspeed")) is not None:
            maxspeed_parseable_count += 1
        if parse_positive_float(data.get("capacity")) is not None:
            capacity_explicit_count += 1
        if _has_explicit_base_disruption_probability(data):
            base_disruption_explicit_count += 1
        source_counts[str(data.get("source", "unknown") or "unknown")] += 1

    rows = [
        counter.to_row(total_length_m, total_routeable_length_m)
        for counter in class_counters.values()
    ]
    rows.sort(
        key=lambda row: (
            _priority_order(str(row["review_priority"])),
            -float(row["routeable_length_share"]),
            -int(row["edge_count"]),
            str(row["highway"]),
        )
    )
    top_review_candidates = [
        row
        for row in rows
        if row["review_priority"] in {"high", "medium"}
    ][:10]

    remaining_blockers = _structural_blockers(
        edge_count=edge_count,
        routeable_edge_count=routeable_edge_count,
    )
    review_items = _review_items(
        edge_count=edge_count,
        highway_defaulted_count=highway_defaulted_count,
        maxspeed_parseable_count=maxspeed_parseable_count,
        capacity_explicit_count=capacity_explicit_count,
        base_disruption_explicit_count=base_disruption_explicit_count,
        top_review_candidates=top_review_candidates,
    )

    return {
        "diagnostics_ready": not remaining_blockers,
        "publication_ready": False,
        "claim_boundary": _claim_boundary(),
        "node_count": graph.number_of_nodes(),
        "edge_count": edge_count,
        "routeable_edge_count": routeable_edge_count,
        "highway_class_count": len(rows),
        "highway_defaulted_count": highway_defaulted_count,
        "highway_defaulted_rate": _rate(highway_defaulted_count, edge_count),
        "length_parseable_count": length_parseable_count,
        "length_parseable_rate": _rate(length_parseable_count, edge_count),
        "total_length_km": round(total_length_m / 1000.0, 6),
        "total_routeable_length_km": round(total_routeable_length_m / 1000.0, 6),
        "maxspeed_parseable_count": maxspeed_parseable_count,
        "maxspeed_parseable_rate": _rate(maxspeed_parseable_count, edge_count),
        "capacity_explicit_count": capacity_explicit_count,
        "capacity_explicit_rate": _rate(capacity_explicit_count, edge_count),
        "base_disruption_explicit_count": base_disruption_explicit_count,
        "base_disruption_explicit_rate": _rate(
            base_disruption_explicit_count,
            edge_count,
        ),
        "source_counts": dict(sorted(source_counts.items())),
        "top_raw_highway_tags": [
            {"raw_highway": highway, "count": count}
            for highway, count in raw_highway_counts.most_common(10)
        ],
        "road_class_rows": rows,
        "top_review_candidates": top_review_candidates,
        "review_items": review_items,
        "remaining_blockers": remaining_blockers,
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


def _raw_rate(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return count / total


def _rate(count: int, total: int) -> float:
    return round(_raw_rate(count, total), 6)


def _dominant_source(source_counts: Counter[str]) -> str:
    if not source_counts:
        return "unknown"
    return source_counts.most_common(1)[0][0]


def _review_priority(
    *,
    routeable_edge_count: int,
    routeable_length_share: float,
    maxspeed_rate: float,
    capacity_rate: float,
    disruption_rate: float,
) -> str:
    if routeable_edge_count <= 0:
        return "low"
    weak_core_evidence = (
        maxspeed_rate < REVIEW_COVERAGE_THRESHOLD
        or capacity_rate < REVIEW_COVERAGE_THRESHOLD
        or disruption_rate < REVIEW_COVERAGE_THRESHOLD
    )
    if weak_core_evidence and routeable_length_share >= 0.05:
        return "high"
    if weak_core_evidence:
        return "medium"
    return "low"


def _priority_order(priority: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(priority, 3)


def _structural_blockers(*, edge_count: int, routeable_edge_count: int) -> list[str]:
    blockers: list[str] = []
    if edge_count <= 0:
        blockers.append("cached road graph has no edges")
    if routeable_edge_count <= 0:
        blockers.append("cached road graph has no bus-practical routeable edges")
    return blockers


def _review_items(
    *,
    edge_count: int,
    highway_defaulted_count: int,
    maxspeed_parseable_count: int,
    capacity_explicit_count: int,
    base_disruption_explicit_count: int,
    top_review_candidates: list[dict[str, object]],
) -> list[str]:
    if edge_count <= 0:
        return ["provide a non-empty cached OSM/GraphML road graph before road evidence review"]

    items: list[str] = []
    if highway_defaulted_count:
        items.append(
            "review edges whose OSM highway tag defaulted to unclassified before relying on class-level proxies"
        )
    if _raw_rate(maxspeed_parseable_count, edge_count) < REVIEW_COVERAGE_THRESHOLD:
        items.append(
            "strengthen free-flow speed evidence for major routeable road classes or document reviewed class-level speed overrides"
        )
    if _raw_rate(capacity_explicit_count, edge_count) < REVIEW_COVERAGE_THRESHOLD:
        items.append(
            "replace built-in road-capacity proxies with reviewed class overrides, traffic-count references, or benchmark-calibrated values"
        )
    if _raw_rate(base_disruption_explicit_count, edge_count) < REVIEW_COVERAGE_THRESHOLD:
        items.append(
            "replace built-in base-disruption probabilities with hazard, incident, scenario, or reviewed sensitivity evidence"
        )
    if top_review_candidates:
        top_classes = ", ".join(str(row["highway"]) for row in top_review_candidates[:5])
        items.append(
            f"prioritize road-input review for high-impact classes: {top_classes}"
        )
    items.append(
        "use this diagnostic to prepare road-class override evidence; it does not create acceptance or calibration by itself"
    )
    return items


def _claim_boundary() -> str:
    return (
        "Road-class diagnostics summarize cached OSM/GraphML evidence coverage. "
        "They do not calibrate road capacity, traffic assignment, disruption "
        "probability, or operational route choice."
    )


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "REVIEW_COVERAGE_THRESHOLD",
    "RoadClassCounters",
    "audit_cached_road_evidence_diagnostics",
    "audit_road_graph_evidence_diagnostics",
]
