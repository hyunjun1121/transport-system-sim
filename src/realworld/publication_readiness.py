"""Aggregate final-study readiness gates for conservative claim control."""

from __future__ import annotations

from datetime import datetime, timezone
import json
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


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PUBLICATION_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "publication_readiness_audit.json"
)
DEFAULT_PUBLICATION_READINESS_DOC_PATH = (
    PROJECT_ROOT / "docs" / "publication_readiness_audit.md"
)
PUBLICATION_READINESS_RESULT_SCOPE = (
    "publication_readiness_audit_not_formal_acceptance"
)


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


def build_publication_readiness_manifest(
    summary: dict[str, Any] | None = None,
    *,
    manifest_path: str | Path = DEFAULT_PUBLICATION_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PUBLICATION_READINESS_DOC_PATH,
) -> dict[str, Any]:
    """Return a machine-readable publication-readiness audit snapshot."""

    summary = summary or audit_publication_readiness()
    gates = dict(summary.get("gates", {}))
    ready_gate_count = sum(1 for value in gates.values() if bool(value))
    blocked_gate_count = len(gates) - ready_gate_count
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "result_scope": PUBLICATION_READINESS_RESULT_SCOPE,
        "claim_boundary": summary.get("claim_boundary", ""),
        "outputs": {
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "publication_ready": bool(summary.get("publication_ready", False)),
        "can_mark_complete": False,
        "verdict": str(summary.get("verdict", "")),
        "gate_count": len(gates),
        "ready_gate_count": ready_gate_count,
        "blocked_gate_count": blocked_gate_count,
        "status_counts": {
            "blocked": blocked_gate_count,
            "ready": ready_gate_count,
        },
        "gates": gates,
        "remaining_blockers": list(summary.get("remaining_blockers", [])),
        "review_items": [
            "resolve blocked parameter, road, and rail evidence gates before final publication claims",
            "treat this audit as claim-readiness triage only, not formal acceptance",
            "rerun final-study readiness after any formal acceptance or evidence artifact changes",
        ],
    }


def build_publication_readiness_markdown(
    manifest: dict[str, Any] | None = None,
) -> str:
    """Return a compact publication-readiness audit document."""

    manifest = manifest or build_publication_readiness_manifest()
    gates = manifest.get("gates", {})
    gate_rows = []
    if isinstance(gates, dict):
        for gate_id, ready in gates.items():
            gate_rows.append(
                f"| `{gate_id}` | `{str(bool(ready)).lower()}` |"
            )
    blockers = [
        str(item)
        for item in manifest.get("remaining_blockers", [])
        if str(item).strip()
    ]
    if blockers:
        blocker_lines = [f"- {item}" for item in blockers]
    else:
        blocker_lines = ["- None recorded."]

    return "\n".join(
        [
            "# Publication Readiness Audit",
            "",
            str(manifest.get("claim_boundary", "")),
            "",
            "This is a claim-readiness audit only. It is not a formal acceptance record, calibrated validation, or operational route approval.",
            "",
            f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
            f"- Verdict: `{manifest.get('verdict', '')}`",
            f"- Ready gates: {manifest.get('ready_gate_count', 0)} / {manifest.get('gate_count', 0)}",
            f"- Blocked gates: {manifest.get('blocked_gate_count', 0)} / {manifest.get('gate_count', 0)}",
            f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
            "",
            "## Evidence Gates",
            "",
            "| Gate | Ready |",
            "| --- | --- |",
            *gate_rows,
            "",
            "## Remaining Blockers",
            "",
            *blocker_lines,
            "",
        ]
    )


def write_publication_readiness_audit(
    *,
    manifest_path: str | Path = DEFAULT_PUBLICATION_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PUBLICATION_READINESS_DOC_PATH,
) -> dict[str, Any]:
    """Write publication-readiness manifest/doc snapshots and return the manifest."""

    manifest_file = Path(manifest_path)
    doc_file = Path(doc_path)
    manifest = build_publication_readiness_manifest(
        manifest_path=manifest_file,
        doc_path=doc_file,
    )
    _preserve_generated_at_when_unchanged(manifest, manifest_file)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc_file.parent.mkdir(parents=True, exist_ok=True)
    doc_file.write_text(
        build_publication_readiness_markdown(manifest),
        encoding="utf-8",
    )
    return manifest


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


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _preserve_generated_at_when_unchanged(
    manifest: dict[str, Any],
    manifest_path: Path,
) -> None:
    """Avoid timestamp-only churn when audit content is unchanged."""

    if not manifest_path.exists():
        return
    try:
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(previous, dict):
        return
    previous_generated_at = previous.get("generated_at")
    if not isinstance(previous_generated_at, str) or not previous_generated_at:
        return
    previous_without_time = dict(previous)
    current_without_time = dict(manifest)
    previous_without_time.pop("generated_at", None)
    current_without_time.pop("generated_at", None)
    if previous_without_time == current_without_time:
        manifest["generated_at"] = previous_generated_at


__all__ = [
    "DEFAULT_PUBLICATION_READINESS_DOC_PATH",
    "DEFAULT_PUBLICATION_READINESS_MANIFEST_PATH",
    "PUBLICATION_READINESS_RESULT_SCOPE",
    "audit_publication_readiness",
    "build_publication_readiness_manifest",
    "build_publication_readiness_markdown",
    "write_publication_readiness_audit",
]
