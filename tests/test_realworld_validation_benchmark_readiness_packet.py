"""Tests for validation benchmark readiness packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.validation_benchmark_readiness_packet import (  # noqa: E402
    DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH,
    VALIDATION_BENCHMARK_READINESS_COLUMNS,
    VALIDATION_BENCHMARK_READINESS_SCOPE,
    build_validation_benchmark_readiness_rows,
    write_validation_benchmark_readiness_packet,
)


def test_validation_benchmark_readiness_rows_classify_current_snapshot() -> None:
    """Current fallback and OSRM artifacts should become conservative rows."""

    rows = build_validation_benchmark_readiness_rows()
    by_id = {row["benchmark_option_id"]: row for row in rows}

    assert len(rows) == 4
    assert by_id["fallback_detour_speed_benchmark"]["readiness_status"] == (
        "needs_human_review_fallback_warn_rows"
    )
    assert by_id["cached_osrm_route_snapshot"]["readiness_status"] == (
        "needs_human_review_osrm_snap_distance"
    )
    assert by_id["cached_osrm_route_snapshot"]["raw_response_file_count"] == "3"
    assert by_id["cached_osrm_route_snapshot"][
        "raw_response_binding_mismatch_count"
    ] == "0"
    assert by_id["cached_osrm_route_snapshot"][
        "raw_response_missing_for_row_count"
    ] == "0"
    assert by_id["cached_osrm_route_snapshot"]["snap_status_counts"] == (
        "pass=1; warn=2"
    )
    assert by_id["cached_osrm_route_snapshot"][
        "max_waypoint_snap_distance_m"
    ] == "265.494619"
    assert by_id["cached_osrm_route_snapshot"]["source_pinning_status"] == (
        "pinned_cached_payloads"
    )
    assert by_id["cached_osrm_route_snapshot"]["unpinned_row_count"] == "0"
    assert by_id["alternative_route_engine_decision"]["readiness_status"] == (
        "needs_human_review_alternative_benchmark_decision"
    )
    assert by_id["validation_acceptance_record"]["readiness_status"] == (
        "blocked_missing_validation_acceptance_record"
    )
    assert {row["claim_boundary"] for row in rows} == {
        VALIDATION_BENCHMARK_READINESS_SCOPE
    }
    assert all(row["can_support_validation_gate"] == "false" for row in rows)

    print("PASS: validation benchmark readiness rows classify current snapshot")


def test_validation_benchmark_readiness_blocks_unpinned_osrm_rows() -> None:
    """Unpinned OSRM snapshot rows should become blockers."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        fallback = root / "fallback.csv"
        osrm = root / "osrm.csv"
        manifest = root / "osrm_manifest.json"
        acceptance = root / "validation_acceptance.json"
        _write_benchmark_csv(fallback, status="pass")
        _write_benchmark_csv(osrm, status="pass")
        manifest.write_text(
            json.dumps(
                {
                    "raw_response_file_count": 1,
                    "unpinned_row_count": 1,
                    "query_url_count": 1,
                }
            ),
            encoding="utf-8",
        )

        rows = build_validation_benchmark_readiness_rows(
            fallback_benchmark_path=fallback,
            osrm_benchmark_path=osrm,
            osrm_benchmark_manifest_path=manifest,
            validation_acceptance_path=acceptance,
        )

    osrm_row = next(
        row for row in rows if row["benchmark_option_id"] == "cached_osrm_route_snapshot"
    )
    assert osrm_row["readiness_status"] == "blocked_unpinned_osrm_snapshot_rows"
    assert "unpinned" in osrm_row["blocking_reason"]

    print("PASS: validation benchmark readiness blocks unpinned OSRM rows")


def test_write_validation_benchmark_readiness_packet_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown review artifacts."""

    rows = build_validation_benchmark_readiness_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "validation_benchmark_readiness.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "packet.md"
        manifest = write_validation_benchmark_readiness_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == VALIDATION_BENCHMARK_READINESS_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["benchmark_gate_closure_candidate_count"] == 0
    assert "Benchmark Strategy Review Packet" in text

    print("PASS: validation benchmark readiness writer emits artifacts")


def test_shipped_validation_benchmark_readiness_packet_matches_current_artifacts() -> None:
    """Committed benchmark readiness packet should match current artifacts."""

    rows = build_validation_benchmark_readiness_rows()

    assert DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH.exists()
    assert DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH.exists()
    with DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert len(written_rows) == len(rows)
    assert [row["benchmark_option_id"] for row in written_rows] == [
        row["benchmark_option_id"] for row in rows
    ]
    assert manifest["row_count"] == 4
    assert manifest["blocking_request_count"] == 1
    assert manifest["human_review_request_count"] == 3
    assert manifest["osrm_raw_response_file_count"] == 3
    assert manifest["osrm_raw_response_binding_mismatch_count"] == 0
    assert manifest["osrm_raw_response_missing_for_row_count"] == 0
    assert manifest["osrm_snap_status_counts"] == "pass=1; warn=2"
    assert manifest["osrm_unpinned_row_count"] == 0
    assert manifest["publication_ready"] is False

    print("PASS: shipped validation benchmark readiness packet matches current artifacts")


def _write_benchmark_csv(path: Path, *, status: str) -> None:
    row = {
        "benchmark_method": "fixture_method",
        "source_class": "fixture_source",
        "status": status,
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    test_validation_benchmark_readiness_rows_classify_current_snapshot()
    test_validation_benchmark_readiness_blocks_unpinned_osrm_rows()
    test_write_validation_benchmark_readiness_packet_outputs_artifacts()
    test_shipped_validation_benchmark_readiness_packet_matches_current_artifacts()
    print("\n=== REALWORLD VALIDATION BENCHMARK READINESS TESTS PASSED ===")
