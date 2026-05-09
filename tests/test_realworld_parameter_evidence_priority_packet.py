"""Tests for parameter evidence priority packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.parameter_evidence_priority_packet import (  # noqa: E402
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
    PARAMETER_EVIDENCE_PRIORITY_COLUMNS,
    PARAMETER_EVIDENCE_PRIORITY_SCOPE,
    build_parameter_evidence_priority_rows,
    write_parameter_evidence_priority_packet,
)


def test_parameter_evidence_priority_rows_classify_current_sources() -> None:
    """Current parameter packets should produce source-priority rows."""

    rows = build_parameter_evidence_priority_rows()
    by_id = {row["priority_id"]: row for row in rows}

    assert len(rows) == 7
    assert by_id["transfer_delay_source_request"]["priority_status"] == (
        "needs_human_review_medium_priority_parameter_source"
    )
    assert by_id["rail_service_parameter_source_request"]["priority_status"] == (
        "blocked_missing_parameter_source"
    )
    assert by_id["rail_service_parameter_source_request"][
        "high_priority_parameter_count"
    ] == "3"
    assert "metro9_capacity_source_extract.csv" in by_id[
        "rail_service_parameter_source_request"
    ]["candidate_artifacts"]
    assert by_id["disruption_scenario_assumption_source_request"][
        "priority_status"
    ] == "needs_human_review_high_priority_parameter_source"
    assert by_id["background_traffic_bpr_calibration_source_request"][
        "priority_status"
    ] == "needs_human_review_high_priority_parameter_source"
    assert by_id["demand_arrival_horizon_censoring_source_request"][
        "priority_status"
    ] == "needs_human_review_medium_priority_parameter_source"
    assert by_id["fleet_vehicle_capacity_source_request"][
        "priority_status"
    ] == "needs_human_review_medium_priority_parameter_source"
    assert by_id["dispatch_turnaround_source_request"]["priority_status"] == (
        "needs_human_review_medium_priority_parameter_source"
    )
    assert "transfer_evidence_review_packet.csv" in by_id[
        "transfer_delay_source_request"
    ]["candidate_artifacts"]
    assert {row["claim_boundary"] for row in rows} == {
        PARAMETER_EVIDENCE_PRIORITY_SCOPE
    }
    assert all(row["can_support_parameter_evidence_gate"] == "false" for row in rows)

    print("PASS: parameter evidence priority rows classify current sources")


def test_parameter_evidence_priority_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_parameter_evidence_priority_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "parameter_priority.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "parameter_priority.md"
        manifest = write_parameter_evidence_priority_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == PARAMETER_EVIDENCE_PRIORITY_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 7
    assert written_manifest["blocking_priority_count"] == 1
    assert written_manifest["human_review_priority_count"] == 6
    assert "Parameter Evidence Priority Packet" in doc_text

    print("PASS: parameter evidence priority writer emits artifacts")


def test_shipped_parameter_evidence_priority_packet_matches_current_outputs() -> None:
    """Committed parameter priority packet should match current parameter artifacts."""

    rows = build_parameter_evidence_priority_rows()

    assert DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH.exists()
    assert DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH.exists()
    with DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["weak_parameter_count"] == 23
    assert manifest["high_priority_parameter_count"] == 9
    assert manifest["medium_priority_parameter_count"] == 14
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped parameter evidence priority packet matches current outputs")


if __name__ == "__main__":
    test_parameter_evidence_priority_rows_classify_current_sources()
    test_parameter_evidence_priority_writer_outputs_artifacts()
    test_shipped_parameter_evidence_priority_packet_matches_current_outputs()
    print("\n=== REALWORLD PARAMETER EVIDENCE PRIORITY TESTS PASSED ===")
