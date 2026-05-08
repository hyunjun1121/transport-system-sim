"""Parameter evidence priority packet.

This module joins the parameter review, source-request, and source-readiness
worksheets. The output ranks cross-cutting demand, fleet, transfer,
disruption, and traffic/BPR evidence work without changing parameter values or
creating weak-parameter acceptance.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.parameter_evidence_request_packet import (
    DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
)
from src.realworld.parameter_review_packet import DEFAULT_PARAMETER_REVIEW_PACKET_PATH
from src.realworld.parameter_source_readiness_packet import (
    DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "parameter_evidence_priority_packet.csv"
)
DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "parameter_evidence_priority_manifest.json"
)
DEFAULT_PARAMETER_EVIDENCE_PRIORITY_DOC_PATH = (
    PROJECT_ROOT / "docs" / "parameter_evidence_priority_packet.md"
)
PARAMETER_EVIDENCE_PRIORITY_SCOPE = (
    "Parameter evidence priority packet only; not source evidence, not "
    "accepted parameter calibration, not weak-parameter acceptance, not "
    "parameter evidence gate closure, and not publication-readiness approval."
)
PARAMETER_EVIDENCE_PRIORITY_COLUMNS: tuple[str, ...] = (
    "priority_id",
    "region_id",
    "parameter_groups",
    "covered_parameters",
    "weak_parameter_count",
    "high_priority_parameter_count",
    "medium_priority_parameter_count",
    "low_priority_parameter_count",
    "readiness_status",
    "priority_status",
    "review_priority",
    "blocking_reason",
    "source_type",
    "source_name",
    "source_cache_path",
    "source_cache_present",
    "raw_payload_path",
    "raw_payload_present",
    "target_output_path",
    "target_output_present",
    "current_evidence_summary",
    "current_values",
    "needed_source_requests",
    "candidate_artifacts",
    "required_reviewer_action",
    "acquisition_command",
    "review_or_derivation_command",
    "publication_use_status",
    "can_support_parameter_evidence_gate",
    "can_support_acceptance_gate",
    "claim_boundary",
)


def build_parameter_evidence_priority_rows(
    *,
    review_packet_path: str | Path = DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    source_request_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    source_readiness_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return parameter evidence priority rows for current source blockers."""

    review_rows = _read_csv_rows(review_packet_path)
    request_rows = _read_csv_rows(source_request_path)
    readiness_rows = _read_csv_rows(source_readiness_path)
    review_by_parameter = {
        row.get("parameter", ""): row
        for row in review_rows
        if str(row.get("parameter", "")).strip()
    }
    readiness_by_request = {
        row.get("request_id", ""): row
        for row in readiness_rows
        if str(row.get("request_id", "")).strip()
    }
    rows = [
        _priority_row(
            request,
            readiness_by_request.get(str(request.get("request_id", "")), {}),
            review_by_parameter=review_by_parameter,
        )
        for request in request_rows
    ]
    rows.sort(key=_priority_sort_key)
    return rows


def write_parameter_evidence_priority_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    source_request_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    source_readiness_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
) -> dict[str, Any]:
    """Write parameter evidence priority CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=PARAMETER_EVIDENCE_PRIORITY_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in PARAMETER_EVIDENCE_PRIORITY_COLUMNS
                }
            )

    summary = build_parameter_evidence_priority_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        review_packet_path=review_packet_path,
        source_request_path=source_request_path,
        source_readiness_path=source_readiness_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_parameter_evidence_priority_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_parameter_evidence_priority_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    source_request_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    source_readiness_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for parameter evidence priority rows."""

    status_counts = _counts(row.get("priority_status", "") for row in rows)
    readiness_counts = _counts(row.get("readiness_status", "") for row in rows)
    group_counts = _counts(row.get("parameter_groups", "") for row in rows)
    weak_parameter_count = sum(_int_value(row.get("weak_parameter_count", "0")) for row in rows)
    high_parameter_count = sum(
        _int_value(row.get("high_priority_parameter_count", "0")) for row in rows
    )
    medium_parameter_count = sum(
        _int_value(row.get("medium_priority_parameter_count", "0")) for row in rows
    )
    return {
        "schema_version": 1,
        "result_scope": PARAMETER_EVIDENCE_PRIORITY_SCOPE,
        "claim_boundary": (
            "This packet prioritizes existing parameter evidence gaps. It does "
            "not create accepted parameter values, does not certify source "
            "sufficiency, and does not close parameter, validation, provenance, "
            "or final-study gates."
        ),
        "row_count": len(rows),
        "region_ids": _region_ids(rows),
        "weak_parameter_count": weak_parameter_count,
        "high_priority_parameter_count": high_parameter_count,
        "medium_priority_parameter_count": medium_parameter_count,
        "priority_status_counts": status_counts,
        "readiness_status_counts": readiness_counts,
        "parameter_group_counts": group_counts,
        "blocking_priority_count": sum(
            1
            for row in rows
            if str(row.get("priority_status", "")).startswith("blocked_")
        ),
        "human_review_priority_count": sum(
            1
            for row in rows
            if str(row.get("priority_status", "")).startswith("needs_human_review_")
        ),
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "parameter_evidence_review_packet": _display_path(review_packet_path),
            "parameter_evidence_source_request_packet": _display_path(
                source_request_path
            ),
            "parameter_source_readiness_packet": _display_path(source_readiness_path),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "resolve blocked transfer evidence before transfer-delay final claims",
            "review high-priority disruption and traffic/BPR rows before final parameter acceptance",
            "review demand, fleet, and dispatch scenario assumptions as bounded planning inputs",
            "rerun parameter and final-study audits after source-backed parameter changes",
        ],
        "remaining_blockers": [
            "transfer-delay source evidence is absent",
            "high-priority disruption and traffic/BPR rows still require human/source-backed decisions",
            "medium-priority demand, fleet, and dispatch rows remain scenario assumptions",
            "parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions",
        ],
    }


def build_parameter_evidence_priority_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for parameter evidence priority review."""

    lines = [
        "# Parameter Evidence Priority Packet",
        "",
        str(manifest.get("claim_boundary", PARAMETER_EVIDENCE_PRIORITY_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Priority rows: {manifest.get('row_count', 0)}",
        f"- Weak parameters: {manifest.get('weak_parameter_count', 0)}",
        f"- Blocking priority rows: {manifest.get('blocking_priority_count', 0)}",
        f"- Human-review priority rows: {manifest.get('human_review_priority_count', 0)}",
        f"- Priority status counts: `{manifest.get('priority_status_counts', {})}`",
        "",
        "## Priority Rows",
        "",
        "| Request | Group | Status | High | Medium | Required Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {request} | {group} | {status} | {high} | {medium} | {action} |".format(
                request=_cell(row.get("priority_id", "")),
                group=_cell(row.get("parameter_groups", "")),
                status=_cell(row.get("priority_status", "")),
                high=_cell(row.get("high_priority_parameter_count", "")),
                medium=_cell(row.get("medium_priority_parameter_count", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is parameter-evidence prioritization support only.",
            "- It does not create source evidence, calibrated values, or weak-parameter acceptance.",
            "- It cannot create or replace `data/parameters/parameter_acceptance.csv`.",
            "",
        ]
    )
    return "\n".join(lines)


def _priority_row(
    request: Mapping[str, str],
    readiness: Mapping[str, str],
    *,
    review_by_parameter: Mapping[str, Mapping[str, str]],
) -> dict[str, str]:
    covered_parameters = _split_values(request.get("covered_parameters", ""))
    review_rows = [
        review_by_parameter[parameter]
        for parameter in covered_parameters
        if parameter in review_by_parameter
    ]
    high_count = _priority_count(review_rows, "high", weak_only=True)
    medium_count = _priority_count(review_rows, "medium", weak_only=True)
    low_count = _priority_count(review_rows, "low", weak_only=False)
    readiness_status = str(
        readiness.get("readiness_status", "")
        or "blocked_missing_parameter_source_readiness"
    )
    priority_status, review_priority = _classify_priority(
        readiness_status=readiness_status,
        high_count=high_count,
        medium_count=medium_count,
    )
    return {
        "priority_id": str(request.get("request_id", "")),
        "region_id": str(request.get("region_id", "")),
        "parameter_groups": str(request.get("parameter_groups", "")),
        "covered_parameters": str(request.get("covered_parameters", "")),
        "weak_parameter_count": str(
            readiness.get("weak_parameter_count", "")
            or request.get("weak_parameter_count", "")
        ),
        "high_priority_parameter_count": str(high_count),
        "medium_priority_parameter_count": str(medium_count),
        "low_priority_parameter_count": str(low_count),
        "readiness_status": readiness_status,
        "priority_status": priority_status,
        "review_priority": review_priority,
        "blocking_reason": str(readiness.get("blocking_reason", "")),
        "source_type": str(request.get("source_type", "")),
        "source_name": str(request.get("source_name", "")),
        "source_cache_path": str(readiness.get("source_cache_path", "")),
        "source_cache_present": str(readiness.get("source_cache_present", "")).lower(),
        "raw_payload_path": str(readiness.get("raw_payload_path", "")),
        "raw_payload_present": str(readiness.get("raw_payload_present", "")).lower(),
        "target_output_path": str(readiness.get("target_output_path", "")),
        "target_output_present": str(readiness.get("target_output_present", "")).lower(),
        "current_evidence_summary": str(request.get("current_evidence_summary", "")),
        "current_values": str(request.get("current_values", "")),
        "needed_source_requests": str(request.get("request_id", "")),
        "candidate_artifacts": str(request.get("source_url_or_citation", "")),
        "required_reviewer_action": str(
            readiness.get("required_reviewer_action", "")
            or request.get("required_external_input", "")
        ),
        "acquisition_command": str(request.get("acquisition_command", "")),
        "review_or_derivation_command": str(
            request.get("review_or_derivation_command", "")
        ),
        "publication_use_status": str(request.get("publication_use_status", "")),
        "can_support_parameter_evidence_gate": "false",
        "can_support_acceptance_gate": "false",
        "claim_boundary": PARAMETER_EVIDENCE_PRIORITY_SCOPE,
    }


def _classify_priority(
    *,
    readiness_status: str,
    high_count: int,
    medium_count: int,
) -> tuple[str, str]:
    if readiness_status.startswith("blocked_"):
        return "blocked_missing_parameter_source", "high"
    if high_count > 0:
        return "needs_human_review_high_priority_parameter_source", "high"
    if medium_count > 0:
        return "needs_human_review_medium_priority_parameter_source", "medium"
    return "needs_human_review_low_priority_parameter_source", "low"


def _priority_sort_key(row: Mapping[str, str]) -> tuple[int, int, int, str]:
    status = str(row.get("priority_status", ""))
    if status.startswith("blocked_"):
        order = 0
    elif "high_priority" in status:
        order = 1
    elif "medium_priority" in status:
        order = 2
    else:
        order = 3
    return (
        order,
        -_int_value(row.get("high_priority_parameter_count", "0")),
        -_int_value(row.get("weak_parameter_count", "0")),
        str(row.get("priority_id", "")),
    )


def _priority_count(
    rows: Sequence[Mapping[str, str]],
    priority: str,
    *,
    weak_only: bool,
) -> int:
    count = 0
    for row in rows:
        if str(row.get("review_priority", "")) != priority:
            continue
        if weak_only and str(row.get("weak_for_final_claim", "")).lower() != "true":
            continue
        count += 1
    return count


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    filepath = Path(path)
    with filepath.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _split_values(value: Any) -> list[str]:
    return [item.strip() for item in str(value).split(";") if item.strip()]


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] += 1
    return dict(sorted(counts.items()))


def _region_ids(rows: Sequence[Mapping[str, str]]) -> list[str]:
    return sorted(
        {
            str(row.get("region_id", "")).strip()
            for row in rows
            if str(row.get("region_id", "")).strip()
        }
    )


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
    "DEFAULT_PARAMETER_EVIDENCE_PRIORITY_DOC_PATH",
    "DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH",
    "DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH",
    "PARAMETER_EVIDENCE_PRIORITY_COLUMNS",
    "PARAMETER_EVIDENCE_PRIORITY_SCOPE",
    "build_parameter_evidence_priority_manifest",
    "build_parameter_evidence_priority_markdown",
    "build_parameter_evidence_priority_rows",
    "write_parameter_evidence_priority_packet",
]
