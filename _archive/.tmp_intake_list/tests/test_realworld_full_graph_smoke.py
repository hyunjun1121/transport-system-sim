"""Smoke test for the full bus-practical pilot graph path."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_full_graph_smoke.py"


def _load_smoke_module():
    spec = importlib.util.spec_from_file_location("run_full_graph_smoke", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_full_graph_smoke"] = module
    spec.loader.exec_module(module)
    return module


def test_full_graph_smoke_runs_without_corridor_reduction() -> None:
    """The full filtered OSM graph should run a tiny two-policy smoke."""

    module = _load_smoke_module()
    result = module.run_full_graph_smoke()

    assert result["analysis_graph_reduced"] is False
    assert result["graph_nodes"] > 1000
    assert result["graph_edges"] > 1000
    assert result["row_count"] == 2
    assert set(result["policies"]) == {"bus_only", "baseline_multimodal"}
    assert all(
        0.0 <= float(value) <= 1.0
        for value in result["completion_rates"].values()
    )
    assert all(
        math.isfinite(float(value)) and float(value) > 0.0
        for value in result["penalized_makespan"].values()
    )
    assert "not calibrated real-world" in result["claim_scope"]

    print("PASS: full bus-practical graph smoke runs without corridor reduction")


def test_full_graph_smoke_cli_accepts_region_cache_and_design_paths() -> None:
    """CLI plumbing should pass explicit input paths and seed to the runner."""

    module = _load_smoke_module()
    calls = []
    original = module.run_full_graph_smoke

    def fake_run_full_graph_smoke(**kwargs):
        calls.append(kwargs)
        return {
            "schema_version": 1,
            "region_id": "fixture",
            "graph_nodes": 2000,
            "graph_edges": 3000,
            "analysis_graph_reduced": False,
            "row_count": 2,
            "policies": ["bus_only", "baseline_multimodal"],
            "scenario_ids": ["no_disruption"],
            "seed": kwargs["seed"],
            "completion_rates": {
                "bus_only": 1.0,
                "baseline_multimodal": 1.0,
            },
            "penalized_makespan": {
                "bus_only": 10.0,
                "baseline_multimodal": 12.0,
            },
            "graph_scale": {},
            "claim_scope": module.FULL_GRAPH_SMOKE_SCOPE,
        }

    module.run_full_graph_smoke = fake_run_full_graph_smoke
    try:
        status = module.main(
            [
                "--region-path",
                "tests/fixtures/synthetic_region_fixture.yaml",
                "--cache-path",
                "data/cache/pilot_region_road.graphml",
                "--scenarios-path",
                "data/scenarios/disruption_scenarios.csv",
                "--policies-path",
                "data/scenarios/policy_alternatives.csv",
                "--seed",
                "77",
                "--no-write",
            ]
        )
    finally:
        module.run_full_graph_smoke = original

    assert status == 0
    assert len(calls) == 1
    call = calls[0]
    assert str(call["region_path"]).endswith("synthetic_region_fixture.yaml")
    assert str(call["cache_path"]).endswith("pilot_region_road.graphml")
    assert str(call["scenarios_path"]).endswith("disruption_scenarios.csv")
    assert str(call["policies_path"]).endswith("policy_alternatives.csv")
    assert call["seed"] == 77

    print("PASS: full graph smoke CLI accepts explicit paths and seed")


if __name__ == "__main__":
    test_full_graph_smoke_runs_without_corridor_reduction()
    test_full_graph_smoke_cli_accepts_region_cache_and_design_paths()
    print("\n=== REALWORLD FULL GRAPH SMOKE TESTS PASSED ===")
