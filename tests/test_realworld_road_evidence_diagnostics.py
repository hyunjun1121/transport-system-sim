"""Tests for road-class evidence diagnostics."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_evidence_diagnostics import (  # noqa: E402
    audit_cached_road_evidence_diagnostics,
    audit_road_graph_evidence_diagnostics,
)


def test_fixture_road_diagnostics_rank_weak_routeable_classes() -> None:
    """Diagnostics should identify routeable classes with weak evidence."""

    graph = nx.MultiDiGraph()
    graph.add_node(1, x=127.1, y=37.5)
    graph.add_node(2, x=127.2, y=37.6)
    graph.add_node(3, x=127.3, y=37.7)
    graph.add_node(4, x=127.4, y=37.8)
    graph.add_edge(
        1,
        2,
        highway="primary",
        length=100.0,
        maxspeed="50",
        capacity=1000,
        base_p_fail=0.02,
    )
    graph.add_edge(2, 3, highway="secondary", length=300.0)
    graph.add_edge(3, 4, highway="service", length=50.0)

    summary = audit_road_graph_evidence_diagnostics(graph)
    rows = {row["highway"]: row for row in summary["road_class_rows"]}

    assert summary["diagnostics_ready"] is True
    assert summary["publication_ready"] is False
    assert summary["edge_count"] == 3
    assert summary["routeable_edge_count"] == 2
    assert summary["total_length_km"] == 0.45
    assert rows["primary"]["review_priority"] == "low"
    assert rows["secondary"]["review_priority"] == "high"
    assert rows["secondary"]["capacity_proxy_edge_count"] == 1
    assert rows["service"]["routeable_edge_count"] == 0
    assert summary["top_review_candidates"][0]["highway"] == "secondary"
    assert summary["review_items"]

    print("PASS: road diagnostics rank weak routeable classes")


def test_missing_graph_is_structural_blocker() -> None:
    """A missing cache should be reported as a blocker, not accepted."""

    with TemporaryDirectory() as tmp:
        summary = audit_cached_road_evidence_diagnostics(Path(tmp) / "missing.graphml")

    assert summary["diagnostics_ready"] is False
    assert summary["edge_count"] == 0
    assert summary["remaining_blockers"]

    print("PASS: road diagnostics report missing graph blocker")


def test_shipped_road_diagnostics_are_diagnosable_not_accepted() -> None:
    """The current pilot cache should produce class-level review diagnostics."""

    summary = audit_cached_road_evidence_diagnostics()

    assert summary["diagnostics_ready"] is True
    assert summary["publication_ready"] is False
    assert summary["edge_count"] == 28947
    assert summary["road_class_rows"]
    assert summary["top_raw_highway_tags"]
    assert summary["capacity_explicit_rate"] == 1.0
    assert any("road-class override" in item for item in summary["review_items"])
    assert "operational route choice" in summary["claim_boundary"]

    print("PASS: shipped road diagnostics are diagnosable but not accepted")


if __name__ == "__main__":
    test_fixture_road_diagnostics_rank_weak_routeable_classes()
    test_missing_graph_is_structural_blocker()
    test_shipped_road_diagnostics_are_diagnosable_not_accepted()
    print("\n=== REALWORLD ROAD EVIDENCE DIAGNOSTICS TESTS PASSED ===")
