"""Tests for the executable Phase 8 micro-probe wrapper."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.phase8_micro_probe import (  # noqa: E402
    MICRO_PROBE_EXPECTED_ROW_COUNT,
    MICRO_PROBE_EXPECTED_SUMMARY_ROW_COUNT,
    MICRO_PROBE_POLICY_IDS,
    MICRO_PROBE_PROFILE_ID,
    MICRO_PROBE_SCENARIO_IDS,
    MICRO_PROBE_SEEDS,
    PHASE8_MICRO_PROBE_SCOPE,
    run_phase8_micro_probe,
)


def test_phase8_micro_probe_runs_frozen_slice_and_deterministic_rerun() -> None:
    """The wrapper should freeze the minimal Phase 8 slice and compare reruns."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        runtime_preflight = root / "runtime_preflight.json"
        _write_runtime_preflight(runtime_preflight, execution_scope="micro_probe")

        result = run_phase8_micro_probe(
            output_dir=root / "primary",
            rerun_output_dir=root / "rerun",
            manifest_path=root / "micro_probe_manifest.json",
            runtime_preflight_manifest_path=runtime_preflight,
        )

        manifest = result["manifest"]
        assert result["manifest_path"].exists()
        assert manifest["phase_id"] == "phase8_micro_probe"
        assert manifest["profile_id"] == MICRO_PROBE_PROFILE_ID
        assert manifest["worker_count"] == 1
        assert manifest["r_equivalent"] == 1
        assert tuple(manifest["policy_ids"]) == MICRO_PROBE_POLICY_IDS
        assert tuple(manifest["scenario_ids"]) == MICRO_PROBE_SCENARIO_IDS
        assert tuple(manifest["seeds"]) == MICRO_PROBE_SEEDS
        assert manifest["expected_row_count"] == MICRO_PROBE_EXPECTED_ROW_COUNT
        assert manifest["actual_row_count"] == MICRO_PROBE_EXPECTED_ROW_COUNT
        assert manifest["expected_summary_row_count"] == (
            MICRO_PROBE_EXPECTED_SUMMARY_ROW_COUNT
        )
        assert manifest["actual_summary_row_count"] == (
            MICRO_PROBE_EXPECTED_SUMMARY_ROW_COUNT
        )
        assert manifest["micro_probe_execution_ready"] is True
        assert manifest["execution_blockers"] == []
        assert manifest["checks"]["deterministic_results_hash_match"] is True
        assert manifest["checks"]["deterministic_summary_hash_match"] is True
        assert manifest["checks"]["profile_inputs_consumed"] is True
        assert manifest["checks"]["profile_input_hashes_match"] is True
        assert manifest["checks"]["profile_ids_match_design"] is True
        assert manifest["checks"]["runtime_preflight_ready_for_micro_probe"] is True
        assert manifest["profile_runtime_inputs"]["primary"][
            "runtime_profile_inputs_consumed"
        ] is True
        assert manifest["profile_runtime_inputs"]["primary"]["demand_profile_id"] == (
            "pilot_default_demand"
        )
        assert manifest["profile_runtime_inputs"]["primary"]["fleet_profile_id"] == (
            "pilot_default_fleet"
        )
        assert manifest["profile_runtime_inputs"]["primary"][
            "demand_profiles_sha256"
        ] == manifest["profile_runtime_inputs"]["deterministic_rerun"][
            "demand_profiles_sha256"
        ]
        assert manifest["profile_runtime_inputs"]["primary"][
            "fleet_profiles_sha256"
        ] == manifest["profile_runtime_inputs"]["deterministic_rerun"][
            "fleet_profiles_sha256"
        ]
        assert manifest["profile_runtime_inputs"]["primary"][
            "can_support_final_study_gate"
        ] is False
        assert manifest["promotion_ready"] is False
        assert manifest["publication_ready"] is False
        assert manifest["final_study_ready"] is False
        assert manifest["formal_acceptance_evidence"] is False
        assert manifest["operational_use_allowed"] is False
        assert manifest["claim_boundary"] == PHASE8_MICRO_PROBE_SCOPE
        assert "not final-study approval" in manifest["claim_boundary"]
        assert result["primary"]["manifest"]["engineering_only"] is True
        # Rail is now a wartime_charter_assumption (source decisions pending) and
        # the Phase-1 retune left the artifact-invalidation matrix with open
        # Phase 9 blockers, so the non-sample micro-probe slice runs under
        # engineering-only bypass — the honest, non-promoted state.
        assert result["primary"]["manifest"]["engineering_only_bypass"] is True

    print("PASS: Phase 8 micro-probe wrapper freezes and verifies the minimal slice")


def test_phase8_micro_probe_requires_micro_probe_runtime_preflight_scope() -> None:
    """A CPU-only preflight is not enough for the executable micro-probe check."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        runtime_preflight = root / "runtime_preflight.json"
        _write_runtime_preflight(runtime_preflight, execution_scope="cpu")

        result = run_phase8_micro_probe(
            output_dir=root / "primary",
            rerun_output_dir=root / "rerun",
            manifest_path=root / "micro_probe_manifest.json",
            runtime_preflight_manifest_path=runtime_preflight,
        )

        manifest = result["manifest"]
        assert manifest["micro_probe_execution_ready"] is False
        assert "runtime_preflight_ready_for_micro_probe failed" in manifest[
            "execution_blockers"
        ]
        assert manifest["runtime_preflight"]["execution_scope"] == "cpu"
        assert manifest["promotion_ready"] is False
        assert manifest["final_study_ready"] is False

    print("PASS: Phase 8 micro-probe rejects non-micro-probe preflight scope")


def _write_runtime_preflight(path: Path, *, execution_scope: str) -> None:
    path.write_text(
        json.dumps(
            {
                "runtime_preflight_ready": True,
                "execution_scope": execution_scope,
                "remaining_blockers": [],
                "final_study_ready": False,
                "formal_acceptance_evidence": False,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    test_phase8_micro_probe_runs_frozen_slice_and_deterministic_rerun()
    test_phase8_micro_probe_requires_micro_probe_runtime_preflight_scope()
    print("\n=== REALWORLD PHASE8 MICRO PROBE TESTS PASSED ===")
