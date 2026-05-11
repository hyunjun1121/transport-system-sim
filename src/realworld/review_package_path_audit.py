"""ZIP-internal path audit for the external expert-review package.

The package inventory proves what files were selected. This audit checks the
next failure mode from the expert reply: whether sub-agent review records inside
the ZIP cite local paths that are also present inside that same ZIP.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable
from zipfile import BadZipFile, ZipFile

from src.realworld.acceptance_records import (
    AcceptanceRecord,
    acceptance_record_from_mapping,
)
from src.realworld.formal_evidence_path_audit import FORMAL_ARTIFACT_RELATIVE_PATHS
from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REVIEW_PACKAGE_ZIP = PROJECT_ROOT / "required_deliverables.zip"
DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_MANIFEST = (
    PROJECT_ROOT / "data" / "manifests" / "review_package_path_audit.json"
)
DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_DOC = (
    PROJECT_ROOT / "docs" / "review_package_path_audit.md"
)
REVIEW_PACKAGE_PATH_AUDIT_CLAIM_BOUNDARY = (
    "This audit checks path references inside the external review ZIP. It does "
    "not validate evidence quality, approve formal acceptance records, certify "
    "calibration, or close final-study gates."
)
REVIEW_RECORD_PREFIX = "data/manifests/agent_reviews/"


@dataclass(frozen=True)
class PackagePathCheck:
    """One local path reference found in one review record inside the ZIP."""

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


def audit_review_package_paths(
    zip_path: str | Path = DEFAULT_REVIEW_PACKAGE_ZIP,
) -> dict[str, Any]:
    """Return a ZIP-internal path audit for packaged review records."""

    package = Path(zip_path)
    if not package.exists():
        return _missing_zip_summary(package)

    try:
        with ZipFile(package) as archive:
            names = {_normalize_path(name) for name in archive.namelist()}
            record_paths = sorted(
                name
                for name in names
                if name.startswith(REVIEW_RECORD_PREFIX) and name.endswith(".json")
            )
            checks, invalid_records = _audit_records(archive, record_paths, names)
    except BadZipFile as exc:
        return _invalid_zip_summary(package, str(exc))

    missing_package = [
        check for check in checks if check.status == "missing_package_path"
    ]
    missing_formal = [
        check for check in checks if check.status == "missing_formal_target"
    ]
    present = [check for check in checks if check.status == "present"]
    unique_missing_package = sorted({check.path for check in missing_package})
    unique_missing_formal = sorted({check.path for check in missing_formal})
    ready = bool(record_paths) and not invalid_records and not missing_package
    status_counts = _status_counts(check.status for check in checks)
    if invalid_records:
        status_counts["invalid_record"] = len(invalid_records)

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": REVIEW_PACKAGE_PATH_AUDIT_CLAIM_BOUNDARY,
        "zip_path": _display_path(package),
        "zip_present": True,
        "zip_valid": True,
        "zip_size_bytes": package.stat().st_size,
        "zip_sha256": _sha256(package),
        "zip_file_count": len(names),
        "record_count": len(record_paths),
        "path_reference_count": len(checks),
        "present_path_count": len(present),
        "missing_package_path_count": len(missing_package),
        "missing_formal_target_count": len(missing_formal),
        "unique_missing_package_path_count": len(unique_missing_package),
        "unique_missing_package_paths": unique_missing_package,
        "unique_missing_formal_target_count": len(unique_missing_formal),
        "unique_missing_formal_targets": unique_missing_formal,
        "invalid_record_count": len(invalid_records),
        "status_counts": status_counts,
        "review_package_paths_ready": ready,
        "acceptance_ready": False,
        "publication_ready": False,
        "can_mark_complete": False,
        "missing_package_paths": [check.to_dict() for check in missing_package],
        "missing_formal_targets": [check.to_dict() for check in missing_formal],
        "invalid_records": invalid_records,
        "remaining_blockers": _remaining_blockers(
            package,
            invalid_records,
            unique_missing_package,
            record_paths,
        ),
        "review_items": [
            "keep formal acceptance target paths absent unless real reviewer decisions exist",
            "send docs/review_package_build.md as a sidecar because it is generated after ZIP assembly",
            "send review_packages/expert_review_handoff_20260510.md and review_packages/expert_review_handoff_20260510.json as ZIP-external checksum and cover-note sidecars",
            "treat ZIP path completeness as package hygiene only, not evidence acceptance",
        ],
    }


def write_review_package_path_audit(
    *,
    zip_path: str | Path = DEFAULT_REVIEW_PACKAGE_ZIP,
    manifest_path: str | Path = DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_DOC,
) -> dict[str, Any]:
    """Write ZIP path-audit JSON and Markdown artifacts."""

    summary = audit_review_package_paths(zip_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(build_review_package_path_audit_markdown(summary), doc)
    return summary


def build_review_package_path_audit_markdown(summary: dict[str, Any]) -> str:
    """Return a Markdown report for the ZIP path audit."""

    lines = [
        "# Review Package Path Audit",
        "",
        str(summary.get("claim_boundary", REVIEW_PACKAGE_PATH_AUDIT_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- ZIP path: `{summary.get('zip_path', '')}`",
        f"- ZIP present: `{str(summary.get('zip_present', False)).lower()}`",
        f"- ZIP valid: `{str(summary.get('zip_valid', False)).lower()}`",
        f"- ZIP files: {summary.get('zip_file_count', 0)}",
        f"- Review records: {summary.get('record_count', 0)}",
        f"- Path references: {summary.get('path_reference_count', 0)}",
        f"- Missing package paths: {summary.get('missing_package_path_count', 0)}",
        f"- Missing formal targets: {summary.get('missing_formal_target_count', 0)}",
        f"- Review package paths ready: `{str(summary.get('review_package_paths_ready', False)).lower()}`",
        f"- Acceptance ready: `{str(summary.get('acceptance_ready', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        f"- Status counts: {_format_counts(summary.get('status_counts', {}))}",
        "",
    ]
    missing_package = summary.get("missing_package_paths", [])
    if missing_package:
        lines.extend(["## Missing Package Paths", ""])
        lines.extend(_path_table(missing_package))
        lines.append("")
    missing_formal = summary.get("missing_formal_targets", [])
    if missing_formal:
        lines.extend(
            [
                "## Missing Formal Targets",
                "",
                "These paths are expected to remain absent until real formal "
                "acceptance decisions are supplied.",
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
        lines.append("- None for ZIP path hygiene. This still does not approve any gate.")
    lines.extend(
        [
            "",
            "## Handoff Sidecar",
            "",
            "Send `review_packages/expert_review_handoff_20260510.md` and "
            "`review_packages/expert_review_handoff_20260510.json` outside "
            "the ZIP as the checksum and cover-note sidecars. Keeping these "
            "files outside the ZIP prevents checksum reporting from changing "
            "the reviewed package.",
        ]
    )
    lines.append("")
    return "\n".join(lines)


def _audit_records(
    archive: ZipFile,
    record_paths: Iterable[str],
    names: set[str],
) -> tuple[list[PackagePathCheck], list[dict[str, str]]]:
    formal_targets = set(FORMAL_ARTIFACT_RELATIVE_PATHS) | {"docs/final_study_audit.md"}
    checks: list[PackagePathCheck] = []
    invalid_records: list[dict[str, str]] = []
    for record_path in record_paths:
        try:
            with archive.open(record_path) as handle:
                raw = json.loads(handle.read().decode("utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("record must be a JSON object")
            record = acceptance_record_from_mapping(raw)
        except Exception as exc:  # pragma: no cover - surfaced in audit artifact
            invalid_records.append({"record_path": record_path, "error": str(exc)})
            continue
        checks.extend(_record_checks(record, record_path, names, formal_targets))
    return checks, invalid_records


def _record_checks(
    record: AcceptanceRecord,
    record_path: str,
    names: set[str],
    formal_targets: set[str],
) -> list[PackagePathCheck]:
    fields = {
        "evidence": record.evidence,
        "source_paths": record.source_paths,
        "reviewed_inputs": record.reviewed_inputs,
        "review_packet_paths": record.review_packet_paths,
    }
    checks: list[PackagePathCheck] = []
    for field, values in fields.items():
        for value in values:
            path_text = _normalize_path(value)
            if not path_text or _looks_external(path_text):
                continue
            if path_text in names:
                status = "present"
            elif path_text in formal_targets:
                status = "missing_formal_target"
            else:
                status = "missing_package_path"
            checks.append(
                PackagePathCheck(
                    record_path=record_path,
                    gate_id=record.gate_id,
                    agent_id=record.agent_id,
                    field=field,
                    path=path_text,
                    status=status,
                )
            )
    return checks


def _missing_zip_summary(package: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": REVIEW_PACKAGE_PATH_AUDIT_CLAIM_BOUNDARY,
        "zip_path": _display_path(package),
        "zip_present": False,
        "zip_valid": False,
        "zip_size_bytes": 0,
        "zip_sha256": "",
        "zip_file_count": 0,
        "record_count": 0,
        "path_reference_count": 0,
        "present_path_count": 0,
        "missing_package_path_count": 0,
        "missing_formal_target_count": 0,
        "unique_missing_package_path_count": 0,
        "unique_missing_package_paths": [],
        "unique_missing_formal_target_count": 0,
        "unique_missing_formal_targets": [],
        "invalid_record_count": 0,
        "status_counts": {},
        "review_package_paths_ready": False,
        "acceptance_ready": False,
        "publication_ready": False,
        "can_mark_complete": False,
        "missing_package_paths": [],
        "missing_formal_targets": [],
        "invalid_records": [],
        "remaining_blockers": [f"{_display_path(package)} is absent"],
        "review_items": ["build the review ZIP before running this audit"],
    }


def _invalid_zip_summary(package: Path, error: str) -> dict[str, Any]:
    summary = _missing_zip_summary(package)
    summary.update(
        {
            "zip_present": True,
            "zip_size_bytes": package.stat().st_size if package.exists() else 0,
            "zip_sha256": _sha256(package) if package.exists() else "",
            "invalid_records": [{"record_path": _display_path(package), "error": error}],
            "invalid_record_count": 1,
            "status_counts": {"invalid_zip": 1},
            "remaining_blockers": [f"{_display_path(package)} is not a valid ZIP: {error}"],
        }
    )
    return summary


def _remaining_blockers(
    package: Path,
    invalid_records: list[dict[str, str]],
    missing_paths: list[str],
    record_paths: list[str],
) -> list[str]:
    blockers: list[str] = []
    if not record_paths:
        blockers.append("review package contains no agent review records")
    if invalid_records:
        blockers.append("fix invalid agent review records inside the review ZIP")
    blockers.extend(f"include referenced package path: {path}" for path in missing_paths)
    if not package.exists():
        blockers.append(f"{_display_path(package)} is absent")
    return blockers


def _status_counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


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


def _format_counts(value: object) -> str:
    if not isinstance(value, dict) or not value:
        return "none"
    return ", ".join(f"{key}={count}" for key, count in sorted(value.items()))


def _normalize_path(value: str) -> str:
    return value.strip().replace("\\", "/").lstrip("./")


def _looks_external(value: str) -> bool:
    lower = value.lower()
    return lower.startswith(("http://", "https://", "doi:", "urn:"))


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_DOC",
    "DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_MANIFEST",
    "DEFAULT_REVIEW_PACKAGE_ZIP",
    "REVIEW_PACKAGE_PATH_AUDIT_CLAIM_BOUNDARY",
    "audit_review_package_paths",
    "build_review_package_path_audit_markdown",
    "write_review_package_path_audit",
]
