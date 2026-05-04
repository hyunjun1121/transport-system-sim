"""Tests for optional OSRM snapshot manifest generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.osrm_snapshot_manifest import (  # noqa: E402
    DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    OSRM_SNAPSHOT_MANIFEST_SCOPE,
    build_osrm_snapshot_manifest,
    write_osrm_snapshot_manifest,
)


def test_current_osrm_snapshot_manifest_counts() -> None:
    """The shipped OSRM CSV should become a conservative manifest."""

    manifest = build_osrm_snapshot_manifest()

    assert manifest["result_scope"] == OSRM_SNAPSHOT_MANIFEST_SCOPE
    assert manifest["row_count"] == 3
    assert manifest["status_counts"] == {"pass": 3}
    assert manifest["source_class_counts"] == {"live_external_router_snapshot": 3}
    assert manifest["reference_version_counts"] == {"live_snapshot_unpinned": 3}
    assert manifest["query_url_count"] == 3
    assert manifest["unpinned_row_count"] == 3
    assert manifest["publication_ready"] is False
    assert manifest["acceptance_ready"] is False
    assert "not validation acceptance" in manifest["claim_boundary"]

    print("PASS: current OSRM snapshot manifest counts are conservative")


def test_osrm_snapshot_manifest_writer_emits_json() -> None:
    """Writer should emit a stable manifest for arbitrary OSRM-like rows."""

    with TemporaryDirectory() as directory:
        benchmark_path = Path(directory) / "external_route_benchmarks_osrm.csv"
        summary_path = Path(directory) / "osrm_route_benchmark_summary.md"
        manifest_path = Path(directory) / "osrm_route_benchmark_manifest.json"
        _write_csv(
            benchmark_path,
            [
                {
                    "route_check_id": "route_bus_direct",
                    "benchmark_method": "osrm_route_v1_driving",
                    "source_class": "cached_external_router_snapshot",
                    "reference_source": "https://router.project-osrm.org",
                    "reference_version": "cached_2026_05_04",
                    "distance_status": "pass",
                    "time_status": "pass",
                    "status": "pass",
                    "notes": "cached OSRM snapshot; url=https://router.project-osrm.org/route/v1/driving/a;b",
                }
            ],
        )
        summary_path.write_text("fixture summary", encoding="utf-8")

        value = write_osrm_snapshot_manifest(
            benchmark_path=benchmark_path,
            summary_path=summary_path,
            manifest_path=manifest_path,
        )
        written = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert value == written
        assert written["row_count"] == 1
        assert written["unpinned_row_count"] == 0
        assert written["query_url_count"] == 1
        assert written["csv_sha256"]
        assert written["summary_sha256"]
        assert written["publication_ready"] is False

    print("PASS: OSRM snapshot manifest writer emits JSON")


def test_shipped_osrm_snapshot_manifest_matches_current_artifact() -> None:
    """The committed manifest should match the current OSRM benchmark CSV."""

    expected = build_osrm_snapshot_manifest()

    assert DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH.exists()
    with DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        written = json.load(handle)

    assert written == expected

    print("PASS: shipped OSRM snapshot manifest matches current artifact")


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "route_check_id",
        "benchmark_method",
        "source_class",
        "reference_source",
        "reference_version",
        "distance_status",
        "time_status",
        "status",
        "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    test_current_osrm_snapshot_manifest_counts()
    test_osrm_snapshot_manifest_writer_emits_json()
    test_shipped_osrm_snapshot_manifest_matches_current_artifact()
    print("\n=== REALWORLD OSRM SNAPSHOT MANIFEST TESTS PASSED ===")
