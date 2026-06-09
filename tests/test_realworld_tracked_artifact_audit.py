"""Tests for clean-checkout tracked-artifact audit."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.tracked_artifact_audit import (  # noqa: E402
    build_dirty_worktree_classification_rows,
    build_tracked_artifact_rows,
    summarize_dirty_worktree_classification_rows,
    summarize_tracked_artifact_rows,
    write_dirty_worktree_classification,
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
            " M data/validation/dirty_worktree_classification.csv",
            " M data/validation/dirty_worktree_classification_manifest.json",
            " M docs/tracked_artifact_audit.md",
            " M docs/dirty_worktree_classification.md",
            " M docs/current_goal_completion_audit.md",
        )
    )
    by_path = {row["path"]: row for row in rows}
    assert "data/validation/tracked_artifact_audit.csv" not in by_path
    assert "data/validation/tracked_artifact_audit_manifest.json" not in by_path
    assert "data/validation/dirty_worktree_classification.csv" not in by_path
    assert "data/validation/dirty_worktree_classification_manifest.json" not in by_path
    assert "docs/tracked_artifact_audit.md" not in by_path
    assert "docs/dirty_worktree_classification.md" not in by_path
    assert "docs/current_goal_completion_audit.md" in by_path


def test_tracked_artifact_rows_ignore_review_package_self_outputs() -> None:
    rows = build_tracked_artifact_rows(
        git_status_lines=(
            "?? data/manifests/review_package_build_manifest.json",
            "?? data/manifests/review_package_inventory.csv",
            "?? data/manifests/review_package_inventory_manifest.json",
            "?? data/manifests/review_package_path_audit.json",
            "?? docs/review_package_build.md",
            "?? docs/review_package_inventory.md",
            "?? docs/review_package_path_audit.md",
            "?? docs/expert_consultation_request.md",
        )
    )
    by_path = {row["path"]: row for row in rows}
    assert "data/manifests/review_package_build_manifest.json" not in by_path
    assert "data/manifests/review_package_inventory.csv" not in by_path
    assert "data/manifests/review_package_inventory_manifest.json" not in by_path
    assert "data/manifests/review_package_path_audit.json" not in by_path
    assert "docs/review_package_build.md" not in by_path
    assert "docs/review_package_inventory.md" not in by_path
    assert "docs/review_package_path_audit.md" not in by_path
    assert "docs/expert_consultation_request.md" in by_path


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
        text = (root / "tracked.md").read_text(encoding="utf-8")
        assert "Tracked Artifact Audit" in text
        assert "excludes its own generated CSV, manifest, and Markdown outputs" in text
        assert "accepted reproduction scope" not in text


def test_write_tracked_artifact_audit_preserves_timestamp_when_unchanged() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest_path = root / "tracked.json"
        write_tracked_artifact_audit(
            rows=[],
            output_path=root / "tracked.csv",
            manifest_path=manifest_path,
            doc_path=root / "tracked.md",
        )
        first = json.loads(manifest_path.read_text(encoding="utf-8"))
        first["generated_at"] = "2000-01-01T00:00:00+00:00"
        manifest_path.write_text(
            json.dumps(first, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        summary = write_tracked_artifact_audit(
            rows=[],
            output_path=root / "tracked.csv",
            manifest_path=manifest_path,
            doc_path=root / "tracked.md",
        )
        loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert summary["generated_at"] == "2000-01-01T00:00:00+00:00"
    assert loaded["generated_at"] == "2000-01-01T00:00:00+00:00"


def test_dirty_worktree_classification_includes_non_reproducibility_paths() -> None:
    rows = build_dirty_worktree_classification_rows(
        git_status_lines=(
            " M plan.md",
            "?? scratch.tmp",
            "?? .tmp_phase4_source_probe/source.json",
            "?? cloned_repo/example.txt",
            " M data/validation/artifact_invalidation_matrix.csv",
        )
    )
    by_path = {row["path"]: row for row in rows}
    assert "plan.md" in by_path
    assert "scratch.tmp" in by_path
    assert ".tmp_phase4_source_probe/source.json" in by_path
    assert "cloned_repo/example.txt" in by_path
    assert "data/validation/artifact_invalidation_matrix.csv" in by_path
    assert by_path["scratch.tmp"]["owner"] == "main_thread_owner_required"
    assert by_path["plan.md"]["phase"] == "phase0_baseline_and_worktree_safety"
    assert by_path["data/validation/artifact_invalidation_matrix.csv"]["phase"] == (
        "phase9_artifact_invalidation_closeout"
    )


def test_dirty_worktree_classification_git_failure_is_fail_closed() -> None:
    rows = build_dirty_worktree_classification_rows(
        git_status_lines=("!! git status failed: fatal example",)
    )
    assert len(rows) == 1
    assert rows[0]["path"] == "<git-status-failed>"
    assert rows[0]["evidence_status"] == "git_status_failed"
    assert rows[0]["new_generated_output_allowed"] == "no"
    summary = summarize_dirty_worktree_classification_rows(rows)
    assert summary["git_status_failed"] is True
    assert summary["new_generated_output_allowed"] is False
    assert summary["remaining_blockers"]


def test_dirty_worktree_classification_summary_is_fail_closed() -> None:
    rows = build_dirty_worktree_classification_rows(
        git_status_lines=("?? docs/example.md", " M src/realworld/example.py")
    )
    summary = summarize_dirty_worktree_classification_rows(rows)
    assert summary["dirty_path_count"] == 2
    assert summary["classified_path_count"] == 2
    assert summary["unclassified_path_count"] == 0
    assert summary["new_generated_output_allowed"] is False
    assert summary["destructive_cleanup_allowed"] is False
    assert summary["remaining_blockers"]


def test_write_dirty_worktree_classification_outputs_files() -> None:
    rows = build_dirty_worktree_classification_rows(
        git_status_lines=(
            "?? data/validation/dirty_worktree_classification.csv",
            " M docs/example.md",
        )
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        summary = write_dirty_worktree_classification(
            rows=rows,
            output_path=root / "dirty.csv",
            manifest_path=root / "dirty.json",
            doc_path=root / "dirty.md",
        )
        loaded = json.loads((root / "dirty.json").read_text(encoding="utf-8"))
        assert loaded["dirty_path_count"] == 2
        assert summary["can_mark_complete"] is False
        assert summary["final_study_ready"] is False
        assert summary["new_generated_output_allowed"] is False
        assert (root / "dirty.csv").exists()
        text = (root / "dirty.md").read_text(encoding="utf-8")
        csv_rows = list(
            csv.DictReader((root / "dirty.csv").read_text(encoding="utf-8").splitlines())
        )
        assert "Dirty Worktree Classification" in text
        assert "does not commit files" in text
        assert any(
            row["allowed_next_action"]
            == "Run claim-boundary review before report, package, or final-study use."
            for row in csv_rows
        )
        assert "or final-study use" not in text
        assert "Run claim-boundary review before report or package use." in text


if __name__ == "__main__":
    test_tracked_artifact_rows_filter_reproducibility_candidates()
    test_tracked_artifact_rows_ignore_own_outputs()
    test_tracked_artifact_rows_ignore_review_package_self_outputs()
    test_tracked_artifact_summary_stays_non_acceptance()
    test_write_tracked_artifact_audit_outputs_files()
    test_write_tracked_artifact_audit_preserves_timestamp_when_unchanged()
    test_dirty_worktree_classification_includes_non_reproducibility_paths()
    test_dirty_worktree_classification_git_failure_is_fail_closed()
    test_dirty_worktree_classification_summary_is_fail_closed()
    test_write_dirty_worktree_classification_outputs_files()
    print("PASS: tracked artifact audit")
