"""Focused validation benchmark strategy decision worksheet.

The benchmark-readiness packet records fallback and OSRM evidence plus the
missing final benchmark strategy decision. This module turns that state into
explicit reviewer options without accepting OSRM, fallback rows, alternative
route engines, or the validation gate.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.validation_acceptance import DEFAULT_VALIDATION_ACCEPTANCE_PATH
from src.realworld.validation_benchmark_readiness_packet import (
    DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH,
)
from src.realworld.validation_strategy_readiness_packet import (
    DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_review_manifest.json"
)
DEFAULT_VALIDATION_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_review_packet.csv"
)
DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "osrm_route_benchmark_manifest.json"
)
DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_benchmark_decision_packet.csv"
)
DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_benchmark_decision_manifest.json"
)
DEFAULT_VALIDATION_BENCHMARK_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "validation_benchmark_decision_packet.md"
)
VALIDATION_BENCHMARK_DECISION_SCOPE = (
    "Validation benchmark decision packet only; not validation acceptance, "
    "not route-engine ground truth, not calibrated traffic validation, and "
    "not operational routing evidence."
)
VALIDATION_BENCHMARK_DECISION_COLUMNS: tuple[str, ...] = (
    "decision_id",
    "decision_topic",
    "candidate_decision",
    "current_evidence",
    "decision_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_validation_gate",
    "claim_boundary",
)


def build_validation_benchmark_decision_rows(
    *,
    validation_review_manifest_path: str | Path = DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH,
    benchmark_readiness_manifest_path: str
    | Path = DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    strategy_readiness_manifest_path: str
    | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    osrm_benchmark_manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    validation_acceptance_path: str | Path = DEFAULT_VALIDATION_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return reviewer rows for benchmark strategy decisions."""

    review_manifest = _read_json_object(validation_review_manifest_path)
    benchmark_manifest = _read_json_object(benchmark_readiness_manifest_path)
    strategy_manifest = _read_json_object(strategy_readiness_manifest_path)
    osrm_manifest = _read_json_object(osrm_benchmark_manifest_path)
    acceptance = Path(validation_acceptance_path)
    evidence_paths = _evidence_paths(
        validation_review_manifest_path=validation_review_manifest_path,
        benchmark_readiness_manifest_path=benchmark_readiness_manifest_path,
        strategy_readiness_manifest_path=strategy_readiness_manifest_path,
        osrm_benchmark_manifest_path=osrm_benchmark_manifest_path,
    )

    fallback_counts = _dict_value(review_manifest, "fallback_benchmark_status_counts")
    osrm_counts = _dict_value(review_manifest, "osrm_benchmark_status_counts")
    summary_flags = _dict_value(review_manifest, "validation_summary_scope_flags")
    route_weak_counts = _dict_value(
        review_manifest,
        "route_road_evidence_exposure_weak_counts",
    )
    fallback_warn_or_fail = _int(fallback_counts.get("warn")) + _int(
        fallback_counts.get("fail")
    )
    osrm_warn_or_fail = _int(osrm_counts.get("warn")) + _int(osrm_counts.get("fail"))
    scaffold_scope = bool(summary_flags.get("scaffold_or_sanity_scope", False))
    weak_exposure = _int(route_weak_counts.get("true")) > 0

    return [
        _row(
            decision_id="fallback_benchmark_scope_option",
            decision_topic="Fallback benchmark scope",
            candidate_decision=(
                "Retain documented fallback detour-speed checks only as "
                "placeholder plausibility evidence"
            ),
            current_evidence=(
                f"fallback_status_counts={_format_counts(fallback_counts)}; "
                f"benchmark_readiness_rows={_int(benchmark_manifest.get('row_count'))}"
            ),
            decision_status=(
                "needs_human_review_fallback_warn_or_fail_policy"
                if fallback_warn_or_fail
                else "needs_human_review_fallback_scope_policy"
            ),
            blocking_reason="",
            required_reviewer_action=(
                "Decide whether fallback warning rows are retained, replaced, "
                "or excluded before validation acceptance."
            ),
            followup_artifacts="data/manifests/validation_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="cached_osrm_snapshot_scope_option",
            decision_topic="Cached OSRM snapshot scope",
            candidate_decision=(
                "Use cached OSRM route rows as optional plausibility evidence "
                "after source, license, and snapshot review"
            ),
            current_evidence=(
                f"osrm_status_counts={_format_counts(osrm_counts)}; "
                f"raw_response_files={_int(osrm_manifest.get('raw_response_file_count'))}; "
                f"unpinned_rows={_int(osrm_manifest.get('unpinned_row_count'))}; "
                f"query_urls={_int(osrm_manifest.get('query_url_count'))}"
            ),
            decision_status=(
                "needs_human_review_osrm_warn_or_fail_policy"
                if osrm_warn_or_fail
                else "needs_human_review_cached_osrm_scope_policy"
            ),
            blocking_reason="",
            required_reviewer_action=(
                "Review cached OSRM rows, retained raw responses, terms, "
                "attribution, and access-date treatment before publication use."
            ),
            followup_artifacts=(
                "data/validation/osrm_route_benchmark_manifest.json; "
                "data/manifests/validation_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="alternative_benchmark_engine_option",
            decision_topic="Alternative benchmark evidence",
            candidate_decision=(
                "Collect or require Valhalla, routingpy, R5/OpenTripPlanner, "
                "UXsim, agency, or literature benchmark evidence"
            ),
            current_evidence=(
                "current benchmark readiness still asks whether OSRM/fallback "
                "checks are sufficient for the target validation scope"
            ),
            decision_status="needs_human_review_alternative_benchmark_scope",
            blocking_reason="",
            required_reviewer_action=(
                "Decide whether alternative route-engine or agency evidence is "
                "needed within the publication schedule."
            ),
            followup_artifacts=(
                "data/validation/validation_benchmark_readiness_packet.csv; "
                "data/manifests/validation_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="validation_summary_scope_boundary",
            decision_topic="Validation claim boundary",
            candidate_decision=(
                "Keep validation summary scoped as scaffold or sanity evidence "
                "until formal acceptance revises the claim boundary"
            ),
            current_evidence=_format_counts(summary_flags),
            decision_status=(
                "blocked_scaffold_validation_scope"
                if scaffold_scope
                else "needs_human_review_validation_scope"
            ),
            blocking_reason=(
                "validation summary still declares scaffold or sanity scope"
                if scaffold_scope
                else ""
            ),
            required_reviewer_action=(
                "Revise or accept validation summary scope only after benchmark "
                "strategy and evidence dependencies are reviewed."
            ),
            followup_artifacts=(
                "data/validation/validation_summary.md; "
                "data/manifests/validation_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="road_evidence_dependency",
            decision_topic="Route road-evidence dependency",
            candidate_decision=(
                "Treat route benchmark interpretation as blocked by weak "
                "route-level road evidence exposure"
            ),
            current_evidence=(
                f"route_road_evidence_exposure_weak_counts={_format_counts(route_weak_counts)}"
            ),
            decision_status=(
                "blocked_weak_route_road_evidence_dependency"
                if weak_exposure
                else "needs_human_review_route_evidence_dependency"
            ),
            blocking_reason=(
                "route-level road evidence exposure remains weak until road evidence gates close"
                if weak_exposure
                else ""
            ),
            required_reviewer_action=(
                "Close road evidence dependencies or keep validation benchmark "
                "claims bounded as plausibility checks."
            ),
            followup_artifacts=(
                "data/validation/canonical_route_road_evidence_exposure.csv; "
                "data/manifests/validation_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="formal_validation_acceptance_boundary",
            decision_topic="Formal validation acceptance",
            candidate_decision=(
                "Record final benchmark strategy only in the formal validation "
                "acceptance artifact"
            ),
            current_evidence=(
                f"acceptance_path={_display_path(acceptance)}; "
                f"acceptance_present={str(acceptance.exists()).lower()}; "
                f"strategy_blocking_requests={_int(strategy_manifest.get('blocking_request_count'))}"
            ),
            decision_status=(
                "needs_human_review_existing_validation_acceptance"
                if acceptance.exists()
                else "blocked_missing_validation_acceptance_record"
            ),
            blocking_reason=(
                "" if acceptance.exists() else "data/manifests/validation_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Create or validate validation_acceptance.json only after "
                "source-backed human review; do not copy this packet into the formal path."
            ),
            followup_artifacts="data/manifests/validation_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_validation_benchmark_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_DECISION_DOC_PATH,
    validation_review_manifest_path: str | Path = DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH,
    benchmark_readiness_manifest_path: str
    | Path = DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    strategy_readiness_manifest_path: str
    | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    osrm_benchmark_manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write benchmark decision CSV, manifest, and Markdown review packet."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=VALIDATION_BENCHMARK_DECISION_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in VALIDATION_BENCHMARK_DECISION_COLUMNS
                }
            )

    summary = build_validation_benchmark_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        validation_review_manifest_path=validation_review_manifest_path,
        benchmark_readiness_manifest_path=benchmark_readiness_manifest_path,
        strategy_readiness_manifest_path=strategy_readiness_manifest_path,
        osrm_benchmark_manifest_path=osrm_benchmark_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_validation_benchmark_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_validation_benchmark_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_DECISION_DOC_PATH,
    validation_review_manifest_path: str | Path = DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH,
    benchmark_readiness_manifest_path: str
    | Path = DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    strategy_readiness_manifest_path: str
    | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    osrm_benchmark_manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for benchmark decision rows."""

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
        "result_scope": VALIDATION_BENCHMARK_DECISION_SCOPE,
        "claim_boundary": (
            VALIDATION_BENCHMARK_DECISION_SCOPE
            + " It cannot create data/manifests/validation_acceptance.json."
        ),
        "row_count": len(rows),
        "decision_ids": [str(row.get("decision_id", "")) for row in rows],
        "decision_status_counts": status_counts,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "alternative_benchmark_decision_recorded": False,
        "validation_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "validation_review_manifest": _display_path(
                Path(validation_review_manifest_path)
            ),
            "validation_benchmark_readiness_manifest": _display_path(
                Path(benchmark_readiness_manifest_path)
            ),
            "validation_strategy_readiness_manifest": _display_path(
                Path(strategy_readiness_manifest_path)
            ),
            "osrm_benchmark_manifest": _display_path(Path(osrm_benchmark_manifest_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "choose whether fallback rows are retained, replaced, or excluded",
            "choose whether cached OSRM is sufficient as a plausibility snapshot",
            "choose whether alternative route-engine or agency evidence is required",
            "resolve route-level road evidence dependency before final validation claims",
            "record final benchmark strategy only in data/manifests/validation_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_validation_benchmark_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown benchmark decision worksheet."""

    lines = [
        "# Validation Benchmark Decision Packet",
        "",
        str(manifest.get("claim_boundary", VALIDATION_BENCHMARK_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Alternative benchmark decision recorded: `{str(manifest.get('alternative_benchmark_decision_recorded', False)).lower()}`",
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
            "- It does not make OSRM, fallback rows, or any alternative benchmark ground truth.",
            "- Keep validation claims blocked until `data/manifests/validation_acceptance.json` is reviewed.",
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
        "can_support_validation_gate": "false",
        "claim_boundary": VALIDATION_BENCHMARK_DECISION_SCOPE,
    }


def _evidence_paths(
    *,
    validation_review_manifest_path: str | Path,
    benchmark_readiness_manifest_path: str | Path,
    strategy_readiness_manifest_path: str | Path,
    osrm_benchmark_manifest_path: str | Path,
) -> str:
    paths = [
        DEFAULT_VALIDATION_REVIEW_PACKET_PATH,
        DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH,
        DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH,
        validation_review_manifest_path,
        benchmark_readiness_manifest_path,
        strategy_readiness_manifest_path,
        osrm_benchmark_manifest_path,
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


def _read_json_object(path: str | Path) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        return {}
    with filepath.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _dict_value(mapping: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key, {})
    return dict(value) if isinstance(value, Mapping) else {}


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
    "DEFAULT_VALIDATION_BENCHMARK_DECISION_DOC_PATH",
    "DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH",
    "DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH",
    "DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH",
    "DEFAULT_VALIDATION_REVIEW_PACKET_PATH",
    "VALIDATION_BENCHMARK_DECISION_COLUMNS",
    "VALIDATION_BENCHMARK_DECISION_SCOPE",
    "build_validation_benchmark_decision_manifest",
    "build_validation_benchmark_decision_markdown",
    "build_validation_benchmark_decision_rows",
    "write_validation_benchmark_decision_packet",
]
