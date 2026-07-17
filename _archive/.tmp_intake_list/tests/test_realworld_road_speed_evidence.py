"""Tests for OSM maxspeed candidate evidence generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_speed_evidence import (  # noqa: E402
    DEFAULT_ROAD_SPEED_EVIDENCE_PATH,
    ROAD_SPEED_EVIDENCE_COLUMNS,
    ROAD_SPEED_EVIDENCE_SCOPE,
    build_cached_road_speed_evidence_rows,
    build_road_speed_evidence_rows,
    write_road_speed_evidence,
)


def test_speed_evidence_summarizes_parseable_maxspeed_tags() -> None:
    """Observed OSM maxspeed tags should become class-level candidate evidence."""

    graph = nx.MultiDiGraph()
    graph.add_node(1)
    graph.add_node(2)
    graph.add_node(3)
    graph.add_node(4)
    graph.add_edge(1, 2, highway="primary", length=100.0, maxspeed="50")
    graph.add_edge(2, 3, highway="primary", length=300.0, maxspeed="60")
    graph.add_edge(3, 4, highway="secondary", length=100.0)
    graph.add_edge(4, 1, highway="service", length=100.0, maxspeed="20")

    rows = build_road_speed_evidence_rows(graph)
    by_class = {row["highway"]: row for row in rows}

    assert set(by_class) == {"primary", "secondary"}
    assert by_class["primary"]["maxspeed_observed_count"] == "2"
    assert by_class["primary"]["median_observed_speed_kph"] == "55"
    assert by_class["primary"]["candidate_speed_kph"] == "55"
    assert by_class["primary"]["candidate_source_class"] == "public-data-derived"
    assert by_class["secondary"]["maxspeed_observed_count"] == "0"
    assert by_class["secondary"]["candidate_source_class"] == "expert assumption"
    assert by_class["primary"]["claim_boundary"] == ROAD_SPEED_EVIDENCE_SCOPE

    print("PASS: speed evidence summarizes parseable maxspeed tags")


def test_write_speed_evidence_outputs_csv_and_manifest() -> None:
    """Writer should emit a stable CSV schema and conservative manifest."""

    graph = nx.MultiDiGraph()
    graph.add_node(1)
    graph.add_node(2)
    graph.add_edge(1, 2, highway="primary", length=100.0, maxspeed="50")
    rows = build_road_speed_evidence_rows(graph)

    with TemporaryDirectory() as directory:
        output = Path(directory) / "speed.csv"
        manifest = Path(directory) / "speed_manifest.json"
        value = write_road_speed_evidence(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            source_graph_path=Path(directory) / "graph.graphml",
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == ROAD_SPEED_EVIDENCE_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 1
        assert value["publication_ready"] is False
        assert written_manifest["rows_with_observed_maxspeed"] == 1
        assert "does not create reviewed speed overrides" in written_manifest["claim_boundary"]

    print("PASS: speed evidence writer emits CSV and manifest")


def test_shipped_speed_evidence_matches_current_cache() -> None:
    """Current cached graph should generate the committed candidate row count."""

    rows = build_cached_road_speed_evidence_rows()

    assert DEFAULT_ROAD_SPEED_EVIDENCE_PATH.exists()
    assert len(rows) == 10
    assert sum(1 for row in rows if int(row["maxspeed_observed_count"]) > 0) >= 4
    assert any(row["highway"] == "residential" for row in rows)

    print("PASS: shipped speed evidence matches current cache dimensions")


if __name__ == "__main__":
    test_speed_evidence_summarizes_parseable_maxspeed_tags()
    test_write_speed_evidence_outputs_csv_and_manifest()
    test_shipped_speed_evidence_matches_current_cache()
    print("\n=== REALWORLD ROAD SPEED EVIDENCE TESTS PASSED ===")
