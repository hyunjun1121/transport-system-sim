"""Runtime preflight manifest for experiment and benchmark runs.

This module records the local runtime context required by ``plan.md`` before
compact, full, benchmark, or GPU-backed ML work. It is environment evidence
only; it does not validate simulation outputs, certify calibration, or close
study gates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import importlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
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
DEFAULT_RUNTIME_PREFLIGHT_DIR = PROJECT_ROOT / "data" / "validation" / "runtime_preflight"
DEFAULT_RUNTIME_PREFLIGHT_DOC_DIR = PROJECT_ROOT / "docs" / "runtime_preflight"
DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_MANIFEST = (
    PROJECT_ROOT / "data" / "validation" / "dirty_worktree_classification_manifest.json"
)
DEFAULT_REQUIREMENTS_PATHS: tuple[Path, ...] = (PROJECT_ROOT / "requirements.txt",)
RUNTIME_PREFLIGHT_SCOPE = (
    "Runtime preflight evidence only; not simulation output evidence, not "
    "calibrated validation, not publication readiness, not final-study "
    "approval, and not formal acceptance."
)
DEFAULT_PACKAGE_SPECS: tuple[str, ...] = (
    "simpy",
    "networkx",
    "numpy",
    "pandas",
    "PyYAML:yaml",
    "matplotlib",
    "seaborn",
    "python-docx:docx",
    "SALib:SALib",
)


@dataclass(frozen=True)
class PackageImportResult:
    """Import/version check result for one runtime package."""

    distribution_name: str
    import_name: str
    package_version: str
    import_status: str
    message: str


def write_runtime_preflight_manifest(
    *,
    phase_id: str,
    execution_scope: str = "cpu",
    package_specs: Sequence[str] = DEFAULT_PACKAGE_SPECS,
    requirements_paths: Sequence[str | Path] = DEFAULT_REQUIREMENTS_PATHS,
    dirty_manifest_path: str | Path = DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_MANIFEST,
    include_gpu: bool = False,
    gpu_smoke_command: str = "",
    analysis_command: str = "",
    command: Sequence[str] | None = None,
    cwd: str | Path = PROJECT_ROOT,
    output_manifest_path: str | Path | None = None,
    output_log_path: str | Path | None = None,
    output_doc_path: str | Path | None = None,
) -> dict[str, Any]:
    """Collect and write a phase-scoped runtime preflight manifest."""

    paths = runtime_preflight_paths(
        phase_id=phase_id,
        output_manifest_path=output_manifest_path,
        output_log_path=output_log_path,
        output_doc_path=output_doc_path,
    )
    manifest = collect_runtime_preflight(
        phase_id=phase_id,
        execution_scope=execution_scope,
        package_specs=package_specs,
        requirements_paths=requirements_paths,
        dirty_manifest_path=dirty_manifest_path,
        include_gpu=include_gpu,
        gpu_smoke_command=gpu_smoke_command,
        analysis_command=analysis_command,
        command=command,
        cwd=cwd,
        output_manifest_path=paths["manifest"],
        output_log_path=paths["log"],
        output_doc_path=paths["doc"],
    )
    return write_runtime_preflight_outputs(
        manifest=manifest,
        manifest_path=paths["manifest"],
        log_path=paths["log"],
        doc_path=paths["doc"],
    )


def collect_runtime_preflight(
    *,
    phase_id: str,
    execution_scope: str = "cpu",
    package_specs: Sequence[str] = DEFAULT_PACKAGE_SPECS,
    requirements_paths: Sequence[str | Path] = DEFAULT_REQUIREMENTS_PATHS,
    dirty_manifest_path: str | Path = DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_MANIFEST,
    include_gpu: bool = False,
    gpu_smoke_command: str = "",
    analysis_command: str = "",
    command: Sequence[str] | None = None,
    cwd: str | Path = PROJECT_ROOT,
    output_manifest_path: str | Path | None = None,
    output_log_path: str | Path | None = None,
    output_doc_path: str | Path | None = None,
) -> dict[str, Any]:
    """Collect local runtime state and return a fail-closed manifest."""

    git_status = run_command(("git", "status", "--short", "--branch"), cwd=cwd)
    git_head = run_command(("git", "rev-parse", "HEAD"), cwd=cwd)
    git_branch = run_command(("git", "branch", "--show-current"), cwd=cwd)
    powershell_version = run_command(
        (
            "powershell",
            "-NoProfile",
            "-Command",
            "$PSVersionTable.PSVersion.ToString()",
        ),
        cwd=cwd,
    )
    cpu_wmi = run_command(
        (
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Processor | Select-Object -First 1 "
            "Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json -Compress",
        ),
        cwd=cwd,
    )
    memory_wmi = run_command(
        (
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_ComputerSystem | Select-Object "
            "TotalPhysicalMemory | ConvertTo-Json -Compress",
        ),
        cwd=cwd,
    )
    nvidia_smi = (
        run_command(
            (
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader",
            ),
            cwd=cwd,
        )
        if include_gpu
        else _skipped_command("nvidia-smi skipped because GPU scope is false")
    )
    pip_check = run_command((sys.executable, "-m", "pip", "check"), cwd=cwd)
    requirements = [_file_context(path) for path in requirements_paths]
    dirty = _dirty_manifest_context(Path(dirty_manifest_path))
    packages = [check_package_import(spec) for spec in package_specs]

    return build_runtime_preflight_manifest(
        phase_id=phase_id,
        execution_scope=execution_scope,
        git_status=git_status,
        git_head=git_head,
        git_branch=git_branch,
        powershell_version=powershell_version,
        cpu_wmi=cpu_wmi,
        memory_wmi=memory_wmi,
        nvidia_smi=nvidia_smi,
        pip_check=pip_check,
        requirements=requirements,
        dirty_worktree=dirty,
        package_results=packages,
        include_gpu=include_gpu,
        gpu_smoke_command=gpu_smoke_command,
        analysis_command=analysis_command,
        command=command,
        cwd=cwd,
        output_manifest_path=output_manifest_path,
        output_log_path=output_log_path,
        output_doc_path=output_doc_path,
    )


def build_runtime_preflight_manifest(
    *,
    phase_id: str,
    execution_scope: str = "cpu",
    git_status: Mapping[str, Any] | None = None,
    git_head: Mapping[str, Any] | None = None,
    git_branch: Mapping[str, Any] | None = None,
    powershell_version: Mapping[str, Any] | None = None,
    cpu_wmi: Mapping[str, Any] | None = None,
    memory_wmi: Mapping[str, Any] | None = None,
    nvidia_smi: Mapping[str, Any] | None = None,
    pip_check: Mapping[str, Any] | None = None,
    requirements: Sequence[Mapping[str, Any]] = (),
    dirty_worktree: Mapping[str, Any] | None = None,
    package_results: Sequence[PackageImportResult | Mapping[str, Any]] = (),
    include_gpu: bool = False,
    gpu_smoke_command: str = "",
    analysis_command: str = "",
    command: Sequence[str] | None = None,
    cwd: str | Path = PROJECT_ROOT,
    output_manifest_path: str | Path | None = None,
    output_log_path: str | Path | None = None,
    output_doc_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build a runtime preflight manifest from collected command evidence."""

    package_dicts = [
        asdict(result) if isinstance(result, PackageImportResult) else dict(result)
        for result in package_results
    ]
    git_status_map = dict(git_status or {})
    git_head_map = dict(git_head or {})
    git_branch_map = dict(git_branch or {})
    pip_check_map = dict(pip_check or {})
    nvidia_map = dict(nvidia_smi or {})
    dirty_map = dict(dirty_worktree or {})
    blockers = _runtime_blockers(
        git_status=git_status_map,
        git_head=git_head_map,
        pip_check=pip_check_map,
        dirty_worktree=dirty_map,
        package_results=package_dicts,
        include_gpu=include_gpu,
        nvidia_smi=nvidia_map,
        gpu_smoke_command=gpu_smoke_command,
    )
    paths = runtime_preflight_paths(
        phase_id=phase_id,
        output_manifest_path=output_manifest_path,
        output_log_path=output_log_path,
        output_doc_path=output_doc_path,
    )
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "phase_id": phase_id,
        "execution_scope": execution_scope,
        "claim_boundary": RUNTIME_PREFLIGHT_SCOPE,
        "result_scope": "runtime_preflight_only_not_output_validation_not_acceptance",
        "command": list(command or []),
        "cwd": str(cwd),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "python": {
            "executable": sys.executable,
            "version": sys.version.split()[0],
        },
        "powershell_version": dict(powershell_version or {}),
        "cpu": {
            "os_cpu_count": os.cpu_count(),
            "wmi": dict(cpu_wmi or {}),
            "parsed": _parse_json_tail(cpu_wmi or {}),
        },
        "memory": {
            "wmi": dict(memory_wmi or {}),
            "parsed": _parse_json_tail(memory_wmi or {}),
        },
        "git": {
            "status": git_status_map,
            "head": git_head_map,
            "branch": _first_line(git_branch_map.get("stdout_tail", ""))
            or _git_branch(git_status_map),
            "branch_command": git_branch_map,
            "head_sha": _first_line(git_head_map.get("stdout_tail", "")),
            "dirty_status_text": git_status_map.get("stdout_tail", ""),
        },
        "dirty_worktree_classification": dirty_map,
        "requirements": list(requirements),
        "pip_check": pip_check_map,
        "package_results": package_dicts,
        "include_gpu": include_gpu,
        "nvidia_smi": nvidia_map,
        "gpu_smoke_command": gpu_smoke_command,
        "analysis_command": analysis_command,
        "cpu_simulation_default": True,
        "simulation_engine_gpu_accelerated": False,
        "gpu_scope_claim_boundary": (
            "GPU evidence applies only to post-simulation ML or explainability "
            "unless a separate GPU simulation engine is implemented and tested."
        ),
        "cpu_gpu_fallback_behavior": (
            "Core simulation remains CPU-bound. GPU failures must fall back to "
            "CPU-only simulation and may only disable optional ML acceleration."
        ),
        "runtime_preflight_ready": not blockers,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "can_mark_complete": False,
        "outputs": {
            "manifest": _display_path(paths["manifest"]),
            "log": _display_path(paths["log"]),
            "doc": _display_path(paths["doc"]),
        },
        "remaining_blockers": blockers,
        "review_items": [
            "rerun this preflight before compact, full, benchmark, or GPU-backed ML runs",
            "keep GPU evidence scoped to post-simulation ML unless a GPU simulation engine exists",
            "record dirty-worktree and package state before generated-output promotion",
        ],
    }


def write_runtime_preflight_outputs(
    *,
    manifest: Mapping[str, Any],
    manifest_path: str | Path,
    log_path: str | Path,
    doc_path: str | Path,
) -> dict[str, Any]:
    """Write runtime preflight JSON, JSONL, and Markdown artifacts."""

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
    write_text_if_changed(_runtime_preflight_jsonl(payload), output_log)
    write_text_if_changed(build_runtime_preflight_markdown(payload), output_doc)
    return payload


def build_runtime_preflight_markdown(manifest: Mapping[str, Any]) -> str:
    """Return a human-readable runtime preflight note."""

    lines = [
        "# Runtime Preflight Manifest",
        "",
        str(manifest.get("claim_boundary", RUNTIME_PREFLIGHT_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Phase ID: `{_cell(str(manifest.get('phase_id', '')))}`",
        f"- Execution scope: `{_cell(str(manifest.get('execution_scope', '')))}`",
        f"- Runtime preflight blockers absent: `{str(manifest.get('runtime_preflight_ready', False)).lower()}`",
        f"- CPU simulation default: `{str(manifest.get('cpu_simulation_default', True)).lower()}`",
        f"- Simulation engine GPU accelerated: `{str(manifest.get('simulation_engine_gpu_accelerated', False)).lower()}`",
        f"- Final-study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        "",
        "## Runtime Evidence",
        "",
        f"- Git HEAD: `{_cell(str(_nested(manifest, 'git', 'head_sha')))}`",
        f"- Git branch: `{_cell(str(_nested(manifest, 'git', 'branch')))}`",
        f"- Python: `{_cell(str(_nested(manifest, 'python', 'version')))}`",
        f"- OS CPU count: `{_cell(str(_nested(manifest, 'cpu', 'os_cpu_count')))}`",
        f"- Pip check: `{_cell(str(_nested(manifest, 'pip_check', 'status')))}`",
        f"- Dirty manifest hash: `{_cell(str(_nested(manifest, 'dirty_worktree_classification', 'sha256')))}`",
        "",
        "## Package Imports",
        "",
        "| Distribution | Import | Version | Status |",
        "| --- | --- | --- | --- |",
    ]
    for result in manifest.get("package_results", []):
        if not isinstance(result, Mapping):
            continue
        lines.append(
            "| {dist} | {imp} | {ver} | {status} |".format(
                dist=_cell(str(result.get("distribution_name", ""))),
                imp=_cell(str(result.get("import_name", ""))),
                ver=_cell(str(result.get("package_version", ""))),
                status=_cell(str(result.get("import_status", ""))),
            )
        )
    blockers = manifest.get("remaining_blockers", [])
    lines.extend(["", "## Remaining Blockers", ""])
    if isinstance(blockers, list) and blockers:
        lines.extend(f"- {_cell(str(blocker))}" for blocker in blockers)
    else:
        lines.append("- none for this runtime-preflight scope")
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This manifest records environment and dependency state before a run. "
            "It does not validate simulation outputs, does not certify source "
            "evidence, and does not close publication or final-study gates.",
            "",
        ]
    )
    return "\n".join(lines)


def runtime_preflight_paths(
    *,
    phase_id: str,
    output_manifest_path: str | Path | None = None,
    output_log_path: str | Path | None = None,
    output_doc_path: str | Path | None = None,
) -> dict[str, Path]:
    """Return phase-scoped runtime preflight output paths."""

    safe_phase = _safe_id(phase_id)
    return {
        "manifest": Path(output_manifest_path)
        if output_manifest_path is not None
        else DEFAULT_RUNTIME_PREFLIGHT_DIR / f"{safe_phase}_runtime_preflight_manifest.json",
        "log": Path(output_log_path)
        if output_log_path is not None
        else DEFAULT_RUNTIME_PREFLIGHT_DIR / f"{safe_phase}_runtime_preflight_log.jsonl",
        "doc": Path(output_doc_path)
        if output_doc_path is not None
        else DEFAULT_RUNTIME_PREFLIGHT_DOC_DIR / f"{safe_phase}_runtime_preflight.md",
    }


def check_package_import(spec: str) -> PackageImportResult:
    """Check package version and import availability."""

    distribution, import_name = _parse_package_spec(spec)
    version = _package_version(distribution)
    if not version:
        return PackageImportResult(
            distribution_name=distribution,
            import_name=import_name,
            package_version="not_installed",
            import_status="missing_distribution",
            message=f"{distribution} is not installed.",
        )
    try:
        importlib.import_module(import_name)
    except Exception as exc:  # pragma: no cover - depends on local package state.
        return PackageImportResult(
            distribution_name=distribution,
            import_name=import_name,
            package_version=version,
            import_status="import_failed",
            message=f"{type(exc).__name__}: {exc}",
        )
    return PackageImportResult(
        distribution_name=distribution,
        import_name=import_name,
        package_version=version,
        import_status="imported",
        message="import succeeded",
    )


def run_command(
    command: Sequence[str],
    *,
    cwd: str | Path = PROJECT_ROOT,
    timeout_sec: int = 60,
) -> dict[str, Any]:
    """Run a bounded command and retain only tails for manifest evidence."""

    args = [str(item) for item in command]
    started = time.perf_counter()
    try:
        result = subprocess.run(
            args,
            cwd=str(cwd),
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
            "stderr_tail": f"{args[0]} not found",
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


def _runtime_preflight_jsonl(manifest: Mapping[str, Any]) -> str:
    records = [
        {
            "record_type": "summary",
            "phase_id": manifest.get("phase_id", ""),
            "execution_scope": manifest.get("execution_scope", ""),
            "runtime_preflight_ready": manifest.get("runtime_preflight_ready", False),
            "simulation_engine_gpu_accelerated": manifest.get(
                "simulation_engine_gpu_accelerated", False
            ),
        },
        {"record_type": "git", **dict(manifest.get("git", {}))},
        {"record_type": "pip_check", **dict(manifest.get("pip_check", {}))},
        {"record_type": "nvidia_smi", **dict(manifest.get("nvidia_smi", {}))},
    ]
    for result in manifest.get("package_results", []):
        if isinstance(result, Mapping):
            records.append({"record_type": "package_import", **dict(result)})
    return "\n".join(
        json.dumps(record, ensure_ascii=True, sort_keys=True) for record in records
    ) + "\n"


def _runtime_blockers(
    *,
    git_status: Mapping[str, Any],
    git_head: Mapping[str, Any],
    pip_check: Mapping[str, Any],
    dirty_worktree: Mapping[str, Any],
    package_results: Sequence[Mapping[str, Any]],
    include_gpu: bool,
    nvidia_smi: Mapping[str, Any],
    gpu_smoke_command: str,
) -> list[str]:
    blockers: list[str] = []
    if git_status.get("status") != "passed":
        blockers.append("git status command did not pass")
    if git_head.get("status") != "passed":
        blockers.append("git HEAD command did not pass")
    if pip_check.get("status") != "passed":
        blockers.append("pip check did not pass")
    if not dirty_worktree.get("manifest_present"):
        blockers.append("dirty worktree classification manifest is absent")
    if dirty_worktree.get("unclassified_path_count", 1) != 0:
        blockers.append("dirty worktree classification has unclassified paths")
    for result in package_results:
        if result.get("import_status") != "imported":
            blockers.append(
                "runtime package import failed or is missing: "
                + str(result.get("distribution_name", ""))
            )
    if include_gpu:
        if nvidia_smi.get("status") != "passed":
            blockers.append("GPU scope requested but nvidia-smi did not pass")
        if not gpu_smoke_command.strip():
            blockers.append("GPU scope requested but no GPU smoke command was recorded")
    return blockers


def _dirty_manifest_context(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": _display_path(path),
            "manifest_present": False,
            "sha256": "",
        }
    digest = _sha256(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = {}
    return {
        "path": _display_path(path),
        "manifest_present": True,
        "sha256": digest,
        "dirty_path_count": payload.get("dirty_path_count"),
        "unclassified_path_count": payload.get("unclassified_path_count"),
        "new_generated_output_allowed": payload.get("new_generated_output_allowed"),
        "final_study_ready": payload.get("final_study_ready"),
    }


def _file_context(path_like: str | Path) -> dict[str, Any]:
    path = Path(path_like)
    return {
        "path": _display_path(path),
        "present": path.exists(),
        "sha256": _sha256(path) if path.exists() else "",
    }


def _parse_package_spec(spec: str) -> tuple[str, str]:
    if ":" in spec:
        distribution, import_name = spec.split(":", 1)
    else:
        distribution = spec
        import_name = spec.replace("-", "_")
    return distribution.strip(), import_name.strip()


def _package_version(distribution_name: str) -> str:
    try:
        return metadata.version(distribution_name)
    except metadata.PackageNotFoundError:
        return ""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _skipped_command(message: str) -> dict[str, Any]:
    return {
        "command": [],
        "status": "skipped",
        "returncode": None,
        "duration_sec": 0.0,
        "stdout_tail": "",
        "stderr_tail": message,
    }


def _parse_json_tail(command_result: Mapping[str, Any]) -> Any:
    text = str(command_result.get("stdout_tail", "")).strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _git_branch(git_status: Mapping[str, Any]) -> str:
    first = _first_line(git_status.get("stdout_tail", ""))
    if first.startswith("## "):
        return first[3:].split("...", 1)[0].strip()
    return ""


def _first_line(value: Any) -> str:
    text = str(value or "").strip()
    return text.splitlines()[0].strip() if text else ""


def _nested(mapping: Mapping[str, Any], first: str, second: str) -> Any:
    value = mapping.get(first, {})
    if isinstance(value, Mapping):
        return value.get(second, "")
    return ""


def _safe_id(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value)
    return cleaned.strip("_") or "runtime_preflight"


def _tail(text: str, limit: int = 4000) -> str:
    normalized = (text or "").strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[-limit:]


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_PACKAGE_SPECS",
    "DEFAULT_RUNTIME_PREFLIGHT_DIR",
    "DEFAULT_RUNTIME_PREFLIGHT_DOC_DIR",
    "PackageImportResult",
    "RUNTIME_PREFLIGHT_SCOPE",
    "build_runtime_preflight_manifest",
    "build_runtime_preflight_markdown",
    "check_package_import",
    "collect_runtime_preflight",
    "run_command",
    "runtime_preflight_paths",
    "write_runtime_preflight_manifest",
    "write_runtime_preflight_outputs",
]
