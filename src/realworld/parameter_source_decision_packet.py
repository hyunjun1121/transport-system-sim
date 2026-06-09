"""Parameter source decision worksheet.

This module turns parameter source-readiness rows into per-request reviewer
decision rows. It does not update parameter values, certify evidence, create
``parameter_acceptance.csv``, or close the parameter evidence gate.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.parameter_acceptance import DEFAULT_PARAMETER_ACCEPTANCE_PATH
from src.realworld.parameter_evidence_priority_packet import (
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
)
from src.realworld.parameter_review_packet import DEFAULT_PARAMETER_REVIEW_PACKET_PATH
from src.realworld.parameter_source_readiness_packet import (
    DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "parameter_source_decision_packet.csv"
)
DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "parameter_source_decision_manifest.json"
)
DEFAULT_PARAMETER_SOURCE_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "parameter_source_decision_packet.md"
)
PARAMETER_SOURCE_DECISION_SCOPE = (
    "Parameter source-decision packet only; not source evidence, not approved "
    "parameter fitting, not weak-parameter decision evidence, not parameter "
    "evidence gate closure, and not publication gate approval."
)
PARAMETER_SOURCE_DECISION_COLUMNS: tuple[str, ...] = (
    "request_id",
    "region_id",
    "parameter_groups",
    "covered_parameters",
    "weak_parameter_count",
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
    "target_output_path",
    "target_output_present",
    "required_reviewer_action",
    "required_evidence_fields",
    "followup_artifacts",
    "evidence_input_paths",
    "target_acceptance_artifact",
    "can_support_parameter_evidence_gate",
    "can_support_acceptance_gate",
    "claim_boundary",
)


def build_parameter_source_decision_rows(
    *,
    readiness_rows: Sequence[Mapping[str, str]] | None = None,
    readiness_packet_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
    readiness_manifest_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    priority_packet_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
    priority_manifest_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    parameter_review_packet_path: str | Path = DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return one pending parameter-source decision row per readiness row."""

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
        parameter_review_packet_path=parameter_review_packet_path,
    )
    decision_rows = [_decision_row(row, evidence_paths=evidence_paths) for row in rows]
    decision_rows.sort(key=lambda row: (_decision_sort_key(row), row["request_id"]))
    return decision_rows


def write_parameter_source_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PARAMETER_SOURCE_DECISION_DOC_PATH,
    readiness_packet_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
    readiness_manifest_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    priority_packet_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
    priority_manifest_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    parameter_review_packet_path: str | Path = DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Write parameter-source decision CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PARAMETER_SOURCE_DECISION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in PARAMETER_SOURCE_DECISION_COLUMNS
                }
            )

    summary = build_parameter_source_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        readiness_packet_path=readiness_packet_path,
        readiness_manifest_path=readiness_manifest_path,
        priority_packet_path=priority_packet_path,
        priority_manifest_path=priority_manifest_path,
        parameter_review_packet_path=parameter_review_packet_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_parameter_source_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_parameter_source_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PARAMETER_SOURCE_DECISION_DOC_PATH,
    readiness_packet_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
    readiness_manifest_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    priority_packet_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
    priority_manifest_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    parameter_review_packet_path: str | Path = DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for parameter-source decisions."""

    decision_counts = _counts(row.get("decision_status", "") for row in rows)
    readiness_counts = _counts(row.get("current_readiness_status", "") for row in rows)
    group_counts = _counts(row.get("parameter_groups", "") for row in rows)
    weak_parameter_count = sum(
        _int_value(row.get("weak_parameter_count", "0")) for row in rows
    )
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
        "result_scope": PARAMETER_SOURCE_DECISION_SCOPE,
        "claim_boundary": (
            PARAMETER_SOURCE_DECISION_SCOPE
            + " It cannot create data/parameters/parameter_acceptance.csv."
        ),
        "row_count": len(rows),
        "region_ids": _region_ids(rows),
        "weak_parameter_count": weak_parameter_count,
        "decision_ids": [str(row.get("request_id", "")) for row in rows],
        "decision_status_counts": decision_counts,
        "readiness_status_counts": readiness_counts,
        "parameter_group_counts": group_counts,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "parameter_acceptance_present": DEFAULT_PARAMETER_ACCEPTANCE_PATH.exists(),
        "parameter_source_decision_recorded": False,
        "parameter_evidence_gate_closure_candidate_count": 0,
        "acceptance_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "parameter_source_readiness_packet": _display_path(readiness_packet_path),
            "parameter_source_readiness_manifest": _display_path(readiness_manifest_path),
            "parameter_evidence_priority_packet": _display_path(priority_packet_path),
            "parameter_evidence_priority_manifest": _display_path(priority_manifest_path),
            "parameter_evidence_review_packet": _display_path(parameter_review_packet_path),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "choose source-backed update, bounded scenario assumption, sensitivity-only treatment, or exclusion for every weak parameter group",
            "record reviewer, decision date, evidence paths, sensitivity treatment, and not-operational claim limits outside this packet",
            "update parameter source tables only after source review",
            "create data/parameters/parameter_acceptance.csv only if retained weak assumptions receive explicit reviewer decisions",
            "rerun parameter, publication, and study-closeout audits after decisions are recorded",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_parameter_source_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for the parameter-source decision worksheet."""

    lines = [
        "# Parameter Source Decision Packet",
        "",
        str(manifest.get("claim_boundary", PARAMETER_SOURCE_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Parameter acceptance present: `{str(manifest.get('parameter_acceptance_present', False)).lower()}`",
        f"- Decision rows: {manifest.get('row_count', 0)}",
        f"- Weak parameters covered: {manifest.get('weak_parameter_count', 0)}",
        f"- Blocking decisions: {manifest.get('blocking_decision_count', 0)}",
        f"- Human-review decisions: {manifest.get('human_review_decision_count', 0)}",
        "",
        "## Decision Rows",
        "",
        "| Request | Group | Status | Options | Required Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {request} | {group} | {status} | {options} | {action} |".format(
                request=_cell(row.get("request_id", "")),
                group=_cell(row.get("parameter_groups", "")),
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
            "- It does not update parameter tables or accept weak assumptions.",
            "- Keep release-scope parameter claims blocked until source-backed changes or formal weak-parameter decisions exist.",
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
    target_present = str(row.get("target_output_present", "")).lower() == "true"
    if readiness_status.startswith("blocked_"):
        decision_status = "blocked_missing_parameter_source_decision"
    elif readiness_status.startswith("needs_human_review_"):
        decision_status = "needs_human_review_parameter_source_decision"
    else:
        decision_status = "blocked_unclassified_parameter_source_decision"
    blocking_reason = str(row.get("blocking_reason", "")).strip()
    if not blocking_reason and decision_status.startswith("blocked_"):
        blocking_reason = "parameter source decision is not classified"
    return {
        "request_id": str(row.get("request_id", "")),
        "region_id": str(row.get("region_id", "")),
        "parameter_groups": str(row.get("parameter_groups", "")),
        "covered_parameters": str(row.get("covered_parameters", "")),
        "weak_parameter_count": str(row.get("weak_parameter_count", "")),
        "review_priority": _review_priority(row),
        "current_readiness_status": readiness_status,
        "decision_topic": "Parameter source, bounded scenario, or sensitivity treatment",
        "candidate_decision_options": _candidate_options(row),
        "provisional_decision": "pending_reviewer_decision",
        "decision_status": decision_status,
        "blocking_reason": blocking_reason,
        "source_type": str(row.get("source_type", "")),
        "source_name": str(row.get("source_name", "")),
        "source_url_or_citation": str(row.get("source_url_or_citation", "")),
        "target_output_path": str(row.get("target_output_path", "")),
        "target_output_present": str(target_present).lower(),
        "required_reviewer_action": (
            "Choose whether to replace with source-backed values, retain as a "
            "bounded scenario assumption, retain as sensitivity-only, or exclude "
            "the affected claim from release-scope interpretation."
        ),
        "required_evidence_fields": (
            "reviewer; decision_date; decision_basis; evidence_paths; "
            "source_or_assumption_scope; sensitivity_treatment; "
            "not_operational_claim_boundary; acceptance_or_exclusion_rationale"
        ),
        "followup_artifacts": _followup_artifacts(row),
        "evidence_input_paths": evidence_paths,
        "target_acceptance_artifact": _display_path(DEFAULT_PARAMETER_ACCEPTANCE_PATH),
        "can_support_parameter_evidence_gate": "false",
        "can_support_acceptance_gate": "false",
        "claim_boundary": PARAMETER_SOURCE_DECISION_SCOPE,
    }


def _candidate_options(row: Mapping[str, str]) -> str:
    options = [
        "replace_with_source_backed_parameter_values",
        "retain_as_bounded_scenario_assumption",
        "retain_as_sensitivity_only",
        "exclude_from_release_scope_claims",
    ]
    group = str(row.get("parameter_groups", ""))
    if group == "transfer":
        options.insert(1, "supply_transfer_layout_or_pedestrian_flow_source")
    if group == "rail":
        options.insert(1, "use_rail_timing_or_gtfs_source_decision_packet")
    return "; ".join(options)


def _followup_artifacts(row: Mapping[str, str]) -> str:
    values = [
        str(row.get("target_output_path", "")),
        _display_path(DEFAULT_PARAMETER_ACCEPTANCE_PATH),
        "data/parameters/parameter_sources.csv",
    ]
    if str(row.get("parameter_groups", "")) == "fleet":
        values.append("data/parameters/fleet_assumptions.csv")
    if str(row.get("parameter_groups", "")) == "rail":
        values.extend(
            [
                "data/rail/rail_source_decision_packet.csv",
                "data/parameters/rail_evidence_review_packet.csv",
                "data/rail/metro9_capacity_source_extract.csv",
                "data/rail/metro9_capacity_source_raw.html",
            ]
        )
    return "; ".join(value for value in values if value)


def _evidence_paths(
    *,
    readiness_packet_path: str | Path,
    readiness_manifest_path: str | Path,
    priority_packet_path: str | Path,
    priority_manifest_path: str | Path,
    parameter_review_packet_path: str | Path,
) -> str:
    paths = [
        readiness_packet_path,
        readiness_manifest_path,
        priority_packet_path,
        priority_manifest_path,
        parameter_review_packet_path,
    ]
    return "; ".join(_display_path(path) for path in paths)


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers = [
        "formal parameter acceptance table is absent",
        "parameter source decisions are pending for weak parameter groups",
        "retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance",
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
    groups = str(row.get("parameter_groups", ""))
    if groups in {"transfer", "rail", "disruption", "road"}:
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


def _int_value(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


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
    "DEFAULT_PARAMETER_SOURCE_DECISION_DOC_PATH",
    "DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH",
    "DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH",
    "PARAMETER_SOURCE_DECISION_COLUMNS",
    "PARAMETER_SOURCE_DECISION_SCOPE",
    "build_parameter_source_decision_manifest",
    "build_parameter_source_decision_markdown",
    "build_parameter_source_decision_rows",
    "write_parameter_source_decision_packet",
]
