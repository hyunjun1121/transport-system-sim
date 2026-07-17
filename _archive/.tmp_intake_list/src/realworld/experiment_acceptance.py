"""Pilot experiment-output acceptance record validation.

Generated pilot rows can be reproducible while still being scaffold outputs.
This module validates the explicit review record that accepts the scenario,
policy, seed, graph-scope, and result-use boundary for final-study experiment
outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPERIMENT_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_acceptance.json"
)

REQUIRED_EXPERIMENT_ACCEPTANCE_FIELDS: tuple[str, ...] = (
    "region_id",
    "accepted",
    "accepted_by",
    "accepted_date",
    "run_profile",
    "expected_row_count",
    "expected_summary_row_count",
    "policy_count",
    "scenario_count",
    "seed_count",
    "graph_scope_accepted",
    "input_validation_accepted",
    "scenario_policy_seed_design_reviewed",
    "common_random_numbers_reviewed",
    "claim_boundary",
    "evidence_paths",
)
ALLOWED_RUN_PROFILES: frozenset[str] = frozenset(
    {"staged_pilot", "full_pilot", "multi_corridor_full_pilot"}
)


@dataclass(frozen=True)
class ExperimentAcceptance:
    """One explicit pilot experiment-output acceptance record."""

    region_id: str
    accepted: bool
    accepted_by: str
    accepted_date: str
    run_profile: str
    expected_row_count: int
    expected_summary_row_count: int
    policy_count: int
    scenario_count: int
    seed_count: int
    graph_scope_accepted: bool
    input_validation_accepted: bool
    scenario_policy_seed_design_reviewed: bool
    common_random_numbers_reviewed: bool
    claim_boundary: str
    evidence_paths: tuple[str, ...]

    @property
    def ready(self) -> bool:
        """Return whether this record can satisfy experiment acceptance."""

        return (
            self.accepted
            and self.run_profile in ALLOWED_RUN_PROFILES
            and self.expected_row_count > 0
            and self.expected_summary_row_count > 0
            and self.policy_count > 0
            and self.scenario_count > 0
            and self.seed_count > 0
            and self.graph_scope_accepted
            and self.input_validation_accepted
            and self.scenario_policy_seed_design_reviewed
            and self.common_random_numbers_reviewed
            and "not operational" in self.claim_boundary.lower()
            and bool(self.evidence_paths)
        )


def load_experiment_acceptance(
    path: str | Path = DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
) -> ExperimentAcceptance:
    """Load and validate a pilot experiment acceptance JSON record."""

    acceptance_path = Path(path)
    with acceptance_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{acceptance_path} must contain a JSON object")
    record = _acceptance_from_mapping(value, acceptance_path)
    validate_experiment_acceptance(record, table_name=str(acceptance_path))
    return record


def summarize_experiment_acceptance(
    path: str | Path = DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return conservative pilot experiment acceptance readiness."""

    acceptance_path = Path(path)
    if not acceptance_path.exists():
        return {
            "acceptance_ready": False,
            "path": _display_path(acceptance_path),
            "record_present": False,
            "remaining_blockers": [
                "create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review"
            ],
        }

    record = load_experiment_acceptance(acceptance_path)
    blockers: list[str] = []
    if not record.accepted:
        blockers.append("experiment acceptance record does not set accepted: true")
    if record.run_profile not in ALLOWED_RUN_PROFILES:
        blockers.append("experiment acceptance record has an unsupported run_profile")
    if (
        record.expected_row_count <= 0
        or record.expected_summary_row_count <= 0
        or record.policy_count <= 0
        or record.scenario_count <= 0
        or record.seed_count <= 0
    ):
        blockers.append("experiment acceptance record must include positive result and design counts")
    if not record.graph_scope_accepted:
        blockers.append("experiment acceptance requires graph_scope_accepted: true")
    if not record.input_validation_accepted:
        blockers.append("experiment acceptance requires input_validation_accepted: true")
    if not record.scenario_policy_seed_design_reviewed:
        blockers.append(
            "experiment acceptance requires scenario_policy_seed_design_reviewed: true"
        )
    if not record.common_random_numbers_reviewed:
        blockers.append("experiment acceptance requires common_random_numbers_reviewed: true")
    if "not operational" not in record.claim_boundary.lower():
        blockers.append("experiment acceptance claim_boundary must include 'not operational'")
    if not record.evidence_paths:
        blockers.append("experiment acceptance record must list evidence_paths")

    return {
        "acceptance_ready": not blockers,
        "path": _display_path(acceptance_path),
        "record_present": True,
        "region_id": record.region_id,
        "run_profile": record.run_profile,
        "expected_row_count": record.expected_row_count,
        "expected_summary_row_count": record.expected_summary_row_count,
        "policy_count": record.policy_count,
        "scenario_count": record.scenario_count,
        "seed_count": record.seed_count,
        "graph_scope_accepted": record.graph_scope_accepted,
        "input_validation_accepted": record.input_validation_accepted,
        "scenario_policy_seed_design_reviewed": (
            record.scenario_policy_seed_design_reviewed
        ),
        "common_random_numbers_reviewed": record.common_random_numbers_reviewed,
        "evidence_paths": list(record.evidence_paths),
        "remaining_blockers": blockers,
    }


def validate_experiment_acceptance(
    record: ExperimentAcceptance,
    *,
    table_name: str = "experiment acceptance",
) -> None:
    """Validate field-level experiment acceptance semantics."""

    if not record.region_id:
        raise ValueError(f"{table_name} region_id must be non-empty")
    if not record.accepted_by:
        raise ValueError(f"{table_name} accepted_by must be non-empty")
    if not record.accepted_date:
        raise ValueError(f"{table_name} accepted_date must be non-empty")
    if record.run_profile not in ALLOWED_RUN_PROFILES:
        allowed = ", ".join(sorted(ALLOWED_RUN_PROFILES))
        raise ValueError(f"{table_name} run_profile must be one of: {allowed}")
    for field_name in (
        "expected_row_count",
        "expected_summary_row_count",
        "policy_count",
        "scenario_count",
        "seed_count",
    ):
        if getattr(record, field_name) <= 0:
            raise ValueError(f"{table_name} {field_name} must be positive")
    if not record.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not record.evidence_paths:
        raise ValueError(f"{table_name} evidence_paths must be non-empty")


def _acceptance_from_mapping(
    row: Mapping[str, Any],
    path: Path,
) -> ExperimentAcceptance:
    missing = [
        field for field in REQUIRED_EXPERIMENT_ACCEPTANCE_FIELDS if field not in row
    ]
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(missing)}")
    evidence_paths = row["evidence_paths"]
    if not isinstance(evidence_paths, Sequence) or isinstance(evidence_paths, str):
        raise ValueError(f"{path} evidence_paths must be a list of paths")
    return ExperimentAcceptance(
        region_id=_clean(row["region_id"]),
        accepted=_bool_field(row, "accepted", path),
        accepted_by=_clean(row["accepted_by"]),
        accepted_date=_clean(row["accepted_date"]),
        run_profile=_clean(row["run_profile"]),
        expected_row_count=_positive_int(row, "expected_row_count", path),
        expected_summary_row_count=_positive_int(
            row, "expected_summary_row_count", path
        ),
        policy_count=_positive_int(row, "policy_count", path),
        scenario_count=_positive_int(row, "scenario_count", path),
        seed_count=_positive_int(row, "seed_count", path),
        graph_scope_accepted=_bool_field(row, "graph_scope_accepted", path),
        input_validation_accepted=_bool_field(row, "input_validation_accepted", path),
        scenario_policy_seed_design_reviewed=_bool_field(
            row, "scenario_policy_seed_design_reviewed", path
        ),
        common_random_numbers_reviewed=_bool_field(
            row, "common_random_numbers_reviewed", path
        ),
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
    "ALLOWED_RUN_PROFILES",
    "DEFAULT_EXPERIMENT_ACCEPTANCE_PATH",
    "ExperimentAcceptance",
    "REQUIRED_EXPERIMENT_ACCEPTANCE_FIELDS",
    "load_experiment_acceptance",
    "summarize_experiment_acceptance",
    "validate_experiment_acceptance",
]
