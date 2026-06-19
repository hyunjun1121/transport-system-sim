"""Offline smoke tests for the pilot-region cached real-world path."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.build_pilot_cache import (
    DEFAULT_CACHE_PATH,
    DEFAULT_MANIFEST_PATH,
    DEFAULT_REGION_PATH,
    main as build_cache_main,
)
from scripts import run_pilot_smoke as smoke_script


def test_pilot_cache_manifest_records_boundary_and_tooling() -> None:
    """The cached OSM snapshot manifest should carry review metadata."""

    assert DEFAULT_MANIFEST_PATH.exists()
    manifest = json.loads(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == 1
    assert manifest["total_edges"] > 0
    assert manifest["overrides_path"].endswith("road_class_overrides.csv")
    assert manifest["overrides_sha256"]
    assert manifest["claim_boundary"]
    assert manifest["result_scope"]
    assert manifest["can_support_road_evidence_gate"] is True

    print("PASS: pilot cache manifest records boundary and tooling metadata")


def test_cached_pilot_region_runs_both_modes() -> None:
    """The cached pilot graph should run both public scenario modes offline."""

    if not DEFAULT_CACHE_PATH.exists():
        build_cache_main()

    result = smoke_script.run_pilot_smoke(DEFAULT_REGION_PATH, DEFAULT_CACHE_PATH)

    assert result["region_id"] == "songpa_public_demo"
    assert result["graph_nodes"] >= 8
    assert result["graph_edges"] >= 12
    assert result["bus_success_count"] == 4
    assert result["multimodal_success_count"] == 4
    assert result["bus_completion_rate"] == 1.0
    assert result["multimodal_completion_rate"] == 1.0
    assert result["multimodal_train_trips"] == 1

    print("PASS: cached pilot region runs bus-only and multimodal smoke")


def test_pilot_smoke_cli_accepts_region_and_cache_paths() -> None:
    """CLI plumbing should pass explicit region/cache paths to the runner."""

    calls = []
    original = smoke_script.run_pilot_smoke

    def fake_run(region_path, cache_path):
        calls.append((region_path, cache_path))
        return {"region_id": "fixture", "graph_nodes": 1, "graph_edges": 1}

    smoke_script.run_pilot_smoke = fake_run
    try:
        status = smoke_script.main(
            [
                "--region",
                "tests/fixtures/synthetic_region_fixture.yaml",
                "--cache",
                "data/cache/pilot_region_road.graphml",
            ]
        )
    finally:
        smoke_script.run_pilot_smoke = original

    assert status == 0
    assert len(calls) == 1
    region_path, cache_path = calls[0]
    assert str(region_path).endswith("synthetic_region_fixture.yaml")
    assert str(cache_path).endswith("pilot_region_road.graphml")

    print("PASS: pilot smoke CLI accepts explicit region and cache paths")


if __name__ == "__main__":
    test_pilot_cache_manifest_records_boundary_and_tooling()
    test_cached_pilot_region_runs_both_modes()
    test_pilot_smoke_cli_accepts_region_and_cache_paths()
    print("\n=== REALWORLD PILOT SMOKE TESTS PASSED ===")
