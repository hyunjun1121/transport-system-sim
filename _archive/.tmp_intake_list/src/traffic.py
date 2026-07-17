"""Dynamic road traffic accounting for route traversal.

The helper in this module is intentionally independent of ``scenario.py`` so it
can be introduced without changing experiment behavior. It records vehicle
entries per edge, converts recent entries to an hourly volume, and evaluates
BPR travel time at the moment a vehicle enters each road edge.
"""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from math import inf, isfinite

import networkx as nx

from src.models import bpr_travel_time
from src.sim_types import (
    EdgeDisruption,
    EdgeTraversal,
    require_non_negative,
    require_non_negative_or_inf,
    require_positive,
)


Edge = tuple[str, str]


class DynamicRoadTraffic:
    """Track dynamic road volumes and traverse routes edge-by-edge.

    Recent edge entries are converted to an hourly flow before calling BPR:

    ``effective_volume = background_volume + entries_in_window * 60 / window``

    The current vehicle is included in ``entries_in_window``. Entries at or
    before ``entry_time - window`` are expired from the rolling window.
    """

    def __init__(
        self,
        graph: nx.DiGraph,
        *,
        volume_window_min: float,
        background_volume: float = 0.0,
        alpha: float = 0.15,
        beta: float = 4.0,
        scale: float = 1.0,
        disruptions: Mapping[Edge, EdgeDisruption] | None = None,
    ) -> None:
        self.graph = graph
        self.volume_window_min = require_positive(
            volume_window_min,
            "volume_window_min",
        )
        self.background_volume = require_non_negative(
            background_volume,
            "background_volume",
        )
        self.alpha = require_non_negative(alpha, "alpha")
        self.beta = require_non_negative(beta, "beta")
        self.scale = require_non_negative(scale, "scale")
        self.disruptions: dict[Edge, EdgeDisruption] = dict(disruptions or {})
        self._entries: defaultdict[Edge, deque[float]] = defaultdict(deque)

    @classmethod
    def from_config(
        cls,
        graph: nx.DiGraph,
        config: Mapping,
        *,
        params: Mapping | None = None,
        disruptions: Mapping[Edge, EdgeDisruption] | None = None,
    ) -> "DynamicRoadTraffic":
        """Build a helper from project config namespaces."""
        traffic_config = config.get("traffic", {})
        bpr_config = config.get("bpr", {})
        params = params or {}

        return cls(
            graph,
            volume_window_min=traffic_config.get("volume_window_min", 60.0),
            background_volume=traffic_config.get("background_volume", 100.0),
            alpha=bpr_config.get("alpha", 0.15),
            beta=bpr_config.get("beta", 4.0),
            scale=params.get("s", 1.0),
            disruptions=disruptions,
        )

    def set_disruptions(
        self, disruptions: Mapping[Edge, EdgeDisruption] | None,
    ) -> None:
        """Replace the active per-edge disruption states."""
        self.disruptions = dict(disruptions or {})

    def clear_entries(self) -> None:
        """Clear all dynamic traffic history."""
        self._entries.clear()

    def entry_count(self, edge: Edge, at_time: float | None = None) -> int:
        """Return the number of recorded entries still in the rolling window."""
        self._require_edge(edge)
        if at_time is not None:
            self._prune_entries(edge, require_non_negative(at_time, "at_time"))
        return len(self._entries[edge])

    def current_volume(self, edge: Edge, at_time: float) -> float:
        """Return current hourly volume before recording a new edge entry."""
        self._require_edge(edge)
        self._prune_entries(edge, require_non_negative(at_time, "at_time"))
        return self._effective_volume_from_count(len(self._entries[edge]))

    def enter_edge(self, edge: Edge, entry_time: float) -> EdgeTraversal:
        """Record one vehicle entering an edge and return its traversal record."""
        self._require_edge(edge)
        entry_time = require_non_negative(entry_time, "entry_time")
        data = self.graph.edges[edge]
        disruption = self.disruptions.get(edge, EdgeDisruption())

        if disruption.is_blocked:
            return EdgeTraversal(
                edge=edge,
                entry_time=entry_time,
                exit_time=inf,
                travel_time=inf,
                effective_volume=self.current_volume(edge, entry_time),
                effective_capacity=0.0,
            )

        mode = data.get("mode", "road")
        effective_capacity = self._effective_capacity(data, disruption)

        if mode != "road":
            travel_time = require_non_negative(data["t0"], "edge t0")
            return EdgeTraversal(
                edge=edge,
                entry_time=entry_time,
                exit_time=entry_time + travel_time,
                travel_time=travel_time,
                effective_volume=self.current_volume(edge, entry_time),
                effective_capacity=effective_capacity,
            )

        if effective_capacity <= 0:
            return EdgeTraversal(
                edge=edge,
                entry_time=entry_time,
                exit_time=inf,
                travel_time=inf,
                effective_volume=self.current_volume(edge, entry_time),
                effective_capacity=effective_capacity,
            )

        effective_volume = self._record_entry_and_volume(edge, entry_time)
        travel_time = bpr_travel_time(
            t0=require_non_negative(data["t0"], "edge t0"),
            volume=effective_volume,
            capacity=effective_capacity,
            alpha=self.alpha,
            beta=self.beta,
            scale=self.scale,
        )
        exit_time = entry_time + travel_time if isfinite(travel_time) else inf

        return EdgeTraversal(
            edge=edge,
            entry_time=entry_time,
            exit_time=exit_time,
            travel_time=travel_time,
            effective_volume=effective_volume,
            effective_capacity=effective_capacity,
        )

    def traverse_route(
        self,
        route: Sequence[str] | Sequence[Edge],
        start_time: float,
    ) -> tuple[float, list[EdgeTraversal]]:
        """Traverse a node path or edge path and return total time plus details."""
        start_time = require_non_negative(start_time, "start_time")
        current_time = start_time
        traversals: list[EdgeTraversal] = []

        for edge in self._route_edges(route):
            traversal = self.enter_edge(edge, current_time)
            traversals.append(traversal)
            if not isfinite(traversal.travel_time):
                return inf, traversals
            current_time = traversal.exit_time

        return current_time - start_time, traversals

    def _record_entry_and_volume(self, edge: Edge, entry_time: float) -> float:
        self._prune_entries(edge, entry_time)
        self._entries[edge].append(entry_time)
        return self._effective_volume_from_count(len(self._entries[edge]))

    def _effective_volume_from_count(self, entry_count: int) -> float:
        dynamic_volume = entry_count * 60.0 / self.volume_window_min
        return self.background_volume + dynamic_volume

    def _prune_entries(self, edge: Edge, at_time: float) -> None:
        entries = self._entries[edge]
        cutoff = at_time - self.volume_window_min
        while entries and entries[0] <= cutoff:
            entries.popleft()

    def _effective_capacity(self, data: Mapping, disruption: EdgeDisruption) -> float:
        capacity = require_non_negative_or_inf(
            data.get("capacity", inf),
            "edge capacity",
        )
        capacity_factor = require_non_negative(
            getattr(disruption, "capacity_factor", 1.0),
            "disruption capacity_factor",
        )
        return capacity * capacity_factor

    def _require_edge(self, edge: Edge) -> None:
        if not self.graph.has_edge(*edge):
            raise KeyError(f"unknown edge: {edge}")

    @staticmethod
    def _route_edges(route: Sequence[str] | Sequence[Edge]) -> Iterable[Edge]:
        if isinstance(route, (str, bytes, bytearray)):
            raise TypeError("route must be a sequence of nodes or edges")
        if not route:
            return ()

        first = route[0]
        if isinstance(first, tuple) and len(first) == 2:
            edges: list[Edge] = []
            for edge in route:
                if not isinstance(edge, tuple) or len(edge) != 2:
                    raise ValueError("edge route entries must be 2-tuples")
                edges.append(edge)
            return tuple(edges)

        return tuple(zip(route, route[1:]))  # type: ignore[arg-type]


DynamicTraffic = DynamicRoadTraffic


__all__ = [
    "DynamicRoadTraffic",
    "DynamicTraffic",
    "Edge",
]
