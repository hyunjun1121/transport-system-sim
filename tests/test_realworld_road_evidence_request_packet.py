"""Tests for road evidence source-request packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_evidence_request_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH,
    DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    ROAD_EVIDENCE_SOURCE_REQUEST_COLUMNS,
    ROAD_EVIDENCE_SOURCE_REQUEST_SCOPE,
    build_road_evidence_source_request_rows,
    write_road_evidence_source_request_packet,
)


def test_road_evidence_source_request_rows_are_actionable() -> None:
    """Rows should name missing source inputs and review/application paths."""

    rows = build_road_evidence_source_request_rows()
    by_id = {row["request_id"]: row for row in rows}

    assert len(rows) == 5
    assert "residential" in by_id["road_speed_limit_source_request"][
        "prioritized_highway_classes"
    ]
    assert by_id["road_speed_limit_source_request"]["expected_derived_fields"] == "speed_kph"
    assert "write_road_speed_evidence.py" in by_id["road_speed_limit_source_request"][
        "fetch_or_acquisition_command"
    ]
    assert (
        by_id["road_capacity_lane_count_source_request"]["expected_derived_fields"]
        == "capacity_veh_per_hr"
    )
    assert "traffic counts" in by_id["road_capacity_lane_count_source_request"][
        "required_external_input"
    ]
    assert by_id["road_disruption_probability_source_request"][
        "expected_derived_fields"
    ] == "base_p_fail;capacity_reduction_factor;blockage_rule"
    assert by_id["reviewed_road_class_override_application_request"][
        "can_close_road_evidence_gate"
    ] == "true"
    assert by_id["reviewed_road_class_override_application_request"][
        "can_close_road_application_gate"
    ] == "true"
    assert {row["claim_boundary"] for row in rows} == {
        ROAD_EVIDENCE_SOURCE_REQUEST_SCOPE
    }

    print("PASS: road evidence source-request rows are actionable")


def test_write_road_evidence_source_request_packet_outputs_csv_and_manifest() -> None:
    """Writer should emit stable CSV fields and non-acceptance manifest."""

    rows = build_road_evidence_source_request_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "road_evidence_request.csv"
        manifest = Path(directory) / "road_evidence_request_manifest.json"
        value = write_road_evidence_source_request_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == ROAD_EVIDENCE_SOURCE_REQUEST_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 5
        assert value["publication_ready"] is False
        assert value["road_evidence_closure_candidate_count"] == 1
        assert value["road_application_closure_candidate_count"] == 1
        assert written_manifest["row_count"] == 5
        assert "does not contain reviewed speed observations" in written_manifest[
            "claim_boundary"
        ]

    print("PASS: road evidence source-request writer emits CSV and manifest")


def test_shipped_road_evidence_source_request_packet_matches_current_inputs() -> None:
    """Current shipped request packet should match deterministic road-review inputs."""

    rows = build_road_evidence_source_request_rows()

    assert DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH.exists()
    assert DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH.exists()
    with DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["request_id"] for row in written_rows] == [
        row["request_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["result_scope"] == ROAD_EVIDENCE_SOURCE_REQUEST_SCOPE

    print("PASS: shipped road evidence source-request packet matches current inputs")


if __name__ == "__main__":
    test_road_evidence_source_request_rows_are_actionable()
    test_write_road_evidence_source_request_packet_outputs_csv_and_manifest()
    test_shipped_road_evidence_source_request_packet_matches_current_inputs()
    print("\n=== REALWORLD ROAD EVIDENCE SOURCE-REQUEST TESTS PASSED ===")
