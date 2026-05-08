"""Rail source decision worksheet.

This module turns rail fetch-readiness rows into per-request reviewer decision
rows. It does not fetch rail data, validate GTFS, derive rail service evidence,
accept sensitivity-only rail assumptions, or close the rail evidence gate.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.rail_evidence_priority_packet import (
    DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
)
from src.realworld.rail_evidence_review_packet import (
    DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
)
from src.realworld.rail_fetch_readiness_packet import (
    DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
)
from src.realworld.rail_timing_request_packet import (
    DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_source_decision_packet.csv"
)
DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_source_decision_manifest.json"
)
DEFAULT_RAIL_SOURCE_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "rail_source_decision_packet.md"
)
DEFAULT_RAIL_SERVICE_EVIDENCE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "rail_service_evidence.csv"
)
RAIL_SOURCE_DECISION_SCOPE = (
    "Rail source-decision packet only; not rail timing evidence, not GTFS "
    "validation, not rail-service calibration, not emergency rail availability "
    "evidence, not sensitivity-only rail acceptance, and not rail evidence gate "
    "closure."
)
RAIL_SOURCE_DECISION_COLUMNS: tuple[str, ...] = (
    "request_id",
    "region_id",
    "evidence_fields",
    "review_priority",
    "current_readiness_status",
    "decision_topic",
    "candidate_decision_options",
    "provisional_decision",
    "decision_status",
    "blocking_reason",
    "source_type",
    "source_name",
    "source_url_or_citation",
    "required_external_input",
    "source_cache_path",
    "source_cache_present",
    "raw_payload_path",
    "raw_payload_present",
    "data_go_kr_key_present",
    "fetch_command",
    "derive_command",
    "target_evidence_artifact",
    "required_reviewer_action",
    "required_evidence_fields",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_timing_fields_after_review",
    "can_support_rail_evidence_gate",
    "can_support_acceptance_gate",
    "claim_boundary",
)


def build_rail_source_decision_rows(
    *,
    readiness_rows: Sequence[Mapping[str, str]] | None = None,
    fetch_readiness_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
    fetch_readiness_manifest_path: str
    | Path = DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    priority_packet_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
    priority_manifest_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    timing_request_packet_path: str
    | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    rail_review_packet_path: str | Path = DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return one pending rail-source decision row per readiness row."""

    rows = (
        list(readiness_rows)
        if readiness_rows is not None
        else _read_csv_rows(fetch_readiness_path)
    )
    evidence_paths = _evidence_paths(
        fetch_readiness_path=fetch_readiness_path,
        fetch_readiness_manifest_path=fetch_readiness_manifest_path,
        priority_packet_path=priority_packet_path,
        priority_manifest_path=priority_manifest_path,
        timing_request_packet_path=timing_request_packet_path,
        rail_review_packet_path=rail_review_packet_path,
    )
    decision_rows = [_decision_row(row, evidence_paths=evidence_paths) for row in rows]
    decision_rows.sort(key=lambda row: (_decision_sort_key(row), row["request_id"]))
    return decision_rows


def write_rail_source_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_DOC_PATH,
    fetch_readiness_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
    fetch_readiness_manifest_path: str
    | Path = DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    priority_packet_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
    priority_manifest_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    timing_request_packet_path: str
    | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    rail_review_packet_path: str | Path = DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Write rail-source decision CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAIL_SOURCE_DECISION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in RAIL_SOURCE_DECISION_COLUMNS
                }
            )

    summary = build_rail_source_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        fetch_readiness_path=fetch_readiness_path,
        fetch_readiness_manifest_path=fetch_readiness_manifest_path,
        priority_packet_path=priority_packet_path,
        priority_manifest_path=priority_manifest_path,
        timing_request_packet_path=timing_request_packet_path,
        rail_review_packet_path=rail_review_packet_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_rail_source_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_rail_source_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_DOC_PATH,
    fetch_readiness_path: str | Path = DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
    fetch_readiness_manifest_path: str
    | Path = DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    priority_packet_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
    priority_manifest_path: str | Path = DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    timing_request_packet_path: str
    | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    rail_review_packet_path: str | Path = DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for rail-source decisions."""

    decision_counts = _counts(row.get("decision_status", "") for row in rows)
    readiness_counts = _counts(row.get("current_readiness_status", "") for row in rows)
    source_type_counts = _counts(row.get("source_type", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("decision_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("decision_status", "")).startswith("needs_human_review_")
    )
    timing_decision_count = sum(
        1
        for row in rows
        if any(
            field in str(row.get("evidence_fields", ""))
            for field in ("headway", "travel_time")
        )
    )
    cache_present_count = sum(
        1
        for row in rows
        if str(row.get("source_cache_present", "")).strip().lower() == "true"
    )
    return {
        "schema_version": 1,
        "result_scope": RAIL_SOURCE_DECISION_SCOPE,
        "claim_boundary": (
            RAIL_SOURCE_DECISION_SCOPE
            + " It cannot create data/parameters/rail_service_evidence.csv."
        ),
        "row_count": len(rows),
        "region_ids": _region_ids(rows),
        "decision_ids": [str(row.get("request_id", "")) for row in rows],
        "decision_status_counts": decision_counts,
        "readiness_status_counts": readiness_counts,
        "source_type_counts": source_type_counts,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "timing_source_decision_count": timing_decision_count,
        "source_cache_present_count": cache_present_count,
        "rail_service_evidence_present": DEFAULT_RAIL_SERVICE_EVIDENCE_PATH.exists(),
        "rail_source_decision_recorded": False,
        "rail_service_evidence_gate_closure_candidate_count": 0,
        "acceptance_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "rail_fetch_readiness_packet": _display_path(fetch_readiness_path),
            "rail_fetch_readiness_manifest": _display_path(
                fetch_readiness_manifest_path
            ),
            "rail_evidence_priority_packet": _display_path(priority_packet_path),
            "rail_evidence_priority_manifest": _display_path(priority_manifest_path),
            "rail_timing_source_request_packet": _display_path(
                timing_request_packet_path
            ),
            "rail_evidence_review_packet": _display_path(rail_review_packet_path),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "choose GTFS, timetable plus shortest-path, another reviewed rail timing source, sensitivity-only treatment, or exclusion for timing claims",
            "choose source-backed capacity evidence, explicit sensitivity-only capacity bounds, or exclusion for capacity-dependent claims",
            "choose source-backed rail availability evidence, accepted scenario-only treatment, or exclusion for availability-dependent claims",
            "preserve raw payloads, cache files, extraction date, source/license review, station binding, and not-operational claim boundaries before deriving evidence",
            "rerun rail, parameter, provenance, publication-readiness, and final-study audits after decisions are recorded",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_rail_source_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for the rail-source decision worksheet."""

    lines = [
        "# Rail Source Decision Packet",
        "",
        str(manifest.get("claim_boundary", RAIL_SOURCE_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Rail-service evidence present: `{str(manifest.get('rail_service_evidence_present', False)).lower()}`",
        f"- Decision rows: {manifest.get('row_count', 0)}",
        f"- Blocking decisions: {manifest.get('blocking_decision_count', 0)}",
        f"- Human-review decisions: {manifest.get('human_review_decision_count', 0)}",
        f"- Timing-source decisions: {manifest.get('timing_source_decision_count', 0)}",
        "",
        "## Decision Rows",
        "",
        "| Request | Fields | Status | Options | Required Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {request} | {fields} | {status} | {options} | {action} |".format(
                request=_cell(row.get("request_id", "")),
                fields=_cell(row.get("evidence_fields", "")),
                status=_cell(row.get("decision_status", "")),
                options=_cell(row.get("candidate_decision_options", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is a reviewer worksheet, not a formal decision record.",
            "- It does not fetch data, derive `rail_service_evidence.csv`, accept GTFS, or certify rail service availability.",
            "- Keep rail evidence claims blocked until source-backed changes or formal acceptance exist.",
            "",
        ]
    )
    return "\n".join(lines)


def _decision_row(
    row: Mapping[str, str],
    *,
    evidence_paths: str,
) -> dict[str, str]:
    readiness_status = str(row.get("readiness_status", ""))
    if readiness_status.startswith("blocked_"):
        decision_status = "blocked_missing_rail_source_decision"
    elif readiness_status.startswith("needs_human_review_"):
        decision_status = "needs_human_review_rail_source_decision"
    elif readiness_status.startswith("ready_"):
        decision_status = "needs_human_review_ready_rail_source_decision"
    else:
        decision_status = "blocked_unclassified_rail_source_decision"
    blocking_reason = str(row.get("blocking_reason", "")).strip()
    if not blocking_reason and decision_status.startswith("blocked_"):
        blocking_reason = "rail source decision is not classified"
    return {
        "request_id": str(row.get("request_id", "")),
        "region_id": str(row.get("region_id", "")),
        "evidence_fields": str(row.get("evidence_fields", "")),
        "review_priority": _review_priority(row),
        "current_readiness_status": readiness_status,
        "decision_topic": _decision_topic(row),
        "candidate_decision_options": _candidate_options(row),
        "provisional_decision": "pending_reviewer_decision",
        "decision_status": decision_status,
        "blocking_reason": blocking_reason,
        "source_type": str(row.get("source_type", "")),
        "source_name": str(row.get("source_name", "")),
        "source_url_or_citation": str(row.get("source_url_or_citation", "")),
        "required_external_input": str(row.get("required_external_input", "")),
        "source_cache_path": str(row.get("source_cache_path", "")),
        "source_cache_present": str(row.get("source_cache_present", "")),
        "raw_payload_path": str(row.get("raw_payload_path", "")),
        "raw_payload_present": str(row.get("raw_payload_present", "")),
        "data_go_kr_key_present": str(row.get("data_go_kr_key_present", "")),
        "fetch_command": str(row.get("fetch_command", "")),
        "derive_command": str(row.get("derive_command", "")),
        "target_evidence_artifact": str(
            row.get("target_evidence_artifact", "")
            or _display_path(DEFAULT_RAIL_SERVICE_EVIDENCE_PATH)
        ),
        "required_reviewer_action": (
            "Choose whether to provide source-backed rail evidence, retain the "
            "item as sensitivity-only or scenario-only within strict claim "
            "limits, or exclude the affected claim from final-study interpretation."
        ),
        "required_evidence_fields": (
            "reviewer; decision_date; decision_basis; evidence_paths; "
            "source_license_or_assumption_scope; extraction_date; raw_payload_path; "
            "station_binding_scope; sensitivity_or_scenario_treatment; "
            "not_operational_claim_boundary; acceptance_or_exclusion_rationale"
        ),
        "followup_artifacts": _followup_artifacts(row),
        "evidence_input_paths": evidence_paths,
        "can_support_timing_fields_after_review": str(
            _can_support_timing_after_review(row)
        ).lower(),
        "can_support_rail_evidence_gate": "false",
        "can_support_acceptance_gate": "false",
        "claim_boundary": RAIL_SOURCE_DECISION_SCOPE,
    }


def _decision_topic(row: Mapping[str, str]) -> str:
    source_type = str(row.get("source_type", ""))
    evidence_fields = str(row.get("evidence_fields", ""))
    if source_type == "public_api_key_required":
        return "Reviewed API cache, live fetch, or alternate rail timing source"
    if source_type == "reviewed_static_gtfs_file_required":
        return "Reviewed static GTFS acquisition and derivation decision"
    if source_type == "operator_or_literature_or_sensitivity_decision":
        return "Rail capacity source or sensitivity-only treatment"
    if source_type == "scenario_or_public_disruption_source_required":
        return "Rail availability source or scenario treatment"
    if "headway" in evidence_fields or "travel_time" in evidence_fields:
        return "Rail timing source decision"
    return "Rail source or assumption treatment"


def _candidate_options(row: Mapping[str, str]) -> str:
    source_type = str(row.get("source_type", ""))
    if source_type == "public_api_key_required":
        options = [
            "provide_reviewed_cached_api_payload",
            "run_reviewed_live_api_fetch_and_cache_raw_payload",
            "use_reviewed_gtfs_or_alternate_timing_source",
            "retain_current_timing_assumption_as_sensitivity_only",
            "exclude_timing_dependent_final_claims",
        ]
    elif source_type == "reviewed_static_gtfs_file_required":
        options = [
            "provide_reviewed_static_gtfs_feed",
            "pair_reviewed_timetable_headway_with_shortest_path_travel_time",
            "use_other_reviewed_transit_timing_source",
            "retain_current_timing_assumption_as_sensitivity_only",
            "exclude_timing_dependent_final_claims",
        ]
    elif source_type == "operator_or_literature_or_sensitivity_decision":
        options = [
            "replace_with_operator_or_literature_capacity_source",
            "retain_capacity_as_sensitivity_only_with_bounds",
            "exclude_capacity_dependent_final_claims",
        ]
    elif source_type == "scenario_or_public_disruption_source_required":
        options = [
            "replace_with_public_disruption_or_incident_source",
            "accept_scenario_only_availability_with_scope",
            "retain_availability_as_sensitivity_only",
            "exclude_availability_dependent_final_claims",
        ]
    else:
        options = [
            "replace_with_source_backed_rail_values",
            "retain_as_sensitivity_only",
            "exclude_from_final_claims",
        ]
    return "; ".join(options)


def _followup_artifacts(row: Mapping[str, str]) -> str:
    values = [
        str(row.get("source_cache_path", "")),
        str(row.get("raw_payload_path", "")),
        str(row.get("target_evidence_artifact", "")),
        "data/parameters/rail_service_evidence.csv",
        "data/parameters/rail_assumptions.csv",
        "data/manifests/provenance_acceptance.json",
        "data/manifests/validation_acceptance.json",
    ]
    if str(row.get("source_type", "")) == "operator_or_literature_or_sensitivity_decision":
        values.append("data/parameters/parameter_acceptance.csv")
    return "; ".join(_dedupe(value for value in values if str(value).strip()))


def _can_support_timing_after_review(row: Mapping[str, str]) -> bool:
    source_type = str(row.get("source_type", ""))
    fields = str(row.get("evidence_fields", ""))
    return source_type in {
        "public_api_key_required",
        "reviewed_static_gtfs_file_required",
    } and ("headway" in fields or "travel_time" in fields)


def _evidence_paths(
    *,
    fetch_readiness_path: str | Path,
    fetch_readiness_manifest_path: str | Path,
    priority_packet_path: str | Path,
    priority_manifest_path: str | Path,
    timing_request_packet_path: str | Path,
    rail_review_packet_path: str | Path,
) -> str:
    paths = [
        fetch_readiness_path,
        fetch_readiness_manifest_path,
        priority_packet_path,
        priority_manifest_path,
        timing_request_packet_path,
        rail_review_packet_path,
    ]
    return "; ".join(_display_path(path) for path in paths)


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers = [
        "rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests",
        "rail timing cache or reviewed GTFS source files are absent for timing requests",
        "retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or explicit acceptance",
    ]
    for row in rows:
        status = str(row.get("decision_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(f"{row.get('request_id', '')}: {reason}")
    return blockers


def _decision_sort_key(row: Mapping[str, str]) -> int:
    status = str(row.get("decision_status", ""))
    if status.startswith("blocked_"):
        return 0
    if status.startswith("needs_human_review_"):
        return 1
    return 2


def _review_priority(row: Mapping[str, str]) -> str:
    source_type = str(row.get("source_type", ""))
    evidence_fields = str(row.get("evidence_fields", ""))
    if source_type in {
        "public_api_key_required",
        "reviewed_static_gtfs_file_required",
        "scenario_or_public_disruption_source_required",
    }:
        return "high"
    if "headway" in evidence_fields or "travel_time" in evidence_fields:
        return "high"
    return "medium"


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip() or "blank"
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


def _dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output


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
    "DEFAULT_RAIL_SOURCE_DECISION_DOC_PATH",
    "DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH",
    "DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH",
    "RAIL_SOURCE_DECISION_COLUMNS",
    "RAIL_SOURCE_DECISION_SCOPE",
    "build_rail_source_decision_manifest",
    "build_rail_source_decision_markdown",
    "build_rail_source_decision_rows",
    "write_rail_source_decision_packet",
]
