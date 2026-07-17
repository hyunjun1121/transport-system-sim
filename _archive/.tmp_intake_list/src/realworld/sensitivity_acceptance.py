"""Sensitivity-analysis acceptance record validation.

Sensitivity outputs can be reproducible without being final-study evidence.
This module validates the explicit review record that accepts the sensitivity
method, result scope, parameter ranges, and Sobol decision for final claims.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SENSITIVITY_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "sensitivity_acceptance.json"
)

REQUIRED_SENSITIVITY_ACCEPTANCE_FIELDS: tuple[str, ...] = (
    "region_id",
    "accepted",
    "accepted_by",
    "accepted_date",
    "sensitivity_method",
    "result_scope",
    "expected_row_count",
    "expected_summary_row_count",
    "graph_scope_accepted",
    "parameter_ranges_reviewed",
    "salib_output_reviewed",
    "nan_or_masked_values_reviewed",
    "sobol_requirement_decision",
    "claim_boundary",
    "evidence_paths",
)
ALLOWED_SENSITIVITY_METHODS: frozenset[str] = frozenset(
    {"deterministic_oat_screening", "salib_morris", "salib_sobol", "morris_plus_sobol"}
)
ALLOWED_SOBOL_DECISIONS: frozenset[str] = frozenset(
    {"not_required", "completed", "required_pending"}
)


@dataclass(frozen=True)
class SensitivityAcceptance:
    """One explicit sensitivity-analysis acceptance record."""

    region_id: str
    accepted: bool
    accepted_by: str
    accepted_date: str
    sensitivity_method: str
    result_scope: str
    expected_row_count: int
    expected_summary_row_count: int
    graph_scope_accepted: bool
    parameter_ranges_reviewed: bool
    salib_output_reviewed: bool
    nan_or_masked_values_reviewed: bool
    sobol_requirement_decision: str
    claim_boundary: str
    evidence_paths: tuple[str, ...]

    @property
    def ready(self) -> bool:
        """Return whether this record can satisfy sensitivity acceptance."""

        return (
            self.accepted
            and self.sensitivity_method in ALLOWED_SENSITIVITY_METHODS
            and self.expected_row_count > 0
            and self.expected_summary_row_count > 0
            and self.graph_scope_accepted
            and self.parameter_ranges_reviewed
            and self.salib_output_reviewed
            and self.nan_or_masked_values_reviewed
            and self.sobol_requirement_decision in {"not_required", "completed"}
            and "not operational" in self.claim_boundary.lower()
            and bool(self.evidence_paths)
        )


def load_sensitivity_acceptance(
    path: str | Path = DEFAULT_SENSITIVITY_ACCEPTANCE_PATH,
) -> SensitivityAcceptance:
    """Load and validate a sensitivity acceptance JSON record."""

    acceptance_path = Path(path)
    with acceptance_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{acceptance_path} must contain a JSON object")
    record = _acceptance_from_mapping(value, acceptance_path)
    validate_sensitivity_acceptance(record, table_name=str(acceptance_path))
    return record


def summarize_sensitivity_acceptance(
    path: str | Path = DEFAULT_SENSITIVITY_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return conservative sensitivity acceptance readiness."""

    acceptance_path = Path(path)
    if not acceptance_path.exists():
        return {
            "acceptance_ready": False,
            "path": _display_path(acceptance_path),
            "record_present": False,
            "remaining_blockers": [
                "create an explicit sensitivity acceptance record after SALib output and Sobol-decision review"
            ],
        }

    record = load_sensitivity_acceptance(acceptance_path)
    blockers: list[str] = []
    if not record.accepted:
        blockers.append("sensitivity acceptance record does not set accepted: true")
    if record.sensitivity_method not in ALLOWED_SENSITIVITY_METHODS:
        blockers.append("sensitivity acceptance record has an unsupported sensitivity_method")
    if record.expected_row_count <= 0 or record.expected_summary_row_count <= 0:
        blockers.append("sensitivity acceptance record must include positive result counts")
    if not record.graph_scope_accepted:
        blockers.append("sensitivity acceptance requires graph_scope_accepted: true")
    if not record.parameter_ranges_reviewed:
        blockers.append("sensitivity acceptance requires parameter_ranges_reviewed: true")
    if not record.salib_output_reviewed:
        blockers.append("sensitivity acceptance requires salib_output_reviewed: true")
    if not record.nan_or_masked_values_reviewed:
        blockers.append("sensitivity acceptance requires nan_or_masked_values_reviewed: true")
    if record.sobol_requirement_decision not in ALLOWED_SOBOL_DECISIONS:
        blockers.append("sensitivity acceptance has an unsupported sobol_requirement_decision")
    if record.sobol_requirement_decision == "required_pending":
        blockers.append("Sobol analysis is marked required but still pending")
    if "not operational" not in record.claim_boundary.lower():
        blockers.append("sensitivity acceptance claim_boundary must include 'not operational'")
    if not record.evidence_paths:
        blockers.append("sensitivity acceptance record must list evidence_paths")

    return {
        "acceptance_ready": not blockers,
        "path": _display_path(acceptance_path),
        "record_present": True,
        "region_id": record.region_id,
        "sensitivity_method": record.sensitivity_method,
        "result_scope": record.result_scope,
        "expected_row_count": record.expected_row_count,
        "expected_summary_row_count": record.expected_summary_row_count,
        "graph_scope_accepted": record.graph_scope_accepted,
        "parameter_ranges_reviewed": record.parameter_ranges_reviewed,
        "salib_output_reviewed": record.salib_output_reviewed,
        "nan_or_masked_values_reviewed": record.nan_or_masked_values_reviewed,
        "sobol_requirement_decision": record.sobol_requirement_decision,
        "evidence_paths": list(record.evidence_paths),
        "remaining_blockers": blockers,
    }


def validate_sensitivity_acceptance(
    record: SensitivityAcceptance,
    *,
    table_name: str = "sensitivity acceptance",
) -> None:
    """Validate field-level sensitivity acceptance semantics."""

    if not record.region_id:
        raise ValueError(f"{table_name} region_id must be non-empty")
    if not record.accepted_by:
        raise ValueError(f"{table_name} accepted_by must be non-empty")
    if not record.accepted_date:
        raise ValueError(f"{table_name} accepted_date must be non-empty")
    if record.sensitivity_method not in ALLOWED_SENSITIVITY_METHODS:
        allowed = ", ".join(sorted(ALLOWED_SENSITIVITY_METHODS))
        raise ValueError(
            f"{table_name} sensitivity_method must be one of: {allowed}"
        )
    if not record.result_scope:
        raise ValueError(f"{table_name} result_scope must be non-empty")
    if record.expected_row_count <= 0:
        raise ValueError(f"{table_name} expected_row_count must be positive")
    if record.expected_summary_row_count <= 0:
        raise ValueError(f"{table_name} expected_summary_row_count must be positive")
    if record.sobol_requirement_decision not in ALLOWED_SOBOL_DECISIONS:
        allowed = ", ".join(sorted(ALLOWED_SOBOL_DECISIONS))
        raise ValueError(
            f"{table_name} sobol_requirement_decision must be one of: {allowed}"
        )
    if not record.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not record.evidence_paths:
        raise ValueError(f"{table_name} evidence_paths must be non-empty")


def _acceptance_from_mapping(
    row: Mapping[str, Any],
    path: Path,
) -> SensitivityAcceptance:
    missing = [
        field for field in REQUIRED_SENSITIVITY_ACCEPTANCE_FIELDS if field not in row
    ]
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(missing)}")
    evidence_paths = row["evidence_paths"]
    if not isinstance(evidence_paths, Sequence) or isinstance(evidence_paths, str):
        raise ValueError(f"{path} evidence_paths must be a list of paths")
    return SensitivityAcceptance(
        region_id=_clean(row["region_id"]),
        accepted=_bool_field(row, "accepted", path),
        accepted_by=_clean(row["accepted_by"]),
        accepted_date=_clean(row["accepted_date"]),
        sensitivity_method=_clean(row["sensitivity_method"]),
        result_scope=_clean(row["result_scope"]),
        expected_row_count=_positive_int(row, "expected_row_count", path),
        expected_summary_row_count=_positive_int(
            row, "expected_summary_row_count", path
        ),
        graph_scope_accepted=_bool_field(row, "graph_scope_accepted", path),
        parameter_ranges_reviewed=_bool_field(row, "parameter_ranges_reviewed", path),
        salib_output_reviewed=_bool_field(row, "salib_output_reviewed", path),
        nan_or_masked_values_reviewed=_bool_field(
            row, "nan_or_masked_values_reviewed", path
        ),
        sobol_requirement_decision=_clean(row["sobol_requirement_decision"]),
        claim_boundary=_clean(row["claim_boundary"]),
        evidence_paths=tuple(_clean(item) for item in evidence_paths if _clean(item)),
    )


def _positive_int(row: Mapping[str, Any], field: str, path: Path) -> int:
    value = row[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path} field {field!r} must be an integer")
    return value


def _bool_field(row: Mapping[str, Any], field: str, path: Path) -> bool:
    value = row[field]
    if not isinstance(value, bool):
        raise ValueError(f"{path} field {field!r} must be boolean")
    return value


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "ALLOWED_SENSITIVITY_METHODS",
    "ALLOWED_SOBOL_DECISIONS",
    "DEFAULT_SENSITIVITY_ACCEPTANCE_PATH",
    "REQUIRED_SENSITIVITY_ACCEPTANCE_FIELDS",
    "SensitivityAcceptance",
    "load_sensitivity_acceptance",
    "summarize_sensitivity_acceptance",
    "validate_sensitivity_acceptance",
]
