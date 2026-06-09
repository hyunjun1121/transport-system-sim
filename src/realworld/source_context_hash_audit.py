"""Raw-file hash audit for cached source-context extracts.

This audit covers small public-source context caches used as reviewer input.
It verifies that cached raw files still match the SHA256 values recorded in
their review extracts. It is not source acceptance, rail evidence, provenance
acceptance, or final-study readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.ktdb_gtfs_source import audit_ktdb_gtfs_raw_hashes
from src.realworld.metro9_capacity_source import audit_metro9_capacity_raw_hash


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_context_hash_audit.json"
)
DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_DOC_PATH = (
    PROJECT_ROOT / "docs" / "source_context_hash_audit.md"
)
SOURCE_CONTEXT_HASH_AUDIT_SCOPE = (
    "Source-context raw-file hash audit only; not source acceptance, not "
    "license certification, not GTFS validation, not rail timing evidence, "
    "not rail capacity acceptance, not provenance gate closure, and not "
    "operational routing approval."
)


def build_source_context_hash_audit() -> dict[str, Any]:
    """Return a conservative source-context raw-file hash audit manifest."""

    source_audits = [
        _source_summary("ktdb_gtfs_source_context", audit_ktdb_gtfs_raw_hashes()),
        _source_summary("metro9_capacity_source_context", audit_metro9_capacity_raw_hash()),
    ]
    ready_count = sum(
        1 for audit in source_audits if audit["raw_file_integrity_ready"]
    )
    file_records = [
        file_record
        for source in source_audits
        for file_record in source["file_records"]
    ]
    blocker_count = sum(len(audit["remaining_hash_blockers"]) for audit in source_audits)
    gate_blockers = _remaining_gate_blockers()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result_scope": SOURCE_CONTEXT_HASH_AUDIT_SCOPE,
        "claim_boundary": (
            "This manifest proves only that retained source-context review "
            "extracts match their cached raw byte payloads. It does not prove "
            "license rights, GTFS validity, transit service calibration, "
            "source provenance acceptance, or final-study readiness."
        ),
        "row_count": len(file_records),
        "source_count": len(source_audits),
        "raw_file_count": len(file_records),
        "source_context_count": len(source_audits),
        "raw_file_integrity_ready_count": ready_count,
        "raw_file_integrity_blocker_count": blocker_count,
        "raw_file_integrity_ready": ready_count == len(source_audits)
        and blocker_count == 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "can_support_rail_evidence_gate": False,
        "can_support_final_provenance_gate": False,
        "provenance_gate_closure_candidate_count": 0,
        "rail_evidence_gate_closure_candidate_count": 0,
        "sources": source_audits,
        "file_records": file_records,
        "remaining_hash_blockers": _remaining_hash_blockers(source_audits),
        "remaining_gate_blockers": gate_blockers,
        "remaining_blockers": _remaining_hash_blockers(source_audits) + gate_blockers,
        "review_items": [
            "retain the raw source payloads with the review extract files",
            "review source terms, attribution, and retention duties separately",
            "do not use source-context hash integrity as GTFS validation",
            "do not promote capacity or timing claims without reviewed evidence",
        ],
    }


def write_source_context_hash_audit(
    *,
    manifest_path: str | Path = DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_DOC_PATH,
) -> dict[str, Any]:
    """Write the source-context hash audit manifest and Markdown summary."""

    manifest = build_source_context_hash_audit()
    manifest_output = Path(manifest_path)
    doc_output = Path(doc_path)
    manifest_output.parent.mkdir(parents=True, exist_ok=True)
    doc_output.parent.mkdir(parents=True, exist_ok=True)
    manifest_output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc_output.write_text(
        build_source_context_hash_audit_markdown(manifest),
        encoding="utf-8",
    )
    return manifest


def build_source_context_hash_audit_markdown(
    manifest: Mapping[str, Any],
) -> str:
    """Return Markdown for the source-context hash audit."""

    lines = [
        "# Source Context Hash Audit",
        "",
        str(manifest.get("claim_boundary", SOURCE_CONTEXT_HASH_AUDIT_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Raw-file integrity ready: `{str(manifest.get('raw_file_integrity_ready', False)).lower()}`",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Source-context rows: {manifest.get('source_context_count', 0)}",
        f"- Raw files checked: {manifest.get('raw_file_count', 0)}",
        f"- Integrity-ready rows: {manifest.get('raw_file_integrity_ready_count', 0)}",
        f"- Integrity blockers: {manifest.get('raw_file_integrity_blocker_count', 0)}",
        f"- Can support rail evidence gate: `{str(manifest.get('can_support_rail_evidence_gate', False)).lower()}`",
        f"- Can support final provenance gate: `{str(manifest.get('can_support_final_provenance_gate', False)).lower()}`",
        "",
        "## Source Hash Checks",
        "",
        "| Source | Raw Payload | Recorded SHA256 | Computed SHA256 | Match |",
        "| --- | --- | --- | --- | --- |",
    ]
    for file_record in manifest.get("file_records", []):
        if not isinstance(file_record, Mapping):
            continue
        lines.append(
            "| {source_id} | {raw_path} | {recorded} | {computed} | {match} |".format(
                source_id=_cell(file_record.get("source_id", "")),
                raw_path=_cell(file_record.get("raw_path", "")),
                recorded=_cell(file_record.get("recorded_sha256", "")),
                computed=_cell(file_record.get("computed_sha256", "")),
                match=_cell(file_record.get("sha256_matches", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This audit checks cached raw-file hash integrity only.",
            "- It does not validate GTFS structure, rail timetable timing, source license, or operator capacity acceptance.",
            "- Keep provenance, rail evidence, publication, final-study, and formal acceptance gates blocked until reviewed evidence exists.",
            "",
        ]
    )
    return "\n".join(lines)


def _source_summary(source_id: str, audit: Mapping[str, Any]) -> dict[str, Any]:
    raw_paths = []
    for key in ("notice_raw_path", "list_raw_path", "raw_path"):
        value = str(audit.get(key, "")).strip()
        if value:
            raw_paths.append(_display_path(value))
    return {
        "source_id": source_id,
        "source_extract_id": str(audit.get("source_id", "")),
        "result_scope": str(audit.get("result_scope", "")),
        "extract_path": _display_path(str(audit.get("extract_path", ""))),
        "raw_paths": raw_paths,
        "file_records": _file_records(source_id, audit),
        "raw_file_integrity_ready": bool(audit.get("raw_file_integrity_ready")),
        "publication_ready": False,
        "can_mark_complete": False,
        "can_support_rail_evidence_gate": False,
        "can_support_final_provenance_gate": False,
        "remaining_hash_blockers": list(audit.get("remaining_blockers", [])),
        "remaining_gate_blockers": _remaining_gate_blockers(),
        "remaining_blockers": list(audit.get("remaining_blockers", []))
        + _remaining_gate_blockers(),
        "claim_boundary": str(audit.get("claim_boundary", "")),
    }


def _file_records(source_id: str, audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    if source_id == "ktdb_gtfs_source_context":
        return [
            {
                "source_id": source_id,
                "file_role": "notice_raw_html",
                "extract_path": _display_path(str(audit.get("extract_path", ""))),
                "raw_path": _display_path(str(audit.get("notice_raw_path", ""))),
                "recorded_sha256": str(
                    audit.get("notice_recorded_raw_file_sha256", "")
                ),
                "computed_sha256": str(audit.get("notice_raw_file_sha256", "")),
                "sha256_matches": bool(
                    audit.get("notice_raw_file_sha256_matches", False)
                ),
                "raw_file_integrity_ready": bool(
                    audit.get("notice_raw_file_sha256_matches", False)
                ),
            },
            {
                "source_id": source_id,
                "file_role": "dataset_list_raw_html",
                "extract_path": _display_path(str(audit.get("extract_path", ""))),
                "raw_path": _display_path(str(audit.get("list_raw_path", ""))),
                "recorded_sha256": str(
                    audit.get("list_recorded_raw_file_sha256", "")
                ),
                "computed_sha256": str(audit.get("list_raw_file_sha256", "")),
                "sha256_matches": bool(
                    audit.get("list_raw_file_sha256_matches", False)
                ),
                "raw_file_integrity_ready": bool(
                    audit.get("list_raw_file_sha256_matches", False)
                ),
            },
        ]
    return [
        {
            "source_id": source_id,
            "file_role": "source_raw_html",
            "extract_path": _display_path(str(audit.get("extract_path", ""))),
            "raw_path": _display_path(str(audit.get("raw_path", ""))),
            "recorded_sha256": str(audit.get("recorded_raw_file_sha256", "")),
            "computed_sha256": str(audit.get("raw_file_sha256", "")),
            "sha256_matches": bool(audit.get("raw_file_sha256_matches", False)),
            "raw_file_integrity_ready": bool(
                audit.get("raw_file_sha256_matches", False)
            ),
        }
    ]


def _remaining_hash_blockers(
    source_audits: Sequence[Mapping[str, Any]],
) -> list[str]:
    blockers: list[str] = []
    for source in source_audits:
        for blocker in source.get("remaining_hash_blockers", []):
            blockers.append(f"{source.get('source_id', '')}: {blocker}")
    return blockers


def _remaining_gate_blockers() -> list[str]:
    return [
        "source terms, license, attribution, and retention review are outside this hash audit",
        "formal provenance acceptance is absent",
        "rail timing and capacity evidence remain unaccepted",
    ]


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _cell(value: object) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    return text or "-"


__all__ = [
    "DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_DOC_PATH",
    "DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_MANIFEST_PATH",
    "SOURCE_CONTEXT_HASH_AUDIT_SCOPE",
    "build_source_context_hash_audit",
    "build_source_context_hash_audit_markdown",
    "write_source_context_hash_audit",
]
