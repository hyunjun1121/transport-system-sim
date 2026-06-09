"""Tests for conservative final-study publication readiness aggregation."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.publication_readiness import (  # noqa: E402
    _summarize_rail_source_decision_manifest,
    _summarize_rail_bounded_treatment_audit,
    _summarize_rail_transit_stress_profile_manifest,
    audit_publication_readiness,
    write_publication_readiness_audit,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT_PATH = ROOT / "scripts" / "audit_publication_readiness.py"


def test_current_publication_readiness_is_blocked() -> None:
    """Current scaffold must not unlock final real-world claims."""

    summary = audit_publication_readiness()

    assert summary["publication_ready"] is False
    assert summary["verdict"] == "final_study_claims_blocked"
    assert summary["gates"]["rail_station_binding_ready"] is True
    assert summary["gates"]["rail_service_evidence_ready"] is False
    assert summary["gates"]["rail_source_decision_ready"] is False
    assert summary["gates"]["rail_transit_stress_profile_ready"] is False
    assert summary["gates"]["rail_bounded_treatment_integrity_ready"] is False
    assert summary["gates"]["road_input_evidence_ready"] is False
    assert summary["gates"]["road_override_evidence_ready"] is False
    assert summary["gates"]["road_override_application_ready"] is False
    assert summary["gates"]["parameter_evidence_ready"] is False
    assert not any("rail station binding" in item for item in summary["remaining_blockers"])
    assert any("rail service evidence" in item for item in summary["remaining_blockers"])
    assert any("rail source decision" in item for item in summary["remaining_blockers"])
    assert any(
        "rail transit stress profile" in item
        for item in summary["remaining_blockers"]
    )

    print("PASS: current publication readiness is blocked")


def test_audit_script_returns_success_without_fail_flag() -> None:
    """The audit script should be usable in default validation without failing."""

    module = _load_audit_script()
    summary = module.audit_publication_readiness()

    assert summary["publication_ready"] is False

    print("PASS: readiness audit script reports blockers without default failure")


def test_publication_readiness_writer_preserves_non_acceptance_scope() -> None:
    """The writer should persist blocked claim-readiness without approval semantics."""

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = write_publication_readiness_audit(
            manifest_path=root / "publication_readiness.json",
            doc_path=root / "publication_readiness.md",
        )

        assert manifest["publication_ready"] is False
        assert manifest["can_mark_complete"] is False
        assert manifest["gate_count"] == 10
        assert manifest["ready_gate_count"] == 1
        assert manifest["blocked_gate_count"] == 9
        assert manifest["status_counts"] == {"blocked": 9, "ready": 1}
        assert "not_formal_acceptance" in manifest["result_scope"]
        assert (root / "publication_readiness.json").exists()
        doc_text = (root / "publication_readiness.md").read_text(encoding="utf-8")
        assert "not a formal acceptance record" in doc_text
        assert "`rail_station_binding_ready` | `true`" in doc_text
        assert "identifier-binding prerequisite only" in doc_text

    print("PASS: publication readiness writer preserves non-acceptance scope")


def test_publication_readiness_writer_preserves_timestamp_when_unchanged() -> None:
    """Repeated writes should not dirty manifests solely via generated_at."""

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest_path = root / "publication_readiness.json"
        doc_path = root / "publication_readiness.md"
        write_publication_readiness_audit(
            manifest_path=manifest_path,
            doc_path=doc_path,
        )
        first = json.loads(manifest_path.read_text(encoding="utf-8"))
        first["generated_at"] = "2000-01-01T00:00:00+00:00"
        manifest_path.write_text(
            json.dumps(first, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        second = write_publication_readiness_audit(
            manifest_path=manifest_path,
            doc_path=doc_path,
        )
        loaded = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert second["generated_at"] == "2000-01-01T00:00:00+00:00"
    assert loaded["generated_at"] == "2000-01-01T00:00:00+00:00"

    print("PASS: publication readiness writer preserves timestamp when unchanged")


def test_rail_source_decision_summary_requires_completed_rows() -> None:
    """Aggregate recorded=true is insufficient without completed row decisions."""

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "rail_source_decision_manifest.json"
        path.write_text(
            json.dumps(
                {
                    "row_count": 5,
                    "completed_source_decision_count": 4,
                    "blocking_decision_count": 0,
                    "human_review_decision_count": 0,
                    "rail_source_decision_recorded": True,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        summary = _summarize_rail_source_decision_manifest(path)

    assert summary["rail_source_decision_ready"] is False
    assert summary["rail_source_decision_recorded"] is True
    assert summary["completed_source_decision_count"] == 4
    assert any("not complete" in item for item in summary["remaining_blockers"])

    print("PASS: rail source-decision summary requires completed rows")


def test_rail_source_decision_summary_rejects_non_publication_manifest() -> None:
    """Complete non-formal source decisions are not publication-ready evidence."""

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "rail_source_decision_manifest.json"
        path.write_text(
            json.dumps(
                {
                    "row_count": 5,
                    "completed_source_decision_count": 5,
                    "blocking_decision_count": 0,
                    "human_review_decision_count": 0,
                    "rail_source_decision_recorded": True,
                    "publication_ready": False,
                    "can_mark_complete": False,
                    "remaining_blockers": [
                        "non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates"
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        summary = _summarize_rail_source_decision_manifest(path)

    assert summary["rail_source_decision_ready"] is False
    assert summary["rail_source_decision_recorded"] is True
    assert summary["completed_source_decision_count"] == 5
    assert any("not publication-ready" in item for item in summary["remaining_blockers"])
    assert any("cannot mark complete" in item for item in summary["remaining_blockers"])

    print("PASS: rail source-decision summary rejects non-publication manifest")


def test_rail_source_decision_summary_rejects_optimistic_non_support_manifest() -> None:
    """Optimistic publication flags cannot bypass explicit rail-support flags."""

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "rail_source_decision_manifest.json"
        path.write_text(
            json.dumps(
                {
                    "row_count": 5,
                    "completed_source_decision_count": 5,
                    "blocking_decision_count": 0,
                    "human_review_decision_count": 0,
                    "rail_source_decision_recorded": True,
                    "publication_ready": True,
                    "can_mark_complete": True,
                    "can_support_publication_gate": False,
                    "can_support_rail_evidence_gate": False,
                    "accepted_source_backed_rail_service_evidence": False,
                    "rail_service_evidence_gate_closure_candidate_count": 0,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        summary = _summarize_rail_source_decision_manifest(path)

    assert summary["rail_source_decision_ready"] is False
    assert summary["source_decision_manifest_publication_ready"] is True
    assert summary["source_decision_manifest_can_mark_complete"] is True
    assert summary["source_decision_manifest_can_support_publication_gate"] is False
    assert summary["source_decision_manifest_can_support_rail_gate"] is False
    assert summary["accepted_source_backed_rail_service_evidence"] is False
    assert summary["rail_service_evidence_gate_closure_candidate_count"] == 0
    assert any("cannot support publication gate" in item for item in summary["remaining_blockers"])
    assert any("cannot support rail evidence gate" in item for item in summary["remaining_blockers"])
    assert any("does not accept source-backed" in item for item in summary["remaining_blockers"])

    print("PASS: rail source-decision summary rejects optimistic non-support manifest")


def test_rail_source_decision_summary_rejects_optimistic_non_formal_scope() -> None:
    """Non-formal action ledgers cannot close rail evidence even with true flags."""

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "rail_source_decision_manifest.json"
        path.write_text(
            json.dumps(
                {
                    "row_count": 5,
                    "completed_source_decision_count": 5,
                    "blocking_decision_count": 0,
                    "human_review_decision_count": 0,
                    "rail_source_decision_recorded": True,
                    "publication_ready": True,
                    "can_mark_complete": True,
                    "can_support_publication_gate": True,
                    "can_support_rail_evidence_gate": True,
                    "accepted_source_backed_rail_service_evidence": True,
                    "rail_service_evidence_gate_closure_candidate_count": 1,
                    "action_ledger_completion_scope": "non_formal_source_review_only",
                    "completed_action_ledger_is_acceptance": False,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        summary = _summarize_rail_source_decision_manifest(path)

    assert summary["rail_source_decision_ready"] is False
    assert summary["non_formal_action_ledger_scope"] is True
    assert summary["completed_action_ledger_is_acceptance"] is False
    assert any("non-formal" in item for item in summary["remaining_blockers"])
    assert any("not formal acceptance" in item for item in summary["remaining_blockers"])

    print("PASS: rail source-decision summary rejects optimistic non-formal scope")


def test_rail_source_decision_summary_rejects_stale_input_manifests() -> None:
    """Optimistic source-decision manifests cannot hide stale input blockers."""

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        fetch_path = root / "rail_fetch_readiness_manifest.json"
        priority_path = root / "rail_evidence_priority_manifest.json"
        source_path = root / "rail_source_decision_manifest.json"
        fetch_path.write_text(
            json.dumps({"blocking_request_count": 1}, indent=2) + "\n",
            encoding="utf-8",
        )
        priority_path.write_text(
            json.dumps(
                {
                    "blocking_priority_count": 1,
                    "human_review_priority_count": 1,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        source_path.write_text(
            json.dumps(
                {
                    "row_count": 5,
                    "completed_source_decision_count": 5,
                    "blocking_decision_count": 0,
                    "human_review_decision_count": 0,
                    "rail_source_decision_recorded": True,
                    "publication_ready": True,
                    "can_mark_complete": True,
                    "can_support_publication_gate": True,
                    "can_support_rail_evidence_gate": True,
                    "accepted_source_backed_rail_service_evidence": True,
                    "rail_service_evidence_gate_closure_candidate_count": 1,
                    "action_ledger_completion_scope": "source_backed_rail_evidence_review",
                    "completed_action_ledger_is_acceptance": True,
                    "inputs": {
                        "rail_fetch_readiness_manifest": str(fetch_path),
                        "rail_evidence_priority_manifest": str(priority_path),
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        summary = _summarize_rail_source_decision_manifest(source_path)

    assert summary["rail_source_decision_ready"] is False
    assert summary["source_decision_input_guard_blocker_count"] == 3
    assert any("fetch-readiness manifest has 1 blocking" in item for item in summary["remaining_blockers"])
    assert any("evidence-priority manifest has 1 blocking" in item for item in summary["remaining_blockers"])
    assert any("evidence-priority manifest has 1 human-review" in item for item in summary["remaining_blockers"])

    print("PASS: rail source-decision summary rejects stale input manifests")


def test_rail_transit_stress_profile_summary_blocks_broken_manifest() -> None:
    """Stress-profile manifest must be clean before publication rail readiness."""

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "rail_transit_stress_manifest.json"
        path.write_text(
            json.dumps(
                {
                    "required_stress_classes_present": True,
                    "missing_runtime_hook_count": 1,
                    "unresolved_linked_artifact_count": 1,
                    "publication_ready": True,
                    "can_mark_complete": True,
                    "can_support_rail_evidence_gate": True,
                    "remaining_blockers": ["synthetic stress blocker"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        summary = _summarize_rail_transit_stress_profile_manifest(path)

    assert summary["rail_transit_stress_profile_ready"] is False
    assert summary["missing_runtime_hook_count"] == 1
    assert summary["unresolved_linked_artifact_count"] == 1
    assert any("missing runtime hooks" in item for item in summary["remaining_blockers"])
    assert any("unresolved" in item for item in summary["remaining_blockers"])
    assert "synthetic stress blocker" in summary["remaining_blockers"]

    print("PASS: rail transit stress-profile summary blocks broken manifest")


def test_rail_bounded_treatment_summary_blocks_pending_or_unsafe_audit() -> None:
    """Bounded-treatment audit must be a fail-closed integrity dependency."""

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "rail_bounded_treatment_audit.json"
        path.write_text(
            json.dumps(
                {
                    "mismatch_count": 1,
                    "warning_count": 1,
                    "unchecked_pending_decision_count": 1,
                    "publication_ready": True,
                    "can_mark_complete": True,
                    "can_support_rail_evidence_gate": True,
                    "can_support_acceptance_gate": True,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        summary = _summarize_rail_bounded_treatment_audit(path)

    assert summary["rail_bounded_treatment_integrity_ready"] is False
    assert summary["mismatch_count"] == 1
    assert summary["warning_count"] == 1
    assert summary["unchecked_pending_decision_count"] == 1
    assert any("mismatches remain" in item for item in summary["remaining_blockers"])
    assert any("warnings remain" in item for item in summary["remaining_blockers"])
    assert any("source decisions remain pending" in item for item in summary["remaining_blockers"])
    assert any("must not claim publication readiness" in item for item in summary["remaining_blockers"])

    print("PASS: rail bounded-treatment summary blocks pending or unsafe audit")


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
    test_publication_readiness_writer_preserves_non_acceptance_scope()
    test_publication_readiness_writer_preserves_timestamp_when_unchanged()
    test_rail_source_decision_summary_requires_completed_rows()
    test_rail_source_decision_summary_rejects_non_publication_manifest()
    test_rail_source_decision_summary_rejects_optimistic_non_support_manifest()
    test_rail_source_decision_summary_rejects_optimistic_non_formal_scope()
    test_rail_source_decision_summary_rejects_stale_input_manifests()
    test_rail_transit_stress_profile_summary_blocks_broken_manifest()
    test_rail_bounded_treatment_summary_blocks_pending_or_unsafe_audit()
    print("\n=== REALWORLD PUBLICATION READINESS TESTS PASSED ===")
