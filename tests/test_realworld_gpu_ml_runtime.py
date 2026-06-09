"""Tests for GPU ML runtime preflight guard."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.gpu_ml_runtime import (  # noqa: E402
    GPU_ML_RUNTIME_SCOPE,
    PackageRuntimeResult,
    build_gpu_ml_runtime_manifest,
    run_nvidia_smi,
    write_gpu_ml_runtime_outputs,
)


def test_missing_package_blocks_gpu_claim() -> None:
    manifest = build_gpu_ml_runtime_manifest(
        package_results=(_missing_result("xgboost"),),
        nvidia_smi=_nvidia_ok(),
        pip_check=_pip_ok(),
        packages=("xgboost",),
    )

    assert manifest["can_support_gpu_ml_claim"] is False
    assert manifest["gpu_ml_runtime_passed"] is False
    assert manifest["simulation_correctness_blocked"] is False
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["remaining_blockers"]

    print("PASS: missing package blocks GPU claim")


def test_nvidia_smi_alone_does_not_support_gpu_claim() -> None:
    manifest = build_gpu_ml_runtime_manifest(
        package_results=(),
        nvidia_smi=_nvidia_ok(),
        pip_check=_pip_ok(),
        packages=(),
    )

    assert manifest["nvidia_smi_available"] is True
    assert manifest["can_support_gpu_ml_claim"] is False
    assert "no GPU ML packages were checked" in manifest["remaining_blockers"]

    print("PASS: nvidia-smi alone does not support GPU claim")


def test_gpu_pass_requires_cpu_fallback() -> None:
    manifest = build_gpu_ml_runtime_manifest(
        package_results=(_gpu_without_cpu_result("xgboost"),),
        nvidia_smi=_nvidia_ok(),
        pip_check=_pip_ok(),
        packages=("xgboost",),
    )

    assert manifest["can_support_gpu_ml_claim"] is False
    assert manifest["cpu_fallback_recorded"] is False
    assert any("CPU fallback" in blocker for blocker in manifest["remaining_blockers"])

    print("PASS: GPU pass without CPU fallback blocks claim")


def test_gpu_and_cpu_pass_supports_bounded_gpu_ml_claim_only() -> None:
    manifest = build_gpu_ml_runtime_manifest(
        package_results=(_gpu_and_cpu_result("xgboost"),),
        nvidia_smi=_nvidia_ok(),
        pip_check=_pip_ok(),
        packages=("xgboost",),
    )

    assert manifest["can_support_gpu_ml_claim"] is True
    assert manifest["gpu_ml_runtime_passed"] is True
    assert manifest["simulation_engine_gpu_accelerated"] is False
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["remaining_blockers"] == []

    print("PASS: GPU and CPU pass supports bounded GPU ML claim only")


def test_write_gpu_ml_runtime_outputs() -> None:
    manifest = build_gpu_ml_runtime_manifest(
        package_results=(_missing_result("xgboost"),),
        nvidia_smi=_nvidia_ok(),
        pip_check=_pip_ok(),
        packages=("xgboost",),
    )

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        written = write_gpu_ml_runtime_outputs(
            manifest=manifest,
            manifest_path=root / "gpu.json",
            log_path=root / "gpu.jsonl",
            doc_path=root / "gpu.md",
        )
        loaded = json.loads((root / "gpu.json").read_text(encoding="utf-8"))
        log_lines = (root / "gpu.jsonl").read_text(encoding="utf-8").splitlines()
        doc = (root / "gpu.md").read_text(encoding="utf-8")

    assert written["claim_boundary"] == GPU_ML_RUNTIME_SCOPE
    assert loaded["can_support_gpu_ml_claim"] is False
    assert loaded["outputs"]["manifest"].endswith("gpu.json")
    assert loaded["outputs"]["log"].endswith("gpu.jsonl")
    assert loaded["outputs"]["doc"].endswith("gpu.md")
    assert len(log_lines) >= 4
    assert "GPU ML Runtime Check" in doc
    assert "does not prove the simulator is GPU accelerated" in doc

    print("PASS: GPU ML runtime outputs are written")


def test_run_nvidia_smi_missing_is_bounded() -> None:
    result = run_nvidia_smi(command=("definitely_missing_nvidia_smi_command",))

    assert result["status"] == "missing"
    assert result["returncode"] is None
    assert "not found" in result["stderr_tail"]

    print("PASS: missing nvidia-smi result is bounded")


def test_cli_help_renders() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check_gpu_ml_runtime.py"),
            "--help",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "--package" in result.stdout
    assert "--require-gpu" in result.stdout
    assert "--fail-on-blockers" in result.stdout

    print("PASS: GPU ML runtime CLI help renders")


def test_cli_records_exact_command_arguments() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        requirements = root / "requirements-ml.txt"
        requirements.write_text("# optional ml requirements fixture\n", encoding="utf-8")
        manifest = root / "gpu.json"
        log = root / "gpu.jsonl"
        doc = root / "gpu.md"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_gpu_ml_runtime.py"),
                "--package",
                "definitely_missing_gpu_runtime_package",
                "--requested-device",
                "cuda",
                "--requirements",
                str(requirements),
                "--import-only",
                "--manifest",
                str(manifest),
                "--log",
                str(log),
                "--doc",
                str(doc),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(manifest.read_text(encoding="utf-8"))

    command = payload["command"]
    assert "--requirements" in command
    assert str(requirements) in command
    assert "--import-only" in command
    assert payload["requirements"]["path"] == requirements.as_posix()

    print("PASS: GPU ML runtime CLI records exact command arguments")


def _missing_result(package: str) -> PackageRuntimeResult:
    return PackageRuntimeResult(
        package_name=package,
        package_version="not_installed",
        requested_device="cuda",
        actual_device="unavailable",
        import_status="missing",
        gpu_check_status="not_run_missing_package",
        cpu_fallback_status="not_run_missing_package",
        can_support_gpu_ml_claim=False,
        duration_sec=0.01,
        message="missing fixture",
    )


def _gpu_without_cpu_result(package: str) -> PackageRuntimeResult:
    return PackageRuntimeResult(
        package_name=package,
        package_version="1.0",
        requested_device="cuda",
        actual_device="cuda",
        import_status="imported",
        gpu_check_status="passed",
        cpu_fallback_status="failed",
        can_support_gpu_ml_claim=True,
        duration_sec=0.01,
        message="gpu-only fixture",
    )


def _gpu_and_cpu_result(package: str) -> PackageRuntimeResult:
    return PackageRuntimeResult(
        package_name=package,
        package_version="1.0",
        requested_device="cuda",
        actual_device="cuda",
        import_status="imported",
        gpu_check_status="passed",
        cpu_fallback_status="passed",
        can_support_gpu_ml_claim=True,
        duration_sec=0.01,
        message="gpu+cpu fixture",
    )


def _nvidia_ok() -> dict[str, object]:
    return {
        "status": "available",
        "returncode": 0,
        "stdout_tail": "NVIDIA GeForce RTX 3090",
        "stderr_tail": "",
    }


def _pip_ok() -> dict[str, object]:
    return {
        "status": "passed",
        "returncode": 0,
        "stdout_tail": "No broken requirements found.",
        "stderr_tail": "",
    }


if __name__ == "__main__":
    test_missing_package_blocks_gpu_claim()
    test_nvidia_smi_alone_does_not_support_gpu_claim()
    test_gpu_pass_requires_cpu_fallback()
    test_gpu_and_cpu_pass_supports_bounded_gpu_ml_claim_only()
    test_write_gpu_ml_runtime_outputs()
    test_run_nvidia_smi_missing_is_bounded()
    test_cli_help_renders()
    test_cli_records_exact_command_arguments()
    print("\n=== REALWORLD GPU ML RUNTIME TESTS PASSED ===")
