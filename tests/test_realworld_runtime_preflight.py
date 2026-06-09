"""Tests for runtime preflight manifests."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.runtime_preflight import (  # noqa: E402
    PackageImportResult,
    RUNTIME_PREFLIGHT_SCOPE,
    build_runtime_preflight_manifest,
    runtime_preflight_paths,
    write_runtime_preflight_outputs,
)


def test_cpu_runtime_preflight_is_environment_evidence_only() -> None:
    manifest = build_runtime_preflight_manifest(
        phase_id="phase8_compact_probe",
        execution_scope="compact",
        git_status=_cmd_ok("## main\n M plan.md"),
        git_head=_cmd_ok("abc123"),
        pip_check=_cmd_ok("No broken requirements found."),
        dirty_worktree=_dirty_ok(),
        package_results=(_pkg_ok("networkx"),),
        include_gpu=False,
    )

    assert manifest["runtime_preflight_ready"] is True
    assert manifest["cpu_simulation_default"] is True
    assert manifest["simulation_engine_gpu_accelerated"] is False
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["remaining_blockers"] == []

    print("PASS: CPU runtime preflight is environment evidence only")


def test_dirty_manifest_is_required() -> None:
    manifest = build_runtime_preflight_manifest(
        phase_id="phase8_compact_probe",
        git_status=_cmd_ok("## main"),
        git_head=_cmd_ok("abc123"),
        pip_check=_cmd_ok("No broken requirements found."),
        dirty_worktree={"manifest_present": False},
        package_results=(_pkg_ok("networkx"),),
    )

    assert manifest["runtime_preflight_ready"] is False
    assert "dirty worktree classification manifest is absent" in manifest["remaining_blockers"]

    print("PASS: dirty manifest is required")


def test_gpu_scope_requires_nvidia_and_smoke_command_metadata() -> None:
    manifest = build_runtime_preflight_manifest(
        phase_id="phase10_gpu_ml",
        execution_scope="gpu_ml",
        git_status=_cmd_ok("## main"),
        git_head=_cmd_ok("abc123"),
        pip_check=_cmd_ok("No broken requirements found."),
        dirty_worktree=_dirty_ok(),
        package_results=(_pkg_ok("xgboost"),),
        include_gpu=True,
        nvidia_smi=_cmd_fail("nvidia-smi failed"),
        gpu_smoke_command="",
    )

    assert manifest["runtime_preflight_ready"] is False
    assert "GPU scope requested but nvidia-smi did not pass" in manifest["remaining_blockers"]
    assert (
        "GPU scope requested but no GPU smoke command was recorded"
        in manifest["remaining_blockers"]
    )
    assert manifest["simulation_engine_gpu_accelerated"] is False

    print("PASS: GPU scope requires nvidia-smi and smoke command metadata")


def test_runtime_preflight_outputs_are_written() -> None:
    manifest = build_runtime_preflight_manifest(
        phase_id="phase8 compact probe",
        git_status=_cmd_ok("## main"),
        git_head=_cmd_ok("abc123"),
        pip_check=_cmd_ok("No broken requirements found."),
        dirty_worktree=_dirty_ok(),
        package_results=(_pkg_ok("networkx"),),
    )

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        written = write_runtime_preflight_outputs(
            manifest=manifest,
            manifest_path=root / "runtime.json",
            log_path=root / "runtime.jsonl",
            doc_path=root / "runtime.md",
        )
        loaded = json.loads((root / "runtime.json").read_text(encoding="utf-8"))
        log = (root / "runtime.jsonl").read_text(encoding="utf-8")
        doc = (root / "runtime.md").read_text(encoding="utf-8")

    assert written["claim_boundary"] == RUNTIME_PREFLIGHT_SCOPE
    assert loaded["runtime_preflight_ready"] is True
    assert "Runtime Preflight Manifest" in doc
    assert "not close publication or final-study gates" in doc
    assert "package_import" in log

    print("PASS: runtime preflight outputs are written")


def test_runtime_preflight_paths_are_phase_scoped() -> None:
    paths = runtime_preflight_paths(phase_id="phase8 compact/probe")

    assert paths["manifest"].as_posix().endswith(
        "data/validation/runtime_preflight/phase8_compact_probe_runtime_preflight_manifest.json"
    )
    assert paths["doc"].as_posix().endswith(
        "docs/runtime_preflight/phase8_compact_probe_runtime_preflight.md"
    )

    print("PASS: runtime preflight paths are phase scoped")


def test_cli_help_renders() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "write_runtime_preflight_manifest.py"),
            "--help",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "--phase-id" in result.stdout
    assert "--include-gpu" in result.stdout
    assert "--gpu-smoke-command" in result.stdout

    print("PASS: runtime preflight CLI help renders")


def _cmd_ok(stdout: str) -> dict[str, object]:
    return {
        "command": ["fixture"],
        "status": "passed",
        "returncode": 0,
        "duration_sec": 0.01,
        "stdout_tail": stdout,
        "stderr_tail": "",
    }


def _cmd_fail(stderr: str) -> dict[str, object]:
    return {
        "command": ["fixture"],
        "status": "failed",
        "returncode": 1,
        "duration_sec": 0.01,
        "stdout_tail": "",
        "stderr_tail": stderr,
    }


def _dirty_ok() -> dict[str, object]:
    return {
        "manifest_present": True,
        "sha256": "sha256:" + "0" * 64,
        "dirty_path_count": 1,
        "unclassified_path_count": 0,
        "new_generated_output_allowed": False,
        "final_study_ready": False,
    }


def _pkg_ok(name: str) -> PackageImportResult:
    return PackageImportResult(
        distribution_name=name,
        import_name=name,
        package_version="1.0",
        import_status="imported",
        message="fixture",
    )


if __name__ == "__main__":
    test_cpu_runtime_preflight_is_environment_evidence_only()
    test_dirty_manifest_is_required()
    test_gpu_scope_requires_nvidia_and_smoke_command_metadata()
    test_runtime_preflight_outputs_are_written()
    test_runtime_preflight_paths_are_phase_scoped()
    test_cli_help_renders()
    print("\n=== REALWORLD RUNTIME PREFLIGHT TESTS PASSED ===")
