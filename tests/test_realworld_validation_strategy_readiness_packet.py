"""Tests for validation strategy-readiness packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.validation_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH,
    VALIDATION_STRATEGY_READINESS_COLUMNS,
    VALIDATION_STRATEGY_READINESS_SCOPE,
    build_validation_strategy_readiness_rows,
    write_validation_strategy_readiness_packet,
)


def test_validation_strategy_readiness_rows_classify_blockers() -> None:
    """Validation review rows should become concrete preflight statuses."""

    rows = build_validation_strategy_readiness_rows(
        review_rows=[
            _row(
                "internal_route_plausibility",
                "true",
                "fail=0; pass=19; warn=2",
                "",
                "review_required_warn_rows",
            ),
            _row(
                "optional_osrm_route_benchmarks",
                "true",
                "fail=0; pass=3; warn=0",
                "snapshot_manifest_raw_response_files=0; snapshot_manifest_unpinned_rows=3",
                "review_required_unpinned_external_snapshot",
            ),
            _row(
                "benchmark_strategy_decision_requirement",
                "false",
                "",
                "",
                "review_required_no_validation_acceptance_record",
            ),
        ]
    )
    by_id = {row["category_id"]: row for row in rows}

    assert by_id["internal_route_plausibility"]["readiness_status"] == (
        "needs_human_review_internal_plausibility_warnings"
    )
    assert by_id["optional_osrm_route_benchmarks"]["readiness_status"] == (
        "blocked_unpinned_external_route_snapshot"
    )
    assert "snapshot_manifest_raw_response_files=0" in by_id[
        "optional_osrm_route_benchmarks"
    ]["coverage_counts"]
    assert by_id["benchmark_strategy_decision_requirement"]["readiness_status"] == (
        "blocked_missing_validation_acceptance_record"
    )
    assert {row["claim_boundary"] for row in rows} == {
        VALIDATION_STRATEGY_READINESS_SCOPE
    }
    assert all(row["can_support_validation_gate"] == "false" for row in rows)

    print("PASS: validation strategy-readiness rows classify blockers")


def test_validation_strategy_readiness_rows_block_missing_osrm_raw_payloads() -> None:
    """Cached external-route snapshots still need retained raw payloads."""

    rows = build_validation_strategy_readiness_rows(
        review_rows=[
            _row(
                "optional_osrm_route_benchmarks",
                "true",
                "fail=0; pass=3; warn=0",
                "snapshot_manifest_raw_response_files=0; snapshot_manifest_unpinned_rows=0",
                "ready_for_review_cached_external_snapshot",
            ),
        ]
    )

    assert rows[0]["readiness_status"] == (
        "blocked_missing_external_route_raw_payloads"
    )
    assert "raw response payloads" in rows[0]["blocking_reason"]
    assert "retain raw payloads" in rows[0]["required_reviewer_action"]

    print("PASS: validation strategy-readiness rows block missing OSRM raw payloads")


def test_validation_strategy_readiness_rows_flag_osrm_snap_distances() -> None:
    """Cached OSRM rows with waypoint snap warnings should require review."""

    rows = build_validation_strategy_readiness_rows(
        review_rows=[
            _row(
                "optional_osrm_route_benchmarks",
                "true",
                "fail=0; pass=3; warn=0",
                (
                    "snapshot_manifest_raw_response_files=3; "
                    "snapshot_manifest_raw_binding_mismatches=0; "
                    "snapshot_manifest_raw_missing_rows=0; "
                    "snapshot_manifest_unpinned_rows=0; "
                    "snapshot_snap_status_pass=1; snapshot_snap_status_warn=2"
                ),
                "review_required_osrm_snap_distance_review",
            ),
        ]
    )

    assert rows[0]["readiness_status"] == (
        "needs_human_review_external_route_snap_distances"
    )
    assert "snap distances" in rows[0]["required_reviewer_action"]

    print("PASS: validation strategy-readiness rows flag OSRM snap distances")


def test_validation_strategy_readiness_rows_classify_weak_route_exposure() -> None:
    """Weak route-road exposure should block stronger validation claims."""

    rows = build_validation_strategy_readiness_rows(
        review_rows=[
            _row(
                "route_road_evidence_exposure",
                "true",
                "true=76",
                "weak_for_final_claim_true=76",
                "review_required_weak_route_road_evidence_exposure",
            ),
        ]
    )

    assert rows[0]["readiness_status"] == "blocked_weak_route_road_evidence_exposure"
    assert rows[0]["blocking_reason"]

    print("PASS: validation strategy-readiness rows classify weak route exposure")


def test_write_validation_strategy_readiness_packet_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_validation_strategy_readiness_rows(
        review_rows=[
            _row(
                "fallback_route_benchmarks",
                "true",
                "fail=1; pass=1; warn=1",
                "",
                "review_required_fallback_warn_or_fail_rows",
            ),
            _row(
                "validation_summary_scope",
                "true",
                "",
                "scaffold_or_sanity_scope=true",
                "scope_boundary_present_review_required",
            ),
        ]
    )

    with TemporaryDirectory() as directory:
        output = Path(directory) / "validation_strategy_readiness.csv"
        manifest = Path(directory) / "validation_strategy_readiness_manifest.json"
        doc = Path(directory) / "validation_strategy_readiness.md"
        value = write_validation_strategy_readiness_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == VALIDATION_STRATEGY_READINESS_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert written_manifest["validation_gate_closure_candidate_count"] == 0
        assert "Benchmark Strategy Review Packet" in text

    print("PASS: validation strategy-readiness writer emits artifacts")


def test_shipped_validation_strategy_readiness_packet_matches_current_review() -> None:
    """Current shipped readiness packet should stay non-accepting."""

    rows = build_validation_strategy_readiness_rows()

    assert DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH.exists()
    assert DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH.exists()
    with DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["category_id"] for row in written_rows] == [
        row["category_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["result_scope"] == VALIDATION_STRATEGY_READINESS_SCOPE
    assert manifest["validation_gate_closure_candidate_count"] == 0

    print("PASS: shipped validation strategy-readiness packet matches current review")


def _row(
    category_id: str,
    artifact_present: str,
    status_counts: str,
    coverage_counts: str,
    review_status: str,
) -> dict[str, str]:
    return {
        "category_id": category_id,
        "evidence_category": category_id,
        "artifact_path": f"data/validation/{category_id}.csv",
        "artifact_present": artifact_present,
        "row_count": "1",
        "status_counts": status_counts,
        "coverage_counts": coverage_counts,
        "review_status": review_status,
        "publication_use_status": "fixture",
    }


if __name__ == "__main__":
    test_validation_strategy_readiness_rows_classify_blockers()
    test_validation_strategy_readiness_rows_block_missing_osrm_raw_payloads()
    test_validation_strategy_readiness_rows_flag_osrm_snap_distances()
    test_validation_strategy_readiness_rows_classify_weak_route_exposure()
    test_write_validation_strategy_readiness_packet_outputs_artifacts()
    test_shipped_validation_strategy_readiness_packet_matches_current_review()
    print("\n=== REALWORLD VALIDATION STRATEGY READINESS PACKET TESTS PASSED ===")
