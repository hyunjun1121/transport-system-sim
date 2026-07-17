"""Tests for clean-checkout reproducibility acceptance record validation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.reproducibility_acceptance import (  # noqa: E402
    load_reproducibility_acceptance,
    summarize_reproducibility_acceptance,
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


def test_missing_default_reproducibility_acceptance_is_blocked() -> None:
    """The current repository should not imply reproducibility acceptance."""

    summary = summarize_reproducibility_acceptance()

    assert summary["acceptance_ready"] is False
    assert summary["record_present"] is False
    assert summary["remaining_blockers"]

    print("PASS: missing default reproducibility acceptance is blocked")


def test_reproducibility_acceptance_fixture_can_pass() -> None:
    """A complete reproducibility acceptance record can satisfy the narrow gate."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "reproducibility_acceptance.json"
        _write_acceptance(path)

        record = load_reproducibility_acceptance(path)
        summary = summarize_reproducibility_acceptance(path)

        assert record.ready is True
        assert summary["acceptance_ready"] is True
        assert summary["remaining_blockers"] == []

    print("PASS: complete reproducibility acceptance fixture can pass")


def test_reproducibility_acceptance_rejects_string_booleans() -> None:
    """Acceptance booleans must not be coerced from strings."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "reproducibility_acceptance.json"
        _write_acceptance(path)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["clean_checkout_tested"] = "true"
        path.write_text(json.dumps(value), encoding="utf-8")

        assert_raises_value_error(
            lambda: load_reproducibility_acceptance(path),
            "must be boolean",
        )

    print("PASS: reproducibility acceptance rejects string booleans")


def test_reproducibility_acceptance_requires_clean_checkout() -> None:
    """Clean-checkout validation must be explicitly reviewed."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "reproducibility_acceptance.json"
        _write_acceptance(path, clean_checkout_tested=False)

        summary = summarize_reproducibility_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("clean_checkout_tested" in item for item in summary["remaining_blockers"])

    print("PASS: reproducibility acceptance requires clean checkout")


def test_reproducibility_acceptance_rejects_bad_command_count() -> None:
    """Validation command counts must be positive integers."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "reproducibility_acceptance.json"
        _write_acceptance(path, expected_validation_command_count=0)

        assert_raises_value_error(
            lambda: load_reproducibility_acceptance(path),
            "expected_validation_command_count",
        )

    print("PASS: reproducibility acceptance rejects bad command count")


def test_reproducibility_acceptance_requires_not_operational_boundary() -> None:
    """Reproducibility acceptance must still block operational claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "reproducibility_acceptance.json"
        _write_acceptance(path, claim_boundary="accepted as operational package")

        summary = summarize_reproducibility_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("not operational" in item for item in summary["remaining_blockers"])

    print("PASS: reproducibility acceptance requires not-operational boundary")


def _write_acceptance(
    path: Path,
    *,
    clean_checkout_tested: bool = True,
    expected_validation_command_count: int = 19,
    claim_boundary: str = "Accepted for quasi-real decision-support study; not operational routing.",
) -> None:
    value = {
        "region_id": "songpa_public_demo",
        "accepted": True,
        "accepted_by": "fixture reviewer",
        "accepted_date": "2026-05-04",
        "clean_checkout_tested": clean_checkout_tested,
        "validation_ladder_passed": True,
        "artifact_regeneration_tested": True,
        "manifest_paths_reviewed": True,
        "no_runtime_cloned_repo_imports": True,
        "expected_validation_command_count": expected_validation_command_count,
        "claim_boundary": claim_boundary,
        "evidence_paths": [
            "docs/reproducibility_package.md",
            "data/manifests/reproducibility_manifest.json",
            "docs/final_study_audit.md",
        ],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle)


if __name__ == "__main__":
    test_missing_default_reproducibility_acceptance_is_blocked()
    test_reproducibility_acceptance_fixture_can_pass()
    test_reproducibility_acceptance_rejects_string_booleans()
    test_reproducibility_acceptance_requires_clean_checkout()
    test_reproducibility_acceptance_rejects_bad_command_count()
    test_reproducibility_acceptance_requires_not_operational_boundary()
    print("\n=== REALWORLD REPRODUCIBILITY ACCEPTANCE TESTS PASSED ===")
