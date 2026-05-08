"""Tests for road source-decision packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_source_decision_packet import (  # noqa: E402
    DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_ROAD_SOURCE_DECISION_PACKET_PATH,
    ROAD_SOURCE_DECISION_COLUMNS,
    ROAD_SOURCE_DECISION_SCOPE,
    build_road_source_decision_rows,
    write_road_source_decision_packet,
)


def test_road_source_decision_rows_classify_current_requests() -> None:
    """Current road source-readiness rows should become decisions."""

    rows = build_road_source_decision_rows()
    by_id = {row["request_id"]: row for row in rows}

    assert len(rows) == 5
    assert set(by_id) == {
        "reviewed_road_class_override_application_request",
        "road_background_traffic_benchmark_request",
        "road_capacity_lane_count_source_request",
        "road_disruption_probability_source_request",
        "road_speed_limit_source_request",
    }
    assert by_id["road_capacity_lane_count_source_request"]["decision_status"] == (
        "blocked_missing_road_source_decision"
    )
    assert by_id["reviewed_road_class_override_application_request"][
        "decision_status"
    ] == "blocked_missing_road_source_decision"
    assert {
        row["decision_status"]
        for row in rows
        if row["request_id"]
        not in {
            "road_capacity_lane_count_source_request",
            "reviewed_road_class_override_application_request",
        }
    } == {"needs_human_review_road_source_decision"}
    assert {row["provisional_decision"] for row in rows} == {
        "pending_reviewer_decision"
    }
    assert "replace_with_traffic_count_or_capacity_reference" in by_id[
        "road_capacity_lane_count_source_request"
    ]["candidate_decision_options"]
    assert "create_reviewed_road_class_overrides" in by_id[
        "reviewed_road_class_override_application_request"
    ]["candidate_decision_options"]
    assert "not_operational_claim_boundary" in by_id[
        "road_background_traffic_benchmark_request"
    ]["required_evidence_fields"]
    assert {row["can_support_road_evidence_gate"] for row in rows} == {"false"}
    assert {row["can_support_road_application_gate"] for row in rows} == {"false"}
    assert {row["can_support_acceptance_gate"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {ROAD_SOURCE_DECISION_SCOPE}

    print("PASS: road source-decision rows classify current requests")


def test_road_source_decision_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_road_source_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "road_source_decision.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "road_source_decision.md"
        manifest = write_road_source_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == ROAD_SOURCE_DECISION_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 5
    assert written_manifest["blocking_decision_count"] == 2
    assert written_manifest["human_review_decision_count"] == 3
    assert written_manifest["road_class_overrides_present"] is False
    assert "Road Source Decision Packet" in doc_text

    print("PASS: road source-decision writer emits artifacts")


def test_shipped_road_source_decision_packet_matches_current_outputs() -> None:
    """Committed decision packet should match current readiness rows."""

    rows = build_road_source_decision_rows()

    assert DEFAULT_ROAD_SOURCE_DECISION_PACKET_PATH.exists()
    assert DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_ROAD_SOURCE_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_decision_count"] == 2
    assert manifest["human_review_decision_count"] == 3
    assert manifest["road_source_decision_recorded"] is False
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped road source-decision packet matches outputs")


if __name__ == "__main__":
    test_road_source_decision_rows_classify_current_requests()
    test_road_source_decision_writer_outputs_artifacts()
    test_shipped_road_source_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD ROAD SOURCE DECISION TESTS PASSED ===")
