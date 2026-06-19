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
from src.realworld.rail_source_decision_packet import (
    DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
)
from src.realworld.rail_fetch_readiness_packet import (
    DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
)
from src.realworld.rail_evidence_priority_packet import (
    DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
)
from src.realworld.rail_transit_stress_profile_packet import (
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH,
)
from src.realworld.rail_bounded_treatment_audit import (
    DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH,
)
from src.realworld.road_evidence import (
    DEFAULT_ROAD_GRAPH_PATH,
    audit_cached_road_evidence,
)
from src.realworld.road_override_audit import audit_road_class_override_evidence
from src.realworld.road_override_audit import audit_road_class_override_application
from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
)


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


def _rail_formal_acceptance_active() -> bool:
    """Return True when reviewer-signed rail source-decision acceptance exists."""

    path = Path(DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH)
    if not path.exists():
        return False
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(manifest, dict):
        return False
    return bool(
        manifest.get("rail_source_decision_recorded", False)
        and manifest.get("publication_ready", False)
        and manifest.get("completed_action_ledger_is_acceptance", False)
    )


def audit_publication_readiness(
    *,
    road_graph_path: str | Path = DEFAULT_ROAD_GRAPH_PATH,
    rail_service_path: str | Path = DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
    rail_station_binding_path: str | Path = DEFAULT_RAIL_STATION_BINDING_PATH,
    rail_source_decision_manifest_path: str
    | Path = DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    rail_transit_stress_profile_manifest_path: str
    | Path = DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH,
    rail_bounded_treatment_audit_path: str
    | Path = DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH,
) -> dict[str, Any]:
    """Return conservative readiness gates for final-study claims."""

    parameter_audit = audit_shipped_parameter_evidence()
    road_audit = audit_cached_road_evidence(road_graph_path)
    road_override_audit = audit_road_class_override_evidence()
    road_override_application_audit = audit_road_class_override_application()
    rail_service_audit = summarize_rail_service_evidence(
        load_rail_service_evidence(rail_service_path),
        formal_acceptance_active=_rail_formal_acceptance_active(),
    )
    station_binding_audit = summarize_rail_station_bindings(
        load_rail_station_bindings(rail_station_binding_path)
    )
    rail_source_decision_audit = _summarize_rail_source_decision_manifest(
        rail_source_decision_manifest_path
    )
    rail_transit_stress_profile_audit = (
        _summarize_rail_transit_stress_profile_manifest(
            rail_transit_stress_profile_manifest_path
        )
    )
    rail_bounded_treatment_audit = _summarize_rail_bounded_treatment_audit(
        rail_bounded_treatment_audit_path
    )

    rail_ready = bool(
        rail_service_audit["publication_ready"]
        and station_binding_audit["binding_ready"]
        and rail_source_decision_audit["rail_source_decision_ready"]
        and rail_transit_stress_profile_audit["rail_transit_stress_profile_ready"]
        and rail_bounded_treatment_audit["rail_bounded_treatment_integrity_ready"]
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
        "rail_source_decision_ready": bool(
            rail_source_decision_audit["rail_source_decision_ready"]
        ),
        "rail_transit_stress_profile_ready": bool(
            rail_transit_stress_profile_audit[
                "rail_transit_stress_profile_ready"
            ]
        ),
        "rail_bounded_treatment_integrity_ready": bool(
            rail_bounded_treatment_audit[
                "rail_bounded_treatment_integrity_ready"
            ]
        ),
        "rail_evidence_ready": rail_ready,
    }
    publication_ready = all(gates.values())

    return {
        "publication_ready": publication_ready,
        "verdict": (
            "evidence_readiness_review_unblocked_not_formal_acceptance"
            if publication_ready
            else "final_study_claims_blocked"
        ),
        "claim_boundary": (
            "This audit aggregates evidence gates. It does not validate "
            "operational routing or certify real emergency operations."
        ),
        "gates": gates,
        "remaining_blockers": _remaining_blockers(
            parameter_audit=parameter_audit,
            road_audit=road_audit,
            road_override_audit=road_override_audit,
            road_override_application_audit=road_override_application_audit,
            rail_service_audit=rail_service_audit,
            station_binding_audit=station_binding_audit,
            rail_source_decision_audit=rail_source_decision_audit,
            rail_transit_stress_profile_audit=rail_transit_stress_profile_audit,
            rail_bounded_treatment_audit=rail_bounded_treatment_audit,
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
            "resolve blocked parameter, road, and rail evidence gates before release-scope publication claims",
            "treat this audit as claim-scope triage only, not formal acceptance",
            "rerun closeout publication-gate audit after any formal acceptance or evidence artifact changes",
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
        blocker_lines = [f"- blocked requirement: {item}" for item in blockers]
    else:
        blocker_lines = ["- None recorded."]

    return "\n".join(
        [
            "# Publication Gate Blocker Audit",
            "",
            str(manifest.get("claim_boundary", "")),
            "",
            "This is a claim-scope audit only. It is not a formal acceptance record, calibrated validation, or operational route approval.",
            "",
            f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
            f"- Verdict: `{manifest.get('verdict', '')}`",
            f"- Unblocked gates: {manifest.get('ready_gate_count', 0)} / {manifest.get('gate_count', 0)}",
            f"- Blocked gates: {manifest.get('blocked_gate_count', 0)} / {manifest.get('gate_count', 0)}",
            f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
            "",
            "## Evidence Gates",
            "",
            "| Gate | Evidence status |",
            "| --- | --- |",
            *gate_rows,
            "",
            "`rail_station_binding_ready` is an identifier-binding prerequisite only; it does not prove rail timing, capacity, availability, or operational rail service.",
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
    preserve_generated_at_when_unchanged(manifest, manifest_file)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    write_json_manifest_if_changed(manifest, manifest_file, sort_keys=True)
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
    rail_source_decision_audit: dict[str, Any],
    rail_transit_stress_profile_audit: dict[str, Any],
    rail_bounded_treatment_audit: dict[str, Any],
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
    blockers.extend(
        f"rail source decision: {item}"
        for item in rail_source_decision_audit.get("remaining_blockers", [])
    )
    blockers.extend(
        f"rail transit stress profile: {item}"
        for item in rail_transit_stress_profile_audit.get("remaining_blockers", [])
    )
    blockers.extend(
        f"rail bounded treatment: {item}"
        for item in rail_bounded_treatment_audit.get("remaining_blockers", [])
    )
    return blockers


def _summarize_rail_source_decision_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "rail_source_decision_ready": False,
            "remaining_blockers": [
                f"rail source-decision manifest is missing: {_display_path(manifest_path)}"
            ],
        }
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    blocking_count = int(manifest.get("blocking_decision_count", 0) or 0)
    human_review_count = int(manifest.get("human_review_decision_count", 0) or 0)
    row_count = int(manifest.get("row_count", 0) or 0)
    completed_count = int(manifest.get("completed_source_decision_count", 0) or 0)
    recorded = bool(manifest.get("rail_source_decision_recorded", False))
    manifest_publication_ready = bool(manifest.get("publication_ready", False))
    can_mark_complete = bool(manifest.get("can_mark_complete", False))
    can_support_publication_gate = bool(
        manifest.get("can_support_publication_gate", False)
    )
    can_support_rail_gate = bool(
        manifest.get("can_support_rail_evidence_gate", False)
    )
    accepted_source_backed_evidence = bool(
        manifest.get("accepted_source_backed_rail_service_evidence", False)
    )
    closure_candidate_count = int(
        manifest.get("rail_service_evidence_gate_closure_candidate_count", 0)
        or 0
    )
    action_ledger_completion_scope = str(
        manifest.get("action_ledger_completion_scope", "")
    ).strip()
    completed_action_ledger_is_acceptance = bool(
        manifest.get("completed_action_ledger_is_acceptance", False)
    )
    non_formal_action_ledger_scope = (
        action_ledger_completion_scope == "non_formal_source_review_only"
    )
    complete = bool(row_count and completed_count == row_count)
    ready_before_input_guard = (
        recorded
        and complete
        and blocking_count == 0
        and human_review_count == 0
        and manifest_publication_ready
        and can_mark_complete
        and can_support_publication_gate
        and can_support_rail_gate
        and accepted_source_backed_evidence
        and closure_candidate_count > 0
        and not non_formal_action_ledger_scope
        and completed_action_ledger_is_acceptance
    )
    input_guard_blockers = (
        _source_decision_input_manifest_blockers(
            manifest_path=manifest_path,
            manifest=manifest,
        )
        if ready_before_input_guard
        else []
    )
    ready = bool(ready_before_input_guard and not input_guard_blockers)
    blockers: list[str] = []
    if not recorded:
        blockers.append("rail source decisions are not recorded as reviewed decisions")
    if not complete:
        blockers.append(
            "rail source decisions are not complete for every rail source-decision row"
        )
    if blocking_count:
        blockers.append(f"{blocking_count} rail timing source decision rows are blocked")
    if human_review_count:
        blockers.append(
            f"{human_review_count} rail capacity or availability source decisions need human review"
        )
    if not manifest_publication_ready:
        blockers.append(
            "rail source-decision manifest is not publication-ready evidence"
        )
    if not can_mark_complete:
        blockers.append("rail source-decision manifest cannot mark complete")
    if not can_support_publication_gate:
        blockers.append("rail source-decision manifest cannot support publication gate")
    if not can_support_rail_gate:
        blockers.append("rail source-decision manifest cannot support rail evidence gate")
    if not accepted_source_backed_evidence:
        blockers.append(
            "rail source-decision manifest does not accept source-backed rail service evidence"
        )
    if closure_candidate_count <= 0:
        blockers.append(
            "rail source-decision manifest has zero rail-service evidence gate closure candidates"
        )
    if non_formal_action_ledger_scope:
        blockers.append(
            "non-formal rail source-decision action ledger cannot close rail evidence gate"
        )
    if not completed_action_ledger_is_acceptance:
        blockers.append(
            "rail source-decision action ledger is not formal acceptance evidence"
        )
    blockers.extend(input_guard_blockers)
    return {
        "rail_source_decision_ready": ready,
        "rail_source_decision_recorded": recorded,
        "action_ledger_completion_scope": action_ledger_completion_scope,
        "completed_action_ledger_is_acceptance": completed_action_ledger_is_acceptance,
        "non_formal_action_ledger_scope": non_formal_action_ledger_scope,
        "source_decision_input_guard_blocker_count": len(input_guard_blockers),
        "source_decision_manifest_publication_ready": manifest_publication_ready,
        "source_decision_manifest_can_mark_complete": can_mark_complete,
        "source_decision_manifest_can_support_publication_gate": (
            can_support_publication_gate
        ),
        "source_decision_manifest_can_support_rail_gate": can_support_rail_gate,
        "accepted_source_backed_rail_service_evidence": accepted_source_backed_evidence,
        "rail_service_evidence_gate_closure_candidate_count": closure_candidate_count,
        "row_count": row_count,
        "completed_source_decision_count": completed_count,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "remaining_blockers": blockers,
    }


def _source_decision_input_manifest_blockers(
    *,
    manifest_path: Path,
    manifest: dict[str, Any],
) -> list[str]:
    """Return stale-input blockers for optimistic rail source-decision manifests."""

    inputs = manifest.get("inputs", {})
    if not isinstance(inputs, dict):
        inputs = {}
    fetch_path = _resolve_input_path(
        manifest_path,
        inputs.get("rail_fetch_readiness_manifest"),
        DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    )
    priority_path = _resolve_input_path(
        manifest_path,
        inputs.get("rail_evidence_priority_manifest"),
        DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    )
    blockers: list[str] = []
    fetch_manifest = _load_optional_json(fetch_path)
    if not fetch_manifest:
        blockers.append(
            f"rail source-decision input guard: missing rail fetch-readiness manifest {_display_path(fetch_path)}"
        )
    else:
        blocking_count = int(fetch_manifest.get("blocking_request_count", 0) or 0)
        if blocking_count:
            blockers.append(
                f"rail source-decision input guard: rail fetch-readiness manifest has {blocking_count} blocking requests"
            )
    priority_manifest = _load_optional_json(priority_path)
    if not priority_manifest:
        blockers.append(
            f"rail source-decision input guard: missing rail evidence-priority manifest {_display_path(priority_path)}"
        )
    else:
        blocking_count = int(priority_manifest.get("blocking_priority_count", 0) or 0)
        human_count = int(priority_manifest.get("human_review_priority_count", 0) or 0)
        if blocking_count:
            blockers.append(
                f"rail source-decision input guard: rail evidence-priority manifest has {blocking_count} blocking priorities"
            )
        if human_count:
            blockers.append(
                f"rail source-decision input guard: rail evidence-priority manifest has {human_count} human-review priorities"
            )
    return blockers


def _resolve_input_path(
    manifest_path: Path,
    raw_path: object,
    default_path: Path,
) -> Path:
    text = str(raw_path or "").strip()
    if not text:
        return default_path
    candidate = Path(text)
    if candidate.is_absolute():
        return candidate
    project_candidate = PROJECT_ROOT / candidate
    if project_candidate.exists():
        return project_candidate
    return manifest_path.parent / candidate


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    return loaded if isinstance(loaded, dict) else None


def _summarize_rail_bounded_treatment_audit(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "rail_bounded_treatment_integrity_ready": False,
            "remaining_blockers": [
                "rail bounded-treatment audit is missing: "
                f"{_display_path(manifest_path)}"
            ],
        }
    with manifest_path.open("r", encoding="utf-8") as handle:
        audit = json.load(handle)
    mismatch_count = int(audit.get("mismatch_count", 0) or 0)
    warning_count = int(audit.get("warning_count", 0) or 0)
    unchecked_pending_decision_count = int(
        audit.get("unchecked_pending_decision_count", 0) or 0
    )
    publication_ready = bool(audit.get("publication_ready", False))
    can_mark_complete = bool(audit.get("can_mark_complete", False))
    can_support_rail_gate = bool(
        audit.get("can_support_rail_evidence_gate", False)
    )
    can_support_acceptance_gate = bool(
        audit.get("can_support_acceptance_gate", False)
    )
    ready = bool(
        mismatch_count == 0
        and warning_count == 0
        and unchecked_pending_decision_count == 0
        and not publication_ready
        and not can_mark_complete
        and not can_support_rail_gate
        and not can_support_acceptance_gate
    )
    blockers: list[str] = []
    if mismatch_count:
        blockers.append(f"{mismatch_count} rail bounded-treatment mismatches remain")
    if warning_count:
        blockers.append(f"{warning_count} rail bounded-treatment warnings remain")
    if unchecked_pending_decision_count:
        blockers.append(
            f"{unchecked_pending_decision_count} rail bounded-treatment source decisions remain pending"
        )
    if publication_ready:
        blockers.append("rail bounded-treatment audit must not claim publication readiness")
    if can_mark_complete:
        blockers.append("rail bounded-treatment audit must not mark complete")
    if can_support_rail_gate:
        blockers.append("rail bounded-treatment audit must not support rail evidence gate")
    if can_support_acceptance_gate:
        blockers.append("rail bounded-treatment audit must not support acceptance gate")
    return {
        "rail_bounded_treatment_integrity_ready": ready,
        "mismatch_count": mismatch_count,
        "warning_count": warning_count,
        "unchecked_pending_decision_count": unchecked_pending_decision_count,
        "bounded_treatment_publication_ready": publication_ready,
        "bounded_treatment_can_mark_complete": can_mark_complete,
        "bounded_treatment_can_support_rail_gate": can_support_rail_gate,
        "bounded_treatment_can_support_acceptance_gate": can_support_acceptance_gate,
        "remaining_blockers": blockers,
    }


def _summarize_rail_transit_stress_profile_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "rail_transit_stress_profile_ready": False,
            "remaining_blockers": [
                "rail transit stress-profile manifest is missing: "
                f"{_display_path(manifest_path)}"
            ],
        }
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    required_present = bool(manifest.get("required_stress_classes_present", False))
    missing_runtime_hook_count = int(
        manifest.get("missing_runtime_hook_count", 0) or 0
    )
    unresolved_linked_artifact_count = int(
        manifest.get("unresolved_linked_artifact_count", 0) or 0
    )
    publication_ready = bool(manifest.get("publication_ready", False))
    can_mark_complete = bool(manifest.get("can_mark_complete", False))
    can_support_rail_gate = bool(
        manifest.get("can_support_rail_evidence_gate", False)
    )
    ready = bool(
        required_present
        and missing_runtime_hook_count == 0
        and unresolved_linked_artifact_count == 0
        and publication_ready
        and can_mark_complete
        and can_support_rail_gate
        and not manifest.get("remaining_blockers", [])
    )
    blockers: list[str] = []
    if not required_present:
        blockers.append("rail transit stress-profile required classes are incomplete")
    if missing_runtime_hook_count:
        blockers.append(
            f"{missing_runtime_hook_count} rail transit stress-profile rows have missing runtime hooks"
        )
    if unresolved_linked_artifact_count:
        blockers.append(
            f"{unresolved_linked_artifact_count} rail transit stress-profile linked artifacts are unresolved"
        )
    if not publication_ready:
        blockers.append(
            "rail transit stress-profile manifest is not publication-ready evidence"
        )
    if not can_mark_complete:
        blockers.append("rail transit stress-profile manifest cannot mark complete")
    if not can_support_rail_gate:
        blockers.append(
            "rail transit stress-profile manifest cannot support rail evidence gate"
        )
    blockers.extend(str(item) for item in manifest.get("remaining_blockers", []))
    return {
        "rail_transit_stress_profile_ready": ready,
        "required_stress_classes_present": required_present,
        "missing_runtime_hook_count": missing_runtime_hook_count,
        "unresolved_linked_artifact_count": unresolved_linked_artifact_count,
        "stress_profile_manifest_publication_ready": publication_ready,
        "stress_profile_manifest_can_mark_complete": can_mark_complete,
        "stress_profile_manifest_can_support_rail_gate": can_support_rail_gate,
        "remaining_blockers": blockers,
    }


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "DEFAULT_PUBLICATION_READINESS_DOC_PATH",
    "DEFAULT_PUBLICATION_READINESS_MANIFEST_PATH",
    "PUBLICATION_READINESS_RESULT_SCOPE",
    "audit_publication_readiness",
    "build_publication_readiness_manifest",
    "build_publication_readiness_markdown",
    "_summarize_rail_transit_stress_profile_manifest",
    "_summarize_rail_bounded_treatment_audit",
    "write_publication_readiness_audit",
]
