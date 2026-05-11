"""Independent final-study audit acceptance record validation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FINAL_AUDIT_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "final_audit_acceptance.json"
)

REQUIRED_FINAL_AUDIT_ACCEPTANCE_FIELDS: tuple[str, ...] = (
    "region_id",
    "accepted",
    "accepted_by",
    "accepted_date",
    "final_study_ready",
    "prompt_to_artifact_checklist_reviewed",
    "all_gate_evidence_reviewed",
    "no_proxy_completion_reviewed",
    "expected_gate_count",
    "reviewed_gate_ids",
    "ready_gate_ids",
    "blocked_gate_ids",
    "claim_boundary",
    "evidence_paths",
)


@dataclass(frozen=True)
class FinalAuditAcceptance:
    """One explicit independent final-study audit acceptance record."""

    region_id: str
    accepted: bool
    accepted_by: str
    accepted_date: str
    final_study_ready: bool
    prompt_to_artifact_checklist_reviewed: bool
    all_gate_evidence_reviewed: bool
    no_proxy_completion_reviewed: bool
    expected_gate_count: int
    reviewed_gate_ids: tuple[str, ...]
    ready_gate_ids: tuple[str, ...]
    blocked_gate_ids: tuple[str, ...]
    claim_boundary: str
    evidence_paths: tuple[str, ...]

    @property
    def ready(self) -> bool:
        """Return whether this record can satisfy final-audit acceptance."""

        return (
            self.accepted
            and bool(self.region_id)
            and bool(self.accepted_by)
            and bool(self.accepted_date)
            and self.final_study_ready
            and self.prompt_to_artifact_checklist_reviewed
            and self.all_gate_evidence_reviewed
            and self.no_proxy_completion_reviewed
            and self.expected_gate_count > 0
            and bool(self.reviewed_gate_ids)
            and bool(self.ready_gate_ids)
            and not self.blocked_gate_ids
            and "not operational" in self.claim_boundary.lower()
            and bool(self.evidence_paths)
        )


def load_final_audit_acceptance(
    path: str | Path = DEFAULT_FINAL_AUDIT_ACCEPTANCE_PATH,
) -> FinalAuditAcceptance:
    """Load and validate a final-audit acceptance JSON record."""

    acceptance_path = Path(path)
    with acceptance_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{acceptance_path} must contain a JSON object")
    record = _acceptance_from_mapping(value, acceptance_path)
    validate_final_audit_acceptance(record, table_name=str(acceptance_path))
    return record


def summarize_final_audit_acceptance(
    path: str | Path = DEFAULT_FINAL_AUDIT_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return conservative independent final-audit acceptance readiness."""

    acceptance_path = Path(path)
    if not acceptance_path.exists():
        return {
            "acceptance_ready": False,
            "path": _display_path(acceptance_path),
            "record_present": False,
            "remaining_blockers": [
                "create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed"
            ],
        }

    record = load_final_audit_acceptance(acceptance_path)
    blockers: list[str] = []
    if not record.accepted:
        blockers.append("final-audit acceptance record does not set accepted: true")
    if not record.final_study_ready:
        blockers.append("final-audit acceptance requires final_study_ready: true")
    if not record.prompt_to_artifact_checklist_reviewed:
        blockers.append(
            "final-audit acceptance requires prompt_to_artifact_checklist_reviewed: true"
        )
    if not record.all_gate_evidence_reviewed:
        blockers.append("final-audit acceptance requires all_gate_evidence_reviewed: true")
    if not record.no_proxy_completion_reviewed:
        blockers.append(
            "final-audit acceptance requires no_proxy_completion_reviewed: true"
        )
    if record.expected_gate_count <= 0:
        blockers.append("final-audit expected_gate_count must be positive")
    if not record.reviewed_gate_ids:
        blockers.append("final-audit acceptance record must list reviewed_gate_ids")
    if not record.ready_gate_ids:
        blockers.append("final-audit acceptance record must list ready_gate_ids")
    if record.blocked_gate_ids:
        blockers.append("final-audit acceptance record must have no blocked_gate_ids")
    if "not operational" not in record.claim_boundary.lower():
        blockers.append("final-audit claim_boundary must include 'not operational'")
    if not record.evidence_paths:
        blockers.append("final-audit acceptance record must list evidence_paths")

    return {
        "acceptance_ready": not blockers,
        "path": _display_path(acceptance_path),
        "record_present": True,
        "region_id": record.region_id,
        "expected_gate_count": record.expected_gate_count,
        "reviewed_gate_ids": list(record.reviewed_gate_ids),
        "ready_gate_ids": list(record.ready_gate_ids),
        "blocked_gate_ids": list(record.blocked_gate_ids),
        "final_study_ready": record.final_study_ready,
        "evidence_paths": list(record.evidence_paths),
        "remaining_blockers": blockers,
    }


def validate_final_audit_acceptance(
    record: FinalAuditAcceptance,
    *,
    table_name: str = "final-audit acceptance",
) -> None:
    """Validate field-level final-audit acceptance semantics."""

    if not record.region_id:
        raise ValueError(f"{table_name} region_id must be non-empty")
    if not record.accepted_by:
        raise ValueError(f"{table_name} accepted_by must be non-empty")
    if not record.accepted_date:
        raise ValueError(f"{table_name} accepted_date must be non-empty")
    if record.expected_gate_count <= 0:
        raise ValueError(f"{table_name} expected_gate_count must be positive")
    if not record.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not record.evidence_paths:
        raise ValueError(f"{table_name} evidence_paths must be non-empty")


def _acceptance_from_mapping(
    row: Mapping[str, Any],
    path: Path,
) -> FinalAuditAcceptance:
    missing = [
        field for field in REQUIRED_FINAL_AUDIT_ACCEPTANCE_FIELDS if field not in row
    ]
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(missing)}")
    return FinalAuditAcceptance(
        region_id=_clean(row["region_id"]),
        accepted=_bool_field(row, "accepted", path),
        accepted_by=_clean(row["accepted_by"]),
        accepted_date=_clean(row["accepted_date"]),
        final_study_ready=_bool_field(row, "final_study_ready", path),
        prompt_to_artifact_checklist_reviewed=_bool_field(
            row,
            "prompt_to_artifact_checklist_reviewed",
            path,
        ),
        all_gate_evidence_reviewed=_bool_field(
            row,
            "all_gate_evidence_reviewed",
            path,
        ),
        no_proxy_completion_reviewed=_bool_field(
            row,
            "no_proxy_completion_reviewed",
            path,
        ),
        expected_gate_count=_positive_int(row, "expected_gate_count", path),
        reviewed_gate_ids=_clean_sequence(row["reviewed_gate_ids"], "reviewed_gate_ids", path),
        ready_gate_ids=_clean_sequence(row["ready_gate_ids"], "ready_gate_ids", path),
        blocked_gate_ids=_clean_sequence(
            row["blocked_gate_ids"],
            "blocked_gate_ids",
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
    "DEFAULT_FINAL_AUDIT_ACCEPTANCE_PATH",
    "FinalAuditAcceptance",
    "REQUIRED_FINAL_AUDIT_ACCEPTANCE_FIELDS",
    "load_final_audit_acceptance",
    "summarize_final_audit_acceptance",
    "validate_final_audit_acceptance",
]
