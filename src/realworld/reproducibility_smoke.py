"""Current-worktree reproducibility smoke runner.

This module runs a bounded validation ladder for the current working tree. It
does not perform clean-checkout reproduction and never creates
``data/manifests/reproducibility_acceptance.json``.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "reproducibility_smoke_manifest.json"
)
DEFAULT_REPRODUCIBILITY_SMOKE_LOG_PATH = (
    PROJECT_ROOT / "data" / "validation" / "reproducibility_smoke_log.jsonl"
)
DEFAULT_REPRODUCIBILITY_SMOKE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "reproducibility_smoke.md"
)

REPRODUCIBILITY_SMOKE_SCOPE = "current_worktree_smoke_not_clean_checkout"
MAX_CAPTURE_CHARS = 4000


@dataclass(frozen=True)
class SmokeCommand:
    """One bounded smoke command or internal check."""

    command_id: str
    label: str
    args: tuple[str, ...] = ()
    kind: str = "subprocess"
    timeout_sec: int = 300


@dataclass(frozen=True)
class SmokeCommandResult:
    """Result from one smoke command or internal check."""

    command_id: str
    label: str
    kind: str
    args: tuple[str, ...]
    status: str
    returncode: int | None
    passed: bool
    duration_sec: float
    stdout_tail: str
    stderr_tail: str

    def to_json(self) -> dict[str, Any]:
        """Return a JSON-serializable result record."""

        return {
            "command_id": self.command_id,
            "label": self.label,
            "kind": self.kind,
            "args": list(self.args),
            "args_display": _display_command(self.args),
            "status": self.status,
            "returncode": self.returncode,
            "passed": self.passed,
            "duration_sec": round(self.duration_sec, 3),
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }


DEFAULT_SMOKE_COMMANDS: tuple[SmokeCommand, ...] = (
    SmokeCommand(
        "py_compile_acceptance_reproducibility",
        "Compile acceptance and reproducibility modules",
        (
            "{python}",
            "-m",
            "py_compile",
            "src/realworld/acceptance_records.py",
            "src/realworld/acceptance_orchestration.py",
            "src/realworld/acceptance_decision_templates.py",
            "src/realworld/acceptance_blocker_queue.py",
            "src/realworld/acceptance_task_assignments.py",
            "src/realworld/agent_review_path_audit.py",
            "src/realworld/formal_acceptance_guard.py",
            "src/realworld/formal_evidence_path_audit.py",
            "src/realworld/formal_acceptance_package.py",
            "src/realworld/formal_acceptance_evidence_matrix.py",
            "src/realworld/formal_acceptance_pre_review.py",
            "src/realworld/goal_completion_audit.py",
            "src/realworld/publication_readiness.py",
            "src/realworld/ktdb_gtfs_source.py",
            "src/realworld/metro9_capacity_source.py",
            "src/realworld/pilot_region_decision_packet.py",
            "src/realworld/source_context_cache_decision_packet.py",
            "src/realworld/source_provenance_decision_packet.py",
            "src/realworld/manuscript_report_decision_packet.py",
            "src/realworld/graph_scale_method_decision_packet.py",
            "src/realworld/parameter_source_decision_packet.py",
            "src/realworld/road_source_decision_packet.py",
            "src/realworld/rail_source_decision_packet.py",
            "src/realworld/clean_checkout_smoke.py",
            "src/realworld/reproducibility_review_packet.py",
            "src/realworld/reproducibility_decision_packet.py",
            "src/realworld/final_audit_decision_packet.py",
            "src/realworld/reproducibility_smoke.py",
            "scripts/run_acceptance_audit.py",
            "scripts/audit_publication_readiness.py",
            "scripts/run_clean_checkout_smoke.py",
            "scripts/write_reproducibility_decision_packet.py",
            "scripts/write_final_audit_decision_packet.py",
            "scripts/write_acceptance_task_assignments.py",
            "scripts/write_formal_acceptance_evidence_matrix.py",
            "scripts/write_formal_acceptance_pre_review.py",
            "scripts/cache_ktdb_gtfs_source.py",
            "scripts/cache_metro9_capacity_source.py",
            "scripts/write_pilot_region_decision_packet.py",
            "scripts/write_source_context_cache_decision_packet.py",
            "scripts/write_source_provenance_decision_packet.py",
            "scripts/write_manuscript_report_decision_packet.py",
            "scripts/write_graph_scale_method_decision_packet.py",
            "scripts/write_parameter_source_decision_packet.py",
            "scripts/write_road_source_decision_packet.py",
            "scripts/write_rail_source_decision_packet.py",
            "scripts/audit_agent_review_paths.py",
            "scripts/run_reproducibility_smoke.py",
            "scripts/audit_plan_artifacts.py",
            "scripts/audit_formal_evidence_paths.py",
            "scripts/validate_formal_acceptance_package.py",
            "tests/test_realworld_acceptance_records.py",
            "tests/test_realworld_acceptance_orchestration.py",
            "tests/test_realworld_acceptance_decision_templates.py",
            "tests/test_realworld_acceptance_blocker_queue.py",
            "tests/test_realworld_acceptance_task_assignments.py",
            "tests/test_realworld_agent_review_path_audit.py",
            "tests/test_realworld_formal_acceptance_guard.py",
            "tests/test_realworld_formal_evidence_path_audit.py",
            "tests/test_realworld_formal_acceptance_package.py",
            "tests/test_realworld_formal_acceptance_evidence_matrix.py",
            "tests/test_realworld_formal_acceptance_pre_review.py",
            "tests/test_realworld_goal_completion_audit.py",
            "tests/test_realworld_ktdb_gtfs_source.py",
            "tests/test_realworld_metro9_capacity_source.py",
            "tests/test_realworld_pilot_region_decision_packet.py",
            "tests/test_realworld_source_context_cache_decision_packet.py",
            "tests/test_realworld_source_provenance_decision_packet.py",
            "tests/test_realworld_manuscript_report_decision_packet.py",
            "tests/test_realworld_graph_scale_method_decision_packet.py",
            "tests/test_realworld_parameter_source_decision_packet.py",
            "tests/test_realworld_road_source_decision_packet.py",
            "tests/test_realworld_rail_source_decision_packet.py",
            "tests/test_realworld_clean_checkout_smoke.py",
            "tests/test_realworld_final_study_readiness.py",
            "tests/test_realworld_plan_audit.py",
            "tests/test_realworld_publication_readiness.py",
            "tests/test_realworld_reproducibility_review_packet.py",
            "tests/test_realworld_reproducibility_decision_packet.py",
            "tests/test_realworld_final_audit_decision_packet.py",
            "tests/test_realworld_reproducibility_smoke.py",
        ),
    ),
    SmokeCommand(
        "test_acceptance_records",
        "Acceptance record schema tests",
        ("{python}", "tests/test_realworld_acceptance_records.py"),
    ),
    SmokeCommand(
        "test_acceptance_orchestration",
        "Acceptance orchestration tests",
        ("{python}", "tests/test_realworld_acceptance_orchestration.py"),
    ),
    SmokeCommand(
        "test_acceptance_templates",
        "Acceptance decision template tests",
        ("{python}", "tests/test_realworld_acceptance_decision_templates.py"),
    ),
    SmokeCommand(
        "test_acceptance_blocker_queue",
        "Acceptance blocker queue tests",
        ("{python}", "tests/test_realworld_acceptance_blocker_queue.py"),
    ),
    SmokeCommand(
        "test_acceptance_task_assignments",
        "Acceptance task assignment tests",
        ("{python}", "tests/test_realworld_acceptance_task_assignments.py"),
    ),
    SmokeCommand(
        "test_agent_review_path_audit",
        "Agent review path audit tests",
        ("{python}", "tests/test_realworld_agent_review_path_audit.py"),
    ),
    SmokeCommand(
        "test_formal_acceptance_guard",
        "Formal acceptance guard tests",
        ("{python}", "tests/test_realworld_formal_acceptance_guard.py"),
    ),
    SmokeCommand(
        "test_formal_evidence_path_audit",
        "Formal evidence path audit tests",
        ("{python}", "tests/test_realworld_formal_evidence_path_audit.py"),
    ),
    SmokeCommand(
        "test_formal_acceptance_package",
        "Formal acceptance package tests",
        ("{python}", "tests/test_realworld_formal_acceptance_package.py"),
    ),
    SmokeCommand(
        "test_formal_acceptance_evidence_matrix",
        "Formal acceptance evidence matrix tests",
        ("{python}", "tests/test_realworld_formal_acceptance_evidence_matrix.py"),
    ),
    SmokeCommand(
        "test_formal_acceptance_pre_review",
        "Formal acceptance pre-review tests",
        ("{python}", "tests/test_realworld_formal_acceptance_pre_review.py"),
    ),
    SmokeCommand(
        "test_goal_completion_audit",
        "Goal completion audit tests",
        ("{python}", "tests/test_realworld_goal_completion_audit.py"),
    ),
    SmokeCommand(
        "test_clean_checkout_smoke",
        "Clean-checkout smoke evidence tests",
        ("{python}", "tests/test_realworld_clean_checkout_smoke.py"),
    ),
    SmokeCommand(
        "test_final_study_readiness",
        "Final study readiness tests",
        ("{python}", "tests/test_realworld_final_study_readiness.py"),
    ),
    SmokeCommand(
        "test_plan_audit",
        "Plan artifact audit tests",
        ("{python}", "tests/test_realworld_plan_audit.py"),
    ),
    SmokeCommand(
        "test_publication_readiness",
        "Publication readiness audit tests",
        ("{python}", "tests/test_realworld_publication_readiness.py"),
    ),
    SmokeCommand(
        "test_reproducibility_review_packet",
        "Reproducibility review packet tests",
        ("{python}", "tests/test_realworld_reproducibility_review_packet.py"),
    ),
    SmokeCommand(
        "test_reproducibility_decision_packet",
        "Reproducibility decision packet tests",
        ("{python}", "tests/test_realworld_reproducibility_decision_packet.py"),
    ),
    SmokeCommand(
        "test_final_audit_decision_packet",
        "Final-audit decision packet tests",
        ("{python}", "tests/test_realworld_final_audit_decision_packet.py"),
    ),
    SmokeCommand(
        "formal_acceptance_package_audit",
        "Validate formal acceptance package",
        ("{python}", "scripts/validate_formal_acceptance_package.py"),
    ),
    SmokeCommand(
        "formal_evidence_path_audit",
        "Run formal evidence path audit",
        ("{python}", "scripts/audit_formal_evidence_paths.py"),
    ),
    SmokeCommand(
        "agent_review_path_audit",
        "Run agent review path audit",
        ("{python}", "scripts/audit_agent_review_paths.py"),
    ),
    SmokeCommand(
        "final_study_readiness_audit",
        "Run final-study readiness audit",
        ("{python}", "scripts/audit_final_study_readiness.py"),
    ),
    SmokeCommand(
        "acceptance_audit",
        "Refresh sub-agent acceptance audit",
        ("{python}", "scripts/run_acceptance_audit.py"),
    ),
    SmokeCommand(
        "plan_artifact_audit",
        "Run scaffold plan artifact audit",
        ("{python}", "scripts/audit_plan_artifacts.py"),
    ),
    SmokeCommand(
        "runtime_cloned_repo_import_boundary",
        "Check runtime cloned_repo import boundary",
        kind="internal_cloned_repo_import_boundary",
    ),
    SmokeCommand(
        "git_diff_check",
        "Run git diff whitespace check",
        ("git", "diff", "--check"),
        timeout_sec=120,
    ),
)

CLEAN_CHECKOUT_MINIMAL_SMOKE_COMMANDS: tuple[SmokeCommand, ...] = (
    SmokeCommand(
        "py_compile_clean_checkout_evidence",
        "Compile clean-checkout and acceptance evidence modules",
        (
            "{python}",
            "-m",
            "py_compile",
            "src/realworld/clean_checkout_smoke.py",
            "src/realworld/reproducibility_smoke.py",
            "src/realworld/reproducibility_review_packet.py",
            "src/realworld/reproducibility_decision_packet.py",
            "src/realworld/final_audit_decision_packet.py",
            "src/realworld/pilot_region_decision_packet.py",
            "src/realworld/source_context_cache_decision_packet.py",
            "src/realworld/source_provenance_decision_packet.py",
            "src/realworld/manuscript_report_decision_packet.py",
            "src/realworld/graph_scale_method_decision_packet.py",
            "src/realworld/parameter_source_decision_packet.py",
            "src/realworld/road_source_decision_packet.py",
            "src/realworld/rail_source_decision_packet.py",
            "src/realworld/final_study_readiness.py",
            "src/realworld/publication_readiness.py",
            "src/realworld/ktdb_gtfs_source.py",
            "src/realworld/metro9_capacity_source.py",
            "scripts/run_clean_checkout_smoke.py",
            "scripts/run_reproducibility_smoke.py",
            "scripts/write_reproducibility_decision_packet.py",
            "scripts/write_final_audit_decision_packet.py",
            "scripts/cache_ktdb_gtfs_source.py",
            "scripts/cache_metro9_capacity_source.py",
            "scripts/write_pilot_region_decision_packet.py",
            "scripts/write_source_context_cache_decision_packet.py",
            "scripts/write_source_provenance_decision_packet.py",
            "scripts/write_manuscript_report_decision_packet.py",
            "scripts/write_graph_scale_method_decision_packet.py",
            "scripts/write_parameter_source_decision_packet.py",
            "scripts/write_road_source_decision_packet.py",
            "scripts/write_rail_source_decision_packet.py",
            "scripts/validate_formal_acceptance_package.py",
            "scripts/audit_final_study_readiness.py",
            "scripts/audit_publication_readiness.py",
            "tests/test_realworld_clean_checkout_smoke.py",
            "tests/test_realworld_reproducibility_review_packet.py",
            "tests/test_realworld_reproducibility_decision_packet.py",
            "tests/test_realworld_final_audit_decision_packet.py",
            "tests/test_realworld_ktdb_gtfs_source.py",
            "tests/test_realworld_metro9_capacity_source.py",
            "tests/test_realworld_pilot_region_decision_packet.py",
            "tests/test_realworld_source_context_cache_decision_packet.py",
            "tests/test_realworld_source_provenance_decision_packet.py",
            "tests/test_realworld_manuscript_report_decision_packet.py",
            "tests/test_realworld_graph_scale_method_decision_packet.py",
            "tests/test_realworld_parameter_source_decision_packet.py",
            "tests/test_realworld_road_source_decision_packet.py",
            "tests/test_realworld_rail_source_decision_packet.py",
            "tests/test_realworld_final_study_readiness.py",
            "tests/test_realworld_publication_readiness.py",
        ),
        timeout_sec=120,
    ),
    SmokeCommand(
        "test_clean_checkout_smoke",
        "Clean-checkout smoke evidence tests",
        ("{python}", "tests/test_realworld_clean_checkout_smoke.py"),
        timeout_sec=120,
    ),
    SmokeCommand(
        "test_reproducibility_review_packet",
        "Reproducibility review packet tests",
        ("{python}", "tests/test_realworld_reproducibility_review_packet.py"),
        timeout_sec=120,
    ),
    SmokeCommand(
        "test_final_study_readiness",
        "Final study readiness tests",
        ("{python}", "tests/test_realworld_final_study_readiness.py"),
        timeout_sec=180,
    ),
    SmokeCommand(
        "test_publication_readiness",
        "Publication readiness audit tests",
        ("{python}", "tests/test_realworld_publication_readiness.py"),
        timeout_sec=180,
    ),
    SmokeCommand(
        "formal_acceptance_package_audit",
        "Validate formal acceptance package",
        ("{python}", "scripts/validate_formal_acceptance_package.py"),
        timeout_sec=120,
    ),
    SmokeCommand(
        "final_study_readiness_audit",
        "Run final-study readiness audit",
        ("{python}", "scripts/audit_final_study_readiness.py"),
        timeout_sec=120,
    ),
    SmokeCommand(
        "runtime_cloned_repo_import_boundary",
        "Check runtime cloned_repo import boundary",
        kind="internal_cloned_repo_import_boundary",
    ),
    SmokeCommand(
        "git_diff_check",
        "Run git diff whitespace check",
        ("git", "diff", "--check"),
        timeout_sec=120,
    ),
)


def run_reproducibility_smoke(
    *,
    commands: Sequence[SmokeCommand] = DEFAULT_SMOKE_COMMANDS,
    manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH,
    log_path: str | Path = DEFAULT_REPRODUCIBILITY_SMOKE_LOG_PATH,
    doc_path: str | Path = DEFAULT_REPRODUCIBILITY_SMOKE_DOC_PATH,
) -> dict[str, Any]:
    """Run smoke commands, write artifacts, and return the manifest."""

    results = [run_smoke_command(command) for command in commands]
    return write_reproducibility_smoke_outputs(
        results=results,
        manifest_path=manifest_path,
        log_path=log_path,
        doc_path=doc_path,
    )


def run_smoke_command(command: SmokeCommand) -> SmokeCommandResult:
    """Run one smoke command or internal check."""

    started = time.perf_counter()
    if command.kind == "internal_cloned_repo_import_boundary":
        hits = _cloned_repo_import_hits((PROJECT_ROOT / "src", PROJECT_ROOT / "tests", PROJECT_ROOT / "scripts"))
        stdout = "hits=0" if not hits else "\n".join(hits)
        duration = time.perf_counter() - started
        return SmokeCommandResult(
            command_id=command.command_id,
            label=command.label,
            kind=command.kind,
            args=(),
            status="passed" if not hits else "failed",
            returncode=0 if not hits else 1,
            passed=not hits,
            duration_sec=duration,
            stdout_tail=_tail(stdout),
            stderr_tail="",
        )
    if command.kind != "subprocess":
        raise ValueError(f"unsupported smoke command kind: {command.kind}")

    args = _resolve_args(command.args)
    try:
        completed = subprocess.run(
            args,
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=command.timeout_sec,
        )
        duration = time.perf_counter() - started
        return SmokeCommandResult(
            command_id=command.command_id,
            label=command.label,
            kind=command.kind,
            args=tuple(command.args),
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
        return SmokeCommandResult(
            command_id=command.command_id,
            label=command.label,
            kind=command.kind,
            args=tuple(command.args),
            status="timeout",
            returncode=None,
            passed=False,
            duration_sec=duration,
            stdout_tail=_tail(stdout),
            stderr_tail=_tail(stderr),
        )


def build_reproducibility_smoke_manifest(
    *,
    results: Sequence[SmokeCommandResult],
    manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH,
    log_path: str | Path = DEFAULT_REPRODUCIBILITY_SMOKE_LOG_PATH,
    doc_path: str | Path = DEFAULT_REPRODUCIBILITY_SMOKE_DOC_PATH,
) -> dict[str, Any]:
    """Build a non-acceptance smoke manifest from command results."""

    passed_count = sum(1 for result in results if result.passed)
    failed_count = len(results) - passed_count
    smoke_passed = failed_count == 0 and bool(results)
    return {
        "schema_version": 1,
        "result_scope": REPRODUCIBILITY_SMOKE_SCOPE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "outputs": {
            "manifest": _display_path(manifest_path),
            "log": _display_path(log_path),
            "doc": _display_path(doc_path),
        },
        "command_count": len(results),
        "passed_count": passed_count,
        "failed_count": failed_count,
        "smoke_passed": smoke_passed,
        "acceptance_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "can_mark_complete": False,
        "clean_checkout_test_performed": False,
        "formal_acceptance_created": False,
        "commands": [result.to_json() for result in results],
        "failed_command_ids": [
            result.command_id for result in results if not result.passed
        ],
        "claim_boundary": (
            "This is a bounded current-worktree smoke run. It is not a "
            "fresh-clone or clean-checkout reproduction, does not create "
            "data/manifests/reproducibility_acceptance.json, and does not "
            "support calibrated real-world or operational routing claims."
        ),
        "required_actions": [
            "run clean-checkout reproduction from a fresh clone or exported package",
            "preserve command logs for the full validation ladder and artifact regeneration",
            "review the scaffold-only reproducibility manifest scope",
            "resolve dirty or untracked worktree state before claiming package reproducibility",
            "create data/manifests/reproducibility_acceptance.json only after human review accepts the clean-checkout package",
        ],
    }


def write_reproducibility_smoke_outputs(
    *,
    results: Sequence[SmokeCommandResult],
    manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH,
    log_path: str | Path = DEFAULT_REPRODUCIBILITY_SMOKE_LOG_PATH,
    doc_path: str | Path = DEFAULT_REPRODUCIBILITY_SMOKE_DOC_PATH,
) -> dict[str, Any]:
    """Write smoke manifest, JSONL command log, and markdown summary."""

    manifest = build_reproducibility_smoke_manifest(
        results=results,
        manifest_path=manifest_path,
        log_path=log_path,
        doc_path=doc_path,
    )
    manifest_file = Path(manifest_path)
    log_file = Path(log_path)
    doc_file = Path(doc_path)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    doc_file.parent.mkdir(parents=True, exist_ok=True)

    with log_file.open("w", encoding="utf-8") as handle:
        for result in results:
            json.dump(result.to_json(), handle, sort_keys=True)
            handle.write("\n")
    with manifest_file.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    doc_file.write_text(build_reproducibility_smoke_markdown(manifest), encoding="utf-8")
    return manifest


def summarize_reproducibility_smoke(
    path: str | Path = DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative summary of the latest smoke manifest."""

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
            "remaining_blockers": [
                "run scripts/run_reproducibility_smoke.py to create current-worktree smoke evidence"
            ],
        }
    with manifest_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
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
        "failed_command_ids": list(value.get("failed_command_ids", [])),
        "remaining_blockers": list(value.get("required_actions", [])),
    }


def build_reproducibility_smoke_markdown(manifest: Mapping[str, Any]) -> str:
    """Return markdown for a smoke manifest."""

    lines = [
        "# Reproducibility Smoke Run",
        "",
        "`data/validation/reproducibility_smoke_manifest.json` records a bounded",
        "current-worktree smoke run. It is not a clean-checkout reproduction and",
        "does not close `data/manifests/reproducibility_acceptance.json`.",
        "",
        "## Summary",
        "",
        f"- Result scope: `{manifest.get('result_scope', '')}`",
        f"- Smoke passed: `{str(manifest.get('smoke_passed', False)).lower()}`",
        f"- Commands passed: {manifest.get('passed_count', 0)} / {manifest.get('command_count', 0)}",
        f"- Clean checkout tested: `{str(manifest.get('clean_checkout_test_performed', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        "",
        "## Command Results",
        "",
        "| Command | Status | Return Code |",
        "| --- | --- | --- |",
    ]
    for command in manifest.get("commands", []):
        if not isinstance(command, Mapping):
            continue
        lines.append(
            "| "
            + _md_cell(str(command.get("command_id", "")))
            + " | "
            + _md_cell(str(command.get("status", "")))
            + " | "
            + _md_cell(str(command.get("returncode", "")))
            + " |"
        )
    lines.extend(
        [
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


def _cloned_repo_import_hits(scan_dirs: Sequence[Path]) -> list[str]:
    hits: list[str] = []
    for directory in scan_dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.py")):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="utf-8", errors="ignore")
            try:
                tree = ast.parse(text, filename=str(path))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if module == "cloned_repo" or module.startswith("cloned_repo."):
                        hits.append(f"{_display_path(path)}:{node.lineno}")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.name
                        if name == "cloned_repo" or name.startswith("cloned_repo."):
                            hits.append(f"{_display_path(path)}:{node.lineno}")
    return hits


def _resolve_args(args: Sequence[str]) -> list[str]:
    return [sys.executable if item == "{python}" else item for item in args]


def _display_command(args: Sequence[str]) -> str:
    display_args = [
        ".\\.venv\\Scripts\\python" if item == "{python}" else item for item in args
    ]
    return subprocess.list2cmdline(display_args)


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
    "DEFAULT_REPRODUCIBILITY_SMOKE_DOC_PATH",
    "DEFAULT_REPRODUCIBILITY_SMOKE_LOG_PATH",
    "DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH",
    "DEFAULT_SMOKE_COMMANDS",
    "CLEAN_CHECKOUT_MINIMAL_SMOKE_COMMANDS",
    "REPRODUCIBILITY_SMOKE_SCOPE",
    "SmokeCommand",
    "SmokeCommandResult",
    "build_reproducibility_smoke_manifest",
    "build_reproducibility_smoke_markdown",
    "run_reproducibility_smoke",
    "run_smoke_command",
    "summarize_reproducibility_smoke",
    "write_reproducibility_smoke_outputs",
]
