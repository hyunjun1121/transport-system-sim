"""Tests for OSM lane-count capacity candidate evidence generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_capacity_evidence import (  # noqa: E402
    DEFAULT_ROAD_CAPACITY_EVIDENCE_PATH,
    ROAD_CAPACITY_EVIDENCE_COLUMNS,
    ROAD_CAPACITY_EVIDENCE_SCOPE,
    build_cached_road_capacity_evidence_rows,
    build_road_capacity_evidence_rows,
    parse_lane_count,
    write_road_capacity_evidence,
)


def test_lane_parser_handles_common_osm_values() -> None:
    """Lane parsing should be conservative for ambiguous tags."""

    assert parse_lane_count({"lanes": "3"}) == 3.0
    assert parse_lane_count({"lanes": "2;3"}) == 2.0
    assert parse_lane_count({"lanes": ["4", "2"]}) == 2.0
    assert parse_lane_count({"lanes:forward": "2", "lanes:backward": "1"}) == 1.0
    assert parse_lane_count({"lanes": "unknown"}) is None

    print("PASS: lane parser handles common OSM values")


def test_capacity_evidence_summarizes_parseable_lane_tags() -> None:
    """Observed OSM lanes should become class-level candidate evidence."""

    graph = nx.MultiDiGraph()
    graph.add_node(1)
    graph.add_node(2)
    graph.add_node(3)
    graph.add_node(4)
    graph.add_edge(1, 2, highway="primary", length=100.0, lanes="2")
    graph.add_edge(2, 3, highway="primary", length=300.0, lanes="4")
    graph.add_edge(3, 4, highway="secondary", length=100.0)
    graph.add_edge(4, 1, highway="service", length=100.0, lanes="1")

    rows = build_road_capacity_evidence_rows(graph, capacity_per_lane_vph=700.0)
    by_class = {row["highway"]: row for row in rows}

    assert set(by_class) == {"primary", "secondary"}
    assert by_class["primary"]["lanes_observed_count"] == "2"
    assert by_class["primary"]["median_observed_lanes"] == "3"
    assert by_class["primary"]["candidate_capacity_veh_per_hr"] == "2100"
    assert by_class["primary"]["candidate_source_class"] == "public-data-derived"
    assert by_class["secondary"]["lanes_observed_count"] == "0"
    assert by_class["secondary"]["candidate_source_class"] == "expert assumption"
    assert by_class["primary"]["claim_boundary"] == ROAD_CAPACITY_EVIDENCE_SCOPE

    print("PASS: capacity evidence summarizes parseable lane tags")


def test_write_capacity_evidence_outputs_csv_and_manifest() -> None:
    """Writer should emit a stable CSV schema and conservative manifest."""

    graph = nx.MultiDiGraph()
    graph.add_node(1)
    graph.add_node(2)
    graph.add_edge(1, 2, highway="primary", length=100.0, lanes="2")
    rows = build_road_capacity_evidence_rows(graph)

    with TemporaryDirectory() as directory:
        output = Path(directory) / "capacity.csv"
        manifest = Path(directory) / "capacity_manifest.json"
        value = write_road_capacity_evidence(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            source_graph_path=Path(directory) / "graph.graphml",
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == ROAD_CAPACITY_EVIDENCE_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 1
        assert value["publication_ready"] is False
        assert written_manifest["rows_with_observed_lanes"] == 1
        assert "does not create reviewed capacity overrides" in written_manifest["claim_boundary"]

    print("PASS: capacity evidence writer emits CSV and manifest")


def test_shipped_capacity_evidence_matches_current_cache() -> None:
    """Current cached graph should generate the committed candidate row count."""

    rows = build_cached_road_capacity_evidence_rows()

    assert DEFAULT_ROAD_CAPACITY_EVIDENCE_PATH.exists()
    assert len(rows) == 10
    assert sum(1 for row in rows if int(row["lanes_observed_count"]) > 0) == 0
    assert any(row["highway"] == "residential" for row in rows)

    print("PASS: shipped capacity evidence matches current cache dimensions")


if __name__ == "__main__":
    test_lane_parser_handles_common_osm_values()
    test_capacity_evidence_summarizes_parseable_lane_tags()
    test_write_capacity_evidence_outputs_csv_and_manifest()
    test_shipped_capacity_evidence_matches_current_cache()
    print("\n=== REALWORLD ROAD CAPACITY EVIDENCE TESTS PASSED ===")
