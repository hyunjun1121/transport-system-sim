"""Context-source cache, retention, or exclusion decision worksheet.

This module turns context-cache requests into per-source reviewer decision
rows. It does not fetch sources, cache extracts, certify licenses, or create
``provenance_acceptance.json``.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.source_context_cache_request_packet import (
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
)
from src.realworld.source_provenance import DEFAULT_SOURCE_PROVENANCE_PATH
from src.realworld.source_provenance_priority_packet import (
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
)
from src.realworld.source_url_remediation_packet import (
    DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_context_cache_decision_packet.csv"
)
DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_context_cache_decision_manifest.json"
)
DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "source_context_cache_decision_packet.md"
)
SOURCE_CONTEXT_CACHE_DECISION_SCOPE = (
    "Source context-cache decision packet only; not source acceptance, not "
    "license certification, not cached source evidence, not provenance gate "
    "closure, and not operational routing approval."
)
SOURCE_CONTEXT_CACHE_DECISION_COLUMNS: tuple[str, ...] = (
    "source_id",
    "source_name",
    "source_type",
    "decision_topic",
    "current_cache_request_status",
    "candidate_decision_options",
    "provisional_decision",
    "decision_status",
    "blocking_reason",
    "target_cache_artifacts",
    "target_cache_artifacts_present",
    "source_url_or_citation",
    "required_reviewer_action",
    "required_evidence_fields",
    "followup_artifacts",
    "evidence_input_paths",
    "target_acceptance_artifact",
    "can_support_final_provenance_gate",
    "claim_boundary",
)


def build_source_context_cache_decision_rows(
    *,
    request_rows: Sequence[Mapping[str, str]] | None = None,
    request_packet_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
    request_manifest_path: str
    | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    source_priority_packet_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    source_url_remediation_packet_path: str
    | Path = DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> list[dict[str, str]]:
    """Return one pending cache/retention/exclusion decision row per context source."""

    rows = (
        list(request_rows)
        if request_rows is not None
        else _read_csv_rows(request_packet_path)
    )
    evidence_paths = _evidence_paths(
        request_packet_path=request_packet_path,
        request_manifest_path=request_manifest_path,
        source_priority_packet_path=source_priority_packet_path,
        source_url_remediation_packet_path=source_url_remediation_packet_path,
        provenance_manifest_path=provenance_manifest_path,
    )
    decision_rows = [_decision_row(row, evidence_paths=evidence_paths) for row in rows]
    decision_rows.sort(key=lambda row: (row["decision_status"], row["source_id"]))
    return decision_rows


def write_source_context_cache_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_DOC_PATH,
    request_packet_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
    request_manifest_path: str
    | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    source_priority_packet_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    source_url_remediation_packet_path: str
    | Path = DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> dict[str, Any]:
    """Write source context-cache decision CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=SOURCE_CONTEXT_CACHE_DECISION_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in SOURCE_CONTEXT_CACHE_DECISION_COLUMNS
                }
            )

    summary = build_source_context_cache_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        request_packet_path=request_packet_path,
        request_manifest_path=request_manifest_path,
        source_priority_packet_path=source_priority_packet_path,
        source_url_remediation_packet_path=source_url_remediation_packet_path,
        provenance_manifest_path=provenance_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_source_context_cache_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_source_context_cache_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_DOC_PATH,
    request_packet_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
    request_manifest_path: str
    | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    source_priority_packet_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    source_url_remediation_packet_path: str
    | Path = DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for context-cache decision rows."""

    status_counts = _counts(row.get("decision_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("decision_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("decision_status", "")).startswith("needs_human_review_")
    )
    missing_target_count = sum(
        1
        for row in rows
        if str(row.get("target_cache_artifacts_present", "")).lower() != "true"
    )
    return {
        "schema_version": 1,
        "result_scope": SOURCE_CONTEXT_CACHE_DECISION_SCOPE,
        "claim_boundary": (
            SOURCE_CONTEXT_CACHE_DECISION_SCOPE
            + " It cannot create data/manifests/provenance_acceptance.json."
        ),
        "row_count": len(rows),
        "decision_ids": [str(row.get("source_id", "")) for row in rows],
        "decision_status_counts": status_counts,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "missing_target_cache_artifact_count": missing_target_count,
        "cache_retention_or_exclusion_decision_recorded": False,
        "provenance_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "source_context_cache_request_packet": _display_path(request_packet_path),
            "source_context_cache_request_manifest": _display_path(
                request_manifest_path
            ),
            "source_provenance_priority_packet": _display_path(
                source_priority_packet_path
            ),
            "source_url_remediation_packet": _display_path(
                source_url_remediation_packet_path
            ),
            "source_provenance_manifest": _display_path(provenance_manifest_path),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "choose cache, sensitivity/context-only retention, or exclusion treatment for each context source",
            "record reviewer, decision date, license/terms result, and attribution duties outside this packet",
            "retain raw responses and SHA256 evidence when a source is cached",
            "derive downstream rail evidence only after retained source extracts are reviewed",
            "record release-scope provenance only in data/manifests/provenance_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_source_context_cache_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for the context-cache decision worksheet."""

    lines = [
        "# Source Context Cache Decision Packet",
        "",
        str(manifest.get("claim_boundary", SOURCE_CONTEXT_CACHE_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Cache/retention/exclusion decision recorded: `{str(manifest.get('cache_retention_or_exclusion_decision_recorded', False)).lower()}`",
        f"- Decision rows: {manifest.get('row_count', 0)}",
        f"- Blocking decisions: {manifest.get('blocking_decision_count', 0)}",
        f"- Human-review decisions: {manifest.get('human_review_decision_count', 0)}",
        f"- Missing target cache artifacts: {manifest.get('missing_target_cache_artifact_count', 0)}",
        "",
        "## Decision Rows",
        "",
        "| Source | Status | Options | Target Artifacts | Required Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {source} | {status} | {options} | {targets} | {action} |".format(
                source=_cell(row.get("source_id", "")),
                status=_cell(row.get("decision_status", "")),
                options=_cell(row.get("candidate_decision_options", "")),
                targets=_cell(row.get("target_cache_artifacts", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is a reviewer worksheet, not a formal decision record.",
            "- It does not cache data, certify terms, or accept source provenance.",
            "- Keep release-scope claims blocked until retained sources are reviewed and formal provenance acceptance exists.",
            "",
        ]
    )
    return "\n".join(lines)


def _decision_row(
    row: Mapping[str, str],
    *,
    evidence_paths: str,
) -> dict[str, str]:
    target_present = str(row.get("target_cache_artifacts_present", "")).lower() == "true"
    decision_status = (
        "needs_human_review_cache_retention_or_exclusion_decision"
        if target_present
        else "blocked_missing_context_source_cache_retention_or_exclusion_decision"
    )
    blocking_reason = (
        ""
        if target_present
        else "no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present"
    )
    return {
        "source_id": str(row.get("source_id", "")),
        "source_name": str(row.get("source_name", "")),
        "source_type": str(row.get("source_type", "")),
        "decision_topic": "Context source cache, retention, or exclusion decision",
        "current_cache_request_status": str(row.get("cache_request_status", "")),
        "candidate_decision_options": _candidate_options(row),
        "provisional_decision": "pending_reviewer_decision",
        "decision_status": decision_status,
        "blocking_reason": blocking_reason,
        "target_cache_artifacts": str(row.get("target_cache_artifacts", "")),
        "target_cache_artifacts_present": str(
            row.get("target_cache_artifacts_present", "")
        ),
        "source_url_or_citation": str(row.get("source_url_or_citation", "")),
        "required_reviewer_action": (
            "Choose whether to cache reviewed source evidence, retain this "
            "source as sensitivity/context-only, or exclude it from release-scope claims."
        ),
        "required_evidence_fields": (
            "reviewer; decision_date; decision_basis; terms_or_license_summary; "
            "attribution_requirements; snapshot_or_exclusion_rationale; "
            "retained_raw_response_policy; sha256_or_digest_if_cached"
        ),
        "followup_artifacts": _followup_artifacts(row),
        "evidence_input_paths": _artifact_list(
            evidence_paths,
            row.get("context_local_artifacts", ""),
        ),
        "target_acceptance_artifact": str(
            row.get(
                "target_acceptance_artifact",
                "data/manifests/provenance_acceptance.json",
            )
        ),
        "can_support_final_provenance_gate": "false",
        "claim_boundary": SOURCE_CONTEXT_CACHE_DECISION_SCOPE,
    }


def _candidate_options(row: Mapping[str, str]) -> str:
    options = [
        "cache_reviewed_extract",
        "retain_as_sensitivity_or_context_only",
        "exclude_from_release_scope_claims",
    ]
    source_id = str(row.get("source_id", ""))
    if source_id == "metro9_capacity_context":
        options.append("retain_capacity_as_sensitivity_only")
    return "; ".join(options)


def _followup_artifacts(row: Mapping[str, str]) -> str:
    values = [
        str(row.get("target_cache_artifacts", "")),
        "data/manifests/provenance_acceptance.json",
    ]
    source_id = str(row.get("source_id", ""))
    if "timetable" in source_id:
        values.append("data/parameters/rail_service_evidence.csv")
    if "shortest_path" in source_id:
        values.append("data/parameters/rail_service_evidence.csv")
    if "gtfs" in source_id:
        values.append("data/parameters/rail_service_evidence.csv")
    return "; ".join(value for value in values if value)


def _evidence_paths(
    *,
    request_packet_path: str | Path,
    request_manifest_path: str | Path,
    source_priority_packet_path: str | Path,
    source_url_remediation_packet_path: str | Path,
    provenance_manifest_path: str | Path,
) -> str:
    paths = [
        request_packet_path,
        request_manifest_path,
        source_priority_packet_path,
        source_url_remediation_packet_path,
        provenance_manifest_path,
    ]
    return "; ".join(_display_path(path) for path in paths)


def _artifact_list(*values: object) -> str:
    artifacts: list[str] = []
    seen: set[str] = set()
    for value in values:
        for artifact in str(value).split(";"):
            clean = artifact.strip()
            if clean and clean not in seen:
                seen.add(clean)
                artifacts.append(clean)
    return "; ".join(artifacts)


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers = [
        "formal provenance acceptance record is absent",
        "target cache/retention/exclusion decisions are pending for context-source rows",
        "retained context sources still require license, attribution, snapshot, and reproducibility review",
    ]
    for row in rows:
        status = str(row.get("decision_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(f"{row.get('source_id', '')}: {reason}")
    return blockers


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


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
    "DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_DOC_PATH",
    "DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH",
    "DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH",
    "SOURCE_CONTEXT_CACHE_DECISION_COLUMNS",
    "SOURCE_CONTEXT_CACHE_DECISION_SCOPE",
    "build_source_context_cache_decision_manifest",
    "build_source_context_cache_decision_markdown",
    "build_source_context_cache_decision_rows",
    "write_source_context_cache_decision_packet",
]
