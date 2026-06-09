"""Assign formal acceptance blockers to deterministic review-agent roles.

This module turns the formal acceptance blocker queue into an auditable work
assignment table. It is still a non-approval artifact: each task tells a
reviewer what evidence or decision is needed, but it cannot accept a gate.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from src.realworld.acceptance_blocker_queue import (
    BLOCKER_QUEUE_COLUMNS,
    NON_APPROVAL_BOUNDARY as BLOCKER_QUEUE_BOUNDARY,
    build_acceptance_blocker_queue_rows,
)
from src.realworld.acceptance_orchestration import (
    ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
    REVIEW_AGENT_DEFINITIONS,
)
from src.realworld.formal_acceptance_package import (
    build_formal_acceptance_package_summary,
)
from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASK_ASSIGNMENT_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "acceptance_task_assignments.csv"
)
DEFAULT_TASK_ASSIGNMENT_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "acceptance_task_assignments_manifest.json"
)
DEFAULT_TASK_ASSIGNMENT_DOC_PATH = (
    PROJECT_ROOT / "docs" / "acceptance_task_assignments.md"
)

TASK_ASSIGNMENT_COLUMNS: tuple[str, ...] = (
    "task_id",
    "gate_id",
    "label",
    "assigned_agent_id",
    "assigned_agent",
    "status",
    "formal_target",
    "review_packet",
    "template_or_worksheet",
    "blocker",
    "action_type",
    "required_output",
    "validation_command",
    "requires_human_review",
    "can_mark_complete",
    "claim_boundary",
)

TASK_ASSIGNMENT_BOUNDARY = (
    "Sub-agent task assignments only. These rows assign review work; they do "
    "not approve evidence, certify licenses, validate calibration, or close "
    "final-study gates."
)

FORMAL_GATE_AGENT_OVERRIDES: dict[str, str] = {
    "parameter_acceptance": "road_rail_parameter_evidence_agent",
    "road_class_overrides": "road_rail_parameter_evidence_agent",
    "final_audit_document": "final_independent_audit_agent",
}


def build_acceptance_task_assignment_rows(
    *,
    package_summary: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Return one assignment row per unresolved formal blocker."""

    summary = package_summary or build_formal_acceptance_package_summary()
    blocker_rows = build_acceptance_blocker_queue_rows(package_summary=summary)
    agent_by_gate, agent_by_id = _build_agent_maps()
    rows: list[dict[str, str]] = []
    for index, blocker_row in enumerate(blocker_rows, start=1):
        gate_id = blocker_row["gate_id"]
        agent_id = FORMAL_GATE_AGENT_OVERRIDES.get(gate_id)
        agent = agent_by_id.get(agent_id or "") if agent_id else None
        if agent is None:
            agent = agent_by_gate.get(gate_id)
        if agent is None:
            raise ValueError(f"no review agent assignment for gate {gate_id!r}")
        rows.append(_assignment_row(index, blocker_row, agent))
    return rows


def write_acceptance_task_assignments(
    *,
    output_path: str | Path = DEFAULT_TASK_ASSIGNMENT_PATH,
    manifest_path: str | Path = DEFAULT_TASK_ASSIGNMENT_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_TASK_ASSIGNMENT_DOC_PATH,
    package_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Write CSV, JSON manifest, and Markdown assignment guide."""

    summary = package_summary or build_formal_acceptance_package_summary()
    rows = build_acceptance_task_assignment_rows(package_summary=summary)
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TASK_ASSIGNMENT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    agent_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    for row in rows:
        agent_counts[row["assigned_agent_id"]] = (
            agent_counts.get(row["assigned_agent_id"], 0) + 1
        )
        action_counts[row["action_type"]] = action_counts.get(row["action_type"], 0) + 1

    value = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": TASK_ASSIGNMENT_BOUNDARY,
        "blocker_queue_claim_boundary": BLOCKER_QUEUE_BOUNDARY,
        "orchestration_claim_boundary": ACCEPTANCE_ORCHESTRATION_CLAIM_BOUNDARY,
        "assignment_path": _display_path(output),
        "task_count": len(rows),
        "assigned_agent_count": len(agent_counts),
        "agent_task_counts": agent_counts,
        "action_type_counts": action_counts,
        "requires_human_review_count": sum(
            1 for row in rows if row["requires_human_review"] == "true"
        ),
        "formal_acceptance_ready": bool(summary.get("formal_acceptance_ready", False)),
        "final_study_ready": bool(summary.get("final_study_ready", False)),
        "can_mark_complete": False,
        "review_items": [
            "each task requires source-backed evidence or an explicit blocked decision",
        "review packets and templates are aids only, not formal decisions",
            "rerun scripts/run_acceptance_audit.py after any formal artifact changes",
        ],
    }
    preserve_generated_at_when_unchanged(value, manifest)
    write_json_manifest_if_changed(value, manifest, sort_keys=True)
    doc.write_text(build_acceptance_task_assignment_markdown(value, rows), encoding="utf-8")
    return value


def summarize_acceptance_task_assignments(
    path: str | Path = DEFAULT_TASK_ASSIGNMENT_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return compact assignment status for audits."""

    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(manifest_path),
            "task_count": 0,
            "assigned_agent_count": 0,
            "can_mark_complete": False,
            "remaining_blockers": ["run scripts/write_acceptance_task_assignments.py"],
        }
    with manifest_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, Mapping):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(manifest_path),
        "task_count": int(value.get("task_count", 0)),
        "assigned_agent_count": int(value.get("assigned_agent_count", 0)),
        "requires_human_review_count": int(
            value.get("requires_human_review_count", 0)
        ),
        "formal_acceptance_ready": bool(value.get("formal_acceptance_ready", False)),
        "final_study_ready": bool(value.get("final_study_ready", False)),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "remaining_blockers": list(value.get("review_items", [])),
    }


def build_acceptance_task_assignment_markdown(
    manifest: Mapping[str, Any],
    rows: list[dict[str, str]],
) -> str:
    """Render a human-readable task assignment document."""

    lines = [
        "# Reviewer Task Assignments",
        "",
        str(manifest.get("claim_boundary", TASK_ASSIGNMENT_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Tasks: {manifest.get('task_count', 0)}",
        f"- Assigned agents: {manifest.get('assigned_agent_count', 0)}",
        f"- Formal decision ready: `{str(manifest.get('formal_acceptance_ready', False)).lower()}`",
        f"- Study-closeout ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- CSV: `{manifest.get('assignment_path', '')}`",
        "",
        "## Assignments",
        "",
        "| Task | Gate | Agent | Action Type | Formal Target | Required Output |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {task} | {gate} | {agent} | {action} | `{target}` | {required} |".format(
                task=_cell(row["task_id"]),
                gate=_cell(row["gate_id"]),
                agent=_cell(row["assigned_agent"]),
                action=_cell(row["action_type"]),
                target=_cell(row["formal_target"]),
                required=_cell(row["required_output"]),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Use this file to assign human/source-backed review work to the deterministic sub-agent roles. If a task cannot be resolved with evidence, keep the formal target absent or explicitly blocked and rerun the audit.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_agent_maps() -> tuple[dict[str, Any], dict[str, Any]]:
    agent_by_gate: dict[str, Any] = {}
    agent_by_id: dict[str, Any] = {}
    for agent in REVIEW_AGENT_DEFINITIONS:
        agent_by_id[agent.agent_id] = agent
        for gate_id in agent.gate_ids:
            agent_by_gate[gate_id] = agent
    return agent_by_gate, agent_by_id


def _assignment_row(index: int, blocker_row: Mapping[str, str], agent: Any) -> dict[str, str]:
    _validate_blocker_row(blocker_row)
    formal_target = str(blocker_row["formal_target"]).strip()
    return {
        "task_id": f"acceptance_task_{index:03d}",
        "gate_id": str(blocker_row["gate_id"]).strip(),
        "label": str(blocker_row["label"]).strip(),
        "assigned_agent_id": str(agent.agent_id),
        "assigned_agent": str(agent.role_name),
        "status": str(blocker_row["status"]).strip(),
        "formal_target": formal_target,
        "review_packet": str(blocker_row["review_packet"]).strip(),
        "template_or_worksheet": str(blocker_row["template_or_worksheet"]).strip(),
        "blocker": str(blocker_row["blocker"]).strip(),
        "action_type": str(blocker_row["action_type"]).strip(),
        "required_output": _required_output(formal_target),
        "validation_command": _validation_command(formal_target),
        "requires_human_review": "true",
        "can_mark_complete": "false",
        "claim_boundary": TASK_ASSIGNMENT_BOUNDARY,
    }


def _validate_blocker_row(row: Mapping[str, str]) -> None:
    missing = [column for column in BLOCKER_QUEUE_COLUMNS if column not in row]
    if missing:
        raise ValueError("blocker row missing columns: " + ", ".join(missing))


def _required_output(formal_target: str) -> str:
    if formal_target.endswith(".json"):
        return "reviewed JSON decision record with real evidence paths"
    if formal_target.endswith(".csv"):
        return "reviewed CSV rows with source-backed or explicitly retained values"
    if formal_target.endswith(".md"):
        return "independent closeout audit document after all prerequisite gates close"
    return "reviewed formal evidence artifact"


def _validation_command(formal_target: str) -> str:
    if formal_target.endswith("road_class_overrides.csv"):
        return (
            ".\\.venv\\Scripts\\python scripts\\audit_road_overrides.py; "
            ".\\.venv\\Scripts\\python scripts\\validate_formal_acceptance_package.py"
        )
    if formal_target.endswith("parameter_acceptance.csv"):
        return (
            ".\\.venv\\Scripts\\python tests\\test_realworld_parameter_acceptance.py; "
            ".\\.venv\\Scripts\\python scripts\\validate_formal_acceptance_package.py"
        )
    return ".\\.venv\\Scripts\\python scripts\\validate_formal_acceptance_package.py"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


__all__ = [
    "DEFAULT_TASK_ASSIGNMENT_DOC_PATH",
    "DEFAULT_TASK_ASSIGNMENT_MANIFEST_PATH",
    "DEFAULT_TASK_ASSIGNMENT_PATH",
    "FORMAL_GATE_AGENT_OVERRIDES",
    "TASK_ASSIGNMENT_BOUNDARY",
    "TASK_ASSIGNMENT_COLUMNS",
    "build_acceptance_task_assignment_markdown",
    "build_acceptance_task_assignment_rows",
    "summarize_acceptance_task_assignments",
    "write_acceptance_task_assignments",
]
