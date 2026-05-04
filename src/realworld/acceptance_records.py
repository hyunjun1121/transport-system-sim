"""Common schema validation for review-agent acceptance records.

The records validated here are machine-readable review outputs. They are not
the same as the formal final-study acceptance artifacts such as
``data/manifests/pilot_acceptance.json``. A record may only mark a gate
complete when the existing final-study readiness audit already considers that
gate ready.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ALLOWED_ACCEPTANCE_STATUSES: frozenset[str] = frozenset(
    {"accepted", "blocked", "needs_human_review", "not_applicable"}
)
REQUIRED_ACCEPTANCE_RECORD_FIELDS: tuple[str, ...] = (
    "gate_id",
    "agent",
    "status",
    "decision",
    "evidence",
    "source_paths",
    "reviewed_inputs",
    "risks",
    "required_actions",
    "generated_at",
    "can_mark_complete",
)


@dataclass(frozen=True)
class AcceptanceRecord:
    """One conservative sub-agent review record for one final-study gate."""

    gate_id: str
    agent: str
    status: str
    decision: str
    evidence: tuple[str, ...]
    source_paths: tuple[str, ...]
    reviewed_inputs: tuple[str, ...]
    risks: tuple[str, ...]
    required_actions: tuple[str, ...]
    generated_at: str
    can_mark_complete: bool
    schema_version: int = 1
    agent_id: str = ""
    record_type: str = "sub_agent_gate_review"
    claim_boundary: str = (
        "Machine-readable review aid only; this is not formal final-study "
        "acceptance and not operational routing approval."
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation."""

        return {
            "schema_version": self.schema_version,
            "record_type": self.record_type,
            "gate_id": self.gate_id,
            "agent_id": self.agent_id,
            "agent": self.agent,
            "status": self.status,
            "decision": self.decision,
            "evidence": list(self.evidence),
            "source_paths": list(self.source_paths),
            "reviewed_inputs": list(self.reviewed_inputs),
            "risks": list(self.risks),
            "required_actions": list(self.required_actions),
            "generated_at": self.generated_at,
            "can_mark_complete": self.can_mark_complete,
            "claim_boundary": self.claim_boundary,
        }


def acceptance_record_from_mapping(value: Mapping[str, Any]) -> AcceptanceRecord:
    """Build and validate an ``AcceptanceRecord`` from JSON-like data."""

    validate_acceptance_record_mapping(value)
    return AcceptanceRecord(
        schema_version=_positive_int(value.get("schema_version", 1), "schema_version"),
        record_type=_clean(value.get("record_type", "sub_agent_gate_review")),
        gate_id=_clean(value["gate_id"]),
        agent_id=_clean(value.get("agent_id", "")),
        agent=_clean(value["agent"]),
        status=_clean(value["status"]),
        decision=_clean(value["decision"]),
        evidence=_clean_sequence(value["evidence"], "evidence"),
        source_paths=_clean_sequence(value["source_paths"], "source_paths"),
        reviewed_inputs=_clean_sequence(value["reviewed_inputs"], "reviewed_inputs"),
        risks=_clean_sequence(value["risks"], "risks"),
        required_actions=_clean_sequence(value["required_actions"], "required_actions"),
        generated_at=_clean(value["generated_at"]),
        can_mark_complete=_bool_value(value["can_mark_complete"], "can_mark_complete"),
        claim_boundary=_clean(value.get("claim_boundary", "")),
    )


def load_acceptance_record(path: str | Path) -> AcceptanceRecord:
    """Load and validate one review-agent acceptance record."""

    record_path = Path(path)
    with record_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, Mapping):
        raise ValueError(f"{record_path} must contain a JSON object")
    return acceptance_record_from_mapping(value)


def validate_acceptance_record_mapping(value: Mapping[str, Any]) -> None:
    """Validate required fields and conservative status semantics."""

    missing = [field for field in REQUIRED_ACCEPTANCE_RECORD_FIELDS if field not in value]
    if missing:
        raise ValueError(
            "acceptance record missing required fields: " + ", ".join(missing)
        )

    gate_id = _clean(value["gate_id"])
    agent = _clean(value["agent"])
    status = _clean(value["status"])
    decision = _clean(value["decision"])
    generated_at = _clean(value["generated_at"])
    can_mark_complete = _bool_value(value["can_mark_complete"], "can_mark_complete")
    evidence = _clean_sequence(value["evidence"], "evidence")
    source_paths = _clean_sequence(value["source_paths"], "source_paths")
    reviewed_inputs = _clean_sequence(value["reviewed_inputs"], "reviewed_inputs")
    risks = _clean_sequence(value["risks"], "risks")
    required_actions = _clean_sequence(value["required_actions"], "required_actions")

    if not gate_id:
        raise ValueError("acceptance record gate_id must be non-empty")
    if not agent:
        raise ValueError("acceptance record agent must be non-empty")
    if status not in ALLOWED_ACCEPTANCE_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_ACCEPTANCE_STATUSES))
        raise ValueError(f"acceptance record status must be one of: {allowed}")
    if not decision:
        raise ValueError("acceptance record decision must be non-empty")
    if not generated_at:
        raise ValueError("acceptance record generated_at must be non-empty")
    if not reviewed_inputs:
        raise ValueError("acceptance record reviewed_inputs must be non-empty")

    if can_mark_complete and status != "accepted":
        raise ValueError("can_mark_complete requires status 'accepted'")
    if status == "accepted":
        if not can_mark_complete:
            raise ValueError("accepted records must set can_mark_complete: true")
        if not evidence:
            raise ValueError("accepted records must list evidence")
        if not source_paths:
            raise ValueError("accepted records must list source_paths")
    else:
        if can_mark_complete:
            raise ValueError("non-accepted records cannot mark a gate complete")
        if status != "not_applicable" and not required_actions:
            raise ValueError("blocked or human-review records must list required_actions")
        if status != "not_applicable" and not risks:
            raise ValueError("blocked or human-review records must list risks")


def acceptance_record_schema() -> dict[str, Any]:
    """Return the JSON Schema written to ``schemas/acceptance_record.schema.json``."""

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Transport Simulation Sub-Agent Acceptance Record",
        "type": "object",
        "required": list(REQUIRED_ACCEPTANCE_RECORD_FIELDS),
        "properties": {
            "schema_version": {"type": "integer", "minimum": 1},
            "record_type": {"type": "string"},
            "gate_id": {"type": "string", "minLength": 1},
            "agent_id": {"type": "string"},
            "agent": {"type": "string", "minLength": 1},
            "status": {"type": "string", "enum": sorted(ALLOWED_ACCEPTANCE_STATUSES)},
            "decision": {"type": "string", "minLength": 1},
            "evidence": {"type": "array", "items": {"type": "string"}},
            "source_paths": {"type": "array", "items": {"type": "string"}},
            "reviewed_inputs": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string"},
            },
            "risks": {"type": "array", "items": {"type": "string"}},
            "required_actions": {"type": "array", "items": {"type": "string"}},
            "generated_at": {"type": "string", "minLength": 1},
            "can_mark_complete": {"type": "boolean"},
            "claim_boundary": {"type": "string"},
        },
        "additionalProperties": True,
    }


def write_acceptance_record_schema(path: str | Path) -> None:
    """Write the JSON Schema file used by human reviewers and CI checks."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(acceptance_record_schema(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _clean_sequence(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise ValueError(f"acceptance record field {field!r} must be a list")
    return tuple(_clean(item) for item in value if _clean(item))


def _bool_value(value: object, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"acceptance record field {field!r} must be boolean")
    return value


def _positive_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"acceptance record field {field!r} must be an integer")
    if value < 1:
        raise ValueError(f"acceptance record field {field!r} must be positive")
    return value


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


__all__ = [
    "ALLOWED_ACCEPTANCE_STATUSES",
    "AcceptanceRecord",
    "REQUIRED_ACCEPTANCE_RECORD_FIELDS",
    "acceptance_record_from_mapping",
    "acceptance_record_schema",
    "load_acceptance_record",
    "validate_acceptance_record_mapping",
    "write_acceptance_record_schema",
]
