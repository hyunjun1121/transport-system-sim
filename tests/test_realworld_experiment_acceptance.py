"""Tests for pilot experiment-output acceptance record validation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.experiment_acceptance import (  # noqa: E402
    load_experiment_acceptance,
    summarize_experiment_acceptance,
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


def test_missing_default_experiment_acceptance_is_blocked() -> None:
    """Phase V created a formal experiment acceptance record; acceptance is ready."""

    summary = summarize_experiment_acceptance()

    assert summary["acceptance_ready"] is True
    assert summary["record_present"] is True
    assert summary["remaining_blockers"] == []

    print("PASS: default experiment acceptance is ready (Phase V)")


def test_experiment_acceptance_fixture_can_pass() -> None:
    """A complete experiment acceptance record can satisfy the narrow gate."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "experiment_acceptance.json"
        _write_acceptance(path)

        record = load_experiment_acceptance(path)
        summary = summarize_experiment_acceptance(path)

        assert record.ready is True
        assert summary["acceptance_ready"] is True
        assert summary["run_profile"] == "full_pilot"
        assert summary["remaining_blockers"] == []

    print("PASS: complete experiment acceptance fixture can pass")


def test_experiment_acceptance_rejects_bad_profile() -> None:
    """Run profile must use a known final-study option."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "experiment_acceptance.json"
        _write_acceptance(path, run_profile="sample_scaffold")

        assert_raises_value_error(
            lambda: load_experiment_acceptance(path),
            "run_profile",
        )

    print("PASS: experiment acceptance rejects bad profile")


def test_experiment_acceptance_rejects_string_booleans() -> None:
    """Acceptance booleans must not be coerced from strings."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "experiment_acceptance.json"
        _write_acceptance(path)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["input_validation_accepted"] = "true"
        path.write_text(json.dumps(value), encoding="utf-8")

        assert_raises_value_error(
            lambda: load_experiment_acceptance(path),
            "must be boolean",
        )

    print("PASS: experiment acceptance rejects string booleans")


def test_experiment_acceptance_requires_input_validation() -> None:
    """Accepted outputs require accepted input validation."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "experiment_acceptance.json"
        _write_acceptance(path, input_validation_accepted=False)

        summary = summarize_experiment_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("input_validation_accepted" in item for item in summary["remaining_blockers"])

    print("PASS: experiment acceptance requires input validation")


def test_experiment_acceptance_requires_not_operational_boundary() -> None:
    """Experiment acceptance must still block operational claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "experiment_acceptance.json"
        _write_acceptance(path, claim_boundary="accepted for operational routing")

        summary = summarize_experiment_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("not operational" in item for item in summary["remaining_blockers"])

    print("PASS: experiment acceptance requires not-operational boundary")


def _write_acceptance(
    path: Path,
    *,
    run_profile: str = "full_pilot",
    input_validation_accepted: bool = True,
    claim_boundary: str = "Accepted for quasi-real decision-support study; not operational routing.",
) -> None:
    value = {
        "region_id": "songpa_public_demo",
        "accepted": True,
        "accepted_by": "fixture reviewer",
        "accepted_date": "2026-05-04",
        "run_profile": run_profile,
        "expected_row_count": 1890,
        "expected_summary_row_count": 63,
        "policy_count": 7,
        "scenario_count": 9,
        "seed_count": 30,
        "graph_scope_accepted": True,
        "input_validation_accepted": input_validation_accepted,
        "scenario_policy_seed_design_reviewed": True,
        "common_random_numbers_reviewed": True,
        "claim_boundary": claim_boundary,
        "evidence_paths": [
            "results/realworld_pilot/pilot_full_results.csv",
            "results/realworld_pilot/pilot_full_summary.csv",
            "results/realworld_pilot/pilot_full_manifest.json",
        ],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle)


if __name__ == "__main__":
    test_missing_default_experiment_acceptance_is_blocked()
    test_experiment_acceptance_fixture_can_pass()
    test_experiment_acceptance_rejects_bad_profile()
    test_experiment_acceptance_rejects_string_booleans()
    test_experiment_acceptance_requires_input_validation()
    test_experiment_acceptance_requires_not_operational_boundary()
    print("\n=== REALWORLD EXPERIMENT ACCEPTANCE TESTS PASSED ===")
