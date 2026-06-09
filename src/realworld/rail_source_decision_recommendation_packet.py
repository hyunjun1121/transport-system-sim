"""Rail source-decision recommendation packet.

This module converts pending rail source-decision rows into conservative
reviewer recommendations. It is intentionally weaker than an action ledger:
it does not provide rail timing evidence, validate GTFS, calibrate rail
service, create publication readiness, or close formal acceptance.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)
from src.realworld.rail_source_decision_packet import (
    DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    RAIL_SOURCE_DECISION_SCOPE,
    build_rail_source_decision_rows,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_source_decision_recommendation_packet.csv"
)
DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_source_decision_recommendation_manifest.json"
)
DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "rail_source_decision_recommendation_packet.md"
)
RAIL_SOURCE_DECISION_RECOMMENDATION_SCOPE = (
    "Rail source-decision recommendation packet only; not an action ledger, not "
    "rail timing evidence, not GTFS validation, not rail-service calibration, "
    "not emergency rail availability evidence, not publication readiness, not "
    "final-study readiness, and not formal acceptance."
)
RAIL_SOURCE_DECISION_RECOMMENDATION_COLUMNS: tuple[str, ...] = (
    "request_id",
    "region_id",
    "evidence_fields",
    "current_readiness_status",
    "source_type",
    "recommendation_status",
    "recommended_treatment",
    "recommended_reviewer_choice",
    "fallback_reviewer_choice",
    "reviewer_action_prompt",
    "required_next_artifacts",
    "reason",
    "must_remain_reviewer_owned",
    "can_prepopulate_action_ledger",
    "can_support_rail_evidence_gate",
    "can_support_acceptance_gate",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
    "claim_boundary",
)


def build_rail_source_decision_recommendation_rows(
    *,
    decision_rows: Sequence[Mapping[str, str]] | None = None,
    decision_packet_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return recommendation rows derived from rail source-decision rows."""

    rows = (
        list(decision_rows)
        if decision_rows is not None
        else _read_csv_rows(decision_packet_path)
    )
    recommendations = [_recommendation_row(row) for row in rows]
    recommendations.sort(key=lambda row: (row["recommendation_status"], row["request_id"]))
    return recommendations


def write_rail_source_decision_recommendation_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_DOC_PATH,
    decision_packet_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    decision_manifest_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write recommendation CSV, manifest, and Markdown review aid."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=RAIL_SOURCE_DECISION_RECOMMENDATION_COLUMNS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in RAIL_SOURCE_DECISION_RECOMMENDATION_COLUMNS
                }
            )

    summary = build_rail_source_decision_recommendation_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        decision_packet_path=decision_packet_path,
        decision_manifest_path=decision_manifest_path,
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_rail_source_decision_recommendation_markdown(summary, rows=rows),
        doc,
    )
    return summary


def build_rail_source_decision_recommendation_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path,
    manifest_path: str | Path,
    doc_path: str | Path,
    decision_packet_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    decision_manifest_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a non-evidence manifest for recommendation rows."""

    request_ids = [str(row.get("request_id", "")).strip() for row in rows]
    empty_request_ids = sum(1 for request_id in request_ids if not request_id)
    duplicate_request_ids = sorted(
        request_id
        for request_id, count in Counter(request_ids).items()
        if request_id and count > 1
    )
    action_unsafe_count = sum(
        1
        for row in rows
        if str(row.get("can_prepopulate_action_ledger", "")).lower() != "false"
    )
    evidence_unsafe_count = sum(
        1
        for row in rows
        if str(row.get("can_support_rail_evidence_gate", "")).lower() != "false"
        or str(row.get("can_support_acceptance_gate", "")).lower() != "false"
        or str(row.get("publication_ready", "")).lower() != "false"
        or str(row.get("final_study_ready", "")).lower() != "false"
        or str(row.get("formal_acceptance_evidence", "")).lower() != "false"
    )
    reviewer_owned_count = sum(
        1
        for row in rows
        if str(row.get("must_remain_reviewer_owned", "")).lower() == "true"
    )
    treatment_counts = _counts(row.get("recommended_treatment", "") for row in rows)
    recommendation_counts = _counts(
        row.get("recommendation_status", "") for row in rows
    )
    blocked_artifact_count = sum(
        1
        for row in rows
        if row.get("recommendation_status") in {
            "blocked_missing_source_artifacts",
            "blocked_key_or_cache_gated",
            "blocked_reviewed_static_input_absent",
        }
    )
    blockers = [
        "recommendation rows are reviewer guidance only and cannot prepopulate action-ledger decisions",
        "completed action ledger remains reviewer-owned and separate from this packet",
        "rail source-decision recommendations do not create rail timing evidence, GTFS validation, rail-service calibration, publication readiness, final-study readiness, or formal acceptance",
    ]
    blockers.extend(
        f"row has empty request_id at index {index}"
        for index, request_id in enumerate(request_ids)
        if not request_id
    )
    blockers.extend(f"duplicate request_id: {request_id}" for request_id in duplicate_request_ids)
    if action_unsafe_count:
        blockers.append(
            f"{action_unsafe_count} recommendation rows can prepopulate action ledgers"
        )
    if evidence_unsafe_count:
        blockers.append(
            f"{evidence_unsafe_count} recommendation rows expose unsafe evidence/readiness flags"
        )
    if reviewer_owned_count != len(rows):
        blockers.append(
            f"{len(rows) - reviewer_owned_count} recommendation rows are not reviewer-owned"
        )

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "result_scope": RAIL_SOURCE_DECISION_RECOMMENDATION_SCOPE,
        "source_decision_scope": RAIL_SOURCE_DECISION_SCOPE,
        "row_count": len(rows),
        "request_id_count": len(set(request_id for request_id in request_ids if request_id)),
        "duplicate_request_ids": duplicate_request_ids,
        "empty_request_id_count": empty_request_ids,
        "recommendation_status_counts": recommendation_counts,
        "recommended_treatment_counts": treatment_counts,
        "blocked_artifact_count": blocked_artifact_count,
        "reviewer_owned_count": reviewer_owned_count,
        "can_prepopulate_action_ledger_count": action_unsafe_count,
        "unsafe_evidence_or_readiness_flag_count": evidence_unsafe_count,
        "publication_ready": False,
        "final_study_ready": False,
        "can_mark_complete": False,
        "can_support_rail_evidence_gate": False,
        "can_support_acceptance_gate": False,
        "formal_acceptance_evidence": False,
        "action_ledger_created": False,
        "must_remain_reviewer_owned": True,
        "rail_source_decision_recorded": False,
        "inputs": {
            "rail_source_decision_packet": _display_path(Path(decision_packet_path)),
            "rail_source_decision_manifest": _display_path(Path(decision_manifest_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "remaining_blockers": blockers,
    }


def build_rail_source_decision_recommendation_markdown(
    summary: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown documentation for the recommendation packet."""

    lines = [
        "# Rail Source Decision Recommendation Packet",
        "",
        "This packet is reviewer guidance only. It is not an action ledger, not rail timing evidence, not GTFS validation, not rail-service calibration, not emergency rail availability evidence, not publication readiness, not final-study readiness, and not formal acceptance.",
        "",
        f"- Row count: {summary.get('row_count', 0)}",
        f"- Blocked source-artifact rows: {summary.get('blocked_artifact_count', 0)}",
        f"- Reviewer-owned rows: {summary.get('reviewer_owned_count', 0)}",
        f"- Action ledger created: {str(summary.get('action_ledger_created', False)).lower()}",
        f"- Rail source decision recorded: {str(summary.get('rail_source_decision_recorded', False)).lower()}",
        f"- Can support rail evidence gate: {str(summary.get('can_support_rail_evidence_gate', False)).lower()}",
        f"- Can support acceptance gate: {str(summary.get('can_support_acceptance_gate', False)).lower()}",
        "",
        "## Recommendations",
        "",
        "| request_id | recommended_treatment | reviewer_action_prompt | recommended_reviewer_choice | fallback_reviewer_choice | reason |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                _cell(str(row.get(column, "")))
                for column in (
                    "request_id",
                    "recommended_treatment",
                    "reviewer_action_prompt",
                    "recommended_reviewer_choice",
                    "fallback_reviewer_choice",
                    "reason",
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Required Boundary",
            "",
            "- Do not copy these recommendations into an action ledger without human reviewer ownership.",
            "- Do not treat source acquisition recommendations as retained local artifacts.",
            "- Do not treat sensitivity-only or scenario-only recommendations as source-backed calibration.",
            "- Keep completed source-decision action ledgers separate from this packet.",
            "",
        ]
    )
    return "\n".join(lines)


def _recommendation_row(row: Mapping[str, str]) -> dict[str, str]:
    request_id = str(row.get("request_id", "")).strip()
    source_type = str(row.get("source_type", "")).strip()
    evidence_fields = str(row.get("evidence_fields", "")).strip()
    base = {
        "request_id": request_id,
        "region_id": str(row.get("region_id", "")).strip(),
        "evidence_fields": evidence_fields,
        "current_readiness_status": str(row.get("current_readiness_status", "")).strip(),
        "source_type": source_type,
        "must_remain_reviewer_owned": "true",
        "can_prepopulate_action_ledger": "false",
        "can_support_rail_evidence_gate": "false",
        "can_support_acceptance_gate": "false",
        "publication_ready": "false",
        "final_study_ready": "false",
        "formal_acceptance_evidence": "false",
        "claim_boundary": RAIL_SOURCE_DECISION_RECOMMENDATION_SCOPE,
    }
    recommendation = _recommendation_for(row)
    return {**base, **recommendation}


def _recommendation_for(row: Mapping[str, str]) -> dict[str, str]:
    request_id = str(row.get("request_id", "")).strip()
    source_type = str(row.get("source_type", "")).strip()
    source_cache_path = str(row.get("source_cache_path", "")).strip()
    raw_payload_path = str(row.get("raw_payload_path", "")).strip()
    current_readiness_status = str(row.get("current_readiness_status", "")).strip()

    if source_type == "reviewed_static_gtfs_file_required":
        return {
            "recommendation_status": "blocked_missing_source_artifacts",
            "recommended_treatment": "source_backed_acquisition_candidate",
            "recommended_reviewer_choice": "provide_reviewed_static_gtfs_feed",
            "fallback_reviewer_choice": "retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_final_claims",
            "reviewer_action_prompt": (
                "Retain and review the GTFS feed and same-feed Validator report, "
                "or explicitly keep/exclude timing-dependent claims."
            ),
            "required_next_artifacts": "data/rail/pilot_gtfs.zip; data/rail/pilot_gtfs_validator_report.json; matching GTFS SHA256; reviewed stop/route/service-window choices",
            "reason": "Static GTFS can support timing only after the retained feed and same-feed Validator report are reviewed and hashable.",
        }
    if source_type == "public_api_key_required":
        status = "blocked_key_or_cache_gated"
        choice = "provide_reviewed_cached_api_payload"
        reason = (
            "API-backed timing remains blocked until a DATA_GO_KR_KEY live fetch or reviewed cached payload is retained."
        )
        if "shortest_path" in request_id:
            required = f"{source_cache_path}; {raw_payload_path}; reviewed station codes; extraction date; SHA256 records"
        else:
            required = f"{source_cache_path}; {raw_payload_path}; reviewed line/direction/service-day/service-window; extraction date; SHA256 records"
        return {
            "recommendation_status": status,
            "recommended_treatment": "key_or_cache_gated_timing_acquisition",
            "recommended_reviewer_choice": choice,
            "fallback_reviewer_choice": "retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_final_claims",
            "reviewer_action_prompt": (
                "Provide retained API cache/raw payload evidence, run a reviewed "
                "live fetch, or explicitly bound/exclude timing-dependent claims."
            ),
            "required_next_artifacts": required,
            "reason": reason,
        }
    if source_type == "reviewed_static_timetable_csv_required":
        if current_readiness_status == "ready_reviewed_static_timetable_cache_for_derivation_review":
            return {
                "recommendation_status": "review_ready_static_timetable_cache",
                "recommended_treatment": "review_static_timetable_headway_cache",
                "recommended_reviewer_choice": "provide_reviewed_static_timetable_csv_and_mapping",
                "fallback_reviewer_choice": "use_reviewed_gtfs_or_alternate_timing_source; exclude_timing_dependent_final_claims",
                "reviewer_action_prompt": (
                    "Review the retained timetable CSV, explicit mapping, "
                    "normalization manifest, filters, and station binding. "
                    "Pair the derived headway with travel-time evidence before "
                    "using timing-dependent claims."
                ),
                "required_next_artifacts": (
                    f"{source_cache_path}; {raw_payload_path}; explicit column "
                    "mapping; source citation; SHA256 records; paired "
                    "shortest-path, GTFS, or matched timetable travel-time evidence"
                ),
                "reason": (
                    "A static timetable cache is present for headway review, "
                    "but it does not close travel-time evidence or rail-service "
                    "calibration by itself."
                ),
            }
        return {
            "recommendation_status": "blocked_reviewed_static_input_absent",
            "recommended_treatment": "defer_or_reviewed_static_timetable_input",
            "recommended_reviewer_choice": "provide_reviewed_static_timetable_csv_and_mapping",
            "fallback_reviewer_choice": "use_reviewed_gtfs_or_alternate_timing_source; exclude_timing_dependent_final_claims",
            "reviewer_action_prompt": (
                "Provide the reviewed timetable CSV plus mapping/normalization "
                "manifest, pair it with travel-time evidence, or exclude timing claims."
            ),
            "required_next_artifacts": "data/rail/pilot_rail_timetable_static_source.csv; data/rail/pilot_rail_timetable_cache_manifest.json; explicit column mapping; source citation; SHA256 records",
            "reason": "A static timetable CSV is useful only if the original table, mapping, filters, and normalization manifest are reviewer-owned.",
        }
    if source_type == "operator_or_literature_or_sensitivity_decision":
        return {
            "recommendation_status": "reviewer_scope_decision_required",
            "recommended_treatment": "sensitivity_only_now",
            "recommended_reviewer_choice": "retain_capacity_as_sensitivity_only_with_bounds",
            "fallback_reviewer_choice": "replace_with_operator_or_literature_capacity_source; exclude_capacity_dependent_final_claims",
            "reviewer_action_prompt": (
                "Record reviewed sensitivity-only capacity bounds and excluded "
                "claim scope, or replace the proxy with source-backed capacity evidence."
            ),
            "required_next_artifacts": "reviewed capacity source or reviewer-owned capacity bounds and excluded claim scope",
            "reason": "Cached capacity context is not enough to treat rail capacity as source-backed calibration.",
        }
    if source_type == "scenario_or_public_disruption_source_required":
        return {
            "recommendation_status": "reviewer_scope_decision_required",
            "recommended_treatment": "scenario_only_now",
            "recommended_reviewer_choice": "record_scenario_only_availability_scope",
            "fallback_reviewer_choice": "replace_with_public_disruption_or_incident_source; exclude_availability_dependent_final_claims",
            "reviewer_action_prompt": (
                "Record reviewed scenario-only availability scope, or replace it "
                "with retained public disruption/incident evidence."
            ),
            "required_next_artifacts": "reviewed scenario-only availability scope or public disruption/incident source with retained provenance",
            "reason": "Current availability treatment is a stress scenario and should not be framed as observed emergency service availability.",
        }
    return {
        "recommendation_status": "blocked_unclassified_source_type",
        "recommended_treatment": "pending_unclassified_review",
        "recommended_reviewer_choice": "pending_reviewer_decision",
        "fallback_reviewer_choice": "exclude_from_final_claims",
        "reviewer_action_prompt": (
            "Classify the source type manually before recording any source decision."
        ),
        "required_next_artifacts": "manual classification required",
        "reason": "Source type is not recognized by the recommendation packet.",
    }


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: Counter[str] = Counter(value or "unknown" for value in values)
    return dict(sorted(counts.items()))


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        return build_rail_source_decision_rows()
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_DOC_PATH",
    "DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_MANIFEST_PATH",
    "DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_PACKET_PATH",
    "RAIL_SOURCE_DECISION_RECOMMENDATION_COLUMNS",
    "RAIL_SOURCE_DECISION_RECOMMENDATION_SCOPE",
    "build_rail_source_decision_recommendation_markdown",
    "build_rail_source_decision_recommendation_manifest",
    "build_rail_source_decision_recommendation_rows",
    "write_rail_source_decision_recommendation_packet",
]
