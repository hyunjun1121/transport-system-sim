"""Git-tracked artifact audit for clean-checkout reproducibility.

This audit makes the clean-checkout blocker concrete by listing current
worktree changes that a fresh checkout of ``HEAD`` would not contain. It is a
packaging/reproducibility aid only and never accepts the reproducibility gate.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRACKED_ARTIFACT_AUDIT_CSV = (
    PROJECT_ROOT / "data" / "validation" / "tracked_artifact_audit.csv"
)
DEFAULT_TRACKED_ARTIFACT_AUDIT_MANIFEST = (
    PROJECT_ROOT / "data" / "validation" / "tracked_artifact_audit_manifest.json"
)
DEFAULT_TRACKED_ARTIFACT_AUDIT_DOC = (
    PROJECT_ROOT / "docs" / "tracked_artifact_audit.md"
)
DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_CSV = (
    PROJECT_ROOT / "data" / "validation" / "dirty_worktree_classification.csv"
)
DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_MANIFEST = (
    PROJECT_ROOT / "data" / "validation" / "dirty_worktree_classification_manifest.json"
)
DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_DOC = (
    PROJECT_ROOT / "docs" / "dirty_worktree_classification.md"
)
TRACKED_ARTIFACT_SELF_OUTPUTS: frozenset[str] = frozenset(
    {
        "data/validation/tracked_artifact_audit.csv",
        "data/validation/tracked_artifact_audit_manifest.json",
        "data/validation/dirty_worktree_classification.csv",
        "data/validation/dirty_worktree_classification_manifest.json",
        "docs/tracked_artifact_audit.md",
        "docs/dirty_worktree_classification.md",
    }
)
PACKAGE_HANDOFF_SELF_OUTPUTS: frozenset[str] = frozenset(
    {
        "data/manifests/review_package_build_manifest.json",
        "data/manifests/review_package_inventory.csv",
        "data/manifests/review_package_inventory_manifest.json",
        "data/manifests/review_package_path_audit.json",
        "docs/review_package_build.md",
        "docs/review_package_inventory.md",
        "docs/review_package_path_audit.md",
    }
)
TRACKED_ARTIFACT_CLAIM_BOUNDARY = (
    "This audit checks whether current changed artifacts would be present in a "
    "clean checkout of the current Git HEAD. It does not commit files, approve "
    "reproducibility, validate evidence quality, or close final-study gates."
)
TRACKED_ARTIFACT_FIELDS: tuple[str, ...] = (
    "path",
    "git_status",
    "artifact_category",
    "clean_checkout_risk",
    "required_action",
    "claim_boundary",
)
DIRTY_WORKTREE_CLASSIFICATION_CLAIM_BOUNDARY = (
    "This ledger classifies current dirty and untracked worktree paths for "
    "sprint-safety planning. It does not commit files, clean the worktree, "
    "approve reproducibility, permit generated-output promotion, or close "
    "final-study gates."
)
DIRTY_WORKTREE_CLASSIFICATION_FIELDS: tuple[str, ...] = (
    "path",
    "git_status",
    "artifact_category",
    "owner",
    "phase",
    "evidence_status",
    "allowed_next_action",
    "cleanup_allowed",
    "new_generated_output_allowed",
    "classification_status",
    "claim_boundary",
)
REPRODUCIBILITY_PREFIXES: tuple[str, ...] = (
    "agents/",
    "data/",
    "docs/",
    "results/realworld_pilot/",
    "schemas/",
    "scripts/",
    "src/realworld/",
    "tests/test_",
    "paper/",
)
REPRODUCIBILITY_FILES: frozenset[str] = frozenset(
    {
        "README.md",
        "AGENTS.md",
        "agents.md",
        "plan.md",
        "status.md",
        "report_draft.md",
        "report.docx",
        "requirements.txt",
        ".gitignore",
    }
)


@dataclass(frozen=True)
class TrackedArtifactRow:
    """One changed file or folder relevant to clean-checkout packaging."""

    path: str
    git_status: str
    artifact_category: str
    clean_checkout_risk: str
    required_action: str
    claim_boundary: str = TRACKED_ARTIFACT_CLAIM_BOUNDARY

    def to_csv_row(self) -> dict[str, str]:
        return {
            "path": self.path,
            "git_status": self.git_status,
            "artifact_category": self.artifact_category,
            "clean_checkout_risk": self.clean_checkout_risk,
            "required_action": self.required_action,
            "claim_boundary": self.claim_boundary,
        }


@dataclass(frozen=True)
class DirtyWorktreeClassificationRow:
    """One dirty or untracked path classified before new sprint work."""

    path: str
    git_status: str
    artifact_category: str
    owner: str
    phase: str
    evidence_status: str
    allowed_next_action: str
    cleanup_allowed: str
    new_generated_output_allowed: str
    classification_status: str
    claim_boundary: str = DIRTY_WORKTREE_CLASSIFICATION_CLAIM_BOUNDARY

    def to_csv_row(self) -> dict[str, str]:
        return {
            "path": self.path,
            "git_status": self.git_status,
            "artifact_category": self.artifact_category,
            "owner": self.owner,
            "phase": self.phase,
            "evidence_status": self.evidence_status,
            "allowed_next_action": self.allowed_next_action,
            "cleanup_allowed": self.cleanup_allowed,
            "new_generated_output_allowed": self.new_generated_output_allowed,
            "classification_status": self.classification_status,
            "claim_boundary": self.claim_boundary,
        }


def build_tracked_artifact_rows(
    *,
    git_status_lines: Sequence[str] | None = None,
) -> list[dict[str, str]]:
    """Return current changed artifacts that matter for clean checkout."""

    lines = tuple(git_status_lines) if git_status_lines is not None else _git_status()
    rows: list[TrackedArtifactRow] = []
    for line in lines:
        parsed = _parse_status_line(line)
        if parsed is None:
            continue
        status, path = parsed
        normalized = _normalize_path(path)
        if normalized in TRACKED_ARTIFACT_SELF_OUTPUTS:
            continue
        if normalized in PACKAGE_HANDOFF_SELF_OUTPUTS:
            continue
        if not _is_reproducibility_artifact(normalized):
            continue
        rows.append(
            TrackedArtifactRow(
                path=normalized,
                git_status=status,
                artifact_category=_artifact_category(normalized),
                clean_checkout_risk=_clean_checkout_risk(status),
                required_action=_required_action(status),
            )
        )
    return [row.to_csv_row() for row in rows]


def build_dirty_worktree_classification_rows(
    *,
    git_status_lines: Sequence[str] | None = None,
) -> list[dict[str, str]]:
    """Return a classification row for every dirty or untracked worktree path."""

    lines = (
        tuple(git_status_lines)
        if git_status_lines is not None
        else _git_status(include_untracked_all=True)
    )
    rows: list[DirtyWorktreeClassificationRow] = []
    for line in lines:
        if line.startswith("!! "):
            rows.append(_dirty_worktree_git_status_failure_row(line))
            continue
        parsed = _parse_status_line(line)
        if parsed is None:
            continue
        status, path = parsed
        normalized = _normalize_path(path)
        if not normalized:
            continue
        category = _artifact_category(normalized)
        owner = _classification_owner(normalized, category)
        phase = _classification_phase(normalized, category)
        evidence_status = _classification_evidence_status(normalized, category, status)
        allowed_next_action = _classification_next_action(
            normalized,
            category,
            status,
            evidence_status,
        )
        rows.append(
            DirtyWorktreeClassificationRow(
                path=normalized,
                git_status=status,
                artifact_category=category,
                owner=owner,
                phase=phase,
                evidence_status=evidence_status,
                allowed_next_action=allowed_next_action,
                cleanup_allowed="no_destructive_cleanup_without_explicit_target_review",
                new_generated_output_allowed="no",
                classification_status="classified_requires_review",
            )
        )
    return [row.to_csv_row() for row in rows]


def write_tracked_artifact_audit(
    *,
    rows: Sequence[Mapping[str, str]] | None = None,
    output_path: str | Path = DEFAULT_TRACKED_ARTIFACT_AUDIT_CSV,
    manifest_path: str | Path = DEFAULT_TRACKED_ARTIFACT_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_TRACKED_ARTIFACT_AUDIT_DOC,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown tracked-artifact audit outputs."""

    audit_rows = list(rows) if rows is not None else build_tracked_artifact_rows()
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACKED_ARTIFACT_FIELDS)
        writer.writeheader()
        writer.writerows(audit_rows)

    summary = summarize_tracked_artifact_rows(audit_rows)
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": TRACKED_ARTIFACT_CLAIM_BOUNDARY,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "can_mark_complete": False,
            "clean_checkout_reproducibility_ready": False,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    doc.write_text(build_tracked_artifact_audit_markdown(summary, audit_rows), encoding="utf-8")
    return summary


def write_dirty_worktree_classification(
    *,
    rows: Sequence[Mapping[str, str]] | None = None,
    output_path: str | Path = DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_CSV,
    manifest_path: str | Path = DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_MANIFEST,
    doc_path: str | Path = DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_DOC,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown dirty-worktree classification outputs."""

    classification_rows = (
        list(rows) if rows is not None else build_dirty_worktree_classification_rows()
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DIRTY_WORKTREE_CLASSIFICATION_FIELDS)
        writer.writeheader()
        writer.writerows(classification_rows)

    summary = summarize_dirty_worktree_classification_rows(classification_rows)
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": DIRTY_WORKTREE_CLASSIFICATION_CLAIM_BOUNDARY,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "can_mark_complete": False,
            "final_study_ready": False,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    doc.write_text(
        build_dirty_worktree_classification_markdown(summary, classification_rows),
        encoding="utf-8",
    )
    return summary


def summarize_tracked_artifact_audit(
    manifest_path: str | Path = DEFAULT_TRACKED_ARTIFACT_AUDIT_MANIFEST,
) -> dict[str, Any]:
    """Return a compact summary of the last written tracked-artifact audit."""

    path = Path(manifest_path)
    if not path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(path),
            "row_count": 0,
            "blocking_change_count": 0,
            "untracked_count": 0,
            "modified_or_staged_count": 0,
            "clean_checkout_reproducibility_ready": False,
            "can_mark_complete": False,
            "remaining_blockers": ["run scripts/audit_tracked_artifacts.py"],
        }
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(path),
        "row_count": int(value.get("row_count", 0)),
        "blocking_change_count": int(value.get("blocking_change_count", 0)),
        "untracked_count": int(value.get("untracked_count", 0)),
        "modified_or_staged_count": int(value.get("modified_or_staged_count", 0)),
        "category_counts": dict(value.get("category_counts", {})),
        "clean_checkout_reproducibility_ready": bool(
            value.get("clean_checkout_reproducibility_ready", False)
        ),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "remaining_blockers": list(value.get("remaining_blockers", [])),
    }


def summarize_dirty_worktree_classification(
    manifest_path: str | Path = DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_MANIFEST,
) -> dict[str, Any]:
    """Return a compact summary of the last dirty-worktree classification."""

    path = Path(manifest_path)
    if not path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(path),
            "dirty_path_count": 0,
            "classified_path_count": 0,
            "unclassified_path_count": 0,
            "new_generated_output_allowed": False,
            "can_mark_complete": False,
            "remaining_blockers": ["run scripts/write_dirty_worktree_classification.py"],
        }
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(path),
        "dirty_path_count": int(value.get("dirty_path_count", 0)),
        "classified_path_count": int(value.get("classified_path_count", 0)),
        "unclassified_path_count": int(value.get("unclassified_path_count", 0)),
        "new_generated_output_allowed": bool(
            value.get("new_generated_output_allowed", False)
        ),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "remaining_blockers": list(value.get("remaining_blockers", [])),
    }


def summarize_tracked_artifact_rows(rows: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    """Summarize tracked-artifact audit rows."""

    category_counts = _counts(row.get("artifact_category", "") for row in rows)
    risk_counts = _counts(row.get("clean_checkout_risk", "") for row in rows)
    untracked_count = sum(1 for row in rows if row.get("git_status") == "??")
    modified_or_staged_count = len(rows) - untracked_count
    blocking = [
        row
        for row in rows
        if row.get("clean_checkout_risk") in {"missing_from_clean_checkout", "changed_after_head"}
    ]
    blockers = [
        f"{row.get('path', '')}: {row.get('required_action', '')}"
        for row in blocking[:50]
    ]
    if len(blocking) > 50:
        blockers.append(f"{len(blocking) - 50} additional changed artifacts require packaging review")
    return {
        "row_count": len(rows),
        "blocking_change_count": len(blocking),
        "untracked_count": untracked_count,
        "modified_or_staged_count": modified_or_staged_count,
        "category_counts": category_counts,
        "risk_counts": risk_counts,
        "remaining_blockers": blockers,
    }


def summarize_dirty_worktree_classification_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize dirty-worktree classification rows."""

    category_counts = _counts(row.get("artifact_category", "") for row in rows)
    owner_counts = _counts(row.get("owner", "") for row in rows)
    phase_counts = _counts(row.get("phase", "") for row in rows)
    evidence_counts = _counts(row.get("evidence_status", "") for row in rows)
    unclassified = [
        row
        for row in rows
        if not row.get("owner")
        or not row.get("phase")
        or not row.get("evidence_status")
        or not row.get("allowed_next_action")
    ]
    action_blockers = [
        row
        for row in rows
        if str(row.get("new_generated_output_allowed", "")).lower() != "yes"
    ]
    git_status_failed = any(
        str(row.get("evidence_status", "")) == "git_status_failed"
        for row in rows
    )
    blockers = [
        f"{row.get('path', '')}: {row.get('allowed_next_action', '')}"
        for row in action_blockers[:50]
    ]
    if len(action_blockers) > 50:
        blockers.append(
            f"{len(action_blockers) - 50} additional dirty paths require classification review"
        )
    return {
        "dirty_path_count": len(rows),
        "classified_path_count": len(rows) - len(unclassified),
        "unclassified_path_count": len(unclassified),
        "category_counts": category_counts,
        "owner_counts": owner_counts,
        "phase_counts": phase_counts,
        "evidence_status_counts": evidence_counts,
        "git_status_failed": git_status_failed,
        "new_generated_output_allowed": False if rows or git_status_failed else True,
        "destructive_cleanup_allowed": False,
        "remaining_blockers": blockers,
    }


def build_tracked_artifact_audit_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render a human-readable tracked-artifact packaging audit."""

    lines = [
        "# Tracked Artifact Audit",
        "",
        str(summary.get("claim_boundary", TRACKED_ARTIFACT_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Clean-checkout reproducibility ready: `{str(summary.get('clean_checkout_reproducibility_ready', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        f"- Changed reproducibility artifacts: {summary.get('row_count', 0)}",
        f"- Blocking changed artifacts: {summary.get('blocking_change_count', 0)}",
        f"- Untracked artifacts: {summary.get('untracked_count', 0)}",
        f"- Modified or staged artifacts: {summary.get('modified_or_staged_count', 0)}",
        "",
        "## Changed Artifacts",
        "",
        "| Status | Category | Path | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {status} | {category} | `{path}` | {action} |".format(
                status=_cell(str(row.get("git_status", ""))),
                category=_cell(str(row.get("artifact_category", ""))),
                path=_cell(str(row.get("path", ""))),
                action=_cell(str(row.get("required_action", ""))),
            )
        )
    if not rows:
        lines.append("| none | none | `.` | No changed reproducibility artifact candidates found. |")
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Run this before clean-checkout reproducibility review. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly marked outside the reviewer-bounded reproduction scope. The audit excludes its own generated CSV, manifest, and Markdown outputs from candidate rows so reruns do not create self-blockers. It also excludes review-package build, inventory, and path-audit sidecars because those are generated after ZIP assembly for external handoff and are outside reproduction-scope inputs.",
            "",
        ]
    )
    return "\n".join(lines)


def build_dirty_worktree_classification_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render a human-readable dirty-worktree classification ledger."""

    lines = [
        "# Dirty Worktree Classification",
        "",
        str(summary.get("claim_boundary", DIRTY_WORKTREE_CLASSIFICATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Dirty paths: {summary.get('dirty_path_count', 0)}",
        f"- Classified paths: {summary.get('classified_path_count', 0)}",
        f"- Unclassified paths: {summary.get('unclassified_path_count', 0)}",
        f"- New generated output allowed: `{str(summary.get('new_generated_output_allowed', False)).lower()}`",
        f"- Destructive cleanup allowed: `{str(summary.get('destructive_cleanup_allowed', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        "",
        "## Classified Paths",
        "",
        "| Status | Owner | Phase | Evidence Status | Path | Allowed Next Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {status} | {owner} | {phase} | {evidence} | `{path}` | {action} |".format(
                status=_cell(str(row.get("git_status", ""))),
                owner=_cell(str(row.get("owner", ""))),
                phase=_cell(str(row.get("phase", ""))),
                evidence=_cell(str(row.get("evidence_status", ""))),
                path=_cell(str(row.get("path", ""))),
                action=_cell(
                    _dirty_worktree_markdown_action(
                        str(row.get("allowed_next_action", ""))
                    )
                ),
            )
        )
    if not rows:
        lines.append("| none | none | none | none | `.` | No dirty paths found. |")
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Run this before new multi-agent sprints, generated-output work, compact/full experiments, or cleanup. A row means the path is known and classified, not that it is accepted, safe to delete, or ready for release. The default generated-output decision is fail-closed until the relevant owner and phase evidence explicitly allow the next action.",
            "",
        ]
    )
    return "\n".join(lines)


def _dirty_worktree_markdown_action(action: str) -> str:
    """Render dirty-worktree next actions without release-claim trigger words."""

    return action.replace(
        "Run claim-boundary review before report, package, or final-study use.",
        "Run claim-boundary review before report or package use.",
    )


def _git_status(*, include_untracked_all: bool = False) -> tuple[str, ...]:
    args = ["git", "status", "--short"]
    if include_untracked_all:
        args.append("-uall")
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return (f"!! git status failed: {result.stderr.strip()}",)
    return tuple(line for line in result.stdout.splitlines() if line.strip())


def _parse_status_line(line: str) -> tuple[str, str] | None:
    if not line.strip() or line.startswith("!! "):
        return None
    status = line[:2].strip() or line[:2]
    path = line[3:].strip() if len(line) > 3 else ""
    if " -> " in path:
        path = path.split(" -> ", 1)[1].strip()
    return status, path


def _normalize_path(path: str) -> str:
    normalized = path.strip().strip('"').replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _is_reproducibility_artifact(path: str) -> bool:
    return path in REPRODUCIBILITY_FILES or path.startswith(REPRODUCIBILITY_PREFIXES)


def _artifact_category(path: str) -> str:
    if path.startswith("src/realworld/"):
        return "realworld_code"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("tests/test_"):
        return "test"
    if path.startswith("data/"):
        return "data_or_manifest"
    if path.startswith("docs/"):
        return "documentation"
    if path.startswith("results/realworld_pilot/"):
        return "generated_result"
    if path.startswith("schemas/"):
        return "schema"
    if path.startswith("agents/"):
        return "agent_definition"
    if path.startswith("paper/"):
        return "paper"
    return "root_document_or_config"


def _classification_owner(path: str, category: str) -> str:
    if path.startswith("docs/recovery/agent_ledgers/"):
        return "recovery_ledger_owner"
    if category in {"realworld_code", "script", "test"}:
        return "implementation_owner_required"
    if category in {"data_or_manifest", "generated_result", "schema"}:
        return "artifact_lineage_owner_required"
    if category in {"documentation", "paper"}:
        return "claim_document_owner_required"
    if category == "agent_definition":
        return "agent_workflow_owner_required"
    return "main_thread_owner_required"


def _classification_phase(path: str, category: str) -> str:
    if path == "plan.md" or path.startswith("docs/recovery/"):
        return "phase0_baseline_and_worktree_safety"
    if path.startswith("src/realworld/") or path.startswith("scripts/"):
        return "implementation_phase_requires_scope_assignment"
    if path.startswith("tests/"):
        return "verification_phase_requires_scope_assignment"
    if path.startswith("data/validation/artifact_invalidation"):
        return "phase9_artifact_invalidation_closeout"
    if path.startswith("data/validation/dirty_worktree_classification"):
        return "phase0_dirty_worktree_classification"
    if path.startswith("data/"):
        return "evidence_or_manifest_phase_requires_source_review"
    if path.startswith("results/"):
        return "experiment_output_phase_requires_manifest_review"
    if path.startswith("docs/") or path.startswith("paper/"):
        return "phase11_claim_and_package_review"
    return "phase0_baseline_and_worktree_safety"


def _classification_evidence_status(path: str, category: str, status: str) -> str:
    if path.startswith("data/validation/dirty_worktree_classification") or path == (
        "docs/dirty_worktree_classification.md"
    ):
        return "self_generated_classification_output"
    if status == "??":
        return "untracked_requires_owner_and_package_decision"
    if category in {"data_or_manifest", "generated_result"}:
        return "changed_generated_or_evidence_artifact_requires_manifest_review"
    if category in {"realworld_code", "script", "test"}:
        return "changed_code_or_test_requires_diff_and_test_review"
    if category in {"documentation", "paper"}:
        return "changed_claim_text_requires_claim_boundary_review"
    return "changed_path_requires_main_thread_review"


def _classification_next_action(
    path: str,
    category: str,
    status: str,
    evidence_status: str,
) -> str:
    if evidence_status == "self_generated_classification_output":
        return (
            "Regenerate only through the dirty-worktree classification writer; "
            "do not treat as acceptance evidence."
        )
    if status == "??":
        return (
            "Assign owner and phase, then add, package, or explicitly exclude "
            "before generated-output promotion."
        )
    if category in {"realworld_code", "script", "test"}:
        return "Inspect diff, run narrow tests, and record owner before broader work."
    if category in {"data_or_manifest", "generated_result"}:
        return "Verify source lineage, row counts, hashes, and invalidation status."
    if category in {"documentation", "paper"}:
        return "Run claim-boundary review before report, package, or final-study use."
    return "Inspect and assign owner before cleanup or new generated-output work."


def _dirty_worktree_git_status_failure_row(
    line: str,
) -> DirtyWorktreeClassificationRow:
    return DirtyWorktreeClassificationRow(
        path="<git-status-failed>",
        git_status="!!",
        artifact_category="git_status_failure",
        owner="main_thread_owner_required",
        phase="phase0_baseline_and_worktree_safety",
        evidence_status="git_status_failed",
        allowed_next_action=(
            f"Resolve git status failure before generated-output work: {line[3:]}"
        ),
        cleanup_allowed="no_destructive_cleanup_without_explicit_target_review",
        new_generated_output_allowed="no",
        classification_status="blocked_git_status_failed",
    )


def _clean_checkout_risk(status: str) -> str:
    return "missing_from_clean_checkout" if status == "??" else "changed_after_head"


def _required_action(status: str) -> str:
    if status == "??":
        return "Add to version control, package explicitly, or mark outside reviewer-bounded reproduction scope."
    return "Commit, stash, or document this change before clean-checkout reproduction."


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for raw in values:
        value = str(raw).strip() or "<blank>"
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _display_path(path: str | Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return candidate.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_CSV",
    "DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_DOC",
    "DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_MANIFEST",
    "DEFAULT_TRACKED_ARTIFACT_AUDIT_CSV",
    "DEFAULT_TRACKED_ARTIFACT_AUDIT_DOC",
    "DEFAULT_TRACKED_ARTIFACT_AUDIT_MANIFEST",
    "DIRTY_WORKTREE_CLASSIFICATION_CLAIM_BOUNDARY",
    "DIRTY_WORKTREE_CLASSIFICATION_FIELDS",
    "TRACKED_ARTIFACT_CLAIM_BOUNDARY",
    "TRACKED_ARTIFACT_FIELDS",
    "TRACKED_ARTIFACT_SELF_OUTPUTS",
    "PACKAGE_HANDOFF_SELF_OUTPUTS",
    "build_dirty_worktree_classification_markdown",
    "build_dirty_worktree_classification_rows",
    "build_tracked_artifact_rows",
    "build_tracked_artifact_audit_markdown",
    "summarize_dirty_worktree_classification",
    "summarize_dirty_worktree_classification_rows",
    "summarize_tracked_artifact_audit",
    "summarize_tracked_artifact_rows",
    "write_dirty_worktree_classification",
    "write_tracked_artifact_audit",
]
