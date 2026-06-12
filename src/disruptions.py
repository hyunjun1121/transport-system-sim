"""Structured edge disruption sampling.

This module keeps disruption state separate from traffic calculations so both
legacy blocked-edge code and future capacity-aware traversal can consume the
same sampled state.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

import networkx as nx
import numpy as np

from src.sim_types import EdgeDisruption, require_non_negative


Edge = tuple[str, str]
DisruptionMode = Literal["blocked", "capacity_reduction"]
DisruptionMap = Mapping[Edge, EdgeDisruption]


def sample_edge_disruptions(
    G: nx.DiGraph,
    p_fail_scale: float,
    rng: np.random.Generator,
    *,
    mode: DisruptionMode = "blocked",
    capacity_reduction_factor: float = 0.5,
    rail_immune: bool = True,
) -> dict[Edge, EdgeDisruption]:
    """Sample per-edge disruptions using scaled Bernoulli probabilities.

    The sampled probability for each eligible edge is
    ``min(edge.p_fail * p_fail_scale, 1.0)``. Rail edges are normal by default
    and do not consume random draws unless ``rail_immune`` is disabled.
    """
    _validate_mode(mode)
    p_fail_scale = _validate_scale(p_fail_scale)
    if mode == "none":
        return {(u, v): EdgeDisruption() for u, v in G.edges()}
    if mode == "capacity_reduction":
        capacity_reduction_factor = _validate_capacity_reduction_factor(
            capacity_reduction_factor
        )

    disruptions: dict[Edge, EdgeDisruption] = {}
    for u, v, data in G.edges(data=True):
        edge = (u, v)
        if rail_immune and data.get("mode") == "rail":
            disruptions[edge] = EdgeDisruption()
            continue

        probability = scaled_failure_probability(data, p_fail_scale)
        if rng.random() < probability:
            disruptions[edge] = _disrupted_state(mode, capacity_reduction_factor)
        else:
            disruptions[edge] = EdgeDisruption()

    return disruptions


def sample_disruptions(
    G: nx.DiGraph,
    p_fail_scale: float,
    rng: np.random.Generator,
    *,
    mode: DisruptionMode = "blocked",
    capacity_reduction_factor: float = 0.5,
    rail_immune: bool = True,
) -> dict[Edge, EdgeDisruption]:
    """Alias for ``sample_edge_disruptions`` with a shorter public name."""
    return sample_edge_disruptions(
        G,
        p_fail_scale,
        rng,
        mode=mode,
        capacity_reduction_factor=capacity_reduction_factor,
        rail_immune=rail_immune,
    )


def scaled_failure_probability(edge_data: Mapping[str, object], p_fail_scale: float) -> float:
    """Return ``p_fail`` multiplied by scale and clipped to ``[0, 1]``."""
    p_fail_scale = _validate_scale(p_fail_scale)
    base_probability = require_non_negative(
        float(edge_data.get("p_fail", 0.0)),
        "edge p_fail",
    )
    return max(0.0, min(base_probability * p_fail_scale, 1.0))


def blocked_edges(disruptions: DisruptionMap) -> list[Edge]:
    """Return edges whose structured disruption state is blocked."""
    return [edge for edge, disruption in disruptions.items() if disruption.is_blocked]


def get_edge_disruption(
    disruptions: DisruptionMap,
    edge: Edge,
) -> EdgeDisruption:
    """Return an edge disruption, defaulting missing edges to normal."""
    return disruptions.get(edge, EdgeDisruption())


def is_edge_blocked(disruptions: DisruptionMap, edge: Edge) -> bool:
    """Return whether an edge is blocked in a disruption map."""
    return get_edge_disruption(disruptions, edge).is_blocked


def is_blocked(
    disruption: EdgeDisruption | DisruptionMap | None,
    edge: Edge | None = None,
) -> bool:
    """Return whether a disruption or a mapped edge is blocked."""
    if edge is not None:
        if isinstance(disruption, Mapping):
            return is_edge_blocked(disruption, edge)
        return False
    return isinstance(disruption, EdgeDisruption) and disruption.is_blocked


def effective_capacity(
    base_capacity: float,
    disruption: EdgeDisruption | None = None,
) -> float:
    """Return capacity after applying a disruption state."""
    base_capacity = require_non_negative(base_capacity, "base_capacity")
    if disruption is None:
        return base_capacity
    if disruption.is_blocked:
        return 0.0
    return max(0.0, base_capacity * disruption.capacity_factor)


def edge_effective_capacity(
    G: nx.DiGraph,
    disruptions: DisruptionMap,
    edge: Edge,
    *,
    capacity_attr: str = "capacity",
) -> float:
    """Return effective capacity for an edge in a graph."""
    return effective_capacity(
        float(G.edges[edge].get(capacity_attr, 0.0)),
        get_edge_disruption(disruptions, edge),
    )


def _disrupted_state(
    mode: DisruptionMode,
    capacity_reduction_factor: float,
) -> EdgeDisruption:
    if mode == "blocked":
        return EdgeDisruption(status="blocked", capacity_factor=0.0)
    return EdgeDisruption(
        status="degraded",
        capacity_factor=capacity_reduction_factor,
    )


def _validate_mode(mode: str) -> None:
    if mode not in {"blocked", "capacity_reduction", "none"}:
        raise ValueError(
            "failure mode must be 'blocked', 'capacity_reduction', or 'none', "
            f"got {mode!r}"
        )


def _validate_scale(p_fail_scale: float) -> float:
    return require_non_negative(p_fail_scale, "p_fail_scale")


def _validate_capacity_reduction_factor(capacity_reduction_factor: float) -> float:
    capacity_reduction_factor = require_non_negative(
        capacity_reduction_factor,
        "capacity_reduction_factor",
    )
    if not 0.0 < capacity_reduction_factor <= 1.0:
        raise ValueError(
            "capacity_reduction_factor must satisfy 0 < factor <= 1, "
            f"got {capacity_reduction_factor!r}"
        )
    return capacity_reduction_factor


def _node_coordinates(
    graph: nx.DiGraph,
) -> dict[str, tuple[float, float] | None]:
    """Extract (x, y) coordinates from graph nodes, returning None for missing."""

    coords: dict[str, tuple[float, float] | None] = {}
    for node in graph.nodes:
        data = graph.nodes[node]
        x = data.get("x")
        y = data.get("y")
        if x is not None and y is not None:
            try:
                coords[node] = (float(x), float(y))
            except (TypeError, ValueError):
                coords[node] = None
        else:
            coords[node] = None
    return coords


def _edge_endpoint_distances_sq(
    graph: nx.DiGraph,
    edge_u: Edge,
    edge_v: Edge,
    coords: dict[str, tuple[float, float] | None],
) -> list[float]:
    """Return squared distances between all endpoint pairs of two edges."""

    distances: list[float] = []
    for node_a in edge_u:
        ca = coords.get(node_a)
        if ca is None:
            continue
        for node_b in edge_v:
            cb = coords.get(node_b)
            if cb is None:
                continue
            dx = ca[0] - cb[0]
            dy = ca[1] - cb[1]
            distances.append(dx * dx + dy * dy)
    return distances


def _build_neighbor_index(
    graph: nx.DiGraph,
    radius_m: float,
    coords: dict[str, tuple[float, float] | None],
) -> dict[Edge, list[Edge]]:
    """Build a spatial neighbor index mapping each edge to nearby edges.

    Two edges are neighbors if any pair of their endpoints is within
    ``radius_m`` meters.  Edges whose endpoints lack coordinates have no
    neighbors.
    """

    radius_sq = radius_m * radius_m
    edges = [(u, v) for u, v in graph.edges()]
    neighbor_index: dict[Edge, list[Edge]] = {edge: [] for edge in edges}

    for i, edge_i in enumerate(edges):
        for j in range(i + 1, len(edges)):
            edge_j = edges[j]
            dists = _edge_endpoint_distances_sq(graph, edge_i, edge_j, coords)
            if any(d <= radius_sq for d in dists):
                neighbor_index[edge_i].append(edge_j)
                neighbor_index[edge_j].append(edge_i)

    return neighbor_index


def sample_correlated_failures(
    G: nx.DiGraph,
    p_fail_scale: float,
    rng: np.random.Generator,
    *,
    mode: DisruptionMode = "blocked",
    capacity_reduction_factor: float = 0.5,
    rail_immune: bool = True,
    correlation_radius_m: float = 0.0,
    correlation_strength: float = 1.0,
) -> dict[Edge, EdgeDisruption]:
    """Sample disruptions with optional spatial correlation between nearby edges.

    When ``correlation_radius_m`` is zero, behavior is identical to
    :func:`sample_edge_disruptions`.  When positive, edges whose endpoints
    are within the radius share a latent normal field that boosts the failure
    probability of geographically close edges.

    The correlated probability for edge ``(u, v)`` is::

        p_base = min(edge_base_p_fail * p_fail_scale, 1.0)
        field_u = latent_field[u]   # shared across all edges touching u
        field_v = latent_field[v]   # shared across all edges touching v
        correlation_boost = max(0, (field_u + field_v) / 2) * correlation_strength
        p_correlated = min(p_base + correlation_boost, 1.0)
    """

    _validate_mode(mode)
    p_fail_scale = _validate_scale(p_fail_scale)
    if mode == "capacity_reduction":
        capacity_reduction_factor = _validate_capacity_reduction_factor(
            capacity_reduction_factor
        )

    correlation_radius_m = _validate_correlation_radius(correlation_radius_m)
    correlation_strength = _validate_correlation_strength(correlation_strength)

    if correlation_radius_m <= 0.0:
        return sample_edge_disruptions(
            G,
            p_fail_scale,
            rng,
            mode=mode,
            capacity_reduction_factor=capacity_reduction_factor,
            rail_immune=rail_immune,
        )

    coords = _node_coordinates(G)
    latent_field: dict[str, float] = {
        node: rng.normal(0.0, 1.0) for node in G.nodes
    }

    disruptions: dict[Edge, EdgeDisruption] = {}
    for u, v, data in G.edges(data=True):
        edge = (u, v)
        if rail_immune and data.get("mode") == "rail":
            disruptions[edge] = EdgeDisruption()
            continue

        p_base = scaled_failure_probability(data, p_fail_scale)
        field_u = latent_field.get(u, 0.0)
        field_v = latent_field.get(v, 0.0)
        correlation_boost = max(0.0, (field_u + field_v) / 2.0) * correlation_strength
        p_correlated = max(0.0, min(p_base + correlation_boost, 1.0))

        if rng.random() < p_correlated:
            disruptions[edge] = _disrupted_state(mode, capacity_reduction_factor)
        else:
            disruptions[edge] = EdgeDisruption()

    return disruptions


def _validate_correlation_radius(value: float) -> float:
    value = _validate_scale(value)
    return value


def _validate_correlation_strength(value: float) -> float:
    return _validate_scale(value)


sample_link_disruptions = sample_edge_disruptions
failed_edges = blocked_edges
edge_is_blocked = is_edge_blocked
get_effective_capacity = effective_capacity


__all__ = [
    "Edge",
    "DisruptionMode",
    "DisruptionMap",
    "sample_edge_disruptions",
    "sample_disruptions",
    "scaled_failure_probability",
    "blocked_edges",
    "get_edge_disruption",
    "is_edge_blocked",
    "is_blocked",
    "effective_capacity",
    "edge_effective_capacity",
    "sample_correlated_failures",
    "sample_link_disruptions",
    "failed_edges",
    "edge_is_blocked",
    "get_effective_capacity",
]
