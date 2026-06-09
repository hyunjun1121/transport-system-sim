"""Rail/transit stress-profile review packet.

This module documents which rail and station-access stress classes are covered
by current scenario, policy, and sensitivity artifacts. It is a review aid only:
it does not derive rail timing evidence, accept capacity assumptions, certify
emergency rail availability, or close any formal gate.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_transit_stress_profile_packet.csv"
)
DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_transit_stress_profile_manifest.json"
)
DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "rail_transit_stress_profile_packet.md"
)
DEFAULT_POLICY_ALTERNATIVES_PATH = (
    PROJECT_ROOT / "data" / "scenarios" / "policy_alternatives.csv"
)
DEFAULT_DISRUPTION_SCENARIOS_PATH = (
    PROJECT_ROOT / "data" / "scenarios" / "disruption_scenarios.csv"
)
DEFAULT_SENSITIVITY_DESIGN_PATH = (
    PROJECT_ROOT / "data" / "scenarios" / "sensitivity_design.csv"
)
DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_source_decision_manifest.json"
)
RAIL_TRANSIT_STRESS_PROFILE_SCOPE = (
    "Rail/transit stress-profile review packet only; scenario and sensitivity "
    "coverage documentation, not rail-service calibration, not emergency rail "
    "availability evidence, not operational service planning, not publication "
    "readiness, not final-study readiness, and not formal acceptance."
)
REQUIRED_STRESS_CLASSES: tuple[str, ...] = (
    "normal_service_assumption",
    "increased_headway",
    "partial_capacity_reduction",
    "rail_access_egress_degradation",
    "station_processing_delay_proxy",
    "partial_unavailability_or_delay",
)
RAIL_TRANSIT_STRESS_PROFILE_COLUMNS: tuple[str, ...] = (
    "profile_id",
    "region_id",
    "stress_class",
    "label",
    "source_treatment",
    "implementation_status",
    "runtime_hook_type",
    "linked_artifact",
    "linked_artifact_key",
    "scenario_or_policy_id",
    "parameter_path",
    "evidence_status",
    "review_required",
    "can_support_rail_evidence_gate",
    "can_support_acceptance_gate",
    "publication_ready",
    "claim_boundary",
    "notes",
)
LINKED_ARTIFACT_KEY_COLUMNS = {
    "policy_alternatives.csv": "policy_id",
    "disruption_scenarios.csv": "scenario_id",
    "sensitivity_design.csv": "parameter_id",
    "rail_service_evidence.csv": "evidence_id",
}


def build_rail_transit_stress_profile_rows(
    *,
    region_id: str = "songpa_public_demo",
    policy_alternatives_path: str | Path = DEFAULT_POLICY_ALTERNATIVES_PATH,
    disruption_scenarios_path: str | Path = DEFAULT_DISRUPTION_SCENARIOS_PATH,
    sensitivity_design_path: str | Path = DEFAULT_SENSITIVITY_DESIGN_PATH,
) -> list[dict[str, str]]:
    """Return conservative rail/transit stress-profile rows."""

    policy_ids = _ids_from_csv(policy_alternatives_path, "policy_id")
    scenario_ids = _ids_from_csv(disruption_scenarios_path, "scenario_id")
    sensitivity_ids = _ids_from_csv(sensitivity_design_path, "parameter_id")
    rows = [
        _row(
            profile_id="rail_normal_service_assumption",
            region_id=region_id,
            stress_class="normal_service_assumption",
            label="Current fixed-headway rail proxy",
            source_treatment="documented_assumption_proxy",
            implementation_status="represented_by_assumption_proxy",
            runtime_hook_type="fixed_headway_rail_assumption",
            linked_artifact="data/parameters/rail_service_evidence.csv",
            linked_artifact_key="songpa_public_demo_rail_proxy_v1",
            scenario_or_policy_id="",
            parameter_path="network.rail_link; multimodal.rail_first_departure_min",
            evidence_status="assumption_proxy_not_accepted",
            review_required=True,
            notes=(
                "Baseline rail service is a documented proxy until reviewed "
                "GTFS, timetable, or shortest-path evidence is retained."
            ),
        ),
        _row(
            profile_id="rail_increased_headway_stress",
            region_id=region_id,
            stress_class="increased_headway",
            label="Rail headway increase stress",
            source_treatment="scenario_only",
            implementation_status=_status(
                "rail_delay_or_partial_unavailability" in policy_ids,
                "data_defined_policy_stress",
            ),
            runtime_hook_type="policy_multiplier",
            linked_artifact="data/scenarios/policy_alternatives.csv",
            linked_artifact_key="rail_delay_or_partial_unavailability",
            scenario_or_policy_id="rail_delay_or_partial_unavailability",
            parameter_path="rail_headway_multiplier",
            evidence_status="scenario_stress_not_availability_evidence",
            review_required=True,
            notes=(
                "Headway stress exposes multimodal fragility but does not "
                "predict actual emergency service availability."
            ),
        ),
        _row(
            profile_id="rail_partial_capacity_reduction_stress",
            region_id=region_id,
            stress_class="partial_capacity_reduction",
            label="Rail capacity reduction stress",
            source_treatment="sensitivity_only",
            implementation_status=_status(
                "rail_delay_or_partial_unavailability" in policy_ids,
                "data_defined_policy_stress",
            ),
            runtime_hook_type="policy_multiplier",
            linked_artifact="data/scenarios/policy_alternatives.csv",
            linked_artifact_key="rail_delay_or_partial_unavailability",
            scenario_or_policy_id="rail_delay_or_partial_unavailability",
            parameter_path="rail_capacity_multiplier",
            evidence_status="sensitivity_only_not_capacity_evidence",
            review_required=True,
            notes=(
                "Capacity stress remains sensitivity-only unless replaced by "
                "operator, literature, or reviewed public-source evidence."
            ),
        ),
        _row(
            profile_id="rail_access_egress_road_degradation",
            region_id=region_id,
            stress_class="rail_access_egress_degradation",
            label="Road access and egress degradation around rail points",
            source_treatment="scenario_only",
            implementation_status=_status(
                "songpa_rail_station_access" in scenario_ids,
                "mapped_disruption_scenario",
            ),
            runtime_hook_type="road_connector_degradation",
            linked_artifact="data/scenarios/disruption_scenarios.csv",
            linked_artifact_key="songpa_rail_station_access",
            scenario_or_policy_id="songpa_rail_station_access",
            parameter_path="rail_station_access selected road edges",
            evidence_status="scenario_only_station_access_road_stress",
            review_required=True,
            notes=(
                "This row degrades road or connector access around rail points; "
                "it is not a rail-service outage model."
            ),
        ),
        _row(
            profile_id="rail_station_processing_delay_proxy",
            region_id=region_id,
            stress_class="station_processing_delay_proxy",
            label="Station processing and transfer-delay proxy",
            source_treatment="sensitivity_only_proxy",
            implementation_status=_status(
                {"transfer_fixed_delay", "transfer_per_passenger_delay"}.issubset(
                    sensitivity_ids
                ),
                "represented_by_transfer_sensitivity",
            ),
            runtime_hook_type="transfer_delay_parameter",
            linked_artifact="data/scenarios/sensitivity_design.csv",
            linked_artifact_key=(
                "transfer_fixed_delay;transfer_per_passenger_delay"
            ),
            scenario_or_policy_id="",
            parameter_path=(
                "multimodal.transfer_time_min; "
                "multimodal.transfer_per_passenger_min"
            ),
            evidence_status="proxy_only_not_station_processing_evidence",
            review_required=True,
            notes=(
                "Transfer-delay sensitivity is a station-processing proxy only "
                "until real station-layout or observed processing evidence is "
                "reviewed."
            ),
        ),
        _row(
            profile_id="rail_partial_unavailability_or_delay",
            region_id=region_id,
            stress_class="partial_unavailability_or_delay",
            label="Partial rail unavailability or delay stress",
            source_treatment="scenario_only",
            implementation_status=_status(
                "rail_delay_or_partial_unavailability" in policy_ids,
                "data_defined_policy_stress",
            ),
            runtime_hook_type="policy_multiplier",
            linked_artifact="data/scenarios/policy_alternatives.csv",
            linked_artifact_key="rail_delay_or_partial_unavailability",
            scenario_or_policy_id="rail_delay_or_partial_unavailability",
            parameter_path=(
                "rail_travel_time_multiplier; rail_headway_multiplier; "
                "rail_capacity_multiplier"
            ),
            evidence_status="scenario_stress_not_disruption_evidence",
            review_required=True,
            notes=(
                "This stress profile is a bounded scenario design and cannot "
                "certify actual service availability or agency operations."
            ),
        ),
    ]
    return rows


def write_rail_transit_stress_profile_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_DOC_PATH,
    rail_source_decision_manifest_path: str
    | Path = DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write rail/transit stress profile CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=RAIL_TRANSIT_STRESS_PROFILE_COLUMNS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = build_rail_transit_stress_profile_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        rail_source_decision_manifest_path=rail_source_decision_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_rail_transit_stress_profile_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_rail_transit_stress_profile_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path,
    manifest_path: str | Path,
    doc_path: str | Path,
    rail_source_decision_manifest_path: str
    | Path = DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for rail/transit stress profiles."""

    stress_classes = {str(row.get("stress_class", "")) for row in rows}
    missing_classes = [
        stress_class
        for stress_class in REQUIRED_STRESS_CLASSES
        if stress_class not in stress_classes
    ]
    review_required_count = sum(_is_true(row.get("review_required", "")) for row in rows)
    missing_runtime_hook_count = sum(
        1 for row in rows if row.get("implementation_status") == "missing_runtime_hook"
    )
    row_integrity_blockers = _stress_profile_integrity_blockers(rows)
    unresolved_linked_artifact_count = sum(
        1
        for blocker in row_integrity_blockers
        if "linked artifact" in blocker
    )
    source_decisions = _read_json(rail_source_decision_manifest_path)
    source_decision_blockers = list(source_decisions.get("remaining_blockers", []))
    return {
        "schema_version": 1,
        "result_scope": RAIL_TRANSIT_STRESS_PROFILE_SCOPE,
        "claim_boundary": (
            RAIL_TRANSIT_STRESS_PROFILE_SCOPE
            + " It can document stress coverage but cannot close rail evidence, "
            "parameter, validation, publication, final-study, or formal "
            "acceptance gates."
        ),
        "row_count": len(rows),
        "required_stress_classes": list(REQUIRED_STRESS_CLASSES),
        "required_stress_classes_present": not missing_classes,
        "missing_stress_classes": missing_classes,
        "stress_class_counts": _counts(row.get("stress_class", "") for row in rows),
        "source_treatment_counts": _counts(
            row.get("source_treatment", "") for row in rows
        ),
        "implementation_status_counts": _counts(
            row.get("implementation_status", "") for row in rows
        ),
        "review_required_count": review_required_count,
        "missing_runtime_hook_count": missing_runtime_hook_count,
        "unresolved_linked_artifact_count": unresolved_linked_artifact_count,
        "rail_source_decision_blocker_count": len(source_decision_blockers),
        "publication_ready": False,
        "final_study_ready": False,
        "can_mark_complete": False,
        "can_support_publication_gate": False,
        "can_support_final_study_gate": False,
        "can_support_rail_evidence_gate": False,
        "can_support_acceptance_gate": False,
        "formal_acceptance_evidence": False,
        "inputs": {
            "policy_alternatives": _display_path(DEFAULT_POLICY_ALTERNATIVES_PATH),
            "disruption_scenarios": _display_path(DEFAULT_DISRUPTION_SCENARIOS_PATH),
            "sensitivity_design": _display_path(DEFAULT_SENSITIVITY_DESIGN_PATH),
            "rail_source_decision_manifest": _display_path(
                rail_source_decision_manifest_path
            ),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "review whether each rail stress class is scenario-only, sensitivity-only, source-backed, or excluded",
            "replace capacity and availability proxy rows with source-backed evidence before release-scope rail claims",
            "keep station-access degradation separate from rail-service outage claims",
            "rerun rail, publication-readiness, and final-study audits after evidence changes",
        ],
        "remaining_blockers": [
            "rail transit stress profiles are scenario/sensitivity review support only",
            "capacity and availability profiles require reviewer decisions before release-scope rail claims",
            *[f"rail source decision: {item}" for item in source_decision_blockers],
            *[
                f"missing rail stress class: {stress_class}"
                for stress_class in missing_classes
            ],
            *row_integrity_blockers,
        ],
    }


def build_rail_transit_stress_profile_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown documentation for rail/transit stress profiles."""

    lines = [
        "# Rail Transit Stress Profile Packet",
        "",
        str(manifest.get("claim_boundary", RAIL_TRANSIT_STRESS_PROFILE_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Final-study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Can support publication gate: `{str(manifest.get('can_support_publication_gate', False)).lower()}`",
        f"- Can support final-study gate: `{str(manifest.get('can_support_final_study_gate', False)).lower()}`",
        f"- Can support rail evidence gate: `{str(manifest.get('can_support_rail_evidence_gate', False)).lower()}`",
        f"- Can support acceptance gate: `{str(manifest.get('can_support_acceptance_gate', False)).lower()}`",
        f"- Formal acceptance evidence: `{str(manifest.get('formal_acceptance_evidence', False)).lower()}`",
        "- Stress-profile rows populated for coverage taxonomy only: "
        f"`{str(manifest.get('required_stress_classes_present', False)).lower()}`",
        f"- Rows: {manifest.get('row_count', 0)}",
        "",
        "## Stress Profiles",
        "",
        "| Profile | Class | Treatment | Runtime Hook | Artifact | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {profile} | {klass} | {treatment} | {hook} | {artifact} | {status} |".format(
                profile=_cell(row.get("profile_id", "")),
                klass=_cell(row.get("stress_class", "")),
                treatment=_cell(row.get("source_treatment", "")),
                hook=_cell(row.get("runtime_hook_type", "")),
                artifact=_cell(
                    f"{row.get('linked_artifact', '')}#{row.get('linked_artifact_key', '')}"
                ),
                status=_cell(row.get("evidence_status", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet documents stress coverage only.",
            "- It does not certify rail timing, capacity, availability, dispatch, or operational service plans.",
            "- Source-backed rail evidence and reviewer decisions are still required before release-scope rail claims.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(
    *,
    profile_id: str,
    region_id: str,
    stress_class: str,
    label: str,
    source_treatment: str,
    implementation_status: str,
    runtime_hook_type: str,
    linked_artifact: str,
    linked_artifact_key: str,
    scenario_or_policy_id: str,
    parameter_path: str,
    evidence_status: str,
    review_required: bool,
    notes: str,
) -> dict[str, str]:
    return {
        "profile_id": profile_id,
        "region_id": region_id,
        "stress_class": stress_class,
        "label": label,
        "source_treatment": source_treatment,
        "implementation_status": implementation_status,
        "runtime_hook_type": runtime_hook_type,
        "linked_artifact": linked_artifact,
        "linked_artifact_key": linked_artifact_key,
        "scenario_or_policy_id": scenario_or_policy_id,
        "parameter_path": parameter_path,
        "evidence_status": evidence_status,
        "review_required": _bool_text(review_required),
        "can_support_rail_evidence_gate": "false",
        "can_support_acceptance_gate": "false",
        "publication_ready": "false",
        "claim_boundary": RAIL_TRANSIT_STRESS_PROFILE_SCOPE,
        "notes": notes,
    }


def _status(condition: bool, status: str) -> str:
    return status if condition else "missing_runtime_hook"


def _stress_profile_integrity_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        profile = str(row.get("profile_id", "")).strip() or "unknown_profile"
        implementation_status = str(row.get("implementation_status", "")).strip()
        runtime_hook_type = str(row.get("runtime_hook_type", "")).strip()
        if implementation_status == "missing_runtime_hook":
            blockers.append(f"{profile}: missing runtime hook")
        if not runtime_hook_type:
            blockers.append(f"{profile}: blank runtime hook")
        blockers.extend(_linked_artifact_blockers(profile, row))
    return blockers


def _linked_artifact_blockers(
    profile: str,
    row: Mapping[str, str],
) -> list[str]:
    artifact_text = str(row.get("linked_artifact", "")).strip()
    key_text = str(row.get("linked_artifact_key", "")).strip()
    if not artifact_text:
        return [f"{profile}: blank linked artifact"]
    artifact_path = Path(artifact_text)
    if not artifact_path.is_absolute():
        artifact_path = PROJECT_ROOT / artifact_path
    if not artifact_path.exists():
        return [f"{profile}: linked artifact is missing: {artifact_text}"]
    if not key_text:
        return [f"{profile}: blank linked artifact key"]
    key_column = LINKED_ARTIFACT_KEY_COLUMNS.get(artifact_path.name)
    if key_column is None:
        return []
    observed_keys = _ids_from_csv(artifact_path, key_column)
    blockers: list[str] = []
    for key in [value.strip() for value in key_text.split(";") if value.strip()]:
        if key not in observed_keys:
            blockers.append(f"{profile}: linked artifact key is missing: {key}")
    return blockers


def _ids_from_csv(path: str | Path, column: str) -> set[str]:
    filepath = Path(path)
    if not filepath.exists():
        return set()
    with filepath.open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            str(row.get(column, "")).strip()
            for row in csv.DictReader(handle)
            if str(row.get(column, "")).strip()
        }


def _read_json(path: str | Path) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        return {}
    with filepath.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _counts(values: Iterable[object]) -> dict[str, int]:
    return dict(sorted(Counter(str(value).strip() or "blank" for value in values).items()))


def _is_true(value: object) -> bool:
    return str(value).strip().lower() == "true"


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


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
    "DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_DOC_PATH",
    "DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH",
    "DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH",
    "RAIL_TRANSIT_STRESS_PROFILE_COLUMNS",
    "RAIL_TRANSIT_STRESS_PROFILE_SCOPE",
    "REQUIRED_STRESS_CLASSES",
    "build_rail_transit_stress_profile_manifest",
    "build_rail_transit_stress_profile_markdown",
    "build_rail_transit_stress_profile_rows",
    "write_rail_transit_stress_profile_packet",
]
