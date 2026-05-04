"""Rail timing fetch-readiness packet generation.

The rail timing source-request worksheet names candidate data sources and
commands. This module adds a deterministic preflight layer that separates
requests that are blocked by missing API keys or reviewed files from requests
that are ready for human review. It does not fetch live data and does not
create rail-service evidence.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.rail_timing_request_packet import (
    DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    RAIL_TIMING_SOURCE_REQUEST_SCOPE,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_fetch_readiness_packet.csv"
)
DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_fetch_readiness_manifest.json"
)
DEFAULT_RAIL_FETCH_READINESS_DOC_PATH = (
    PROJECT_ROOT / "docs" / "rail_fetch_readiness_packet.md"
)
RAIL_FETCH_READINESS_SCOPE = (
    "Rail fetch-readiness packet only; not rail timing evidence, not GTFS "
    "validation, not rail-service calibration, and not operational rail "
    "availability evidence."
)
RAIL_FETCH_READINESS_COLUMNS: tuple[str, ...] = (
    "request_id",
    "region_id",
    "evidence_fields",
    "source_type",
    "source_name",
    "readiness_status",
    "blocking_reason",
    "source_cache_path",
    "source_cache_present",
    "raw_payload_path",
    "raw_payload_present",
    "data_go_kr_key_present",
    "required_reviewer_action",
    "fetch_command",
    "derive_command",
    "target_evidence_artifact",
    "can_support_rail_evidence_gate",
    "claim_boundary",
    "notes",
)


def build_rail_fetch_readiness_rows(
    *,
    request_rows: Sequence[Mapping[str, str]] | None = None,
    request_packet_path: str | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    env: Mapping[str, str] | None = None,
) -> list[dict[str, str]]:
    """Return fetch-readiness rows for rail timing source requests."""

    rows = (
        list(request_rows)
        if request_rows is not None
        else _load_request_rows(request_packet_path)
    )
    environment = os.environ if env is None else env
    key_present = bool(str(environment.get("DATA_GO_KR_KEY", "")).strip())
    return [_readiness_row(row, data_go_kr_key_present=key_present) for row in rows]


def write_rail_fetch_readiness_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_DOC_PATH,
    request_packet_path: str | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
) -> dict[str, Any]:
    """Write rail fetch-readiness CSV, manifest, and Markdown artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAIL_FETCH_READINESS_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {column: str(row.get(column, "")) for column in RAIL_FETCH_READINESS_COLUMNS}
            )

    summary = build_rail_fetch_readiness_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        request_packet_path=request_packet_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_rail_fetch_readiness_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_rail_fetch_readiness_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_DOC_PATH,
    request_packet_path: str | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for rail fetch-readiness rows."""

    status_counts = _counts(row.get("readiness_status", "") for row in rows)
    source_type_counts = _counts(row.get("source_type", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if row.get("readiness_status", "").startswith("blocked_")
    )
    key_required_count = sum(
        1 for row in rows if row.get("source_type") == "public_api_key_required"
    )
    key_present_count = sum(
        1
        for row in rows
        if row.get("source_type") == "public_api_key_required"
        and _is_true(row.get("data_go_kr_key_present", "false"))
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            RAIL_FETCH_READINESS_SCOPE
            + " This packet cannot close rail evidence or provenance gates."
        ),
        "result_scope": RAIL_FETCH_READINESS_SCOPE,
        "row_count": len(rows),
        "readiness_status_counts": status_counts,
        "source_type_counts": source_type_counts,
        "blocking_request_count": blocking_count,
        "data_go_kr_key_required_count": key_required_count,
        "data_go_kr_key_present_request_count": key_present_count,
        "rail_evidence_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "rail_timing_source_request_packet": _display_path(
                Path(request_packet_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "supply DATA_GO_KR_KEY only for reviewed optional live fetches",
            "obtain reviewed static GTFS input before GTFS derivation",
            "retain raw payloads and cache files before deriving rail timing evidence",
            "review capacity and availability rows as bounded assumptions or replace with source-backed evidence",
            "create formal rail or parameter acceptance only after source-backed review",
        ],
        "remaining_blockers": [
            "rail timing cache files are absent unless source_cache_present is true",
            "API-key and reviewed-GTFS rows require external reviewer-provided inputs",
            "this packet is readiness evidence only and cannot create rail_service_evidence.csv",
        ],
    }


def build_rail_fetch_readiness_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable rail fetch-readiness packet."""

    lines = [
        "# Rail Fetch Readiness Packet",
        "",
        str(manifest.get("claim_boundary", RAIL_FETCH_READINESS_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Request rows: {manifest.get('row_count', 0)}",
        f"- Blocking requests: {manifest.get('blocking_request_count', 0)}",
        f"- Status counts: `{manifest.get('readiness_status_counts', {})}`",
        "",
        "## Readiness Rows",
        "",
        "| Request | Source Type | Status | Cache | Required Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        cache = "present" if _is_true(row.get("source_cache_present", "")) else "absent"
        lines.append(
            "| {request} | {source_type} | {status} | {cache} | {action} |".format(
                request=_cell(row.get("request_id", "")),
                source_type=_cell(row.get("source_type", "")),
                status=_cell(row.get("readiness_status", "")),
                cache=cache,
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Provide a reviewed API key, GTFS file, or explicit assumption decision where rows are blocked.",
            "- Preserve raw payloads and cache files before deriving rail timing evidence.",
            "- Re-run rail evidence and final-study readiness audits after evidence changes.",
            "- Do not create formal acceptance artifacts from this readiness packet alone.",
            "",
        ]
    )
    return "\n".join(lines)


def _readiness_row(
    row: Mapping[str, str],
    *,
    data_go_kr_key_present: bool,
) -> dict[str, str]:
    source_type = str(row.get("source_type", ""))
    cache_path = str(row.get("source_cache_path", ""))
    raw_path = str(row.get("raw_payload_path", ""))
    cache_present = _path_exists(cache_path)
    raw_present = _path_exists(raw_path)
    readiness_status, blocking_reason, action = _classify(
        source_type=source_type,
        cache_present=cache_present,
        raw_present=raw_present,
        data_go_kr_key_present=data_go_kr_key_present,
    )
    return {
        "request_id": str(row.get("request_id", "")),
        "region_id": str(row.get("region_id", "")),
        "evidence_fields": str(row.get("evidence_fields", "")),
        "source_type": source_type,
        "source_name": str(row.get("source_name", "")),
        "readiness_status": readiness_status,
        "blocking_reason": blocking_reason,
        "source_cache_path": cache_path,
        "source_cache_present": str(cache_present).lower(),
        "raw_payload_path": raw_path,
        "raw_payload_present": str(raw_present).lower(),
        "data_go_kr_key_present": str(data_go_kr_key_present).lower(),
        "required_reviewer_action": action,
        "fetch_command": str(row.get("fetch_command", "")),
        "derive_command": str(row.get("derive_command", "")),
        "target_evidence_artifact": "data/parameters/rail_service_evidence.csv",
        "can_support_rail_evidence_gate": "false",
        "claim_boundary": RAIL_FETCH_READINESS_SCOPE,
        "notes": str(row.get("notes", "")),
    }


def _classify(
    *,
    source_type: str,
    cache_present: bool,
    raw_present: bool,
    data_go_kr_key_present: bool,
) -> tuple[str, str, str]:
    if source_type == "public_api_key_required":
        if cache_present and raw_present:
            return (
                "ready_cached_api_payload_for_derivation_review",
                "",
                "review cached payload and run the listed derive command",
            )
        if data_go_kr_key_present:
            return (
                "ready_for_reviewed_live_api_fetch",
                "",
                "run the listed fetch command only after source and query choices are reviewed",
            )
        return (
            "blocked_missing_data_go_kr_key",
            "DATA_GO_KR_KEY is absent and no cached payload is present",
            "provide DATA_GO_KR_KEY or a reviewed cached API payload before derivation",
        )
    if source_type == "reviewed_static_gtfs_file_required":
        if cache_present:
            return (
                "ready_reviewed_gtfs_file_for_derivation_review",
                "",
                "review GTFS stop, route, service-window, and run the listed derive command",
            )
        return (
            "blocked_missing_reviewed_gtfs_file",
            "reviewed GTFS file is absent",
            "provide a reviewed GTFS zip or directory before derivation",
        )
    if source_type == "operator_or_literature_or_sensitivity_decision":
        return (
            "needs_human_review_capacity_treatment",
            "",
            "accept sensitivity-only capacity bounds or replace them with source-backed capacity evidence",
        )
    if source_type == "scenario_or_public_disruption_source_required":
        return (
            "needs_human_review_availability_scenario",
            "",
            "accept scenario-only rail availability bounds or replace them with source-backed disruption evidence",
        )
    return (
        "blocked_unclassified_source_type",
        f"unrecognized source_type {source_type!r}",
        "classify this rail request before evidence derivation",
    )


def _load_request_rows(path: str | Path) -> list[dict[str, str]]:
    packet = Path(path)
    if not packet.exists():
        return []
    with packet.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _path_exists(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    if ";" in text:
        return all(_path_exists(part.strip()) for part in text.split(";") if part.strip())
    return (PROJECT_ROOT / text).exists()


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


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
    "DEFAULT_RAIL_FETCH_READINESS_DOC_PATH",
    "DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH",
    "DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH",
    "RAIL_FETCH_READINESS_COLUMNS",
    "RAIL_FETCH_READINESS_SCOPE",
    "build_rail_fetch_readiness_manifest",
    "build_rail_fetch_readiness_markdown",
    "build_rail_fetch_readiness_rows",
    "write_rail_fetch_readiness_packet",
]
