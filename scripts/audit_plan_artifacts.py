"""Audit current plan-gate artifacts without claiming final-study acceptance."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.parameter_audit import audit_shipped_parameter_evidence  # noqa: E402
from src.realworld.pilot_privacy_review_packet import (  # noqa: E402
    DEFAULT_PILOT_PRIVACY_REVIEW_DOC_PATH,
    DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
    DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH,
)
from src.realworld.pilot_region_decision_packet import (  # noqa: E402
    DEFAULT_PILOT_REGION_DECISION_DOC_PATH,
    DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH,
    DEFAULT_PILOT_REGION_DECISION_PACKET_PATH,
)
from src.realworld.acceptance_orchestration import (  # noqa: E402
    DEFAULT_AGENT_REVIEW_DIR,
    REVIEW_AGENT_DEFINITIONS,
    summarize_acceptance_orchestration_manifest,
)
from src.realworld.acceptance_decision_templates import (  # noqa: E402
    DEFAULT_ACCEPTANCE_TEMPLATE_DOC_PATH,
    DEFAULT_ACCEPTANCE_TEMPLATE_MANIFEST_PATH,
    DEFAULT_PARAMETER_ACCEPTANCE_TEMPLATE_PATH,
    summarize_acceptance_decision_templates,
)
from src.realworld.acceptance_blocker_queue import (  # noqa: E402
    DEFAULT_BLOCKER_QUEUE_DOC_PATH,
    DEFAULT_BLOCKER_QUEUE_MANIFEST_PATH,
    DEFAULT_BLOCKER_QUEUE_PATH,
    summarize_acceptance_blocker_queue,
)
from src.realworld.acceptance_task_assignments import (  # noqa: E402
    DEFAULT_TASK_ASSIGNMENT_DOC_PATH,
    DEFAULT_TASK_ASSIGNMENT_MANIFEST_PATH,
    DEFAULT_TASK_ASSIGNMENT_PATH,
    summarize_acceptance_task_assignments,
)
from src.realworld.acceptance_records import load_acceptance_record  # noqa: E402
from src.realworld.agent_review_path_audit import (  # noqa: E402
    DEFAULT_AGENT_REVIEW_PATH_AUDIT_DOC,
    DEFAULT_AGENT_REVIEW_PATH_AUDIT_MANIFEST,
    audit_agent_review_paths,
)
from src.realworld.review_package_path_audit import (  # noqa: E402
    DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_DOC,
    DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_MANIFEST,
    audit_review_package_paths,
)
from src.realworld.review_package_handoff import (  # noqa: E402
    DEFAULT_EXPERT_REVIEW_HANDOFF_DOC,
    build_expert_review_handoff_summary,
)
from src.realworld.claim_alignment_review_packet import (  # noqa: E402
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_DOC_PATH,
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
)
from src.realworld.claim_language_guard import (  # noqa: E402
    DEFAULT_CLAIM_LANGUAGE_GUARD_DOC_PATH,
    DEFAULT_CLAIM_LANGUAGE_GUARD_MANIFEST_PATH,
    DEFAULT_CLAIM_LANGUAGE_GUARD_PATH,
    summarize_claim_language_guard,
)
from src.realworld.artifact_invalidation_matrix import (  # noqa: E402
    DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION,
    DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_TEMPLATE,
    DEFAULT_ARTIFACT_INVALIDATION_CSV,
    DEFAULT_ARTIFACT_INVALIDATION_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_TEMPLATE,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
    artifact_invalidation_blocks_phase9,
    summarize_artifact_invalidation_action_batch_inspection_manifest,
)
from src.realworld.figure_table_review_packet import (  # noqa: E402
    DEFAULT_FIGURE_TABLE_REVIEW_DOC_PATH,
    DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
)
from src.realworld.manuscript_report_decision_packet import (  # noqa: E402
    DEFAULT_MANUSCRIPT_REPORT_DECISION_DOC_PATH,
    DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH,
    DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH,
)
from src.realworld.experiment_package_review_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_DOC_PATH,
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
)
from src.realworld.experiment_design_decision_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_DESIGN_DECISION_DOC_PATH,
    DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH,
)
from src.realworld.experiment_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH,
)
from src.realworld.experiment_statistical_plan import (  # noqa: E402
    DEFAULT_EXPERIMENT_STATISTICAL_PLAN_DOC_PATH,
    DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH,
)
from src.realworld.deterministic_rerun_audit import (  # noqa: E402
    DEFAULT_DETERMINISTIC_RERUN_AUDIT_CSV,
    DEFAULT_DETERMINISTIC_RERUN_AUDIT_DOC,
    DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST,
)
from src.realworld.rail_evidence import (  # noqa: E402
    DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
    load_rail_service_evidence,
    summarize_rail_service_evidence,
)
from src.realworld.rail_station_binding import (  # noqa: E402
    DEFAULT_RAIL_STATION_BINDING_PATH,
    load_rail_station_bindings,
    summarize_rail_station_bindings,
)
from src.realworld.road_evidence import audit_cached_road_evidence  # noqa: E402
from src.realworld.road_evidence_diagnostics import (  # noqa: E402
    audit_cached_road_evidence_diagnostics,
)
from src.realworld.road_override_audit import (  # noqa: E402
    audit_road_class_override_application,
    audit_road_class_override_evidence,
)
from src.realworld.final_study_readiness import audit_final_study_readiness  # noqa: E402
from src.realworld.formal_acceptance_guard import (  # noqa: E402
    audit_formal_acceptance_artifacts,
)
from src.realworld.formal_acceptance_package import (  # noqa: E402
    DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_DOC_PATH,
    DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_MANIFEST_PATH,
    build_formal_acceptance_package_summary,
)
from src.realworld.formal_acceptance_evidence_matrix import (  # noqa: E402
    DEFAULT_EVIDENCE_MATRIX_DOC_PATH,
    DEFAULT_EVIDENCE_MATRIX_MANIFEST_PATH,
    DEFAULT_EVIDENCE_MATRIX_PATH,
    summarize_formal_acceptance_evidence_matrix,
)
from src.realworld.formal_acceptance_pre_review import (  # noqa: E402
    DEFAULT_PRE_REVIEW_DOC_PATH,
    DEFAULT_PRE_REVIEW_MANIFEST_PATH,
    summarize_formal_acceptance_pre_review,
)
from src.realworld.formal_evidence_path_audit import (  # noqa: E402
    DEFAULT_FORMAL_EVIDENCE_PATH_AUDIT_DOC,
    DEFAULT_FORMAL_EVIDENCE_PATH_AUDIT_MANIFEST,
    audit_formal_evidence_paths,
)
from src.realworld.sensitivity_diagnostics import (  # noqa: E402
    audit_morris_sensitivity_diagnostics,
)
from src.realworld.reproducibility_review_packet import (  # noqa: E402
    DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH,
    DEFAULT_REPRODUCIBILITY_REVIEW_PACKET_PATH,
)
from src.realworld.reproducibility_decision_packet import (  # noqa: E402
    DEFAULT_REPRODUCIBILITY_DECISION_DOC_PATH,
    DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH,
    DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH,
)
from src.realworld.final_audit_decision_packet import (  # noqa: E402
    DEFAULT_FINAL_AUDIT_DECISION_DOC_PATH,
    DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH,
    DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH,
)
from src.realworld.rail_fetch_readiness_packet import (  # noqa: E402
    DEFAULT_RAIL_FETCH_READINESS_DOC_PATH,
    DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
)
from src.realworld.rail_evidence_priority_packet import (  # noqa: E402
    DEFAULT_RAIL_EVIDENCE_PRIORITY_DOC_PATH,
    DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
)
from src.realworld.rail_source_decision_packet import (  # noqa: E402
    DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_DOC_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_MANIFEST_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_DOC_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
)
from src.realworld.rail_source_decision_recommendation_packet import (  # noqa: E402
    DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_DOC_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_MANIFEST_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_PACKET_PATH,
)
from src.realworld.road_source_readiness_packet import (  # noqa: E402
    DEFAULT_ROAD_SOURCE_READINESS_DOC_PATH,
    DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
)
from src.realworld.road_source_decision_packet import (  # noqa: E402
    DEFAULT_ROAD_SOURCE_DECISION_DOC_PATH,
    DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_ROAD_SOURCE_DECISION_PACKET_PATH,
)
from src.realworld.road_evidence_priority_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_PRIORITY_DOC_PATH,
    DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
)
from src.realworld.parameter_source_readiness_packet import (  # noqa: E402
    DEFAULT_PARAMETER_SOURCE_READINESS_DOC_PATH,
    DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
)
from src.realworld.parameter_source_decision_packet import (  # noqa: E402
    DEFAULT_PARAMETER_SOURCE_DECISION_DOC_PATH,
    DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH,
)
from src.realworld.parameter_evidence_priority_packet import (  # noqa: E402
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_DOC_PATH,
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
)
from src.realworld.graph_scale_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH,
)
from src.realworld.graph_scale_method_decision_packet import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_METHOD_DECISION_DOC_PATH,
    DEFAULT_GRAPH_SCALE_METHOD_DECISION_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_METHOD_DECISION_PACKET_PATH,
)
from src.realworld.graph_scale_manifest_audit import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_DOC_PATH,
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
)
from src.realworld.goal_completion_audit import (  # noqa: E402
    DEFAULT_GOAL_COMPLETION_MANIFEST_PATH,
)
from src.realworld.publication_readiness import (  # noqa: E402
    DEFAULT_PUBLICATION_READINESS_DOC_PATH,
    DEFAULT_PUBLICATION_READINESS_MANIFEST_PATH,
    audit_publication_readiness,
    _summarize_rail_bounded_treatment_audit,
)
from src.realworld.rail_bounded_treatment_audit import (  # noqa: E402
    DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_DOC_PATH,
    DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH,
)
from src.realworld.rail_transit_stress_profile_packet import (  # noqa: E402
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_DOC_PATH,
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH,
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH,
)
from src.realworld.demand_fleet_behavior_profiles import (  # noqa: E402
    DEFAULT_BEHAVIOR_PROFILE_PATH,
    DEFAULT_DEMAND_PROFILE_PATH,
    DEFAULT_FLEET_PROFILE_PATH,
    DEFAULT_PROFILE_DOC_PATH,
    DEFAULT_PROFILE_MANIFEST_PATH,
)
from src.realworld.disruption_scenarios import (  # noqa: E402
    DEFAULT_SCENARIO_DOC_PATH,
    DEFAULT_SCENARIO_MANIFEST_PATH,
    DEFAULT_SCENARIO_PATH,
)
from src.realworld.full_graph_runtime_readiness_packet import (  # noqa: E402
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_DOC_PATH,
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH,
    DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH,
)
from src.realworld.validation_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_VALIDATION_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH,
)
from src.realworld.validation_benchmark_readiness_packet import (  # noqa: E402
    DEFAULT_VALIDATION_BENCHMARK_READINESS_DOC_PATH,
    DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH,
)
from src.realworld.validation_benchmark_decision_packet import (  # noqa: E402
    DEFAULT_VALIDATION_BENCHMARK_DECISION_DOC_PATH,
    DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH,
)
from src.realworld.integrated_evidence_review_packet import (  # noqa: E402
    DEFAULT_INTEGRATED_EVIDENCE_REVIEW_DOC_PATH,
    DEFAULT_INTEGRATED_EVIDENCE_REVIEW_MANIFEST_PATH,
    DEFAULT_INTEGRATED_EVIDENCE_REVIEW_PACKET_PATH,
)
from src.realworld.sensitivity_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH,
)
from src.realworld.sensitivity_index_review_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_INDEX_REVIEW_DOC_PATH,
    DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH,
)
from src.realworld.sensitivity_method_decision_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_METHOD_DECISION_DOC_PATH,
    DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH,
)
from src.realworld.reproducibility_smoke import (  # noqa: E402
    summarize_reproducibility_smoke,
)
from src.realworld.source_provenance import (  # noqa: E402
    summarize_source_provenance_manifest,
)
from src.realworld.source_license_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_LICENSE_REVIEW_DOC_PATH,
    DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
)
from src.realworld.source_url_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REVIEW_DOC_PATH,
    DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
)
from src.realworld.source_url_remediation_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REMEDIATION_DOC_PATH,
    DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
)
from src.realworld.source_provenance_priority_packet import (  # noqa: E402
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_DOC_PATH,
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
)
from src.realworld.source_context_cache_request_packet import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_DOC_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
)
from src.realworld.source_context_cache_decision_packet import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_DOC_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH,
)
from src.realworld.source_provenance_decision_packet import (  # noqa: E402
    DEFAULT_SOURCE_PROVENANCE_DECISION_DOC_PATH,
    DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH,
    DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH,
)
from src.realworld.tracked_artifact_audit import (  # noqa: E402
    DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_CSV,
    DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_DOC,
    DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_MANIFEST,
    DEFAULT_TRACKED_ARTIFACT_AUDIT_CSV,
    DEFAULT_TRACKED_ARTIFACT_AUDIT_DOC,
    DEFAULT_TRACKED_ARTIFACT_AUDIT_MANIFEST,
    build_dirty_worktree_classification_rows,
    summarize_dirty_worktree_classification,
    summarize_tracked_artifact_audit,
)
from src.realworld.phase_gate_ledger import (  # noqa: E402
    DEFAULT_PHASE_GATE_LEDGER_AUDIT_DOC,
    DEFAULT_PHASE_GATE_LEDGER_AUDIT_MANIFEST,
    DEFAULT_PHASE_GATE_LEDGER_SCHEMA,
    audit_phase_gate_ledgers,
    summarize_phase_gate_ledger_audit,
)
from src.realworld.gpu_ml_runtime import (  # noqa: E402
    DEFAULT_GPU_ML_RUNTIME_DOC,
    DEFAULT_GPU_ML_RUNTIME_LOG,
    DEFAULT_GPU_ML_RUNTIME_MANIFEST,
    GPU_ML_RUNTIME_SCOPE,
)

SCAFFOLD_VERDICT = (
    "executable_quasi_real_scaffold_not_final_calibrated_study"
)


@dataclass(frozen=True)
class CsvExpectation:
    """Expected row count for a generated CSV artifact."""

    label: str
    path: Path
    expected_rows: int | None = None


@dataclass(frozen=True)
class JsonExpectation:
    """Expected JSON artifact."""

    label: str
    path: Path


CSV_EXPECTATIONS = (
    CsvExpectation(
        "rail_service_evidence",
        ROOT / "data" / "parameters" / "rail_service_evidence.csv",
        1,
    ),
    CsvExpectation(
        "rail_station_bindings",
        ROOT / "data" / "parameters" / "rail_station_bindings.csv",
        4,
    ),
    CsvExpectation(
        "rail_evidence_review_packet",
        ROOT / "data" / "parameters" / "rail_evidence_review_packet.csv",
        12,
    ),
    CsvExpectation(
        "rail_timing_source_request_packet",
        ROOT / "data" / "rail" / "rail_timing_source_request_packet.csv",
        6,
    ),
    CsvExpectation(
        "rail_fetch_readiness_packet",
        DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
        6,
    ),
    CsvExpectation(
        "rail_evidence_priority_packet",
        DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "rail_source_decision_packet",
        DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
        6,
    ),
    CsvExpectation(
        "rail_source_decision_action_ledger_template",
        DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_PATH,
        6,
    ),
    CsvExpectation(
        "rail_source_decision_recommendation_packet",
        DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_PACKET_PATH,
        6,
    ),
    CsvExpectation(
        "rail_transit_stress_profile_packet",
        DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH,
        6,
    ),
    CsvExpectation(
        "demand_profiles",
        DEFAULT_DEMAND_PROFILE_PATH,
        2,
    ),
    CsvExpectation(
        "fleet_profiles",
        DEFAULT_FLEET_PROFILE_PATH,
        6,
    ),
    CsvExpectation(
        "behavior_profiles",
        DEFAULT_BEHAVIOR_PROFILE_PATH,
        6,
    ),
    CsvExpectation(
        "disruption_scenarios",
        DEFAULT_SCENARIO_PATH,
        8,
    ),
    CsvExpectation(
        "road_class_overrides_draft",
        ROOT / "data" / "parameters" / "road_class_overrides_draft.csv",
        10,
    ),
    CsvExpectation(
        "road_speed_evidence_candidates",
        ROOT / "data" / "parameters" / "road_speed_evidence_candidates.csv",
        10,
    ),
    CsvExpectation(
        "road_capacity_evidence_candidates",
        ROOT / "data" / "parameters" / "road_capacity_evidence_candidates.csv",
        10,
    ),
    CsvExpectation(
        "road_evidence_review_packet",
        ROOT / "data" / "parameters" / "road_evidence_review_packet.csv",
        10,
    ),
    CsvExpectation(
        "road_source_readiness_packet",
        DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
        5,
    ),
    CsvExpectation(
        "road_source_decision_packet",
        DEFAULT_ROAD_SOURCE_DECISION_PACKET_PATH,
        5,
    ),
    CsvExpectation(
        "road_evidence_priority_packet",
        DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
        11,
    ),
    CsvExpectation(
        "road_evidence_source_request_packet",
        ROOT / "data" / "road" / "road_evidence_source_request_packet.csv",
        5,
    ),
    CsvExpectation(
        "parameter_evidence_review_packet",
        ROOT / "data" / "parameters" / "parameter_evidence_review_packet.csv",
        29,
    ),
    CsvExpectation(
        "parameter_evidence_source_request_packet",
        ROOT
        / "data"
        / "parameters"
        / "parameter_evidence_source_request_packet.csv",
        7,
    ),
    CsvExpectation(
        "parameter_source_readiness_packet",
        DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "parameter_source_decision_packet",
        DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "parameter_evidence_priority_packet",
        DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "parameter_acceptance_template",
        DEFAULT_PARAMETER_ACCEPTANCE_TEMPLATE_PATH,
        25,
    ),
    CsvExpectation(
        "formal_acceptance_blocker_queue",
        DEFAULT_BLOCKER_QUEUE_PATH,
        15,
    ),
    CsvExpectation(
        "acceptance_task_assignments",
        DEFAULT_TASK_ASSIGNMENT_PATH,
        15,
    ),
    CsvExpectation(
        "formal_acceptance_evidence_matrix",
        DEFAULT_EVIDENCE_MATRIX_PATH,
        12,
    ),
    CsvExpectation(
        "tracked_artifact_audit",
        DEFAULT_TRACKED_ARTIFACT_AUDIT_CSV,
        None,
    ),
    CsvExpectation(
        "dirty_worktree_classification",
        DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_CSV,
        None,
    ),
    CsvExpectation(
        "source_license_review_packet",
        DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
        11,
    ),
    CsvExpectation(
        "source_url_review_packet",
        DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
        None,
    ),
    CsvExpectation(
        "source_url_remediation_packet",
        DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
        None,
    ),
    CsvExpectation(
        "source_provenance_priority_packet",
        DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
        11,
    ),
    CsvExpectation(
        "source_context_cache_request_packet",
        DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
        3,
    ),
    CsvExpectation(
        "source_context_cache_decision_packet",
        DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH,
        3,
    ),
    CsvExpectation(
        "source_provenance_decision_packet",
        DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "pilot_privacy_review_packet",
        DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "pilot_region_decision_packet",
        DEFAULT_PILOT_REGION_DECISION_PACKET_PATH,
        6,
    ),
    CsvExpectation(
        "experiment_package_review_packet",
        DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
        9,
    ),
    CsvExpectation(
        "experiment_strategy_readiness_packet",
        DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH,
        9,
    ),
    CsvExpectation(
        "experiment_design_decision_packet",
        DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH,
        8,
    ),
    CsvExpectation(
        "deterministic_rerun_audit",
        DEFAULT_DETERMINISTIC_RERUN_AUDIT_CSV,
        7,
    ),
    CsvExpectation(
        "claim_alignment_review_packet",
        DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
        None,
    ),
    CsvExpectation(
        "claim_language_guard",
        DEFAULT_CLAIM_LANGUAGE_GUARD_PATH,
        None,
    ),
    CsvExpectation(
        "artifact_invalidation_matrix",
        DEFAULT_ARTIFACT_INVALIDATION_CSV,
        51,
    ),
    CsvExpectation(
        "artifact_invalidation_closeout_template",
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_TEMPLATE,
        51,
    ),
    CsvExpectation(
        "artifact_invalidation_closeout_action_queue",
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE,
        51,
    ),
    CsvExpectation(
        "artifact_invalidation_action_batch_inspection",
        DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION,
        51,
    ),
    CsvExpectation(
        "artifact_invalidation_closeout_readiness_audit",
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT,
        51,
    ),
    CsvExpectation(
        "artifact_invalidation_quarantine_closeout_template",
        DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_TEMPLATE,
        6,
    ),
    CsvExpectation(
        "artifact_invalidation_quarantine_scope_audit",
        DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT,
        None,
    ),
    CsvExpectation(
        "artifact_invalidation_quarantine_non_evidence_index",
        DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX,
        None,
    ),
    CsvExpectation(
        "artifact_invalidation_quarantine_non_evidence_transfer_packet",
        DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET,
        6,
    ),
    CsvExpectation(
        "figure_table_review_packet",
        DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
        8,
    ),
    CsvExpectation(
        "manuscript_report_decision_packet",
        DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "pilot_sample_results",
        ROOT / "results" / "realworld_pilot" / "pilot_sample_results.csv",
        32,
    ),
    CsvExpectation(
        "pilot_staged_results",
        ROOT / "results" / "realworld_pilot" / "pilot_staged_results.csv",
        315,
    ),
    CsvExpectation(
        "pilot_multi_corridor_results",
        ROOT / "results" / "realworld_pilot" / "pilot_multi_corridor_results.csv",
        32,
    ),
    CsvExpectation(
        "pilot_multi_corridor_summary",
        ROOT / "results" / "realworld_pilot" / "pilot_multi_corridor_summary.csv",
        16,
    ),
    CsvExpectation(
        "pilot_multi_corridor_full_results",
        ROOT
        / "results"
        / "realworld_pilot"
        / "pilot_multi_corridor_full_results.csv",
        1890,
    ),
    CsvExpectation(
        "pilot_multi_corridor_full_summary",
        ROOT
        / "results"
        / "realworld_pilot"
        / "pilot_multi_corridor_full_summary.csv",
        63,
    ),
    CsvExpectation(
        "pilot_full_results",
        ROOT / "results" / "realworld_pilot" / "pilot_full_results.csv",
        1890,
    ),
    CsvExpectation(
        "pilot_full_summary",
        ROOT / "results" / "realworld_pilot" / "pilot_full_summary.csv",
        63,
    ),
    CsvExpectation(
        "morris_results",
        ROOT / "results" / "realworld_pilot" / "morris_results.csv",
        4320,
    ),
    CsvExpectation(
        "morris_summary",
        ROOT / "results" / "realworld_pilot" / "morris_summary.csv",
        7056,
    ),
    CsvExpectation(
        "sensitivity_review_packet",
        ROOT / "data" / "validation" / "sensitivity_review_packet.csv",
        6,
    ),
    CsvExpectation(
        "sensitivity_index_review_packet",
        DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "sensitivity_strategy_readiness_packet",
        DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "sensitivity_method_decision_packet",
        DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "main_result_table",
        ROOT / "results" / "realworld_pilot" / "tables" / "main_result_table.csv",
        63,
    ),
    CsvExpectation(
        "sensitivity_result_table",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "sensitivity_result_table.csv",
        98,
    ),
    CsvExpectation(
        "bottleneck_attribution_table",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "bottleneck_attribution_table.csv",
        63,
    ),
    CsvExpectation(
        "policy_regime_table",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "policy_regime_table.csv",
        27,
    ),
    CsvExpectation(
        "pilot_full_metric_ci",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "pilot_full_metric_ci.csv",
        819,
    ),
    CsvExpectation(
        "pilot_full_paired_delta_ci",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "pilot_full_paired_delta_ci.csv",
        702,
    ),
    CsvExpectation(
        "pilot_multi_corridor_metric_ci",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "pilot_multi_corridor_metric_ci.csv",
        208,
    ),
    CsvExpectation(
        "pilot_multi_corridor_paired_delta_ci",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "pilot_multi_corridor_paired_delta_ci.csv",
        156,
    ),
    CsvExpectation(
        "pilot_multi_corridor_full_metric_ci",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "pilot_multi_corridor_full_metric_ci.csv",
        819,
    ),
    CsvExpectation(
        "pilot_multi_corridor_full_paired_delta_ci",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "pilot_multi_corridor_full_paired_delta_ci.csv",
        702,
    ),
    CsvExpectation(
        "accessibility_loss",
        ROOT / "data" / "validation" / "accessibility_loss.csv",
        127,
    ),
    CsvExpectation(
        "canonical_route_road_evidence_exposure",
        ROOT
        / "data"
        / "validation"
        / "canonical_route_road_evidence_exposure.csv",
        76,
    ),
    CsvExpectation(
        "validation_review_packet",
        ROOT / "data" / "validation" / "validation_review_packet.csv",
        7,
    ),
    CsvExpectation(
        "validation_strategy_readiness_packet",
        DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "validation_benchmark_readiness_packet",
        DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH,
        4,
    ),
    CsvExpectation(
        "validation_benchmark_decision_packet",
        DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH,
        6,
    ),
    CsvExpectation(
        "integrated_evidence_review_packet",
        DEFAULT_INTEGRATED_EVIDENCE_REVIEW_PACKET_PATH,
        5,
    ),
    CsvExpectation(
        "reproducibility_review_packet",
        DEFAULT_REPRODUCIBILITY_REVIEW_PACKET_PATH,
        8,
    ),
    CsvExpectation(
        "reproducibility_decision_packet",
        DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "final_audit_decision_packet",
        DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "graph_scale_route_comparison",
        ROOT / "data" / "validation" / "graph_scale_route_comparison.csv",
        3,
    ),
    CsvExpectation(
        "graph_scale_alternate_routes",
        ROOT / "data" / "validation" / "graph_scale_alternate_routes.csv",
        9,
    ),
    CsvExpectation(
        "graph_scale_multi_corridor_routes",
        ROOT / "data" / "validation" / "graph_scale_multi_corridor_routes.csv",
        9,
    ),
    CsvExpectation(
        "graph_scale_review_packet",
        ROOT / "data" / "validation" / "graph_scale_review_packet.csv",
        4,
    ),
    CsvExpectation(
        "graph_scale_strategy_readiness_packet",
        DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH,
        5,
    ),
    CsvExpectation(
        "graph_scale_method_decision_packet",
        DEFAULT_GRAPH_SCALE_METHOD_DECISION_PACKET_PATH,
        7,
    ),
    CsvExpectation(
        "full_graph_runtime_readiness_packet",
        DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH,
        4,
    ),
    CsvExpectation(
        "graph_scale_result_comparison",
        ROOT / "data" / "validation" / "graph_scale_result_comparison.csv",
        819,
    ),
    CsvExpectation(
        "graph_scale_manifest_audit",
        DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
        13,
    ),
)

JSON_EXPECTATIONS = (
    JsonExpectation(
        "pilot_road_cache_manifest",
        ROOT / "data" / "cache" / "pilot_region_road_manifest.json",
    ),
    JsonExpectation(
        "figure_table_manifest",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "figure_table_manifest.json",
    ),
    JsonExpectation(
        "morris_manifest",
        ROOT / "results" / "realworld_pilot" / "morris_manifest.json",
    ),
    JsonExpectation(
        "sensitivity_review_manifest",
        ROOT / "data" / "validation" / "sensitivity_review_manifest.json",
    ),
    JsonExpectation(
        "sensitivity_index_review_manifest",
        DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "sensitivity_strategy_readiness_manifest",
        DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "sensitivity_method_decision_manifest",
        DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "validation_review_manifest",
        ROOT / "data" / "validation" / "validation_review_manifest.json",
    ),
    JsonExpectation(
        "validation_strategy_readiness_manifest",
        DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "validation_benchmark_readiness_manifest",
        DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "validation_benchmark_decision_manifest",
        DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "integrated_evidence_review_manifest",
        DEFAULT_INTEGRATED_EVIDENCE_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "canonical_route_road_evidence_exposure_manifest",
        ROOT
        / "data"
        / "validation"
        / "canonical_route_road_evidence_exposure_manifest.json",
    ),
    JsonExpectation(
        "road_evidence_priority_manifest",
        DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    ),
    JsonExpectation(
        "osrm_route_benchmark_manifest",
        ROOT / "data" / "validation" / "osrm_route_benchmark_manifest.json",
    ),
    JsonExpectation(
        "reproducibility_manifest",
        ROOT / "data" / "manifests" / "reproducibility_manifest.json",
    ),
    JsonExpectation(
        "source_provenance_manifest",
        ROOT / "data" / "manifests" / "source_provenance_manifest.json",
    ),
    JsonExpectation(
        "source_license_review_manifest",
        DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "source_url_review_manifest",
        DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "source_url_remediation_manifest",
        DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "source_provenance_priority_manifest",
        DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    ),
    JsonExpectation(
        "source_context_cache_request_manifest",
        DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    ),
    JsonExpectation(
        "source_context_cache_decision_manifest",
        DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "source_provenance_decision_manifest",
        DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "rail_fetch_readiness_manifest",
        DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "rail_evidence_priority_manifest",
        DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    ),
    JsonExpectation(
        "rail_source_decision_manifest",
        DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "rail_source_decision_action_ledger_template_manifest",
        DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_MANIFEST_PATH,
    ),
    JsonExpectation(
        "rail_source_decision_recommendation_manifest",
        DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "rail_transit_stress_profile_manifest",
        DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH,
    ),
    JsonExpectation(
        "demand_fleet_behavior_profile_manifest",
        DEFAULT_PROFILE_MANIFEST_PATH,
    ),
    JsonExpectation(
        "disruption_scenarios_manifest",
        DEFAULT_SCENARIO_MANIFEST_PATH,
    ),
    JsonExpectation(
        "rail_bounded_treatment_audit",
        DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH,
    ),
    JsonExpectation(
        "road_source_readiness_manifest",
        DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "road_source_decision_manifest",
        DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "parameter_source_readiness_manifest",
        DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "parameter_source_decision_manifest",
        DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "parameter_evidence_priority_manifest",
        DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    ),
    JsonExpectation(
        "pilot_privacy_review_manifest",
        DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "pilot_region_decision_manifest",
        DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "experiment_package_review_manifest",
        DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "experiment_strategy_readiness_manifest",
        DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "experiment_design_decision_manifest",
        DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "experiment_statistical_analysis_plan",
        DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH,
    ),
    JsonExpectation(
        "deterministic_rerun_audit_manifest",
        DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST,
    ),
    JsonExpectation(
        "claim_alignment_review_manifest",
        DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "claim_language_guard_manifest",
        DEFAULT_CLAIM_LANGUAGE_GUARD_MANIFEST_PATH,
    ),
    JsonExpectation(
        "artifact_invalidation_matrix_manifest",
        DEFAULT_ARTIFACT_INVALIDATION_MANIFEST,
    ),
    JsonExpectation(
        "artifact_invalidation_closeout_manifest",
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST,
    ),
    JsonExpectation(
        "artifact_invalidation_closeout_action_queue_manifest",
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_MANIFEST,
    ),
    JsonExpectation(
        "artifact_invalidation_action_batch_inspection_manifest",
        DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_MANIFEST,
    ),
    JsonExpectation(
        "artifact_invalidation_closeout_readiness_audit_manifest",
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_MANIFEST,
    ),
    JsonExpectation(
        "artifact_invalidation_quarantine_closeout_manifest",
        DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_MANIFEST,
    ),
    JsonExpectation(
        "artifact_invalidation_quarantine_scope_audit_manifest",
        DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
    ),
    JsonExpectation(
        "artifact_invalidation_quarantine_non_evidence_index_manifest",
        DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_MANIFEST,
    ),
    JsonExpectation(
        "artifact_invalidation_quarantine_non_evidence_transfer_manifest",
        DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
    ),
    JsonExpectation(
        "figure_table_review_manifest",
        DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "manuscript_report_decision_manifest",
        DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "road_speed_evidence_manifest",
        ROOT / "data" / "parameters" / "road_speed_evidence_manifest.json",
    ),
    JsonExpectation(
        "road_capacity_evidence_manifest",
        ROOT / "data" / "parameters" / "road_capacity_evidence_manifest.json",
    ),
    JsonExpectation(
        "road_evidence_review_manifest",
        ROOT / "data" / "parameters" / "road_evidence_review_manifest.json",
    ),
    JsonExpectation(
        "road_evidence_source_request_manifest",
        ROOT / "data" / "road" / "road_evidence_source_request_manifest.json",
    ),
    JsonExpectation(
        "rail_evidence_review_manifest",
        ROOT / "data" / "parameters" / "rail_evidence_review_manifest.json",
    ),
    JsonExpectation(
        "rail_timing_source_request_manifest",
        ROOT / "data" / "rail" / "rail_timing_source_request_manifest.json",
    ),
    JsonExpectation(
        "parameter_evidence_review_manifest",
        ROOT / "data" / "parameters" / "parameter_evidence_review_manifest.json",
    ),
    JsonExpectation(
        "parameter_evidence_source_request_manifest",
        ROOT
        / "data"
        / "parameters"
        / "parameter_evidence_source_request_manifest.json",
    ),
    JsonExpectation(
        "pilot_full_statistics_manifest",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "pilot_full_statistics_manifest.json",
    ),
    JsonExpectation(
        "pilot_multi_corridor_statistics_manifest",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "pilot_multi_corridor_statistics_manifest.json",
    ),
    JsonExpectation(
        "pilot_multi_corridor_full_statistics_manifest",
        ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "pilot_multi_corridor_full_statistics_manifest.json",
    ),
    JsonExpectation(
        "graph_scale_review_manifest",
        ROOT / "data" / "validation" / "graph_scale_review_manifest.json",
    ),
    JsonExpectation(
        "graph_scale_strategy_readiness_manifest",
        DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "graph_scale_method_decision_manifest",
        DEFAULT_GRAPH_SCALE_METHOD_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "full_graph_smoke_manifest",
        DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH,
    ),
    JsonExpectation(
        "full_graph_runtime_readiness_manifest",
        DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "graph_scale_result_comparison_manifest",
        ROOT
        / "data"
        / "validation"
        / "graph_scale_result_comparison_manifest.json",
    ),
    JsonExpectation(
        "graph_scale_manifest_audit_manifest",
        DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH,
    ),
    JsonExpectation(
        "acceptance_orchestration_manifest",
        ROOT / "data" / "manifests" / "acceptance_orchestration_manifest.json",
    ),
    JsonExpectation(
        "acceptance_review_agents",
        ROOT / "agents" / "acceptance_review_agents.json",
    ),
    JsonExpectation(
        "acceptance_record_schema",
        ROOT / "schemas" / "acceptance_record.schema.json",
    ),
    JsonExpectation(
        "reproducibility_review_manifest",
        DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "reproducibility_decision_manifest",
        DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "final_audit_decision_manifest",
        DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "acceptance_decision_template_manifest",
        DEFAULT_ACCEPTANCE_TEMPLATE_MANIFEST_PATH,
    ),
    JsonExpectation(
        "formal_acceptance_package_manifest",
        DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_MANIFEST_PATH,
    ),
    JsonExpectation(
        "formal_evidence_path_audit",
        DEFAULT_FORMAL_EVIDENCE_PATH_AUDIT_MANIFEST,
    ),
    JsonExpectation(
        "formal_acceptance_blocker_queue_manifest",
        DEFAULT_BLOCKER_QUEUE_MANIFEST_PATH,
    ),
    JsonExpectation(
        "acceptance_task_assignments_manifest",
        DEFAULT_TASK_ASSIGNMENT_MANIFEST_PATH,
    ),
    JsonExpectation(
        "formal_acceptance_evidence_matrix_manifest",
        DEFAULT_EVIDENCE_MATRIX_MANIFEST_PATH,
    ),
    JsonExpectation(
        "formal_acceptance_pre_review_manifest",
        DEFAULT_PRE_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "agent_review_path_audit",
        DEFAULT_AGENT_REVIEW_PATH_AUDIT_MANIFEST,
    ),
    JsonExpectation(
        "review_package_path_audit",
        DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_MANIFEST,
    ),
    JsonExpectation(
        "tracked_artifact_audit_manifest",
        DEFAULT_TRACKED_ARTIFACT_AUDIT_MANIFEST,
    ),
    JsonExpectation(
        "dirty_worktree_classification_manifest",
        DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_MANIFEST,
    ),
    JsonExpectation(
        "phase_gate_ledger_schema",
        DEFAULT_PHASE_GATE_LEDGER_SCHEMA,
    ),
    JsonExpectation(
        "phase_gate_ledger_audit_manifest",
        DEFAULT_PHASE_GATE_LEDGER_AUDIT_MANIFEST,
    ),
    JsonExpectation(
        "gpu_ml_runtime_manifest",
        DEFAULT_GPU_ML_RUNTIME_MANIFEST,
    ),
    JsonExpectation(
        "current_goal_completion_audit_manifest",
        DEFAULT_GOAL_COMPLETION_MANIFEST_PATH,
    ),
    JsonExpectation(
        "publication_readiness_audit",
        DEFAULT_PUBLICATION_READINESS_MANIFEST_PATH,
    ),
)

GRAPH_SCALE_MANIFEST_EXPECTATIONS = (
    JsonExpectation(
        "pilot_result_manifest",
        ROOT / "results" / "realworld_pilot" / "pilot_result_manifest.json",
    ),
    JsonExpectation(
        "pilot_sample_manifest",
        ROOT / "results" / "realworld_pilot" / "pilot_sample_manifest.json",
    ),
    JsonExpectation(
        "pilot_staged_manifest",
        ROOT / "results" / "realworld_pilot" / "pilot_staged_manifest.json",
    ),
    JsonExpectation(
        "pilot_multi_corridor_manifest",
        ROOT
        / "results"
        / "realworld_pilot"
        / "pilot_multi_corridor_manifest.json",
    ),
    JsonExpectation(
        "pilot_multi_corridor_full_manifest",
        ROOT
        / "results"
        / "realworld_pilot"
        / "pilot_multi_corridor_full_manifest.json",
    ),
    JsonExpectation(
        "pilot_full_manifest",
        ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json",
    ),
    JsonExpectation(
        "sensitivity_manifest",
        ROOT / "results" / "realworld_pilot" / "sensitivity_manifest.json",
    ),
    JsonExpectation(
        "morris_manifest",
        ROOT / "results" / "realworld_pilot" / "morris_manifest.json",
    ),
)

FIGURE_GRAPH_SCALE_MANIFEST = JsonExpectation(
    "figure_table_manifest",
    ROOT
    / "results"
    / "realworld_pilot"
    / "tables"
    / "figure_table_manifest.json",
)

DOC_EXPECTATIONS = (
    ROOT / "plan.md",
    ROOT / "status.md",
    ROOT / "README.md",
    ROOT / "docs" / "analysis_corridor_method_note.md",
    ROOT / "docs" / "realworld_pipeline.md",
    ROOT / "docs" / "third_party_adaptations.md",
    ROOT / "docs" / "graph_scale_diagnostics.md",
    ROOT / "docs" / "graph_scale_review_packet.md",
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_GRAPH_SCALE_METHOD_DECISION_DOC_PATH,
    ROOT / "docs" / "full_graph_smoke.md",
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_DOC_PATH,
    ROOT / "docs" / "graph_scale_result_comparison.md",
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_DOC_PATH,
    ROOT / "docs" / "schemas" / "graph_scale_acceptance_schema.md",
    ROOT / "docs" / "schemas" / "validation_acceptance_schema.md",
    ROOT / "docs" / "validation_review_packet.md",
    DEFAULT_VALIDATION_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_VALIDATION_BENCHMARK_READINESS_DOC_PATH,
    DEFAULT_VALIDATION_BENCHMARK_DECISION_DOC_PATH,
    DEFAULT_INTEGRATED_EVIDENCE_REVIEW_DOC_PATH,
    ROOT / "docs" / "osrm_route_benchmark_manifest.md",
    ROOT / "docs" / "route_road_evidence_exposure.md",
    ROOT / "docs" / "schemas" / "sensitivity_acceptance_schema.md",
    ROOT / "docs" / "sensitivity_diagnostics.md",
    ROOT / "docs" / "sensitivity_review_packet.md",
    DEFAULT_SENSITIVITY_INDEX_REVIEW_DOC_PATH,
    DEFAULT_SENSITIVITY_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_SENSITIVITY_METHOD_DECISION_DOC_PATH,
    ROOT / "docs" / "road_evidence_diagnostics.md",
    ROOT / "docs" / "road_evidence_review_packet.md",
    ROOT / "docs" / "road_evidence_source_request_packet.md",
    DEFAULT_ROAD_EVIDENCE_PRIORITY_DOC_PATH,
    ROOT / "docs" / "accessibility_loss_analysis.md",
    ROOT / "docs" / "schemas" / "experiment_acceptance_schema.md",
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_DOC_PATH,
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_EXPERIMENT_DESIGN_DECISION_DOC_PATH,
    DEFAULT_EXPERIMENT_STATISTICAL_PLAN_DOC_PATH,
    DEFAULT_DETERMINISTIC_RERUN_AUDIT_DOC,
    ROOT / "docs" / "schemas" / "provenance_acceptance_schema.md",
    ROOT / "docs" / "source_provenance_manifest.md",
    DEFAULT_SOURCE_LICENSE_REVIEW_DOC_PATH,
    DEFAULT_SOURCE_URL_REVIEW_DOC_PATH,
    DEFAULT_SOURCE_URL_REMEDIATION_DOC_PATH,
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_DOC_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_DOC_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_DOC_PATH,
    DEFAULT_SOURCE_PROVENANCE_DECISION_DOC_PATH,
    ROOT / "docs" / "schemas" / "manuscript_acceptance_schema.md",
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_DOC_PATH,
    DEFAULT_CLAIM_LANGUAGE_GUARD_DOC_PATH,
    DEFAULT_ARTIFACT_INVALIDATION_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_DOC,
    DEFAULT_FIGURE_TABLE_REVIEW_DOC_PATH,
    DEFAULT_MANUSCRIPT_REPORT_DECISION_DOC_PATH,
    ROOT / "docs" / "schemas" / "reproducibility_acceptance_schema.md",
    ROOT / "docs" / "schemas" / "final_audit_acceptance_schema.md",
    ROOT / "docs" / "schemas" / "pilot_acceptance_schema.md",
    DEFAULT_PILOT_PRIVACY_REVIEW_DOC_PATH,
    DEFAULT_PILOT_REGION_DECISION_DOC_PATH,
    ROOT / "docs" / "schemas" / "parameter_acceptance_schema.md",
    ROOT / "docs" / "parameter_evidence_review_packet.md",
    ROOT / "docs" / "parameter_evidence_source_request_packet.md",
    DEFAULT_PARAMETER_SOURCE_READINESS_DOC_PATH,
    DEFAULT_PARAMETER_SOURCE_DECISION_DOC_PATH,
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_DOC_PATH,
    ROOT / "docs" / "reproducibility_package.md",
    ROOT / "docs" / "reproducibility_review_packet.md",
    DEFAULT_REPRODUCIBILITY_DECISION_DOC_PATH,
    DEFAULT_FINAL_AUDIT_DECISION_DOC_PATH,
    DEFAULT_ACCEPTANCE_TEMPLATE_DOC_PATH,
    DEFAULT_BLOCKER_QUEUE_DOC_PATH,
    DEFAULT_TASK_ASSIGNMENT_DOC_PATH,
    DEFAULT_EVIDENCE_MATRIX_DOC_PATH,
    DEFAULT_PRE_REVIEW_DOC_PATH,
    ROOT / "docs" / "human_acceptance_runbook.md",
    ROOT / "docs" / "formal_acceptance_artifact_guard.md",
    DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_DOC_PATH,
    DEFAULT_FORMAL_EVIDENCE_PATH_AUDIT_DOC,
    DEFAULT_AGENT_REVIEW_PATH_AUDIT_DOC,
    DEFAULT_REVIEW_PACKAGE_PATH_AUDIT_DOC,
    DEFAULT_EXPERT_REVIEW_HANDOFF_DOC,
    DEFAULT_TRACKED_ARTIFACT_AUDIT_DOC,
    DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_DOC,
    DEFAULT_PHASE_GATE_LEDGER_AUDIT_DOC,
    ROOT / "docs" / "plan_completion_audit.md",
    ROOT / "docs" / "current_goal_completion_audit.md",
    DEFAULT_PUBLICATION_READINESS_DOC_PATH,
    ROOT / "docs" / "agents" / "acceptance_review_agents.md",
    ROOT / "docs" / "review_packets" / "acceptance_review_index.md",
    ROOT / "docs" / "review_packets" / "pilot_region_accepted.md",
    ROOT / "docs" / "review_packets" / "data_provenance.md",
    ROOT / "docs" / "review_packets" / "graph_scale_strategy.md",
    ROOT / "docs" / "review_packets" / "cached_osm_input.md",
    ROOT / "docs" / "review_packets" / "parameter_evidence.md",
    ROOT / "docs" / "review_packets" / "rail_evidence.md",
    ROOT / "docs" / "review_packets" / "validation_package.md",
    ROOT / "docs" / "review_packets" / "sensitivity_analysis.md",
    ROOT / "docs" / "review_packets" / "full_experiment_output.md",
    ROOT / "docs" / "review_packets" / "manuscript_report_alignment.md",
    ROOT / "docs" / "review_packets" / "reproducibility.md",
    ROOT / "docs" / "review_packets" / "final_audit.md",
    ROOT / "docs" / "schemas" / "road_class_override_schema.md",
    ROOT / "docs" / "schemas" / "rail_station_cache_schema.md",
    ROOT / "docs" / "schemas" / "rail_timetable_cache_schema.md",
    ROOT / "docs" / "schemas" / "rail_gtfs_cache_schema.md",
    ROOT / "docs" / "schemas" / "rail_shortest_path_cache_schema.md",
    ROOT / "docs" / "rail_evidence_review_packet.md",
    ROOT / "docs" / "rail_timing_source_request_packet.md",
    DEFAULT_RAIL_FETCH_READINESS_DOC_PATH,
    DEFAULT_RAIL_EVIDENCE_PRIORITY_DOC_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_DOC_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_ACTION_LEDGER_TEMPLATE_DOC_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_DOC_PATH,
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_DOC_PATH,
    DEFAULT_GPU_ML_RUNTIME_DOC,
    DEFAULT_PROFILE_DOC_PATH,
    DEFAULT_SCENARIO_DOC_PATH,
    DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_DOC_PATH,
    DEFAULT_ROAD_SOURCE_READINESS_DOC_PATH,
    DEFAULT_ROAD_SOURCE_DECISION_DOC_PATH,
    ROOT / "paper" / "paper_draft.md",
)


def main() -> int:
    """Run artifact checks and print a conservative JSON audit summary."""

    summary = audit_artifacts()
    print(json.dumps(summary, indent=2, sort_keys=True))
    dirty_gate_ok = bool(
        summary.get("dirty_worktree_classification", {}).get(
            "coverage_matches_current_git_status",
            False,
        )
    )
    phase_gate_closure_ok = bool(
        summary.get("phase_gate_ledger_audit", {}).get(
            "phase_gate_ledgers_ready",
            False,
        )
    )
    claim_language_ok = bool(
        summary.get("claim_language_guard", {}).get(
            "claim_language_guard_ready",
            False,
        )
    )
    return (
        0
        if summary["all_required_artifacts_present"]
        and dirty_gate_ok
        and phase_gate_closure_ok
        and claim_language_ok
        else 1
    )


def audit_artifacts() -> dict[str, Any]:
    """Return a structured scaffold audit for current generated artifacts."""

    csv_checks = [_check_csv(expectation) for expectation in CSV_EXPECTATIONS]
    json_checks = [_check_json(expectation) for expectation in JSON_EXPECTATIONS]
    graph_scale_checks = [
        *[
            _check_direct_graph_scale_manifest(expectation)
            for expectation in GRAPH_SCALE_MANIFEST_EXPECTATIONS
        ],
        *_check_figure_graph_scale_manifest(FIGURE_GRAPH_SCALE_MANIFEST),
    ]
    acceptance_record_checks = _check_agent_review_records()
    doc_checks = [_check_doc(path) for path in DOC_EXPECTATIONS]
    parameter_audit = audit_shipped_parameter_evidence()
    road_audit = audit_cached_road_evidence()
    road_diagnostics = audit_cached_road_evidence_diagnostics()
    road_override_audit = audit_road_class_override_evidence()
    road_override_application_audit = audit_road_class_override_application()
    rail_service_audit = summarize_rail_service_evidence(
        load_rail_service_evidence(DEFAULT_RAIL_SERVICE_EVIDENCE_PATH)
    )
    rail_station_binding_audit = summarize_rail_station_bindings(
        load_rail_station_bindings(DEFAULT_RAIL_STATION_BINDING_PATH)
    )
    rail_bounded_treatment_audit = _summarize_rail_bounded_treatment_audit(
        DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH
    )
    sensitivity_diagnostics = audit_morris_sensitivity_diagnostics()
    source_provenance = summarize_source_provenance_manifest()
    final_study_audit = audit_final_study_readiness()
    acceptance_orchestration = summarize_acceptance_orchestration_manifest()
    acceptance_templates = summarize_acceptance_decision_templates()
    acceptance_blocker_queue = summarize_acceptance_blocker_queue()
    acceptance_task_assignments = summarize_acceptance_task_assignments()
    formal_acceptance_evidence_matrix = (
        summarize_formal_acceptance_evidence_matrix()
    )
    formal_acceptance_pre_review = summarize_formal_acceptance_pre_review()
    agent_review_paths = audit_agent_review_paths()
    review_package_paths = audit_review_package_paths()
    review_handoff = build_expert_review_handoff_summary()
    tracked_artifacts = summarize_tracked_artifact_audit()
    dirty_worktree_classification = summarize_dirty_worktree_classification()
    dirty_worktree_freshness = _audit_dirty_worktree_classification_freshness(
        dirty_worktree_classification
    )
    saved_phase_gate_ledgers = summarize_phase_gate_ledger_audit()
    current_phase_gate_ledgers = audit_phase_gate_ledgers()
    gpu_ml_runtime = _summarize_gpu_ml_runtime_manifest()
    claim_language_guard = summarize_claim_language_guard()
    artifact_action_batch_inspection = (
        summarize_artifact_invalidation_action_batch_inspection_manifest()
    )
    (
        artifact_preflight_blocks_phase9,
        artifact_preflight_blockers,
        artifact_preflight_summary,
    ) = artifact_invalidation_blocks_phase9()
    reproducibility_smoke = summarize_reproducibility_smoke()
    formal_acceptance_guard = audit_formal_acceptance_artifacts()
    formal_acceptance_package = build_formal_acceptance_package_summary()
    formal_evidence_paths = audit_formal_evidence_paths()
    pilot_road_cache_manifest = audit_pilot_road_cache_manifest()
    publication_readiness = audit_publication_readiness()
    evidence_gates = dict(publication_readiness.get("gates", {}))
    all_checks = [
        *csv_checks,
        *json_checks,
        *graph_scale_checks,
        *acceptance_record_checks,
        *doc_checks,
    ]
    return {
        "verdict": SCAFFOLD_VERDICT,
        "all_required_artifacts_present": all(
            bool(item["ok"]) for item in all_checks
        ),
        "claim_boundary": (
            "These checks verify artifact presence, schemas, and row counts for "
            "the current scaffold. They do not certify calibrated real-world "
            "accuracy or operational readiness."
        ),
        "csv_checks": csv_checks,
        "json_checks": json_checks,
        "graph_scale_checks": graph_scale_checks,
        "acceptance_record_checks": acceptance_record_checks,
        "doc_checks": doc_checks,
        "pilot_road_cache_manifest_audit": pilot_road_cache_manifest,
        "parameter_evidence_audit": {
            "publication_ready": parameter_audit["publication_ready"],
            "core_parameter_count": parameter_audit["core_parameter_count"],
            "weak_core_parameter_count": parameter_audit[
                "weak_core_parameter_count"
            ],
            "missing_core_parameter_count": parameter_audit[
                "missing_core_parameter_count"
            ],
            "core_evidence_category_counts": parameter_audit[
                "core_evidence_category_counts"
            ],
            "remaining_blockers": parameter_audit["remaining_blockers"],
        },
        "road_evidence_audit": {
            "publication_ready": road_audit["publication_ready"],
            "node_count": road_audit["node_count"],
            "edge_count": road_audit["edge_count"],
            "routeable_edge_count": road_audit["routeable_edge_count"],
            "cache_manifest_metadata_ready": pilot_road_cache_manifest[
                "metadata_ready"
            ],
            "length_parseable_count": road_audit["length_parseable_count"],
            "maxspeed_parseable_rate": road_audit["maxspeed_parseable_rate"],
            "capacity_explicit_rate": road_audit["capacity_explicit_rate"],
            "remaining_blockers": road_audit["remaining_blockers"],
        },
        "road_evidence_diagnostics_audit": {
            "diagnostics_ready": road_diagnostics["diagnostics_ready"],
            "edge_count": road_diagnostics["edge_count"],
            "routeable_edge_count": road_diagnostics["routeable_edge_count"],
            "highway_class_count": road_diagnostics["highway_class_count"],
            "total_routeable_length_km": road_diagnostics[
                "total_routeable_length_km"
            ],
            "maxspeed_parseable_rate": road_diagnostics[
                "maxspeed_parseable_rate"
            ],
            "capacity_explicit_rate": road_diagnostics["capacity_explicit_rate"],
            "base_disruption_explicit_rate": road_diagnostics[
                "base_disruption_explicit_rate"
            ],
            "top_review_candidates": [
                row["highway"]
                for row in road_diagnostics["top_review_candidates"][:5]
            ],
            "review_items": road_diagnostics["review_items"],
            "remaining_blockers": road_diagnostics["remaining_blockers"],
        },
        "road_override_evidence_audit": {
            "publication_ready": road_override_audit["publication_ready"],
            "override_table_present": road_override_audit["override_table_present"],
            "row_count": road_override_audit["row_count"],
            "draft_table_present": road_override_audit.get(
                "draft_table_present",
                False,
            ),
            "draft_row_count": road_override_audit.get("draft_row_count", 0),
            "draft_source_class_counts": road_override_audit.get(
                "draft_source_class_counts",
                {},
            ),
            "remaining_blockers": road_override_audit["remaining_blockers"],
        },
        "road_override_application_audit": {
            "publication_ready": road_override_application_audit["publication_ready"],
            "manifest_present": road_override_application_audit["manifest_present"],
            "overrides_applied": road_override_application_audit["overrides_applied"],
            "sha256_matches": road_override_application_audit["sha256_matches"],
            "remaining_blockers": road_override_application_audit[
                "remaining_blockers"
            ],
        },
        "rail_evidence_audit": {
            "publication_ready": bool(evidence_gates.get("rail_evidence_ready", False)),
            "service_publication_ready": rail_service_audit["publication_ready"],
            "station_binding_ready": rail_station_binding_audit["binding_ready"],
            "source_decision_ready": bool(
                evidence_gates.get("rail_source_decision_ready", False)
            ),
            "transit_stress_profile_ready": bool(
                evidence_gates.get("rail_transit_stress_profile_ready", False)
            ),
            "bounded_treatment_integrity_ready": bool(
                evidence_gates.get("rail_bounded_treatment_integrity_ready", False)
            ),
            "bounded_treatment_pending_decision_count": (
                rail_bounded_treatment_audit[
                    "unchecked_pending_decision_count"
                ]
            ),
            "bounded_treatment_warning_count": rail_bounded_treatment_audit[
                "warning_count"
            ],
            "bounded_treatment_mismatch_count": rail_bounded_treatment_audit[
                "mismatch_count"
            ],
            "service_remaining_blockers": rail_service_audit["remaining_blockers"],
            "station_binding_remaining_blockers": rail_station_binding_audit[
                "remaining_blockers"
            ],
            "bounded_treatment_remaining_blockers": rail_bounded_treatment_audit[
                "remaining_blockers"
            ],
        },
        "sensitivity_diagnostics_audit": {
            "diagnostics_ready": sensitivity_diagnostics["diagnostics_ready"],
            "row_count": sensitivity_diagnostics["row_count"],
            "manifest_summary_row_count": sensitivity_diagnostics.get(
                "manifest_summary_row_count"
            ),
            "expected_summary_row_count_from_manifest_dimensions": sensitivity_diagnostics.get(
                "expected_summary_row_count_from_manifest_dimensions"
            ),
            "rows_with_index_issues": sensitivity_diagnostics[
                "rows_with_index_issues"
            ],
            "zero_mu_star_count": sensitivity_diagnostics["zero_mu_star_count"],
            "analysis_graph_reduced": sensitivity_diagnostics.get(
                "analysis_graph_reduced"
            ),
            "review_items": sensitivity_diagnostics["review_items"],
            "remaining_blockers": sensitivity_diagnostics["remaining_blockers"],
        },
        "source_provenance_audit": {
            "diagnostics_ready": source_provenance["diagnostics_ready"],
            "record_count": source_provenance["record_count"],
            "local_artifact_count": source_provenance.get("local_artifact_count", 0),
            "review_status_counts": source_provenance.get(
                "review_status_counts",
                {},
            ),
            "review_items": source_provenance["review_items"],
            "remaining_blockers": source_provenance["remaining_blockers"],
        },
        "publication_readiness_audit": {
            "publication_ready": bool(
                publication_readiness.get("publication_ready", False)
            ),
            "verdict": publication_readiness.get("verdict", ""),
            "gates": evidence_gates,
            "remaining_blockers": publication_readiness.get(
                "remaining_blockers",
                [],
            ),
        },
        "final_study_readiness_audit": {
            "final_study_ready": final_study_audit["final_study_ready"],
            "verdict": final_study_audit["verdict"],
            "gate_count": final_study_audit["gate_count"],
            "blocked_gate_ids": final_study_audit["blocked_gate_ids"],
            "ready_gate_ids": final_study_audit["ready_gate_ids"],
        },
        "acceptance_orchestration_audit": {
            "manifest_present": acceptance_orchestration["manifest_present"],
            "record_count": acceptance_orchestration["record_count"],
            "status_counts": acceptance_orchestration["status_counts"],
            "can_mark_complete_count": acceptance_orchestration[
                "can_mark_complete_count"
            ],
            "blocked_or_review_record_count": acceptance_orchestration[
                "blocked_or_review_record_count"
            ],
            "final_study_ready": acceptance_orchestration["final_study_ready"],
            "remaining_blocker_count": len(
                acceptance_orchestration["remaining_blockers"]
            ),
        },
        "acceptance_decision_template_audit": {
            "manifest_present": acceptance_templates["manifest_present"],
            "json_template_count": acceptance_templates["json_template_count"],
            "parameter_template_row_count": acceptance_templates[
                "parameter_template_row_count"
            ],
            "can_mark_complete": acceptance_templates["can_mark_complete"],
            "final_study_ready": acceptance_templates["final_study_ready"],
            "formal_acceptance_created": acceptance_templates[
                "formal_acceptance_created"
            ],
        },
        "reproducibility_smoke_audit": {
            "manifest_present": reproducibility_smoke["manifest_present"],
            "result_scope": reproducibility_smoke["result_scope"],
            "command_count": reproducibility_smoke["command_count"],
            "passed_count": reproducibility_smoke["passed_count"],
            "failed_count": reproducibility_smoke["failed_count"],
            "smoke_passed": reproducibility_smoke["smoke_passed"],
            "clean_checkout_test_performed": reproducibility_smoke[
                "clean_checkout_test_performed"
            ],
            "can_mark_complete": reproducibility_smoke["can_mark_complete"],
        },
        "formal_acceptance_blocker_queue_audit": {
            "manifest_present": acceptance_blocker_queue["manifest_present"],
            "row_count": acceptance_blocker_queue["row_count"],
            "status_counts": acceptance_blocker_queue.get("status_counts", {}),
            "formal_acceptance_ready": acceptance_blocker_queue.get(
                "formal_acceptance_ready",
                False,
            ),
            "final_study_ready": acceptance_blocker_queue.get(
                "final_study_ready",
                False,
            ),
            "can_mark_complete": acceptance_blocker_queue["can_mark_complete"],
        },
        "acceptance_task_assignment_audit": {
            "manifest_present": acceptance_task_assignments["manifest_present"],
            "task_count": acceptance_task_assignments["task_count"],
            "assigned_agent_count": acceptance_task_assignments[
                "assigned_agent_count"
            ],
            "requires_human_review_count": acceptance_task_assignments.get(
                "requires_human_review_count",
                0,
            ),
            "formal_acceptance_ready": acceptance_task_assignments.get(
                "formal_acceptance_ready",
                False,
            ),
            "final_study_ready": acceptance_task_assignments.get(
                "final_study_ready",
                False,
            ),
            "can_mark_complete": acceptance_task_assignments["can_mark_complete"],
        },
        "formal_acceptance_evidence_matrix_audit": {
            "manifest_present": formal_acceptance_evidence_matrix[
                "manifest_present"
            ],
            "row_count": formal_acceptance_evidence_matrix["row_count"],
            "formal_gate_count": formal_acceptance_evidence_matrix.get(
                "formal_gate_count",
                0,
            ),
            "status_counts": formal_acceptance_evidence_matrix.get(
                "status_counts",
                {},
            ),
            "human_decision_required_count": formal_acceptance_evidence_matrix[
                "human_decision_required_count"
            ],
            "formal_acceptance_ready": formal_acceptance_evidence_matrix.get(
                "formal_acceptance_ready",
                False,
            ),
            "final_study_ready": formal_acceptance_evidence_matrix.get(
                "final_study_ready",
                False,
            ),
            "can_mark_complete": formal_acceptance_evidence_matrix[
                "can_mark_complete"
            ],
        },
        "formal_acceptance_pre_review_audit": {
            "manifest_present": formal_acceptance_pre_review["manifest_present"],
            "record_count": formal_acceptance_pre_review["record_count"],
            "recommendation_counts": formal_acceptance_pre_review[
                "recommendation_counts"
            ],
            "human_decision_required_count": formal_acceptance_pre_review[
                "human_decision_required_count"
            ],
            "formal_approval": formal_acceptance_pre_review["formal_approval"],
            "final_study_ready": formal_acceptance_pre_review[
                "final_study_ready"
            ],
            "can_mark_complete": formal_acceptance_pre_review[
                "can_mark_complete"
            ],
        },
        "agent_review_path_audit": {
            "record_count": agent_review_paths["record_count"],
            "invalid_record_count": agent_review_paths["invalid_record_count"],
            "path_reference_count": agent_review_paths["path_reference_count"],
            "missing_required_path_count": agent_review_paths[
                "missing_required_path_count"
            ],
            "missing_formal_target_count": agent_review_paths[
                "missing_formal_target_count"
            ],
            "unique_missing_formal_target_count": agent_review_paths[
                "unique_missing_formal_target_count"
            ],
            "agent_review_paths_ready": agent_review_paths[
                "agent_review_paths_ready"
            ],
            "can_mark_complete": agent_review_paths["can_mark_complete"],
        },
        "review_package_path_audit": {
            "zip_present": review_package_paths["zip_present"],
            "zip_valid": review_package_paths["zip_valid"],
            "zip_file_count": review_package_paths["zip_file_count"],
            "record_count": review_package_paths["record_count"],
            "path_reference_count": review_package_paths["path_reference_count"],
            "missing_package_path_count": review_package_paths[
                "missing_package_path_count"
            ],
            "missing_formal_target_count": review_package_paths[
                "missing_formal_target_count"
            ],
            "unique_missing_package_path_count": review_package_paths[
                "unique_missing_package_path_count"
            ],
            "unique_missing_formal_target_count": review_package_paths[
                "unique_missing_formal_target_count"
            ],
            "review_package_paths_ready": review_package_paths[
                "review_package_paths_ready"
            ],
            "can_mark_complete": review_package_paths["can_mark_complete"],
        },
        "expert_review_handoff": {
            "zip_path": review_handoff["zip"]["path"],
            "zip_file_count": review_handoff["zip"]["file_count"],
            "zip_sha256": review_handoff["zip"]["sha256"],
            "mirror_zip_matches": review_handoff["mirror_zip"]["matches_zip"],
            "missing_formal_target_count": review_handoff["formal_status"][
                "missing_formal_target_count"
            ],
            "formal_target_count": review_handoff["formal_status"][
                "formal_target_count"
            ],
            "can_mark_complete": review_handoff["can_mark_complete"],
        },
        "tracked_artifact_audit": {
            "manifest_present": tracked_artifacts["manifest_present"],
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
        "dirty_worktree_classification": {
            "manifest_present": dirty_worktree_classification["manifest_present"],
            "dirty_path_count": dirty_worktree_classification["dirty_path_count"],
            "current_dirty_path_count": dirty_worktree_freshness[
                "current_dirty_path_count"
            ],
            "saved_csv_dirty_path_count": dirty_worktree_freshness[
                "saved_csv_dirty_path_count"
            ],
            "saved_path_count": dirty_worktree_freshness["saved_path_count"],
            "current_path_count": dirty_worktree_freshness["current_path_count"],
            "classified_path_count": dirty_worktree_classification[
                "classified_path_count"
            ],
            "unclassified_path_count": dirty_worktree_classification[
                "unclassified_path_count"
            ],
            "new_generated_output_allowed": dirty_worktree_classification[
                "new_generated_output_allowed"
            ],
            "freshness_status": dirty_worktree_freshness["freshness_status"],
            "coverage_matches_current_git_status": dirty_worktree_freshness[
                "coverage_matches_current_git_status"
            ],
            "can_mark_complete": dirty_worktree_classification["can_mark_complete"],
            "remaining_blockers": [
                *dirty_worktree_classification["remaining_blockers"],
                *dirty_worktree_freshness["remaining_blockers"],
            ],
        },
        "phase_gate_ledger_audit": {
            "manifest_present": saved_phase_gate_ledgers["manifest_present"],
            "expected_phase_count": current_phase_gate_ledgers[
                "expected_phase_count"
            ],
            "valid_ledger_count": current_phase_gate_ledgers["valid_ledger_count"],
            "missing_phase_count": current_phase_gate_ledgers["missing_phase_count"],
            "invalid_ledger_count": current_phase_gate_ledgers[
                "invalid_ledger_count"
            ],
            "closed_phase_count": current_phase_gate_ledgers["closed_phase_count"],
            "saved_support_present": saved_phase_gate_ledgers[
                "phase_gate_support_present"
            ],
            "current_support_present": current_phase_gate_ledgers[
                "phase_gate_support_present"
            ],
            "phase_gate_ledgers_ready": current_phase_gate_ledgers[
                "phase_gate_ledgers_ready"
            ],
            "can_mark_complete": current_phase_gate_ledgers["can_mark_complete"],
            "remaining_blockers": _unique_strings(
                [
                    *saved_phase_gate_ledgers["remaining_blockers"],
                    *current_phase_gate_ledgers["remaining_blockers"],
                ]
            ),
        },
        "gpu_ml_runtime_audit": {
            "manifest_present": gpu_ml_runtime["manifest_present"],
            "log_present": gpu_ml_runtime["log_present"],
            "doc_present": gpu_ml_runtime["doc_present"],
            "can_support_gpu_ml_claim": gpu_ml_runtime[
                "can_support_gpu_ml_claim"
            ],
            "gpu_ml_runtime_passed": gpu_ml_runtime["gpu_ml_runtime_passed"],
            "cpu_fallback_recorded": gpu_ml_runtime["cpu_fallback_recorded"],
            "nvidia_smi_available": gpu_ml_runtime["nvidia_smi_available"],
            "simulation_engine_gpu_accelerated": gpu_ml_runtime[
                "simulation_engine_gpu_accelerated"
            ],
            "simulation_correctness_blocked": gpu_ml_runtime[
                "simulation_correctness_blocked"
            ],
            "publication_ready": gpu_ml_runtime["publication_ready"],
            "final_study_ready": gpu_ml_runtime["final_study_ready"],
            "formal_acceptance_evidence": gpu_ml_runtime[
                "formal_acceptance_evidence"
            ],
            "requirements_path": gpu_ml_runtime["requirements_path"],
            "requirements_status": gpu_ml_runtime["requirements_status"],
            "package_results": gpu_ml_runtime["package_results"],
            "command": gpu_ml_runtime["command"],
            "claim_boundary": gpu_ml_runtime["claim_boundary"],
            "remaining_blockers": gpu_ml_runtime["remaining_blockers"],
        },
        "claim_language_guard": {
            "manifest_present": claim_language_guard.get("manifest_present", False),
            "scan_complete": claim_language_guard.get("scan_complete", False),
            "release_blocked": claim_language_guard.get("release_blocked", True),
            "claims_approved": claim_language_guard.get("claims_approved", False),
            "formal_acceptance_created": claim_language_guard.get(
                "formal_acceptance_created",
                False,
            ),
            "target_file_count": claim_language_guard.get("target_file_count", 0),
            "scanned_file_count": claim_language_guard.get("scanned_file_count", 0),
            "missing_target_count": claim_language_guard.get(
                "missing_target_count",
                0,
            ),
            "unreadable_target_count": claim_language_guard.get(
                "unreadable_target_count",
                0,
            ),
            "reserved_match_count": claim_language_guard.get(
                "reserved_match_count",
                0,
            ),
            "blocking_finding_count": claim_language_guard.get(
                "blocking_finding_count",
                0,
            ),
            "explicit_non_approval_count": claim_language_guard.get(
                "explicit_non_approval_count",
                0,
            ),
            "formal_evidence_backed_count": claim_language_guard.get(
                "formal_evidence_backed_count",
                0,
            ),
            "claim_language_guard_ready": claim_language_guard.get(
                "claim_language_guard_ready",
                False,
            ),
            "publication_ready": claim_language_guard.get(
                "publication_ready",
                False,
            ),
            "final_study_ready": claim_language_guard.get(
                "final_study_ready",
                False,
            ),
            "can_mark_complete": claim_language_guard.get(
                "can_mark_complete",
                False,
            ),
            "remaining_blockers": claim_language_guard.get(
                "remaining_blockers",
                [],
            ),
        },
        "artifact_invalidation_action_batch_inspection": {
            "manifest_present": artifact_action_batch_inspection.get(
                "manifest_present",
                False,
            ),
            "row_count": artifact_action_batch_inspection.get("row_count", 0),
            "action_batch_counts": artifact_action_batch_inspection.get(
                "action_batch_counts",
                {},
            ),
            "dependency_stage_counts": artifact_action_batch_inspection.get(
                "dependency_stage_counts",
                {},
            ),
            "recommended_disposition_counts": artifact_action_batch_inspection.get(
                "recommended_disposition_counts",
                {},
            ),
            "inspection_classification_counts": artifact_action_batch_inspection.get(
                "inspection_classification_counts",
                {},
            ),
            "regeneration_candidate_count": artifact_action_batch_inspection.get(
                "regeneration_candidate_count",
                0,
            ),
            "exclusion_or_non_evidence_candidate_count": artifact_action_batch_inspection.get(
                "exclusion_or_non_evidence_candidate_count",
                0,
            ),
            "evidence_backed_closeout_row_count": artifact_action_batch_inspection.get(
                "evidence_backed_closeout_row_count",
                0,
            ),
            "pending_or_blocked_row_count": artifact_action_batch_inspection.get(
                "pending_or_blocked_row_count",
                0,
            ),
            "action_queue_blocks_phase9_row_count": artifact_action_batch_inspection.get(
                "action_queue_blocks_phase9_row_count",
                0,
            ),
            "reviewer_signoff_required_row_count": artifact_action_batch_inspection.get(
                "reviewer_signoff_required_row_count",
                0,
            ),
            "can_clear_invalidation_gate": artifact_action_batch_inspection.get(
                "can_clear_invalidation_gate",
                False,
            ),
            "can_mark_complete": artifact_action_batch_inspection.get(
                "can_mark_complete",
                False,
            ),
            "phase9_promotion_ready": artifact_action_batch_inspection.get(
                "phase9_promotion_ready",
                False,
            ),
            "publication_ready": artifact_action_batch_inspection.get(
                "publication_ready",
                False,
            ),
            "final_study_ready": artifact_action_batch_inspection.get(
                "final_study_ready",
                False,
            ),
            "formal_acceptance_evidence": artifact_action_batch_inspection.get(
                "formal_acceptance_evidence",
                False,
            ),
            "must_not_be_used_as_closeout_manifest": artifact_action_batch_inspection.get(
                "must_not_be_used_as_closeout_manifest",
                True,
            ),
            "remaining_blockers": artifact_action_batch_inspection.get(
                "remaining_blockers",
                [],
            ),
        },
        "artifact_invalidation_preflight_audit": {
            "blocks_phase9": artifact_preflight_blocks_phase9,
            "matrix_manifest_present": artifact_preflight_summary.get(
                "manifest_present",
                False,
            ),
            "matrix_row_count": artifact_preflight_summary.get("row_count", 0),
            "blocking_row_count": artifact_preflight_summary.get(
                "blocking_row_count",
                0,
            ),
            "closeout_manifest_present": artifact_preflight_summary.get(
                "closeout_snapshot",
                {},
            ).get("manifest_present", False),
            "closeout_pending_or_invalid_row_count": artifact_preflight_summary.get(
                "closeout_snapshot",
                {},
            ).get("pending_or_invalid_row_count", 0),
            "closeout_csv_verification_status": artifact_preflight_summary.get(
                "closeout_snapshot",
                {},
            ).get("closeout_csv_verification_status", ""),
            "closeout_csv_summary_matches_manifest": artifact_preflight_summary.get(
                "closeout_snapshot",
                {},
            ).get("closeout_csv_summary_matches_manifest", False),
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "remaining_blockers": artifact_preflight_blockers,
        },
        "formal_acceptance_guard_audit": {
            "artifact_count": formal_acceptance_guard["artifact_count"],
            "present_count": formal_acceptance_guard["present_count"],
            "missing_count": formal_acceptance_guard["missing_count"],
            "template_or_placeholder_count": formal_acceptance_guard[
                "template_or_placeholder_count"
            ],
            "formal_acceptance_ready": formal_acceptance_guard[
                "formal_acceptance_ready"
            ],
            "can_mark_complete": formal_acceptance_guard["can_mark_complete"],
        },
        "formal_acceptance_package_audit": {
            "gate_count": formal_acceptance_package["gate_count"],
            "ready_gate_count": formal_acceptance_package["ready_gate_count"],
            "blocked_gate_count": formal_acceptance_package["blocked_gate_count"],
            "invalid_gate_count": formal_acceptance_package["invalid_gate_count"],
            "formal_acceptance_ready": formal_acceptance_package[
                "formal_acceptance_ready"
            ],
            "final_study_ready": formal_acceptance_package["final_study_ready"],
            "can_mark_complete": formal_acceptance_package["can_mark_complete"],
        },
        "formal_evidence_path_audit": {
            "artifact_count": formal_evidence_paths["artifact_count"],
            "present_artifact_count": formal_evidence_paths[
                "present_artifact_count"
            ],
            "evidence_item_count": formal_evidence_paths["evidence_item_count"],
            "missing_local_evidence_count": formal_evidence_paths[
                "missing_local_evidence_count"
            ],
            "placeholder_evidence_count": formal_evidence_paths[
                "placeholder_evidence_count"
            ],
            "can_mark_complete": formal_evidence_paths["can_mark_complete"],
        },
        "remaining_blockers": [
            "accepted pilot input package and final graph-scale method acceptance",
            "reviewed source/license/snapshot provenance acceptance",
            "cached GTFS, timetable, shortest-path, or equivalent rail service evidence for final-study claims",
            "road, fleet, transfer, disruption, demand/time, and censoring parameter source strengthening",
            "publication-level plausibility benchmark decision",
            "reviewed manuscript/report acceptance after evidence gates close",
            "clean-checkout reproducibility acceptance after final evidence gates close",
            "review of data/validation/reproducibility_review_packet.csv before clean-checkout acceptance",
            "independent final-audit acceptance after every pre-final gate closes",
            "human/source-backed review of sub-agent acceptance packets and formal acceptance artifacts",
        ],
    }


def _check_csv(expectation: CsvExpectation) -> dict[str, Any]:
    if not expectation.path.exists():
        return {
            "label": expectation.label,
            "path": _display_path(expectation.path),
            "ok": False,
            "error": "missing file",
        }
    with expectation.path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    row_count = len(rows)
    expected = expectation.expected_rows
    ok = expected is None or row_count == expected
    return {
        "label": expectation.label,
        "path": _display_path(expectation.path),
        "ok": ok,
        "rows": row_count,
        "expected_rows": expected,
    }


def _check_json(expectation: JsonExpectation) -> dict[str, Any]:
    if not expectation.path.exists():
        return {
            "label": expectation.label,
            "path": _display_path(expectation.path),
            "ok": False,
            "error": "missing file",
        }
    with expectation.path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return {
        "label": expectation.label,
        "path": _display_path(expectation.path),
        "ok": isinstance(value, dict),
        "top_level_keys": sorted(value) if isinstance(value, dict) else [],
    }


def audit_pilot_road_cache_manifest(
    path: Path = ROOT / "data" / "cache" / "pilot_region_road_manifest.json",
) -> dict[str, Any]:
    """Summarize whether the road cache manifest exposes review metadata."""

    manifest = _read_json_object(path)
    if manifest is None:
        return {
            "manifest_present": False,
            "metadata_ready": False,
            "path": _display_path(path),
            "remaining_blockers": ["pilot road cache manifest is missing or invalid"],
        }

    boundary = manifest.get("boundary")
    tooling = manifest.get("tooling")
    boundary_ready = (
        isinstance(boundary, dict)
        and boundary.get("type") == "bbox"
        and all(
            isinstance(boundary.get(key), (int, float))
            for key in ("north", "south", "east", "west")
        )
    )
    tooling_ready = (
        isinstance(tooling, dict)
        and bool(tooling.get("builder"))
        and bool(tooling.get("graph_writer"))
        and bool(tooling.get("extractor"))
    )
    attribution_ready = "OpenStreetMap contributors" in str(
        manifest.get("attribution", "")
    ) or manifest.get("source") == "curated_public_coordinate_osm_style_fixture"
    claim_limit_ready = "publication claims" in str(manifest.get("claim_limit", ""))
    metadata_ready = bool(
        boundary_ready and tooling_ready and attribution_ready and claim_limit_ready
    )
    blockers: list[str] = []
    if not boundary_ready:
        blockers.append("cache manifest boundary bbox metadata is missing or incomplete")
    if not tooling_ready:
        blockers.append("cache manifest tooling metadata is missing or incomplete")
    if not attribution_ready:
        blockers.append("cache manifest attribution metadata requires review")
    if not claim_limit_ready:
        blockers.append("cache manifest claim-limit boundary is missing")
    blockers.append(
        "cache manifest metadata does not replace road-source review or calibrated evidence"
    )
    return {
        "manifest_present": True,
        "metadata_ready": metadata_ready,
        "path": _display_path(path),
        "source": manifest.get("source", ""),
        "created_utc": manifest.get("created_utc", ""),
        "boundary_ready": boundary_ready,
        "tooling_ready": tooling_ready,
        "attribution_ready": attribution_ready,
        "claim_limit_ready": claim_limit_ready,
        "node_count": manifest.get("node_count"),
        "edge_count": manifest.get("edge_count"),
        "remaining_blockers": blockers,
    }


def _check_direct_graph_scale_manifest(expectation: JsonExpectation) -> dict[str, Any]:
    value = _read_json_object(expectation.path)
    if value is None:
        return {
            "label": expectation.label,
            "path": _display_path(expectation.path),
            "ok": False,
            "error": "missing or non-object JSON",
        }
    return _graph_scale_check_result(
        label=expectation.label,
        path=expectation.path,
        graph_scale=value.get("graph_scale"),
    )


def _check_figure_graph_scale_manifest(
    expectation: JsonExpectation,
) -> list[dict[str, Any]]:
    value = _read_json_object(expectation.path)
    if value is None:
        return [
            {
                "label": f"{expectation.label}:pilot",
                "path": _display_path(expectation.path),
                "ok": False,
                "error": "missing or non-object JSON",
            },
            {
                "label": f"{expectation.label}:sensitivity",
                "path": _display_path(expectation.path),
                "ok": False,
                "error": "missing or non-object JSON",
            },
        ]
    graph_scale = value.get("graph_scale")
    if not isinstance(graph_scale, dict):
        pilot_scale = None
        sensitivity_scale = None
    else:
        pilot_scale = graph_scale.get("pilot")
        sensitivity_scale = graph_scale.get("sensitivity")
    return [
        _graph_scale_check_result(
            label=f"{expectation.label}:pilot",
            path=expectation.path,
            graph_scale=pilot_scale,
        ),
        _graph_scale_check_result(
            label=f"{expectation.label}:sensitivity",
            path=expectation.path,
            graph_scale=sensitivity_scale,
        ),
    ]


def _graph_scale_check_result(
    *,
    label: str,
    path: Path,
    graph_scale: object,
) -> dict[str, Any]:
    if not isinstance(graph_scale, dict):
        return {
            "label": label,
            "path": _display_path(path),
            "ok": False,
            "error": "missing graph_scale object",
        }
    source = graph_scale.get("source")
    analysis = graph_scale.get("analysis")
    ok = (
        isinstance(source, dict)
        and isinstance(analysis, dict)
        and _positive_int(source.get("nodes"))
        and _positive_int(source.get("edges"))
        and _positive_int(analysis.get("nodes"))
        and _positive_int(analysis.get("edges"))
        and isinstance(analysis.get("reduced"), bool)
        and bool(str(analysis.get("strategy", "")).strip())
    )
    return {
        "label": label,
        "path": _display_path(path),
        "ok": bool(ok),
        "source_nodes": source.get("nodes") if isinstance(source, dict) else None,
        "source_edges": source.get("edges") if isinstance(source, dict) else None,
        "analysis_nodes": analysis.get("nodes") if isinstance(analysis, dict) else None,
        "analysis_edges": analysis.get("edges") if isinstance(analysis, dict) else None,
        "analysis_reduced": analysis.get("reduced") if isinstance(analysis, dict) else None,
        "analysis_strategy": analysis.get("strategy") if isinstance(analysis, dict) else "",
    }


def _read_json_object(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else None


def _positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _audit_dirty_worktree_classification_freshness(
    manifest_summary: dict[str, Any],
) -> dict[str, Any]:
    """Check saved dirty-worktree ledger coverage against current git status."""

    current_rows = build_dirty_worktree_classification_rows()
    saved_rows = _read_csv_rows(DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_CSV)
    current_count = len(current_rows)
    saved_csv_count = len(saved_rows)
    saved_count = int(manifest_summary.get("dirty_path_count", 0))
    current_paths = {str(row.get("path", "")) for row in current_rows}
    saved_paths = {str(row.get("path", "")) for row in saved_rows}
    git_status_failed = any(
        row.get("evidence_status") == "git_status_failed"
        for row in current_rows
    )
    matches = (
        bool(manifest_summary.get("manifest_present", False))
        and saved_count == current_count
        and saved_csv_count == current_count
        and saved_paths == current_paths
        and not git_status_failed
    )
    blockers: list[str] = []
    if not manifest_summary.get("manifest_present", False):
        blockers.append("dirty worktree classification manifest is missing")
    if not DEFAULT_DIRTY_WORKTREE_CLASSIFICATION_CSV.exists():
        blockers.append("dirty worktree classification CSV is missing")
    if saved_count != current_count:
        blockers.append(
            "dirty worktree classification is stale or incomplete: "
            f"manifest_dirty_path_count={saved_count}; "
            f"current_dirty_path_count={current_count}"
        )
    if saved_csv_count != current_count:
        blockers.append(
            "dirty worktree classification CSV row count is stale or incomplete: "
            f"csv_dirty_path_count={saved_csv_count}; "
            f"current_dirty_path_count={current_count}"
        )
    if saved_paths != current_paths:
        missing_from_saved = sorted(current_paths - saved_paths)
        extra_in_saved = sorted(saved_paths - current_paths)
        blockers.append(
            "dirty worktree classification path set does not match current git status: "
            f"missing_from_saved={missing_from_saved[:5]}; "
            f"extra_in_saved={extra_in_saved[:5]}"
        )
    if git_status_failed:
        blockers.append("current git status failed during dirty classification freshness check")
    return {
        "current_dirty_path_count": current_count,
        "saved_csv_dirty_path_count": saved_csv_count,
        "saved_path_count": len(saved_paths),
        "current_path_count": len(current_paths),
        "freshness_status": "fresh" if matches else "blocked_stale_or_incomplete",
        "coverage_matches_current_git_status": matches,
        "remaining_blockers": blockers,
    }


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _summarize_gpu_ml_runtime_manifest() -> dict[str, Any]:
    if not DEFAULT_GPU_ML_RUNTIME_MANIFEST.exists():
        return {
            "manifest_present": False,
            "log_present": DEFAULT_GPU_ML_RUNTIME_LOG.exists(),
            "doc_present": DEFAULT_GPU_ML_RUNTIME_DOC.exists(),
            "can_support_gpu_ml_claim": False,
            "gpu_ml_runtime_passed": False,
            "cpu_fallback_recorded": False,
            "nvidia_smi_available": False,
            "simulation_engine_gpu_accelerated": False,
            "simulation_correctness_blocked": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "requirements_path": "",
            "requirements_status": "missing_manifest",
            "package_results": [],
            "command": [],
            "claim_boundary": GPU_ML_RUNTIME_SCOPE,
            "remaining_blockers": ["GPU ML runtime manifest is missing"],
        }
    try:
        payload = json.loads(
            DEFAULT_GPU_ML_RUNTIME_MANIFEST.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        return {
            "manifest_present": True,
            "log_present": DEFAULT_GPU_ML_RUNTIME_LOG.exists(),
            "doc_present": DEFAULT_GPU_ML_RUNTIME_DOC.exists(),
            "can_support_gpu_ml_claim": False,
            "gpu_ml_runtime_passed": False,
            "cpu_fallback_recorded": False,
            "nvidia_smi_available": False,
            "simulation_engine_gpu_accelerated": False,
            "simulation_correctness_blocked": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "requirements_path": "",
            "requirements_status": "invalid_manifest",
            "package_results": [],
            "command": [],
            "claim_boundary": GPU_ML_RUNTIME_SCOPE,
            "remaining_blockers": [
                f"GPU ML runtime manifest is invalid JSON: {exc}"
            ],
        }
    requirements = payload.get("requirements", {})
    if not isinstance(requirements, dict):
        requirements = {}
    package_results = payload.get("package_results", [])
    if not isinstance(package_results, list):
        package_results = []
    command = payload.get("command", [])
    if not isinstance(command, list):
        command = []
    blockers = payload.get("remaining_blockers", [])
    if not isinstance(blockers, list):
        blockers = ["GPU ML runtime remaining_blockers is not an array"]
    if not DEFAULT_GPU_ML_RUNTIME_LOG.exists():
        blockers = [*blockers, "GPU ML runtime JSONL log is missing"]
    if not DEFAULT_GPU_ML_RUNTIME_DOC.exists():
        blockers = [*blockers, "GPU ML runtime Markdown note is missing"]
    return {
        "manifest_present": True,
        "log_present": DEFAULT_GPU_ML_RUNTIME_LOG.exists(),
        "doc_present": DEFAULT_GPU_ML_RUNTIME_DOC.exists(),
        "can_support_gpu_ml_claim": bool(
            payload.get("can_support_gpu_ml_claim", False)
        ),
        "gpu_ml_runtime_passed": bool(payload.get("gpu_ml_runtime_passed", False)),
        "cpu_fallback_recorded": bool(
            payload.get("cpu_fallback_recorded", False)
        ),
        "nvidia_smi_available": bool(payload.get("nvidia_smi_available", False)),
        "simulation_engine_gpu_accelerated": bool(
            payload.get("simulation_engine_gpu_accelerated", False)
        ),
        "simulation_correctness_blocked": bool(
            payload.get("simulation_correctness_blocked", False)
        ),
        "publication_ready": bool(payload.get("publication_ready", False)),
        "final_study_ready": bool(payload.get("final_study_ready", False)),
        "formal_acceptance_evidence": bool(
            payload.get("formal_acceptance_evidence", False)
        ),
        "requirements_path": str(requirements.get("path", "")),
        "requirements_status": str(requirements.get("status", "")),
        "package_results": package_results,
        "command": command,
        "claim_boundary": str(payload.get("claim_boundary", GPU_ML_RUNTIME_SCOPE)),
        "remaining_blockers": _unique_strings([str(item) for item in blockers]),
    }


def _check_doc(path: Path) -> dict[str, Any]:
    return {
        "label": path.stem,
        "path": _display_path(path),
        "ok": path.exists() and path.stat().st_size > 0,
    }


def _check_agent_review_records() -> list[dict[str, Any]]:
    expected = {
        gate_id
        for agent in REVIEW_AGENT_DEFINITIONS
        for gate_id in agent.gate_ids
    }
    checks: list[dict[str, Any]] = []
    for gate_id in sorted(expected):
        matches = sorted(DEFAULT_AGENT_REVIEW_DIR.glob(f"{gate_id}__*.json"))
        if not matches:
            checks.append(
                {
                    "label": gate_id,
                    "path": _display_path(DEFAULT_AGENT_REVIEW_DIR),
                    "ok": False,
                    "error": "missing agent review record",
                }
            )
            continue
        record_path = matches[0]
        try:
            record = load_acceptance_record(record_path)
        except Exception as exc:  # pragma: no cover - surfaced in JSON audit output
            checks.append(
                {
                    "label": gate_id,
                    "path": _display_path(record_path),
                    "ok": False,
                    "error": str(exc),
                }
            )
            continue
        checks.append(
            {
                "label": gate_id,
                "path": _display_path(record_path),
                "ok": (
                    record.gate_id == gate_id
                    and record.status in {"blocked", "needs_human_review", "accepted"}
                    and (record.status == "accepted") == record.can_mark_complete
                ),
                "status": record.status,
                "can_mark_complete": record.can_mark_complete,
                "required_action_count": len(record.required_actions),
                "risk_count": len(record.risks),
            }
        )
    return checks


def _unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
