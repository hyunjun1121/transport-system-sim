"""Rail bounded-treatment consistency audit.

This module cross-checks rail source-decision rows against rail/transit
stress-profile rows for bounded capacity and availability treatments. It is a
review aid only. It does not validate rail service, accept capacity or
availability assumptions, derive rail evidence, or close any readiness gate.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.rail_source_decision_packet import (
    DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
)
from src.realworld.rail_transit_stress_profile_packet import (
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_bounded_treatment_audit.json"
)
DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_DOC_PATH = (
    PROJECT_ROOT / "docs" / "rail_bounded_treatment_audit.md"
)
RAIL_BOUNDED_TREATMENT_AUDIT_SCOPE = (
    "Rail bounded-treatment consistency audit only; cross-artifact mismatch "
    "check between rail source-decision rows and stress-profile rows, not rail "
    "capacity evidence, not rail availability evidence, not rail-service "
    "calibration, not operational service planning, and not formal acceptance."
)
CAPACITY_REQUEST_ID = "rail_capacity_treatment_request"
AVAILABILITY_REQUEST_ID = "rail_availability_scenario_request"
GATE_FIELDS = (
    "publication_ready",
    "can_mark_complete",
    "can_support_rail_evidence_gate",
    "can_support_acceptance_gate",
)
LINKED_ARTIFACT_KEY_COLUMNS = {
    "policy_alternatives.csv": "policy_id",
    "disruption_scenarios.csv": "scenario_id",
    "sensitivity_design.csv": "parameter_id",
    "rail_service_evidence.csv": "evidence_id",
}


def build_rail_bounded_treatment_audit(
    *,
    source_decision_rows: Sequence[Mapping[str, str]] | None = None,
    stress_profile_rows: Sequence[Mapping[str, str]] | None = None,
    source_decision_path: str | Path = DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    stress_profile_path: str | Path = DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH,
) -> dict[str, Any]:
    """Return a non-acceptance audit of bounded rail treatments."""

    source_rows = (
        list(source_decision_rows)
        if source_decision_rows is not None
        else _read_csv_rows(source_decision_path)
    )
    stress_rows = (
        list(stress_profile_rows)
        if stress_profile_rows is not None
        else _read_csv_rows(stress_profile_path)
    )
    row_results = [
        _capacity_result(source_rows, stress_rows),
        _availability_result(source_rows, stress_rows),
    ]
    mismatch_count = sum(1 for result in row_results if result["status"] == "mismatch")
    warning_count = sum(len(result["warnings"]) for result in row_results)
    unchecked_pending_decision_count = sum(
        1
        for result in row_results
        if result["decision_status"] in {
            "blocked_missing_rail_source_decision",
            "needs_human_review_rail_source_decision",
        }
        or result["decision_choice"] == "pending_reviewer_decision"
    )
    return {
        "schema_version": 1,
        "audit_scope": RAIL_BOUNDED_TREATMENT_AUDIT_SCOPE,
        "claim_boundary": (
            RAIL_BOUNDED_TREATMENT_AUDIT_SCOPE
            + " It can identify internal consistency gaps but cannot turn "
            "scenario-only or sensitivity-only rows into accepted evidence."
        ),
        "source_decision_input": _display_path(source_decision_path),
        "stress_profile_input": _display_path(stress_profile_path),
        "row_count": len(row_results),
        "mismatch_count": mismatch_count,
        "warning_count": warning_count,
        "unchecked_pending_decision_count": unchecked_pending_decision_count,
        "publication_ready": False,
        "can_mark_complete": False,
        "can_support_rail_evidence_gate": False,
        "can_support_acceptance_gate": False,
        "audit_verdict": "mismatch" if mismatch_count else "bounded_review_support_only",
        "results": row_results,
        "remaining_blockers": [
            "rail bounded-treatment audit is consistency review support only",
            "capacity and availability still require reviewer source decisions before final claims",
            "stress-profile coverage does not certify rail service, emergency availability, or capacity evidence",
            *[
                f"{result['request_id']}: {blocker}"
                for result in row_results
                for blocker in result["blockers"]
            ],
        ],
    }


def write_rail_bounded_treatment_audit(
    *,
    audit: Mapping[str, Any],
    output_path: str | Path = DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH,
    doc_path: str | Path = DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_DOC_PATH,
) -> dict[str, Any]:
    """Write audit JSON and Markdown documentation."""

    output = Path(output_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    doc.write_text(build_rail_bounded_treatment_markdown(audit), encoding="utf-8")
    return dict(audit)


def build_rail_bounded_treatment_markdown(audit: Mapping[str, Any]) -> str:
    """Return Markdown documentation for the bounded-treatment audit."""

    lines = [
        "# Rail Bounded Treatment Audit",
        "",
        str(audit.get("claim_boundary", RAIL_BOUNDED_TREATMENT_AUDIT_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Audit verdict: `{audit.get('audit_verdict', '')}`",
        f"- Internal mapping mismatches: {audit.get('mismatch_count', 0)}",
        "- Mismatch count is an internal consistency check only, not validation evidence.",
        f"- Warnings: {audit.get('warning_count', 0)}",
        f"- Pending source decisions: {audit.get('unchecked_pending_decision_count', 0)}",
        f"- Publication ready: `{str(audit.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(audit.get('can_mark_complete', False)).lower()}`",
        f"- Can support rail evidence gate: `{str(audit.get('can_support_rail_evidence_gate', False)).lower()}`",
        f"- Can support acceptance gate: `{str(audit.get('can_support_acceptance_gate', False)).lower()}`",
        "",
        "## Row Checks",
        "",
        "| Request | Status | Decision | Matched Stress Classes | Blockers | Warnings |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in audit.get("results", []):
        if not isinstance(result, Mapping):
            continue
        lines.append(
            "| {request} | {status} | {decision} | {classes} | {blockers} | {warnings} |".format(
                request=_cell(result.get("request_id", "")),
                status=_cell(result.get("status", "")),
                decision=_cell(result.get("decision_choice", "")),
                classes=_cell("; ".join(result.get("matched_stress_classes", []))),
                blockers=_cell("; ".join(result.get("blockers", []))),
                warnings=_cell("; ".join(result.get("warnings", []))),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This audit checks whether bounded capacity and availability treatments are internally mapped to stress-profile rows.",
            "- It does not validate rail timing, rail capacity, emergency rail availability, dispatch, or service operations.",
            "- It must not be used as publication readiness, final-study readiness, rail evidence, or formal acceptance.",
            "",
        ]
    )
    return "\n".join(lines)


def _capacity_result(
    source_rows: Sequence[Mapping[str, str]],
    stress_rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    source = _single_by_value(source_rows, "request_id", CAPACITY_REQUEST_ID)
    stress = _single_by_value(stress_rows, "stress_class", "partial_capacity_reduction")
    blockers: list[str] = []
    warnings: list[str] = []
    if source is None:
        blockers.append("missing or duplicate rail capacity source-decision row")
        source = {}
    if stress is None:
        blockers.append("missing or duplicate partial-capacity stress-profile row")
        stress = {}
    if source and "capacity" not in str(source.get("evidence_fields", "")):
        blockers.append("capacity decision row does not name capacity evidence field")
    options = str(source.get("candidate_decision_options", ""))
    for option in (
        "retain_capacity_as_sensitivity_only_with_bounds",
        "exclude_capacity_dependent_release_scope_claims",
    ):
        if source and option not in options:
            blockers.append(f"capacity decision options missing {option}")
    if stress:
        if stress.get("source_treatment") != "sensitivity_only":
            blockers.append("partial-capacity stress is not sensitivity-only")
        if stress.get("evidence_status") != "sensitivity_only_not_capacity_evidence":
            blockers.append("partial-capacity stress status no longer blocks evidence use")
        if stress.get("parameter_path") != "rail_capacity_multiplier":
            blockers.append("partial-capacity stress is not tied to rail_capacity_multiplier")
        if stress.get("review_required") != "true":
            blockers.append("partial-capacity stress no longer requires review")
    _append_gate_flag_blockers(blockers, "capacity source-decision", source)
    _append_gate_flag_blockers(blockers, "partial-capacity stress-profile", stress)
    _append_stress_profile_integrity_blockers(
        blockers,
        stress,
        expected_implementation_status="data_defined_policy_stress",
    )
    _append_completed_bounded_decision_blockers(blockers, "capacity", source)
    _append_region_mismatch(blockers, source, [stress] if stress else [])
    _append_decision_status_warnings(warnings, source)
    return _result(
        request_id=CAPACITY_REQUEST_ID,
        treatment_type="capacity_sensitivity_only",
        source=source,
        stress_rows=[stress] if stress else [],
        blockers=blockers,
        warnings=warnings,
    )


def _availability_result(
    source_rows: Sequence[Mapping[str, str]],
    stress_rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    source = _single_by_value(source_rows, "request_id", AVAILABILITY_REQUEST_ID)
    required_classes = (
        "increased_headway",
        "partial_unavailability_or_delay",
        "rail_access_egress_degradation",
    )
    matched = [_single_by_value(stress_rows, "stress_class", klass) for klass in required_classes]
    matched_rows = [row for row in matched if row is not None]
    blockers: list[str] = []
    warnings: list[str] = []
    if source is None:
        blockers.append("missing or duplicate rail availability source-decision row")
        source = {}
    missing_classes = [
        klass for klass, row in zip(required_classes, matched, strict=True) if row is None
    ]
    blockers.extend(f"missing availability stress class {klass}" for klass in missing_classes)
    if source and "availability" not in str(source.get("evidence_fields", "")):
        blockers.append("availability decision row does not name availability evidence field")
    options = str(source.get("candidate_decision_options", ""))
    for option in (
        "record_scenario_only_availability_scope",
        "retain_availability_as_sensitivity_only",
        "exclude_availability_dependent_release_scope_claims",
    ):
        if source and option not in options:
            blockers.append(f"availability decision options missing {option}")
    by_class = {row.get("stress_class", ""): row for row in matched_rows}
    for klass in ("increased_headway", "partial_unavailability_or_delay"):
        row = by_class.get(klass)
        if row and row.get("source_treatment") != "scenario_only":
            blockers.append(f"{klass} stress is not scenario-only")
        if row and "not" not in row.get("evidence_status", ""):
            blockers.append(f"{klass} stress status does not preserve evidence boundary")
    station = by_class.get("rail_access_egress_degradation")
    if station and station.get("runtime_hook_type") != "road_connector_degradation":
        blockers.append("station-access stress is not framed as road connector degradation")
    if station and "not a rail-service outage model" not in station.get("notes", ""):
        blockers.append("station-access stress no longer blocks rail-service outage interpretation")
    if source.get("decision_choice") == "retain_availability_as_sensitivity_only":
        warnings.append(
            "current availability coverage is scenario-only/road-connector based, not sensitivity-only"
        )
    _append_gate_flag_blockers(blockers, "availability source-decision", source)
    for row in matched_rows:
        _append_gate_flag_blockers(blockers, f"{row.get('stress_class', '')} stress-profile", row)
        expected_status = (
            "mapped_disruption_scenario"
            if row.get("stress_class") == "rail_access_egress_degradation"
            else "data_defined_policy_stress"
        )
        _append_stress_profile_integrity_blockers(
            blockers,
            row,
            expected_implementation_status=expected_status,
        )
    _append_completed_bounded_decision_blockers(blockers, "availability", source)
    _append_region_mismatch(blockers, source, matched_rows)
    _append_decision_status_warnings(warnings, source)
    return _result(
        request_id=AVAILABILITY_REQUEST_ID,
        treatment_type="availability_scenario_only",
        source=source,
        stress_rows=matched_rows,
        blockers=blockers,
        warnings=warnings,
    )


def _result(
    *,
    request_id: str,
    treatment_type: str,
    source: Mapping[str, str],
    stress_rows: Sequence[Mapping[str, str]],
    blockers: Sequence[str],
    warnings: Sequence[str],
) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "treatment_type": treatment_type,
        "status": "mismatch" if blockers else "coverage_documented_not_evidence",
        "decision_status": str(source.get("decision_status", "")),
        "decision_choice": str(source.get("decision_choice", "")),
        "decision_scope": str(source.get("decision_scope", "")),
        "evidence_fields": str(source.get("evidence_fields", "")),
        "source_type": str(source.get("source_type", "")),
        "candidate_decision_options": str(source.get("candidate_decision_options", "")),
        "allowed_bounded_fallback": str(source.get("allowed_bounded_fallback", "")),
        "matched_stress_classes": [str(row.get("stress_class", "")) for row in stress_rows],
        "matched_source_treatments": [
            str(row.get("source_treatment", "")) for row in stress_rows
        ],
        "matched_linked_artifacts": [
            f"{row.get('linked_artifact', '')}#{row.get('linked_artifact_key', '')}"
            for row in stress_rows
        ],
        "matched_runtime_hooks": [str(row.get("runtime_hook_type", "")) for row in stress_rows],
        "matched_evidence_statuses": [
            str(row.get("evidence_status", "")) for row in stress_rows
        ],
        "blockers": list(blockers),
        "warnings": list(warnings),
        "publication_ready": False,
        "can_mark_complete": False,
        "can_support_rail_evidence_gate": False,
        "can_support_acceptance_gate": False,
    }


def _single_by_value(
    rows: Sequence[Mapping[str, str]],
    column: str,
    value: str,
) -> Mapping[str, str] | None:
    matches = [row for row in rows if str(row.get(column, "")).strip() == value]
    return matches[0] if len(matches) == 1 else None


def _append_gate_flag_blockers(
    blockers: list[str],
    label: str,
    row: Mapping[str, str],
) -> None:
    for field in GATE_FIELDS:
        if str(row.get(field, "")).strip().lower() == "true":
            blockers.append(f"{label} sets {field}=true")


def _append_stress_profile_integrity_blockers(
    blockers: list[str],
    row: Mapping[str, str],
    *,
    expected_implementation_status: str | None = None,
) -> None:
    """Block coverage claims when the linked runtime or artifact is not resolvable."""

    if not row:
        return
    stress_class = str(row.get("stress_class", "")).strip() or "unknown stress"
    implementation_status = str(row.get("implementation_status", "")).strip()
    runtime_hook_type = str(row.get("runtime_hook_type", "")).strip()
    if implementation_status == "missing_runtime_hook":
        blockers.append(f"{stress_class} stress-profile has missing runtime hook")
    if (
        expected_implementation_status
        and implementation_status != expected_implementation_status
    ):
        blockers.append(
            f"{stress_class} stress-profile implementation status is "
            f"{implementation_status or 'blank'}, expected {expected_implementation_status}"
        )
    if not runtime_hook_type:
        blockers.append(f"{stress_class} stress-profile has blank runtime hook")
    _append_linked_artifact_blockers(blockers, stress_class, row)


def _append_linked_artifact_blockers(
    blockers: list[str],
    stress_class: str,
    row: Mapping[str, str],
) -> None:
    artifact_text = str(row.get("linked_artifact", "")).strip()
    key_text = str(row.get("linked_artifact_key", "")).strip()
    if not artifact_text:
        blockers.append(f"{stress_class} stress-profile has blank linked artifact")
        return
    artifact_path = Path(artifact_text)
    if not artifact_path.is_absolute():
        artifact_path = PROJECT_ROOT / artifact_path
    if not artifact_path.exists():
        blockers.append(
            f"{stress_class} stress-profile linked artifact is missing: {artifact_text}"
        )
        return
    if not key_text:
        blockers.append(f"{stress_class} stress-profile has blank linked artifact key")
        return
    key_column = LINKED_ARTIFACT_KEY_COLUMNS.get(artifact_path.name)
    if key_column is None:
        return
    observed_keys = _csv_values(artifact_path, key_column)
    expected_keys = [key.strip() for key in key_text.split(";") if key.strip()]
    for key in expected_keys:
        if key not in observed_keys:
            blockers.append(
                f"{stress_class} stress-profile linked artifact key is missing: {key}"
            )


def _append_region_mismatch(
    blockers: list[str],
    source: Mapping[str, str],
    stress_rows: Sequence[Mapping[str, str]],
) -> None:
    source_region = str(source.get("region_id", "")).strip()
    for row in stress_rows:
        stress_region = str(row.get("region_id", "")).strip()
        if source_region and stress_region and source_region != stress_region:
            blockers.append(
                f"region mismatch: source decision {source_region}, stress row {stress_region}"
            )


def _append_decision_status_warnings(warnings: list[str], source: Mapping[str, str]) -> None:
    if source.get("decision_choice") == "pending_reviewer_decision":
        warnings.append("source decision is still pending reviewer decision")
    if str(source.get("decision_status", "")).startswith("needs_human_review_"):
        warnings.append("source decision still needs human review")
    if str(source.get("decision_status", "")).startswith("blocked_"):
        warnings.append("source decision is still blocked")


def _append_completed_bounded_decision_blockers(
    blockers: list[str],
    label: str,
    source: Mapping[str, str],
) -> None:
    choice = str(source.get("decision_choice", "")).strip()
    if not choice or choice == "pending_reviewer_decision":
        return
    bounded_choices = (
        "sensitivity_only",
        "scenario_only",
        "exclude",
    )
    if not any(token in choice for token in bounded_choices):
        return
    required = (
        "reviewer",
        "decision_date",
        "decision_basis",
        "excluded_or_retained_claim_scope",
        "not_operational_claim_boundary",
        "bounded_treatment_or_exclusion_rationale",
    )
    missing = [field for field in required if not str(source.get(field, "")).strip()]
    if missing:
        blockers.append(
            f"{label} bounded decision missing required fields: {', '.join(missing)}"
        )


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _csv_values(path: Path, column: str) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            str(row.get(column, "")).strip()
            for row in csv.DictReader(handle)
            if str(row.get(column, "")).strip()
        }


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
    "AVAILABILITY_REQUEST_ID",
    "CAPACITY_REQUEST_ID",
    "DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_DOC_PATH",
    "DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH",
    "RAIL_BOUNDED_TREATMENT_AUDIT_SCOPE",
    "build_rail_bounded_treatment_audit",
    "build_rail_bounded_treatment_markdown",
    "write_rail_bounded_treatment_audit",
]
