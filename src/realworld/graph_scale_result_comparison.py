"""Compare current full-pilot and full-profile multi-corridor outputs.

This module writes review evidence only. It helps reviewers inspect whether
the graph-scale choice changes summary metrics, but it does not accept a graph
method or validate calibrated real-world results.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_SUMMARY_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_summary.csv"
)
DEFAULT_CANDIDATE_SUMMARY_PATH = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "pilot_multi_corridor_full_summary.csv"
)
DEFAULT_RESULT_COMPARISON_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_result_comparison.csv"
)
DEFAULT_RESULT_COMPARISON_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "graph_scale_result_comparison_manifest.json"
)

RESULT_COMPARISON_SCOPE = (
    "graph_scale_result_comparison_review_packet_not_graph_scale_acceptance"
)
KEY_COLUMNS: tuple[str, ...] = (
    "region_id",
    "graph_source",
    "policy_id",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "mode",
)
SUMMARY_METRIC_COLUMNS: tuple[str, ...] = (
    "mean_completion_rate",
    "mean_censored_count",
    "mean_penalized_makespan",
    "mean_makespan",
    "mean_road_vehicle_service_minutes",
    "mean_train_service_minutes",
    "mean_total_service_minutes",
    "mean_passenger_travel_minutes",
    "mean_passengers_per_total_service_minute",
    "mean_first_arrival_time",
    "mean_median_arrival_time",
    "mean_p80_arrival_time",
    "mean_p95_arrival_time",
)
HIGHER_IS_BETTER_SUMMARY_METRICS = frozenset(
    {"mean_completion_rate", "mean_passengers_per_total_service_minute"}
)
LOWER_IS_BETTER_SUMMARY_METRICS = frozenset(
    set(SUMMARY_METRIC_COLUMNS) - HIGHER_IS_BETTER_SUMMARY_METRICS
)
RESULT_COMPARISON_COLUMNS: tuple[str, ...] = (
    *KEY_COLUMNS,
    "metric",
    "metric_direction",
    "current_value",
    "candidate_value",
    "delta_candidate_minus_current",
    "abs_delta",
    "relative_delta_to_current",
    "comparison_status",
    "interpretation",
    "claim_scope",
)


def build_graph_scale_result_comparison_rows(
    *,
    current_summary_path: str | Path = DEFAULT_CURRENT_SUMMARY_PATH,
    candidate_summary_path: str | Path = DEFAULT_CANDIDATE_SUMMARY_PATH,
    claim_scope: str = RESULT_COMPARISON_SCOPE,
) -> list[dict[str, Any]]:
    """Return metric-level deltas between current and candidate summaries."""

    current_rows = _read_csv_rows(current_summary_path)
    candidate_rows = _read_csv_rows(candidate_summary_path)
    current_index = _index_rows(current_rows)
    candidate_index = _index_rows(candidate_rows)
    keys = sorted(set(current_index) | set(candidate_index))

    rows: list[dict[str, Any]] = []
    for key in keys:
        current = current_index.get(key)
        candidate = candidate_index.get(key)
        base = dict(zip(KEY_COLUMNS, key))
        for metric in SUMMARY_METRIC_COLUMNS:
            rows.append(
                {
                    **base,
                    **_metric_delta_fields(current, candidate, metric),
                    "claim_scope": claim_scope,
                }
            )
    return rows


def write_graph_scale_result_comparison(
    *,
    rows: Sequence[Mapping[str, Any]],
    output_path: str | Path = DEFAULT_RESULT_COMPARISON_PATH,
    manifest_path: str | Path = DEFAULT_RESULT_COMPARISON_MANIFEST_PATH,
    current_summary_path: str | Path = DEFAULT_CURRENT_SUMMARY_PATH,
    candidate_summary_path: str | Path = DEFAULT_CANDIDATE_SUMMARY_PATH,
) -> dict[str, Any]:
    """Write the comparison CSV plus conservative manifest."""

    output = Path(output_path)
    manifest_file = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=RESULT_COMPARISON_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    status_counts = _status_counts(rows)
    finite_abs_deltas = [
        float(row["abs_delta"])
        for row in rows
        if isinstance(row.get("abs_delta"), (float, int))
        and math.isfinite(float(row["abs_delta"]))
    ]
    value = {
        "schema_version": 1,
        "result_scope": RESULT_COMPARISON_SCOPE,
        "publication_ready": False,
        "claim_boundary": (
            "This comparison is graph-scale review evidence only. It does not "
            "accept a graph method, validate real-world calibration, or support "
            "operational routing claims."
        ),
        "inputs": {
            "current_summary": _display_path(current_summary_path),
            "candidate_summary": _display_path(candidate_summary_path),
        },
        "outputs": {
            "comparison": _display_path(output),
            "manifest": _display_path(manifest_file),
        },
        "row_count": len(rows),
        "metric_count": len(SUMMARY_METRIC_COLUMNS),
        "group_count": int(len(rows) / len(SUMMARY_METRIC_COLUMNS))
        if SUMMARY_METRIC_COLUMNS
        else 0,
        "comparison_status_counts": status_counts,
        "max_abs_delta": _round(max(finite_abs_deltas)) if finite_abs_deltas else "",
        "review_items": [
            "review candidate_worsens and nonfinite_difference rows before any graph-scale acceptance",
            "decide whether changed blocked-scenario outcomes reflect a better graph abstraction or an unintended scenario-method interaction",
            "regenerate sensitivity, figures, tables, and manuscript interpretation after the accepted graph-scale method is selected",
        ],
    }
    with manifest_file.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _metric_delta_fields(
    current: Mapping[str, str] | None,
    candidate: Mapping[str, str] | None,
    metric: str,
) -> dict[str, Any]:
    direction = _metric_direction(metric)
    if current is None:
        return {
            "metric": metric,
            "metric_direction": direction,
            "current_value": "",
            "candidate_value": _display_value(candidate.get(metric) if candidate else ""),
            "delta_candidate_minus_current": "",
            "abs_delta": "",
            "relative_delta_to_current": "",
            "comparison_status": "candidate_only",
            "interpretation": "candidate group has no matching current full-pilot row",
        }
    if candidate is None:
        return {
            "metric": metric,
            "metric_direction": direction,
            "current_value": _display_value(current.get(metric)),
            "candidate_value": "",
            "delta_candidate_minus_current": "",
            "abs_delta": "",
            "relative_delta_to_current": "",
            "comparison_status": "current_only",
            "interpretation": "current full-pilot group has no matching candidate row",
        }

    current_value = _float_value(current.get(metric))
    candidate_value = _float_value(candidate.get(metric))
    if current_value is None or candidate_value is None:
        return {
            "metric": metric,
            "metric_direction": direction,
            "current_value": _display_value(current.get(metric)),
            "candidate_value": _display_value(candidate.get(metric)),
            "delta_candidate_minus_current": "",
            "abs_delta": "",
            "relative_delta_to_current": "",
            "comparison_status": "nonfinite_difference",
            "interpretation": "one or both values are non-finite and require review",
        }

    delta = candidate_value - current_value
    abs_delta = abs(delta)
    relative = "" if current_value == 0 else _round(delta / abs(current_value))
    status = _comparison_status(delta, direction)
    return {
        "metric": metric,
        "metric_direction": direction,
        "current_value": _round(current_value),
        "candidate_value": _round(candidate_value),
        "delta_candidate_minus_current": _round(delta),
        "abs_delta": _round(abs_delta),
        "relative_delta_to_current": relative,
        "comparison_status": status,
        "interpretation": _interpretation(status),
    }


def _index_rows(rows: Sequence[Mapping[str, str]]) -> dict[tuple[str, ...], Mapping[str, str]]:
    return {tuple(str(row.get(column, "")).strip() for column in KEY_COLUMNS): row for row in rows}


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _metric_direction(metric: str) -> str:
    if metric in HIGHER_IS_BETTER_SUMMARY_METRICS:
        return "higher_is_better"
    if metric in LOWER_IS_BETTER_SUMMARY_METRICS:
        return "lower_is_better"
    return "context_dependent"


def _comparison_status(delta: float, direction: str) -> str:
    if abs(delta) <= 1e-9:
        return "same_or_close"
    if direction == "higher_is_better":
        return "candidate_improves" if delta > 0 else "candidate_worsens"
    if direction == "lower_is_better":
        return "candidate_improves" if delta < 0 else "candidate_worsens"
    return "changed_requires_review"


def _interpretation(status: str) -> str:
    if status == "same_or_close":
        return "candidate and current summary values match within tolerance"
    if status == "candidate_improves":
        return "candidate graph improves this summary metric directionally"
    if status == "candidate_worsens":
        return "candidate graph worsens this summary metric directionally"
    return "review required before interpreting graph-scale effect"


def _status_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("comparison_status", "")).strip()
        if status:
            counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _float_value(value: object) -> float | None:
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _display_value(value: object) -> str:
    return "" if value is None else str(value).strip()


def _round(value: float) -> float:
    return round(value, 6)


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "DEFAULT_CANDIDATE_SUMMARY_PATH",
    "DEFAULT_CURRENT_SUMMARY_PATH",
    "DEFAULT_RESULT_COMPARISON_MANIFEST_PATH",
    "DEFAULT_RESULT_COMPARISON_PATH",
    "KEY_COLUMNS",
    "RESULT_COMPARISON_COLUMNS",
    "RESULT_COMPARISON_SCOPE",
    "SUMMARY_METRIC_COLUMNS",
    "build_graph_scale_result_comparison_rows",
    "write_graph_scale_result_comparison",
]
