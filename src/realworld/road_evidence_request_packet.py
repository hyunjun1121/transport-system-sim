"""Road evidence source-request packet generation.

The current road-evidence blocker requires reviewed source inputs, not a
renamed draft override table. This module writes a small source-request
worksheet that names the missing source packages, candidate cache outputs,
review commands, and evidence fields required before road speed, capacity,
background-traffic, disruption, and override-application claims can be
strengthened.

The packet does not fetch live data, does not create ``road_class_overrides.csv``,
and does not upgrade road-calibration claims.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.road_evidence_review_packet import (
    DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    build_road_evidence_review_rows,
)
from src.realworld.road_override_audit import DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_evidence_source_request_packet.csv"
)
DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_evidence_source_request_manifest.json"
)
DEFAULT_REGION_ID = "songpa_public_demo"
ROAD_EVIDENCE_SOURCE_REQUEST_SCOPE = (
    "Road evidence source-request packet; not reviewed speed evidence, "
    "not calibrated capacity evidence, not accepted disruption evidence, "
    "not applied road-class overrides, and not operational routing evidence."
)
ROAD_EVIDENCE_SOURCE_REQUEST_COLUMNS: tuple[str, ...] = (
    "request_id",
    "region_id",
    "evidence_fields",
    "source_type",
    "source_name",
    "source_url_or_citation",
    "required_external_input",
    "prioritized_highway_classes",
    "review_priority_basis",
    "source_cache_path",
    "raw_payload_path",
    "fetch_or_acquisition_command",
    "derive_or_review_command",
    "target_output_path",
    "expected_source_status",
    "expected_derived_fields",
    "can_close_road_evidence_gate",
    "can_close_road_application_gate",
    "publication_use_status",
    "claim_boundary",
    "notes",
)


def build_road_evidence_source_request_rows(
    *,
    review_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    draft_override_path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
    region_id: str = DEFAULT_REGION_ID,
) -> list[dict[str, str]]:
    """Return exact source-request rows for the current pilot road evidence gap."""

    resolved_region_id = _clean_region_id(region_id)
    review_rows = _load_or_build_review_rows(review_packet_path)
    high_priority = _priority_classes(review_rows, priority="high")
    all_priority = _priority_classes(review_rows, priority=None)
    high_text = ";".join(high_priority)
    all_text = ";".join(all_priority)
    basis = _review_basis(review_rows)

    return [
        _row(
            request_id="road_speed_limit_source_request",
            evidence_fields="free_flow_speed;speed_limit",
            source_type="public_speed_limit_or_benchmark_source_required",
            source_name="Reviewed OSM maxspeed extract, public speed-limit source, or routing benchmark",
            source_url_or_citation="data/parameters/road_speed_evidence_candidates.csv",
            required_external_input=(
                "reviewed speed-limit evidence for high-priority road classes; "
                "fallback classes must be explicitly accepted as assumptions"
            ),
            prioritized_highway_classes=high_text,
            review_priority_basis=basis,
            source_cache_path="data/parameters/road_speed_evidence_candidates.csv",
            raw_payload_path="data/cache/pilot_region_road.graphml",
            fetch_or_acquisition_command=(
                ".\\.venv\\Scripts\\python scripts\\write_road_speed_evidence.py"
            ),
            derive_or_review_command=(
                "review speed candidates, public speed-limit sources, or benchmark "
                "calibration notes before editing data\\parameters\\road_class_overrides.csv"
            ),
            target_output_path="data/parameters/road_class_overrides.csv",
            expected_source_status="source_backed_or_benchmark_calibrated_speed",
            expected_derived_fields="speed_kph",
            can_close_road_evidence_gate=False,
            can_close_road_application_gate=False,
            publication_use_status="speed source support only; does not close capacity or disruption evidence",
            notes=(
                "Sparse cached maxspeed tags are review support. Do not treat mapper "
                "fallback speeds as calibrated road speeds."
            ),
            region_id=resolved_region_id,
        ),
        _row(
            request_id="road_capacity_lane_count_source_request",
            evidence_fields="capacity;lanes;road_class_capacity",
            source_type="traffic_count_or_capacity_reference_required",
            source_name="Reviewed lane counts, traffic counts, or literature/agency capacity reference",
            source_url_or_citation="data/parameters/road_capacity_evidence_candidates.csv",
            required_external_input=(
                "reviewed lane-count coverage, traffic counts, agency road-class "
                "capacity table, or literature capacity proxy"
            ),
            prioritized_highway_classes=all_text,
            review_priority_basis=basis,
            source_cache_path="data/parameters/road_capacity_evidence_candidates.csv",
            raw_payload_path="data/cache/pilot_region_road.graphml",
            fetch_or_acquisition_command=(
                ".\\.venv\\Scripts\\python scripts\\write_road_capacity_evidence.py"
            ),
            derive_or_review_command=(
                "review lane/capacity evidence and replace draft capacity values in "
                "data\\parameters\\road_class_overrides.csv"
            ),
            target_output_path="data/parameters/road_class_overrides.csv",
            expected_source_status="source_backed_or_literature_derived_capacity",
            expected_derived_fields="capacity_veh_per_hr",
            can_close_road_evidence_gate=False,
            can_close_road_application_gate=False,
            publication_use_status="capacity source support only; does not close speed or disruption evidence",
            notes=(
                "Current cached lane evidence has zero parseable lane rows, so capacity "
                "must come from another reviewed source or accepted sensitivity boundary."
            ),
            region_id=resolved_region_id,
        ),
        _row(
            request_id="road_background_traffic_benchmark_request",
            evidence_fields="background_traffic;free_flow_time;route_time_plausibility",
            source_type="routing_or_observed_traffic_benchmark_required",
            source_name="Reviewed route benchmark or observed traffic-speed source",
            source_url_or_citation="data/validation/external_route_benchmarks.csv; data/validation/validation_summary.md",
            required_external_input=(
                "reviewed OSRM/Valhalla/routingpy/R5/OTP/UXsim benchmark decision, "
                "observed speed source, or explicit background-traffic sensitivity treatment"
            ),
            prioritized_highway_classes=high_text,
            review_priority_basis=basis,
            source_cache_path="data/validation/external_route_benchmarks.csv",
            raw_payload_path="data/validation/external_route_benchmarks_osrm.csv",
            fetch_or_acquisition_command=(
                ".\\.venv\\Scripts\\python scripts\\run_plausibility_validation.py"
            ),
            derive_or_review_command=(
                "review benchmark status and decide whether background traffic remains "
                "sensitivity-only or becomes benchmark-calibrated"
            ),
            target_output_path="data/parameters/parameter_sources.csv",
            expected_source_status="benchmark_calibrated_or_sensitivity_only",
            expected_derived_fields="background_traffic_multiplier;free_flow_time",
            can_close_road_evidence_gate=False,
            can_close_road_application_gate=False,
            publication_use_status="benchmark plausibility support only; benchmark is not ground truth",
            notes=(
                "This supports plausibility and background-traffic treatment. It does "
                "not by itself calibrate traffic assignment or spillback."
            ),
            region_id=resolved_region_id,
        ),
        _row(
            request_id="road_disruption_probability_source_request",
            evidence_fields="base_disruption_probability;capacity_reduction;blockage_rule",
            source_type="hazard_incident_or_reviewed_scenario_source_required",
            source_name="Reviewed hazard, incident, exposure, or scenario-rule source",
            source_url_or_citation="data/scenarios/disruption_scenarios.csv",
            required_external_input=(
                "public hazard/exposure layer, incident history, literature rule, or "
                "explicitly reviewed scenario-only disruption treatment"
            ),
            prioritized_highway_classes=all_text,
            review_priority_basis=basis,
            source_cache_path="data/scenarios/disruption_scenarios.csv",
            raw_payload_path="data/validation/accessibility_loss.csv",
            fetch_or_acquisition_command=(
                ".\\.venv\\Scripts\\python scripts\\run_accessibility_loss_analysis.py"
            ),
            derive_or_review_command=(
                "review disruption scenario rules and replace draft base_p_fail values "
                "or mark them as accepted sensitivity-only assumptions"
            ),
            target_output_path="data/parameters/road_class_overrides.csv",
            expected_source_status="hazard_source_backed_or_reviewed_scenario_rule",
            expected_derived_fields="base_p_fail;capacity_reduction_factor;blockage_rule",
            can_close_road_evidence_gate=False,
            can_close_road_application_gate=False,
            publication_use_status="disruption-source support only; scenario-based disruptions are not observed outcomes",
            notes=(
                "Current base disruption probabilities are mapper defaults. Final claims "
                "need reviewed source-backed or explicitly sensitivity-only treatment."
            ),
            region_id=resolved_region_id,
        ),
        _row(
            request_id="reviewed_road_class_override_application_request",
            evidence_fields="speed;capacity;base_disruption;override_application",
            source_type="reviewed_override_table_and_manifest_application_required",
            source_name="Reviewed road_class_overrides.csv plus accepted pilot manifest",
            source_url_or_citation="docs/schemas/road_class_override_schema.md",
            required_external_input=(
                "reviewed road_class_overrides.csv with strong source classes; "
                "rerun pilot outputs with --road-class-overrides-path; reviewer acceptance"
            ),
            prioritized_highway_classes=all_text,
            review_priority_basis=basis,
            source_cache_path=str(Path(draft_override_path).as_posix()),
            raw_payload_path="",
            fetch_or_acquisition_command=(
                ".\\.venv\\Scripts\\python scripts\\write_road_class_override_template.py "
                "--output data\\parameters\\road_class_overrides_draft.csv --overwrite"
            ),
            derive_or_review_command=(
                ".\\.venv\\Scripts\\python scripts\\run_pilot_experiments.py --full "
                "--road-class-overrides-path data\\parameters\\road_class_overrides.csv"
            ),
            target_output_path="data/parameters/road_class_overrides.csv; results/realworld_pilot/pilot_full_manifest.json",
            expected_source_status="reviewed_override_table_applied_to_manifest",
            expected_derived_fields="speed_kph;capacity_veh_per_hr;base_p_fail;road_class_overrides_sha256",
            can_close_road_evidence_gate=True,
            can_close_road_application_gate=True,
            publication_use_status="candidate road gate closure path after reviewed table and accepted rerun",
            notes=(
                "This row names the closure path. The request packet itself is not the "
                "reviewed override table and does not close any gate."
            ),
            region_id=resolved_region_id,
        ),
    ]


def write_road_evidence_source_request_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH,
    review_packet_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    draft_override_path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
) -> dict[str, Any]:
    """Write road evidence source-request rows and a conservative manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ROAD_EVIDENCE_SOURCE_REQUEST_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    gate_candidates = [
        row
        for row in rows
        if str(row.get("can_close_road_evidence_gate", "")).lower() == "true"
    ]
    application_candidates = [
        row
        for row in rows
        if str(row.get("can_close_road_application_gate", "")).lower() == "true"
    ]
    region_ids = sorted(
        {
            str(row.get("region_id", "")).strip()
            for row in rows
            if str(row.get("region_id", "")).strip()
        }
    )
    value = {
        "schema_version": 1,
        "result_scope": ROAD_EVIDENCE_SOURCE_REQUEST_SCOPE,
        "inputs": {
            "road_evidence_review_packet": _display_path(review_packet_path),
            "road_class_overrides_draft": _display_path(draft_override_path),
        },
        "outputs": {
            "road_evidence_source_request_packet": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "region_ids": region_ids,
        "source_type_counts": _counts(row["source_type"] for row in rows),
        "evidence_field_counts": _field_counts(row["evidence_fields"] for row in rows),
        "road_evidence_closure_candidate_count": len(gate_candidates),
        "road_application_closure_candidate_count": len(application_candidates),
        "requires_reviewed_external_input_count": sum(
            1
            for row in rows
            if "required" in row["source_type"] or "reviewed" in row["source_type"]
        ),
        "publication_ready": False,
        "claim_boundary": (
            "This packet identifies required road-evidence sources and review "
            "commands. It does not contain reviewed speed observations, traffic "
            "counts, capacity calibration, accepted disruption probabilities, "
            "or proof that overrides were applied to final outputs."
        ),
        "review_items": [
            "collect source-backed or explicitly accepted sensitivity evidence for speed, capacity, background traffic, and disruption rules",
            "move reviewed values into data/parameters/road_class_overrides.csv only after source review",
            "rerun pilot experiments with the reviewed override table and verify manifest SHA256 application",
            "rerun road, publication-readiness, and final-study-readiness audits after road evidence changes",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _row(
    *,
    request_id: str,
    evidence_fields: str,
    source_type: str,
    source_name: str,
    source_url_or_citation: str,
    required_external_input: str,
    prioritized_highway_classes: str,
    review_priority_basis: str,
    source_cache_path: str,
    raw_payload_path: str,
    fetch_or_acquisition_command: str,
    derive_or_review_command: str,
    target_output_path: str,
    expected_source_status: str,
    expected_derived_fields: str,
    can_close_road_evidence_gate: bool,
    can_close_road_application_gate: bool,
    publication_use_status: str,
    notes: str,
    region_id: str = DEFAULT_REGION_ID,
) -> dict[str, str]:
    return {
        "request_id": request_id,
        "region_id": region_id,
        "evidence_fields": evidence_fields,
        "source_type": source_type,
        "source_name": source_name,
        "source_url_or_citation": source_url_or_citation,
        "required_external_input": required_external_input,
        "prioritized_highway_classes": prioritized_highway_classes,
        "review_priority_basis": review_priority_basis,
        "source_cache_path": source_cache_path,
        "raw_payload_path": raw_payload_path,
        "fetch_or_acquisition_command": fetch_or_acquisition_command,
        "derive_or_review_command": derive_or_review_command,
        "target_output_path": target_output_path,
        "expected_source_status": expected_source_status,
        "expected_derived_fields": expected_derived_fields,
        "can_close_road_evidence_gate": str(can_close_road_evidence_gate).lower(),
        "can_close_road_application_gate": str(can_close_road_application_gate).lower(),
        "publication_use_status": publication_use_status,
        "claim_boundary": ROAD_EVIDENCE_SOURCE_REQUEST_SCOPE,
        "notes": notes,
    }


def _clean_region_id(region_id: str) -> str:
    text = str(region_id).strip()
    if not text:
        raise ValueError("region_id must be non-empty")
    return text


def _load_or_build_review_rows(path: str | Path) -> list[dict[str, str]]:
    packet = Path(path)
    if not packet.exists():
        return build_road_evidence_review_rows()
    with packet.open("r", encoding="utf-8", newline="") as handle:
        return [
            {str(key): str(value or "") for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def _priority_classes(
    rows: Sequence[Mapping[str, str]],
    *,
    priority: str | None,
) -> list[str]:
    values: list[str] = []
    for row in rows:
        if priority is not None and row.get("review_priority") != priority:
            continue
        highway = str(row.get("highway", "")).strip()
        if highway:
            values.append(highway)
    return values


def _review_basis(rows: Sequence[Mapping[str, str]]) -> str:
    high = len(_priority_classes(rows, priority="high"))
    medium = len(_priority_classes(rows, priority="medium"))
    weak = sum(
        1
        for row in rows
        if str(row.get("weak_for_final_claim", "")).lower() == "true"
    )
    return (
        f"road_evidence_review_packet rows={len(rows)}; "
        f"high_priority={high}; medium_priority={medium}; weak_rows={weak}"
    )


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


def _display_path(path: str | Path) -> str:
    value = Path(path)
    try:
        return value.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return value.as_posix()


__all__ = [
    "DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH",
    "DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH",
    "ROAD_EVIDENCE_SOURCE_REQUEST_COLUMNS",
    "ROAD_EVIDENCE_SOURCE_REQUEST_SCOPE",
    "build_road_evidence_source_request_rows",
    "write_road_evidence_source_request_packet",
]
