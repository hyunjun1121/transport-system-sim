"""Cross-cutting parameter evidence source-request packet generation.

The parameter review packet identifies weak assumptions. This module turns the
cross-cutting gaps into a source-request worksheet: demand, fleet, dispatch,
transfer, disruption scenario, and traffic/BPR calibration inputs. It names
required source packages and review commands, but it does not create accepted
parameter calibration, weak-parameter acceptance, or publication readiness.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.parameter_review_packet import (
    DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    build_parameter_review_rows,
)
from src.realworld.parameters import DEFAULT_PARAMETER_DIR


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH = (
    PROJECT_ROOT
    / "data"
    / "parameters"
    / "parameter_evidence_source_request_packet.csv"
)
DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "parameters"
    / "parameter_evidence_source_request_manifest.json"
)
PARAMETER_EVIDENCE_SOURCE_REQUEST_SCOPE = (
    "Parameter evidence source-request packet; not source evidence, not "
    "accepted parameter calibration, not weak-parameter acceptance, and not "
    "publication-readiness approval."
)
PARAMETER_EVIDENCE_SOURCE_REQUEST_COLUMNS: tuple[str, ...] = (
    "request_id",
    "region_id",
    "parameter_groups",
    "covered_parameters",
    "weak_parameter_count",
    "evidence_fields",
    "source_type",
    "source_name",
    "source_url_or_citation",
    "required_external_input",
    "current_evidence_summary",
    "current_values",
    "review_priority_basis",
    "source_cache_path",
    "raw_payload_path",
    "acquisition_command",
    "review_or_derivation_command",
    "target_output_path",
    "expected_source_status",
    "expected_derived_fields",
    "can_close_parameter_evidence_gate",
    "can_close_acceptance_gate",
    "publication_use_status",
    "claim_boundary",
    "notes",
)

DEMAND_TIME_CENSORING_PARAMETERS: tuple[str, ...] = (
    "passenger_volume",
    "passenger_arrival_distribution",
    "simulation_time_horizon",
    "late_arrival_penalty",
    "censored_passenger_penalty",
)
FLEET_CAPACITY_PARAMETERS: tuple[str, ...] = (
    "bus_capacity",
    "last_mile_vehicle_capacity",
    "direct_bus_fleet_size",
    "feeder_fleet_size",
    "last_mile_fleet_size",
)
DISPATCH_TURNAROUND_PARAMETERS: tuple[str, ...] = (
    "dispatch_interval",
    "turnaround_time",
)
TRANSFER_PARAMETERS: tuple[str, ...] = (
    "transfer_fixed_delay",
    "transfer_per_passenger_delay",
)
DISRUPTION_SCENARIO_PARAMETERS: tuple[str, ...] = (
    "disruption_probability",
    "capacity_reduction_factor",
    "blockage_rule",
    "base_disruption_probability",
)
TRAFFIC_BPR_PARAMETERS: tuple[str, ...] = (
    "background_traffic_multiplier",
    "traffic_volume_window",
    "bpr_alpha",
    "bpr_beta",
)


def build_parameter_evidence_source_request_rows(
    *,
    review_packet_path: str | Path = DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    parameter_dir: str | Path = DEFAULT_PARAMETER_DIR,
) -> list[dict[str, str]]:
    """Return deterministic source-request rows for cross-cutting parameter gaps."""

    review_rows = _load_or_build_review_rows(review_packet_path, parameter_dir)
    by_parameter = {
        str(row.get("parameter", "")).strip(): row
        for row in review_rows
        if str(row.get("parameter", "")).strip()
    }

    return [
        _request_row(
            request_id="demand_arrival_horizon_censoring_source_request",
            parameter_groups="demand_time_censoring",
            parameters=DEMAND_TIME_CENSORING_PARAMETERS,
            evidence_fields=(
                "passenger_volume;arrival_distribution;simulation_time_horizon;"
                "late_arrival_penalty;censored_passenger_penalty"
            ),
            source_type="planning_scenario_or_literature_source_required",
            source_name=(
                "Reviewed demand planning scenario, arrival-process evidence, "
                "exercise design, or literature values"
            ),
            source_url_or_citation=(
                "data/parameters/parameter_sources.csv; "
                "data/scenarios/sensitivity_design.csv"
            ),
            required_external_input=(
                "reviewed passenger-volume basis, arrival process or assembly "
                "window, simulation horizon, and KPI penalty rationale or "
                "explicit sensitivity-only treatment"
            ),
            source_cache_path="data/scenarios/sensitivity_design.csv",
            raw_payload_path="",
            acquisition_command=(
                "manual reviewed scenario, planning, or literature acquisition; "
                "do not infer demand from current simulation outputs"
            ),
            review_or_derivation_command=(
                "update data\\parameters\\parameter_sources.csv, then run "
                ".\\.venv\\Scripts\\python scripts\\write_parameter_review_packet.py"
            ),
            target_output_path="data/parameters/parameter_sources.csv",
            expected_source_status="source_backed_or_reviewed_scenario_assumption",
            expected_derived_fields=(
                "passenger_volume;arrival_distribution;simulation_time_horizon;"
                "late_arrival_penalty;censored_passenger_penalty"
            ),
            publication_use_status=(
                "demand and KPI source-request support only; not calibrated demand"
            ),
            notes=(
                "These parameters define the decision-support scenario and censoring "
                "KPI. They still require source review or explicit bounded-scenario "
                "acceptance before final claims."
            ),
            review_rows=review_rows,
            by_parameter=by_parameter,
        ),
        _request_row(
            request_id="fleet_vehicle_capacity_source_request",
            parameter_groups="fleet",
            parameters=FLEET_CAPACITY_PARAMETERS,
            evidence_fields="vehicle_capacity;fleet_size;load_factor",
            source_type="agency_fleet_roster_or_planning_source_required",
            source_name=(
                "Reviewed agency fleet roster, vehicle-capacity source, exercise "
                "fleet package, or transport-planning literature"
            ),
            source_url_or_citation="data/parameters/fleet_assumptions.csv",
            required_external_input=(
                "reviewed vehicle capacities, feasible load factors, available "
                "fleet counts by role, or explicit scenario-fleet assumption"
            ),
            source_cache_path="data/parameters/fleet_assumptions.csv",
            raw_payload_path="",
            acquisition_command=(
                "manual agency, exercise, or literature source acquisition; do "
                "not treat config fleet sizes as an operational inventory"
            ),
            review_or_derivation_command=(
                "update data\\parameters\\fleet_assumptions.csv, then run "
                ".\\.venv\\Scripts\\python scripts\\write_parameter_review_packet.py"
            ),
            target_output_path=(
                "data/parameters/fleet_assumptions.csv; "
                "data/parameters/parameter_sources.csv"
            ),
            expected_source_status="source_backed_or_reviewed_fleet_scenario",
            expected_derived_fields=(
                "bus_capacity;last_mile_vehicle_capacity;direct_bus_fleet_size;"
                "feeder_fleet_size;last_mile_fleet_size"
            ),
            publication_use_status=(
                "fleet source-request support only; not accepted vehicle inventory"
            ),
            notes=(
                "The current values are scenario assumptions. A final study needs "
                "reviewed source-backed capacities/counts or explicit sensitivity "
                "boundaries."
            ),
            review_rows=review_rows,
            by_parameter=by_parameter,
        ),
        _request_row(
            request_id="dispatch_turnaround_source_request",
            parameter_groups="fleet",
            parameters=DISPATCH_TURNAROUND_PARAMETERS,
            evidence_fields="dispatch_interval;turnaround_time;first_departure_anchor",
            source_type="operating_schedule_or_planning_rule_required",
            source_name=(
                "Reviewed dispatch schedule, staging rule, depot/layover basis, "
                "or policy scenario rule"
            ),
            source_url_or_citation=(
                "data/parameters/fleet_assumptions.csv; "
                "data/scenarios/policy_alternatives.csv"
            ),
            required_external_input=(
                "reviewed dispatch interval, turnaround or layover time, first "
                "departure anchor, or explicit policy-sensitivity treatment"
            ),
            source_cache_path=(
                "data/parameters/fleet_assumptions.csv; "
                "data/scenarios/policy_alternatives.csv"
            ),
            raw_payload_path="",
            acquisition_command=(
                "manual operating-plan, exercise-design, or literature acquisition"
            ),
            review_or_derivation_command=(
                "review policy_alternatives.csv and fleet_assumptions.csv, then "
                "run .\\.venv\\Scripts\\python scripts\\write_parameter_review_packet.py"
            ),
            target_output_path=(
                "data/parameters/fleet_assumptions.csv; "
                "data/parameters/parameter_sources.csv"
            ),
            expected_source_status="reviewed_schedule_or_policy_scenario_rule",
            expected_derived_fields="dispatch_interval;turnaround_time",
            publication_use_status=(
                "dispatch source-request support only; not an operating timetable"
            ),
            notes=(
                "Dispatch and turnaround settings govern both bus-only and "
                "multimodal road legs. This worksheet does not approve a real "
                "deployment schedule."
            ),
            review_rows=review_rows,
            by_parameter=by_parameter,
        ),
        _request_row(
            request_id="transfer_delay_source_request",
            parameter_groups="transfer",
            parameters=TRANSFER_PARAMETERS,
            evidence_fields="transfer_fixed_delay;transfer_per_passenger_delay",
            source_type="station_layout_or_pedestrian_flow_source_required",
            source_name=(
                "Reviewed station-transfer geometry, walking/crowding evidence, "
                "observed transfer range, or pedestrian-flow literature"
            ),
            source_url_or_citation=(
                "data/parameters/parameter_sources.csv; "
                "data/regions/pilot_region.yaml"
            ),
            required_external_input=(
                "reviewed transfer path length, walking speed, vertical-circulation "
                "or crowding assumptions, and per-passenger delay treatment"
            ),
            source_cache_path="data/parameters/parameter_sources.csv",
            raw_payload_path="",
            acquisition_command=(
                "manual station-layout, field-observation, or literature acquisition"
            ),
            review_or_derivation_command=(
                "replace or bound transfer delay rows in "
                "data\\parameters\\parameter_sources.csv, then run "
                ".\\.venv\\Scripts\\python scripts\\write_parameter_review_packet.py"
            ),
            target_output_path="data/parameters/parameter_sources.csv",
            expected_source_status="source_backed_or_reviewed_transfer_assumption",
            expected_derived_fields=(
                "transfer_fixed_delay;transfer_per_passenger_delay"
            ),
            publication_use_status=(
                "transfer source-request support only; not observed transfer timing"
            ),
            notes=(
                "The baseline fixed transfer delay and disabled crowding delay remain "
                "assumptions until reviewed transfer evidence or sensitivity bounds "
                "are recorded."
            ),
            review_rows=review_rows,
            by_parameter=by_parameter,
        ),
        _request_row(
            request_id="disruption_scenario_assumption_source_request",
            parameter_groups="disruption",
            parameters=DISRUPTION_SCENARIO_PARAMETERS,
            evidence_fields=(
                "disruption_probability;capacity_reduction_factor;blockage_rule;"
                "base_disruption_probability"
            ),
            source_type="hazard_incident_or_scenario_rule_source_required",
            source_name=(
                "Reviewed hazard, incident, exposure, accessibility-loss, or "
                "scenario-rule source"
            ),
            source_url_or_citation=(
                "data/scenarios/disruption_scenarios.csv; "
                "data/validation/accessibility_loss.csv"
            ),
            required_external_input=(
                "public hazard or incident data, reviewed scenario-family rules, "
                "capacity-loss literature, or explicit sensitivity-only treatment"
            ),
            source_cache_path=(
                "data/scenarios/disruption_scenarios.csv; "
                "data/validation/accessibility_loss.csv"
            ),
            raw_payload_path="data/validation/accessibility_loss_summary.md",
            acquisition_command=(
                ".\\.venv\\Scripts\\python scripts\\run_accessibility_loss_analysis.py"
            ),
            review_or_derivation_command=(
                "review disruption_scenarios.csv and accessibility_loss outputs, "
                "then update data\\parameters\\parameter_sources.csv"
            ),
            target_output_path=(
                "data/scenarios/disruption_scenarios.csv; "
                "data/parameters/parameter_sources.csv"
            ),
            expected_source_status="reviewed_hazard_source_or_scenario_rule",
            expected_derived_fields=(
                "disruption_probability;capacity_reduction_factor;blockage_rule;"
                "base_disruption_probability"
            ),
            publication_use_status=(
                "disruption source-request support only; not observed disruption "
                "probability"
            ),
            notes=(
                "The road evidence request packet owns road-class override inputs. "
                "This row keeps scenario-level disruption assumptions and capacity "
                "loss treatment explicit."
            ),
            review_rows=review_rows,
            by_parameter=by_parameter,
        ),
        _request_row(
            request_id="background_traffic_bpr_calibration_source_request",
            parameter_groups="road",
            parameters=TRAFFIC_BPR_PARAMETERS,
            evidence_fields=(
                "background_traffic_multiplier;traffic_volume_window;bpr_alpha;"
                "bpr_beta"
            ),
            source_type="traffic_benchmark_or_literature_calibration_required",
            source_name=(
                "Reviewed route-time benchmark, observed traffic counts/speeds, "
                "or BPR calibration literature"
            ),
            source_url_or_citation=(
                "data/validation/external_route_benchmarks.csv; "
                "data/validation/external_route_benchmarks_osrm.csv; "
                "Bureau of Public Roads 1964 Traffic Assignment Manual"
            ),
            required_external_input=(
                "reviewed route-time benchmarks, traffic counts or speed profiles, "
                "rolling-window justification, and local BPR calibration decision"
            ),
            source_cache_path=(
                "data/validation/external_route_benchmarks.csv; "
                "data/scenarios/sensitivity_design.csv"
            ),
            raw_payload_path="data/validation/external_route_benchmarks_osrm.csv",
            acquisition_command=(
                ".\\.venv\\Scripts\\python scripts\\run_plausibility_validation.py"
            ),
            review_or_derivation_command=(
                "review benchmark deltas and BPR defaults before updating "
                "data\\parameters\\parameter_sources.csv"
            ),
            target_output_path="data/parameters/parameter_sources.csv",
            expected_source_status=(
                "benchmark_calibrated_or_literature_default_with_sensitivity_boundary"
            ),
            expected_derived_fields=(
                "background_traffic_multiplier;traffic_volume_window;bpr_alpha;"
                "bpr_beta"
            ),
            publication_use_status=(
                "traffic-model source-request support only; benchmark is not ground truth"
            ),
            notes=(
                "Existing road packets cover road-class speed and capacity inputs. "
                "This row keeps background traffic, rolling-window, and BPR "
                "treatment visible for final claim boundaries."
            ),
            review_rows=review_rows,
            by_parameter=by_parameter,
        ),
    ]


def write_parameter_evidence_source_request_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH,
    review_packet_path: str | Path = DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    parameter_dir: str | Path = DEFAULT_PARAMETER_DIR,
) -> dict[str, Any]:
    """Write parameter source-request rows and a non-acceptance manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=PARAMETER_EVIDENCE_SOURCE_REQUEST_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    evidence_candidates = [
        row
        for row in rows
        if str(row.get("can_close_parameter_evidence_gate", "")).lower() == "true"
    ]
    acceptance_candidates = [
        row
        for row in rows
        if str(row.get("can_close_acceptance_gate", "")).lower() == "true"
    ]
    covered_parameters = _unique_fields(row["covered_parameters"] for row in rows)
    value = {
        "schema_version": 1,
        "result_scope": PARAMETER_EVIDENCE_SOURCE_REQUEST_SCOPE,
        "inputs": {
            "parameter_evidence_review_packet": _display_path(review_packet_path),
            "parameter_dir": _display_path(parameter_dir),
        },
        "outputs": {
            "parameter_evidence_source_request_packet": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "covered_parameter_count": len(covered_parameters),
        "covered_parameters": covered_parameters,
        "weak_parameter_count": sum(
            _safe_int(row.get("weak_parameter_count", "0")) for row in rows
        ),
        "parameter_group_counts": _field_counts(
            row["parameter_groups"] for row in rows
        ),
        "source_type_counts": _counts(row["source_type"] for row in rows),
        "evidence_field_counts": _field_counts(row["evidence_fields"] for row in rows),
        "parameter_evidence_gate_closure_candidate_count": len(evidence_candidates),
        "acceptance_gate_closure_candidate_count": len(acceptance_candidates),
        "requires_reviewed_external_input_count": sum(
            1
            for row in rows
            if "required" in row["source_type"] or "reviewed" in row["source_type"]
        ),
        "publication_ready": False,
        "claim_boundary": (
            "This packet identifies required cross-cutting parameter source "
            "inputs and review commands. It does not contain reviewed source "
            "observations, accepted parameter values, weak-parameter acceptance, "
            "calibration proof, or final-study publication readiness."
        ),
        "review_items": [
            "collect reviewed source packages for demand, fleet, dispatch, transfer, disruption, and traffic/BPR assumptions",
            "update parameter_sources.csv or fleet_assumptions.csv only after source review",
            "use parameter_acceptance.csv separately for retained weak assumptions inside conservative claim boundaries",
            "rerun parameter review, publication-readiness, and final-study-readiness audits after source changes",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _request_row(
    *,
    request_id: str,
    parameter_groups: str,
    parameters: Sequence[str],
    evidence_fields: str,
    source_type: str,
    source_name: str,
    source_url_or_citation: str,
    required_external_input: str,
    source_cache_path: str,
    raw_payload_path: str,
    acquisition_command: str,
    review_or_derivation_command: str,
    target_output_path: str,
    expected_source_status: str,
    expected_derived_fields: str,
    publication_use_status: str,
    notes: str,
    review_rows: Sequence[Mapping[str, str]],
    by_parameter: Mapping[str, Mapping[str, str]],
    region_id: str = "songpa_public_demo",
) -> dict[str, str]:
    covered = [parameter for parameter in parameters if parameter in by_parameter]
    current_rows = [by_parameter[parameter] for parameter in covered]
    return {
        "request_id": request_id,
        "region_id": region_id,
        "parameter_groups": parameter_groups,
        "covered_parameters": ";".join(covered),
        "weak_parameter_count": str(
            sum(
                1
                for row in current_rows
                if str(row.get("weak_for_final_claim", "")).lower() == "true"
            )
        ),
        "evidence_fields": evidence_fields,
        "source_type": source_type,
        "source_name": source_name,
        "source_url_or_citation": source_url_or_citation,
        "required_external_input": required_external_input,
        "current_evidence_summary": _current_evidence_summary(
            parameters,
            by_parameter,
        ),
        "current_values": _current_values(parameters, by_parameter),
        "review_priority_basis": _review_basis(
            review_rows,
            current_rows,
        ),
        "source_cache_path": source_cache_path,
        "raw_payload_path": raw_payload_path,
        "acquisition_command": acquisition_command,
        "review_or_derivation_command": review_or_derivation_command,
        "target_output_path": target_output_path,
        "expected_source_status": expected_source_status,
        "expected_derived_fields": expected_derived_fields,
        "can_close_parameter_evidence_gate": "false",
        "can_close_acceptance_gate": "false",
        "publication_use_status": publication_use_status,
        "claim_boundary": PARAMETER_EVIDENCE_SOURCE_REQUEST_SCOPE,
        "notes": notes,
    }


def _load_or_build_review_rows(
    path: str | Path,
    parameter_dir: str | Path,
) -> list[dict[str, str]]:
    packet = Path(path)
    if not packet.exists():
        return build_parameter_review_rows(parameter_dir=parameter_dir)
    with packet.open("r", encoding="utf-8", newline="") as handle:
        return [
            {str(key): str(value or "") for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def _current_evidence_summary(
    parameters: Sequence[str],
    by_parameter: Mapping[str, Mapping[str, str]],
) -> str:
    parts: list[str] = []
    for parameter in parameters:
        row = by_parameter.get(parameter)
        if row is None:
            parts.append(f"{parameter}=missing")
            continue
        parts.append(
            (
                f"{parameter}={row.get('evidence_category', '')}/"
                f"{row.get('review_priority', '')}/weak="
                f"{row.get('weak_for_final_claim', '')}"
            )
        )
    return "; ".join(parts)


def _current_values(
    parameters: Sequence[str],
    by_parameter: Mapping[str, Mapping[str, str]],
) -> str:
    parts: list[str] = []
    for parameter in parameters:
        row = by_parameter.get(parameter)
        if row is None:
            continue
        value = str(row.get("current_value", "")).strip()
        unit = str(row.get("unit", "")).strip()
        parts.append(f"{parameter}={value} {unit}".strip())
    return "; ".join(parts)


def _review_basis(
    all_rows: Sequence[Mapping[str, str]],
    current_rows: Sequence[Mapping[str, str]],
) -> str:
    priority_counts = _counts(str(row.get("review_priority", "")) for row in current_rows)
    weak = sum(
        1
        for row in current_rows
        if str(row.get("weak_for_final_claim", "")).lower() == "true"
    )
    parts = [
        f"parameter_evidence_review_packet rows={len(all_rows)}",
        f"covered={len(current_rows)}",
        f"weak={weak}",
    ]
    parts.extend(
        f"{priority}_priority={count}"
        for priority, count in priority_counts.items()
        if priority
    )
    return "; ".join(parts)


def _unique_fields(values: Iterable[str]) -> list[str]:
    fields: set[str] = set()
    for value in values:
        for token in str(value).replace("|", ";").split(";"):
            key = token.strip()
            if key:
                fields.add(key)
    return sorted(fields)


def _field_counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        for token in str(value).replace("|", ";").split(";"):
            key = token.strip()
            if key:
                counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _safe_int(value: object) -> int:
    try:
        return int(str(value))
    except ValueError:
        return 0


def _display_path(path: str | Path) -> str:
    value = Path(path)
    try:
        return value.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return value.as_posix()


__all__ = [
    "DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH",
    "DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH",
    "PARAMETER_EVIDENCE_SOURCE_REQUEST_COLUMNS",
    "PARAMETER_EVIDENCE_SOURCE_REQUEST_SCOPE",
    "build_parameter_evidence_source_request_rows",
    "write_parameter_evidence_source_request_packet",
]
