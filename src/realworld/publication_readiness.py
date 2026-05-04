"""Aggregate final-study readiness gates for conservative claim control."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.realworld.parameter_audit import audit_shipped_parameter_evidence
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
from src.realworld.road_evidence import (
    DEFAULT_ROAD_GRAPH_PATH,
    audit_cached_road_evidence,
)
from src.realworld.road_override_audit import audit_road_class_override_evidence
from src.realworld.road_override_audit import audit_road_class_override_application


def audit_publication_readiness(
    *,
    road_graph_path: str | Path = DEFAULT_ROAD_GRAPH_PATH,
    rail_service_path: str | Path = DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
    rail_station_binding_path: str | Path = DEFAULT_RAIL_STATION_BINDING_PATH,
) -> dict[str, Any]:
    """Return conservative readiness gates for final-study claims."""

    parameter_audit = audit_shipped_parameter_evidence()
    road_audit = audit_cached_road_evidence(road_graph_path)
    road_override_audit = audit_road_class_override_evidence()
    road_override_application_audit = audit_road_class_override_application()
    rail_service_audit = summarize_rail_service_evidence(
        load_rail_service_evidence(rail_service_path)
    )
    station_binding_audit = summarize_rail_station_bindings(
        load_rail_station_bindings(rail_station_binding_path)
    )

    rail_ready = bool(
        rail_service_audit["publication_ready"]
        and station_binding_audit["binding_ready"]
    )
    gates = {
        "parameter_evidence_ready": bool(parameter_audit["publication_ready"]),
        "road_input_evidence_ready": bool(road_audit["publication_ready"]),
        "road_override_evidence_ready": bool(
            road_override_audit["publication_ready"]
        ),
        "road_override_application_ready": bool(
            road_override_application_audit["publication_ready"]
        ),
        "rail_service_evidence_ready": bool(rail_service_audit["publication_ready"]),
        "rail_station_binding_ready": bool(station_binding_audit["binding_ready"]),
        "rail_evidence_ready": rail_ready,
    }
    publication_ready = all(gates.values())

    return {
        "publication_ready": publication_ready,
        "verdict": (
            "final_study_claims_allowed"
            if publication_ready
            else "final_study_claims_blocked"
        ),
        "claim_boundary": (
            "This audit aggregates evidence-readiness gates. It does not "
            "validate operational routing or certify real emergency operations."
        ),
        "gates": gates,
        "remaining_blockers": _remaining_blockers(
            parameter_audit=parameter_audit,
            road_audit=road_audit,
            road_override_audit=road_override_audit,
            road_override_application_audit=road_override_application_audit,
            rail_service_audit=rail_service_audit,
            station_binding_audit=station_binding_audit,
        ),
    }


def _remaining_blockers(
    *,
    parameter_audit: dict[str, Any],
    road_audit: dict[str, Any],
    road_override_audit: dict[str, Any],
    road_override_application_audit: dict[str, Any],
    rail_service_audit: dict[str, Any],
    station_binding_audit: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    blockers.extend(
        f"parameter evidence: {item}"
        for item in parameter_audit.get("remaining_blockers", [])
    )
    blockers.extend(
        f"road input evidence: {item}"
        for item in road_audit.get("remaining_blockers", [])
    )
    blockers.extend(
        f"road override evidence: {item}"
        for item in road_override_audit.get("remaining_blockers", [])
    )
    blockers.extend(
        f"road override application: {item}"
        for item in road_override_application_audit.get("remaining_blockers", [])
    )
    blockers.extend(
        f"rail service evidence: {item}"
        for item in rail_service_audit.get("remaining_blockers", [])
    )
    blockers.extend(
        f"rail station binding: {item}"
        for item in station_binding_audit.get("remaining_blockers", [])
    )
    return blockers


__all__ = ["audit_publication_readiness"]
