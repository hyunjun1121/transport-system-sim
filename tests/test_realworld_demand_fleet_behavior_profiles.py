"""Tests for Phase 5 demand/fleet/behavior profile review artifacts."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.demand_fleet_behavior_profiles import (  # noqa: E402
    BEHAVIOR_PROFILE_COLUMNS,
    DEFAULT_BEHAVIOR_PROFILE_PATH,
    DEFAULT_DEMAND_PROFILE_PATH,
    DEFAULT_FLEET_PROFILE_PATH,
    DEFAULT_PROFILE_MANIFEST_PATH,
    DEMAND_PROFILE_COLUMNS,
    FLEET_PROFILE_COLUMNS,
    PROFILE_SCOPE,
    build_phase5_profile_rows,
    write_phase5_profile_packet,
)


def test_phase5_profile_rows_have_expected_contract_shape() -> None:
    """Current Phase 5 packet should expose bounded profile contracts."""

    rows = build_phase5_profile_rows()

    assert len(rows["demand"]) == 2
    assert len(rows["fleet"]) == 6
    assert len(rows["behavior"]) == 6
    assert {row["profile_id"] for row in rows["demand"]} == {
        "config_default_demand",
        "pilot_default_demand",
    }
    assert {row["profile_id"] for row in rows["fleet"]} == {
        "config_default_fleet",
        "pilot_default_fleet",
    }
    assert {row["profile_id"] for row in rows["behavior"]} == {
        "pilot_default_behavior"
    }
    assert {row["claim_boundary"] for row in rows["demand"]} == {PROFILE_SCOPE}
    assert {row["claim_boundary"] for row in rows["fleet"]} == {PROFILE_SCOPE}
    assert {row["claim_boundary"] for row in rows["behavior"]} == {PROFILE_SCOPE}

    print("PASS: Phase 5 profile rows have expected bounded contract shape")


def test_pilot_demand_sigma_is_not_blank() -> None:
    """Pilot demand should inherit the pilot fixture sigma level."""

    rows = build_phase5_profile_rows()
    demand_by_id = {row["profile_id"]: row for row in rows["demand"]}

    assert demand_by_id["pilot_default_demand"]["arrival_param_sigma"] == "0.75"
    assert demand_by_id["pilot_default_demand"][
        "evidence_status"
    ] == "bounded_scenario_assumption_not_calibration"
    assert demand_by_id["pilot_default_demand"][
        "completion_denominator"
    ] == "total_scenario_demand"

    print("PASS: pilot demand sigma is explicit and non-blank")


def test_writer_outputs_non_acceptance_artifacts() -> None:
    """Writer should emit CSVs, manifest, and Markdown without gate support."""

    rows = build_phase5_profile_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        manifest = write_phase5_profile_packet(
            rows=rows,
            demand_path=root / "demand_profiles.csv",
            fleet_path=root / "fleet_profiles.csv",
            behavior_path=root / "behavior_profiles.csv",
            manifest_path=root / "demand_fleet_behavior_profile_manifest.json",
            doc_path=root / "demand_fleet_behavior_profiles.md",
        )
        demand_rows = _read_csv(root / "demand_profiles.csv")
        fleet_rows = _read_csv(root / "fleet_profiles.csv")
        behavior_rows = _read_csv(root / "behavior_profiles.csv")
        written_manifest = json.loads(
            (root / "demand_fleet_behavior_profile_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        doc_text = (root / "demand_fleet_behavior_profiles.md").read_text(
            encoding="utf-8"
        )

    assert tuple(demand_rows[0].keys()) == DEMAND_PROFILE_COLUMNS
    assert tuple(fleet_rows[0].keys()) == FLEET_PROFILE_COLUMNS
    assert tuple(behavior_rows[0].keys()) == BEHAVIOR_PROFILE_COLUMNS
    assert manifest["row_counts"] == {"demand": 2, "fleet": 6, "behavior": 6}
    assert written_manifest["row_counts"] == manifest["row_counts"]
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_parameter_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["runtime_profile_consumption"] == {
        "pilot_experiments_consumes_profiles": True,
        "runtime_consumer": "src/realworld/pilot_experiments.py",
        "consumption_scope": (
            "pilot_default demand and fleet rows are consumed as bounded "
            "runtime inputs; this is not calibration, operating roster "
            "evidence, publication readiness, final-study readiness, or "
            "formal acceptance"
        ),
    }
    assert not any(
        "not yet consumed as runtime inputs" in item
        for item in manifest["remaining_blockers"]
    )
    assert "not calibrated OD demand" in doc_text
    assert "not formal acceptance" in doc_text

    print("PASS: Phase 5 writer emits non-acceptance artifacts")


def test_shipped_phase5_outputs_match_current_rows() -> None:
    """Shipped Phase 5 outputs should match the current generated rows."""

    rows = build_phase5_profile_rows()

    assert DEFAULT_DEMAND_PROFILE_PATH.exists()
    assert DEFAULT_FLEET_PROFILE_PATH.exists()
    assert DEFAULT_BEHAVIOR_PROFILE_PATH.exists()
    assert DEFAULT_PROFILE_MANIFEST_PATH.exists()
    assert _read_csv(DEFAULT_DEMAND_PROFILE_PATH) == rows["demand"]
    assert _read_csv(DEFAULT_FLEET_PROFILE_PATH) == rows["fleet"]
    assert _read_csv(DEFAULT_BEHAVIOR_PROFILE_PATH) == rows["behavior"]
    manifest = json.loads(DEFAULT_PROFILE_MANIFEST_PATH.read_text(encoding="utf-8"))
    assert manifest["row_counts"] == {"demand": 2, "fleet": 6, "behavior": 6}
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_parameter_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False

    print("PASS: shipped Phase 5 profile outputs match current rows")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    test_phase5_profile_rows_have_expected_contract_shape()
    test_pilot_demand_sigma_is_not_blank()
    test_writer_outputs_non_acceptance_artifacts()
    test_shipped_phase5_outputs_match_current_rows()
    print("\n=== REALWORLD DEMAND FLEET BEHAVIOR PROFILE TESTS PASSED ===")
