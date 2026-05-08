"""Source URL remediation packet generation.

This module converts source-URL review rows into a concrete remediation queue.
It is a reviewer aid only: unreachable URLs, missing public links, and reachable
pages still require source-backed review before provenance acceptance.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.source_url_review_packet import (
    DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
    SOURCE_URL_REVIEW_SCOPE,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_url_remediation_packet.csv"
)
DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_url_remediation_manifest.json"
)
DEFAULT_SOURCE_URL_REMEDIATION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "source_url_remediation_packet.md"
)
SOURCE_URL_REMEDIATION_SCOPE = (
    "Source URL remediation packet only; not source acceptance, not license "
    "certification, not calibrated real-world validation, and not operational "
    "routing approval."
)
SOURCE_URL_REMEDIATION_COLUMNS: tuple[str, ...] = (
    "source_id",
    "source_name",
    "source_type",
    "url",
    "alternate_url_candidates",
    "url_status",
    "http_status",
    "remediation_status",
    "priority",
    "evidence_gap",
    "required_reviewer_action",
    "target_acceptance_artifact",
    "source_review_packet",
    "can_support_final_provenance_gate",
    "claim_boundary",
    "notes",
)


def build_source_url_remediation_rows(
    *,
    url_rows: Sequence[Mapping[str, str]] | None = None,
    url_review_packet_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return remediation rows from URL review rows or a review-packet CSV."""

    rows = (
        list(url_rows)
        if url_rows is not None
        else _load_url_rows(url_review_packet_path)
    )
    reachable_urls_by_source_id = _reachable_urls_by_source_id(rows)
    return [
        _remediation_row(
            row,
            reachable_urls_by_source_id=reachable_urls_by_source_id,
        )
        for row in rows
    ]


def write_source_url_remediation_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_URL_REMEDIATION_DOC_PATH,
    url_review_packet_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown source-URL remediation artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SOURCE_URL_REMEDIATION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in SOURCE_URL_REMEDIATION_COLUMNS
                }
            )

    summary = build_source_url_remediation_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        url_review_packet_path=url_review_packet_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_source_url_remediation_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_source_url_remediation_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_URL_REMEDIATION_DOC_PATH,
    url_review_packet_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for source-URL remediation rows."""

    remediation_counts = _counts(row.get("remediation_status", "") for row in rows)
    priority_counts = _counts(row.get("priority", "") for row in rows)
    blocking_issue_count = sum(
        1
        for row in rows
        if row.get("remediation_status", "").startswith("blocked_")
    )
    live_check_required_count = sum(
        1
        for row in rows
        if row.get("remediation_status") == "live_check_required"
    )
    alternate_candidate_row_count = sum(
        1 for row in rows if str(row.get("alternate_url_candidates", "")).strip()
    )
    closure_candidate_count = sum(
        1
        for row in rows
        if _is_true(row.get("can_support_final_provenance_gate", "false"))
    )
    remaining_blockers = _remaining_blockers(
        blocking_issue_count=blocking_issue_count,
        live_check_required_count=live_check_required_count,
        remediation_counts=remediation_counts,
    )
    review_items = _review_items(remediation_counts)
    return {
        "schema_version": 1,
        "claim_boundary": (
            SOURCE_URL_REMEDIATION_SCOPE
            + " Remediation rows identify review work only and cannot close "
            "data/manifests/provenance_acceptance.json."
        ),
        "result_scope": SOURCE_URL_REMEDIATION_SCOPE,
        "row_count": len(rows),
        "remediation_status_counts": remediation_counts,
        "priority_counts": priority_counts,
        "blocking_issue_count": blocking_issue_count,
        "live_check_required_count": live_check_required_count,
        "alternate_candidate_row_count": alternate_candidate_row_count,
        "provenance_gate_closure_candidate_count": closure_candidate_count,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "source_url_review_packet": _display_path(Path(url_review_packet_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": review_items,
        "remaining_blockers": remaining_blockers,
    }


def build_source_url_remediation_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable source-URL remediation queue."""

    lines = [
        "# Source URL Remediation Packet",
        "",
        str(manifest.get("claim_boundary", SOURCE_URL_REMEDIATION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Remediation rows: {manifest.get('row_count', 0)}",
        f"- Blocking issues: {manifest.get('blocking_issue_count', 0)}",
        f"- Live checks still required: {manifest.get('live_check_required_count', 0)}",
        f"- Status counts: `{manifest.get('remediation_status_counts', {})}`",
        "",
        "## Remediation Rows",
        "",
        "| Source | URL Status | Remediation | Alternate Candidates | Priority | Required Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {source} | {url_status} | {remediation} | {candidates} | {priority} | {action} |".format(
                source=_cell(row.get("source_id", "")),
                url_status=_cell(row.get("url_status", "")),
                remediation=_cell(row.get("remediation_status", "")),
                candidates=_cell(row.get("alternate_url_candidates", "")),
                priority=_cell(row.get("priority", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Replace stale or unreachable public URLs with verified official sources, or exclude them from final claims.",
            "- Confirm that local repository citations are acceptable for project-owned inputs.",
            "- Treat `reachable` as connectivity evidence only; license and source suitability still need review.",
            "- Create `data/manifests/provenance_acceptance.json` only after source-backed review.",
            "",
        ]
    )
    return "\n".join(lines)


def _remediation_row(
    row: Mapping[str, str],
    *,
    reachable_urls_by_source_id: Mapping[str, tuple[str, ...]],
) -> dict[str, str]:
    source_id = str(row.get("source_id", ""))
    source_type = str(row.get("source_type", ""))
    url_status = str(row.get("url_status", ""))
    alternate_url_candidates = _alternate_url_candidates(
        row,
        reachable_urls_by_source_id=reachable_urls_by_source_id,
    )
    remediation_status, priority, evidence_gap, action = _classify(
        source_has_reachable_url=bool(alternate_url_candidates),
        source_type=source_type,
        url_status=url_status,
    )
    return {
        "source_id": source_id,
        "source_name": str(row.get("source_name", "")),
        "source_type": source_type,
        "url": str(row.get("url", "")),
        "alternate_url_candidates": "; ".join(alternate_url_candidates),
        "url_status": url_status,
        "http_status": str(row.get("http_status", "")),
        "remediation_status": remediation_status,
        "priority": priority,
        "evidence_gap": evidence_gap,
        "required_reviewer_action": action,
        "target_acceptance_artifact": "data/manifests/provenance_acceptance.json",
        "source_review_packet": "data/manifests/source_url_review_packet.csv",
        "can_support_final_provenance_gate": "false",
        "claim_boundary": SOURCE_URL_REMEDIATION_SCOPE,
        "notes": _row_notes(row, remediation_status),
    }


def _classify(
    *,
    source_has_reachable_url: bool,
    source_type: str,
    url_status: str,
) -> tuple[str, str, str, str]:
    if url_status == "reachable":
        return (
            "reachable_needs_license_review",
            "medium",
            "connectivity is observed but official source identity, license, attribution, and snapshot suitability are unreviewed",
            "verify source identity, terms, attribution, and retained-snapshot policy before acceptance",
        )
    if url_status == "not_checked":
        return (
            "live_check_required",
            "high",
            "URL has not been checked for current reachability",
            "run the live source-URL check and then manually verify or replace the source",
        )
    if url_status == "no_url_detected" and source_type == "repository_input":
        return (
            "local_citation_needs_review",
            "medium",
            "project-owned local citation has no public HTTP URL",
            "confirm the local citation is sufficient for project-owned input and privacy scope",
        )
    if url_status == "no_url_detected":
        return (
            "blocked_missing_url_or_citation",
            "high",
            "non-repository source lacks a public URL or explicit citation",
            "add a verified official URL, source citation, cached extract, or exclusion decision",
        )
    if url_status in {"http_error", "network_error"}:
        if source_has_reachable_url:
            return (
                "alternate_reachable_url_needs_review",
                "medium",
                "one cited URL failed, but the same source has at least one reachable URL row",
                "verify whether the reachable URL is sufficient, then replace or remove the failed alternate citation before acceptance",
            )
        return (
            "blocked_unreachable_or_http_error",
            "high",
            "live check could not reach the cited public URL",
            "manually verify the URL, replace stale links, cache retained extracts, or exclude the source from final claims",
        )
    return (
        "blocked_unclassified_url_status",
        "high",
        f"unrecognized URL status: {url_status}",
        "inspect the URL-review row and classify the evidence gap before acceptance",
    )


def _row_notes(row: Mapping[str, str], remediation_status: str) -> str:
    base = str(row.get("notes", "")).strip()
    if base:
        return f"{remediation_status}: {base}"
    return remediation_status


def _load_url_rows(path: str | Path) -> list[dict[str, str]]:
    packet = Path(path)
    if not packet.exists():
        return []
    with packet.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _reachable_urls_by_source_id(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, tuple[str, ...]]:
    values: dict[str, list[str]] = {}
    for row in rows:
        if row.get("url_status") != "reachable":
            continue
        source_id = str(row.get("source_id", "")).strip()
        url = str(row.get("url", "")).strip()
        if not source_id or not url:
            continue
        bucket = values.setdefault(source_id, [])
        if url not in bucket:
            bucket.append(url)
    return {key: tuple(urls) for key, urls in values.items()}


def _alternate_url_candidates(
    row: Mapping[str, str],
    *,
    reachable_urls_by_source_id: Mapping[str, tuple[str, ...]],
) -> tuple[str, ...]:
    url_status = str(row.get("url_status", ""))
    if url_status not in {"http_error", "network_error", "not_checked"}:
        return ()
    source_id = str(row.get("source_id", "")).strip()
    current_url = str(row.get("url", "")).strip()
    return tuple(
        url
        for url in reachable_urls_by_source_id.get(source_id, ())
        if url and url != current_url
    )


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _review_items(remediation_counts: Mapping[str, int]) -> list[str]:
    items: list[str] = []
    if any(key.startswith("blocked_") for key in remediation_counts):
        items.append("manually open or replace blocked public URLs")
    if remediation_counts.get("live_check_required", 0):
        items.append("run the live source-URL check before provenance review")
    if remediation_counts.get("local_citation_needs_review", 0):
        items.append("confirm project-owned local citations where no public URL is expected")
    if remediation_counts.get("reachable_needs_license_review", 0) or remediation_counts.get(
        "alternate_reachable_url_needs_review",
        0,
    ):
        items.append(
            "verify license, attribution, derivative-use, source identity, and snapshot records before provenance acceptance"
        )
    if remediation_counts.get("alternate_reachable_url_needs_review", 0):
        items.append(
            "review alternate URL candidates before replacing or removing failed citations"
        )
    items.extend(
        [
            "provide reviewed target payloads for retained context-source rows or exclude them from final claims",
            "create data/manifests/provenance_acceptance.json only after source-backed review",
        ]
    )
    return items


def _remaining_blockers(
    *,
    blocking_issue_count: int,
    live_check_required_count: int,
    remediation_counts: Mapping[str, int],
) -> list[str]:
    blockers = [
        "formal provenance acceptance record is absent",
        "remediation rows do not certify official source identity or license compatibility",
    ]
    if blocking_issue_count:
        blockers.append("blocked URL rows require verified replacement, caching, or exclusion decisions")
    if live_check_required_count:
        blockers.append("unchecked URL rows require a live check or explicit offline-review decision")
    if remediation_counts.get("local_citation_needs_review", 0):
        blockers.append("local-citation rows require reviewer confirmation")
    if remediation_counts.get("reachable_needs_license_review", 0) or remediation_counts.get(
        "alternate_reachable_url_needs_review",
        0,
    ):
        blockers.append("reachable URL rows still require source/license/snapshot review")
    return blockers


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
    "DEFAULT_SOURCE_URL_REMEDIATION_DOC_PATH",
    "DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH",
    "DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH",
    "SOURCE_URL_REMEDIATION_COLUMNS",
    "SOURCE_URL_REMEDIATION_SCOPE",
    "build_source_url_remediation_manifest",
    "build_source_url_remediation_markdown",
    "build_source_url_remediation_rows",
    "write_source_url_remediation_packet",
]
