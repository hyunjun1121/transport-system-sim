"""Tests for bounded reproducibility smoke evidence."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.reproducibility_smoke import (  # noqa: E402
    CLEAN_CHECKOUT_MINIMAL_SMOKE_COMMANDS,
    REPRODUCIBILITY_SMOKE_SCOPE,
    SmokeCommand,
    SmokeCommandResult,
    build_reproducibility_smoke_manifest,
    run_smoke_command,
    run_reproducibility_smoke,
    summarize_reproducibility_smoke,
    write_reproducibility_smoke_outputs,
)


def test_smoke_manifest_never_accepts_reproducibility_gate() -> None:
    """Even a passing smoke manifest must stay non-acceptance evidence."""

    result = _result("fixture_pass", passed=True)
    manifest = build_reproducibility_smoke_manifest(results=(result,))

    assert manifest["result_scope"] == REPRODUCIBILITY_SMOKE_SCOPE
    assert manifest["smoke_passed"] is True
    assert manifest["acceptance_ready"] is False
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["clean_checkout_test_performed"] is False
    assert "not a fresh-clone or clean-checkout reproduction" in manifest[
        "claim_boundary"
    ]

    print("PASS: smoke manifest never accepts reproducibility gate")


def test_write_smoke_outputs_and_summary() -> None:
    """Writer should emit JSON manifest, JSONL log, and markdown doc."""

    results = (_result("fixture_pass", passed=True), _result("fixture_fail", passed=False))

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest_path = root / "manifest.json"
        log_path = root / "log.jsonl"
        doc_path = root / "smoke.md"
        manifest = write_reproducibility_smoke_outputs(
            results=results,
            manifest_path=manifest_path,
            log_path=log_path,
            doc_path=doc_path,
        )
        summary = summarize_reproducibility_smoke(manifest_path)

        assert manifest_path.exists()
        assert log_path.exists()
        assert doc_path.exists()
        assert len(log_path.read_text(encoding="utf-8").splitlines()) == 2
        written = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert written["failed_count"] == 1
        assert manifest["smoke_passed"] is False
        assert summary["manifest_present"] is True
        assert summary["failed_count"] == 1
        assert summary["can_mark_complete"] is False
        assert "Reproducibility Smoke Run" in doc_path.read_text(encoding="utf-8")

    print("PASS: smoke outputs and summary are written")


def test_missing_smoke_summary_is_blocked() -> None:
    """Missing smoke evidence should become an explicit blocker."""

    with TemporaryDirectory() as tmp:
        summary = summarize_reproducibility_smoke(Path(tmp) / "missing.json")

    assert summary["manifest_present"] is False
    assert summary["smoke_passed"] is False
    assert summary["remaining_blockers"]

    print("PASS: missing smoke summary is blocked")


def test_run_reproducibility_smoke_subset_records_command_status() -> None:
    """A tiny command subset should record pass and fail results."""

    commands = (
        SmokeCommand(
            "tiny_pass",
            "Tiny passing command",
            ("{python}", "-c", "print('ok')"),
            timeout_sec=30,
        ),
        SmokeCommand(
            "tiny_fail",
            "Tiny failing command",
            ("{python}", "-c", "import sys; sys.exit(2)"),
            timeout_sec=30,
        ),
    )
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = run_reproducibility_smoke(
            commands=commands,
            manifest_path=root / "manifest.json",
            log_path=root / "log.jsonl",
            doc_path=root / "smoke.md",
        )

    assert manifest["command_count"] == 2
    assert manifest["passed_count"] == 1
    assert manifest["failed_count"] == 1
    assert manifest["smoke_passed"] is False
    assert manifest["failed_command_ids"] == ["tiny_fail"]

    print("PASS: reproducibility smoke subset records command status")


def test_run_smoke_command_timeout_is_bounded() -> None:
    """Timed-out commands should return a timeout record instead of hanging."""

    command = SmokeCommand(
        "tiny_timeout",
        "Tiny timeout command",
        ("{python}", "-c", "import time; print('started', flush=True); time.sleep(30)"),
        timeout_sec=1,
    )
    result = run_smoke_command(command)

    assert result.command_id == "tiny_timeout"
    assert result.status == "timeout"
    assert result.returncode is None
    assert result.passed is False
    assert result.duration_sec < 10
    assert "started" in result.stdout_tail

    print("PASS: reproducibility smoke timeout returns bounded result")


def test_clean_checkout_minimal_profile_is_bounded() -> None:
    """The clean-checkout profile should stay small enough for clone smoke."""

    ids = {command.command_id for command in CLEAN_CHECKOUT_MINIMAL_SMOKE_COMMANDS}

    assert len(CLEAN_CHECKOUT_MINIMAL_SMOKE_COMMANDS) == 9
    assert "test_clean_checkout_smoke" in ids
    assert "test_publication_readiness" in ids
    assert "formal_acceptance_package_audit" in ids
    assert "final_study_readiness_audit" in ids
    assert "runtime_cloned_repo_import_boundary" in ids

    print("PASS: clean-checkout minimal smoke profile is bounded")


def _result(command_id: str, *, passed: bool) -> SmokeCommandResult:
    return SmokeCommandResult(
        command_id=command_id,
        label=command_id,
        kind="fixture",
        args=(),
        status="passed" if passed else "failed",
        returncode=0 if passed else 1,
        passed=passed,
        duration_sec=0.01,
        stdout_tail="",
        stderr_tail="",
    )


if __name__ == "__main__":
    test_smoke_manifest_never_accepts_reproducibility_gate()
    test_write_smoke_outputs_and_summary()
    test_missing_smoke_summary_is_blocked()
    test_run_reproducibility_smoke_subset_records_command_status()
    test_run_smoke_command_timeout_is_bounded()
    test_clean_checkout_minimal_profile_is_bounded()
    print("\n=== REALWORLD REPRODUCIBILITY SMOKE TESTS PASSED ===")
