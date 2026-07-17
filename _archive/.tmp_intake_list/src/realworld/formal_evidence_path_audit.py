"""Audit evidence paths referenced by formal acceptance artifacts.

This audit validates evidence-path hygiene only. It does not decide whether
evidence is scientifically sufficient and never creates acceptance records.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FORMAL_EVIDENCE_PATH_AUDIT_MANIFEST = (
    PROJECT_ROOT / "data" / "manifests" / "formal_evidence_path_audit.json"
)
DEFAULT_FORMAL_EVIDENCE_PATH_AUDIT_DOC = (
    PROJECT_ROOT / "docs" / "formal_evidence_path_audit.md"
)

EVIDENCE_FIELD_NAMES = (
    "evidence_paths",
    "source_paths",
    "reviewed_inputs",
    "data_snapshot_paths",
)
FORMAL_ARTIFACT_RELATIVE_PATHS = (
    "data/manifests/pilot_acceptance.json",
    "data/manifests/graph_scale_acceptance.json",
    "data/manifests/provenance_acceptance.json",
    "data/parameters/parameter_acceptance.csv",
    "data/parameters/road_class_overrides.csv",
    "data/manifests/validation_acceptance.json",
    "data/manifests/sensitivity_acceptance.json",
    "data/manifests/experiment_acceptance.json",
    "data/manifests/manuscript_acceptance.json",
    "data/manifests/reproducibility_acceptance.json",
    "data/manifests/final_audit_acceptance.json",
)
CLAIM_BOUNDARY = (
    "This audit checks whether formal acceptance artifacts point to concrete "
    "local evidence files or explicit external references. It does not approve "
    "the evidence, validate licenses, certify calibration, or close final-study "
    "gates."
)


def audit_formal_evidence_paths(
    *,
    root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Return an evidence-path hygiene audit for formal acceptance artifacts."""

    project_root = Path(root)
    artifacts = [
        _audit_artifact(project_root, project_root / relative_path)
        for relative_path in FORMAL_ARTIFACT_RELATIVE_PATHS
    ]
    present_artifacts = [item for item in artifacts if item["artifact_present"]]
    evidence_items = [
        evidence
        for artifact in artifacts
        for evidence in artifact.get("evidence_items", [])
    ]
    status_counts = _counts(item["status"] for item in evidence_items)
    missing_local_count = status_counts.get("missing_local_evidence", 0)
    placeholder_count = status_counts.get("placeholder_evidence", 0)
    empty_record_count = sum(
        1
        for artifact in present_artifacts
        if artifact["evidence_item_count"] == 0
        and artifact["artifact_type"] in {"json", "csv"}
    )
    blockers: list[str] = []
    for artifact in present_artifacts:
        if artifact["evidence_item_count"] == 0 and artifact["artifact_type"] in {
            "json",
            "csv",
        }:
            blockers.append(
                f"{artifact['path']}: no evidence_paths, source_paths, reviewed_inputs, or data_snapshot_paths found"
            )
    for item in evidence_items:
        if item["status"] in {"missing_local_evidence", "placeholder_evidence"}:
            blockers.append(
                f"{item['artifact_path']}: {item['status']} -> {item['raw_value']}"
            )

    can_mark_complete = (
        bool(present_artifacts)
        and not blockers
        and placeholder_count == 0
        and missing_local_count == 0
        and empty_record_count == 0
    )
    return {
        "schema_version": 1,
        "claim_boundary": CLAIM_BOUNDARY,
        "artifact_count": len(artifacts),
        "present_artifact_count": len(present_artifacts),
        "evidence_item_count": len(evidence_items),
        "status_counts": status_counts,
        "missing_local_evidence_count": missing_local_count,
        "placeholder_evidence_count": placeholder_count,
        "empty_evidence_record_count": empty_record_count,
        "can_mark_complete": can_mark_complete,
        "formal_evidence_paths_ready": can_mark_complete,
        "artifacts": artifacts,
        "remaining_blockers": blockers,
        "review_items": [
            "review all external references for source, license, and citation compatibility",
            "replace REVIEW_REQUIRED placeholders before any formal acceptance package is considered",
            "ensure every local evidence path exists in the repository or generated package",
            "treat this as path hygiene only; scientific sufficiency still requires human review",
        ],
    }


def write_formal_evidence_path_audit(
    *,
    root: str | Path = PROJECT_ROOT,
    manifest_path: str | Path = DEFAULT_FORMAL_EVIDENCE_PATH_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_FORMAL_EVIDENCE_PATH_AUDIT_DOC,
) -> dict[str, Any]:
    """Write formal evidence-path audit JSON and Markdown artifacts."""

    summary = audit_formal_evidence_paths(root=root)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    doc.write_text(build_formal_evidence_path_markdown(summary), encoding="utf-8")
    return summary


def build_formal_evidence_path_markdown(summary: Mapping[str, Any]) -> str:
    """Return a human-readable evidence-path audit."""

    lines = [
        "# Formal Evidence Path Audit",
        "",
        str(summary.get("claim_boundary", CLAIM_BOUNDARY)),
        "",
        "## Verdict",
        "",
        f"- Formal evidence paths ready: `{str(summary.get('formal_evidence_paths_ready', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        f"- Formal artifacts present: {summary.get('present_artifact_count', 0)} / {summary.get('artifact_count', 0)}",
        f"- Evidence items: {summary.get('evidence_item_count', 0)}",
        f"- Missing local evidence: {summary.get('missing_local_evidence_count', 0)}",
        f"- Placeholder evidence values: {summary.get('placeholder_evidence_count', 0)}",
        "",
        "## Artifact Summary",
        "",
        "| Artifact | Present | Evidence Items | Blockers |",
        "| --- | --- | --- | --- |",
    ]
    for artifact in summary.get("artifacts", []):
        if not isinstance(artifact, Mapping):
            continue
        blockers = artifact.get("blockers", [])
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_cell(str(artifact.get('path', '')))}`",
                    str(artifact.get("artifact_present", False)).lower(),
                    str(artifact.get("evidence_item_count", 0)),
                    _cell("<br>".join(str(item) for item in blockers) or "none"),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Use", ""])
    lines.append(
        "Run this audit after a reviewer adds or edits formal acceptance artifacts. "
        "A clean evidence-path audit is necessary but not sufficient for final "
        "study acceptance."
    )
    lines.append("")
    return "\n".join(lines)


def _audit_artifact(project_root: Path, path: Path) -> dict[str, Any]:
    artifact_type = _artifact_type(path)
    if not path.exists():
        return {
            "path": _display_path(project_root, path),
            "artifact_present": False,
            "artifact_type": artifact_type,
            "evidence_item_count": 0,
            "evidence_items": [],
            "blockers": [],
        }
    if artifact_type == "json":
        rows = [_read_json_object(path)]
    elif artifact_type == "csv":
        rows = _read_csv_rows(path)
    else:
        rows = []
    evidence_items = [
        _audit_evidence_value(project_root, path, field, value)
        for row in rows
        for field, value in _iter_evidence_values(row)
    ]
    blockers = [
        f"{item['status']}: {item['raw_value']}"
        for item in evidence_items
        if item["status"] in {"missing_local_evidence", "placeholder_evidence"}
    ]
    return {
        "path": _display_path(project_root, path),
        "artifact_present": True,
        "artifact_type": artifact_type,
        "evidence_item_count": len(evidence_items),
        "evidence_items": evidence_items,
        "blockers": blockers,
    }


def _iter_evidence_values(row: Mapping[str, Any]) -> Iterable[tuple[str, str]]:
    for field in EVIDENCE_FIELD_NAMES:
        if field not in row:
            continue
        value = row[field]
        for item in _flatten_evidence_value(value):
            cleaned = str(item).strip()
            if cleaned:
                yield field, cleaned


def _flatten_evidence_value(value: object) -> list[str]:
    if isinstance(value, str):
        parts = []
        for item in value.replace("|", ";").split(";"):
            stripped = item.strip()
            if stripped:
                parts.append(stripped)
        return parts
    if isinstance(value, (list, tuple)):
        output: list[str] = []
        for item in value:
            output.extend(_flatten_evidence_value(item))
        return output
    return [str(value)] if value is not None else []


def _audit_evidence_value(
    project_root: Path,
    artifact_path: Path,
    field: str,
    raw_value: str,
) -> dict[str, Any]:
    lowered = raw_value.lower()
    if "review_required" in lowered or "placeholder" in lowered:
        status = "placeholder_evidence"
        resolved = ""
    elif _is_external_reference(raw_value):
        status = "external_reference_needs_review"
        resolved = raw_value
    else:
        candidate = Path(raw_value)
        if not candidate.is_absolute():
            candidate = project_root / candidate
        status = "present_local_evidence" if candidate.exists() else "missing_local_evidence"
        resolved = _display_path(project_root, candidate)
    return {
        "artifact_path": _display_path(project_root, artifact_path),
        "field": field,
        "raw_value": raw_value,
        "status": status,
        "resolved_path": resolved,
    }


def _artifact_type(path: Path) -> str:
    if path.suffix.lower() == ".json":
        return "json"
    if path.suffix.lower() == ".csv":
        return "csv"
    if path.suffix.lower() == ".md":
        return "markdown"
    return "other"


def _read_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _is_external_reference(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(("http://", "https://", "doi:", "urn:"))


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _display_path(project_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


__all__ = [
    "CLAIM_BOUNDARY",
    "DEFAULT_FORMAL_EVIDENCE_PATH_AUDIT_DOC",
    "DEFAULT_FORMAL_EVIDENCE_PATH_AUDIT_MANIFEST",
    "FORMAL_ARTIFACT_RELATIVE_PATHS",
    "audit_formal_evidence_paths",
    "build_formal_evidence_path_markdown",
    "write_formal_evidence_path_audit",
]
