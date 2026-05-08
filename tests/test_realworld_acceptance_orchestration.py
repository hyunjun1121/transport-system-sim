"""Tests for sub-agent acceptance orchestration."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.acceptance_orchestration import (  # noqa: E402
    DEFAULT_REVIEW_STATUS_SNAPSHOT_MANIFESTS,
    REVIEW_AGENT_DEFINITIONS,
    build_acceptance_record,
    summarize_acceptance_orchestration_manifest,
    write_acceptance_orchestration_outputs,
)
from src.realworld.acceptance_records import load_acceptance_record  # noqa: E402
from src.realworld.final_study_readiness import audit_final_study_readiness  # noqa: E402


def test_acceptance_orchestration_defines_required_review_agents() -> None:
    names = {agent.role_name for agent in REVIEW_AGENT_DEFINITIONS}
    assert "Pilot Region & Privacy Review Agent" in names
    assert "OSM / Source / License / Provenance Review Agent" in names
    assert "Graph Scale Method Review Agent" in names
    assert "Road / Rail / Parameter Evidence Agent" in names
    assert "Validation Benchmark Strategy Agent" in names
    assert "Sensitivity Analysis Review Agent" in names
    assert "Full Experiment Package Agent" in names
    assert "Paper / Report Claim Alignment Agent" in names
    assert "Clean-Checkout Reproducibility Agent" in names
    assert "Final Independent Audit Agent" in names


def test_review_agents_point_at_current_readiness_packets() -> None:
    """Reviewer intake should include current blocker-classification packets."""

    agents = {agent.agent_id: agent for agent in REVIEW_AGENT_DEFINITIONS}

    pilot_agent = agents["pilot_region_privacy_review_agent"]
    assert "data/manifests/pilot_privacy_review_packet.csv" in (
        pilot_agent.review_packet_paths
    )
    assert "data/manifests/pilot_region_decision_packet.csv" in (
        pilot_agent.review_packet_paths
    )
    assert "data/manifests/pilot_privacy_review_manifest.json" in (
        pilot_agent.source_paths
    )
    assert "data/manifests/pilot_region_decision_manifest.json" in (
        pilot_agent.source_paths
    )
    assert "data/manifests/current_goal_completion_audit.json" in (
        pilot_agent.reviewed_inputs
    )

    graph_agent = agents["graph_scale_method_review_agent"]
    assert (
        "data/validation/graph_scale_strategy_readiness_packet.csv"
        in graph_agent.review_packet_paths
    )
    assert (
        "data/validation/graph_scale_method_decision_packet.csv"
        in graph_agent.review_packet_paths
    )
    assert (
        "data/validation/full_graph_runtime_readiness_packet.csv"
        in graph_agent.review_packet_paths
    )
    assert "data/validation/graph_scale_manifest_audit.csv" in (
        graph_agent.review_packet_paths
    )

    provenance_agent = agents["osm_source_license_provenance_review_agent"]
    assert "data/manifests/source_url_review_packet.csv" in (
        provenance_agent.review_packet_paths
    )
    assert "data/manifests/source_provenance_priority_packet.csv" in (
        provenance_agent.review_packet_paths
    )
    assert "data/manifests/source_context_cache_request_packet.csv" in (
        provenance_agent.review_packet_paths
    )
    assert "data/manifests/source_context_cache_decision_packet.csv" in (
        provenance_agent.review_packet_paths
    )
    assert "data/manifests/current_goal_completion_audit.json" in (
        provenance_agent.reviewed_inputs
    )

    evidence_agent = agents["road_rail_parameter_evidence_agent"]
    assert (
        "data/parameters/parameter_source_readiness_packet.csv"
        in evidence_agent.review_packet_paths
    )
    assert (
        "data/parameters/parameter_evidence_priority_packet.csv"
        in evidence_agent.review_packet_paths
    )
    assert (
        "data/parameters/parameter_source_decision_packet.csv"
        in evidence_agent.review_packet_paths
    )
    assert "data/road/road_source_readiness_packet.csv" in (
        evidence_agent.review_packet_paths
    )
    assert "data/road/road_source_decision_packet.csv" in (
        evidence_agent.review_packet_paths
    )
    assert "data/road/road_evidence_priority_packet.csv" in (
        evidence_agent.review_packet_paths
    )
    assert "data/rail/rail_fetch_readiness_packet.csv" in (
        evidence_agent.review_packet_paths
    )
    assert "data/rail/rail_evidence_priority_packet.csv" in (
        evidence_agent.review_packet_paths
    )
    assert "data/rail/rail_source_decision_packet.csv" in (
        evidence_agent.review_packet_paths
    )

    validation_agent = agents["validation_benchmark_strategy_agent"]
    assert (
        "data/validation/validation_strategy_readiness_packet.csv"
        in validation_agent.review_packet_paths
    )
    assert (
        "data/validation/validation_benchmark_readiness_packet.csv"
        in validation_agent.review_packet_paths
    )
    assert (
        "data/validation/validation_benchmark_decision_packet.csv"
        in validation_agent.review_packet_paths
    )

    sensitivity_agent = agents["sensitivity_analysis_review_agent"]
    assert (
        "data/validation/sensitivity_index_review_packet.csv"
        in sensitivity_agent.review_packet_paths
    )
    assert (
        "data/validation/sensitivity_strategy_readiness_packet.csv"
        in sensitivity_agent.review_packet_paths
    )
    assert (
        "data/validation/sensitivity_method_decision_packet.csv"
        in sensitivity_agent.review_packet_paths
    )

    experiment_agent = agents["full_experiment_package_agent"]
    assert "data/manifests/experiment_strategy_readiness_packet.csv" in (
        experiment_agent.review_packet_paths
    )
    assert "data/manifests/experiment_design_decision_packet.csv" in (
        experiment_agent.review_packet_paths
    )

    manuscript_agent = agents["paper_report_claim_alignment_agent"]
    assert "data/manifests/figure_table_review_packet.csv" in (
        manuscript_agent.review_packet_paths
    )
    assert "data/manifests/figure_table_review_manifest.json" in (
        manuscript_agent.reviewed_inputs
    )

    reproducibility_agent = agents["clean_checkout_reproducibility_agent"]
    assert "data/validation/tracked_artifact_audit.csv" in (
        reproducibility_agent.review_packet_paths
    )
    assert "data/manifests/current_goal_completion_audit.json" in (
        reproducibility_agent.source_paths
    )

    final_agent = agents["final_independent_audit_agent"]
    assert "data/manifests/current_goal_completion_audit.json" in (
        final_agent.source_paths
    )


def test_default_review_status_snapshots_cover_formal_workflow() -> None:
    snapshot_ids = [item[0] for item in DEFAULT_REVIEW_STATUS_SNAPSHOT_MANIFESTS]
    assert len(snapshot_ids) == len(set(snapshot_ids))
    assert "formal_acceptance_blocker_queue" in snapshot_ids
    assert "acceptance_task_assignments" in snapshot_ids
    assert "formal_acceptance_evidence_matrix" in snapshot_ids
    assert "formal_acceptance_pre_review" in snapshot_ids
    assert "formal_acceptance_package_audit" in snapshot_ids
    assert "formal_evidence_path_audit" in snapshot_ids
    assert "agent_review_path_audit" in snapshot_ids
    assert "tracked_artifact_audit" in snapshot_ids
    assert "current_goal_completion_audit" in snapshot_ids
    assert "publication_readiness_audit" in snapshot_ids
    assert "source_context_cache_request" in snapshot_ids
    assert "source_context_cache_decision" in snapshot_ids
    assert "parameter_source_decision" in snapshot_ids
    assert "road_source_decision" in snapshot_ids
    assert "rail_source_decision" in snapshot_ids
    assert "pilot_region_decision" in snapshot_ids
    assert "graph_scale_method_decision" in snapshot_ids
    assert "validation_benchmark_decision" in snapshot_ids
    assert "experiment_design_decision" in snapshot_ids
    assert "figure_table_review" in snapshot_ids


def test_acceptance_orchestration_blocks_nonready_gate_without_completion() -> None:
    audit = audit_final_study_readiness()
    gate_map = {gate["gate_id"]: gate for gate in audit["gates"]}
    pilot_agent = next(
        agent
        for agent in REVIEW_AGENT_DEFINITIONS
        if agent.agent_id == "pilot_region_privacy_review_agent"
    )
    record = build_acceptance_record(
        pilot_agent,
        gate_map["pilot_region_accepted"],
        "2026-05-04T00:00:00+00:00",
    )
    assert record.status == "needs_human_review"
    assert record.can_mark_complete is False
    assert record.required_actions
    assert record.risks
    assert "data/manifests/pilot_privacy_review_packet.csv" in (
        record.review_packet_paths
    )


def test_acceptance_orchestration_writes_records_and_manifest() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        source_priority_path = root / "source_provenance_priority_manifest.json"
        source_priority_path.write_text(
            json.dumps(
                {
                    "outputs": {
                        "csv": "data/manifests/source_provenance_priority_packet.csv"
                    },
                    "row_count": 11,
                    "blocking_source_count": 4,
                    "human_review_source_count": 7,
                    "context_only_source_count": 4,
                    "cached_snapshot_source_count": 3,
                    "repository_input_source_count": 4,
                    "provenance_gate_closure_candidate_count": 0,
                    "can_mark_complete": False,
                    "publication_ready": False,
                    "review_items": ["cache or exclude context-only sources"],
                    "remaining_blockers": [
                        "context-only public sources still need cached extracts"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        pilot_region_decision_snapshot_path = (
            root / "pilot_region_decision_manifest.json"
        )
        pilot_region_decision_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 6,
                    "blocking_decision_count": 3,
                    "human_review_decision_count": 3,
                    "pilot_acceptance_closure_candidate_count": 0,
                    "can_mark_complete": False,
                    "publication_ready": False,
                    "decision_status_counts": {
                        "blocked_missing_pilot_acceptance_record": 1,
                        "needs_human_review_pilot_case_scope": 1,
                    },
                    "remaining_blockers": [
                        "data/manifests/pilot_acceptance.json is absent"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        validation_snapshot_path = root / "validation_benchmark_manifest.json"
        validation_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 4,
                    "blocking_request_count": 1,
                    "human_review_request_count": 3,
                    "benchmark_gate_closure_candidate_count": 0,
                    "can_mark_complete": False,
                    "publication_ready": False,
                    "readiness_status_counts": {
                        "blocked_missing_validation_acceptance_record": 1,
                        "needs_human_review_cached_osrm_snapshot": 1,
                    },
                    "remaining_blockers": [
                        "validation_acceptance_record is absent"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        validation_decision_snapshot_path = root / "validation_benchmark_decision_manifest.json"
        validation_decision_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 6,
                    "blocking_decision_count": 3,
                    "human_review_decision_count": 3,
                    "validation_gate_closure_candidate_count": 0,
                    "can_mark_complete": False,
                    "publication_ready": False,
                    "decision_status_counts": {
                        "blocked_missing_validation_acceptance_record": 1,
                        "needs_human_review_cached_osrm_scope_policy": 1,
                    },
                    "remaining_blockers": [
                        "data/manifests/validation_acceptance.json is absent"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        experiment_design_snapshot_path = root / "experiment_design_decision_manifest.json"
        experiment_design_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 8,
                    "blocking_decision_count": 4,
                    "human_review_decision_count": 4,
                    "experiment_gate_closure_candidate_count": 0,
                    "can_mark_complete": False,
                    "publication_ready": False,
                    "decision_status_counts": {
                        "blocked_missing_experiment_acceptance_record": 1,
                        "needs_human_review_scenario_policy_seed_design": 1,
                    },
                    "remaining_blockers": [
                        "data/manifests/experiment_acceptance.json is absent"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        figure_table_snapshot_path = root / "figure_table_review_manifest.json"
        figure_table_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 8,
                    "blocking_review_count": 3,
                    "human_review_count": 5,
                    "manuscript_gate_closure_candidate_count": 0,
                    "can_mark_complete": False,
                    "publication_ready": False,
                    "review_status_counts": {
                        "blocked_missing_manuscript_acceptance_record": 1,
                        "blocked_reduced_graph_scope_dependency": 1,
                        "needs_human_review_caption_boundary": 1,
                    },
                    "remaining_blockers": [
                        "data/manifests/manuscript_acceptance.json is absent"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        graph_result_snapshot_path = root / "graph_result_manifest.json"
        graph_result_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 819,
                    "can_mark_complete": False,
                    "publication_ready": False,
                    "comparison_status_counts": {
                        "candidate_worsens": 24,
                        "nonfinite_difference": 30,
                        "same_or_close": 741,
                    },
                    "review_items": [
                        "review candidate_worsens and nonfinite_difference rows"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        graph_method_decision_snapshot_path = (
            root / "graph_method_decision_manifest.json"
        )
        graph_method_decision_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 7,
                    "blocking_decision_count": 4,
                    "human_review_decision_count": 3,
                    "graph_scale_gate_closure_candidate_count": 0,
                    "can_mark_complete": False,
                    "publication_ready": False,
                    "decision_status_counts": {
                        "blocked_missing_graph_scale_acceptance_record": 1,
                        "needs_human_review_reduced_corridor_warning_policy": 1,
                    },
                    "remaining_blockers": [
                        "data/manifests/graph_scale_acceptance.json is absent"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        source_url_snapshot_path = root / "source_url_manifest.json"
        source_url_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 17,
                    "unreachable_or_error_count": 1,
                    "requires_reviewer_confirmation_count": 17,
                    "provenance_gate_closure_candidate_count": 0,
                    "can_mark_complete": False,
                    "publication_ready": False,
                    "url_status_counts": {
                        "network_error": 1,
                        "no_url_detected": 4,
                        "reachable": 12,
                    },
                    "remaining_blockers": [
                        "failed URL rows require remediation review"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        source_context_cache_snapshot_path = (
            root / "source_context_cache_request_manifest.json"
        )
        source_context_cache_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 4,
                    "blocking_request_count": 4,
                    "missing_target_cache_artifact_count": 4,
                    "can_mark_complete": False,
                    "publication_ready": False,
                    "cache_request_status_counts": {
                        "blocked_missing_context_source_cache": 4,
                    },
                    "remaining_blockers": [
                        "context-only public sources still lack reviewed cached extracts"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        source_context_cache_decision_snapshot_path = (
            root / "source_context_cache_decision_manifest.json"
        )
        source_context_cache_decision_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 4,
                    "blocking_decision_count": 4,
                    "human_review_decision_count": 0,
                    "decision_status_counts": {
                        "blocked_missing_context_source_cache_or_exclusion_decision": 4
                    },
                    "publication_ready": False,
                    "can_mark_complete": False,
                    "provenance_gate_closure_candidate_count": 0,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        parameter_source_decision_snapshot_path = (
            root / "parameter_source_decision_manifest.json"
        )
        parameter_source_decision_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 6,
                    "blocking_decision_count": 1,
                    "human_review_decision_count": 5,
                    "decision_status_counts": {
                        "blocked_missing_parameter_source_decision": 1,
                        "needs_human_review_parameter_source_decision": 5,
                    },
                    "publication_ready": False,
                    "can_mark_complete": False,
                    "parameter_evidence_gate_closure_candidate_count": 0,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        road_source_decision_snapshot_path = (
            root / "road_source_decision_manifest.json"
        )
        road_source_decision_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 5,
                    "blocking_decision_count": 2,
                    "human_review_decision_count": 3,
                    "cached_osm_input_gate_closure_candidate_count": 0,
                    "publication_ready": False,
                    "can_mark_complete": False,
                    "decision_status_counts": {
                        "blocked_missing_road_source_decision": 2,
                        "needs_human_review_road_source_decision": 3,
                    },
                    "remaining_blockers": [
                        "road source decisions are pending"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        rail_source_decision_snapshot_path = (
            root / "rail_source_decision_manifest.json"
        )
        rail_source_decision_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 5,
                    "blocking_decision_count": 3,
                    "human_review_decision_count": 2,
                    "rail_service_evidence_gate_closure_candidate_count": 0,
                    "publication_ready": False,
                    "can_mark_complete": False,
                    "decision_status_counts": {
                        "blocked_missing_rail_source_decision": 3,
                        "needs_human_review_rail_source_decision": 2,
                    },
                    "remaining_blockers": [
                        "rail source decisions are pending"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        formal_queue_snapshot_path = root / "formal_queue_manifest.json"
        formal_queue_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 15,
                    "requires_human_review_count": 15,
                    "can_mark_complete": False,
                    "status_counts": {"blocked": 15},
                    "remaining_blockers": [
                        "resolve each formal blocker with source-backed evidence"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        pre_review_snapshot_path = root / "formal_pre_review_manifest.json"
        pre_review_snapshot_path.write_text(
            json.dumps(
                {
                    "record_count": 12,
                    "human_decision_required_count": 12,
                    "can_mark_complete": False,
                    "recommendation_counts": {
                        "blocked_missing_evidence": 8,
                        "blocked_requires_human_decision": 4,
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        agent_path_snapshot_path = root / "agent_path_manifest.json"
        agent_path_snapshot_path.write_text(
            json.dumps(
                {
                    "record_count": 12,
                    "can_mark_complete": False,
                    "agent_review_paths_ready": True,
                    "missing_required_path_count": 0,
                    "missing_formal_target_count": 36,
                    "status_counts": {
                        "missing_formal_target": 36,
                        "present": 617,
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        tracked_artifact_snapshot_path = root / "tracked_artifact_manifest.json"
        tracked_artifact_snapshot_path.write_text(
            json.dumps(
                {
                    "row_count": 3,
                    "blocking_change_count": 2,
                    "modified_or_staged_count": 2,
                    "untracked_count": 1,
                    "can_mark_complete": False,
                    "category_counts": {
                        "generated_review_artifact": 2,
                        "untracked_candidate": 1,
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        goal_completion_snapshot_path = root / "current_goal_completion_audit.json"
        goal_completion_snapshot_path.write_text(
            json.dumps(
                {
                    "gate_count": 15,
                    "ready_gate_count": 3,
                    "blocked_gate_count": 12,
                    "missing_acceptance_artifact_count": 12,
                    "final_study_ready": False,
                    "can_mark_complete": False,
                    "status_counts": {
                        "blocked": 12,
                        "missing_acceptance_artifact": 12,
                        "ready": 3,
                    },
                    "remaining_blockers": [
                        "final-study readiness audit is still false"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        publication_snapshot_path = root / "publication_readiness_audit.json"
        publication_snapshot_path.write_text(
            json.dumps(
                {
                    "gate_count": 7,
                    "ready_gate_count": 1,
                    "blocked_gate_count": 6,
                    "publication_ready": False,
                    "can_mark_complete": False,
                    "status_counts": {
                        "blocked": 6,
                        "ready": 1,
                    },
                    "remaining_blockers": [
                        "parameter evidence: weak assumptions remain"
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        manifest = write_acceptance_orchestration_outputs(
            output_dir=root / "agent_reviews",
            review_packet_dir=root / "review_packets",
            manifest_path=root / "acceptance_orchestration_manifest.json",
            agent_definition_path=root / "agents.json",
            agent_doc_path=root / "agents.md",
            schema_path=root / "schema.json",
            source_provenance_priority_manifest_path=source_priority_path,
            review_status_snapshot_manifests=(
                (
                    "source_provenance_priority",
                    "Source Provenance Priority",
                    source_priority_path,
                ),
                (
                    "pilot_region_decision",
                    "Pilot Region Decision",
                    pilot_region_decision_snapshot_path,
                ),
                (
                    "validation_benchmark_readiness",
                    "Validation Benchmark Readiness",
                    validation_snapshot_path,
                ),
                (
                    "validation_benchmark_decision",
                    "Validation Benchmark Decision",
                    validation_decision_snapshot_path,
                ),
                (
                    "experiment_design_decision",
                    "Experiment Design Decision",
                    experiment_design_snapshot_path,
                ),
                (
                    "figure_table_review",
                    "Figure/Table Review",
                    figure_table_snapshot_path,
                ),
                (
                    "graph_scale_result_comparison",
                    "Graph-Scale Result Comparison",
                    graph_result_snapshot_path,
                ),
                (
                    "graph_scale_method_decision",
                    "Graph-Scale Method Decision",
                    graph_method_decision_snapshot_path,
                ),
                (
                    "source_url_review",
                    "Source URL Review",
                    source_url_snapshot_path,
                ),
                (
                    "source_context_cache_request",
                    "Source Context Cache Requests",
                    source_context_cache_snapshot_path,
                ),
                (
                    "source_context_cache_decision",
                    "Source Context Cache Decisions",
                    source_context_cache_decision_snapshot_path,
                ),
                (
                    "parameter_source_decision",
                    "Parameter Source Decisions",
                    parameter_source_decision_snapshot_path,
                ),
                (
                    "road_source_decision",
                    "Road Source Decisions",
                    road_source_decision_snapshot_path,
                ),
                (
                    "rail_source_decision",
                    "Rail Source Decisions",
                    rail_source_decision_snapshot_path,
                ),
                (
                    "formal_acceptance_blocker_queue",
                    "Formal Acceptance Blocker Queue",
                    formal_queue_snapshot_path,
                ),
                (
                    "formal_acceptance_pre_review",
                    "Formal Acceptance Pre-Review",
                    pre_review_snapshot_path,
                ),
                (
                    "agent_review_path_audit",
                    "Agent Review Path Audit",
                    agent_path_snapshot_path,
                ),
                (
                    "tracked_artifact_audit",
                    "Tracked Artifact Audit",
                    tracked_artifact_snapshot_path,
                ),
                (
                    "current_goal_completion_audit",
                    "Current Goal Completion Audit",
                    goal_completion_snapshot_path,
                ),
                (
                    "publication_readiness_audit",
                    "Publication Readiness Audit",
                    publication_snapshot_path,
                ),
            ),
        )
        assert manifest["final_study_ready"] is False
        assert manifest["record_count"] >= 10
        assert manifest["blocked_or_review_record_count"] >= 1
        assert manifest["can_mark_complete_count"] == 0
        assert manifest["source_provenance_priority"]["row_count"] == 11
        assert (
            manifest["source_provenance_priority"]["blocking_source_count"] == 4
        )
        assert (
            manifest["source_provenance_priority"][
                "provenance_gate_closure_candidate_count"
            ]
            == 0
        )
        snapshots = {
            item["snapshot_id"]: item
            for item in manifest["review_packet_snapshots"]
        }
        assert snapshots["source_provenance_priority"]["blocking_count"] == 4
        assert snapshots["pilot_region_decision"]["blocking_count"] == 3
        assert snapshots["pilot_region_decision"]["human_review_count"] == 3
        assert (
            snapshots["pilot_region_decision"]["status_counts"][
                "blocked_missing_pilot_acceptance_record"
            ]
            == 1
        )
        assert (
            snapshots["validation_benchmark_readiness"]["human_review_count"]
            == 3
        )
        assert (
            snapshots["validation_benchmark_readiness"][
                "gate_closure_candidate_count"
            ]
            == 0
        )
        assert snapshots["validation_benchmark_decision"]["blocking_count"] == 3
        assert snapshots["validation_benchmark_decision"]["human_review_count"] == 3
        assert (
            snapshots["validation_benchmark_decision"]["status_counts"][
                "blocked_missing_validation_acceptance_record"
            ]
            == 1
        )
        assert snapshots["experiment_design_decision"]["blocking_count"] == 4
        assert snapshots["experiment_design_decision"]["human_review_count"] == 4
        assert (
            snapshots["experiment_design_decision"]["status_counts"][
                "blocked_missing_experiment_acceptance_record"
            ]
            == 1
        )
        assert snapshots["figure_table_review"]["blocking_count"] == 3
        assert snapshots["figure_table_review"]["human_review_count"] == 5
        assert (
            snapshots["figure_table_review"]["status_counts"][
                "blocked_missing_manuscript_acceptance_record"
            ]
            == 1
        )
        assert (
            snapshots["graph_scale_result_comparison"]["status_counts"][
                "candidate_worsens"
            ]
            == 24
        )
        assert snapshots["graph_scale_method_decision"]["blocking_count"] == 4
        assert snapshots["graph_scale_method_decision"]["human_review_count"] == 3
        assert (
            snapshots["graph_scale_method_decision"]["status_counts"][
                "blocked_missing_graph_scale_acceptance_record"
            ]
            == 1
        )
        assert snapshots["source_url_review"]["blocking_count"] == 1
        assert snapshots["source_url_review"]["human_review_count"] == 17
        assert (
            snapshots["source_url_review"]["status_counts"]["network_error"]
            == 1
        )
        assert snapshots["source_context_cache_request"]["row_count"] == 4
        assert snapshots["source_context_cache_request"]["blocking_count"] == 4
        assert (
            snapshots["source_context_cache_request"]["status_counts"][
                "blocked_missing_context_source_cache"
            ]
            == 4
        )
        assert snapshots["source_context_cache_decision"]["row_count"] == 4
        assert snapshots["source_context_cache_decision"]["blocking_count"] == 4
        assert (
            snapshots["source_context_cache_decision"]["status_counts"][
                "blocked_missing_context_source_cache_or_exclusion_decision"
            ]
            == 4
        )
        assert snapshots["parameter_source_decision"]["row_count"] == 6
        assert snapshots["parameter_source_decision"]["blocking_count"] == 1
        assert snapshots["parameter_source_decision"]["human_review_count"] == 5
        assert (
            snapshots["parameter_source_decision"]["status_counts"][
                "blocked_missing_parameter_source_decision"
            ]
            == 1
        )
        assert snapshots["road_source_decision"]["row_count"] == 5
        assert snapshots["road_source_decision"]["blocking_count"] == 2
        assert snapshots["road_source_decision"]["human_review_count"] == 3
        assert (
            snapshots["road_source_decision"]["status_counts"][
                "blocked_missing_road_source_decision"
            ]
            == 2
        )
        assert snapshots["rail_source_decision"]["row_count"] == 5
        assert snapshots["rail_source_decision"]["blocking_count"] == 3
        assert snapshots["rail_source_decision"]["human_review_count"] == 2
        assert (
            snapshots["rail_source_decision"]["status_counts"][
                "blocked_missing_rail_source_decision"
            ]
            == 3
        )
        assert (
            snapshots["formal_acceptance_blocker_queue"]["blocking_count"]
            == 15
        )
        assert (
            snapshots["formal_acceptance_blocker_queue"]["human_review_count"]
            == 15
        )
        assert (
            snapshots["formal_acceptance_pre_review"]["blocking_count"]
            == 12
        )
        assert (
            snapshots["formal_acceptance_pre_review"]["human_review_count"]
            == 12
        )
        assert snapshots["agent_review_path_audit"]["row_count"] == 12
        assert snapshots["agent_review_path_audit"]["blocking_count"] == 0
        assert (
            snapshots["agent_review_path_audit"]["status_counts"][
                "missing_formal_target"
            ]
            == 36
        )
        assert snapshots["tracked_artifact_audit"]["blocking_count"] == 2
        assert (
            snapshots["tracked_artifact_audit"]["status_counts"][
                "generated_review_artifact"
            ]
            == 2
        )
        assert snapshots["current_goal_completion_audit"]["row_count"] == 15
        assert snapshots["current_goal_completion_audit"]["blocking_count"] == 12
        assert (
            snapshots["current_goal_completion_audit"]["status_counts"][
                "missing_acceptance_artifact"
            ]
            == 12
        )
        assert snapshots["publication_readiness_audit"]["row_count"] == 7
        assert snapshots["publication_readiness_audit"]["blocking_count"] == 6
        assert snapshots["publication_readiness_audit"]["status_counts"]["ready"] == 1
        assert (root / "acceptance_orchestration_manifest.json").exists()
        index_path = root / "review_packets" / "acceptance_review_index.md"
        assert index_path.exists()
        index_text = index_path.read_text(encoding="utf-8")
        assert "Source Provenance Priority Snapshot" in index_text
        assert "Blocking context-only sources: 4" in index_text
        assert "cache or exclude context-only sources" in index_text
        assert "Review Packet Status Snapshots" in index_text
        assert "`Validation Benchmark Readiness`" in index_text
        assert "`Validation Benchmark Decision`" in index_text
        assert "`Experiment Design Decision`" in index_text
        assert "`Pilot Region Decision`" in index_text
        assert "`Graph-Scale Result Comparison`" in index_text
        assert "`Graph-Scale Method Decision`" in index_text
        assert "`Source URL Review`" in index_text
        assert "`Source Context Cache Requests`" in index_text
        assert "`Road Source Decisions`" in index_text
        assert "`Rail Source Decisions`" in index_text
        assert "`Formal Acceptance Blocker Queue`" in index_text
        assert "`Formal Acceptance Pre-Review`" in index_text
        assert "`Agent Review Path Audit`" in index_text
        assert "`Tracked Artifact Audit`" in index_text
        assert "`Current Goal Completion Audit`" in index_text
        assert "`Publication Readiness Audit`" in index_text
        assert "candidate_worsens=24" in index_text
        assert "blocked_missing_pilot_acceptance_record=1" in index_text
        assert "needs_human_review_reduced_corridor_warning_policy=1" in index_text
        assert "network_error=1" in index_text
        assert "blocked_missing_context_source_cache=4" in index_text
        assert "blocked_missing_road_source_decision=2" in index_text
        assert "blocked_missing_rail_source_decision=3" in index_text
        assert "needs_human_review_cached_osrm_scope_policy=1" in index_text
        assert "needs_human_review_scenario_policy_seed_design=1" in index_text
        assert "blocked_missing_evidence=8" in index_text
        assert "missing_formal_target=36" in index_text
        assert "generated_review_artifact=2" in index_text
        assert "missing_acceptance_artifact=12" in index_text
        assert "parameter evidence: weak assumptions remain" in index_text
        assert "blocked_missing_validation_acceptance_record=1" in index_text
        assert "blocked_missing_experiment_acceptance_record=1" in index_text

        first_record_path = Path(manifest["records"][0]["record_path"])
        if not first_record_path.is_absolute():
            first_record_path = ROOT / first_record_path
        # The manifest stores project-relative paths for normal runs. In this
        # tempfile run, validate by opening the real file directly from output_dir.
        generated_records = sorted((root / "agent_reviews").glob("*.json"))
        assert generated_records
        loaded = load_acceptance_record(generated_records[0])
        assert loaded.status in {"blocked", "needs_human_review"}
        assert loaded.review_packet_paths


def test_acceptance_orchestration_summary_reports_absent_manifest() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        summary = summarize_acceptance_orchestration_manifest(
            Path(tmpdir) / "missing.json"
        )
    assert summary["manifest_present"] is False
    assert summary["remaining_blockers"]


if __name__ == "__main__":
    test_acceptance_orchestration_defines_required_review_agents()
    test_review_agents_point_at_current_readiness_packets()
    test_default_review_status_snapshots_cover_formal_workflow()
    test_acceptance_orchestration_blocks_nonready_gate_without_completion()
    test_acceptance_orchestration_writes_records_and_manifest()
    test_acceptance_orchestration_summary_reports_absent_manifest()
    print("PASS: acceptance orchestration")
