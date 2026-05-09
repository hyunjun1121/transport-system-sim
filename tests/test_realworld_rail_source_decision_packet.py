"""Tests for rail source-decision packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_source_decision_packet import (  # noqa: E402
    DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    RAIL_SOURCE_DECISION_COLUMNS,
    RAIL_SOURCE_DECISION_SCOPE,
    build_rail_source_decision_rows,
    write_rail_source_decision_packet,
)
from src.realworld.rail_timing_request_packet import (  # noqa: E402
    KTDB_GTFS_SOURCE_METADATA_PATHS,
    METRO9_CAPACITY_RAW_PATH,
    METRO9_CAPACITY_SOURCE_CITATION,
    RAIL_CAPACITY_REVIEW_INPUT_PATHS,
)


def test_rail_source_decision_rows_classify_current_requests() -> None:
    """Current rail fetch-readiness rows should become pending decisions."""

    rows = build_rail_source_decision_rows()
    by_id = {row["request_id"]: row for row in rows}

    assert len(rows) == 5
    assert set(by_id) == {
        "rail_availability_scenario_request",
        "rail_capacity_treatment_request",
        "rail_shortest_path_travel_time_request",
        "rail_static_gtfs_timing_request",
        "rail_timetable_headway_request",
    }
    assert {
        row["decision_status"]
        for row in rows
        if row["request_id"]
        in {
            "rail_shortest_path_travel_time_request",
            "rail_static_gtfs_timing_request",
            "rail_timetable_headway_request",
        }
    } == {"blocked_missing_rail_source_decision"}
    assert {
        row["decision_status"]
        for row in rows
        if row["request_id"]
        in {
            "rail_availability_scenario_request",
            "rail_capacity_treatment_request",
        }
    } == {"needs_human_review_rail_source_decision"}
    assert {row["provisional_decision"] for row in rows} == {
        "pending_reviewer_decision"
    }
    assert "provide_reviewed_static_gtfs_feed" in by_id[
        "rail_static_gtfs_timing_request"
    ]["candidate_decision_options"]
    gtfs = by_id["rail_static_gtfs_timing_request"]
    assert gtfs["raw_payload_path"] == KTDB_GTFS_SOURCE_METADATA_PATHS
    assert gtfs["raw_payload_present"] == "true"
    assert "replace_with_operator_or_literature_capacity_source" in by_id[
        "rail_capacity_treatment_request"
    ]["candidate_decision_options"]
    capacity = by_id["rail_capacity_treatment_request"]
    assert capacity["source_url_or_citation"] == METRO9_CAPACITY_SOURCE_CITATION
    assert capacity["source_cache_path"] == RAIL_CAPACITY_REVIEW_INPUT_PATHS
    assert capacity["raw_payload_path"] == METRO9_CAPACITY_RAW_PATH
    assert "metro9_capacity_source_extract.csv" in capacity["followup_artifacts"]
    assert "metro9_capacity_source_raw.html" in capacity["followup_artifacts"]
    assert capacity["can_support_rail_evidence_gate"] == "false"
    assert "not_operational_claim_boundary" in by_id[
        "rail_timetable_headway_request"
    ]["required_evidence_fields"]
    assert {
        row["can_support_timing_fields_after_review"]
        for row in rows
        if row["request_id"]
        in {
            "rail_shortest_path_travel_time_request",
            "rail_static_gtfs_timing_request",
            "rail_timetable_headway_request",
        }
    } == {"true"}
    assert {row["can_support_rail_evidence_gate"] for row in rows} == {"false"}
    assert {row["can_support_acceptance_gate"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {RAIL_SOURCE_DECISION_SCOPE}

    print("PASS: rail source-decision rows classify current requests")


def test_rail_source_decision_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_rail_source_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "rail_source_decision.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "rail_source_decision.md"
        manifest = write_rail_source_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == RAIL_SOURCE_DECISION_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 5
    assert written_manifest["blocking_decision_count"] == 3
    assert written_manifest["human_review_decision_count"] == 2
    assert written_manifest["timing_source_decision_count"] == 3
    assert "Rail Source Decision Packet" in doc_text
    assert "metro9_capacity_source_extract.csv" in doc_text
    assert "metro9_capacity_source_raw.html" in doc_text

    print("PASS: rail source-decision writer emits artifacts")


def test_shipped_rail_source_decision_packet_matches_current_outputs() -> None:
    """Committed decision packet should match current readiness rows."""

    rows = build_rail_source_decision_rows()

    assert DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH.exists()
    assert DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_decision_count"] == 3
    assert manifest["human_review_decision_count"] == 2
    assert manifest["rail_source_decision_recorded"] is False
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped rail source-decision packet matches outputs")


if __name__ == "__main__":
    test_rail_source_decision_rows_classify_current_requests()
    test_rail_source_decision_writer_outputs_artifacts()
    test_shipped_rail_source_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD RAIL SOURCE DECISION TESTS PASSED ===")
