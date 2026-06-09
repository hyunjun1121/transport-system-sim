"""Tests for rail evidence priority packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_evidence_priority_packet import (  # noqa: E402
    DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
    RAIL_EVIDENCE_PRIORITY_COLUMNS,
    RAIL_EVIDENCE_PRIORITY_SCOPE,
    build_rail_evidence_priority_rows,
    write_rail_evidence_priority_packet,
)
from src.realworld.rail_timing_request_packet import (  # noqa: E402
    KTDB_GTFS_SOURCE_METADATA_PATHS,
    METRO9_CAPACITY_RAW_PATH,
    RAIL_CAPACITY_REVIEW_INPUT_PATHS,
    STATIC_TIMETABLE_SOURCE_NAME,
)


def test_rail_evidence_priority_rows_classify_current_closure_paths() -> None:
    """Current rail packets should produce field-level closure priorities."""

    rows = build_rail_evidence_priority_rows()
    by_id = {row["priority_id"]: row for row in rows}

    assert len(rows) == 7
    assert by_id["rail_timetable_headway_request"]["readiness_status"] == (
        "blocked_missing_data_go_kr_key"
    )
    assert by_id["rail_static_timetable_csv_headway_request"]["readiness_status"] == (
        "ready_reviewed_static_timetable_cache_for_derivation_review"
    )
    assert by_id["rail_static_timetable_csv_headway_request"]["source_name"] == (
        STATIC_TIMETABLE_SOURCE_NAME
    )
    assert by_id["rail_static_timetable_csv_headway_request"][
        "can_close_timing_fields_after_review"
    ] == "false"
    assert by_id["rail_static_timetable_csv_headway_request"][
        "source_cache_present"
    ] == "true"
    assert by_id["rail_static_timetable_csv_headway_request"][
        "raw_payload_present"
    ] == "true"
    assert by_id["rail_shortest_path_travel_time_request"]["readiness_status"] == (
        "blocked_missing_data_go_kr_key"
    )
    assert by_id["rail_static_gtfs_timing_request"]["readiness_status"] == (
        "blocked_missing_reviewed_gtfs_file"
    )
    assert by_id["rail_static_gtfs_timing_request"][
        "can_close_timing_fields_after_review"
    ] == "true"
    assert by_id["rail_static_gtfs_timing_request"]["raw_payload_path"] == (
        KTDB_GTFS_SOURCE_METADATA_PATHS
    )
    assert by_id["rail_static_gtfs_timing_request"]["raw_payload_present"] == "true"
    assert by_id["station_binding_prerequisite"]["readiness_status"] == (
        "prerequisite_ready_not_timing_evidence"
    )
    assert by_id["rail_capacity_treatment_request"]["readiness_status"] == (
        "needs_human_review_capacity_treatment"
    )
    assert by_id["rail_capacity_treatment_request"]["source_cache_path"] == (
        RAIL_CAPACITY_REVIEW_INPUT_PATHS
    )
    assert by_id["rail_capacity_treatment_request"]["source_cache_present"] == "true"
    assert by_id["rail_capacity_treatment_request"]["raw_payload_path"] == (
        METRO9_CAPACITY_RAW_PATH
    )
    assert by_id["rail_capacity_treatment_request"]["raw_payload_present"] == "true"
    assert {row["claim_boundary"] for row in rows} == {
        RAIL_EVIDENCE_PRIORITY_SCOPE
    }
    assert all(row["can_support_rail_evidence_gate"] == "false" for row in rows)

    print("PASS: rail evidence priority rows classify current closure paths")


def test_rail_evidence_priority_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_rail_evidence_priority_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "rail_priority.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "rail_priority.md"
        manifest = write_rail_evidence_priority_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == RAIL_EVIDENCE_PRIORITY_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 7
    assert written_manifest["blocking_priority_count"] == 3
    assert written_manifest["human_review_priority_count"] == 2
    assert "Rail Evidence Priority Packet" in doc_text
    assert STATIC_TIMETABLE_SOURCE_NAME in doc_text
    assert "metro9_capacity_source_extract.csv" in doc_text
    assert "metro9_capacity_source_raw.html" in doc_text

    print("PASS: rail evidence priority writer emits artifacts")


def test_shipped_rail_evidence_priority_packet_matches_current_outputs() -> None:
    """Committed rail priority packet should match current rail artifacts."""

    rows = build_rail_evidence_priority_rows()

    assert DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH.exists()
    assert DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH.exists()
    with DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["timing_closure_candidate_count"] == 1
    assert manifest["station_binding_prerequisite_ready"] is True
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped rail evidence priority packet matches current outputs")


if __name__ == "__main__":
    test_rail_evidence_priority_rows_classify_current_closure_paths()
    test_rail_evidence_priority_writer_outputs_artifacts()
    test_shipped_rail_evidence_priority_packet_matches_current_outputs()
    print("\n=== REALWORLD RAIL EVIDENCE PRIORITY TESTS PASSED ===")
