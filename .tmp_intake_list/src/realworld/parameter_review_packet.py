"""Parameter evidence review-packet generation.

The parameter audit reports whether final-study claims are blocked. This module
turns that audit into a CSV worksheet that reviewers can use to decide which
parameters need public-data, literature, agency, benchmark, or explicit
accepted-assumption support. It is deliberately a review aid, not an acceptance
record.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.parameter_audit import (
    CORE_PARAMETER_GROUPS,
    GROUP_BLOCKER_MESSAGES,
    audit_shipped_parameter_evidence,
    evidence_category_for_source_class,
)
from src.realworld.parameters import (
    DEFAULT_PARAMETER_DIR,
    ParameterRecord,
    validate_shipped_parameter_tables,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARAMETER_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "parameter_evidence_review_packet.csv"
)
DEFAULT_PARAMETER_REVIEW_PACKET_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "parameter_evidence_review_manifest.json"
)
PARAMETER_REVIEW_PACKET_COLUMNS: tuple[str, ...] = (
    "parameter",
    "group",
    "present",
    "evidence_category",
    "strongest_source_class",
    "weak_for_final_claim",
    "review_priority",
    "current_value",
    "unit",
    "source_name",
    "source_url_or_citation",
    "applies_to",
    "uncertainty_range",
    "source_tables",
    "source_classes",
    "recommended_upgrade",
    "candidate_artifacts",
    "claim_boundary",
    "notes",
)
PARAMETER_REVIEW_PACKET_SCOPE = (
    "Parameter evidence review packet; not accepted parameter calibration, "
    "operational evidence, or publication-readiness approval."
)
METRO9_CAPACITY_EXTRACT_PATH = "data/rail/metro9_capacity_source_extract.csv"
METRO9_CAPACITY_RAW_PATH = "data/rail/metro9_capacity_source_raw.html"

RECOMMENDED_UPGRADES: Mapping[str, str] = {
    "road": (
        "Replace or accept road speed, capacity, background traffic, and BPR "
        "inputs using public speed limits, traffic counts, routing benchmarks, "
        "or reviewed road-class overrides."
    ),
    "disruption": (
        "Replace or accept disruption probabilities and degradation factors "
        "using public hazard/incident data, scenario literature, or reviewed "
        "sensitivity-bound assumptions."
    ),
    "fleet": (
        "Replace or accept vehicle capacity, fleet size, dispatch, and "
        "turnaround assumptions using agency planning values, literature, or "
        "reviewed scenario assumptions."
    ),
    "rail": (
        "Derive or accept rail headway, travel time, and capacity using cached "
        "GTFS, public timetables, shortest-path records, operator sources, or "
        "explicit sensitivity-only treatment."
    ),
    "transfer": (
        "Replace or accept transfer delays using station-layout evidence, "
        "observed ranges, pedestrian-flow literature, or reviewed scenario "
        "assumptions."
    ),
    "demand_time_censoring": (
        "Replace or accept demand, arrival, horizon, and penalty settings using "
        "planning assumptions, scenario design, literature, and sensitivity "
        "bounds."
    ),
}

CANDIDATE_ARTIFACTS: Mapping[str, str] = {
    "road": (
        "data/parameters/road_speed_evidence_candidates.csv; "
        "data/parameters/road_capacity_evidence_candidates.csv; "
        "data/parameters/road_class_overrides_draft.csv; "
        "data/validation/external_route_benchmarks_osrm.csv"
    ),
    "disruption": (
        "data/scenarios/disruption_scenarios.csv; "
        "data/validation/accessibility_loss.csv"
    ),
    "fleet": "data/parameters/fleet_assumptions.csv",
    "rail": (
        "data/parameters/rail_service_evidence.csv; "
        "data/parameters/rail_station_bindings.csv; "
        "docs/rail_gtfs_cache_schema.md; docs/rail_timetable_cache_schema.md; "
        "docs/rail_shortest_path_cache_schema.md"
    ),
    "transfer": "data/parameters/parameter_sources.csv",
    "demand_time_censoring": (
        "data/parameters/parameter_sources.csv; "
        "data/scenarios/sensitivity_design.csv"
    ),
}

PARAMETER_CANDIDATE_ARTIFACTS: Mapping[str, str] = {
    "rail_capacity": (
        f"{CANDIDATE_ARTIFACTS['rail']}; "
        f"{METRO9_CAPACITY_EXTRACT_PATH}; {METRO9_CAPACITY_RAW_PATH}"
    ),
}


def build_parameter_review_rows(
    *,
    parameter_dir: str | Path = DEFAULT_PARAMETER_DIR,
) -> list[dict[str, str]]:
    """Return core-parameter review rows for shipped parameter tables."""

    tables = validate_shipped_parameter_tables(parameter_dir)
    audit = audit_shipped_parameter_evidence(parameter_dir)
    statuses = {
        str(item["parameter"]): item
        for item in audit["core_parameter_status"]
        if isinstance(item, Mapping)
    }
    records_by_parameter = _records_by_parameter(tables)
    rows: list[dict[str, str]] = []

    for group, parameters in CORE_PARAMETER_GROUPS.items():
        for parameter in parameters:
            status = statuses[parameter]
            records = records_by_parameter.get(parameter, ())
            strongest = _strongest_record(records)
            rows.append(_row_for_parameter(parameter, group, status, records, strongest))

    rows.sort(
        key=lambda row: (
            _priority_rank(row["review_priority"]),
            row["group"],
            row["parameter"],
        )
    )
    return rows


def write_parameter_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PARAMETER_REVIEW_PACKET_MANIFEST_PATH,
    parameter_dir: str | Path = DEFAULT_PARAMETER_DIR,
) -> dict[str, Any]:
    """Write parameter review rows and a conservative manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=PARAMETER_REVIEW_PACKET_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    weak_rows = [
        row
        for row in rows
        if str(row.get("weak_for_final_claim", "")).lower() == "true"
    ]
    priorities = _counts(row["review_priority"] for row in rows)
    groups = _counts(row["group"] for row in weak_rows)
    value = {
        "schema_version": 1,
        "result_scope": PARAMETER_REVIEW_PACKET_SCOPE,
        "parameter_dir": _display_path(parameter_dir),
        "outputs": {
            "parameter_evidence_review_packet": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "weak_for_final_claim_count": len(weak_rows),
        "review_priority_counts": priorities,
        "weak_group_counts": groups,
        "publication_ready": False,
        "claim_boundary": (
            "This packet organizes parameter evidence review. It does not "
            "create accepted parameter values, calibration, or final-study "
            "publication readiness."
        ),
        "review_items": [
            "replace weak rows with public, literature, agency, timetable, or benchmark evidence where possible",
            "use parameter_acceptance.csv only for reviewed weak assumptions retained inside conservative claim boundaries",
            "rerun publication-readiness and final-study-readiness audits after parameter evidence changes",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _row_for_parameter(
    parameter: str,
    group: str,
    status: Mapping[str, object],
    records: Sequence[tuple[str, ParameterRecord]],
    strongest: ParameterRecord | None,
) -> dict[str, str]:
    weak = bool(status["weak_for_final_claim"])
    return {
        "parameter": parameter,
        "group": group,
        "present": str(bool(status["present"])).lower(),
        "evidence_category": str(status["evidence_category"]),
        "strongest_source_class": str(status["strongest_source_class"]),
        "weak_for_final_claim": str(weak).lower(),
        "review_priority": _review_priority(group, status),
        "current_value": "" if strongest is None else strongest.value,
        "unit": "" if strongest is None else strongest.unit,
        "source_name": "" if strongest is None else strongest.source_name,
        "source_url_or_citation": (
            "" if strongest is None else strongest.source_url_or_citation
        ),
        "applies_to": "" if strongest is None else strongest.applies_to,
        "uncertainty_range": "" if strongest is None else strongest.uncertainty_range,
        "source_tables": "; ".join(sorted({table for table, _ in records})),
        "source_classes": "; ".join(
            sorted({record.source_class for _, record in records})
        ),
        "recommended_upgrade": RECOMMENDED_UPGRADES.get(group, ""),
        "candidate_artifacts": PARAMETER_CANDIDATE_ARTIFACTS.get(
            parameter,
            CANDIDATE_ARTIFACTS.get(group, ""),
        ),
        "claim_boundary": PARAMETER_REVIEW_PACKET_SCOPE,
        "notes": (
            GROUP_BLOCKER_MESSAGES.get(group, "")
            if weak
            else "Current evidence category is not weak for final claims under the audit rules."
        ),
    }


def _review_priority(group: str, status: Mapping[str, object]) -> str:
    category = str(status["evidence_category"])
    if category == "missing":
        return "critical"
    if not bool(status["weak_for_final_claim"]):
        return "low"
    if group in {"road", "rail", "disruption"}:
        return "high"
    if category == "sensitivity-only":
        return "high"
    return "medium"


def _strongest_record(
    records: Sequence[tuple[str, ParameterRecord]],
) -> ParameterRecord | None:
    if not records:
        return None
    return max(
        (record for _, record in records),
        key=lambda record: _category_rank(evidence_category_for_source_class(record.source_class)),
    )


def _category_rank(category: str) -> int:
    return {
        "benchmark-supported": 4,
        "source-backed": 3,
        "assumption-only": 2,
        "sensitivity-only": 1,
        "missing": 0,
    }.get(category, 0)


def _records_by_parameter(
    tables: Mapping[str, Sequence[ParameterRecord]],
) -> dict[str, list[tuple[str, ParameterRecord]]]:
    records: dict[str, list[tuple[str, ParameterRecord]]] = {}
    for table_name, table_records in tables.items():
        for record in table_records:
            records.setdefault(record.parameter, []).append((table_name, record))
    return records


def _priority_rank(priority: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(priority, 4)


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "DEFAULT_PARAMETER_REVIEW_PACKET_MANIFEST_PATH",
    "DEFAULT_PARAMETER_REVIEW_PACKET_PATH",
    "PARAMETER_REVIEW_PACKET_COLUMNS",
    "PARAMETER_REVIEW_PACKET_SCOPE",
    "build_parameter_review_rows",
    "write_parameter_review_packet",
]
