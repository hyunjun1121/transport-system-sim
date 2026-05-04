"""Tests for rail evidence review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_evidence_review_packet import (  # noqa: E402
    DEFAULT_RAIL_EVIDENCE_REVIEW_MANIFEST_PATH,
    DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
    RAIL_EVIDENCE_REVIEW_COLUMNS,
    RAIL_EVIDENCE_REVIEW_PACKET_SCOPE,
    build_rail_evidence_review_rows,
    write_rail_evidence_review_packet,
)


def test_rail_evidence_review_rows_cover_current_gaps() -> None:
    """The review packet should expose station-binding readiness and timing gaps."""

    rows = build_rail_evidence_review_rows()
    by_item = {row["review_item_id"]: row for row in rows}

    assert len(rows) == 10
    assert by_item["rail_station_binding_S"]["evidence_status"] == "official_station_code_bound"
    assert by_item["rail_station_binding_R"]["weak_for_final_claim"] == "false"
    assert by_item["rail_headway"]["evidence_status"] == "missing_cached_timing_evidence"
    assert by_item["rail_headway"]["weak_for_final_claim"] == "true"
    assert by_item["rail_travel_time"]["review_priority"] == "high"
    assert by_item["rail_capacity"]["evidence_status"] == "source_backed_or_sensitivity_acknowledged"
    assert by_item["rail_capacity"]["weak_for_final_claim"] == "false"
    assert by_item["rail_timetable_derivation_path"]["evidence_status"] == "derivation_path_available_no_default_cache"
    assert {row["claim_boundary"] for row in rows} == {RAIL_EVIDENCE_REVIEW_PACKET_SCOPE}

    print("PASS: rail evidence review rows cover current gaps")


def test_write_rail_evidence_review_packet_outputs_csv_and_manifest() -> None:
    """Writer should emit stable CSV fields and non-acceptance manifest."""

    rows = build_rail_evidence_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "rail_evidence_review.csv"
        manifest = Path(directory) / "rail_evidence_review_manifest.json"
        value = write_rail_evidence_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == RAIL_EVIDENCE_REVIEW_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 10
        assert value["publication_ready"] is False
        assert value["station_binding_ready"] is True
        assert value["service_publication_ready"] is False
        assert written_manifest["row_count"] == 10
        assert written_manifest["weak_for_final_claim_count"] == 7
        assert "does not derive headway or travel time" in written_manifest["claim_boundary"]

    print("PASS: rail evidence review packet writer emits CSV and manifest")


def test_shipped_rail_evidence_review_packet_matches_current_inputs() -> None:
    """Current shipped review packet should match deterministic rail inputs."""

    rows = build_rail_evidence_review_rows()

    assert DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_RAIL_EVIDENCE_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_RAIL_EVIDENCE_REVIEW_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["review_item_id"] for row in written_rows] == [
        row["review_item_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["result_scope"] == RAIL_EVIDENCE_REVIEW_PACKET_SCOPE

    print("PASS: shipped rail evidence review packet matches current inputs")


if __name__ == "__main__":
    test_rail_evidence_review_rows_cover_current_gaps()
    test_write_rail_evidence_review_packet_outputs_csv_and_manifest()
    test_shipped_rail_evidence_review_packet_matches_current_inputs()
    print("\n=== REALWORLD RAIL EVIDENCE REVIEW PACKET TESTS PASSED ===")
