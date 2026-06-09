"""Tests for validation-package review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.validation_review_packet import (  # noqa: E402
    DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH,
    DEFAULT_VALIDATION_REVIEW_PACKET_PATH,
    VALIDATION_REVIEW_COLUMNS,
    VALIDATION_REVIEW_PACKET_SCOPE,
    build_validation_review_rows,
    write_validation_review_packet,
)


def test_validation_review_rows_summarize_current_artifacts() -> None:
    """Current validation artifacts should become conservative review rows."""

    rows = build_validation_review_rows()
    by_category = {row["category_id"]: row for row in rows}

    assert len(rows) == 7
    assert set(by_category) == {
        "internal_route_plausibility",
        "fallback_route_benchmarks",
        "optional_osrm_route_benchmarks",
        "accessibility_loss_coverage",
        "route_road_evidence_exposure",
        "validation_summary_scope",
        "benchmark_strategy_decision_requirement",
    }
    assert by_category["internal_route_plausibility"]["row_count"] == "21"
    assert by_category["internal_route_plausibility"]["status_counts"] == (
        "fail=0; pass=19; warn=2"
    )
    assert by_category["fallback_route_benchmarks"]["status_counts"] == (
        "fail=1; pass=1; warn=1"
    )
    assert by_category["optional_osrm_route_benchmarks"]["status_counts"] == (
        "fail=0; pass=3; warn=0"
    )
    assert "snapshot_manifest_present=true" in by_category[
        "optional_osrm_route_benchmarks"
    ]["coverage_counts"]
    assert "snapshot_manifest_unpinned_rows=0" in by_category[
        "optional_osrm_route_benchmarks"
    ]["coverage_counts"]
    assert "snapshot_manifest_raw_response_files=3" in by_category[
        "optional_osrm_route_benchmarks"
    ]["coverage_counts"]
    assert "snapshot_manifest_raw_binding_mismatches=0" in by_category[
        "optional_osrm_route_benchmarks"
    ]["coverage_counts"]
    assert "snapshot_manifest_raw_missing_rows=0" in by_category[
        "optional_osrm_route_benchmarks"
    ]["coverage_counts"]
    assert "snapshot_snap_status_warn=2" in by_category[
        "optional_osrm_route_benchmarks"
    ]["coverage_counts"]
    assert by_category["optional_osrm_route_benchmarks"]["review_status"] == (
        "review_required_osrm_snap_distance_review"
    )
    assert by_category["accessibility_loss_coverage"]["row_count"] == "127"
    assert "disconnected=22" in by_category["accessibility_loss_coverage"][
        "status_counts"
    ]
    assert by_category["route_road_evidence_exposure"]["row_count"] == "76"
    assert by_category["route_road_evidence_exposure"]["status_counts"] == (
        "true=76"
    )
    assert by_category["validation_summary_scope"]["review_status"] == (
        "scope_boundary_present_review_required"
    )
    assert by_category["benchmark_strategy_decision_requirement"][
        "artifact_present"
    ] == "false"
    assert {row["acceptance_ready"] for row in rows} == {"false"}
    assert {row["publication_ready"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {
        VALIDATION_REVIEW_PACKET_SCOPE
    }

    print("PASS: validation review rows summarize current artifacts")


def test_write_validation_review_packet_outputs_csv_and_manifest() -> None:
    """Writer should emit stable CSV fields and a non-acceptance manifest."""

    rows = build_validation_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "validation_review.csv"
        manifest = Path(directory) / "validation_review_manifest.json"
        acceptance_path = Path(directory) / "validation_acceptance.json"
        value = write_validation_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            validation_acceptance_path=acceptance_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == VALIDATION_REVIEW_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 7
        assert value["publication_ready"] is False
        assert value["acceptance_ready"] is False
        assert value["review_required"] is True
        assert value["acceptance_gate_closure_candidate_count"] == 0
        assert value["internal_plausibility_status_counts"] == {
            "fail": 0,
            "pass": 19,
            "warn": 2,
        }
        assert written_manifest["row_count"] == 7
        assert written_manifest["route_road_evidence_exposure_row_count"] == 76
        assert written_manifest["optional_osrm_benchmark_present"] is True
        assert written_manifest["optional_osrm_benchmark_manifest_present"] is True
        assert written_manifest["optional_osrm_benchmark_unpinned_row_count"] == 0
        assert (
            written_manifest["optional_osrm_benchmark_raw_response_file_count"]
            == 3
        )
        assert (
            written_manifest[
                "optional_osrm_benchmark_raw_response_binding_mismatch_count"
            ]
            == 0
        )
        assert (
            written_manifest[
                "optional_osrm_benchmark_raw_response_missing_for_row_count"
            ]
            == 0
        )
        assert written_manifest["optional_osrm_benchmark_snap_status_counts"] == {
            "pass": 1,
            "warn": 2,
        }
        assert "does not close the validation gate" in written_manifest[
            "claim_boundary"
        ]
        assert not acceptance_path.exists()

    print("PASS: validation review packet writer emits CSV and manifest")


def test_validation_review_rows_handle_temp_fixtures() -> None:
    """Temp fixtures should surface missing OSRM and incomplete scope wording."""

    with TemporaryDirectory() as directory:
        paths = _write_validation_fixture(Path(directory), include_osrm=False)
        rows = build_validation_review_rows(**paths)
        by_category = {row["category_id"]: row for row in rows}

        assert len(rows) == 6
        assert "optional_osrm_route_benchmarks" not in by_category
        assert by_category["internal_route_plausibility"]["status_counts"] == (
            "fail=1; pass=1; warn=0"
        )
        assert by_category["internal_route_plausibility"]["review_status"] == (
            "review_required_fail_rows"
        )
        assert by_category["accessibility_loss_coverage"]["row_count"] == "3"
        assert "routes=2" in by_category["accessibility_loss_coverage"][
            "coverage_counts"
        ]
        assert "disconnected=1" in by_category["accessibility_loss_coverage"][
            "status_counts"
        ]
        assert by_category["route_road_evidence_exposure"]["row_count"] == "2"
        assert by_category["route_road_evidence_exposure"]["review_status"] == (
            "review_required_weak_route_road_evidence_exposure"
        )
        assert by_category["validation_summary_scope"]["review_status"] == (
            "scope_boundary_incomplete_review_required"
        )
        assert "osrm_benchmark_present=false" in by_category[
            "benchmark_strategy_decision_requirement"
        ]["coverage_counts"]

        output = Path(directory) / "validation_review_packet.csv"
        manifest = Path(directory) / "validation_review_manifest.json"
        value = write_validation_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            **paths,
        )
        assert value["row_count"] == 6
        assert value["optional_osrm_benchmark_present"] is False
        assert value["internal_plausibility_status_counts"]["fail"] == 1
        assert value["accessibility_criticality_counts"]["disconnected"] == 1
        assert value["route_road_evidence_exposure_row_count"] == 2
        assert not Path(paths["validation_acceptance_path"]).exists()

    print("PASS: validation review rows handle temp fixtures")


def test_shipped_validation_review_packet_matches_current_artifacts() -> None:
    """Current shipped packet should match deterministic validation inputs."""

    expected_rows = build_validation_review_rows()

    assert DEFAULT_VALIDATION_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_VALIDATION_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        written_rows = list(reader)
        assert tuple(reader.fieldnames or ()) == VALIDATION_REVIEW_COLUMNS
    with DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert written_rows == expected_rows
    assert manifest["row_count"] == len(expected_rows)
    assert manifest["result_scope"] == VALIDATION_REVIEW_PACKET_SCOPE
    assert manifest["publication_ready"] is False
    assert manifest["acceptance_ready"] is False
    assert manifest["acceptance_gate_closure_candidate_count"] == 0
    assert manifest["review_required"] is True

    print("PASS: shipped validation review packet matches current artifacts")


def _write_validation_fixture(
    directory: Path,
    *,
    include_osrm: bool,
) -> dict[str, Path]:
    route_path = directory / "route_plausibility.csv"
    fallback_path = directory / "external_route_benchmarks.csv"
    osrm_path = directory / "external_route_benchmarks_osrm.csv"
    osrm_manifest_path = directory / "osrm_route_benchmark_manifest.json"
    accessibility_path = directory / "accessibility_loss.csv"
    route_exposure_path = directory / "canonical_route_road_evidence_exposure.csv"
    summary_path = directory / "validation_summary.md"
    acceptance_path = directory / "validation_acceptance.json"

    _write_csv(
        route_path,
        ["category", "subject", "metric", "status"],
        [
            {
                "category": "route",
                "subject": "A->D",
                "metric": "road_route_available",
                "status": "pass",
            },
            {
                "category": "connector",
                "subject": "A",
                "metric": "connector_distance_m",
                "status": "fail",
            },
        ],
    )
    benchmark_rows = [
        {
            "subject": "A->D",
            "benchmark_method": "fixture_fallback",
            "source_class": "documented_executable_fallback",
            "reference_version": "",
            "status": "pass",
        },
        {
            "subject": "R->D",
            "benchmark_method": "fixture_fallback",
            "source_class": "documented_executable_fallback",
            "reference_version": "",
            "status": "warn",
        },
    ]
    _write_csv(
        fallback_path,
        ["subject", "benchmark_method", "source_class", "reference_version", "status"],
        benchmark_rows,
    )
    if include_osrm:
        _write_csv(
            osrm_path,
            [
                "subject",
                "benchmark_method",
                "source_class",
                "reference_version",
                "status",
            ],
            [
                {
                    "subject": "A->D",
                    "benchmark_method": "osrm_route_v1_driving",
                    "source_class": "live_external_router_snapshot",
                    "reference_version": "live_snapshot_unpinned",
                    "status": "pass",
                }
            ],
        )
    _write_csv(
        accessibility_path,
        [
            "route_id",
            "baseline_available",
            "disrupted_available",
            "criticality_class",
        ],
        [
            {
                "route_id": "bus_direct",
                "baseline_available": "true",
                "disrupted_available": "false",
                "criticality_class": "disconnected",
            },
            {
                "route_id": "bus_direct",
                "baseline_available": "true",
                "disrupted_available": "true",
                "criticality_class": "high_time_loss",
            },
            {
                "route_id": "rail_access",
                "baseline_available": "true",
                "disrupted_available": "true",
                "criticality_class": "low_time_loss",
            },
        ],
    )
    _write_csv(
        route_exposure_path,
        [
            "graph_variant",
            "route_check_id",
            "route_rank",
            "weak_for_final_claim",
        ],
        [
            {
                "graph_variant": "fixture_variant",
                "route_check_id": "route_bus_direct",
                "route_rank": "1",
                "weak_for_final_claim": "true",
            },
            {
                "graph_variant": "fixture_variant",
                "route_check_id": "route_last_mile",
                "route_rank": "1",
                "weak_for_final_claim": "false",
            },
        ],
    )
    summary_path.write_text(
        "# Fixture Validation Summary\n\nThis fixture omits the required scope boundary.\n",
        encoding="utf-8",
    )
    return {
        "route_plausibility_path": route_path,
        "fallback_benchmark_path": fallback_path,
        "osrm_benchmark_path": osrm_path,
        "osrm_benchmark_manifest_path": osrm_manifest_path,
        "accessibility_loss_path": accessibility_path,
        "route_road_evidence_exposure_path": route_exposure_path,
        "validation_summary_path": summary_path,
        "validation_acceptance_path": acceptance_path,
    }


def _write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    test_validation_review_rows_summarize_current_artifacts()
    test_write_validation_review_packet_outputs_csv_and_manifest()
    test_validation_review_rows_handle_temp_fixtures()
    test_shipped_validation_review_packet_matches_current_artifacts()
    print("\n=== REALWORLD VALIDATION REVIEW PACKET TESTS PASSED ===")
