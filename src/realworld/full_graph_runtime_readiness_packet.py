"""Full-graph runtime review packet generation.

The graph-scale review packet lists the full bus-practical graph as a possible
method, but the current repository only has a bounded two-row smoke on that
graph. This module turns the smoke evidence and full-profile design counts into
review rows without generating full-graph outputs or accepting a graph-scale
method.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "full_graph_smoke_manifest.json"
)
DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "full_graph_runtime_readiness_packet.csv"
)
DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "full_graph_runtime_readiness_manifest.json"
)
DEFAULT_FULL_GRAPH_RUNTIME_READINESS_DOC_PATH = (
    PROJECT_ROOT / "docs" / "full_graph_runtime_readiness_packet.md"
)
DEFAULT_PILOT_FULL_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json"
)
DEFAULT_FULL_GRAPH_FULL_PROFILE_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_graph_manifest.json"
)
FULL_GRAPH_RUNTIME_READINESS_SCOPE = (
    "Full-graph runtime review packet only; not full-graph experiment "
    "output, not graph-scale acceptance, not calibrated validation, and not "
    "operational routing evidence."
)
FULL_GRAPH_RUNTIME_READINESS_COLUMNS: tuple[str, ...] = (
    "item_id",
    "region_id",
    "source_graph_nodes",
    "source_graph_edges",
    "expected_full_profile_rows",
    "observed_full_graph_rows",
    "observed_smoke_rows",
    "observed_smoke_duration_sec",
    "estimated_full_profile_runtime_sec",
    "evidence_path",
    "readiness_status",
    "blocking_reason",
    "required_reviewer_action",
    "can_support_graph_scale_gate",
    "claim_boundary",
)


def build_full_graph_runtime_readiness_rows(
    *,
    smoke_manifest_path: str | Path = DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH,
    pilot_full_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    full_graph_full_profile_manifest_path: str
    | Path = DEFAULT_FULL_GRAPH_FULL_PROFILE_MANIFEST_PATH,
) -> list[dict[str, str]]:
    """Return review rows for full-graph runtime scope."""

    smoke_path = Path(smoke_manifest_path)
    pilot_path = Path(pilot_full_manifest_path)
    full_profile_path = Path(full_graph_full_profile_manifest_path)
    smoke = _load_json_object(smoke_path)
    pilot = _load_json_object(pilot_path)
    full_profile = _load_json_object(full_profile_path)
    context = _runtime_context(
        smoke=smoke,
        pilot=pilot,
        full_profile=full_profile,
        smoke_path=smoke_path,
        full_profile_path=full_profile_path,
    )
    return [
        _smoke_row(context),
        _full_profile_row(context),
        _runtime_scope_decision_row(context),
        _downstream_regeneration_row(context),
    ]


def write_full_graph_runtime_readiness_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_DOC_PATH,
    smoke_manifest_path: str | Path = DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH,
    pilot_full_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    full_graph_full_profile_manifest_path: str
    | Path = DEFAULT_FULL_GRAPH_FULL_PROFILE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write full-graph runtime review CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FULL_GRAPH_RUNTIME_READINESS_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in FULL_GRAPH_RUNTIME_READINESS_COLUMNS
                }
            )

    summary = build_full_graph_runtime_readiness_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        smoke_manifest_path=smoke_manifest_path,
        pilot_full_manifest_path=pilot_full_manifest_path,
        full_graph_full_profile_manifest_path=full_graph_full_profile_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_full_graph_runtime_readiness_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_full_graph_runtime_readiness_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_DOC_PATH,
    smoke_manifest_path: str | Path = DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH,
    pilot_full_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    full_graph_full_profile_manifest_path: str
    | Path = DEFAULT_FULL_GRAPH_FULL_PROFILE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for full-graph runtime review."""

    status_counts = _counts(row.get("readiness_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("readiness_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("readiness_status", "")).startswith("needs_human_review_")
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            FULL_GRAPH_RUNTIME_READINESS_SCOPE
            + " This packet cannot close data/manifests/graph_scale_acceptance.json."
        ),
        "result_scope": FULL_GRAPH_RUNTIME_READINESS_SCOPE,
        "row_count": len(rows),
        "readiness_status_counts": status_counts,
        "blocking_request_count": blocking_count,
        "human_review_request_count": human_review_count,
        "full_graph_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "full_graph_smoke_manifest": _display_path(Path(smoke_manifest_path)),
            "pilot_full_manifest": _display_path(Path(pilot_full_manifest_path)),
            "full_graph_full_profile_manifest": _display_path(
                Path(full_graph_full_profile_manifest_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "review the measured two-row full-graph smoke before extrapolating runtime",
            "generate full-graph scenario-policy-seed outputs if full-graph execution is selected",
            "or record in graph_scale_acceptance.json why release-scope claims exclude full-graph execution",
            "decide downstream sensitivity, figure, table, and manuscript regeneration scope",
        ],
        "remaining_blockers": [
            "full-graph full-profile outputs are absent",
            "full-graph runtime-scope decision requires graph_scale_acceptance.json",
            "downstream regeneration decisions are unresolved if full-graph execution is selected",
        ],
    }


def build_full_graph_runtime_readiness_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable full-graph runtime review packet."""

    lines = [
        "# Full Graph Runtime Review Packet",
        "",
        str(manifest.get("claim_boundary", FULL_GRAPH_RUNTIME_READINESS_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Review rows: {manifest.get('row_count', 0)}",
        f"- Blocking requests: {manifest.get('blocking_request_count', 0)}",
        f"- Human-review requests: {manifest.get('human_review_request_count', 0)}",
        f"- Status counts: `{manifest.get('readiness_status_counts', {})}`",
        "",
        "## Review Rows",
        "",
        "| Item | Status | Evidence | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {item} | {status} | {evidence} | {action} |".format(
                item=_cell(row.get("item_id", "")),
                status=_cell(row.get("readiness_status", "")),
                evidence=_cell(row.get("evidence_path", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Do not treat smoke runtime as full-profile full-graph evidence.",
            "- Select full graph, reduced corridor, multi-corridor candidate, or an explicitly bounded scope only in the formal graph-scale decision record.",
            "- Re-run affected downstream outputs after the selected graph method is recorded.",
            "",
        ]
    )
    return "\n".join(lines)


def _runtime_context(
    *,
    smoke: Mapping[str, Any],
    pilot: Mapping[str, Any],
    full_profile: Mapping[str, Any],
    smoke_path: Path,
    full_profile_path: Path,
) -> dict[str, Any]:
    expected_rows = _int(pilot.get("expected_row_count")) or _int(pilot.get("row_count"))
    smoke_rows = _int(smoke.get("row_count"))
    smoke_duration = _float(smoke.get("duration_sec"))
    full_profile_rows = _int(full_profile.get("row_count"))
    estimate = ""
    if expected_rows > 0 and smoke_rows > 0 and smoke_duration > 0.0:
        estimate = str(round((smoke_duration / smoke_rows) * expected_rows, 1))
    return {
        "region_id": str(pilot.get("region_id") or smoke.get("region_id") or ""),
        "source_graph_nodes": str(
            _int(smoke.get("graph_nodes"))
            or _int(pilot.get("source_graph_nodes"))
            or _int(pilot.get("graph_nodes"))
        ),
        "source_graph_edges": str(
            _int(smoke.get("graph_edges"))
            or _int(pilot.get("source_graph_edges"))
            or _int(pilot.get("graph_edges"))
        ),
        "expected_full_profile_rows": str(expected_rows),
        "observed_full_graph_rows": str(full_profile_rows),
        "observed_smoke_rows": str(smoke_rows),
        "observed_smoke_duration_sec": (
            "" if smoke_duration <= 0.0 else str(round(smoke_duration, 3))
        ),
        "estimated_full_profile_runtime_sec": estimate,
        "smoke_present": bool(smoke),
        "smoke_passed": bool(smoke.get("smoke_passed", False)),
        "smoke_reduced": bool(smoke.get("analysis_graph_reduced", True)),
        "smoke_path": _display_path(smoke_path),
        "full_profile_present": bool(full_profile),
        "full_profile_reduced": bool(full_profile.get("analysis_graph_reduced", True)),
        "full_profile_path": _display_path(full_profile_path),
    }


def _smoke_row(context: Mapping[str, Any]) -> dict[str, str]:
    status = "blocked_missing_full_graph_smoke_evidence"
    reason = "full graph smoke manifest is absent or did not pass"
    action = "run scripts/run_full_graph_smoke.py before reviewing full-graph runtime scope"
    if (
        context.get("smoke_present")
        and context.get("smoke_passed")
        and not context.get("smoke_reduced")
    ):
        status = "needs_human_review_full_graph_smoke_scope"
        reason = ""
        action = "review the two-row smoke as feasibility evidence only"
    return _row(
        "full_graph_smoke_execution",
        context,
        evidence_path=str(context.get("smoke_path", "")),
        readiness_status=status,
        blocking_reason=reason,
        required_reviewer_action=action,
    )


def _full_profile_row(context: Mapping[str, Any]) -> dict[str, str]:
    expected_rows = _int(context.get("expected_full_profile_rows"))
    observed_rows = _int(context.get("observed_full_graph_rows"))
    if (
        context.get("full_profile_present")
        and not context.get("full_profile_reduced")
        and observed_rows >= expected_rows > 0
    ):
        return _row(
            "full_graph_full_profile_outputs",
            context,
            evidence_path=str(context.get("full_profile_path", "")),
            readiness_status="needs_human_review_full_graph_full_profile_outputs",
            blocking_reason="",
            required_reviewer_action="review full-graph outputs before graph-scale method selection",
        )
    return _row(
        "full_graph_full_profile_outputs",
        context,
        evidence_path=str(context.get("full_profile_path", "")),
        readiness_status="blocked_missing_full_graph_full_profile_outputs",
        blocking_reason="full scenario-policy-seed outputs are absent on the full graph",
        required_reviewer_action=(
            "generate full-graph outputs or formally bound release-scope claims away "
            "from full-graph execution"
        ),
    )


def _runtime_scope_decision_row(context: Mapping[str, Any]) -> dict[str, str]:
    return _row(
        "full_graph_runtime_scope_decision",
        context,
        evidence_path=str(context.get("smoke_path", "")),
        readiness_status="needs_human_review_full_graph_runtime_scope_decision",
        blocking_reason="",
        required_reviewer_action=(
            "decide whether the measured smoke supports excluding full-graph "
            "full-profile execution or whether full outputs must be generated"
        ),
    )


def _downstream_regeneration_row(context: Mapping[str, Any]) -> dict[str, str]:
    return _row(
        "full_graph_downstream_regeneration",
        context,
        evidence_path=str(context.get("full_profile_path", "")),
        readiness_status="blocked_missing_downstream_full_graph_regeneration_decision",
        blocking_reason=(
            "sensitivity, figures, tables, and manuscript interpretation have "
            "not been regenerated for a selected full-graph method"
        ),
        required_reviewer_action=(
            "record downstream regeneration requirements after graph-scale "
            "method selection"
        ),
    )


def _row(
    item_id: str,
    context: Mapping[str, Any],
    *,
    evidence_path: str,
    readiness_status: str,
    blocking_reason: str,
    required_reviewer_action: str,
) -> dict[str, str]:
    return {
        "item_id": item_id,
        "region_id": str(context.get("region_id", "")),
        "source_graph_nodes": str(context.get("source_graph_nodes", "")),
        "source_graph_edges": str(context.get("source_graph_edges", "")),
        "expected_full_profile_rows": str(
            context.get("expected_full_profile_rows", "")
        ),
        "observed_full_graph_rows": str(context.get("observed_full_graph_rows", "")),
        "observed_smoke_rows": str(context.get("observed_smoke_rows", "")),
        "observed_smoke_duration_sec": str(
            context.get("observed_smoke_duration_sec", "")
        ),
        "estimated_full_profile_runtime_sec": str(
            context.get("estimated_full_profile_runtime_sec", "")
        ),
        "evidence_path": evidence_path,
        "readiness_status": readiness_status,
        "blocking_reason": blocking_reason,
        "required_reviewer_action": required_reviewer_action,
        "can_support_graph_scale_gate": "false",
        "claim_boundary": FULL_GRAPH_RUNTIME_READINESS_SCOPE,
    }


def _load_json_object(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        return {}
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _int(value: object) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def _float(value: object) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 0.0


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_FULL_GRAPH_FULL_PROFILE_MANIFEST_PATH",
    "DEFAULT_FULL_GRAPH_RUNTIME_READINESS_DOC_PATH",
    "DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH",
    "DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH",
    "DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH",
    "FULL_GRAPH_RUNTIME_READINESS_COLUMNS",
    "FULL_GRAPH_RUNTIME_READINESS_SCOPE",
    "build_full_graph_runtime_readiness_manifest",
    "build_full_graph_runtime_readiness_markdown",
    "build_full_graph_runtime_readiness_rows",
    "write_full_graph_runtime_readiness_packet",
]
