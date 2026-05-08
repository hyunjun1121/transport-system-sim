"""Parameter source-readiness packet generation.

The cross-cutting parameter source-request worksheet names the source packages
needed for demand, fleet, dispatch, transfer, disruption, and traffic/BPR
assumptions. This module classifies those requests into concrete pre-review
states without accepting weak assumptions or changing parameter values.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.parameter_evidence_request_packet import (
    DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    PARAMETER_EVIDENCE_SOURCE_REQUEST_SCOPE,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "parameter_source_readiness_packet.csv"
)
DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "parameter_source_readiness_manifest.json"
)
DEFAULT_PARAMETER_SOURCE_READINESS_DOC_PATH = (
    PROJECT_ROOT / "docs" / "parameter_source_readiness_packet.md"
)
PARAMETER_SOURCE_READINESS_SCOPE = (
    "Parameter source-readiness packet only; not source evidence, not accepted "
    "parameter calibration, not weak-parameter acceptance, not evidence-gate "
    "closure, and not publication-readiness approval."
)
PARAMETER_SOURCE_READINESS_COLUMNS: tuple[str, ...] = (
    "request_id",
    "region_id",
    "parameter_groups",
    "covered_parameters",
    "weak_parameter_count",
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
    "acquisition_command",
    "review_or_derivation_command",
    "can_support_parameter_evidence_gate",
    "can_support_acceptance_gate",
    "claim_boundary",
    "notes",
)


def build_parameter_source_readiness_rows(
    *,
    request_rows: Sequence[Mapping[str, str]] | None = None,
    request_packet_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return source-readiness rows for parameter evidence source requests."""

    rows = (
        list(request_rows)
        if request_rows is not None
        else _load_request_rows(request_packet_path)
    )
    return [_readiness_row(row) for row in rows]


def write_parameter_source_readiness_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_DOC_PATH,
    request_packet_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
) -> dict[str, Any]:
    """Write parameter source-readiness CSV, manifest, and Markdown artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PARAMETER_SOURCE_READINESS_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in PARAMETER_SOURCE_READINESS_COLUMNS
                }
            )

    summary = build_parameter_source_readiness_manifest(
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
        build_parameter_source_readiness_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_parameter_source_readiness_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PARAMETER_SOURCE_READINESS_DOC_PATH,
    request_packet_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for parameter source-readiness rows."""

    status_counts = _counts(row.get("readiness_status", "") for row in rows)
    group_counts = _counts(row.get("parameter_groups", "") for row in rows)
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
    weak_parameter_count = sum(_int_value(row.get("weak_parameter_count", "0")) for row in rows)
    return {
        "schema_version": 1,
        "claim_boundary": (
            PARAMETER_SOURCE_READINESS_SCOPE
            + " This packet cannot close parameter evidence or formal acceptance gates."
        ),
        "result_scope": PARAMETER_SOURCE_READINESS_SCOPE,
        "row_count": len(rows),
        "weak_parameter_count": weak_parameter_count,
        "readiness_status_counts": status_counts,
        "parameter_group_counts": group_counts,
        "source_url_or_citation_present_count": source_citation_count,
        "required_external_input_present_count": external_input_count,
        "blocking_request_count": blocking_count,
        "human_review_request_count": human_review_count,
        "parameter_evidence_gate_closure_candidate_count": 0,
        "acceptance_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "parameter_evidence_source_request_packet": _display_path(
                Path(request_packet_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "replace weak demand, fleet, transfer, disruption, and traffic assumptions with reviewed sources or bounded scenario decisions",
            "update parameter_sources.csv or fleet_assumptions.csv only after source review",
            "use parameter_acceptance.csv separately for retained weak assumptions",
            "rerun parameter, publication-readiness, and final-study-readiness audits after source changes",
        ],
        "remaining_blockers": [
            "all rows require human review or external source decisions before final claims",
            "this packet is readiness evidence only and cannot create accepted parameter values",
            "parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions",
        ],
    }


def build_parameter_source_readiness_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable parameter source-readiness packet."""

    lines = [
        "# Parameter Source Readiness Packet",
        "",
        str(manifest.get("claim_boundary", PARAMETER_SOURCE_READINESS_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Request rows: {manifest.get('row_count', 0)}",
        f"- Weak parameters covered: {manifest.get('weak_parameter_count', 0)}",
        f"- Blocking requests: {manifest.get('blocking_request_count', 0)}",
        f"- Human-review requests: {manifest.get('human_review_request_count', 0)}",
        f"- Status counts: `{manifest.get('readiness_status_counts', {})}`",
        "",
        "## Readiness Rows",
        "",
        "| Request | Source | Group | Status | Source Cache | Target | Required Input | Required Action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        source_cache = (
            "present" if _is_true(row.get("source_cache_present", "")) else "absent"
        )
        target = "present" if _is_true(row.get("target_output_present", "")) else "absent"
        lines.append(
            "| {request} | {source} | {group} | {status} | {source_cache} | {target} | {input} | {action} |".format(
                request=_cell(row.get("request_id", "")),
                source=_cell(_source_summary(row)),
                group=_cell(row.get("parameter_groups", "")),
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
            "- Supply reviewed sources or explicit bounded-scenario decisions for every row.",
            "- Update parameter tables only after source review.",
            "- Use formal weak-parameter acceptance separately when assumptions remain weak.",
            "- Do not create formal acceptance artifacts from this readiness packet alone.",
            "",
        ]
    )
    return "\n".join(lines)


def _readiness_row(row: Mapping[str, str]) -> dict[str, str]:
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
    )
    return {
        "request_id": str(row.get("request_id", "")),
        "region_id": str(row.get("region_id", "")),
        "parameter_groups": str(row.get("parameter_groups", "")),
        "covered_parameters": str(row.get("covered_parameters", "")),
        "weak_parameter_count": str(row.get("weak_parameter_count", "")),
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
        "acquisition_command": str(row.get("acquisition_command", "")),
        "review_or_derivation_command": str(row.get("review_or_derivation_command", "")),
        "can_support_parameter_evidence_gate": "false",
        "can_support_acceptance_gate": "false",
        "claim_boundary": PARAMETER_SOURCE_READINESS_SCOPE,
        "notes": str(row.get("notes", "")),
    }


def _classify(
    *,
    source_type: str,
    cache_present: bool,
    raw_present: bool,
    target_present: bool,
) -> tuple[str, str, str]:
    if source_type == "planning_scenario_or_literature_source_required":
        if cache_present and target_present:
            return (
                "needs_human_review_demand_scenario",
                "",
                "review demand scale, arrival process, time horizon, and censoring penalty rationale",
            )
        return (
            "blocked_missing_demand_scenario_source",
            "demand scenario or parameter target artifact is absent",
            "supply reviewed demand/planning scenario evidence before final demand claims",
        )
    if source_type == "agency_fleet_roster_or_planning_source_required":
        if cache_present and target_present:
            return (
                "needs_human_review_fleet_package",
                "",
                "review vehicle capacities and finite fleet counts as source-backed or scenario-bounded",
            )
        return (
            "blocked_missing_fleet_source",
            "fleet assumptions or parameter target artifact is absent",
            "supply fleet roster, planning package, literature, or bounded scenario evidence",
        )
    if source_type == "operating_schedule_or_planning_rule_required":
        if cache_present and target_present:
            return (
                "needs_human_review_dispatch_policy",
                "",
                "review dispatch interval and turnaround treatment as policy scenario assumptions",
            )
        return (
            "blocked_missing_dispatch_policy_source",
            "dispatch policy source artifacts are absent",
            "supply operating-plan, staging, layover, or policy scenario evidence",
        )
    if source_type == "station_layout_or_pedestrian_flow_source_required":
        if raw_present:
            return (
                "needs_human_review_transfer_source",
                "",
                "review transfer geometry or pedestrian-flow evidence before final transfer claims",
            )
        return (
            "blocked_missing_transfer_source",
            "no station-layout, observed transfer, or pedestrian-flow source artifact is present",
            "supply transfer path, walking/crowding, field-observation, or literature evidence",
        )
    if source_type == "hazard_incident_or_scenario_rule_source_required":
        if cache_present and target_present:
            return (
                "needs_human_review_disruption_parameter_scenario",
                "",
                "review scenario-only disruption rules or replace them with hazard/incident evidence",
            )
        return (
            "blocked_missing_disruption_parameter_source",
            "disruption scenario or parameter target artifact is absent",
            "supply hazard, incident, capacity-loss, or reviewed scenario-rule evidence",
        )
    if source_type == "traffic_benchmark_or_literature_calibration_required":
        if cache_present and target_present:
            status = "needs_human_review_traffic_bpr_calibration"
            if raw_present:
                status = "needs_human_review_traffic_bpr_with_benchmark_snapshot"
            return (
                status,
                "",
                "review route benchmark, traffic-volume window, and BPR default treatment",
            )
        return (
            "blocked_missing_traffic_bpr_source",
            "traffic benchmark or parameter target artifact is absent",
            "supply traffic benchmark, observed speed/count, or BPR literature evidence",
        )
    return (
        "blocked_unclassified_source_type",
        f"unrecognized source_type {source_type!r}",
        "classify this parameter request before evidence review",
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


def _int_value(value: object) -> int:
    try:
        return int(value)
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
    "DEFAULT_PARAMETER_SOURCE_READINESS_DOC_PATH",
    "DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH",
    "DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH",
    "PARAMETER_SOURCE_READINESS_COLUMNS",
    "PARAMETER_SOURCE_READINESS_SCOPE",
    "build_parameter_source_readiness_manifest",
    "build_parameter_source_readiness_markdown",
    "build_parameter_source_readiness_rows",
    "write_parameter_source_readiness_packet",
]
