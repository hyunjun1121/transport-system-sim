"""Tests for clean-checkout tracked-artifact audit."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.tracked_artifact_audit import (  # noqa: E402
    build_tracked_artifact_rows,
    summarize_tracked_artifact_rows,
    write_tracked_artifact_audit,
)


def test_tracked_artifact_rows_filter_reproducibility_candidates() -> None:
    rows = build_tracked_artifact_rows(
        git_status_lines=(
            " M plan.md",
            "?? src/realworld/new_module.py",
            "?? tests/test_realworld_new_module.py",
            " M tests/test_scenario.py",
            "?? scratch.tmp",
        )
    )
    by_path = {row["path"]: row for row in rows}
    assert "plan.md" in by_path
    assert "src/realworld/new_module.py" in by_path
    assert "tests/test_realworld_new_module.py" in by_path
    assert "tests/test_scenario.py" in by_path
    assert "scratch.tmp" not in by_path
    assert by_path["plan.md"]["clean_checkout_risk"] == "changed_after_head"
    assert (
        by_path["src/realworld/new_module.py"]["clean_checkout_risk"]
        == "missing_from_clean_checkout"
    )


def test_tracked_artifact_rows_ignore_own_outputs() -> None:
    rows = build_tracked_artifact_rows(
        git_status_lines=(
            " M data/validation/tracked_artifact_audit.csv",
            " M data/validation/tracked_artifact_audit_manifest.json",
            " M docs/tracked_artifact_audit.md",
            " M docs/current_goal_completion_audit.md",
        )
    )
    by_path = {row["path"]: row for row in rows}
    assert "data/validation/tracked_artifact_audit.csv" not in by_path
    assert "data/validation/tracked_artifact_audit_manifest.json" not in by_path
    assert "docs/tracked_artifact_audit.md" not in by_path
    assert "docs/current_goal_completion_audit.md" in by_path


def test_tracked_artifact_summary_stays_non_acceptance() -> None:
    rows = build_tracked_artifact_rows(
        git_status_lines=("?? data/manifests/example.json", " M status.md")
    )
    summary = summarize_tracked_artifact_rows(rows)
    assert summary["row_count"] == 2
    assert summary["blocking_change_count"] == 2
    assert summary["untracked_count"] == 1
    assert summary["modified_or_staged_count"] == 1
    assert summary["remaining_blockers"]


def test_write_tracked_artifact_audit_outputs_files() -> None:
    rows = build_tracked_artifact_rows(git_status_lines=("?? docs/example.md",))
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        summary = write_tracked_artifact_audit(
            rows=rows,
            output_path=root / "tracked.csv",
            manifest_path=root / "tracked.json",
            doc_path=root / "tracked.md",
        )
        loaded = json.loads((root / "tracked.json").read_text(encoding="utf-8"))
        assert loaded["row_count"] == 1
        assert summary["can_mark_complete"] is False
        assert (root / "tracked.csv").exists()
        assert "Tracked Artifact Audit" in (root / "tracked.md").read_text(
            encoding="utf-8"
        )


if __name__ == "__main__":
    test_tracked_artifact_rows_filter_reproducibility_candidates()
    test_tracked_artifact_rows_ignore_own_outputs()
    test_tracked_artifact_summary_stays_non_acceptance()
    test_write_tracked_artifact_audit_outputs_files()
    print("PASS: tracked artifact audit")
