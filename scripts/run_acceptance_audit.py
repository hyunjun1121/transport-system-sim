"""Run the full sub-agent acceptance orchestration audit.

This command refreshes review packets and writes conservative sub-agent review
records. It does not create formal final-study acceptance artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.acceptance_orchestration import (  # noqa: E402
    write_acceptance_orchestration_outputs,
)
from src.realworld.acceptance_decision_templates import (  # noqa: E402
    write_acceptance_decision_templates,
)
from src.realworld.acceptance_blocker_queue import (  # noqa: E402
    write_acceptance_blocker_queue,
)
from src.realworld.acceptance_task_assignments import (  # noqa: E402
    write_acceptance_task_assignments,
)
from src.realworld.agent_review_path_audit import (  # noqa: E402
    write_agent_review_path_audit,
)
from src.realworld.claim_alignment_review_packet import (  # noqa: E402
    build_claim_alignment_review_rows,
    write_claim_alignment_review_packet,
)
from src.realworld.figure_table_review_packet import (  # noqa: E402
    build_figure_table_review_rows,
    write_figure_table_review_packet,
)
from src.realworld.manuscript_report_decision_packet import (  # noqa: E402
    build_manuscript_report_decision_rows,
    write_manuscript_report_decision_packet,
)
from src.realworld.experiment_package_review_packet import (  # noqa: E402
    build_experiment_package_review_rows,
    write_experiment_package_review_packet,
)
from src.realworld.experiment_design_decision_packet import (  # noqa: E402
    build_experiment_design_decision_rows,
    write_experiment_design_decision_packet,
)
from src.realworld.experiment_strategy_readiness_packet import (  # noqa: E402
    build_experiment_strategy_readiness_rows,
    write_experiment_strategy_readiness_packet,
)
from src.realworld.formal_acceptance_guard import (  # noqa: E402
    audit_formal_acceptance_artifacts,
)
from src.realworld.formal_acceptance_package import (  # noqa: E402
    write_formal_acceptance_package_audit,
)
from src.realworld.formal_acceptance_evidence_matrix import (  # noqa: E402
    write_formal_acceptance_evidence_matrix,
)
from src.realworld.formal_acceptance_pre_review import (  # noqa: E402
    write_formal_acceptance_pre_review,
)
from src.realworld.goal_completion_audit import write_goal_completion_audit  # noqa: E402
from src.realworld.graph_scale_manifest_audit import (  # noqa: E402
    build_graph_scale_manifest_audit_rows,
    write_graph_scale_manifest_audit,
)
from src.realworld.graph_scale_review import write_graph_scale_review_packet  # noqa: E402
from src.realworld.graph_scale_review import build_graph_scale_review_rows  # noqa: E402
from src.realworld.graph_scale_strategy_readiness_packet import (  # noqa: E402
    build_graph_scale_strategy_readiness_rows,
    write_graph_scale_strategy_readiness_packet,
)
from src.realworld.graph_scale_method_decision_packet import (  # noqa: E402
    build_graph_scale_method_decision_rows,
    write_graph_scale_method_decision_packet,
)
from src.realworld.parameter_evidence_request_packet import (  # noqa: E402
    build_parameter_evidence_source_request_rows,
    write_parameter_evidence_source_request_packet,
)
from src.realworld.parameter_source_readiness_packet import (  # noqa: E402
    build_parameter_source_readiness_rows,
    write_parameter_source_readiness_packet,
)
from src.realworld.parameter_source_decision_packet import (  # noqa: E402
    build_parameter_source_decision_rows,
    write_parameter_source_decision_packet,
)
from src.realworld.parameter_evidence_priority_packet import (  # noqa: E402
    build_parameter_evidence_priority_rows,
    write_parameter_evidence_priority_packet,
)
from src.realworld.parameter_review_packet import (  # noqa: E402
    build_parameter_review_rows,
    write_parameter_review_packet,
)
from src.realworld.pilot_privacy_review_packet import (  # noqa: E402
    build_pilot_privacy_review_rows,
    write_pilot_privacy_review_packet,
)
from src.realworld.pilot_region_decision_packet import (  # noqa: E402
    build_pilot_region_decision_rows,
    write_pilot_region_decision_packet,
)
from src.realworld.publication_readiness import (  # noqa: E402
    write_publication_readiness_audit,
)
from src.realworld.pilot_experiments import (  # noqa: E402
    DEFAULT_CACHE_PATH,
    DEFAULT_REGION_PATH,
    load_pilot_inputs,
)
from src.realworld.rail_evidence_review_packet import (  # noqa: E402
    build_rail_evidence_review_rows,
    write_rail_evidence_review_packet,
)
from src.realworld.rail_timing_request_packet import (  # noqa: E402
    build_rail_timing_source_request_rows,
    write_rail_timing_source_request_packet,
)
from src.realworld.rail_fetch_readiness_packet import (  # noqa: E402
    build_rail_fetch_readiness_rows,
    write_rail_fetch_readiness_packet,
)
from src.realworld.rail_evidence_priority_packet import (  # noqa: E402
    build_rail_evidence_priority_rows,
    write_rail_evidence_priority_packet,
)
from src.realworld.rail_source_decision_packet import (  # noqa: E402
    build_rail_source_decision_rows,
    write_rail_source_decision_packet,
)
from src.realworld.road_evidence_request_packet import (  # noqa: E402
    build_road_evidence_source_request_rows,
    write_road_evidence_source_request_packet,
)
from src.realworld.road_source_readiness_packet import (  # noqa: E402
    build_road_source_readiness_rows,
    write_road_source_readiness_packet,
)
from src.realworld.road_source_decision_packet import (  # noqa: E402
    build_road_source_decision_rows,
    write_road_source_decision_packet,
)
from src.realworld.road_evidence_review_packet import (  # noqa: E402
    build_road_evidence_review_rows,
    write_road_evidence_review_packet,
)
from src.realworld.road_evidence_priority_packet import (  # noqa: E402
    build_road_evidence_priority_rows,
    write_road_evidence_priority_packet,
)
from src.realworld.source_license_review_packet import (  # noqa: E402
    build_source_license_review_rows,
    write_source_license_review_packet,
)
from src.realworld.source_url_review_packet import (  # noqa: E402
    build_source_url_review_rows,
    write_source_url_review_packet,
)
from src.realworld.source_url_remediation_packet import (  # noqa: E402
    build_source_url_remediation_rows,
    write_source_url_remediation_packet,
)
from src.realworld.source_provenance_priority_packet import (  # noqa: E402
    build_source_provenance_priority_rows,
    write_source_provenance_priority_packet,
)
from src.realworld.source_context_cache_request_packet import (  # noqa: E402
    build_source_context_cache_request_rows,
    write_source_context_cache_request_packet,
)
from src.realworld.source_context_cache_decision_packet import (  # noqa: E402
    build_source_context_cache_decision_rows,
    write_source_context_cache_decision_packet,
)
from src.realworld.source_provenance_decision_packet import (  # noqa: E402
    build_source_provenance_decision_rows,
    write_source_provenance_decision_packet,
)
from src.realworld.reproducibility_review_packet import (  # noqa: E402
    build_reproducibility_review_rows,
    write_reproducibility_review_packet,
)
from src.realworld.reproducibility_decision_packet import (  # noqa: E402
    build_reproducibility_decision_rows,
    write_reproducibility_decision_packet,
)
from src.realworld.reproducibility_smoke import summarize_reproducibility_smoke  # noqa: E402
from src.realworld.tracked_artifact_audit import (  # noqa: E402
    build_tracked_artifact_rows,
    write_tracked_artifact_audit,
)
from src.realworld.route_road_evidence_exposure import (  # noqa: E402
    build_route_road_evidence_exposure_rows,
    write_route_road_evidence_exposure,
)
from src.realworld.sensitivity_review_packet import (  # noqa: E402
    build_sensitivity_review_rows,
    write_sensitivity_review_packet,
)
from src.realworld.sensitivity_index_review_packet import (  # noqa: E402
    build_sensitivity_index_review_rows,
    write_sensitivity_index_review_packet,
)
from src.realworld.sensitivity_method_decision_packet import (  # noqa: E402
    build_sensitivity_method_decision_rows,
    write_sensitivity_method_decision_packet,
)
from src.realworld.sensitivity_strategy_readiness_packet import (  # noqa: E402
    build_sensitivity_strategy_readiness_rows,
    write_sensitivity_strategy_readiness_packet,
)
from src.realworld.validation_review_packet import (  # noqa: E402
    build_validation_review_rows,
    write_validation_review_packet,
)
from src.realworld.validation_benchmark_readiness_packet import (  # noqa: E402
    build_validation_benchmark_readiness_rows,
    write_validation_benchmark_readiness_packet,
)
from src.realworld.validation_benchmark_decision_packet import (  # noqa: E402
    build_validation_benchmark_decision_rows,
    write_validation_benchmark_decision_packet,
)
from src.realworld.validation_strategy_readiness_packet import (  # noqa: E402
    build_validation_strategy_readiness_rows,
    write_validation_strategy_readiness_packet,
)


def main() -> int:
    """Refresh review artifacts, write agent records, and print a JSON summary."""

    args = _parse_args()
    initial_git_status_lines = _git_status_lines()
    refreshed = _refresh_existing_review_packets(
        live_source_url_checks=args.live_source_url_checks,
        source_url_timeout_sec=args.source_url_timeout_sec,
        initial_git_status_lines=initial_git_status_lines,
    )
    formal_guard = audit_formal_acceptance_artifacts()
    formal_package = write_formal_acceptance_package_audit()
    formal_evidence_paths = formal_package.get("formal_evidence_path_audit", {})
    blocker_queue = write_acceptance_blocker_queue(package_summary=formal_package)
    task_assignments = write_acceptance_task_assignments(
        package_summary=formal_package
    )
    evidence_matrix = write_formal_acceptance_evidence_matrix(
        package_summary=formal_package
    )
    pre_review = write_formal_acceptance_pre_review(
        package_summary=formal_package
    )
    reproducibility_smoke = summarize_reproducibility_smoke()
    refreshed.append("data/manifests/formal_acceptance_blocker_queue.csv")
    refreshed.append("data/manifests/acceptance_task_assignments.csv")
    refreshed.append("data/manifests/formal_acceptance_evidence_matrix.csv")
    refreshed.append(
        "data/manifests/draft_acceptance/formal_acceptance_pre_review_manifest.json"
    )
    manifest = write_acceptance_orchestration_outputs()
    agent_review_paths = write_agent_review_path_audit()
    refreshed.append("data/manifests/agent_review_path_audit.json")
    tracked_artifact_rows = build_tracked_artifact_rows(
        git_status_lines=initial_git_status_lines,
    )
    tracked_artifacts = write_tracked_artifact_audit(rows=tracked_artifact_rows)
    refreshed.append("data/validation/tracked_artifact_audit.csv")
    manifest = write_acceptance_orchestration_outputs()
    goal_audit = write_goal_completion_audit()
    refreshed.append("data/manifests/current_goal_completion_audit.json")
    publication_readiness = write_publication_readiness_audit()
    refreshed.append("data/manifests/publication_readiness_audit.json")
    manifest = write_acceptance_orchestration_outputs()
    summary = {
        "acceptance_orchestration": manifest,
        "refreshed_review_artifacts": refreshed,
        "goal_audit": {
            "final_study_ready": goal_audit["final_study_ready"],
            "verdict": goal_audit["verdict"],
            "ready_gate_count": len(goal_audit["ready_gate_ids"]),
            "blocked_gate_count": len(goal_audit["blocked_gate_ids"]),
        },
        "publication_readiness": {
            "publication_ready": publication_readiness["publication_ready"],
            "verdict": publication_readiness["verdict"],
            "ready_gate_count": publication_readiness["ready_gate_count"],
            "blocked_gate_count": publication_readiness["blocked_gate_count"],
        },
        "formal_acceptance_guard": {
            "artifact_count": formal_guard["artifact_count"],
            "present_count": formal_guard["present_count"],
            "template_or_placeholder_count": formal_guard[
                "template_or_placeholder_count"
            ],
            "formal_acceptance_ready": formal_guard["formal_acceptance_ready"],
        },
        "formal_acceptance_package": {
            "gate_count": formal_package["gate_count"],
            "ready_gate_count": formal_package["ready_gate_count"],
            "blocked_gate_count": formal_package["blocked_gate_count"],
            "invalid_gate_count": formal_package["invalid_gate_count"],
            "formal_acceptance_ready": formal_package["formal_acceptance_ready"],
            "can_mark_complete": formal_package["can_mark_complete"],
        },
        "formal_evidence_path_audit": {
            "present_artifact_count": formal_evidence_paths.get(
                "present_artifact_count",
                0,
            ),
            "evidence_item_count": formal_evidence_paths.get(
                "evidence_item_count",
                0,
            ),
            "missing_local_evidence_count": formal_evidence_paths.get(
                "missing_local_evidence_count",
                0,
            ),
            "placeholder_evidence_count": formal_evidence_paths.get(
                "placeholder_evidence_count",
                0,
            ),
            "can_mark_complete": formal_evidence_paths.get(
                "can_mark_complete",
                False,
            ),
        },
        "agent_review_path_audit": {
            "record_count": agent_review_paths["record_count"],
            "missing_required_path_count": agent_review_paths[
                "missing_required_path_count"
            ],
            "missing_formal_target_count": agent_review_paths[
                "missing_formal_target_count"
            ],
            "agent_review_paths_ready": agent_review_paths[
                "agent_review_paths_ready"
            ],
            "can_mark_complete": agent_review_paths["can_mark_complete"],
        },
        "tracked_artifact_audit": {
            "row_count": tracked_artifacts["row_count"],
            "blocking_change_count": tracked_artifacts["blocking_change_count"],
            "untracked_count": tracked_artifacts["untracked_count"],
            "modified_or_staged_count": tracked_artifacts[
                "modified_or_staged_count"
            ],
            "clean_checkout_reproducibility_ready": tracked_artifacts[
                "clean_checkout_reproducibility_ready"
            ],
            "can_mark_complete": tracked_artifacts["can_mark_complete"],
        },
        "formal_acceptance_blocker_queue": {
            "row_count": blocker_queue["row_count"],
            "formal_acceptance_ready": blocker_queue["formal_acceptance_ready"],
            "final_study_ready": blocker_queue["final_study_ready"],
            "can_mark_complete": blocker_queue["can_mark_complete"],
        },
        "acceptance_task_assignments": {
            "task_count": task_assignments["task_count"],
            "assigned_agent_count": task_assignments["assigned_agent_count"],
            "formal_acceptance_ready": task_assignments["formal_acceptance_ready"],
            "final_study_ready": task_assignments["final_study_ready"],
            "can_mark_complete": task_assignments["can_mark_complete"],
        },
        "formal_acceptance_evidence_matrix": {
            "row_count": evidence_matrix["row_count"],
            "human_decision_required_count": evidence_matrix[
                "human_decision_required_count"
            ],
            "formal_acceptance_ready": evidence_matrix["formal_acceptance_ready"],
            "final_study_ready": evidence_matrix["final_study_ready"],
            "can_mark_complete": evidence_matrix["can_mark_complete"],
        },
        "formal_acceptance_pre_review": {
            "record_count": pre_review["record_count"],
            "recommendation_counts": pre_review["recommendation_counts"],
            "human_decision_required_count": pre_review[
                "human_decision_required_count"
            ],
            "formal_approval": pre_review["formal_approval"],
            "final_study_ready": pre_review["final_study_ready"],
            "can_mark_complete": pre_review["can_mark_complete"],
        },
        "reproducibility_smoke": {
            "manifest_present": reproducibility_smoke["manifest_present"],
            "smoke_passed": reproducibility_smoke["smoke_passed"],
            "command_count": reproducibility_smoke["command_count"],
            "clean_checkout_test_performed": reproducibility_smoke[
                "clean_checkout_test_performed"
            ],
            "can_mark_complete": reproducibility_smoke["can_mark_complete"],
        },
        "claim_boundary": (
            "This command writes review aids only. It does not fabricate formal "
            "acceptance, reviewer decisions, source claims, licenses, or final audit approval."
        ),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_blockers and not manifest["final_study_ready"]:
        return 1
    return 0


def _refresh_existing_review_packets(
    *,
    live_source_url_checks: bool = False,
    source_url_timeout_sec: float = 8.0,
    initial_git_status_lines: list[str] | None = None,
) -> list[str]:
    refreshed: list[str] = []
    pilot_privacy_rows = build_pilot_privacy_review_rows()
    write_pilot_privacy_review_packet(rows=pilot_privacy_rows)
    refreshed.append("data/manifests/pilot_privacy_review_packet.csv")
    pilot_decision_rows = build_pilot_region_decision_rows()
    write_pilot_region_decision_packet(rows=pilot_decision_rows)
    refreshed.append("data/manifests/pilot_region_decision_packet.csv")
    graph_scale_manifest_rows = build_graph_scale_manifest_audit_rows()
    write_graph_scale_manifest_audit(rows=graph_scale_manifest_rows)
    refreshed.append("data/validation/graph_scale_manifest_audit.csv")
    graph_scale_rows = build_graph_scale_review_rows()
    write_graph_scale_review_packet(rows=graph_scale_rows)
    refreshed.append("data/validation/graph_scale_review_packet.csv")
    graph_scale_readiness_rows = build_graph_scale_strategy_readiness_rows(
        review_rows=graph_scale_rows,
    )
    write_graph_scale_strategy_readiness_packet(rows=graph_scale_readiness_rows)
    refreshed.append("data/validation/graph_scale_strategy_readiness_packet.csv")
    graph_scale_method_decision_rows = build_graph_scale_method_decision_rows()
    write_graph_scale_method_decision_packet(rows=graph_scale_method_decision_rows)
    refreshed.append("data/validation/graph_scale_method_decision_packet.csv")
    parameter_rows = build_parameter_review_rows()
    write_parameter_review_packet(rows=parameter_rows)
    refreshed.append("data/parameters/parameter_evidence_review_packet.csv")
    parameter_request_rows = build_parameter_evidence_source_request_rows()
    write_parameter_evidence_source_request_packet(rows=parameter_request_rows)
    refreshed.append("data/parameters/parameter_evidence_source_request_packet.csv")
    parameter_readiness_rows = build_parameter_source_readiness_rows(
        request_rows=parameter_request_rows,
    )
    write_parameter_source_readiness_packet(rows=parameter_readiness_rows)
    refreshed.append("data/parameters/parameter_source_readiness_packet.csv")
    parameter_priority_rows = build_parameter_evidence_priority_rows()
    write_parameter_evidence_priority_packet(rows=parameter_priority_rows)
    refreshed.append("data/parameters/parameter_evidence_priority_packet.csv")
    parameter_decision_rows = build_parameter_source_decision_rows(
        readiness_rows=parameter_readiness_rows,
    )
    write_parameter_source_decision_packet(rows=parameter_decision_rows)
    refreshed.append("data/parameters/parameter_source_decision_packet.csv")
    rail_rows = build_rail_evidence_review_rows()
    write_rail_evidence_review_packet(rows=rail_rows)
    refreshed.append("data/parameters/rail_evidence_review_packet.csv")
    rail_request_rows = build_rail_timing_source_request_rows()
    write_rail_timing_source_request_packet(rows=rail_request_rows)
    refreshed.append("data/rail/rail_timing_source_request_packet.csv")
    rail_fetch_rows = build_rail_fetch_readiness_rows(request_rows=rail_request_rows)
    write_rail_fetch_readiness_packet(rows=rail_fetch_rows)
    refreshed.append("data/rail/rail_fetch_readiness_packet.csv")
    rail_priority_rows = build_rail_evidence_priority_rows()
    write_rail_evidence_priority_packet(rows=rail_priority_rows)
    refreshed.append("data/rail/rail_evidence_priority_packet.csv")
    rail_decision_rows = build_rail_source_decision_rows(
        readiness_rows=rail_fetch_rows,
    )
    write_rail_source_decision_packet(rows=rail_decision_rows)
    refreshed.append("data/rail/rail_source_decision_packet.csv")
    road_rows = build_road_evidence_review_rows()
    write_road_evidence_review_packet(rows=road_rows)
    refreshed.append("data/parameters/road_evidence_review_packet.csv")
    road_request_rows = build_road_evidence_source_request_rows()
    write_road_evidence_source_request_packet(rows=road_request_rows)
    refreshed.append("data/road/road_evidence_source_request_packet.csv")
    road_readiness_rows = build_road_source_readiness_rows(
        request_rows=road_request_rows,
    )
    write_road_source_readiness_packet(rows=road_readiness_rows)
    refreshed.append("data/road/road_source_readiness_packet.csv")
    road_decision_rows = build_road_source_decision_rows(
        readiness_rows=road_readiness_rows,
    )
    write_road_source_decision_packet(rows=road_decision_rows)
    refreshed.append("data/road/road_source_decision_packet.csv")
    source_license_rows = build_source_license_review_rows()
    write_source_license_review_packet(rows=source_license_rows)
    refreshed.append("data/manifests/source_license_review_packet.csv")
    source_url_rows = build_source_url_review_rows(
        live_check=live_source_url_checks,
        timeout_sec=source_url_timeout_sec,
        preserve_existing_live=not live_source_url_checks,
    )
    write_source_url_review_packet(rows=source_url_rows)
    refreshed.append("data/manifests/source_url_review_packet.csv")
    source_url_remediation_rows = build_source_url_remediation_rows(
        url_rows=source_url_rows,
    )
    write_source_url_remediation_packet(rows=source_url_remediation_rows)
    refreshed.append("data/manifests/source_url_remediation_packet.csv")
    source_priority_rows = build_source_provenance_priority_rows()
    write_source_provenance_priority_packet(rows=source_priority_rows)
    refreshed.append("data/manifests/source_provenance_priority_packet.csv")
    source_context_cache_rows = build_source_context_cache_request_rows(
        source_priority_rows=source_priority_rows,
    )
    write_source_context_cache_request_packet(rows=source_context_cache_rows)
    refreshed.append("data/manifests/source_context_cache_request_packet.csv")
    source_context_cache_decision_rows = build_source_context_cache_decision_rows(
        request_rows=source_context_cache_rows,
    )
    write_source_context_cache_decision_packet(
        rows=source_context_cache_decision_rows,
    )
    refreshed.append("data/manifests/source_context_cache_decision_packet.csv")
    source_provenance_decision_rows = build_source_provenance_decision_rows()
    write_source_provenance_decision_packet(rows=source_provenance_decision_rows)
    refreshed.append("data/manifests/source_provenance_decision_packet.csv")
    claim_alignment_rows = build_claim_alignment_review_rows()
    write_claim_alignment_review_packet(rows=claim_alignment_rows)
    refreshed.append("data/manifests/claim_alignment_review_packet.csv")
    figure_table_review_rows = build_figure_table_review_rows()
    write_figure_table_review_packet(rows=figure_table_review_rows)
    refreshed.append("data/manifests/figure_table_review_packet.csv")
    manuscript_report_decision_rows = build_manuscript_report_decision_rows()
    write_manuscript_report_decision_packet(rows=manuscript_report_decision_rows)
    refreshed.append("data/manifests/manuscript_report_decision_packet.csv")
    pilot_inputs = load_pilot_inputs(
        region_path=DEFAULT_REGION_PATH,
        cache_path=DEFAULT_CACHE_PATH,
        reduce_graph=False,
    )
    route_exposure_rows = build_route_road_evidence_exposure_rows(pilot_inputs.graph)
    write_route_road_evidence_exposure(rows=route_exposure_rows)
    refreshed.append("data/validation/canonical_route_road_evidence_exposure.csv")
    road_priority_rows = build_road_evidence_priority_rows()
    write_road_evidence_priority_packet(rows=road_priority_rows)
    refreshed.append("data/road/road_evidence_priority_packet.csv")
    sensitivity_rows = build_sensitivity_review_rows()
    write_sensitivity_review_packet(rows=sensitivity_rows)
    refreshed.append("data/validation/sensitivity_review_packet.csv")
    sensitivity_index_rows = build_sensitivity_index_review_rows()
    write_sensitivity_index_review_packet(rows=sensitivity_index_rows)
    refreshed.append("data/validation/sensitivity_index_review_packet.csv")
    sensitivity_readiness_rows = build_sensitivity_strategy_readiness_rows(
        review_rows=sensitivity_rows,
    )
    write_sensitivity_strategy_readiness_packet(rows=sensitivity_readiness_rows)
    refreshed.append("data/validation/sensitivity_strategy_readiness_packet.csv")
    sensitivity_method_rows = build_sensitivity_method_decision_rows()
    write_sensitivity_method_decision_packet(rows=sensitivity_method_rows)
    refreshed.append("data/validation/sensitivity_method_decision_packet.csv")
    experiment_rows = build_experiment_package_review_rows()
    write_experiment_package_review_packet(rows=experiment_rows)
    refreshed.append("data/manifests/experiment_package_review_packet.csv")
    experiment_readiness_rows = build_experiment_strategy_readiness_rows(
        review_rows=experiment_rows,
    )
    write_experiment_strategy_readiness_packet(rows=experiment_readiness_rows)
    refreshed.append("data/manifests/experiment_strategy_readiness_packet.csv")
    experiment_design_decision_rows = build_experiment_design_decision_rows()
    write_experiment_design_decision_packet(rows=experiment_design_decision_rows)
    refreshed.append("data/manifests/experiment_design_decision_packet.csv")
    benchmark_readiness_rows = build_validation_benchmark_readiness_rows()
    write_validation_benchmark_readiness_packet(rows=benchmark_readiness_rows)
    refreshed.append("data/validation/validation_benchmark_readiness_packet.csv")
    validation_rows = build_validation_review_rows()
    write_validation_review_packet(rows=validation_rows)
    refreshed.append("data/validation/validation_review_packet.csv")
    validation_readiness_rows = build_validation_strategy_readiness_rows(
        review_rows=validation_rows,
    )
    write_validation_strategy_readiness_packet(rows=validation_readiness_rows)
    refreshed.append("data/validation/validation_strategy_readiness_packet.csv")
    validation_benchmark_decision_rows = build_validation_benchmark_decision_rows()
    write_validation_benchmark_decision_packet(
        rows=validation_benchmark_decision_rows
    )
    refreshed.append("data/validation/validation_benchmark_decision_packet.csv")
    reproducibility_rows = build_reproducibility_review_rows(
        git_status_lines=initial_git_status_lines,
    )
    write_reproducibility_review_packet(
        rows=reproducibility_rows,
        git_status_lines=initial_git_status_lines,
    )
    refreshed.append("data/validation/reproducibility_review_packet.csv")
    reproducibility_decision_rows = build_reproducibility_decision_rows()
    write_reproducibility_decision_packet(rows=reproducibility_decision_rows)
    refreshed.append("data/validation/reproducibility_decision_packet.csv")
    write_acceptance_decision_templates()
    refreshed.append("data/manifests/acceptance_decision_template_manifest.json")
    return refreshed


def _git_status_lines() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return [f"!! git status failed: {result.stderr.strip()}"]
    return [line for line in result.stdout.splitlines() if line.strip()]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when final-study gates remain blocked.",
    )
    parser.add_argument(
        "--live-source-url-checks",
        action="store_true",
        help=(
            "Run bounded live HTTP reachability checks for source URL review rows. "
            "This records reviewer-aid evidence only and never closes provenance acceptance."
        ),
    )
    parser.add_argument(
        "--source-url-timeout-sec",
        type=float,
        default=8.0,
        help="Per-URL timeout for --live-source-url-checks.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
