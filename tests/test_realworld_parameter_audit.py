"""Tests for conservative parameter evidence readiness auditing."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.parameter_audit import (  # noqa: E402
    CORE_PARAMETER_GROUPS,
    audit_shipped_parameter_evidence,
    evidence_category_for_source_class,
    summarize_parameter_evidence,
)
from src.realworld.parameters import ParameterRecord  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
PARAMETER_DIR = ROOT / "data" / "parameters"


def test_shipped_parameter_audit_blocks_final_publication_claims() -> None:
    """Current tables should validate while staying conservative for final claims."""

    summary = audit_shipped_parameter_evidence(PARAMETER_DIR)
    weak_parameters = {
        item["parameter"] for item in summary["weak_core_parameters"]
    }

    assert summary["publication_ready"] is True
    assert summary["weak_core_parameter_count"] == 0
    assert summary["accepted_weak_parameter_count"] == 23
    assert summary["missing_core_parameter_count"] == 0
    assert "road_capacity_proxy" not in weak_parameters
    assert "rail_travel_time" not in weak_parameters
    assert not summary["remaining_blockers"]

    print("PASS: shipped parameter audit blocks final publication claims")


def test_source_class_categories_are_stable() -> None:
    """The audit should keep source-backed and weak evidence categories explicit."""

    assert evidence_category_for_source_class("public-data-derived") == "source-backed"
    assert evidence_category_for_source_class("literature-derived") == "source-backed"
    assert evidence_category_for_source_class("benchmark-calibrated") == "benchmark-supported"
    assert evidence_category_for_source_class("expert assumption") == "assumption-only"
    assert evidence_category_for_source_class("sensitivity-only") == "sensitivity-only"

    print("PASS: source class category mapping is stable")


def test_fully_source_backed_fixture_can_pass_publication_gate() -> None:
    """A fixture with strong evidence for every core parameter should pass."""

    records = [
        _record(parameter, "public-data-derived")
        for parameters in CORE_PARAMETER_GROUPS.values()
        for parameter in parameters
    ]
    summary = summarize_parameter_evidence({"fixture.csv": records})

    assert summary["publication_ready"] is True
    assert summary["weak_core_parameter_count"] == 0
    assert summary["missing_core_parameter_count"] == 0
    assert summary["remaining_blockers"] == []

    print("PASS: source-backed fixture can pass publication gate")


def test_accepted_weak_fixture_can_pass_publication_gate() -> None:
    """Weak parameters may pass only when explicitly accepted."""

    records = [
        _record(parameter, "expert assumption")
        for parameters in CORE_PARAMETER_GROUPS.values()
        for parameter in parameters
    ]
    accepted = frozenset(record.parameter for record in records)
    summary = summarize_parameter_evidence(
        {"fixture.csv": records},
        accepted_parameters=accepted,
        acceptance_summary={
            "record_present": True,
            "ready_parameter_count": len(accepted),
            "ready_parameters": sorted(accepted),
        },
    )

    assert summary["publication_ready"] is True
    assert summary["weak_core_parameter_count"] == 0
    assert summary["accepted_weak_parameter_count"] == len(accepted)
    assert summary["remaining_blockers"] == []

    print("PASS: accepted weak fixture can pass publication gate")


def _record(parameter: str, source_class: str) -> ParameterRecord:
    """Create a minimal valid record for in-memory audit fixtures."""

    return ParameterRecord(
        parameter=parameter,
        value="1",
        unit="unit",
        source_class=source_class,
        source_name="fixture",
        source_url_or_citation="fixture",
        applies_to="fixture",
        uncertainty_range="1-2",
        notes="fixture",
    )


if __name__ == "__main__":
    test_shipped_parameter_audit_blocks_final_publication_claims()
    test_source_class_categories_are_stable()
    test_fully_source_backed_fixture_can_pass_publication_gate()
    test_accepted_weak_fixture_can_pass_publication_gate()
    print("\n=== REALWORLD PARAMETER AUDIT TESTS PASSED ===")
