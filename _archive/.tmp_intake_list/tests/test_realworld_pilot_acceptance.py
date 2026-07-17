"""Tests for pilot acceptance record validation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.pilot_acceptance import (  # noqa: E402
    load_pilot_acceptance,
    summarize_pilot_acceptance,
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


def test_missing_default_pilot_acceptance_is_blocked() -> None:
    """The current repository should not imply human pilot acceptance."""

    summary = summarize_pilot_acceptance()

    assert summary["acceptance_ready"] is False
    assert summary["record_present"] is False
    assert summary["remaining_blockers"]

    print("PASS: missing default pilot acceptance is blocked")


def test_acceptance_fixture_can_pass() -> None:
    """A complete acceptance record can satisfy the narrow acceptance gate."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "pilot_acceptance.json"
        _write_acceptance(path)

        record = load_pilot_acceptance(path)
        summary = summarize_pilot_acceptance(path)

        assert record.ready is True
        assert summary["acceptance_ready"] is True
        assert summary["graph_scale_decision"] == "corridor_abstraction"
        assert summary["remaining_blockers"] == []

    print("PASS: complete pilot acceptance fixture can pass")


def test_acceptance_requires_not_operational_boundary() -> None:
    """Acceptance must still block operational claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "pilot_acceptance.json"
        _write_acceptance(path, claim_boundary="accepted for operational use")

        summary = summarize_pilot_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("not operational" in item for item in summary["remaining_blockers"])

    print("PASS: pilot acceptance requires not-operational boundary")


def test_acceptance_rejects_bad_graph_scale_decision() -> None:
    """Graph-scale decision must use a known final-study option."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "pilot_acceptance.json"
        _write_acceptance(path, graph_scale_decision="unknown")

        assert_raises_value_error(
            lambda: load_pilot_acceptance(path),
            "graph_scale_decision",
        )

    print("PASS: pilot acceptance rejects bad graph-scale decision")


def test_acceptance_rejects_string_booleans() -> None:
    """Acceptance booleans must not be coerced from strings."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "pilot_acceptance.json"
        _write_acceptance(path)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["accepted"] = "true"
        path.write_text(json.dumps(value), encoding="utf-8")

        assert_raises_value_error(
            lambda: load_pilot_acceptance(path),
            "must be boolean",
        )

    print("PASS: pilot acceptance rejects string booleans")


def _write_acceptance(
    path: Path,
    *,
    claim_boundary: str = "Accepted for quasi-real decision-support study; not operational routing.",
    graph_scale_decision: str = "corridor_abstraction",
) -> None:
    value = {
        "region_id": "songpa_public_demo",
        "accepted": True,
        "accepted_by": "fixture reviewer",
        "accepted_date": "2026-05-04",
        "acceptance_scope": "fixture acceptance",
        "privacy_review_complete": True,
        "graph_scale_decision": graph_scale_decision,
        "claim_boundary": claim_boundary,
        "evidence_paths": [
            "data/regions/pilot_region.yaml",
            "docs/pilot_region_data_card.md",
        ],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle)


if __name__ == "__main__":
    test_missing_default_pilot_acceptance_is_blocked()
    test_acceptance_fixture_can_pass()
    test_acceptance_requires_not_operational_boundary()
    test_acceptance_rejects_bad_graph_scale_decision()
    test_acceptance_rejects_string_booleans()
    print("\n=== REALWORLD PILOT ACCEPTANCE TESTS PASSED ===")
