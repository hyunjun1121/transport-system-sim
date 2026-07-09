"""Tests for the scaffold plan-artifact audit helper."""

from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
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

    assert summary["all_required_artifacts_present"] in (True, False)
    assert "not_final_calibrated_study" in summary["verdict"]
    assert "do not certify calibrated real-world" in summary["claim_boundary"]
    assert summary["remaining_blockers"]
    assert any(
        row["label"] == "pilot_full_results" and row["rows"] >= 2430
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
        row["label"] == "validation_benchmark_readiness_packet" and row["rows"] == 4
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "validation_benchmark_decision_packet" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "integrated_evidence_review_packet" and row["rows"] == 5
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "reproducibility_review_packet" and row["rows"] == 8
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "reproducibility_decision_packet" and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "final_audit_decision_packet" and row["rows"] == 7
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
        row["label"] == "graph_scale_method_decision_packet" and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_region_decision_packet" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "source_provenance_decision_packet" and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "graph_scale_result_comparison" and row["rows"] == 6877
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_full_metric_ci" and row["rows"] >= 1053
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "pilot_full_paired_delta_ci" and row["rows"] >= 936
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
        row["label"] == "road_speed_evidence_candidates" and row["rows"] == 8
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "road_capacity_evidence_candidates" and row["rows"] == 8
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
        row["label"] == "road_source_decision_packet" and row["rows"] == 5
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
        row["label"] == "rail_evidence_review_packet" and row["rows"] == 12
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_timing_source_request_packet" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_fetch_readiness_packet" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_evidence_priority_packet" and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_source_decision_packet" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_source_decision_action_ledger_template"
        and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_source_decision_recommendation_packet"
        and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "rail_transit_stress_profile_packet" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "demand_profiles" and row["rows"] == 2
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "fleet_profiles" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "behavior_profiles" and row["rows"] == 6
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "disruption_scenarios" and row["rows"] == 22
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_evidence_review_packet" and row["rows"] == 29
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_evidence_source_request_packet"
        and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_source_readiness_packet" and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_evidence_priority_packet" and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_acceptance_template" and row["rows"] == 0
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "formal_acceptance_blocker_queue" and row["rows"] == 2
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "acceptance_task_assignments" and row["rows"] == 2
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
        row["label"] == "source_context_cache_request_packet" and row["rows"] == 3
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "source_context_cache_decision_packet" and row["rows"] == 3
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "parameter_source_decision_packet" and row["rows"] == 7
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "experiment_strategy_readiness_packet"
        and row["rows"] == 9
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "experiment_design_decision_packet"
        and row["rows"] == 8
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "figure_table_review_packet"
        and row["rows"] == 8
        for row in summary["csv_checks"]
    )
    assert any(
        row["label"] == "manuscript_report_decision_packet"
        and row["rows"] == 7
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
        row["label"] == "sensitivity_method_decision_packet"
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
        row["label"] == "road_source_decision_manifest" and row["ok"]
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
        row["label"] == "rail_source_decision_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "rail_source_decision_action_ledger_template_manifest"
        and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "rail_source_decision_recommendation_manifest"
        and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "rail_transit_stress_profile_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "demand_fleet_behavior_profile_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "disruption_scenarios_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "rail_bounded_treatment_audit" and row["ok"]
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
        row["label"] == "graph_scale_method_decision_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "pilot_region_decision_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "source_provenance_decision_manifest" and row["ok"]
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
        row["label"] == "sensitivity_method_decision_manifest" and row["ok"]
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
        row["label"] == "validation_benchmark_readiness_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "validation_benchmark_decision_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "integrated_evidence_review_manifest" and row["ok"]
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
        row["label"] == "reproducibility_decision_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "final_audit_decision_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "source_provenance_priority_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "source_context_cache_request_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "source_context_cache_decision_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "parameter_source_decision_manifest" and row["ok"]
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
        row["label"] == "review_package_path_audit" and row["ok"]
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
        row["label"] == "experiment_design_decision_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "figure_table_review_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "manuscript_report_decision_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "current_goal_completion_audit_manifest" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "phase_gate_ledger_schema" and row["ok"]
        for row in summary["json_checks"]
    )
    assert any(
        row["label"] == "phase_gate_ledger_audit_manifest" and row["ok"]
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
        row["path"] == "docs/reproducibility_decision_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/final_audit_decision_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/source_provenance_priority_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/source_context_cache_request_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/source_context_cache_decision_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/parameter_source_decision_packet.md" and row["ok"]
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
        row["path"] == "docs/road_source_decision_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/rail_evidence_priority_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/rail_source_decision_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/rail_source_decision_action_ledger_template.md"
        and row["ok"]
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
        row["path"] == "docs/experiment_design_decision_packet.md"
        and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/figure_table_review_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/manuscript_report_decision_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/demand_fleet_behavior_profiles.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/phase_gate_ledger_audit.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/human_acceptance_runbook.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    runbook_text = (ROOT / "docs" / "human_acceptance_runbook.md").read_text(
        encoding="utf-8"
    )
    for expected in (
        "docs/source_context_cache_decision_packet.md",
        "docs/pilot_region_decision_packet.md",
        "scripts\\write_source_license_review_packet.py",
        "scripts\\write_source_provenance_decision_packet.py",
        "scripts\\write_pilot_privacy_review_packet.py",
        "scripts\\write_rail_evidence_review_packet.py",
        "scripts\\write_road_evidence_review_packet.py",
        "scripts\\write_parameter_review_packet.py",
        "scripts\\write_transfer_evidence_review_packet.py",
        "scripts\\write_graph_scale_review_packet.py",
        "scripts\\write_osm_graph_snapshot_review_packet.py",
        "scripts\\write_validation_review_packet.py",
        "scripts\\write_integrated_evidence_review_packet.py",
        "scripts\\cache_ktdb_gtfs_source.py",
        "scripts\\cache_metro9_capacity_source.py",
        "docs/integrated_evidence_review_packet.md",
        "docs/rail_evidence_priority_packet.md",
        "docs/road_source_decision_packet.md",
        "docs/road_evidence_priority_packet.md",
        "docs/parameter_evidence_priority_packet.md",
        "docs/parameter_source_decision_packet.md",
        "docs/validation_benchmark_decision_packet.md",
        "docs/sensitivity_method_decision_packet.md",
        "docs/experiment_design_decision_packet.md",
        "docs/figure_table_review_packet.md",
        "docs/reproducibility_review_packet.md",
        "docs/reproducibility_decision_packet.md",
        "docs/final_audit_decision_packet.md",
        "scripts\\write_acceptance_blocker_queue.py",
        "scripts\\write_acceptance_task_assignments.py",
        "scripts\\write_formal_acceptance_evidence_matrix.py",
        "scripts\\audit_agent_review_paths.py",
        "scripts\\write_phase_gate_ledgers.py",
    ):
        assert expected in runbook_text
    assert "not approve paper or report claims" in runbook_text
    assert "do not fetch external" in runbook_text
    assert "road data or create overrides" in runbook_text
    for doc_path in ("README.md", "status.md", "agents.md"):
        doc_text = (ROOT / doc_path).read_text(encoding="utf-8")
        assert "write_formal_acceptance_blocker_queue.py" in doc_text
        assert "write_acceptance_blocker_queue.py" in doc_text
    docs_by_path = {
        doc_path: (ROOT / doc_path).read_text(encoding="utf-8")
        for doc_path in (
            "README.md",
            "agents.md",
            "docs/reproducibility_package.md",
            "docs/realworld_pipeline.md",
            "paper/paper_draft.md",
        )
    }
    assert "produce a 7-row\n  source-request worksheet" in docs_by_path["README.md"]
    assert (
        "parameter_evidence_source_request_packet.csv # 7-row parameter source-request aid"
        in docs_by_path["agents.md"]
    )
    assert (
        "reproducibility_review_packet.csv # 8-row clean-checkout review aid"
        in docs_by_path["agents.md"]
    )
    assert (
        "7 rows for demand, fleet, dispatch, transfer, rail, disruption, and traffic/BPR"
        in docs_by_path["docs/reproducibility_package.md"]
    )
    assert (
        "7 request rows covering\n  25 demand, fleet, dispatch, transfer, rail, disruption, and traffic/BPR"
        in docs_by_path["paper/paper_draft.md"]
    )
    assert (
        "7 request rows for demand, fleet, dispatch, transfer, rail, disruption, and traffic/BPR"
        in docs_by_path["docs/realworld_pipeline.md"]
    )
    for doc_path, doc_text in docs_by_path.items():
        assert "produce a 6-row" not in doc_text, doc_path
        assert "# 6-row parameter source-request aid" not in doc_text, doc_path
        assert "6 rows for demand, fleet, dispatch, transfer, disruption" not in doc_text, doc_path
        assert "6 request rows covering 22 demand" not in doc_text, doc_path
        assert "6 request rows for demand, fleet, dispatch, transfer, disruption" not in doc_text, doc_path
    script_names = sorted(path.name for path in (ROOT / "scripts").glob("*.py"))
    for doc_path in ("agents.md", "status.md"):
        doc_text = (ROOT / doc_path).read_text(encoding="utf-8")
        missing_scripts = [name for name in script_names if name not in doc_text]
        assert not missing_scripts, f"{doc_path} is missing {missing_scripts}"
    plan_completion_text = (ROOT / "docs" / "plan_completion_audit.md").read_text(
        encoding="utf-8"
    )
    assert "static plan-gate snapshot" in plan_completion_text
    assert "docs/current_goal_completion_audit.md" in plan_completion_text
    plan_text = (ROOT / "plan.md").read_text(encoding="utf-8")
    for expected in (
        "Mission",
        "Claim Boundary",
        "Stop Conditions",
        "decision-support",
        "Sub-Agent",
    ):
        assert expected in plan_text, f"plan.md missing section: {expected}"
    assert any(
        row["path"] == "docs/validation_strategy_readiness_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/validation_benchmark_readiness_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/validation_benchmark_decision_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/integrated_evidence_review_packet.md" and row["ok"]
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
        row["path"] == "docs/sensitivity_method_decision_packet.md"
        and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/graph_scale_method_decision_packet.md"
        and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/pilot_region_decision_packet.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "docs/source_provenance_decision_packet.md" and row["ok"]
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
        row["path"] == "docs/review_package_path_audit.md" and row["ok"]
        for row in summary["doc_checks"]
    )
    assert any(
        row["path"] == "review_packages/expert_review_handoff_20260510.md"
        and row["ok"]
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
    # 6 of 12 acceptance records now report can_mark_complete=True at the
    # per-record level, but the overall study/final-acceptance gates remain
    # blocked (final_study_ready=False throughout). Assert the honest per-record
    # split rather than the old all-False invariant.
    can_complete = [
        row for row in summary["acceptance_record_checks"]
        if row["can_mark_complete"] is True
    ]
    assert len(can_complete) == 6
    assert len(can_complete) < len(summary["acceptance_record_checks"])
    assert summary["acceptance_orchestration_audit"]["manifest_present"] is True
    assert summary["acceptance_orchestration_audit"]["record_count"] == 12
    assert summary["acceptance_orchestration_audit"]["status_counts"] == {
        "accepted": 6,
        "blocked": 5,
        "needs_human_review": 1,
    }
    assert summary["acceptance_orchestration_audit"]["can_mark_complete_count"] == 6
    assert summary["acceptance_orchestration_audit"]["final_study_ready"] is False
    assert summary["acceptance_decision_template_audit"]["manifest_present"] is True
    assert summary["acceptance_decision_template_audit"]["json_template_count"] == 9
    assert (
        summary["acceptance_decision_template_audit"]["parameter_template_row_count"]
        == 0
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
    guard_audit = summary["formal_acceptance_guard_audit"]
    assert guard_audit["artifact_count"] == 12
    assert guard_audit["present_count"] + guard_audit["missing_count"] == 12
    assert guard_audit["template_or_placeholder_count"] <= guard_audit["present_count"]
    if guard_audit["present_count"]:
        assert (
            guard_audit["template_or_placeholder_count"]
            <= guard_audit["present_count"]
        )
    assert guard_audit["can_mark_complete"] is False
    assert summary["formal_acceptance_package_audit"]["gate_count"] == 12
    assert summary["formal_acceptance_package_audit"]["ready_gate_count"] == 11
    assert summary["formal_acceptance_package_audit"]["blocked_gate_count"] == 1
    assert summary["formal_acceptance_package_audit"]["can_mark_complete"] is False
    evidence_path_audit = summary["formal_evidence_path_audit"]
    assert evidence_path_audit["artifact_count"] == 11
    assert 0 <= evidence_path_audit["present_artifact_count"] <= 11
    assert evidence_path_audit["can_mark_complete"] is False
    assert summary["formal_acceptance_blocker_queue_audit"]["manifest_present"] is True
    assert summary["formal_acceptance_blocker_queue_audit"]["row_count"] == 2
    assert (
        summary["formal_acceptance_blocker_queue_audit"]["can_mark_complete"] is False
    )
    assert summary["acceptance_task_assignment_audit"]["manifest_present"] is True
    assert summary["acceptance_task_assignment_audit"]["task_count"] == 2
    assert summary["acceptance_task_assignment_audit"]["assigned_agent_count"] == 2
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
        == 1
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
    assert (
        0
        <= summary["agent_review_path_audit"]["missing_formal_target_count"]
        <= summary["agent_review_path_audit"]["path_reference_count"]
    )
    assert (
        0
        <= summary["agent_review_path_audit"]["unique_missing_formal_target_count"]
        <= 12
    )
    assert summary["agent_review_path_audit"]["agent_review_paths_ready"] is True
    assert summary["agent_review_path_audit"]["can_mark_complete"] is False
    assert summary["review_package_path_audit"]["zip_present"] is True
    assert summary["review_package_path_audit"]["zip_valid"] is True
    assert summary["review_package_path_audit"]["record_count"] == 12
    assert summary["review_package_path_audit"]["missing_package_path_count"] == 0
    assert (
        0
        <= summary["review_package_path_audit"]["missing_formal_target_count"]
        <= summary["review_package_path_audit"]["path_reference_count"]
    )
    assert (
        0
        <= summary["review_package_path_audit"][
            "unique_missing_formal_target_count"
        ]
        <= 12
    )
    assert summary["review_package_path_audit"]["review_package_paths_ready"] is True
    assert summary["review_package_path_audit"]["can_mark_complete"] is False
    assert summary["expert_review_handoff"]["zip_path"] == "required_deliverables.zip"
    assert summary["expert_review_handoff"]["zip_file_count"] > 0
    assert summary["expert_review_handoff"]["zip_sha256"]
    assert summary["expert_review_handoff"]["mirror_zip_matches"] is True
    assert summary["expert_review_handoff"]["missing_formal_target_count"] == 0
    assert summary["expert_review_handoff"]["can_mark_complete"] is False
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
    assert summary["dirty_worktree_classification"]["manifest_present"] is True
    assert (
        summary["dirty_worktree_classification"]["classified_path_count"]
        == summary["dirty_worktree_classification"]["dirty_path_count"]
    )
    assert (
        summary["dirty_worktree_classification"]["current_dirty_path_count"]
        >= summary["dirty_worktree_classification"]["dirty_path_count"]
    )
    assert summary["dirty_worktree_classification"]["unclassified_path_count"] == 0
    assert (
        summary["dirty_worktree_classification"]["new_generated_output_allowed"]
        is False
    )
    assert summary["dirty_worktree_classification"]["can_mark_complete"] is False
    assert summary["phase_gate_ledger_audit"]["manifest_present"] is True
    assert summary["phase_gate_ledger_audit"]["expected_phase_count"] == 13
    assert summary["phase_gate_ledger_audit"]["valid_ledger_count"] == 13
    assert summary["phase_gate_ledger_audit"]["missing_phase_count"] == 0
    assert summary["phase_gate_ledger_audit"]["invalid_ledger_count"] == 0
    assert summary["phase_gate_ledger_audit"]["closed_phase_count"] == 0
    assert summary["phase_gate_ledger_audit"]["current_support_present"] is True
    assert summary["phase_gate_ledger_audit"]["phase_gate_ledgers_ready"] is False
    assert summary["phase_gate_ledger_audit"]["can_mark_complete"] is False
    assert summary["gpu_ml_runtime_audit"]["manifest_present"] is True
    assert summary["gpu_ml_runtime_audit"]["log_present"] is True
    assert summary["gpu_ml_runtime_audit"]["doc_present"] is True
    assert (
        summary["gpu_ml_runtime_audit"]["simulation_engine_gpu_accelerated"]
        is False
    )
    assert (
        summary["gpu_ml_runtime_audit"]["simulation_correctness_blocked"]
        is False
    )
    assert summary["gpu_ml_runtime_audit"]["publication_ready"] is False
    assert summary["gpu_ml_runtime_audit"]["final_study_ready"] is False
    assert (
        summary["gpu_ml_runtime_audit"]["formal_acceptance_evidence"]
        is False
    )
    assert (
        summary["gpu_ml_runtime_audit"]["requirements_path"]
        in {"requirements.txt", "requirements-ml.txt"}
    )
    assert summary["gpu_ml_runtime_audit"]["requirements_status"] == "present"
    assert summary["gpu_ml_runtime_audit"]["package_results"]
    assert "check_gpu_ml_runtime.py" in " ".join(
        summary["gpu_ml_runtime_audit"]["command"]
    )
    assert summary["claim_language_guard"]["manifest_present"] is True
    assert summary["claim_language_guard"]["claims_approved"] is False
    assert (
        summary["claim_language_guard"]["formal_acceptance_created"] is False
    )
    assert summary["claim_language_guard"]["publication_ready"] is False
    assert summary["claim_language_guard"]["final_study_ready"] is False
    assert summary["claim_language_guard"]["can_mark_complete"] is False
    assert summary["claim_language_guard"]["reserved_match_count"] >= 0
    assert summary["claim_language_guard"]["blocking_finding_count"] >= 0
    assert (
        summary["artifact_invalidation_action_batch_inspection"][
            "manifest_present"
        ]
        is True
    )
    assert (
        summary["artifact_invalidation_action_batch_inspection"]["row_count"]
        == 51
    )
    assert (
        summary["artifact_invalidation_action_batch_inspection"][
            "action_batch_counts"
        ]["quarantine_non_evidence"]
        == 6
    )
    assert (
        summary["artifact_invalidation_action_batch_inspection"][
            "regeneration_candidate_count"
        ]
        == 45
    )
    assert (
        summary["artifact_invalidation_action_batch_inspection"][
            "exclusion_or_non_evidence_candidate_count"
        ]
        == 6
    )
    artifact_invalidation_action_batch_inspection = summary[
        "artifact_invalidation_action_batch_inspection"
    ]
    assert (
        artifact_invalidation_action_batch_inspection[
            "evidence_backed_closeout_row_count"
        ]
        >= 0
    )
    assert (
        artifact_invalidation_action_batch_inspection[
            "evidence_backed_closeout_row_count"
        ]
        + artifact_invalidation_action_batch_inspection[
            "pending_or_blocked_row_count"
        ]
        == artifact_invalidation_action_batch_inspection["row_count"]
    )
    assert (
        summary["artifact_invalidation_action_batch_inspection"][
            "action_queue_blocks_phase9_row_count"
        ]
        == summary["artifact_invalidation_action_batch_inspection"]["row_count"]
    )
    assert (
        summary["artifact_invalidation_action_batch_inspection"][
            "phase9_promotion_ready"
        ]
        is False
    )
    assert (
        summary["artifact_invalidation_action_batch_inspection"][
            "publication_ready"
        ]
        is False
    )
    assert (
        summary["artifact_invalidation_action_batch_inspection"][
            "final_study_ready"
        ]
        is False
    )
    assert (
        summary["artifact_invalidation_action_batch_inspection"][
            "formal_acceptance_evidence"
        ]
        is False
    )
    assert (
        summary["artifact_invalidation_action_batch_inspection"][
            "must_not_be_used_as_closeout_manifest"
        ]
        is True
    )
    # The Phase-1 input retune (road/rail) left the artifact-invalidation matrix
    # with unresolved stale downstream rows, so Phase 9 promotion is blocked.
    assert summary["artifact_invalidation_preflight_audit"]["blocks_phase9"] is True
    assert (
        summary["artifact_invalidation_preflight_audit"][
            "matrix_manifest_present"
        ]
        is True
    )
    assert (
        summary["artifact_invalidation_preflight_audit"]["matrix_row_count"]
        == 51
    )
    assert (
        summary["artifact_invalidation_preflight_audit"][
            "closeout_manifest_present"
        ]
        is True
    )
    assert (
        summary["artifact_invalidation_preflight_audit"][
            "closeout_pending_or_invalid_row_count"
        ]
        >= 0
    )
    assert (
        summary["artifact_invalidation_preflight_audit"]["phase9_promotion_ready"]
        is False
    )
    assert (
        summary["artifact_invalidation_preflight_audit"]["publication_ready"]
        is False
    )
    assert (
        summary["artifact_invalidation_preflight_audit"]["final_study_ready"]
        is False
    )
    assert (
        summary["artifact_invalidation_preflight_audit"][
            "formal_acceptance_evidence"
        ]
        is False
    )
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
    assert summary["parameter_evidence_audit"]["publication_ready"] is True
    assert summary["parameter_evidence_audit"]["weak_core_parameter_count"] == 0
    assert summary["parameter_evidence_audit"]["missing_core_parameter_count"] == 0
    assert summary["road_evidence_audit"]["publication_ready"] is True
    assert summary["road_evidence_audit"]["edge_count"] == 28947
    assert summary["road_evidence_audit"]["cache_manifest_metadata_ready"] is False
    assert summary["road_evidence_audit"]["capacity_explicit_rate"] == 1.0
    assert summary["pilot_road_cache_manifest_audit"]["manifest_present"] is True
    assert summary["pilot_road_cache_manifest_audit"]["metadata_ready"] is False
    assert summary["pilot_road_cache_manifest_audit"]["boundary_ready"] is False
    assert summary["pilot_road_cache_manifest_audit"]["tooling_ready"] is False
    assert summary["pilot_road_cache_manifest_audit"]["edge_count"] is None
    assert any(
        "cache manifest metadata does not replace road-source review" in blocker
        for blocker in summary["pilot_road_cache_manifest_audit"][
            "remaining_blockers"
        ]
    )
    assert summary["road_evidence_diagnostics_audit"]["diagnostics_ready"] is True
    assert summary["road_evidence_diagnostics_audit"]["edge_count"] == 28947
    assert summary["road_evidence_diagnostics_audit"]["highway_class_count"] >= 5
    assert isinstance(
        summary["road_evidence_diagnostics_audit"]["top_review_candidates"], list
    )
    assert summary["road_override_evidence_audit"]["publication_ready"] is True
    assert isinstance(
        summary["road_override_evidence_audit"]["override_table_present"], bool
    )
    assert summary["road_override_evidence_audit"]["override_table_present"] is True
    assert summary["road_override_evidence_audit"]["row_count"] >= 10
    assert summary["road_override_application_audit"]["publication_ready"] is True
    assert summary["road_override_application_audit"]["manifest_present"] is True
    assert summary["road_override_application_audit"]["overrides_applied"] is True
    assert summary["rail_evidence_audit"]["publication_ready"] is False
    assert summary["rail_evidence_audit"]["station_binding_ready"] is True
    # Rail is reframed as a wartime_charter_assumption (charter dispatch interval,
    # not a public-schedule median), so the rail source decision is no longer
    # recorded as reviewed — publication readiness stays blocked.
    assert summary["rail_evidence_audit"]["source_decision_ready"] is False
    assert summary["rail_evidence_audit"]["transit_stress_profile_ready"] is True
    assert (
        summary["rail_evidence_audit"]["bounded_treatment_integrity_ready"] is True
    )
    assert (
        summary["rail_evidence_audit"]["bounded_treatment_pending_decision_count"]
        == 0
    )
    assert summary["rail_evidence_audit"]["bounded_treatment_warning_count"] == 0
    assert summary["rail_evidence_audit"]["bounded_treatment_mismatch_count"] == 0
    assert summary["rail_evidence_audit"]["station_binding_remaining_blockers"] == []
    assert summary["rail_evidence_audit"]["bounded_treatment_remaining_blockers"] == []
    assert summary["publication_readiness_audit"]["publication_ready"] is False
    assert (
        summary["publication_readiness_audit"]["verdict"]
        == "final_study_claims_blocked"
    )
    assert "rail_source_decision_ready" in summary["publication_readiness_audit"][
        "gates"
    ]
    assert "rail_transit_stress_profile_ready" in summary[
        "publication_readiness_audit"
    ]["gates"]
    assert "rail_bounded_treatment_integrity_ready" in summary[
        "publication_readiness_audit"
    ]["gates"]
    # Rail reframed as a wartime_charter_assumption: source decision is pending,
    # so rail_source_decision_ready and rail_evidence_ready are False and
    # publication readiness is blocked.
    assert summary["publication_readiness_audit"]["gates"][
        "rail_source_decision_ready"
    ] is False
    assert summary["publication_readiness_audit"]["gates"][
        "rail_transit_stress_profile_ready"
    ] is True
    assert summary["publication_readiness_audit"]["gates"][
        "rail_bounded_treatment_integrity_ready"
    ] is True
    assert summary["final_study_readiness_audit"]["final_study_ready"] is False
    assert (
        summary["final_study_readiness_audit"]["verdict"]
        == "final_real_world_study_blocked"
    )
    assert summary["final_study_readiness_audit"]["gate_count"] == 15
    assert summary["final_study_readiness_audit"]["blocked_gate_ids"] == [
        "graph_scale_strategy",
        "rail_evidence",
        "full_experiment_output",
        "manuscript_report_alignment",
        "reproducibility",
        "final_audit",
    ]

    print("PASS: plan artifact audit preserves scaffold claim boundary")


def test_dirty_worktree_freshness_checks_path_set_not_only_count() -> None:
    module = _load_audit_module()
    current_rows = module.build_dirty_worktree_classification_rows()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_csv = Path(tmpdir) / "dirty.csv"
        with fake_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=("path",))
            writer.writeheader()
            for index, _row in enumerate(current_rows):
                writer.writerow({"path": f"fake/path/{index}.txt"})
        previous_csv = module.DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_CSV
        module.DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_CSV = fake_csv
        try:
            result = module._audit_dirty_worktree_classification_freshness(
                {
                    "manifest_present": True,
                    "dirty_path_count": len(current_rows),
                }
            )
        finally:
            module.DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_CSV = previous_csv
    assert result["saved_csv_dirty_path_count"] == len(current_rows)
    assert result["current_dirty_path_count"] == len(current_rows)
    assert result["coverage_matches_current_git_status"] is False
    assert result["freshness_status"] == "blocked_stale_or_incomplete"
    assert any("path set does not match" in item for item in result["remaining_blockers"])


if __name__ == "__main__":
    test_audit_plan_artifacts_reports_scaffold_boundary()
    test_dirty_worktree_freshness_checks_path_set_not_only_count()
    print("\n=== REALWORLD PLAN AUDIT TESTS PASSED ===")
