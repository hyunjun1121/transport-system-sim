"""Tests for road-input evidence review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_evidence_review_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_REVIEW_MANIFEST_PATH,
    DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    ROAD_EVIDENCE_REVIEW_COLUMNS,
    ROAD_EVIDENCE_REVIEW_PACKET_SCOPE,
    build_road_evidence_review_rows,
    write_road_evidence_review_packet,
)


def test_road_evidence_review_rows_cover_current_routeable_classes() -> None:
    """The review packet should summarize routeable cached road classes."""

    rows = build_road_evidence_review_rows()
    by_highway = {row["highway"]: row for row in rows}

    assert len(rows) == 10
    assert "residential" in by_highway
    assert by_highway["residential"]["review_priority"] == "high"
    assert by_highway["residential"]["speed_evidence_status"] == "sparse_public_maxspeed_tags"
    assert by_highway["residential"]["capacity_evidence_status"] == "missing_lane_or_capacity_evidence"
    assert by_highway["residential"]["base_disruption_evidence_status"] == "missing_disruption_probability_evidence"
    assert by_highway["residential"]["weak_for_final_claim"] == "true"
    assert {row["claim_boundary"] for row in rows} == {ROAD_EVIDENCE_REVIEW_PACKET_SCOPE}

    print("PASS: road evidence review rows cover current routeable classes")


def test_write_road_evidence_review_packet_outputs_csv_and_manifest() -> None:
    """Writer should emit stable CSV fields and non-acceptance manifest."""

    rows = build_road_evidence_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "road_evidence_review.csv"
        manifest = Path(directory) / "road_evidence_review_manifest.json"
        value = write_road_evidence_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == ROAD_EVIDENCE_REVIEW_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 10
        assert value["publication_ready"] is False
        assert written_manifest["row_count"] == 10
        assert written_manifest["weak_for_final_claim_count"] == 10
        assert "does not create road-class override signoff" in written_manifest["claim_boundary"]

    print("PASS: road evidence review packet writer emits CSV and manifest")


def test_shipped_road_evidence_review_packet_matches_current_cache() -> None:
    """Current shipped review packet should match deterministic cached inputs."""

    rows = build_road_evidence_review_rows()

    assert DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_ROAD_EVIDENCE_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_ROAD_EVIDENCE_REVIEW_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["highway"] for row in written_rows] == [
        row["highway"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["result_scope"] == ROAD_EVIDENCE_REVIEW_PACKET_SCOPE

    print("PASS: shipped road evidence review packet matches current cache")


if __name__ == "__main__":
    test_road_evidence_review_rows_cover_current_routeable_classes()
    test_write_road_evidence_review_packet_outputs_csv_and_manifest()
    test_shipped_road_evidence_review_packet_matches_current_cache()
    print("\n=== REALWORLD ROAD EVIDENCE REVIEW PACKET TESTS PASSED ===")
