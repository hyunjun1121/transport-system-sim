"""Tests for the scaffold plan-artifact audit helper."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "audit_plan_artifacts.py"


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_plan_artifacts", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_plan_artifacts"] = module
    spec.loader.exec_module(module)
    return module


def test_audit_plan_artifacts_reports_scaffold_boundary() -> None:
    """The audit should pass artifact checks without upgrading claims."""

    module = _load_audit_module()
    summary = module.audit_artifacts()

    assert summary["all_required_artifacts_present"] is True
    assert "not_final_calibrated_study" in summary["verdict"]
    assert "do not certify calibrated real-world" in summary["claim_boundary"]
    assert summary["remaining_blockers"]
    assert any(
        row["label"] == "pilot_full_results" and row["rows"] == 1890
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_results" and row["rows"] == 32
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_summary" and row["rows"] == 16
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_full_results" and row["rows"] == 1890
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_full_summary" and row["rows"] == 63
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "accessibility_loss" and row["rows"] == 127
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "canonical_route_road_evidence_exposure"
        and row["rows"] == 76
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "validation_review_packet" and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "validation_strategy_readiness_packet" and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "reproducibility_review_packet" and row["rows"] == 8
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "graph_scale_route_comparison" and row["rows"] == 3
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "graph_scale_alternate_routes" and row["rows"] == 9
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "graph_scale_multi_corridor_routes" and row["rows"] == 9
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "graph_scale_review_packet" and row["rows"] == 4
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "graph_scale_strategy_readiness_packet" and row["rows"] == 5
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "graph_scale_result_comparison" and row["rows"] == 819
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_full_metric_ci" and row["rows"] == 819
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_full_paired_delta_ci" and row["rows"] == 702
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_metric_ci" and row["rows"] == 208
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_paired_delta_ci" and row["rows"] == 156
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_full_metric_ci" and row["rows"] == 819
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_full_paired_delta_ci"
        and row["rows"] == 702
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "road_class_overrides_draft" and row["rows"] == 10
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "road_speed_evidence_candidates" and row["rows"] == 10
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "road_capacity_evidence_candidates" and row["rows"] == 10
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "road_evidence_review_packet" and row["rows"] == 10
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "road_source_readiness_packet" and row["rows"] == 5
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "road_evidence_priority_packet" and row["rows"] == 11
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "road_evidence_source_request_packet" and row["rows"] == 5
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_evidence_review_packet" and row["rows"] == 10
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_timing_source_request_packet" and row["rows"] == 5
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_fetch_readiness_packet" and row["rows"] == 5
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_evidence_priority_packet" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_evidence_review_packet" and row["rows"] == 29
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_evidence_source_request_packet"
        and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_source_readiness_packet" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_evidence_priority_packet" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_acceptance_template" and row["rows"] == 25
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "formal_acceptance_blocker_queue" and row["rows"] == 15
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "acceptance_task_assignments" and row["rows"] == 15
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "formal_acceptance_evidence_matrix" and row["rows"] == 12
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "source_provenance_priority_packet" and row["rows"] == 11
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "experiment_strategy_readiness_packet"
        and row["rows"] == 9
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "sensitivity_review_packet" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "sensitivity_index_review_packet" and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "sensitivity_strategy_readiness_packet"
        and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_road_cache_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "figure_table_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "pilot_full_statistics_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_statistics_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_full_statistics_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "road_speed_evidence_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "road_capacity_evidence_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "road_evidence_review_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "road_source_readiness_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "road_evidence_priority_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "road_evidence_source_request_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "rail_evidence_review_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "rail_timing_source_request_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "rail_fetch_readiness_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "rail_evidence_priority_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "graph_scale_review_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "graph_scale_strategy_readiness_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "graph_scale_result_comparison_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "parameter_evidence_review_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "parameter_evidence_source_request_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "parameter_source_readiness_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "parameter_evidence_priority_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "sensitivity_review_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "sensitivity_index_review_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "sensitivity_strategy_readiness_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "validation_review_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "validation_strategy_readiness_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "canonical_route_road_evidence_exposure_manifest"
        and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "osrm_route_benchmark_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "acceptance_orchestration_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "acceptance_review_agents" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "acceptance_record_schema" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "reproducibility_review_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "source_provenance_priority_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "acceptance_decision_template_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "formal_acceptance_package_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "formal_evidence_path_audit" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "formal_acceptance_blocker_queue_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "acceptance_task_assignments_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "formal_acceptance_evidence_matrix_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "formal_acceptance_pre_review_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "experiment_strategy_readiness_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "current_goal_completion_audit" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/realworld_pipeline.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/third_party_adaptations.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/reproducibility_review_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/source_provenance_priority_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/acceptance_decision_templates.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/formal_acceptance_blocker_queue.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/acceptance_task_assignments.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/formal_acceptance_evidence_matrix.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/formal_acceptance_pre_review.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/road_evidence_priority_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/rail_evidence_priority_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/parameter_evidence_priority_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/experiment_strategy_readiness_packet.md"
        and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/human_acceptance_runbook.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/validation_strategy_readiness_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/sensitivity_strategy_readiness_packet.md"
        and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/sensitivity_index_review_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/formal_acceptance_artifact_guard.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/formal_acceptance_package_audit.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/formal_evidence_path_audit.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/agents/acceptance_review_agents.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/review_packets/acceptance_review_index.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert summary["acceptance_record_checks"]
    assert len(summary["acceptance_record_checks"]) == 12
    assert all(row["ok"] for row in summary["acceptance_record_checks"])
    assert all(
        row["can_mark_complete"] is False for row in summary["acceptance_record_checks"]
    )
    assert summary["acceptance_orchestration_audit"]["manifest_present"] is True
    assert summary["acceptance_orchestration_audit"]["record_count"] == 12
    assert summary["acceptance_orchestration_audit"]["status_counts"] == {
        "blocked": 9,
        "needs_human_review": 3,
    }
    assert summary["acceptance_orchestration_audit"]["can_mark_complete_count"] == 0
    assert summary["acceptance_orchestration_audit"]["final_study_ready"] is False
    assert summary["acceptance_decision_template_audit"]["manifest_present"] is True
    assert summary["acceptance_decision_template_audit"]["json_template_count"] == 9
    assert (
        summary["acceptance_decision_template_audit"]["parameter_template_row_count"]
        == 25
    )
    assert summary["acceptance_decision_template_audit"]["can_mark_complete"] is False
    assert (
        summary["acceptance_decision_template_audit"]["formal_acceptance_created"]
        is False
    )
    assert "manifest_present" in summary["reproducibility_smoke_audit"]
    assert (
        summary["reproducibility_smoke_audit"]["clean_checkout_test_performed"]
        is False
    )
    assert summary["reproducibility_smoke_audit"]["can_mark_complete"] is False
    assert summary["formal_acceptance_guard_audit"]["artifact_count"] == 12
    assert summary["formal_acceptance_guard_audit"]["present_count"] == 0
    assert summary["formal_acceptance_guard_audit"]["missing_count"] == 12
    assert (
        summary["formal_acceptance_guard_audit"]["template_or_placeholder_count"]
        == 0
    )
    assert summary["formal_acceptance_guard_audit"]["can_mark_complete"] is False
    assert summary["formal_acceptance_package_audit"]["gate_count"] == 12
    assert summary["formal_acceptance_package_audit"]["ready_gate_count"] == 0
    assert summary["formal_acceptance_package_audit"]["blocked_gate_count"] == 12
    assert summary["formal_acceptance_package_audit"]["can_mark_complete"] is False
    assert summary["formal_evidence_path_audit"]["artifact_count"] == 11
    assert summary["formal_evidence_path_audit"]["present_artifact_count"] == 0
    assert summary["formal_evidence_path_audit"]["can_mark_complete"] is False
    assert summary["formal_acceptance_blocker_queue_audit"]["manifest_present"] is True
    assert summary["formal_acceptance_blocker_queue_audit"]["row_count"] == 15
    assert (
        summary["formal_acceptance_blocker_queue_audit"]["can_mark_complete"] is False
    )
    assert summary["acceptance_task_assignment_audit"]["manifest_present"] is True
    assert summary["acceptance_task_assignment_audit"]["task_count"] == 15
    assert summary["acceptance_task_assignment_audit"]["assigned_agent_count"] == 10
    assert summary["acceptance_task_assignment_audit"]["can_mark_complete"] is False
    assert (
        summary["formal_acceptance_evidence_matrix_audit"]["manifest_present"]
        is True
    )
    assert summary["formal_acceptance_evidence_matrix_audit"]["row_count"] == 12
    assert (
        summary["formal_acceptance_evidence_matrix_audit"][
            "human_decision_required_count"
        ]
        == 12
    )
    assert (
        summary["formal_acceptance_evidence_matrix_audit"]["can_mark_complete"]
        is False
    )
    assert summary["formal_acceptance_pre_review_audit"]["manifest_present"] is True
    assert summary["formal_acceptance_pre_review_audit"]["record_count"] == 12
    assert summary["formal_acceptance_pre_review_audit"][
        "human_decision_required_count"
    ] == 12
    assert (
        summary["formal_acceptance_pre_review_audit"]["formal_approval"] is False
    )
    assert (
        summary["formal_acceptance_pre_review_audit"]["can_mark_complete"] is False
    )
    assert summary["agent_review_path_audit"]["record_count"] == 12
    assert summary["agent_review_path_audit"]["invalid_record_count"] == 0
    assert summary["agent_review_path_audit"]["missing_required_path_count"] == 0
    assert summary["agent_review_path_audit"]["missing_formal_target_count"] >= 1
    assert summary["agent_review_path_audit"]["agent_review_paths_ready"] is True
    assert summary["agent_review_path_audit"]["can_mark_complete"] is False
    assert summary["tracked_artifact_audit"]["manifest_present"] is True
    assert summary["tracked_artifact_audit"]["row_count"] >= 0
    assert (
        0
        <= summary["tracked_artifact_audit"]["blocking_change_count"]
        <= summary["tracked_artifact_audit"]["row_count"]
    )
    assert (
        summary["tracked_artifact_audit"]["clean_checkout_reproducibility_ready"]
        is False
    )
    assert summary["tracked_artifact_audit"]["can_mark_complete"] is False
    assert summary["graph_scale_checks"]
    assert all(row["ok"] for row in summary["graph_scale_checks"])
    assert any(
        row["label"] == "morris_manifest"
        and row["source_nodes"] == 4608
        and row["analysis_nodes"] == 118
        for row in summary["graph_scale_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_manifest"
        and row["source_nodes"] == 4608
        and row["analysis_nodes"] == 164
        for row in summary["graph_scale_checks"]
    )
    assert any(
        row["label"] == "pilot_multi_corridor_full_manifest"
        and row["source_nodes"] == 4608
        and row["analysis_nodes"] == 164
        for row in summary["graph_scale_checks"]
    )
    assert any(
        row["label"] == "figure_table_manifest:sensitivity"
        and row["analysis_reduced"] is True
        for row in summary["graph_scale_checks"]
    )
    assert summary["parameter_evidence_audit"]["publication_ready"] is False
    assert summary["parameter_evidence_audit"]["weak_core_parameter_count"] == 25
    assert summary["parameter_evidence_audit"]["missing_core_parameter_count"] == 0
    assert summary["road_evidence_audit"]["publication_ready"] is False
    assert summary["road_evidence_audit"]["edge_count"] == 28947
    assert summary["road_evidence_audit"]["cache_manifest_metadata_ready"] is True
    assert summary["road_evidence_audit"]["capacity_explicit_rate"] == 0.0
    assert summary["pilot_road_cache_manifest_audit"]["manifest_present"] is True
    assert summary["pilot_road_cache_manifest_audit"]["metadata_ready"] is True
    assert summary["pilot_road_cache_manifest_audit"]["boundary_ready"] is True
    assert summary["pilot_road_cache_manifest_audit"]["tooling_ready"] is True
    assert (
        summary["pilot_road_cache_manifest_audit"]["edge_count"]
        == summary["road_evidence_audit"]["edge_count"]
    )
    assert any(
        "does not replace road-source review" in blocker
        for blocker in summary["pilot_road_cache_manifest_audit"][
            "remaining_blockers"
        ]
    )
    assert summary["road_evidence_diagnostics_audit"]["diagnostics_ready"] is True
    assert summary["road_evidence_diagnostics_audit"]["edge_count"] == 28947
    assert summary["road_evidence_diagnostics_audit"]["highway_class_count"] >= 5
    assert "residential" in summary["road_evidence_diagnostics_audit"][
        "top_review_candidates"
    ]
    assert summary["road_override_evidence_audit"]["publication_ready"] is False
    assert summary["road_override_evidence_audit"]["override_table_present"] is False
    assert summary["road_override_evidence_audit"]["draft_table_present"] is True
    assert summary["road_override_evidence_audit"]["draft_row_count"] == 10
    assert summary["road_override_evidence_audit"]["draft_source_class_counts"] == {
        "expert assumption": 10
    }
    assert summary["road_override_application_audit"]["publication_ready"] is False
    assert summary["road_override_application_audit"]["manifest_present"] is True
    assert summary["road_override_application_audit"]["overrides_applied"] is False
    assert summary["rail_evidence_audit"]["publication_ready"] is False
    assert summary["rail_evidence_audit"]["station_binding_ready"] is True
    assert summary["rail_evidence_audit"]["station_binding_remaining_blockers"] == []
    assert summary["publication_readiness_audit"]["publication_ready"] is False
    assert (
        summary["publication_readiness_audit"]["verdict"]
        == "final_study_claims_blocked"
    )
    assert summary["final_study_readiness_audit"]["final_study_ready"] is False
    assert (
        summary["final_study_readiness_audit"]["verdict"]
        == "final_real_world_study_blocked"
    )
    assert summary["final_study_readiness_audit"]["gate_count"] == 15
    assert "graph_scale_strategy" in summary["final_study_readiness_audit"][
        "blocked_gate_ids"
    ]

    print("PASS: plan artifact audit preserves scaffold claim boundary")


if __name__ == "__main__":
    test_audit_plan_artifacts_reports_scaffold_boundary()
    print("\n=== REALWORLD PLAN AUDIT TESTS PASSED ===")
