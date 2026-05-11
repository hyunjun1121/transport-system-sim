"""Tests for OSM graph snapshot review packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.osm_graph_snapshot_review_packet import (  # noqa: E402
    DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_MANIFEST_PATH,
    DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_PACKET_PATH,
    OSM_GRAPH_SNAPSHOT_REVIEW_COLUMNS,
    OSM_GRAPH_SNAPSHOT_REVIEW_SCOPE,
    build_osm_graph_snapshot_review_rows,
    write_osm_graph_snapshot_review_packet,
)


def test_osm_graph_snapshot_review_rows_classify_current_state() -> None:
    """Current OSM cache, road evidence, and graph-scope rows stay blocked."""

    rows = build_osm_graph_snapshot_review_rows()
    by_id = {row["review_id"]: row for row in rows}

    assert len(rows) == 6
    assert by_id["osm_graph_cache_metadata"]["review_status"] == (
        "needs_human_review_osm_cache_metadata"
    )
    assert by_id["osm_source_provenance_dependency"]["review_status"] == (
        "blocked_osm_source_provenance_pending"
    )
    assert by_id["road_evidence_priority_dependency"]["review_status"] == (
        "blocked_road_evidence_priority_dependencies"
    )
    assert by_id["road_source_decision_dependency"]["review_status"] == (
        "blocked_road_source_decisions_pending"
    )
    assert by_id["graph_scale_manifest_dependency"]["review_status"] == (
        "blocked_graph_scale_acceptance_missing"
    )
    assert by_id["osm_snapshot_claim_boundary"]["review_status"] == (
        "blocked_osm_snapshot_claim_boundary"
    )
    assert {row["claim_boundary"] for row in rows} == {
        OSM_GRAPH_SNAPSHOT_REVIEW_SCOPE
    }
    assert all(row["can_support_cached_osm_gate"] == "false" for row in rows)

    print("PASS: OSM graph snapshot review rows classify current state")


def test_osm_graph_snapshot_review_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_osm_graph_snapshot_review_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "osm_graph_snapshot_review.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "packet.md"
        manifest = write_osm_graph_snapshot_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == OSM_GRAPH_SNAPSHOT_REVIEW_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 6
    assert written_manifest["blocking_review_count"] == 5
    assert written_manifest["human_review_count"] == 1
    assert "OSM Graph Snapshot Review Packet" in doc_text

    print("PASS: OSM graph snapshot review writer emits artifacts")


def test_shipped_osm_graph_snapshot_review_packet_matches_current_outputs() -> None:
    """Committed OSM graph snapshot packet should match current manifests."""

    rows = build_osm_graph_snapshot_review_rows()

    assert DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_review_count"] == 5
    assert manifest["human_review_count"] == 1
    assert manifest["cached_osm_gate_closure_candidate_count"] == 0
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped OSM graph snapshot review packet matches outputs")


if __name__ == "__main__":
    test_osm_graph_snapshot_review_rows_classify_current_state()
    test_osm_graph_snapshot_review_writer_outputs_artifacts()
    test_shipped_osm_graph_snapshot_review_packet_matches_current_outputs()
    print("\n=== REALWORLD OSM GRAPH SNAPSHOT REVIEW TESTS PASSED ===")
