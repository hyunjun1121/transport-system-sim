"""Morris index handling review packet.

The broad sensitivity review packet reports aggregate unavailable-index and
zero-effect counts. This module makes those counts metric-specific so reviewers
can decide how to handle blank/non-finite Morris indices, zero ``mu_star``
rows, and parameter-ranking claims before any sensitivity acceptance record is
created.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.sensitivity import (
    DEFAULT_MORRIS_MANIFEST_PATH,
    DEFAULT_MORRIS_SUMMARY_PATH,
)
from src.realworld.sensitivity_diagnostics import UNAVAILABLE_INDEX_STATUSES


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "sensitivity_index_review_packet.csv"
)
DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "sensitivity_index_review_manifest.json"
)
DEFAULT_SENSITIVITY_INDEX_REVIEW_DOC_PATH = (
    PROJECT_ROOT / "docs" / "sensitivity_index_review_packet.md"
)
SENSITIVITY_INDEX_REVIEW_SCOPE = (
    "Sensitivity index review packet only; not sensitivity acceptance, not a "
    "Sobol waiver, not calibrated real-world sensitivity evidence, and not "
    "operational routing evidence."
)
SENSITIVITY_INDEX_REVIEW_COLUMNS: tuple[str, ...] = (
    "metric",
    "total_rows",
    "available_rows",
    "unavailable_index_rows",
    "zero_mu_star_rows",
    "positive_mu_star_rows",
    "metric_policy_scenario_groups",
    "all_zero_groups",
    "unavailable_groups",
    "affected_unavailable_policies",
    "affected_unavailable_scenarios",
    "index_review_status",
    "required_reviewer_action",
    "publication_use_status",
    "can_support_sensitivity_gate",
    "claim_boundary",
)


def build_sensitivity_index_review_rows(
    *,
    summary_path: str | Path = DEFAULT_MORRIS_SUMMARY_PATH,
    manifest_path: str | Path = DEFAULT_MORRIS_MANIFEST_PATH,
) -> list[dict[str, str]]:
    """Return metric-level Morris index handling review rows."""

    rows = _read_csv_rows(summary_path)
    manifest = _read_json_object(manifest_path)
    parameter_count = _parameter_count(rows=rows, manifest=manifest)
    metrics = sorted({row.get("metric", "") for row in rows if row.get("metric", "")})
    output: list[dict[str, str]] = []
    for metric in metrics:
        metric_rows = [row for row in rows if row.get("metric", "") == metric]
        output.append(_metric_row(metric, metric_rows, parameter_count=parameter_count))
    return output


def write_sensitivity_index_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SENSITIVITY_INDEX_REVIEW_DOC_PATH,
    summary_path: str | Path = DEFAULT_MORRIS_SUMMARY_PATH,
    morris_manifest_path: str | Path = DEFAULT_MORRIS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write metric-level Morris index review CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SENSITIVITY_INDEX_REVIEW_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in SENSITIVITY_INDEX_REVIEW_COLUMNS
                }
            )

    summary = build_sensitivity_index_review_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        summary_path=summary_path,
        morris_manifest_path=morris_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_sensitivity_index_review_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_sensitivity_index_review_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SENSITIVITY_INDEX_REVIEW_DOC_PATH,
    summary_path: str | Path = DEFAULT_MORRIS_SUMMARY_PATH,
    morris_manifest_path: str | Path = DEFAULT_MORRIS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for Morris index review rows."""

    status_counts = _counts(row.get("index_review_status", "") for row in rows)
    unavailable_total = sum(_int_value(row.get("unavailable_index_rows", "")) or 0 for row in rows)
    zero_total = sum(_int_value(row.get("zero_mu_star_rows", "")) or 0 for row in rows)
    positive_total = sum(_int_value(row.get("positive_mu_star_rows", "")) or 0 for row in rows)
    all_zero_groups = sum(_int_value(row.get("all_zero_groups", "")) or 0 for row in rows)
    unavailable_groups = sum(_int_value(row.get("unavailable_groups", "")) or 0 for row in rows)
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("index_review_status", "")).startswith("needs_human_review_")
    )
    return {
        "schema_version": 1,
        "result_scope": SENSITIVITY_INDEX_REVIEW_SCOPE,
        "claim_boundary": (
            "This packet summarizes Morris index handling by metric. It does "
            "not create sensitivity acceptance, does not waive Sobol analysis, "
            "and does not support calibrated final-study sensitivity claims."
        ),
        "row_count": len(rows),
        "metric_ids": [str(row.get("metric", "")) for row in rows],
        "index_review_status_counts": status_counts,
        "human_review_metric_count": human_review_count,
        "unavailable_index_row_count": unavailable_total,
        "zero_mu_star_row_count": zero_total,
        "positive_mu_star_row_count": positive_total,
        "all_zero_group_count": all_zero_groups,
        "unavailable_group_count": unavailable_groups,
        "sensitivity_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "morris_summary": _display_path(Path(summary_path)),
            "morris_manifest": _display_path(Path(morris_manifest_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "document how unavailable p80/p95 arrival Morris indices are handled before manuscript use",
            "interpret zero mu_star rows as scaffold diagnostics rather than calibrated no-effect findings",
            "decide whether Morris screening is sufficient or Sobol analysis is required in sensitivity_acceptance.json",
            "keep sensitivity figures and tables inside scaffold scope until graph-scale and sensitivity acceptance close",
        ],
        "remaining_blockers": [
            "metric-level index handling still requires human review",
            "Morris-vs-Sobol method decision is absent from formal sensitivity acceptance",
        ],
    }


def build_sensitivity_index_review_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for the Morris index handling review packet."""

    lines = [
        "# Sensitivity Index Review Packet",
        "",
        str(manifest.get("claim_boundary", SENSITIVITY_INDEX_REVIEW_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Metrics: {manifest.get('row_count', 0)}",
        f"- Unavailable index rows: {manifest.get('unavailable_index_row_count', 0)}",
        f"- Zero `mu_star` rows: {manifest.get('zero_mu_star_row_count', 0)}",
        f"- All-zero metric/policy/scenario groups: {manifest.get('all_zero_group_count', 0)}",
        f"- Status counts: `{manifest.get('index_review_status_counts', {})}`",
        "",
        "## Rows",
        "",
        "| Metric | Unavailable | Zero mu_star | Positive mu_star | All-zero groups | Status | Required action |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {metric} | {unavailable} | {zero} | {positive} | {groups} | {status} | {action} |".format(
                metric=_cell(row.get("metric", "")),
                unavailable=_cell(row.get("unavailable_index_rows", "")),
                zero=_cell(row.get("zero_mu_star_rows", "")),
                positive=_cell(row.get("positive_mu_star_rows", "")),
                groups=_cell(row.get("all_zero_groups", "")),
                status=_cell(row.get("index_review_status", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is metric-level index-handling review support only.",
            "- It does not accept Morris results, waive Sobol analysis, or prove no-effect parameter findings.",
            "- It cannot create or replace `data/manifests/sensitivity_acceptance.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def _metric_row(
    metric: str,
    rows: Sequence[Mapping[str, str]],
    *,
    parameter_count: int,
) -> dict[str, str]:
    unavailable_rows = [row for row in rows if _is_unavailable(row)]
    available_rows = [row for row in rows if not _is_unavailable(row)]
    zero_rows = [row for row in available_rows if _float_value(row.get("mu_star", "")) == 0.0]
    positive_rows = [
        row
        for row in available_rows
        if (_float_value(row.get("mu_star", "")) or 0.0) > 0.0
    ]
    group_counts = _group_counts(rows)
    zero_group_counts = _group_counts(zero_rows)
    unavailable_group_counts = _group_counts(unavailable_rows)
    all_zero_groups = sum(
        1
        for group, count in zero_group_counts.items()
        if count == parameter_count and group_counts.get(group, 0) == parameter_count
    )
    status, action, publication_status = _metric_status(
        unavailable_count=len(unavailable_rows),
        zero_count=len(zero_rows),
    )
    return {
        "metric": metric,
        "total_rows": str(len(rows)),
        "available_rows": str(len(available_rows)),
        "unavailable_index_rows": str(len(unavailable_rows)),
        "zero_mu_star_rows": str(len(zero_rows)),
        "positive_mu_star_rows": str(len(positive_rows)),
        "metric_policy_scenario_groups": str(len(group_counts)),
        "all_zero_groups": str(all_zero_groups),
        "unavailable_groups": str(len(unavailable_group_counts)),
        "affected_unavailable_policies": _join_sorted(
            row.get("policy_id", "") for row in unavailable_rows
        ),
        "affected_unavailable_scenarios": _join_sorted(
            row.get("scenario_id", "") for row in unavailable_rows
        ),
        "index_review_status": status,
        "required_reviewer_action": action,
        "publication_use_status": publication_status,
        "can_support_sensitivity_gate": "false",
        "claim_boundary": SENSITIVITY_INDEX_REVIEW_SCOPE,
    }


def _metric_status(
    *,
    unavailable_count: int,
    zero_count: int,
) -> tuple[str, str, str]:
    if unavailable_count:
        return (
            "needs_human_review_unavailable_indices",
            "document unavailable index handling for this metric before using rankings",
            "blocked_from_final_claims_until_unavailable_index_review",
        )
    if zero_count:
        return (
            "needs_human_review_zero_mu_star_rows",
            "interpret zero mu_star rows before claiming parameter influence or no effect",
            "review_required_before_parameter_ranking_claims",
        )
    return (
        "needs_human_review_positive_indices",
        "review positive Morris rankings against scaffold scope before manuscript use",
        "review_required_before_final_sensitivity_claims",
    )


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    filepath = Path(path)
    with filepath.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json_object(path: str | Path) -> dict[str, Any]:
    filepath = Path(path)
    with filepath.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{filepath} must contain a JSON object")
    return value


def _parameter_count(
    *,
    rows: Sequence[Mapping[str, str]],
    manifest: Mapping[str, Any],
) -> int:
    parameters = manifest.get("parameter_ids")
    if isinstance(parameters, list) and parameters:
        return len(parameters)
    return len({row.get("parameter_id", "") for row in rows if row.get("parameter_id", "")})


def _group_counts(rows: Sequence[Mapping[str, str]]) -> Counter[tuple[str, str, str]]:
    return Counter(
        (
            str(row.get("metric", "")),
            str(row.get("policy_id", "")),
            str(row.get("scenario_id", "")),
        )
        for row in rows
    )


def _is_unavailable(row: Mapping[str, str]) -> bool:
    return str(row.get("index_status", "")).strip() in UNAVAILABLE_INDEX_STATUSES


def _float_value(value: Any) -> float | None:
    text = "" if value is None else str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _int_value(value: Any) -> int | None:
    try:
        text = str(value).strip()
        if not text:
            return None
        return int(float(text))
    except (TypeError, ValueError):
        return None


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] += 1
    return dict(sorted(counts.items()))


def _join_sorted(values: Iterable[Any]) -> str:
    return "; ".join(sorted({str(value).strip() for value in values if str(value).strip()}))


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_SENSITIVITY_INDEX_REVIEW_DOC_PATH",
    "DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH",
    "DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH",
    "SENSITIVITY_INDEX_REVIEW_COLUMNS",
    "SENSITIVITY_INDEX_REVIEW_SCOPE",
    "build_sensitivity_index_review_manifest",
    "build_sensitivity_index_review_markdown",
    "build_sensitivity_index_review_rows",
    "write_sensitivity_index_review_packet",
]
