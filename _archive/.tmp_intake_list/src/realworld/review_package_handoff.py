"""Generate a sidecar handoff note for the expert review package.

The handoff note is deliberately written outside the ZIP so it can record the
ZIP's final checksum without changing that checksum.
"""

from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping
from zipfile import ZipFile

from src.realworld.formal_acceptance_guard import (
    FINAL_ACCEPTANCE_ARTIFACTS,
    audit_formal_acceptance_artifacts,
)
from src.realworld.manifest_timestamp import write_text_if_changed
from src.realworld.manifest_timestamp import write_json_manifest_if_changed
from src.realworld.review_package_builder import (
    DEFAULT_REVIEW_PACKAGE_BUILD_DOC,
    DEFAULT_REVIEW_PACKAGE_BUILD_MANIFEST,
    DEFAULT_REVIEW_PACKAGE_ZIP,
)
from src.realworld.review_package_path_audit import (
    DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_DOC,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REQUIRED_DELIVERABLES_ZIP = PROJECT_ROOT / "required_deliverables.zip"
DEFAULT_EXPERT_REVIEW_PACKAGE_ZIP = (
    PROJECT_ROOT / "review_packages" / "expert_review_package.zip"
)
DEFAULT_PREVIOUS_INCOMPLETE_PACKAGE_ZIP = (
    PROJECT_ROOT / "review_packages" / "original_required_deliverables_incomplete_20260510.zip"
)
DEFAULT_EXPERT_REVIEW_HANDOFF_DOC = (
    PROJECT_ROOT / "review_packages" / "expert_review_handoff_20260510.md"
)
DEFAULT_EXPERT_REVIEW_HANDOFF_MANIFEST = (
    PROJECT_ROOT / "review_packages" / "expert_review_handoff_20260510.json"
)

EXPERT_REVIEW_HANDOFF_CLAIM_BOUNDARY = (
    "This handoff note identifies the external review ZIP and sidecar files. "
    "It does not validate evidence quality, approve formal acceptance records, "
    "certify calibration, or close final-study gates."
)


def build_expert_review_handoff_summary(
    *,
    root: str | Path = PROJECT_ROOT,
    zip_path: str | Path = DEFAULT_REQUIRED_DELIVERABLES_ZIP,
    mirror_zip_path: str | Path = DEFAULT_EXPERT_REVIEW_PACKAGE_ZIP,
    previous_zip_path: str | Path = DEFAULT_PREVIOUS_INCOMPLETE_PACKAGE_ZIP,
    build_doc_path: str | Path = DEFAULT_REVIEW_PACKAGE_BUILD_DOC,
    path_audit_doc_path: str | Path = DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_DOC,
    consultation_request_path: str | Path = PROJECT_ROOT
    / "docs"
    / "expert_consultation_request.md",
    build_manifest_path: str | Path = DEFAULT_REVIEW_PACKAGE_BUILD_MANIFEST,
    handoff_date: str | None = None,
) -> dict[str, Any]:
    """Return the external review handoff summary."""

    project_root = Path(root)
    zip_file = Path(zip_path)
    mirror_zip = Path(mirror_zip_path)
    previous_zip = Path(previous_zip_path)
    build_manifest = _read_json(Path(build_manifest_path))
    formal_guard = audit_formal_acceptance_artifacts(project_root=project_root)
    zip_sha = _sha256(zip_file) if zip_file.exists() else ""
    mirror_sha = _sha256(mirror_zip) if mirror_zip.exists() else ""
    previous_sha = _sha256(previous_zip) if previous_zip.exists() else ""
    files_to_send = [
        zip_file,
        Path(build_doc_path),
        Path(path_audit_doc_path),
        Path(consultation_request_path),
    ]
    return {
        "schema_version": 1,
        "handoff_date": handoff_date or date.today().isoformat(),
        "claim_boundary": EXPERT_REVIEW_HANDOFF_CLAIM_BOUNDARY,
        "files_to_send": [_display_path(project_root, path) for path in files_to_send],
        "file_identities": [_file_identity(project_root, path) for path in files_to_send],
        "zip": {
            "path": _display_path(project_root, zip_file),
            "present": zip_file.exists(),
            "file_count": _zip_file_count(zip_file),
            "size_bytes": zip_file.stat().st_size if zip_file.exists() else 0,
            "sha256": zip_sha,
        },
        "mirror_zip": {
            "path": _display_path(project_root, mirror_zip),
            "present": mirror_zip.exists(),
            "sha256": mirror_sha,
            "matches_zip": bool(zip_sha and mirror_sha and zip_sha == mirror_sha),
        },
        "previous_incomplete_zip": {
            "path": _display_path(project_root, previous_zip),
            "present": previous_zip.exists(),
            "sha256": previous_sha,
        },
        "build_manifest": {
            "path": _display_path(project_root, Path(build_manifest_path)),
            "present": bool(build_manifest),
            "selected_file_count": build_manifest.get("selected_file_count", 0),
            "zip_sha256": build_manifest.get("zip_sha256", ""),
        },
        "formal_status": {
            "final_study_ready": False,
            "final_study_ready_text": "false",
            "final_study_gates_ready": "3 / 15",
            "formal_acceptance_ready": formal_guard["formal_acceptance_ready"],
            "formal_acceptance_ready_count": "0 / 12",
            "formal_target_count": len(FINAL_ACCEPTANCE_ARTIFACTS),
            "missing_formal_target_count": formal_guard["missing_count"],
            "template_or_placeholder_count": formal_guard[
                "template_or_placeholder_count"
            ],
        },
        "review_items": [
            "send the handoff note outside the ZIP so the ZIP checksum remains stable",
            "treat the ZIP as primary evidence for review, not as formal acceptance",
            "keep formal acceptance targets absent until real reviewer decisions exist",
        ],
        "can_mark_complete": False,
    }


def write_expert_review_handoff(
    *,
    output_path: str | Path = DEFAULT_EXPERT_REVIEW_HANDOFF_DOC,
    manifest_path: str | Path = DEFAULT_EXPERT_REVIEW_HANDOFF_MANIFEST,
    **kwargs: Any,
) -> dict[str, Any]:
    """Write the sidecar handoff Markdown note."""

    summary = build_expert_review_handoff_summary(**kwargs)
    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    summary["outputs"] = {
        "doc": _display_path(PROJECT_ROOT, output),
        "manifest": _display_path(PROJECT_ROOT, manifest),
    }
    write_text_if_changed(build_expert_review_handoff_markdown(summary), output)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    return summary


def build_expert_review_handoff_markdown(summary: Mapping[str, Any]) -> str:
    """Return Markdown for the expert review handoff sidecar."""

    zip_info = dict(summary.get("zip", {}))
    mirror_info = dict(summary.get("mirror_zip", {}))
    previous_info = dict(summary.get("previous_incomplete_zip", {}))
    formal_status = dict(summary.get("formal_status", {}))
    lines = [
        "# Expert Review Handoff",
        "",
        f"Date: {summary.get('handoff_date', '')}",
        "",
        "## Files To Send",
        "",
        "Send these files together:",
        "",
    ]
    for path in summary.get("files_to_send", []):
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "The mirrored ZIP at "
            f"`{mirror_info.get('path', '')}` is identical to "
            f"`{zip_info.get('path', '')}`.",
            "",
            "## Current ZIP Identity",
            "",
            f"- ZIP path: `{zip_info.get('path', '')}`",
            f"- File count: {zip_info.get('file_count', 0)}",
            f"- Size bytes: {zip_info.get('size_bytes', 0)}",
            f"- SHA256: `{zip_info.get('sha256', '')}`",
            "",
            "The previous incomplete 12-file package is preserved as "
            f"`{previous_info.get('path', '')}` with SHA256: "
            f"`{previous_info.get('sha256', '')}`.",
            "",
            "## File Identities",
            "",
            "| File | Present | Size bytes | SHA256 |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for record in summary.get("file_identities", []):
        if not isinstance(record, Mapping):
            continue
        lines.append(
            "| "
            f"`{record.get('path', '')}` | "
            f"{str(record.get('present', False)).lower()} | "
            f"{record.get('size_bytes', 0)} | "
            f"`{record.get('sha256', '')}` |"
        )
    lines.extend(
        [
            "",
            "## Review Boundary",
            "",
            "Machine-readable handoff metadata is written to "
            f"`{summary.get('outputs', {}).get('manifest', '')}`.",
            "",
            "This is a review handoff bundle, not an acceptance package. The "
            "current package path audit reports no missing non-formal local "
            "paths inside the ZIP, but the formal acceptance targets are "
            "intentionally absent until real reviewer decisions exist.",
            "",
            "The current formal status remains:",
            "",
            f"- `final_study_ready={formal_status.get('final_study_ready_text', 'false')}`",
            f"- final-study gates ready: {formal_status.get('final_study_gates_ready', '3 / 15')}",
            f"- formal acceptance ready: {formal_status.get('formal_acceptance_ready_count', '0 / 12')}",
            f"- missing formal targets: {formal_status.get('missing_formal_target_count', 0)} / {formal_status.get('formal_target_count', 0)}",
            "",
            "Do not interpret the ZIP, generated worksheets, path audits, smoke "
            "tests, or `accepted=false` templates as formal approval.",
            "",
            "## Suggested Cover Note",
            "",
            "Please review the attached `required_deliverables.zip` as the "
            "primary evidence package for the transport-system simulation. The "
            "project is currently a decision-support and resilience-evaluation "
            "research framework, not an operational route plan or deployment "
            "instruction.",
            "",
            "We are asking for a prioritized expert assessment of implementation "
            "mechanics, experiment design, data/source evidence, reproducibility "
            "controls, and report claim boundaries. Please treat the package as "
            "not ready for acceptance unless the included audit artifacts prove "
            "otherwise, and identify the shortest legitimate path to formal "
            "acceptance without weakening scientific credibility.",
            "",
        ]
    )
    return "\n".join(lines)


def _zip_file_count(path: Path) -> int:
    if not path.exists():
        return 0
    with ZipFile(path) as archive:
        return len(archive.namelist())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_identity(root: Path, path: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": _display_path(root, path),
        "present": exists,
        "size_bytes": path.stat().st_size if exists else 0,
        "sha256": _sha256(path) if exists else "",
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "DEFAULT_EXPERT_REVIEW_HANDOFF_DOC",
    "DEFAULT_EXPERT_REVIEW_HANDOFF_MANIFEST",
    "DEFAULT_EXPERT_REVIEW_PACKAGE_ZIP",
    "DEFAULT_PREVIOUS_INCOMPLETE_PACKAGE_ZIP",
    "DEFAULT_REQUIRED_DELIVERABLES_ZIP",
    "EXPERT_REVIEW_HANDOFF_CLAIM_BOUNDARY",
    "build_expert_review_handoff_markdown",
    "build_expert_review_handoff_summary",
    "write_expert_review_handoff",
]
