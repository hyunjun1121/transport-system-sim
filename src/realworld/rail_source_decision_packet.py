"""Rail source decision worksheet.

This module turns rail fetch-readiness rows into per-request reviewer decision
rows. It does not fetch rail data, validate GTFS, derive rail service evidence,
approve sensitivity-only rail assumptions, or close the rail evidence gate.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import date
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
DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_PATH = (
    PROJECT_ROOT
    / "data"
    / "rail"
    / "rail_source_decision_action_ledger_template.csv"
)
DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "rail"
    / "rail_source_decision_action_ledger_template_manifest.json"
)
DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "rail_source_decision_action_ledger_template.md"
)
DEFAULT_RAIL_SERVICE_EVIDENCE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "rail_service_evidence.csv"
)
RAIL_SOURCE_DECISION_SCOPE = (
    "Rail source-decision packet only; not rail timing evidence, not GTFS "
    "validation, not rail-service calibration, not emergency rail availability "
    "evidence, not sensitivity-only rail approval, and not rail evidence gate "
    "closure, not publication gate evidence, not study-closeout evidence, and "
    "not a formal decision record."
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
    "decision_scope",
    "decision_choice",
    "current_artifact_status",
    "minimum_evidence_to_acquire",
    "allowed_bounded_fallback",
    "decision_completion_output",
    "reviewer",
    "decision_date",
    "decision_basis",
    "artifact_sha256s",
    "excluded_or_retained_claim_scope",
    "not_operational_claim_boundary",
    "bounded_treatment_or_exclusion_rationale",
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
RAIL_SOURCE_DECISION_ACTION_COLUMNS: tuple[str, ...] = (
    "request_id",
    "decision_choice",
    "reviewer",
    "decision_date",
    "decision_basis",
    "artifact_sha256s",
    "excluded_or_retained_claim_scope",
    "not_operational_claim_boundary",
    "bounded_treatment_or_exclusion_rationale",
)
_ACTION_MERGE_FIELDS = set(RAIL_SOURCE_DECISION_ACTION_COLUMNS) - {"request_id"}
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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
    action_ledger_path: str | Path | None = None,
    action_rows: Sequence[Mapping[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Return one pending rail-source decision row per readiness row."""

    if action_ledger_path is not None and action_rows is not None:
        raise ValueError("provide either action_ledger_path or action_rows, not both")
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
    if action_ledger_path is not None:
        decision_rows = apply_rail_source_decision_action_ledger(
            decision_rows,
            action_rows=_read_action_ledger_rows(action_ledger_path),
        )
    elif action_rows is not None:
        decision_rows = apply_rail_source_decision_action_ledger(
            decision_rows,
            action_rows=action_rows,
        )
    decision_rows.sort(key=lambda row: (_decision_sort_key(row), row["request_id"]))
    return decision_rows


def apply_rail_source_decision_action_ledger(
    rows: Sequence[Mapping[str, str]],
    *,
    action_rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Merge non-formal reviewer action fields into generated decision rows."""

    by_request_id = {str(row.get("request_id", "")).strip(): dict(row) for row in rows}
    if "" in by_request_id:
        raise ValueError("rail source-decision rows must have non-empty request_id")
    seen: set[str] = set()
    for action_row in action_rows:
        _validate_action_row_columns(action_row)
        request_id = str(action_row.get("request_id", "")).strip()
        if not request_id:
            if any(str(value).strip() for value in action_row.values()):
                raise ValueError("action ledger row has reviewer fields but no request_id")
            continue
        if request_id in seen:
            raise ValueError(f"duplicate action ledger request_id: {request_id}")
        seen.add(request_id)
        if request_id not in by_request_id:
            raise ValueError(f"unknown action ledger request_id: {request_id}")
        merged = by_request_id[request_id]
        for field in _ACTION_MERGE_FIELDS:
            value = str(action_row.get(field, "")).strip()
            if value:
                merged[field] = value
        status, reason = _effective_decision_status_and_reason(merged)
        merged["decision_status"] = status
        if reason:
            merged["blocking_reason"] = reason
        elif status == "completed_non_formal_source_review_decision":
            merged["blocking_reason"] = ""
        by_request_id[request_id] = merged
    return [dict(row) for row in by_request_id.values()]


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


def build_rail_source_decision_action_ledger_template_rows(
    rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Return ledger-compatible action rows for reviewer completion."""

    template_rows: list[dict[str, str]] = []
    for row in rows:
        template = {column: "" for column in RAIL_SOURCE_DECISION_ACTION_COLUMNS}
        template["request_id"] = str(row.get("request_id", "")).strip()
        template["decision_choice"] = "pending_reviewer_decision"
        template_rows.append(template)
    return template_rows


def write_rail_source_decision_action_ledger_template(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_PATH,
    manifest_path: str
    | Path = DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_DOC_PATH,
) -> dict[str, Any]:
    """Write a non-formal reviewer action-ledger template."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    template_rows = build_rail_source_decision_action_ledger_template_rows(rows)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=RAIL_SOURCE_DECISION_ACTION_COLUMNS,
        )
        writer.writeheader()
        writer.writerows(template_rows)

    summary = build_rail_source_decision_action_ledger_template_manifest(
        rows=rows,
        template_rows=template_rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_rail_source_decision_action_ledger_template_markdown(
            summary,
            rows=rows,
        ),
        encoding="utf-8",
    )
    return summary


def build_rail_source_decision_action_ledger_template_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    template_rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_PATH,
    manifest_path: str
    | Path = DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_DOC_PATH,
) -> dict[str, Any]:
    """Return conservative status for the action-ledger template."""

    protected_fields = sorted(
        set(RAIL_SOURCE_DECISION_COLUMNS) - set(RAIL_SOURCE_DECISION_ACTION_COLUMNS)
    )
    return {
        "schema_version": 1,
        "result_scope": "rail_source_decision_action_ledger_template_not_acceptance",
        "claim_boundary": (
            "Template only. This CSV is a reviewer worksheet for the optional "
            "--action-ledger input. It is not rail timing evidence, not GTFS "
            "validation, not rail-service calibration, not emergency rail "
            "availability evidence, not publication gate evidence, not "
            "study-closeout evidence, and not a formal decision record."
        ),
        "template_only": True,
        "ledger_compatible": True,
        "row_count": len(template_rows),
        "source_decision_row_count": len(rows),
        "action_columns": list(RAIL_SOURCE_DECISION_ACTION_COLUMNS),
        "protected_fields_excluded": protected_fields,
        "decision_ids": [str(row.get("request_id", "")) for row in rows],
        "candidate_decision_options_by_request_id": {
            str(row.get("request_id", "")): _split_options(
                row.get("candidate_decision_options", "")
            )
            for row in rows
        },
        "decision_topics_by_request_id": {
            str(row.get("request_id", "")): str(row.get("decision_topic", ""))
            for row in rows
        },
        "current_decision_status_counts": _counts(
            _effective_decision_status(row) for row in rows
        ),
        "template_action_status_counts": _counts(
            _action_decision_status(row) for row in template_rows
        ),
        "publication_ready": False,
        "can_mark_complete": False,
        "can_support_rail_evidence_gate": False,
        "can_support_publication_gate": False,
        "can_support_final_study_gate": False,
        "can_support_acceptance_gate": False,
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "copy this template to a reviewer-owned action ledger path before editing",
            "choose exactly one listed decision_choice per request_id",
            "fill reviewer, ISO YYYY-MM-DD decision_date, decision_basis, and not_operational_claim_boundary for every non-pending row",
            "for source-backed acquisition choices, fill artifact_sha256s as path=64hex_sha256 for every source_cache_path and raw_payload_path artifact",
            "for sensitivity-only, scenario-only, or exclusion choices, fill excluded_or_retained_claim_scope and bounded_treatment_or_exclusion_rationale",
            "rerun scripts/write_rail_source_decision_packet.py --action-ledger <edited_csv> and the publication-gate/study-closeout audits after reviewer edits",
        ],
        "remaining_blockers": [
            "template rows are pending reviewer action decisions",
            "template output does not create source-backed rail evidence",
            "template output does not close publication, study-closeout, or formal decision gates",
        ],
    }


def build_rail_source_decision_action_ledger_template_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown guide for the action-ledger template."""

    lines = [
        "# Rail Source Decision Action Template",
        "",
        str(manifest.get("claim_boundary", "")),
        "",
        "## Verdict",
        "",
        f"- Template only: `{str(manifest.get('template_only', False)).lower()}`",
        f"- Ledger compatible: `{str(manifest.get('ledger_compatible', False)).lower()}`",
        f"- Publication gate supported: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Template rows: {manifest.get('row_count', 0)}",
        f"- CSV: `{manifest.get('outputs', {}).get('csv', '')}`",
        "",
        "## How To Use",
        "",
        "1. Copy the CSV to a reviewer-owned action ledger path.",
        "2. Edit only the columns present in the CSV.",
        "3. Choose exactly one listed `decision_choice` for each `request_id`.",
        "4. Use ISO `YYYY-MM-DD` format for `decision_date` on every non-pending row.",
        "5. For source-backed acquisition choices, set `artifact_sha256s` as semicolon-separated `path=64hex_sha256` entries for every retained `source_cache_path` and `raw_payload_path` artifact.",
        "6. Run `scripts/write_rail_source_decision_packet.py --action-ledger <edited_csv>`.",
        "7. Rerun publication-gate and study-closeout gate audits.",
        "",
        "## Non-Formal Example Rows",
        "",
        "These examples are guidance for a copied, reviewer-owned action ledger.",
        "Do not paste them into the generated template unless a reviewer has made",
        "the corresponding bounded-treatment decision.",
        "",
        "| request_id | example_decision_choice | required reviewer additions |",
        "| --- | --- | --- |",
        "| rail_capacity_treatment_request | retain_capacity_as_sensitivity_only_with_bounds | reviewer, decision_date, decision_basis, excluded_or_retained_claim_scope, not_operational_claim_boundary, bounded_treatment_or_exclusion_rationale |",
        "| rail_availability_scenario_request | record_scenario_only_availability_scope | reviewer, decision_date, decision_basis, excluded_or_retained_claim_scope, not_operational_claim_boundary, bounded_treatment_or_exclusion_rationale |",
        "",
        "Source-backed acquisition examples are intentionally omitted here because",
        "they require retained local source artifacts and `path=64hex_sha256`",
        "entries for every required cache/raw payload before the action row can",
        "be complete.",
        "",
        "## Decision Context",
        "",
        "| Request | Topic | Current Status | Options | Required Evidence Or Scope |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {request} | {topic} | {status} | {options} | {evidence} |".format(
                request=_cell(row.get("request_id", "")),
                topic=_cell(row.get("decision_topic", "")),
                status=_cell(_effective_decision_status(row)),
                options=_cell(row.get("candidate_decision_options", "")),
                evidence=_cell(row.get("minimum_evidence_to_acquire", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This template is not a formal decision record.",
            "- It does not fetch data, validate GTFS, derive rail service evidence, or certify rail availability.",
            "- Acquisition choices remain incomplete unless all listed local source/cache/raw artifacts exist and their SHA256 values match the action ledger.",
            "- Completed non-formal source decisions must still be checked by rail evidence, publication-gate, study-closeout, and formal-decision gates.",
            "",
        ]
    )
    return "\n".join(lines)


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

    decision_counts = _counts(_effective_decision_status(row) for row in rows)
    readiness_counts = _counts(row.get("current_readiness_status", "") for row in rows)
    source_type_counts = _counts(row.get("source_type", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if _effective_decision_status(row).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if _effective_decision_status(row).startswith("needs_human_review_")
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
    action_status_counts = _counts(_action_decision_status(row) for row in rows)
    acquisition_required_count = sum(
        1
        for row in rows
        if "acquire" in str(row.get("minimum_evidence_to_acquire", "")).lower()
        or "provide" in str(row.get("minimum_evidence_to_acquire", "")).lower()
    )
    fallback_option_count = sum(
        1
        for row in rows
        if str(row.get("allowed_bounded_fallback", "")).strip()
    )
    acquisition_decision_count = sum(
        1 for row in rows if _decision_category(row) == "acquisition"
    )
    exclusion_decision_count = sum(
        1 for row in rows if _decision_category(row) == "exclusion"
    )
    sensitivity_only_decision_count = sum(
        1 for row in rows if _decision_category(row) == "sensitivity_only"
    )
    scenario_only_decision_count = sum(
        1 for row in rows if _decision_category(row) == "scenario_only"
    )
    completed_decision_count = action_status_counts.get(
        "completed_non_formal_source_review_decision",
        0,
    )
    rail_source_decision_recorded = bool(
        rows and completed_decision_count == len(rows)
    )
    missing_decision_evidence_count = sum(
        count
        for status, count in action_status_counts.items()
        if status.startswith("incomplete_") or status.startswith("invalid_")
    )
    rail_service_evidence_artifact_present = (
        DEFAULT_RAIL_SERVICE_EVIDENCE_PATH.exists()
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
        "source_backed_acquisition_required_count": acquisition_required_count,
        "bounded_fallback_option_count": fallback_option_count,
        "action_decision_status_counts": action_status_counts,
        "acquisition_decision_count": acquisition_decision_count,
        "exclusion_decision_count": exclusion_decision_count,
        "sensitivity_only_decision_count": sensitivity_only_decision_count,
        "scenario_only_decision_count": scenario_only_decision_count,
        "invalid_action_decision_count": action_status_counts.get(
            "invalid_action_decision_choice",
            0,
        )
        + action_status_counts.get(
            "invalid_action_decision_date",
            0,
        ),
        "missing_evidence_for_non_pending_actions_count": (
            missing_decision_evidence_count
        ),
        "missing_decision_evidence_count": missing_decision_evidence_count,
        "completed_source_decision_count": completed_decision_count,
        "rail_service_evidence_artifact_present": (
            rail_service_evidence_artifact_present
        ),
        "rail_service_evidence_present": rail_service_evidence_artifact_present,
        "accepted_source_backed_rail_service_evidence": False,
        "rail_source_decision_recorded": rail_source_decision_recorded,
        "action_ledger_completion_scope": "non_formal_source_review_only",
        "completed_action_ledger_is_acceptance": False,
        "rail_service_evidence_gate_closure_candidate_count": 0,
        "acceptance_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "final_study_ready": False,
        "can_mark_complete": False,
        "can_support_publication_gate": False,
        "can_support_final_study_gate": False,
        "can_support_rail_evidence_gate": False,
        "can_support_acceptance_gate": False,
        "formal_acceptance_evidence": False,
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
            "choose source-backed rail availability evidence, reviewer-scoped scenario-only treatment, or exclusion for availability-dependent claims",
            "preserve raw payloads, cache files, extraction date, source/license review, station binding, and not-operational claim boundaries before deriving evidence",
            "for acquisition action choices, provide path=64hex_sha256 entries for every retained source_cache_path and raw_payload_path artifact",
            "rerun rail, parameter, provenance, publication-gate, and study-closeout audits after decisions are recorded",
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
        f"- Publication gate supported: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Study-closeout gate supported: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Can support publication gate: `{str(manifest.get('can_support_publication_gate', False)).lower()}`",
        f"- Can support study-closeout gate: `{str(manifest.get('can_support_final_study_gate', False)).lower()}`",
        f"- Can support rail evidence gate: `{str(manifest.get('can_support_rail_evidence_gate', False)).lower()}`",
        f"- Can support acceptance gate: `{str(manifest.get('can_support_acceptance_gate', False)).lower()}`",
        f"- Formal acceptance evidence: `{str(manifest.get('formal_acceptance_evidence', False)).lower()}`",
        f"- Completed action ledger is acceptance: `{str(manifest.get('completed_action_ledger_is_acceptance', False)).lower()}`",
        "- Proxy/scaffold rail-service artifact present for inspection: "
        f"`{str(manifest.get('rail_service_evidence_artifact_present', False)).lower()}`",
        "- Source-backed rail-service evidence approved: `false`",
        "- Artifact presence is not rail evidence acceptance or gate closure.",
        f"- Decision rows: {manifest.get('row_count', 0)}",
        f"- Blocking decisions: {manifest.get('blocking_decision_count', 0)}",
        f"- Human-review decisions: {manifest.get('human_review_decision_count', 0)}",
        f"- Timing-source decisions: {manifest.get('timing_source_decision_count', 0)}",
        f"- Completed non-formal source decisions: {manifest.get('completed_source_decision_count', 0)}",
        f"- Action decision status counts: `{manifest.get('action_decision_status_counts', {})}`",
        f"- Acquisition / exclusion / sensitivity-only / scenario-only decisions: "
        f"{manifest.get('acquisition_decision_count', 0)} / "
        f"{manifest.get('exclusion_decision_count', 0)} / "
        f"{manifest.get('sensitivity_only_decision_count', 0)} / "
        f"{manifest.get('scenario_only_decision_count', 0)}",
        "",
        "## Decision Rows",
        "",
        "| Request | Fields | Status | Source | Cache | Options | Required Action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {request} | {fields} | {status} | {source} | {cache} | {options} | {action} |".format(
                request=_cell(row.get("request_id", "")),
                fields=_cell(row.get("evidence_fields", "")),
                status=_cell(row.get("decision_status", "")),
                source=_cell(_source_summary(row)),
                cache=_cell(_cache_summary(row)),
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
            "- Action-ledger fields are non-formal source-review metadata and do not by themselves close rail evidence, parameter, provenance, publication, study-closeout, or formal decision gates.",
            "- Source-backed acquisition action rows are incomplete unless every listed local source/cache/raw artifact exists and matches the supplied SHA256.",
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
        "decision_scope": "non_formal_source_review",
        "decision_choice": "pending_reviewer_decision",
        "current_artifact_status": _current_artifact_status(row),
        "minimum_evidence_to_acquire": _minimum_evidence_to_acquire(row),
        "allowed_bounded_fallback": _allowed_bounded_fallback(row),
        "decision_completion_output": _decision_completion_output(row),
        "reviewer": "",
        "decision_date": "",
        "decision_basis": "",
        "artifact_sha256s": "",
        "excluded_or_retained_claim_scope": "",
        "not_operational_claim_boundary": (
            "not operational routing, not rail-service calibration, not a "
            "formal decision record"
        ),
        "bounded_treatment_or_exclusion_rationale": "",
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
            "limits, or exclude the affected claim from study-closeout interpretation."
        ),
        "required_evidence_fields": (
            "reviewer; ISO YYYY-MM-DD decision_date; decision_basis; evidence_paths; "
            "source_license_or_assumption_scope; extraction_date; raw_payload_path; "
            "station_binding_scope; sensitivity_or_scenario_treatment; "
            "not_operational_claim_boundary; bounded_treatment_or_exclusion_rationale"
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
    if source_type == "reviewed_static_timetable_csv_required":
        return "Reviewed static timetable CSV normalization and derivation decision"
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
            "exclude_timing_dependent_release_scope_claims",
        ]
    elif source_type == "reviewed_static_timetable_csv_required":
        options = [
            "provide_reviewed_static_timetable_csv_and_mapping",
            "pair_reviewed_static_timetable_headway_with_shortest_path_travel_time",
            "use_reviewed_gtfs_or_alternate_timing_source",
            "retain_current_timing_assumption_as_sensitivity_only",
            "exclude_timing_dependent_release_scope_claims",
        ]
    elif source_type == "reviewed_static_gtfs_file_required":
        options = [
            "provide_reviewed_static_gtfs_feed",
            "pair_reviewed_timetable_headway_with_shortest_path_travel_time",
            "use_other_reviewed_transit_timing_source",
            "retain_current_timing_assumption_as_sensitivity_only",
            "exclude_timing_dependent_release_scope_claims",
        ]
    elif source_type == "operator_or_literature_or_sensitivity_decision":
        options = [
            "replace_with_operator_or_literature_capacity_source",
            "retain_capacity_as_sensitivity_only_with_bounds",
            "exclude_capacity_dependent_release_scope_claims",
        ]
    elif source_type == "scenario_or_public_disruption_source_required":
        options = [
            "replace_with_public_disruption_or_incident_source",
            "record_scenario_only_availability_scope",
            "retain_availability_as_sensitivity_only",
            "exclude_availability_dependent_release_scope_claims",
        ]
    else:
        options = [
            "replace_with_source_backed_rail_values",
            "retain_as_sensitivity_only",
            "exclude_from_release_scope_claims",
        ]
    return "; ".join(options)


def _action_decision_status(row: Mapping[str, str]) -> str:
    choice = str(row.get("decision_choice", "")).strip()
    if not choice or choice == "pending_reviewer_decision":
        return "pending_action_decision"
    options = _option_set(row)
    if choice not in options:
        return "invalid_action_decision_choice"
    missing_common = _missing_common_decision_fields(row)
    if "decision_date" not in missing_common and not _is_iso_decision_date(
        str(row.get("decision_date", "")).strip()
    ):
        return "invalid_action_decision_date"
    category = _decision_category(row)
    if category == "acquisition":
        missing = [
            *missing_common,
            *[
                field
                for field in ("source_cache_path", "artifact_sha256s")
                if not str(row.get(field, "")).strip()
            ],
        ]
        if missing or not _source_artifact_hashes_match(row):
            return "incomplete_source_backed_acquisition_decision"
    elif category in {"exclusion", "sensitivity_only", "scenario_only"}:
        missing = [
            *missing_common,
            *[
                field
                for field in (
                    "excluded_or_retained_claim_scope",
                    "bounded_treatment_or_exclusion_rationale",
                )
                if not str(row.get(field, "")).strip()
            ],
        ]
        if missing:
            return f"incomplete_{category}_decision"
    else:
        if missing_common:
            return "incomplete_other_source_decision"
    return "completed_non_formal_source_review_decision"


def _source_artifact_hashes_match(row: Mapping[str, str]) -> bool:
    paths = _source_artifact_paths(row)
    hashes = _parse_artifact_sha256s(str(row.get("artifact_sha256s", "")))
    if not paths or not hashes:
        return False
    for path_text in paths:
        local_path = Path(path_text)
        if not local_path.is_absolute():
            local_path = PROJECT_ROOT / local_path
        if not local_path.is_file():
            return False
        actual = hashlib.sha256(local_path.read_bytes()).hexdigest().lower()
        keys = _artifact_hash_keys(path_text)
        if not any(hashes.get(key) == actual for key in keys):
            return False
    return True


def _source_artifact_paths(row: Mapping[str, str]) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for field in ("source_cache_path", "raw_payload_path"):
        for value in str(row.get(field, "")).split(";"):
            path_text = value.strip()
            if not path_text:
                continue
            normalized = _normalize_artifact_key(path_text)
            if normalized not in seen:
                seen.add(normalized)
                paths.append(path_text)
    return paths


def _parse_artifact_sha256s(value: str) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for entry in value.split(";"):
        entry = entry.strip()
        if not entry or "=" not in entry:
            continue
        key, digest = entry.split("=", 1)
        key = _normalize_artifact_key(key)
        digest = digest.strip().lower()
        if key and _SHA256_RE.match(digest):
            hashes[key] = digest
    return hashes


def _artifact_hash_keys(path_text: str) -> set[str]:
    normalized = _normalize_artifact_key(path_text)
    return {
        normalized,
        Path(normalized).name,
    }


def _normalize_artifact_key(value: str) -> str:
    return value.strip().replace("\\", "/")


def _effective_decision_status(row: Mapping[str, str]) -> str:
    status, _ = _effective_decision_status_and_reason(row)
    return status


def _effective_decision_status_and_reason(row: Mapping[str, str]) -> tuple[str, str]:
    action_status = _action_decision_status(row)
    if action_status == "pending_action_decision":
        return (
            str(row.get("decision_status", "")).strip()
            or "blocked_unclassified_rail_source_decision",
            str(row.get("blocking_reason", "")).strip(),
        )
    if action_status == "completed_non_formal_source_review_decision":
        return action_status, ""
    return action_status, f"non-formal action decision is not complete: {action_status}"


def _decision_category(row: Mapping[str, str]) -> str:
    choice = str(row.get("decision_choice", "")).strip()
    if not choice or choice == "pending_reviewer_decision":
        return "pending"
    if "exclude" in choice:
        return "exclusion"
    if "scenario_only" in choice:
        return "scenario_only"
    if "sensitivity_only" in choice:
        return "sensitivity_only"
    if (
        choice.startswith("provide_")
        or choice.startswith("run_")
        or choice.startswith("use_")
        or choice.startswith("replace_with_")
        or "source_backed" in choice
    ):
        return "acquisition"
    return "other"


def _option_set(row: Mapping[str, str]) -> set[str]:
    options = str(row.get("candidate_decision_options", "")).strip()
    if not options:
        options = _candidate_options(row)
    return {option.strip() for option in options.split(";") if option.strip()}


def _missing_common_decision_fields(row: Mapping[str, str]) -> list[str]:
    required = [
        "reviewer",
        "decision_date",
        "decision_basis",
        "not_operational_claim_boundary",
    ]
    return [field for field in required if not str(row.get(field, "")).strip()]


def _is_iso_decision_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return bool(_ISO_DATE_RE.match(value))


def _current_artifact_status(row: Mapping[str, str]) -> str:
    source_type = str(row.get("source_type", ""))
    readiness_status = str(row.get("readiness_status", ""))
    source_cache_present = str(row.get("source_cache_present", "")).lower() == "true"
    raw_payload_present = str(row.get("raw_payload_present", "")).lower() == "true"
    key_present = str(row.get("data_go_kr_key_present", "")).lower() == "true"
    if source_type == "public_api_key_required":
        if source_cache_present and raw_payload_present:
            return "cached_api_payload_present_pending_review"
        if key_present:
            return "api_key_present_live_fetch_still_requires_reviewed_cache"
        return "missing_api_key_and_reviewed_cache"
    if source_type == "reviewed_static_gtfs_file_required":
        if source_cache_present and raw_payload_present:
            return "reviewed_gtfs_and_source_context_present_pending_validation"
        if raw_payload_present:
            return "source_context_present_reviewed_gtfs_or_validator_absent"
        return "missing_reviewed_gtfs_and_validator_report"
    if source_type == "reviewed_static_timetable_csv_required":
        if source_cache_present and raw_payload_present:
            return "normalized_static_timetable_cache_present_pending_review"
        if raw_payload_present:
            return "static_timetable_source_present_normalized_cache_absent"
        return "missing_reviewed_static_timetable_csv_mapping_or_manifest"
    if source_type == "operator_or_literature_or_sensitivity_decision":
        if source_cache_present or raw_payload_present:
            return "capacity_context_present_pending_human_decision"
        return "capacity_context_absent_pending_human_decision"
    if source_type == "scenario_or_public_disruption_source_required":
        if source_cache_present:
            return "scenario_file_present_pending_availability_scope_decision"
        return "rail_availability_source_or_scenario_file_absent"
    if readiness_status.startswith("ready_"):
        return "ready_status_requires_human_decision_before_use"
    return "unclassified_artifact_status_requires_review"


def _minimum_evidence_to_acquire(row: Mapping[str, str]) -> str:
    source_type = str(row.get("source_type", ""))
    if source_type == "public_api_key_required":
        return (
            "provide reviewed API cache or run reviewed live fetch; retain raw "
            "payload, cache file, source citation, extraction date, station "
            "binding, and license/provenance review"
        )
    if source_type == "reviewed_static_gtfs_file_required":
        return (
            "provide reviewed static GTFS zip or directory plus retained GTFS "
            "Validator report, reviewed stop/route/service-window choices, "
            "source citation, extraction date, and license/provenance review"
        )
    if source_type == "reviewed_static_timetable_csv_required":
        return (
            "provide reviewed static timetable CSV, explicit source-column "
            "mapping, retained normalization manifest, reviewed station/line/"
            "direction/service-day/service-window choices, source citation, "
            "extraction date, and license/provenance review"
        )
    if source_type == "operator_or_literature_or_sensitivity_decision":
        return (
            "provide operator or literature capacity evidence, or record "
            "reviewed sensitivity-only capacity bounds with source and scope"
        )
    if source_type == "scenario_or_public_disruption_source_required":
        return (
            "provide public disruption/availability source, or record reviewed "
            "scenario-only rail availability bounds and excluded claim scope"
        )
    return (
        "provide source-backed rail evidence or record reviewed exclusion from "
        "release-scope claims"
    )


def _allowed_bounded_fallback(row: Mapping[str, str]) -> str:
    source_type = str(row.get("source_type", ""))
    if source_type in {
        "public_api_key_required",
        "reviewed_static_gtfs_file_required",
        "reviewed_static_timetable_csv_required",
    }:
        return (
            "retain timing as sensitivity-only with explicit bounds, or exclude "
            "timing-dependent release-scope claims"
        )
    if source_type == "operator_or_literature_or_sensitivity_decision":
        return (
            "retain capacity as sensitivity-only with explicit bounds, or "
            "exclude capacity-dependent release-scope claims"
        )
    if source_type == "scenario_or_public_disruption_source_required":
        return (
            "retain availability as scenario-only or sensitivity-only, or "
            "exclude availability-dependent release-scope claims"
        )
    return "exclude unsupported rail-dependent release-scope claims"


def _decision_completion_output(row: Mapping[str, str]) -> str:
    source_type = str(row.get("source_type", ""))
    if source_type in {
        "public_api_key_required",
        "reviewed_static_gtfs_file_required",
        "reviewed_static_timetable_csv_required",
    }:
        return (
            "reviewed cache and derived rail_service_evidence row, or recorded "
            "timing exclusion/sensitivity-only decision"
        )
    if source_type == "operator_or_literature_or_sensitivity_decision":
        return (
            "reviewed capacity evidence row, parameter acceptance decision, or "
            "recorded sensitivity-only/exclusion decision"
        )
    if source_type == "scenario_or_public_disruption_source_required":
        return (
            "reviewed availability evidence row, scenario-only decision, or "
            "recorded exclusion decision"
        )
    return "reviewed rail source decision or recorded exclusion decision"


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
    if str(row.get("source_type", "")) == "reviewed_static_timetable_csv_required":
        values.append("scripts/normalize_rail_timetable_cache.py")
    return "; ".join(_dedupe(value for value in values if str(value).strip()))


def _can_support_timing_after_review(row: Mapping[str, str]) -> bool:
    source_type = str(row.get("source_type", ""))
    fields = str(row.get("evidence_fields", ""))
    return source_type in {
        "public_api_key_required",
        "reviewed_static_gtfs_file_required",
        "reviewed_static_timetable_csv_required",
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
    blockers: list[str] = []
    action_statuses = [_action_decision_status(row) for row in rows]
    if any(status == "pending_action_decision" for status in action_statuses):
        blockers.append(
            "rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests"
        )
    if any(
        status
        not in {
            "pending_action_decision",
            "completed_non_formal_source_review_decision",
        }
        for status in action_statuses
    ):
        blockers.append(
            "rail source decisions include invalid or incomplete non-formal action rows"
        )
    blockers.extend(
        [
            "rail timing cache or reviewed GTFS source files remain required for source-backed timing claims",
            "retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment",
            "non-formal source decisions do not close rail evidence, publication, study-closeout, or formal decision gates",
        ]
    )
    for row in rows:
        action_status = _action_decision_status(row)
        if action_status not in {
            "pending_action_decision",
            "completed_non_formal_source_review_decision",
        }:
            blockers.append(f"{row.get('request_id', '')}: {action_status}")
        status = _effective_decision_status(row)
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(f"{row.get('request_id', '')}: {reason}")
    return blockers


def _decision_sort_key(row: Mapping[str, str]) -> int:
    status = _effective_decision_status(row)
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


def _read_action_ledger_rows(path: str | Path) -> list[dict[str, str]]:
    return _read_csv_rows(path)


def _validate_action_row_columns(row: Mapping[str, str]) -> None:
    for key, value in row.items():
        if key in RAIL_SOURCE_DECISION_ACTION_COLUMNS:
            continue
        if str(value).strip():
            raise ValueError(
                "action ledger may only set non-formal reviewer fields; "
                f"unexpected field with value: {key}"
            )


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


def _split_options(value: object) -> list[str]:
    return [option.strip() for option in str(value).split(";") if option.strip()]


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _cell(value: object) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    return text or "-"


def _source_summary(row: Mapping[str, str]) -> str:
    name = str(row.get("source_name", "")).strip()
    citation = str(row.get("source_url_or_citation", "")).strip()
    if name and citation:
        return f"{name}; {citation}"
    return name or citation


def _cache_summary(row: Mapping[str, str]) -> str:
    cache_state = (
        "present"
        if str(row.get("source_cache_present", "")).strip().lower() == "true"
        else "absent"
    )
    paths = [str(row.get("source_cache_path", "")).strip()]
    raw_path = str(row.get("raw_payload_path", "")).strip()
    if raw_path:
        raw_state = (
            "present"
            if str(row.get("raw_payload_present", "")).strip().lower() == "true"
            else "absent"
        )
        paths.append(f"raw {raw_state}: {raw_path}")
    path_text = "; ".join(path for path in paths if path) or "no cache path named"
    return f"{cache_state}: {path_text}"


__all__ = [
    "DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_DOC_PATH",
    "DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_MANIFEST_PATH",
    "DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_PATH",
    "DEFAULT_RAIL_SOURCE_DECISION_DOC_PATH",
    "DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH",
    "DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH",
    "RAIL_SOURCE_DECISION_ACTION_COLUMNS",
    "RAIL_SOURCE_DECISION_COLUMNS",
    "RAIL_SOURCE_DECISION_SCOPE",
    "apply_rail_source_decision_action_ledger",
    "build_rail_source_decision_action_ledger_template_manifest",
    "build_rail_source_decision_action_ledger_template_markdown",
    "build_rail_source_decision_action_ledger_template_rows",
    "build_rail_source_decision_manifest",
    "build_rail_source_decision_markdown",
    "build_rail_source_decision_rows",
    "write_rail_source_decision_action_ledger_template",
    "write_rail_source_decision_packet",
]
