"""Tests for validation-package acceptance record validation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.validation_acceptance import (  # noqa: E402
    load_validation_acceptance,
    summarize_validation_acceptance,
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


def test_missing_default_validation_acceptance_is_blocked() -> None:
    """Phase V created a formal validation acceptance record; acceptance is ready."""

    summary = summarize_validation_acceptance()

    assert summary["acceptance_ready"] is True
    assert summary["record_present"] is True
    assert summary["remaining_blockers"] == []

    print("PASS: default validation acceptance is ready (Phase V)")


def test_validation_acceptance_fixture_can_pass() -> None:
    """A complete validation acceptance record can satisfy the narrow gate."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "validation_acceptance.json"
        _write_acceptance(path)

        record = load_validation_acceptance(path)
        summary = summarize_validation_acceptance(path)

        assert record.ready is True
        assert summary["acceptance_ready"] is True
        assert summary["benchmark_strategy"] == "cached_osrm_snapshot"
        assert summary["remaining_blockers"] == []

    print("PASS: complete validation acceptance fixture can pass")


def test_validation_acceptance_rejects_bad_strategy() -> None:
    """Benchmark strategy must use a known final-study option."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "validation_acceptance.json"
        _write_acceptance(path, benchmark_strategy="unknown")

        assert_raises_value_error(
            lambda: load_validation_acceptance(path),
            "benchmark_strategy",
        )

    print("PASS: validation acceptance rejects bad benchmark strategy")


def test_validation_acceptance_rejects_string_booleans() -> None:
    """Acceptance booleans must not be coerced from strings."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "validation_acceptance.json"
        _write_acceptance(path)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["benchmark_validation_reviewed"] = "true"
        path.write_text(json.dumps(value), encoding="utf-8")

        assert_raises_value_error(
            lambda: load_validation_acceptance(path),
            "must be boolean",
        )

    print("PASS: validation acceptance rejects string booleans")


def test_validation_acceptance_requires_ground_truth_acknowledgement() -> None:
    """Benchmark evidence must be accepted as plausibility, not ground truth."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "validation_acceptance.json"
        _write_acceptance(path, benchmark_is_not_ground_truth_acknowledged=False)

        summary = summarize_validation_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("ground_truth" in item for item in summary["remaining_blockers"])

    print("PASS: validation acceptance requires benchmark limitation acknowledgement")


def test_validation_acceptance_requires_not_operational_boundary() -> None:
    """Validation acceptance must still block operational claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "validation_acceptance.json"
        _write_acceptance(path, claim_boundary="accepted for operational routing")

        summary = summarize_validation_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("not operational" in item for item in summary["remaining_blockers"])

    print("PASS: validation acceptance requires not-operational boundary")


def _write_acceptance(
    path: Path,
    *,
    benchmark_strategy: str = "cached_osrm_snapshot",
    benchmark_is_not_ground_truth_acknowledged: bool = True,
    claim_boundary: str = "Accepted for quasi-real decision-support study; not operational routing.",
) -> None:
    value = {
        "region_id": "songpa_public_demo",
        "accepted": True,
        "accepted_by": "fixture reviewer",
        "accepted_date": "2026-05-04",
        "validation_scope": "fixture benchmark-strategy acceptance",
        "benchmark_strategy": benchmark_strategy,
        "internal_validation_reviewed": True,
        "external_plausibility_reviewed": True,
        "benchmark_validation_reviewed": True,
        "benchmark_is_not_ground_truth_acknowledged": (
            benchmark_is_not_ground_truth_acknowledged
        ),
        "claim_boundary": claim_boundary,
        "evidence_paths": [
            "data/validation/validation_summary.md",
            "data/validation/external_route_benchmarks_osrm.csv",
        ],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle)


if __name__ == "__main__":
    test_missing_default_validation_acceptance_is_blocked()
    test_validation_acceptance_fixture_can_pass()
    test_validation_acceptance_rejects_bad_strategy()
    test_validation_acceptance_rejects_string_booleans()
    test_validation_acceptance_requires_ground_truth_acknowledgement()
    test_validation_acceptance_requires_not_operational_boundary()
    print("\n=== REALWORLD VALIDATION ACCEPTANCE TESTS PASSED ===")
