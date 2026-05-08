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
from src.realworld.claim_alignment_review_packet import (  # noqa: E402
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_DOC_PATH,
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
)
from src.realworld.figure_table_review_packet import (  # noqa: E402
    DEFAULT_FIGURE_TABLE_REVIEW_DOC_PATH,
    DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
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
from src.realworld.road_source_readiness_packet import (  # noqa: E402
    DEFAULT_ROAD_SOURCE_READINESS_DOC_PATH,
    DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
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
from src.realworld.tracked_artifact_audit import (  # noqa: E402
    DEFAULT_TRACKED_ARTIFACT_AUDIT_CSV,
    DEFAULT_TRACKED_ARTIFACT_AUDIT_DOC,
    DEFAULT_TRACKED_ARTIFACT_AUDIT_MANIFEST,
    summarize_tracked_artifact_audit,
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
        10,
    ),
    CsvExpectation(
        "rail_timing_source_request_packet",
        ROOT / "data" / "rail" / "rail_timing_source_request_packet.csv",
        5,
    ),
    CsvExpectation(
        "rail_fetch_readiness_packet",
        DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
        5,
    ),
    CsvExpectation(
        "rail_evidence_priority_packet",
        DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
        6,
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
        6,
    ),
    CsvExpectation(
        "parameter_source_readiness_packet",
        DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
        6,
    ),
    CsvExpectation(
        "parameter_evidence_priority_packet",
        DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
        6,
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
        4,
    ),
    CsvExpectation(
        "pilot_privacy_review_packet",
        DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH,
        7,
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
        "claim_alignment_review_packet",
        DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
        None,
    ),
    CsvExpectation(
        "figure_table_review_packet",
        DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
        8,
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
        7056,
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
        "reproducibility_review_packet",
        DEFAULT_REPRODUCIBILITY_REVIEW_PACKET_PATH,
        8,
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
        "rail_fetch_readiness_manifest",
        DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "rail_evidence_priority_manifest",
        DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    ),
    JsonExpectation(
        "road_source_readiness_manifest",
        DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    ),
    JsonExpectation(
        "parameter_source_readiness_manifest",
        DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
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
        "claim_alignment_review_manifest",
        DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    ),
    JsonExpectation(
        "figure_table_review_manifest",
        DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
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
        "tracked_artifact_audit_manifest",
        DEFAULT_TRACKED_ARTIFACT_AUDIT_MANIFEST,
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
    ROOT / "docs" / "full_graph_smoke.md",
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_DOC_PATH,
    ROOT / "docs" / "graph_scale_result_comparison.md",
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_DOC_PATH,
    ROOT / "docs" / "graph_scale_acceptance_schema.md",
    ROOT / "docs" / "validation_acceptance_schema.md",
    ROOT / "docs" / "validation_review_packet.md",
    DEFAULT_VALIDATION_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_VALIDATION_BENCHMARK_READINESS_DOC_PATH,
    DEFAULT_VALIDATION_BENCHMARK_DECISION_DOC_PATH,
    ROOT / "docs" / "osrm_route_benchmark_manifest.md",
    ROOT / "docs" / "route_road_evidence_exposure.md",
    ROOT / "docs" / "sensitivity_acceptance_schema.md",
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
    ROOT / "docs" / "experiment_acceptance_schema.md",
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_DOC_PATH,
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_EXPERIMENT_DESIGN_DECISION_DOC_PATH,
    ROOT / "docs" / "provenance_acceptance_schema.md",
    ROOT / "docs" / "source_provenance_manifest.md",
    DEFAULT_SOURCE_LICENSE_REVIEW_DOC_PATH,
    DEFAULT_SOURCE_URL_REVIEW_DOC_PATH,
    DEFAULT_SOURCE_URL_REMEDIATION_DOC_PATH,
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_DOC_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_DOC_PATH,
    ROOT / "docs" / "manuscript_acceptance_schema.md",
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_DOC_PATH,
    DEFAULT_FIGURE_TABLE_REVIEW_DOC_PATH,
    ROOT / "docs" / "reproducibility_acceptance_schema.md",
    ROOT / "docs" / "final_audit_acceptance_schema.md",
    ROOT / "docs" / "pilot_acceptance_schema.md",
    DEFAULT_PILOT_PRIVACY_REVIEW_DOC_PATH,
    ROOT / "docs" / "parameter_acceptance_schema.md",
    ROOT / "docs" / "parameter_evidence_review_packet.md",
    ROOT / "docs" / "parameter_evidence_source_request_packet.md",
    DEFAULT_PARAMETER_SOURCE_READINESS_DOC_PATH,
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_DOC_PATH,
    ROOT / "docs" / "reproducibility_package.md",
    ROOT / "docs" / "reproducibility_review_packet.md",
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
    DEFAULT_TRACKED_ARTIFACT_AUDIT_DOC,
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
    ROOT / "docs" / "road_class_override_schema.md",
    ROOT / "docs" / "rail_station_cache_schema.md",
    ROOT / "docs" / "rail_timetable_cache_schema.md",
    ROOT / "docs" / "rail_gtfs_cache_schema.md",
    ROOT / "docs" / "rail_shortest_path_cache_schema.md",
    ROOT / "docs" / "rail_evidence_review_packet.md",
    ROOT / "docs" / "rail_timing_source_request_packet.md",
    DEFAULT_RAIL_FETCH_READINESS_DOC_PATH,
    DEFAULT_RAIL_EVIDENCE_PRIORITY_DOC_PATH,
    DEFAULT_ROAD_SOURCE_READINESS_DOC_PATH,
    ROOT / "paper" / "paper_draft.md",
)


def main() -> int:
    """Run artifact checks and print a conservative JSON audit summary."""

    summary = audit_artifacts()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["all_required_artifacts_present"] else 1


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
    tracked_artifacts = summarize_tracked_artifact_audit()
    reproducibility_smoke = summarize_reproducibility_smoke()
    formal_acceptance_guard = audit_formal_acceptance_artifacts()
    formal_acceptance_package = build_formal_acceptance_package_summary()
    formal_evidence_paths = audit_formal_evidence_paths()
    pilot_road_cache_manifest = audit_pilot_road_cache_manifest()
    evidence_gates = {
        "parameter_evidence_ready": parameter_audit["publication_ready"],
        "road_input_evidence_ready": road_audit["publication_ready"],
        "road_override_evidence_ready": road_override_audit["publication_ready"],
        "road_override_application_ready": road_override_application_audit[
            "publication_ready"
        ],
        "rail_service_evidence_ready": rail_service_audit["publication_ready"],
        "rail_station_binding_ready": rail_station_binding_audit["binding_ready"],
        "rail_evidence_ready": bool(
            rail_service_audit["publication_ready"]
            and rail_station_binding_audit["binding_ready"]
        ),
    }
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
            "publication_ready": evidence_gates["rail_evidence_ready"],
            "service_publication_ready": rail_service_audit["publication_ready"],
            "station_binding_ready": rail_station_binding_audit["binding_ready"],
            "service_remaining_blockers": rail_service_audit["remaining_blockers"],
            "station_binding_remaining_blockers": rail_station_binding_audit[
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
            "publication_ready": all(evidence_gates.values()),
            "verdict": (
                "final_study_claims_allowed"
                if all(evidence_gates.values())
                else "final_study_claims_blocked"
            ),
            "gates": evidence_gates,
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


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
