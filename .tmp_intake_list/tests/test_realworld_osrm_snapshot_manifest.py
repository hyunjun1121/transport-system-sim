"""Tests for optional OSRM snapshot manifest generation."""

from __future__ import annotations

import csv
import importlib.util
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_osrm_route_benchmark.py"

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
    assert manifest["source_class_counts"] == {
        "cached_external_router_snapshot": 3
    }
    assert len(manifest["reference_version_counts"]) == 1
    reference_version = next(iter(manifest["reference_version_counts"]))
    assert reference_version.startswith("cached_osrm_snapshot_")
    assert manifest["reference_version_counts"][reference_version] == 3
    assert manifest["query_url_count"] == 3
    assert manifest["unpinned_row_count"] == 0
    assert manifest["raw_response_file_count"] == 3
    assert {
        Path(item["path"]).name for item in manifest["raw_response_files"]
    } == {
        "route_bus_direct.json",
        "route_last_mile.json",
        "route_rail_access.json",
    }
    assert manifest["publication_ready"] is False
    assert manifest["acceptance_ready"] is False
    assert "not validation acceptance" in manifest["claim_boundary"]
    assert not any("raw OSRM response" in item for item in manifest["review_items"])

    print("PASS: current OSRM snapshot manifest counts are conservative")


def test_osrm_snapshot_manifest_writer_emits_json() -> None:
    """Writer should emit a stable manifest for arbitrary OSRM-like rows."""

    with TemporaryDirectory() as directory:
        benchmark_path = Path(directory) / "external_route_benchmarks_osrm.csv"
        summary_path = Path(directory) / "osrm_route_benchmark_summary.md"
        manifest_path = Path(directory) / "osrm_route_benchmark_manifest.json"
        raw_dir = Path(directory) / "raw"
        raw_dir.mkdir()
        raw_file = raw_dir / "route_bus_direct.json"
        raw_file.write_text('{"fixture": true}\n', encoding="utf-8")
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
            raw_response_dir=raw_dir,
        )
        written = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert value == written
        assert written["row_count"] == 1
        assert written["unpinned_row_count"] == 0
        assert written["raw_response_file_count"] == 1
        assert written["raw_response_files"][0]["path"].endswith(
            "route_bus_direct.json"
        )
        assert written["raw_response_files"][0]["sha256"]
        assert written["query_url_count"] == 1
        assert written["csv_sha256"]
        assert written["summary_sha256"]
        assert written["publication_ready"] is False

    print("PASS: OSRM snapshot manifest writer emits JSON")


def test_osrm_runner_writes_raw_payloads_into_manifest() -> None:
    """Runner should connect retained raw payloads to the manifest path."""

    module = _load_runner_module()

    class FakeGraph:
        def number_of_nodes(self) -> int:
            return 2

        def number_of_edges(self) -> int:
            return 1

    class FakeRoute:
        check_id = "route_bus_direct"
        source = "A"
        target = "D"
        label = "bus direct road leg"

    class FakeRecord:
        status = "pass"
        route_check_id = "route_bus_direct"
        subject = "A->D"
        distance_ratio = 1.0
        time_ratio = 1.0

    def fake_load_graphml(path: Path, normalize: bool = True) -> object:
        assert normalize is True
        return {"path": str(path)}

    def fake_build_simulator_graph(road_graph: object, region: dict) -> FakeGraph:
        assert region["region_id"] == "fixture_region"
        return FakeGraph()

    def fake_build_osrm_route_benchmarks(
        graph: FakeGraph,
        *,
        base_url: str,
        timeout_s: float,
        source_class: str,
        reference_version: str,
        payload_callback=None,
    ) -> tuple[str, ...]:
        assert base_url == "https://router.project-osrm.org"
        assert timeout_s == 3.0
        assert source_class == "cached_external_router_snapshot"
        assert reference_version.startswith("cached_osrm_snapshot_")
        assert payload_callback is not None
        route = FakeRoute()
        payload = {"routes": [{"distance": 100.0, "duration": 60.0}]}
        payload_callback(
            route,
            "https://router.project-osrm.org/route/v1/driving/a;b?overview=false",
            payload,
        )
        return ("benchmark",)

    def fake_evaluate_external_route_benchmarks(
        graph: FakeGraph,
        benchmarks: tuple[str, ...],
        *,
        region_id: str,
    ) -> tuple[FakeRecord, ...]:
        assert benchmarks == ("benchmark",)
        assert region_id == "fixture_region"
        return (FakeRecord(),)

    def fake_benchmark_status_counts(records: tuple[FakeRecord, ...]) -> dict[str, int]:
        return {"pass": len(records), "warn": 0, "fail": 0}

    def fake_benchmark_records_to_csv_rows(
        records: tuple[FakeRecord, ...],
    ) -> tuple[dict[str, str], ...]:
        row = {field: "" for field in module.BENCHMARK_CSV_FIELDS}
        row.update(
            {
                "region_id": "fixture_region",
                "benchmark_id": "route_bus_direct_osrm",
                "route_check_id": "route_bus_direct",
                "subject": "A->D",
                "benchmark_method": "osrm_route_v1_driving",
                "source_class": "cached_external_router_snapshot",
                "reference_source": "https://router.project-osrm.org",
                "reference_version": "cached_osrm_snapshot_fixture",
                "distance_status": "pass",
                "time_status": "pass",
                "status": "pass",
                "notes": (
                    "optional cached OSRM route API snapshot; "
                    "reference_version=cached_osrm_snapshot_fixture; "
                    "url=https://router.project-osrm.org/route/v1/driving/a;b"
                ),
            }
        )
        return (row,)

    originals = {
        "load_graphml": module.load_graphml,
        "build_simulator_graph": module.build_simulator_graph,
        "build_osrm_route_benchmarks": module.build_osrm_route_benchmarks,
        "evaluate_external_route_benchmarks": module.evaluate_external_route_benchmarks,
        "benchmark_status_counts": module.benchmark_status_counts,
        "benchmark_records_to_csv_rows": module.benchmark_records_to_csv_rows,
    }
    module.load_graphml = fake_load_graphml
    module.build_simulator_graph = fake_build_simulator_graph
    module.build_osrm_route_benchmarks = fake_build_osrm_route_benchmarks
    module.evaluate_external_route_benchmarks = fake_evaluate_external_route_benchmarks
    module.benchmark_status_counts = fake_benchmark_status_counts
    module.benchmark_records_to_csv_rows = fake_benchmark_records_to_csv_rows
    try:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            region_path = root / "region.yaml"
            cache_path = root / "road.graphml"
            output_path = root / "benchmarks.csv"
            summary_path = root / "summary.md"
            manifest_path = root / "manifest.json"
            raw_dir = root / "raw"
            region_path.write_text("region_id: fixture_region\n", encoding="utf-8")
            cache_path.write_text("", encoding="utf-8")

            result = module.run_osrm_route_benchmark(
                region_path=region_path,
                cache_path=cache_path,
                output_path=output_path,
                summary_path=summary_path,
                manifest_path=manifest_path,
                timeout_s=3.0,
                raw_output_dir=raw_dir,
            )

            raw_file = raw_dir / "route_bus_direct.json"
            raw_payload = json.loads(raw_file.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

            assert result["raw_output_dir"] == str(raw_dir)
            assert raw_payload["route_check_id"] == "route_bus_direct"
            assert raw_payload["payload"]["routes"][0]["distance"] == 100.0
            assert raw_payload["snapshot_reference_version"].startswith(
                "cached_osrm_snapshot_"
            )
            assert manifest["raw_response_file_count"] == 1
            assert manifest["raw_response_files"][0]["path"].endswith(
                "route_bus_direct.json"
            )
            assert manifest["unpinned_row_count"] == 0
    finally:
        for name, value in originals.items():
            setattr(module, name, value)

    print("PASS: OSRM runner writes raw payloads into manifest")


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


def _load_runner_module():
    spec = importlib.util.spec_from_file_location("run_osrm_route_benchmark", RUNNER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_osrm_route_benchmark"] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    test_current_osrm_snapshot_manifest_counts()
    test_osrm_snapshot_manifest_writer_emits_json()
    test_osrm_runner_writes_raw_payloads_into_manifest()
    test_shipped_osrm_snapshot_manifest_matches_current_artifact()
    print("\n=== REALWORLD OSRM SNAPSHOT MANIFEST TESTS PASSED ===")
