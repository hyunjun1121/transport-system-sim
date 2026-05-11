"""Explicit acceptance records for weak parameter assumptions.

Parameter source tables can contain expert assumptions or sensitivity-only
values. Those rows are weak for final claims unless they are replaced by
stronger evidence or explicitly accepted within a conservative claim boundary.
This module validates that optional acceptance record.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARAMETER_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "parameter_acceptance.csv"
)

REQUIRED_COLUMNS: tuple[str, ...] = (
    "parameter",
    "accepted",
    "accepted_by",
    "accepted_date",
    "acceptance_scope",
    "claim_boundary",
    "sensitivity_reviewed",
    "evidence_paths",
    "notes",
)


@dataclass(frozen=True)
class ParameterAcceptance:
    """One explicit weak-parameter acceptance record."""

    parameter: str
    accepted: bool
    accepted_by: str
    accepted_date: str
    acceptance_scope: str
    claim_boundary: str
    sensitivity_reviewed: bool
    evidence_paths: tuple[str, ...]
    notes: str

    @property
    def ready(self) -> bool:
        """Return whether this record can accept a weak parameter."""

        return (
            self.accepted
            and self.sensitivity_reviewed
            and "not operational" in self.claim_boundary.lower()
            and bool(self.evidence_paths)
        )


def load_parameter_acceptance(
    path: str | Path = DEFAULT_PARAMETER_ACCEPTANCE_PATH,
) -> list[ParameterAcceptance]:
    """Load and validate a parameter-acceptance CSV."""

    acceptance_path = Path(path)
    with acceptance_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_columns(reader.fieldnames, acceptance_path)
        records: list[ParameterAcceptance] = []
        for row in reader:
            if None in row:
                raise ValueError(f"{acceptance_path}:{reader.line_num} has too many columns")
            if not any(_clean(value) for value in row.values()):
                continue
            records.append(_record_from_row(row, acceptance_path, reader.line_num))
    validate_parameter_acceptance(records, table_name=str(acceptance_path))
    return records


def summarize_parameter_acceptance(
    path: str | Path = DEFAULT_PARAMETER_ACCEPTANCE_PATH,
) -> dict[str, object]:
    """Return conservative readiness for optional parameter acceptance."""

    acceptance_path = Path(path)
    if not acceptance_path.exists():
        return {
            "path": _display_path(acceptance_path),
            "record_present": False,
            "accepted_parameter_count": 0,
            "ready_parameter_count": 0,
            "ready_parameters": [],
            "remaining_blockers": [
                "create reviewed parameter acceptance records only for weak assumptions retained in final claims"
            ],
        }

    records = load_parameter_acceptance(acceptance_path)
    ready = [record for record in records if record.ready]
    blockers: list[str] = []
    not_ready = [record.parameter for record in records if not record.ready]
    if not_ready:
        blockers.append(
            "fix non-ready parameter acceptance rows: " + ", ".join(sorted(not_ready))
        )
    return {
        "path": _display_path(acceptance_path),
        "record_present": True,
        "accepted_parameter_count": len(records),
        "ready_parameter_count": len(ready),
        "ready_parameters": sorted(record.parameter for record in ready),
        "remaining_blockers": blockers,
    }


def validate_parameter_acceptance(
    records: Sequence[ParameterAcceptance],
    *,
    table_name: str = "parameter acceptance",
) -> None:
    """Validate table-level parameter acceptance invariants."""

    if not records:
        raise ValueError(f"{table_name} must contain at least one acceptance row")
    seen: set[str] = set()
    duplicates: list[str] = []
    for record in records:
        if record.parameter in seen and record.parameter not in duplicates:
            duplicates.append(record.parameter)
        seen.add(record.parameter)
        _validate_record(record, table_name)
    if duplicates:
        raise ValueError(
            f"{table_name} has duplicate parameter rows: {', '.join(sorted(duplicates))}"
        )


def ready_accepted_parameters(
    records: Sequence[ParameterAcceptance],
) -> frozenset[str]:
    """Return parameter names with ready acceptance records."""

    return frozenset(record.parameter for record in records if record.ready)


def _validate_record(record: ParameterAcceptance, table_name: str) -> None:
    if not record.parameter:
        raise ValueError(f"{table_name} parameter must be non-empty")
    if not record.accepted_by:
        raise ValueError(f"{table_name} accepted_by must be non-empty")
    if not record.accepted_date:
        raise ValueError(f"{table_name} accepted_date must be non-empty")
    if not record.acceptance_scope:
        raise ValueError(f"{table_name} acceptance_scope must be non-empty")
    if not record.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not record.evidence_paths:
        raise ValueError(f"{table_name} evidence_paths must be non-empty")


def _validate_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    if not fieldnames:
        raise ValueError(f"{path} must have a CSV header")
    missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"{path} missing required columns: {', '.join(missing)}")


def _record_from_row(
    row: Mapping[str, str | None],
    path: Path,
    line_num: int,
) -> ParameterAcceptance:
    values = {column: _clean(row.get(column)) for column in REQUIRED_COLUMNS}
    for column, value in values.items():
        if not value:
            raise ValueError(f"{path}:{line_num} field {column!r} must be non-empty")
    return ParameterAcceptance(
        parameter=values["parameter"],
        accepted=_bool_token(values["accepted"], path, line_num, "accepted"),
        accepted_by=values["accepted_by"],
        accepted_date=values["accepted_date"],
        acceptance_scope=values["acceptance_scope"],
        claim_boundary=values["claim_boundary"],
        sensitivity_reviewed=_bool_token(
            values["sensitivity_reviewed"],
            path,
            line_num,
            "sensitivity_reviewed",
        ),
        evidence_paths=tuple(
            token.strip()
            for token in values["evidence_paths"].replace("|", ";").split(";")
            if token.strip()
        ),
        notes=values["notes"],
    )


def _bool_token(value: str, path: Path, line_num: int, field_name: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"{path}:{line_num} field {field_name!r} must be true or false")


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "DEFAULT_PARAMETER_ACCEPTANCE_PATH",
    "ParameterAcceptance",
    "REQUIRED_COLUMNS",
    "load_parameter_acceptance",
    "ready_accepted_parameters",
    "summarize_parameter_acceptance",
    "validate_parameter_acceptance",
]
