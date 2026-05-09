"""Tests for parameter source-decision packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.parameter_source_decision_packet import (  # noqa: E402
    DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH,
    PARAMETER_SOURCE_DECISION_COLUMNS,
    PARAMETER_SOURCE_DECISION_SCOPE,
    build_parameter_source_decision_rows,
    write_parameter_source_decision_packet,
)


def test_parameter_source_decision_rows_classify_current_requests() -> None:
    """Current parameter source-readiness rows should become decisions."""

    rows = build_parameter_source_decision_rows()
    by_id = {row["request_id"]: row for row in rows}

    assert len(rows) == 7
    assert set(by_id) == {
        "background_traffic_bpr_calibration_source_request",
        "demand_arrival_horizon_censoring_source_request",
        "dispatch_turnaround_source_request",
        "disruption_scenario_assumption_source_request",
        "fleet_vehicle_capacity_source_request",
        "rail_service_parameter_source_request",
        "transfer_delay_source_request",
    }
    assert by_id["transfer_delay_source_request"]["decision_status"] == (
        "needs_human_review_parameter_source_decision"
    )
    assert by_id["rail_service_parameter_source_request"]["decision_status"] == (
        "blocked_missing_parameter_source_decision"
    )
    assert {
        row["decision_status"]
        for row in rows
        if row["request_id"] not in {
            "rail_service_parameter_source_request",
        }
    } == {"needs_human_review_parameter_source_decision"}
    assert {row["provisional_decision"] for row in rows} == {
        "pending_reviewer_decision"
    }
    assert "retain_as_sensitivity_only" in by_id[
        "disruption_scenario_assumption_source_request"
    ]["candidate_decision_options"]
    assert "supply_transfer_layout_or_pedestrian_flow_source" in by_id[
        "transfer_delay_source_request"
    ]["candidate_decision_options"]
    assert "use_rail_timing_or_gtfs_source_decision_packet" in by_id[
        "rail_service_parameter_source_request"
    ]["candidate_decision_options"]
    assert "metro9_capacity_source_extract.csv" in by_id[
        "rail_service_parameter_source_request"
    ]["followup_artifacts"]
    assert "not_operational_claim_boundary" in by_id[
        "background_traffic_bpr_calibration_source_request"
    ]["required_evidence_fields"]
    assert {row["can_support_parameter_evidence_gate"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {
        PARAMETER_SOURCE_DECISION_SCOPE
    }

    print("PASS: parameter source-decision rows classify current requests")


def test_parameter_source_decision_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_parameter_source_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "parameter_source_decision.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "parameter_source_decision.md"
        manifest = write_parameter_source_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                PARAMETER_SOURCE_DECISION_COLUMNS
            )
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 7
    assert written_manifest["blocking_decision_count"] == 1
    assert written_manifest["human_review_decision_count"] == 6
    assert written_manifest["weak_parameter_count"] == 23
    assert written_manifest["parameter_acceptance_present"] is False
    assert "Parameter Source Decision Packet" in doc_text

    print("PASS: parameter source-decision writer emits artifacts")


def test_shipped_parameter_source_decision_packet_matches_current_outputs() -> None:
    """Committed decision packet should match current readiness rows."""

    rows = build_parameter_source_decision_rows()

    assert DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH.exists()
    assert DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_decision_count"] == 1
    assert manifest["human_review_decision_count"] == 6
    assert manifest["parameter_source_decision_recorded"] is False
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped parameter source-decision packet matches outputs")


if __name__ == "__main__":
    test_parameter_source_decision_rows_classify_current_requests()
    test_parameter_source_decision_writer_outputs_artifacts()
    test_shipped_parameter_source_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD PARAMETER SOURCE DECISION TESTS PASSED ===")
