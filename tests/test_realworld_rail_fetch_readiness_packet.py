"""Tests for rail fetch-readiness packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_fetch_readiness_packet import (  # noqa: E402
    DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
    RAIL_FETCH_READINESS_COLUMNS,
    RAIL_FETCH_READINESS_SCOPE,
    build_rail_fetch_readiness_rows,
    write_rail_fetch_readiness_packet,
)
from src.realworld.rail_timing_request_packet import (  # noqa: E402
    KTDB_GTFS_SOURCE_CITATION,
    KTDB_GTFS_SOURCE_METADATA_PATHS,
    KTDB_GTFS_SOURCE_NAME,
    METRO9_CAPACITY_RAW_PATH,
    METRO9_CAPACITY_SOURCE_CITATION,
    RAIL_CAPACITY_REVIEW_INPUT_PATHS,
    STATIC_TIMETABLE_SOURCE_CITATION,
    STATIC_TIMETABLE_SOURCE_NAME,
)


def test_rail_fetch_readiness_rows_classify_blockers() -> None:
    """Rail source requests should become concrete preflight statuses."""

    rows = build_rail_fetch_readiness_rows(
        request_rows=[
            _request("api", "public_api_key_required", "data/rail/missing.csv"),
            _request("gtfs", "reviewed_static_gtfs_file_required", "data/rail/missing_gtfs.zip"),
            _request(
                "static_timetable",
                "reviewed_static_timetable_csv_required",
                "data/rail/missing_timetable_cache.csv",
            ),
            _request(
                "capacity",
                "operator_or_literature_or_sensitivity_decision",
                "data/parameters/rail_assumptions.csv",
            ),
        ],
        env={},
    )
    by_id = {row["request_id"]: row for row in rows}

    assert by_id["api"]["readiness_status"] == "blocked_missing_data_go_kr_key"
    assert by_id["api"]["source_url_or_citation"] == "fixture citation for api"
    assert by_id["api"]["required_external_input"] == "fixture input for api"
    assert by_id["gtfs"]["readiness_status"] == "blocked_missing_reviewed_gtfs_file"
    assert by_id["static_timetable"]["readiness_status"] == (
        "blocked_missing_reviewed_static_timetable_csv"
    )
    assert by_id["capacity"]["readiness_status"] == (
        "needs_human_review_capacity_treatment"
    )
    assert {row["claim_boundary"] for row in rows} == {RAIL_FETCH_READINESS_SCOPE}
    assert all(row["can_support_rail_evidence_gate"] == "false" for row in rows)

    print("PASS: rail fetch-readiness rows classify blockers")


def test_rail_fetch_readiness_rows_notice_api_key() -> None:
    """API rows should move to reviewed-fetch readiness when a key is supplied."""

    rows = build_rail_fetch_readiness_rows(
        request_rows=[
            _request("api", "public_api_key_required", "data/rail/missing.csv"),
        ],
        env={"DATA_GO_KR_KEY": "fixture-key"},
    )

    assert rows[0]["readiness_status"] == "ready_for_reviewed_live_api_fetch"
    assert rows[0]["data_go_kr_key_present"] == "true"

    print("PASS: rail fetch-readiness rows notice API key")


def test_write_rail_fetch_readiness_packet_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_rail_fetch_readiness_rows(
        request_rows=[
            _request("api", "public_api_key_required", "data/rail/missing.csv"),
            _request(
                "availability",
                "scenario_or_public_disruption_source_required",
                "data/scenarios/disruption_scenarios.csv",
            ),
        ],
        env={},
    )

    with TemporaryDirectory() as directory:
        output = Path(directory) / "rail_fetch_readiness.csv"
        manifest = Path(directory) / "rail_fetch_readiness_manifest.json"
        doc = Path(directory) / "rail_fetch_readiness.md"
        value = write_rail_fetch_readiness_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == RAIL_FETCH_READINESS_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert value["region_ids"] == ["songpa_public_demo"]
        assert value["source_url_or_citation_present_count"] == len(rows)
        assert value["required_external_input_specified_count"] == len(rows)
        assert value["required_external_input_text_present_count"] == len(rows)
        assert value["required_external_input_present_count"] == 1
        assert written_manifest["rail_evidence_gate_closure_candidate_count"] == 0
        assert "Rail Fetch Review Packet" in text
        assert "fixture citation for api" in text
        assert "fixture input for api" in text

    print("PASS: rail fetch-readiness writer emits artifacts")


def test_shipped_rail_fetch_readiness_packet_matches_current_requests() -> None:
    """Current shipped readiness packet should stay non-accepting."""

    rows = build_rail_fetch_readiness_rows()

    assert DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH.exists()
    assert DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH.exists()
    with DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["request_id"] for row in written_rows] == [
        row["request_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["region_ids"] == ["songpa_public_demo"]
    assert manifest["result_scope"] == RAIL_FETCH_READINESS_SCOPE
    assert manifest["rail_evidence_gate_closure_candidate_count"] == 0
    assert manifest["source_url_or_citation_present_count"] == len(rows)
    assert manifest["required_external_input_specified_count"] == len(rows)
    assert manifest["required_external_input_text_present_count"] == len(rows)
    assert manifest["required_external_input_present_count"] == 3
    by_id = {row["request_id"]: row for row in written_rows}
    gtfs = by_id["rail_static_gtfs_timing_request"]
    assert gtfs["source_name"] == KTDB_GTFS_SOURCE_NAME
    assert gtfs["source_url_or_citation"] == KTDB_GTFS_SOURCE_CITATION
    assert "reviewed KTDB" in gtfs["required_external_input"]
    assert "GTFS Validator report" in gtfs["required_external_input"]
    assert "pilot_gtfs_validator_report.json" in gtfs["source_cache_path"]
    assert gtfs["raw_payload_path"] == KTDB_GTFS_SOURCE_METADATA_PATHS
    assert gtfs["raw_payload_present"] == "true"
    assert gtfs["readiness_status"] == "blocked_missing_reviewed_gtfs_file"
    assert "GTFS Validator report" in gtfs["blocking_reason"]
    static_csv = by_id["rail_static_timetable_csv_headway_request"]
    assert static_csv["source_type"] == "reviewed_static_timetable_csv_required"
    assert static_csv["source_name"] == STATIC_TIMETABLE_SOURCE_NAME
    assert static_csv["source_url_or_citation"] == STATIC_TIMETABLE_SOURCE_CITATION
    assert "explicit source-column mappings" in static_csv["required_external_input"]
    assert "normalize_rail_timetable_cache.py" in static_csv["fetch_command"]
    assert "pilot_rail_timetable_static_source.csv" in static_csv["raw_payload_path"]
    assert static_csv["source_cache_present"] == "true"
    assert static_csv["raw_payload_present"] == "true"
    assert static_csv["readiness_status"] == (
        "ready_reviewed_static_timetable_cache_for_derivation_review"
    )
    capacity = by_id["rail_capacity_treatment_request"]
    assert capacity["readiness_status"] == "needs_human_review_capacity_treatment"
    assert capacity["source_url_or_citation"] == METRO9_CAPACITY_SOURCE_CITATION
    assert capacity["source_cache_path"] == RAIL_CAPACITY_REVIEW_INPUT_PATHS
    assert capacity["source_cache_present"] == "true"
    assert capacity["raw_payload_path"] == METRO9_CAPACITY_RAW_PATH
    assert capacity["raw_payload_present"] == "true"
    assert capacity["can_support_rail_evidence_gate"] == "false"

    print("PASS: shipped rail fetch-readiness packet matches current requests")


def _request(request_id: str, source_type: str, cache_path: str) -> dict[str, str]:
    return {
        "request_id": request_id,
        "region_id": "songpa_public_demo",
        "evidence_fields": "headway",
        "source_type": source_type,
        "source_name": request_id,
        "source_url_or_citation": f"fixture citation for {request_id}",
        "required_external_input": f"fixture input for {request_id}",
        "source_cache_path": cache_path,
        "raw_payload_path": "data/rail/missing_raw.json",
        "fetch_command": "fixture fetch",
        "derive_command": "fixture derive",
        "notes": "fixture",
    }


if __name__ == "__main__":
    test_rail_fetch_readiness_rows_classify_blockers()
    test_rail_fetch_readiness_rows_notice_api_key()
    test_write_rail_fetch_readiness_packet_outputs_artifacts()
    test_shipped_rail_fetch_readiness_packet_matches_current_requests()
    print("\n=== REALWORLD RAIL FETCH READINESS PACKET TESTS PASSED ===")
