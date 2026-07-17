"""Route-level accessibility-loss and critical-edge diagnostics.

These helpers inspect an adapted simulator graph. They are scaffold diagnostics
for route fragility, not calibrated evidence about real operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping, Sequence

import networkx as nx


ACCESSIBILITY_CLAIM_SCOPE = "scaffold_accessibility_diagnostic_not_calibrated"
ACCESSIBILITY_CSV_FIELDS = (
    "region_id",
    "route_id",
    "route_label",
    "source",
    "target",
    "baseline_available",
    "baseline_distance_m",
    "baseline_time_min",
    "baseline_edge_count",
    "tested_edge_u",
    "tested_edge_v",
    "tested_edge_rank",
    "tested_edge_length_m",
    "tested_edge_time_min",
    "disrupted_available",
    "disrupted_distance_m",
    "disrupted_time_min",
    "distance_loss_m",
    "time_loss_min",
    "time_loss_ratio",
    "criticality_class",
    "claim_scope",
    "notes",
)


@dataclass(frozen=True)
class AccessibilityRoute:
    """One road-mode OD pair to inspect for accessibility loss."""

    route_id: str
    source: Any
    target: Any
    label: str


@dataclass(frozen=True)
class AccessibilityLossRecord:
    """Route accessibility impact after removing one baseline path edge."""

    region_id: str
    route_id: str
    route_label: str
    source: Any
    target: Any
    baseline_available: bool
    baseline_distance_m: float
    baseline_time_min: float
    baseline_edge_count: int
    tested_edge_u: Any = ""
    tested_edge_v: Any = ""
    tested_edge_rank: int = 0
    tested_edge_length_m: float = float("nan")
    tested_edge_time_min: float = float("nan")
    disrupted_available: bool = False
    disrupted_distance_m: float = float("nan")
    disrupted_time_min: float = float("nan")
    distance_loss_m: float = float("nan")
    time_loss_min: float = float("nan")
    time_loss_ratio: float = float("nan")
    criticality_class: str = "unavailable"
    claim_scope: str = ACCESSIBILITY_CLAIM_SCOPE
    notes: str = ""

    def as_csv_row(self) -> dict[str, str]:
        """Return this record using the stable CSV schema."""

        values = {
            "region_id": self.region_id,
            "route_id": self.route_id,
            "route_label": self.route_label,
            "source": str(self.source),
            "target": str(self.target),
            "baseline_available": str(self.baseline_available).lower(),
            "baseline_distance_m": _format_float(self.baseline_distance_m),
            "baseline_time_min": _format_float(self.baseline_time_min),
            "baseline_edge_count": str(self.baseline_edge_count),
            "tested_edge_u": str(self.tested_edge_u),
            "tested_edge_v": str(self.tested_edge_v),
            "tested_edge_rank": str(self.tested_edge_rank),
            "tested_edge_length_m": _format_float(self.tested_edge_length_m),
            "tested_edge_time_min": _format_float(self.tested_edge_time_min),
            "disrupted_available": str(self.disrupted_available).lower(),
            "disrupted_distance_m": _format_float(self.disrupted_distance_m),
            "disrupted_time_min": _format_float(self.disrupted_time_min),
            "distance_loss_m": _format_float(self.distance_loss_m),
            "time_loss_min": _format_float(self.time_loss_min),
            "time_loss_ratio": _format_float(self.time_loss_ratio),
            "criticality_class": self.criticality_class,
            "claim_scope": self.claim_scope,
            "notes": self.notes,
        }
        return {field: values[field] for field in ACCESSIBILITY_CSV_FIELDS}


DEFAULT_ACCESSIBILITY_ROUTES = (
    AccessibilityRoute("bus_direct", "A", "D", "bus direct road accessibility"),
    AccessibilityRoute("rail_access", "A", "S", "assembly to rail access"),
    AccessibilityRoute("last_mile", "R", "D", "rail egress to destination"),
)


def evaluate_accessibility_loss(
    graph: nx.DiGraph,
    *,
    region_id: str | None = None,
    routes: Sequence[AccessibilityRoute] = DEFAULT_ACCESSIBILITY_ROUTES,
) -> tuple[AccessibilityLossRecord, ...]:
    """Return route-level edge-removal accessibility diagnostics."""

    resolved_region_id = region_id or str(graph.graph.get("region_id", "unknown_region"))
    road_graph = _road_mode_view(graph)
    records: list[AccessibilityLossRecord] = []
    for route in routes:
        records.extend(
            evaluate_route_accessibility_loss(
                road_graph,
                route,
                region_id=resolved_region_id,
            )
        )
    return tuple(records)


def evaluate_route_accessibility_loss(
    road_graph: nx.DiGraph,
    route: AccessibilityRoute,
    *,
    region_id: str,
) -> tuple[AccessibilityLossRecord, ...]:
    """Remove each baseline shortest-time path edge and measure route loss."""

    if not _has_path(road_graph, route.source, route.target):
        return (
            AccessibilityLossRecord(
                region_id=region_id,
                route_id=route.route_id,
                route_label=route.label,
                source=route.source,
                target=route.target,
                baseline_available=False,
                baseline_distance_m=float("nan"),
                baseline_time_min=float("nan"),
                baseline_edge_count=0,
                criticality_class="baseline_disconnected",
                notes="baseline road route unavailable",
            ),
        )

    baseline_path = tuple(
        nx.shortest_path(road_graph, route.source, route.target, weight="t0")
    )
    baseline_time = _path_sum(road_graph, baseline_path, "t0")
    baseline_distance = _path_sum(road_graph, baseline_path, "length_m")
    baseline_edges = tuple(zip(baseline_path, baseline_path[1:]))
    records: list[AccessibilityLossRecord] = []
    for rank, (u, v) in enumerate(baseline_edges, start=1):
        disrupted = road_graph.copy()
        disrupted.remove_edge(u, v)
        disrupted_available = _has_path(disrupted, route.source, route.target)
        if disrupted_available:
            disrupted_path = tuple(
                nx.shortest_path(disrupted, route.source, route.target, weight="t0")
            )
            disrupted_time = _path_sum(disrupted, disrupted_path, "t0")
            disrupted_distance = _path_sum(disrupted, disrupted_path, "length_m")
            time_loss = disrupted_time - baseline_time
            distance_loss = disrupted_distance - baseline_distance
            time_loss_ratio = _ratio(time_loss, baseline_time)
            criticality = classify_criticality(time_loss, time_loss_ratio)
            notes = "single directed baseline edge removed; alternate road route available"
        else:
            disrupted_time = float("nan")
            disrupted_distance = float("nan")
            time_loss = float("inf")
            distance_loss = float("inf")
            time_loss_ratio = float("inf")
            criticality = "disconnected"
            notes = "single directed baseline edge removal disconnects this road route"

        edge_data = road_graph.edges[u, v]
        records.append(
            AccessibilityLossRecord(
                region_id=region_id,
                route_id=route.route_id,
                route_label=route.label,
                source=route.source,
                target=route.target,
                baseline_available=True,
                baseline_distance_m=baseline_distance,
                baseline_time_min=baseline_time,
                baseline_edge_count=len(baseline_edges),
                tested_edge_u=u,
                tested_edge_v=v,
                tested_edge_rank=rank,
                tested_edge_length_m=_finite_or_nan(edge_data.get("length_m")),
                tested_edge_time_min=_finite_or_nan(edge_data.get("t0")),
                disrupted_available=disrupted_available,
                disrupted_distance_m=disrupted_distance,
                disrupted_time_min=disrupted_time,
                distance_loss_m=distance_loss,
                time_loss_min=time_loss,
                time_loss_ratio=time_loss_ratio,
                criticality_class=criticality,
                notes=notes,
            )
        )
    return tuple(records)


def summarize_accessibility_loss(
    records: Sequence[AccessibilityLossRecord],
) -> dict[str, Any]:
    """Return small review-oriented counts for accessibility diagnostics."""

    route_ids = sorted({record.route_id for record in records})
    criticality_counts: dict[str, int] = {}
    for record in records:
        criticality_counts[record.criticality_class] = (
            criticality_counts.get(record.criticality_class, 0) + 1
        )
    disconnected_count = criticality_counts.get("disconnected", 0) + criticality_counts.get(
        "baseline_disconnected", 0
    )
    return {
        "diagnostics_ready": bool(records),
        "row_count": len(records),
        "route_count": len(route_ids),
        "route_ids": route_ids,
        "criticality_counts": dict(sorted(criticality_counts.items())),
        "disconnected_count": disconnected_count,
        "claim_scope": ACCESSIBILITY_CLAIM_SCOPE,
        "review_items": [
            "treat edge-removal impacts as scaffold route-fragility diagnostics, not calibrated outage probabilities",
            "review whether directed edge removal, bidirectional road-link removal, or corridor-level disruption matches the final study design",
            "combine these diagnostics with accepted graph-scale, road evidence, and validation gates before manuscript claims",
        ],
    }


def records_to_csv_rows(
    records: Sequence[AccessibilityLossRecord],
) -> tuple[dict[str, str], ...]:
    """Return accessibility records as stable CSV rows."""

    return tuple(record.as_csv_row() for record in records)


def classify_criticality(time_loss_min: float, time_loss_ratio: float) -> str:
    """Classify route loss into review-oriented severity classes."""

    if time_loss_min == float("inf") or time_loss_ratio == float("inf"):
        return "disconnected"
    if not isfinite(time_loss_min) or not isfinite(time_loss_ratio):
        return "unknown"
    if time_loss_min >= 10.0 or time_loss_ratio >= 0.50:
        return "high_time_loss"
    if time_loss_min >= 2.0 or time_loss_ratio >= 0.10:
        return "moderate_time_loss"
    return "low_time_loss"


def _road_mode_view(graph: nx.DiGraph) -> nx.DiGraph:
    road = nx.subgraph_view(
        graph,
        filter_edge=lambda u, v: graph.edges[u, v].get("mode") == "road",
    )
    return nx.DiGraph(road)


def _has_path(graph: nx.DiGraph, source: Any, target: Any) -> bool:
    try:
        return nx.has_path(graph, source, target)
    except (nx.NetworkXException, KeyError):
        return False


def _path_sum(graph: nx.DiGraph, path: Sequence[Any], attr: str) -> float:
    total = 0.0
    for u, v in zip(path, path[1:]):
        total += _finite_or_nan(graph.edges[u, v].get(attr))
    return total


def _ratio(numerator: float, denominator: float) -> float:
    if not isfinite(numerator):
        return numerator
    if not isfinite(denominator) or denominator == 0.0:
        return float("nan")
    return numerator / denominator


def _finite_or_nan(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return parsed if isfinite(parsed) else float("nan")


def _format_float(value: Any) -> str:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return ""
    if parsed == float("inf"):
        return "inf"
    if parsed == float("-inf"):
        return "-inf"
    if not isfinite(parsed):
        return ""
    return f"{parsed:.6f}".rstrip("0").rstrip(".")


__all__ = [
    "ACCESSIBILITY_CLAIM_SCOPE",
    "ACCESSIBILITY_CSV_FIELDS",
    "DEFAULT_ACCESSIBILITY_ROUTES",
    "AccessibilityLossRecord",
    "AccessibilityRoute",
    "classify_criticality",
    "evaluate_accessibility_loss",
    "evaluate_route_accessibility_loss",
    "records_to_csv_rows",
    "summarize_accessibility_loss",
]
