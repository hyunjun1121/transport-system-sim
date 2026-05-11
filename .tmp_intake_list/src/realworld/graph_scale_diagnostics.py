"""Graph-scale diagnostics for reduced pilot analysis corridors.

These helpers compare baseline road routes on the full bus-practical simulator
graph and the reduced analysis graph. They support graph-scale review, but they
do not accept a corridor abstraction as a final publication method.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from itertools import islice
from typing import Any, Iterable, Mapping, Sequence

import networkx as nx

from src.realworld.plausibility import DEFAULT_ROUTE_CHECKS, RouteCheck


GRAPH_SCALE_DIAGNOSTIC_SCOPE = (
    "graph_scale_route_parity_scaffold_not_graph_scale_acceptance"
)
GRAPH_SCALE_ALTERNATE_ROUTE_SCOPE = (
    "graph_scale_alternate_route_sensitivity_scaffold_not_graph_scale_acceptance"
)

GRAPH_SCALE_CSV_FIELDS: tuple[str, ...] = (
    "region_id",
    "route_check_id",
    "route_label",
    "source",
    "target",
    "full_graph_nodes",
    "full_graph_edges",
    "analysis_graph_nodes",
    "analysis_graph_edges",
    "analysis_graph_reduced",
    "full_route_available",
    "analysis_route_available",
    "full_time_path_nodes",
    "analysis_time_path_nodes",
    "full_time_path_edges",
    "analysis_time_path_edges",
    "full_time_min",
    "analysis_time_min",
    "time_delta_min",
    "time_ratio",
    "full_distance_m",
    "analysis_distance_m",
    "distance_delta_m",
    "distance_ratio",
    "full_time_path_edge_coverage",
    "full_distance_path_edge_coverage",
    "status",
    "claim_scope",
    "notes",
)

GRAPH_SCALE_ALTERNATE_ROUTE_CSV_FIELDS: tuple[str, ...] = (
    "region_id",
    "route_check_id",
    "route_label",
    "source",
    "target",
    "full_graph_nodes",
    "full_graph_edges",
    "analysis_graph_nodes",
    "analysis_graph_edges",
    "analysis_graph_reduced",
    "requested_path_count",
    "full_route_rank",
    "full_path_available",
    "analysis_route_available",
    "exact_full_path_present_in_analysis",
    "full_path_nodes",
    "full_path_edges",
    "full_time_min",
    "full_distance_m",
    "edge_coverage_in_analysis",
    "analysis_shortest_time_min",
    "analysis_shortest_distance_m",
    "analysis_shortest_time_ratio_to_full_path",
    "status",
    "claim_scope",
    "notes",
)

PASS = "pass"
WARN = "warn"
FAIL = "fail"


@dataclass(frozen=True)
class GraphScaleRouteComparison:
    """One full-graph versus reduced-graph route comparison row."""

    region_id: str
    route_check_id: str
    route_label: str
    source: Any
    target: Any
    full_graph_nodes: int
    full_graph_edges: int
    analysis_graph_nodes: int
    analysis_graph_edges: int
    analysis_graph_reduced: bool
    full_route_available: bool
    analysis_route_available: bool
    full_time_path: tuple[Any, ...]
    analysis_time_path: tuple[Any, ...]
    full_time_min: float
    analysis_time_min: float
    full_distance_m: float
    analysis_distance_m: float
    full_time_path_edge_coverage: float
    full_distance_path_edge_coverage: float
    status: str
    notes: str
    claim_scope: str = GRAPH_SCALE_DIAGNOSTIC_SCOPE

    @property
    def time_delta_min(self) -> float:
        """Return reduced-minus-full free-flow time delta."""

        return _delta(self.analysis_time_min, self.full_time_min)

    @property
    def time_ratio(self) -> float:
        """Return reduced/full free-flow time ratio."""

        return _ratio(self.analysis_time_min, self.full_time_min)

    @property
    def distance_delta_m(self) -> float:
        """Return reduced-minus-full route distance delta."""

        return _delta(self.analysis_distance_m, self.full_distance_m)

    @property
    def distance_ratio(self) -> float:
        """Return reduced/full route distance ratio."""

        return _ratio(self.analysis_distance_m, self.full_distance_m)

    def as_csv_row(self) -> dict[str, str]:
        """Return this comparison using the stable CSV schema."""

        values = {
            "region_id": self.region_id,
            "route_check_id": self.route_check_id,
            "route_label": self.route_label,
            "source": str(self.source),
            "target": str(self.target),
            "full_graph_nodes": str(self.full_graph_nodes),
            "full_graph_edges": str(self.full_graph_edges),
            "analysis_graph_nodes": str(self.analysis_graph_nodes),
            "analysis_graph_edges": str(self.analysis_graph_edges),
            "analysis_graph_reduced": str(self.analysis_graph_reduced).lower(),
            "full_route_available": str(self.full_route_available).lower(),
            "analysis_route_available": str(self.analysis_route_available).lower(),
            "full_time_path_nodes": ">".join(str(node) for node in self.full_time_path),
            "analysis_time_path_nodes": ">".join(
                str(node) for node in self.analysis_time_path
            ),
            "full_time_path_edges": str(max(len(self.full_time_path) - 1, 0)),
            "analysis_time_path_edges": str(max(len(self.analysis_time_path) - 1, 0)),
            "full_time_min": _format_float(self.full_time_min),
            "analysis_time_min": _format_float(self.analysis_time_min),
            "time_delta_min": _format_float(self.time_delta_min),
            "time_ratio": _format_float(self.time_ratio),
            "full_distance_m": _format_float(self.full_distance_m),
            "analysis_distance_m": _format_float(self.analysis_distance_m),
            "distance_delta_m": _format_float(self.distance_delta_m),
            "distance_ratio": _format_float(self.distance_ratio),
            "full_time_path_edge_coverage": _format_float(
                self.full_time_path_edge_coverage
            ),
            "full_distance_path_edge_coverage": _format_float(
                self.full_distance_path_edge_coverage
            ),
            "status": self.status,
            "claim_scope": self.claim_scope,
            "notes": self.notes,
        }
        return {field: values[field] for field in GRAPH_SCALE_CSV_FIELDS}


@dataclass(frozen=True)
class GraphScaleAlternateRouteComparison:
    """One full-graph alternate-route coverage row."""

    region_id: str
    route_check_id: str
    route_label: str
    source: Any
    target: Any
    full_graph_nodes: int
    full_graph_edges: int
    analysis_graph_nodes: int
    analysis_graph_edges: int
    analysis_graph_reduced: bool
    requested_path_count: int
    full_route_rank: int
    full_path: tuple[Any, ...]
    analysis_route_available: bool
    exact_full_path_present_in_analysis: bool
    full_time_min: float
    full_distance_m: float
    edge_coverage_in_analysis: float
    analysis_shortest_time_min: float
    analysis_shortest_distance_m: float
    status: str
    notes: str
    claim_scope: str = GRAPH_SCALE_ALTERNATE_ROUTE_SCOPE

    @property
    def full_path_available(self) -> bool:
        """Return whether a full-graph candidate route exists."""

        return bool(self.full_path)

    @property
    def analysis_shortest_time_ratio_to_full_path(self) -> float:
        """Return analysis shortest-time route divided by this full-path time."""

        return _ratio(self.analysis_shortest_time_min, self.full_time_min)

    def as_csv_row(self) -> dict[str, str]:
        """Return this alternate-route comparison using the stable CSV schema."""

        values = {
            "region_id": self.region_id,
            "route_check_id": self.route_check_id,
            "route_label": self.route_label,
            "source": str(self.source),
            "target": str(self.target),
            "full_graph_nodes": str(self.full_graph_nodes),
            "full_graph_edges": str(self.full_graph_edges),
            "analysis_graph_nodes": str(self.analysis_graph_nodes),
            "analysis_graph_edges": str(self.analysis_graph_edges),
            "analysis_graph_reduced": str(self.analysis_graph_reduced).lower(),
            "requested_path_count": str(self.requested_path_count),
            "full_route_rank": str(self.full_route_rank),
            "full_path_available": str(self.full_path_available).lower(),
            "analysis_route_available": str(self.analysis_route_available).lower(),
            "exact_full_path_present_in_analysis": str(
                self.exact_full_path_present_in_analysis
            ).lower(),
            "full_path_nodes": ">".join(str(node) for node in self.full_path),
            "full_path_edges": str(max(len(self.full_path) - 1, 0)),
            "full_time_min": _format_float(self.full_time_min),
            "full_distance_m": _format_float(self.full_distance_m),
            "edge_coverage_in_analysis": _format_float(
                self.edge_coverage_in_analysis
            ),
            "analysis_shortest_time_min": _format_float(
                self.analysis_shortest_time_min
            ),
            "analysis_shortest_distance_m": _format_float(
                self.analysis_shortest_distance_m
            ),
            "analysis_shortest_time_ratio_to_full_path": _format_float(
                self.analysis_shortest_time_ratio_to_full_path
            ),
            "status": self.status,
            "claim_scope": self.claim_scope,
            "notes": self.notes,
        }
        return {
            field: values[field] for field in GRAPH_SCALE_ALTERNATE_ROUTE_CSV_FIELDS
        }


def compare_graph_scale_routes(
    full_graph: nx.DiGraph,
    analysis_graph: nx.DiGraph,
    *,
    region_id: str | None = None,
    routes: Sequence[RouteCheck] = DEFAULT_ROUTE_CHECKS,
) -> tuple[GraphScaleRouteComparison, ...]:
    """Compare canonical road routes between full and reduced graphs."""

    resolved_region_id = region_id or str(
        full_graph.graph.get(
            "region_id",
            analysis_graph.graph.get("region_id", "unknown_region"),
        )
    )
    full_road = _road_mode_view(full_graph)
    analysis_road = _road_mode_view(analysis_graph)
    records = [
        _compare_route(
            full_road,
            analysis_road,
            full_graph=full_graph,
            analysis_graph=analysis_graph,
            region_id=resolved_region_id,
            route=route,
        )
        for route in routes
    ]
    return tuple(records)


def compare_graph_scale_alternate_routes(
    full_graph: nx.DiGraph,
    analysis_graph: nx.DiGraph,
    *,
    region_id: str | None = None,
    routes: Sequence[RouteCheck] = DEFAULT_ROUTE_CHECKS,
    path_count: int = 3,
) -> tuple[GraphScaleAlternateRouteComparison, ...]:
    """Compare top full-graph alternate routes against the reduced graph.

    Rows are generated from the full bus-practical graph. The reduced graph is
    then checked for exact edge preservation and route availability. This is a
    sensitivity diagnostic for graph-scale review, not acceptance evidence.
    """

    if path_count < 1:
        raise ValueError("path_count must be at least 1")
    resolved_region_id = region_id or str(
        full_graph.graph.get(
            "region_id",
            analysis_graph.graph.get("region_id", "unknown_region"),
        )
    )
    full_road = _road_mode_view(full_graph)
    analysis_road = _road_mode_view(analysis_graph)
    records: list[GraphScaleAlternateRouteComparison] = []
    for route in routes:
        analysis_time_path = _shortest_path(
            analysis_road,
            route.source,
            route.target,
            "t0",
        )
        analysis_available = bool(analysis_time_path)
        analysis_time = _path_sum(analysis_road, analysis_time_path, "t0")
        analysis_distance = _path_sum(analysis_road, analysis_time_path, "length_m")
        full_paths = _shortest_simple_paths(
            full_road,
            route.source,
            route.target,
            "t0",
            path_count,
        )
        for rank, full_path in enumerate(full_paths, start=1):
            exact_present = _path_edges_present(analysis_graph, full_path)
            coverage = _edge_coverage(analysis_graph, full_path)
            status = _alternate_route_status(
                rank=rank,
                analysis_available=analysis_available,
                exact_present=exact_present,
            )
            records.append(
                GraphScaleAlternateRouteComparison(
                    region_id=resolved_region_id,
                    route_check_id=route.check_id,
                    route_label=route.label,
                    source=route.source,
                    target=route.target,
                    full_graph_nodes=full_graph.number_of_nodes(),
                    full_graph_edges=full_graph.number_of_edges(),
                    analysis_graph_nodes=analysis_graph.number_of_nodes(),
                    analysis_graph_edges=analysis_graph.number_of_edges(),
                    analysis_graph_reduced=bool(
                        analysis_graph.graph.get("experiment_subgraph", False)
                    ),
                    requested_path_count=path_count,
                    full_route_rank=rank,
                    full_path=full_path,
                    analysis_route_available=analysis_available,
                    exact_full_path_present_in_analysis=exact_present,
                    full_time_min=_path_sum(full_road, full_path, "t0"),
                    full_distance_m=_path_sum(full_road, full_path, "length_m"),
                    edge_coverage_in_analysis=coverage,
                    analysis_shortest_time_min=analysis_time,
                    analysis_shortest_distance_m=analysis_distance,
                    status=status,
                    notes=_alternate_notes(status, rank),
                )
            )
    return tuple(records)


def summarize_graph_scale_route_comparisons(
    records: Iterable[GraphScaleRouteComparison],
) -> dict[str, Any]:
    """Return conservative summary values for graph-scale route diagnostics."""

    rows = tuple(records)
    status_counts = {PASS: 0, WARN: 0, FAIL: 0}
    for row in rows:
        status_counts[row.status] = status_counts.get(row.status, 0) + 1
    route_count = len(rows)
    exact_time_matches = sum(1 for row in rows if row.status == PASS)
    return {
        "row_count": route_count,
        "route_count": route_count,
        "status_counts": status_counts,
        "exact_time_path_match_count": exact_time_matches,
        "all_routes_available": all(
            row.full_route_available and row.analysis_route_available for row in rows
        ),
        "all_time_paths_preserved": all(
            _near(row.full_time_path_edge_coverage, 1.0) for row in rows
        ),
        "all_distance_paths_preserved": all(
            _near(row.full_distance_path_edge_coverage, 1.0) for row in rows
        ),
        "claim_scope": GRAPH_SCALE_DIAGNOSTIC_SCOPE,
        "review_items": [
            "confirm whether baseline shortest-route parity is sufficient for a corridor abstraction",
            "review alternate corridor sensitivity before graph-scale acceptance",
            "rerun this diagnostic after any OSM cache, connector, or road-class override change",
            "do not use this diagnostic as final graph-scale acceptance by itself",
        ],
    }


def summarize_graph_scale_alternate_route_comparisons(
    records: Iterable[GraphScaleAlternateRouteComparison],
) -> dict[str, Any]:
    """Return conservative summary values for alternate-route diagnostics."""

    rows = tuple(records)
    status_counts = {PASS: 0, WARN: 0, FAIL: 0}
    for row in rows:
        status_counts[row.status] = status_counts.get(row.status, 0) + 1
    rank_one_rows = [row for row in rows if row.full_route_rank == 1]
    non_rank_one_rows = [row for row in rows if row.full_route_rank > 1]
    coverage_values = [
        row.edge_coverage_in_analysis
        for row in rows
        if _finite_float(row.edge_coverage_in_analysis) is not None
    ]
    return {
        "row_count": len(rows),
        "route_count": len({row.route_check_id for row in rows}),
        "requested_path_count": max(
            (row.requested_path_count for row in rows),
            default=0,
        ),
        "status_counts": status_counts,
        "rank_one_path_count": len(rank_one_rows),
        "rank_one_exact_preserved_count": sum(
            1 for row in rank_one_rows if row.exact_full_path_present_in_analysis
        ),
        "alternate_path_count": len(non_rank_one_rows),
        "alternate_exact_preserved_count": sum(
            1 for row in non_rank_one_rows if row.exact_full_path_present_in_analysis
        ),
        "min_edge_coverage_in_analysis": (
            min(coverage_values) if coverage_values else float("nan")
        ),
        "all_analysis_routes_available": all(
            row.analysis_route_available for row in rows
        ),
        "all_rank_one_paths_preserved": all(
            row.exact_full_path_present_in_analysis for row in rank_one_rows
        ),
        "all_alternate_paths_preserved": bool(non_rank_one_rows)
        and all(row.exact_full_path_present_in_analysis for row in non_rank_one_rows),
        "claim_scope": GRAPH_SCALE_ALTERNATE_ROUTE_SCOPE,
        "review_items": [
            "use this table to decide whether the reduced corridor omits important alternate routes",
            "treat missing alternate paths as graph-scale uncertainty, not operational failure evidence",
            "add full-graph runtime or multi-corridor experiments if omitted alternates affect claims",
            "do not use this diagnostic as final graph-scale acceptance by itself",
        ],
    }


def graph_scale_records_to_csv_rows(
    records: Iterable[GraphScaleRouteComparison],
) -> tuple[dict[str, str], ...]:
    """Convert graph-scale comparison records to CSV-ready dictionaries."""

    return tuple(record.as_csv_row() for record in records)


def graph_scale_alternate_records_to_csv_rows(
    records: Iterable[GraphScaleAlternateRouteComparison],
) -> tuple[dict[str, str], ...]:
    """Convert alternate-route comparison records to CSV-ready dictionaries."""

    return tuple(record.as_csv_row() for record in records)


def _compare_route(
    full_road: nx.DiGraph,
    analysis_road: nx.DiGraph,
    *,
    full_graph: nx.DiGraph,
    analysis_graph: nx.DiGraph,
    region_id: str,
    route: RouteCheck,
) -> GraphScaleRouteComparison:
    full_time_path = _shortest_path(full_road, route.source, route.target, "t0")
    analysis_time_path = _shortest_path(
        analysis_road,
        route.source,
        route.target,
        "t0",
    )
    full_distance_path = _shortest_path(
        full_road,
        route.source,
        route.target,
        "length_m",
    )
    full_available = bool(full_time_path)
    analysis_available = bool(analysis_time_path)

    full_time = _path_sum(full_road, full_time_path, "t0")
    analysis_time = _path_sum(analysis_road, analysis_time_path, "t0")
    full_distance = _path_sum(full_road, full_time_path, "length_m")
    analysis_distance = _path_sum(analysis_road, analysis_time_path, "length_m")
    time_path_coverage = _edge_coverage(analysis_graph, full_time_path)
    distance_path_coverage = _edge_coverage(analysis_graph, full_distance_path)
    status = _comparison_status(
        full_available=full_available,
        analysis_available=analysis_available,
        time_delta=_delta(analysis_time, full_time),
        distance_delta=_delta(analysis_distance, full_distance),
        time_path_coverage=time_path_coverage,
    )
    return GraphScaleRouteComparison(
        region_id=region_id,
        route_check_id=route.check_id,
        route_label=route.label,
        source=route.source,
        target=route.target,
        full_graph_nodes=full_graph.number_of_nodes(),
        full_graph_edges=full_graph.number_of_edges(),
        analysis_graph_nodes=analysis_graph.number_of_nodes(),
        analysis_graph_edges=analysis_graph.number_of_edges(),
        analysis_graph_reduced=bool(
            analysis_graph.graph.get("experiment_subgraph", False)
        ),
        full_route_available=full_available,
        analysis_route_available=analysis_available,
        full_time_path=full_time_path,
        analysis_time_path=analysis_time_path,
        full_time_min=full_time,
        analysis_time_min=analysis_time,
        full_distance_m=full_distance,
        analysis_distance_m=analysis_distance,
        full_time_path_edge_coverage=time_path_coverage,
        full_distance_path_edge_coverage=distance_path_coverage,
        status=status,
        notes=_notes(status),
    )


def _road_mode_view(graph: nx.DiGraph) -> nx.DiGraph:
    return nx.subgraph_view(
        graph,
        filter_edge=lambda u, v: graph.edges[u, v].get("mode") == "road",
    )


def _shortest_path(
    graph: nx.DiGraph,
    source: Any,
    target: Any,
    weight: str,
) -> tuple[Any, ...]:
    try:
        return tuple(nx.shortest_path(graph, source, target, weight=weight))
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return ()


def _shortest_simple_paths(
    graph: nx.DiGraph,
    source: Any,
    target: Any,
    weight: str,
    path_count: int,
) -> tuple[tuple[Any, ...], ...]:
    try:
        paths = nx.shortest_simple_paths(graph, source, target, weight=weight)
        return tuple(tuple(path) for path in islice(paths, path_count))
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return ()


def _path_sum(graph: nx.DiGraph, path: Sequence[Any], attr: str) -> float:
    if len(path) < 2:
        return float("nan")
    total = 0.0
    for u, v in zip(path, path[1:]):
        value = _finite_float(graph.edges[u, v].get(attr))
        if value is None:
            return float("nan")
        total += value
    return total


def _edge_coverage(graph: nx.DiGraph, path: Sequence[Any]) -> float:
    edges = tuple(zip(path, path[1:]))
    if not edges:
        return float("nan")
    present = sum(1 for edge in edges if graph.has_edge(*edge))
    return present / len(edges)


def _path_edges_present(graph: nx.DiGraph, path: Sequence[Any]) -> bool:
    edges = tuple(zip(path, path[1:]))
    return bool(edges) and all(graph.has_edge(*edge) for edge in edges)


def _comparison_status(
    *,
    full_available: bool,
    analysis_available: bool,
    time_delta: float,
    distance_delta: float,
    time_path_coverage: float,
) -> str:
    if not full_available or not analysis_available:
        return FAIL
    if (
        _near(time_delta, 0.0)
        and _near(distance_delta, 0.0)
        and _near(time_path_coverage, 1.0)
    ):
        return PASS
    return WARN


def _notes(status: str) -> str:
    if status == PASS:
        return (
            "baseline shortest-time route is preserved in the reduced analysis "
            "graph; this still does not review alternate corridor sensitivity"
        )
    if status == WARN:
        return (
            "route remains available but reduced graph differs from full graph; "
            "review before accepting a corridor abstraction"
        )
    return (
        "route unavailable in full or reduced graph; graph-scale method is not "
        "ready for final claims"
    )


def _alternate_route_status(
    *,
    rank: int,
    analysis_available: bool,
    exact_present: bool,
) -> str:
    if not analysis_available:
        return FAIL
    if exact_present:
        return PASS
    return WARN if rank > 1 else FAIL


def _alternate_notes(status: str, rank: int) -> str:
    if status == PASS:
        if rank == 1:
            return (
                "full-graph shortest-time path is exactly present in the reduced "
                "analysis graph"
            )
        return (
            "full-graph alternate path is exactly present in the reduced analysis "
            "graph"
        )
    if status == WARN:
        return (
            "full-graph alternate path is not exactly present in the reduced "
            "analysis graph; treat as corridor-abstraction uncertainty"
        )
    return (
        "route is unavailable or the full-graph shortest path is missing from "
        "the reduced analysis graph"
    )


def _delta(left: float, right: float) -> float:
    if _finite_float(left) is None or _finite_float(right) is None:
        return float("nan")
    return left - right


def _ratio(numerator: float, denominator: float) -> float:
    parsed_numerator = _finite_float(numerator)
    parsed_denominator = _finite_float(denominator)
    if (
        parsed_numerator is None
        or parsed_denominator is None
        or parsed_denominator <= 0.0
    ):
        return float("nan")
    return parsed_numerator / parsed_denominator


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


def _near(left: float, right: float, *, tolerance: float = 1e-6) -> bool:
    parsed_left = _finite_float(left)
    parsed_right = _finite_float(right)
    if parsed_left is None or parsed_right is None:
        return False
    return abs(parsed_left - parsed_right) <= tolerance


def _format_float(value: float) -> str:
    parsed = _finite_float(value)
    if parsed is None:
        return ""
    return f"{parsed:.6f}"


__all__ = [
    "FAIL",
    "GRAPH_SCALE_ALTERNATE_ROUTE_CSV_FIELDS",
    "GRAPH_SCALE_ALTERNATE_ROUTE_SCOPE",
    "GRAPH_SCALE_CSV_FIELDS",
    "GRAPH_SCALE_DIAGNOSTIC_SCOPE",
    "PASS",
    "WARN",
    "GraphScaleAlternateRouteComparison",
    "GraphScaleRouteComparison",
    "compare_graph_scale_alternate_routes",
    "compare_graph_scale_routes",
    "graph_scale_alternate_records_to_csv_rows",
    "graph_scale_records_to_csv_rows",
    "summarize_graph_scale_alternate_route_comparisons",
    "summarize_graph_scale_route_comparisons",
]
