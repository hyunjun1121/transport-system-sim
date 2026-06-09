"""Formal acceptance evidence matrix for reviewer intake.

The matrix joins the formal package intake, blocker queue, task assignments,
and review-agent definitions into one per-artifact view. It is intentionally a
non-approval artifact: it helps reviewers find required evidence and commands,
but it never creates or substitutes for formal acceptance records.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.realworld.acceptance_task_assignments import (
    FORMAL_GATE_AGENT_OVERRIDES,
    build_acceptance_task_assignment_rows,
)
from src.realworld.acceptance_orchestration import (
    ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
    REVIEW_AGENT_DEFINITIONS,
    ReviewAgentDefinition,
)
from src.realworld.formal_acceptance_package import (
    CLAIM_BOUNDARY as FORMAL_PACKAGE_CLAIM_BOUNDARY,
    build_formal_acceptance_package_summary,
)
from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_MATRIX_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "formal_acceptance_evidence_matrix.csv"
)
DEFAULT_EVIDENCE_MATRIX_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "manifests"
    / "formal_acceptance_evidence_matrix_manifest.json"
)
DEFAULT_EVIDENCE_MATRIX_DOC_PATH = (
    PROJECT_ROOT / "docs" / "formal_acceptance_evidence_matrix.md"
)

EVIDENCE_MATRIX_BOUNDARY = (
    "Formal review evidence matrix only. Rows connect each required review "
    "artifact to review packets, templates, agents, blockers, and check "
    "commands. They do not approve evidence, certify sources, calibrate results, "
    "or close final-study gates."
)

EVIDENCE_MATRIX_COLUMNS: tuple[str, ...] = (
    "gate_id",
    "label",
    "assigned_agent_id",
    "assigned_agent",
    "formal_target",
    "formal_status",
    "formal_record_present",
    "formal_ready",
    "blocker_count",
    "template_or_worksheet",
    "review_packets",
    "source_paths",
    "reviewed_inputs",
    "required_actions",
    "validation_commands",
    "human_decision_required",
    "can_mark_complete",
    "claim_boundary",
)


def build_formal_acceptance_evidence_matrix_rows(
    *,
    package_summary: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Return one reviewer-intake row per formal acceptance artifact."""

    summary = package_summary or build_formal_acceptance_package_summary()
    assignment_rows = build_acceptance_task_assignment_rows(package_summary=summary)
    assignments_by_gate: dict[str, list[Mapping[str, str]]] = {}
    for row in assignment_rows:
        assignments_by_gate.setdefault(str(row["gate_id"]), []).append(row)

    rows: list[dict[str, str]] = []
    for gate in summary.get("gates", []):
        if not isinstance(gate, Mapping):
            continue
        gate_id = str(gate.get("gate_id", "")).strip()
        if not gate_id:
            continue
        assignments = assignments_by_gate.get(gate_id, [])
        agent = _resolve_agent(gate_id, assignments, gate)
        rows.append(_matrix_row(gate, assignments, agent))
    return rows


def write_formal_acceptance_evidence_matrix(
    *,
    output_path: str | Path = DEFAULT_EVIDENCE_MATRIX_PATH,
    manifest_path: str | Path = DEFAULT_EVIDENCE_MATRIX_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_EVIDENCE_MATRIX_DOC_PATH,
    package_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Write CSV, JSON manifest, and Markdown evidence matrix artifacts."""

    summary = package_summary or build_formal_acceptance_package_summary()
    rows = build_formal_acceptance_evidence_matrix_rows(package_summary=summary)
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EVIDENCE_MATRIX_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    status_counts: dict[str, int] = {}
    for row in rows:
        status = row["formal_status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    value = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": EVIDENCE_MATRIX_BOUNDARY,
        "formal_package_claim_boundary": summary.get(
            "claim_boundary", FORMAL_PACKAGE_CLAIM_BOUNDARY
        ),
        "orchestration_claim_boundary": ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
        "matrix_path": _display_path(output),
        "row_count": len(rows),
        "formal_gate_count": int(summary.get("gate_count", len(rows))),
        "ready_gate_count": int(summary.get("ready_gate_count", 0)),
        "blocked_gate_count": int(summary.get("blocked_gate_count", 0)),
        "invalid_gate_count": int(summary.get("invalid_gate_count", 0)),
        "status_counts": status_counts,
        "human_decision_required_count": sum(
            1 for row in rows if row["human_decision_required"] == "true"
        ),
        "formal_acceptance_ready": bool(summary.get("formal_acceptance_ready", False)),
        "final_study_ready": bool(summary.get("final_study_ready", False)),
        "can_mark_complete": False,
        "review_items": [
            "inspect one matrix row per formal target before creating any formal artifact",
            "use the listed review packets and templates as intake aids only",
            "leave formal targets absent or blocked when source-backed evidence is missing",
            "rerun scripts/validate_formal_acceptance_package.py after any formal artifact is added",
        ],
    }
    preserve_generated_at_when_unchanged(value, manifest)
    write_json_manifest_if_changed(value, manifest, sort_keys=True)
    doc.write_text(
        build_formal_acceptance_evidence_matrix_markdown(value, rows),
        encoding="utf-8",
    )
    return value


def summarize_formal_acceptance_evidence_matrix(
    path: str | Path = DEFAULT_EVIDENCE_MATRIX_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return compact evidence-matrix status for audits."""

    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(manifest_path),
            "row_count": 0,
            "human_decision_required_count": 0,
            "can_mark_complete": False,
            "remaining_blockers": [
                "run scripts/write_formal_acceptance_evidence_matrix.py"
            ],
        }
    with manifest_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, Mapping):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(manifest_path),
        "row_count": int(value.get("row_count", 0)),
        "formal_gate_count": int(value.get("formal_gate_count", 0)),
        "status_counts": dict(value.get("status_counts", {})),
        "human_decision_required_count": int(
            value.get("human_decision_required_count", 0)
        ),
        "formal_acceptance_ready": bool(value.get("formal_acceptance_ready", False)),
        "final_study_ready": bool(value.get("final_study_ready", False)),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "remaining_blockers": list(value.get("review_items", [])),
    }


def build_formal_acceptance_evidence_matrix_markdown(
    manifest: Mapping[str, Any],
    rows: list[dict[str, str]],
) -> str:
    """Render a concise human-readable evidence matrix."""

    lines = [
        "# Formal Review Evidence Matrix",
        "",
        str(manifest.get("claim_boundary", EVIDENCE_MATRIX_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Matrix rows: {manifest.get('row_count', 0)}",
        f"- Formal gates: {manifest.get('formal_gate_count', 0)}",
        f"- Ready formal gates: {manifest.get('ready_gate_count', 0)}",
        f"- Blocked formal gates: {manifest.get('blocked_gate_count', 0)}",
        f"- Human decisions required: {manifest.get('human_decision_required_count', 0)}",
        f"- Formal acceptance ready: `{str(manifest.get('formal_acceptance_ready', False)).lower()}`",
        f"- Final-study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- CSV: `{manifest.get('matrix_path', '')}`",
        "",
        "## Matrix",
        "",
        "| Gate | Agent | Formal Target | Status | Template Or Worksheet | Review Packets | Check Commands |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {gate} | {agent} | `{target}` | `{status}` | `{template}` | {packets} | {validation} |".format(
                gate=_cell(row["gate_id"]),
                agent=_cell(row["assigned_agent"]),
                target=_cell(row["formal_target"]),
                status=_cell(row["formal_status"]),
                template=_cell(row["template_or_worksheet"]),
                packets=_cell(_compact_join(row["review_packets"])),
                validation=_cell(_compact_join(row["validation_commands"])),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Use this matrix as the reviewer intake index. The matrix tells reviewers which packets, templates, paths, and commands belong to each formal target. It must not be copied into a formal acceptance path and cannot make the active goal complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _matrix_row(
    gate: Mapping[str, Any],
    assignments: list[Mapping[str, str]],
    agent: ReviewAgentDefinition | None,
) -> dict[str, str]:
    gate_id = str(gate.get("gate_id", "")).strip()
    blockers = _string_list(gate.get("remaining_blockers", []))
    review_packets = _dedupe(
        [
            *[str(row.get("review_packet", "")) for row in assignments],
            *([] if agent is None else list(agent.review_packet_paths)),
        ]
    )
    templates = _dedupe(
        str(row.get("template_or_worksheet", "")) for row in assignments
    )
    validation_commands = _dedupe(
        str(row.get("validation_command", "")) for row in assignments
    )
    required_actions = _dedupe(
        [
            *([] if agent is None else list(agent.required_actions)),
            *blockers,
            *[str(row.get("blocker", "")) for row in assignments],
        ]
    )
    source_paths = _dedupe(
        [
            *([] if agent is None else list(agent.source_paths)),
            str(gate.get("path", "")).strip(),
        ]
    )
    reviewed_inputs = _dedupe(
        [] if agent is None else list(agent.reviewed_inputs)
    )
    ready = bool(gate.get("ready", False))
    return {
        "gate_id": gate_id,
        "label": str(gate.get("label", gate_id)).strip(),
        "assigned_agent_id": "" if agent is None else str(agent.agent_id),
        "assigned_agent": "" if agent is None else str(agent.role_name),
        "formal_target": str(gate.get("path", "")).strip(),
        "formal_status": str(gate.get("status", "")).strip(),
        "formal_record_present": str(bool(gate.get("record_present", False))).lower(),
        "formal_ready": str(ready).lower(),
        "blocker_count": str(len(blockers)),
        "template_or_worksheet": _join(templates),
        "review_packets": _join(review_packets),
        "source_paths": _join(source_paths),
        "reviewed_inputs": _join(reviewed_inputs),
        "required_actions": _join(required_actions),
        "validation_commands": _join(validation_commands),
        "human_decision_required": str(not ready).lower(),
        "can_mark_complete": "false",
        "claim_boundary": EVIDENCE_MATRIX_BOUNDARY,
    }


def _resolve_agent(
    gate_id: str,
    assignments: list[Mapping[str, str]],
    gate: Mapping[str, Any],
) -> ReviewAgentDefinition | None:
    agent_by_id = {agent.agent_id: agent for agent in REVIEW_AGENT_DEFINITIONS}
    agent_by_gate: dict[str, ReviewAgentDefinition] = {}
    for agent in REVIEW_AGENT_DEFINITIONS:
        for handled_gate in agent.gate_ids:
            agent_by_gate[handled_gate] = agent

    if assignments:
        agent_id = str(assignments[0].get("assigned_agent_id", "")).strip()
        if agent_id in agent_by_id:
            return agent_by_id[agent_id]
    override_id = FORMAL_GATE_AGENT_OVERRIDES.get(gate_id)
    if override_id in agent_by_id:
        return agent_by_id[override_id]
    if gate_id in agent_by_gate:
        return agent_by_gate[gate_id]

    formal_target = str(gate.get("path", "")).strip()
    for agent in REVIEW_AGENT_DEFINITIONS:
        if formal_target in agent.final_acceptance_artifacts:
            return agent
    return None


def _string_list(value: object) -> tuple[str, ...]:
    if isinstance(value, list | tuple):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return (str(value).strip(),) if str(value).strip() else ()


def _dedupe(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        output.append(value)
    return tuple(output)


def _join(values: Iterable[str]) -> str:
    return "; ".join(_dedupe(values))


def _compact_join(value: str) -> str:
    parts = [part.strip() for part in value.split(";") if part.strip()]
    if len(parts) <= 2:
        return "<br>".join(parts) if parts else "none"
    return "<br>".join([parts[0], parts[1], f"+{len(parts) - 2} more"])


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "DEFAULT_EVIDENCE_MATRIX_DOC_PATH",
    "DEFAULT_EVIDENCE_MATRIX_MANIFEST_PATH",
    "DEFAULT_EVIDENCE_MATRIX_PATH",
    "EVIDENCE_MATRIX_BOUNDARY",
    "EVIDENCE_MATRIX_COLUMNS",
    "build_formal_acceptance_evidence_matrix_markdown",
    "build_formal_acceptance_evidence_matrix_rows",
    "summarize_formal_acceptance_evidence_matrix",
    "write_formal_acceptance_evidence_matrix",
]
