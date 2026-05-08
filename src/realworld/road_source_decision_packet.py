"""Road source decision worksheet.

This module turns road source-readiness rows into per-request reviewer
decision rows. It does not update road defaults, create
``road_class_overrides.csv``, certify source sufficiency, or close the cached
OSM input gate.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.road_evidence_priority_packet import (
    DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
)
from src.realworld.road_evidence_request_packet import (
    DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
)
from src.realworld.road_evidence_review_packet import (
    DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
)
from src.realworld.road_override_audit import DEFAULT_ROAD_CLASS_OVERRIDE_PATH
from src.realworld.road_source_readiness_packet import (
    DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_SOURCE_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_source_decision_packet.csv"
)
DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_source_decision_manifest.json"
)
DEFAULT_ROAD_SOURCE_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "road_source_decision_packet.md"
)
ROAD_SOURCE_DECISION_SCOPE = (
    "Road source-decision packet only; not road evidence, not accepted road "
    "calibration, not reviewed road-class override approval, not cached OSM "
    "input gate closure, and not publication-readiness approval."
)
ROAD_SOURCE_DECISION_COLUMNS: tuple[str, ...] = (
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
    "target_output_path",
    "target_output_present",
    "required_reviewer_action",
    "required_evidence_fields",
    "followup_artifacts",
    "evidence_input_paths",
    "target_override_artifact",
    "can_support_road_evidence_gate",
    "can_support_road_application_gate",
    "can_support_acceptance_gate",
    "claim_boundary",
)


def build_road_source_decision_rows(
    *,
    readiness_rows: Sequence[Mapping[str, str]] | None = None,
    readiness_packet_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
    readiness_manifest_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    priority_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
    priority_manifest_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    road_review_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    source_request_packet_path: str
    | Path = DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return one pending road-source decision row per readiness row."""

    rows = (
        list(readiness_rows)
        if readiness_rows is not None
        else _read_csv_rows(readiness_packet_path)
    )
    evidence_paths = _evidence_paths(
        readiness_packet_path=readiness_packet_path,
        readiness_manifest_path=readiness_manifest_path,
        priority_packet_path=priority_packet_path,
        priority_manifest_path=priority_manifest_path,
        road_review_packet_path=road_review_packet_path,
        source_request_packet_path=source_request_packet_path,
    )
    decision_rows = [_decision_row(row, evidence_paths=evidence_paths) for row in rows]
    decision_rows.sort(key=lambda row: (_decision_sort_key(row), row["request_id"]))
    return decision_rows


def write_road_source_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_SOURCE_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_ROAD_SOURCE_DECISION_DOC_PATH,
    readiness_packet_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
    readiness_manifest_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    priority_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
    priority_manifest_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    road_review_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    source_request_packet_path: str
    | Path = DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
) -> dict[str, Any]:
    """Write road-source decision CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROAD_SOURCE_DECISION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in ROAD_SOURCE_DECISION_COLUMNS
                }
            )

    summary = build_road_source_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        readiness_packet_path=readiness_packet_path,
        readiness_manifest_path=readiness_manifest_path,
        priority_packet_path=priority_packet_path,
        priority_manifest_path=priority_manifest_path,
        road_review_packet_path=road_review_packet_path,
        source_request_packet_path=source_request_packet_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_road_source_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_road_source_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_SOURCE_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_ROAD_SOURCE_DECISION_DOC_PATH,
    readiness_packet_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
    readiness_manifest_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    priority_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
    priority_manifest_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    road_review_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    source_request_packet_path: str
    | Path = DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for road-source decisions."""

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
    return {
        "schema_version": 1,
        "result_scope": ROAD_SOURCE_DECISION_SCOPE,
        "claim_boundary": (
            ROAD_SOURCE_DECISION_SCOPE
            + " It cannot create data/parameters/road_class_overrides.csv."
        ),
        "row_count": len(rows),
        "region_ids": _region_ids(rows),
        "decision_ids": [str(row.get("request_id", "")) for row in rows],
        "decision_status_counts": decision_counts,
        "readiness_status_counts": readiness_counts,
        "source_type_counts": source_type_counts,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "road_class_overrides_present": DEFAULT_ROAD_CLASS_OVERRIDE_PATH.exists(),
        "road_source_decision_recorded": False,
        "cached_osm_input_gate_closure_candidate_count": 0,
        "road_evidence_gate_closure_candidate_count": 0,
        "road_application_gate_closure_candidate_count": 0,
        "acceptance_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "road_source_readiness_packet": _display_path(readiness_packet_path),
            "road_source_readiness_manifest": _display_path(readiness_manifest_path),
            "road_evidence_priority_packet": _display_path(priority_packet_path),
            "road_evidence_priority_manifest": _display_path(priority_manifest_path),
            "road_evidence_review_packet": _display_path(road_review_packet_path),
            "road_evidence_source_request_packet": _display_path(
                source_request_packet_path
            ),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "choose source-backed update, reviewed road-class override, sensitivity-only treatment, benchmark-only treatment, or exclusion for every road-source request",
            "record reviewer, decision date, evidence paths, source class, override scope, and not-operational claim limits outside this packet",
            "create data/parameters/road_class_overrides.csv only after source-backed road evidence review",
            "rerun pilot outputs with reviewed overrides before road-calibration or cached-OSM input claims",
            "rerun road, validation, publication-readiness, and final-study audits after decisions are recorded",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_road_source_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for the road-source decision worksheet."""

    lines = [
        "# Road Source Decision Packet",
        "",
        str(manifest.get("claim_boundary", ROAD_SOURCE_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Road-class overrides present: `{str(manifest.get('road_class_overrides_present', False)).lower()}`",
        f"- Decision rows: {manifest.get('row_count', 0)}",
        f"- Blocking decisions: {manifest.get('blocking_decision_count', 0)}",
        f"- Human-review decisions: {manifest.get('human_review_decision_count', 0)}",
        "",
        "## Decision Rows",
        "",
        "| Request | Status | Options | Target | Required Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {request} | {status} | {options} | {target} | {action} |".format(
                request=_cell(row.get("request_id", "")),
                status=_cell(row.get("decision_status", "")),
                options=_cell(row.get("candidate_decision_options", "")),
                target=_cell(row.get("target_output_path", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is a reviewer worksheet, not a formal decision record.",
            "- It does not create reviewed overrides, apply overrides, calibrate road inputs, or accept cached OSM input claims.",
            "- Keep road and cached-input claims blocked until source-backed changes or formal acceptance exist.",
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
        decision_status = "blocked_missing_road_source_decision"
    elif readiness_status.startswith("needs_human_review_"):
        decision_status = "needs_human_review_road_source_decision"
    else:
        decision_status = "blocked_unclassified_road_source_decision"
    blocking_reason = str(row.get("blocking_reason", "")).strip()
    if not blocking_reason and decision_status.startswith("blocked_"):
        blocking_reason = "road source decision is not classified"
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
        "target_output_path": str(row.get("target_output_path", "")),
        "target_output_present": str(row.get("target_output_present", "")),
        "required_reviewer_action": (
            "Choose whether to replace with source-backed road evidence, create "
            "reviewed road-class overrides, retain the value as sensitivity-only "
            "or benchmark-only, or exclude the affected claim from final-study "
            "interpretation."
        ),
        "required_evidence_fields": (
            "reviewer; decision_date; decision_basis; evidence_paths; "
            "source_class; affected_highway_classes; override_or_sensitivity_scope; "
            "not_operational_claim_boundary; acceptance_or_exclusion_rationale"
        ),
        "followup_artifacts": _followup_artifacts(row),
        "evidence_input_paths": evidence_paths,
        "target_override_artifact": _display_path(DEFAULT_ROAD_CLASS_OVERRIDE_PATH),
        "can_support_road_evidence_gate": "false",
        "can_support_road_application_gate": "false",
        "can_support_acceptance_gate": "false",
        "claim_boundary": ROAD_SOURCE_DECISION_SCOPE,
    }


def _decision_topic(row: Mapping[str, str]) -> str:
    source_type = str(row.get("source_type", ""))
    if "speed" in source_type:
        return "Road speed source or fallback treatment"
    if "capacity" in source_type:
        return "Road capacity source or sensitivity treatment"
    if "benchmark" in source_type:
        return "Route benchmark and background-traffic treatment"
    if "hazard" in source_type:
        return "Road disruption source or scenario treatment"
    if "override" in source_type:
        return "Reviewed road-class override and application decision"
    return "Road source or assumption treatment"


def _candidate_options(row: Mapping[str, str]) -> str:
    source_type = str(row.get("source_type", ""))
    if source_type == "public_speed_limit_or_benchmark_source_required":
        options = [
            "replace_with_source_backed_speed_values",
            "accept_fallback_speed_assumption_with_scope",
            "retain_speed_as_sensitivity_only",
            "exclude_speed_dependent_final_claims",
        ]
    elif source_type == "traffic_count_or_capacity_reference_required":
        options = [
            "replace_with_traffic_count_or_capacity_reference",
            "create_reviewed_capacity_override_assumption",
            "retain_capacity_as_sensitivity_only",
            "exclude_capacity_dependent_final_claims",
        ]
    elif source_type == "routing_or_observed_traffic_benchmark_required":
        options = [
            "keep_benchmark_as_plausibility_only",
            "use_benchmark_calibrated_background_traffic_with_limits",
            "collect_observed_traffic_source",
            "retain_background_traffic_as_sensitivity_only",
        ]
    elif source_type == "hazard_incident_or_reviewed_scenario_source_required":
        options = [
            "replace_with_hazard_or_incident_source",
            "accept_scenario_only_disruption_with_scope",
            "retain_disruption_as_sensitivity_only",
            "exclude_disruption_probability_final_claims",
        ]
    elif source_type == "reviewed_override_table_and_manifest_application_required":
        options = [
            "create_reviewed_road_class_overrides",
            "rerun_pilot_with_reviewed_overrides",
            "retain_current_mapper_defaults_as_sensitivity_only",
            "exclude_road_calibration_final_claims",
        ]
    else:
        options = [
            "replace_with_source_backed_road_values",
            "retain_as_sensitivity_only",
            "exclude_from_final_claims",
        ]
    return "; ".join(options)


def _followup_artifacts(row: Mapping[str, str]) -> str:
    values = [
        str(row.get("target_output_path", "")),
        _display_path(DEFAULT_ROAD_CLASS_OVERRIDE_PATH),
        "results/realworld_pilot/pilot_full_manifest.json",
        "data/manifests/validation_acceptance.json",
    ]
    source_type = str(row.get("source_type", ""))
    if source_type == "routing_or_observed_traffic_benchmark_required":
        values.append("data/parameters/parameter_sources.csv")
    return "; ".join(value for value in values if value)


def _evidence_paths(
    *,
    readiness_packet_path: str | Path,
    readiness_manifest_path: str | Path,
    priority_packet_path: str | Path,
    priority_manifest_path: str | Path,
    road_review_packet_path: str | Path,
    source_request_packet_path: str | Path,
) -> str:
    paths = [
        readiness_packet_path,
        readiness_manifest_path,
        priority_packet_path,
        priority_manifest_path,
        road_review_packet_path,
        source_request_packet_path,
    ]
    return "; ".join(_display_path(path) for path in paths)


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers = [
        "reviewed road_class_overrides.csv is absent",
        "road source decisions are pending for speed, capacity, disruption, benchmark, and override-application requests",
        "retained road assumptions require source-backed updates, sensitivity-only limits, benchmark-only limits, or explicit acceptance",
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
    request_id = str(row.get("request_id", ""))
    if request_id in {
        "road_capacity_lane_count_source_request",
        "road_disruption_probability_source_request",
        "reviewed_road_class_override_application_request",
    }:
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
    "DEFAULT_ROAD_SOURCE_DECISION_DOC_PATH",
    "DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH",
    "DEFAULT_ROAD_SOURCE_DECISION_PACKET_PATH",
    "ROAD_SOURCE_DECISION_COLUMNS",
    "ROAD_SOURCE_DECISION_SCOPE",
    "build_road_source_decision_manifest",
    "build_road_source_decision_markdown",
    "build_road_source_decision_rows",
    "write_road_source_decision_packet",
]
