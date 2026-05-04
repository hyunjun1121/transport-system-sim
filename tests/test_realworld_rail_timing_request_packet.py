"""Tests for rail timing source-request packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_timing_request_packet import (  # noqa: E402
    DEFAULT_RAIL_TIMING_SOURCE_REQUEST_MANIFEST_PATH,
    DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    RAIL_TIMING_SOURCE_REQUEST_COLUMNS,
    RAIL_TIMING_SOURCE_REQUEST_SCOPE,
    build_rail_timing_source_request_rows,
    write_rail_timing_source_request_packet,
)


def test_rail_timing_source_request_rows_are_actionable() -> None:
    """Rows should name exact missing source inputs and derivation paths."""

    rows = build_rail_timing_source_request_rows()
    by_id = {row["request_id"]: row for row in rows}

    assert len(rows) == 5
    assert by_id["rail_timetable_headway_request"]["expected_derived_fields"] == "headway"
    assert "DATA_GO_KR_KEY" in by_id["rail_timetable_headway_request"]["required_external_input"]
    assert "fetch_rail_timetable_cache.py" in by_id["rail_timetable_headway_request"]["fetch_command"]
    assert by_id["rail_shortest_path_travel_time_request"]["expected_derived_fields"] == "travel_time"
    assert "derive_rail_shortest_path_evidence.py" in by_id["rail_shortest_path_travel_time_request"]["derive_command"]
    assert by_id["rail_static_gtfs_timing_request"]["can_close_rail_timing_gate"] == "true"
    assert by_id["rail_static_gtfs_timing_request"]["expected_derived_fields"] == "headway;travel_time"
    assert by_id["rail_capacity_treatment_request"]["can_close_rail_timing_gate"] == "false"
    assert {row["claim_boundary"] for row in rows} == {RAIL_TIMING_SOURCE_REQUEST_SCOPE}

    print("PASS: rail timing source-request rows are actionable")


def test_write_rail_timing_source_request_packet_outputs_csv_and_manifest() -> None:
    """Writer should emit stable CSV fields and non-acceptance manifest."""

    rows = build_rail_timing_source_request_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "rail_timing_request.csv"
        manifest = Path(directory) / "rail_timing_request_manifest.json"
        value = write_rail_timing_source_request_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == RAIL_TIMING_SOURCE_REQUEST_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 5
        assert value["publication_ready"] is False
        assert value["timing_closure_candidate_count"] == 1
        assert value["requires_private_or_reviewed_input_count"] == 3
        assert written_manifest["row_count"] == 5
        assert "does not contain cached source observations" in written_manifest["claim_boundary"]

    print("PASS: rail timing source-request writer emits CSV and manifest")


def test_shipped_rail_timing_source_request_packet_matches_current_inputs() -> None:
    """Current shipped request packet should match deterministic station bindings."""

    rows = build_rail_timing_source_request_rows()

    assert DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH.exists()
    assert DEFAULT_RAIL_TIMING_SOURCE_REQUEST_MANIFEST_PATH.exists()
    with DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_RAIL_TIMING_SOURCE_REQUEST_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["request_id"] for row in written_rows] == [
        row["request_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["result_scope"] == RAIL_TIMING_SOURCE_REQUEST_SCOPE

    print("PASS: shipped rail timing source-request packet matches current inputs")


if __name__ == "__main__":
    test_rail_timing_source_request_rows_are_actionable()
    test_write_rail_timing_source_request_packet_outputs_csv_and_manifest()
    test_shipped_rail_timing_source_request_packet_matches_current_inputs()
    print("\n=== REALWORLD RAIL TIMING SOURCE-REQUEST TESTS PASSED ===")
