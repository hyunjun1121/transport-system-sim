"""Clean-checkout reproducibility acceptance record validation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "reproducibility_acceptance.json"
)

REQUIRED_REPRODUCIBILITY_ACCEPTANCE_FIELDS: tuple[str, ...] = (
    "region_id",
    "accepted",
    "accepted_by",
    "accepted_date",
    "clean_checkout_tested",
    "validation_ladder_passed",
    "artifact_regeneration_tested",
    "manifest_paths_reviewed",
    "no_runtime_cloned_repo_imports",
    "expected_validation_command_count",
    "claim_boundary",
    "evidence_paths",
)


@dataclass(frozen=True)
class ReproducibilityAcceptance:
    """One explicit clean-checkout reproducibility acceptance record."""

    region_id: str
    accepted: bool
    accepted_by: str
    accepted_date: str
    clean_checkout_tested: bool
    validation_ladder_passed: bool
    artifact_regeneration_tested: bool
    manifest_paths_reviewed: bool
    no_runtime_cloned_repo_imports: bool
    expected_validation_command_count: int
    claim_boundary: str
    evidence_paths: tuple[str, ...]

    @property
    def ready(self) -> bool:
        """Return whether this record can satisfy reproducibility acceptance."""

        return (
            self.accepted
            and bool(self.region_id)
            and bool(self.accepted_by)
            and bool(self.accepted_date)
            and self.clean_checkout_tested
            and self.validation_ladder_passed
            and self.artifact_regeneration_tested
            and self.manifest_paths_reviewed
            and self.no_runtime_cloned_repo_imports
            and self.expected_validation_command_count > 0
            and "not operational" in self.claim_boundary.lower()
            and bool(self.evidence_paths)
        )


def load_reproducibility_acceptance(
    path: str | Path = DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH,
) -> ReproducibilityAcceptance:
    """Load and validate a reproducibility acceptance JSON record."""

    acceptance_path = Path(path)
    with acceptance_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{acceptance_path} must contain a JSON object")
    record = _acceptance_from_mapping(value, acceptance_path)
    validate_reproducibility_acceptance(record, table_name=str(acceptance_path))
    return record


def summarize_reproducibility_acceptance(
    path: str | Path = DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return conservative reproducibility acceptance readiness."""

    acceptance_path = Path(path)
    if not acceptance_path.exists():
        return {
            "acceptance_ready": False,
            "path": _display_path(acceptance_path),
            "record_present": False,
            "remaining_blockers": [
                "create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks"
            ],
        }

    record = load_reproducibility_acceptance(acceptance_path)
    blockers: list[str] = []
    if not record.accepted:
        blockers.append("reproducibility acceptance record does not set accepted: true")
    if not record.clean_checkout_tested:
        blockers.append("reproducibility acceptance requires clean_checkout_tested: true")
    if not record.validation_ladder_passed:
        blockers.append("reproducibility acceptance requires validation_ladder_passed: true")
    if not record.artifact_regeneration_tested:
        blockers.append(
            "reproducibility acceptance requires artifact_regeneration_tested: true"
        )
    if not record.manifest_paths_reviewed:
        blockers.append("reproducibility acceptance requires manifest_paths_reviewed: true")
    if not record.no_runtime_cloned_repo_imports:
        blockers.append(
            "reproducibility acceptance requires no_runtime_cloned_repo_imports: true"
        )
    if record.expected_validation_command_count <= 0:
        blockers.append(
            "reproducibility acceptance expected_validation_command_count must be positive"
        )
    if "not operational" not in record.claim_boundary.lower():
        blockers.append(
            "reproducibility acceptance claim_boundary must include 'not operational'"
        )
    if not record.evidence_paths:
        blockers.append("reproducibility acceptance record must list evidence_paths")

    return {
        "acceptance_ready": not blockers,
        "path": _display_path(acceptance_path),
        "record_present": True,
        "region_id": record.region_id,
        "expected_validation_command_count": record.expected_validation_command_count,
        "clean_checkout_tested": record.clean_checkout_tested,
        "validation_ladder_passed": record.validation_ladder_passed,
        "artifact_regeneration_tested": record.artifact_regeneration_tested,
        "manifest_paths_reviewed": record.manifest_paths_reviewed,
        "no_runtime_cloned_repo_imports": record.no_runtime_cloned_repo_imports,
        "evidence_paths": list(record.evidence_paths),
        "remaining_blockers": blockers,
    }


def validate_reproducibility_acceptance(
    record: ReproducibilityAcceptance,
    *,
    table_name: str = "reproducibility acceptance",
) -> None:
    """Validate field-level reproducibility acceptance semantics."""

    if not record.region_id:
        raise ValueError(f"{table_name} region_id must be non-empty")
    if not record.accepted_by:
        raise ValueError(f"{table_name} accepted_by must be non-empty")
    if not record.accepted_date:
        raise ValueError(f"{table_name} accepted_date must be non-empty")
    if record.expected_validation_command_count <= 0:
        raise ValueError(
            f"{table_name} expected_validation_command_count must be positive"
        )
    if not record.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not record.evidence_paths:
        raise ValueError(f"{table_name} evidence_paths must be non-empty")


def _acceptance_from_mapping(
    row: Mapping[str, Any],
    path: Path,
) -> ReproducibilityAcceptance:
    missing = [
        field
        for field in REQUIRED_REPRODUCIBILITY_ACCEPTANCE_FIELDS
        if field not in row
    ]
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(missing)}")
    return ReproducibilityAcceptance(
        region_id=_clean(row["region_id"]),
        accepted=_bool_field(row, "accepted", path),
        accepted_by=_clean(row["accepted_by"]),
        accepted_date=_clean(row["accepted_date"]),
        clean_checkout_tested=_bool_field(row, "clean_checkout_tested", path),
        validation_ladder_passed=_bool_field(row, "validation_ladder_passed", path),
        artifact_regeneration_tested=_bool_field(
            row, "artifact_regeneration_tested", path
        ),
        manifest_paths_reviewed=_bool_field(row, "manifest_paths_reviewed", path),
        no_runtime_cloned_repo_imports=_bool_field(
            row, "no_runtime_cloned_repo_imports", path
        ),
        expected_validation_command_count=_positive_int(
            row,
            "expected_validation_command_count",
            path,
        ),
        claim_boundary=_clean(row["claim_boundary"]),
        evidence_paths=_clean_sequence(row["evidence_paths"], "evidence_paths", path),
    )


def _positive_int(row: Mapping[str, Any], field: str, path: Path) -> int:
    value = row[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path} field {field!r} must be an integer")
    return value


def _clean_sequence(value: object, field: str, path: Path) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise ValueError(f"{path} {field} must be a list of strings")
    return tuple(_clean(item) for item in value if _clean(item))


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
    "DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH",
    "REQUIRED_REPRODUCIBILITY_ACCEPTANCE_FIELDS",
    "ReproducibilityAcceptance",
    "load_reproducibility_acceptance",
    "summarize_reproducibility_acceptance",
    "validate_reproducibility_acceptance",
]
