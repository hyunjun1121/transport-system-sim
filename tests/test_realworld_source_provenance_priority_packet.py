"""Tests for source provenance priority packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.source_provenance_priority_packet import (  # noqa: E402
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    SOURCE_PROVENANCE_PRIORITY_COLUMNS,
    SOURCE_PROVENANCE_PRIORITY_SCOPE,
    build_source_provenance_priority_rows,
    write_source_provenance_priority_packet,
)


def test_source_provenance_priority_rows_classify_current_sources() -> None:
    """Current source packets should become per-source priority rows."""

    rows = build_source_provenance_priority_rows()
    by_id = {row["source_id"]: row for row in rows}

    assert len(rows) == 11
    assert by_id["seoul_shortest_path_api_context"]["priority_status"] == (
        "blocked_context_only_source_not_cached"
    )
    assert by_id["seoul_timetable_api_context"]["priority_status"] == (
        "blocked_context_only_source_not_cached"
    )
    assert by_id["ktdb_public_transport_gtfs_context"]["review_status"] == (
        "cached_snapshot_pending_review"
    )
    assert by_id["ktdb_public_transport_gtfs_context"]["priority_status"] == (
        "needs_human_review_cached_snapshot_source"
    )
    assert by_id["ktdb_public_transport_gtfs_context"]["local_artifact_count"] == "11"
    assert by_id["metro9_capacity_context"]["priority_status"] == (
        "needs_human_review_cached_snapshot_source"
    )
    assert by_id["osm_overpass_road_snapshot"]["priority_status"] == (
        "needs_human_review_cached_snapshot_source"
    )
    assert by_id["pilot_region_spec"]["priority_status"] == (
        "needs_human_review_repository_input_source"
    )
    assert "alternate_reachable_url_needs_review=1" in by_id[
        "ktdb_public_transport_gtfs_context"
    ]["url_remediation_status_counts"]
    assert "https://www.ktdb.go.kr/www/selectPbldataChargerWebList.do" in by_id[
        "ktdb_public_transport_gtfs_context"
    ]["alternate_url_candidates"]
    assert {row["claim_boundary"] for row in rows} == {
        SOURCE_PROVENANCE_PRIORITY_SCOPE
    }
    assert all(row["can_support_final_provenance_gate"] == "false" for row in rows)

    print("PASS: source provenance priority rows classify current sources")


def test_source_provenance_priority_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_source_provenance_priority_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "source_priority.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "source_priority.md"
        manifest = write_source_provenance_priority_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == SOURCE_PROVENANCE_PRIORITY_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 11
    assert written_manifest["blocking_source_count"] == 2
    assert written_manifest["human_review_source_count"] == 9
    assert written_manifest["alternate_url_candidate_source_count"] == 1
    assert "Source Provenance Priority Packet" in doc_text

    print("PASS: source provenance priority writer emits artifacts")


def test_shipped_source_provenance_priority_packet_matches_current_outputs() -> None:
    """Committed source priority packet should match current source artifacts."""

    rows = build_source_provenance_priority_rows()

    assert DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH.exists()
    assert DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH.exists()
    with DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["context_only_source_count"] == 2
    assert manifest["cached_snapshot_source_count"] == 5
    assert manifest["repository_input_source_count"] == 4
    assert manifest["url_remediation_row_count"] == 17
    assert manifest["alternate_url_candidate_source_count"] == 1
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped source provenance priority packet matches current outputs")


if __name__ == "__main__":
    test_source_provenance_priority_rows_classify_current_sources()
    test_source_provenance_priority_writer_outputs_artifacts()
    test_shipped_source_provenance_priority_packet_matches_current_outputs()
    print("\n=== REALWORLD SOURCE PROVENANCE PRIORITY TESTS PASSED ===")
