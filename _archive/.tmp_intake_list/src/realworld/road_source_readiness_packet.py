"""Road source-readiness packet generation.

The road evidence source-request worksheet names the source packages needed for
speed, capacity, background-traffic, disruption, and override-application
claims. This module adds a deterministic preflight layer that classifies which
requests are blocked by missing source evidence and which are merely ready for
human review. It does not create reviewed road overrides or calibrate the road
network.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.road_evidence_request_packet import (
    DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    ROAD_EVIDENCE_SOURCE_REQUEST_SCOPE,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_source_readiness_packet.csv"
)
DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_source_readiness_manifest.json"
)
DEFAULT_ROAD_SOURCE_READINESS_DOC_PATH = (
    PROJECT_ROOT / "docs" / "road_source_readiness_packet.md"
)
DEFAULT_ROAD_SPEED_EVIDENCE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_speed_evidence_manifest.json"
)
DEFAULT_ROAD_CAPACITY_EVIDENCE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_capacity_evidence_manifest.json"
)
DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_review_manifest.json"
)
DEFAULT_PILOT_FULL_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json"
)
ROAD_SOURCE_READINESS_SCOPE = (
    "Road source-readiness packet only; not reviewed road-class overrides, "
    "not calibrated speed or capacity evidence, not accepted disruption "
    "evidence, not proof that overrides were applied, and not operational "
    "routing evidence."
)
ROAD_SOURCE_READINESS_COLUMNS: tuple[str, ...] = (
    "request_id",
    "region_id",
    "evidence_fields",
    "source_type",
    "source_name",
    "source_url_or_citation",
    "required_external_input",
    "readiness_status",
    "blocking_reason",
    "source_cache_path",
    "source_cache_present",
    "raw_payload_path",
    "raw_payload_present",
    "target_output_path",
    "target_output_present",
    "required_reviewer_action",
    "fetch_or_acquisition_command",
    "derive_or_review_command",
    "can_support_road_evidence_gate",
    "can_support_road_application_gate",
    "claim_boundary",
    "notes",
)


def build_road_source_readiness_rows(
    *,
    request_rows: Sequence[Mapping[str, str]] | None = None,
    request_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    speed_manifest_path: str | Path = DEFAULT_ROAD_SPEED_EVIDENCE_MANIFEST_PATH,
    capacity_manifest_path: str | Path = DEFAULT_ROAD_CAPACITY_EVIDENCE_MANIFEST_PATH,
    validation_manifest_path: str | Path = DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH,
    pilot_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
) -> list[dict[str, str]]:
    """Return source-readiness rows for road evidence source requests."""

    rows = (
        list(request_rows)
        if request_rows is not None
        else _load_request_rows(request_packet_path)
    )
    context = {
        "speed_manifest": _load_json(speed_manifest_path),
        "capacity_manifest": _load_json(capacity_manifest_path),
        "validation_manifest": _load_json(validation_manifest_path),
        "pilot_manifest": _load_json(pilot_manifest_path),
    }
    return [_readiness_row(row, context=context) for row in rows]


def write_road_source_readiness_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_DOC_PATH,
    request_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
) -> dict[str, Any]:
    """Write road source-readiness CSV, manifest, and Markdown artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROAD_SOURCE_READINESS_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {column: str(row.get(column, "")) for column in ROAD_SOURCE_READINESS_COLUMNS}
            )

    summary = build_road_source_readiness_manifest(
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
        build_road_source_readiness_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_road_source_readiness_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_DOC_PATH,
    request_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for road source-readiness rows."""

    status_counts = _counts(row.get("readiness_status", "") for row in rows)
    source_type_counts = _counts(row.get("source_type", "") for row in rows)
    region_ids = _region_ids(rows)
    source_citation_count = sum(
        1 for row in rows if str(row.get("source_url_or_citation", "")).strip()
    )
    external_input_count = sum(
        1 for row in rows if str(row.get("required_external_input", "")).strip()
    )
    blocking_count = sum(
        1 for row in rows if str(row.get("readiness_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("readiness_status", "")).startswith("needs_human_review_")
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            ROAD_SOURCE_READINESS_SCOPE
            + " This packet cannot close cached-road, parameter, validation, or "
            "formal road acceptance gates."
        ),
        "result_scope": ROAD_SOURCE_READINESS_SCOPE,
        "row_count": len(rows),
        "region_ids": region_ids,
        "readiness_status_counts": status_counts,
        "source_type_counts": source_type_counts,
        "source_url_or_citation_present_count": source_citation_count,
        "required_external_input_present_count": external_input_count,
        "blocking_request_count": blocking_count,
        "human_review_request_count": human_review_count,
        "road_evidence_gate_closure_candidate_count": 0,
        "road_application_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "road_evidence_source_request_packet": _display_path(
                Path(request_packet_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "replace sparse speed candidates with reviewed speed evidence or accepted assumptions",
            "provide traffic counts, agency capacity references, or reviewed capacity assumptions",
            "review benchmark and disruption scenario treatment before final claims",
            "create data/parameters/road_class_overrides.csv only after source-backed review",
            "rerun pilot outputs with reviewed overrides before road calibration claims",
        ],
        "remaining_blockers": _remaining_blockers(
            rows,
            extra=[
                "capacity and disruption evidence still require external source or formal assumption decisions",
                "this packet is readiness evidence only and cannot create road-class overrides",
            ],
        ),
    }


def build_road_source_readiness_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable road source-readiness packet."""

    lines = [
        "# Road Source Readiness Packet",
        "",
        str(manifest.get("claim_boundary", ROAD_SOURCE_READINESS_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Region IDs: `{manifest.get('region_ids', [])}`",
        f"- Request rows: {manifest.get('row_count', 0)}",
        f"- Blocking requests: {manifest.get('blocking_request_count', 0)}",
        f"- Human-review requests: {manifest.get('human_review_request_count', 0)}",
        f"- Status counts: `{manifest.get('readiness_status_counts', {})}`",
        "",
        "## Readiness Rows",
        "",
        "| Request | Source | Source Type | Status | Source Cache | Target | Required Input | Required Action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        source_cache = (
            "present" if _is_true(row.get("source_cache_present", "")) else "absent"
        )
        target = "present" if _is_true(row.get("target_output_present", "")) else "absent"
        lines.append(
            "| {request} | {source} | {source_type} | {status} | {source_cache} | {target} | {input} | {action} |".format(
                request=_cell(row.get("request_id", "")),
                source=_cell(_source_summary(row)),
                source_type=_cell(row.get("source_type", "")),
                status=_cell(row.get("readiness_status", "")),
                source_cache=source_cache,
                target=target,
                input=_cell(row.get("required_external_input", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Supply reviewed speed, capacity, disruption, and benchmark evidence or bounded assumptions.",
            "- Move accepted road-class values into `data/parameters/road_class_overrides.csv` only after review.",
            "- Re-run pilot outputs with the reviewed override table before road-calibration claims.",
            "- Do not create formal acceptance artifacts from this readiness packet alone.",
            "",
        ]
    )
    return "\n".join(lines)


def _readiness_row(
    row: Mapping[str, str],
    *,
    context: Mapping[str, Mapping[str, Any] | None],
) -> dict[str, str]:
    source_type = str(row.get("source_type", ""))
    cache_path = str(row.get("source_cache_path", ""))
    raw_path = str(row.get("raw_payload_path", ""))
    target_path = str(row.get("target_output_path", ""))
    cache_present = _path_exists(cache_path)
    raw_present = _path_exists(raw_path)
    target_present = _path_exists(target_path)
    readiness_status, blocking_reason, action = _classify(
        source_type=source_type,
        cache_present=cache_present,
        raw_present=raw_present,
        target_present=target_present,
        context=context,
    )
    return {
        "request_id": str(row.get("request_id", "")),
        "region_id": str(row.get("region_id", "")),
        "evidence_fields": str(row.get("evidence_fields", "")),
        "source_type": source_type,
        "source_name": str(row.get("source_name", "")),
        "source_url_or_citation": str(row.get("source_url_or_citation", "")),
        "required_external_input": str(row.get("required_external_input", "")),
        "readiness_status": readiness_status,
        "blocking_reason": blocking_reason,
        "source_cache_path": cache_path,
        "source_cache_present": str(cache_present).lower(),
        "raw_payload_path": raw_path,
        "raw_payload_present": str(raw_present).lower(),
        "target_output_path": target_path,
        "target_output_present": str(target_present).lower(),
        "required_reviewer_action": action,
        "fetch_or_acquisition_command": str(row.get("fetch_or_acquisition_command", "")),
        "derive_or_review_command": str(row.get("derive_or_review_command", "")),
        "can_support_road_evidence_gate": "false",
        "can_support_road_application_gate": "false",
        "claim_boundary": ROAD_SOURCE_READINESS_SCOPE,
        "notes": str(row.get("notes", "")),
    }


def _classify(
    *,
    source_type: str,
    cache_present: bool,
    raw_present: bool,
    target_present: bool,
    context: Mapping[str, Mapping[str, Any] | None],
) -> tuple[str, str, str]:
    if source_type == "public_speed_limit_or_benchmark_source_required":
        observed = _int_value(context.get("speed_manifest"), "rows_with_observed_maxspeed")
        if cache_present and observed > 0:
            return (
                "needs_human_review_sparse_speed_candidates",
                "",
                "review sparse maxspeed candidates or replace them with public speed-limit or benchmark evidence",
            )
        return (
            "blocked_missing_speed_source_candidates",
            "road speed candidate evidence is absent or has no observed maxspeed rows",
            "generate or supply reviewed speed-limit evidence before road-class overrides",
        )
    if source_type == "traffic_count_or_capacity_reference_required":
        observed = _int_value(context.get("capacity_manifest"), "rows_with_observed_lanes")
        if cache_present and observed > 0:
            return (
                "needs_human_review_lane_capacity_candidates",
                "",
                "review lane-derived capacity candidates against traffic counts or agency references",
            )
        return (
            "blocked_missing_capacity_source",
            "cached lane-count evidence has no parseable observed lane rows",
            "provide traffic counts, agency capacity references, or reviewed capacity assumptions",
        )
    if source_type == "routing_or_observed_traffic_benchmark_required":
        if cache_present or raw_present:
            return (
                "needs_human_review_benchmark_strategy",
                "",
                "decide whether current route benchmarks are plausibility-only or support a bounded traffic assumption",
            )
        return (
            "blocked_missing_route_benchmark",
            "route benchmark artifacts are absent",
            "run or supply reviewed route benchmark evidence before background-traffic claims",
        )
    if source_type == "hazard_incident_or_reviewed_scenario_source_required":
        if cache_present:
            return (
                "needs_human_review_disruption_scenario",
                "",
                "accept scenario-only disruption treatment or replace it with hazard, incident, or literature evidence",
            )
        return (
            "blocked_missing_disruption_source",
            "disruption scenario or source artifact is absent",
            "provide hazard, incident, literature, or reviewed scenario evidence",
        )
    if source_type == "reviewed_override_table_and_manifest_application_required":
        pilot = context.get("pilot_manifest") or {}
        overrides_applied = bool(pilot.get("road_class_overrides_applied", False))
        if target_present and overrides_applied:
            return (
                "needs_human_review_override_application_manifest",
                "",
                "review override sources and verify the pilot manifest applies the reviewed table",
            )
        if target_present:
            return (
                "blocked_override_not_applied_to_pilot_manifest",
                "reviewed override target exists but pilot manifest does not show it was applied",
                "rerun pilot outputs with --road-class-overrides-path and verify manifest SHA256",
            )
        return (
            "blocked_missing_reviewed_road_class_overrides",
            "data/parameters/road_class_overrides.csv is absent",
            "create reviewed road_class_overrides.csv after source-backed road evidence review",
        )
    return (
        "blocked_unclassified_source_type",
        f"unrecognized source_type {source_type!r}",
        "classify this road request before evidence derivation",
    )


def _remaining_blockers(
    rows: Sequence[Mapping[str, str]],
    *,
    extra: Sequence[str] = (),
) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("readiness_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(reason)
    blockers.extend(str(reason).strip() for reason in extra if str(reason).strip())
    return list(dict.fromkeys(blockers))


def _load_request_rows(path: str | Path) -> list[dict[str, str]]:
    packet = Path(path)
    if not packet.exists():
        return []
    with packet.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_json(path: str | Path) -> dict[str, Any] | None:
    record = Path(path)
    if not record.exists():
        return None
    with record.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else None


def _path_exists(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    if ";" in text:
        return all(_path_exists(part.strip()) for part in text.split(";") if part.strip())
    candidate = Path(text)
    if candidate.is_absolute():
        return candidate.exists()
    return (PROJECT_ROOT / candidate).exists()


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _region_ids(rows: Sequence[Mapping[str, str]]) -> list[str]:
    return sorted(
        {
            str(row.get("region_id", "")).strip()
            for row in rows
            if str(row.get("region_id", "")).strip()
        }
    )


def _int_value(record: Mapping[str, Any] | None, key: str) -> int:
    try:
        return int((record or {}).get(key, 0))
    except (TypeError, ValueError):
        return 0


def _is_true(value: str) -> bool:
    return str(value).strip().lower() == "true"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _source_summary(row: Mapping[str, str]) -> str:
    name = str(row.get("source_name", "")).strip()
    citation = str(row.get("source_url_or_citation", "")).strip()
    if name and citation:
        return f"{name}<br>{citation}"
    return name or citation


__all__ = [
    "DEFAULT_ROAD_SOURCE_READINESS_DOC_PATH",
    "DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH",
    "DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH",
    "ROAD_SOURCE_READINESS_COLUMNS",
    "ROAD_SOURCE_READINESS_SCOPE",
    "build_road_source_readiness_manifest",
    "build_road_source_readiness_markdown",
    "build_road_source_readiness_rows",
    "write_road_source_readiness_packet",
]
