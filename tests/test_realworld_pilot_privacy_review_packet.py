"""Tests for pilot-region privacy review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.pilot_privacy_review_packet import (  # noqa: E402
    DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
    DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH,
    PILOT_PRIVACY_REVIEW_COLUMNS,
    PILOT_PRIVACY_REVIEW_SCOPE,
    build_pilot_privacy_review_rows,
    write_pilot_privacy_review_packet,
)


def test_pilot_privacy_review_rows_cover_region_points_and_claims() -> None:
    """Rows should cover region geography, coordinate policy, and data card."""

    rows = build_pilot_privacy_review_rows()
    by_id = {row["review_item_id"]: row for row in rows}

    assert len(rows) == 7
    assert by_id["region_boundary"]["item_type"] == "boundary"
    assert by_id["assembly_zone:A"]["coordinate_class"] == "public"
    assert by_id["destination_zone:D"]["coordinate_class"] == "synthetic"
    assert by_id["destination_zone:D"]["synthetic_or_aggregated"] == "true"
    assert by_id["rail_access_point:S"]["sensitivity_label"] == "public_station_area"
    assert by_id["rail_egress_point:R"]["sensitivity_label"] == "public_station_area"
    assert by_id["coordinate_policy"]["coordinate_class"] == (
        "public_or_synthetic_points_only"
    )
    assert "non-operational" in by_id["data_card_claim_boundary"][
        "required_reviewer_decision"
    ]
    assert {row["claim_boundary"] for row in rows} == {
        PILOT_PRIVACY_REVIEW_SCOPE
    }
    assert all(row["can_support_pilot_acceptance"] == "false" for row in rows)

    print("PASS: pilot privacy review rows cover region points and claims")


def test_write_pilot_privacy_review_packet_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown review artifacts."""

    rows = build_pilot_privacy_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "pilot_privacy_review.csv"
        manifest = Path(directory) / "pilot_privacy_review_manifest.json"
        doc = Path(directory) / "pilot_privacy_review.md"
        value = write_pilot_privacy_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == PILOT_PRIVACY_REVIEW_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert written_manifest["row_count"] == len(rows)
        assert written_manifest["pilot_acceptance_closure_candidate_count"] == 0
        assert "Pilot Privacy Review Packet" in text

    print("PASS: pilot privacy review writer emits artifacts")


def test_shipped_pilot_privacy_review_packet_matches_current_region() -> None:
    """Current shipped packet should match deterministic pilot inputs."""

    rows = build_pilot_privacy_review_rows()

    assert DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["review_item_id"] for row in written_rows] == [
        row["review_item_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["result_scope"] == PILOT_PRIVACY_REVIEW_SCOPE

    print("PASS: shipped pilot privacy review packet matches current region")


if __name__ == "__main__":
    test_pilot_privacy_review_rows_cover_region_points_and_claims()
    test_write_pilot_privacy_review_packet_outputs_artifacts()
    test_shipped_pilot_privacy_review_packet_matches_current_region()
    print("\n=== REALWORLD PILOT PRIVACY REVIEW PACKET TESTS PASSED ===")
