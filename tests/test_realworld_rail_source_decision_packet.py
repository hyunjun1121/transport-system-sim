"""Tests for rail source-decision packet."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_source_decision_packet import (  # noqa: E402
    DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    RAIL_SOURCE_DECISION_ACTION_COLUMNS,
    RAIL_SOURCE_DECISION_COLUMNS,
    RAIL_SOURCE_DECISION_SCOPE,
    apply_rail_source_decision_action_ledger,
    build_rail_source_decision_manifest,
    build_rail_source_decision_rows,
    write_rail_source_decision_packet,
)
from src.realworld.rail_timing_request_packet import (  # noqa: E402
    KTDB_GTFS_SOURCE_METADATA_PATHS,
    METRO9_CAPACITY_RAW_PATH,
    METRO9_CAPACITY_SOURCE_CITATION,
    RAIL_CAPACITY_REVIEW_INPUT_PATHS,
)
from scripts.write_rail_source_decision_packet import (  # noqa: E402
    main as write_rail_source_decision_main,
)


def test_rail_source_decision_rows_classify_current_requests() -> None:
    """Current rail fetch-readiness rows should become pending decisions."""

    rows = build_rail_source_decision_rows()
    by_id = {row["request_id"]: row for row in rows}

    assert len(rows) == 6
    assert set(by_id) == {
        "rail_availability_scenario_request",
        "rail_capacity_treatment_request",
        "rail_shortest_path_travel_time_request",
        "rail_static_timetable_csv_headway_request",
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
    assert by_id["rail_static_timetable_csv_headway_request"]["decision_status"] == (
        "needs_human_review_ready_rail_source_decision"
    )
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
    assert {row["decision_scope"] for row in rows} == {"non_formal_source_review"}
    assert {row["decision_choice"] for row in rows} == {"pending_reviewer_decision"}
    assert all(row["minimum_evidence_to_acquire"] for row in rows)
    assert all(row["allowed_bounded_fallback"] for row in rows)
    assert all(row["decision_completion_output"] for row in rows)
    assert all("not operational" in row["not_operational_claim_boundary"] for row in rows)
    assert "provide_reviewed_static_gtfs_feed" in by_id[
        "rail_static_gtfs_timing_request"
    ]["candidate_decision_options"]
    assert "provide_reviewed_static_timetable_csv_and_mapping" in by_id[
        "rail_static_timetable_csv_headway_request"
    ]["candidate_decision_options"]
    static_csv = by_id["rail_static_timetable_csv_headway_request"]
    assert static_csv["current_artifact_status"] == (
        "normalized_static_timetable_cache_present_pending_review"
    )
    assert static_csv["source_cache_present"] == "true"
    assert static_csv["raw_payload_present"] == "true"
    assert "normalize_rail_timetable_cache.py" in static_csv["followup_artifacts"]
    assert static_csv["can_support_timing_fields_after_review"] == "true"
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
            "rail_static_timetable_csv_headway_request",
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
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_publication_gate"] is False
    assert manifest["can_support_final_study_gate"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["accepted_source_backed_rail_service_evidence"] is False
    assert manifest["completed_action_ledger_is_acceptance"] is False
    assert manifest["action_ledger_completion_scope"] == (
        "non_formal_source_review_only"
    )
    assert written_manifest["row_count"] == 6
    assert written_manifest["blocking_decision_count"] == 3
    assert written_manifest["human_review_decision_count"] == 3
    assert written_manifest["timing_source_decision_count"] == 4
    assert written_manifest["action_decision_status_counts"] == {
        "pending_action_decision": 6
    }
    assert written_manifest["completed_source_decision_count"] == 0
    assert written_manifest["invalid_action_decision_count"] == 0
    assert written_manifest["missing_evidence_for_non_pending_actions_count"] == 0
    assert written_manifest["missing_decision_evidence_count"] == 0
    assert "rail_service_evidence_artifact_present" in written_manifest
    assert any(
        "source decisions are pending" in blocker
        for blocker in written_manifest["remaining_blockers"]
    )
    assert "Rail Source Decision Packet" in doc_text
    assert "not publication gate evidence" in doc_text
    assert "not study-closeout evidence" in doc_text
    assert "not a formal decision record" in doc_text
    assert "Proxy/scaffold rail-service artifact present for inspection" in doc_text
    assert "Source-backed rail-service evidence approved: `false`" in doc_text
    assert "Artifact presence is not rail evidence acceptance" in doc_text
    assert "metro9_capacity_source_extract.csv" in doc_text
    assert "metro9_capacity_source_raw.html" in doc_text

    print("PASS: rail source-decision writer emits artifacts")


def test_rail_source_decision_manifest_classifies_non_formal_action_ledger() -> None:
    """Reviewed action choices should be counted without creating acceptance."""

    base_rows = {row["request_id"]: row for row in build_rail_source_decision_rows()}
    acquired = _reviewed_row(
        base_rows["rail_static_gtfs_timing_request"],
        decision_choice="provide_reviewed_static_gtfs_feed",
        artifact_sha256s="pilot_gtfs.zip=abc123; pilot_gtfs_validator_report.json=def456",
    )
    excluded = _reviewed_row(
        base_rows["rail_timetable_headway_request"],
        decision_choice="exclude_timing_dependent_release_scope_claims",
        excluded_or_retained_claim_scope=(
            "exclude headway-dependent release-scope claims"
        ),
        bounded_treatment_or_exclusion_rationale="no reviewed timetable cache is available",
    )
    invalid = _reviewed_row(
        base_rows["rail_capacity_treatment_request"],
        decision_choice="unsupported_choice",
    )
    incomplete = _reviewed_row(
        base_rows["rail_shortest_path_travel_time_request"],
        decision_choice="provide_reviewed_cached_api_payload",
        artifact_sha256s="",
    )

    manifest = build_rail_source_decision_manifest(
        rows=[acquired, excluded, invalid, incomplete],
    )

    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_publication_gate"] is False
    assert manifest["can_support_final_study_gate"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["completed_action_ledger_is_acceptance"] is False
    assert manifest["acceptance_gate_closure_candidate_count"] == 0
    assert manifest["rail_service_evidence_gate_closure_candidate_count"] == 0
    assert manifest["completed_source_decision_count"] == 1
    assert manifest["acquisition_decision_count"] == 2
    assert manifest["exclusion_decision_count"] == 1
    assert manifest["invalid_action_decision_count"] == 1
    assert manifest["missing_evidence_for_non_pending_actions_count"] == 3
    assert manifest["missing_decision_evidence_count"] == 3
    assert manifest["action_decision_status_counts"][
        "completed_non_formal_source_review_decision"
    ] == 1
    assert manifest["action_decision_status_counts"][
        "invalid_action_decision_choice"
    ] == 1
    assert manifest["action_decision_status_counts"][
        "incomplete_source_backed_acquisition_decision"
    ] == 2

    print("PASS: rail source-decision manifest classifies non-formal action ledger")


def test_acquisition_decision_requires_existing_artifact_hashes() -> None:
    """Source-backed choices require existing local files and matching SHA256s."""

    base_rows = {row["request_id"]: row for row in build_rail_source_decision_rows()}
    capacity = base_rows["rail_capacity_treatment_request"]
    good = _reviewed_row(
        capacity,
        decision_choice="replace_with_operator_or_literature_capacity_source",
        artifact_sha256s=_artifact_sha256s_for_row(capacity),
    )
    bad_hash = _reviewed_row(
        capacity,
        decision_choice="replace_with_operator_or_literature_capacity_source",
        artifact_sha256s="data/rail/metro9_capacity_source_extract.csv="
        + ("0" * 64),
    )
    missing_gtfs = _reviewed_row(
        base_rows["rail_static_gtfs_timing_request"],
        decision_choice="provide_reviewed_static_gtfs_feed",
        artifact_sha256s="data/rail/pilot_gtfs.zip=" + ("1" * 64),
    )

    good_manifest = build_rail_source_decision_manifest(rows=[good])
    bad_manifest = build_rail_source_decision_manifest(rows=[bad_hash, missing_gtfs])

    assert good_manifest["completed_source_decision_count"] == 1
    assert good_manifest["missing_evidence_for_non_pending_actions_count"] == 0
    assert good_manifest["missing_decision_evidence_count"] == 0
    assert good_manifest["action_decision_status_counts"] == {
        "completed_non_formal_source_review_decision": 1
    }
    assert bad_manifest["completed_source_decision_count"] == 0
    assert bad_manifest["missing_evidence_for_non_pending_actions_count"] == 2
    assert bad_manifest["missing_decision_evidence_count"] == 2
    assert bad_manifest["action_decision_status_counts"] == {
        "incomplete_source_backed_acquisition_decision": 2
    }

    print("PASS: acquisition decisions require existing artifact SHA256 evidence")


def test_rail_source_decision_manifest_records_complete_non_formal_ledger() -> None:
    """Complete non-formal decisions should be recorded without closing gates."""

    base_rows = {row["request_id"]: row for row in build_rail_source_decision_rows()}
    rows = [
        _reviewed_row(
            base_rows["rail_shortest_path_travel_time_request"],
            decision_choice="exclude_timing_dependent_release_scope_claims",
            excluded_or_retained_claim_scope="exclude shortest-path timing claims",
            bounded_treatment_or_exclusion_rationale=(
                "no reviewed shortest-path cache is available"
            ),
        ),
        _reviewed_row(
            base_rows["rail_static_gtfs_timing_request"],
            decision_choice="retain_current_timing_assumption_as_sensitivity_only",
            excluded_or_retained_claim_scope=(
                "retain GTFS timing as sensitivity-only proxy"
            ),
            bounded_treatment_or_exclusion_rationale=(
                "reviewed GTFS feed and validator report are absent"
            ),
        ),
        _reviewed_row(
            base_rows["rail_timetable_headway_request"],
            decision_choice="exclude_timing_dependent_release_scope_claims",
            excluded_or_retained_claim_scope=(
                "exclude headway-dependent release-scope claims"
            ),
            bounded_treatment_or_exclusion_rationale=(
                "no reviewed timetable cache is available"
            ),
        ),
        _reviewed_row(
            base_rows["rail_static_timetable_csv_headway_request"],
            decision_choice="exclude_timing_dependent_release_scope_claims",
            excluded_or_retained_claim_scope=(
                "exclude static timetable CSV headway-dependent release-scope claims"
            ),
            bounded_treatment_or_exclusion_rationale=(
                "no reviewed static timetable CSV and normalization manifest are available"
            ),
        ),
        _reviewed_row(
            base_rows["rail_availability_scenario_request"],
            decision_choice="record_scenario_only_availability_scope",
            excluded_or_retained_claim_scope=(
                "retain availability stress as scenario-only treatment"
            ),
            bounded_treatment_or_exclusion_rationale=(
                "no source-backed rail availability evidence is available"
            ),
        ),
        _reviewed_row(
            base_rows["rail_capacity_treatment_request"],
            decision_choice="retain_capacity_as_sensitivity_only_with_bounds",
            excluded_or_retained_claim_scope=(
                "retain rail capacity as sensitivity-only bounds"
            ),
            bounded_treatment_or_exclusion_rationale=(
                "operator or literature capacity source has not been reviewed"
            ),
        ),
    ]

    manifest = build_rail_source_decision_manifest(rows=rows)

    assert manifest["row_count"] == 6
    assert manifest["completed_source_decision_count"] == 6
    assert manifest["rail_source_decision_recorded"] is True
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_publication_gate"] is False
    assert manifest["can_support_final_study_gate"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["completed_action_ledger_is_acceptance"] is False
    assert manifest["action_ledger_completion_scope"] == (
        "non_formal_source_review_only"
    )
    assert manifest["rail_service_evidence_gate_closure_candidate_count"] == 0
    assert manifest["acceptance_gate_closure_candidate_count"] == 0
    assert not any(
        "source decisions are pending" in blocker
        for blocker in manifest["remaining_blockers"]
    )
    assert any(
        "do not close rail evidence" in blocker
        for blocker in manifest["remaining_blockers"]
    )

    print(
        "PASS: complete rail source-decision ledger records non-formal aggregate"
    )


def test_rail_source_decision_action_ledger_merges_review_fields_only() -> None:
    """Action ledger should merge reviewer fields without changing protected fields."""

    rows = build_rail_source_decision_rows()
    merged = apply_rail_source_decision_action_ledger(
        rows,
        action_rows=[
            _ledger_row(
                "rail_capacity_treatment_request",
                decision_choice="retain_capacity_as_sensitivity_only_with_bounds",
                excluded_or_retained_claim_scope=(
                    "retain rail capacity as sensitivity-only bounds"
                ),
                bounded_treatment_or_exclusion_rationale=(
                    "operator or literature capacity source has not been reviewed"
                ),
            )
        ],
    )
    capacity = {
        row["request_id"]: row for row in merged
    }["rail_capacity_treatment_request"]
    manifest = build_rail_source_decision_manifest(rows=merged)

    assert capacity["decision_choice"] == "retain_capacity_as_sensitivity_only_with_bounds"
    assert capacity["reviewer"] == "reviewer fixture"
    assert capacity["source_type"] == "operator_or_literature_or_sensitivity_decision"
    assert capacity["can_support_rail_evidence_gate"] == "false"
    assert capacity["can_support_acceptance_gate"] == "false"
    assert capacity["decision_status"] == "completed_non_formal_source_review_decision"
    assert manifest["completed_source_decision_count"] == 1
    assert manifest["rail_source_decision_recorded"] is False
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_support_publication_gate"] is False
    assert manifest["can_support_final_study_gate"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["formal_acceptance_evidence"] is False

    print("PASS: rail source-decision action ledger merges only reviewer fields")


def test_rail_source_decision_action_ledger_rejects_bad_rows() -> None:
    """Ledger merge should fail loudly for unknown, duplicate, or protected rows."""

    rows = build_rail_source_decision_rows()

    _assert_raises(
        ValueError,
        lambda: apply_rail_source_decision_action_ledger(
            rows,
            action_rows=[
                _ledger_row(
                    "unknown_request",
                    decision_choice="exclude_timing_dependent_release_scope_claims",
                )
            ],
        ),
    )
    _assert_raises(
        ValueError,
        lambda: apply_rail_source_decision_action_ledger(
            rows,
            action_rows=[
                _ledger_row(
                    "rail_timetable_headway_request",
                    decision_choice="exclude_timing_dependent_release_scope_claims",
                ),
                _ledger_row(
                    "rail_timetable_headway_request",
                    decision_choice="exclude_timing_dependent_release_scope_claims",
                ),
            ],
        ),
    )
    protected = _ledger_row(
        "rail_timetable_headway_request",
        decision_choice="exclude_timing_dependent_release_scope_claims",
    )
    protected["can_support_rail_evidence_gate"] = "true"
    _assert_raises(
        ValueError,
        lambda: apply_rail_source_decision_action_ledger(
            rows,
            action_rows=[protected],
        ),
    )

    print("PASS: rail source-decision action ledger rejects bad rows")


def test_action_ledger_requires_iso_decision_date() -> None:
    """Non-pending action decisions should require an ISO decision date."""

    rows = build_rail_source_decision_rows()
    merged = apply_rail_source_decision_action_ledger(
        rows,
        action_rows=[
            _ledger_row(
                "rail_capacity_treatment_request",
                decision_choice="retain_capacity_as_sensitivity_only_with_bounds",
                decision_date="June 3 2026",
                excluded_or_retained_claim_scope=(
                    "retain rail capacity as sensitivity-only bounds"
                ),
                bounded_treatment_or_exclusion_rationale=(
                    "operator or literature capacity source has not been reviewed"
                ),
            )
        ],
    )
    capacity = {
        row["request_id"]: row for row in merged
    }["rail_capacity_treatment_request"]
    manifest = build_rail_source_decision_manifest(rows=merged)

    assert capacity["decision_status"] == "invalid_action_decision_date"
    assert manifest["completed_source_decision_count"] == 0
    assert manifest["invalid_action_decision_count"] == 1
    assert manifest["missing_evidence_for_non_pending_actions_count"] == 1
    assert manifest["missing_decision_evidence_count"] == 1
    assert manifest["action_decision_status_counts"] == {
        "invalid_action_decision_date": 1,
        "pending_action_decision": 5,
    }

    print("PASS: action ledger requires ISO decision date")


def test_rail_source_decision_cli_accepts_action_ledger() -> None:
    """CLI should merge an optional action ledger into temp artifacts."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        action_ledger = root / "action_ledger.csv"
        output = root / "rail_source_decision.csv"
        manifest_path = root / "rail_source_decision_manifest.json"
        doc_path = root / "rail_source_decision.md"
        _write_action_ledger(action_ledger, _complete_action_ledger_rows())

        exit_code = write_rail_source_decision_main(
            [
                "--action-ledger",
                str(action_ledger),
                "--output",
                str(output),
                "--manifest",
                str(manifest_path),
                "--doc",
                str(doc_path),
            ]
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        with output.open("r", encoding="utf-8", newline="") as handle:
            written_rows = list(csv.DictReader(handle))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert manifest["completed_source_decision_count"] == 6
    assert manifest["rail_source_decision_recorded"] is True
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_publication_gate"] is False
    assert manifest["can_support_final_study_gate"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["completed_action_ledger_is_acceptance"] is False
    assert manifest["acceptance_gate_closure_candidate_count"] == 0
    assert not any(
        "source decisions are pending" in blocker
        for blocker in manifest["remaining_blockers"]
    )
    assert {row["decision_status"] for row in written_rows} == {
        "completed_non_formal_source_review_decision"
    }
    assert "not a formal decision record" in doc_text

    print("PASS: rail source-decision CLI accepts action ledger")


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

    assert len(written_rows) == len(rows)
    for shipped_row in written_rows:
        assert shipped_row["request_id"] in {r["request_id"] for r in rows}
    assert manifest["row_count"] == len(written_rows)
    # Rail is reframed as a wartime_charter_assumption proxy; the source-decision
    # ledger ships in the honest non-accepting state (rail gates blocked under
    # charter, final_study_ready=False project invariant). Asserting False here.
    assert manifest["blocking_decision_count"] == 3
    assert manifest["human_review_decision_count"] == 3
    assert manifest["rail_source_decision_recorded"] is False
    assert manifest["completed_source_decision_count"] == 0
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_publication_gate"] is False
    assert manifest["can_support_final_study_gate"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["completed_action_ledger_is_acceptance"] is False

    print("PASS: shipped rail source-decision packet matches outputs")


def _reviewed_row(
    row: dict[str, str],
    *,
    decision_choice: str,
    artifact_sha256s: str = "artifact=abc123",
    excluded_or_retained_claim_scope: str = "bounded review scope",
    bounded_treatment_or_exclusion_rationale: str = "reviewed non-formal decision fixture",
) -> dict[str, str]:
    value = dict(row)
    value.update(
        {
            "decision_choice": decision_choice,
            "reviewer": "reviewer fixture",
            "decision_date": "2026-06-03",
            "decision_basis": "test fixture evidence review",
            "artifact_sha256s": artifact_sha256s,
            "excluded_or_retained_claim_scope": excluded_or_retained_claim_scope,
            "not_operational_claim_boundary": (
                "not operational routing, not rail-service calibration, not a formal decision record"
            ),
            "bounded_treatment_or_exclusion_rationale": bounded_treatment_or_exclusion_rationale,
        }
    )
    return value


def _ledger_row(
    request_id: str,
    *,
    decision_choice: str,
    decision_date: str = "2026-06-03",
    artifact_sha256s: str = "artifact=abc123",
    excluded_or_retained_claim_scope: str = "bounded review scope",
    bounded_treatment_or_exclusion_rationale: str = "reviewed non-formal decision fixture",
) -> dict[str, str]:
    return {
        "request_id": request_id,
        "decision_choice": decision_choice,
        "reviewer": "reviewer fixture",
        "decision_date": decision_date,
        "decision_basis": "test fixture evidence review",
        "artifact_sha256s": artifact_sha256s,
        "excluded_or_retained_claim_scope": excluded_or_retained_claim_scope,
        "not_operational_claim_boundary": (
            "not operational routing, not rail-service calibration, not a formal decision record"
        ),
        "bounded_treatment_or_exclusion_rationale": bounded_treatment_or_exclusion_rationale,
    }


def _complete_action_ledger_rows() -> list[dict[str, str]]:
    return [
        _ledger_row(
            "rail_shortest_path_travel_time_request",
            decision_choice="exclude_timing_dependent_release_scope_claims",
            excluded_or_retained_claim_scope="exclude shortest-path timing claims",
            bounded_treatment_or_exclusion_rationale=(
                "no reviewed shortest-path cache is available"
            ),
        ),
        _ledger_row(
            "rail_static_gtfs_timing_request",
            decision_choice="retain_current_timing_assumption_as_sensitivity_only",
            excluded_or_retained_claim_scope=(
                "retain GTFS timing as sensitivity-only proxy"
            ),
            bounded_treatment_or_exclusion_rationale=(
                "reviewed GTFS feed and validator report are absent"
            ),
        ),
        _ledger_row(
            "rail_timetable_headway_request",
            decision_choice="exclude_timing_dependent_release_scope_claims",
            excluded_or_retained_claim_scope=(
                "exclude headway-dependent release-scope claims"
            ),
            bounded_treatment_or_exclusion_rationale=(
                "no reviewed timetable cache is available"
            ),
        ),
        _ledger_row(
            "rail_static_timetable_csv_headway_request",
            decision_choice="exclude_timing_dependent_release_scope_claims",
            excluded_or_retained_claim_scope=(
                "exclude static timetable CSV headway-dependent release-scope claims"
            ),
            bounded_treatment_or_exclusion_rationale=(
                "no reviewed static timetable CSV and normalization manifest are available"
            ),
        ),
        _ledger_row(
            "rail_availability_scenario_request",
            decision_choice="record_scenario_only_availability_scope",
            excluded_or_retained_claim_scope=(
                "retain availability stress as scenario-only treatment"
            ),
            bounded_treatment_or_exclusion_rationale=(
                "no source-backed rail availability evidence is available"
            ),
        ),
        _ledger_row(
            "rail_capacity_treatment_request",
            decision_choice="retain_capacity_as_sensitivity_only_with_bounds",
            excluded_or_retained_claim_scope=(
                "retain rail capacity as sensitivity-only bounds"
            ),
            bounded_treatment_or_exclusion_rationale=(
                "operator or literature capacity source has not been reviewed"
            ),
        ),
    ]


def _artifact_sha256s_for_row(row: dict[str, str]) -> str:
    entries: list[str] = []
    for field in ("source_cache_path", "raw_payload_path"):
        for value in row.get(field, "").split(";"):
            path_text = value.strip()
            if not path_text:
                continue
            path = Path(path_text)
            if not path.is_absolute():
                path = PROJECT_ROOT / path
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            entries.append(f"{path_text}={digest}")
    return "; ".join(entries)


def _write_action_ledger(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAIL_SOURCE_DECISION_ACTION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _assert_raises(exception_type: type[BaseException], func) -> None:
    try:
        func()
    except exception_type:
        return
    raise AssertionError(f"expected {exception_type.__name__}")


if __name__ == "__main__":
    test_rail_source_decision_rows_classify_current_requests()
    test_rail_source_decision_writer_outputs_artifacts()
    test_rail_source_decision_manifest_classifies_non_formal_action_ledger()
    test_acquisition_decision_requires_existing_artifact_hashes()
    test_rail_source_decision_manifest_records_complete_non_formal_ledger()
    test_rail_source_decision_action_ledger_merges_review_fields_only()
    test_rail_source_decision_action_ledger_rejects_bad_rows()
    test_action_ledger_requires_iso_decision_date()
    test_rail_source_decision_cli_accepts_action_ledger()
    test_shipped_rail_source_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD RAIL SOURCE DECISION TESTS PASSED ===")
