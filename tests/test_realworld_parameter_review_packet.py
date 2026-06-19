"""Tests for parameter evidence review-packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.parameter_review_packet import (  # noqa: E402
    DEFAULT_PARAMETER_REVIEW_PACKET_MANIFEST_PATH,
    DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    METRO9_CAPACITY_EXTRACT_PATH,
    METRO9_CAPACITY_RAW_PATH,
    PARAMETER_REVIEW_PACKET_COLUMNS,
    PARAMETER_REVIEW_PACKET_SCOPE,
    build_parameter_review_rows,
    write_parameter_review_packet,
)


def test_parameter_review_rows_cover_current_core_parameters() -> None:
    """The shipped review packet should expose every core parameter status."""

    rows = build_parameter_review_rows()
    by_parameter = {row["parameter"]: row for row in rows}

    assert len(rows) == 29
    assert len(by_parameter) == 29
    assert by_parameter["road_capacity_proxy"]["review_priority"] == "low"
    assert by_parameter["rail_headway"]["review_priority"] == "low"
    assert by_parameter["bpr_alpha"]["weak_for_final_claim"] == "false"
    assert by_parameter["rail_capacity"]["evidence_category"] == "source-backed"
    assert by_parameter["rail_capacity"]["weak_for_final_claim"] == "false"
    assert (
        METRO9_CAPACITY_EXTRACT_PATH
        in by_parameter["rail_capacity"]["candidate_artifacts"]
    )
    assert (
        METRO9_CAPACITY_RAW_PATH
        in by_parameter["rail_capacity"]["candidate_artifacts"]
    )
    assert by_parameter["road_capacity_proxy"]["claim_boundary"] == PARAMETER_REVIEW_PACKET_SCOPE
    assert "road_capacity_evidence_candidates.csv" in by_parameter["road_capacity_proxy"]["candidate_artifacts"]
    assert sum(1 for row in rows if row["weak_for_final_claim"] == "true") == 0

    print("PASS: parameter review rows cover current core parameters")


def test_write_parameter_review_packet_outputs_csv_and_manifest() -> None:
    """Writer should emit a stable CSV schema and conservative manifest."""

    rows = build_parameter_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "parameter_review.csv"
        manifest = Path(directory) / "parameter_review_manifest.json"
        value = write_parameter_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == PARAMETER_REVIEW_PACKET_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 29
        assert value["publication_ready"] is False
        assert written_manifest["weak_for_final_claim_count"] == 0
        assert "does not create accepted parameter values" in written_manifest["claim_boundary"]

    print("PASS: parameter review packet writer emits CSV and manifest")


def test_shipped_parameter_review_packet_matches_current_audit() -> None:
    """Current generated review packet should match current audit dimensions."""

    rows = build_parameter_review_rows()

    assert DEFAULT_PARAMETER_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_PARAMETER_REVIEW_PACKET_MANIFEST_PATH.exists()
    assert len(rows) == 29
    assert all(row["review_priority"] == "low" for row in rows)

    with DEFAULT_PARAMETER_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_PARAMETER_REVIEW_PACKET_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["row_count"] == len(rows)

    print("PASS: shipped parameter review packet matches current audit dimensions")


if __name__ == "__main__":
    test_parameter_review_rows_cover_current_core_parameters()
    test_write_parameter_review_packet_outputs_csv_and_manifest()
    test_shipped_parameter_review_packet_matches_current_audit()
    print("\n=== REALWORLD PARAMETER REVIEW PACKET TESTS PASSED ===")
