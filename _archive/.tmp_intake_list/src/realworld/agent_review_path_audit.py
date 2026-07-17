"""Path hygiene audit for sub-agent review records.

Sub-agent records are review aids, but their cited evidence should still point
to either existing local files or explicit formal acceptance targets that are
expected to remain absent until human/source-backed approval is supplied.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from src.realworld.acceptance_orchestration import (
    DEFAULT_AGENT_REVIEW_DIR,
    REVIEW_AGENT_DEFINITIONS,
)
from src.realworld.acceptance_records import AcceptanceRecord, load_acceptance_record


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AGENT_REVIEW_PATH_AUDIT_MANIFEST = (
    PROJECT_ROOT / "data" / "manifests" / "agent_review_path_audit.json"
)
DEFAULT_AGENT_REVIEW_PATH_AUDIT_DOC = (
    PROJECT_ROOT / "docs" / "agent_review_path_audit.md"
)
AGENT_REVIEW_PATH_CLAIM_BOUNDARY = (
    "This audit checks sub-agent review-record path hygiene only. It does not "
    "approve evidence quality, licenses, calibration, reviewer decisions, or "
    "final-study readiness."
)


@dataclass(frozen=True)
class PathCheck:
    """One path reference in one sub-agent record."""

    record_path: str
    gate_id: str
    agent_id: str
    field: str
    path: str
    status: str

    def to_dict(self) -> dict[str, str]:
        return {
            "record_path": self.record_path,
            "gate_id": self.gate_id,
            "agent_id": self.agent_id,
            "field": self.field,
            "path": self.path,
            "status": self.status,
        }


def audit_agent_review_paths(
    *,
    root: str | Path = PROJECT_ROOT,
    review_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Audit path references in generated sub-agent review records."""

    project_root = Path(root)
    record_dir = Path(review_dir) if review_dir is not None else DEFAULT_AGENT_REVIEW_DIR
    formal_targets = _formal_targets()
    record_paths = sorted(record_dir.glob("*.json"))
    checks: list[PathCheck] = []
    invalid_records: list[dict[str, str]] = []
    for path in record_paths:
        try:
            record = load_acceptance_record(path)
        except Exception as exc:  # pragma: no cover - surfaced in audit artifact
            invalid_records.append(
                {
                    "record_path": _display_path(path, project_root),
                    "error": str(exc),
                }
            )
            continue
        checks.extend(_record_path_checks(record, path, project_root, formal_targets))

    missing_required = [
        check for check in checks if check.status == "missing_required_path"
    ]
    missing_formal = [
        check for check in checks if check.status == "missing_formal_target"
    ]
    unique_missing_formal = sorted({check.path for check in missing_formal})
    existing = [check for check in checks if check.status == "present"]
    ready = not invalid_records and not missing_required and bool(record_paths)
    status_counts = _status_counts(
        present_count=len(existing),
        missing_required_path_count=len(missing_required),
        missing_formal_target_count=len(missing_formal),
        invalid_record_count=len(invalid_records),
    )
    return {
        "schema_version": 1,
        "claim_boundary": AGENT_REVIEW_PATH_CLAIM_BOUNDARY,
        "record_dir": _display_path(record_dir, project_root),
        "record_count": len(record_paths),
        "invalid_record_count": len(invalid_records),
        "path_reference_count": len(checks),
        "present_path_count": len(existing),
        "missing_required_path_count": len(missing_required),
        "missing_formal_target_count": len(missing_formal),
        "unique_missing_formal_target_count": len(unique_missing_formal),
        "unique_missing_formal_targets": unique_missing_formal,
        "status_counts": status_counts,
        "agent_review_paths_ready": ready,
        "can_mark_complete": False,
        "invalid_records": invalid_records,
        "missing_required_paths": [check.to_dict() for check in missing_required],
        "missing_formal_targets": [check.to_dict() for check in missing_formal],
        "remaining_blockers": _remaining_blockers(invalid_records, missing_required),
    }


def write_agent_review_path_audit(
    *,
    root: str | Path = PROJECT_ROOT,
    review_dir: str | Path | None = None,
    manifest_path: str | Path = DEFAULT_AGENT_REVIEW_PATH_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_AGENT_REVIEW_PATH_AUDIT_DOC,
) -> dict[str, Any]:
    """Write path-hygiene JSON and Markdown audit artifacts."""

    summary = audit_agent_review_paths(root=root, review_dir=review_dir)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(build_agent_review_path_audit_markdown(summary), encoding="utf-8")
    return summary


def build_agent_review_path_audit_markdown(summary: dict[str, Any]) -> str:
    """Return a human-readable agent-review path hygiene report."""

    lines = [
        "# Agent Review Path Audit",
        "",
        str(summary.get("claim_boundary", AGENT_REVIEW_PATH_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Agent review paths ready: `{str(summary.get('agent_review_paths_ready', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        f"- Review records: {summary.get('record_count', 0)}",
        f"- Path references: {summary.get('path_reference_count', 0)}",
        f"- Present paths: {summary.get('present_path_count', 0)}",
        f"- Missing required paths: {summary.get('missing_required_path_count', 0)}",
        f"- Missing formal targets: {summary.get('missing_formal_target_count', 0)}",
        f"- Unique missing formal targets: {summary.get('unique_missing_formal_target_count', 0)}",
        f"- Status counts: {_format_status_counts(summary.get('status_counts', {}))}",
        "",
    ]
    missing_required = summary.get("missing_required_paths", [])
    if missing_required:
        lines.extend(["## Missing Required Paths", ""])
        lines.extend(_path_table(missing_required))
        lines.append("")
    missing_formal = summary.get("missing_formal_targets", [])
    if missing_formal:
        lines.extend(
            [
                "## Missing Formal Targets",
                "",
                "These are expected to remain absent until reviewed acceptance decisions are supplied.",
                "",
            ]
        )
        lines.extend(_path_table(missing_formal))
        lines.append("")
    blockers = summary.get("remaining_blockers", [])
    lines.extend(["## Remaining Blockers", ""])
    if blockers:
        lines.extend(f"- {item}" for item in blockers)
    else:
        lines.append("- None for path hygiene. This still does not approve any gate.")
    lines.append("")
    return "\n".join(lines)


def _record_path_checks(
    record: AcceptanceRecord,
    record_path: Path,
    root: Path,
    formal_targets: set[str],
) -> list[PathCheck]:
    checks: list[PathCheck] = []
    fields = {
        "evidence": record.evidence,
        "source_paths": record.source_paths,
        "reviewed_inputs": record.reviewed_inputs,
        "review_packet_paths": record.review_packet_paths,
    }
    for field, values in fields.items():
        for value in values:
            path_text = _normalize_path(value)
            if not path_text or _looks_external(path_text):
                continue
            resolved = root / path_text
            if resolved.exists():
                status = "present"
            elif path_text in formal_targets:
                status = "missing_formal_target"
            else:
                status = "missing_required_path"
            checks.append(
                PathCheck(
                    record_path=_display_path(record_path, root),
                    gate_id=record.gate_id,
                    agent_id=record.agent_id,
                    field=field,
                    path=path_text,
                    status=status,
                )
            )
    return checks


def _formal_targets() -> set[str]:
    targets = {
        _normalize_path(path)
        for agent in REVIEW_AGENT_DEFINITIONS
        for path in agent.final_acceptance_artifacts
    }
    targets.add("docs/final_study_audit.md")
    targets.add("data/manifests/final_audit_acceptance.json")
    return targets


def _remaining_blockers(
    invalid_records: list[dict[str, str]],
    missing_required: Iterable[PathCheck],
) -> list[str]:
    blockers: list[str] = []
    if invalid_records:
        blockers.append("fix invalid sub-agent review JSON records")
    for check in missing_required:
        blockers.append(
            f"create or correct {check.field} path {check.path} in {check.record_path}"
        )
    return blockers


def _status_counts(
    *,
    present_count: int,
    missing_required_path_count: int,
    missing_formal_target_count: int,
    invalid_record_count: int,
) -> dict[str, int]:
    counts = {
        "present": present_count,
        "missing_formal_target": missing_formal_target_count,
    }
    if missing_required_path_count:
        counts["missing_required_path"] = missing_required_path_count
    if invalid_record_count:
        counts["invalid_record"] = invalid_record_count
    return counts


def _format_status_counts(value: object) -> str:
    if not isinstance(value, dict) or not value:
        return "none"
    return ", ".join(f"{key}={count}" for key, count in sorted(value.items()))


def _path_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Gate | Field | Path | Record |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {gate} | {field} | `{path}` | `{record}` |".format(
                gate=_cell(str(row.get("gate_id", ""))),
                field=_cell(str(row.get("field", ""))),
                path=_cell(str(row.get("path", ""))),
                record=_cell(str(row.get("record_path", ""))),
            )
        )
    return lines


def _normalize_path(value: str) -> str:
    return value.strip().replace("\\", "/").lstrip("./")


def _looks_external(value: str) -> bool:
    lower = value.lower()
    return lower.startswith(("http://", "https://", "doi:", "urn:"))


def _display_path(path: Path, root: Path = PROJECT_ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "AGENT_REVIEW_PATH_CLAIM_BOUNDARY",
    "DEFAULT_AGENT_REVIEW_PATH_AUDIT_DOC",
    "DEFAULT_AGENT_REVIEW_PATH_AUDIT_MANIFEST",
    "audit_agent_review_paths",
    "build_agent_review_path_audit_markdown",
    "write_agent_review_path_audit",
]
