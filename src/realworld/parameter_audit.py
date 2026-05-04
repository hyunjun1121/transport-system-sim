"""Conservative publication-readiness audit for pilot parameter evidence.

The CSV validators in :mod:`src.realworld.parameters` check table schema and
coverage. This module answers a different question: whether the current core
parameters are backed by evidence strong enough for final-study claims.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from src.realworld.parameter_acceptance import (
    DEFAULT_PARAMETER_ACCEPTANCE_PATH,
    load_parameter_acceptance,
    ready_accepted_parameters,
    summarize_parameter_acceptance,
)
from src.realworld.parameters import (
    DEFAULT_PARAMETER_DIR,
    ParameterRecord,
    validate_shipped_parameter_tables,
)


SOURCE_CLASS_TO_CATEGORY: Mapping[str, str] = {
    "public-data-derived": "source-backed",
    "literature-derived": "source-backed",
    "agency/timetable-derived": "source-backed",
    "benchmark-calibrated": "benchmark-supported",
    "expert assumption": "assumption-only",
    "sensitivity-only": "sensitivity-only",
}

EVIDENCE_CATEGORY_RANK: Mapping[str, int] = {
    "benchmark-supported": 4,
    "source-backed": 3,
    "assumption-only": 2,
    "sensitivity-only": 1,
    "missing": 0,
}

WEAK_EVIDENCE_CATEGORIES: frozenset[str] = frozenset(
    {"assumption-only", "sensitivity-only", "missing"}
)

CORE_PARAMETER_GROUPS: Mapping[str, tuple[str, ...]] = {
    "road": (
        "road_free_flow_speed",
        "road_capacity_proxy",
        "background_traffic_multiplier",
        "bpr_alpha",
        "bpr_beta",
        "traffic_volume_window",
    ),
    "disruption": (
        "disruption_probability",
        "capacity_reduction_factor",
        "blockage_rule",
        "base_disruption_probability",
    ),
    "fleet": (
        "bus_capacity",
        "direct_bus_fleet_size",
        "feeder_fleet_size",
        "last_mile_fleet_size",
        "last_mile_vehicle_capacity",
        "turnaround_time",
        "dispatch_interval",
    ),
    "rail": (
        "rail_access_point",
        "rail_egress_point",
        "rail_headway",
        "rail_travel_time",
        "rail_capacity",
    ),
    "transfer": (
        "transfer_fixed_delay",
        "transfer_per_passenger_delay",
    ),
    "demand_time_censoring": (
        "passenger_volume",
        "passenger_arrival_distribution",
        "simulation_time_horizon",
        "late_arrival_penalty",
        "censored_passenger_penalty",
    ),
}

GROUP_BLOCKER_MESSAGES: Mapping[str, str] = {
    "road": (
        "strengthen road speed, capacity, and background traffic values with "
        "public speed limits, traffic counts, or benchmark-calibrated routing"
    ),
    "disruption": (
        "replace scenario-only disruption probabilities and degradation rules "
        "with public hazard, incident, literature, or expert-reviewed evidence"
    ),
    "fleet": (
        "replace generic fleet and vehicle-capacity assumptions with agency, "
        "planning, literature, or accepted scenario evidence"
    ),
    "rail": (
        "derive rail headway and travel time from cached GTFS, timetable, "
        "operator, or agency records, and keep rail capacity source-backed or "
        "explicitly sensitivity-only"
    ),
    "transfer": (
        "support transfer delays with station-layout evidence, observed ranges, "
        "or literature rather than generic fixed delays"
    ),
    "demand_time_censoring": (
        "justify demand scale, arrival process, time horizon, and censoring "
        "penalties with planning assumptions or sensitivity-bound evidence"
    ),
}


@dataclass(frozen=True)
class ParameterAuditStatus:
    """Publication-readiness status for one core parameter."""

    parameter: str
    group: str
    present: bool
    evidence_category: str
    strongest_source_class: str
    source_classes: tuple[str, ...]
    tables: tuple[str, ...]
    accepted_weak_assumption: bool
    weak_for_final_claim: bool

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return {
            "parameter": self.parameter,
            "group": self.group,
            "present": self.present,
            "evidence_category": self.evidence_category,
            "strongest_source_class": self.strongest_source_class,
            "source_classes": list(self.source_classes),
            "tables": list(self.tables),
            "accepted_weak_assumption": self.accepted_weak_assumption,
            "weak_for_final_claim": self.weak_for_final_claim,
        }


def audit_shipped_parameter_evidence(
    directory: str | Path = DEFAULT_PARAMETER_DIR,
) -> dict[str, object]:
    """Validate shipped parameter tables and summarize evidence readiness."""

    tables = validate_shipped_parameter_tables(directory)
    acceptance_path = Path(directory) / DEFAULT_PARAMETER_ACCEPTANCE_PATH.name
    acceptance_summary = summarize_parameter_acceptance(acceptance_path)
    accepted_parameters = (
        ready_accepted_parameters(load_parameter_acceptance(acceptance_path))
        if acceptance_path.exists()
        else frozenset()
    )
    return summarize_parameter_evidence(
        tables,
        accepted_parameters=accepted_parameters,
        acceptance_summary=acceptance_summary,
    )


def summarize_parameter_evidence(
    tables: Mapping[str, Sequence[ParameterRecord]],
    *,
    accepted_parameters: frozenset[str] = frozenset(),
    acceptance_summary: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return a conservative audit summary for parameter evidence tables."""

    records_by_parameter: dict[str, list[tuple[str, ParameterRecord]]] = defaultdict(list)
    source_class_counts: Counter[str] = Counter()
    evidence_category_counts: Counter[str] = Counter()
    table_row_counts: dict[str, int] = {}

    for table_name, records in tables.items():
        table_row_counts[table_name] = len(records)
        for record in records:
            records_by_parameter[record.parameter].append((table_name, record))
            source_class_counts[record.source_class] += 1
            evidence_category_counts[evidence_category_for_source_class(record.source_class)] += 1

    statuses = [
        _status_for_parameter(
            parameter,
            group,
            records_by_parameter,
            accepted_parameters=accepted_parameters,
        )
        for group, parameters in CORE_PARAMETER_GROUPS.items()
        for parameter in parameters
    ]
    weak_statuses = [status for status in statuses if status.weak_for_final_claim]
    missing_statuses = [status for status in statuses if not status.present]
    weak_groups = sorted({status.group for status in weak_statuses})
    core_category_counts = Counter(status.evidence_category for status in statuses)

    return {
        "publication_ready": not weak_statuses,
        "claim_boundary": (
            "This audit checks whether core parameter values are supported by "
            "public, literature, agency, timetable, or benchmark-calibrated "
            "evidence. It does not certify operational accuracy."
        ),
        "table_row_counts": dict(sorted(table_row_counts.items())),
        "source_class_counts": dict(sorted(source_class_counts.items())),
        "evidence_category_counts": dict(sorted(evidence_category_counts.items())),
        "core_parameter_count": len(statuses),
        "weak_core_parameter_count": len(weak_statuses),
        "accepted_weak_parameter_count": sum(
            1 for status in statuses if status.accepted_weak_assumption
        ),
        "missing_core_parameter_count": len(missing_statuses),
        "core_evidence_category_counts": dict(sorted(core_category_counts.items())),
        "weak_core_parameters": [status.as_dict() for status in weak_statuses],
        "missing_core_parameters": [status.as_dict() for status in missing_statuses],
        "core_parameter_status": [status.as_dict() for status in statuses],
        "remaining_blockers": [
            GROUP_BLOCKER_MESSAGES[group] for group in weak_groups
        ],
        "parameter_acceptance": dict(acceptance_summary or {}),
    }


def evidence_category_for_source_class(source_class: str) -> str:
    """Map a source_class value to a broader evidence category."""

    normalized = source_class.strip().lower()
    if normalized not in SOURCE_CLASS_TO_CATEGORY:
        raise ValueError(f"unknown source_class: {source_class!r}")
    return SOURCE_CLASS_TO_CATEGORY[normalized]


def _status_for_parameter(
    parameter: str,
    group: str,
    records_by_parameter: Mapping[str, Sequence[tuple[str, ParameterRecord]]],
    *,
    accepted_parameters: frozenset[str],
) -> ParameterAuditStatus:
    records = list(records_by_parameter.get(parameter, ()))
    if not records:
        return ParameterAuditStatus(
            parameter=parameter,
            group=group,
            present=False,
            evidence_category="missing",
            strongest_source_class="missing",
            source_classes=(),
            tables=(),
            accepted_weak_assumption=False,
            weak_for_final_claim=True,
        )

    strongest_table, strongest_record = max(
        records,
        key=lambda item: EVIDENCE_CATEGORY_RANK[
            evidence_category_for_source_class(item[1].source_class)
        ],
    )
    del strongest_table
    category = evidence_category_for_source_class(strongest_record.source_class)
    accepted_weak_assumption = (
        category in WEAK_EVIDENCE_CATEGORIES and parameter in accepted_parameters
    )
    return ParameterAuditStatus(
        parameter=parameter,
        group=group,
        present=True,
        evidence_category=category,
        strongest_source_class=strongest_record.source_class,
        source_classes=tuple(
            sorted({record.source_class for _, record in records})
        ),
        tables=tuple(sorted({table_name for table_name, _ in records})),
        accepted_weak_assumption=accepted_weak_assumption,
        weak_for_final_claim=(
            category in WEAK_EVIDENCE_CATEGORIES and not accepted_weak_assumption
        ),
    )


__all__ = [
    "CORE_PARAMETER_GROUPS",
    "EVIDENCE_CATEGORY_RANK",
    "GROUP_BLOCKER_MESSAGES",
    "ParameterAuditStatus",
    "SOURCE_CLASS_TO_CATEGORY",
    "WEAK_EVIDENCE_CATEGORIES",
    "audit_shipped_parameter_evidence",
    "evidence_category_for_source_class",
    "summarize_parameter_evidence",
]
