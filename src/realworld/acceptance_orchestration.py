"""Sub-agent acceptance orchestration for final-study gate review.

This module turns the final-study readiness blockers into deterministic,
auditable review-agent tasks. It intentionally writes review records under
``data/manifests/agent_reviews/`` instead of writing the formal acceptance
artifacts that require human or source-backed decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.realworld.acceptance_records import (
    AcceptanceRecord,
    acceptance_record_from_mapping,
    validate_acceptance_record_mapping,
    write_acceptance_record_schema,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AGENT_DEFINITION_PATH = PROJECT_ROOT / "agents" / "acceptance_review_agents.json"
DEFAULT_AGENT_DOC_PATH = PROJECT_ROOT / "docs" / "agents" / "acceptance_review_agents.md"
DEFAULT_AGENT_REVIEW_DIR = PROJECT_ROOT / "data" / "manifests" / "agent_reviews"
DEFAULT_REVIEW_PACKET_DIR = PROJECT_ROOT / "docs" / "review_packets"
DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "acceptance_orchestration_manifest.json"
)
DEFAULT_ACCEPTANCE_SCHEMA_PATH = PROJECT_ROOT / "schemas" / "acceptance_record.schema.json"
DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_provenance_priority_manifest.json"
)
DEFAULT_REVIEW_STATUS_SNAPSHOT_MANIFESTS: tuple[tuple[str, str, Path], ...] = (
    (
        "source_provenance_priority",
        "Source Provenance Priority",
        PROJECT_ROOT / "data" / "manifests" / "source_provenance_priority_manifest.json",
    ),
    (
        "source_context_cache_request",
        "Source Context Cache Requests",
        PROJECT_ROOT
        / "data"
        / "manifests"
        / "source_context_cache_request_manifest.json",
    ),
    (
        "source_context_cache_decision",
        "Source Context Cache Decisions",
        PROJECT_ROOT
        / "data"
        / "manifests"
        / "source_context_cache_decision_manifest.json",
    ),
    (
        "source_license_review",
        "Source/License Review",
        PROJECT_ROOT / "data" / "manifests" / "source_license_review_manifest.json",
    ),
    (
        "source_url_review",
        "Source URL Review",
        PROJECT_ROOT / "data" / "manifests" / "source_url_review_manifest.json",
    ),
    (
        "source_url_remediation",
        "Source URL Remediation",
        PROJECT_ROOT / "data" / "manifests" / "source_url_remediation_manifest.json",
    ),
    (
        "graph_scale_review",
        "Graph-Scale Method Review",
        PROJECT_ROOT / "data" / "validation" / "graph_scale_review_manifest.json",
    ),
    (
        "full_graph_runtime_readiness",
        "Full-Graph Runtime Readiness",
        PROJECT_ROOT
        / "data"
        / "validation"
        / "full_graph_runtime_readiness_manifest.json",
    ),
    (
        "graph_scale_strategy_readiness",
        "Graph-Scale Strategy Readiness",
        PROJECT_ROOT / "data" / "validation" / "graph_scale_strategy_readiness_manifest.json",
    ),
    (
        "graph_scale_manifest_audit",
        "Graph-Scale Manifest Audit",
        PROJECT_ROOT / "data" / "validation" / "graph_scale_manifest_audit_manifest.json",
    ),
    (
        "graph_scale_result_comparison",
        "Graph-Scale Result Comparison",
        PROJECT_ROOT
        / "data"
        / "validation"
        / "graph_scale_result_comparison_manifest.json",
    ),
    (
        "road_evidence_priority",
        "Road Evidence Priority",
        PROJECT_ROOT / "data" / "road" / "road_evidence_priority_manifest.json",
    ),
    (
        "road_source_readiness",
        "Road Source Readiness",
        PROJECT_ROOT / "data" / "road" / "road_source_readiness_manifest.json",
    ),
    (
        "road_source_decision",
        "Road Source Decisions",
        PROJECT_ROOT / "data" / "road" / "road_source_decision_manifest.json",
    ),
    (
        "parameter_evidence_priority",
        "Parameter Evidence Priority",
        PROJECT_ROOT / "data" / "parameters" / "parameter_evidence_priority_manifest.json",
    ),
    (
        "parameter_source_readiness",
        "Parameter Source Readiness",
        PROJECT_ROOT
        / "data"
        / "parameters"
        / "parameter_source_readiness_manifest.json",
    ),
    (
        "parameter_source_decision",
        "Parameter Source Decisions",
        PROJECT_ROOT
        / "data"
        / "parameters"
        / "parameter_source_decision_manifest.json",
    ),
    (
        "rail_evidence_priority",
        "Rail Evidence Priority",
        PROJECT_ROOT / "data" / "rail" / "rail_evidence_priority_manifest.json",
    ),
    (
        "rail_fetch_readiness",
        "Rail Fetch Readiness",
        PROJECT_ROOT / "data" / "rail" / "rail_fetch_readiness_manifest.json",
    ),
    (
        "rail_source_decision",
        "Rail Source Decisions",
        PROJECT_ROOT / "data" / "rail" / "rail_source_decision_manifest.json",
    ),
    (
        "validation_benchmark_readiness",
        "Validation Benchmark Readiness",
        PROJECT_ROOT / "data" / "validation" / "validation_benchmark_readiness_manifest.json",
    ),
    (
        "validation_benchmark_decision",
        "Validation Benchmark Decision",
        PROJECT_ROOT / "data" / "validation" / "validation_benchmark_decision_manifest.json",
    ),
    (
        "validation_strategy_readiness",
        "Validation Strategy Readiness",
        PROJECT_ROOT / "data" / "validation" / "validation_strategy_readiness_manifest.json",
    ),
    (
        "sensitivity_method_decision",
        "Sensitivity Method Decision",
        PROJECT_ROOT / "data" / "validation" / "sensitivity_method_decision_manifest.json",
    ),
    (
        "sensitivity_strategy_readiness",
        "Sensitivity Strategy Readiness",
        PROJECT_ROOT / "data" / "validation" / "sensitivity_strategy_readiness_manifest.json",
    ),
    (
        "experiment_strategy_readiness",
        "Experiment Strategy Readiness",
        PROJECT_ROOT / "data" / "manifests" / "experiment_strategy_readiness_manifest.json",
    ),
    (
        "experiment_design_decision",
        "Experiment Design Decision",
        PROJECT_ROOT / "data" / "manifests" / "experiment_design_decision_manifest.json",
    ),
    (
        "figure_table_review",
        "Figure/Table Review",
        PROJECT_ROOT / "data" / "manifests" / "figure_table_review_manifest.json",
    ),
    (
        "reproducibility_review",
        "Reproducibility Review",
        PROJECT_ROOT / "data" / "validation" / "reproducibility_review_manifest.json",
    ),
    (
        "acceptance_decision_templates",
        "Acceptance Decision Templates",
        PROJECT_ROOT / "data" / "manifests" / "acceptance_decision_template_manifest.json",
    ),
    (
        "formal_acceptance_blocker_queue",
        "Formal Acceptance Blocker Queue",
        PROJECT_ROOT / "data" / "manifests" / "formal_acceptance_blocker_queue_manifest.json",
    ),
    (
        "acceptance_task_assignments",
        "Acceptance Task Assignments",
        PROJECT_ROOT / "data" / "manifests" / "acceptance_task_assignments_manifest.json",
    ),
    (
        "formal_acceptance_evidence_matrix",
        "Formal Evidence Matrix",
        PROJECT_ROOT / "data" / "manifests" / "formal_acceptance_evidence_matrix_manifest.json",
    ),
    (
        "formal_acceptance_pre_review",
        "Formal Acceptance Pre-Review",
        PROJECT_ROOT
        / "data"
        / "manifests"
        / "draft_acceptance"
        / "formal_acceptance_pre_review_manifest.json",
    ),
    (
        "formal_acceptance_package_audit",
        "Formal Package Audit",
        PROJECT_ROOT / "data" / "manifests" / "formal_acceptance_package_audit.json",
    ),
    (
        "formal_evidence_path_audit",
        "Formal Evidence Path Audit",
        PROJECT_ROOT / "data" / "manifests" / "formal_evidence_path_audit.json",
    ),
    (
        "agent_review_path_audit",
        "Agent Review Path Audit",
        PROJECT_ROOT / "data" / "manifests" / "agent_review_path_audit.json",
    ),
    (
        "tracked_artifact_audit",
        "Tracked Artifact Audit",
        PROJECT_ROOT / "data" / "validation" / "tracked_artifact_audit_manifest.json",
    ),
    (
        "current_goal_completion_audit",
        "Current Goal Completion Audit",
        PROJECT_ROOT / "data" / "manifests" / "current_goal_completion_audit.json",
    ),
    (
        "publication_readiness_audit",
        "Publication Readiness Audit",
        PROJECT_ROOT / "data" / "manifests" / "publication_readiness_audit.json",
    ),
)
ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY = (
    "Sub-agent records are review aids. They do not replace formal acceptance "
    "artifacts, source-backed reviewer decisions, calibrated validation, or "
    "operational routing approval."
)


@dataclass(frozen=True)
class ReviewAgentDefinition:
    """Configuration for one deterministic review-agent role."""

    agent_id: str
    role_name: str
    gate_ids: tuple[str, ...]
    mission: str
    non_ready_status: str
    final_acceptance_artifacts: tuple[str, ...]
    source_paths: tuple[str, ...]
    reviewed_inputs: tuple[str, ...]
    review_packet_paths: tuple[str, ...]
    decision_rules: tuple[str, ...]
    required_actions: tuple[str, ...]
    risks: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable definition."""

        return {
            "agent_id": self.agent_id,
            "role_name": self.role_name,
            "gate_ids": list(self.gate_ids),
            "mission": self.mission,
            "non_ready_status": self.non_ready_status,
            "final_acceptance_artifacts": list(self.final_acceptance_artifacts),
            "source_paths": list(self.source_paths),
            "reviewed_inputs": list(self.reviewed_inputs),
            "review_packet_paths": list(self.review_packet_paths),
            "decision_rules": list(self.decision_rules),
            "required_actions": list(self.required_actions),
            "risks": list(self.risks),
            "non_fabrication_rule": (
                "Do not mark accepted unless the final-study readiness gate is "
                "already ready with evidence-backed acceptance records."
            ),
        }


REVIEW_AGENT_DEFINITIONS: tuple[ReviewAgentDefinition, ...] = (
    ReviewAgentDefinition(
        agent_id="pilot_region_privacy_review_agent",
        role_name="Pilot Region & Privacy Review Agent",
        gate_ids=("pilot_region_accepted",),
        mission=(
            "Review pilot-region choice, privacy risk, sensitive geography, "
            "re-identification risk, and whether region use is acceptable."
        ),
        non_ready_status="needs_human_review",
        final_acceptance_artifacts=("data/manifests/pilot_acceptance.json",),
        source_paths=(
            "data/regions/pilot_region.yaml",
            "docs/pilot_region_data_card.md",
            "data/manifests/pilot_privacy_review_packet.csv",
            "data/manifests/pilot_privacy_review_manifest.json",
        ),
        reviewed_inputs=(
            "data/regions/pilot_region.yaml",
            "docs/pilot_region_data_card.md",
            "docs/current_goal_completion_audit.md",
            "data/manifests/current_goal_completion_audit.json",
            "data/manifests/pilot_privacy_review_packet.csv",
            "data/manifests/pilot_privacy_review_manifest.json",
            "docs/pilot_privacy_review_packet.md",
        ),
        review_packet_paths=(
            "data/manifests/pilot_privacy_review_packet.csv",
            "docs/review_packets/pilot_region_accepted.md",
        ),
        decision_rules=(
            "Accept only after privacy, sensitivity, and not-operational claim boundaries are reviewed.",
            "Treat missing privacy decision as needs_human_review, not accepted.",
        ),
        required_actions=(
            "Record an explicit pilot acceptance decision with reviewer, scope, privacy review, evidence paths, and not-operational claim boundary.",
        ),
        risks=(
            "Sensitive geography or destination abstraction could be overinterpreted as operational routing.",
            "Region choice may not be reusable unless privacy and scope are documented.",
        ),
    ),
    ReviewAgentDefinition(
        agent_id="osm_source_license_provenance_review_agent",
        role_name="OSM / Source / License / Provenance Review Agent",
        gate_ids=("data_provenance",),
        mission=(
            "Review OpenStreetMap and other source provenance, license terms, "
            "attribution duties, derivative-use constraints, snapshots, and reproducibility."
        ),
        non_ready_status="blocked",
        final_acceptance_artifacts=("data/manifests/provenance_acceptance.json",),
        source_paths=(
            "data/manifests/source_provenance_manifest.json",
            "data/manifests/source_license_review_packet.csv",
            "data/manifests/source_url_review_packet.csv",
            "data/manifests/source_url_remediation_packet.csv",
            "data/manifests/source_provenance_priority_packet.csv",
            "data/manifests/source_context_cache_request_packet.csv",
            "data/manifests/source_context_cache_decision_packet.csv",
            "data/manifests/reproducibility_manifest.json",
            "data/cache/pilot_region_road_manifest.json",
            "cloned_repo_manifest.md",
        ),
        reviewed_inputs=(
            "data/manifests/source_provenance_manifest.json",
            "data/manifests/source_license_review_manifest.json",
            "data/manifests/source_url_review_manifest.json",
            "data/manifests/source_url_remediation_manifest.json",
            "data/manifests/source_provenance_priority_manifest.json",
            "data/manifests/source_context_cache_request_manifest.json",
            "data/manifests/source_context_cache_decision_manifest.json",
            "data/manifests/reproducibility_manifest.json",
            "data/manifests/current_goal_completion_audit.json",
            "docs/reproducibility_package.md",
            "cloned_repo_manifest.md",
        ),
        review_packet_paths=(
            "data/manifests/source_license_review_packet.csv",
            "data/manifests/source_url_review_packet.csv",
            "data/manifests/source_url_remediation_packet.csv",
            "data/manifests/source_provenance_priority_packet.csv",
            "data/manifests/source_context_cache_request_packet.csv",
            "data/manifests/source_context_cache_decision_packet.csv",
            "docs/review_packets/data_provenance.md",
        ),
        decision_rules=(
            "Do not assume license compatibility without cited or source-backed evidence.",
            "Block final claims while source records are pending review or context-only.",
        ),
        required_actions=(
            "Review source URLs, licenses, attribution, local snapshots, privacy abstraction, and reproducibility scope.",
            "Create data/manifests/provenance_acceptance.json only after source-backed review.",
        ),
        risks=(
            "License or attribution requirements may be incomplete.",
            "Scaffold reproducibility scope cannot support final calibrated claims.",
        ),
    ),
    ReviewAgentDefinition(
        agent_id="graph_scale_method_review_agent",
        role_name="Graph Scale Method Review Agent",
        gate_ids=("graph_scale_strategy",),
        mission=(
            "Review graph-scale computation methodology, reproducible node/edge "
            "coverage metrics, route-parity diagnostics, and corridor/full-graph assumptions."
        ),
        non_ready_status="needs_human_review",
        final_acceptance_artifacts=("data/manifests/graph_scale_acceptance.json",),
        source_paths=(
            "results/realworld_pilot/pilot_full_manifest.json",
            "data/validation/graph_scale_route_comparison.csv",
            "data/validation/graph_scale_alternate_routes.csv",
            "data/validation/graph_scale_multi_corridor_routes.csv",
            "data/validation/full_graph_runtime_readiness_packet.csv",
            "data/validation/graph_scale_manifest_audit.csv",
            "data/validation/graph_scale_strategy_readiness_packet.csv",
            "data/validation/graph_scale_result_comparison.csv",
        ),
        reviewed_inputs=(
            "docs/analysis_corridor_method_note.md",
            "docs/graph_scale_diagnostics.md",
            "docs/graph_scale_manifest_audit.md",
            "data/validation/graph_scale_review_packet.csv",
            "data/validation/full_graph_runtime_readiness_manifest.json",
            "data/validation/graph_scale_manifest_audit_manifest.json",
            "data/validation/graph_scale_strategy_readiness_manifest.json",
            "data/validation/graph_scale_result_comparison.csv",
            "data/validation/graph_scale_result_comparison_manifest.json",
        ),
        review_packet_paths=(
            "data/validation/graph_scale_review_packet.csv",
            "data/validation/full_graph_runtime_readiness_packet.csv",
            "data/validation/graph_scale_manifest_audit.csv",
            "data/validation/graph_scale_strategy_readiness_packet.csv",
            "docs/review_packets/graph_scale_strategy.md",
        ),
        decision_rules=(
            "Accept only one graph-scale strategy whose node/edge counts match the pilot manifest.",
            "Do not treat route-parity diagnostics alone as final graph-scale acceptance.",
        ),
        required_actions=(
            "Choose and document reduced-corridor, multi-corridor, or full-graph strategy.",
            "Create graph_scale_acceptance.json with matching graph counts and evidence paths.",
        ),
        risks=(
            "Reduced corridor may omit detours or alternate-route behavior.",
            "Full graph may be computationally expensive without accepted sampling strategy.",
        ),
    ),
    ReviewAgentDefinition(
        agent_id="road_rail_parameter_evidence_agent",
        role_name="Road / Rail / Parameter Evidence Agent",
        gate_ids=("cached_osm_input", "parameter_evidence", "rail_evidence"),
        mission=(
            "Review road overrides, rail assumptions, speeds, capacities, costs, "
            "weights, dispatch parameters, and parameter provenance."
        ),
        non_ready_status="blocked",
        final_acceptance_artifacts=(
            "data/parameters/road_class_overrides.csv",
            "data/parameters/parameter_acceptance.csv",
        ),
        source_paths=(
            "data/parameters/parameter_sources.csv",
            "data/parameters/road_class_overrides_draft.csv",
            "data/parameters/rail_service_evidence.csv",
            "data/parameters/rail_station_bindings.csv",
            "data/parameters/parameter_source_readiness_packet.csv",
            "data/parameters/parameter_evidence_priority_packet.csv",
            "data/parameters/parameter_source_decision_packet.csv",
            "data/road/road_source_readiness_packet.csv",
            "data/road/road_source_decision_packet.csv",
            "data/road/road_evidence_priority_packet.csv",
            "data/rail/rail_fetch_readiness_packet.csv",
            "data/rail/rail_evidence_priority_packet.csv",
            "data/rail/rail_source_decision_packet.csv",
        ),
        reviewed_inputs=(
            "data/parameters/parameter_evidence_review_packet.csv",
            "data/parameters/parameter_evidence_source_request_packet.csv",
            "data/parameters/parameter_source_readiness_manifest.json",
            "data/parameters/parameter_evidence_priority_manifest.json",
            "data/parameters/parameter_source_decision_manifest.json",
            "data/parameters/road_evidence_review_packet.csv",
            "data/road/road_evidence_source_request_packet.csv",
            "data/road/road_source_readiness_manifest.json",
            "data/road/road_source_decision_manifest.json",
            "data/road/road_evidence_priority_manifest.json",
            "data/parameters/rail_evidence_review_packet.csv",
            "data/rail/rail_timing_source_request_packet.csv",
            "data/rail/rail_fetch_readiness_manifest.json",
            "data/rail/rail_evidence_priority_manifest.json",
            "data/rail/rail_source_decision_manifest.json",
        ),
        review_packet_paths=(
            "data/parameters/parameter_evidence_review_packet.csv",
            "data/parameters/parameter_source_readiness_packet.csv",
            "data/parameters/parameter_evidence_priority_packet.csv",
            "data/parameters/parameter_source_decision_packet.csv",
            "data/parameters/road_evidence_review_packet.csv",
            "data/road/road_source_readiness_packet.csv",
            "data/road/road_source_decision_packet.csv",
            "data/road/road_evidence_priority_packet.csv",
            "data/parameters/rail_evidence_review_packet.csv",
            "data/rail/rail_fetch_readiness_packet.csv",
            "data/rail/rail_evidence_priority_packet.csv",
            "data/rail/rail_source_decision_packet.csv",
            "docs/review_packets/cached_osm_input.md",
            "docs/review_packets/parameter_evidence.md",
            "docs/review_packets/rail_evidence.md",
        ),
        decision_rules=(
            "Flag unsupported parameters; never accept weak defaults silently.",
            "Use reviewed overrides or accepted weak-parameter records before final claims.",
        ),
        required_actions=(
            "Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.",
            "Create road_class_overrides.csv and parameter_acceptance.csv only after review.",
        ),
        risks=(
            "Road capacity and speed fallbacks are proxy values.",
            "Rail timing and capacity evidence remains assumption or sensitivity-only in the scaffold.",
            "Weak core parameters can determine the policy winner.",
        ),
    ),
    ReviewAgentDefinition(
        agent_id="validation_benchmark_strategy_agent",
        role_name="Validation Benchmark Strategy Agent",
        gate_ids=("validation_package",),
        mission=(
            "Review validation benchmark design, metrics, thresholds, sampling "
            "strategy, failure cases, and implemented-versus-proposed validation scope."
        ),
        non_ready_status="needs_human_review",
        final_acceptance_artifacts=("data/manifests/validation_acceptance.json",),
        source_paths=(
            "data/validation/validation_review_packet.csv",
            "data/validation/validation_strategy_readiness_packet.csv",
            "data/validation/validation_benchmark_readiness_packet.csv",
            "data/validation/validation_benchmark_decision_packet.csv",
            "data/validation/osrm_route_benchmark_manifest.json",
            "data/validation/accessibility_loss.csv",
            "data/validation/canonical_route_road_evidence_exposure.csv",
        ),
        reviewed_inputs=(
            "docs/validation_review_packet.md",
            "docs/validation_strategy_readiness_packet.md",
            "docs/validation_benchmark_readiness_packet.md",
            "docs/validation_benchmark_decision_packet.md",
            "docs/osrm_route_benchmark_manifest.md",
            "data/validation/validation_review_manifest.json",
            "data/validation/validation_strategy_readiness_manifest.json",
            "data/validation/validation_benchmark_readiness_manifest.json",
            "data/validation/validation_benchmark_decision_manifest.json",
        ),
        review_packet_paths=(
            "data/validation/validation_review_packet.csv",
            "data/validation/validation_strategy_readiness_packet.csv",
            "data/validation/validation_benchmark_readiness_packet.csv",
            "data/validation/validation_benchmark_decision_packet.csv",
            "docs/review_packets/validation_package.md",
        ),
        decision_rules=(
            "Benchmark snapshots are plausibility checks, not ground truth.",
            "Accept only with explicit thresholds, sample scope, and failure-case handling.",
        ),
        required_actions=(
            "Review validation thresholds, benchmark scope, snapshot pinning, and failure cases.",
            "Create validation_acceptance.json after benchmark-strategy review.",
        ),
        risks=(
            "Live or unpinned route benchmarks are not reproducible enough for final claims.",
            "Plausibility checks cannot prove operational accuracy.",
        ),
    ),
    ReviewAgentDefinition(
        agent_id="sensitivity_analysis_review_agent",
        role_name="Sensitivity Analysis Review Agent",
        gate_ids=("sensitivity_analysis",),
        mission=(
            "Review sensitivity method, scenario ranges, outputs, interpretation, "
            "and whether Morris or Sobol evidence is sufficient for the target claim."
        ),
        non_ready_status="blocked",
        final_acceptance_artifacts=("data/manifests/sensitivity_acceptance.json",),
        source_paths=(
            "results/realworld_pilot/morris_manifest.json",
            "results/realworld_pilot/morris_results.csv",
            "results/realworld_pilot/morris_summary.csv",
            "data/validation/sensitivity_strategy_readiness_packet.csv",
            "data/validation/sensitivity_index_review_packet.csv",
            "data/validation/sensitivity_method_decision_packet.csv",
        ),
        reviewed_inputs=(
            "data/validation/sensitivity_review_packet.csv",
            "data/validation/sensitivity_review_manifest.json",
            "data/validation/sensitivity_index_review_manifest.json",
            "docs/sensitivity_index_review_packet.md",
            "data/validation/sensitivity_strategy_readiness_manifest.json",
            "data/validation/sensitivity_method_decision_manifest.json",
            "docs/sensitivity_method_decision_packet.md",
            "scripts/run_sensitivity.py",
        ),
        review_packet_paths=(
            "data/validation/sensitivity_review_packet.csv",
            "data/validation/sensitivity_index_review_packet.csv",
            "data/validation/sensitivity_strategy_readiness_packet.csv",
            "data/validation/sensitivity_method_decision_packet.csv",
            "docs/review_packets/sensitivity_analysis.md",
        ),
        decision_rules=(
            "Do not interpret scaffold Morris screening as final calibrated sensitivity evidence.",
            "Accept only if parameter ranges, outputs, and Sobol/Morris decision are justified.",
        ),
        required_actions=(
            "Review parameter ranges and decide whether Morris is enough or Sobol is required.",
            "Create sensitivity_acceptance.json after final input and graph scope are accepted.",
        ),
        risks=(
            "Sensitivity outputs are scaffold-level while upstream evidence gates remain blocked.",
            "Wrong parameter ranges can reverse strategy-regime conclusions.",
        ),
    ),
    ReviewAgentDefinition(
        agent_id="full_experiment_package_agent",
        role_name="Full Experiment Package Agent",
        gate_ids=("full_experiment_output",),
        mission=(
            "Review scripts, configs, manifests, outputs, checksums where available, "
            "scenario-policy-seed design, and run instructions for the experiment package."
        ),
        non_ready_status="blocked",
        final_acceptance_artifacts=("data/manifests/experiment_acceptance.json",),
        source_paths=(
            "results/realworld_pilot/pilot_full_manifest.json",
            "results/realworld_pilot/pilot_full_results.csv",
            "results/realworld_pilot/pilot_full_summary.csv",
            "data/manifests/experiment_package_review_packet.csv",
            "data/manifests/experiment_strategy_readiness_packet.csv",
            "data/manifests/experiment_design_decision_packet.csv",
        ),
        reviewed_inputs=(
            "scripts/run_pilot_experiments.py",
            "data/scenarios/disruption_scenarios.csv",
            "data/scenarios/policy_alternatives.csv",
            "data/manifests/experiment_package_review_manifest.json",
            "data/manifests/experiment_strategy_readiness_manifest.json",
            "data/manifests/experiment_design_decision_manifest.json",
            "docs/experiment_design_decision_packet.md",
        ),
        review_packet_paths=(
            "data/manifests/experiment_package_review_packet.csv",
            "data/manifests/experiment_strategy_readiness_packet.csv",
            "data/manifests/experiment_design_decision_packet.csv",
            "docs/review_packets/full_experiment_output.md",
        ),
        decision_rules=(
            "Do not accept experiment outputs before input-evidence and graph-scale gates are accepted.",
            "Expected row counts must match the pilot manifest.",
        ),
        required_actions=(
            "Regenerate or accept full outputs after input, graph-scale, and validation gates close.",
            "Create experiment_acceptance.json with matching run profile and row counts.",
        ),
        risks=(
            "Current outputs are useful scaffold runs, not final calibrated study results.",
            "Upstream input changes invalidate current experiment summaries.",
        ),
    ),
    ReviewAgentDefinition(
        agent_id="paper_report_claim_alignment_agent",
        role_name="Paper / Report Claim Alignment Agent",
        gate_ids=("manuscript_report_alignment",),
        mission=(
            "Review paper/report claims against available evidence and flag unsupported, "
            "overstated, stale, or operationally risky claims."
        ),
        non_ready_status="blocked",
        final_acceptance_artifacts=("data/manifests/manuscript_acceptance.json",),
        source_paths=(
            "paper/paper_draft.md",
            "report_draft.md",
            "report.docx",
            "results/realworld_pilot/tables/figure_table_manifest.json",
            "data/manifests/claim_alignment_review_packet.csv",
            "data/manifests/figure_table_review_packet.csv",
        ),
        reviewed_inputs=(
            "scripts/audit_publication_readiness.py",
            "docs/current_goal_completion_audit.md",
            "data/manifests/current_goal_completion_audit.json",
            "paper/paper_draft.md",
            "report_draft.md",
            "data/manifests/claim_alignment_review_manifest.json",
            "data/manifests/figure_table_review_manifest.json",
            "docs/figure_table_review_packet.md",
        ),
        review_packet_paths=(
            "data/manifests/claim_alignment_review_packet.csv",
            "data/manifests/figure_table_review_packet.csv",
            "docs/review_packets/manuscript_report_alignment.md",
        ),
        decision_rules=(
            "Do not let manuscript claims outrun accepted evidence gates.",
            "Keep not-operational and scaffold claim boundaries visible until final acceptance.",
        ),
        required_actions=(
            "Revise or hold claims until all supporting evidence gates are accepted.",
            "Create manuscript_acceptance.json after claim-by-claim review.",
        ),
        risks=(
            "Paper/report can overstate scaffold results as calibrated real-world findings.",
            "Figures and tables can imply finality before evidence gates close.",
        ),
    ),
    ReviewAgentDefinition(
        agent_id="clean_checkout_reproducibility_agent",
        role_name="Clean-Checkout Reproducibility Agent",
        gate_ids=("reproducibility",),
        mission=(
            "Perform or script clean-checkout reproduction, smoke validation, import-boundary checks, "
            "and artifact regeneration without faking a successful full reproduction."
        ),
        non_ready_status="blocked",
        final_acceptance_artifacts=("data/manifests/reproducibility_acceptance.json",),
        source_paths=(
            "data/manifests/reproducibility_manifest.json",
            "data/validation/reproducibility_review_manifest.json",
            "data/validation/reproducibility_smoke_manifest.json",
            "data/validation/clean_checkout_reproducibility_smoke_manifest.json",
            "data/validation/tracked_artifact_audit_manifest.json",
            "data/manifests/current_goal_completion_audit.json",
            "docs/reproducibility_package.md",
            "requirements.txt",
        ),
        reviewed_inputs=(
            "docs/reproducibility_package.md",
            "data/manifests/reproducibility_manifest.json",
            "data/manifests/current_goal_completion_audit.json",
            "data/validation/reproducibility_review_packet.csv",
            "data/validation/tracked_artifact_audit.csv",
            "scripts/audit_plan_artifacts.py",
        ),
        review_packet_paths=(
            "data/validation/reproducibility_review_packet.csv",
            "data/validation/tracked_artifact_audit.csv",
            "docs/review_packets/reproducibility.md",
        ),
        decision_rules=(
            "If full clean-checkout reproduction is too expensive, record smoke scope and keep full reproduction blocked.",
            "Do not treat local passing tests as clean-checkout reproduction.",
        ),
        required_actions=(
            "Run or document clean-checkout validation with command log and artifact regeneration evidence.",
            "Create reproducibility_acceptance.json only after accepted reproduction scope is complete.",
        ),
        risks=(
            "Local dirty-tree validation can miss missing files or untracked artifacts.",
            "Scaffold reproducibility manifests do not prove final package reproducibility.",
        ),
    ),
    ReviewAgentDefinition(
        agent_id="final_independent_audit_agent",
        role_name="Final Independent Audit Agent",
        gate_ids=("final_audit",),
        mission=(
            "Aggregate all acceptance records, verify every gate is accepted or blocked, "
            "and produce the final audit summary only after pre-final gates close."
        ),
        non_ready_status="blocked",
        final_acceptance_artifacts=(
            "docs/final_study_audit.md",
            "data/manifests/final_audit_acceptance.json",
        ),
        source_paths=(
            "docs/current_goal_completion_audit.md",
            "data/manifests/current_goal_completion_audit.json",
            "data/manifests/acceptance_orchestration_manifest.json",
            "data/manifests/formal_acceptance_evidence_matrix.csv",
            "data/manifests/formal_acceptance_package_audit.json",
        ),
        reviewed_inputs=(
            "docs/current_goal_completion_audit.md",
            "data/manifests/current_goal_completion_audit.json",
            "data/manifests/acceptance_orchestration_manifest.json",
            "data/manifests/formal_acceptance_evidence_matrix_manifest.json",
            "data/manifests/formal_acceptance_package_audit.json",
            "scripts/audit_final_study_readiness.py",
        ),
        review_packet_paths=("docs/review_packets/final_audit.md",),
        decision_rules=(
            "Keep final_study_ready false unless every pre-final gate is accepted with evidence.",
            "Do not create docs/final_study_audit.md as a proxy for actual acceptance.",
        ),
        required_actions=(
            "After all pre-final gates are ready, write the independent prompt-to-artifact final audit.",
            "Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.",
        ),
        risks=(
            "A final audit created before pre-final gate closure would launder incomplete evidence.",
            "Proxy signals such as tests or generated manifests are not enough for final completion.",
        ),
    ),
)


def write_acceptance_orchestration_outputs(
    *,
    output_dir: Path = DEFAULT_AGENT_REVIEW_DIR,
    review_packet_dir: Path = DEFAULT_REVIEW_PACKET_DIR,
    manifest_path: Path = DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH,
    agent_definition_path: Path = DEFAULT_AGENT_DEFINITION_PATH,
    agent_doc_path: Path = DEFAULT_AGENT_DOC_PATH,
    schema_path: Path = DEFAULT_ACCEPTANCE_SCHEMA_PATH,
    source_provenance_priority_manifest_path: Path = (
        DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH
    ),
    review_status_snapshot_manifests: tuple[tuple[str, str, Path], ...] = (
        DEFAULT_REVIEW_STATUS_SNAPSHOT_MANIFESTS
    ),
) -> dict[str, Any]:
    """Write definitions, per-gate records, review packets, schema, and manifest."""

    from src.realworld.final_study_readiness import audit_final_study_readiness

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    final_audit = audit_final_study_readiness()
    source_priority = _load_source_provenance_priority_summary(
        source_provenance_priority_manifest_path
    )
    review_packet_snapshots = _load_review_status_snapshots(
        review_status_snapshot_manifests
    )
    gate_map = {str(gate["gate_id"]): gate for gate in final_audit["gates"]}

    output_dir.mkdir(parents=True, exist_ok=True)
    review_packet_dir.mkdir(parents=True, exist_ok=True)
    agent_definition_path.parent.mkdir(parents=True, exist_ok=True)
    agent_doc_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    write_acceptance_record_schema(schema_path)

    agent_definition_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "claim_boundary": ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
                "agents": [agent.to_dict() for agent in REVIEW_AGENT_DEFINITIONS],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    agent_doc_path.write_text(
        build_agent_definition_markdown(),
        encoding="utf-8",
    )

    records: list[AcceptanceRecord] = []
    packet_paths: list[str] = []
    for agent in REVIEW_AGENT_DEFINITIONS:
        for gate_id in agent.gate_ids:
            gate = gate_map.get(gate_id)
            if gate is None:
                record = _missing_gate_record(agent, gate_id, generated_at)
            else:
                record = build_acceptance_record(agent, gate, generated_at)
            record_path = output_dir / f"{gate_id}__{agent.agent_id}.json"
            record_path.write_text(
                json.dumps(record.to_dict(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            acceptance_record_from_mapping(record.to_dict())
            records.append(record)

            packet_path = review_packet_dir / f"{gate_id}.md"
            packet_path.write_text(
                build_gate_review_packet(record, agent, gate),
                encoding="utf-8",
            )
            packet_paths.append(_display_path(packet_path))

    manifest = _build_manifest(
        records,
        final_audit=final_audit,
        generated_at=generated_at,
        record_dir=output_dir,
        packet_paths=packet_paths,
        agent_definition_path=agent_definition_path,
        schema_path=schema_path,
        source_provenance_priority=source_priority,
        review_packet_snapshots=review_packet_snapshots,
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    index_path = review_packet_dir / "acceptance_review_index.md"
    index_path.write_text(
        build_acceptance_review_index(manifest, records),
        encoding="utf-8",
    )
    manifest["review_index_path"] = _display_path(index_path)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def build_acceptance_record(
    agent: ReviewAgentDefinition,
    gate: Mapping[str, Any],
    generated_at: str,
) -> AcceptanceRecord:
    """Build one conservative review-agent record from a final-study gate."""

    gate_ready = bool(gate.get("ready", False))
    gate_id = str(gate.get("gate_id", ""))
    blockers = _string_list(gate.get("blockers", []))
    evidence = _dedupe_strings(
        [
            *_string_list(gate.get("evidence", [])),
            *agent.review_packet_paths,
        ]
    )
    source_paths = _dedupe_strings(
        [*agent.source_paths, *agent.final_acceptance_artifacts]
    )
    reviewed_inputs = _dedupe_strings(
        [*agent.reviewed_inputs, *_string_list(gate.get("evidence", []))]
    )

    if gate_ready:
        status = "accepted"
        can_mark_complete = True
        decision = (
            f"{agent.role_name} can mark gate {gate_id} complete because the "
            "final-study readiness audit already reports this gate as ready."
        )
        risks = tuple(agent.risks)
        required_actions: tuple[str, ...] = ()
    else:
        status = agent.non_ready_status
        can_mark_complete = False
        decision = (
            f"{agent.role_name} cannot accept gate {gate_id}; the current "
            f"final-study readiness audit reports blockers."
        )
        risks = _dedupe_strings([*agent.risks, *blockers])
        required_actions = _dedupe_strings([*agent.required_actions, *blockers])

    record = AcceptanceRecord(
        gate_id=gate_id,
        agent_id=agent.agent_id,
        agent=agent.role_name,
        status=status,
        decision=decision,
        evidence=evidence,
        source_paths=source_paths,
        reviewed_inputs=reviewed_inputs,
        review_packet_paths=agent.review_packet_paths,
        risks=risks,
        required_actions=required_actions,
        generated_at=generated_at,
        can_mark_complete=can_mark_complete,
        claim_boundary=ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
    )
    validate_acceptance_record_mapping(record.to_dict())
    return record


def summarize_acceptance_orchestration_manifest(
    path: str | Path = DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a compact status summary for goal-completion audit consumption."""

    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(manifest_path),
            "record_count": 0,
            "status_counts": {},
            "can_mark_complete_count": 0,
            "final_study_ready": False,
            "remaining_blockers": ["run scripts/run_acceptance_audit.py"],
        }
    with manifest_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, Mapping):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    records = value.get("records", [])
    if not isinstance(records, list):
        raise ValueError(f"{manifest_path} records must be a list")
    for row in records:
        if not isinstance(row, Mapping):
            raise ValueError(f"{manifest_path} records must contain JSON objects")
        # The manifest stores record summaries. Full record validation happens
        # against the per-gate JSON files when available.
    return {
        "manifest_present": True,
        "path": _display_path(manifest_path),
        "record_count": int(value.get("record_count", len(records))),
        "status_counts": dict(value.get("status_counts", {})),
        "can_mark_complete_count": int(value.get("can_mark_complete_count", 0)),
        "final_study_ready": bool(value.get("final_study_ready", False)),
        "blocked_or_review_record_count": int(
            value.get("blocked_or_review_record_count", 0)
        ),
        "remaining_blockers": _string_list(value.get("remaining_blockers", [])),
    }


def build_agent_definition_markdown() -> str:
    """Render human-readable sub-agent definitions."""

    lines = [
        "# Acceptance Review Agents",
        "",
        ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
        "",
        "These deterministic sub-agents convert final-study blockers into auditable review tasks. They do not approve the study by themselves.",
        "",
    ]
    for agent in REVIEW_AGENT_DEFINITIONS:
        lines.extend(
            [
                f"## {agent.role_name}",
                "",
                f"- Agent ID: `{agent.agent_id}`",
                f"- Gates: {', '.join(f'`{gate}`' for gate in agent.gate_ids)}",
                f"- Non-ready status: `{agent.non_ready_status}`",
                f"- Mission: {agent.mission}",
                f"- Formal acceptance artifacts: {', '.join(f'`{path}`' for path in agent.final_acceptance_artifacts)}",
                "",
                "Decision rules:",
            ]
        )
        for rule in agent.decision_rules:
            lines.append(f"- {rule}")
        lines.extend(["", "Required actions when not ready:"])
        for action in agent.required_actions:
            lines.append(f"- {action}")
        lines.append("")
    return "\n".join(lines)


def build_gate_review_packet(
    record: AcceptanceRecord,
    agent: ReviewAgentDefinition,
    gate: Mapping[str, Any] | None,
) -> str:
    """Render one human review packet for a gate-agent record."""

    gate_label = str((gate or {}).get("label", record.gate_id))
    lines = [
        f"# {gate_label} Review Packet",
        "",
        ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
        "",
        f"- Gate ID: `{record.gate_id}`",
        f"- Agent: `{record.agent}`",
        f"- Status: `{record.status}`",
        f"- Can mark complete: `{str(record.can_mark_complete).lower()}`",
        f"- Generated at: `{record.generated_at}`",
        "",
        "## Decision",
        "",
        record.decision,
        "",
        "## Reviewed Inputs",
        "",
        *_bullet_lines(record.reviewed_inputs),
        "",
        "## Evidence And Source Paths",
        "",
        *_bullet_lines(_dedupe_strings([*record.evidence, *record.source_paths])),
        "",
        "## Risks",
        "",
        *_bullet_lines(record.risks),
        "",
        "## Required Actions",
        "",
        *_bullet_lines(record.required_actions or ("No further action for this gate scope.",)),
        "",
        "## Formal Acceptance Boundary",
        "",
        "To close this final-study gate, create or update the formal acceptance artifact listed in the agent definition. Do not edit this review packet as a substitute for formal acceptance.",
        "",
        "Formal acceptance artifacts:",
        "",
        *_bullet_lines(agent.final_acceptance_artifacts),
        "",
    ]
    if gate:
        lines.extend(
            [
                "## Current Final-Study Gate Details",
                "",
                "```json",
                json.dumps(gate, indent=2, sort_keys=True),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def build_acceptance_review_index(
    manifest: Mapping[str, Any],
    records: Iterable[AcceptanceRecord],
) -> str:
    """Render the aggregate human review index."""

    lines = [
        "# Acceptance Review Index",
        "",
        ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
        "",
        f"- Final-study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Record count: {manifest.get('record_count', 0)}",
        f"- Can-mark-complete records: {manifest.get('can_mark_complete_count', 0)}",
        "",
        "| Gate | Agent | Status | Can Mark Complete | Required Action Count |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{record.gate_id}`",
                    record.agent,
                    f"`{record.status}`",
                    f"`{str(record.can_mark_complete).lower()}`",
                    str(len(record.required_actions)),
                ]
            )
            + " |"
        )
    source_priority = manifest.get("source_provenance_priority")
    if isinstance(source_priority, Mapping):
        lines.extend(_source_provenance_priority_index_lines(source_priority))
    review_packet_snapshots = manifest.get("review_packet_snapshots")
    if isinstance(review_packet_snapshots, list):
        lines.extend(_review_packet_snapshot_index_lines(review_packet_snapshots))
    lines.extend(
        [
            "",
            "## Remaining Blockers",
            "",
            *_bullet_lines(_string_list(manifest.get("remaining_blockers", []))),
            "",
        ]
    )
    return "\n".join(lines)


def _missing_gate_record(
    agent: ReviewAgentDefinition,
    gate_id: str,
    generated_at: str,
) -> AcceptanceRecord:
    record = AcceptanceRecord(
        gate_id=gate_id,
        agent_id=agent.agent_id,
        agent=agent.role_name,
        status="blocked",
        decision=f"{agent.role_name} cannot review missing gate {gate_id}.",
        evidence=agent.review_packet_paths,
        source_paths=agent.source_paths,
        reviewed_inputs=agent.reviewed_inputs or agent.source_paths,
        review_packet_paths=agent.review_packet_paths,
        risks=("The final-study audit did not expose this expected gate.",),
        required_actions=("Update final_study_readiness gate definitions or agent mapping.",),
        generated_at=generated_at,
        can_mark_complete=False,
        claim_boundary=ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
    )
    validate_acceptance_record_mapping(record.to_dict())
    return record


def _build_manifest(
    records: list[AcceptanceRecord],
    *,
    final_audit: Mapping[str, Any],
    generated_at: str,
    record_dir: Path,
    packet_paths: list[str],
    agent_definition_path: Path,
    schema_path: Path,
    source_provenance_priority: Mapping[str, Any],
    review_packet_snapshots: list[Mapping[str, Any]],
) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for record in records:
        status_counts[record.status] = status_counts.get(record.status, 0) + 1
    blocked_or_review = [
        record
        for record in records
        if record.status in {"blocked", "needs_human_review"}
    ]
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "claim_boundary": ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
        "final_study_ready": bool(final_audit.get("final_study_ready", False)),
        "final_study_verdict": final_audit.get("verdict", ""),
        "record_count": len(records),
        "status_counts": status_counts,
        "can_mark_complete_count": sum(
            1 for record in records if record.can_mark_complete
        ),
        "blocked_or_review_record_count": len(blocked_or_review),
        "agent_definition_path": _display_path(agent_definition_path),
        "schema_path": _display_path(schema_path),
        "record_dir": _display_path(record_dir),
        "review_packet_paths": sorted(set(packet_paths)),
        "source_provenance_priority": dict(source_provenance_priority),
        "review_packet_snapshots": [dict(snapshot) for snapshot in review_packet_snapshots],
        "records": [
            {
                "gate_id": record.gate_id,
                "agent_id": record.agent_id,
                "agent": record.agent,
                "status": record.status,
                "can_mark_complete": record.can_mark_complete,
                "record_path": _display_path(
                    record_dir / f"{record.gate_id}__{record.agent_id}.json"
                ),
                "required_action_count": len(record.required_actions),
                "risk_count": len(record.risks),
            }
            for record in records
        ],
        "remaining_blockers": _dedupe_strings(
            [
                *[
                    f"{record.gate_id}: {action}"
                    for record in blocked_or_review
                    for action in record.required_actions
                ],
                *_string_list(final_audit.get("remaining_blockers", [])),
            ]
        ),
    }


def _load_review_status_snapshots(
    specs: tuple[tuple[str, str, Path], ...],
) -> list[dict[str, Any]]:
    """Load compact non-acceptance status snapshots for reviewer triage."""

    snapshots: list[dict[str, Any]] = []
    for snapshot_id, label, path in specs:
        snapshots.append(_load_review_status_snapshot(snapshot_id, label, path))
    return snapshots


def _load_review_status_snapshot(
    snapshot_id: str,
    label: str,
    path: Path,
) -> dict[str, Any]:
    """Load one review-packet manifest into a stable summary row."""

    base: dict[str, Any] = {
        "snapshot_id": snapshot_id,
        "label": label,
        "path": _display_path(path),
        "manifest_present": path.exists(),
        "manifest_valid": False,
        "row_count": 0,
        "blocking_count": 0,
        "human_review_count": 0,
        "gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "status_counts": {},
        "remaining_blockers": [],
        "review_items": [],
    }
    if not path.exists():
        base["remaining_blockers"] = [f"{label} manifest is absent"]
        return base
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        base["remaining_blockers"] = [f"{label} manifest is invalid JSON: {exc}"]
        return base

    base["manifest_valid"] = True
    base["row_count"] = _first_int(
        data,
        (
            "row_count",
            "task_count",
            "record_count",
            "gate_count",
            "formal_gate_count",
            "artifact_count",
            "json_template_count",
        ),
    )
    status_counts = _status_counts(data)
    base["blocking_count"] = _first_int(
        data,
        (
            "blocking_request_count",
            "blocking_decision_count",
            "blocking_priority_count",
            "blocking_review_count",
            "blocking_source_count",
            "blocked_gate_count",
            "invalid_gate_count",
            "blocking_issue_count",
            "blocking_change_count",
            "missing_snapshot_or_context_only_count",
            "unreachable_or_error_count",
            "template_or_placeholder_count",
            "missing_required_path_count",
            "missing_local_evidence_count",
            "placeholder_evidence_count",
            "empty_evidence_record_count",
        ),
    )
    if base["blocking_count"] == 0:
        base["blocking_count"] = _status_prefix_count(status_counts, ("blocked",))
    base["human_review_count"] = _first_int(
        data,
        (
            "human_review_request_count",
            "human_review_decision_count",
            "human_review_priority_count",
            "human_review_count",
            "human_review_source_count",
            "human_decision_required_count",
            "review_required_count",
            "requires_reviewer_confirmation_count",
            "requires_human_review_count",
        ),
    )
    if base["human_review_count"] == 0:
        base["human_review_count"] = _status_prefix_count(
            status_counts,
            ("needs_human_review", "needs_review"),
        )
    base["gate_closure_candidate_count"] = _first_int(
        data,
        (
            "provenance_gate_closure_candidate_count",
            "graph_scale_gate_closure_candidate_count",
            "benchmark_gate_closure_candidate_count",
            "validation_gate_closure_candidate_count",
            "sensitivity_gate_closure_candidate_count",
            "experiment_gate_closure_candidate_count",
            "acceptance_gate_closure_candidate_count",
        ),
    )
    base["publication_ready"] = bool(data.get("publication_ready", False))
    base["can_mark_complete"] = bool(
        data.get("can_mark_complete", data.get("acceptance_ready", False))
    )
    base["status_counts"] = status_counts
    base["remaining_blockers"] = list(_string_list(data.get("remaining_blockers", [])))
    base["review_items"] = list(_string_list(data.get("review_items", [])))
    base["result_scope"] = str(data.get("result_scope", ""))
    return base


def _load_source_provenance_priority_summary(path: Path) -> dict[str, Any]:
    """Load compact source-provenance triage status for the review index."""

    if not path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(path),
            "row_count": 0,
            "blocking_source_count": 0,
            "human_review_source_count": 0,
            "context_only_source_count": 0,
            "cached_snapshot_source_count": 0,
            "repository_input_source_count": 0,
            "provenance_gate_closure_candidate_count": 0,
            "can_mark_complete": False,
            "publication_ready": False,
            "remaining_blockers": [
                "source provenance priority manifest is absent"
            ],
            "review_items": [
                "generate the source provenance priority packet before provenance review"
            ],
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "manifest_present": True,
            "manifest_valid": False,
            "path": _display_path(path),
            "row_count": 0,
            "blocking_source_count": 0,
            "human_review_source_count": 0,
            "context_only_source_count": 0,
            "cached_snapshot_source_count": 0,
            "repository_input_source_count": 0,
            "provenance_gate_closure_candidate_count": 0,
            "can_mark_complete": False,
            "publication_ready": False,
            "remaining_blockers": [
                f"source provenance priority manifest is invalid JSON: {exc}"
            ],
            "review_items": [
                "regenerate the source provenance priority packet before provenance review"
            ],
        }
    return {
        "manifest_present": True,
        "manifest_valid": True,
        "path": _display_path(path),
        "packet_path": str(data.get("outputs", {}).get("csv", "")),
        "row_count": int(data.get("row_count", 0) or 0),
        "blocking_source_count": int(data.get("blocking_source_count", 0) or 0),
        "human_review_source_count": int(
            data.get("human_review_source_count", 0) or 0
        ),
        "context_only_source_count": int(
            data.get("context_only_source_count", 0) or 0
        ),
        "cached_snapshot_source_count": int(
            data.get("cached_snapshot_source_count", 0) or 0
        ),
        "repository_input_source_count": int(
            data.get("repository_input_source_count", 0) or 0
        ),
        "provenance_gate_closure_candidate_count": int(
            data.get("provenance_gate_closure_candidate_count", 0) or 0
        ),
        "priority_status_counts": data.get("priority_status_counts", {}),
        "can_mark_complete": bool(data.get("can_mark_complete", False)),
        "publication_ready": bool(data.get("publication_ready", False)),
        "remaining_blockers": list(_string_list(data.get("remaining_blockers", []))),
        "review_items": list(_string_list(data.get("review_items", []))),
        "claim_boundary": str(data.get("claim_boundary", "")),
    }


def _source_provenance_priority_index_lines(
    source_priority: Mapping[str, Any],
) -> list[str]:
    """Render source-provenance triage status inside the acceptance index."""

    lines = [
        "",
        "## Source Provenance Priority Snapshot",
        "",
        (
            "This section summarizes the provenance triage packet for the "
            "data-provenance reviewer. It is not source acceptance or license "
            "approval."
        ),
        "",
        f"- Manifest: `{source_priority.get('path', '')}`",
        f"- Packet: `{source_priority.get('packet_path', '')}`",
        (
            "- Manifest present: "
            f"`{str(source_priority.get('manifest_present', False)).lower()}`"
        ),
        f"- Source rows: {source_priority.get('row_count', 0)}",
        f"- Blocking context-only sources: {source_priority.get('blocking_source_count', 0)}",
        f"- Human-review sources: {source_priority.get('human_review_source_count', 0)}",
        f"- Cached public snapshots: {source_priority.get('cached_snapshot_source_count', 0)}",
        f"- Repository input sources: {source_priority.get('repository_input_source_count', 0)}",
        (
            "- Provenance gate closure candidates: "
            f"{source_priority.get('provenance_gate_closure_candidate_count', 0)}"
        ),
        (
            "- Can mark complete from provenance triage: "
            f"`{str(source_priority.get('can_mark_complete', False)).lower()}`"
        ),
        "",
        "Required reviewer actions:",
        "",
        *_bullet_lines(_string_list(source_priority.get("review_items", []))),
    ]
    remaining_blockers = _string_list(source_priority.get("remaining_blockers", []))
    if remaining_blockers:
        lines.extend(["", "Provenance blockers:", "", *_bullet_lines(remaining_blockers)])
    return lines


def _review_packet_snapshot_index_lines(
    snapshots: list[object],
) -> list[str]:
    """Render compact review-packet status counts in the human index."""

    rows = [snapshot for snapshot in snapshots if isinstance(snapshot, Mapping)]
    lines = [
        "",
        "## Review Packet Status Snapshots",
        "",
        (
            "These manifest summaries help reviewers triage existing packets. "
            "They do not accept any gate or choose a final method."
        ),
        "",
        (
            "| Packet | Rows | Blocking | Human Review | Gate Candidates | "
            "Can Complete | Key Status Counts |"
        ),
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row.get('label', '')}`",
                    str(row.get("row_count", 0)),
                    str(row.get("blocking_count", 0)),
                    str(row.get("human_review_count", 0)),
                    str(row.get("gate_closure_candidate_count", 0)),
                    f"`{str(row.get('can_mark_complete', False)).lower()}`",
                    _status_counts_summary(row.get("status_counts", {})),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Priority blockers by packet:",
            "",
        ]
    )
    for row in rows:
        blockers = _string_list(row.get("remaining_blockers", []))
        if not blockers:
            continue
        first = blockers[0]
        extra = len(blockers) - 1
        suffix = f" (+{extra} more)" if extra > 0 else ""
        lines.append(f"- `{row.get('label', '')}`: {first}{suffix}")
    return lines


def _first_int(data: Mapping[str, Any], keys: tuple[str, ...]) -> int:
    for key in keys:
        if key in data:
            try:
                return int(data.get(key, 0) or 0)
            except (TypeError, ValueError):
                return 0
    return 0


def _status_counts(data: Mapping[str, Any]) -> dict[str, int]:
    for key in (
        "readiness_status_counts",
        "decision_status_counts",
        "priority_status_counts",
        "review_status_counts",
        "snapshot_status_counts",
        "url_status_counts",
        "remediation_status_counts",
        "cache_request_status_counts",
        "coverage_status_counts",
        "comparison_status_counts",
        "recommendation_counts",
        "action_type_counts",
        "category_counts",
        "risk_counts",
        "status_counts",
    ):
        value = data.get(key)
        if not isinstance(value, Mapping):
            continue
        output: dict[str, int] = {}
        for status, count in value.items():
            try:
                output[str(status)] = int(count)
            except (TypeError, ValueError):
                continue
        return output
    return {}


def _status_counts_summary(value: object) -> str:
    if not isinstance(value, Mapping) or not value:
        return ""
    parts = [f"{key}={count}" for key, count in sorted(value.items())]
    summary = "; ".join(parts[:3])
    extra = len(parts) - 3
    if extra > 0:
        summary = f"{summary}; +{extra} more"
    return summary


def _status_prefix_count(
    status_counts: Mapping[str, int],
    prefixes: tuple[str, ...],
) -> int:
    total = 0
    for status, count in status_counts.items():
        if any(status.startswith(prefix) for prefix in prefixes):
            total += int(count)
    return total


def _bullet_lines(values: Iterable[str]) -> list[str]:
    items = [value for value in values if str(value).strip()]
    if not items:
        return ["- None recorded."]
    return [f"- {value}" for value in items]


def _string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list | tuple):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _dedupe_strings(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        output.append(value)
    return tuple(output)


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY",
    "DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH",
    "DEFAULT_ACCEPTANCE_SCHEMA_PATH",
    "DEFAULT_AGENT_DEFINITION_PATH",
    "DEFAULT_AGENT_DOC_PATH",
    "DEFAULT_AGENT_REVIEW_DIR",
    "DEFAULT_REVIEW_STATUS_SNAPSHOT_MANIFESTS",
    "DEFAULT_REVIEW_PACKET_DIR",
    "DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH",
    "REVIEW_AGENT_DEFINITIONS",
    "ReviewAgentDefinition",
    "build_acceptance_record",
    "build_acceptance_review_index",
    "build_agent_definition_markdown",
    "build_gate_review_packet",
    "summarize_acceptance_orchestration_manifest",
    "write_acceptance_orchestration_outputs",
]
