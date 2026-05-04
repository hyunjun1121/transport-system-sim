"""Tests for conservative final-study publication readiness aggregation."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.publication_readiness import audit_publication_readiness  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT_PATH = ROOT / "scripts" / "audit_publication_readiness.py"


def test_current_publication_readiness_is_blocked() -> None:
    """Current scaffold must not unlock final real-world claims."""

    summary = audit_publication_readiness()

    assert summary["publication_ready"] is False
    assert summary["verdict"] == "final_study_claims_blocked"
    assert summary["gates"]["rail_station_binding_ready"] is True
    assert summary["gates"]["rail_service_evidence_ready"] is False
    assert summary["gates"]["road_input_evidence_ready"] is False
    assert summary["gates"]["road_override_evidence_ready"] is False
    assert summary["gates"]["road_override_application_ready"] is False
    assert summary["gates"]["parameter_evidence_ready"] is False
    assert not any("rail station binding" in item for item in summary["remaining_blockers"])
    assert any("rail service evidence" in item for item in summary["remaining_blockers"])

    print("PASS: current publication readiness is blocked")


def test_audit_script_returns_success_without_fail_flag() -> None:
    """The audit script should be usable in default validation without failing."""

    module = _load_audit_script()
    summary = module.audit_publication_readiness()

    assert summary["publication_ready"] is False

    print("PASS: readiness audit script reports blockers without default failure")


def _load_audit_script():
    spec = importlib.util.spec_from_file_location(
        "audit_publication_readiness", AUDIT_SCRIPT_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_publication_readiness"] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    test_current_publication_readiness_is_blocked()
    test_audit_script_returns_success_without_fail_flag()
    print("\n=== REALWORLD PUBLICATION READINESS TESTS PASSED ===")
