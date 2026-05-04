"""Reproducibility review packet generation.

This module creates a deterministic review worksheet for the clean-checkout
reproducibility gate. It does not perform or accept full clean-checkout
reproduction, and it never writes ``reproducibility_acceptance.json``.
"""

from __future__ import annotations

import csv
import ast
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.clean_checkout_smoke import (
    DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
    summarize_clean_checkout_smoke,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPRODUCIBILITY_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "reproducibility_manifest.json"
)
DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "reproducibility_acceptance.json"
)
DEFAULT_REPRODUCIBILITY_PACKAGE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "reproducibility_package.md"
)
DEFAULT_GOAL_AUDIT_PATH = PROJECT_ROOT / "docs" / "current_goal_completion_audit.md"
DEFAULT_REPRODUCIBILITY_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "reproducibility_review_packet.csv"
)
DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "reproducibility_review_manifest.json"
)
DEFAULT_CLEAN_CHECKOUT_SMOKE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "clean_checkout_reproducibility_smoke.md"
)

REPRODUCIBILITY_REVIEW_PACKET_SCOPE = (
    "reproducibility_review_packet_not_reproducibility_acceptance"
)
REPRODUCIBILITY_REVIEW_COLUMNS: tuple[str, ...] = (
    "category_id",
    "check_name",
    "artifact_path",
    "artifact_present",
    "status",
    "status_detail",
    "review_required",
    "acceptance_ready",
    "publication_ready",
    "required_action",
    "evidence_paths",
    "claim_boundary",
)
DEFAULT_SCAN_DIRS: tuple[Path, ...] = (
    PROJECT_ROOT / "src",
    PROJECT_ROOT / "tests",
    PROJECT_ROOT / "scripts",
)


def build_reproducibility_review_rows(
    *,
    reproducibility_manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
    reproducibility_acceptance_path: str | Path = DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH,
    reproducibility_package_doc_path: str | Path = DEFAULT_REPRODUCIBILITY_PACKAGE_DOC_PATH,
    goal_audit_path: str | Path = DEFAULT_GOAL_AUDIT_PATH,
    clean_checkout_smoke_manifest_path: str
    | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
    git_status_lines: Sequence[str] | None = None,
    scan_dirs: Sequence[str | Path] = DEFAULT_SCAN_DIRS,
) -> list[dict[str, str]]:
    """Build conservative reproducibility review rows."""

    manifest = _read_json_object(reproducibility_manifest_path)
    package_text = _read_text(reproducibility_package_doc_path)
    goal_text = _read_text(goal_audit_path)
    status_lines = (
        tuple(git_status_lines)
        if git_status_lines is not None
        else tuple(_git_status_lines())
    )
    import_hits = _cloned_repo_import_hits(scan_dirs)
    clean_checkout_smoke = summarize_clean_checkout_smoke(
        clean_checkout_smoke_manifest_path
    )

    return [
        _manifest_scope_row(reproducibility_manifest_path, manifest),
        _formal_acceptance_row(reproducibility_acceptance_path),
        _git_worktree_row(status_lines),
        _untracked_artifact_row(status_lines),
        _command_ladder_row(reproducibility_manifest_path, manifest),
        _cloned_repo_import_row(import_hits),
        _clean_checkout_smoke_row(
            clean_checkout_smoke_manifest_path,
            clean_checkout_smoke,
        ),
        _clean_checkout_scope_row(
            reproducibility_package_doc_path,
            goal_audit_path,
            package_text=package_text,
            goal_text=goal_text,
        ),
    ]


def write_reproducibility_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_REPRODUCIBILITY_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH,
    reproducibility_manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
    reproducibility_acceptance_path: str | Path = DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH,
    clean_checkout_smoke_manifest_path: str
    | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
    git_status_lines: Sequence[str] | None = None,
    scan_dirs: Sequence[str | Path] = DEFAULT_SCAN_DIRS,
) -> dict[str, Any]:
    """Write the reproducibility review worksheet and manifest."""

    output = Path(output_path)
    manifest_output = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=REPRODUCIBILITY_REVIEW_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    status_lines = (
        tuple(git_status_lines)
        if git_status_lines is not None
        else tuple(_git_status_lines())
    )
    import_hits = _cloned_repo_import_hits(scan_dirs)
    source_manifest = _read_json_object(reproducibility_manifest_path)
    clean_checkout_smoke = summarize_clean_checkout_smoke(
        clean_checkout_smoke_manifest_path
    )
    status_counts = _counts(row.get("status", "") for row in rows)
    command_count, validation_command_count = _command_counts(source_manifest)
    modified_count = _git_status_prefix_count(status_lines, prefixes=("M", "A", "D", "R", "C"))
    untracked_count = _git_status_prefix_count(status_lines, prefixes=("??",))

    value = {
        "schema_version": 1,
        "result_scope": REPRODUCIBILITY_REVIEW_PACKET_SCOPE,
        "input_artifact_paths": {
            "reproducibility_manifest": _display_path(reproducibility_manifest_path),
            "reproducibility_acceptance": _display_path(reproducibility_acceptance_path),
        },
        "outputs": {
            "reproducibility_review_packet": _display_path(output),
            "manifest": _display_path(manifest_output),
        },
        "row_count": len(rows),
        "category_ids": [str(row.get("category_id", "")) for row in rows],
        "status_counts": status_counts,
        "review_required": True,
        "acceptance_ready": False,
        "publication_ready": False,
        "acceptance_gate_closure_candidate_count": 0,
        "reproducibility_acceptance_record_present": Path(
            reproducibility_acceptance_path
        ).exists(),
        "reproducibility_manifest_scope": str(source_manifest.get("scope", "")),
        "command_count": command_count,
        "validation_command_count": validation_command_count,
        "git_status_line_count": len(status_lines),
        "git_modified_or_staged_count": modified_count,
        "git_untracked_count": untracked_count,
        "no_runtime_cloned_repo_imports": len(import_hits) == 0,
        "runtime_cloned_repo_import_hits": import_hits,
        "clean_checkout_smoke_present": clean_checkout_smoke["manifest_present"],
        "clean_checkout_smoke_passed": clean_checkout_smoke["smoke_passed"],
        "clean_checkout_smoke_scope": clean_checkout_smoke["result_scope"],
        "clean_checkout_smoke_command_count": clean_checkout_smoke["command_count"],
        "clean_checkout_test_performed": clean_checkout_smoke[
            "clean_checkout_test_performed"
        ],
        "full_clean_environment_tested": clean_checkout_smoke[
            "full_clean_environment_tested"
        ],
        "claim_boundary": (
            "This packet records clean-checkout reproducibility review status. "
            "It does not create data/manifests/reproducibility_acceptance.json, "
            "does not prove full clean-environment reproduction, and does not "
            "support operational routing or calibrated real-world claims."
        ),
        "review_items": [
            "commit or otherwise package required untracked artifacts before claiming clean-checkout reproducibility",
            "run clean-checkout validation from a fresh clone or exported package and preserve command logs",
            "decide whether bounded current-Python clean-checkout smoke is sufficient or whether a clean-environment dependency reinstall is required",
            "review manifest command counts and artifact regeneration scope",
            "keep cloned_repo snapshots out of runtime imports",
            "record any accepted decision only in data/manifests/reproducibility_acceptance.json",
        ],
    }
    with manifest_output.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _manifest_scope_row(path: str | Path, manifest: Mapping[str, Any]) -> dict[str, str]:
    scope = str(manifest.get("scope", "")).strip()
    present = Path(path).exists()
    if not present:
        status = "missing_reproducibility_manifest"
    elif "scaffold" in scope.lower():
        status = "blocked_scaffold_only_manifest_scope"
    else:
        status = "ready_for_review_non_scaffold_manifest_scope"
    return _review_row(
        category_id="reproducibility_manifest_scope",
        check_name="Reproducibility manifest scope",
        artifact_path=path,
        artifact_present=present,
        status=status,
        status_detail=f"scope={scope or '<missing>'}",
        required_action=(
            "Replace scaffold-only manifest scope with a reviewed final-study "
            "reproduction package before acceptance."
        ),
        evidence_paths=[path],
    )


def _formal_acceptance_row(path: str | Path) -> dict[str, str]:
    present = Path(path).exists()
    return _review_row(
        category_id="formal_reproducibility_acceptance_record",
        check_name="Formal reproducibility acceptance record",
        artifact_path=path,
        artifact_present=present,
        status=(
            "review_required_existing_acceptance_record_is_separate"
            if present
            else "blocked_no_reproducibility_acceptance_record"
        ),
        status_detail=(
            "The acceptance record exists and must be validated separately."
            if present
            else "No formal reproducibility acceptance record is present."
        ),
        required_action=(
            "Create reproducibility_acceptance.json only after reviewed "
            "clean-checkout validation, artifact regeneration, manifest path "
            "review, command-count review, and not-operational claim boundary."
        ),
        evidence_paths=[path],
    )


def _git_worktree_row(status_lines: Sequence[str]) -> dict[str, str]:
    modified_count = _git_status_prefix_count(status_lines, prefixes=("M", "A", "D", "R", "C"))
    untracked_count = _git_status_prefix_count(status_lines, prefixes=("??",))
    clean = not status_lines
    return _review_row(
        category_id="git_worktree_state",
        check_name="Git worktree cleanliness",
        artifact_path=".",
        artifact_present=True,
        status="ready_for_review_clean_worktree" if clean else "blocked_dirty_worktree",
        status_detail=(
            f"status_lines={len(status_lines)}; "
            f"modified_or_staged={modified_count}; untracked={untracked_count}"
        ),
        required_action=(
            "Resolve, stage, commit, or intentionally document all required "
            "worktree changes before clean-checkout reproduction."
        ),
        evidence_paths=["git status --short"],
    )


def _untracked_artifact_row(status_lines: Sequence[str]) -> dict[str, str]:
    untracked = sorted(
        _git_status_path(line)
        for line in status_lines
        if line.startswith("?? ")
    )
    candidate_count = len(
        [
            path
            for path in untracked
            if path.startswith(("data/", "docs/", "results/", "schemas/", "agents/", "src/realworld/", "scripts/", "tests/"))
        ]
    )
    return _review_row(
        category_id="untracked_required_artifact_risk",
        check_name="Untracked artifact risk",
        artifact_path=".",
        artifact_present=True,
        status=(
            "blocked_untracked_reproducibility_artifacts"
            if candidate_count
            else "ready_for_review_no_untracked_reproducibility_artifacts"
        ),
        status_detail=(
            f"untracked_total={len(untracked)}; "
            f"untracked_candidate_reproducibility_artifacts={candidate_count}"
        ),
        required_action=(
            "Ensure required generated code, data, docs, scripts, tests, and "
            "manifests are included in the package before clean-checkout tests."
        ),
        evidence_paths=["git status --short"],
    )


def _command_ladder_row(
    path: str | Path,
    manifest: Mapping[str, Any],
) -> dict[str, str]:
    command_count, validation_command_count = _command_counts(manifest)
    ready = command_count > 0 and validation_command_count > 0
    return _review_row(
        category_id="validation_command_ladder",
        check_name="Validation command ladder",
        artifact_path=path,
        artifact_present=Path(path).exists(),
        status=(
            "ready_for_review_command_ladder_present"
            if ready
            else "blocked_missing_validation_command_ladder"
        ),
        status_detail=(
            f"commands={command_count}; validation_commands={validation_command_count}"
        ),
        required_action=(
            "Review command counts, command scope, and artifact-regeneration "
            "coverage before recording reproducibility acceptance."
        ),
        evidence_paths=[path],
    )


def _cloned_repo_import_row(import_hits: Sequence[str]) -> dict[str, str]:
    return _review_row(
        category_id="runtime_cloned_repo_import_boundary",
        check_name="Runtime cloned_repo import boundary",
        artifact_path="src; tests; scripts",
        artifact_present=True,
        status=(
            "ready_for_review_no_cloned_repo_runtime_imports"
            if not import_hits
            else "blocked_runtime_cloned_repo_imports"
        ),
        status_detail=(
            "hits=0" if not import_hits else "hits=" + " | ".join(import_hits[:20])
        ),
        required_action=(
            "Remove runtime cloned_repo imports or document why the import "
            "boundary has changed before reproducibility acceptance."
        ),
        evidence_paths=["src", "tests", "scripts"],
    )


def _clean_checkout_smoke_row(
    path: str | Path,
    summary: Mapping[str, Any],
) -> dict[str, str]:
    present = bool(summary.get("manifest_present", False))
    passed = bool(summary.get("smoke_passed", False))
    full_environment = bool(summary.get("full_clean_environment_tested", False))
    if not present:
        status = "blocked_clean_checkout_smoke_not_run"
    elif not passed:
        status = "blocked_clean_checkout_smoke_failed"
    elif full_environment:
        status = "ready_for_review_full_clean_checkout_smoke"
    else:
        status = "ready_for_review_bounded_clean_checkout_smoke"
    return _review_row(
        category_id="bounded_clean_checkout_smoke",
        check_name="Bounded clean-checkout source-tree smoke",
        artifact_path=path,
        artifact_present=present,
        status=status,
        status_detail=(
            f"scope={summary.get('result_scope', '') or '<missing>'}; "
            f"passed={_bool_text(passed)}; "
            f"commands={summary.get('command_count', 0)}; "
            f"full_clean_environment_tested={_bool_text(full_environment)}; "
            f"source_commit={summary.get('source_commit', '')}"
        ),
        required_action=(
            "Use this as bounded source-checkout evidence only. Review whether "
            "a full clean-environment reproduction with dependency installation "
            "and artifact regeneration is required before acceptance."
        ),
        evidence_paths=[path, DEFAULT_CLEAN_CHECKOUT_SMOKE_DOC_PATH],
    )


def _clean_checkout_scope_row(
    package_doc_path: str | Path,
    goal_audit_path: str | Path,
    *,
    package_text: str,
    goal_text: str,
) -> dict[str, str]:
    package_mentions_scaffold = "scaffold" in package_text.lower()
    goal_blocks_final = "final-study ready: `false`" in goal_text.lower()
    return _review_row(
        category_id="clean_checkout_execution_scope",
        check_name="Clean-checkout execution scope",
        artifact_path=package_doc_path,
        artifact_present=Path(package_doc_path).exists(),
        status="blocked_full_clean_checkout_not_run",
        status_detail=(
            f"package_mentions_scaffold={_bool_text(package_mentions_scaffold)}; "
            f"goal_audit_blocks_final={_bool_text(goal_blocks_final)}"
        ),
        required_action=(
            "Run a fresh-clone or exported-package reproduction and preserve "
            "logs. If only smoke scope is feasible, keep full reproduction "
            "blocked and document the smoke boundary."
        ),
        evidence_paths=[package_doc_path, goal_audit_path],
    )


def _review_row(
    *,
    category_id: str,
    check_name: str,
    artifact_path: str | Path,
    artifact_present: bool,
    status: str,
    status_detail: str,
    required_action: str,
    evidence_paths: Sequence[str | Path],
) -> dict[str, str]:
    return {
        "category_id": category_id,
        "check_name": check_name,
        "artifact_path": _display_path(artifact_path),
        "artifact_present": _bool_text(artifact_present),
        "status": status,
        "status_detail": status_detail,
        "review_required": "true",
        "acceptance_ready": "false",
        "publication_ready": "false",
        "required_action": required_action,
        "evidence_paths": "; ".join(_display_path(path) for path in evidence_paths),
        "claim_boundary": REPRODUCIBILITY_REVIEW_PACKET_SCOPE,
    }


def _git_status_lines() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return ["!! git status unavailable"]
    if result.returncode != 0:
        return [f"!! git status failed: {result.stderr.strip()}"]
    return [line for line in result.stdout.splitlines() if line.strip()]


def _cloned_repo_import_hits(scan_dirs: Sequence[str | Path]) -> list[str]:
    hits: list[str] = []
    for raw_dir in scan_dirs:
        directory = Path(raw_dir)
        if not directory.is_absolute():
            directory = PROJECT_ROOT / directory
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


def _command_counts(manifest: Mapping[str, Any]) -> tuple[int, int]:
    commands = manifest.get("commands", [])
    validation_commands = manifest.get("validation_commands", [])
    return len(_flatten_commands(commands)), len(_flatten_commands(validation_commands))


def _flatten_commands(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if not isinstance(value, Sequence):
        return []
    output: list[str] = []
    for item in value:
        output.extend(_flatten_commands(item))
    return output


def _git_status_prefix_count(
    lines: Sequence[str],
    *,
    prefixes: Sequence[str],
) -> int:
    count = 0
    for line in lines:
        status = line[:2]
        if "??" in prefixes and status == "??":
            count += 1
            continue
        if any(prefix in status for prefix in prefixes if prefix != "??"):
            count += 1
    return count


def _git_status_path(line: str) -> str:
    return line[3:].replace("\\", "/") if len(line) > 3 else ""


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


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _bool_text(value: object) -> str:
    return str(bool(value)).lower()


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH",
    "DEFAULT_REPRODUCIBILITY_REVIEW_PACKET_PATH",
    "REPRODUCIBILITY_REVIEW_COLUMNS",
    "REPRODUCIBILITY_REVIEW_PACKET_SCOPE",
    "build_reproducibility_review_rows",
    "write_reproducibility_review_packet",
]
