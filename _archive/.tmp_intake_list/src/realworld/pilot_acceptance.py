"""Pilot-region acceptance record validation.

The final study cannot be marked complete solely because a region YAML and
data card exist. This module validates an explicit human acceptance record that
documents privacy, graph-scope, and claim-boundary review for the pilot case.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PILOT_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "pilot_acceptance.json"
)

REQUIRED_ACCEPTANCE_FIELDS: tuple[str, ...] = (
    "region_id",
    "accepted",
    "accepted_by",
    "accepted_date",
    "acceptance_scope",
    "privacy_review_complete",
    "graph_scale_decision",
    "claim_boundary",
    "evidence_paths",
)
ALLOWED_GRAPH_SCALE_DECISIONS: frozenset[str] = frozenset(
    {"corridor_abstraction", "full_graph_runtime", "multi_corridor_ensemble"}
)


@dataclass(frozen=True)
class PilotAcceptance:
    """One explicit pilot-region acceptance record."""

    region_id: str
    accepted: bool
    accepted_by: str
    accepted_date: str
    acceptance_scope: str
    privacy_review_complete: bool
    graph_scale_decision: str
    claim_boundary: str
    evidence_paths: tuple[str, ...]

    @property
    def ready(self) -> bool:
        """Return whether the record can satisfy the pilot acceptance gate."""

        return (
            self.accepted
            and self.privacy_review_complete
            and self.graph_scale_decision in ALLOWED_GRAPH_SCALE_DECISIONS
            and "not operational" in self.claim_boundary.lower()
            and bool(self.evidence_paths)
        )


def load_pilot_acceptance(
    path: str | Path = DEFAULT_PILOT_ACCEPTANCE_PATH,
) -> PilotAcceptance:
    """Load and validate a pilot acceptance JSON record."""

    acceptance_path = Path(path)
    with acceptance_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{acceptance_path} must contain a JSON object")
    record = _acceptance_from_mapping(value, acceptance_path)
    validate_pilot_acceptance(record, table_name=str(acceptance_path))
    return record


def summarize_pilot_acceptance(
    path: str | Path = DEFAULT_PILOT_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return conservative pilot-acceptance readiness for final-study claims."""

    acceptance_path = Path(path)
    if not acceptance_path.exists():
        return {
            "acceptance_ready": False,
            "path": _display_path(acceptance_path),
            "record_present": False,
            "remaining_blockers": [
                "create an explicit pilot acceptance record after privacy and case-scope review"
            ],
        }

    record = load_pilot_acceptance(acceptance_path)
    blockers: list[str] = []
    if not record.accepted:
        blockers.append("pilot acceptance record does not set accepted: true")
    if not record.privacy_review_complete:
        blockers.append("pilot acceptance record does not confirm privacy_review_complete: true")
    if record.graph_scale_decision not in ALLOWED_GRAPH_SCALE_DECISIONS:
        blockers.append("pilot acceptance record has an unsupported graph_scale_decision")
    if "not operational" not in record.claim_boundary.lower():
        blockers.append("pilot acceptance claim_boundary must include 'not operational'")
    if not record.evidence_paths:
        blockers.append("pilot acceptance record must list evidence_paths")

    return {
        "acceptance_ready": not blockers,
        "path": _display_path(acceptance_path),
        "record_present": True,
        "region_id": record.region_id,
        "graph_scale_decision": record.graph_scale_decision,
        "privacy_review_complete": record.privacy_review_complete,
        "evidence_paths": list(record.evidence_paths),
        "remaining_blockers": blockers,
    }


def validate_pilot_acceptance(
    record: PilotAcceptance,
    *,
    table_name: str = "pilot acceptance",
) -> None:
    """Validate field-level pilot acceptance semantics."""

    if not record.region_id:
        raise ValueError(f"{table_name} region_id must be non-empty")
    if not record.accepted_by:
        raise ValueError(f"{table_name} accepted_by must be non-empty")
    if not record.accepted_date:
        raise ValueError(f"{table_name} accepted_date must be non-empty")
    if not record.acceptance_scope:
        raise ValueError(f"{table_name} acceptance_scope must be non-empty")
    if record.graph_scale_decision not in ALLOWED_GRAPH_SCALE_DECISIONS:
        allowed = ", ".join(sorted(ALLOWED_GRAPH_SCALE_DECISIONS))
        raise ValueError(
            f"{table_name} graph_scale_decision must be one of: {allowed}"
        )
    if not record.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not record.evidence_paths:
        raise ValueError(f"{table_name} evidence_paths must be non-empty")


def _acceptance_from_mapping(
    row: Mapping[str, Any],
    path: Path,
) -> PilotAcceptance:
    missing = [field for field in REQUIRED_ACCEPTANCE_FIELDS if field not in row]
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(missing)}")
    evidence_paths = row["evidence_paths"]
    if not isinstance(evidence_paths, Sequence) or isinstance(evidence_paths, str):
        raise ValueError(f"{path} evidence_paths must be a list of paths")
    return PilotAcceptance(
        region_id=_clean(row["region_id"]),
        accepted=_bool_field(row, "accepted", path),
        accepted_by=_clean(row["accepted_by"]),
        accepted_date=_clean(row["accepted_date"]),
        acceptance_scope=_clean(row["acceptance_scope"]),
        privacy_review_complete=_bool_field(row, "privacy_review_complete", path),
        graph_scale_decision=_clean(row["graph_scale_decision"]),
        claim_boundary=_clean(row["claim_boundary"]),
        evidence_paths=tuple(_clean(item) for item in evidence_paths if _clean(item)),
    )


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _bool_field(row: Mapping[str, Any], field: str, path: Path) -> bool:
    value = row[field]
    if not isinstance(value, bool):
        raise ValueError(f"{path} field {field!r} must be boolean")
    return value


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "ALLOWED_GRAPH_SCALE_DECISIONS",
    "DEFAULT_PILOT_ACCEPTANCE_PATH",
    "PilotAcceptance",
    "REQUIRED_ACCEPTANCE_FIELDS",
    "load_pilot_acceptance",
    "summarize_pilot_acceptance",
    "validate_pilot_acceptance",
]
