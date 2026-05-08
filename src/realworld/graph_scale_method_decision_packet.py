"""Focused graph-scale method decision worksheet.

The graph-scale review and strategy-readiness packets show feasible graph
options and blockers. This module turns that state into explicit reviewer
decision rows without choosing a graph method, creating
``data/manifests/graph_scale_acceptance.json``, or closing the graph-scale
gate.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.full_graph_runtime_readiness_packet import (
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH,
)
from src.realworld.graph_scale_review import (
    DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
)
from src.realworld.graph_scale_strategy_readiness_packet import (
    DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
    DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH_SCALE_METHOD_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_method_decision_packet.csv"
)
DEFAULT_GRAPH_SCALE_METHOD_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "graph_scale_method_decision_manifest.json"
)
DEFAULT_GRAPH_SCALE_METHOD_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "graph_scale_method_decision_packet.md"
)
GRAPH_SCALE_METHOD_DECISION_SCOPE = (
    "Graph-scale method-decision packet only; not graph-scale acceptance, "
    "not calibrated real-world validation, not traffic model validation, and "
    "not operational routing evidence."
)
GRAPH_SCALE_METHOD_DECISION_COLUMNS: tuple[str, ...] = (
    "decision_id",
    "decision_topic",
    "candidate_decision",
    "current_evidence",
    "decision_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_graph_scale_gate",
    "claim_boundary",
)


def build_graph_scale_method_decision_rows(
    *,
    review_packet_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
    review_manifest_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH,
    strategy_manifest_path: str
    | Path = DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
    result_comparison_manifest_path: str
    | Path = DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH,
    full_graph_runtime_manifest_path: str
    | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
    acceptance_path: str | Path = DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return reviewer rows for graph-scale method selection decisions."""

    review_rows = _load_csv_rows(review_packet_path)
    review_manifest = _read_json_object(review_manifest_path)
    strategy_manifest = _read_json_object(strategy_manifest_path)
    result_manifest = _read_json_object(result_comparison_manifest_path)
    runtime_manifest = _read_json_object(full_graph_runtime_manifest_path)
    acceptance = Path(acceptance_path)
    by_option = {str(row.get("option_id", "")): row for row in review_rows}
    evidence_paths = _evidence_paths(
        review_packet_path=review_packet_path,
        review_manifest_path=review_manifest_path,
        strategy_manifest_path=strategy_manifest_path,
        result_comparison_manifest_path=result_comparison_manifest_path,
        full_graph_runtime_manifest_path=full_graph_runtime_manifest_path,
    )

    return [
        _row(
            decision_id="current_reduced_corridor_method_option",
            decision_topic="Current reduced-corridor method",
            candidate_decision=(
                "Accept the current 118-node reduced corridor only if omitted "
                "alternate paths are immaterial under a documented "
                "corridor-selection rule"
            ),
            current_evidence=_option_evidence(
                by_option.get("current_reduced_corridor", {})
            ),
            decision_status=(
                "needs_human_review_reduced_corridor_warning_policy"
            ),
            blocking_reason="",
            required_reviewer_action=(
                "Decide whether the six alternate-route warning rows are "
                "acceptable or require a broader graph method."
            ),
            followup_artifacts="data/manifests/graph_scale_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="multi_corridor_candidate_method_option",
            decision_topic="164-node multi-corridor candidate",
            candidate_decision=(
                "Use the 164-node multi-corridor graph only after deciding "
                "whether the separated candidate output is sufficient or a "
                "full-profile run is required"
            ),
            current_evidence=_option_evidence(
                by_option.get("multi_corridor_candidate", {})
            ),
            decision_status="blocked_incomplete_multi_corridor_run_profile",
            blocking_reason=(
                "multi-corridor candidate has only separated/sample-scale output"
            ),
            required_reviewer_action=(
                "Use the existing full-profile candidate, regenerate the "
                "accepted output package on this graph, or exclude this option."
            ),
            followup_artifacts=(
                "results/realworld_pilot/pilot_multi_corridor_full_manifest.json; "
                "data/manifests/graph_scale_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="multi_corridor_full_candidate_method_option",
            decision_topic="164-node full-profile multi-corridor candidate",
            candidate_decision=(
                "Replace the current reduced corridor with the full-profile "
                "multi-corridor candidate if result deltas are reviewed and "
                "downstream artifacts are regenerated as needed"
            ),
            current_evidence=(
                _option_evidence(
                    by_option.get("multi_corridor_full_candidate", {})
                )
                + "; "
                + _result_comparison_evidence(result_manifest)
            ),
            decision_status="needs_human_review_multi_corridor_result_delta_policy",
            blocking_reason="",
            required_reviewer_action=(
                "Review candidate_worsens and nonfinite result differences "
                "before selecting the multi-corridor full-profile method."
            ),
            followup_artifacts=(
                "data/validation/graph_scale_result_comparison.csv; "
                "data/manifests/graph_scale_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="full_bus_practical_graph_method_option",
            decision_topic="Full bus-practical graph option",
            candidate_decision=(
                "Use the full 4,608-node bus-practical graph only if full "
                "scenario-policy-seed outputs are generated or formally "
                "excluded from scope"
            ),
            current_evidence=(
                _option_evidence(by_option.get("full_bus_practical_graph", {}))
                + "; "
                + _runtime_evidence(runtime_manifest)
            ),
            decision_status="blocked_missing_full_graph_full_profile_outputs",
            blocking_reason=(
                "full bus-practical graph has smoke/runtime evidence only, "
                "not full scenario-policy-seed output"
            ),
            required_reviewer_action=(
                "Generate full-graph outputs or record in the formal graph-scale "
                "acceptance why full-graph execution is outside scope."
            ),
            followup_artifacts=(
                "results/realworld_pilot/pilot_full_graph_manifest.json; "
                "data/manifests/graph_scale_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="graph_sensitive_result_interpretation",
            decision_topic="Graph-sensitive result interpretation",
            candidate_decision=(
                "Interpret policy outcomes only after selecting a graph method "
                "and reviewing current-vs-candidate result differences"
            ),
            current_evidence=_result_comparison_evidence(result_manifest),
            decision_status="needs_human_review_graph_sensitive_result_deltas",
            blocking_reason="",
            required_reviewer_action=(
                "Decide whether changed outcomes reflect a better graph "
                "abstraction or a scenario-method interaction that requires "
                "additional runs."
            ),
            followup_artifacts=(
                "data/validation/graph_scale_result_comparison.csv; "
                "paper/paper_draft.md; report_draft.md"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="downstream_regeneration_scope",
            decision_topic="Downstream regeneration after method selection",
            candidate_decision=(
                "Regenerate or explicitly retain sensitivity, figures, tables, "
                "experiment summaries, and manuscript interpretation after the "
                "accepted graph method is selected"
            ),
            current_evidence=_strategy_evidence(strategy_manifest),
            decision_status="blocked_missing_downstream_regeneration_decision",
            blocking_reason=(
                "accepted graph choice still requires downstream regeneration "
                "decisions for sensitivity, figures, tables, and manuscript "
                "interpretation"
            ),
            required_reviewer_action=(
                "Record which downstream artifacts will be regenerated, retained "
                "as review evidence, or excluded from final claims."
            ),
            followup_artifacts=(
                "results/realworld_pilot/morris_manifest.json; "
                "results/realworld_pilot/tables/figure_table_manifest.json; "
                "data/manifests/graph_scale_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="formal_graph_scale_acceptance_boundary",
            decision_topic="Formal graph-scale acceptance",
            candidate_decision=(
                "Record the selected graph-scale method, source graph counts, "
                "analysis graph counts, evidence paths, and claim boundary only "
                "in the formal acceptance path"
            ),
            current_evidence=(
                f"acceptance_path={_display_path(acceptance)}; "
                f"acceptance_present={str(acceptance.exists()).lower()}; "
                f"review_options={_int(review_manifest.get('row_count'))}"
            ),
            decision_status=(
                "needs_human_review_existing_graph_scale_acceptance"
                if acceptance.exists()
                else "blocked_missing_graph_scale_acceptance_record"
            ),
            blocking_reason=(
                ""
                if acceptance.exists()
                else "data/manifests/graph_scale_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Create or validate graph_scale_acceptance.json only after "
                "source-backed human review; do not copy this packet into the "
                "formal path."
            ),
            followup_artifacts="data/manifests/graph_scale_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_graph_scale_method_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_GRAPH_SCALE_METHOD_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_GRAPH_SCALE_METHOD_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_GRAPH_SCALE_METHOD_DECISION_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
    review_manifest_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH,
    strategy_manifest_path: str
    | Path = DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
    result_comparison_manifest_path: str
    | Path = DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH,
    full_graph_runtime_manifest_path: str
    | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write graph-scale method-decision CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=GRAPH_SCALE_METHOD_DECISION_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in GRAPH_SCALE_METHOD_DECISION_COLUMNS
                }
            )

    summary = build_graph_scale_method_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        review_packet_path=review_packet_path,
        review_manifest_path=review_manifest_path,
        strategy_manifest_path=strategy_manifest_path,
        result_comparison_manifest_path=result_comparison_manifest_path,
        full_graph_runtime_manifest_path=full_graph_runtime_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_graph_scale_method_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_graph_scale_method_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_GRAPH_SCALE_METHOD_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_GRAPH_SCALE_METHOD_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_GRAPH_SCALE_METHOD_DECISION_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
    review_manifest_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH,
    strategy_manifest_path: str
    | Path = DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
    result_comparison_manifest_path: str
    | Path = DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH,
    full_graph_runtime_manifest_path: str
    | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for graph-scale method decisions."""

    status_counts = _counts(row.get("decision_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("decision_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("decision_status", "")).startswith("needs_human_review_")
    )
    return {
        "schema_version": 1,
        "result_scope": GRAPH_SCALE_METHOD_DECISION_SCOPE,
        "claim_boundary": (
            GRAPH_SCALE_METHOD_DECISION_SCOPE
            + " It cannot create data/manifests/graph_scale_acceptance.json."
        ),
        "row_count": len(rows),
        "decision_ids": [str(row.get("decision_id", "")) for row in rows],
        "decision_status_counts": status_counts,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "selected_graph_method_recorded": False,
        "downstream_regeneration_decision_recorded": False,
        "graph_scale_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "graph_scale_review_packet": _display_path(Path(review_packet_path)),
            "graph_scale_review_manifest": _display_path(Path(review_manifest_path)),
            "graph_scale_strategy_readiness_manifest": _display_path(
                Path(strategy_manifest_path)
            ),
            "graph_scale_result_comparison_manifest": _display_path(
                Path(result_comparison_manifest_path)
            ),
            "full_graph_runtime_readiness_manifest": _display_path(
                Path(full_graph_runtime_manifest_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "decide whether current reduced-corridor alternate-route warnings are acceptable",
            "decide whether the 164-node full-profile multi-corridor candidate should replace the current analysis graph",
            "decide whether full-graph execution must be generated or formally scoped out",
            "review graph-sensitive result deltas before interpreting policy outcomes",
            "record downstream regeneration requirements after method selection",
            "record final graph-scale decisions only in data/manifests/graph_scale_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_graph_scale_method_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown graph-scale method-decision worksheet."""

    lines = [
        "# Graph-Scale Method Decision Packet",
        "",
        str(manifest.get("claim_boundary", GRAPH_SCALE_METHOD_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Selected graph method recorded: `{str(manifest.get('selected_graph_method_recorded', False)).lower()}`",
        f"- Downstream regeneration decision recorded: `{str(manifest.get('downstream_regeneration_decision_recorded', False)).lower()}`",
        f"- Decision rows: {manifest.get('row_count', 0)}",
        f"- Blocking decisions: {manifest.get('blocking_decision_count', 0)}",
        f"- Human-review decisions: {manifest.get('human_review_decision_count', 0)}",
        f"- Status counts: `{manifest.get('decision_status_counts', {})}`",
        "",
        "## Decision Rows",
        "",
        "| Decision | Status | Candidate | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {decision} | {status} | {candidate} | {action} |".format(
                decision=_cell(row.get("decision_id", "")),
                status=_cell(row.get("decision_status", "")),
                candidate=_cell(row.get("candidate_decision", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is a reviewer worksheet, not an acceptance record.",
            "- It does not select a graph method, approve full-graph exclusion, or accept downstream regeneration scope.",
            "- Keep graph-scale claims blocked until `data/manifests/graph_scale_acceptance.json` is reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(
    *,
    decision_id: str,
    decision_topic: str,
    candidate_decision: str,
    current_evidence: str,
    decision_status: str,
    blocking_reason: str,
    required_reviewer_action: str,
    followup_artifacts: str,
    evidence_input_paths: str,
) -> dict[str, str]:
    return {
        "decision_id": decision_id,
        "decision_topic": decision_topic,
        "candidate_decision": candidate_decision,
        "current_evidence": current_evidence,
        "decision_status": decision_status,
        "blocking_reason": blocking_reason,
        "required_reviewer_action": required_reviewer_action,
        "followup_artifacts": followup_artifacts,
        "evidence_input_paths": evidence_input_paths,
        "can_support_graph_scale_gate": "false",
        "claim_boundary": GRAPH_SCALE_METHOD_DECISION_SCOPE,
    }


def _option_evidence(row: Mapping[str, Any]) -> str:
    if not row:
        return "graph-scale review row missing"
    parts = [
        f"option_id={row.get('option_id', '')}",
        f"source_graph={row.get('source_graph_nodes', '')}/{row.get('source_graph_edges', '')}",
        f"analysis_graph={row.get('analysis_graph_nodes', '')}/{row.get('analysis_graph_edges', '')}",
        f"analysis_graph_reduced={row.get('analysis_graph_reduced', '')}",
        f"alternate_route_warn={row.get('alternate_route_warn', '')}",
        f"alternate_paths_preserved={row.get('alternate_paths_preserved', '')}",
        f"experiment_run_profile={row.get('experiment_run_profile', '')}",
        f"experiment_rows={row.get('experiment_row_count', '')}",
    ]
    return "; ".join(parts)


def _result_comparison_evidence(manifest: Mapping[str, Any]) -> str:
    counts = _mapping_value(manifest, "comparison_status_counts")
    if not counts:
        return "result_comparison_manifest_missing_or_invalid"
    return (
        f"comparison_rows={_int(manifest.get('row_count'))}; "
        f"candidate_improves={_int(counts.get('candidate_improves'))}; "
        f"candidate_worsens={_int(counts.get('candidate_worsens'))}; "
        f"nonfinite_difference={_int(counts.get('nonfinite_difference'))}; "
        f"same_or_close={_int(counts.get('same_or_close'))}"
    )


def _runtime_evidence(manifest: Mapping[str, Any]) -> str:
    counts = _mapping_value(manifest, "readiness_status_counts")
    if not manifest:
        return "full_graph_runtime_readiness_manifest_missing"
    return (
        f"runtime_rows={_int(manifest.get('row_count'))}; "
        f"runtime_blocking_requests={_int(manifest.get('blocking_request_count'))}; "
        f"runtime_human_review_requests={_int(manifest.get('human_review_request_count'))}; "
        f"runtime_status_counts={_format_counts(counts)}"
    )


def _strategy_evidence(manifest: Mapping[str, Any]) -> str:
    blockers = _list_value(manifest, "remaining_blockers")
    return (
        f"strategy_rows={_int(manifest.get('row_count'))}; "
        f"strategy_blocking_requests={_int(manifest.get('blocking_request_count'))}; "
        f"strategy_human_review_requests={_int(manifest.get('human_review_request_count'))}; "
        f"remaining_blockers={len(blockers)}"
    )


def _evidence_paths(
    *,
    review_packet_path: str | Path,
    review_manifest_path: str | Path,
    strategy_manifest_path: str | Path,
    result_comparison_manifest_path: str | Path,
    full_graph_runtime_manifest_path: str | Path,
) -> str:
    paths = [
        review_packet_path,
        review_manifest_path,
        DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH,
        strategy_manifest_path,
        DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH,
        full_graph_runtime_manifest_path,
        result_comparison_manifest_path,
    ]
    return "; ".join(_display_path(Path(path)) for path in paths)


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("decision_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(reason)
    return blockers


def _load_csv_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json_object(path: str | Path) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        return {}
    with filepath.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _mapping_value(mapping: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key, {})
    return dict(value) if isinstance(value, Mapping) else {}


def _list_value(mapping: Mapping[str, Any], key: str) -> list[str]:
    value = mapping.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _format_counts(counts: Mapping[str, Any]) -> str:
    return "; ".join(f"{key}={counts[key]}" for key in sorted(counts))


def _int(value: object) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_GRAPH_SCALE_METHOD_DECISION_DOC_PATH",
    "DEFAULT_GRAPH_SCALE_METHOD_DECISION_MANIFEST_PATH",
    "DEFAULT_GRAPH_SCALE_METHOD_DECISION_PACKET_PATH",
    "GRAPH_SCALE_METHOD_DECISION_COLUMNS",
    "GRAPH_SCALE_METHOD_DECISION_SCOPE",
    "build_graph_scale_method_decision_manifest",
    "build_graph_scale_method_decision_markdown",
    "build_graph_scale_method_decision_rows",
    "write_graph_scale_method_decision_packet",
]
