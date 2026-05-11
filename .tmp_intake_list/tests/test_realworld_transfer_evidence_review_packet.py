"""Tests for transfer evidence review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.transfer_evidence_review_packet import (  # noqa: E402
    DEFAULT_TRANSFER_EVIDENCE_REVIEW_MANIFEST_PATH,
    DEFAULT_TRANSFER_EVIDENCE_REVIEW_PACKET_PATH,
    TRANSFER_EVIDENCE_REVIEW_COLUMNS,
    TRANSFER_EVIDENCE_REVIEW_SCOPE,
    build_transfer_evidence_review_rows,
    write_transfer_evidence_review_packet,
)


def test_transfer_evidence_review_rows_expose_current_transfer_gap() -> None:
    """Rows should trace current transfer values and keep source gaps visible."""

    rows = build_transfer_evidence_review_rows()
    by_id = {row["review_item_id"]: row for row in rows}

    assert len(rows) == 5
    assert set(by_id) == {
        "transfer_delay_parameter_trace",
        "transfer_sensitivity_bounds",
        "transfer_access_station_context",
        "transfer_egress_station_context",
        "transfer_station_layout_or_observation_gap",
    }
    assert by_id["transfer_delay_parameter_trace"]["current_value"] == (
        "fixed=5 min; per_passenger=0 min/pax"
    )
    assert "fixed_range=0-10" in by_id["transfer_sensitivity_bounds"]["current_value"]
    assert "station_code=936" in by_id["transfer_access_station_context"]["current_value"]
    assert "station_code=814" in by_id["transfer_egress_station_context"]["current_value"]
    assert by_id["transfer_station_layout_or_observation_gap"]["evidence_status"] == (
        "missing_station_layout_or_observed_transfer_source"
    )
    assert {row["claim_boundary"] for row in rows} == {TRANSFER_EVIDENCE_REVIEW_SCOPE}

    print("PASS: transfer evidence review rows expose current gap")


def test_transfer_evidence_review_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_transfer_evidence_review_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "transfer_evidence.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "transfer_evidence.md"
        manifest = write_transfer_evidence_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == TRANSFER_EVIDENCE_REVIEW_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["blocking_review_count"] == 1
    assert manifest["human_review_count"] == 4
    assert written_manifest["row_count"] == 5
    assert "Transfer Evidence Review Packet" in doc_text

    print("PASS: transfer evidence review writer emits artifacts")


def test_shipped_transfer_evidence_review_packet_matches_current_outputs() -> None:
    """Committed transfer review packet should match current inputs."""

    rows = build_transfer_evidence_review_rows()

    assert DEFAULT_TRANSFER_EVIDENCE_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_TRANSFER_EVIDENCE_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_TRANSFER_EVIDENCE_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_TRANSFER_EVIDENCE_REVIEW_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_review_count"] == 1
    assert manifest["parameter_evidence_gate_closure_candidate_count"] == 0
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped transfer evidence review packet matches outputs")


if __name__ == "__main__":
    test_transfer_evidence_review_rows_expose_current_transfer_gap()
    test_transfer_evidence_review_writer_outputs_artifacts()
    test_shipped_transfer_evidence_review_packet_matches_current_outputs()
    print("\n=== REALWORLD TRANSFER EVIDENCE REVIEW TESTS PASSED ===")
