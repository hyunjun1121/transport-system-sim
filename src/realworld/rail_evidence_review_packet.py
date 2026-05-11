"""Rail evidence review-packet generation.

This module consolidates rail station bindings, current rail-service evidence,
rail assumptions, and available cached-derivation paths into one review
worksheet. The packet supports rail-evidence review; it is not timetable
calibration, GTFS validation, emergency rail availability evidence, or
operational routing evidence.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.rail_evidence import (
    DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
    RailServiceEvidence,
    load_rail_service_evidence,
    summarize_rail_service_evidence,
)
from src.realworld.rail_station_binding import (
    DEFAULT_RAIL_STATION_BINDING_PATH,
    RailStationBinding,
    load_rail_station_bindings,
    summarize_rail_station_bindings,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_ASSUMPTIONS_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "rail_assumptions.csv"
)
DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "rail_evidence_review_packet.csv"
)
DEFAULT_RAIL_EVIDENCE_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "rail_evidence_review_manifest.json"
)
METRO9_CAPACITY_EXTRACT_PATH = "data/rail/metro9_capacity_source_extract.csv"
METRO9_CAPACITY_RAW_PATH = "data/rail/metro9_capacity_source_raw.html"
RAIL_CAPACITY_REVIEW_ARTIFACTS = (
    "data/parameters/rail_assumptions.csv; "
    f"{METRO9_CAPACITY_EXTRACT_PATH}; "
    f"{METRO9_CAPACITY_RAW_PATH}; "
    "data/parameters/parameter_sources.csv"
)
RAIL_EVIDENCE_REVIEW_PACKET_SCOPE = (
    "Rail evidence review packet; not accepted rail-service calibration, "
    "GTFS validation, emergency rail availability evidence, or operational "
    "routing evidence."
)
RAIL_EVIDENCE_REVIEW_COLUMNS: tuple[str, ...] = (
    "review_item_id",
    "region_id",
    "evidence_group",
    "rail_component",
    "current_value",
    "unit",
    "evidence_status",
    "source_status",
    "source_artifact_status",
    "station_binding_ready",
    "service_publication_ready",
    "weak_for_final_claim",
    "review_priority",
    "current_source",
    "candidate_artifacts",
    "recommended_upgrade",
    "publication_use_status",
    "claim_boundary",
    "notes",
)


def build_rail_evidence_review_rows(
    *,
    service_evidence_path: str | Path = DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
    station_binding_path: str | Path = DEFAULT_RAIL_STATION_BINDING_PATH,
    assumptions_path: str | Path = DEFAULT_RAIL_ASSUMPTIONS_PATH,
    required_points: Sequence[str] = ("S", "R"),
) -> list[dict[str, str]]:
    """Return rail-evidence review rows for the current pilot inputs."""

    service_records = load_rail_service_evidence(service_evidence_path)
    service_summary = summarize_rail_service_evidence(service_records)
    station_records = load_rail_station_bindings(station_binding_path)
    station_summary = summarize_rail_station_bindings(
        station_records,
        required_points=required_points,
    )
    assumptions = _load_assumptions(assumptions_path)
    service_record = service_records[0]

    rows: list[dict[str, str]] = []
    rows.extend(
        _station_binding_rows(
            station_records=station_records,
            station_summary=station_summary,
            service_summary=service_summary,
            required_points=required_points,
        )
    )
    rows.extend(
        _service_value_rows(
            service_record=service_record,
            service_summary=service_summary,
            station_summary=station_summary,
            assumptions=assumptions,
        )
    )
    rows.extend(
        _service_context_rows(
            service_record=service_record,
            service_summary=service_summary,
            station_summary=station_summary,
            assumptions=assumptions,
        )
    )
    rows.extend(
        _derivation_path_rows(
            service_record=service_record,
            service_summary=service_summary,
            station_summary=station_summary,
        )
    )
    return rows


def write_rail_evidence_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_EVIDENCE_REVIEW_MANIFEST_PATH,
    service_evidence_path: str | Path = DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
    station_binding_path: str | Path = DEFAULT_RAIL_STATION_BINDING_PATH,
    assumptions_path: str | Path = DEFAULT_RAIL_ASSUMPTIONS_PATH,
) -> dict[str, Any]:
    """Write rail-evidence review rows and a conservative manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=RAIL_EVIDENCE_REVIEW_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    weak_rows = [
        row
        for row in rows
        if str(row.get("weak_for_final_claim", "")).lower() == "true"
    ]
    value = {
        "schema_version": 1,
        "result_scope": RAIL_EVIDENCE_REVIEW_PACKET_SCOPE,
        "inputs": {
            "rail_service_evidence": _display_path(service_evidence_path),
            "rail_station_bindings": _display_path(station_binding_path),
            "rail_assumptions": _display_path(assumptions_path),
            "metro9_capacity_extract": METRO9_CAPACITY_EXTRACT_PATH,
            "metro9_capacity_raw": METRO9_CAPACITY_RAW_PATH,
        },
        "outputs": {
            "rail_evidence_review_packet": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "weak_for_final_claim_count": len(weak_rows),
        "review_priority_counts": _counts(row["review_priority"] for row in rows),
        "evidence_status_counts": _counts(row["evidence_status"] for row in rows),
        "source_artifact_status_counts": _counts(
            row["source_artifact_status"] for row in rows
        ),
        "station_binding_ready": _all_bool(rows, "station_binding_ready"),
        "service_publication_ready": _all_bool(rows, "service_publication_ready"),
        "publication_ready": False,
        "claim_boundary": (
            "This packet organizes rail-evidence review. It does not derive "
            "headway or travel time from a cached timetable, GTFS feed, or "
            "shortest-path artifact, and it does not certify emergency rail "
            "availability or operational route feasibility."
        ),
        "review_items": [
            "cache and review timetable, GTFS, or shortest-path timing evidence",
            "derive headway and travel time into rail_service_evidence.csv with source artifact SHA256",
            "keep rail capacity source-backed or explicitly sensitivity-only",
            "add rail delay, unavailability, and station-access scenarios before stronger resilience claims",
            "rerun rail, publication-readiness, and final-study-readiness audits after rail evidence changes",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _station_binding_rows(
    *,
    station_records: Sequence[RailStationBinding],
    station_summary: Mapping[str, object],
    service_summary: Mapping[str, object],
    required_points: Sequence[str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    region_id = station_records[0].region_id if station_records else ""
    ready_points = set(station_summary.get("official_required_points", []))
    for point in required_points:
        point_records = [record for record in station_records if record.point_id == point]
        ready = point in ready_points
        rows.append(
            _row(
                review_item_id=f"rail_station_binding_{point}",
                region_id=region_id,
                evidence_group="station_binding",
                rail_component=f"{point}_station_binding",
                current_value=_station_current_value(point_records),
                unit="station",
                evidence_status=(
                    "official_station_code_bound" if ready else "missing_official_station_binding"
                ),
                source_status=_source_statuses(
                    record.source_status for record in point_records
                ),
                source_artifact_status=(
                    "station_binding_cache_committed"
                    if ready
                    else "station_binding_gap"
                ),
                station_binding_ready=bool(station_summary["binding_ready"]),
                service_publication_ready=bool(service_summary["publication_ready"]),
                weak_for_final_claim=not ready,
                review_priority="low" if ready else "high",
                current_source=_source_names(point_records),
                candidate_artifacts=(
                    "data/rail/pilot_station_binding_cache.csv; "
                    "data/parameters/rail_station_bindings.csv"
                ),
                recommended_upgrade=(
                    "Keep station binding reproducible and separate from rail-service timing evidence."
                    if ready
                    else "Add official station-code binding rows for the required rail point."
                ),
                publication_use_status=(
                    "station_binding_ready_not_service_timing"
                    if ready
                    else "blocked_for_station_binding"
                ),
                notes="Station binding does not certify headway, travel time, capacity, or availability.",
            )
        )
    return rows


def _service_value_rows(
    *,
    service_record: RailServiceEvidence,
    service_summary: Mapping[str, object],
    station_summary: Mapping[str, object],
    assumptions: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    derived_ready = service_summary["derived_field_ready"]
    assert isinstance(derived_ready, Mapping)
    source_artifact_status = _service_source_artifact_status(service_summary)
    return [
        _row(
            review_item_id="rail_headway",
            region_id=service_record.region_id,
            evidence_group="service_timing",
            rail_component="headway",
            current_value=_number_text(service_record.headway_min),
            unit="min",
            evidence_status=(
                "cached_timing_derived"
                if bool(derived_ready.get("headway"))
                else "missing_cached_timing_evidence"
            ),
            source_status=service_record.source_status,
            source_artifact_status=source_artifact_status,
            station_binding_ready=bool(station_summary["binding_ready"]),
            service_publication_ready=bool(service_summary["publication_ready"]),
            weak_for_final_claim=not (
                bool(derived_ready.get("headway"))
                and bool(service_summary["source_artifact_ready"])
            ),
            review_priority="high",
            current_source=_assumption_source(assumptions, "rail_headway", service_record),
            candidate_artifacts=(
                "data/parameters/rail_service_evidence.csv; "
                "docs/schemas/rail_timetable_cache_schema.md; docs/schemas/rail_gtfs_cache_schema.md"
            ),
            recommended_upgrade=(
                "Derive headway from a reviewed timetable or static GTFS cache and record artifact SHA256."
            ),
            publication_use_status="blocked_until_cached_timing_derivation",
            notes="Current fixed headway is a scenario proxy.",
        ),
        _row(
            review_item_id="rail_travel_time",
            region_id=service_record.region_id,
            evidence_group="service_timing",
            rail_component="travel_time",
            current_value=_number_text(service_record.travel_time_min),
            unit="min",
            evidence_status=(
                "cached_timing_derived"
                if bool(derived_ready.get("travel_time"))
                else "missing_cached_timing_evidence"
            ),
            source_status=service_record.source_status,
            source_artifact_status=source_artifact_status,
            station_binding_ready=bool(station_summary["binding_ready"]),
            service_publication_ready=bool(service_summary["publication_ready"]),
            weak_for_final_claim=not (
                bool(derived_ready.get("travel_time"))
                and bool(service_summary["source_artifact_ready"])
            ),
            review_priority="high",
            current_source=_assumption_source(
                assumptions,
                "rail_travel_time",
                service_record,
            ),
            candidate_artifacts=(
                "data/parameters/rail_service_evidence.csv; "
                "docs/schemas/rail_shortest_path_cache_schema.md; "
                "docs/schemas/rail_timetable_cache_schema.md; docs/schemas/rail_gtfs_cache_schema.md"
            ),
            recommended_upgrade=(
                "Derive travel time from reviewed shortest-path, timetable, or GTFS cache and record artifact SHA256."
            ),
            publication_use_status="blocked_until_cached_timing_derivation",
            notes="Current travel time is an abstract station-area service-leg proxy.",
        ),
        _row(
            review_item_id="rail_capacity",
            region_id=service_record.region_id,
            evidence_group="capacity",
            rail_component="capacity",
            current_value=_number_text(service_record.capacity_pax_per_train),
            unit="pax/train",
            evidence_status=(
                "source_backed_or_sensitivity_acknowledged"
                if bool(service_summary["capacity_sensitivity_acknowledged"])
                else "missing_capacity_evidence_or_sensitivity_acknowledgement"
            ),
            source_status=_source_status_with_assumption(
                service_record,
                assumptions,
                "rail_capacity",
            ),
            source_artifact_status="capacity_retained_as_sensitivity_axis",
            station_binding_ready=bool(station_summary["binding_ready"]),
            service_publication_ready=bool(service_summary["publication_ready"]),
            weak_for_final_claim=not bool(
                service_summary["capacity_sensitivity_acknowledged"]
            ),
            review_priority="medium",
            current_source=_assumption_source(
                assumptions,
                "rail_capacity",
                service_record,
            ),
            candidate_artifacts=RAIL_CAPACITY_REVIEW_ARTIFACTS,
            recommended_upgrade=(
                "Review the cached Metro9 capacity context, keep capacity explicitly "
                "sensitivity-only, or replace it with source-backed route-leg capacity evidence."
            ),
            publication_use_status="usable_as_sensitivity_only_not_point_calibration",
            notes=(
                "Cached Metro9 capacity context is review input only; capacity "
                "treatment does not solve missing rail timing evidence."
            ),
        ),
    ]


def _service_context_rows(
    *,
    service_record: RailServiceEvidence,
    service_summary: Mapping[str, object],
    station_summary: Mapping[str, object],
    assumptions: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    return [
        _row(
            review_item_id="rail_service_window",
            region_id=service_record.region_id,
            evidence_group="availability",
            rail_component="service_window",
            current_value=_assumption_value(assumptions, "rail_service_window"),
            unit="rule",
            evidence_status="scheduled_public_service_proxy",
            source_status=_assumption_status(assumptions, "rail_service_window"),
            source_artifact_status="no_emergency_service_artifact",
            station_binding_ready=bool(station_summary["binding_ready"]),
            service_publication_ready=bool(service_summary["publication_ready"]),
            weak_for_final_claim=True,
            review_priority="high",
            current_source=_assumption_source(
                assumptions,
                "rail_service_window",
                service_record,
            ),
            candidate_artifacts=(
                "data/parameters/rail_assumptions.csv; data/scenarios/policy_alternatives.csv"
            ),
            recommended_upgrade=(
                "Document the selected public-service window and add rail delay or unavailability scenarios."
            ),
            publication_use_status="scenario_assumption_only",
            notes="Scheduled service context is not emergency rail availability.",
        ),
        _row(
            review_item_id="rail_availability_rule",
            region_id=service_record.region_id,
            evidence_group="availability",
            rail_component="availability_rule",
            current_value=_assumption_value(assumptions, "rail_availability_rule"),
            unit="rule",
            evidence_status="uncalibrated_availability_rule",
            source_status=_assumption_status(assumptions, "rail_availability_rule"),
            source_artifact_status="no_disruption_or_availability_artifact",
            station_binding_ready=bool(station_summary["binding_ready"]),
            service_publication_ready=bool(service_summary["publication_ready"]),
            weak_for_final_claim=True,
            review_priority="high",
            current_source=_assumption_source(
                assumptions,
                "rail_availability_rule",
                service_record,
            ),
            candidate_artifacts=(
                "data/scenarios/disruption_scenarios.csv; docs/rail_evidence.md"
            ),
            recommended_upgrade=(
                "Add rail delay, partial unavailability, station access closure, and service-window scenarios."
            ),
            publication_use_status="scenario_assumption_only",
            notes="Current default rail path remains scheduled-service proxy.",
        ),
    ]


def _derivation_path_rows(
    *,
    service_record: RailServiceEvidence,
    service_summary: Mapping[str, object],
    station_summary: Mapping[str, object],
) -> list[dict[str, str]]:
    return [
        _derivation_row(
            review_item_id="rail_timetable_derivation_path",
            component="timetable_cache",
            script_path=PROJECT_ROOT / "scripts" / "derive_rail_service_evidence.py",
            doc_path=PROJECT_ROOT / "docs" / "schemas" / "rail_timetable_cache_schema.md",
            service_record=service_record,
            service_summary=service_summary,
            station_summary=station_summary,
            recommended_upgrade=(
                "Cache a reviewed station-event timetable extract and derive headway plus matched travel time."
            ),
            priority="high",
        ),
        _derivation_row(
            review_item_id="rail_gtfs_derivation_path",
            component="gtfs_cache",
            script_path=PROJECT_ROOT / "scripts" / "derive_rail_gtfs_evidence.py",
            doc_path=PROJECT_ROOT / "docs" / "schemas" / "rail_gtfs_cache_schema.md",
            service_record=service_record,
            service_summary=service_summary,
            station_summary=station_summary,
            recommended_upgrade=(
                "Commit or reference a reviewed static GTFS feed and derive headway plus stop-to-stop travel time."
            ),
            priority="medium",
        ),
        _derivation_row(
            review_item_id="rail_shortest_path_derivation_path",
            component="shortest_path_cache",
            script_path=PROJECT_ROOT / "scripts" / "derive_rail_shortest_path_evidence.py",
            doc_path=PROJECT_ROOT / "docs" / "schemas" / "rail_shortest_path_cache_schema.md",
            service_record=service_record,
            service_summary=service_summary,
            station_summary=station_summary,
            recommended_upgrade=(
                "Cache a reviewed station-to-station shortest-path extract for travel time, then pair it with headway evidence."
            ),
            priority="high",
        ),
    ]


def _derivation_row(
    *,
    review_item_id: str,
    component: str,
    script_path: Path,
    doc_path: Path,
    service_record: RailServiceEvidence,
    service_summary: Mapping[str, object],
    station_summary: Mapping[str, object],
    recommended_upgrade: str,
    priority: str,
) -> dict[str, str]:
    path_available = script_path.exists() and doc_path.exists()
    return _row(
        review_item_id=review_item_id,
        region_id=service_record.region_id,
        evidence_group="derivation_path",
        rail_component=component,
        current_value="available" if path_available else "missing",
        unit="code_path",
        evidence_status=(
            "derivation_path_available_no_default_cache"
            if path_available
            else "derivation_path_missing"
        ),
        source_status="repository_derivation_code",
        source_artifact_status="no_reviewed_default_source_cache",
        station_binding_ready=bool(station_summary["binding_ready"]),
        service_publication_ready=bool(service_summary["publication_ready"]),
        weak_for_final_claim=True,
        review_priority=priority,
        current_source=f"{_display_path(script_path)}; {_display_path(doc_path)}",
        candidate_artifacts=f"{_display_path(script_path)}; {_display_path(doc_path)}",
        recommended_upgrade=recommended_upgrade,
        publication_use_status="derivation_path_only_not_evidence",
        notes="A parser or derivation script does not create evidence until a reviewed source cache is committed.",
    )


def _row(
    *,
    review_item_id: str,
    region_id: str,
    evidence_group: str,
    rail_component: str,
    current_value: str,
    unit: str,
    evidence_status: str,
    source_status: str,
    source_artifact_status: str,
    station_binding_ready: bool,
    service_publication_ready: bool,
    weak_for_final_claim: bool,
    review_priority: str,
    current_source: str,
    candidate_artifacts: str,
    recommended_upgrade: str,
    publication_use_status: str,
    notes: str,
) -> dict[str, str]:
    return {
        "review_item_id": review_item_id,
        "region_id": region_id,
        "evidence_group": evidence_group,
        "rail_component": rail_component,
        "current_value": current_value,
        "unit": unit,
        "evidence_status": evidence_status,
        "source_status": source_status,
        "source_artifact_status": source_artifact_status,
        "station_binding_ready": str(station_binding_ready).lower(),
        "service_publication_ready": str(service_publication_ready).lower(),
        "weak_for_final_claim": str(weak_for_final_claim).lower(),
        "review_priority": review_priority,
        "current_source": current_source,
        "candidate_artifacts": candidate_artifacts,
        "recommended_upgrade": recommended_upgrade,
        "publication_use_status": publication_use_status,
        "claim_boundary": RAIL_EVIDENCE_REVIEW_PACKET_SCOPE,
        "notes": notes,
    }


def _load_assumptions(path: str | Path) -> dict[str, dict[str, str]]:
    assumption_path = Path(path)
    if not assumption_path.exists():
        return {}
    with assumption_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return {
            str(row.get("parameter", "")).strip(): {
                str(key): str(value or "").strip()
                for key, value in row.items()
                if key is not None
            }
            for row in reader
            if str(row.get("parameter", "")).strip()
        }


def _station_current_value(records: Sequence[RailStationBinding]) -> str:
    if not records:
        return "missing"
    values = []
    for record in records:
        identifier = record.station_code or record.station_id
        values.append(f"{record.station_name}({identifier})")
    return "; ".join(values)


def _source_names(records: Sequence[RailStationBinding]) -> str:
    return "; ".join(dict.fromkeys(record.source_name for record in records))


def _source_statuses(values: Sequence[str] | object) -> str:
    return "; ".join(dict.fromkeys(str(value) for value in values if str(value)))


def _service_source_artifact_status(summary: Mapping[str, object]) -> str:
    if bool(summary["source_artifact_ready"]):
        return "cached_source_artifact_verified"
    if int(summary["derived_record_count"]) > 0:
        return "cached_source_artifact_missing_or_digest_mismatch"
    return "no_cached_timing_artifact"


def _source_status_with_assumption(
    service_record: RailServiceEvidence,
    assumptions: Mapping[str, Mapping[str, str]],
    key: str,
) -> str:
    source_class = assumptions.get(key, {}).get("source_class", "")
    if not source_class:
        return service_record.source_status
    return f"{service_record.source_status}; {source_class}"


def _assumption_source(
    assumptions: Mapping[str, Mapping[str, str]],
    key: str,
    fallback: RailServiceEvidence,
) -> str:
    row = assumptions.get(key, {})
    return row.get("source_url_or_citation") or fallback.source_url_or_citation


def _assumption_value(
    assumptions: Mapping[str, Mapping[str, str]],
    key: str,
) -> str:
    return assumptions.get(key, {}).get("value", "")


def _assumption_status(
    assumptions: Mapping[str, Mapping[str, str]],
    key: str,
) -> str:
    return assumptions.get(key, {}).get("source_class", "")


def _number_text(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.6g}"


def _counts(values: Sequence[str] | object) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _all_bool(rows: Sequence[Mapping[str, str]], column: str) -> bool:
    return all(str(row.get(column, "")).lower() == "true" for row in rows)


def _display_path(path: str | Path) -> str:
    value = Path(path)
    try:
        return str(value.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(value)


__all__ = [
    "DEFAULT_RAIL_ASSUMPTIONS_PATH",
    "DEFAULT_RAIL_EVIDENCE_REVIEW_MANIFEST_PATH",
    "DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH",
    "METRO9_CAPACITY_EXTRACT_PATH",
    "METRO9_CAPACITY_RAW_PATH",
    "RAIL_CAPACITY_REVIEW_ARTIFACTS",
    "RAIL_EVIDENCE_REVIEW_COLUMNS",
    "RAIL_EVIDENCE_REVIEW_PACKET_SCOPE",
    "build_rail_evidence_review_rows",
    "write_rail_evidence_review_packet",
]
