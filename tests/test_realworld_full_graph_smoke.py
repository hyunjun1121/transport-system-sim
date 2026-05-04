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


if __name__ == "__main__":
    test_full_graph_smoke_runs_without_corridor_reduction()
    print("\n=== REALWORLD FULL GRAPH SMOKE TESTS PASSED ===")
