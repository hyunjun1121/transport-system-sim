"""Tests for independent final-audit acceptance record validation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.final_audit_acceptance import (  # noqa: E402
    load_final_audit_acceptance,
    summarize_final_audit_acceptance,
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


def test_missing_default_final_audit_acceptance_is_blocked() -> None:
    """The current repository should not imply independent final-audit acceptance."""

    summary = summarize_final_audit_acceptance()

    assert summary["acceptance_ready"] is False
    assert summary["record_present"] is False
    assert summary["remaining_blockers"]

    print("PASS: missing default final-audit acceptance is blocked")


def test_final_audit_acceptance_fixture_can_pass() -> None:
    """A complete final-audit acceptance record can satisfy the narrow gate."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "final_audit_acceptance.json"
        _write_acceptance(path)

        record = load_final_audit_acceptance(path)
        summary = summarize_final_audit_acceptance(path)

        assert record.ready is True
        assert summary["acceptance_ready"] is True
        assert summary["remaining_blockers"] == []

    print("PASS: complete final-audit acceptance fixture can pass")


def test_final_audit_acceptance_rejects_string_booleans() -> None:
    """Acceptance booleans must not be coerced from strings."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "final_audit_acceptance.json"
        _write_acceptance(path)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["final_study_ready"] = "true"
        path.write_text(json.dumps(value), encoding="utf-8")

        assert_raises_value_error(
            lambda: load_final_audit_acceptance(path),
            "must be boolean",
        )

    print("PASS: final-audit acceptance rejects string booleans")


def test_final_audit_acceptance_requires_no_blocked_gates() -> None:
    """A final audit with blocked gates must stay blocked."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "final_audit_acceptance.json"
        _write_acceptance(path, blocked_gate_ids=["rail_evidence"])

        summary = summarize_final_audit_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("blocked_gate_ids" in item for item in summary["remaining_blockers"])

    print("PASS: final-audit acceptance requires no blocked gates")


def test_final_audit_acceptance_requires_prompt_checklist() -> None:
    """Prompt-to-artifact checklist review is mandatory."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "final_audit_acceptance.json"
        _write_acceptance(path, prompt_to_artifact_checklist_reviewed=False)

        summary = summarize_final_audit_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("prompt_to_artifact" in item for item in summary["remaining_blockers"])

    print("PASS: final-audit acceptance requires prompt checklist")


def test_final_audit_acceptance_requires_not_operational_boundary() -> None:
    """Final audit acceptance must still block operational claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "final_audit_acceptance.json"
        _write_acceptance(path, claim_boundary="accepted as operational package")

        summary = summarize_final_audit_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("not operational" in item for item in summary["remaining_blockers"])

    print("PASS: final-audit acceptance requires not-operational boundary")


def _write_acceptance(
    path: Path,
    *,
    blocked_gate_ids: list[str] | None = None,
    prompt_to_artifact_checklist_reviewed: bool = True,
    claim_boundary: str = "Accepted for quasi-real decision-support study; not operational routing.",
) -> None:
    blocked = [] if blocked_gate_ids is None else blocked_gate_ids
    ready_ids = ["pilot_region_accepted", "cached_osm_input"]
    value = {
        "region_id": "songpa_public_demo",
        "accepted": True,
        "accepted_by": "fixture reviewer",
        "accepted_date": "2026-05-04",
        "final_study_ready": True,
        "prompt_to_artifact_checklist_reviewed": prompt_to_artifact_checklist_reviewed,
        "all_gate_evidence_reviewed": True,
        "no_proxy_completion_reviewed": True,
        "expected_gate_count": 2,
        "reviewed_gate_ids": ready_ids,
        "ready_gate_ids": ready_ids,
        "blocked_gate_ids": blocked,
        "claim_boundary": claim_boundary,
        "evidence_paths": [
            "docs/final_study_audit.md",
            "data/manifests/final_audit_acceptance.json",
        ],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle)


if __name__ == "__main__":
    test_missing_default_final_audit_acceptance_is_blocked()
    test_final_audit_acceptance_fixture_can_pass()
    test_final_audit_acceptance_rejects_string_booleans()
    test_final_audit_acceptance_requires_no_blocked_gates()
    test_final_audit_acceptance_requires_prompt_checklist()
    test_final_audit_acceptance_requires_not_operational_boundary()
    print("\n=== REALWORLD FINAL-AUDIT ACCEPTANCE TESTS PASSED ===")
