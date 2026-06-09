"""Bounded clean-checkout reproducibility smoke evidence.

This module clones the committed source tree into a temporary directory and
runs the existing reproducibility smoke ladder there. It is source-checkout
evidence only: it uses the current Python environment, does not reinstall
dependencies by default, and never creates formal acceptance records.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "clean_checkout_reproducibility_smoke_manifest.json"
)
DEFAULT_CLEAN_CHECKOUT_SMOKE_LOG_PATH = (
    PROJECT_ROOT / "data" / "validation" / "clean_checkout_reproducibility_smoke_log.jsonl"
)
DEFAULT_CLEAN_CHECKOUT_SMOKE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "clean_checkout_reproducibility_smoke.md"
)
CLEAN_CHECKOUT_SMOKE_SELF_OUTPUTS: frozenset[str] = frozenset(
    {
        "data/validation/clean_checkout_reproducibility_smoke_manifest.json",
        "data/validation/clean_checkout_reproducibility_smoke_log.jsonl",
        "docs/clean_checkout_reproducibility_smoke.md",
    }
)
CLEAN_CHECKOUT_SMOKE_SCOPE = "clean_checkout_source_tree_smoke_not_formal_acceptance"
MAX_CAPTURE_CHARS = 4000
ARTIFACT_REGENERATION_SCOPE = (
    "bounded_review_and_audit_artifact_regeneration_not_full_reproduction"
)


ARTIFACT_REGENERATION_COMMANDS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "regenerate_reproducibility_review_packet",
        "Regenerate reproducibility review packet",
        ("{python}", "scripts/write_reproducibility_review_packet.py"),
    ),
    (
        "regenerate_reproducibility_decision_packet",
        "Regenerate reproducibility decision packet",
        ("{python}", "scripts/write_reproducibility_decision_packet.py"),
    ),
    (
        "regenerate_final_audit_decision_packet",
        "Regenerate final-audit decision packet",
        ("{python}", "scripts/write_final_audit_decision_packet.py"),
    ),
    (
        "regenerate_acceptance_audit",
        "Regenerate acceptance audit artifacts",
        ("{python}", "scripts/run_acceptance_audit.py"),
    ),
    (
        "regenerate_plan_artifact_audit",
        "Regenerate plan artifact audit",
        ("{python}", "scripts/audit_plan_artifacts.py"),
    ),
)


@dataclass(frozen=True)
class CleanCheckoutStepResult:
    """One outer clean-checkout orchestration step."""

    step_id: str
    label: str
    args: tuple[str, ...]
    cwd: str
    status: str
    returncode: int | None
    passed: bool
    duration_sec: float
    stdout_tail: str
    stderr_tail: str

    def to_json(self) -> dict[str, Any]:
        """Return a JSON-serializable result record."""

        return {
            "step_id": self.step_id,
            "label": self.label,
            "args": list(self.args),
            "args_display": subprocess.list2cmdline(list(self.args)),
            "cwd": self.cwd,
            "status": self.status,
            "returncode": self.returncode,
            "passed": self.passed,
            "duration_sec": round(self.duration_sec, 3),
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }


def run_clean_checkout_smoke(
    *,
    source_repo: str | Path = PROJECT_ROOT,
    manifest_path: str | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
    log_path: str | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_LOG_PATH,
    doc_path: str | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_DOC_PATH,
    python_executable: str | Path = sys.executable,
    install_dependencies: bool = False,
    artifact_regeneration: bool = False,
    keep_checkout: bool = False,
    checkout_parent: str | Path | None = None,
    timeout_sec: int = 1800,
) -> dict[str, Any]:
    """Clone committed source, run smoke in the clone, and write evidence."""

    source_path = Path(source_repo).resolve()
    source_commit = _git_text(("git", "rev-parse", "HEAD"), cwd=source_path)
    source_status_lines = _filter_source_status_lines(
        _git_lines(("git", "status", "--short"), cwd=source_path)
    )
    checkout_dir, cleanup = _prepare_checkout_dir(
        checkout_parent=checkout_parent,
        keep_checkout=keep_checkout,
    )
    outer_steps: list[CleanCheckoutStepResult] = []
    inner_manifest: dict[str, Any] = {}
    inner_log_text = ""

    try:
        outer_steps.append(
            _run_step(
                "git_clone_source_tree",
                "Clone committed source tree",
                (
                    "git",
                    "-c",
                    "core.longpaths=true",
                    "clone",
                    "--no-tags",
                    str(source_path),
                    str(checkout_dir),
                ),
                cwd=checkout_dir.parent,
                timeout_sec=timeout_sec,
            )
        )
        if outer_steps[-1].passed and source_commit:
            outer_steps.append(
                _run_step(
                    "git_checkout_source_commit",
                    "Checkout exact source commit",
                    ("git", "-c", "core.longpaths=true", "checkout", source_commit),
                    cwd=checkout_dir,
                    timeout_sec=120,
                )
            )
        if outer_steps and outer_steps[-1].passed:
            smoke_python = Path(python_executable)
            if install_dependencies:
                venv_dir = checkout_dir / ".clean-smoke-venv"
                outer_steps.append(
                    _run_step(
                        "create_clean_checkout_venv",
                        "Create clean-checkout virtual environment",
                        (str(python_executable), "-m", "venv", str(venv_dir)),
                        cwd=checkout_dir,
                        timeout_sec=timeout_sec,
                    )
                )
                smoke_python = _venv_python_path(venv_dir)
            if outer_steps[-1].passed and install_dependencies:
                outer_steps.append(
                    _run_step(
                        "upgrade_clean_checkout_pip",
                        "Upgrade pip in clean-checkout virtual environment",
                        (
                            str(smoke_python),
                            "-m",
                            "pip",
                            "install",
                            "--upgrade",
                            "pip",
                        ),
                        cwd=checkout_dir,
                        timeout_sec=timeout_sec,
                    )
                )
            if outer_steps[-1].passed and install_dependencies:
                outer_steps.append(
                    _run_step(
                        "install_clean_checkout_requirements",
                        "Install clean-checkout requirements",
                        (
                            str(smoke_python),
                            "-m",
                            "pip",
                            "install",
                            "-r",
                            "requirements.txt",
                        ),
                        cwd=checkout_dir,
                        timeout_sec=timeout_sec,
                    )
                )
        if outer_steps and outer_steps[-1].passed:
            outer_steps.append(
                _run_step(
                    "run_reproducibility_smoke_in_clean_checkout",
                    "Run bounded reproducibility smoke in clean checkout",
                    (
                        str(smoke_python),
                        "scripts/run_reproducibility_smoke.py",
                        "--profile",
                        "clean-checkout-minimal",
                    ),
                    cwd=checkout_dir,
                    timeout_sec=timeout_sec,
                )
            )
        if outer_steps and outer_steps[-1].passed and artifact_regeneration:
            for step_id, label, command_args in ARTIFACT_REGENERATION_COMMANDS:
                outer_steps.append(
                    _run_step(
                        step_id,
                        label,
                        _resolve_artifact_regeneration_args(
                            command_args,
                            python_executable=smoke_python,
                        ),
                        cwd=checkout_dir,
                        timeout_sec=timeout_sec,
                    )
                )
                if not outer_steps[-1].passed:
                    break
        inner_manifest = _read_json_object(
            checkout_dir / "data" / "validation" / "reproducibility_smoke_manifest.json"
        )
        inner_log_text = _read_text(
            checkout_dir / "data" / "validation" / "reproducibility_smoke_log.jsonl"
        )
    finally:
        if cleanup:
            cleanup()

    manifest = build_clean_checkout_smoke_manifest(
        source_repo=source_path,
        source_commit=source_commit,
        source_status_lines=source_status_lines,
        checkout_dir=checkout_dir,
        checkout_retained=keep_checkout,
        python_executable=python_executable,
        install_dependencies=install_dependencies,
        artifact_regeneration=artifact_regeneration,
        outer_steps=outer_steps,
        inner_manifest=inner_manifest,
        manifest_path=manifest_path,
        log_path=log_path,
        doc_path=doc_path,
    )
    write_clean_checkout_smoke_outputs(
        manifest=manifest,
        outer_steps=outer_steps,
        inner_log_text=inner_log_text,
        manifest_path=manifest_path,
        log_path=log_path,
        doc_path=doc_path,
    )
    return manifest


def build_clean_checkout_smoke_manifest(
    *,
    source_repo: str | Path,
    source_commit: str,
    source_status_lines: Sequence[str],
    checkout_dir: str | Path,
    checkout_retained: bool,
    python_executable: str | Path,
    install_dependencies: bool = False,
    artifact_regeneration: bool = False,
    outer_steps: Sequence[CleanCheckoutStepResult],
    inner_manifest: Mapping[str, Any],
    manifest_path: str | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
    log_path: str | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_LOG_PATH,
    doc_path: str | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_DOC_PATH,
) -> dict[str, Any]:
    """Build a non-acceptance clean-checkout smoke manifest."""

    inner_command_count = int(inner_manifest.get("command_count", 0) or 0)
    inner_passed_count = int(inner_manifest.get("passed_count", 0) or 0)
    inner_failed_count = int(inner_manifest.get("failed_count", 0) or 0)
    outer_passed = bool(outer_steps) and all(step.passed for step in outer_steps)
    smoke_passed = outer_passed and bool(inner_manifest.get("smoke_passed", False))
    clean_checkout_test_performed = any(
        step.step_id == "run_reproducibility_smoke_in_clean_checkout"
        for step in outer_steps
    )
    dependency_install_tested = install_dependencies and any(
        step.step_id == "install_clean_checkout_requirements" and step.passed
        for step in outer_steps
    )
    full_clean_environment_tested = dependency_install_tested and smoke_passed
    artifact_regeneration_step_ids = {
        step_id for step_id, _, _ in ARTIFACT_REGENERATION_COMMANDS
    }
    artifact_regeneration_steps = [
        step for step in outer_steps if step.step_id in artifact_regeneration_step_ids
    ]
    artifact_regeneration_tested = (
        artifact_regeneration
        and len(artifact_regeneration_steps) == len(ARTIFACT_REGENERATION_COMMANDS)
        and all(step.passed for step in artifact_regeneration_steps)
    )
    return {
        "schema_version": 1,
        "result_scope": CLEAN_CHECKOUT_SMOKE_SCOPE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "outputs": {
            "manifest": _display_path(manifest_path),
            "log": _display_path(log_path),
            "doc": _display_path(doc_path),
        },
        "source": {
            "source_repo": str(Path(source_repo)),
            "source_commit": source_commit,
            "source_git_status_line_count": len(source_status_lines),
            "source_git_status_lines": list(source_status_lines),
            "source_dirty_worktree_ignored": bool(source_status_lines),
        },
        "checkout": {
            "checkout_dir": str(Path(checkout_dir)),
            "checkout_retained": checkout_retained,
            "source_tree_cloned": any(
                step.step_id == "git_clone_source_tree" and step.passed
                for step in outer_steps
            ),
        },
        "environment_scope": (
            "clean_source_checkout_fresh_venv_with_dependency_install"
            if install_dependencies
            else "clean_source_checkout_current_python_environment"
        ),
        "python_executable": str(python_executable),
        "install_dependencies_requested": install_dependencies,
        "artifact_regeneration_requested": artifact_regeneration,
        "artifact_regeneration_scope": (
            ARTIFACT_REGENERATION_SCOPE if artifact_regeneration else ""
        ),
        "artifact_regeneration_step_ids": [
            step.step_id for step in artifact_regeneration_steps
        ],
        "outer_step_count": len(outer_steps),
        "outer_steps_passed": outer_passed,
        "outer_failed_step_ids": [step.step_id for step in outer_steps if not step.passed],
        "command_count": inner_command_count,
        "passed_count": inner_passed_count,
        "failed_count": inner_failed_count,
        "smoke_passed": smoke_passed,
        "inner_smoke": {
            "manifest_present": bool(inner_manifest),
            "result_scope": str(inner_manifest.get("result_scope", "")),
            "command_count": inner_command_count,
            "passed_count": inner_passed_count,
            "failed_count": inner_failed_count,
            "failed_command_ids": list(inner_manifest.get("failed_command_ids", [])),
        },
        "acceptance_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "can_mark_complete": False,
        "clean_checkout_test_performed": clean_checkout_test_performed,
        "full_clean_environment_tested": full_clean_environment_tested,
        "dependency_install_tested": dependency_install_tested,
        "artifact_regeneration_tested": artifact_regeneration_tested,
        "formal_acceptance_created": False,
        "claim_boundary": (
            "This is bounded clean source-checkout smoke evidence. It tests the "
            "committed source tree in a fresh clone"
            + (
                " with a fresh virtual environment and dependency installation"
                if install_dependencies
                else " using the current Python environment"
            )
            + ", but it does not "
            "execute the full command ladder"
            + (
                ", and its artifact regeneration is limited to bounded review "
                "and audit artifacts"
                if artifact_regeneration
                else " or artifact-regeneration acceptance protocol"
            )
            + ". It does not create "
            "data/manifests/reproducibility_acceptance.json, and does not "
            "support calibrated real-world or operational routing claims."
        ),
        "required_actions": _required_actions(
            install_dependencies=install_dependencies,
            full_clean_environment_tested=full_clean_environment_tested,
            artifact_regeneration=artifact_regeneration,
            artifact_regeneration_tested=artifact_regeneration_tested,
        ),
        "outer_steps": [step.to_json() for step in outer_steps],
    }


def write_clean_checkout_smoke_outputs(
    *,
    manifest: Mapping[str, Any],
    outer_steps: Sequence[CleanCheckoutStepResult],
    inner_log_text: str,
    manifest_path: str | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
    log_path: str | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_LOG_PATH,
    doc_path: str | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_DOC_PATH,
) -> None:
    """Write manifest, combined JSONL log, and markdown summary."""

    manifest_file = Path(manifest_path)
    log_file = Path(log_path)
    doc_file = Path(doc_path)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    doc_file.parent.mkdir(parents=True, exist_ok=True)

    with manifest_file.open("w", encoding="utf-8") as handle:
        json.dump(dict(manifest), handle, indent=2, sort_keys=True)
        handle.write("\n")
    with log_file.open("w", encoding="utf-8") as handle:
        for step in outer_steps:
            record = {"record_type": "clean_checkout_outer_step", **step.to_json()}
            json.dump(record, handle, sort_keys=True)
            handle.write("\n")
        for line in inner_log_text.splitlines():
            if not line.strip():
                continue
            try:
                inner = json.loads(line)
            except json.JSONDecodeError:
                inner = {"raw": line}
            record = {"record_type": "inner_reproducibility_smoke_command", **inner}
            json.dump(record, handle, sort_keys=True)
            handle.write("\n")
    doc_file.write_text(build_clean_checkout_smoke_markdown(manifest), encoding="utf-8")


def summarize_clean_checkout_smoke(
    path: str | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative summary of clean-checkout smoke evidence."""

    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(manifest_path),
            "result_scope": "",
            "command_count": 0,
            "passed_count": 0,
            "failed_count": 0,
            "smoke_passed": False,
            "acceptance_ready": False,
            "can_mark_complete": False,
            "clean_checkout_test_performed": False,
            "full_clean_environment_tested": False,
            "artifact_regeneration_tested": False,
            "remaining_blockers": [
                "run scripts/run_clean_checkout_smoke.py to create bounded clean-checkout source-tree smoke evidence"
            ],
        }
    value = _read_json_object(manifest_path)
    if not value:
        raise ValueError(f"{manifest_path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(manifest_path),
        "result_scope": str(value.get("result_scope", "")),
        "command_count": int(value.get("command_count", 0)),
        "passed_count": int(value.get("passed_count", 0)),
        "failed_count": int(value.get("failed_count", 0)),
        "smoke_passed": bool(value.get("smoke_passed", False)),
        "acceptance_ready": bool(value.get("acceptance_ready", False)),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "clean_checkout_test_performed": bool(
            value.get("clean_checkout_test_performed", False)
        ),
        "full_clean_environment_tested": bool(
            value.get("full_clean_environment_tested", False)
        ),
        "dependency_install_tested": bool(value.get("dependency_install_tested", False)),
        "artifact_regeneration_tested": bool(
            value.get("artifact_regeneration_tested", False)
        ),
        "artifact_regeneration_scope": str(
            value.get("artifact_regeneration_scope", "")
        ),
        "source_commit": str((value.get("source") or {}).get("source_commit", "")),
        "source_status_lines": list(
            (value.get("source") or {}).get("source_git_status_lines", [])
        ),
        "environment_scope": str(value.get("environment_scope", "")),
        "failed_command_ids": list(
            (value.get("inner_smoke") or {}).get("failed_command_ids", [])
        ),
        "outer_failed_step_ids": list(value.get("outer_failed_step_ids", [])),
        "remaining_blockers": list(value.get("required_actions", [])),
    }


def build_clean_checkout_smoke_markdown(manifest: Mapping[str, Any]) -> str:
    """Return markdown for a clean-checkout smoke manifest."""

    source = manifest.get("source", {})
    inner = manifest.get("inner_smoke", {})
    if not isinstance(source, Mapping):
        source = {}
    if not isinstance(inner, Mapping):
        inner = {}
    lines = [
        "# Clean-Checkout Reproducibility Smoke",
        "",
        "`data/validation/clean_checkout_reproducibility_smoke_manifest.json`",
        "records a bounded clean source-checkout smoke run. It is not formal",
        "reproducibility acceptance and does not close",
        "`data/manifests/reproducibility_acceptance.json`.",
        "",
        "## Summary",
        "",
        f"- Result scope: `{manifest.get('result_scope', '')}`",
        f"- Smoke passed: `{str(manifest.get('smoke_passed', False)).lower()}`",
        f"- Commands passed: {manifest.get('passed_count', 0)} / {manifest.get('command_count', 0)}",
        f"- Clean checkout tested: `{str(manifest.get('clean_checkout_test_performed', False)).lower()}`",
        f"- Full clean environment tested: `{str(manifest.get('full_clean_environment_tested', False)).lower()}`",
        f"- Artifact regeneration tested: `{str(manifest.get('artifact_regeneration_tested', False)).lower()}`",
        f"- Artifact regeneration scope: `{manifest.get('artifact_regeneration_scope', '')}`",
        f"- Source commit: `{source.get('source_commit', '')}`",
        f"- Environment scope: `{manifest.get('environment_scope', '')}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        "",
        "## Outer Steps",
        "",
        "| Step | Status | Return Code |",
        "| --- | --- | --- |",
    ]
    for step in manifest.get("outer_steps", []):
        if not isinstance(step, Mapping):
            continue
        lines.append(
            "| "
            + _md_cell(str(step.get("step_id", "")))
            + " | "
            + _md_cell(str(step.get("status", "")))
            + " | "
            + _md_cell(str(step.get("returncode", "")))
            + " |"
        )
    lines.extend(
        [
            "",
            "## Inner Smoke",
            "",
            f"- Inner scope: `{inner.get('result_scope', '')}`",
            f"- Failed commands: `{', '.join(inner.get('failed_command_ids', []))}`",
            "",
            "## Claim Boundary",
            "",
            str(manifest.get("claim_boundary", "")),
            "",
            "## Required Actions",
            "",
        ]
    )
    for action in manifest.get("required_actions", []):
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def _run_step(
    step_id: str,
    label: str,
    args: Sequence[str],
    *,
    cwd: str | Path,
    timeout_sec: int,
) -> CleanCheckoutStepResult:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            list(args),
            cwd=Path(cwd),
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout_sec,
        )
        duration = time.perf_counter() - started
        return CleanCheckoutStepResult(
            step_id=step_id,
            label=label,
            args=tuple(str(item) for item in args),
            cwd=str(Path(cwd)),
            status="passed" if completed.returncode == 0 else "failed",
            returncode=completed.returncode,
            passed=completed.returncode == 0,
            duration_sec=duration,
            stdout_tail=_tail(completed.stdout),
            stderr_tail=_tail(completed.stderr),
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - started
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return CleanCheckoutStepResult(
            step_id=step_id,
            label=label,
            args=tuple(str(item) for item in args),
            cwd=str(Path(cwd)),
            status="timeout",
            returncode=None,
            passed=False,
            duration_sec=duration,
            stdout_tail=_tail(stdout),
            stderr_tail=_tail(stderr),
        )


def _prepare_checkout_dir(
    *,
    checkout_parent: str | Path | None,
    keep_checkout: bool,
) -> tuple[Path, Any]:
    if checkout_parent is None:
        if keep_checkout:
            checkout_root = Path(
                tempfile.mkdtemp(prefix="transport_system_clean_checkout_")
            )
            return checkout_root / "checkout", lambda: None
        temp_dir = tempfile.TemporaryDirectory(
            prefix="transport_system_clean_checkout_",
            ignore_cleanup_errors=True,
        )
        checkout_dir = Path(temp_dir.name) / "checkout"
        return checkout_dir, temp_dir.cleanup

    parent = Path(checkout_parent).resolve()
    parent.mkdir(parents=True, exist_ok=True)
    checkout_dir = parent / "transport-system-sim-clean-checkout"
    if checkout_dir.exists():
        if not _safe_to_remove_checkout_dir(checkout_dir):
            raise ValueError(f"refusing to remove unsafe checkout path: {checkout_dir}")
        _rmtree_allowing_readonly(checkout_dir)
    return checkout_dir, (
        lambda: None if keep_checkout else _remove_if_safe(checkout_dir)
    )


def _safe_to_remove_checkout_dir(path: Path) -> bool:
    resolved = path.resolve()
    name_ok = resolved.name == "transport-system-sim-clean-checkout"
    root = resolved.anchor
    far_enough = str(resolved) not in {root, str(PROJECT_ROOT.resolve())}
    return name_ok and far_enough


def _venv_python_path(venv_dir: Path) -> Path:
    if sys.platform.startswith("win"):
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _resolve_artifact_regeneration_args(
    args: Sequence[str],
    *,
    python_executable: str | Path,
) -> tuple[str, ...]:
    return tuple(
        str(python_executable) if item == "{python}" else str(item) for item in args
    )


def _required_actions(
    *,
    install_dependencies: bool,
    full_clean_environment_tested: bool,
    artifact_regeneration: bool,
    artifact_regeneration_tested: bool,
) -> list[str]:
    actions = [
        "review whether the bounded clean-checkout smoke is sufficient for the intended review scope",
    ]
    if not install_dependencies or not full_clean_environment_tested:
        actions.append(
            "run a full clean-environment reproduction with dependency installation if publication acceptance requires it"
        )
    if not artifact_regeneration or not artifact_regeneration_tested:
        actions.append(
            "run bounded clean-checkout artifact-regeneration commands before formal reproducibility review"
        )
    actions.extend(
        [
            "preserve full command-ladder logs before formal acceptance",
            "keep data/manifests/reproducibility_acceptance.json absent until a human reviewer records the reproduction scope",
        ]
    )
    return actions


def _remove_if_safe(path: Path) -> None:
    if path.exists():
        if not _safe_to_remove_checkout_dir(path):
            raise ValueError(f"refusing to remove unsafe checkout path: {path}")
        _rmtree_allowing_readonly(path)


def _rmtree_allowing_readonly(path: Path) -> None:
    """Remove a checkout tree even when Git object files are read-only."""

    def _make_writable_and_retry(
        func: Any,
        failing_path: str,
        exc_info: object,
    ) -> None:
        del exc_info
        os.chmod(failing_path, stat.S_IREAD | stat.S_IWRITE)
        func(failing_path)

    shutil.rmtree(path, onerror=_make_writable_and_retry)


def _git_text(args: Sequence[str], *, cwd: Path) -> str:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        errors="replace",
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _git_lines(args: Sequence[str], *, cwd: Path) -> list[str]:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        errors="replace",
    )
    if completed.returncode != 0:
        return []
    return [line.rstrip() for line in completed.stdout.splitlines() if line.strip()]


def _filter_source_status_lines(lines: Sequence[str]) -> list[str]:
    """Drop clean-checkout smoke outputs from source dirtiness checks."""

    filtered: list[str] = []
    for line in lines:
        normalized = _status_path(line)
        if normalized in CLEAN_CHECKOUT_SMOKE_SELF_OUTPUTS:
            continue
        filtered.append(line)
    return filtered


def _status_path(line: str) -> str:
    if len(line) >= 3 and line[2] == " ":
        path = line[3:].strip()
    elif len(line) >= 2 and line[1] == " ":
        path = line[2:].strip()
    else:
        path = line[3:].strip() if len(line) > 3 else ""
    if " -> " in path:
        path = path.split(" -> ", 1)[1].strip()
    return path.strip().strip('"').replace("\\", "/").lstrip("./")


def _read_json_object(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        return {}
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _read_text(path: str | Path) -> str:
    text_path = Path(path)
    if not text_path.exists():
        return ""
    return text_path.read_text(encoding="utf-8")


def _tail(value: str) -> str:
    if len(value) <= MAX_CAPTURE_CHARS:
        return value
    return value[-MAX_CAPTURE_CHARS:]


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "ARTIFACT_REGENERATION_COMMANDS",
    "ARTIFACT_REGENERATION_SCOPE",
    "CLEAN_CHECKOUT_SMOKE_SCOPE",
    "DEFAULT_CLEAN_CHECKOUT_SMOKE_DOC_PATH",
    "DEFAULT_CLEAN_CHECKOUT_SMOKE_LOG_PATH",
    "DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH",
    "CleanCheckoutStepResult",
    "build_clean_checkout_smoke_manifest",
    "build_clean_checkout_smoke_markdown",
    "run_clean_checkout_smoke",
    "summarize_clean_checkout_smoke",
    "write_clean_checkout_smoke_outputs",
]
