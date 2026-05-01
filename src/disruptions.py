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
    if mode not in {"blocked", "capacity_reduction"}:
        raise ValueError(
            "failure mode must be 'blocked' or 'capacity_reduction', "
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
    "sample_link_disruptions",
    "failed_edges",
    "edge_is_blocked",
    "get_effective_capacity",
]
