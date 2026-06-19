"""Tests for graph-scale route comparison diagnostics."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.graph_scale_diagnostics import (  # noqa: E402
    FAIL,
    GRAPH_SCALE_ALTERNATE_ROUTE_CSV_FIELDS,
    GRAPH_SCALE_ALTERNATE_ROUTE_SCOPE,
    GRAPH_SCALE_CSV_FIELDS,
    GRAPH_SCALE_DIAGNOSTIC_SCOPE,
    PASS,
    WARN,
    compare_graph_scale_alternate_routes,
    compare_graph_scale_routes,
    graph_scale_alternate_records_to_csv_rows,
    graph_scale_records_to_csv_rows,
    summarize_graph_scale_alternate_route_comparisons,
    summarize_graph_scale_route_comparisons,
)
from src.realworld.pilot_experiments import (  # noqa: E402
    load_pilot_inputs,
    pilot_experiment_multi_corridor_subgraph,
    pilot_experiment_subgraph,
)


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "validation" / "graph_scale_route_comparison.csv"
SUMMARY_PATH = ROOT / "data" / "validation" / "graph_scale_route_comparison_summary.md"
ALTERNATE_CSV_PATH = ROOT / "data" / "validation" / "graph_scale_alternate_routes.csv"
ALTERNATE_SUMMARY_PATH = (
    ROOT / "data" / "validation" / "graph_scale_alternate_routes_summary.md"
)
MULTI_CORRIDOR_CSV_PATH = (
    ROOT / "data" / "validation" / "graph_scale_multi_corridor_routes.csv"
)
MULTI_CORRIDOR_SUMMARY_PATH = (
    ROOT / "data" / "validation" / "graph_scale_multi_corridor_routes_summary.md"
)


def test_preserved_routes_pass_graph_scale_comparison() -> None:
    """A reduced graph preserving shortest routes should pass parity checks."""

    full_graph = synthetic_full_graph()
    reduced = pilot_experiment_subgraph(full_graph)
    records = compare_graph_scale_routes(full_graph, reduced, region_id="synthetic")
    summary = summarize_graph_scale_route_comparisons(records)

    assert len(records) == 3
    assert {record.status for record in records} == {PASS}
    assert summary["all_routes_available"] is True
    assert summary["all_time_paths_preserved"] is True
    assert summary["claim_scope"] == GRAPH_SCALE_DIAGNOSTIC_SCOPE

    print("PASS: preserved routes pass graph-scale comparison")


def test_changed_reduced_route_warns() -> None:
    """A route that remains available but differs should warn."""

    full_graph = synthetic_full_graph()
    reduced = full_graph.copy()
    reduced.remove_edge("A", "X")
    reduced.remove_edge("X", "D")

    records = compare_graph_scale_routes(full_graph, reduced, region_id="synthetic")
    bus_direct = _record(records, "route_bus_direct")

    assert bus_direct.status == WARN
    assert bus_direct.full_route_available is True
    assert bus_direct.analysis_route_available is True
    assert bus_direct.time_ratio > 1.0

    print("PASS: changed reduced route warns")


def test_missing_reduced_route_fails() -> None:
    """A missing analysis route should fail graph-scale comparison."""

    full_graph = synthetic_full_graph()
    reduced = pilot_experiment_subgraph(full_graph)
    reduced.remove_edge("R", "Z")
    reduced.remove_edge("Z", "D")

    records = compare_graph_scale_routes(full_graph, reduced, region_id="synthetic")
    last_mile = _record(records, "route_last_mile")

    assert last_mile.status == FAIL
    assert last_mile.full_route_available is True
    assert last_mile.analysis_route_available is False

    print("PASS: missing reduced route fails")


def test_alternate_route_diagnostic_flags_omitted_alternates() -> None:
    """Alternate full-graph routes omitted by the corridor should warn."""

    full_graph = synthetic_full_graph()
    reduced = pilot_experiment_subgraph(full_graph)
    records = compare_graph_scale_alternate_routes(
        full_graph,
        reduced,
        region_id="synthetic",
        path_count=2,
    )
    summary = summarize_graph_scale_alternate_route_comparisons(records)
    bus_direct_rows = [
        record for record in records if record.route_check_id == "route_bus_direct"
    ]

    assert len(records) == 4
    assert bus_direct_rows[0].full_route_rank == 1
    assert bus_direct_rows[0].status == PASS
    assert bus_direct_rows[1].full_route_rank == 2
    assert bus_direct_rows[1].status == WARN
    assert bus_direct_rows[1].exact_full_path_present_in_analysis is False
    assert summary["claim_scope"] == GRAPH_SCALE_ALTERNATE_ROUTE_SCOPE
    assert summary["all_rank_one_paths_preserved"] is True
    assert summary["all_alternate_paths_preserved"] is False

    print("PASS: alternate route diagnostic flags omitted alternates")


def test_multi_corridor_candidate_preserves_top_alternates() -> None:
    """A multi-corridor candidate can preserve top full-graph route choices."""

    full_graph = synthetic_full_graph()
    multi_corridor = pilot_experiment_multi_corridor_subgraph(
        full_graph,
        path_count=2,
    )
    records = compare_graph_scale_alternate_routes(
        full_graph,
        multi_corridor,
        region_id="synthetic",
        path_count=2,
    )
    summary = summarize_graph_scale_alternate_route_comparisons(records)

    assert len(records) == 4
    assert {record.status for record in records} == {PASS}
    assert summary["all_rank_one_paths_preserved"] is True
    assert summary["all_alternate_paths_preserved"] is True
    assert multi_corridor.graph["corridor_strategy"].startswith("multi_")
    assert multi_corridor.number_of_edges() > pilot_experiment_subgraph(
        full_graph
    ).number_of_edges()

    print("PASS: multi-corridor candidate preserves top alternates")


def test_shipped_graph_scale_csv_matches_current_scaffold() -> None:
    """The generated CSV should match the deterministic current pilot graph."""

    records = current_pilot_graph_scale_records()
    expected_rows = list(graph_scale_records_to_csv_rows(records))
    with CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == list(GRAPH_SCALE_CSV_FIELDS)
    assert len(rows) == 3
    assert {row["status"] for row in rows} == {PASS}
    assert {row["claim_scope"] for row in rows} == {GRAPH_SCALE_DIAGNOSTIC_SCOPE}
    assert {row["analysis_graph_reduced"] for row in rows} == {"true"}
    for shipped_row, expected_row in zip(rows, expected_rows):
        assert shipped_row["route_check_id"] == expected_row["route_check_id"]
        assert shipped_row["status"] == expected_row["status"]
        assert shipped_row["analysis_graph_reduced"] == expected_row["analysis_graph_reduced"]

    print("PASS: shipped graph-scale CSV matches current scaffold")


def test_shipped_graph_scale_alternate_csv_matches_current_scaffold() -> None:
    """The generated alternate CSV should match the deterministic pilot graph."""

    records = current_pilot_graph_scale_alternate_records()
    expected_rows = list(graph_scale_alternate_records_to_csv_rows(records))
    with ALTERNATE_CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == list(GRAPH_SCALE_ALTERNATE_ROUTE_CSV_FIELDS)
    assert len(rows) == len(expected_rows)
    assert len(rows) >= 3
    assert {row["claim_scope"] for row in rows} == {
        GRAPH_SCALE_ALTERNATE_ROUTE_SCOPE
    }
    assert {row["analysis_graph_reduced"] for row in rows} == {"true"}
    for shipped_row, expected_row in zip(rows, expected_rows):
        assert shipped_row["route_check_id"] == expected_row["route_check_id"]
        assert shipped_row["status"] == expected_row["status"]
        assert shipped_row["analysis_graph_reduced"] == expected_row["analysis_graph_reduced"]

    print("PASS: shipped graph-scale alternate CSV matches current scaffold")


def test_shipped_graph_scale_multi_corridor_csv_matches_current_scaffold() -> None:
    """The generated multi-corridor CSV should match the pilot graph."""

    records = current_pilot_graph_scale_multi_corridor_records()
    expected_rows = list(graph_scale_alternate_records_to_csv_rows(records))
    with MULTI_CORRIDOR_CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == list(GRAPH_SCALE_ALTERNATE_ROUTE_CSV_FIELDS)
    assert len(rows) == len(expected_rows)
    assert len(rows) == 9
    assert {row["claim_scope"] for row in rows} == {
        GRAPH_SCALE_ALTERNATE_ROUTE_SCOPE
    }
    assert {row["analysis_graph_reduced"] for row in rows} == {"true"}
    assert all(row["status"] == PASS for row in rows)
    for shipped_row, expected_row in zip(rows, expected_rows):
        assert shipped_row["route_check_id"] == expected_row["route_check_id"]
        assert shipped_row["status"] == expected_row["status"]
        assert shipped_row["analysis_graph_reduced"] == expected_row["analysis_graph_reduced"]

    print("PASS: shipped graph-scale multi-corridor CSV matches current scaffold")


def test_graph_scale_summary_labels_scaffold_scope() -> None:
    """The generated summary should not claim graph-scale acceptance."""

    text = SUMMARY_PATH.read_text(encoding="utf-8")
    lower_text = text.lower()

    assert "songpa_public_demo" in text
    assert "graph_scale_route_comparison.csv" in text
    assert "not graph-scale acceptance" in lower_text
    assert "not calibrated" in lower_text
    assert "graph_scale_acceptance.json" in text

    print("PASS: graph-scale summary labels scaffold scope")


def test_graph_scale_alternate_summary_labels_scaffold_scope() -> None:
    """The alternate summary should not claim graph-scale acceptance."""

    text = ALTERNATE_SUMMARY_PATH.read_text(encoding="utf-8")
    lower_text = text.lower()

    assert "songpa_public_demo" in text
    assert "graph_scale_alternate_routes.csv" in text
    assert "alternate-route sensitivity diagnostic" in lower_text
    assert "not graph-scale acceptance" in lower_text
    assert "not calibrated" in lower_text
    assert "graph_scale_acceptance.json" in text

    print("PASS: graph-scale alternate summary labels scaffold scope")


def test_graph_scale_multi_corridor_summary_labels_candidate_scope() -> None:
    """The multi-corridor summary should not claim graph-scale acceptance."""

    text = MULTI_CORRIDOR_SUMMARY_PATH.read_text(encoding="utf-8")
    lower_text = text.lower()

    assert "songpa_public_demo" in text
    assert "graph_scale_multi_corridor_routes.csv" in text
    assert "multi-corridor candidate diagnostic" in lower_text
    assert "not graph-scale acceptance" in lower_text
    assert "not calibrated" in lower_text
    assert "graph_scale_acceptance.json" in text

    print("PASS: graph-scale multi-corridor summary labels candidate scope")


def synthetic_full_graph() -> nx.DiGraph:
    """Return a tiny simulator-style graph with required route pairs."""

    graph = nx.DiGraph()
    graph.graph["region_id"] = "synthetic"
    for node in ("A", "X", "Y", "D", "S", "R", "Z"):
        graph.add_node(node, x=0.0, y=0.0)
    _add_road(graph, "A", "X", length_m=500.0, t0=1.0)
    _add_road(graph, "X", "D", length_m=500.0, t0=1.0)
    _add_road(graph, "A", "Y", length_m=700.0, t0=2.0)
    _add_road(graph, "Y", "D", length_m=700.0, t0=2.0)
    _add_road(graph, "A", "S", length_m=300.0, t0=1.0)
    _add_road(graph, "R", "Z", length_m=400.0, t0=1.0)
    _add_road(graph, "Z", "D", length_m=400.0, t0=1.0)
    return graph


def current_pilot_graph_scale_records():
    """Build current full/reduced pilot graphs and return comparison records."""

    full_inputs = load_pilot_inputs(reduce_graph=False)
    reduced_inputs = load_pilot_inputs(reduce_graph=True)
    return compare_graph_scale_routes(
        full_inputs.graph,
        reduced_inputs.graph,
        region_id=full_inputs.region_id,
    )


def current_pilot_graph_scale_alternate_records():
    """Build current full/reduced pilot graphs and return alternate records."""

    full_inputs = load_pilot_inputs(reduce_graph=False)
    reduced_inputs = load_pilot_inputs(reduce_graph=True)
    return compare_graph_scale_alternate_routes(
        full_inputs.graph,
        reduced_inputs.graph,
        region_id=full_inputs.region_id,
        path_count=3,
    )


def current_pilot_graph_scale_multi_corridor_records():
    """Build current full/multi-corridor pilot graphs and return records."""

    full_inputs = load_pilot_inputs(reduce_graph=False)
    multi_corridor = pilot_experiment_multi_corridor_subgraph(
        full_inputs.graph,
        path_count=3,
    )
    return compare_graph_scale_alternate_routes(
        full_inputs.graph,
        multi_corridor,
        region_id=full_inputs.region_id,
        path_count=3,
    )


def _add_road(
    graph: nx.DiGraph,
    source: str,
    target: str,
    *,
    length_m: float,
    t0: float,
) -> None:
    graph.add_edge(
        source,
        target,
        mode="road",
        length_m=length_m,
        t0=t0,
        capacity=1000.0,
        base_p_fail=0.0,
        p_fail=0.0,
    )


def _record(records, route_check_id: str):
    for record in records:
        if record.route_check_id == route_check_id:
            return record
    raise AssertionError(f"missing graph-scale record {route_check_id!r}")


if __name__ == "__main__":
    test_preserved_routes_pass_graph_scale_comparison()
    test_changed_reduced_route_warns()
    test_missing_reduced_route_fails()
    test_alternate_route_diagnostic_flags_omitted_alternates()
    test_multi_corridor_candidate_preserves_top_alternates()
    test_shipped_graph_scale_csv_matches_current_scaffold()
    test_shipped_graph_scale_alternate_csv_matches_current_scaffold()
    test_shipped_graph_scale_multi_corridor_csv_matches_current_scaffold()
    test_graph_scale_summary_labels_scaffold_scope()
    test_graph_scale_alternate_summary_labels_scaffold_scope()
    test_graph_scale_multi_corridor_summary_labels_candidate_scope()
    print("\n=== REALWORLD GRAPH-SCALE DIAGNOSTIC TESTS PASSED ===")
