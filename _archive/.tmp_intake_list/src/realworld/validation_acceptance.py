"""Validation-package acceptance record validation.

Validation artifacts can show internal consistency and route plausibility, but
they do not automatically justify publication-level claims. This module
validates the explicit review record that accepts a benchmark strategy and its
claim boundary for the final study.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VALIDATION_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "validation_acceptance.json"
)

REQUIRED_VALIDATION_ACCEPTANCE_FIELDS: tuple[str, ...] = (
    "region_id",
    "accepted",
    "accepted_by",
    "accepted_date",
    "validation_scope",
    "benchmark_strategy",
    "internal_validation_reviewed",
    "external_plausibility_reviewed",
    "benchmark_validation_reviewed",
    "benchmark_is_not_ground_truth_acknowledged",
    "claim_boundary",
    "evidence_paths",
)
ALLOWED_BENCHMARK_STRATEGIES: frozenset[str] = frozenset(
    {
        "cached_osrm_snapshot",
        "cached_valhalla_snapshot",
        "cached_r5_or_otp_snapshot",
        "cached_routingpy_snapshot",
        "documented_fallback_plus_cached_external_snapshot",
        "documented_plausibility_only",
        "uxsim_corridor_benchmark",
    }
)


@dataclass(frozen=True)
class ValidationAcceptance:
    """One explicit validation-package acceptance record."""

    region_id: str
    accepted: bool
    accepted_by: str
    accepted_date: str
    validation_scope: str
    benchmark_strategy: str
    internal_validation_reviewed: bool
    external_plausibility_reviewed: bool
    benchmark_validation_reviewed: bool
    benchmark_is_not_ground_truth_acknowledged: bool
    claim_boundary: str
    evidence_paths: tuple[str, ...]

    @property
    def ready(self) -> bool:
        """Return whether this record can satisfy validation acceptance."""

        return (
            self.accepted
            and self.benchmark_strategy in ALLOWED_BENCHMARK_STRATEGIES
            and self.internal_validation_reviewed
            and self.external_plausibility_reviewed
            and self.benchmark_validation_reviewed
            and self.benchmark_is_not_ground_truth_acknowledged
            and "not operational" in self.claim_boundary.lower()
            and bool(self.evidence_paths)
        )


def load_validation_acceptance(
    path: str | Path = DEFAULT_VALIDATION_ACCEPTANCE_PATH,
) -> ValidationAcceptance:
    """Load and validate a validation-package acceptance JSON record."""

    acceptance_path = Path(path)
    with acceptance_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{acceptance_path} must contain a JSON object")
    record = _acceptance_from_mapping(value, acceptance_path)
    validate_validation_acceptance(record, table_name=str(acceptance_path))
    return record


def summarize_validation_acceptance(
    path: str | Path = DEFAULT_VALIDATION_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return conservative validation acceptance readiness."""

    acceptance_path = Path(path)
    if not acceptance_path.exists():
        return {
            "acceptance_ready": False,
            "path": _display_path(acceptance_path),
            "record_present": False,
            "remaining_blockers": [
                "create an explicit validation acceptance record after benchmark-strategy review"
            ],
        }

    record = load_validation_acceptance(acceptance_path)
    blockers: list[str] = []
    if not record.accepted:
        blockers.append("validation acceptance record does not set accepted: true")
    if record.benchmark_strategy not in ALLOWED_BENCHMARK_STRATEGIES:
        blockers.append("validation acceptance record has an unsupported benchmark_strategy")
    if not record.internal_validation_reviewed:
        blockers.append("validation acceptance requires internal_validation_reviewed: true")
    if not record.external_plausibility_reviewed:
        blockers.append("validation acceptance requires external_plausibility_reviewed: true")
    if not record.benchmark_validation_reviewed:
        blockers.append("validation acceptance requires benchmark_validation_reviewed: true")
    if not record.benchmark_is_not_ground_truth_acknowledged:
        blockers.append(
            "validation acceptance must acknowledge benchmark_is_not_ground_truth"
        )
    if "not operational" not in record.claim_boundary.lower():
        blockers.append("validation acceptance claim_boundary must include 'not operational'")
    if not record.evidence_paths:
        blockers.append("validation acceptance record must list evidence_paths")

    return {
        "acceptance_ready": not blockers,
        "path": _display_path(acceptance_path),
        "record_present": True,
        "region_id": record.region_id,
        "validation_scope": record.validation_scope,
        "benchmark_strategy": record.benchmark_strategy,
        "internal_validation_reviewed": record.internal_validation_reviewed,
        "external_plausibility_reviewed": record.external_plausibility_reviewed,
        "benchmark_validation_reviewed": record.benchmark_validation_reviewed,
        "benchmark_is_not_ground_truth_acknowledged": (
            record.benchmark_is_not_ground_truth_acknowledged
        ),
        "evidence_paths": list(record.evidence_paths),
        "remaining_blockers": blockers,
    }


def validate_validation_acceptance(
    record: ValidationAcceptance,
    *,
    table_name: str = "validation acceptance",
) -> None:
    """Validate field-level validation acceptance semantics."""

    if not record.region_id:
        raise ValueError(f"{table_name} region_id must be non-empty")
    if not record.accepted_by:
        raise ValueError(f"{table_name} accepted_by must be non-empty")
    if not record.accepted_date:
        raise ValueError(f"{table_name} accepted_date must be non-empty")
    if not record.validation_scope:
        raise ValueError(f"{table_name} validation_scope must be non-empty")
    if record.benchmark_strategy not in ALLOWED_BENCHMARK_STRATEGIES:
        allowed = ", ".join(sorted(ALLOWED_BENCHMARK_STRATEGIES))
        raise ValueError(
            f"{table_name} benchmark_strategy must be one of: {allowed}"
        )
    if not record.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not record.evidence_paths:
        raise ValueError(f"{table_name} evidence_paths must be non-empty")


def _acceptance_from_mapping(
    row: Mapping[str, Any],
    path: Path,
) -> ValidationAcceptance:
    missing = [
        field for field in REQUIRED_VALIDATION_ACCEPTANCE_FIELDS if field not in row
    ]
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(missing)}")
    evidence_paths = row["evidence_paths"]
    if not isinstance(evidence_paths, Sequence) or isinstance(evidence_paths, str):
        raise ValueError(f"{path} evidence_paths must be a list of paths")
    return ValidationAcceptance(
        region_id=_clean(row["region_id"]),
        accepted=_bool_field(row, "accepted", path),
        accepted_by=_clean(row["accepted_by"]),
        accepted_date=_clean(row["accepted_date"]),
        validation_scope=_clean(row["validation_scope"]),
        benchmark_strategy=_clean(row["benchmark_strategy"]),
        internal_validation_reviewed=_bool_field(
            row, "internal_validation_reviewed", path
        ),
        external_plausibility_reviewed=_bool_field(
            row, "external_plausibility_reviewed", path
        ),
        benchmark_validation_reviewed=_bool_field(
            row, "benchmark_validation_reviewed", path
        ),
        benchmark_is_not_ground_truth_acknowledged=_bool_field(
            row, "benchmark_is_not_ground_truth_acknowledged", path
        ),
        claim_boundary=_clean(row["claim_boundary"]),
        evidence_paths=tuple(_clean(item) for item in evidence_paths if _clean(item)),
    )


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
    "ALLOWED_BENCHMARK_STRATEGIES",
    "DEFAULT_VALIDATION_ACCEPTANCE_PATH",
    "REQUIRED_VALIDATION_ACCEPTANCE_FIELDS",
    "ValidationAcceptance",
    "load_validation_acceptance",
    "summarize_validation_acceptance",
    "validate_validation_acceptance",
]
