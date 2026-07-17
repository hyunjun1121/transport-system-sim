"""Tests for sensitivity-analysis acceptance record validation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.sensitivity_acceptance import (  # noqa: E402
    load_sensitivity_acceptance,
    summarize_sensitivity_acceptance,
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


def test_missing_default_sensitivity_acceptance_is_blocked() -> None:
    """The current repository should not imply sensitivity acceptance."""

    summary = summarize_sensitivity_acceptance()

    assert summary["acceptance_ready"] is False
    assert summary["record_present"] is False
    assert summary["remaining_blockers"]

    print("PASS: missing default sensitivity acceptance is blocked")


def test_sensitivity_acceptance_fixture_can_pass() -> None:
    """A complete sensitivity acceptance record can satisfy the narrow gate."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "sensitivity_acceptance.json"
        _write_acceptance(path)

        record = load_sensitivity_acceptance(path)
        summary = summarize_sensitivity_acceptance(path)

        assert record.ready is True
        assert summary["acceptance_ready"] is True
        assert summary["sensitivity_method"] == "salib_morris"
        assert summary["remaining_blockers"] == []

    print("PASS: complete sensitivity acceptance fixture can pass")


def test_sensitivity_acceptance_rejects_bad_method() -> None:
    """Sensitivity method must use a known final-study option."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "sensitivity_acceptance.json"
        _write_acceptance(path, sensitivity_method="unknown")

        assert_raises_value_error(
            lambda: load_sensitivity_acceptance(path),
            "sensitivity_method",
        )

    print("PASS: sensitivity acceptance rejects bad method")


def test_sensitivity_acceptance_rejects_string_booleans() -> None:
    """Acceptance booleans must not be coerced from strings."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "sensitivity_acceptance.json"
        _write_acceptance(path)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["salib_output_reviewed"] = "true"
        path.write_text(json.dumps(value), encoding="utf-8")

        assert_raises_value_error(
            lambda: load_sensitivity_acceptance(path),
            "must be boolean",
        )

    print("PASS: sensitivity acceptance rejects string booleans")


def test_sobol_required_pending_blocks_acceptance() -> None:
    """If Sobol is required, final acceptance should stay blocked until complete."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "sensitivity_acceptance.json"
        _write_acceptance(path, sobol_requirement_decision="required_pending")

        summary = summarize_sensitivity_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("Sobol" in item for item in summary["remaining_blockers"])

    print("PASS: pending Sobol decision blocks sensitivity acceptance")


def test_sensitivity_acceptance_requires_not_operational_boundary() -> None:
    """Sensitivity acceptance must still block operational claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "sensitivity_acceptance.json"
        _write_acceptance(path, claim_boundary="accepted for operational routing")

        summary = summarize_sensitivity_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("not operational" in item for item in summary["remaining_blockers"])

    print("PASS: sensitivity acceptance requires not-operational boundary")


def _write_acceptance(
    path: Path,
    *,
    sensitivity_method: str = "salib_morris",
    sobol_requirement_decision: str = "not_required",
    claim_boundary: str = "Accepted for quasi-real decision-support study; not operational routing.",
) -> None:
    value = {
        "region_id": "songpa_public_demo",
        "accepted": True,
        "accepted_by": "fixture reviewer",
        "accepted_date": "2026-05-04",
        "sensitivity_method": sensitivity_method,
        "result_scope": "Accepted fixture sensitivity result scope.",
        "expected_row_count": 4320,
        "expected_summary_row_count": 7056,
        "graph_scope_accepted": True,
        "parameter_ranges_reviewed": True,
        "salib_output_reviewed": True,
        "nan_or_masked_values_reviewed": True,
        "sobol_requirement_decision": sobol_requirement_decision,
        "claim_boundary": claim_boundary,
        "evidence_paths": [
            "results/realworld_pilot/morris_results.csv",
            "results/realworld_pilot/morris_summary.csv",
            "results/realworld_pilot/morris_manifest.json",
        ],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle)


if __name__ == "__main__":
    test_missing_default_sensitivity_acceptance_is_blocked()
    test_sensitivity_acceptance_fixture_can_pass()
    test_sensitivity_acceptance_rejects_bad_method()
    test_sensitivity_acceptance_rejects_string_booleans()
    test_sobol_required_pending_blocks_acceptance()
    test_sensitivity_acceptance_requires_not_operational_boundary()
    print("\n=== REALWORLD SENSITIVITY ACCEPTANCE TESTS PASSED ===")
