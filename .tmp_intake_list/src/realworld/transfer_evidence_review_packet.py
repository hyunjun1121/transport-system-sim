"""Transfer-delay evidence review packet.

This packet makes the current transfer-delay assumptions auditable. It is a
review aid only: it does not provide observed station transfer timing, certify
station layouts, accept transfer parameters, or close parameter evidence gates.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

from src.realworld.rail_station_binding import (
    DEFAULT_RAIL_STATION_BINDING_PATH,
    load_rail_station_bindings,
    summarize_rail_station_bindings,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.yaml"
DEFAULT_PARAMETER_SOURCES_PATH = PROJECT_ROOT / "data" / "parameters" / "parameter_sources.csv"
DEFAULT_SENSITIVITY_DESIGN_PATH = PROJECT_ROOT / "data" / "scenarios" / "sensitivity_design.csv"
DEFAULT_REGION_PATH = PROJECT_ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_TRANSFER_EVIDENCE_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "transfer_evidence_review_packet.csv"
)
DEFAULT_TRANSFER_EVIDENCE_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "transfer_evidence_review_manifest.json"
)
DEFAULT_TRANSFER_EVIDENCE_REVIEW_DOC_PATH = (
    PROJECT_ROOT / "docs" / "transfer_evidence_review_packet.md"
)
TRANSFER_EVIDENCE_REVIEW_SCOPE = (
    "Transfer evidence review packet only; not observed transfer timing, not "
    "station-layout validation, not accepted transfer calibration, not "
    "weak-parameter acceptance, and not operational routing evidence."
)
TRANSFER_EVIDENCE_REVIEW_COLUMNS: tuple[str, ...] = (
    "review_item_id",
    "region_id",
    "evidence_group",
    "transfer_component",
    "current_value",
    "unit",
    "evidence_status",
    "source_status",
    "source_artifact_status",
    "review_priority",
    "weak_for_final_claim",
    "current_source",
    "candidate_artifacts",
    "recommended_upgrade",
    "publication_use_status",
    "claim_boundary",
    "notes",
)


def build_transfer_evidence_review_rows(
    *,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    parameter_sources_path: str | Path = DEFAULT_PARAMETER_SOURCES_PATH,
    sensitivity_design_path: str | Path = DEFAULT_SENSITIVITY_DESIGN_PATH,
    region_path: str | Path = DEFAULT_REGION_PATH,
    station_binding_path: str | Path = DEFAULT_RAIL_STATION_BINDING_PATH,
) -> list[dict[str, str]]:
    """Return conservative transfer-delay review rows for the pilot region."""

    config = _read_yaml_mapping(config_path)
    region = _read_yaml_mapping(region_path)
    parameters = _read_csv_by_key(parameter_sources_path, "parameter")
    sensitivity = _read_csv_by_key(sensitivity_design_path, "parameter_id")
    station_records = load_rail_station_bindings(station_binding_path)
    station_summary = summarize_rail_station_bindings(station_records)
    access = _preferred_station_text(station_records, point_id="S", preferred_codes=("936",))
    egress = _preferred_station_text(station_records, point_id="R", preferred_codes=("814",))
    region_id = str(region.get("region_id", "songpa_public_demo"))
    multimodal = config.get("multimodal", {}) if isinstance(config.get("multimodal"), Mapping) else {}
    transfer_fixed = _clean_number(multimodal.get("transfer_time_min", ""))
    transfer_per_passenger = _clean_number(multimodal.get("transfer_per_passenger_min", ""))

    fixed_row = parameters.get("transfer_fixed_delay", {})
    per_row = parameters.get("transfer_per_passenger_delay", {})
    fixed_sensitivity = sensitivity.get("transfer_fixed_delay", {})
    per_sensitivity = sensitivity.get("transfer_per_passenger_delay", {})

    return [
        _row(
            review_item_id="transfer_delay_parameter_trace",
            region_id=region_id,
            evidence_group="parameter_trace",
            transfer_component="fixed_and_per_passenger_delay",
            current_value=(
                f"fixed={transfer_fixed} min; "
                f"per_passenger={transfer_per_passenger} min/pax"
            ),
            unit="min; min/pax",
            evidence_status="documented_parameter_proxy",
            source_status="config_and_parameter_sources_present",
            source_artifact_status="review_inputs_present",
            review_priority="high",
            weak_for_final_claim="true",
            current_source=_join_paths((config_path, parameter_sources_path)),
            candidate_artifacts=_join_paths((parameter_sources_path, sensitivity_design_path)),
            recommended_upgrade=(
                "replace or bound transfer delay rows with reviewed station-layout, "
                "observed transfer, pedestrian-flow, or explicit sensitivity evidence"
            ),
            publication_use_status="transfer_assumption_trace_only",
            notes=(
                "Current transfer delay is applied to shuttle-arrival batches before "
                "rail boarding; it is not observed station dwell or circulation time."
            ),
        ),
        _row(
            review_item_id="transfer_sensitivity_bounds",
            region_id=region_id,
            evidence_group="sensitivity_bounds",
            transfer_component="transfer_delay_uncertainty",
            current_value=(
                "fixed_default={fixed_default}; fixed_range={fixed_min}-{fixed_max}; "
                "per_passenger_default={per_default}; per_passenger_range={per_min}-{per_max}"
            ).format(
                fixed_default=_first_field(fixed_sensitivity, ("baseline", "default_value")),
                fixed_min=_first_field(fixed_sensitivity, ("low", "min_value")),
                fixed_max=_first_field(fixed_sensitivity, ("high", "max_value")),
                per_default=_first_field(per_sensitivity, ("baseline", "default_value")),
                per_min=_first_field(per_sensitivity, ("low", "min_value")),
                per_max=_first_field(per_sensitivity, ("high", "max_value")),
            ),
            unit="min; min/pax",
            evidence_status="sensitivity_bounds_present",
            source_status="sensitivity_only",
            source_artifact_status="sensitivity_design_present",
            review_priority="medium",
            weak_for_final_claim="true",
            current_source=_display_path(sensitivity_design_path),
            candidate_artifacts=_join_paths((sensitivity_design_path, parameter_sources_path)),
            recommended_upgrade=(
                "confirm whether sensitivity bounds are sufficient for final claims "
                "or replace them with source-backed transfer timing evidence"
            ),
            publication_use_status="sensitivity_bounds_only_not_transfer_calibration",
            notes=(
                "Sensitivity bounds expose uncertainty but do not validate the baseline "
                "fixed delay or disabled per-passenger delay."
            ),
        ),
        _row(
            review_item_id="transfer_access_station_context",
            region_id=region_id,
            evidence_group="station_context",
            transfer_component="rail_access_station",
            current_value=access,
            unit="station binding",
            evidence_status="public_station_context_present",
            source_status="official_station_code_bound",
            source_artifact_status="station_binding_cache_committed",
            review_priority="medium",
            weak_for_final_claim="true",
            current_source=_join_paths((region_path, station_binding_path)),
            candidate_artifacts=_join_paths((station_binding_path, parameter_sources_path)),
            recommended_upgrade=(
                "review access-station transfer path, walking speed, vertical "
                "circulation, and crowding assumptions before final transfer claims"
            ),
            publication_use_status="station_context_only_not_transfer_timing",
            notes=(
                "Station binding identifies the public station context but does not "
                "measure feeder drop-off to platform transfer time."
            ),
        ),
        _row(
            review_item_id="transfer_egress_station_context",
            region_id=region_id,
            evidence_group="station_context",
            transfer_component="rail_egress_station",
            current_value=egress,
            unit="station binding",
            evidence_status="public_station_context_present",
            source_status="official_station_code_bound",
            source_artifact_status="station_binding_cache_committed",
            review_priority="medium",
            weak_for_final_claim="true",
            current_source=_join_paths((region_path, station_binding_path)),
            candidate_artifacts=_join_paths((station_binding_path, parameter_sources_path)),
            recommended_upgrade=(
                "review egress-station circulation and last-mile boarding assumptions "
                "if transfer handling is extended beyond pre-rail boarding"
            ),
            publication_use_status="station_context_only_not_transfer_timing",
            notes=(
                "The current simulator applies the configured transfer delay before "
                "rail boarding; this row keeps the egress station context visible."
            ),
        ),
        _row(
            review_item_id="transfer_station_layout_or_observation_gap",
            region_id=region_id,
            evidence_group="remaining_source_gap",
            transfer_component="station_layout_or_observed_transfer_time",
            current_value="absent",
            unit="source artifact",
            evidence_status="missing_station_layout_or_observed_transfer_source",
            source_status="source_gap",
            source_artifact_status="no_station_layout_or_observed_transfer_artifact",
            review_priority="high",
            weak_for_final_claim="true",
            current_source=_join_paths((fixed_row.get("source_url_or_citation", ""), per_row.get("source_url_or_citation", ""))),
            candidate_artifacts=(
                "reviewed station-layout source; observed transfer range; "
                "pedestrian-flow literature; data/parameters/parameter_acceptance.csv"
            ),
            recommended_upgrade=(
                "supply reviewed station-layout, field-observation, pedestrian-flow "
                "literature, or explicit weak-parameter acceptance before final claims"
            ),
            publication_use_status="blocking_gap_for_transfer_calibration_claims",
            notes=(
                "This row intentionally preserves the unresolved source gap even "
                "though transfer model values and station context are now traceable."
            ),
        ),
    ]


def write_transfer_evidence_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_TRANSFER_EVIDENCE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_TRANSFER_EVIDENCE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_TRANSFER_EVIDENCE_REVIEW_DOC_PATH,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    parameter_sources_path: str | Path = DEFAULT_PARAMETER_SOURCES_PATH,
    sensitivity_design_path: str | Path = DEFAULT_SENSITIVITY_DESIGN_PATH,
    region_path: str | Path = DEFAULT_REGION_PATH,
    station_binding_path: str | Path = DEFAULT_RAIL_STATION_BINDING_PATH,
) -> dict[str, Any]:
    """Write transfer-evidence review CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRANSFER_EVIDENCE_REVIEW_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {column: str(row.get(column, "")) for column in TRANSFER_EVIDENCE_REVIEW_COLUMNS}
            )

    summary = build_transfer_evidence_review_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        config_path=config_path,
        parameter_sources_path=parameter_sources_path,
        sensitivity_design_path=sensitivity_design_path,
        region_path=region_path,
        station_binding_path=station_binding_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_transfer_evidence_review_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_transfer_evidence_review_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_TRANSFER_EVIDENCE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_TRANSFER_EVIDENCE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_TRANSFER_EVIDENCE_REVIEW_DOC_PATH,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    parameter_sources_path: str | Path = DEFAULT_PARAMETER_SOURCES_PATH,
    sensitivity_design_path: str | Path = DEFAULT_SENSITIVITY_DESIGN_PATH,
    region_path: str | Path = DEFAULT_REGION_PATH,
    station_binding_path: str | Path = DEFAULT_RAIL_STATION_BINDING_PATH,
) -> dict[str, Any]:
    """Return a non-accepting manifest for transfer evidence review."""

    blocking_count = sum(
        1
        for row in rows
        if str(row.get("evidence_status", "")).startswith("missing_")
        or str(row.get("source_artifact_status", "")).startswith("no_")
    )
    human_review_count = len(rows) - blocking_count
    return {
        "schema_version": 1,
        "result_scope": TRANSFER_EVIDENCE_REVIEW_SCOPE,
        "claim_boundary": (
            "This packet traces transfer-delay assumptions, sensitivity bounds, "
            "and station context. It does not supply observed transfer timing, "
            "station-layout validation, pedestrian-flow calibration, or accepted "
            "weak-parameter decisions."
        ),
        "row_count": len(rows),
        "blocking_review_count": blocking_count,
        "human_review_count": human_review_count,
        "review_priority_counts": _counts(row.get("review_priority", "") for row in rows),
        "evidence_status_counts": _counts(row.get("evidence_status", "") for row in rows),
        "source_artifact_status_counts": _counts(
            row.get("source_artifact_status", "") for row in rows
        ),
        "weak_for_final_claim_count": sum(
            1 for row in rows if str(row.get("weak_for_final_claim", "")).lower() == "true"
        ),
        "transfer_source_artifact_present": True,
        "parameter_evidence_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "config": _display_path(config_path),
            "parameter_sources": _display_path(parameter_sources_path),
            "sensitivity_design": _display_path(sensitivity_design_path),
            "region": _display_path(region_path),
            "rail_station_bindings": _display_path(station_binding_path),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "remaining_blockers": [
            "station-layout, observed transfer, or pedestrian-flow source artifact is still absent",
            "transfer delay values remain weak assumptions until source-backed review or explicit weak-parameter acceptance",
            "formal parameter_acceptance.csv is absent",
        ],
        "review_items": [
            "review whether current fixed and per-passenger transfer delay values are bounded scenario assumptions or must be replaced",
            "supply station-layout, observed transfer, pedestrian-flow literature, or field-review evidence before calibrated transfer claims",
            "keep station binding separate from station transfer timing evidence",
            "rerun parameter source-readiness and final-study audits after transfer evidence changes",
        ],
    }


def build_transfer_evidence_review_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for the transfer-evidence review packet."""

    lines = [
        "# Transfer Evidence Review Packet",
        "",
        str(manifest.get("claim_boundary", TRANSFER_EVIDENCE_REVIEW_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Rows: {manifest.get('row_count', 0)}",
        f"- Blocking review rows: {manifest.get('blocking_review_count', 0)}",
        f"- Human-review rows: {manifest.get('human_review_count', 0)}",
        "",
        "## Review Rows",
        "",
        "| Item | Status | Current Value | Required Upgrade |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {item} | {status} | {value} | {upgrade} |".format(
                item=_cell(row.get("review_item_id", "")),
                status=_cell(row.get("evidence_status", "")),
                value=_cell(row.get("current_value", "")),
                upgrade=_cell(row.get("recommended_upgrade", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is review support, not transfer calibration.",
            "- Station binding does not measure platform, vertical-circulation, crowding, or boarding delay.",
            "- Keep final transfer claims blocked until source-backed review or formal weak-parameter acceptance exists.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(**values: str) -> dict[str, str]:
    row = {column: "" for column in TRANSFER_EVIDENCE_REVIEW_COLUMNS}
    row.update({key: str(value) for key, value in values.items()})
    row["claim_boundary"] = TRANSFER_EVIDENCE_REVIEW_SCOPE
    return row


def _read_yaml_mapping(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _read_csv_by_key(path: str | Path, key: str) -> dict[str, dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            str(row.get(key, "")).strip(): {str(k): str(v or "") for k, v in row.items()}
            for row in csv.DictReader(handle)
            if str(row.get(key, "")).strip()
        }


def _preferred_station_text(
    records: Sequence[object],
    *,
    point_id: str,
    preferred_codes: Sequence[str],
) -> str:
    candidates = [
        record
        for record in records
        if getattr(record, "point_id", "") == point_id
        and getattr(record, "is_official", False)
    ]
    preferred = [
        record
        for record in candidates
        if getattr(record, "station_code", "") in set(preferred_codes)
    ]
    selected = preferred[0] if preferred else (candidates[0] if candidates else None)
    if selected is None:
        return "missing official station binding"
    return (
        f"{getattr(selected, 'station_name', '')} "
        f"station_id={getattr(selected, 'station_id', '')}; "
        f"station_code={getattr(selected, 'station_code', '')}"
    )


def _clean_number(value: object) -> str:
    text = str(value).strip()
    if text.endswith(".0"):
        return text[:-2]
    return text


def _first_field(row: Mapping[str, str], keys: Sequence[str]) -> str:
    for key in keys:
        value = row.get(key, "")
        if str(value).strip():
            return str(value).strip()
    return ""


def _join_paths(values: Iterable[object]) -> str:
    parts = [_display_path(value) for value in values if str(value).strip()]
    return "; ".join(parts)


def _display_path(path: object) -> str:
    text = str(path).strip()
    if not text:
        return ""
    filepath = Path(text)
    if not filepath.exists() and (PROJECT_ROOT / filepath).exists():
        filepath = PROJECT_ROOT / filepath
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except (OSError, ValueError):
        return text


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _cell(value: object) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    return text or "-"


__all__ = [
    "DEFAULT_TRANSFER_EVIDENCE_REVIEW_DOC_PATH",
    "DEFAULT_TRANSFER_EVIDENCE_REVIEW_MANIFEST_PATH",
    "DEFAULT_TRANSFER_EVIDENCE_REVIEW_PACKET_PATH",
    "TRANSFER_EVIDENCE_REVIEW_COLUMNS",
    "TRANSFER_EVIDENCE_REVIEW_SCOPE",
    "build_transfer_evidence_review_rows",
    "write_transfer_evidence_review_packet",
]
