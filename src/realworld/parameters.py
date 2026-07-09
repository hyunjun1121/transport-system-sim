"""Load and validate pilot parameter evidence tables.

The tables are provenance records for quasi-real decision-support experiments.
They do not imply that the current pilot inputs are calibrated observations.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import math
from pathlib import Path
import re
from typing import Iterable, Mapping, Sequence


REQUIRED_COLUMNS: tuple[str, ...] = (
    "parameter",
    "value",
    "unit",
    "source_class",
    "source_name",
    "source_url_or_citation",
    "applies_to",
    "uncertainty_range",
    "notes",
)

ALWAYS_NON_EMPTY_COLUMNS: tuple[str, ...] = (
    "parameter",
    "value",
    "unit",
    "source_class",
    "source_name",
    "source_url_or_citation",
    "applies_to",
)

ALLOWED_SOURCE_CLASSES: frozenset[str] = frozenset(
    {
        "public-data-derived",
        "literature-derived",
        "design-standard-derived",
        "agency/timetable-derived",
        "benchmark-calibrated",
        "expert assumption",
        "sensitivity-only",
    }
)

ASSUMPTION_SOURCE_CLASSES: frozenset[str] = frozenset(
    {"expert assumption", "sensitivity-only"}
)

MINIMUM_PARAMETER_NAMES: tuple[str, ...] = (
    "road_free_flow_speed",
    "road_capacity_proxy",
    "background_traffic_multiplier",
    "bpr_alpha",
    "bpr_beta",
    "disruption_probability",
    "capacity_reduction_factor",
    "blockage_rule",
    "bus_capacity",
    "direct_bus_fleet_size",
    "feeder_fleet_size",
    "last_mile_fleet_size",
    "turnaround_time",
    "dispatch_interval",
    "rail_headway",
    "rail_travel_time",
    "rail_capacity",
    "transfer_fixed_delay",
    "transfer_per_passenger_delay",
    "passenger_arrival_distribution",
    "simulation_time_horizon",
    "late_arrival_penalty",
    "censored_passenger_penalty",
)

REQUIRED_RAIL_PARAMETERS: tuple[str, ...] = (
    "rail_access_point",
    "rail_egress_point",
    "rail_headway",
    "rail_travel_time",
    "rail_capacity",
)

REQUIRED_FLEET_PARAMETERS: tuple[str, ...] = (
    "bus_capacity",
    "direct_bus_fleet_size",
    "feeder_fleet_size",
    "last_mile_fleet_size",
    "turnaround_time",
    "dispatch_interval",
)

DEFAULT_PARAMETER_DIR = Path(__file__).resolve().parents[2] / "data" / "parameters"

SHIPPED_TABLE_REQUIREMENTS: Mapping[str, tuple[str, ...]] = {
    "parameter_sources.csv": MINIMUM_PARAMETER_NAMES,
    "rail_assumptions.csv": REQUIRED_RAIL_PARAMETERS,
    "fleet_assumptions.csv": REQUIRED_FLEET_PARAMETERS,
}

NON_NUMERIC_UNITS: frozenset[str] = frozenset(
    {"rule", "distribution", "node", "policy", "text", "categorical"}
)

EMPTY_MARKERS: frozenset[str] = frozenset({"", "n/a", "na", "none", "null", "tbd"})

_NUMERIC_TOKEN_RE = re.compile(
    r"[-+]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))(?:[eE][-+]?\d+)?"
)


@dataclass(frozen=True)
class ParameterRecord:
    """One normalized row from a parameter evidence table."""

    parameter: str
    value: str
    unit: str
    source_class: str
    source_name: str
    source_url_or_citation: str
    applies_to: str
    uncertainty_range: str
    notes: str


def load_parameter_table(path: str | Path) -> list[ParameterRecord]:
    """Load one parameter evidence CSV and validate row-level schema rules."""

    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_columns(reader.fieldnames, csv_path)
        records: list[ParameterRecord] = []
        for row in reader:
            if None in row:
                raise ValueError(f"{csv_path}:{reader.line_num} has too many columns")
            if _is_blank_row(row):
                continue
            record = _record_from_row(row)
            _validate_record(record, csv_path, reader.line_num)
            records.append(record)

    if not records:
        raise ValueError(f"{csv_path} must contain at least one parameter row")
    return records


def validate_parameter_table(
    path: str | Path,
    *,
    required_parameters: Iterable[str] = (),
) -> list[ParameterRecord]:
    """Load and validate one CSV including optional required-parameter coverage."""

    records = load_parameter_table(path)
    validate_parameter_records(
        records,
        required_parameters=required_parameters,
        table_name=str(path),
    )
    return records


def validate_parameter_records(
    records: Sequence[ParameterRecord],
    *,
    required_parameters: Iterable[str] = (),
    table_name: str = "parameter table",
) -> None:
    """Validate table-level invariants for already-loaded records."""

    if not records:
        raise ValueError(f"{table_name} must contain at least one parameter row")

    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for index, record in enumerate(records, start=1):
        if record.parameter in seen and record.parameter not in duplicates:
            duplicates.append(record.parameter)
        seen[record.parameter] = index
    if duplicates:
        raise ValueError(
            f"{table_name} has duplicate parameter rows: {', '.join(sorted(duplicates))}"
        )

    validate_parameter_coverage(
        records,
        required_parameters=required_parameters,
        table_name=table_name,
    )


def validate_parameter_coverage(
    records: Sequence[ParameterRecord],
    *,
    required_parameters: Iterable[str],
    table_name: str = "parameter table",
) -> None:
    """Raise if any required parameter names are absent."""

    required = {name.strip() for name in required_parameters if name.strip()}
    if not required:
        return
    present = {record.parameter for record in records}
    missing = sorted(required - present)
    if missing:
        raise ValueError(
            f"{table_name} missing required parameters: {', '.join(missing)}"
        )


def load_shipped_parameter_tables(
    directory: str | Path = DEFAULT_PARAMETER_DIR,
) -> dict[str, list[ParameterRecord]]:
    """Load all shipped parameter evidence tables without applying coverage rules."""

    parameter_dir = Path(directory)
    return {
        filename: load_parameter_table(parameter_dir / filename)
        for filename in SHIPPED_TABLE_REQUIREMENTS
    }


def validate_shipped_parameter_tables(
    directory: str | Path = DEFAULT_PARAMETER_DIR,
) -> dict[str, list[ParameterRecord]]:
    """Validate the shipped parameter evidence package and return loaded rows."""

    parameter_dir = Path(directory)
    tables: dict[str, list[ParameterRecord]] = {}
    for filename, required in SHIPPED_TABLE_REQUIREMENTS.items():
        path = parameter_dir / filename
        tables[filename] = validate_parameter_table(
            path,
            required_parameters=required,
        )

    all_records = [record for records in tables.values() for record in records]
    validate_parameter_coverage(
        all_records,
        required_parameters=MINIMUM_PARAMETER_NAMES,
        table_name="shipped parameter tables",
    )
    return tables


def numeric_tokens(value: str) -> tuple[float, ...]:
    """Return finite numeric tokens embedded in a value string."""

    numbers: list[float] = []
    for match in _NUMERIC_TOKEN_RE.finditer(value):
        try:
            number = float(match.group(0))
        except ValueError:
            continue
        if math.isfinite(number):
            numbers.append(number)
    return tuple(numbers)


def _validate_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    if not fieldnames:
        raise ValueError(f"{path} must have a CSV header")
    missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"{path} missing required columns: {', '.join(missing)}")


def _record_from_row(row: Mapping[str, str | None]) -> ParameterRecord:
    values = {column: _clean(row.get(column)) for column in REQUIRED_COLUMNS}
    return ParameterRecord(
        parameter=values["parameter"],
        value=values["value"],
        unit=values["unit"],
        source_class=values["source_class"].lower(),
        source_name=values["source_name"],
        source_url_or_citation=values["source_url_or_citation"],
        applies_to=values["applies_to"],
        uncertainty_range=values["uncertainty_range"],
        notes=values["notes"],
    )


def _validate_record(record: ParameterRecord, path: Path, line_num: int) -> None:
    location = f"{path}:{line_num}"
    for field_name in ALWAYS_NON_EMPTY_COLUMNS:
        if _is_empty(getattr(record, field_name)):
            raise ValueError(f"{location} field {field_name!r} must be non-empty")

    if record.source_class not in ALLOWED_SOURCE_CLASSES:
        allowed = ", ".join(sorted(ALLOWED_SOURCE_CLASSES))
        raise ValueError(
            f"{location} has invalid source_class {record.source_class!r}; "
            f"allowed: {allowed}"
        )

    if _requires_numeric_value(record.unit) and not numeric_tokens(record.value):
        raise ValueError(
            f"{location} parameter {record.parameter!r} has non-numeric value "
            f"{record.value!r} for unit {record.unit!r}"
        )

    if record.source_class in ASSUMPTION_SOURCE_CLASSES:
        if _is_empty(record.uncertainty_range):
            raise ValueError(
                f"{location} assumption or sensitivity row {record.parameter!r} "
                "must include uncertainty_range"
            )
        if _is_empty(record.notes):
            raise ValueError(
                f"{location} assumption or sensitivity row {record.parameter!r} "
                "must include notes"
            )


def _requires_numeric_value(unit: str) -> bool:
    return unit.strip().lower() not in NON_NUMERIC_UNITS


def _is_blank_row(row: Mapping[str, str | None]) -> bool:
    return not any(_clean(value) for value in row.values())


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _is_empty(value: str) -> bool:
    return value.strip().lower() in EMPTY_MARKERS


__all__ = [
    "ALLOWED_SOURCE_CLASSES",
    "ASSUMPTION_SOURCE_CLASSES",
    "DEFAULT_PARAMETER_DIR",
    "MINIMUM_PARAMETER_NAMES",
    "ParameterRecord",
    "REQUIRED_COLUMNS",
    "REQUIRED_FLEET_PARAMETERS",
    "REQUIRED_RAIL_PARAMETERS",
    "SHIPPED_TABLE_REQUIREMENTS",
    "load_parameter_table",
    "load_shipped_parameter_tables",
    "numeric_tokens",
    "validate_parameter_coverage",
    "validate_parameter_records",
    "validate_parameter_table",
    "validate_shipped_parameter_tables",
]
