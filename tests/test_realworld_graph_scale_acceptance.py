"""Tests for graph-scale acceptance record validation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.graph_scale_acceptance import (  # noqa: E402
    load_graph_scale_acceptance,
    summarize_graph_scale_acceptance,
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


def test_missing_default_graph_scale_acceptance_is_blocked() -> None:
    """The current repository should not imply graph-scale acceptance."""

    summary = summarize_graph_scale_acceptance()

    assert summary["acceptance_ready"] is False
    assert summary["record_present"] is False
    assert summary["remaining_blockers"]

    print("PASS: missing default graph-scale acceptance is blocked")


def test_graph_scale_acceptance_fixture_can_pass() -> None:
    """A complete graph-scale acceptance record can satisfy the gate."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "graph_scale_acceptance.json"
        _write_acceptance(path)

        record = load_graph_scale_acceptance(path)
        summary = summarize_graph_scale_acceptance(path)

        assert record.ready is True
        assert summary["acceptance_ready"] is True
        assert summary["graph_scale_decision"] == "corridor_abstraction"
        assert summary["remaining_blockers"] == []

    print("PASS: complete graph-scale acceptance fixture can pass")


def test_graph_scale_acceptance_rejects_bad_decision() -> None:
    """Graph-scale decision must use a known final-study option."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "graph_scale_acceptance.json"
        _write_acceptance(path, graph_scale_decision="unknown")

        assert_raises_value_error(
            lambda: load_graph_scale_acceptance(path),
            "graph_scale_decision",
        )

    print("PASS: graph-scale acceptance rejects bad decision")


def test_graph_scale_acceptance_rejects_string_booleans() -> None:
    """Acceptance booleans must not be coerced from strings."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "graph_scale_acceptance.json"
        _write_acceptance(path)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["corridor_reduction_accepted"] = "true"
        path.write_text(json.dumps(value), encoding="utf-8")

        assert_raises_value_error(
            lambda: load_graph_scale_acceptance(path),
            "must be boolean",
        )

    print("PASS: graph-scale acceptance rejects string booleans")


def test_corridor_abstraction_requires_sensitivity_review() -> None:
    """Corridor abstraction requires explicit reduction and sensitivity review."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "graph_scale_acceptance.json"
        _write_acceptance(path, alternate_corridor_sensitivity_reviewed=False)

        summary = summarize_graph_scale_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any(
            "alternate_corridor_sensitivity_reviewed" in item
            for item in summary["remaining_blockers"]
        )

    print("PASS: corridor abstraction requires sensitivity review")


def test_graph_scale_acceptance_requires_not_operational_boundary() -> None:
    """Graph-scale acceptance must still block operational claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "graph_scale_acceptance.json"
        _write_acceptance(path, claim_boundary="accepted for operational routing")

        summary = summarize_graph_scale_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("not operational" in item for item in summary["remaining_blockers"])

    print("PASS: graph-scale acceptance requires not-operational boundary")


def _write_acceptance(
    path: Path,
    *,
    graph_scale_decision: str = "corridor_abstraction",
    alternate_corridor_sensitivity_reviewed: bool = True,
    claim_boundary: str = "Accepted for quasi-real decision-support study; not operational routing.",
) -> None:
    value = {
        "region_id": "songpa_public_demo",
        "accepted": True,
        "accepted_by": "fixture reviewer",
        "accepted_date": "2026-05-04",
        "graph_scale_decision": graph_scale_decision,
        "source_graph_nodes": 4608,
        "source_graph_edges": 9148,
        "analysis_graph_nodes": 118,
        "analysis_graph_edges": 174,
        "corridor_reduction_accepted": True,
        "alternate_corridor_sensitivity_reviewed": alternate_corridor_sensitivity_reviewed,
        "claim_boundary": claim_boundary,
        "evidence_paths": [
            "docs/analysis_corridor_method_note.md",
            "results/realworld_pilot/pilot_full_manifest.json",
        ],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle)


if __name__ == "__main__":
    test_missing_default_graph_scale_acceptance_is_blocked()
    test_graph_scale_acceptance_fixture_can_pass()
    test_graph_scale_acceptance_rejects_bad_decision()
    test_graph_scale_acceptance_rejects_string_booleans()
    test_corridor_abstraction_requires_sensitivity_review()
    test_graph_scale_acceptance_requires_not_operational_boundary()
    print("\n=== REALWORLD GRAPH-SCALE ACCEPTANCE TESTS PASSED ===")
