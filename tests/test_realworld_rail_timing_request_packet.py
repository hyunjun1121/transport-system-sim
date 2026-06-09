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
    KTDB_GTFS_SOURCE_METADATA_PATHS,
    METRO9_CAPACITY_EXTRACT_PATH,
    METRO9_CAPACITY_RAW_PATH,
    METRO9_CAPACITY_SOURCE_CITATION,
    RAIL_CAPACITY_REVIEW_INPUT_PATHS,
    RAIL_TIMING_SOURCE_REQUEST_COLUMNS,
    RAIL_TIMING_SOURCE_REQUEST_SCOPE,
    STATIC_TIMETABLE_SOURCE_CITATION,
    STATIC_TIMETABLE_SOURCE_NAME,
    build_rail_timing_source_request_rows,
    write_rail_timing_source_request_packet,
)


def test_rail_timing_source_request_rows_are_actionable() -> None:
    """Rows should name exact missing source inputs and derivation paths."""

    rows = build_rail_timing_source_request_rows()
    by_id = {row["request_id"]: row for row in rows}

    assert len(rows) == 6
    assert by_id["rail_timetable_headway_request"]["expected_derived_fields"] == "headway"
    assert "DATA_GO_KR_KEY" in by_id["rail_timetable_headway_request"]["required_external_input"]
    assert "fetch_rail_timetable_cache.py" in by_id["rail_timetable_headway_request"]["fetch_command"]
    static_csv = by_id["rail_static_timetable_csv_headway_request"]
    assert static_csv["source_type"] == "reviewed_static_timetable_csv_required"
    assert static_csv["source_name"] == STATIC_TIMETABLE_SOURCE_NAME
    assert static_csv["source_url_or_citation"] == STATIC_TIMETABLE_SOURCE_CITATION
    assert static_csv["expected_derived_fields"] == "headway"
    assert static_csv["can_close_rail_timing_gate"] == "false"
    assert "explicit source-column mappings" in static_csv["required_external_input"]
    assert "normalize_rail_timetable_cache.py" in static_csv["fetch_command"]
    assert "REVIEWED_TRIP_ID_COLUMN" in static_csv["fetch_command"]
    assert static_csv["source_cache_path"] == (
        "data/rail/pilot_rail_static_timetable_cache.csv"
    )
    assert "pilot_rail_timetable_static_source.csv" in static_csv["raw_payload_path"]
    assert "pilot_rail_static_timetable_cache_manifest.json" in static_csv[
        "raw_payload_path"
    ]
    assert "own station identifier namespace" in static_csv["notes"]
    assert by_id["rail_timetable_headway_request"]["source_cache_path"] == (
        "data/rail/pilot_rail_timetable_api_cache.csv"
    )
    assert by_id["rail_timetable_headway_request"]["source_cache_path"] != static_csv[
        "source_cache_path"
    ]
    assert STATIC_TIMETABLE_SOURCE_CITATION in static_csv[
        "derive_command"
    ]
    assert by_id["rail_shortest_path_travel_time_request"]["expected_derived_fields"] == "travel_time"
    assert "derive_rail_shortest_path_evidence.py" in by_id["rail_shortest_path_travel_time_request"]["derive_command"]
    assert by_id["rail_static_gtfs_timing_request"]["can_close_rail_timing_gate"] == "true"
    assert by_id["rail_static_gtfs_timing_request"]["expected_derived_fields"] == "headway;travel_time"
    assert "GTFS Validator report" in by_id[
        "rail_static_gtfs_timing_request"
    ]["required_external_input"]
    assert "pilot_gtfs_validator_report.json" in by_id[
        "rail_static_gtfs_timing_request"
    ]["source_cache_path"]
    assert "--gtfs-validator-report" in by_id[
        "rail_static_gtfs_timing_request"
    ]["derive_command"]
    assert by_id["rail_static_gtfs_timing_request"]["raw_payload_path"] == (
        KTDB_GTFS_SOURCE_METADATA_PATHS
    )
    assert "cached KTDB source metadata" in by_id[
        "rail_static_gtfs_timing_request"
    ]["fetch_command"]
    assert by_id["rail_capacity_treatment_request"]["can_close_rail_timing_gate"] == "false"
    capacity = by_id["rail_capacity_treatment_request"]
    assert capacity["source_url_or_citation"] == METRO9_CAPACITY_SOURCE_CITATION
    assert capacity["source_cache_path"] == RAIL_CAPACITY_REVIEW_INPUT_PATHS
    assert capacity["raw_payload_path"] == METRO9_CAPACITY_RAW_PATH
    assert METRO9_CAPACITY_EXTRACT_PATH in capacity["source_cache_path"]
    assert "review only" in capacity["notes"]
    assert {row["claim_boundary"] for row in rows} == {RAIL_TIMING_SOURCE_REQUEST_SCOPE}

    print("PASS: rail timing source-request rows are actionable")


def test_rail_timing_source_request_rows_use_binding_region_and_cache_prefix() -> None:
    """Rows should be reusable for non-pilot station-binding tables."""

    with TemporaryDirectory() as directory:
        binding_path = Path(directory) / "rail_station_bindings.csv"
        _write_station_binding_fixture(binding_path)

        rows = build_rail_timing_source_request_rows(
            station_binding_path=binding_path,
            cache_prefix="synthetic_region_fixture",
        )
        expected_binding_arg = str(binding_path).replace("/", "\\")
    by_id = {row["request_id"]: row for row in rows}

    assert {row["region_id"] for row in rows} == {"synthetic_region_fixture"}
    assert by_id["rail_timetable_headway_request"]["source_cache_path"] == (
        "data/rail/synthetic_region_fixture_rail_timetable_api_cache.csv"
    )
    assert by_id["rail_static_timetable_csv_headway_request"]["source_cache_path"] == (
        "data/rail/synthetic_region_fixture_rail_static_timetable_cache.csv"
    )
    assert "synthetic_region_fixture_rail_timetable_static_source.csv" in by_id[
        "rail_static_timetable_csv_headway_request"
    ]["fetch_command"]
    assert "synthetic_region_fixture_rail_static_timetable_cache_manifest.json" in by_id[
        "rail_static_timetable_csv_headway_request"
    ]["fetch_command"]
    assert "--region-id synthetic_region_fixture" in by_id[
        "rail_timetable_headway_request"
    ]["derive_command"]
    assert "synthetic_region_fixture_rail_headway_v1" in by_id[
        "rail_timetable_headway_request"
    ]["derive_command"]
    assert f"--station-bindings {expected_binding_arg}" in by_id[
        "rail_timetable_headway_request"
    ]["derive_command"]
    assert "synthetic_region_fixture_rail_shortest_path_cache.csv" in by_id[
        "rail_shortest_path_travel_time_request"
    ]["fetch_command"]
    assert f"--station-bindings {expected_binding_arg}" in by_id[
        "rail_shortest_path_travel_time_request"
    ]["derive_command"]
    assert "synthetic_region_fixture_rail_gtfs_v1" in by_id[
        "rail_static_gtfs_timing_request"
    ]["derive_command"]
    assert "synthetic_region_fixture_gtfs_validator_report.json" in by_id[
        "rail_static_gtfs_timing_request"
    ]["derive_command"]

    print("PASS: rail timing source-request rows use binding region and cache prefix")


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

        assert len(written_rows) == 6
        assert value["publication_ready"] is False
        assert value["region_ids"] == ["songpa_public_demo"]
        assert value["timing_closure_candidate_count"] == 1
        assert value["requires_private_or_reviewed_input_count"] == 4
        assert written_manifest["row_count"] == 6
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
    assert manifest["region_ids"] == ["songpa_public_demo"]
    assert manifest["result_scope"] == RAIL_TIMING_SOURCE_REQUEST_SCOPE

    print("PASS: shipped rail timing source-request packet matches current inputs")


def _write_station_binding_fixture(path: Path) -> None:
    columns = [
        "binding_id",
        "region_id",
        "point_id",
        "station_name",
        "station_id",
        "station_code",
        "source_name",
        "source_url_or_citation",
        "source_accessed_date",
        "source_status",
        "claim_scope",
        "notes",
    ]
    rows = [
        {
            "binding_id": "synthetic_S_1",
            "region_id": "synthetic_region_fixture",
            "point_id": "S",
            "station_name": "Synthetic Access",
            "station_id": "S100",
            "station_code": "100",
            "source_name": "Synthetic fixture",
            "source_url_or_citation": "tests/fixtures/synthetic_region_fixture.yaml",
            "source_accessed_date": "2026-05-08",
            "source_status": "official_station_code_bound",
            "claim_scope": "official station-code binding fixture only",
            "notes": "fixture row",
        },
        {
            "binding_id": "synthetic_R_1",
            "region_id": "synthetic_region_fixture",
            "point_id": "R",
            "station_name": "Synthetic Egress",
            "station_id": "R200",
            "station_code": "200",
            "source_name": "Synthetic fixture",
            "source_url_or_citation": "tests/fixtures/synthetic_region_fixture.yaml",
            "source_accessed_date": "2026-05-08",
            "source_status": "official_station_code_bound",
            "claim_scope": "official station-code binding fixture only",
            "notes": "fixture row",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    test_rail_timing_source_request_rows_are_actionable()
    test_rail_timing_source_request_rows_use_binding_region_and_cache_prefix()
    test_write_rail_timing_source_request_packet_outputs_csv_and_manifest()
    test_shipped_rail_timing_source_request_packet_matches_current_inputs()
    print("\n=== REALWORLD RAIL TIMING SOURCE-REQUEST TESTS PASSED ===")
