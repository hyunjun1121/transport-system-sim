"""Tests for road evidence priority packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_evidence_priority_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
    ROAD_EVIDENCE_PRIORITY_COLUMNS,
    ROAD_EVIDENCE_PRIORITY_SCOPE,
    build_road_evidence_priority_rows,
    write_road_evidence_priority_packet,
)


def test_road_evidence_priority_rows_rank_current_route_exposure() -> None:
    """Current road review packets should produce route-weighted priorities."""

    rows = build_road_evidence_priority_rows()
    by_highway = {row["highway"]: row for row in rows}

    assert len(rows) == 11
    assert by_highway["connector"]["priority_status"] == (
        "blocked_exposed_connector_assumption"
    )
    assert by_highway["primary"]["priority_status"] == (
        "needs_review_exposed_medium_priority_road_evidence_gap"
    )
    assert by_highway["primary"]["canonical_exposure_rows"] == "12"
    assert by_highway["primary"]["exposed_route_count"] == "2"
    assert by_highway["trunk"]["priority_status"] == (
        "queued_no_current_canonical_route_exposure"
    )
    assert by_highway["trunk"]["canonical_exposure_rows"] == "0"
    assert "road_capacity_lane_count_source_request" in by_highway["primary"][
        "needed_source_requests"
    ]
    assert (
        "data/validation/canonical_route_road_evidence_exposure.csv"
        in by_highway["primary"]["candidate_artifacts"]
    )
    assert (
        "data/validation/canonical_route_road_evidence_exposure_manifest.json"
        in by_highway["primary"]["candidate_artifacts"]
    )
    assert {row["claim_boundary"] for row in rows} == {
        ROAD_EVIDENCE_PRIORITY_SCOPE
    }
    assert all(row["can_support_road_evidence_gate"] == "false" for row in rows)

    print("PASS: road evidence priority rows rank current route exposure")


def test_road_evidence_priority_writer_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_road_evidence_priority_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "road_priority.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "road_priority.md"
        manifest = write_road_evidence_priority_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == ROAD_EVIDENCE_PRIORITY_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 11
    assert written_manifest["exposed_highway_count"] == 7
    assert written_manifest["unexposed_highway_count"] == 4
    assert written_manifest["inputs"]["route_road_evidence_exposure_manifest"] == (
        "data/validation/canonical_route_road_evidence_exposure_manifest.json"
    )
    assert "Road Evidence Priority Packet" in doc_text

    print("PASS: road evidence priority writer emits artifacts")


def test_shipped_road_evidence_priority_packet_matches_current_outputs() -> None:
    """Committed road priority packet should match current road artifacts."""

    rows = build_road_evidence_priority_rows()

    assert DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH.exists()
    assert DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH.exists()
    with DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["exposed_highway_count"] == 7
    # Road evidence re-derived from the regenerated 8-class Goseong corridor
    # exposure set; only the connector row is blocking, so the blocking count is 1.
    assert manifest["blocking_priority_count"] == 1
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["inputs"]["route_road_evidence_exposure_manifest"] == (
        "data/validation/canonical_route_road_evidence_exposure_manifest.json"
    )

    print("PASS: shipped road evidence priority packet matches current outputs")


if __name__ == "__main__":
    test_road_evidence_priority_rows_rank_current_route_exposure()
    test_road_evidence_priority_writer_outputs_artifacts()
    test_shipped_road_evidence_priority_packet_matches_current_outputs()
    print("\n=== REALWORLD ROAD EVIDENCE PRIORITY TESTS PASSED ===")
