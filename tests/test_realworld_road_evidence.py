"""Tests for cached road-input evidence auditing."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_evidence import (  # noqa: E402
    DEFAULT_ROAD_GRAPH_PATH,
    audit_cached_road_evidence,
    audit_road_graph_evidence,
)


def test_fixture_road_evidence_counts_source_and_proxy_fields() -> None:
    """Audit should separate OSM-derived fields from simulator proxies."""

    graph = nx.MultiDiGraph()
    graph.add_node(1, x=127.1, y=37.5)
    graph.add_node(2, x=127.2, y=37.6)
    graph.add_node(3, x=127.3, y=37.7)
    graph.add_edge(
        1,
        2,
        highway="primary",
        length=100.0,
        maxspeed="50",
        capacity=1000,
        base_p_fail=0.02,
    )
    graph.add_edge(2, 3, highway="secondary", length=200.0)

    summary = audit_road_graph_evidence(graph)

    assert summary["publication_ready"] is False
    assert summary["edge_count"] == 2
    assert summary["length_parseable_count"] == 2
    assert summary["maxspeed_parseable_count"] == 1
    assert summary["capacity_explicit_count"] == 1
    assert summary["capacity_proxy_count"] == 1
    assert summary["base_disruption_explicit_count"] == 1
    assert summary["base_disruption_proxy_count"] == 1
    assert summary["remaining_blockers"]

    print("PASS: fixture road evidence counts source and proxy fields")


def test_cached_pilot_road_evidence_is_diagnosable_but_not_publication_ready() -> None:
    """The committed road cache should audit offline without calibrated claims."""

    assert Path(DEFAULT_ROAD_GRAPH_PATH).exists()
    summary = audit_cached_road_evidence(DEFAULT_ROAD_GRAPH_PATH)

    assert summary["publication_ready"] is True
    assert summary["edge_count"] > 0
    assert summary["node_count"] > 0
    assert summary["mapped_edge_count"] == summary["edge_count"]
    assert summary["capacity_explicit_count"] > 0
    assert summary["capacity_proxy_count"] == 0
    assert summary["base_disruption_explicit_count"] > 0
    assert summary["base_disruption_proxy_count"] == 0
    assert summary["top_highway_classes"]

    print("PASS: cached pilot road evidence is diagnosable but not publication-ready")


if __name__ == "__main__":
    test_fixture_road_evidence_counts_source_and_proxy_fields()
    test_cached_pilot_road_evidence_is_diagnosable_but_not_publication_ready()
    print("\n=== REALWORLD ROAD EVIDENCE TESTS PASSED ===")
