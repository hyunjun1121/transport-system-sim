"""Phase-gate ledger templates and audit helpers.

The ledgers written here are conservative closure controls for ``plan.md``.
Generated templates do not close phases. A phase may only be treated as closed
when a reviewed ledger explicitly records a closed gate decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PHASE_GATE_LEDGER_DIR = PROJECT_ROOT / "data" / "manifests" / "phase_gates"
DEFAULT_PHASE_GATE_LEDGER_SCHEMA = PROJECT_ROOT / "schemas" / "phase_gate_ledger.schema.json"
DEFAULT_PHASE_GATE_LEDGER_AUDIT_MANIFEST = (
    PROJECT_ROOT / "data" / "manifests" / "phase_gate_ledger_audit.json"
)
DEFAULT_PHASE_GATE_LEDGER_AUDIT_DOC = PROJECT_ROOT / "docs" / "phase_gate_ledger_audit.md"

PHASE_GATE_LEDGER_CLAIM_BOUNDARY = (
    "Phase-gate ledger control only; generated templates do not close phases, "
    "approve final-study gates, validate real-world accuracy, or authorize "
    "operational routing."
)
DEFAULT_PHASE_GATE_DECISION_AUTHORITY = (
    "human/source-backed reviewer after required audits"
)
ALLOWED_PHASE_GATE_STATUSES: frozenset[str] = frozenset(
    {"not_started", "in_progress", "blocked", "ready_for_review", "closed"}
)
ALLOWED_PHASE_GATE_DECISIONS: frozenset[str] = frozenset(
    {"not_closed", "blocked", "ready_for_review", "closed", "not_applicable"}
)
REQUIRED_PHASE_GATE_LEDGER_FIELDS: tuple[str, ...] = (
    "schema_version",
    "phase_id",
    "objective",
    "status",
    "prerequisites",
    "source_inputs",
    "generated_outputs",
    "tests",
    "sub_agents",
    "command_results",
    "artifact_hashes",
    "self_refine",
    "dependency_control",
    "findings",
    "claim_boundary",
    "gate_decision",
    "decision_authority",
    "can_mark_complete",
    "final_study_ready",
    "generated_at",
)


@dataclass(frozen=True)
class PhaseGateSpec:
    """Canonical phase entry from the implementation workflow."""

    phase_id: str
    objective: str
    prerequisites: tuple[str, ...]


CANONICAL_PHASE_GATE_SPECS: tuple[PhaseGateSpec, ...] = (
    PhaseGateSpec(
        phase_id="phase0_baseline_and_worktree_safety",
        objective="Freeze baseline context, classify dirty worktree paths, and record hardware/package state before new generated work.",
        prerequisites=("current plan.md inspected", "dirty worktree classification ledger refreshed"),
    ),
    PhaseGateSpec(
        phase_id="phase1_region_scenario_demand_registry",
        objective="Define reusable region, scenario, demand, fleet, and behavior registries before route or experiment generation.",
        prerequisites=("phase0_baseline_and_worktree_safety closed",),
    ),
    PhaseGateSpec(
        phase_id="phase2_road_network_input",
        objective="Build and audit real-world road-network inputs with reproducible source snapshots and routing-engine boundaries.",
        prerequisites=("phase1_region_scenario_demand_registry closed",),
    ),
    PhaseGateSpec(
        phase_id="phase3_road_attribute_evidence",
        objective="Attach reviewed road capacity, speed, lane, and disruption-parameter evidence to road links.",
        prerequisites=("phase2_road_network_input closed",),
    ),
    PhaseGateSpec(
        phase_id="phase4_rail_transit_multimodal_evidence",
        objective="Bind rail, station, timetable, transfer, and multimodal evidence without overstating operational timetable authority.",
        prerequisites=("phase1_region_scenario_demand_registry closed",),
    ),
    PhaseGateSpec(
        phase_id="phase5_demand_fleet_behavior_profiles",
        objective="Review and bound demand-arrival, fleet, transfer, and traveler-behavior profiles with source-backed assumptions.",
        prerequisites=("phase1_region_scenario_demand_registry closed",),
    ),
    PhaseGateSpec(
        phase_id="phase6_disruption_scenario_library",
        objective="Create structured disruption scenarios for roads, rail, transfers, demand surges, and multi-hazard combinations.",
        prerequisites=("phase2_road_network_input closed", "phase4_rail_transit_multimodal_evidence closed"),
    ),
    PhaseGateSpec(
        phase_id="phase7_external_benchmark_layer",
        objective="Compare simulator travel-time and routing behavior against external route or observed benchmark sources.",
        prerequisites=("phase2_road_network_input closed", "phase3_road_attribute_evidence closed"),
    ),
    PhaseGateSpec(
        phase_id="phase8_compact_experiment_gate",
        objective="Run compact experiments and review diagnostics before full stochastic experiment expansion.",
        prerequisites=("phase3_road_attribute_evidence closed", "phase4_rail_transit_multimodal_evidence closed", "phase5_demand_fleet_behavior_profiles closed"),
    ),
    PhaseGateSpec(
        phase_id="phase9_full_experiment_gate",
        objective="Run full experiments only after upstream source evidence, parameter evidence, benchmark review, artifact review, and compact gates pass.",
        prerequisites=("phase8_compact_experiment_gate closed", "artifact invalidation closeout verified"),
    ),
    PhaseGateSpec(
        phase_id="phase10_ml_decision_support",
        objective="Train and evaluate decision-support models using audited simulation outputs without confusing ML metrics with validation.",
        prerequisites=("phase9_full_experiment_gate closed",),
    ),
    PhaseGateSpec(
        phase_id="phase11_figures_reports_package",
        objective="Generate figures, reports, and review packages only from audited and claim-bounded outputs.",
        prerequisites=("phase9_full_experiment_gate closed", "phase10_ml_decision_support closed"),
    ),
    PhaseGateSpec(
        phase_id="phase12_formal_acceptance_final_audit",
        objective="Prepare formal review and closeout records only after every evidence, benchmark-check, reproducibility, and package gate has supporting review.",
        prerequisites=("phase11_figures_reports_package closed", "all formal review artifacts inspected"),
    ),
)


def phase_gate_ledger_schema() -> dict[str, Any]:
    """Return the JSON Schema for one phase-gate ledger."""

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Transport Simulation Phase Gate Ledger",
        "type": "object",
        "required": list(REQUIRED_PHASE_GATE_LEDGER_FIELDS),
        "properties": {
            "schema_version": {"type": "integer", "minimum": 1},
            "phase_id": {"type": "string", "minLength": 1},
            "objective": {"type": "string", "minLength": 1},
            "status": {
                "type": "string",
                "enum": sorted(ALLOWED_PHASE_GATE_STATUSES),
            },
            "prerequisites": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "source_inputs": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "generated_outputs": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "tests": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "sub_agents": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "command_results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["command", "status", "exit_code"],
                    "properties": {
                        "command": {"type": "string", "minLength": 1},
                        "status": {"type": "string", "minLength": 1},
                        "exit_code": {"type": "integer"},
                    },
                    "additionalProperties": True,
                },
            },
            "artifact_hashes": {
                "type": "object",
                "additionalProperties": {
                    "type": "string",
                    "pattern": "^sha256:[0-9a-fA-F]{64}$",
                },
            },
            "self_refine": {
                "type": "object",
                "required": ["performed", "status", "notes"],
                "properties": {
                    "performed": {"type": "boolean"},
                    "status": {"type": "string", "minLength": 1},
                    "notes": {"type": "string", "minLength": 1},
                },
                "additionalProperties": True,
            },
            "dependency_control": {
                "type": "object",
                "required": [
                    "dependency_status",
                    "parallelism_mode",
                    "synthesis_barrier",
                    "write_locks",
                ],
                "properties": {
                    "dependency_status": {"type": "string", "minLength": 1},
                    "parallelism_mode": {"type": "string", "minLength": 1},
                    "synthesis_barrier": {"type": "string", "minLength": 1},
                    "write_locks": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                    },
                },
                "additionalProperties": True,
            },
            "findings": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "claim_boundary": {"type": "string", "minLength": 1},
            "gate_decision": {
                "type": "string",
                "enum": sorted(ALLOWED_PHASE_GATE_DECISIONS),
            },
            "decision_authority": {"type": "string", "minLength": 1},
            "can_mark_complete": {"type": "boolean"},
            "final_study_ready": {"type": "boolean"},
            "generated_at": {"type": "string", "minLength": 1},
        },
        "additionalProperties": True,
    }


def build_phase_gate_template(
    spec: PhaseGateSpec,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Return a fail-closed phase-gate ledger template."""

    return {
        "schema_version": 1,
        "phase_id": spec.phase_id,
        "objective": spec.objective,
        "status": "blocked",
        "prerequisites": list(spec.prerequisites),
        "source_inputs": [],
        "generated_outputs": [],
        "tests": [],
        "sub_agents": [],
        "command_results": [],
        "artifact_hashes": {},
        "self_refine": {
            "performed": False,
            "status": "not_performed",
            "notes": "generated template; self-refine review required before closure",
        },
        "dependency_control": {
            "dependency_status": "not_satisfied",
            "parallelism_mode": "not_started",
            "synthesis_barrier": "not_verified",
            "write_locks": [],
        },
        "findings": [
            "generated template only; requires source-backed implementation and review before closure"
        ],
        "claim_boundary": PHASE_GATE_LEDGER_CLAIM_BOUNDARY,
        "gate_decision": "not_closed",
        "decision_authority": DEFAULT_PHASE_GATE_DECISION_AUTHORITY,
        "can_mark_complete": False,
        "final_study_ready": False,
        "generated_at": generated_at or _utc_now(),
    }


def validate_phase_gate_ledger_mapping(value: Mapping[str, Any]) -> None:
    """Validate required fields and conservative closure semantics."""

    missing = [
        field for field in REQUIRED_PHASE_GATE_LEDGER_FIELDS if field not in value
    ]
    if missing:
        raise ValueError("phase gate ledger missing required fields: " + ", ".join(missing))

    phase_id = _clean(value["phase_id"])
    objective = _clean(value["objective"])
    status = _clean(value["status"])
    gate_decision = _clean(value["gate_decision"])
    decision_authority = _clean(value["decision_authority"])
    generated_at = _clean(value["generated_at"])
    claim_boundary = _clean(value["claim_boundary"])
    can_mark_complete = _bool_value(value["can_mark_complete"], "can_mark_complete")
    final_study_ready = _bool_value(value["final_study_ready"], "final_study_ready")

    if not phase_id:
        raise ValueError("phase gate ledger phase_id must be non-empty")
    if not objective:
        raise ValueError("phase gate ledger objective must be non-empty")
    if status not in ALLOWED_PHASE_GATE_STATUSES:
        raise ValueError(
            "phase gate ledger status must be one of: "
            + ", ".join(sorted(ALLOWED_PHASE_GATE_STATUSES))
        )
    if gate_decision not in ALLOWED_PHASE_GATE_DECISIONS:
        raise ValueError(
            "phase gate ledger gate_decision must be one of: "
            + ", ".join(sorted(ALLOWED_PHASE_GATE_DECISIONS))
        )
    if not decision_authority:
        raise ValueError("phase gate ledger decision_authority must be non-empty")
    if not generated_at:
        raise ValueError("phase gate ledger generated_at must be non-empty")
    if not claim_boundary:
        raise ValueError("phase gate ledger claim_boundary must be non-empty")

    for field in (
        "prerequisites",
        "source_inputs",
        "generated_outputs",
        "tests",
        "sub_agents",
        "findings",
    ):
        _clean_sequence(value[field], field)
    _clean_command_results(value["command_results"])
    _validate_string_mapping(value["artifact_hashes"], "artifact_hashes")
    _validate_self_refine(value["self_refine"])
    _validate_dependency_control(value["dependency_control"])

    if can_mark_complete and status != "closed":
        raise ValueError("can_mark_complete requires status 'closed'")
    if can_mark_complete and gate_decision != "closed":
        raise ValueError("can_mark_complete requires gate_decision 'closed'")
    if final_study_ready and not can_mark_complete:
        raise ValueError("final_study_ready requires can_mark_complete")
    if status == "closed" and gate_decision != "closed":
        raise ValueError("closed status requires gate_decision 'closed'")
    if gate_decision == "closed" and not can_mark_complete:
        raise ValueError("closed gate_decision requires can_mark_complete")
    if not can_mark_complete and not value.get("findings"):
        raise ValueError("non-complete phase ledgers must list findings")
    if can_mark_complete:
        _validate_closure_evidence(value)


def load_phase_gate_ledger(path: str | Path) -> dict[str, Any]:
    """Load and validate one phase-gate ledger."""

    ledger_path = Path(path)
    with ledger_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, Mapping):
        raise ValueError(f"{ledger_path} must contain a JSON object")
    validate_phase_gate_ledger_mapping(value)
    return dict(value)


def audit_phase_gate_ledgers(
    *,
    ledger_dir: str | Path = DEFAULT_PHASE_GATE_LEDGER_DIR,
    expected_specs: Sequence[PhaseGateSpec] = CANONICAL_PHASE_GATE_SPECS,
) -> dict[str, Any]:
    """Return a fail-closed audit summary for current phase-gate ledgers."""

    directory = Path(ledger_dir)
    expected_ids = [spec.phase_id for spec in expected_specs]
    expected_set = set(expected_ids)
    existing_paths = {path.stem: path for path in directory.glob("*.json")} if directory.exists() else {}
    missing = [phase_id for phase_id in expected_ids if phase_id not in existing_paths]
    unexpected = sorted(phase_id for phase_id in existing_paths if phase_id not in expected_set)
    invalid: list[dict[str, str]] = []
    ledgers: list[dict[str, Any]] = []

    for phase_id in expected_ids:
        path = existing_paths.get(phase_id)
        if path is None:
            continue
        try:
            ledger = load_phase_gate_ledger(path)
        except Exception as exc:  # pragma: no cover - surfaced by audit output
            invalid.append(
                {
                    "phase_id": phase_id,
                    "path": _display_path(path),
                    "error": str(exc),
                }
            )
            continue
        ledgers.append(ledger)

    status_counts: dict[str, int] = {}
    decision_counts: dict[str, int] = {}
    for ledger in ledgers:
        status = str(ledger.get("status", ""))
        decision = str(ledger.get("gate_decision", ""))
        status_counts[status] = status_counts.get(status, 0) + 1
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

    closed_count = sum(
        1
        for ledger in ledgers
        if ledger.get("status") == "closed"
        and ledger.get("gate_decision") == "closed"
        and bool(ledger.get("can_mark_complete", False))
    )
    valid_count = len(ledgers)
    all_expected_present = not missing
    all_valid = not invalid
    support_present = all_expected_present and all_valid and valid_count == len(expected_ids)
    ready = support_present and closed_count == len(expected_ids)
    blockers: list[str] = []
    if missing:
        blockers.append("missing phase-gate ledger files: " + ", ".join(missing))
    if invalid:
        blockers.append(
            "invalid phase-gate ledger files: "
            + ", ".join(item["phase_id"] for item in invalid)
        )
    if unexpected:
        blockers.append("unexpected phase-gate ledger files: " + ", ".join(unexpected))
    if support_present and not ready:
        blockers.append(
            "phase-gate ledgers exist but are not all closed with can_mark_complete=true"
        )

    manifest = {
        "schema_version": 1,
        "generated_at": _utc_now(),
        "claim_boundary": PHASE_GATE_LEDGER_CLAIM_BOUNDARY,
        "ledger_dir": _display_path(directory),
        "expected_phase_count": len(expected_ids),
        "ledger_file_count": len(existing_paths),
        "valid_ledger_count": valid_count,
        "missing_phase_count": len(missing),
        "invalid_ledger_count": len(invalid),
        "unexpected_ledger_count": len(unexpected),
        "closed_phase_count": closed_count,
        "status_counts": status_counts,
        "gate_decision_counts": decision_counts,
        "missing_phase_ids": missing,
        "unexpected_phase_ids": unexpected,
        "invalid_ledgers": invalid,
        "all_expected_phase_ledgers_present": all_expected_present,
        "all_expected_phase_ledgers_valid": all_valid,
        "phase_gate_support_present": support_present,
        "phase_gate_ledgers_ready": ready,
        "can_mark_complete": ready,
        "final_study_ready": False,
        "remaining_blockers": blockers,
    }
    return manifest


def write_phase_gate_ledgers(
    *,
    ledger_dir: str | Path = DEFAULT_PHASE_GATE_LEDGER_DIR,
    schema_path: str | Path = DEFAULT_PHASE_GATE_LEDGER_SCHEMA,
    audit_manifest_path: str | Path = DEFAULT_PHASE_GATE_LEDGER_AUDIT_MANIFEST,
    audit_doc_path: str | Path = DEFAULT_PHASE_GATE_LEDGER_AUDIT_DOC,
    expected_specs: Sequence[PhaseGateSpec] = CANONICAL_PHASE_GATE_SPECS,
) -> dict[str, Any]:
    """Write schema, fail-closed ledger templates, audit manifest, and markdown."""

    directory = Path(ledger_dir)
    directory.mkdir(parents=True, exist_ok=True)
    schema_output = Path(schema_path)
    schema_output.parent.mkdir(parents=True, exist_ok=True)
    write_json_manifest_if_changed(
        phase_gate_ledger_schema(),
        schema_output,
        sort_keys=True,
    )

    for spec in expected_specs:
        path = directory / f"{spec.phase_id}.json"
        ledger = build_phase_gate_template(spec)
        if path.exists() and not _should_refresh_existing_template(path):
            continue
        preserve_generated_at_when_unchanged(ledger, path)
        write_json_manifest_if_changed(ledger, path, sort_keys=True)

    audit = audit_phase_gate_ledgers(
        ledger_dir=directory,
        expected_specs=expected_specs,
    )
    audit_output = Path(audit_manifest_path)
    audit_output.parent.mkdir(parents=True, exist_ok=True)
    preserve_generated_at_when_unchanged(audit, audit_output)
    write_json_manifest_if_changed(audit, audit_output, sort_keys=True)
    write_text_if_changed(build_phase_gate_ledger_audit_markdown(audit), audit_doc_path)
    return audit


def summarize_phase_gate_ledger_audit(
    path: str | Path = DEFAULT_PHASE_GATE_LEDGER_AUDIT_MANIFEST,
) -> dict[str, Any]:
    """Summarize the saved phase-gate audit manifest."""

    audit_path = Path(path)
    if not audit_path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(audit_path),
            "phase_gate_support_present": False,
            "phase_gate_ledgers_ready": False,
            "can_mark_complete": False,
            "final_study_ready": False,
            "remaining_blockers": ["phase-gate audit manifest is missing"],
        }
    try:
        value = json.loads(audit_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "manifest_present": True,
            "path": _display_path(audit_path),
            "phase_gate_support_present": False,
            "phase_gate_ledgers_ready": False,
            "can_mark_complete": False,
            "final_study_ready": False,
            "remaining_blockers": [f"phase-gate audit manifest is invalid JSON: {exc}"],
        }
    if not isinstance(value, Mapping):
        return {
            "manifest_present": True,
            "path": _display_path(audit_path),
            "phase_gate_support_present": False,
            "phase_gate_ledgers_ready": False,
            "can_mark_complete": False,
            "final_study_ready": False,
            "remaining_blockers": ["phase-gate audit manifest is not a JSON object"],
        }
    return {
        "manifest_present": True,
        "path": _display_path(audit_path),
        "expected_phase_count": int(value.get("expected_phase_count", 0)),
        "valid_ledger_count": int(value.get("valid_ledger_count", 0)),
        "missing_phase_count": int(value.get("missing_phase_count", 0)),
        "invalid_ledger_count": int(value.get("invalid_ledger_count", 0)),
        "closed_phase_count": int(value.get("closed_phase_count", 0)),
        "phase_gate_support_present": bool(value.get("phase_gate_support_present", False)),
        "phase_gate_ledgers_ready": bool(value.get("phase_gate_ledgers_ready", False)),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "final_study_ready": bool(value.get("final_study_ready", False)),
        "remaining_blockers": list(value.get("remaining_blockers", [])),
    }


def build_phase_gate_ledger_audit_markdown(audit: Mapping[str, Any]) -> str:
    """Return a markdown summary of a phase-gate ledger audit."""

    lines = [
        "# Phase Gate Ledger Audit",
        "",
        PHASE_GATE_LEDGER_CLAIM_BOUNDARY,
        "",
        f"- Expected phases: {audit.get('expected_phase_count', 0)}",
        f"- Valid ledgers: {audit.get('valid_ledger_count', 0)}",
        f"- Missing phases: {audit.get('missing_phase_count', 0)}",
        f"- Invalid ledgers: {audit.get('invalid_ledger_count', 0)}",
        f"- Closed phases: {audit.get('closed_phase_count', 0)}",
        f"- Support present: `{str(audit.get('phase_gate_support_present', False)).lower()}`",
        f"- All ledgers ready: `{str(audit.get('phase_gate_ledgers_ready', False)).lower()}`",
        f"- Can mark complete: `{str(audit.get('can_mark_complete', False)).lower()}`",
        f"- Final-study ready: `{str(audit.get('final_study_ready', False)).lower()}`",
        "",
        "## Status Counts",
        "",
    ]
    status_counts = audit.get("status_counts", {})
    if isinstance(status_counts, Mapping) and status_counts:
        for status, count in sorted(status_counts.items()):
            lines.append(f"- `{status}`: {count}")
    else:
        lines.append("- No valid phase ledgers found.")

    blockers = list(audit.get("remaining_blockers", []))
    lines.extend(["", "## Remaining Blockers", ""])
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- None recorded.")
    lines.append("")
    return "\n".join(lines)


def _clean(value: object) -> str:
    return str(value).strip()


def _clean_sequence(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"phase gate ledger {field} must be an array")
    cleaned = tuple(str(item).strip() for item in value)
    if any(not item for item in cleaned):
        raise ValueError(f"phase gate ledger {field} entries must be non-empty")
    return cleaned


def _validate_string_mapping(value: object, field: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"phase gate ledger {field} must be an object")
    result: dict[str, str] = {}
    for key, raw in value.items():
        clean_key = str(key).strip()
        clean_value = str(raw).strip()
        if not clean_key or not clean_value:
            raise ValueError(f"phase gate ledger {field} entries must be non-empty")
        if field == "artifact_hashes" and not _is_sha256_value(clean_value):
            raise ValueError(
                "phase gate ledger artifact_hashes values must use sha256:<64 hex>"
            )
        result[clean_key] = clean_value
    return result


def _validate_self_refine(value: object) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("phase gate ledger self_refine must be an object")
    if "performed" not in value or "status" not in value or "notes" not in value:
        raise ValueError("phase gate ledger self_refine missing required fields")
    _bool_value(value["performed"], "self_refine.performed")
    if not _clean(value["status"]):
        raise ValueError("phase gate ledger self_refine.status must be non-empty")
    if not _clean(value["notes"]):
        raise ValueError("phase gate ledger self_refine.notes must be non-empty")
    return value


def _validate_dependency_control(value: object) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("phase gate ledger dependency_control must be an object")
    required = (
        "dependency_status",
        "parallelism_mode",
        "synthesis_barrier",
        "write_locks",
    )
    missing = [field for field in required if field not in value]
    if missing:
        raise ValueError(
            "phase gate ledger dependency_control missing required fields: "
            + ", ".join(missing)
        )
    for field in ("dependency_status", "parallelism_mode", "synthesis_barrier"):
        if not _clean(value[field]):
            raise ValueError(f"phase gate ledger dependency_control.{field} must be non-empty")
    _clean_sequence(value["write_locks"], "dependency_control.write_locks")
    return value


def _validate_closure_evidence(value: Mapping[str, Any]) -> None:
    """Require substantive evidence before a ledger may close a phase."""

    for field in ("source_inputs", "generated_outputs", "tests", "sub_agents", "findings"):
        if not _clean_sequence(value[field], field):
            raise ValueError(f"closed phase gate ledger requires non-empty {field}")
    commands = _clean_command_results(value["command_results"])
    if not commands:
        raise ValueError("closed phase gate ledger requires command_results")
    if any(row["status"] != "passed" or row["exit_code"] != 0 for row in commands):
        raise ValueError("closed phase gate ledger command_results must all pass")
    if not _validate_string_mapping(value["artifact_hashes"], "artifact_hashes"):
        raise ValueError("closed phase gate ledger requires artifact_hashes")

    self_refine = _validate_self_refine(value["self_refine"])
    if self_refine.get("performed") is not True:
        raise ValueError("closed phase gate ledger requires self_refine.performed=true")
    if _clean(self_refine.get("status", "")) not in {
        "passed",
        "no_open_blockers",
        "reviewed",
    }:
        raise ValueError(
            "closed phase gate ledger requires self_refine.status to show review passed"
        )

    dependency = _validate_dependency_control(value["dependency_control"])
    if _clean(dependency.get("dependency_status", "")) != "satisfied":
        raise ValueError(
            "closed phase gate ledger requires dependency_control.dependency_status=satisfied"
        )
    if _clean(dependency.get("synthesis_barrier", "")) != "passed":
        raise ValueError(
            "closed phase gate ledger requires dependency_control.synthesis_barrier=passed"
        )
    if not _clean_sequence(dependency["write_locks"], "dependency_control.write_locks"):
        raise ValueError("closed phase gate ledger requires dependency write_locks")
    if value.get("claim_boundary") != PHASE_GATE_LEDGER_CLAIM_BOUNDARY:
        raise ValueError("closed phase gate ledger must preserve the claim boundary")
    decision_authority = _clean(value.get("decision_authority", ""))
    if decision_authority == DEFAULT_PHASE_GATE_DECISION_AUTHORITY:
        raise ValueError("closed phase gate ledger requires reviewed decision_authority")
    if not decision_authority.startswith("reviewer:"):
        raise ValueError(
            "closed phase gate ledger decision_authority must start with reviewer:"
        )


def _clean_command_results(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("phase gate ledger command_results must be an array")
    rows: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("phase gate ledger command_results entries must be objects")
        command = _clean(item.get("command", ""))
        status = _clean(item.get("status", ""))
        exit_code = item.get("exit_code")
        if not command or not status:
            raise ValueError("phase gate ledger command_results command/status must be non-empty")
        if not isinstance(exit_code, int) or isinstance(exit_code, bool):
            raise ValueError("phase gate ledger command_results exit_code must be integer")
        rows.append({"command": command, "status": status, "exit_code": exit_code})
    return rows


def _is_sha256_value(value: str) -> bool:
    prefix = "sha256:"
    if not value.startswith(prefix):
        return False
    digest = value[len(prefix) :]
    if len(digest) != 64:
        return False
    return all(char in "0123456789abcdefABCDEF" for char in digest)


def _should_refresh_existing_template(path: Path) -> bool:
    """Refresh only generated, non-reviewed templates."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(value, Mapping):
        return False
    return (
        value.get("can_mark_complete") is False
        and value.get("status") in {"blocked", "not_started"}
        and value.get("gate_decision") in {"not_closed", "blocked"}
        and not value.get("source_inputs")
        and not value.get("generated_outputs")
        and not value.get("tests")
        and _clean(value.get("decision_authority", ""))
        == DEFAULT_PHASE_GATE_DECISION_AUTHORITY
    )


def _bool_value(value: object, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"phase gate ledger {field} must be boolean")
    return value


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "ALLOWED_PHASE_GATE_DECISIONS",
    "ALLOWED_PHASE_GATE_STATUSES",
    "CANONICAL_PHASE_GATE_SPECS",
    "DEFAULT_PHASE_GATE_DECISION_AUTHORITY",
    "DEFAULT_PHASE_GATE_LEDGER_AUDIT_DOC",
    "DEFAULT_PHASE_GATE_LEDGER_AUDIT_MANIFEST",
    "DEFAULT_PHASE_GATE_LEDGER_DIR",
    "DEFAULT_PHASE_GATE_LEDGER_SCHEMA",
    "PHASE_GATE_LEDGER_CLAIM_BOUNDARY",
    "PhaseGateSpec",
    "audit_phase_gate_ledgers",
    "build_phase_gate_ledger_audit_markdown",
    "build_phase_gate_template",
    "load_phase_gate_ledger",
    "phase_gate_ledger_schema",
    "summarize_phase_gate_ledger_audit",
    "validate_phase_gate_ledger_mapping",
    "write_phase_gate_ledgers",
]
