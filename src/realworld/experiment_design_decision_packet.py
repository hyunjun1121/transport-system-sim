"""Focused experiment run-profile and design decision worksheet.

The experiment package and strategy-readiness packets record that full pilot
outputs exist but remain scaffold evidence. This module turns the remaining
run-profile, scenario-policy-seed, graph-scope, input-dependency, and formal
acceptance choices into explicit reviewer rows without accepting experiment
outputs or creating ``data/manifests/experiment_acceptance.json``.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.experiment_acceptance import DEFAULT_EXPERIMENT_ACCEPTANCE_PATH
from src.realworld.experiment_package_review_packet import (
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
    DEFAULT_PILOT_FULL_MANIFEST_PATH,
)
from src.realworld.experiment_strategy_readiness_packet import (
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PILOT_SAMPLE_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_sample_manifest.json"
)
DEFAULT_PILOT_STAGED_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_staged_manifest.json"
)
DEFAULT_PILOT_MULTI_CORRIDOR_MANIFEST_PATH = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "pilot_multi_corridor_manifest.json"
)
DEFAULT_PILOT_MULTI_CORRIDOR_FULL_MANIFEST_PATH = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "pilot_multi_corridor_full_manifest.json"
)
DEFAULT_PILOT_EXPERIMENT_DESIGN_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "pilot_experiment_design.json"
)
DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "graph_scale_acceptance.json"
)
DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_design_decision_packet.csv"
)
DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_design_decision_manifest.json"
)
DEFAULT_EXPERIMENT_DESIGN_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "experiment_design_decision_packet.md"
)
EXPERIMENT_DESIGN_DECISION_SCOPE = (
    "Experiment design-decision packet only; not experiment acceptance, not "
    "calibrated real-world results, not graph-scale acceptance, and not "
    "operational routing evidence."
)
EXPERIMENT_DESIGN_DECISION_COLUMNS: tuple[str, ...] = (
    "decision_id",
    "decision_topic",
    "candidate_decision",
    "current_evidence",
    "decision_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_experiment_gate",
    "claim_boundary",
)


def build_experiment_design_decision_rows(
    *,
    sample_manifest_path: str | Path = DEFAULT_PILOT_SAMPLE_MANIFEST_PATH,
    staged_manifest_path: str | Path = DEFAULT_PILOT_STAGED_MANIFEST_PATH,
    full_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    multi_corridor_manifest_path: str
    | Path = DEFAULT_PILOT_MULTI_CORRIDOR_MANIFEST_PATH,
    multi_corridor_full_manifest_path: str
    | Path = DEFAULT_PILOT_MULTI_CORRIDOR_FULL_MANIFEST_PATH,
    design_path: str | Path = DEFAULT_PILOT_EXPERIMENT_DESIGN_PATH,
    package_manifest_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    strategy_manifest_path: str
    | Path = DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
    graph_scale_acceptance_path: str | Path = DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
    experiment_acceptance_path: str | Path = DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return reviewer rows for experiment run-profile and design decisions."""

    sample_manifest = _read_json_object(sample_manifest_path)
    staged_manifest = _read_json_object(staged_manifest_path)
    full_manifest = _read_json_object(full_manifest_path)
    multi_manifest = _read_json_object(multi_corridor_manifest_path)
    multi_full_manifest = _read_json_object(multi_corridor_full_manifest_path)
    design = _read_json_object(design_path)
    package_manifest = _read_json_object(package_manifest_path)
    strategy_manifest = _read_json_object(strategy_manifest_path)
    graph_acceptance = Path(graph_scale_acceptance_path)
    experiment_acceptance = Path(experiment_acceptance_path)
    evidence_paths = _evidence_paths(
        sample_manifest_path=sample_manifest_path,
        staged_manifest_path=staged_manifest_path,
        full_manifest_path=full_manifest_path,
        multi_corridor_manifest_path=multi_corridor_manifest_path,
        multi_corridor_full_manifest_path=multi_corridor_full_manifest_path,
        design_path=design_path,
        package_manifest_path=package_manifest_path,
        strategy_manifest_path=strategy_manifest_path,
    )
    graph_reduced = any(
        _analysis_graph_is_reduced(manifest)
        for manifest in (full_manifest, multi_full_manifest)
    )
    result_scope = str(full_manifest.get("result_scope", ""))
    road_overrides_applied = bool(full_manifest.get("road_class_overrides_applied"))
    strategy_remaining_blockers = _list_value(strategy_manifest, "remaining_blockers")
    upstream_blocked = (not road_overrides_applied) or any(
        "upstream input" in item or "road override" in item
        for item in strategy_remaining_blockers
    )

    return [
        _row(
            decision_id="sample_staged_full_profile_context",
            decision_topic="Sample, staged, and full run-profile scope",
            candidate_decision=(
                "Use sample and staged outputs as implementation checks, and "
                "treat the current full_pilot profile as the candidate full "
                "scenario-policy-seed run only after review"
            ),
            current_evidence=_profile_evidence(
                sample=sample_manifest,
                staged=staged_manifest,
                full=full_manifest,
            ),
            decision_status="needs_human_review_current_full_profile_scope",
            blocking_reason="",
            required_reviewer_action=(
                "Decide whether the current full_pilot run profile is retained, "
                "regenerated, or kept as scaffold-only evidence."
            ),
            followup_artifacts=(
                "results/realworld_pilot/pilot_full_manifest.json; "
                "data/manifests/experiment_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="multi_corridor_profile_option",
            decision_topic="Multi-corridor candidate profile",
            candidate_decision=(
                "Use the multi-corridor full-profile candidate only if graph-scale "
                "review selects that method"
            ),
            current_evidence=_multi_corridor_evidence(
                multi=multi_manifest,
                multi_full=multi_full_manifest,
                graph_acceptance=graph_acceptance,
            ),
            decision_status="needs_human_review_multi_corridor_profile_scope",
            blocking_reason="",
            required_reviewer_action=(
                "Choose whether the single-corridor full output, multi-corridor "
                "full candidate, or a regenerated output should support the "
                "experiment package."
            ),
            followup_artifacts=(
                "data/manifests/graph_scale_acceptance.json; "
                "data/manifests/experiment_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="scenario_policy_seed_design",
            decision_topic="Scenario-policy-seed design",
            candidate_decision=(
                "Use the current 7-policy, 9-scenario, 30-seed common-random-number "
                "full design as the candidate reviewed design"
            ),
            current_evidence=_design_evidence(
                full_manifest=full_manifest,
                design_manifest=design,
            ),
            decision_status="needs_human_review_scenario_policy_seed_design",
            blocking_reason="",
            required_reviewer_action=(
                "Review policy exclusions, scenario scope, seed count, CRN pairing, "
                "and row-count multiplication before experiment-gate review."
            ),
            followup_artifacts=(
                "data/manifests/pilot_experiment_design.json; "
                "data/manifests/experiment_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="graph_scope_dependency",
            decision_topic="Graph-scope dependency",
            candidate_decision=(
                "Use experiment outputs only on the graph-scale method chosen "
                "by formal graph-scale review"
            ),
            current_evidence=_graph_evidence(
                full_manifest=full_manifest,
                multi_full_manifest=multi_full_manifest,
                graph_acceptance=graph_acceptance,
            ),
            decision_status=(
                "blocked_graph_scale_dependency"
                if graph_reduced or not graph_acceptance.exists()
                else "needs_human_review_graph_scope_dependency"
            ),
            blocking_reason=(
                "experiment outputs depend on a graph method that is not selected by review"
                if graph_reduced or not graph_acceptance.exists()
                else ""
            ),
            required_reviewer_action=(
                "Provide graph-scale review record or regenerate outputs on the "
                "selected graph method before experiment-output review."
            ),
            followup_artifacts=(
                "data/manifests/graph_scale_acceptance.json; "
                "data/manifests/experiment_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="input_evidence_dependency",
            decision_topic="Input-evidence dependency",
            candidate_decision=(
                "Use current experiment outputs only after upstream input, "
                "road override, parameter, validation, and provenance gates close"
            ),
            current_evidence=(
                f"road_class_overrides_applied={str(road_overrides_applied).lower()}; "
                f"strategy_blocking_requests={_int(strategy_manifest.get('blocking_request_count'))}; "
                f"package_row_count_mismatches={_int(package_manifest.get('row_count_mismatch_count'))}"
            ),
            decision_status=(
                "blocked_input_evidence_dependency"
                if upstream_blocked
                else "needs_human_review_input_evidence_dependency"
            ),
            blocking_reason=(
                "upstream input, road override, parameter, validation, or provenance gates are not closed"
                if upstream_blocked
                else ""
            ),
            required_reviewer_action=(
                "Close upstream evidence gates or document why current outputs "
                "remain scaffold-only."
            ),
            followup_artifacts=(
                "data/parameters/road_class_overrides.csv; "
                "data/manifests/experiment_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="result_scope_boundary",
            decision_topic="Experiment result claim boundary",
            candidate_decision=(
                "Keep current full-pilot outputs scoped as scaffold or decision-support "
                "evidence until formal acceptance revises the claim boundary"
            ),
            current_evidence=result_scope,
            decision_status=(
                "blocked_scaffold_or_not_calibrated_experiment_scope"
                if _scope_is_scaffold_or_uncalibrated(result_scope)
                else "needs_human_review_result_scope"
            ),
            blocking_reason=(
                "current full-pilot result scope is scaffold or not calibrated"
                if _scope_is_scaffold_or_uncalibrated(result_scope)
                else ""
            ),
            required_reviewer_action=(
                "Keep manuscript/report claims bounded until experiment acceptance "
                "records the reviewed result scope."
            ),
            followup_artifacts=(
                "paper/paper_draft.md; report_draft.md; "
                "data/manifests/experiment_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="regenerate_or_retain_outputs",
            decision_topic="Regenerate-or-retain decision",
            candidate_decision=(
                "Decide whether to retain current outputs, regenerate after graph/input "
                "review, or keep them only as review evidence"
            ),
            current_evidence=(
                f"package_review_rows={_int(package_manifest.get('row_count'))}; "
                f"package_publication_ready={str(package_manifest.get('publication_ready', False)).lower()}; "
                f"strategy_human_review_requests={_int(strategy_manifest.get('human_review_request_count'))}; "
                f"strategy_blocking_requests={_int(strategy_manifest.get('blocking_request_count'))}"
            ),
            decision_status="needs_human_review_regenerate_or_retain_outputs",
            blocking_reason="",
            required_reviewer_action=(
                "Record whether reviewed outputs should use the current full_pilot run, "
                "a multi-corridor/full-graph rerun, or a later regenerated package."
            ),
            followup_artifacts=(
                "results/realworld_pilot/pilot_full_manifest.json; "
                "data/manifests/experiment_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="formal_experiment_acceptance_boundary",
            decision_topic="Formal experiment acceptance",
            candidate_decision=(
                "Record the selected run profile, graph scope, design, CRN, counts, "
                "checksums, and claim boundary only in the formal experiment acceptance path"
            ),
            current_evidence=(
                f"acceptance_path={_display_path(experiment_acceptance)}; "
                f"acceptance_present={str(experiment_acceptance.exists()).lower()}"
            ),
            decision_status=(
                "needs_human_review_existing_experiment_acceptance"
                if experiment_acceptance.exists()
                else "blocked_missing_experiment_acceptance_record"
            ),
            blocking_reason=(
                ""
                if experiment_acceptance.exists()
                else "data/manifests/experiment_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Create or validate experiment_acceptance.json only after "
                "source-backed human review; do not copy this packet into the formal path."
            ),
            followup_artifacts="data/manifests/experiment_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_experiment_design_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_EXPERIMENT_DESIGN_DECISION_DOC_PATH,
    sample_manifest_path: str | Path = DEFAULT_PILOT_SAMPLE_MANIFEST_PATH,
    staged_manifest_path: str | Path = DEFAULT_PILOT_STAGED_MANIFEST_PATH,
    full_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    multi_corridor_manifest_path: str
    | Path = DEFAULT_PILOT_MULTI_CORRIDOR_MANIFEST_PATH,
    multi_corridor_full_manifest_path: str
    | Path = DEFAULT_PILOT_MULTI_CORRIDOR_FULL_MANIFEST_PATH,
    design_path: str | Path = DEFAULT_PILOT_EXPERIMENT_DESIGN_PATH,
    package_manifest_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    strategy_manifest_path: str
    | Path = DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write experiment design-decision CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=EXPERIMENT_DESIGN_DECISION_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in EXPERIMENT_DESIGN_DECISION_COLUMNS
                }
            )

    summary = build_experiment_design_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        sample_manifest_path=sample_manifest_path,
        staged_manifest_path=staged_manifest_path,
        full_manifest_path=full_manifest_path,
        multi_corridor_manifest_path=multi_corridor_manifest_path,
        multi_corridor_full_manifest_path=multi_corridor_full_manifest_path,
        design_path=design_path,
        package_manifest_path=package_manifest_path,
        strategy_manifest_path=strategy_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_experiment_design_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_experiment_design_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_EXPERIMENT_DESIGN_DECISION_DOC_PATH,
    sample_manifest_path: str | Path = DEFAULT_PILOT_SAMPLE_MANIFEST_PATH,
    staged_manifest_path: str | Path = DEFAULT_PILOT_STAGED_MANIFEST_PATH,
    full_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    multi_corridor_manifest_path: str
    | Path = DEFAULT_PILOT_MULTI_CORRIDOR_MANIFEST_PATH,
    multi_corridor_full_manifest_path: str
    | Path = DEFAULT_PILOT_MULTI_CORRIDOR_FULL_MANIFEST_PATH,
    design_path: str | Path = DEFAULT_PILOT_EXPERIMENT_DESIGN_PATH,
    package_manifest_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    strategy_manifest_path: str
    | Path = DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for experiment design-decision rows."""

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
        "result_scope": EXPERIMENT_DESIGN_DECISION_SCOPE,
        "claim_boundary": (
            EXPERIMENT_DESIGN_DECISION_SCOPE
            + " It cannot create data/manifests/experiment_acceptance.json."
        ),
        "row_count": len(rows),
        "decision_ids": [str(row.get("decision_id", "")) for row in rows],
        "decision_status_counts": status_counts,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "selected_run_profile_recorded": False,
        "scenario_policy_seed_decision_recorded": False,
        "experiment_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "pilot_sample_manifest": _display_path(Path(sample_manifest_path)),
            "pilot_staged_manifest": _display_path(Path(staged_manifest_path)),
            "pilot_full_manifest": _display_path(Path(full_manifest_path)),
            "pilot_multi_corridor_manifest": _display_path(
                Path(multi_corridor_manifest_path)
            ),
            "pilot_multi_corridor_full_manifest": _display_path(
                Path(multi_corridor_full_manifest_path)
            ),
            "pilot_experiment_design": _display_path(Path(design_path)),
            "experiment_package_review_manifest": _display_path(
                Path(package_manifest_path)
            ),
            "experiment_strategy_readiness_manifest": _display_path(
                Path(strategy_manifest_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "choose whether the current full_pilot or multi-corridor full candidate is the run profile to review",
            "review the 7-policy, 9-scenario, 30-seed design and excluded policy treatment",
            "resolve graph-scale and upstream input-evidence dependencies before output review",
            "decide whether outputs must be regenerated after graph/input review",
            "record experiment gate decisions only in data/manifests/experiment_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_experiment_design_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown experiment design-decision worksheet."""

    lines = [
        "# Experiment Design Decision Packet",
        "",
        str(manifest.get("claim_boundary", EXPERIMENT_DESIGN_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Selected run profile recorded: `{str(manifest.get('selected_run_profile_recorded', False)).lower()}`",
        f"- Scenario-policy-seed decision recorded: `{str(manifest.get('scenario_policy_seed_decision_recorded', False)).lower()}`",
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
            "- It does not select a final run profile, accept graph scope, or approve scenario-policy-seed design.",
            "- Keep full-experiment claims blocked until `data/manifests/experiment_acceptance.json` is reviewed.",
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
        "can_support_experiment_gate": "false",
        "claim_boundary": EXPERIMENT_DESIGN_DECISION_SCOPE,
    }


def _profile_evidence(
    *,
    sample: Mapping[str, Any],
    staged: Mapping[str, Any],
    full: Mapping[str, Any],
) -> str:
    return "; ".join(
        (
            "sample=" + _manifest_summary(sample),
            "staged=" + _manifest_summary(staged),
            "full=" + _manifest_summary(full),
        )
    )


def _multi_corridor_evidence(
    *,
    multi: Mapping[str, Any],
    multi_full: Mapping[str, Any],
    graph_acceptance: Path,
) -> str:
    return "; ".join(
        (
            "multi_corridor=" + _manifest_summary(multi),
            "multi_corridor_full=" + _manifest_summary(multi_full),
            f"graph_acceptance_present={str(graph_acceptance.exists()).lower()}",
        )
    )


def _manifest_summary(manifest: Mapping[str, Any]) -> str:
    design = _mapping_value(manifest, "scenario_policy_seed_design")
    return (
        f"{manifest.get('run_profile', 'missing')} rows={_int(manifest.get('row_count'))} "
        f"policies={_int(design.get('policy_count', len(_sequence(manifest.get('policy_ids')))))} "
        f"scenarios={_int(design.get('scenario_count', len(_sequence(manifest.get('scenario_ids')))))} "
        f"seeds={_int(design.get('seed_count', len(_sequence(manifest.get('seeds')))))} "
        f"graph={_int(manifest.get('graph_nodes'))}/{_int(manifest.get('graph_edges'))}"
    )


def _design_evidence(
    *,
    full_manifest: Mapping[str, Any],
    design_manifest: Mapping[str, Any],
) -> str:
    design = _mapping_value(full_manifest, "scenario_policy_seed_design")
    excluded = _mapping_value(design_manifest, "excluded_policy_ids")
    return (
        f"run_profile={full_manifest.get('run_profile', '')}; "
        f"policy_count={_int(design.get('policy_count'))}; "
        f"scenario_count={_int(design.get('scenario_count'))}; "
        f"seed_count={_int(design.get('seed_count'))}; "
        f"expected_row_count={_int(design.get('expected_row_count'))}; "
        f"observed_row_count={_int(full_manifest.get('row_count'))}; "
        f"common_random_numbers={str(design.get('common_random_numbers', False)).lower()}; "
        f"excluded_policy_ids={';'.join(sorted(excluded)) or 'none'}"
    )


def _graph_evidence(
    *,
    full_manifest: Mapping[str, Any],
    multi_full_manifest: Mapping[str, Any],
    graph_acceptance: Path,
) -> str:
    return (
        f"full={_graph_summary(full_manifest)}; "
        f"multi_corridor_full={_graph_summary(multi_full_manifest)}; "
        f"graph_scale_acceptance_present={str(graph_acceptance.exists()).lower()}"
    )


def _graph_summary(manifest: Mapping[str, Any]) -> str:
    graph_scale = _mapping_value(manifest, "graph_scale")
    analysis = _mapping_value(graph_scale, "analysis")
    source = _mapping_value(graph_scale, "source")
    return (
        f"reduced={str(_analysis_graph_is_reduced(manifest)).lower()} "
        f"analysis_nodes={analysis.get('nodes', manifest.get('graph_nodes', ''))} "
        f"analysis_edges={analysis.get('edges', manifest.get('graph_edges', ''))} "
        f"source_nodes={source.get('nodes', manifest.get('source_graph_nodes', ''))} "
        f"source_edges={source.get('edges', manifest.get('source_graph_edges', ''))}"
    )


def _analysis_graph_is_reduced(manifest: Mapping[str, Any]) -> bool:
    graph_scale = _mapping_value(manifest, "graph_scale")
    analysis = _mapping_value(graph_scale, "analysis")
    if "reduced" in analysis:
        return bool(analysis.get("reduced"))
    return bool(manifest.get("analysis_graph_reduced", False))


def _scope_is_scaffold_or_uncalibrated(scope: str) -> bool:
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
    sample_manifest_path: str | Path,
    staged_manifest_path: str | Path,
    full_manifest_path: str | Path,
    multi_corridor_manifest_path: str | Path,
    multi_corridor_full_manifest_path: str | Path,
    design_path: str | Path,
    package_manifest_path: str | Path,
    strategy_manifest_path: str | Path,
) -> str:
    paths = [
        sample_manifest_path,
        staged_manifest_path,
        full_manifest_path,
        multi_corridor_manifest_path,
        multi_corridor_full_manifest_path,
        design_path,
        DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
        DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH,
        package_manifest_path,
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


def _mapping_value(mapping: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key, {})
    return dict(value) if isinstance(value, Mapping) else {}


def _list_value(mapping: Mapping[str, Any], key: str) -> list[str]:
    value = mapping.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _sequence(value: object) -> tuple[object, ...]:
    if isinstance(value, Sequence) and not isinstance(value, str):
        return tuple(value)
    return ()


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
    "DEFAULT_EXPERIMENT_DESIGN_DECISION_DOC_PATH",
    "DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH",
    "DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH",
    "DEFAULT_PILOT_EXPERIMENT_DESIGN_PATH",
    "DEFAULT_PILOT_MULTI_CORRIDOR_FULL_MANIFEST_PATH",
    "DEFAULT_PILOT_MULTI_CORRIDOR_MANIFEST_PATH",
    "DEFAULT_PILOT_SAMPLE_MANIFEST_PATH",
    "DEFAULT_PILOT_STAGED_MANIFEST_PATH",
    "EXPERIMENT_DESIGN_DECISION_COLUMNS",
    "EXPERIMENT_DESIGN_DECISION_SCOPE",
    "build_experiment_design_decision_manifest",
    "build_experiment_design_decision_markdown",
    "build_experiment_design_decision_rows",
    "write_experiment_design_decision_packet",
]
