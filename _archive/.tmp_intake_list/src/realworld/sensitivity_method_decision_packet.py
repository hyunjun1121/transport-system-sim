"""Focused Morris-vs-Sobol sensitivity method decision worksheet.

The strategy-readiness packet records that the Morris-vs-Sobol decision is
missing. This module turns that missing decision into explicit reviewer options
without accepting Morris outputs, waiving Sobol analysis, or closing the
sensitivity gate.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.sensitivity import DEFAULT_MORRIS_MANIFEST_PATH
from src.realworld.sensitivity_acceptance import DEFAULT_SENSITIVITY_ACCEPTANCE_PATH
from src.realworld.sensitivity_index_review_packet import (
    DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH,
)
from src.realworld.sensitivity_strategy_readiness_packet import (
    DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "sensitivity_method_decision_packet.csv"
)
DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "sensitivity_method_decision_manifest.json"
)
DEFAULT_SENSITIVITY_METHOD_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "sensitivity_method_decision_packet.md"
)
SENSITIVITY_METHOD_DECISION_SCOPE = (
    "Sensitivity method-decision packet only; not sensitivity acceptance, not "
    "a Sobol waiver, not calibrated real-world sensitivity evidence, and not "
    "operational routing evidence."
)
SENSITIVITY_METHOD_DECISION_COLUMNS: tuple[str, ...] = (
    "decision_id",
    "decision_topic",
    "candidate_decision",
    "current_evidence",
    "decision_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_sensitivity_gate",
    "claim_boundary",
)


def build_sensitivity_method_decision_rows(
    *,
    morris_manifest_path: str | Path = DEFAULT_MORRIS_MANIFEST_PATH,
    index_manifest_path: str | Path = DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    strategy_manifest_path: str
    | Path = DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
    acceptance_path: str | Path = DEFAULT_SENSITIVITY_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return focused reviewer rows for the Morris-vs-Sobol decision."""

    morris_manifest = _read_json_object(morris_manifest_path)
    index_manifest = _read_json_object(index_manifest_path)
    strategy_manifest = _read_json_object(strategy_manifest_path)
    acceptance = Path(acceptance_path)

    evidence_paths = _evidence_paths(
        morris_manifest_path=morris_manifest_path,
        index_manifest_path=index_manifest_path,
        strategy_manifest_path=strategy_manifest_path,
    )
    method = str(morris_manifest.get("method", "salib_morris") or "salib_morris")
    result_scope = str(morris_manifest.get("result_scope", ""))
    summary_rows = _int(morris_manifest.get("summary_row_count"))
    unavailable_rows = _int(index_manifest.get("unavailable_index_row_count"))
    zero_rows = _int(index_manifest.get("zero_mu_star_row_count"))
    all_zero_groups = _int(index_manifest.get("all_zero_group_count"))
    graph_reduced = _analysis_graph_is_reduced(
        morris_manifest=morris_manifest,
        strategy_manifest=strategy_manifest,
    )

    return [
        _row(
            decision_id="retain_morris_screening_option",
            decision_topic="Morris screening scope",
            candidate_decision=(
                "Treat current Morris output as screening evidence inside a "
                "reviewed scaffold or final-study claim boundary"
            ),
            current_evidence=(
                f"method={method}; morris_summary_rows={summary_rows}; "
                f"strategy_blocking_requests={_int(strategy_manifest.get('blocking_request_count'))}; "
                f"strategy_human_review_requests={_int(strategy_manifest.get('human_review_request_count'))}"
            ),
            decision_status="needs_human_review_morris_screening_scope",
            blocking_reason="",
            required_reviewer_action=(
                "Decide whether Morris screening is sufficient for the intended "
                "claim boundary after graph, parameter, and index-handling review."
            ),
            followup_artifacts="data/manifests/sensitivity_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="run_sobol_extension_option",
            decision_topic="Sobol extension scope",
            candidate_decision=(
                "Run Sobol first-order and total-order analysis before final "
                "sensitivity acceptance"
            ),
            current_evidence=(
                "current artifacts are Morris diagnostics only; no committed "
                "Sobol result or Sobol acceptance decision is present"
            ),
            decision_status="blocked_missing_morris_vs_sobol_decision",
            blocking_reason=(
                "Morris-vs-Sobol method decision is not recorded in formal acceptance"
            ),
            required_reviewer_action=(
                "Choose whether Sobol is required, then define compute budget, "
                "sample design, output metrics, and interpretation rules if it is run."
            ),
            followup_artifacts=(
                "results/realworld_pilot/sobol_results.csv; "
                "results/realworld_pilot/sobol_manifest.json; "
                "data/manifests/sensitivity_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="defer_sensitivity_acceptance_option",
            decision_topic="Sensitivity gate deferral",
            candidate_decision=(
                "Keep sensitivity acceptance blocked until upstream evidence and "
                "method scope are reviewed"
            ),
            current_evidence=(
                f"strategy_remaining_blockers={len(_list_value(strategy_manifest, 'remaining_blockers'))}; "
                "formal sensitivity acceptance is separate"
            ),
            decision_status="needs_human_review_defer_or_continue",
            blocking_reason="",
            required_reviewer_action=(
                "Confirm whether to defer final sensitivity claims or collect "
                "additional Morris/Sobol evidence."
            ),
            followup_artifacts="docs/review_packets/sensitivity_analysis.md",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="index_handling_policy",
            decision_topic="Morris index handling",
            candidate_decision=(
                "Document treatment of unavailable indices and zero-effect rows "
                "before ranking parameters"
            ),
            current_evidence=(
                f"unavailable_index_rows={unavailable_rows}; "
                f"zero_mu_star_rows={zero_rows}; all_zero_groups={all_zero_groups}"
            ),
            decision_status="needs_human_review_index_handling_policy",
            blocking_reason="",
            required_reviewer_action=(
                "Decide whether unavailable p80/p95 rows are excluded, retained "
                "as unavailable diagnostics, or regenerated before manuscript use."
            ),
            followup_artifacts=(
                "data/validation/sensitivity_index_review_packet.csv; "
                "data/manifests/sensitivity_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="graph_scope_dependency",
            decision_topic="Graph scope dependency",
            candidate_decision=(
                "Use sensitivity outputs only on the accepted graph-scale method"
            ),
            current_evidence=_graph_scope_evidence(
                morris_manifest=morris_manifest,
                graph_reduced=graph_reduced,
            ),
            decision_status=(
                "blocked_reduced_graph_scope_dependency"
                if graph_reduced
                else "needs_human_review_graph_scope_dependency"
            ),
            blocking_reason=(
                "sensitivity outputs use a reduced analysis graph"
                if graph_reduced
                else ""
            ),
            required_reviewer_action=(
                "Close graph-scale acceptance or regenerate sensitivity outputs "
                "on the accepted graph method before final sensitivity claims."
            ),
            followup_artifacts=(
                "data/manifests/graph_scale_acceptance.json; "
                "data/manifests/sensitivity_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="result_scope_boundary",
            decision_topic="Sensitivity claim boundary",
            candidate_decision=(
                "Keep Morris output scoped as scaffold evidence unless accepted "
                "on final input and graph evidence"
            ),
            current_evidence=result_scope,
            decision_status=(
                "blocked_scaffold_result_scope"
                if _scope_is_scaffold(result_scope)
                else "needs_human_review_result_scope"
            ),
            blocking_reason=(
                "current sensitivity result scope is scaffold or not calibrated"
                if _scope_is_scaffold(result_scope)
                else ""
            ),
            required_reviewer_action=(
                "Keep manuscript/report claims bounded until the formal sensitivity "
                "record accepts scope and interpretation."
            ),
            followup_artifacts="data/manifests/sensitivity_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="formal_sensitivity_acceptance_boundary",
            decision_topic="Formal sensitivity acceptance",
            candidate_decision=(
                "Record the reviewed Morris/Sobol, graph-scope, parameter-range, "
                "and index-handling decision only in the formal acceptance path"
            ),
            current_evidence=(
                f"acceptance_path={_display_path(acceptance)}; "
                f"acceptance_present={str(acceptance.exists()).lower()}"
            ),
            decision_status=(
                "needs_human_review_existing_sensitivity_acceptance"
                if acceptance.exists()
                else "blocked_missing_sensitivity_acceptance_record"
            ),
            blocking_reason=(
                "" if acceptance.exists() else "data/manifests/sensitivity_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Create or validate sensitivity_acceptance.json only after source-backed "
                "human review; do not copy this packet into the formal path."
            ),
            followup_artifacts="data/manifests/sensitivity_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_sensitivity_method_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SENSITIVITY_METHOD_DECISION_DOC_PATH,
    morris_manifest_path: str | Path = DEFAULT_MORRIS_MANIFEST_PATH,
    index_manifest_path: str | Path = DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    strategy_manifest_path: str
    | Path = DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write method-decision CSV, manifest, and Markdown review packet."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=SENSITIVITY_METHOD_DECISION_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in SENSITIVITY_METHOD_DECISION_COLUMNS
                }
            )

    summary = build_sensitivity_method_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        morris_manifest_path=morris_manifest_path,
        index_manifest_path=index_manifest_path,
        strategy_manifest_path=strategy_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_sensitivity_method_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_sensitivity_method_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SENSITIVITY_METHOD_DECISION_DOC_PATH,
    morris_manifest_path: str | Path = DEFAULT_MORRIS_MANIFEST_PATH,
    index_manifest_path: str | Path = DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    strategy_manifest_path: str
    | Path = DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for method-decision rows."""

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
        "result_scope": SENSITIVITY_METHOD_DECISION_SCOPE,
        "claim_boundary": (
            SENSITIVITY_METHOD_DECISION_SCOPE
            + " It cannot create data/manifests/sensitivity_acceptance.json."
        ),
        "row_count": len(rows),
        "decision_ids": [str(row.get("decision_id", "")) for row in rows],
        "decision_status_counts": status_counts,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "sobol_decision_recorded": False,
        "sobol_waiver_created": False,
        "sensitivity_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "morris_manifest": _display_path(Path(morris_manifest_path)),
            "sensitivity_index_review_manifest": _display_path(
                Path(index_manifest_path)
            ),
            "sensitivity_strategy_readiness_manifest": _display_path(
                Path(strategy_manifest_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "choose whether current Morris screening is sufficient for the intended claim boundary",
            "choose whether Sobol analysis must be run before final sensitivity acceptance",
            "document unavailable Morris index and zero mu_star handling before ranking parameters",
            "resolve graph-scale dependency before treating sensitivity outputs as final-study evidence",
            "record any final method decision only in data/manifests/sensitivity_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_sensitivity_method_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a Markdown method-decision worksheet."""

    lines = [
        "# Sensitivity Method Decision Packet",
        "",
        str(manifest.get("claim_boundary", SENSITIVITY_METHOD_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Sobol decision recorded: `{str(manifest.get('sobol_decision_recorded', False)).lower()}`",
        f"- Sobol waiver created: `{str(manifest.get('sobol_waiver_created', False)).lower()}`",
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
            "- It does not run Sobol, waive Sobol, accept Morris, or prove parameter dominance.",
            "- Keep final-study claims blocked until `data/manifests/sensitivity_acceptance.json` is reviewed.",
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
        "can_support_sensitivity_gate": "false",
        "claim_boundary": SENSITIVITY_METHOD_DECISION_SCOPE,
    }


def _analysis_graph_is_reduced(
    *,
    morris_manifest: Mapping[str, Any],
    strategy_manifest: Mapping[str, Any],
) -> bool:
    graph_scale = morris_manifest.get("graph_scale", {})
    if isinstance(graph_scale, Mapping):
        analysis = graph_scale.get("analysis", {})
        if isinstance(analysis, Mapping) and "reduced" in analysis:
            return bool(analysis.get("reduced", False))
    blockers = _list_value(strategy_manifest, "remaining_blockers")
    return any("reduced analysis graph" in item for item in blockers)


def _graph_scope_evidence(
    *,
    morris_manifest: Mapping[str, Any],
    graph_reduced: bool,
) -> str:
    graph_scale = morris_manifest.get("graph_scale", {})
    source: Mapping[str, Any] = {}
    analysis: Mapping[str, Any] = {}
    if isinstance(graph_scale, Mapping):
        maybe_source = graph_scale.get("source", {})
        maybe_analysis = graph_scale.get("analysis", {})
        source = maybe_source if isinstance(maybe_source, Mapping) else {}
        analysis = maybe_analysis if isinstance(maybe_analysis, Mapping) else {}
    return (
        f"source_nodes={source.get('nodes', morris_manifest.get('source_graph_nodes', ''))}; "
        f"source_edges={source.get('edges', morris_manifest.get('source_graph_edges', ''))}; "
        f"analysis_nodes={analysis.get('nodes', morris_manifest.get('graph_nodes', ''))}; "
        f"analysis_edges={analysis.get('edges', morris_manifest.get('graph_edges', ''))}; "
        f"analysis_graph_reduced={str(graph_reduced).lower()}"
    )


def _scope_is_scaffold(scope: str) -> bool:
    lowered = scope.lower()
    return "scaffold" in lowered or "not calibrated" in lowered


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("decision_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(reason)
    return blockers


def _evidence_paths(
    *,
    morris_manifest_path: str | Path,
    index_manifest_path: str | Path,
    strategy_manifest_path: str | Path,
) -> str:
    paths = [
        DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH,
        DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH,
        morris_manifest_path,
        index_manifest_path,
        strategy_manifest_path,
    ]
    return "; ".join(_display_path(Path(path)) for path in paths)


def _read_json_object(path: str | Path) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        return {}
    with filepath.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


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


def _int(value: object) -> int:
    try:
        return int(str(value).strip())
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
    "DEFAULT_SENSITIVITY_METHOD_DECISION_DOC_PATH",
    "DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH",
    "DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH",
    "SENSITIVITY_METHOD_DECISION_COLUMNS",
    "SENSITIVITY_METHOD_DECISION_SCOPE",
    "build_sensitivity_method_decision_manifest",
    "build_sensitivity_method_decision_markdown",
    "build_sensitivity_method_decision_rows",
    "write_sensitivity_method_decision_packet",
]
