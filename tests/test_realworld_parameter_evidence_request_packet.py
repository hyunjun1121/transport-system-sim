"""Tests for cross-cutting parameter evidence source-request packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.parameter_evidence_request_packet import (  # noqa: E402
    DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH,
    DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    PARAMETER_EVIDENCE_SOURCE_REQUEST_COLUMNS,
    PARAMETER_EVIDENCE_SOURCE_REQUEST_SCOPE,
    build_parameter_evidence_source_request_rows,
    write_parameter_evidence_source_request_packet,
)


def test_parameter_evidence_source_request_rows_are_actionable() -> None:
    """Rows should cover current cross-cutting source gaps and commands."""

    rows = build_parameter_evidence_source_request_rows()
    by_id = {row["request_id"]: row for row in rows}

    assert len(rows) == 6
    assert by_id["demand_arrival_horizon_censoring_source_request"][
        "weak_parameter_count"
    ] == "5"
    assert "arrival process" in by_id[
        "demand_arrival_horizon_censoring_source_request"
    ]["required_external_input"]
    assert "passenger_volume" in by_id[
        "demand_arrival_horizon_censoring_source_request"
    ]["covered_parameters"]
    assert by_id["fleet_vehicle_capacity_source_request"][
        "expected_derived_fields"
    ] == (
        "bus_capacity;last_mile_vehicle_capacity;direct_bus_fleet_size;"
        "feeder_fleet_size;last_mile_fleet_size"
    )
    assert "fleet_assumptions.csv" in by_id[
        "fleet_vehicle_capacity_source_request"
    ]["target_output_path"]
    assert "dispatch_interval" in by_id[
        "dispatch_turnaround_source_request"
    ]["expected_derived_fields"]
    assert "transfer_per_passenger_delay" in by_id[
        "transfer_delay_source_request"
    ]["covered_parameters"]
    assert by_id["disruption_scenario_assumption_source_request"][
        "expected_derived_fields"
    ] == (
        "disruption_probability;capacity_reduction_factor;blockage_rule;"
        "base_disruption_probability"
    )
    assert "run_accessibility_loss_analysis.py" in by_id[
        "disruption_scenario_assumption_source_request"
    ]["acquisition_command"]
    assert "bpr_alpha" in by_id[
        "background_traffic_bpr_calibration_source_request"
    ]["covered_parameters"]
    assert "run_plausibility_validation.py" in by_id[
        "background_traffic_bpr_calibration_source_request"
    ]["acquisition_command"]
    assert {row["can_close_acceptance_gate"] for row in rows} == {"false"}
    assert {row["can_close_parameter_evidence_gate"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {
        PARAMETER_EVIDENCE_SOURCE_REQUEST_SCOPE
    }

    print("PASS: parameter evidence source-request rows are actionable")


def test_write_parameter_evidence_source_request_packet_outputs_manifest() -> None:
    """Writer should emit stable CSV fields and non-acceptance manifest."""

    rows = build_parameter_evidence_source_request_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "parameter_evidence_request.csv"
        manifest = Path(directory) / "parameter_evidence_request_manifest.json"
        value = write_parameter_evidence_source_request_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                PARAMETER_EVIDENCE_SOURCE_REQUEST_COLUMNS
            )
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 6
        assert value["publication_ready"] is False
        assert value["parameter_evidence_gate_closure_candidate_count"] == 0
        assert value["acceptance_gate_closure_candidate_count"] == 0
        assert value["covered_parameter_count"] == 22
        assert written_manifest["row_count"] == 6
        assert "does not contain reviewed source observations" in written_manifest[
            "claim_boundary"
        ]

    print("PASS: parameter evidence source-request writer emits CSV and manifest")


def test_shipped_parameter_evidence_source_request_packet_matches_current_inputs() -> None:
    """Current generated request packet should match current review-packet inputs."""

    rows = build_parameter_evidence_source_request_rows()

    assert DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH.exists()
    assert DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH.exists()
    with DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert written_rows == rows
    assert manifest["publication_ready"] is False
    assert manifest["row_count"] == len(rows)
    assert manifest["result_scope"] == PARAMETER_EVIDENCE_SOURCE_REQUEST_SCOPE

    print("PASS: shipped parameter evidence source-request packet matches inputs")


if __name__ == "__main__":
    test_parameter_evidence_source_request_rows_are_actionable()
    test_write_parameter_evidence_source_request_packet_outputs_manifest()
    test_shipped_parameter_evidence_source_request_packet_matches_current_inputs()
    print("\n=== REALWORLD PARAMETER EVIDENCE SOURCE-REQUEST TESTS PASSED ===")
