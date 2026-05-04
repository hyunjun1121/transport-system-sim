"""Readiness validation for real-world simulator graphs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import isfinite
from typing import Any

import networkx as nx


REQUIRED_EDGE_FIELDS = ("t0", "capacity", "p_fail", "base_p_fail", "mode")
DEFAULT_REQUIRED_NODE_IDS = {
    "assembly": "A",
    "destination": "D",
    "rail_access": "S",
    "rail_egress": "R",
}
DEFAULT_REQUIRED_ROUTES = (
    ("bus-only", "assembly", "destination"),
    ("multimodal access", "assembly", "rail_access"),
    ("multimodal last-mile", "rail_egress", "destination"),
)


@dataclass(frozen=True)
class GraphReadinessReport:
    """Structured result for simulator graph readiness checks."""

    ok: bool
    errors: tuple[str, ...]
    required_nodes: Mapping[str, Any]
    checked_routes: tuple[tuple[str, Any, Any], ...]

    def raise_for_errors(self) -> None:
        """Raise one actionable ValueError when validation failed."""

        if not self.ok:
            raise ValueError("Graph readiness validation failed:\n- " + "\n- ".join(self.errors))


def validate_graph_readiness(
    graph: nx.DiGraph,
    *,
    required_nodes: Mapping[str, Any] | Sequence[Any] | None = None,
    required_routes: Sequence[tuple[str, str, str] | tuple[Any, Any]] | None = None,
) -> GraphReadinessReport:
    """Validate that a graph can be used by the current scenario runner.

    The default contract checks canonical simulator nodes ``A``, ``D``, ``S``,
    and ``R`` plus road-mode routeability for ``A -> D``, ``A -> S``, and
    ``R -> D``. ``required_nodes`` can be a role mapping or a four-item sequence
    in ``(A, D, S, R)`` order.
    """

    node_ids = _normalize_required_nodes(required_nodes)
    routes = _normalize_required_routes(required_routes, node_ids)
    errors: list[str] = []

    errors.extend(_node_errors(graph, node_ids))
    errors.extend(_edge_errors(graph))
    errors.extend(_route_errors(graph, routes))

    return GraphReadinessReport(
        ok=not errors,
        errors=tuple(errors),
        required_nodes=dict(node_ids),
        checked_routes=tuple(routes),
    )


def assert_graph_ready(
    graph: nx.DiGraph,
    *,
    required_nodes: Mapping[str, Any] | Sequence[Any] | None = None,
    required_routes: Sequence[tuple[str, str, str] | tuple[Any, Any]] | None = None,
) -> None:
    """Raise ``ValueError`` unless ``graph`` satisfies simulator readiness."""

    validate_graph_readiness(
        graph,
        required_nodes=required_nodes,
        required_routes=required_routes,
    ).raise_for_errors()


def _normalize_required_nodes(
    required_nodes: Mapping[str, Any] | Sequence[Any] | None,
) -> dict[str, Any]:
    if required_nodes is None:
        return dict(DEFAULT_REQUIRED_NODE_IDS)

    if isinstance(required_nodes, Mapping):
        nodes = dict(DEFAULT_REQUIRED_NODE_IDS)
        aliases = {
            "A": "assembly",
            "D": "destination",
            "S": "rail_access",
            "R": "rail_egress",
        }
        for key, value in required_nodes.items():
            role = aliases.get(str(key), str(key))
            nodes[role] = value
        return nodes

    if isinstance(required_nodes, (str, bytes)) or len(required_nodes) != 4:
        raise ValueError("required_nodes must be a mapping or a four-item sequence")

    assembly, destination, rail_access, rail_egress = required_nodes
    return {
        "assembly": assembly,
        "destination": destination,
        "rail_access": rail_access,
        "rail_egress": rail_egress,
    }


def _normalize_required_routes(
    required_routes: Sequence[tuple[str, str, str] | tuple[Any, Any]] | None,
    node_ids: Mapping[str, Any],
) -> list[tuple[str, Any, Any]]:
    if required_routes is None:
        return [
            (label, node_ids[source_role], node_ids[target_role])
            for label, source_role, target_role in DEFAULT_REQUIRED_ROUTES
        ]

    routes: list[tuple[str, Any, Any]] = []
    for index, route in enumerate(required_routes):
        if len(route) == 2:
            source, target = route
            routes.append((f"route {index + 1}", source, target))
            continue
        if len(route) == 3:
            label, source, target = route
            routes.append((str(label), source, target))
            continue
        raise ValueError("required_routes entries must be (source, target) or (label, source, target)")
    return routes


def _node_errors(graph: nx.DiGraph, node_ids: Mapping[str, Any]) -> list[str]:
    missing = [
        f"{role}={node_id!r}"
        for role, node_id in node_ids.items()
        if node_id not in graph
    ]
    if not missing:
        return []
    return ["Missing required nodes: " + ", ".join(missing)]


def _edge_errors(graph: nx.DiGraph) -> list[str]:
    errors: list[str] = []
    for u, v, data in graph.edges(data=True):
        edge_label = _edge_label(u, v)
        missing = [field for field in REQUIRED_EDGE_FIELDS if field not in data]
        if missing:
            errors.append(
                f"Edge {edge_label} missing required fields: {', '.join(missing)}"
            )
            continue

        mode = data.get("mode")
        if not isinstance(mode, str) or not mode:
            errors.append(f"Edge {edge_label} has invalid mode: expected non-empty string, got {mode!r}")

        for field in ("t0", "capacity"):
            value = _finite_float(data.get(field))
            if value is None or value <= 0.0:
                errors.append(
                    f"Edge {edge_label} has invalid {field}: "
                    f"must be positive and finite, got {data.get(field)!r}"
                )

        for field in ("p_fail", "base_p_fail"):
            value = _finite_float(data.get(field))
            if value is None or not 0.0 <= value <= 1.0:
                errors.append(
                    f"Edge {edge_label} has invalid {field}: "
                    f"must satisfy 0 <= p <= 1, got {data.get(field)!r}"
                )
    return errors


def _route_errors(
    graph: nx.DiGraph,
    routes: Sequence[tuple[str, Any, Any]],
) -> list[str]:
    errors: list[str] = []
    road_graph = nx.subgraph_view(
        graph,
        filter_edge=lambda u, v: graph.edges[u, v].get("mode") == "road",
    )
    for label, source, target in routes:
        missing = [node for node in (source, target) if node not in graph]
        if missing:
            errors.append(
                f"Cannot check {label} road-mode route {source!r} -> {target!r}: "
                f"missing node(s) {', '.join(repr(node) for node in missing)}"
            )
            continue
        try:
            has_path = nx.has_path(road_graph, source, target)
        except nx.NodeNotFound:
            has_path = False
        if not has_path:
            errors.append(
                f"Disconnected road-mode segment for {label}: "
                f"no route {source!r} -> {target!r}"
            )
    return errors


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


def _edge_label(u: Any, v: Any) -> str:
    return f"{u!r}->{v!r}"


validate_simulator_graph = validate_graph_readiness
assert_simulator_graph_ready = assert_graph_ready


__all__ = [
    "DEFAULT_REQUIRED_NODE_IDS",
    "DEFAULT_REQUIRED_ROUTES",
    "GraphReadinessReport",
    "REQUIRED_EDGE_FIELDS",
    "assert_graph_ready",
    "assert_simulator_graph_ready",
    "validate_graph_readiness",
    "validate_simulator_graph",
]
