"""Tests for reproducibility review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld import reproducibility_review_packet as packet_module  # noqa: E402
from src.realworld.reproducibility_review_packet import (  # noqa: E402
    REPRODUCIBILITY_REVIEW_COLUMNS,
    REPRODUCIBILITY_REVIEW_PACKET_SCOPE,
    build_reproducibility_review_rows,
    write_reproducibility_review_packet,
)


def test_reproducibility_review_rows_are_conservative() -> None:
    """Current package review rows should not imply acceptance."""

    rows = build_reproducibility_review_rows()
    by_category = {row["category_id"]: row for row in rows}

    assert len(rows) == 8
    assert set(by_category) == {
        "reproducibility_manifest_scope",
        "formal_reproducibility_acceptance_record",
        "git_worktree_state",
        "untracked_required_artifact_risk",
        "validation_command_ladder",
        "runtime_cloned_repo_import_boundary",
        "bounded_clean_checkout_smoke",
        "clean_checkout_execution_scope",
    }
    assert by_category["formal_reproducibility_acceptance_record"]["status"] == (
        "blocked_no_reproducibility_acceptance_record"
    )
    assert by_category["clean_checkout_execution_scope"]["status"] == (
        "blocked_full_clean_checkout_not_run"
    )
    assert "current_goal_completion_audit.json" in (
        by_category["clean_checkout_execution_scope"]["evidence_paths"]
    )
    assert "goal_manifest_can_mark_complete=false" in (
        by_category["clean_checkout_execution_scope"]["status_detail"]
    )
    assert by_category["bounded_clean_checkout_smoke"]["status"] in {
        "blocked_clean_checkout_smoke_not_run",
        "ready_for_review_bounded_clean_checkout_smoke",
        "ready_for_review_full_clean_checkout_smoke",
    }
    assert {row["acceptance_ready"] for row in rows} == {"false"}
    assert {row["publication_ready"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {
        REPRODUCIBILITY_REVIEW_PACKET_SCOPE
    }

    print("PASS: reproducibility review rows are conservative")


def test_reproducibility_review_rows_handle_fixture_state() -> None:
    """Fixture inputs should expose dirty/untracked worktree risk."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = root / "reproducibility_manifest.json"
        package_doc = root / "reproducibility_package.md"
        goal_audit = root / "goal.md"
        goal_manifest = root / "goal.json"
        acceptance = root / "reproducibility_acceptance.json"
        scan_dir = root / "src"
        scan_dir.mkdir()
        (scan_dir / "ok.py").write_text("import os\n", encoding="utf-8")
        manifest.write_text(
            json.dumps(
                {
                    "scope": "scaffold-only test package",
                    "commands": ["cmd one", "cmd two"],
                    "validation_commands": [["test one"], "test two"],
                }
            ),
            encoding="utf-8",
        )
        package_doc.write_text("This scaffold package is not final.\n", encoding="utf-8")
        goal_audit.write_text("Final-study ready: `false`\n", encoding="utf-8")
        goal_manifest.write_text(
            json.dumps({"final_study_ready": False, "can_mark_complete": False}),
            encoding="utf-8",
        )

        rows = build_reproducibility_review_rows(
            reproducibility_manifest_path=manifest,
            reproducibility_acceptance_path=acceptance,
            reproducibility_package_doc_path=package_doc,
            goal_audit_path=goal_audit,
            goal_audit_manifest_path=goal_manifest,
            git_status_lines=(" M plan.md", "?? data/new.csv"),
            scan_dirs=(scan_dir,),
        )
        by_category = {row["category_id"]: row for row in rows}

        assert by_category["reproducibility_manifest_scope"]["status"] == (
            "blocked_scaffold_only_manifest_scope"
        )
        assert by_category["git_worktree_state"]["status"] == "blocked_dirty_worktree"
        assert by_category["untracked_required_artifact_risk"]["status"] == (
            "blocked_untracked_reproducibility_artifacts"
        )
        assert by_category["validation_command_ladder"]["status"] == (
            "ready_for_review_command_ladder_present"
        )
        assert by_category["runtime_cloned_repo_import_boundary"]["status"] == (
            "ready_for_review_no_cloned_repo_runtime_imports"
        )
        assert "goal_manifest_blocks_final=true" in (
            by_category["clean_checkout_execution_scope"]["status_detail"]
        )
        assert goal_manifest.as_posix() in (
            by_category["clean_checkout_execution_scope"]["evidence_paths"]
        )

    print("PASS: reproducibility review rows handle fixture state")


def test_reproducibility_review_detects_cloned_repo_imports() -> None:
    """Runtime cloned_repo imports should block the review row."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = root / "reproducibility_manifest.json"
        package_doc = root / "reproducibility_package.md"
        goal_audit = root / "goal.md"
        goal_manifest = root / "goal.json"
        acceptance = root / "reproducibility_acceptance.json"
        scan_dir = root / "src"
        scan_dir.mkdir()
        (scan_dir / "bad.py").write_text("from cloned_repo.example import x\n", encoding="utf-8")
        manifest.write_text(
            json.dumps({"scope": "final", "commands": ["cmd"], "validation_commands": ["test"]}),
            encoding="utf-8",
        )
        package_doc.write_text("package\n", encoding="utf-8")
        goal_audit.write_text("Final-study ready: `false`\n", encoding="utf-8")
        goal_manifest.write_text(
            json.dumps({"final_study_ready": False, "can_mark_complete": False}),
            encoding="utf-8",
        )

        rows = build_reproducibility_review_rows(
            reproducibility_manifest_path=manifest,
            reproducibility_acceptance_path=acceptance,
            reproducibility_package_doc_path=package_doc,
            goal_audit_path=goal_audit,
            goal_audit_manifest_path=goal_manifest,
            git_status_lines=(),
            scan_dirs=(scan_dir,),
        )
        by_category = {row["category_id"]: row for row in rows}

        assert by_category["runtime_cloned_repo_import_boundary"]["status"] == (
            "blocked_runtime_cloned_repo_imports"
        )
        assert "bad.py:1" in by_category["runtime_cloned_repo_import_boundary"][
            "status_detail"
        ]

    print("PASS: reproducibility review detects cloned_repo imports")


def test_reproducibility_review_records_clean_checkout_commit_match() -> None:
    """The clean-checkout row should expose the smoke source commit relation."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = root / "reproducibility_manifest.json"
        package_doc = root / "reproducibility_package.md"
        goal_audit = root / "goal.md"
        goal_manifest = root / "goal.json"
        clean_checkout = root / "clean_checkout.json"
        acceptance = root / "reproducibility_acceptance.json"
        scan_dir = root / "src"
        scan_dir.mkdir()
        (scan_dir / "ok.py").write_text("import os\n", encoding="utf-8")
        manifest.write_text(
            json.dumps(
                {
                    "scope": "scaffold-only test package",
                    "commands": ["cmd"],
                    "validation_commands": ["test"],
                }
            ),
            encoding="utf-8",
        )
        package_doc.write_text("This scaffold package is not final.\n", encoding="utf-8")
        goal_audit.write_text("Final-study ready: `false`\n", encoding="utf-8")
        goal_manifest.write_text(
            json.dumps({"final_study_ready": False, "can_mark_complete": False}),
            encoding="utf-8",
        )
        review_head = packet_module._git_head_commit()
        clean_checkout.write_text(
            json.dumps(
                {
                    "result_scope": "clean_checkout_source_tree_smoke_not_formal_acceptance",
                    "command_count": 1,
                    "passed_count": 1,
                    "failed_count": 0,
                    "smoke_passed": True,
                    "clean_checkout_test_performed": True,
                    "full_clean_environment_tested": False,
                    "source": {
                        "source_commit": review_head,
                    },
                }
            ),
            encoding="utf-8",
        )

        rows = build_reproducibility_review_rows(
            reproducibility_manifest_path=manifest,
            reproducibility_acceptance_path=acceptance,
            reproducibility_package_doc_path=package_doc,
            goal_audit_path=goal_audit,
            goal_audit_manifest_path=goal_manifest,
            clean_checkout_smoke_manifest_path=clean_checkout,
            git_status_lines=(),
            scan_dirs=(scan_dir,),
        )
        by_category = {row["category_id"]: row for row in rows}
        detail = by_category["bounded_clean_checkout_smoke"]["status_detail"]

        assert f"source_commit={review_head}" in detail
        assert f"review_git_head_commit={review_head}" in detail
        assert "matches_review_head=true" in detail
        assert "source_commit_relation_to_review_head=matches_review_head" in detail
        assert "source_commit_lag_count=0" in detail
        assert "source_commit_reachable_from_review_head=true" in detail

    print("PASS: reproducibility review records clean-checkout commit match")


def test_reproducibility_review_records_clean_checkout_ancestor_relation() -> None:
    """Committed smoke evidence can honestly reference an earlier source commit."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = root / "reproducibility_manifest.json"
        package_doc = root / "reproducibility_package.md"
        goal_audit = root / "goal.md"
        goal_manifest = root / "goal.json"
        clean_checkout = root / "clean_checkout.json"
        acceptance = root / "reproducibility_acceptance.json"
        scan_dir = root / "src"
        scan_dir.mkdir()
        (scan_dir / "ok.py").write_text("import os\n", encoding="utf-8")
        manifest.write_text(
            json.dumps(
                {
                    "scope": "scaffold-only test package",
                    "commands": ["cmd"],
                    "validation_commands": ["test"],
                }
            ),
            encoding="utf-8",
        )
        package_doc.write_text("This scaffold package is not final.\n", encoding="utf-8")
        goal_audit.write_text("Final-study ready: `false`\n", encoding="utf-8")
        goal_manifest.write_text(
            json.dumps({"final_study_ready": False, "can_mark_complete": False}),
            encoding="utf-8",
        )
        clean_checkout.write_text(
            json.dumps(
                {
                    "result_scope": "clean_checkout_source_tree_smoke_not_formal_acceptance",
                    "command_count": 1,
                    "passed_count": 1,
                    "failed_count": 0,
                    "smoke_passed": True,
                    "clean_checkout_test_performed": True,
                    "full_clean_environment_tested": False,
                    "source": {
                        "source_commit": "source-parent",
                    },
                }
            ),
            encoding="utf-8",
        )
        original_head = packet_module._git_head_commit
        original_relation = packet_module._source_commit_relation_to_review_head

        def fake_relation(source_commit: str, review_head: str) -> tuple[str, int, bool]:
            assert source_commit == "source-parent"
            assert review_head == "review-head"
            return "ancestor_of_review_head", 2, True

        packet_module._git_head_commit = lambda: "review-head"
        packet_module._source_commit_relation_to_review_head = fake_relation
        try:
            rows = build_reproducibility_review_rows(
                reproducibility_manifest_path=manifest,
                reproducibility_acceptance_path=acceptance,
                reproducibility_package_doc_path=package_doc,
                goal_audit_path=goal_audit,
                goal_audit_manifest_path=goal_manifest,
                clean_checkout_smoke_manifest_path=clean_checkout,
                git_status_lines=(),
                scan_dirs=(scan_dir,),
            )
            output = root / "reproducibility_review.csv"
            manifest_output = root / "reproducibility_review_manifest.json"
            value = write_reproducibility_review_packet(
                rows=rows,
                output_path=output,
                manifest_path=manifest_output,
                reproducibility_manifest_path=manifest,
                reproducibility_acceptance_path=acceptance,
                goal_audit_manifest_path=goal_manifest,
                clean_checkout_smoke_manifest_path=clean_checkout,
                git_status_lines=(),
                scan_dirs=(scan_dir,),
            )
        finally:
            packet_module._git_head_commit = original_head
            packet_module._source_commit_relation_to_review_head = original_relation

        by_category = {row["category_id"]: row for row in rows}
        detail = by_category["bounded_clean_checkout_smoke"]["status_detail"]

        assert "source_commit=source-parent" in detail
        assert "review_git_head_commit=review-head" in detail
        assert "matches_review_head=false" in detail
        assert (
            "source_commit_relation_to_review_head=ancestor_of_review_head" in detail
        )
        assert "source_commit_lag_count=2" in detail
        assert "source_commit_reachable_from_review_head=true" in detail
        assert value["clean_checkout_smoke_matches_review_head"] is False
        assert (
            value["clean_checkout_smoke_source_commit_relation_to_review_head"]
            == "ancestor_of_review_head"
        )
        assert value["clean_checkout_smoke_source_commit_lag_count"] == 2
        assert (
            value["clean_checkout_smoke_source_commit_reachable_from_review_head"]
            is True
        )

    print("PASS: reproducibility review records clean-checkout ancestor relation")


def test_reproducibility_review_preserves_clean_checkout_freshness_snapshot() -> None:
    """Writer should not churn solely because the packaging commit moved."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = root / "reproducibility_manifest.json"
        package_doc = root / "reproducibility_package.md"
        goal_audit = root / "goal.md"
        goal_manifest = root / "goal.json"
        clean_checkout = root / "clean_checkout.json"
        acceptance = root / "reproducibility_acceptance.json"
        output = root / "reproducibility_review.csv"
        manifest_output = root / "reproducibility_review_manifest.json"
        scan_dir = root / "src"
        scan_dir.mkdir()
        (scan_dir / "ok.py").write_text("import os\n", encoding="utf-8")
        manifest.write_text(
            json.dumps(
                {
                    "scope": "scaffold-only test package",
                    "commands": ["cmd"],
                    "validation_commands": ["test"],
                }
            ),
            encoding="utf-8",
        )
        package_doc.write_text("This scaffold package is not final.\n", encoding="utf-8")
        goal_audit.write_text("Final-study ready: `false`\n", encoding="utf-8")
        goal_manifest.write_text(
            json.dumps({"final_study_ready": False, "can_mark_complete": False}),
            encoding="utf-8",
        )
        clean_checkout.write_text(
            json.dumps(
                {
                    "result_scope": "clean_checkout_source_tree_smoke_not_formal_acceptance",
                    "command_count": 1,
                    "passed_count": 1,
                    "failed_count": 0,
                    "smoke_passed": True,
                    "clean_checkout_test_performed": True,
                    "full_clean_environment_tested": True,
                    "artifact_regeneration_tested": True,
                    "source": {
                        "source_commit": "source-parent",
                    },
                }
            ),
            encoding="utf-8",
        )
        original_head = packet_module._git_head_commit
        original_relation = packet_module._source_commit_relation_to_review_head

        def first_relation(
            source_commit: str, review_head: str
        ) -> tuple[str, int, bool]:
            assert source_commit == "source-parent"
            assert review_head == "review-head-1"
            return "ancestor_of_review_head", 2, True

        def second_relation(
            source_commit: str, review_head: str
        ) -> tuple[str, int, bool]:
            assert source_commit == "source-parent"
            assert review_head == "review-head-2"
            return "ancestor_of_review_head", 3, True

        try:
            packet_module._git_head_commit = lambda: "review-head-1"
            packet_module._source_commit_relation_to_review_head = first_relation
            rows = build_reproducibility_review_rows(
                reproducibility_manifest_path=manifest,
                reproducibility_acceptance_path=acceptance,
                reproducibility_package_doc_path=package_doc,
                goal_audit_path=goal_audit,
                goal_audit_manifest_path=goal_manifest,
                clean_checkout_smoke_manifest_path=clean_checkout,
                git_status_lines=(),
                scan_dirs=(scan_dir,),
            )
            write_reproducibility_review_packet(
                rows=rows,
                output_path=output,
                manifest_path=manifest_output,
                reproducibility_manifest_path=manifest,
                reproducibility_acceptance_path=acceptance,
                goal_audit_manifest_path=goal_manifest,
                clean_checkout_smoke_manifest_path=clean_checkout,
                git_status_lines=(),
                scan_dirs=(scan_dir,),
            )

            packet_module._git_head_commit = lambda: "review-head-2"
            packet_module._source_commit_relation_to_review_head = second_relation
            rows = build_reproducibility_review_rows(
                reproducibility_manifest_path=manifest,
                reproducibility_acceptance_path=acceptance,
                reproducibility_package_doc_path=package_doc,
                goal_audit_path=goal_audit,
                goal_audit_manifest_path=goal_manifest,
                clean_checkout_smoke_manifest_path=clean_checkout,
                git_status_lines=(),
                scan_dirs=(scan_dir,),
            )
            value = write_reproducibility_review_packet(
                rows=rows,
                output_path=output,
                manifest_path=manifest_output,
                reproducibility_manifest_path=manifest,
                reproducibility_acceptance_path=acceptance,
                goal_audit_manifest_path=goal_manifest,
                clean_checkout_smoke_manifest_path=clean_checkout,
                git_status_lines=(),
                scan_dirs=(scan_dir,),
            )
        finally:
            packet_module._git_head_commit = original_head
            packet_module._source_commit_relation_to_review_head = original_relation

        with output.open("r", encoding="utf-8", newline="") as handle:
            written_rows = list(csv.DictReader(handle))
        by_category = {row["category_id"]: row for row in written_rows}
        detail = by_category["bounded_clean_checkout_smoke"]["status_detail"]

        assert value["review_git_head_commit"] == "review-head-1"
        assert value["clean_checkout_smoke_source_commit_lag_count"] == 2
        assert "review_git_head_commit=review-head-1" in detail
        assert "source_commit_lag_count=2" in detail
        assert "review_git_head_commit=review-head-2" not in detail
        assert "source_commit_lag_count=3" not in detail

    print("PASS: reproducibility review preserves clean-checkout freshness snapshot")


def test_write_reproducibility_review_packet_outputs_csv_and_manifest() -> None:
    """Writer should emit stable CSV fields and non-acceptance manifest."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        missing_clean_checkout = root / "missing_clean_checkout.json"
        goal_manifest = root / "goal.json"
        goal_manifest.write_text(
            json.dumps({"final_study_ready": False, "can_mark_complete": False}),
            encoding="utf-8",
        )
        rows = build_reproducibility_review_rows(
            clean_checkout_smoke_manifest_path=missing_clean_checkout,
            goal_audit_manifest_path=goal_manifest,
            git_status_lines=(),
        )
        output = root / "reproducibility_review.csv"
        manifest = root / "reproducibility_review_manifest.json"
        value = write_reproducibility_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            goal_audit_manifest_path=goal_manifest,
            clean_checkout_smoke_manifest_path=missing_clean_checkout,
            git_status_lines=(),
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == REPRODUCIBILITY_REVIEW_COLUMNS
        written_manifest = json.loads(manifest.read_text(encoding="utf-8"))

        assert len(written_rows) == 8
        assert value["acceptance_ready"] is False
        assert value["publication_ready"] is False
        assert value["clean_checkout_test_performed"] is False
        assert value["clean_checkout_smoke_present"] is False
        assert value["clean_checkout_smoke_source_commit"] == ""
        assert value["clean_checkout_smoke_matches_review_head"] is False
        assert (
            value["clean_checkout_smoke_source_commit_relation_to_review_head"]
            == "unknown"
        )
        assert value["clean_checkout_smoke_source_commit_lag_count"] is None
        assert (
            value["clean_checkout_smoke_source_commit_reachable_from_review_head"]
            is False
        )
        assert isinstance(value["review_git_head_commit"], str)
        assert value["acceptance_gate_closure_candidate_count"] == 0
        assert written_manifest["row_count"] == 8
        assert written_manifest["input_artifact_paths"][
            "current_goal_completion_audit_manifest"
        ] == goal_manifest.as_posix()
        assert "does not prove full clean-environment reproduction" in written_manifest[
            "claim_boundary"
        ]

    print("PASS: reproducibility review packet writer emits CSV and manifest")


def test_writer_captures_git_status_before_writing_outputs() -> None:
    """Manifest Git counts should not include the CSV written by the writer."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        output = root / "reproducibility_review.csv"
        manifest = root / "reproducibility_review_manifest.json"
        scan_dir = root / "src"
        scan_dir.mkdir()
        rows = [
            {
                "category_id": "git_worktree_state",
                "status": "ready_for_review_clean_worktree",
            }
        ]
        original_git_status_lines = packet_module._git_status_lines

        def fake_git_status_lines() -> list[str]:
            return [" M reproducibility_review.csv"] if output.exists() else []

        packet_module._git_status_lines = fake_git_status_lines
        try:
            value = packet_module.write_reproducibility_review_packet(
                rows=rows,
                output_path=output,
                manifest_path=manifest,
                clean_checkout_smoke_manifest_path=root / "missing_clean_checkout.json",
                scan_dirs=(scan_dir,),
            )
        finally:
            packet_module._git_status_lines = original_git_status_lines

        assert output.exists()
        assert value["git_status_line_count"] == 0
        assert value["git_modified_or_staged_count"] == 0

    print("PASS: writer captures git status before writing outputs")


if __name__ == "__main__":
    test_reproducibility_review_rows_are_conservative()
    test_reproducibility_review_rows_handle_fixture_state()
    test_reproducibility_review_detects_cloned_repo_imports()
    test_reproducibility_review_records_clean_checkout_commit_match()
    test_reproducibility_review_records_clean_checkout_ancestor_relation()
    test_reproducibility_review_preserves_clean_checkout_freshness_snapshot()
    test_write_reproducibility_review_packet_outputs_csv_and_manifest()
    test_writer_captures_git_status_before_writing_outputs()
    print("\n=== REALWORLD REPRODUCIBILITY REVIEW PACKET TESTS PASSED ===")
