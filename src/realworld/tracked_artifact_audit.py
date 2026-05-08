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
TRACKED_ARTIFACT_SELF_OUTPUTS: frozenset[str] = frozenset(
    {
        "data/validation/tracked_artifact_audit.csv",
        "data/validation/tracked_artifact_audit_manifest.json",
        "docs/tracked_artifact_audit.md",
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
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(build_tracked_artifact_audit_markdown(summary, audit_rows), encoding="utf-8")
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
            "Run this before clean-checkout reproducibility acceptance. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly excluded from the accepted reproduction scope.",
            "",
        ]
    )
    return "\n".join(lines)


def _git_status() -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "status", "--short"],
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
    return path.strip().strip('"').replace("\\", "/").lstrip("./")


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


def _clean_checkout_risk(status: str) -> str:
    return "missing_from_clean_checkout" if status == "??" else "changed_after_head"


def _required_action(status: str) -> str:
    if status == "??":
        return "Add to version control, package explicitly, or exclude from accepted reproduction scope."
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
    "DEFAULT_TRACKED_ARTIFACT_AUDIT_CSV",
    "DEFAULT_TRACKED_ARTIFACT_AUDIT_DOC",
    "DEFAULT_TRACKED_ARTIFACT_AUDIT_MANIFEST",
    "TRACKED_ARTIFACT_CLAIM_BOUNDARY",
    "TRACKED_ARTIFACT_FIELDS",
    "TRACKED_ARTIFACT_SELF_OUTPUTS",
    "build_tracked_artifact_rows",
    "build_tracked_artifact_audit_markdown",
    "summarize_tracked_artifact_audit",
    "summarize_tracked_artifact_rows",
    "write_tracked_artifact_audit",
]
