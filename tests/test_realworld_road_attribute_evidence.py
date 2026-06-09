"""Tests for edge-level road-attribute evidence rows."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_attribute_evidence import (  # noqa: E402
    EVIDENCE_CLASSES,
    ROAD_ATTRIBUTE_EVIDENCE_COLUMNS,
    ROAD_ATTRIBUTE_EVIDENCE_SCOPE,
    build_cached_road_attribute_evidence_rows,
    build_road_attribute_evidence_rows,
    write_road_attribute_evidence,
)


def test_edge_rows_keep_capacity_candidates_separate_from_used_proxy() -> None:
    """Observed lanes should not make mapper-default capacity review-ready."""

    graph = nx.MultiDiGraph()
    graph.add_node(1)
    graph.add_node(2)
    graph.add_edge(
        1,
        2,
        key=0,
        osmid="duplicate-osm-way",
        highway="primary",
        length=1_000.0,
        maxspeed="50",
        lanes="2",
    )

    rows = build_road_attribute_evidence_rows(graph)
    row = rows[0]

    assert row["capacity_proxy_veh_per_hr"] == "1400"
    assert row["lane_based_capacity_candidate_veh_per_hr"] == "1600"
    assert row["lane_based_capacity_evidence_class"] == "OSM-derived"
    assert row["capacity_evidence_class"] == "expert proxy"
    assert row["weak_for_final_claim"] == "true"
    assert set(row["attribute_assumptions"].split(";")) >= {
        "capacity",
        "base_p_fail",
    }
    assert row["claim_boundary"] == ROAD_ATTRIBUTE_EVIDENCE_SCOPE

    print("PASS: lane-derived capacity candidates stay separate from used proxy")


def test_source_backed_labels_require_source_markers() -> None:
    """Explicit numeric model fields are not source-backed without markers."""

    graph = nx.MultiDiGraph()
    graph.add_node("a")
    graph.add_node("b")
    graph.add_node("c")
    graph.add_edge(
        "a",
        "b",
        key="unreviewed",
        id="explicit-unreviewed",
        highway="secondary",
        length=600,
        maxspeed=50,
        capacity=900,
        base_p_fail=0.2,
    )
    graph.add_edge(
        "b",
        "c",
        key="reviewed",
        realworld_edge_id="reviewed-edge",
        highway="secondary",
        length=600,
        maxspeed=50,
        capacity=900,
        capacity_source_class="source-backed",
        base_p_fail=0.02,
        base_p_fail_source_class="source-backed",
    )

    rows = {
        row["realworld_edge_id"]: row
        for row in build_road_attribute_evidence_rows(
            graph,
            benchmark_travel_time_by_edge_id={"reviewed-edge": 0.9},
            benchmark_source_label="osrm_snapshot",
            benchmark_snapshot_path="data/cache/osrm/example.json",
        )
    }

    unreviewed = rows["explicit-unreviewed"]
    assert unreviewed["capacity_evidence_class"] == "expert proxy"
    assert unreviewed["base_disruption_evidence_class"] == "sensitivity-only"
    assert unreviewed["weak_for_final_claim"] == "true"

    reviewed = rows["reviewed-edge"]
    assert reviewed["capacity_evidence_class"] == "source-backed"
    assert reviewed["base_disruption_evidence_class"] == "source-backed"
    assert reviewed["benchmark_evidence_class"] == "routing-engine benchmarked"
    assert reviewed["benchmark_source_label"] == "osrm_snapshot"
    assert reviewed["weak_for_final_claim"] == "false"

    print("PASS: source-backed labels require explicit source markers")


def test_edge_ids_are_unique_even_when_osm_way_id_repeats() -> None:
    """Evidence rows need unique edge IDs for benchmark joins."""

    graph = nx.MultiDiGraph()
    graph.add_nodes_from([1, 2, 3])
    graph.add_edge(1, 2, key=0, osmid="same-way", highway="primary", length=100, maxspeed=50)
    graph.add_edge(2, 3, key=0, osmid="same-way", highway="primary", length=100, maxspeed=50)

    rows = build_road_attribute_evidence_rows(graph)
    edge_ids = [row["edge_id"] for row in rows]

    assert len(edge_ids) == len(set(edge_ids))
    assert all(row["realworld_edge_id"] == "same-way" for row in rows)

    print("PASS: edge IDs are unique when OSM way IDs repeat")


def test_writer_outputs_csv_and_non_acceptance_manifest() -> None:
    """Writer should emit a stable schema and conservative manifest."""

    graph = nx.MultiDiGraph()
    graph.add_node(1)
    graph.add_node(2)
    graph.add_edge(1, 2, highway="primary", length=100, maxspeed=50)
    rows = build_road_attribute_evidence_rows(graph)

    with TemporaryDirectory() as directory:
        output = Path(directory) / "road_attribute.csv"
        manifest = Path(directory) / "road_attribute_manifest.json"
        value = write_road_attribute_evidence(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            source_graph_path=Path(directory) / "graph.graphml",
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == ROAD_ATTRIBUTE_EVIDENCE_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 1
        assert value["publication_ready"] is False
        assert value["formal_acceptance_created"] is False
        assert value["can_mark_complete"] is False
        assert written_manifest["weak_for_final_claim_count"] == 1

    print("PASS: road-attribute writer emits CSV and non-acceptance manifest")


def test_cached_road_attribute_rows_have_unique_edge_ids() -> None:
    """Current cached graph should not duplicate edge-level evidence IDs."""

    rows = build_cached_road_attribute_evidence_rows()
    edge_ids = [row["edge_id"] for row in rows]

    assert rows
    assert len(edge_ids) == len(set(edge_ids))
    assert all(
        row["capacity_evidence_class"] in EVIDENCE_CLASSES for row in rows
    )
    assert any(row["weak_for_final_claim"] == "true" for row in rows)

    print("PASS: cached road-attribute rows have unique edge IDs")


if __name__ == "__main__":
    test_edge_rows_keep_capacity_candidates_separate_from_used_proxy()
    test_source_backed_labels_require_source_markers()
    test_edge_ids_are_unique_even_when_osm_way_id_repeats()
    test_writer_outputs_csv_and_non_acceptance_manifest()
    test_cached_road_attribute_rows_have_unique_edge_ids()
    print("\n=== REALWORLD ROAD ATTRIBUTE EVIDENCE TESTS PASSED ===")
