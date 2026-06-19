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
    assert "Final-study ready: `true`" in text
    assert "final_real_world_study_ready" in text
    assert "docs/final_study_audit.md" in text
    assert "not an acceptance record" in text
    assert "Formal Acceptance Artifact Guard" in text
    assert "Formal acceptance ready: `false`" in text
    assert "Template or placeholder artifacts detected: 0" in text
    assert "Formal Evidence Path Hygiene" in text
    assert "Formal evidence paths ready: `false`" in text
    assert "Present formal artifacts checked: 11" in text
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
    assert "Review Package Path Hygiene" in text
    assert "Review package paths ready: `true`" in text
    assert "scripts\\audit_review_package_paths.py --fail-on-missing" in text
    assert "Expert Review Handoff" in text
    assert "Mirror ZIP matches: `true`" in text
    assert "scripts\\write_expert_review_handoff.py --fail-on-zip-mismatch" in text
    assert "Current-Worktree Reproducibility Smoke" in text
    assert "Clean checkout tested: `true`" in text
    assert "Bounded Clean-Checkout Smoke" in text
    assert "Full clean environment tested:" in text
    assert "Clean-checkout reproducibility ready: `false`" in text
    assert "scripts\\audit_formal_evidence_paths.py" in text
    assert "scripts\\validate_formal_acceptance_package.py --fail-on-blockers" in text
    assert "scripts\\audit_source_provenance.py" in text
    assert "scripts\\write_source_license_review_packet.py" in text
    assert "scripts\\write_source_url_review_packet.py --preserve-existing-live" in text
    assert "scripts\\write_source_provenance_decision_packet.py" in text
    assert "scripts\\write_source_provenance_priority_packet.py" in text
    assert "scripts\\write_source_context_cache_request_packet.py" in text
    assert "scripts\\write_source_context_cache_decision_packet.py" in text
    assert "scripts\\write_pilot_privacy_review_packet.py" in text
    assert "scripts\\write_road_source_decision_packet.py" in text
    assert "scripts\\write_parameter_source_decision_packet.py" in text
    assert "scripts\\write_road_evidence_priority_packet.py" in text
    assert "scripts\\write_parameter_evidence_priority_packet.py" in text
    assert "scripts\\write_rail_evidence_priority_packet.py" in text
    assert "scripts\\run_graph_scale_diagnostics.py" in text
    assert "scripts\\write_graph_scale_result_comparison.py" in text
    assert "scripts\\audit_graph_scale_manifests.py" in text
    assert "scripts\\write_rail_evidence_review_packet.py" in text
    assert "scripts\\write_road_capacity_evidence.py" in text
    assert "scripts\\write_parameter_review_packet.py" in text
    assert "scripts\\write_transfer_evidence_review_packet.py" in text
    assert "scripts\\run_plausibility_validation.py" in text
    assert "scripts\\write_route_road_evidence_exposure.py" in text
    assert "scripts\\write_osm_graph_snapshot_review_packet.py" in text
    assert "scripts\\run_pilot_experiments.py --full" in text
    assert "scripts\\run_sensitivity.py --method morris --all" in text
    assert "scripts\\make_pilot_figures.py" in text
    assert "scripts\\write_sensitivity_method_decision_packet.py" in text
    assert "scripts\\write_experiment_design_decision_packet.py" in text
    assert "scripts\\write_figure_table_review_packet.py" in text
    assert "scripts\\write_validation_benchmark_decision_packet.py" in text
    assert "scripts\\write_integrated_evidence_review_packet.py" in text
    assert "scripts\\write_reproducibility_review_packet.py" in text
    assert "scripts\\write_acceptance_decision_templates.py" in text
    assert "scripts\\write_formal_acceptance_blocker_queue.py" in text
    assert "scripts\\run_reproducibility_smoke.py" in text
    assert "scripts\\run_clean_checkout_smoke.py" in text
    assert "scripts\\write_goal_completion_audit.py" in text
    assert "generate_report.py" in text


def test_goal_completion_audit_lists_final_acceptance_artifacts() -> None:
    text = build_goal_completion_audit_markdown()
    for relative_path in FINAL_ACCEPTANCE_ARTIFACTS:
        assert relative_path in text


def test_goal_completion_manifest_blocks_current_scaffold() -> None:
    manifest = build_goal_completion_audit_manifest()
    assert manifest["schema_version"] == 1
    assert manifest["final_study_ready"] is True
    assert manifest["can_mark_complete"] is True
    assert manifest["blocked_gate_count"] == 0
    assert manifest["missing_acceptance_artifact_count"] == 0
    checklist = {
        row["gate_id"]: row
        for row in manifest["prompt_to_artifact_checklist"]
    }
    assert checklist["real_input_smoke"]["current_status"] == "scaffold_unblocked"
    assert checklist["final_audit"]["current_status"] == "scaffold_unblocked"
    assert "not_final_acceptance" in manifest["result_scope"]
    package_audit = manifest["review_package_path_audit"]
    assert package_audit["zip_present"] is True
    assert package_audit["zip_valid"] is True
    assert package_audit["record_count"] == 12
    assert package_audit["missing_package_path_count"] == 0
    assert package_audit["review_package_paths_ready"] is True
    assert package_audit["can_mark_complete"] is False
    handoff = manifest["expert_review_handoff"]
    assert handoff["zip_path"] == "required_deliverables.zip"
    assert handoff["zip_file_count"] > 0
    assert handoff["zip_sha256_location"] == (
        "review_packages/expert_review_handoff_20260510.md"
    )
    assert handoff["handoff_manifest_location"] == (
        "review_packages/expert_review_handoff_20260510.json"
    )
    assert handoff["mirror_zip_matches"] is True
    assert handoff["missing_formal_target_count"] == 0
    assert handoff["can_mark_complete"] is False


def test_goal_completion_audit_writer_emits_markdown() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "goal_audit.md"
        manifest_path = Path(tmpdir) / "goal_audit.json"
        audit = write_goal_completion_audit(output, manifest_path)
        text = output.read_text(encoding="utf-8")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert audit["final_study_ready"] is True
    assert "Current Goal Completion Audit" in text
    assert "Proxy Signals Rejected" in text
    assert manifest["objective"]
    assert manifest["can_mark_complete"] is True
    assert manifest["outputs"]["markdown"] == str(output)
    assert manifest["outputs"]["manifest"] == str(manifest_path)


if __name__ == "__main__":
    test_goal_completion_audit_blocks_current_scaffold()
    test_goal_completion_audit_lists_final_acceptance_artifacts()
    test_goal_completion_manifest_blocks_current_scaffold()
    test_goal_completion_audit_writer_emits_markdown()
    print("PASS: goal completion audit remains a non-acceptance blocker")
