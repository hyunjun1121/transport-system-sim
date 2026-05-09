"""Integrated E2/E3/E5 evidence review worksheet.

The immediate execution plan asks for the integrated rail-evidence,
external-benchmark, validation, and pilot-experiment outputs to be reviewed
together. This module consolidates the existing non-approval manifests into a
small reviewer worksheet. It does not fetch new evidence, approve source
material, accept validation benchmarks, accept experiment outputs, or create
formal final-study artifacts.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_source_decision_manifest.json"
)
DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_benchmark_decision_manifest.json"
)
DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_strategy_readiness_manifest.json"
)
DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_design_decision_manifest.json"
)
DEFAULT_INTEGRATED_EVIDENCE_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "integrated_evidence_review_packet.csv"
)
DEFAULT_INTEGRATED_EVIDENCE_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "integrated_evidence_review_manifest.json"
)
DEFAULT_INTEGRATED_EVIDENCE_REVIEW_DOC_PATH = (
    PROJECT_ROOT / "docs" / "integrated_evidence_review_packet.md"
)
INTEGRATED_EVIDENCE_REVIEW_SCOPE = (
    "Integrated evidence review packet only; not rail evidence acceptance, "
    "not validation acceptance, not experiment acceptance, not calibrated "
    "real-world evidence, and not operational routing evidence."
)
INTEGRATED_EVIDENCE_REVIEW_COLUMNS: tuple[str, ...] = (
    "review_id",
    "review_topic",
    "input_area",
    "current_evidence",
    "integration_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_final_claims",
    "claim_boundary",
)


def build_integrated_evidence_review_rows(
    *,
    rail_source_decision_manifest_path: str
    | Path = DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    validation_benchmark_decision_manifest_path: str
    | Path = DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    validation_strategy_readiness_manifest_path: str
    | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    experiment_design_decision_manifest_path: str
    | Path = DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
) -> list[dict[str, str]]:
    """Return conservative integration-review rows for existing packets."""

    rail = _read_json_object(rail_source_decision_manifest_path)
    benchmark = _read_json_object(validation_benchmark_decision_manifest_path)
    validation = _read_json_object(validation_strategy_readiness_manifest_path)
    experiment = _read_json_object(experiment_design_decision_manifest_path)
    evidence_paths = _evidence_paths(
        rail_source_decision_manifest_path=rail_source_decision_manifest_path,
        validation_benchmark_decision_manifest_path=(
            validation_benchmark_decision_manifest_path
        ),
        validation_strategy_readiness_manifest_path=(
            validation_strategy_readiness_manifest_path
        ),
        experiment_design_decision_manifest_path=(
            experiment_design_decision_manifest_path
        ),
    )

    rail_blocking = _int(rail.get("blocking_decision_count"))
    benchmark_blocking = _int(benchmark.get("blocking_decision_count"))
    validation_blocking = _int(validation.get("blocking_request_count"))
    experiment_blocking = _int(experiment.get("blocking_decision_count"))
    total_blocking = (
        rail_blocking
        + benchmark_blocking
        + validation_blocking
        + experiment_blocking
    )
    total_human_review = (
        _int(rail.get("human_review_decision_count"))
        + _int(benchmark.get("human_review_decision_count"))
        + _int(validation.get("human_review_request_count"))
        + _int(experiment.get("human_review_decision_count"))
    )

    return [
        _row(
            review_id="e2_rail_timing_capacity_dependency",
            review_topic="E2 rail timing, capacity, and availability dependency",
            input_area="rail_evidence",
            current_evidence=_current_evidence(
                row_count=rail.get("row_count"),
                blocking=rail_blocking,
                human_review=rail.get("human_review_decision_count"),
                status_counts=rail.get("decision_status_counts"),
                extra={
                    "rail_service_evidence_present": rail.get(
                        "rail_service_evidence_present"
                    ),
                    "source_cache_present_count": rail.get(
                        "source_cache_present_count"
                    ),
                },
            ),
            integration_status=_dependency_status(
                blocking_count=rail_blocking,
                human_review_count=_int(rail.get("human_review_decision_count")),
                blocked_status="blocked_rail_source_decisions_pending",
                review_status="needs_human_review_rail_source_scope",
            ),
            blocking_reason=_first_blocker(rail),
            required_reviewer_action=(
                "Choose reviewed timetable, shortest-path, GTFS, capacity, and "
                "availability treatment before rail-dependent claims are retained."
            ),
            followup_artifacts=(
                "data/parameters/rail_service_evidence.csv; "
                "data/manifests/provenance_acceptance.json; "
                "data/parameters/parameter_acceptance.csv"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="e3_external_benchmark_dependency",
            review_topic="E3 fallback and external-route benchmark dependency",
            input_area="validation_benchmark",
            current_evidence=_current_evidence(
                row_count=benchmark.get("row_count"),
                blocking=benchmark_blocking,
                human_review=benchmark.get("human_review_decision_count"),
                status_counts=benchmark.get("decision_status_counts"),
                extra={
                    "alternative_benchmark_decision_recorded": benchmark.get(
                        "alternative_benchmark_decision_recorded"
                    ),
                    "validation_gate_closure_candidate_count": benchmark.get(
                        "validation_gate_closure_candidate_count"
                    ),
                },
            ),
            integration_status=_dependency_status(
                blocking_count=benchmark_blocking,
                human_review_count=_int(benchmark.get("human_review_decision_count")),
                blocked_status="blocked_validation_benchmark_decisions_pending",
                review_status="needs_human_review_validation_benchmark_scope",
            ),
            blocking_reason=_first_blocker(benchmark),
            required_reviewer_action=(
                "Decide whether fallback rows, cached OSRM, or another route "
                "engine can be used only as plausibility evidence."
            ),
            followup_artifacts="data/manifests/validation_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="validation_strategy_dependency",
            review_topic="Validation strategy and road-evidence dependency",
            input_area="validation_strategy",
            current_evidence=_current_evidence(
                row_count=validation.get("row_count"),
                blocking=validation_blocking,
                human_review=validation.get("human_review_request_count"),
                status_counts=validation.get("readiness_status_counts"),
                extra={
                    "validation_gate_closure_candidate_count": validation.get(
                        "validation_gate_closure_candidate_count"
                    )
                },
            ),
            integration_status=_dependency_status(
                blocking_count=validation_blocking,
                human_review_count=_int(validation.get("human_review_request_count")),
                blocked_status="blocked_validation_strategy_dependencies",
                review_status="needs_human_review_validation_strategy_scope",
            ),
            blocking_reason=_first_blocker(validation),
            required_reviewer_action=(
                "Resolve weak route-road evidence exposure and validation-scope "
                "limitations before final validation claims."
            ),
            followup_artifacts=(
                "data/validation/validation_strategy_readiness_packet.csv; "
                "data/manifests/validation_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="e5_experiment_profile_dependency",
            review_topic="E5 pilot scenario-policy-seed and graph-scope dependency",
            input_area="pilot_experiments",
            current_evidence=_current_evidence(
                row_count=experiment.get("row_count"),
                blocking=experiment_blocking,
                human_review=experiment.get("human_review_decision_count"),
                status_counts=experiment.get("decision_status_counts"),
                extra={
                    "selected_run_profile_recorded": experiment.get(
                        "selected_run_profile_recorded"
                    ),
                    "scenario_policy_seed_decision_recorded": experiment.get(
                        "scenario_policy_seed_decision_recorded"
                    ),
                },
            ),
            integration_status=_dependency_status(
                blocking_count=experiment_blocking,
                human_review_count=_int(experiment.get("human_review_decision_count")),
                blocked_status="blocked_experiment_design_dependencies",
                review_status="needs_human_review_experiment_profile_scope",
            ),
            blocking_reason=_first_blocker(experiment),
            required_reviewer_action=(
                "Choose retained or regenerated experiment outputs only after "
                "graph-scale and upstream input dependencies are resolved."
            ),
            followup_artifacts=(
                "data/manifests/experiment_acceptance.json; "
                "data/manifests/graph_scale_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="integrated_claim_boundary",
            review_topic="Integrated E2/E3/validation/E5 claim boundary",
            input_area="cross_gate_boundary",
            current_evidence=_current_evidence(
                row_count=4,
                blocking=total_blocking,
                human_review=total_human_review,
                status_counts={
                    "rail_blocking": rail_blocking,
                    "benchmark_blocking": benchmark_blocking,
                    "validation_blocking": validation_blocking,
                    "experiment_blocking": experiment_blocking,
                },
                extra={
                    "formal_gate_closure_candidate_count": 0,
                    "publication_ready": False,
                },
            ),
            integration_status=(
                "blocked_integrated_claim_boundary"
                if total_blocking
                else (
                    "needs_human_review_integrated_claim_boundary"
                    if total_human_review
                    else "ready_for_review_integrated_claim_boundary"
                )
            ),
            blocking_reason=(
                "one or more integrated evidence dependencies remain blocked"
                if total_blocking
                else ""
            ),
            required_reviewer_action=(
                "Keep fallback and OSRM rows labeled as plausibility checks and "
                "keep pilot outputs scaffold-scoped until the formal evidence "
                "and acceptance records are reviewed."
            ),
            followup_artifacts=(
                "data/manifests/validation_acceptance.json; "
                "data/manifests/experiment_acceptance.json; "
                "data/manifests/provenance_acceptance.json; "
                "data/manifests/graph_scale_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_integrated_evidence_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_INTEGRATED_EVIDENCE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_INTEGRATED_EVIDENCE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_INTEGRATED_EVIDENCE_REVIEW_DOC_PATH,
    rail_source_decision_manifest_path: str
    | Path = DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    validation_benchmark_decision_manifest_path: str
    | Path = DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    validation_strategy_readiness_manifest_path: str
    | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    experiment_design_decision_manifest_path: str
    | Path = DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write integrated review CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=INTEGRATED_EVIDENCE_REVIEW_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in INTEGRATED_EVIDENCE_REVIEW_COLUMNS
                }
            )

    summary = build_integrated_evidence_review_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        rail_source_decision_manifest_path=rail_source_decision_manifest_path,
        validation_benchmark_decision_manifest_path=(
            validation_benchmark_decision_manifest_path
        ),
        validation_strategy_readiness_manifest_path=(
            validation_strategy_readiness_manifest_path
        ),
        experiment_design_decision_manifest_path=(
            experiment_design_decision_manifest_path
        ),
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_integrated_evidence_review_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_integrated_evidence_review_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_INTEGRATED_EVIDENCE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_INTEGRATED_EVIDENCE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_INTEGRATED_EVIDENCE_REVIEW_DOC_PATH,
    rail_source_decision_manifest_path: str
    | Path = DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    validation_benchmark_decision_manifest_path: str
    | Path = DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    validation_strategy_readiness_manifest_path: str
    | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    experiment_design_decision_manifest_path: str
    | Path = DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for integrated evidence review."""

    status_counts = _counts(row.get("integration_status", "") for row in rows)
    blocking_count = sum(
        1
        for row in rows
        if str(row.get("integration_status", "")).startswith("blocked_")
    )
    human_review_row_count = sum(
        1
        for row in rows
        if str(row.get("integration_status", "")).startswith("needs_human_review_")
    )
    underlying_human_review_count = sum(
        _current_evidence_int(row.get("current_evidence", ""), "human_review_count")
        for row in rows
        if row.get("review_id") != "integrated_claim_boundary"
    )
    return {
        "schema_version": 1,
        "result_scope": INTEGRATED_EVIDENCE_REVIEW_SCOPE,
        "claim_boundary": (
            INTEGRATED_EVIDENCE_REVIEW_SCOPE
            + " It cannot create formal acceptance artifacts."
        ),
        "row_count": len(rows),
        "review_ids": [str(row.get("review_id", "")) for row in rows],
        "worker_ids": ["E2", "E3", "E5"],
        "review_status_counts": status_counts,
        "blocking_review_count": blocking_count,
        "human_review_row_count": human_review_row_count,
        "underlying_human_review_count": underlying_human_review_count,
        "human_review_count": underlying_human_review_count,
        "integrated_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "rail_source_decision_manifest": _display_path(
                Path(rail_source_decision_manifest_path)
            ),
            "validation_benchmark_decision_manifest": _display_path(
                Path(validation_benchmark_decision_manifest_path)
            ),
            "validation_strategy_readiness_manifest": _display_path(
                Path(validation_strategy_readiness_manifest_path)
            ),
            "experiment_design_decision_manifest": _display_path(
                Path(experiment_design_decision_manifest_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "review rail timing, capacity, and availability decisions before retaining rail-dependent claims",
            "keep fallback and OSRM benchmarks labeled as plausibility checks unless validation acceptance changes that boundary",
            "review validation road-evidence dependencies before final validation claims",
            "review scenario-policy-seed, graph-scope, and regeneration decisions before experiment acceptance",
            "record final decisions only in the relevant formal acceptance artifacts",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_integrated_evidence_review_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown integrated review worksheet."""

    lines = [
        "# Integrated Evidence Review Packet",
        "",
        str(manifest.get("claim_boundary", INTEGRATED_EVIDENCE_REVIEW_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Review rows: {manifest.get('row_count', 0)}",
        f"- Blocking rows: {manifest.get('blocking_review_count', 0)}",
        f"- Human-review rows: {manifest.get('human_review_row_count', 0)}",
        f"- Underlying human-review decisions: {manifest.get('underlying_human_review_count', 0)}",
        f"- Status counts: `{manifest.get('review_status_counts', {})}`",
        "",
        "## Review Rows",
        "",
        "| Review | Status | Evidence | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {review} | {status} | {evidence} | {action} |".format(
                review=_cell(row.get("review_id", "")),
                status=_cell(row.get("integration_status", "")),
                evidence=_cell(row.get("current_evidence", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is a reviewer worksheet, not an acceptance record.",
            "- It does not make fallback or OSRM benchmarks ground truth.",
            "- It does not certify rail timing, rail capacity, or pilot experiment outputs.",
            "- Keep final-study claims blocked until the relevant formal acceptance artifacts are reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(
    *,
    review_id: str,
    review_topic: str,
    input_area: str,
    current_evidence: str,
    integration_status: str,
    blocking_reason: str,
    required_reviewer_action: str,
    followup_artifacts: str,
    evidence_input_paths: str,
) -> dict[str, str]:
    return {
        "review_id": review_id,
        "review_topic": review_topic,
        "input_area": input_area,
        "current_evidence": current_evidence,
        "integration_status": integration_status,
        "blocking_reason": blocking_reason,
        "required_reviewer_action": required_reviewer_action,
        "followup_artifacts": followup_artifacts,
        "evidence_input_paths": evidence_input_paths,
        "can_support_final_claims": "false",
        "claim_boundary": INTEGRATED_EVIDENCE_REVIEW_SCOPE,
    }


def _dependency_status(
    *,
    blocking_count: int,
    human_review_count: int,
    blocked_status: str,
    review_status: str,
) -> str:
    if blocking_count:
        return blocked_status
    if human_review_count:
        return review_status
    return "ready_for_review_no_blocking_rows"


def _evidence_paths(
    *,
    rail_source_decision_manifest_path: str | Path,
    validation_benchmark_decision_manifest_path: str | Path,
    validation_strategy_readiness_manifest_path: str | Path,
    experiment_design_decision_manifest_path: str | Path,
) -> str:
    paths = [
        PROJECT_ROOT / "data" / "rail" / "rail_source_decision_packet.csv",
        rail_source_decision_manifest_path,
        PROJECT_ROOT / "data" / "validation" / "validation_benchmark_decision_packet.csv",
        validation_benchmark_decision_manifest_path,
        PROJECT_ROOT / "data" / "validation" / "validation_review_packet.csv",
        validation_strategy_readiness_manifest_path,
        PROJECT_ROOT / "data" / "manifests" / "experiment_design_decision_packet.csv",
        experiment_design_decision_manifest_path,
    ]
    return "; ".join(_display_path(Path(path)) for path in paths)


def _current_evidence(
    *,
    row_count: object,
    blocking: object,
    human_review: object,
    status_counts: object,
    extra: Mapping[str, object] | None = None,
) -> str:
    fields: dict[str, object] = {
        "row_count": row_count,
        "blocking_count": blocking,
        "human_review_count": human_review,
        "status_counts": status_counts,
    }
    if extra:
        fields.update(extra)
    return "; ".join(
        f"{key}={_format_value(value)}" for key, value in fields.items()
    )


def _format_value(value: object) -> str:
    if isinstance(value, Mapping):
        return json.dumps(value, sort_keys=True)
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _first_blocker(manifest: Mapping[str, Any]) -> str:
    blockers = manifest.get("remaining_blockers")
    if isinstance(blockers, list) and blockers:
        return str(blockers[0])
    return ""


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("integration_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(reason)
    return blockers


def _current_evidence_int(value: object, field_name: str) -> int:
    prefix = f"{field_name}="
    for part in str(value).split("; "):
        if not part.startswith(prefix):
            continue
        return _int(part.removeprefix(prefix))
    return 0


def _read_json_object(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.exists():
        return {}
    try:
        value = json.loads(candidate.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()
