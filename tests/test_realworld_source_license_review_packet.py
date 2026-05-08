"""Tests for source/license review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.source_license_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
    SOURCE_LICENSE_REVIEW_COLUMNS,
    SOURCE_LICENSE_REVIEW_SCOPE,
    build_source_license_review_rows,
    write_source_license_review_packet,
)


def test_source_license_review_rows_are_source_specific() -> None:
    """Rows should convert source provenance into concrete review actions."""

    rows = build_source_license_review_rows()
    by_id = {row["source_id"]: row for row in rows}

    assert len(rows) >= 8
    assert by_id["osm_overpass_road_snapshot"]["license_review_required"] == "true"
    assert by_id["osm_overpass_road_snapshot"]["snapshot_status"] == (
        "local_artifacts_present"
    )
    assert by_id["seoul_shortest_path_api_context"]["snapshot_status"] == (
        "context_only_not_cached"
    )
    assert by_id["ktdb_public_transport_gtfs_context"]["review_status"] == (
        "cached_snapshot_pending_review"
    )
    assert by_id["ktdb_public_transport_gtfs_context"]["snapshot_status"] == (
        "local_artifacts_present"
    )
    assert by_id["ktdb_public_transport_gtfs_context"]["local_artifact_count"] == "11"
    assert by_id["ktdb_public_transport_gtfs_context"][
        "publication_use_status"
    ] == "cached source pending license, attribution, and snapshot review"
    assert "provide a reviewed target payload" in by_id[
        "seoul_shortest_path_api_context"
    ]["required_reviewer_decision"]
    assert by_id["pilot_region_spec"]["privacy_review_required"] == "true"
    assert {row["claim_boundary"] for row in rows} == {
        SOURCE_LICENSE_REVIEW_SCOPE
    }
    assert all(row["can_support_final_provenance_gate"] == "false" for row in rows)

    print("PASS: source/license review rows are source specific")


def test_write_source_license_review_packet_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown review artifacts."""

    rows = build_source_license_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "source_license_review.csv"
        manifest = Path(directory) / "source_license_review_manifest.json"
        doc = Path(directory) / "source_license_review.md"
        value = write_source_license_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == SOURCE_LICENSE_REVIEW_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert written_manifest["row_count"] == len(rows)
        assert written_manifest["provenance_gate_closure_candidate_count"] == 0
        assert "Source And License Review Packet" in text

    print("PASS: source/license review writer emits artifacts")


def test_shipped_source_license_review_packet_matches_current_manifest() -> None:
    """Current shipped packet should match deterministic provenance inputs."""

    rows = build_source_license_review_rows()

    assert DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["source_id"] for row in written_rows] == [
        row["source_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["result_scope"] == SOURCE_LICENSE_REVIEW_SCOPE

    print("PASS: shipped source/license review packet matches current manifest")


if __name__ == "__main__":
    test_source_license_review_rows_are_source_specific()
    test_write_source_license_review_packet_outputs_artifacts()
    test_shipped_source_license_review_packet_matches_current_manifest()
    print("\n=== REALWORLD SOURCE/LICENSE REVIEW PACKET TESTS PASSED ===")
