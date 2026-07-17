"""Offline tests for route accessibility-loss diagnostics."""

import csv
import os
import sys
from pathlib import Path

import networkx as nx
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld import build_simulator_graph, load_graphml
from src.realworld.accessibility import (
    ACCESSIBILITY_CLAIM_SCOPE,
    ACCESSIBILITY_CSV_FIELDS,
    AccessibilityRoute,
    classify_criticality,
    evaluate_accessibility_loss,
    evaluate_route_accessibility_loss,
    records_to_csv_rows,
    summarize_accessibility_loss,
)


ROOT = Path(__file__).resolve().parents[1]
REGION_PATH = ROOT / "data" / "regions" / "pilot_region.yaml"
CACHE_PATH = ROOT / "data" / "cache" / "pilot_region_road.graphml"
CSV_PATH = ROOT / "data" / "validation" / "accessibility_loss.csv"
SUMMARY_PATH = ROOT / "data" / "validation" / "accessibility_loss_summary.md"


def test_criticality_classification() -> None:
    """Criticality classes should be deterministic and review-oriented."""

    assert classify_criticality(0.1, 0.01) == "low_time_loss"
    assert classify_criticality(2.0, 0.05) == "moderate_time_loss"
    assert classify_criticality(0.5, 0.10) == "moderate_time_loss"
    assert classify_criticality(10.0, 0.05) == "high_time_loss"
    assert classify_criticality(1.0, 0.50) == "high_time_loss"
    assert classify_criticality(float("inf"), float("inf")) == "disconnected"

    print("PASS: accessibility criticality classification is deterministic")


def test_route_accessibility_loss_detects_reroute_and_disconnection() -> None:
    """Removing baseline path edges should measure reroutes and disconnections."""

    route = AccessibilityRoute("synthetic", "A", "D", "synthetic route")
    records = evaluate_route_accessibility_loss(
        synthetic_accessibility_graph(include_alternate=True),
        route,
        region_id="synthetic",
    )
    assert len(records) == 2
    assert all(record.baseline_available for record in records)
    assert all(record.disrupted_available for record in records)
    assert all(record.time_loss_min > 0.0 for record in records)
    assert {record.claim_scope for record in records} == {ACCESSIBILITY_CLAIM_SCOPE}

    disconnected = evaluate_route_accessibility_loss(
        synthetic_accessibility_graph(include_alternate=False),
        route,
        region_id="synthetic",
    )
    assert len(disconnected) == 2
    assert {record.criticality_class for record in disconnected} == {"disconnected"}
    assert not any(record.disrupted_available for record in disconnected)

    print("PASS: accessibility loss detects reroutes and disconnections")


def test_missing_baseline_route_is_reported() -> None:
    """A missing baseline route should return one blocked diagnostic row."""

    graph = synthetic_accessibility_graph(include_alternate=False)
    graph.remove_edge("A", "B")
    graph.remove_edge("B", "D")
    route = AccessibilityRoute("missing", "A", "D", "missing route")

    records = evaluate_route_accessibility_loss(graph, route, region_id="synthetic")

    assert len(records) == 1
    assert not records[0].baseline_available
    assert records[0].criticality_class == "baseline_disconnected"

    print("PASS: missing baseline route is reported")


def test_shipped_accessibility_loss_csv_matches_current_scaffold() -> None:
    """The shipped CSV should match deterministic pilot accessibility diagnostics."""

    expected_rows = list(records_to_csv_rows(current_pilot_records()))
    with CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == list(ACCESSIBILITY_CSV_FIELDS)
    assert rows == expected_rows
    assert len(rows) > 0
    assert {row["claim_scope"] for row in rows} == {ACCESSIBILITY_CLAIM_SCOPE}
    assert {"bus_direct", "rail_access", "last_mile"} <= {
        row["route_id"] for row in rows
    }

    summary = summarize_accessibility_loss(current_pilot_records())
    assert summary["diagnostics_ready"]
    assert summary["row_count"] == len(rows)

    print("PASS: shipped accessibility-loss CSV matches current scaffold")


def test_accessibility_summary_labels_scaffold_scope() -> None:
    """The summary should block calibrated or operational interpretation."""

    text = SUMMARY_PATH.read_text(encoding="utf-8")
    lower_text = text.lower()

    assert "songpa_public_demo" in text
    assert "accessibility_loss.csv" in text
    assert "scaffold route-fragility diagnostic" in lower_text
    assert "not calibrated" in lower_text
    assert "not an operational" in lower_text
    assert "final manuscript claims still require" in lower_text

    print("PASS: accessibility summary labels scaffold scope")


def synthetic_accessibility_graph(*, include_alternate: bool) -> nx.DiGraph:
    """Return a tiny road-mode graph with a direct and optional alternate path."""

    graph = nx.DiGraph()
    graph.graph["region_id"] = "synthetic"
    graph.add_node("A")
    graph.add_node("B")
    graph.add_node("C")
    graph.add_node("D")
    add_road_edge(graph, "A", "B", 500.0, 1.0)
    add_road_edge(graph, "B", "D", 500.0, 1.0)
    if include_alternate:
        add_road_edge(graph, "A", "C", 1000.0, 4.0)
        add_road_edge(graph, "C", "D", 1000.0, 4.0)
    return graph


def add_road_edge(graph: nx.DiGraph, source: str, target: str, length_m: float, t0: float) -> None:
    graph.add_edge(
        source,
        target,
        length_m=length_m,
        t0=t0,
        capacity=1000.0,
        base_p_fail=0.0,
        p_fail=0.0,
        mode="road",
    )


def current_pilot_records():
    with REGION_PATH.open("r", encoding="utf-8") as handle:
        region = yaml.safe_load(handle)
    road_graph = load_graphml(CACHE_PATH, normalize=True)
    simulator_graph = build_simulator_graph(road_graph, region)
    return evaluate_accessibility_loss(
        simulator_graph,
        region_id=str(region["region_id"]),
    )


def run_all_tests() -> None:
    test_criticality_classification()
    test_route_accessibility_loss_detects_reroute_and_disconnection()
    test_missing_baseline_route_is_reported()
    test_shipped_accessibility_loss_csv_matches_current_scaffold()
    test_accessibility_summary_labels_scaffold_scope()
    print("\n=== REALWORLD ACCESSIBILITY TESTS PASSED ===")


if __name__ == "__main__":
    run_all_tests()
