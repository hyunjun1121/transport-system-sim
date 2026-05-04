"""Tests for generic sub-agent acceptance-record validation."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.acceptance_records import (  # noqa: E402
    AcceptanceRecord,
    acceptance_record_from_mapping,
    acceptance_record_schema,
    validate_acceptance_record_mapping,
)


def _blocked_record() -> dict[str, object]:
    return {
        "gate_id": "pilot_region_accepted",
        "agent": "Pilot Region & Privacy Review Agent",
        "status": "needs_human_review",
        "decision": "Human privacy review is required.",
        "evidence": ["docs/pilot_region_data_card.md"],
        "source_paths": ["data/regions/pilot_region.yaml"],
        "reviewed_inputs": ["data/regions/pilot_region.yaml"],
        "risks": ["Privacy decision is missing."],
        "required_actions": ["Create pilot acceptance record after review."],
        "generated_at": "2026-05-04T00:00:00+00:00",
        "can_mark_complete": False,
    }


def test_acceptance_record_validates_blocked_or_review_status() -> None:
    value = _blocked_record()
    validate_acceptance_record_mapping(value)
    record = acceptance_record_from_mapping(value)
    assert isinstance(record, AcceptanceRecord)
    assert record.status == "needs_human_review"
    assert record.can_mark_complete is False


def test_acceptance_record_rejects_success_shaped_nonaccepted_record() -> None:
    value = _blocked_record()
    value["required_actions"] = []
    try:
        validate_acceptance_record_mapping(value)
    except ValueError as exc:
        assert "required_actions" in str(exc)
    else:
        raise AssertionError("expected missing required_actions to fail")


def test_acceptance_record_rejects_can_mark_complete_without_acceptance() -> None:
    value = _blocked_record()
    value["can_mark_complete"] = True
    try:
        validate_acceptance_record_mapping(value)
    except ValueError as exc:
        assert "can_mark_complete" in str(exc)
    else:
        raise AssertionError("expected invalid can_mark_complete to fail")


def test_acceptance_record_schema_contains_required_fields() -> None:
    schema = acceptance_record_schema()
    required = set(schema["required"])
    assert "gate_id" in required
    assert "status" in required
    assert "can_mark_complete" in required


if __name__ == "__main__":
    test_acceptance_record_validates_blocked_or_review_status()
    test_acceptance_record_rejects_success_shaped_nonaccepted_record()
    test_acceptance_record_rejects_can_mark_complete_without_acceptance()
    test_acceptance_record_schema_contains_required_fields()
    print("PASS: acceptance-record schema validation")
