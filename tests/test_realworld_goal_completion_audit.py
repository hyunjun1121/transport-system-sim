"""Tests for the non-acceptance active-goal completion audit."""

from __future__ import annotations

from pathlib import Path
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.goal_completion_audit import (
    FINAL_ACCEPTANCE_ARTIFACTS,
    build_goal_completion_audit_manifest,
    build_goal_completion_audit_markdown,
    write_goal_completion_audit,
)


def test_goal_completion_audit_blocks_current_scaffold() -> None:
    text = build_goal_completion_audit_markdown()
    assert "Prompt-To-Artifact Checklist" in text
    assert "Region-Scope Review Metadata" in text
    assert "songpa_public_demo" in text
    assert "Rail Evidence" in text
    assert "Final-study ready: `false`" in text
    assert "final_real_world_study_blocked" in text
    assert "docs/final_study_audit.md" in text
    assert "not an acceptance record" in text
    assert "Formal Acceptance Artifact Guard" in text
    assert "Formal acceptance ready: `false`" in text
    assert "Template or placeholder artifacts detected: 0" in text
    assert "Formal Evidence Path Hygiene" in text
    assert "Formal evidence paths ready: `false`" in text
    assert "Present formal artifacts checked: 0" in text
    assert "Formal Acceptance Package Intake" in text
    assert "Formal package ready: `false`" in text
    assert "Human Acceptance Runbook" in text
    assert "docs/human_acceptance_runbook.md" in text
    assert "Formal Acceptance Blocker Queue" in text
    assert "Queue rows:" in text
    assert "Acceptance Task Assignments" in text
    assert "Assigned agents:" in text
    assert "scripts\\write_acceptance_task_assignments.py" in text
    assert "Formal Acceptance Evidence Matrix" in text
    assert "Human decisions required:" in text
    assert "scripts\\write_formal_acceptance_evidence_matrix.py" in text
    assert "Formal Acceptance Pre-Review" in text
    assert "Draft records:" in text
    assert "Formal approval made: `false`" in text
    assert "scripts\\write_formal_acceptance_pre_review.py" in text
    assert "Current-Worktree Reproducibility Smoke" in text
    assert "Clean checkout tested: `false`" in text
    assert "Bounded Clean-Checkout Smoke" in text
    assert "Full clean environment tested:" in text
    assert "Clean-checkout reproducibility ready: `false`" in text
    assert "scripts\\audit_formal_evidence_paths.py" in text
    assert "scripts\\validate_formal_acceptance_package.py --fail-on-blockers" in text
    assert "scripts\\audit_source_provenance.py" in text
    assert "scripts\\write_source_url_review_packet.py --preserve-existing-live" in text
    assert "scripts\\write_source_provenance_priority_packet.py" in text
    assert "scripts\\write_source_context_cache_request_packet.py" in text
    assert "scripts\\write_source_context_cache_decision_packet.py" in text
    assert "scripts\\write_road_source_decision_packet.py" in text
    assert "scripts\\write_parameter_source_decision_packet.py" in text
    assert "scripts\\write_sensitivity_method_decision_packet.py" in text
    assert "scripts\\write_experiment_design_decision_packet.py" in text
    assert "scripts\\write_figure_table_review_packet.py" in text
    assert "scripts\\write_validation_benchmark_decision_packet.py" in text
    assert "scripts\\run_reproducibility_smoke.py" in text
    assert "scripts\\run_clean_checkout_smoke.py" in text


def test_goal_completion_audit_lists_final_acceptance_artifacts() -> None:
    text = build_goal_completion_audit_markdown()
    for relative_path in FINAL_ACCEPTANCE_ARTIFACTS:
        assert relative_path in text


def test_goal_completion_manifest_blocks_current_scaffold() -> None:
    manifest = build_goal_completion_audit_manifest()
    assert manifest["schema_version"] == 1
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["blocked_gate_count"] == 12
    assert manifest["missing_acceptance_artifact_count"] == len(
        FINAL_ACCEPTANCE_ARTIFACTS
    )
    checklist = {
        row["gate_id"]: row
        for row in manifest["prompt_to_artifact_checklist"]
    }
    assert checklist["real_input_smoke"]["current_status"] == "ready"
    assert checklist["final_audit"]["current_status"] == "blocked"
    assert checklist["final_audit"]["missing_or_weak_requirements"]
    assert "not_final_acceptance" in manifest["result_scope"]


def test_goal_completion_audit_writer_emits_markdown() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "goal_audit.md"
        manifest_path = Path(tmpdir) / "goal_audit.json"
        audit = write_goal_completion_audit(output, manifest_path)
        text = output.read_text(encoding="utf-8")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert audit["final_study_ready"] is False
    assert "Current Goal Completion Audit" in text
    assert "Proxy Signals Rejected" in text
    assert manifest["objective"]
    assert manifest["can_mark_complete"] is False
    assert manifest["outputs"]["markdown"] == str(output)
    assert manifest["outputs"]["manifest"] == str(manifest_path)


if __name__ == "__main__":
    test_goal_completion_audit_blocks_current_scaffold()
    test_goal_completion_audit_lists_final_acceptance_artifacts()
    test_goal_completion_manifest_blocks_current_scaffold()
    test_goal_completion_audit_writer_emits_markdown()
    print("PASS: goal completion audit remains a non-acceptance blocker")
