"""Offline smoke tests for the pilot-region cached real-world path."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.build_pilot_cache import DEFAULT_CACHE_PATH, DEFAULT_REGION_PATH, main as build_cache_main
from scripts.run_pilot_smoke import run_pilot_smoke


def test_cached_pilot_region_runs_both_modes() -> None:
    """The cached pilot graph should run both public scenario modes offline."""

    if not DEFAULT_CACHE_PATH.exists():
        build_cache_main()

    result = run_pilot_smoke(DEFAULT_REGION_PATH, DEFAULT_CACHE_PATH)

    assert result["region_id"] == "songpa_public_demo"
    assert result["graph_nodes"] >= 8
    assert result["graph_edges"] >= 12
    assert result["bus_success_count"] == 4
    assert result["multimodal_success_count"] == 4
    assert result["bus_completion_rate"] == 1.0
    assert result["multimodal_completion_rate"] == 1.0
    assert result["multimodal_train_trips"] == 1

    print("PASS: cached pilot region runs bus-only and multimodal smoke")


if __name__ == "__main__":
    test_cached_pilot_region_runs_both_modes()
    print("\n=== REALWORLD PILOT SMOKE TESTS PASSED ===")
