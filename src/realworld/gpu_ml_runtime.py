"""GPU-backed ML runtime preflight guard.

This module checks optional ML packages without making GPU acceleration a
requirement for the simulator. A passing result can only support a bounded
GPU-backed ML post-analysis claim for the checked package. It is not simulation
runtime evidence, not model-quality evidence, and not acceptance evidence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import importlib
from importlib import metadata
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence

from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GPU_ML_RUNTIME_MANIFEST = (
    PROJECT_ROOT / "data" / "validation" / "gpu_ml_runtime_manifest.json"
)
DEFAULT_GPU_ML_RUNTIME_LOG = (
    PROJECT_ROOT / "data" / "validation" / "gpu_ml_runtime_log.jsonl"
)
DEFAULT_GPU_ML_RUNTIME_DOC = PROJECT_ROOT / "docs" / "gpu_ml_runtime_check.md"
DEFAULT_REQUIREMENTS_PATH = PROJECT_ROOT / "requirements.txt"
GPU_ML_RUNTIME_SCOPE = (
    "GPU ML runtime preflight only; not simulation acceleration evidence, not "
    "ML model-quality evidence, not publication readiness, not final-study "
    "approval, and not formal acceptance."
)
DEFAULT_GPU_PACKAGES: tuple[str, ...] = ("xgboost",)


@dataclass(frozen=True)
class PackageRuntimeResult:
    """Runtime check result for one optional ML package."""

    package_name: str
    package_version: str
    requested_device: str
    actual_device: str
    import_status: str
    gpu_check_status: str
    cpu_fallback_status: str
    can_support_gpu_ml_claim: bool
    duration_sec: float
    message: str


def check_gpu_ml_runtime(
    *,
    packages: Sequence[str] = DEFAULT_GPU_PACKAGES,
    requested_device: str = "cuda",
    run_fit: bool = True,
    nvidia_smi_command: Sequence[str] = ("nvidia-smi",),
    pip_check_command: Sequence[str] | None = None,
    requirements_path: str | Path = DEFAULT_REQUIREMENTS_PATH,
    output_manifest_path: str | Path = DEFAULT_GPU_ML_RUNTIME_MANIFEST,
    output_log_path: str | Path = DEFAULT_GPU_ML_RUNTIME_LOG,
    output_doc_path: str | Path = DEFAULT_GPU_ML_RUNTIME_DOC,
    command: Sequence[str] | None = None,
    cwd: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Check optional GPU ML packages and return a conservative manifest."""

    nvidia_smi = run_nvidia_smi(command=nvidia_smi_command)
    pip_check = run_pip_check(command=pip_check_command)
    results = [
        check_package_runtime(
            package,
            requested_device=requested_device,
            run_fit=run_fit,
        )
        for package in packages
    ]
    return build_gpu_ml_runtime_manifest(
        package_results=results,
        requested_device=requested_device,
        nvidia_smi=nvidia_smi,
        pip_check=pip_check,
        packages=packages,
        requirements_path=requirements_path,
        output_manifest_path=output_manifest_path,
        output_log_path=output_log_path,
        output_doc_path=output_doc_path,
        command=command,
        cwd=cwd,
    )


def check_package_runtime(
    package_name: str,
    *,
    requested_device: str = "cuda",
    run_fit: bool = True,
) -> PackageRuntimeResult:
    """Run the smallest available GPU check for a supported optional package."""

    started = time.perf_counter()
    version = _package_version(package_name)
    if not version:
        return _package_result(
            package_name=package_name,
            package_version="not_installed",
            requested_device=requested_device,
            actual_device="unavailable",
            import_status="missing",
            gpu_check_status="not_run_missing_package",
            cpu_fallback_status="not_run_missing_package",
            can_support_gpu_ml_claim=False,
            started=started,
            message=f"{package_name} is not installed in the active Python environment.",
        )

    try:
        module = importlib.import_module(package_name)
    except Exception as exc:  # pragma: no cover - depends on local package state.
        return _package_result(
            package_name=package_name,
            package_version=version,
            requested_device=requested_device,
            actual_device="unavailable",
            import_status="import_failed",
            gpu_check_status="not_run_import_failed",
            cpu_fallback_status="not_run_import_failed",
            can_support_gpu_ml_claim=False,
            started=started,
            message=f"{type(exc).__name__}: {exc}",
        )

    if not run_fit:
        return _package_result(
            package_name=package_name,
            package_version=version,
            requested_device=requested_device,
            actual_device="not_checked",
            import_status="imported",
            gpu_check_status="skipped_by_request",
            cpu_fallback_status="skipped_by_request",
            can_support_gpu_ml_claim=False,
            started=started,
            message="Package import checked only; no fit/runtime check was requested.",
        )

    if package_name == "xgboost":
        return _check_xgboost(module, version, requested_device, started)
    if package_name == "torch":
        return _check_torch(module, version, requested_device, started)
    if package_name == "cupy":
        return _check_cupy(module, version, requested_device, started)

    return _package_result(
        package_name=package_name,
        package_version=version,
        requested_device=requested_device,
        actual_device="unsupported_check",
        import_status="imported",
        gpu_check_status="unsupported_package_check",
        cpu_fallback_status="unsupported_package_check",
        can_support_gpu_ml_claim=False,
        started=started,
        message=(
            "Package imported, but this guard has no package-specific GPU fit "
            "check for it."
        ),
    )


def run_nvidia_smi(
    *,
    command: Sequence[str] = ("nvidia-smi",),
    timeout_sec: int = 20,
) -> dict[str, Any]:
    """Run nvidia-smi and retain bounded evidence."""

    started = time.perf_counter()
    try:
        result = subprocess.run(
            list(command),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
    except FileNotFoundError:
        return {
            "status": "missing",
            "returncode": None,
            "duration_sec": round(time.perf_counter() - started, 3),
            "stdout_tail": "",
            "stderr_tail": "nvidia-smi not found",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "timeout",
            "returncode": None,
            "duration_sec": round(time.perf_counter() - started, 3),
            "stdout_tail": _tail(exc.stdout or ""),
            "stderr_tail": _tail(exc.stderr or ""),
        }
    return {
        "status": "available" if result.returncode == 0 else "failed",
        "returncode": result.returncode,
        "duration_sec": round(time.perf_counter() - started, 3),
        "stdout_tail": _tail(result.stdout),
        "stderr_tail": _tail(result.stderr),
    }


def run_pip_check(
    *,
    command: Sequence[str] | None = None,
    timeout_sec: int = 60,
) -> dict[str, Any]:
    """Run pip check and retain bounded evidence."""

    args = list(command) if command is not None else [sys.executable, "-m", "pip", "check"]
    started = time.perf_counter()
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
    except FileNotFoundError:
        return {
            "command": args,
            "status": "missing",
            "returncode": None,
            "duration_sec": round(time.perf_counter() - started, 3),
            "stdout_tail": "",
            "stderr_tail": "pip check command not found",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": args,
            "status": "timeout",
            "returncode": None,
            "duration_sec": round(time.perf_counter() - started, 3),
            "stdout_tail": _tail(exc.stdout or ""),
            "stderr_tail": _tail(exc.stderr or ""),
        }
    return {
        "command": args,
        "status": "passed" if result.returncode == 0 else "failed",
        "returncode": result.returncode,
        "duration_sec": round(time.perf_counter() - started, 3),
        "stdout_tail": _tail(result.stdout),
        "stderr_tail": _tail(result.stderr),
    }


def build_gpu_ml_runtime_manifest(
    *,
    package_results: Sequence[PackageRuntimeResult],
    requested_device: str = "cuda",
    nvidia_smi: Mapping[str, Any] | None = None,
    pip_check: Mapping[str, Any] | None = None,
    packages: Sequence[str] | None = None,
    command: Sequence[str] | None = None,
    cwd: str | Path = PROJECT_ROOT,
    requirements_path: str | Path = DEFAULT_REQUIREMENTS_PATH,
    output_manifest_path: str | Path = DEFAULT_GPU_ML_RUNTIME_MANIFEST,
    output_log_path: str | Path = DEFAULT_GPU_ML_RUNTIME_LOG,
    output_doc_path: str | Path = DEFAULT_GPU_ML_RUNTIME_DOC,
) -> dict[str, Any]:
    """Build a fail-closed GPU ML runtime manifest."""

    result_dicts = [asdict(result) for result in package_results]
    gpu_claim_packages = [
        result.package_name
        for result in package_results
        if result.can_support_gpu_ml_claim
    ]
    blockers = _gpu_runtime_blockers(
        package_results=package_results,
        nvidia_smi=nvidia_smi or {},
        pip_check=pip_check or {},
    )
    requirements = _requirements_context(Path(requirements_path))
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": GPU_ML_RUNTIME_SCOPE,
        "result_scope": "gpu_ml_runtime_preflight_only_not_simulation_acceleration_not_acceptance",
        "command": list(command or []),
        "cwd": str(cwd),
        "requested_device": requested_device,
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "requirements": requirements,
        "packages_requested": list(packages or [r.package_name for r in package_results]),
        "package_results": result_dicts,
        "package_count": len(package_results),
        "gpu_claim_supported_package_count": len(gpu_claim_packages),
        "gpu_claim_supported_packages": gpu_claim_packages,
        "nvidia_smi": dict(nvidia_smi or {}),
        "nvidia_smi_available": (nvidia_smi or {}).get("status") == "available",
        "pip_check": dict(pip_check or {}),
        "pip_check_passed": (pip_check or {}).get("status") == "passed",
        "gpu_ml_runtime_passed": bool(gpu_claim_packages) and not blockers,
        "can_support_gpu_ml_claim": bool(gpu_claim_packages) and not blockers,
        "cpu_fallback_recorded": any(
            result.cpu_fallback_status == "passed" for result in package_results
        ),
        "simulation_engine_gpu_accelerated": False,
        "simulation_correctness_blocked": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "can_mark_complete": False,
        "outputs": {
            "manifest": _display_path(Path(output_manifest_path)),
            "log": _display_path(Path(output_log_path)),
            "doc": _display_path(Path(output_doc_path)),
        },
        "remaining_blockers": blockers,
    }


def write_gpu_ml_runtime_outputs(
    *,
    manifest: Mapping[str, Any],
    manifest_path: str | Path = DEFAULT_GPU_ML_RUNTIME_MANIFEST,
    log_path: str | Path = DEFAULT_GPU_ML_RUNTIME_LOG,
    doc_path: str | Path = DEFAULT_GPU_ML_RUNTIME_DOC,
) -> dict[str, Any]:
    """Write JSON and Markdown GPU runtime preflight artifacts."""

    output_manifest = Path(manifest_path)
    output_log = Path(log_path)
    output_doc = Path(doc_path)
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    output_log.parent.mkdir(parents=True, exist_ok=True)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(manifest)
    payload["outputs"] = {
        "manifest": _display_path(output_manifest),
        "log": _display_path(output_log),
        "doc": _display_path(output_doc),
    }
    preserve_generated_at_when_unchanged(payload, output_manifest)
    write_json_manifest_if_changed(payload, output_manifest, sort_keys=True)
    write_text_if_changed(_build_gpu_ml_runtime_jsonl(payload), output_log)
    write_text_if_changed(build_gpu_ml_runtime_markdown(payload), output_doc)
    return payload


def build_gpu_ml_runtime_markdown(manifest: Mapping[str, Any]) -> str:
    """Return a human-readable runtime preflight note."""

    lines = [
        "# GPU ML Runtime Check",
        "",
        str(manifest.get("claim_boundary", GPU_ML_RUNTIME_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- GPU ML runtime passed: `{str(manifest.get('gpu_ml_runtime_passed', False)).lower()}`",
        f"- Can support GPU ML claim: `{str(manifest.get('can_support_gpu_ml_claim', False)).lower()}`",
        f"- CPU fallback recorded: `{str(manifest.get('cpu_fallback_recorded', False)).lower()}`",
        f"- Simulation engine GPU accelerated: `{str(manifest.get('simulation_engine_gpu_accelerated', False)).lower()}`",
        f"- NVIDIA SMI available: `{str(manifest.get('nvidia_smi_available', False)).lower()}`",
        "",
        "## Package Results",
        "",
        "| Package | Version | Requested | Actual | Import | GPU Check | CPU Fallback | Claim Support |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in manifest.get("package_results", []):
        if not isinstance(result, Mapping):
            continue
        lines.append(
            "| {pkg} | {ver} | {req} | {actual} | {imp} | {gpu} | {cpu} | {claim} |".format(
                pkg=_cell(str(result.get("package_name", ""))),
                ver=_cell(str(result.get("package_version", ""))),
                req=_cell(str(result.get("requested_device", ""))),
                actual=_cell(str(result.get("actual_device", ""))),
                imp=_cell(str(result.get("import_status", ""))),
                gpu=_cell(str(result.get("gpu_check_status", ""))),
                cpu=_cell(str(result.get("cpu_fallback_status", ""))),
                claim=_cell(str(result.get("can_support_gpu_ml_claim", ""))),
            )
        )
    blockers = manifest.get("remaining_blockers", [])
    lines.extend(
        [
            "",
            "## Remaining Blockers",
            "",
        ]
    )
    if isinstance(blockers, list) and blockers:
        lines.extend(f"- {_cell(str(blocker))}" for blocker in blockers)
    else:
        lines.append("- none for the checked GPU ML runtime scope")
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This file can only support a bounded post-simulation GPU ML runtime "
            "claim for packages whose package-specific GPU check and CPU fallback "
            "both passed. It does not make the SimPy/NetworkX simulator GPU "
            "accelerated, does not prove the simulator is GPU accelerated, and "
            "does not prove model validity.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_gpu_ml_runtime_jsonl(manifest: Mapping[str, Any]) -> str:
    records: list[dict[str, Any]] = [
        {
            "record_type": "summary",
            "gpu_ml_runtime_passed": manifest.get("gpu_ml_runtime_passed", False),
            "can_support_gpu_ml_claim": manifest.get("can_support_gpu_ml_claim", False),
            "cpu_fallback_recorded": manifest.get("cpu_fallback_recorded", False),
            "simulation_engine_gpu_accelerated": manifest.get(
                "simulation_engine_gpu_accelerated", False
            ),
        },
        {
            "record_type": "nvidia_smi",
            **(
                dict(manifest.get("nvidia_smi", {}))
                if isinstance(manifest.get("nvidia_smi", {}), Mapping)
                else {}
            ),
        },
        {
            "record_type": "pip_check",
            **(
                dict(manifest.get("pip_check", {}))
                if isinstance(manifest.get("pip_check", {}), Mapping)
                else {}
            ),
        },
    ]
    for result in manifest.get("package_results", []):
        if isinstance(result, Mapping):
            records.append({"record_type": "package_result", **dict(result)})
    return "\n".join(
        json.dumps(record, ensure_ascii=True, sort_keys=True) for record in records
    ) + "\n"


def _check_xgboost(
    module: Any,
    version: str,
    requested_device: str,
    started: float,
) -> PackageRuntimeResult:
    try:
        import numpy as np

        x = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
        y = np.array([0, 0, 1, 1])
        gpu_model = module.XGBClassifier(
            n_estimators=2,
            max_depth=1,
            learning_rate=1.0,
            tree_method="hist",
            device=requested_device,
            eval_metric="logloss",
            verbosity=0,
        )
        gpu_model.fit(x, y)
        config = gpu_model.get_booster().save_config().lower()
        gpu_used = "cuda" in config or "\"device\":\"cuda" in config
        cpu_model = module.XGBClassifier(
            n_estimators=2,
            max_depth=1,
            learning_rate=1.0,
            tree_method="hist",
            device="cpu",
            eval_metric="logloss",
            verbosity=0,
        )
        cpu_model.fit(x, y)
    except Exception as exc:  # pragma: no cover - depends on optional package state.
        return _package_result(
            package_name="xgboost",
            package_version=version,
            requested_device=requested_device,
            actual_device="unavailable",
            import_status="imported",
            gpu_check_status="failed",
            cpu_fallback_status="not_run_after_gpu_failure",
            can_support_gpu_ml_claim=False,
            started=started,
            message=f"{type(exc).__name__}: {exc}",
        )
    return _package_result(
        package_name="xgboost",
        package_version=version,
        requested_device=requested_device,
        actual_device=requested_device if gpu_used else "not_confirmed",
        import_status="imported",
        gpu_check_status="passed" if gpu_used else "fit_passed_device_not_confirmed",
        cpu_fallback_status="passed",
        can_support_gpu_ml_claim=gpu_used,
        started=started,
        message="XGBoost small GPU fit and CPU fallback completed."
        if gpu_used
        else "XGBoost fit completed, but booster config did not confirm CUDA use.",
    )


def _check_torch(
    module: Any,
    version: str,
    requested_device: str,
    started: float,
) -> PackageRuntimeResult:
    try:
        cuda_available = bool(module.cuda.is_available())
        if not cuda_available:
            cpu_value = module.tensor([1.0, 2.0], device="cpu").sum().item()
            return _package_result(
                package_name="torch",
                package_version=version,
                requested_device=requested_device,
                actual_device="cpu",
                import_status="imported",
                gpu_check_status="failed_cuda_unavailable",
                cpu_fallback_status="passed" if cpu_value == 3.0 else "failed",
                can_support_gpu_ml_claim=False,
                started=started,
                message="torch imported, but torch.cuda.is_available() is false.",
            )
        tensor = module.tensor([1.0, 2.0], device=requested_device)
        gpu_value = float(tensor.sum().item())
        cpu_value = float(module.tensor([1.0, 2.0], device="cpu").sum().item())
    except Exception as exc:  # pragma: no cover - depends on optional package state.
        return _package_result(
            package_name="torch",
            package_version=version,
            requested_device=requested_device,
            actual_device="unavailable",
            import_status="imported",
            gpu_check_status="failed",
            cpu_fallback_status="not_run_after_gpu_failure",
            can_support_gpu_ml_claim=False,
            started=started,
            message=f"{type(exc).__name__}: {exc}",
        )
    return _package_result(
        package_name="torch",
        package_version=version,
        requested_device=requested_device,
        actual_device=str(tensor.device),
        import_status="imported",
        gpu_check_status="passed" if gpu_value == 3.0 else "failed",
        cpu_fallback_status="passed" if cpu_value == 3.0 else "failed",
        can_support_gpu_ml_claim=(gpu_value == 3.0 and cpu_value == 3.0),
        started=started,
        message="torch CUDA tensor check and CPU fallback completed.",
    )


def _check_cupy(
    module: Any,
    version: str,
    requested_device: str,
    started: float,
) -> PackageRuntimeResult:
    try:
        array = module.asarray([1.0, 2.0])
        value = float(array.sum().get())
    except Exception as exc:  # pragma: no cover - depends on optional package state.
        return _package_result(
            package_name="cupy",
            package_version=version,
            requested_device=requested_device,
            actual_device="unavailable",
            import_status="imported",
            gpu_check_status="failed",
            cpu_fallback_status="not_applicable_cupy_only",
            can_support_gpu_ml_claim=False,
            started=started,
            message=f"{type(exc).__name__}: {exc}",
        )
    return _package_result(
        package_name="cupy",
        package_version=version,
        requested_device=requested_device,
        actual_device="cuda",
        import_status="imported",
        gpu_check_status="passed" if value == 3.0 else "failed",
        cpu_fallback_status="not_applicable_cupy_only",
        can_support_gpu_ml_claim=False,
        started=started,
        message=(
            "CuPy CUDA array check completed, but no CPU fallback was recorded "
            "for a model package."
        ),
    )


def _gpu_runtime_blockers(
    *,
    package_results: Sequence[PackageRuntimeResult],
    nvidia_smi: Mapping[str, Any],
    pip_check: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if nvidia_smi.get("status") != "available":
        blockers.append("nvidia-smi evidence is unavailable or failed")
    if pip_check.get("status") != "passed":
        blockers.append("pip check did not pass")
    if not package_results:
        blockers.append("no GPU ML packages were checked")
    if not any(result.can_support_gpu_ml_claim for result in package_results):
        blockers.append("no checked package completed a confirmed GPU runtime check")
    if not any(result.cpu_fallback_status == "passed" for result in package_results):
        blockers.append("no checked package recorded a passing CPU fallback")
    for result in package_results:
        if result.import_status != "imported":
            blockers.append(f"{result.package_name}: {result.import_status}")
        elif result.gpu_check_status != "passed":
            blockers.append(f"{result.package_name}: {result.gpu_check_status}")
        elif result.cpu_fallback_status != "passed":
            blockers.append(f"{result.package_name}: CPU fallback not passed")
    return blockers


def _package_version(package_name: str) -> str:
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return ""


def _requirements_context(path: Path) -> dict[str, str]:
    if not path.exists():
        return {
            "path": _display_path(path),
            "status": "missing",
            "sha256": "",
        }
    return {
        "path": _display_path(path),
        "status": "present",
        "sha256": _sha256_file(path),
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _package_result(
    *,
    package_name: str,
    package_version: str,
    requested_device: str,
    actual_device: str,
    import_status: str,
    gpu_check_status: str,
    cpu_fallback_status: str,
    can_support_gpu_ml_claim: bool,
    started: float,
    message: str,
) -> PackageRuntimeResult:
    return PackageRuntimeResult(
        package_name=package_name,
        package_version=package_version,
        requested_device=requested_device,
        actual_device=actual_device,
        import_status=import_status,
        gpu_check_status=gpu_check_status,
        cpu_fallback_status=cpu_fallback_status,
        can_support_gpu_ml_claim=can_support_gpu_ml_claim,
        duration_sec=round(time.perf_counter() - started, 3),
        message=message,
    )


def _tail(value: object, limit: int = 4000) -> str:
    text = value.decode(errors="replace") if isinstance(value, bytes) else str(value or "")
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[-limit:]


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_GPU_ML_RUNTIME_DOC",
    "DEFAULT_GPU_ML_RUNTIME_LOG",
    "DEFAULT_GPU_ML_RUNTIME_MANIFEST",
    "DEFAULT_GPU_PACKAGES",
    "GPU_ML_RUNTIME_SCOPE",
    "PackageRuntimeResult",
    "build_gpu_ml_runtime_manifest",
    "build_gpu_ml_runtime_markdown",
    "check_gpu_ml_runtime",
    "check_package_runtime",
    "run_nvidia_smi",
    "run_pip_check",
    "write_gpu_ml_runtime_outputs",
]
