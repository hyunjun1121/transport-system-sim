"""Source and license review-packet generation.

The source-provenance manifest records what sources exist. This module turns
those records into one reviewer row per source so license, attribution,
snapshot, privacy, and reproducibility decisions are concrete. It deliberately
does not create ``provenance_acceptance.json`` and does not mark any source as
accepted.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.source_provenance import (
    DEFAULT_SOURCE_PROVENANCE_PATH,
    SourceProvenanceRecord,
    load_source_provenance_manifest,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_license_review_packet.csv"
)
DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_license_review_manifest.json"
)
DEFAULT_SOURCE_LICENSE_REVIEW_DOC_PATH = (
    PROJECT_ROOT / "docs" / "source_license_review_packet.md"
)
SOURCE_LICENSE_REVIEW_SCOPE = (
    "Source/license review packet only; not source acceptance, not license "
    "certification, not calibrated real-world validation, and not operational "
    "routing approval."
)
SOURCE_LICENSE_REVIEW_COLUMNS: tuple[str, ...] = (
    "source_id",
    "source_name",
    "source_type",
    "review_status",
    "source_url_or_citation",
    "license_or_terms",
    "local_artifact_count",
    "missing_local_artifacts",
    "snapshot_status",
    "license_review_required",
    "attribution_review_required",
    "snapshot_review_required",
    "privacy_review_required",
    "reproducibility_review_required",
    "required_reviewer_decision",
    "target_acceptance_artifact",
    "can_support_final_provenance_gate",
    "publication_use_status",
    "claim_boundary",
    "notes",
)


def build_source_license_review_rows(
    *,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> list[dict[str, str]]:
    """Return source/license review rows for every provenance manifest record."""

    manifest = load_source_provenance_manifest(provenance_manifest_path)
    return [_row_for_record(record) for record in manifest.records]


def write_source_license_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_LICENSE_REVIEW_DOC_PATH,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown source/license review artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=SOURCE_LICENSE_REVIEW_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({column: str(row.get(column, "")) for column in SOURCE_LICENSE_REVIEW_COLUMNS})

    summary = build_source_license_review_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        provenance_manifest_path=provenance_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_source_license_review_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_source_license_review_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_LICENSE_REVIEW_DOC_PATH,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for the source/license review packet."""

    status_counts = _counts(row.get("review_status", "") for row in rows)
    source_type_counts = _counts(row.get("source_type", "") for row in rows)
    snapshot_status_counts = _counts(row.get("snapshot_status", "") for row in rows)
    missing_snapshot_count = sum(
        1 for row in rows if row.get("snapshot_status") != "local_artifacts_present"
    )
    review_required_count = sum(
        1
        for row in rows
        if _is_true(row.get("license_review_required", "false"))
        or _is_true(row.get("attribution_review_required", "false"))
        or _is_true(row.get("snapshot_review_required", "false"))
        or _is_true(row.get("privacy_review_required", "false"))
        or _is_true(row.get("reproducibility_review_required", "false"))
    )
    closure_candidate_count = sum(
        1 for row in rows if _is_true(row.get("can_support_final_provenance_gate", "false"))
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            SOURCE_LICENSE_REVIEW_SCOPE
            + " A reviewer must still create data/manifests/provenance_acceptance.json "
            "from source-backed decisions before the provenance gate can close."
        ),
        "result_scope": SOURCE_LICENSE_REVIEW_SCOPE,
        "row_count": len(rows),
        "source_type_counts": source_type_counts,
        "review_status_counts": status_counts,
        "snapshot_status_counts": snapshot_status_counts,
        "review_required_count": review_required_count,
        "missing_snapshot_or_context_only_count": missing_snapshot_count,
        "provenance_gate_closure_candidate_count": closure_candidate_count,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "source_provenance_manifest": _display_path(Path(provenance_manifest_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "verify each source URL, license, attribution requirement, and derivative-use constraint",
            "provide reviewed target payloads for context-source rows or explicitly exclude them from final claims",
            "confirm local artifact paths and snapshot dates for every cached source",
            "review project-owned synthetic/privacy abstraction before provenance acceptance",
            "create data/manifests/provenance_acceptance.json only after all retained sources are reviewed",
        ],
        "remaining_blockers": [
            "formal provenance acceptance record is absent",
            "source/license packet rows are review aids and do not certify license compatibility",
            "context-source target artifacts still need reviewed payloads or explicit exclusion from final claims",
        ],
    }


def build_source_license_review_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable source/license review packet."""

    lines = [
        "# Source And License Review Packet",
        "",
        str(manifest.get("claim_boundary", SOURCE_LICENSE_REVIEW_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Source rows: {manifest.get('row_count', 0)}",
        f"- Rows requiring review: {manifest.get('review_required_count', 0)}",
        f"- Closure candidates: {manifest.get('provenance_gate_closure_candidate_count', 0)}",
        "",
        "## Source Review Rows",
        "",
        "| Source | Status | Snapshot | Required Decision | Final Gate Support |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {source} | {status} | {snapshot} | {decision} | `{support}` |".format(
                source=_cell(row.get("source_id", "")),
                status=_cell(row.get("review_status", "")),
                snapshot=_cell(row.get("snapshot_status", "")),
                decision=_cell(row.get("required_reviewer_decision", "")),
                support=_cell(row.get("can_support_final_provenance_gate", "false")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Review official source terms and attribution requirements for every retained public source.",
            "- Provide reviewed target payloads or exclude context-source rows before using them in final claims.",
            "- Confirm project-owned synthetic/privacy abstractions before accepting the pilot package.",
            "- Create `data/manifests/provenance_acceptance.json` only after source-backed review.",
            "",
        ]
    )
    return "\n".join(lines)


def _row_for_record(record: SourceProvenanceRecord) -> dict[str, str]:
    missing = _missing_artifacts(record)
    snapshot_status = _snapshot_status(record, missing)
    source_requires_license_review = record.source_type not in {
        "repository_input",
    }
    privacy_review_required = record.source_id in {
        "pilot_region_spec",
        "structured_scenario_tables",
    }
    reproducibility_review_required = (
        bool(missing)
        or record.review_status != "reviewed"
        or record.review_status == "context_only_not_cached"
    )
    can_support_final = (
        record.review_status == "reviewed"
        and not missing
        and "not operational" in record.claim_boundary.lower()
    )
    return {
        "source_id": record.source_id,
        "source_name": record.source_name,
        "source_type": record.source_type,
        "review_status": record.review_status,
        "source_url_or_citation": record.source_url_or_citation,
        "license_or_terms": record.license_or_terms,
        "local_artifact_count": str(len(record.local_artifact_paths)),
        "missing_local_artifacts": ";".join(missing),
        "snapshot_status": snapshot_status,
        "license_review_required": _bool_text(source_requires_license_review),
        "attribution_review_required": _bool_text(source_requires_license_review),
        "snapshot_review_required": _bool_text(record.review_status != "reviewed" or bool(missing)),
        "privacy_review_required": _bool_text(privacy_review_required),
        "reproducibility_review_required": _bool_text(reproducibility_review_required),
        "required_reviewer_decision": _required_decision(record, snapshot_status),
        "target_acceptance_artifact": "data/manifests/provenance_acceptance.json",
        "can_support_final_provenance_gate": _bool_text(can_support_final),
        "publication_use_status": _publication_use_status(record, can_support_final),
        "claim_boundary": SOURCE_LICENSE_REVIEW_SCOPE,
        "notes": record.notes,
    }


def _required_decision(record: SourceProvenanceRecord, snapshot_status: str) -> str:
    if record.review_status == "context_only_not_cached":
        return (
            "provide a reviewed target payload with terms/attribution review, "
            "or exclude this context-source row from final-study claims"
        )
    if snapshot_status != "local_artifacts_present":
        return "repair or document missing local artifacts before provenance acceptance"
    if record.review_status == "cached_snapshot_pending_review":
        return "review source terms, attribution, snapshot date, and retained local artifacts"
    if record.review_status == "repository_input_pending_review":
        return "review project-owned assumptions, privacy abstraction, and claim boundary"
    if record.review_status == "reviewed":
        return "ensure the formal provenance acceptance record cites this reviewed source"
    return "resolve unsupported review status before provenance acceptance"


def _publication_use_status(record: SourceProvenanceRecord, can_support_final: bool) -> str:
    if can_support_final:
        return "eligible for formal provenance acceptance if cited by reviewer"
    if record.review_status == "context_only_not_cached":
        return "context only; cannot support final claims until cached or excluded"
    if record.review_status == "repository_input_pending_review":
        return "repository input pending human/source-scope review"
    if record.review_status == "cached_snapshot_pending_review":
        return "cached source pending license, attribution, and snapshot review"
    return "not accepted for final claims"


def _snapshot_status(record: SourceProvenanceRecord, missing: Sequence[str]) -> str:
    if record.review_status == "context_only_not_cached":
        return "context_only_not_cached"
    if missing:
        return "missing_local_artifacts"
    return "local_artifacts_present"


def _missing_artifacts(record: SourceProvenanceRecord) -> list[str]:
    missing: list[str] = []
    for relative in record.local_artifact_paths:
        if not (PROJECT_ROOT / relative).exists():
            missing.append(relative)
    return missing


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _is_true(value: str) -> bool:
    return str(value).strip().lower() == "true"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_SOURCE_LICENSE_REVIEW_DOC_PATH",
    "DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH",
    "DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH",
    "SOURCE_LICENSE_REVIEW_COLUMNS",
    "SOURCE_LICENSE_REVIEW_SCOPE",
    "build_source_license_review_manifest",
    "build_source_license_review_markdown",
    "build_source_license_review_rows",
    "write_source_license_review_packet",
]
