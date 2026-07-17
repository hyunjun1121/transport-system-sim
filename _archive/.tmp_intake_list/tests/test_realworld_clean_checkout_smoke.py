"""Tests for bounded clean-checkout smoke evidence."""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.clean_checkout_smoke import (  # noqa: E402
    ARTIFACT_REGENERATION_COMMANDS,
    ARTIFACT_REGENERATION_SCOPE,
    CLEAN_CHECKOUT_SMOKE_SCOPE,
    CleanCheckoutStepResult,
    _prepare_checkout_dir,
    _filter_source_status_lines,
    _remove_if_safe,
    build_clean_checkout_smoke_manifest,
    summarize_clean_checkout_smoke,
    write_clean_checkout_smoke_outputs,
)


def test_clean_checkout_smoke_manifest_never_accepts_gate() -> None:
    """Passing clean-checkout smoke must remain non-acceptance evidence."""

    manifest = build_clean_checkout_smoke_manifest(
        source_repo="repo",
        source_commit="abc123",
        source_status_lines=(),
        checkout_dir="checkout",
        checkout_retained=False,
        python_executable="python",
        outer_steps=(
            _step("git_clone_source_tree", passed=True),
            _step("run_reproducibility_smoke_in_clean_checkout", passed=True),
        ),
        inner_manifest={
            "result_scope": "current_worktree_smoke_not_clean_checkout",
            "command_count": 2,
            "passed_count": 2,
            "failed_count": 0,
            "smoke_passed": True,
            "failed_command_ids": [],
        },
    )

    assert manifest["result_scope"] == CLEAN_CHECKOUT_SMOKE_SCOPE
    assert manifest["smoke_passed"] is True
    assert manifest["acceptance_ready"] is False
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["clean_checkout_test_performed"] is True
    assert manifest["full_clean_environment_tested"] is False
    assert manifest["dependency_install_tested"] is False
    assert manifest["formal_acceptance_created"] is False
    assert manifest["source"]["source_git_status_lines"] == []

    print("PASS: clean-checkout smoke manifest never accepts gate")


def test_clean_checkout_smoke_manifest_records_dependency_install_scope() -> None:
    """Dependency-install smoke should remain non-acceptance evidence."""

    manifest = build_clean_checkout_smoke_manifest(
        source_repo="repo",
        source_commit="abc123",
        source_status_lines=(),
        checkout_dir="checkout",
        checkout_retained=False,
        python_executable="python",
        install_dependencies=True,
        outer_steps=(
            _step("git_clone_source_tree", passed=True),
            _step("git_checkout_source_commit", passed=True),
            _step("create_clean_checkout_venv", passed=True),
            _step("upgrade_clean_checkout_pip", passed=True),
            _step("install_clean_checkout_requirements", passed=True),
            _step("run_reproducibility_smoke_in_clean_checkout", passed=True),
        ),
        inner_manifest={
            "result_scope": "current_worktree_smoke_not_clean_checkout",
            "command_count": 2,
            "passed_count": 2,
            "failed_count": 0,
            "smoke_passed": True,
            "failed_command_ids": [],
        },
    )

    assert manifest["smoke_passed"] is True
    assert manifest["install_dependencies_requested"] is True
    assert manifest["dependency_install_tested"] is True
    assert manifest["full_clean_environment_tested"] is True
    assert manifest["artifact_regeneration_tested"] is False
    assert manifest["acceptance_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["environment_scope"] == (
        "clean_source_checkout_fresh_venv_with_dependency_install"
    )

    print("PASS: dependency-install clean-checkout smoke remains non-acceptance")


def test_clean_checkout_smoke_manifest_records_artifact_regeneration_scope() -> None:
    """Bounded artifact regeneration should be explicit non-acceptance evidence."""

    manifest = build_clean_checkout_smoke_manifest(
        source_repo="repo",
        source_commit="abc123",
        source_status_lines=(),
        checkout_dir="checkout",
        checkout_retained=False,
        python_executable="python",
        install_dependencies=True,
        artifact_regeneration=True,
        outer_steps=(
            _step("git_clone_source_tree", passed=True),
            _step("git_checkout_source_commit", passed=True),
            _step("create_clean_checkout_venv", passed=True),
            _step("upgrade_clean_checkout_pip", passed=True),
            _step("install_clean_checkout_requirements", passed=True),
            _step("run_reproducibility_smoke_in_clean_checkout", passed=True),
            *(
                _step(step_id, passed=True)
                for step_id, _, _ in ARTIFACT_REGENERATION_COMMANDS
            ),
        ),
        inner_manifest={
            "result_scope": "current_worktree_smoke_not_clean_checkout",
            "command_count": 2,
            "passed_count": 2,
            "failed_count": 0,
            "smoke_passed": True,
            "failed_command_ids": [],
        },
    )

    assert manifest["smoke_passed"] is True
    assert manifest["artifact_regeneration_requested"] is True
    assert manifest["artifact_regeneration_tested"] is True
    assert manifest["artifact_regeneration_scope"] == ARTIFACT_REGENERATION_SCOPE
    assert manifest["artifact_regeneration_step_ids"] == [
        step_id for step_id, _, _ in ARTIFACT_REGENERATION_COMMANDS
    ]
    assert manifest["acceptance_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert not any(
        action.startswith("run bounded clean-checkout artifact-regeneration")
        for action in manifest["required_actions"]
    )

    print("PASS: artifact-regeneration clean-checkout smoke remains non-acceptance")


def test_clean_checkout_smoke_outputs_and_summary() -> None:
    """Writer should emit manifest, combined JSONL log, and markdown doc."""

    manifest = build_clean_checkout_smoke_manifest(
        source_repo="repo",
        source_commit="abc123",
        source_status_lines=(" M plan.md",),
        checkout_dir="checkout",
        checkout_retained=False,
        python_executable="python",
        outer_steps=(
            _step("git_clone_source_tree", passed=True),
            _step("run_reproducibility_smoke_in_clean_checkout", passed=True),
        ),
        inner_manifest={
            "result_scope": "current_worktree_smoke_not_clean_checkout",
            "command_count": 1,
            "passed_count": 1,
            "failed_count": 0,
            "smoke_passed": True,
            "failed_command_ids": [],
        },
    )
    inner_log = json.dumps({"command_id": "inner", "passed": True})

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest_path = root / "manifest.json"
        log_path = root / "log.jsonl"
        doc_path = root / "smoke.md"
        write_clean_checkout_smoke_outputs(
            manifest=manifest,
            outer_steps=(_step("git_clone_source_tree", passed=True),),
            inner_log_text=inner_log,
            manifest_path=manifest_path,
            log_path=log_path,
            doc_path=doc_path,
        )
        summary = summarize_clean_checkout_smoke(manifest_path)

        assert manifest_path.exists()
        assert log_path.exists()
        assert doc_path.exists()
        assert summary["source_status_lines"] == [" M plan.md"]
        assert len(log_path.read_text(encoding="utf-8").splitlines()) == 2
        assert summary["manifest_present"] is True
        assert summary["smoke_passed"] is True
        assert summary["clean_checkout_test_performed"] is True
        assert summary["full_clean_environment_tested"] is False
        assert summary["artifact_regeneration_tested"] is False
        assert "Clean-Checkout Reproducibility Smoke" in doc_path.read_text(
            encoding="utf-8"
        )

    print("PASS: clean-checkout smoke outputs and summary are written")


def test_clean_checkout_source_status_ignores_own_outputs() -> None:
    filtered = _filter_source_status_lines(
        (
            "M data/validation/clean_checkout_reproducibility_smoke_log.jsonl",
            " M data/validation/clean_checkout_reproducibility_smoke_manifest.json",
            " M data/validation/clean_checkout_reproducibility_smoke_log.jsonl",
            " M docs/clean_checkout_reproducibility_smoke.md",
            " M plan.md",
        )
    )

    assert filtered == [" M plan.md"]

    print("PASS: clean-checkout smoke ignores only its own output files")


def test_missing_clean_checkout_smoke_summary_is_blocked() -> None:
    """Missing clean-checkout smoke should become an explicit blocker."""

    with TemporaryDirectory() as tmp:
        summary = summarize_clean_checkout_smoke(Path(tmp) / "missing.json")

    assert summary["manifest_present"] is False
    assert summary["smoke_passed"] is False
    assert summary["clean_checkout_test_performed"] is False
    assert summary["remaining_blockers"]

    print("PASS: missing clean-checkout smoke summary is blocked")


def test_clean_checkout_cleanup_handles_readonly_git_files() -> None:
    """Explicit checkout-parent cleanup should handle read-only Git files."""

    with TemporaryDirectory() as tmp:
        checkout_dir = Path(tmp) / "transport-system-sim-clean-checkout"
        object_dir = checkout_dir / ".git" / "objects" / "00"
        object_dir.mkdir(parents=True)
        readonly_object = object_dir / "fixture-object"
        readonly_object.write_text("object", encoding="utf-8")
        readonly_object.chmod(stat.S_IREAD)

        _remove_if_safe(checkout_dir)

        assert not checkout_dir.exists()

    print("PASS: clean-checkout cleanup handles read-only Git files")


def test_clean_checkout_prepare_replaces_readonly_existing_checkout() -> None:
    """Preparing a fixed checkout parent should replace stale read-only trees."""

    with TemporaryDirectory() as tmp:
        parent = Path(tmp)
        checkout_dir = parent / "transport-system-sim-clean-checkout"
        object_dir = checkout_dir / ".git" / "objects" / "00"
        object_dir.mkdir(parents=True)
        readonly_object = object_dir / "fixture-object"
        readonly_object.write_text("object", encoding="utf-8")
        readonly_object.chmod(stat.S_IREAD)

        prepared_dir, cleanup = _prepare_checkout_dir(
            checkout_parent=parent,
            keep_checkout=False,
        )

        assert prepared_dir == checkout_dir
        assert not checkout_dir.exists()
        cleanup()

    print("PASS: clean-checkout prepare replaces read-only existing checkout")


def _step(step_id: str, *, passed: bool) -> CleanCheckoutStepResult:
    return CleanCheckoutStepResult(
        step_id=step_id,
        label=step_id,
        args=("fixture",),
        cwd=".",
        status="passed" if passed else "failed",
        returncode=0 if passed else 1,
        passed=passed,
        duration_sec=0.01,
        stdout_tail="",
        stderr_tail="",
    )


if __name__ == "__main__":
    test_clean_checkout_smoke_manifest_never_accepts_gate()
    test_clean_checkout_smoke_manifest_records_dependency_install_scope()
    test_clean_checkout_smoke_manifest_records_artifact_regeneration_scope()
    test_clean_checkout_smoke_outputs_and_summary()
    test_clean_checkout_source_status_ignores_own_outputs()
    test_missing_clean_checkout_smoke_summary_is_blocked()
    test_clean_checkout_cleanup_handles_readonly_git_files()
    test_clean_checkout_prepare_replaces_readonly_existing_checkout()
    print("\n=== REALWORLD CLEAN-CHECKOUT SMOKE TESTS PASSED ===")
