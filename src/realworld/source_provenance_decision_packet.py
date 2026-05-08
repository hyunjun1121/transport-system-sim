"""Focused source-provenance decision worksheet.

The source/license, URL, priority, and context-cache packets expose detailed
review work. This module turns their current state into provenance-gate
decision rows without creating ``data/manifests/provenance_acceptance.json`` or
certifying source/license sufficiency.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.provenance_acceptance import DEFAULT_PROVENANCE_ACCEPTANCE_PATH
from src.realworld.reproducibility_review_packet import (
    DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
)
from src.realworld.source_context_cache_decision_packet import (
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH,
)
from src.realworld.source_context_cache_request_packet import (
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
)
from src.realworld.source_license_review_packet import (
    DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
)
from src.realworld.source_provenance import DEFAULT_SOURCE_PROVENANCE_PATH
from src.realworld.source_provenance_priority_packet import (
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
)
from src.realworld.source_url_remediation_packet import (
    DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
)
from src.realworld.source_url_review_packet import (
    DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_provenance_decision_packet.csv"
)
DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_provenance_decision_manifest.json"
)
DEFAULT_SOURCE_PROVENANCE_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "source_provenance_decision_packet.md"
)
SOURCE_PROVENANCE_DECISION_SCOPE = (
    "Source-provenance decision packet only; not source acceptance, not license "
    "certification, not cached source evidence, not provenance gate closure, "
    "not calibrated real-world validation, and not operational routing approval."
)
SOURCE_PROVENANCE_DECISION_COLUMNS: tuple[str, ...] = (
    "decision_id",
    "decision_topic",
    "candidate_decision",
    "current_evidence",
    "decision_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_provenance_acceptance",
    "claim_boundary",
)


def build_source_provenance_decision_rows(
    *,
    source_provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
    source_license_manifest_path: str
    | Path = DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    source_url_manifest_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    source_url_remediation_manifest_path: str
    | Path = DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    source_priority_manifest_path: str
    | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    source_context_request_manifest_path: str
    | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    source_context_decision_manifest_path: str
    | Path = DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    reproducibility_manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
    provenance_acceptance_path: str | Path = DEFAULT_PROVENANCE_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return reviewer rows for final source-provenance decisions."""

    source_manifest = _read_json_object(source_provenance_manifest_path)
    license_manifest = _read_json_object(source_license_manifest_path)
    url_manifest = _read_json_object(source_url_manifest_path)
    remediation_manifest = _read_json_object(source_url_remediation_manifest_path)
    priority_manifest = _read_json_object(source_priority_manifest_path)
    context_request_manifest = _read_json_object(source_context_request_manifest_path)
    context_decision_manifest = _read_json_object(source_context_decision_manifest_path)
    reproducibility_manifest = _read_json_object(reproducibility_manifest_path)
    acceptance_path = Path(provenance_acceptance_path)
    evidence_paths = _evidence_paths(
        source_provenance_manifest_path=source_provenance_manifest_path,
        source_license_manifest_path=source_license_manifest_path,
        source_url_manifest_path=source_url_manifest_path,
        source_url_remediation_manifest_path=source_url_remediation_manifest_path,
        source_priority_manifest_path=source_priority_manifest_path,
        source_context_request_manifest_path=source_context_request_manifest_path,
        source_context_decision_manifest_path=source_context_decision_manifest_path,
        reproducibility_manifest_path=reproducibility_manifest_path,
    )
    context_blocking_count = _int(context_decision_manifest.get("blocking_decision_count"))
    reproducibility_scope = str(reproducibility_manifest.get("scope", "")).strip()
    reproducibility_scope_blocked = "scaffold" in reproducibility_scope.lower()

    return [
        _row(
            decision_id="source_inventory_review_decision",
            decision_topic="Source inventory review",
            candidate_decision=(
                "Retain the current 11-row source manifest only after reviewer "
                "confirms source identity, scope, and local artifacts"
            ),
            current_evidence=_source_inventory_evidence(source_manifest),
            decision_status="needs_human_review_source_inventory",
            blocking_reason="",
            required_reviewer_action=(
                "Confirm the retained source inventory and any excluded sources "
                "before provenance acceptance."
            ),
            followup_artifacts="data/manifests/provenance_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="license_attribution_decision",
            decision_topic="License and attribution review",
            candidate_decision=(
                "Accept source license, attribution, derivative-use, snapshot, "
                "and privacy abstraction treatment only after row-level review"
            ),
            current_evidence=_license_evidence(license_manifest),
            decision_status="needs_human_review_license_attribution",
            blocking_reason="",
            required_reviewer_action=(
                "Review every source/license row and record accepted license "
                "scope in provenance_acceptance.json."
            ),
            followup_artifacts=(
                "data/manifests/source_license_review_packet.csv; "
                "data/manifests/provenance_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="context_source_cache_or_exclusion_decision",
            decision_topic="Context source cache or exclusion",
            candidate_decision=(
                "Cache retained context-source target artifacts or explicitly "
                "exclude the source from final claims"
            ),
            current_evidence=_context_evidence(
                context_request_manifest,
                context_decision_manifest,
            ),
            decision_status=(
                "blocked_missing_context_cache_or_exclusion_decisions"
                if context_blocking_count
                else "needs_human_review_context_cache_decisions"
            ),
            blocking_reason=(
                "context-source target cache artifacts still lack reviewed source payloads or explicit exclusion decisions"
                if context_blocking_count
                else ""
            ),
            required_reviewer_action=(
                "Resolve cache, exclusion, or sensitivity-only treatment for "
                "each context source before final provenance claims."
            ),
            followup_artifacts=(
                "data/manifests/source_context_cache_decision_packet.csv; "
                "data/manifests/provenance_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="url_remediation_decision",
            decision_topic="URL remediation review",
            candidate_decision=(
                "Retain reachable URLs, local citations, and alternate URL "
                "replacements only after reviewer confirmation"
            ),
            current_evidence=_url_evidence(url_manifest, remediation_manifest),
            decision_status="needs_human_review_url_remediation",
            blocking_reason="",
            required_reviewer_action=(
                "Confirm URL identity, local-citation rows, and alternate URL "
                "candidates before provenance acceptance."
            ),
            followup_artifacts=(
                "data/manifests/source_url_remediation_packet.csv; "
                "data/manifests/provenance_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="cached_snapshot_repository_scope_decision",
            decision_topic="Cached snapshot and repository-input scope",
            candidate_decision=(
                "Accept cached public snapshots and repository-owned inputs only "
                "inside a not-operational, non-calibrated claim boundary"
            ),
            current_evidence=_priority_evidence(priority_manifest),
            decision_status=(
                "needs_human_review_cached_snapshot_and_repository_scope"
            ),
            blocking_reason="",
            required_reviewer_action=(
                "Review cached snapshots, repository-owned inputs, and privacy "
                "abstraction before retaining them for final claims."
            ),
            followup_artifacts=(
                "data/manifests/source_provenance_priority_packet.csv; "
                "data/manifests/provenance_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="reproducibility_source_scope_decision",
            decision_topic="Source reproducibility scope",
            candidate_decision=(
                "Replace the scaffold-only reproduction scope with reviewed "
                "source snapshot and cache reproduction evidence"
            ),
            current_evidence=(
                f"reproducibility_scope={_clean(reproducibility_scope)}; "
                f"scope_contains_scaffold={str(reproducibility_scope_blocked).lower()}"
            ),
            decision_status=(
                "blocked_scaffold_reproducibility_manifest_scope"
                if reproducibility_scope_blocked
                else "needs_human_review_reproducibility_source_scope"
            ),
            blocking_reason=(
                "reproducibility manifest remains scaffold-only"
                if reproducibility_scope_blocked
                else ""
            ),
            required_reviewer_action=(
                "Confirm retained source snapshots and cache reproduction "
                "evidence before provenance acceptance."
            ),
            followup_artifacts=(
                "data/manifests/reproducibility_manifest.json; "
                "data/manifests/provenance_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="formal_provenance_acceptance_boundary",
            decision_topic="Formal provenance acceptance",
            candidate_decision=(
                "Record accepted sources, reviewer, date, license scope, "
                "cache/exclusion decisions, evidence paths, and claim boundary "
                "only in the formal provenance acceptance path"
            ),
            current_evidence=(
                f"acceptance_path={_display_path(acceptance_path)}; "
                f"acceptance_present={str(acceptance_path.exists()).lower()}"
            ),
            decision_status=(
                "needs_human_review_existing_provenance_acceptance"
                if acceptance_path.exists()
                else "blocked_missing_provenance_acceptance_record"
            ),
            blocking_reason=(
                ""
                if acceptance_path.exists()
                else "data/manifests/provenance_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Create or validate provenance_acceptance.json only after "
                "source-backed human review; do not copy this packet into the "
                "formal path."
            ),
            followup_artifacts="data/manifests/provenance_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_source_provenance_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_PROVENANCE_DECISION_DOC_PATH,
    source_provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
    source_license_manifest_path: str
    | Path = DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    source_url_manifest_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    source_url_remediation_manifest_path: str
    | Path = DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    source_priority_manifest_path: str
    | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    source_context_request_manifest_path: str
    | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    source_context_decision_manifest_path: str
    | Path = DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    reproducibility_manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write source-provenance decision CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=SOURCE_PROVENANCE_DECISION_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in SOURCE_PROVENANCE_DECISION_COLUMNS
                }
            )

    summary = build_source_provenance_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        source_provenance_manifest_path=source_provenance_manifest_path,
        source_license_manifest_path=source_license_manifest_path,
        source_url_manifest_path=source_url_manifest_path,
        source_url_remediation_manifest_path=source_url_remediation_manifest_path,
        source_priority_manifest_path=source_priority_manifest_path,
        source_context_request_manifest_path=source_context_request_manifest_path,
        source_context_decision_manifest_path=source_context_decision_manifest_path,
        reproducibility_manifest_path=reproducibility_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_source_provenance_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_source_provenance_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_PROVENANCE_DECISION_DOC_PATH,
    source_provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
    source_license_manifest_path: str
    | Path = DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    source_url_manifest_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    source_url_remediation_manifest_path: str
    | Path = DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    source_priority_manifest_path: str
    | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    source_context_request_manifest_path: str
    | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    source_context_decision_manifest_path: str
    | Path = DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    reproducibility_manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for provenance decision rows."""

    status_counts = _counts(row.get("decision_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("decision_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("decision_status", "")).startswith("needs_human_review_")
    )
    return {
        "schema_version": 1,
        "result_scope": SOURCE_PROVENANCE_DECISION_SCOPE,
        "claim_boundary": (
            SOURCE_PROVENANCE_DECISION_SCOPE
            + " It cannot create data/manifests/provenance_acceptance.json."
        ),
        "row_count": len(rows),
        "decision_ids": [str(row.get("decision_id", "")) for row in rows],
        "decision_status_counts": status_counts,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "provenance_decision_recorded": False,
        "source_inventory_decision_recorded": False,
        "license_attribution_decision_recorded": False,
        "context_cache_or_exclusion_decision_recorded": False,
        "provenance_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "source_provenance_manifest": _display_path(
                source_provenance_manifest_path
            ),
            "source_license_review_manifest": _display_path(
                source_license_manifest_path
            ),
            "source_url_review_manifest": _display_path(source_url_manifest_path),
            "source_url_remediation_manifest": _display_path(
                source_url_remediation_manifest_path
            ),
            "source_provenance_priority_manifest": _display_path(
                source_priority_manifest_path
            ),
            "source_context_cache_request_manifest": _display_path(
                source_context_request_manifest_path
            ),
            "source_context_cache_decision_manifest": _display_path(
                source_context_decision_manifest_path
            ),
            "reproducibility_manifest": _display_path(reproducibility_manifest_path),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "confirm retained source inventory and excluded-source scope",
            "review license, attribution, derivative-use, snapshot, privacy, and reproducibility obligations",
            "resolve context-source target cache, exclusion, or sensitivity-only decisions",
            "confirm reachable URLs, local citations, and alternate URL candidates",
            "record final provenance only in data/manifests/provenance_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_source_provenance_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown provenance decision worksheet."""

    lines = [
        "# Source Provenance Decision Packet",
        "",
        str(manifest.get("claim_boundary", SOURCE_PROVENANCE_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Provenance decision recorded: `{str(manifest.get('provenance_decision_recorded', False)).lower()}`",
        f"- Decision rows: {manifest.get('row_count', 0)}",
        f"- Blocking decisions: {manifest.get('blocking_decision_count', 0)}",
        f"- Human-review decisions: {manifest.get('human_review_decision_count', 0)}",
        f"- Status counts: `{manifest.get('decision_status_counts', {})}`",
        "",
        "## Decision Rows",
        "",
        "| Decision | Status | Candidate | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {decision} | {status} | {candidate} | {action} |".format(
                decision=_cell(row.get("decision_id", "")),
                status=_cell(row.get("decision_status", "")),
                candidate=_cell(row.get("candidate_decision", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is a reviewer worksheet, not a provenance acceptance record.",
            "- It does not certify licenses, accept source snapshots, cache context sources, or close the provenance gate.",
            "- Keep provenance claims blocked until `data/manifests/provenance_acceptance.json` is reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(
    *,
    decision_id: str,
    decision_topic: str,
    candidate_decision: str,
    current_evidence: str,
    decision_status: str,
    blocking_reason: str,
    required_reviewer_action: str,
    followup_artifacts: str,
    evidence_input_paths: str,
) -> dict[str, str]:
    return {
        "decision_id": decision_id,
        "decision_topic": decision_topic,
        "candidate_decision": candidate_decision,
        "current_evidence": current_evidence,
        "decision_status": decision_status,
        "blocking_reason": blocking_reason,
        "required_reviewer_action": required_reviewer_action,
        "followup_artifacts": followup_artifacts,
        "evidence_input_paths": evidence_input_paths,
        "can_support_provenance_acceptance": "false",
        "claim_boundary": SOURCE_PROVENANCE_DECISION_SCOPE,
    }


def _source_inventory_evidence(manifest: Mapping[str, Any]) -> str:
    records = manifest.get("records", [])
    record_count = len(records) if isinstance(records, Sequence) else 0
    review_status_counts = _counts(
        record.get("review_status", "")
        for record in records
        if isinstance(record, Mapping)
    )
    return (
        f"region_id={_clean(manifest.get('region_id'))}; "
        f"source_record_count={record_count}; "
        f"review_status_counts={review_status_counts}"
    )


def _license_evidence(manifest: Mapping[str, Any]) -> str:
    return (
        f"row_count={_int(manifest.get('row_count'))}; "
        f"review_required_count={_int(manifest.get('review_required_count'))}; "
        f"missing_snapshot_or_context_only_count={_int(manifest.get('missing_snapshot_or_context_only_count'))}; "
        f"publication_ready={str(manifest.get('publication_ready', False)).lower()}"
    )


def _context_evidence(
    request_manifest: Mapping[str, Any],
    decision_manifest: Mapping[str, Any],
) -> str:
    return (
        f"context_source_count={_int(request_manifest.get('context_source_count'))}; "
        f"missing_target_cache_artifact_count={_int(decision_manifest.get('missing_target_cache_artifact_count'))}; "
        f"blocking_decision_count={_int(decision_manifest.get('blocking_decision_count'))}; "
        f"cache_or_exclusion_decision_recorded={str(decision_manifest.get('cache_or_exclusion_decision_recorded', False)).lower()}"
    )


def _url_evidence(
    url_manifest: Mapping[str, Any],
    remediation_manifest: Mapping[str, Any],
) -> str:
    return (
        f"url_row_count={_int(url_manifest.get('row_count'))}; "
        f"unreachable_or_error_count={_int(url_manifest.get('unreachable_or_error_count'))}; "
        f"remediation_row_count={_int(remediation_manifest.get('row_count'))}; "
        f"alternate_candidate_row_count={_int(remediation_manifest.get('alternate_candidate_row_count'))}; "
        f"remediation_status_counts={remediation_manifest.get('remediation_status_counts', {})}"
    )


def _priority_evidence(manifest: Mapping[str, Any]) -> str:
    return (
        f"source_rows={_int(manifest.get('row_count'))}; "
        f"cached_snapshot_source_count={_int(manifest.get('cached_snapshot_source_count'))}; "
        f"repository_input_source_count={_int(manifest.get('repository_input_source_count'))}; "
        f"context_only_source_count={_int(manifest.get('context_only_source_count'))}; "
        f"human_review_source_count={_int(manifest.get('human_review_source_count'))}"
    )


def _evidence_paths(
    *,
    source_provenance_manifest_path: str | Path,
    source_license_manifest_path: str | Path,
    source_url_manifest_path: str | Path,
    source_url_remediation_manifest_path: str | Path,
    source_priority_manifest_path: str | Path,
    source_context_request_manifest_path: str | Path,
    source_context_decision_manifest_path: str | Path,
    reproducibility_manifest_path: str | Path,
) -> str:
    paths = [
        source_provenance_manifest_path,
        DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
        source_license_manifest_path,
        DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
        source_url_manifest_path,
        DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
        source_url_remediation_manifest_path,
        DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
        source_priority_manifest_path,
        DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
        source_context_request_manifest_path,
        DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH,
        source_context_decision_manifest_path,
        reproducibility_manifest_path,
    ]
    return "; ".join(_display_path(path) for path in paths)


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("decision_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(reason)
    return blockers


def _read_json_object(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        return {}
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _int(value: object) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _display_path(path: str | Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return candidate.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_SOURCE_PROVENANCE_DECISION_DOC_PATH",
    "DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH",
    "DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH",
    "SOURCE_PROVENANCE_DECISION_COLUMNS",
    "SOURCE_PROVENANCE_DECISION_SCOPE",
    "build_source_provenance_decision_manifest",
    "build_source_provenance_decision_markdown",
    "build_source_provenance_decision_rows",
    "write_source_provenance_decision_packet",
]
