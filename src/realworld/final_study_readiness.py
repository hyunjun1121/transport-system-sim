"""Plan-level final-study readiness audit.

This module maps the final definition of done in ``plan.md`` to concrete
repository artifacts. It deliberately separates scaffold artifact presence from
final-study readiness so generated outputs do not accidentally unlock
calibrated real-world claims.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

from src.realworld.final_audit_acceptance import summarize_final_audit_acceptance
from src.realworld.parameter_audit import audit_shipped_parameter_evidence
from src.realworld.graph_scale_acceptance import summarize_graph_scale_acceptance
from src.realworld.experiment_acceptance import summarize_experiment_acceptance
from src.realworld.manuscript_acceptance import summarize_manuscript_acceptance
from src.realworld.pilot_acceptance import summarize_pilot_acceptance
from src.realworld.provenance_acceptance import summarize_provenance_acceptance
from src.realworld.publication_readiness import audit_publication_readiness
from src.realworld.rail_evidence import (
    DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
    load_rail_service_evidence,
    summarize_rail_service_evidence,
)
from src.realworld.rail_station_binding import (
    DEFAULT_RAIL_STATION_BINDING_PATH,
    load_rail_station_bindings,
    summarize_rail_station_bindings,
)
from src.realworld.road_evidence import audit_cached_road_evidence
from src.realworld.road_evidence_diagnostics import (
    audit_cached_road_evidence_diagnostics,
)
from src.realworld.road_override_audit import (
    audit_road_class_override_application,
    audit_road_class_override_evidence,
)
from src.realworld.reproducibility_acceptance import (
    summarize_reproducibility_acceptance,
)
from src.realworld.reproducibility_review_packet import (
    DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH,
)
from src.realworld.reproducibility_smoke import summarize_reproducibility_smoke
from src.realworld.clean_checkout_smoke import summarize_clean_checkout_smoke
from src.realworld.sensitivity_acceptance import summarize_sensitivity_acceptance
from src.realworld.source_provenance import summarize_source_provenance_manifest
from src.realworld.validation_acceptance import summarize_validation_acceptance


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FINAL_AUDIT_PATH = PROJECT_ROOT / "docs" / "final_study_audit.md"
DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "claim_alignment_review_manifest.json"
)
DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_package_review_manifest.json"
)
DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_url_review_manifest.json"
)
DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_url_remediation_manifest.json"
)
DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_fetch_readiness_manifest.json"
)
DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_source_readiness_manifest.json"
)
FINAL_GATE_IDS: tuple[str, ...] = (
    "pilot_region_accepted",
    "cached_osm_input",
    "real_input_smoke",
    "graph_scale_strategy",
    "data_provenance",
    "parameter_evidence",
    "rail_evidence",
    "validation_package",
    "structured_disruptions",
    "policy_alternatives",
    "sensitivity_analysis",
    "full_experiment_output",
    "manuscript_report_alignment",
    "reproducibility",
    "final_audit",
)


def audit_final_study_readiness() -> dict[str, Any]:
    """Return a plan-to-artifact final readiness audit."""

    publication_audit = audit_publication_readiness()
    parameter_audit = audit_shipped_parameter_evidence()
    road_audit = audit_cached_road_evidence()
    road_diagnostics = audit_cached_road_evidence_diagnostics()
    road_override_audit = audit_road_class_override_evidence()
    road_override_application_audit = audit_road_class_override_application()
    rail_service_audit = summarize_rail_service_evidence(
        load_rail_service_evidence(DEFAULT_RAIL_SERVICE_EVIDENCE_PATH)
    )
    rail_station_audit = summarize_rail_station_bindings(
        load_rail_station_bindings(DEFAULT_RAIL_STATION_BINDING_PATH)
    )

    pilot_manifest = _load_json(
        PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json"
    )
    experiment_package_review_manifest = _load_json(
        DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH
    )
    morris_manifest = _load_json(
        PROJECT_ROOT / "results" / "realworld_pilot" / "morris_manifest.json"
    )
    figure_manifest = _load_json(
        PROJECT_ROOT
        / "results"
        / "realworld_pilot"
        / "tables"
        / "figure_table_manifest.json"
    )
    claim_alignment_manifest = _load_json(DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH)
    reproducibility_manifest = _load_json(
        PROJECT_ROOT / "data" / "manifests" / "reproducibility_manifest.json"
    )
    reproducibility_review_manifest = _load_json(
        DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH
    )
    source_url_review_manifest = _load_json(DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH)
    source_url_remediation_manifest = _load_json(
        DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH
    )
    rail_fetch_readiness_manifest = _load_json(DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH)
    road_source_readiness_manifest = _load_json(
        DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH
    )
    pilot_acceptance = summarize_pilot_acceptance()
    graph_scale_acceptance = summarize_graph_scale_acceptance()
    validation_acceptance = summarize_validation_acceptance()
    sensitivity_acceptance = summarize_sensitivity_acceptance()
    experiment_acceptance = summarize_experiment_acceptance()
    provenance_acceptance = summarize_provenance_acceptance()
    source_provenance = summarize_source_provenance_manifest()
    manuscript_acceptance = summarize_manuscript_acceptance()
    reproducibility_acceptance = summarize_reproducibility_acceptance()
    reproducibility_smoke = summarize_reproducibility_smoke()
    clean_checkout_smoke = summarize_clean_checkout_smoke()
    final_audit_acceptance = summarize_final_audit_acceptance()

    pre_final_gates = [
        _pilot_region_gate(pilot_acceptance),
        _cached_osm_gate(
            road_audit,
            road_override_audit,
            road_override_application_audit,
            road_diagnostics=road_diagnostics,
            road_source_readiness_manifest=road_source_readiness_manifest,
        ),
        _real_input_smoke_gate(pilot_manifest),
        _graph_scale_gate(pilot_manifest, graph_scale_acceptance),
        _data_provenance_gate(
            reproducibility_manifest,
            provenance_acceptance,
            source_provenance,
            source_url_review_manifest,
            source_url_remediation_manifest,
        ),
        _evidence_gate(
            gate_id="parameter_evidence",
            label="Parameter Evidence",
            audit=parameter_audit,
            ready_key="publication_ready",
            evidence=[
                "data/parameters/parameter_sources.csv",
                "data/parameters/parameter_evidence_review_packet.csv",
                "data/parameters/parameter_evidence_review_manifest.json",
                "data/parameters/parameter_evidence_source_request_packet.csv",
                "data/parameters/parameter_evidence_source_request_manifest.json",
                "scripts/audit_parameter_evidence.py",
                "scripts/write_parameter_review_packet.py",
                "scripts/write_parameter_evidence_source_request_packet.py",
            ],
        ),
        _rail_gate(rail_service_audit, rail_station_audit, rail_fetch_readiness_manifest),
        _validation_gate(validation_acceptance),
        _structured_disruption_gate(),
        _policy_gate(),
        _sensitivity_gate(morris_manifest, sensitivity_acceptance),
        _full_experiment_gate(
            pilot_manifest,
            experiment_acceptance,
            experiment_package_review_manifest,
        ),
        _manuscript_report_gate(
            figure_manifest,
            claim_alignment_manifest,
            publication_audit,
            manuscript_acceptance,
        ),
        _reproducibility_gate(
            reproducibility_manifest,
            reproducibility_acceptance,
            reproducibility_review_manifest,
            reproducibility_smoke,
            clean_checkout_smoke,
        ),
    ]
    gates = [
        *pre_final_gates,
        _final_audit_gate(pre_final_gates, final_audit_acceptance),
    ]
    gate_map = {gate["gate_id"]: gate for gate in gates}
    missing_gate_ids = [
        gate_id for gate_id in FINAL_GATE_IDS if gate_id not in gate_map
    ]
    final_ready = all(bool(gate["ready"]) for gate in gates) and not missing_gate_ids

    return {
        "final_study_ready": final_ready,
        "verdict": (
            "final_real_world_study_ready"
            if final_ready
            else "final_real_world_study_blocked"
        ),
        "claim_boundary": (
            "This audit checks plan-level final-study gates against current "
            "artifacts. Scaffold artifacts, passing tests, and generated "
            "figures are not sufficient unless every final gate is ready."
        ),
        "objective": (
            "Implement all plan.md requirements for a reproducible, "
            "real-world or quasi-real regional transport-resilience study "
            "without overclaiming operational accuracy."
        ),
        "gate_count": len(gates),
        "missing_gate_ids": missing_gate_ids,
        "ready_gate_ids": [gate["gate_id"] for gate in gates if gate["ready"]],
        "blocked_gate_ids": [gate["gate_id"] for gate in gates if not gate["ready"]],
        "gates": gates,
        "remaining_blockers": [
            f"{gate['label']}: {blocker}"
            for gate in gates
            for blocker in gate["blockers"]
        ],
    }


def _pilot_region_gate(pilot_acceptance: dict[str, Any]) -> dict[str, Any]:
    region_path = PROJECT_ROOT / "data" / "regions" / "pilot_region.yaml"
    data_card_path = PROJECT_ROOT / "docs" / "pilot_region_data_card.md"
    accepted = bool(pilot_acceptance["acceptance_ready"])
    return _gate(
        "pilot_region_accepted",
        "Pilot Region Accepted",
        ready=accepted,
        artifact_present=region_path.exists() and data_card_path.exists(),
        evidence=[
            "data/regions/pilot_region.yaml",
            "docs/pilot_region_data_card.md",
            "data/manifests/pilot_privacy_review_packet.csv",
            "data/manifests/pilot_privacy_review_manifest.json",
            "docs/pilot_privacy_review_packet.md",
            "data/manifests/pilot_acceptance.json",
        ],
        blockers=[] if accepted else list(pilot_acceptance["remaining_blockers"]),
        details={
            "acceptance_record_present": pilot_acceptance["record_present"],
            "acceptance_path": pilot_acceptance["path"],
            "pilot_privacy_review_packet_present": (
                PROJECT_ROOT / "data" / "manifests" / "pilot_privacy_review_packet.csv"
            ).exists(),
            "pilot_privacy_review_manifest_present": (
                PROJECT_ROOT / "data" / "manifests" / "pilot_privacy_review_manifest.json"
            ).exists(),
        },
    )


def _cached_osm_gate(
    road_audit: dict[str, Any],
    road_override_audit: dict[str, Any],
    road_override_application_audit: dict[str, Any],
    road_diagnostics: dict[str, Any] | None = None,
    road_source_readiness_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    road_diagnostics = road_diagnostics or {
        "diagnostics_ready": True,
        "top_review_candidates": [],
        "remaining_blockers": [],
    }
    ready = bool(
        road_audit["publication_ready"]
        and road_override_audit["publication_ready"]
        and road_override_application_audit["publication_ready"]
    )
    blockers = [
        *[f"road input evidence: {item}" for item in road_audit["remaining_blockers"]],
        *[
            f"road diagnostics: {item}"
            for item in road_diagnostics["remaining_blockers"]
        ],
        *[
            f"road override evidence: {item}"
            for item in road_override_audit["remaining_blockers"]
        ],
        *[
            f"road override application: {item}"
            for item in road_override_application_audit["remaining_blockers"]
        ],
    ]
    return _gate(
        "cached_osm_input",
        "Cached OSM Input",
        ready=ready,
        artifact_present=bool(road_audit["edge_count"] > 0),
        evidence=[
            "data/cache/pilot_region_road.graphml",
            "data/cache/pilot_region_road_manifest.json",
            "scripts/audit_road_evidence.py",
            "scripts/audit_road_evidence_diagnostics.py",
            "data/parameters/road_speed_evidence_candidates.csv",
            "data/parameters/road_capacity_evidence_candidates.csv",
            "data/parameters/road_evidence_review_packet.csv",
            "data/parameters/road_evidence_review_manifest.json",
            "data/road/road_evidence_source_request_packet.csv",
            "data/road/road_evidence_source_request_manifest.json",
            "data/road/road_source_readiness_packet.csv",
            "data/road/road_source_readiness_manifest.json",
            "docs/road_source_readiness_packet.md",
            "scripts/write_road_speed_evidence.py",
            "scripts/write_road_capacity_evidence.py",
            "scripts/write_road_evidence_review_packet.py",
            "scripts/write_road_evidence_source_request_packet.py",
            "scripts/write_road_source_readiness_packet.py",
            "data/parameters/road_class_overrides_draft.csv",
            "scripts/write_road_class_override_template.py",
            "scripts/audit_road_overrides.py",
        ],
        blockers=[] if ready else blockers,
        details={
            "edge_count": road_audit["edge_count"],
            "routeable_edge_count": road_audit["routeable_edge_count"],
            "road_publication_ready": road_audit["publication_ready"],
            "road_diagnostics_ready": road_diagnostics["diagnostics_ready"],
            "road_diagnostics_top_review_candidates": [
                row["highway"]
                for row in road_diagnostics["top_review_candidates"][:5]
            ],
            "road_override_draft_table_present": road_override_audit.get(
                "draft_table_present",
                False,
            ),
            "road_override_draft_row_count": road_override_audit.get(
                "draft_row_count",
                0,
            ),
            "override_application_ready": road_override_application_audit[
                "publication_ready"
            ],
            "source_readiness_manifest_present": bool(road_source_readiness_manifest),
            "source_readiness_blocking_request_count": (
                road_source_readiness_manifest or {}
            ).get("blocking_request_count", 0),
            "source_readiness_human_review_request_count": (
                road_source_readiness_manifest or {}
            ).get("human_review_request_count", 0),
            "source_readiness_status_counts": (
                road_source_readiness_manifest or {}
            ).get("readiness_status_counts", {}),
            "source_readiness_publication_ready": (
                road_source_readiness_manifest or {}
            ).get("publication_ready", False),
            "source_readiness_can_mark_complete": (
                road_source_readiness_manifest or {}
            ).get("can_mark_complete", False),
        },
    )


def _real_input_smoke_gate(pilot_manifest: dict[str, Any] | None) -> dict[str, Any]:
    policy_ids = set(_list_value(pilot_manifest, "policy_ids"))
    required = {"bus_only", "baseline_multimodal"}
    ready = bool(required <= policy_ids and pilot_manifest)
    return _gate(
        "real_input_smoke",
        "Real Input Smoke",
        ready=ready,
        artifact_present=bool(pilot_manifest),
        evidence=[
            "scripts/run_pilot_smoke.py",
            "scripts/run_full_graph_smoke.py",
            "results/realworld_pilot/pilot_full_manifest.json",
        ],
        blockers=[] if ready else ["run cached-graph bus-only and multimodal smoke"],
    )


def _graph_scale_gate(
    pilot_manifest: dict[str, Any] | None,
    graph_scale_acceptance: dict[str, Any],
) -> dict[str, Any]:
    accepted = bool(graph_scale_acceptance["acceptance_ready"])
    if not pilot_manifest:
        return _gate(
            "graph_scale_strategy",
            "Graph-Scale Strategy",
            ready=False,
            artifact_present=False,
            evidence=[
                "data/manifests/graph_scale_acceptance.json",
                "results/realworld_pilot/pilot_full_manifest.json",
            ],
            blockers=[
                "create a pilot full manifest with source and analysis graph scale",
                *([] if accepted else list(graph_scale_acceptance["remaining_blockers"])),
            ],
            details={
                "acceptance_record_present": graph_scale_acceptance["record_present"],
                "acceptance_path": graph_scale_acceptance["path"],
            },
        )
    count_blockers = _graph_scale_count_blockers(
        pilot_manifest,
        graph_scale_acceptance,
    )
    blockers = [
        *([] if accepted else list(graph_scale_acceptance["remaining_blockers"])),
        *count_blockers,
    ]
    return _gate(
        "graph_scale_strategy",
        "Graph-Scale Strategy",
        ready=accepted and not count_blockers,
        artifact_present="graph_scale" in pilot_manifest,
        evidence=[
            "data/manifests/graph_scale_acceptance.json",
            "docs/analysis_corridor_method_note.md",
            "docs/graph_scale_diagnostics.md",
            "data/validation/graph_scale_route_comparison.csv",
            "data/validation/graph_scale_route_comparison_summary.md",
            "data/validation/graph_scale_alternate_routes.csv",
            "data/validation/graph_scale_alternate_routes_summary.md",
            "data/validation/graph_scale_multi_corridor_routes.csv",
            "data/validation/graph_scale_multi_corridor_routes_summary.md",
            "data/validation/graph_scale_review_packet.csv",
            "data/validation/graph_scale_review_manifest.json",
            "data/validation/graph_scale_result_comparison.csv",
            "data/validation/graph_scale_result_comparison_manifest.json",
            "scripts/write_graph_scale_review_packet.py",
            "scripts/write_graph_scale_result_comparison.py",
            "scripts/run_graph_scale_diagnostics.py",
            "results/realworld_pilot/pilot_multi_corridor_results.csv",
            "results/realworld_pilot/pilot_multi_corridor_summary.csv",
            "results/realworld_pilot/pilot_multi_corridor_manifest.json",
            "results/realworld_pilot/pilot_multi_corridor_full_results.csv",
            "results/realworld_pilot/pilot_multi_corridor_full_summary.csv",
            "results/realworld_pilot/pilot_multi_corridor_full_manifest.json",
            "results/realworld_pilot/pilot_full_manifest.json",
        ],
        blockers=blockers,
        details={
            "acceptance_record_present": graph_scale_acceptance["record_present"],
            "acceptance_path": graph_scale_acceptance["path"],
            "acceptance_graph_scale_decision": graph_scale_acceptance.get(
                "graph_scale_decision", ""
            ),
            "acceptance_source_graph_nodes": graph_scale_acceptance.get(
                "source_graph_nodes"
            ),
            "acceptance_source_graph_edges": graph_scale_acceptance.get(
                "source_graph_edges"
            ),
            "acceptance_analysis_graph_nodes": graph_scale_acceptance.get(
                "analysis_graph_nodes"
            ),
            "acceptance_analysis_graph_edges": graph_scale_acceptance.get(
                "analysis_graph_edges"
            ),
            "analysis_graph_reduced": bool(pilot_manifest.get("analysis_graph_reduced")),
            "analysis_graph_strategy": pilot_manifest.get("analysis_graph_strategy", ""),
            "source_graph_nodes": pilot_manifest.get("source_graph_nodes"),
            "source_graph_edges": pilot_manifest.get("source_graph_edges"),
            "analysis_graph_nodes": pilot_manifest.get("graph_nodes"),
            "analysis_graph_edges": pilot_manifest.get("graph_edges"),
        },
    )


def _graph_scale_count_blockers(
    pilot_manifest: dict[str, Any],
    graph_scale_acceptance: dict[str, Any],
) -> list[str]:
    if not graph_scale_acceptance.get("record_present"):
        return []
    comparisons = (
        (
            "source_graph_nodes",
            graph_scale_acceptance.get("source_graph_nodes"),
            pilot_manifest.get("source_graph_nodes"),
        ),
        (
            "source_graph_edges",
            graph_scale_acceptance.get("source_graph_edges"),
            pilot_manifest.get("source_graph_edges"),
        ),
        (
            "analysis_graph_nodes",
            graph_scale_acceptance.get("analysis_graph_nodes"),
            pilot_manifest.get("graph_nodes"),
        ),
        (
            "analysis_graph_edges",
            graph_scale_acceptance.get("analysis_graph_edges"),
            pilot_manifest.get("graph_edges"),
        ),
    )
    mismatches = [
        f"{label}: acceptance={accepted!r}, manifest={manifest!r}"
        for label, accepted, manifest in comparisons
        if accepted != manifest
    ]
    if not mismatches:
        return []
    return [
        "graph-scale acceptance counts must match the pilot full manifest counts: "
        + "; ".join(mismatches)
    ]


def _data_provenance_gate(
    reproducibility_manifest: dict[str, Any] | None,
    provenance_acceptance: dict[str, Any],
    source_provenance: dict[str, Any],
    source_url_review_manifest: dict[str, Any] | None = None,
    source_url_remediation_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    artifact_present = bool(reproducibility_manifest) and bool(
        source_provenance.get("manifest_present", False)
    )
    scope = str((reproducibility_manifest or {}).get("scope", ""))
    remaining = list((reproducibility_manifest or {}).get("remaining_upgrades", []))
    acceptance_ready = bool(provenance_acceptance["acceptance_ready"])
    source_provenance_ready = bool(source_provenance.get("diagnostics_ready", False))
    url_manifest = source_url_review_manifest or {}
    url_remediation_manifest = source_url_remediation_manifest or {}
    scope_blocked = "scaffold" in scope.lower()
    ready = (
        artifact_present
        and source_provenance_ready
        and acceptance_ready
        and not scope_blocked
        and not remaining
    )
    blockers: list[str] = []
    if not source_provenance_ready:
        blockers.extend(source_provenance.get("remaining_blockers", []))
    if not acceptance_ready:
        blockers.extend(provenance_acceptance["remaining_blockers"])
    if scope_blocked or remaining:
        blockers.append(
            "replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance"
        )
    return _gate(
        "data_provenance",
        "Data Provenance",
        ready=ready,
        artifact_present=artifact_present,
        evidence=[
            "data/manifests/provenance_acceptance.json",
            "data/manifests/source_provenance_manifest.json",
            "data/manifests/source_license_review_packet.csv",
            "data/manifests/source_license_review_manifest.json",
            "data/manifests/source_url_review_packet.csv",
            "data/manifests/source_url_review_manifest.json",
            "data/manifests/source_url_remediation_packet.csv",
            "data/manifests/source_url_remediation_manifest.json",
            "data/manifests/reproducibility_manifest.json",
            "docs/source_license_review_packet.md",
            "docs/source_url_review_packet.md",
            "docs/source_url_remediation_packet.md",
            "docs/reproducibility_package.md",
            "docs/pilot_region_data_card.md",
            "scripts/audit_source_provenance.py",
            "scripts/write_source_license_review_packet.py",
            "scripts/write_source_url_review_packet.py",
            "scripts/write_source_url_remediation_packet.py",
        ],
        blockers=blockers,
        details={
            "acceptance_record_present": provenance_acceptance["record_present"],
            "acceptance_path": provenance_acceptance["path"],
            "source_provenance_manifest_present": source_provenance.get(
                "manifest_present",
                False,
            ),
            "source_provenance_path": source_provenance.get("path", ""),
            "source_provenance_record_count": source_provenance.get("record_count", 0),
            "source_provenance_review_status_counts": source_provenance.get(
                "review_status_counts",
                {},
            ),
            "source_license_review_packet_present": (
                PROJECT_ROOT / "data" / "manifests" / "source_license_review_packet.csv"
            ).exists(),
            "source_license_review_manifest_present": (
                PROJECT_ROOT / "data" / "manifests" / "source_license_review_manifest.json"
            ).exists(),
            "source_url_review_packet_present": (
                PROJECT_ROOT / "data" / "manifests" / "source_url_review_packet.csv"
            ).exists(),
            "source_url_review_manifest_present": (
                PROJECT_ROOT / "data" / "manifests" / "source_url_review_manifest.json"
            ).exists(),
            "source_url_live_check_performed": url_manifest.get(
                "live_check_performed",
                False,
            ),
            "source_url_status_counts": url_manifest.get("url_status_counts", {}),
            "source_url_unreachable_or_error_count": url_manifest.get(
                "unreachable_or_error_count",
                0,
            ),
            "source_url_publication_ready": url_manifest.get(
                "publication_ready",
                False,
            ),
            "source_url_can_mark_complete": url_manifest.get(
                "can_mark_complete",
                False,
            ),
            "source_url_remediation_manifest_present": (
                PROJECT_ROOT
                / "data"
                / "manifests"
                / "source_url_remediation_manifest.json"
            ).exists(),
            "source_url_remediation_row_count": url_remediation_manifest.get(
                "row_count",
                0,
            ),
            "source_url_remediation_status_counts": url_remediation_manifest.get(
                "remediation_status_counts",
                {},
            ),
            "source_url_remediation_blocking_issue_count": url_remediation_manifest.get(
                "blocking_issue_count",
                0,
            ),
            "source_url_remediation_live_check_required_count": url_remediation_manifest.get(
                "live_check_required_count",
                0,
            ),
            "source_url_remediation_publication_ready": url_remediation_manifest.get(
                "publication_ready",
                False,
            ),
            "source_url_remediation_can_mark_complete": url_remediation_manifest.get(
                "can_mark_complete",
                False,
            ),
            "scope": scope,
            "remaining_upgrade_count": len(remaining),
        },
    )


def _evidence_gate(
    *,
    gate_id: str,
    label: str,
    audit: dict[str, Any],
    ready_key: str,
    evidence: list[str],
) -> dict[str, Any]:
    ready = bool(audit[ready_key])
    return _gate(
        gate_id,
        label,
        ready=ready,
        artifact_present=True,
        evidence=evidence,
        blockers=[] if ready else list(audit.get("remaining_blockers", [])),
    )


def _rail_gate(
    rail_service_audit: dict[str, Any],
    rail_station_audit: dict[str, Any],
    rail_fetch_readiness_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ready = bool(
        rail_service_audit["publication_ready"] and rail_station_audit["binding_ready"]
    )
    blockers = [
        *[
            f"rail service evidence: {item}"
            for item in rail_service_audit["remaining_blockers"]
        ],
        *[
            f"rail station binding: {item}"
            for item in rail_station_audit["remaining_blockers"]
        ],
    ]
    return _gate(
        "rail_evidence",
        "Rail Evidence",
        ready=ready,
        artifact_present=True,
        evidence=[
            "data/parameters/rail_service_evidence.csv",
            "data/parameters/rail_station_bindings.csv",
            "data/parameters/rail_evidence_review_packet.csv",
            "data/parameters/rail_evidence_review_manifest.json",
            "data/rail/rail_timing_source_request_packet.csv",
            "data/rail/rail_timing_source_request_manifest.json",
            "data/rail/rail_fetch_readiness_packet.csv",
            "data/rail/rail_fetch_readiness_manifest.json",
            "docs/rail_fetch_readiness_packet.md",
            "scripts/audit_rail_evidence.py",
            "scripts/write_rail_evidence_review_packet.py",
            "scripts/write_rail_timing_source_request_packet.py",
            "scripts/write_rail_fetch_readiness_packet.py",
            "scripts/fetch_rail_timetable_cache.py",
            "scripts/derive_rail_headway_evidence.py",
            "scripts/derive_rail_service_evidence.py",
            "scripts/derive_rail_gtfs_evidence.py",
            "docs/rail_gtfs_cache_schema.md",
            "scripts/fetch_rail_shortest_path_cache.py",
            "scripts/derive_rail_shortest_path_evidence.py",
        ],
        blockers=[] if ready else blockers,
        details={
            "service_publication_ready": rail_service_audit["publication_ready"],
            "station_binding_ready": rail_station_audit["binding_ready"],
            "fetch_readiness_manifest_present": bool(rail_fetch_readiness_manifest),
            "fetch_readiness_blocking_request_count": (
                rail_fetch_readiness_manifest or {}
            ).get("blocking_request_count", 0),
            "fetch_readiness_status_counts": (
                rail_fetch_readiness_manifest or {}
            ).get("readiness_status_counts", {}),
            "fetch_readiness_publication_ready": (
                rail_fetch_readiness_manifest or {}
            ).get("publication_ready", False),
            "fetch_readiness_can_mark_complete": (
                rail_fetch_readiness_manifest or {}
            ).get("can_mark_complete", False),
        },
    )


def _validation_gate(validation_acceptance: dict[str, Any]) -> dict[str, Any]:
    summary_path = PROJECT_ROOT / "data" / "validation" / "validation_summary.md"
    review_manifest_path = (
        PROJECT_ROOT / "data" / "validation" / "validation_review_manifest.json"
    )
    osrm_summary_path = (
        PROJECT_ROOT / "data" / "validation" / "osrm_route_benchmark_summary.md"
    )
    osrm_manifest_path = (
        PROJECT_ROOT / "data" / "validation" / "osrm_route_benchmark_manifest.json"
    )
    accessibility_path = (
        PROJECT_ROOT / "data" / "validation" / "accessibility_loss.csv"
    )
    accessibility_summary_path = (
        PROJECT_ROOT / "data" / "validation" / "accessibility_loss_summary.md"
    )
    route_exposure_path = (
        PROJECT_ROOT
        / "data"
        / "validation"
        / "canonical_route_road_evidence_exposure.csv"
    )
    route_exposure_manifest_path = (
        PROJECT_ROOT
        / "data"
        / "validation"
        / "canonical_route_road_evidence_exposure_manifest.json"
    )
    text = _read_text(summary_path)
    review_manifest = _load_json(review_manifest_path)
    artifact_present = (
        summary_path.exists()
        and osrm_summary_path.exists()
        and osrm_manifest_path.exists()
        and accessibility_path.exists()
        and accessibility_summary_path.exists()
        and route_exposure_path.exists()
        and route_exposure_manifest_path.exists()
    )
    acceptance_ready = bool(validation_acceptance["acceptance_ready"])
    summary_scope_blocked = _validation_summary_scope_is_blocked(text)
    ready = artifact_present and acceptance_ready and not summary_scope_blocked
    blockers: list[str] = []
    if not artifact_present:
        blockers.append("create validation summary and benchmark summary artifacts")
    if not acceptance_ready:
        blockers.extend(validation_acceptance["remaining_blockers"])
    if summary_scope_blocked:
        blockers.append(
            "revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review"
        )
    return _gate(
        "validation_package",
        "Validation Package",
        ready=ready,
        artifact_present=artifact_present,
        evidence=[
            "data/manifests/validation_acceptance.json",
            "data/validation/validation_summary.md",
            "data/validation/external_route_benchmarks.csv",
            "data/validation/external_route_benchmarks_osrm.csv",
            "data/validation/osrm_route_benchmark_manifest.json",
            "data/validation/accessibility_loss.csv",
            "data/validation/accessibility_loss_summary.md",
            "data/validation/canonical_route_road_evidence_exposure.csv",
            "data/validation/canonical_route_road_evidence_exposure_manifest.json",
            "data/validation/validation_review_packet.csv",
            "data/validation/validation_review_manifest.json",
            "scripts/run_plausibility_validation.py",
            "scripts/run_accessibility_loss_analysis.py",
            "scripts/write_route_road_evidence_exposure.py",
            "scripts/run_osrm_route_benchmark.py",
            "scripts/write_osrm_snapshot_manifest.py",
            "scripts/write_validation_review_packet.py",
        ],
        blockers=[] if ready else blockers,
        details={
            "acceptance_record_present": validation_acceptance["record_present"],
            "acceptance_path": validation_acceptance["path"],
            "benchmark_strategy": validation_acceptance.get("benchmark_strategy", ""),
            "summary_scope_blocked": summary_scope_blocked,
            "review_packet_row_count": _dict_int(review_manifest, "row_count"),
            "route_road_evidence_exposure_row_count": _dict_int(
                review_manifest,
                "route_road_evidence_exposure_row_count",
            ),
            "review_packet_publication_ready": bool(
                review_manifest.get("publication_ready", False)
            )
            if review_manifest
            else False,
            "review_packet_acceptance_gate_closure_candidate_count": _dict_int(
                review_manifest,
                "acceptance_gate_closure_candidate_count",
            ),
            "review_packet_osrm_present": bool(
                review_manifest.get("optional_osrm_benchmark_present", False)
            )
            if review_manifest
            else False,
            "review_packet_osrm_manifest_present": bool(
                review_manifest.get(
                    "optional_osrm_benchmark_manifest_present",
                    False,
                )
            )
            if review_manifest
            else False,
            "review_packet_osrm_unpinned_row_count": _dict_int(
                review_manifest,
                "optional_osrm_benchmark_unpinned_row_count",
            ),
        },
    )


def _validation_summary_scope_is_blocked(text: str) -> bool:
    normalized = text.lower()
    blocked_markers = (
        "scaffold/sanity evidence",
        "not calibrated",
        "not ground truth",
    )
    return any(marker in normalized for marker in blocked_markers)


def _structured_disruption_gate() -> dict[str, Any]:
    path = PROJECT_ROOT / "data" / "scenarios" / "disruption_scenarios.csv"
    rows = _csv_rows(path)
    families = {row.get("family", "") for row in rows}
    required = {
        "random",
        "critical_link",
        "access_road",
        "last_mile",
        "rail_station_access",
        "spatial_hazard_overlay",
    }
    ready = bool(required <= families)
    return _gate(
        "structured_disruptions",
        "Structured Disruptions",
        ready=ready,
        artifact_present=path.exists(),
        evidence=["data/scenarios/disruption_scenarios.csv"],
        blockers=[] if ready else [
            "include random, critical-link, access/last-mile, station-access, and spatial disruption families"
        ],
        details={"families": sorted(families)},
    )


def _policy_gate() -> dict[str, Any]:
    path = PROJECT_ROOT / "data" / "scenarios" / "policy_alternatives.csv"
    rows = _csv_rows(path)
    policies = {row.get("policy_id", "") for row in rows}
    required = {
        "bus_only",
        "baseline_multimodal",
        "multimodal_lastmile_redundancy",
        "staggered_or_adaptive_dispatch",
    }
    ready = bool(required <= policies)
    return _gate(
        "policy_alternatives",
        "Policy Alternatives",
        ready=ready,
        artifact_present=path.exists(),
        evidence=["data/scenarios/policy_alternatives.csv"],
        blockers=[] if ready else ["include the required baseline and redundancy policies"],
        details={"policy_count": len(policies), "required_policies_present": sorted(required & policies)},
    )


def _sensitivity_gate(
    morris_manifest: dict[str, Any] | None,
    sensitivity_acceptance: dict[str, Any],
) -> dict[str, Any]:
    review_manifest = _load_json(
        PROJECT_ROOT / "data" / "validation" / "sensitivity_review_manifest.json"
    )
    artifact_present = bool(morris_manifest)
    scope = str((morris_manifest or {}).get("result_scope", ""))
    acceptance_ready = bool(sensitivity_acceptance["acceptance_ready"])
    scope_blocked = _sensitivity_scope_is_blocked(scope)
    count_blockers = _sensitivity_count_blockers(
        morris_manifest,
        sensitivity_acceptance,
    )
    ready = (
        artifact_present
        and acceptance_ready
        and not scope_blocked
        and not count_blockers
    )
    blockers: list[str] = []
    if not artifact_present:
        blockers.append("create accepted sensitivity outputs and manifest")
    if not acceptance_ready:
        blockers.extend(sensitivity_acceptance["remaining_blockers"])
    if scope_blocked:
        blockers.append(
            "accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level"
        )
    blockers.extend(count_blockers)
    return _gate(
        "sensitivity_analysis",
        "Sensitivity Analysis",
        ready=ready,
        artifact_present=artifact_present,
        evidence=[
            "data/manifests/sensitivity_acceptance.json",
            "results/realworld_pilot/morris_results.csv",
            "results/realworld_pilot/morris_summary.csv",
            "results/realworld_pilot/morris_manifest.json",
            "data/validation/sensitivity_review_packet.csv",
            "data/validation/sensitivity_review_manifest.json",
            "scripts/run_sensitivity.py",
            "scripts/audit_sensitivity_diagnostics.py",
            "scripts/write_sensitivity_review_packet.py",
        ],
        blockers=[] if ready else blockers,
        details={
            "acceptance_record_present": sensitivity_acceptance["record_present"],
            "acceptance_path": sensitivity_acceptance["path"],
            "accepted_method": sensitivity_acceptance.get("sensitivity_method", ""),
            "sobol_requirement_decision": sensitivity_acceptance.get(
                "sobol_requirement_decision", ""
            ),
            "method": (morris_manifest or {}).get("method", ""),
            "row_count": (morris_manifest or {}).get("row_count", 0),
            "summary_row_count": (morris_manifest or {}).get("summary_row_count", 0),
            "review_packet_row_count": (review_manifest or {}).get("row_count", 0),
            "review_packet_publication_ready": (review_manifest or {}).get(
                "publication_ready",
                False,
            ),
            "review_packet_acceptance_gate_closure_candidate_count": (
                review_manifest or {}
            ).get("acceptance_gate_closure_candidate_count", 0),
            "review_packet_rows_with_index_issues": (review_manifest or {}).get(
                "rows_with_index_issues",
                0,
            ),
            "review_packet_zero_mu_star_count": (review_manifest or {}).get(
                "zero_mu_star_count",
                0,
            ),
            "result_scope": scope,
            "scope_blocked": scope_blocked,
        },
    )


def _sensitivity_scope_is_blocked(scope: str) -> bool:
    normalized = scope.lower()
    return "scaffold" in normalized or "not calibrated" in normalized


def _sensitivity_count_blockers(
    morris_manifest: dict[str, Any] | None,
    sensitivity_acceptance: dict[str, Any],
) -> list[str]:
    if not morris_manifest or not sensitivity_acceptance.get("record_present"):
        return []
    comparisons = (
        (
            "row_count",
            sensitivity_acceptance.get("expected_row_count"),
            morris_manifest.get("row_count"),
        ),
        (
            "summary_row_count",
            sensitivity_acceptance.get("expected_summary_row_count"),
            morris_manifest.get("summary_row_count"),
        ),
    )
    mismatches = [
        f"{label}: acceptance={accepted!r}, manifest={manifest!r}"
        for label, accepted, manifest in comparisons
        if accepted != manifest
    ]
    if not mismatches:
        return []
    return [
        "sensitivity acceptance counts must match the Morris manifest counts: "
        + "; ".join(mismatches)
    ]


def _full_experiment_gate(
    pilot_manifest: dict[str, Any] | None,
    experiment_acceptance: dict[str, Any],
    experiment_package_review_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    artifact_present = bool(pilot_manifest)
    status = str((pilot_manifest or {}).get("design_status", ""))
    scope = str((pilot_manifest or {}).get("result_scope", ""))
    acceptance_ready = bool(experiment_acceptance["acceptance_ready"])
    scope_blocked = _experiment_scope_is_blocked(scope, status)
    count_blockers = _experiment_count_blockers(
        pilot_manifest,
        experiment_acceptance,
    )
    ready = (
        artifact_present
        and acceptance_ready
        and not scope_blocked
        and not count_blockers
    )
    blockers: list[str] = []
    if not artifact_present:
        blockers.append("create full pilot outputs and manifest")
    if not acceptance_ready:
        blockers.extend(experiment_acceptance["remaining_blockers"])
    if scope_blocked:
        blockers.append(
            "accept or regenerate full pilot outputs after input validation and graph-scale decision"
        )
    blockers.extend(count_blockers)
    review_manifest = experiment_package_review_manifest or {}
    if not review_manifest:
        blockers.append("generate experiment-package review packet before experiment acceptance")
    elif _dict_int(review_manifest, "experiment_acceptance_gate_closure_candidate_count") == 0:
        blockers.append("review experiment-package rows before formal experiment acceptance")
    return _gate(
        "full_experiment_output",
        "Full Experiment Output",
        ready=ready,
        artifact_present=artifact_present,
        evidence=[
            "data/manifests/experiment_acceptance.json",
            "results/realworld_pilot/pilot_full_results.csv",
            "results/realworld_pilot/pilot_full_summary.csv",
            "results/realworld_pilot/pilot_full_manifest.json",
            "data/manifests/experiment_package_review_packet.csv",
            "data/manifests/experiment_package_review_manifest.json",
            "docs/experiment_package_review_packet.md",
        ],
        blockers=[] if ready else blockers,
        details={
            "acceptance_record_present": experiment_acceptance["record_present"],
            "acceptance_path": experiment_acceptance["path"],
            "accepted_run_profile": experiment_acceptance.get("run_profile", ""),
            "row_count": (pilot_manifest or {}).get("row_count", 0),
            "summary_row_count": (pilot_manifest or {}).get("summary_row_count", 0),
            "design_status": status,
            "result_scope": scope,
            "scope_blocked": scope_blocked,
            "experiment_package_review_manifest_present": bool(review_manifest),
            "experiment_package_review_row_count": review_manifest.get("row_count", 0),
            "experiment_package_review_count_mismatch_count": review_manifest.get(
                "row_count_mismatch_count",
                0,
            ),
            "experiment_package_review_publication_ready": review_manifest.get(
                "publication_ready",
                False,
            ),
        },
    )


def _experiment_scope_is_blocked(scope: str, status: str) -> bool:
    normalized_scope = scope.lower()
    normalized_status = status.lower()
    return (
        "pending" in normalized_status
        or "scaffold" in normalized_scope
        or "not calibrated" in normalized_scope
    )


def _experiment_count_blockers(
    pilot_manifest: dict[str, Any] | None,
    experiment_acceptance: dict[str, Any],
) -> list[str]:
    if not pilot_manifest or not experiment_acceptance.get("record_present"):
        return []
    design = pilot_manifest.get("scenario_policy_seed_design", {})
    if not isinstance(design, dict):
        design = {}
    comparisons = (
        (
            "run_profile",
            experiment_acceptance.get("run_profile"),
            pilot_manifest.get("run_profile"),
        ),
        (
            "row_count",
            experiment_acceptance.get("expected_row_count"),
            pilot_manifest.get("row_count"),
        ),
        (
            "summary_row_count",
            experiment_acceptance.get("expected_summary_row_count"),
            pilot_manifest.get("summary_row_count"),
        ),
        (
            "policy_count",
            experiment_acceptance.get("policy_count"),
            design.get("policy_count"),
        ),
        (
            "scenario_count",
            experiment_acceptance.get("scenario_count"),
            design.get("scenario_count"),
        ),
        (
            "seed_count",
            experiment_acceptance.get("seed_count"),
            design.get("seed_count"),
        ),
    )
    mismatches = [
        f"{label}: acceptance={accepted!r}, manifest={manifest!r}"
        for label, accepted, manifest in comparisons
        if accepted != manifest
    ]
    if not mismatches:
        return []
    return [
        "experiment acceptance counts must match the pilot full manifest: "
        + "; ".join(mismatches)
    ]


def _manuscript_report_gate(
    figure_manifest: dict[str, Any] | None,
    claim_alignment_manifest: dict[str, Any] | None,
    publication_audit: dict[str, Any],
    manuscript_acceptance: dict[str, Any],
) -> dict[str, Any]:
    paper = PROJECT_ROOT / "paper" / "paper_draft.md"
    report = PROJECT_ROOT / "report_draft.md"
    docx = PROJECT_ROOT / "report.docx"
    artifact_present = paper.exists() and report.exists() and docx.exists()
    scope = str((figure_manifest or {}).get("claim_boundary", ""))
    acceptance_ready = bool(manuscript_acceptance["acceptance_ready"])
    scope_blocked = "scaffold" in scope.lower()
    ready = (
        artifact_present
        and publication_audit["publication_ready"]
        and acceptance_ready
        and not scope_blocked
    )
    blockers: list[str] = []
    if not publication_audit["publication_ready"]:
        blockers.append("close evidence gates before final paper/report claims")
    if not acceptance_ready:
        blockers.extend(manuscript_acceptance["remaining_blockers"])
    if scope_blocked:
        blockers.append(
            "revise figure/table claim boundary from scaffold to accepted study scope"
        )
    claim_manifest = claim_alignment_manifest or {}
    overclaim_count = _dict_int(claim_manifest, "overclaim_candidate_count")
    if not claim_manifest:
        blockers.append("generate claim-alignment review packet before manuscript acceptance")
    elif overclaim_count:
        blockers.append(
            "review or revise claim-alignment overclaim candidates before manuscript acceptance"
        )
    return _gate(
        "manuscript_report_alignment",
        "Manuscript Report Alignment",
        ready=ready,
        artifact_present=artifact_present,
        evidence=[
            "data/manifests/manuscript_acceptance.json",
            "paper/paper_draft.md",
            "report_draft.md",
            "report.docx",
            "results/realworld_pilot/tables/figure_table_manifest.json",
            "data/manifests/claim_alignment_review_packet.csv",
            "data/manifests/claim_alignment_review_manifest.json",
            "docs/claim_alignment_review_packet.md",
        ],
        blockers=blockers,
        details={
            "acceptance_record_present": manuscript_acceptance["record_present"],
            "acceptance_path": manuscript_acceptance["path"],
            "figure_claim_boundary_scope_blocked": scope_blocked,
            "claim_alignment_review_manifest_present": bool(claim_manifest),
            "claim_alignment_review_row_count": claim_manifest.get("row_count", 0),
            "claim_alignment_overclaim_candidate_count": overclaim_count,
            "claim_alignment_publication_ready": claim_manifest.get(
                "publication_ready",
                False,
            ),
            "publication_ready": publication_audit["publication_ready"],
        },
    )


def _reproducibility_gate(
    reproducibility_manifest: dict[str, Any] | None,
    reproducibility_acceptance: dict[str, Any],
    reproducibility_review_manifest: dict[str, Any] | None,
    reproducibility_smoke: dict[str, Any],
    clean_checkout_smoke: dict[str, Any] | None = None,
) -> dict[str, Any]:
    artifact_present = bool(reproducibility_manifest)
    scope = str((reproducibility_manifest or {}).get("scope", ""))
    remaining = list((reproducibility_manifest or {}).get("remaining_upgrades", []))
    commands = list((reproducibility_manifest or {}).get("validation_commands", []))
    review_manifest = reproducibility_review_manifest or {}
    acceptance_ready = bool(reproducibility_acceptance["acceptance_ready"])
    count_blockers = _reproducibility_count_blockers(
        commands,
        reproducibility_acceptance,
    )
    scope_blocked = "scaffold" in scope.lower()
    ready = (
        artifact_present
        and acceptance_ready
        and not count_blockers
        and not scope_blocked
        and not remaining
    )
    blockers: list[str] = []
    if not acceptance_ready:
        blockers.extend(reproducibility_acceptance["remaining_blockers"])
    blockers.extend(count_blockers)
    if scope_blocked or remaining:
        blockers.append(
            "replace scaffold-only manifest with clean-checkout final reproduction package"
        )
    if not review_manifest:
        blockers.append("create reproducibility review packet before clean-checkout acceptance")
    clean_smoke = clean_checkout_smoke or {}
    if clean_smoke and clean_smoke.get("manifest_present") and not clean_smoke.get(
        "smoke_passed"
    ):
        blockers.append("resolve failed bounded clean-checkout smoke before acceptance")
    return _gate(
        "reproducibility",
        "Reproducibility",
        ready=ready,
        artifact_present=artifact_present,
        evidence=[
            "data/manifests/reproducibility_acceptance.json",
            "docs/reproducibility_package.md",
            "data/manifests/reproducibility_manifest.json",
            "data/validation/reproducibility_review_packet.csv",
            "data/validation/reproducibility_review_manifest.json",
            "data/validation/reproducibility_smoke_manifest.json",
            "docs/reproducibility_smoke.md",
            "data/validation/clean_checkout_reproducibility_smoke_manifest.json",
            "docs/clean_checkout_reproducibility_smoke.md",
        ],
        blockers=blockers,
        details={
            "acceptance_record_present": reproducibility_acceptance["record_present"],
            "acceptance_path": reproducibility_acceptance["path"],
            "scope": scope,
            "validation_command_count": len(commands),
            "accepted_validation_command_count": reproducibility_acceptance.get(
                "expected_validation_command_count"
            ),
            "review_packet_present": bool(review_manifest),
            "review_packet_row_count": review_manifest.get("row_count"),
            "review_packet_clean_checkout_test_performed": review_manifest.get(
                "clean_checkout_test_performed"
            ),
            "review_packet_git_status_line_count": review_manifest.get(
                "git_status_line_count"
            ),
            "review_packet_untracked_count": review_manifest.get(
                "git_untracked_count"
            ),
            "review_packet_no_runtime_cloned_repo_imports": review_manifest.get(
                "no_runtime_cloned_repo_imports"
            ),
            "current_worktree_smoke_present": reproducibility_smoke.get(
                "manifest_present"
            ),
            "current_worktree_smoke_passed": reproducibility_smoke.get("smoke_passed"),
            "current_worktree_smoke_command_count": reproducibility_smoke.get(
                "command_count"
            ),
            "current_worktree_smoke_failed_count": reproducibility_smoke.get(
                "failed_count"
            ),
            "current_worktree_smoke_scope": reproducibility_smoke.get(
                "result_scope"
            ),
            "clean_checkout_smoke_present": clean_smoke.get("manifest_present"),
            "clean_checkout_smoke_passed": clean_smoke.get("smoke_passed"),
            "clean_checkout_smoke_command_count": clean_smoke.get("command_count"),
            "clean_checkout_smoke_failed_count": clean_smoke.get("failed_count"),
            "clean_checkout_smoke_scope": clean_smoke.get("result_scope"),
            "clean_checkout_smoke_environment_scope": clean_smoke.get(
                "environment_scope"
            ),
            "clean_checkout_smoke_full_clean_environment_tested": clean_smoke.get(
                "full_clean_environment_tested"
            ),
        },
    )


def _reproducibility_count_blockers(
    commands: list[Any],
    reproducibility_acceptance: dict[str, Any],
) -> list[str]:
    if not reproducibility_acceptance.get("record_present"):
        return []
    accepted = reproducibility_acceptance.get("expected_validation_command_count")
    manifest_count = len(commands)
    if accepted == manifest_count:
        return []
    return [
        "reproducibility acceptance validation command count must match the manifest: "
        f"acceptance={accepted!r}, manifest={manifest_count!r}"
    ]


def _final_audit_gate(
    pre_final_gates: list[dict[str, Any]],
    final_audit_acceptance: dict[str, Any],
) -> dict[str, Any]:
    text = _read_text(DEFAULT_FINAL_AUDIT_PATH)
    artifact_present = DEFAULT_FINAL_AUDIT_PATH.exists()
    acceptance_ready = bool(final_audit_acceptance["acceptance_ready"])
    count_blockers = _final_audit_count_blockers(
        pre_final_gates,
        final_audit_acceptance,
    )
    blocked_pre_final = [gate["gate_id"] for gate in pre_final_gates if not gate["ready"]]
    audit_text_ready = "prompt-to-artifact checklist" in text.lower()
    ready = (
        artifact_present
        and audit_text_ready
        and acceptance_ready
        and not count_blockers
        and not blocked_pre_final
    )
    blockers: list[str] = []
    if not artifact_present:
        blockers.append("create docs/final_study_audit.md after all other gates close")
    elif not audit_text_ready:
        blockers.append(
            "final audit note must include a prompt-to-artifact checklist review"
        )
    if not acceptance_ready:
        blockers.extend(final_audit_acceptance["remaining_blockers"])
    blockers.extend(count_blockers)
    if blocked_pre_final:
        blockers.append(
            "all pre-final gates must be ready before final audit acceptance: "
            + ", ".join(blocked_pre_final)
        )
    return _gate(
        "final_audit",
        "Final Audit",
        ready=ready,
        artifact_present=artifact_present,
        evidence=[
            "docs/final_study_audit.md",
            "data/manifests/final_audit_acceptance.json",
        ],
        blockers=blockers,
        details={
            "acceptance_record_present": final_audit_acceptance["record_present"],
            "acceptance_path": final_audit_acceptance["path"],
            "blocked_pre_final_gate_ids": blocked_pre_final,
            "expected_gate_count": final_audit_acceptance.get("expected_gate_count"),
            "pre_final_gate_count": len(pre_final_gates),
        },
    )


def _final_audit_count_blockers(
    pre_final_gates: list[dict[str, Any]],
    final_audit_acceptance: dict[str, Any],
) -> list[str]:
    if not final_audit_acceptance.get("record_present"):
        return []
    blockers: list[str] = []
    expected_gate_count = final_audit_acceptance.get("expected_gate_count")
    if expected_gate_count != len(pre_final_gates):
        blockers.append(
            "final-audit expected_gate_count must match pre-final gate count: "
            f"acceptance={expected_gate_count!r}, current={len(pre_final_gates)!r}"
        )
    reviewed = set(_list_value(final_audit_acceptance, "reviewed_gate_ids"))
    current = {str(gate["gate_id"]) for gate in pre_final_gates}
    if reviewed != current:
        blockers.append(
            "final-audit reviewed_gate_ids must match current pre-final gates"
        )
    ready = set(_list_value(final_audit_acceptance, "ready_gate_ids"))
    current_ready = {str(gate["gate_id"]) for gate in pre_final_gates if gate["ready"]}
    if ready != current_ready:
        blockers.append("final-audit ready_gate_ids must match current ready gates")
    blocked = set(_list_value(final_audit_acceptance, "blocked_gate_ids"))
    current_blocked = {
        str(gate["gate_id"]) for gate in pre_final_gates if not gate["ready"]
    }
    if blocked != current_blocked:
        blockers.append("final-audit blocked_gate_ids must match current blocked gates")
    return blockers


def _gate(
    gate_id: str,
    label: str,
    *,
    ready: bool,
    artifact_present: bool,
    evidence: list[str],
    blockers: list[str],
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "label": label,
        "ready": bool(ready),
        "artifact_present": bool(artifact_present),
        "evidence": evidence,
        "blockers": blockers,
        "details": details or {},
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else None


def _csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _list_value(value: dict[str, Any] | None, key: str) -> Iterable[str]:
    raw = (value or {}).get(key, [])
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw]


def _dict_int(value: dict[str, Any] | None, key: str) -> int:
    raw = (value or {}).get(key, 0)
    return int(raw) if isinstance(raw, int | float) else 0


__all__ = [
    "FINAL_GATE_IDS",
    "audit_final_study_readiness",
]
