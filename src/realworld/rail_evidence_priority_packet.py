"""Rail evidence priority packet.

This module joins rail evidence review rows with rail timing source requests
and fetch-readiness rows. The output names the concrete closure paths for
headway, travel time, capacity, availability, and station-binding prerequisites
without fetching live data or creating accepted rail-service evidence.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.rail_evidence_review_packet import (
    DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
)
from src.realworld.rail_fetch_readiness_packet import (
    DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
)
from src.realworld.rail_timing_request_packet import (
    DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_evidence_priority_packet.csv"
)
DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_evidence_priority_manifest.json"
)
DEFAULT_RAIL_EVIDENCE_PRIORITY_DOC_PATH = (
    PROJECT_ROOT / "docs" / "rail_evidence_priority_packet.md"
)
RAIL_EVIDENCE_PRIORITY_SCOPE = (
    "Rail evidence priority packet only; not cached rail timing evidence, "
    "not GTFS validation, not rail-service calibration, not emergency rail "
    "availability evidence, and not operational routing evidence."
)
RAIL_EVIDENCE_PRIORITY_COLUMNS: tuple[str, ...] = (
    "priority_id",
    "region_id",
    "evidence_fields",
    "closure_path_type",
    "source_name",
    "readiness_status",
    "blocking_reason",
    "review_priority",
    "station_binding_ready",
    "source_cache_path",
    "source_cache_present",
    "raw_payload_path",
    "raw_payload_present",
    "data_go_kr_key_present",
    "can_close_timing_fields_after_review",
    "timing_fields_closed_if_completed",
    "target_evidence_artifact",
    "needed_source_request_ids",
    "related_review_item_ids",
    "required_reviewer_action",
    "fetch_or_acquisition_command",
    "derive_or_review_command",
    "publication_use_status",
    "can_support_rail_evidence_gate",
    "claim_boundary",
)


def build_rail_evidence_priority_rows(
    *,
    evidence_review_path: str | Path = DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
    timing_request_path: str | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    fetch_readiness_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return rail evidence priority rows for current rail blockers."""

    evidence_rows = _read_csv_rows(evidence_review_path)
    request_rows = _read_csv_rows(timing_request_path)
    readiness_rows = _read_csv_rows(fetch_readiness_path)
    evidence_by_group = _evidence_by_group(evidence_rows)
    readiness_by_request = {
        row.get("request_id", ""): row for row in readiness_rows if row.get("request_id", "")
    }
    request_by_id = {
        row.get("request_id", ""): row for row in request_rows if row.get("request_id", "")
    }

    output = [
        _station_binding_row(evidence_by_group.get("station_binding", [])),
        _request_priority_row(
            request_by_id["rail_timetable_headway_request"],
            readiness_by_request.get("rail_timetable_headway_request", {}),
            related_review_item_ids=("rail_headway", "rail_timetable_derivation_path"),
            review_priority="high",
        ),
        _request_priority_row(
            request_by_id["rail_shortest_path_travel_time_request"],
            readiness_by_request.get("rail_shortest_path_travel_time_request", {}),
            related_review_item_ids=(
                "rail_travel_time",
                "rail_shortest_path_derivation_path",
            ),
            review_priority="high",
        ),
        _request_priority_row(
            request_by_id["rail_static_gtfs_timing_request"],
            readiness_by_request.get("rail_static_gtfs_timing_request", {}),
            related_review_item_ids=(
                "rail_headway",
                "rail_travel_time",
                "rail_gtfs_derivation_path",
            ),
            review_priority="high",
        ),
        _request_priority_row(
            request_by_id["rail_capacity_treatment_request"],
            readiness_by_request.get("rail_capacity_treatment_request", {}),
            related_review_item_ids=("rail_capacity",),
            review_priority="medium",
        ),
        _request_priority_row(
            request_by_id["rail_availability_scenario_request"],
            readiness_by_request.get("rail_availability_scenario_request", {}),
            related_review_item_ids=(
                "rail_service_window",
                "rail_availability_rule",
            ),
            review_priority="high",
        ),
    ]
    output.sort(key=_priority_sort_key)
    return output


def write_rail_evidence_priority_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_DOC_PATH,
    evidence_review_path: str | Path = DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
    timing_request_path: str | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    fetch_readiness_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
) -> dict[str, Any]:
    """Write rail evidence priority CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAIL_EVIDENCE_PRIORITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {column: str(row.get(column, "")) for column in RAIL_EVIDENCE_PRIORITY_COLUMNS}
            )

    summary = build_rail_evidence_priority_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        evidence_review_path=evidence_review_path,
        timing_request_path=timing_request_path,
        fetch_readiness_path=fetch_readiness_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_rail_evidence_priority_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_rail_evidence_priority_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_DOC_PATH,
    evidence_review_path: str | Path = DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
    timing_request_path: str | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    fetch_readiness_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for rail evidence priority rows."""

    status_counts = _counts(row.get("readiness_status", "") for row in rows)
    blocking_count = sum(
        1
        for row in rows
        if str(row.get("readiness_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("readiness_status", "")).startswith("needs_human_review_")
    )
    timing_candidate_count = sum(
        1
        for row in rows
        if str(row.get("can_close_timing_fields_after_review", "")).lower() == "true"
    )
    return {
        "schema_version": 1,
        "result_scope": RAIL_EVIDENCE_PRIORITY_SCOPE,
        "claim_boundary": (
            "This packet prioritizes rail evidence closure paths. It does not "
            "fetch API data, provide GTFS files, derive rail_service_evidence.csv, "
            "or close rail, parameter, provenance, validation, or final-study gates."
        ),
        "row_count": len(rows),
        "readiness_status_counts": status_counts,
        "blocking_priority_count": blocking_count,
        "human_review_priority_count": human_review_count,
        "timing_closure_candidate_count": timing_candidate_count,
        "station_binding_prerequisite_ready": any(
            row.get("priority_id") == "station_binding_prerequisite"
            and row.get("readiness_status") == "prerequisite_ready_not_timing_evidence"
            for row in rows
        ),
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "rail_evidence_review_packet": _display_path(evidence_review_path),
            "rail_timing_source_request_packet": _display_path(timing_request_path),
            "rail_fetch_readiness_packet": _display_path(fetch_readiness_path),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "decide whether GTFS, timetable plus shortest-path, or another reviewed source path will close rail timing",
            "supply DATA_GO_KR_KEY or reviewed cached payloads only after source review",
            "keep capacity and availability as bounded assumptions unless source-backed evidence is added",
            "rerun rail evidence, parameter evidence, publication-readiness, and final-study audits after rail evidence changes",
        ],
        "remaining_blockers": [
            "rail timing cache files are absent",
            "DATA_GO_KR_KEY or reviewed GTFS input is absent",
            "capacity and availability treatment still require human/source-backed decisions",
        ],
    }


def build_rail_evidence_priority_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for rail evidence priority review."""

    lines = [
        "# Rail Evidence Priority Packet",
        "",
        str(manifest.get("claim_boundary", RAIL_EVIDENCE_PRIORITY_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Priority rows: {manifest.get('row_count', 0)}",
        f"- Blocking priorities: {manifest.get('blocking_priority_count', 0)}",
        f"- Human-review priorities: {manifest.get('human_review_priority_count', 0)}",
        f"- Timing closure candidates: {manifest.get('timing_closure_candidate_count', 0)}",
        f"- Status counts: `{manifest.get('readiness_status_counts', {})}`",
        "",
        "## Priority Rows",
        "",
        "| Priority | Fields | Status | Cache | Timing Closure | Required Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        cache = "present" if row.get("source_cache_present") == "true" else "absent"
        lines.append(
            "| {priority} | {fields} | {status} | {cache} | {closure} | {action} |".format(
                priority=_cell(row.get("priority_id", "")),
                fields=_cell(row.get("evidence_fields", "")),
                status=_cell(row.get("readiness_status", "")),
                cache=cache,
                closure=_cell(row.get("timing_fields_closed_if_completed", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is rail-evidence prioritization support only.",
            "- It does not fetch live data, validate GTFS, derive rail service evidence, or certify rail availability.",
            "- It cannot create or replace `data/parameters/rail_service_evidence.csv`.",
            "",
        ]
    )
    return "\n".join(lines)


def _station_binding_row(rows: Sequence[Mapping[str, str]]) -> dict[str, str]:
    region_id = rows[0].get("region_id", "") if rows else ""
    ready = bool(rows) and all(
        str(row.get("station_binding_ready", "")).lower() == "true" for row in rows
    )
    review_items = _join_sorted(row.get("review_item_id", "") for row in rows)
    source_cache_present = "true" if ready else "false"
    return {
        "priority_id": "station_binding_prerequisite",
        "region_id": region_id,
        "evidence_fields": "station_binding",
        "closure_path_type": "prerequisite",
        "source_name": "cached official station-name binding extract",
        "readiness_status": (
            "prerequisite_ready_not_timing_evidence"
            if ready
            else "blocked_missing_station_binding"
        ),
        "blocking_reason": "",
        "review_priority": "low",
        "station_binding_ready": str(ready).lower(),
        "source_cache_path": "data/parameters/rail_station_bindings.csv",
        "source_cache_present": source_cache_present,
        "raw_payload_path": "data/rail/pilot_station_binding_cache.csv",
        "raw_payload_present": source_cache_present,
        "data_go_kr_key_present": "false",
        "can_close_timing_fields_after_review": "false",
        "timing_fields_closed_if_completed": "",
        "target_evidence_artifact": "data/parameters/rail_station_bindings.csv",
        "needed_source_request_ids": "",
        "related_review_item_ids": review_items,
        "required_reviewer_action": (
            "keep station binding separate from timing, capacity, and availability evidence"
        ),
        "fetch_or_acquisition_command": "not applicable",
        "derive_or_review_command": "review station binding cache and source provenance",
        "publication_use_status": "prerequisite_ready_not_service_timing",
        "can_support_rail_evidence_gate": "false",
        "claim_boundary": RAIL_EVIDENCE_PRIORITY_SCOPE,
    }


def _request_priority_row(
    request: Mapping[str, str],
    readiness: Mapping[str, str],
    *,
    related_review_item_ids: Sequence[str],
    review_priority: str,
) -> dict[str, str]:
    readiness_status = str(
        readiness.get("readiness_status", "")
        or "needs_human_review_source_request"
    )
    source_cache_present = str(readiness.get("source_cache_present", "")).lower()
    raw_payload_present = str(readiness.get("raw_payload_present", "")).lower()
    can_close_timing = (
        str(request.get("can_close_rail_timing_gate", "")).lower() == "true"
    )
    evidence_fields = str(request.get("evidence_fields", ""))
    return {
        "priority_id": str(request.get("request_id", "")),
        "region_id": str(request.get("region_id", "")),
        "evidence_fields": evidence_fields,
        "closure_path_type": str(request.get("source_type", "")),
        "source_name": str(request.get("source_name", "")),
        "readiness_status": readiness_status,
        "blocking_reason": str(readiness.get("blocking_reason", "")),
        "review_priority": review_priority,
        "station_binding_ready": "true",
        "source_cache_path": str(request.get("source_cache_path", "")),
        "source_cache_present": source_cache_present or "false",
        "raw_payload_path": str(request.get("raw_payload_path", "")),
        "raw_payload_present": raw_payload_present or "false",
        "data_go_kr_key_present": str(
            readiness.get("data_go_kr_key_present", "")
        ).lower()
        or "false",
        "can_close_timing_fields_after_review": str(can_close_timing).lower(),
        "timing_fields_closed_if_completed": (
            evidence_fields if can_close_timing else ""
        ),
        "target_evidence_artifact": str(
            readiness.get("target_evidence_artifact", "")
            or "data/parameters/rail_service_evidence.csv"
        ),
        "needed_source_request_ids": str(request.get("request_id", "")),
        "related_review_item_ids": _join_sorted(related_review_item_ids),
        "required_reviewer_action": str(
            readiness.get("required_reviewer_action", "")
            or request.get("required_external_input", "")
        ),
        "fetch_or_acquisition_command": str(request.get("fetch_command", "")),
        "derive_or_review_command": str(request.get("derive_command", "")),
        "publication_use_status": str(request.get("publication_use_status", "")),
        "can_support_rail_evidence_gate": "false",
        "claim_boundary": RAIL_EVIDENCE_PRIORITY_SCOPE,
    }


def _evidence_by_group(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, list[Mapping[str, str]]]:
    grouped: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("evidence_group", ""))].append(row)
    return dict(grouped)


def _priority_sort_key(row: Mapping[str, str]) -> tuple[int, str]:
    status = str(row.get("readiness_status", ""))
    if status.startswith("blocked_"):
        order = 0
    elif status.startswith("needs_human_review_"):
        order = 1
    elif status.startswith("prerequisite_ready"):
        order = 2
    else:
        order = 3
    return (order, str(row.get("priority_id", "")))


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    filepath = Path(path)
    with filepath.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] += 1
    return dict(sorted(counts.items()))


def _join_sorted(values: Iterable[Any]) -> str:
    return "; ".join(sorted({str(value).strip() for value in values if str(value).strip()}))


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_RAIL_EVIDENCE_PRIORITY_DOC_PATH",
    "DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH",
    "DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH",
    "RAIL_EVIDENCE_PRIORITY_COLUMNS",
    "RAIL_EVIDENCE_PRIORITY_SCOPE",
    "build_rail_evidence_priority_manifest",
    "build_rail_evidence_priority_markdown",
    "build_rail_evidence_priority_rows",
    "write_rail_evidence_priority_packet",
]
