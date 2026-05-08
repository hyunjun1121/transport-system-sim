"""Source provenance priority packet.

This module joins source/license review rows with URL remediation rows. The
output ranks provenance work by source so reviewers can separate context-source
target gaps, cached snapshots, repository inputs, and URL remediation without
creating source acceptance or license certification.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.source_license_review_packet import (
    DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
)
from src.realworld.source_url_remediation_packet import (
    DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_provenance_priority_packet.csv"
)
DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_provenance_priority_manifest.json"
)
DEFAULT_SOURCE_PROVENANCE_PRIORITY_DOC_PATH = (
    PROJECT_ROOT / "docs" / "source_provenance_priority_packet.md"
)
SOURCE_PROVENANCE_PRIORITY_SCOPE = (
    "Source provenance priority packet only; not source acceptance, not "
    "license certification, not calibrated real-world validation, not "
    "provenance gate closure, and not operational routing approval."
)
SOURCE_PROVENANCE_PRIORITY_COLUMNS: tuple[str, ...] = (
    "source_id",
    "source_name",
    "source_type",
    "review_status",
    "priority_status",
    "review_priority",
    "snapshot_status",
    "local_artifact_count",
    "url_row_count",
    "reachable_url_count",
    "url_remediation_status_counts",
    "license_review_required",
    "attribution_review_required",
    "snapshot_review_required",
    "privacy_review_required",
    "reproducibility_review_required",
    "required_reviewer_decision",
    "url_required_reviewer_actions",
    "alternate_url_candidates",
    "source_url_or_citation",
    "target_acceptance_artifact",
    "publication_use_status",
    "can_support_final_provenance_gate",
    "claim_boundary",
    "notes",
)


def build_source_provenance_priority_rows(
    *,
    source_license_review_path: str | Path = DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
    source_url_remediation_path: str | Path = DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return one priority row per source from current provenance packets."""

    license_rows = _read_csv_rows(source_license_review_path)
    remediation_rows = _read_csv_rows(source_url_remediation_path)
    remediation_by_source = _group_by(remediation_rows, "source_id")
    rows = [
        _priority_row(
            row,
            remediation_by_source.get(str(row.get("source_id", "")), []),
        )
        for row in license_rows
    ]
    rows.sort(key=_priority_sort_key)
    return rows


def write_source_provenance_priority_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_DOC_PATH,
    source_license_review_path: str | Path = DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
    source_url_remediation_path: str | Path = DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
) -> dict[str, Any]:
    """Write source provenance priority CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=SOURCE_PROVENANCE_PRIORITY_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in SOURCE_PROVENANCE_PRIORITY_COLUMNS
                }
            )

    summary = build_source_provenance_priority_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        source_license_review_path=source_license_review_path,
        source_url_remediation_path=source_url_remediation_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_source_provenance_priority_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_source_provenance_priority_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_DOC_PATH,
    source_license_review_path: str | Path = DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
    source_url_remediation_path: str | Path = DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for source provenance priority rows."""

    priority_counts = _counts(row.get("priority_status", "") for row in rows)
    review_priority_counts = _counts(row.get("review_priority", "") for row in rows)
    review_status_counts = _counts(row.get("review_status", "") for row in rows)
    source_type_counts = _counts(row.get("source_type", "") for row in rows)
    return {
        "schema_version": 1,
        "result_scope": SOURCE_PROVENANCE_PRIORITY_SCOPE,
        "claim_boundary": (
            "This packet prioritizes existing source provenance review work. "
            "It does not create provenance_acceptance.json, certify license "
            "compatibility, accept source snapshots, or close provenance, "
            "validation, reproducibility, or final-study gates."
        ),
        "row_count": len(rows),
        "source_type_counts": source_type_counts,
        "review_status_counts": review_status_counts,
        "priority_status_counts": priority_counts,
        "review_priority_counts": review_priority_counts,
        "blocking_source_count": sum(
            1
            for row in rows
            if str(row.get("priority_status", "")).startswith("blocked_")
        ),
        "human_review_source_count": sum(
            1
            for row in rows
            if str(row.get("priority_status", "")).startswith("needs_human_review_")
        ),
        "context_only_source_count": sum(
            1 for row in rows if row.get("review_status") == "context_only_not_cached"
        ),
        "cached_snapshot_source_count": sum(
            1
            for row in rows
            if row.get("review_status") == "cached_snapshot_pending_review"
        ),
        "repository_input_source_count": sum(
            1
            for row in rows
            if row.get("review_status") == "repository_input_pending_review"
        ),
        "url_remediation_row_count": sum(
            _int_value(row.get("url_row_count", "0")) for row in rows
        ),
        "alternate_url_candidate_source_count": sum(
            1
            for row in rows
            if str(row.get("alternate_url_candidates", "")).strip()
        ),
        "alternate_url_issue_source_count": sum(
            1
            for row in rows
            if "alternate_reachable_url_needs_review" in row.get(
                "url_remediation_status_counts",
                "",
            )
        ),
        "local_citation_review_source_count": sum(
            1
            for row in rows
            if "local_citation_needs_review" in row.get(
                "url_remediation_status_counts",
                "",
            )
        ),
        "provenance_gate_closure_candidate_count": sum(
            1
            for row in rows
            if str(row.get("can_support_final_provenance_gate", "")).lower()
            == "true"
        ),
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "source_license_review_packet": _display_path(source_license_review_path),
            "source_url_remediation_packet": _display_path(
                source_url_remediation_path
            ),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "provide reviewed target payloads or explicitly exclude context-source rows before final claims",
            "review cached public snapshots for license, attribution, snapshot, and reproducibility suitability",
            "confirm project-owned local citations and privacy abstraction for repository inputs",
            "resolve alternate URL issues before provenance acceptance",
            "create data/manifests/provenance_acceptance.json only after source-backed review",
        ],
        "remaining_blockers": [
            "formal provenance acceptance record is absent",
            "context-source target artifacts still need reviewed payloads or exclusion decisions",
            "cached public snapshots still require license, attribution, snapshot, and reproducibility review",
            "repository inputs still require human scope/privacy/reproducibility review",
            "URL remediation rows still require reviewer confirmation",
        ],
    }


def build_source_provenance_priority_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for source provenance priority review."""

    lines = [
        "# Source Provenance Priority Packet",
        "",
        str(manifest.get("claim_boundary", SOURCE_PROVENANCE_PRIORITY_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Priority rows: {manifest.get('row_count', 0)}",
        f"- Blocking sources: {manifest.get('blocking_source_count', 0)}",
        f"- Human-review sources: {manifest.get('human_review_source_count', 0)}",
        f"- Priority status counts: `{manifest.get('priority_status_counts', {})}`",
        "",
        "## Priority Rows",
        "",
        "| Source | Type | Status | Priority | URLs | Alternate Candidates | Required Decision |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {source} | {stype} | {status} | {priority} | {urls} | {candidates} | {decision} |".format(
                source=_cell(row.get("source_id", "")),
                stype=_cell(row.get("source_type", "")),
                status=_cell(row.get("priority_status", "")),
                priority=_cell(row.get("review_priority", "")),
                urls=_cell(row.get("url_remediation_status_counts", "")),
                candidates=_cell(row.get("alternate_url_candidates", "")),
                decision=_cell(row.get("required_reviewer_decision", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is source-provenance prioritization support only.",
            "- It does not certify source terms, license compatibility, or snapshot suitability.",
            "- It cannot create or replace `data/manifests/provenance_acceptance.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def _priority_row(
    source: Mapping[str, str],
    remediation_rows: Sequence[Mapping[str, str]],
) -> dict[str, str]:
    priority_status, review_priority = _classify_priority(source, remediation_rows)
    remediation_status_counts = _counts(
        row.get("remediation_status", "") for row in remediation_rows
    )
    actions = _join_sorted(
        row.get("required_reviewer_action", "") for row in remediation_rows
    )
    alternate_url_candidates = _join_sorted(
        row.get("alternate_url_candidates", "") for row in remediation_rows
    )
    return {
        "source_id": str(source.get("source_id", "")),
        "source_name": str(source.get("source_name", "")),
        "source_type": str(source.get("source_type", "")),
        "review_status": str(source.get("review_status", "")),
        "priority_status": priority_status,
        "review_priority": review_priority,
        "snapshot_status": str(source.get("snapshot_status", "")),
        "local_artifact_count": str(source.get("local_artifact_count", "")),
        "url_row_count": str(len(remediation_rows)),
        "reachable_url_count": str(
            sum(1 for row in remediation_rows if row.get("url_status") == "reachable")
        ),
        "url_remediation_status_counts": _format_counts(remediation_status_counts),
        "license_review_required": str(source.get("license_review_required", "")),
        "attribution_review_required": str(
            source.get("attribution_review_required", "")
        ),
        "snapshot_review_required": str(source.get("snapshot_review_required", "")),
        "privacy_review_required": str(source.get("privacy_review_required", "")),
        "reproducibility_review_required": str(
            source.get("reproducibility_review_required", "")
        ),
        "required_reviewer_decision": str(
            source.get("required_reviewer_decision", "")
        ),
        "url_required_reviewer_actions": actions,
        "alternate_url_candidates": alternate_url_candidates,
        "source_url_or_citation": str(source.get("source_url_or_citation", "")),
        "target_acceptance_artifact": str(
            source.get(
                "target_acceptance_artifact",
                "data/manifests/provenance_acceptance.json",
            )
        ),
        "publication_use_status": str(source.get("publication_use_status", "")),
        "can_support_final_provenance_gate": "false",
        "claim_boundary": SOURCE_PROVENANCE_PRIORITY_SCOPE,
        "notes": str(source.get("notes", "")),
    }


def _classify_priority(
    source: Mapping[str, str],
    remediation_rows: Sequence[Mapping[str, str]],
) -> tuple[str, str]:
    review_status = str(source.get("review_status", ""))
    remediation_statuses = {
        str(row.get("remediation_status", "")) for row in remediation_rows
    }
    if review_status == "context_only_not_cached":
        return "blocked_context_only_source_not_cached", "high"
    if any(status.startswith("blocked_") for status in remediation_statuses):
        return "blocked_url_remediation_required", "high"
    if "live_check_required" in remediation_statuses:
        return "blocked_live_url_check_required", "high"
    if review_status == "cached_snapshot_pending_review":
        return "needs_human_review_cached_snapshot_source", "high"
    if review_status == "repository_input_pending_review":
        return "needs_human_review_repository_input_source", "medium"
    if "alternate_reachable_url_needs_review" in remediation_statuses:
        return "needs_human_review_alternate_url_source", "medium"
    return "needs_human_review_source_provenance", "medium"


def _priority_sort_key(row: Mapping[str, str]) -> tuple[int, str, str]:
    status = str(row.get("priority_status", ""))
    if status.startswith("blocked_"):
        order = 0
    elif row.get("review_priority") == "high":
        order = 1
    elif row.get("review_priority") == "medium":
        order = 2
    else:
        order = 3
    return (order, str(row.get("source_type", "")), str(row.get("source_id", "")))


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    filepath = Path(path)
    with filepath.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _group_by(
    rows: Sequence[Mapping[str, str]],
    key: str,
) -> dict[str, list[Mapping[str, str]]]:
    grouped: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key, ""))].append(row)
    return dict(grouped)


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] += 1
    return dict(sorted(counts.items()))


def _format_counts(counts: Mapping[str, int]) -> str:
    return "; ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _join_sorted(values: Iterable[Any]) -> str:
    return "; ".join(sorted({str(value).strip() for value in values if str(value).strip()}))


def _int_value(value: Any) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_SOURCE_PROVENANCE_PRIORITY_DOC_PATH",
    "DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH",
    "DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH",
    "SOURCE_PROVENANCE_PRIORITY_COLUMNS",
    "SOURCE_PROVENANCE_PRIORITY_SCOPE",
    "build_source_provenance_priority_manifest",
    "build_source_provenance_priority_markdown",
    "build_source_provenance_priority_rows",
    "write_source_provenance_priority_packet",
]
