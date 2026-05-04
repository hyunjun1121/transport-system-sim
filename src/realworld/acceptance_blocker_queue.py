"""Machine-readable queue for remaining formal acceptance blockers."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from src.realworld.formal_acceptance_package import (
    CLAIM_BOUNDARY,
    build_formal_acceptance_package_summary,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BLOCKER_QUEUE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "formal_acceptance_blocker_queue.csv"
)
DEFAULT_BLOCKER_QUEUE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "formal_acceptance_blocker_queue_manifest.json"
)
DEFAULT_BLOCKER_QUEUE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "formal_acceptance_blocker_queue.md"
)

BLOCKER_QUEUE_COLUMNS: tuple[str, ...] = (
    "gate_id",
    "label",
    "status",
    "formal_target",
    "review_packet",
    "template_or_worksheet",
    "blocker",
    "action_type",
    "requires_human_review",
    "can_mark_complete",
    "claim_boundary",
)

NON_APPROVAL_BOUNDARY = (
    "Formal acceptance blocker queue only. Rows are work items for reviewers; "
    "they do not create approvals, source evidence, calibrated validation, or "
    "operational routing permission."
)

REVIEW_PACKET_BY_GATE: dict[str, str] = {
    "pilot_region_accepted": "docs/review_packets/pilot_region_accepted.md",
    "graph_scale_strategy": "docs/review_packets/graph_scale_strategy.md",
    "data_provenance": "docs/review_packets/data_provenance.md",
    "parameter_acceptance": "docs/review_packets/parameter_evidence.md",
    "road_class_overrides": "docs/review_packets/cached_osm_input.md",
    "validation_package": "docs/review_packets/validation_package.md",
    "sensitivity_analysis": "docs/review_packets/sensitivity_analysis.md",
    "full_experiment_output": "docs/review_packets/full_experiment_output.md",
    "manuscript_report_alignment": "docs/review_packets/manuscript_report_alignment.md",
    "reproducibility": "docs/review_packets/reproducibility.md",
    "final_audit_document": "docs/review_packets/final_audit.md",
    "final_audit": "docs/review_packets/final_audit.md",
}

TEMPLATE_OR_WORKSHEET_BY_GATE: dict[str, str] = {
    "pilot_region_accepted": (
        "data/manifests/acceptance_templates/pilot_acceptance_template.json"
    ),
    "graph_scale_strategy": (
        "data/manifests/acceptance_templates/graph_scale_acceptance_template.json"
    ),
    "data_provenance": (
        "data/manifests/acceptance_templates/provenance_acceptance_template.json"
    ),
    "parameter_acceptance": "data/parameters/parameter_acceptance_template.csv",
    "road_class_overrides": "data/parameters/road_class_overrides_draft.csv",
    "validation_package": (
        "data/manifests/acceptance_templates/validation_acceptance_template.json"
    ),
    "sensitivity_analysis": (
        "data/manifests/acceptance_templates/sensitivity_acceptance_template.json"
    ),
    "full_experiment_output": (
        "data/manifests/acceptance_templates/experiment_acceptance_template.json"
    ),
    "manuscript_report_alignment": (
        "data/manifests/acceptance_templates/manuscript_acceptance_template.json"
    ),
    "reproducibility": (
        "data/manifests/acceptance_templates/reproducibility_acceptance_template.json"
    ),
    "final_audit_document": "docs/human_acceptance_runbook.md",
    "final_audit": (
        "data/manifests/acceptance_templates/final_audit_acceptance_template.json"
    ),
}


def build_acceptance_blocker_queue_rows(
    *,
    package_summary: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Return one CSV row per unresolved formal acceptance blocker."""

    summary = package_summary or build_formal_acceptance_package_summary()
    rows: list[dict[str, str]] = []
    for gate in summary.get("gates", []):
        if not isinstance(gate, Mapping):
            continue
        gate_id = str(gate.get("gate_id", "")).strip()
        blockers = gate.get("remaining_blockers", [])
        if not isinstance(blockers, list):
            blockers = [blockers] if blockers else []
        for blocker in blockers:
            blocker_text = str(blocker).strip()
            if not blocker_text:
                continue
            rows.append(_queue_row(gate, blocker_text))
    return rows


def write_acceptance_blocker_queue(
    *,
    output_path: str | Path = DEFAULT_BLOCKER_QUEUE_PATH,
    manifest_path: str | Path = DEFAULT_BLOCKER_QUEUE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_BLOCKER_QUEUE_DOC_PATH,
    package_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Write CSV, JSON manifest, and Markdown documentation for blockers."""

    summary = package_summary or build_formal_acceptance_package_summary()
    rows = build_acceptance_blocker_queue_rows(package_summary=summary)
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=BLOCKER_QUEUE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    status_counts: dict[str, int] = {}
    for row in rows:
        status = row["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    value = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": NON_APPROVAL_BOUNDARY,
        "package_claim_boundary": summary.get("claim_boundary", CLAIM_BOUNDARY),
        "queue_path": _display_path(output),
        "row_count": len(rows),
        "gate_count": int(summary.get("gate_count", 0)),
        "formal_acceptance_ready": bool(summary.get("formal_acceptance_ready", False)),
        "final_study_ready": bool(summary.get("final_study_ready", False)),
        "can_mark_complete": False,
        "status_counts": status_counts,
        "requires_human_review_count": sum(
            1 for row in rows if row["requires_human_review"] == "true"
        ),
        "review_items": [
            "resolve each row with source-backed evidence or keep the formal target absent",
            "rerun validate_formal_acceptance_package.py after any formal artifact is added",
            "do not treat this queue as acceptance or calibration evidence",
        ],
    }
    manifest.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(build_acceptance_blocker_queue_markdown(value, rows), encoding="utf-8")
    return value


def summarize_acceptance_blocker_queue(
    path: str | Path = DEFAULT_BLOCKER_QUEUE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return compact blocker-queue status for audits."""

    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(manifest_path),
            "row_count": 0,
            "can_mark_complete": False,
            "remaining_blockers": ["run scripts/write_acceptance_blocker_queue.py"],
        }
    with manifest_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, Mapping):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(manifest_path),
        "row_count": int(value.get("row_count", 0)),
        "status_counts": dict(value.get("status_counts", {})),
        "formal_acceptance_ready": bool(value.get("formal_acceptance_ready", False)),
        "final_study_ready": bool(value.get("final_study_ready", False)),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "remaining_blockers": list(value.get("review_items", [])),
    }


def build_acceptance_blocker_queue_markdown(
    manifest: Mapping[str, Any],
    rows: list[dict[str, str]],
) -> str:
    """Render a concise human-readable queue document."""

    lines = [
        "# Formal Acceptance Blocker Queue",
        "",
        str(manifest.get("claim_boundary", NON_APPROVAL_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Queue rows: {manifest.get('row_count', 0)}",
        f"- Formal acceptance ready: `{str(manifest.get('formal_acceptance_ready', False)).lower()}`",
        f"- Final-study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- CSV: `{manifest.get('queue_path', '')}`",
        "",
        "## Queue",
        "",
        "| Gate | Action Type | Formal Target | Review Packet | Blocker |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {gate} | {action} | `{target}` | `{packet}` | {blocker} |".format(
                gate=_cell(row["gate_id"]),
                action=_cell(row["action_type"]),
                target=_cell(row["formal_target"]),
                packet=_cell(row["review_packet"]),
                blocker=_cell(row["blocker"]),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Work this queue from top to bottom. If evidence is missing, leave the formal target absent. If evidence exists, update the formal target with a real reviewed decision and rerun the formal acceptance audits.",
            "",
        ]
    )
    return "\n".join(lines)


def _queue_row(gate: Mapping[str, Any], blocker: str) -> dict[str, str]:
    gate_id = str(gate.get("gate_id", "")).strip()
    return {
        "gate_id": gate_id,
        "label": str(gate.get("label", gate_id)).strip(),
        "status": str(gate.get("status", "")).strip(),
        "formal_target": str(gate.get("path", "")).strip(),
        "review_packet": REVIEW_PACKET_BY_GATE.get(gate_id, ""),
        "template_or_worksheet": TEMPLATE_OR_WORKSHEET_BY_GATE.get(gate_id, ""),
        "blocker": blocker,
        "action_type": _action_type(blocker),
        "requires_human_review": "true",
        "can_mark_complete": "false",
        "claim_boundary": NON_APPROVAL_BOUNDARY,
    }


def _action_type(blocker: str) -> str:
    text = blocker.lower()
    if "missing" in text or "absent" in text or "create" in text:
        return "create_or_supply_formal_evidence"
    if "replace" in text:
        return "replace_weak_or_scaffold_evidence"
    if "apply" in text:
        return "apply_reviewed_input_and_regenerate"
    if "review" in text:
        return "review_and_decide"
    return "resolve_blocker"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


__all__ = [
    "BLOCKER_QUEUE_COLUMNS",
    "DEFAULT_BLOCKER_QUEUE_DOC_PATH",
    "DEFAULT_BLOCKER_QUEUE_MANIFEST_PATH",
    "DEFAULT_BLOCKER_QUEUE_PATH",
    "NON_APPROVAL_BOUNDARY",
    "build_acceptance_blocker_queue_markdown",
    "build_acceptance_blocker_queue_rows",
    "summarize_acceptance_blocker_queue",
    "write_acceptance_blocker_queue",
]
