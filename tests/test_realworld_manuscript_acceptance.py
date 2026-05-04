"""Tests for manuscript/report acceptance record validation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.manuscript_acceptance import (  # noqa: E402
    load_manuscript_acceptance,
    summarize_manuscript_acceptance,
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


def test_missing_default_manuscript_acceptance_is_blocked() -> None:
    """The current repository should not imply manuscript/report acceptance."""

    summary = summarize_manuscript_acceptance()

    assert summary["acceptance_ready"] is False
    assert summary["record_present"] is False
    assert summary["remaining_blockers"]

    print("PASS: missing default manuscript acceptance is blocked")


def test_manuscript_acceptance_fixture_can_pass() -> None:
    """A complete manuscript/report acceptance record can satisfy the narrow gate."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "manuscript_acceptance.json"
        _write_acceptance(path)

        record = load_manuscript_acceptance(path)
        summary = summarize_manuscript_acceptance(path)

        assert record.ready is True
        assert summary["acceptance_ready"] is True
        assert summary["remaining_blockers"] == []

    print("PASS: complete manuscript acceptance fixture can pass")


def test_manuscript_acceptance_rejects_string_booleans() -> None:
    """Acceptance booleans must not be coerced from strings."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "manuscript_acceptance.json"
        _write_acceptance(path)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["paper_reviewed"] = "true"
        path.write_text(json.dumps(value), encoding="utf-8")

        assert_raises_value_error(
            lambda: load_manuscript_acceptance(path),
            "must be boolean",
        )

    print("PASS: manuscript acceptance rejects string booleans")


def test_manuscript_acceptance_requires_report_review() -> None:
    """The Korean report must be explicitly reviewed."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "manuscript_acceptance.json"
        _write_acceptance(path, korean_report_reviewed=False)

        summary = summarize_manuscript_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("korean_report_reviewed" in item for item in summary["remaining_blockers"])

    print("PASS: manuscript acceptance requires report review")


def test_manuscript_acceptance_requires_result_alignment() -> None:
    """Result claims must be aligned with accepted evidence before readiness."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "manuscript_acceptance.json"
        _write_acceptance(path, result_claims_aligned=False)

        summary = summarize_manuscript_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("result_claims_aligned" in item for item in summary["remaining_blockers"])

    print("PASS: manuscript acceptance requires result alignment")


def test_manuscript_acceptance_requires_not_operational_boundary() -> None:
    """Manuscript/report acceptance must still block operational claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "manuscript_acceptance.json"
        _write_acceptance(path, claim_boundary="accepted as operational guidance")

        summary = summarize_manuscript_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("not operational" in item for item in summary["remaining_blockers"])

    print("PASS: manuscript acceptance requires not-operational boundary")


def _write_acceptance(
    path: Path,
    *,
    korean_report_reviewed: bool = True,
    result_claims_aligned: bool = True,
    claim_boundary: str = "Accepted for quasi-real decision-support study; not operational routing.",
) -> None:
    value = {
        "region_id": "songpa_public_demo",
        "accepted": True,
        "accepted_by": "fixture reviewer",
        "accepted_date": "2026-05-04",
        "paper_reviewed": True,
        "korean_report_reviewed": korean_report_reviewed,
        "docx_regenerated": True,
        "figure_table_manifest_reviewed": True,
        "evidence_gates_reviewed": True,
        "result_claims_aligned": result_claims_aligned,
        "claim_boundary": claim_boundary,
        "evidence_paths": [
            "paper/paper_draft.md",
            "report_draft.md",
            "report.docx",
            "results/realworld_pilot/tables/figure_table_manifest.json",
        ],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle)


if __name__ == "__main__":
    test_missing_default_manuscript_acceptance_is_blocked()
    test_manuscript_acceptance_fixture_can_pass()
    test_manuscript_acceptance_rejects_string_booleans()
    test_manuscript_acceptance_requires_report_review()
    test_manuscript_acceptance_requires_result_alignment()
    test_manuscript_acceptance_requires_not_operational_boundary()
    print("\n=== REALWORLD MANUSCRIPT ACCEPTANCE TESTS PASSED ===")
