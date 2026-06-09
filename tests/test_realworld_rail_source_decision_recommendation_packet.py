"""Tests for rail source-decision recommendation packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.write_rail_source_decision_recommendation_packet import (  # noqa: E402
    main as write_recommendation_main,
)
from src.realworld.rail_source_decision_packet import (  # noqa: E402
    build_rail_source_decision_rows,
)
from src.realworld.rail_source_decision_recommendation_packet import (  # noqa: E402
    DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_MANIFEST_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_PACKET_PATH,
    RAIL_SOURCE_DECISION_RECOMMENDATION_COLUMNS,
    RAIL_SOURCE_DECISION_RECOMMENDATION_SCOPE,
    build_rail_source_decision_recommendation_rows,
    write_rail_source_decision_recommendation_packet,
)


def test_recommendation_rows_classify_current_rail_source_decisions() -> None:
    """Recommendation rows should classify each rail source-decision request."""

    rows = build_rail_source_decision_recommendation_rows(
        decision_rows=build_rail_source_decision_rows()
    )
    by_id = {row["request_id"]: row for row in rows}

    assert len(rows) == 6
    assert by_id["rail_static_gtfs_timing_request"]["recommended_treatment"] == (
        "source_backed_acquisition_candidate"
    )
    assert by_id["rail_static_gtfs_timing_request"][
        "recommended_reviewer_choice"
    ] == "provide_reviewed_static_gtfs_feed"
    assert "pilot_gtfs_validator_report.json" in by_id[
        "rail_static_gtfs_timing_request"
    ]["required_next_artifacts"]
    assert "same-feed Validator report" in by_id[
        "rail_static_gtfs_timing_request"
    ]["reviewer_action_prompt"]

    assert by_id["rail_timetable_headway_request"]["recommended_treatment"] == (
        "key_or_cache_gated_timing_acquisition"
    )
    assert by_id["rail_shortest_path_travel_time_request"][
        "recommended_reviewer_choice"
    ] == "provide_reviewed_cached_api_payload"
    assert by_id["rail_static_timetable_csv_headway_request"][
        "recommendation_status"
    ] == "review_ready_static_timetable_cache"
    assert by_id["rail_static_timetable_csv_headway_request"][
        "recommended_treatment"
    ] == "review_static_timetable_headway_cache"
    assert by_id["rail_static_timetable_csv_headway_request"][
        "recommended_reviewer_choice"
    ] == "provide_reviewed_static_timetable_csv_and_mapping"
    assert "normalization manifest" in by_id[
        "rail_static_timetable_csv_headway_request"
    ]["reviewer_action_prompt"]
    assert by_id["rail_capacity_treatment_request"]["recommended_treatment"] == (
        "sensitivity_only_now"
    )
    assert "sensitivity-only capacity bounds" in by_id[
        "rail_capacity_treatment_request"
    ]["reviewer_action_prompt"]
    assert by_id["rail_availability_scenario_request"]["recommended_treatment"] == (
        "scenario_only_now"
    )
    assert "scenario-only availability scope" in by_id[
        "rail_availability_scenario_request"
    ]["reviewer_action_prompt"]
    assert all(row["reviewer_action_prompt"] for row in rows)
    assert {row["must_remain_reviewer_owned"] for row in rows} == {"true"}
    assert {row["can_prepopulate_action_ledger"] for row in rows} == {"false"}
    assert {row["can_support_rail_evidence_gate"] for row in rows} == {"false"}
    assert {row["can_support_acceptance_gate"] for row in rows} == {"false"}
    assert {row["publication_ready"] for row in rows} == {"false"}
    assert {row["final_study_ready"] for row in rows} == {"false"}
    assert {row["formal_acceptance_evidence"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {
        RAIL_SOURCE_DECISION_RECOMMENDATION_SCOPE
    }

    print("PASS: rail source-decision recommendation rows classify requests")


def test_recommendation_writer_outputs_non_evidence_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown with hard guard flags."""

    rows = build_rail_source_decision_recommendation_rows(
        decision_rows=build_rail_source_decision_rows()
    )
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "rail_source_decision_recommendations.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "rail_source_decision_recommendations.md"
        manifest = write_rail_source_decision_recommendation_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )
        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                RAIL_SOURCE_DECISION_RECOMMENDATION_COLUMNS
            )
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert written_rows == rows
    assert manifest["row_count"] == 6
    assert manifest["blocked_artifact_count"] == 3
    assert manifest["reviewer_owned_count"] == 6
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["action_ledger_created"] is False
    assert manifest["rail_source_decision_recorded"] is False
    assert manifest["can_prepopulate_action_ledger_count"] == 0
    assert manifest["unsafe_evidence_or_readiness_flag_count"] == 0
    assert written_manifest["recommended_treatment_counts"][
        "key_or_cache_gated_timing_acquisition"
    ] == 2
    assert "not an action ledger" in doc_text
    assert "not rail timing evidence" in doc_text
    assert "not publication readiness" in doc_text
    assert "not final-study readiness" in doc_text
    assert "not formal acceptance" in doc_text
    assert "reviewer_action_prompt" in doc_text

    print("PASS: recommendation writer emits non-evidence artifacts")


def test_recommendation_cli_writes_temp_outputs() -> None:
    """CLI should write recommendation artifacts from the current decision packet."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "recommendations.csv"
        manifest_path = root / "recommendations_manifest.json"
        doc_path = root / "recommendations.md"
        exit_code = write_recommendation_main(
            [
                "--output",
                str(output),
                "--manifest",
                str(manifest_path),
                "--doc",
                str(doc_path),
            ]
        )
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert exit_code == 0
        assert output.exists()
        assert doc_path.exists()
        assert written_manifest["row_count"] == 6
        assert written_manifest["action_ledger_created"] is False
        assert written_manifest["can_support_rail_evidence_gate"] is False

    print("PASS: recommendation CLI writes temp outputs")


def test_shipped_recommendation_packet_matches_current_outputs() -> None:
    """Shipped recommendation packet should match current decision rows."""

    rows = build_rail_source_decision_recommendation_rows()

    assert DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_PACKET_PATH.exists()
    assert DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_MANIFEST_PATH.exists()
    with DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["reviewer_owned_count"] == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False

    print("PASS: shipped recommendation packet matches current outputs")


if __name__ == "__main__":
    test_recommendation_rows_classify_current_rail_source_decisions()
    test_recommendation_writer_outputs_non_evidence_artifacts()
    test_recommendation_cli_writes_temp_outputs()
    test_shipped_recommendation_packet_matches_current_outputs()
    print("\n=== REALWORLD RAIL SOURCE DECISION RECOMMENDATION TESTS PASSED ===")
