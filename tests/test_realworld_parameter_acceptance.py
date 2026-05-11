"""Tests for weak-parameter acceptance records."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.parameter_acceptance import (  # noqa: E402
    REQUIRED_COLUMNS,
    load_parameter_acceptance,
    ready_accepted_parameters,
    summarize_parameter_acceptance,
)


def assert_raises_value_error(func, expected_message: str) -> None:
    """Assert that a zero-argument function raises ValueError with context."""

    try:
        func()
    except ValueError as exc:
        message = str(exc)
        assert expected_message in message, message
        return
    raise AssertionError("expected ValueError")


def test_missing_default_parameter_acceptance_is_reported() -> None:
    """Current scaffold should not silently accept weak assumptions."""

    summary = summarize_parameter_acceptance()

    assert summary["record_present"] is False
    assert summary["ready_parameter_count"] == 0
    assert summary["remaining_blockers"]

    print("PASS: missing default parameter acceptance is reported")


def test_parameter_acceptance_fixture_can_pass() -> None:
    """A complete reviewed acceptance row can accept one weak parameter."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "parameter_acceptance.csv"
        _write_acceptance(path, parameter="road_capacity_proxy")

        records = load_parameter_acceptance(path)
        summary = summarize_parameter_acceptance(path)

        assert records[0].ready is True
        assert ready_accepted_parameters(records) == frozenset({"road_capacity_proxy"})
        assert summary["ready_parameters"] == ["road_capacity_proxy"]
        assert summary["remaining_blockers"] == []

    print("PASS: parameter acceptance fixture can pass")


def test_parameter_acceptance_requires_not_operational_boundary() -> None:
    """Accepted weak parameters must still block operational claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "parameter_acceptance.csv"
        _write_acceptance(
            path,
            parameter="road_capacity_proxy",
            claim_boundary="accepted for operational use",
        )

        summary = summarize_parameter_acceptance(path)

        assert summary["ready_parameter_count"] == 0
        assert summary["remaining_blockers"]

    print("PASS: parameter acceptance requires not-operational boundary")


def test_parameter_acceptance_rejects_bad_boolean() -> None:
    """CSV booleans must be explicit true/false tokens."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "parameter_acceptance.csv"
        _write_acceptance(path, parameter="road_capacity_proxy", accepted="yes")

        assert_raises_value_error(
            lambda: load_parameter_acceptance(path),
            "must be true or false",
        )

    print("PASS: parameter acceptance rejects bad booleans")


def _write_acceptance(
    path: Path,
    *,
    parameter: str,
    accepted: str = "true",
    sensitivity_reviewed: str = "true",
    claim_boundary: str = "Accepted for bounded decision-support sensitivity use; not operational routing.",
) -> None:
    row = {
        "parameter": parameter,
        "accepted": accepted,
        "accepted_by": "fixture reviewer",
        "accepted_date": "2026-05-04",
        "acceptance_scope": "fixture parameter acceptance",
        "claim_boundary": claim_boundary,
        "sensitivity_reviewed": sensitivity_reviewed,
        "evidence_paths": "data/parameters/parameter_sources.csv;docs/schemas/pilot_acceptance_schema.md",
        "notes": "fixture row",
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    test_missing_default_parameter_acceptance_is_reported()
    test_parameter_acceptance_fixture_can_pass()
    test_parameter_acceptance_requires_not_operational_boundary()
    test_parameter_acceptance_rejects_bad_boolean()
    print("\n=== REALWORLD PARAMETER ACCEPTANCE TESTS PASSED ===")
