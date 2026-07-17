"""Tests for the experiment statistical-analysis plan."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.experiment_statistical_plan import (  # noqa: E402
    build_experiment_statistical_plan,
    write_experiment_statistical_plan,
)


def test_statistical_plan_builds_review_ready_non_acceptance_note() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        paths = _write_bundle(root)
        manifest = build_experiment_statistical_plan(**paths)
    assert manifest["selected_profile_id"] == "full_pilot"
    assert manifest["blocking_check_count"] == 1
    assert manifest["statistical_plan_ready_for_review"] is False
    assert manifest["acceptance_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert "completion_rate" in manifest["primary_metrics"]


def test_statistical_plan_blocks_row_count_mismatch() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        paths = _write_bundle(root, row_count=11)
        manifest = build_experiment_statistical_plan(**paths)
    by_id = {check["check_id"]: check for check in manifest["checks"]}
    assert by_id["result_row_count_matches_design"]["status"] == "blocked_row_count_mismatch"


def test_write_statistical_plan_outputs_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        paths = _write_bundle(root)
        summary = write_experiment_statistical_plan(
            **paths,
            manifest_path=root / "plan.json",
            doc_path=root / "plan.md",
        )
        loaded = json.loads((root / "plan.json").read_text(encoding="utf-8"))
        doc = (root / "plan.md").read_text(encoding="utf-8")
    assert loaded["acceptance_ready"] is False
    assert summary["can_mark_complete"] is False
    assert "Experiment Statistical Analysis Plan" in doc


def _write_bundle(root: Path, *, row_count: int = 12) -> dict[str, Path]:
    design = root / "design.json"
    pilot = root / "pilot.json"
    statistics = root / "statistics.json"
    crn = root / "crn.json"
    replication = root / "replication.json"
    design.write_text(
        json.dumps(
            {
                "region_id": "demo",
                "profiles": {
                    "full_pilot": {
                        "design_status": "candidate",
                        "result_scope": "scaffold",
                        "analysis_graph_strategy": "single_corridor",
                        "policy_ids": ["bus_only", "baseline_multimodal"],
                        "scenario_ids": ["no_disruption", "blocked"],
                        "seeds": [1, 2, 3],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    pilot.write_text(
        json.dumps(
            {
                "run_profile": "full_pilot",
                "region_id": "demo",
                "graph_source": "fixture",
                "row_count": row_count,
                "summary_row_count": 4,
            }
        ),
        encoding="utf-8",
    )
    statistics.write_text(
        json.dumps(
            {
                "source_run_profile": "full_pilot",
                "ci_method": "normal_approximation",
                "multiple_comparison_method": "exploratory secondary comparisons",
            }
        ),
        encoding="utf-8",
    )
    crn.write_text(
        json.dumps({"structural_crn_pairing_ready": True}),
        encoding="utf-8",
    )
    replication.write_text(
        json.dumps(
            {
                "paired_statistics_structurally_ready": True,
                "needs_human_review_count": 3,
            }
        ),
        encoding="utf-8",
    )
    return {
        "design_path": design,
        "pilot_manifest_path": pilot,
        "statistics_manifest_path": statistics,
        "crn_manifest_path": crn,
        "replication_manifest_path": replication,
    }


if __name__ == "__main__":
    test_statistical_plan_builds_review_ready_non_acceptance_note()
    test_statistical_plan_blocks_row_count_mismatch()
    test_write_statistical_plan_outputs_files()
    print("PASS: experiment statistical analysis plan")
