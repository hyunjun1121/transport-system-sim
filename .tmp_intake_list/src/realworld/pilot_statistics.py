"""Uncertainty summaries for cached pilot experiment outputs.

The pilot experiment CSVs are reproducible scaffold outputs. These helpers add
seed-replication confidence intervals and paired policy-delta summaries without
upgrading the claim boundary to calibrated real-world evidence.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.pilot_experiments import (
    DEFAULT_OUTPUT_DIR,
    METRIC_COLUMNS,
    PROJECT_ROOT,
    SUMMARY_GROUP_COLUMNS,
)


DEFAULT_PILOT_FULL_RESULTS_PATH = DEFAULT_OUTPUT_DIR / "pilot_full_results.csv"
DEFAULT_PILOT_FULL_MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "pilot_full_manifest.json"
DEFAULT_PILOT_TABLE_DIR = DEFAULT_OUTPUT_DIR / "tables"
DEFAULT_STATISTICS_SCOPE = (
    "Pilot scaffold uncertainty summary; not calibrated real-world confidence "
    "evidence or an operational forecast."
)
DEFAULT_MULTIPLE_COMPARISON_BOUNDARY = (
    "No formal multiple-comparison correction is accepted for the current "
    "scaffold outputs. Primary comparisons must be selected before formal "
    "experiment acceptance; all other scenario, policy, and metric comparisons "
    "are exploratory."
)

METRIC_CI_COLUMNS = SUMMARY_GROUP_COLUMNS + (
    "metric",
    "sample_count",
    "mean",
    "std_dev",
    "std_error",
    "ci95_low",
    "ci95_high",
    "claim_scope",
)
PAIRED_DELTA_CI_COLUMNS = (
    "region_id",
    "graph_source",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "baseline_policy_id",
    "comparison_policy_id",
    "baseline_mode",
    "comparison_mode",
    "metric",
    "metric_direction",
    "paired_count",
    "mean_delta",
    "std_dev_delta",
    "std_error_delta",
    "ci95_low",
    "ci95_high",
    "delta_interpretation",
    "claim_scope",
)
HIGHER_IS_BETTER_METRICS = frozenset(
    {"completion_rate", "passengers_per_total_service_minute"}
)
LOWER_IS_BETTER_METRICS = frozenset(set(METRIC_COLUMNS) - HIGHER_IS_BETTER_METRICS)


def load_pilot_result_rows(path: str | Path) -> list[dict[str, str]]:
    """Load pilot result rows from CSV."""

    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_metric_ci_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    metrics: Sequence[str] = METRIC_COLUMNS,
    claim_scope: str = DEFAULT_STATISTICS_SCOPE,
) -> list[dict[str, Any]]:
    """Return one confidence-interval row per group and metric."""

    grouped: dict[tuple[str, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(_text(row.get(column)) for column in SUMMARY_GROUP_COLUMNS)].append(row)

    output_rows: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group_rows = grouped[key]
        base = dict(zip(SUMMARY_GROUP_COLUMNS, key))
        for metric in metrics:
            stats = _summary_stats(_finite_values(row.get(metric) for row in group_rows))
            output_rows.append(
                {
                    **base,
                    "metric": metric,
                    "sample_count": stats["count"],
                    "mean": stats["mean"],
                    "std_dev": stats["std_dev"],
                    "std_error": stats["std_error"],
                    "ci95_low": stats["ci95_low"],
                    "ci95_high": stats["ci95_high"],
                    "claim_scope": claim_scope,
                }
            )
    return output_rows


def build_paired_delta_ci_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    baseline_policy_id: str = "bus_only",
    metrics: Sequence[str] = METRIC_COLUMNS,
    claim_scope: str = DEFAULT_STATISTICS_SCOPE,
) -> list[dict[str, Any]]:
    """Return paired comparison-policy minus baseline confidence intervals."""

    paired_index: dict[tuple[str, str, str, str, str, str], dict[str, Mapping[str, Any]]] = (
        defaultdict(dict)
    )
    for row in rows:
        key = (
            _text(row.get("region_id")),
            _text(row.get("graph_source")),
            _text(row.get("scenario_id")),
            _text(row.get("scenario_family")),
            _text(row.get("scenario_type")),
            _text(row.get("seed")),
        )
        paired_index[key][_text(row.get("policy_id"))] = row

    delta_groups: dict[
        tuple[str, str, str, str, str, str, str, str, str, str],
        list[float],
    ] = defaultdict(list)
    for key, by_policy in paired_index.items():
        baseline = by_policy.get(baseline_policy_id)
        if baseline is None:
            continue
        for policy_id, comparison in by_policy.items():
            if policy_id == baseline_policy_id:
                continue
            for metric in metrics:
                group_key = (
                    key[0],
                    key[1],
                    key[2],
                    key[3],
                    key[4],
                    baseline_policy_id,
                    policy_id,
                    _text(baseline.get("mode")),
                    _text(comparison.get("mode")),
                    metric,
                )
                delta_groups.setdefault(group_key, [])
                baseline_value = _float_value(baseline.get(metric))
                comparison_value = _float_value(comparison.get(metric))
                if baseline_value is None or comparison_value is None:
                    continue
                delta_groups[group_key].append(comparison_value - baseline_value)

    output_rows: list[dict[str, Any]] = []
    for key in sorted(delta_groups):
        stats = _summary_stats(delta_groups[key])
        metric = key[9]
        metric_direction = _metric_direction(metric)
        output_rows.append(
            {
                "region_id": key[0],
                "graph_source": key[1],
                "scenario_id": key[2],
                "scenario_family": key[3],
                "scenario_type": key[4],
                "baseline_policy_id": key[5],
                "comparison_policy_id": key[6],
                "baseline_mode": key[7],
                "comparison_mode": key[8],
                "metric": metric,
                "metric_direction": metric_direction,
                "paired_count": stats["count"],
                "mean_delta": stats["mean"],
                "std_dev_delta": stats["std_dev"],
                "std_error_delta": stats["std_error"],
                "ci95_low": stats["ci95_low"],
                "ci95_high": stats["ci95_high"],
                "delta_interpretation": _delta_interpretation(metric_direction),
                "claim_scope": claim_scope,
            }
        )
    return output_rows


def write_pilot_statistics_outputs(
    *,
    rows: Sequence[Mapping[str, Any]],
    output_dir: str | Path = DEFAULT_PILOT_TABLE_DIR,
    output_prefix: str = "pilot_full",
    source_results_path: str | Path = DEFAULT_PILOT_FULL_RESULTS_PATH,
    source_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    claim_scope: str = DEFAULT_STATISTICS_SCOPE,
) -> dict[str, Any]:
    """Write metric and paired-delta CI CSVs plus a manifest."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    _validate_output_prefix(output_prefix)
    metric_rows = build_metric_ci_rows(rows, claim_scope=claim_scope)
    paired_rows = build_paired_delta_ci_rows(rows, claim_scope=claim_scope)
    metric_path = directory / f"{output_prefix}_metric_ci.csv"
    paired_path = directory / f"{output_prefix}_paired_delta_ci.csv"
    manifest_path = directory / f"{output_prefix}_statistics_manifest.json"

    _write_csv(metric_path, METRIC_CI_COLUMNS, metric_rows)
    _write_csv(paired_path, PAIRED_DELTA_CI_COLUMNS, paired_rows)
    source_manifest = _load_json_object(source_manifest_path)
    manifest = _statistics_manifest(
        source_results_path=source_results_path,
        source_manifest_path=source_manifest_path,
        source_manifest=source_manifest,
        output_prefix=output_prefix,
        metric_path=metric_path,
        paired_path=paired_path,
        manifest_path=manifest_path,
        metric_rows=metric_rows,
        paired_rows=paired_rows,
        claim_scope=claim_scope,
    )
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return {
        "metric_rows": metric_rows,
        "paired_delta_rows": paired_rows,
        "metric_path": metric_path,
        "paired_delta_path": paired_path,
        "manifest_path": manifest_path,
        "manifest": manifest,
    }


def _summary_stats(values: Sequence[float]) -> dict[str, Any]:
    count = len(values)
    if count == 0:
        return {
            "count": 0,
            "mean": "",
            "std_dev": "",
            "std_error": "",
            "ci95_low": "",
            "ci95_high": "",
        }
    mean = sum(values) / count
    if count == 1:
        std_dev = 0.0
    else:
        variance = sum((value - mean) ** 2 for value in values) / (count - 1)
        std_dev = math.sqrt(variance)
    std_error = std_dev / math.sqrt(count)
    margin = 1.96 * std_error
    return {
        "count": count,
        "mean": _round_float(mean),
        "std_dev": _round_float(std_dev),
        "std_error": _round_float(std_error),
        "ci95_low": _round_float(mean - margin),
        "ci95_high": _round_float(mean + margin),
    }


def _finite_values(values: Iterable[Any]) -> list[float]:
    finite: list[float] = []
    for value in values:
        parsed = _float_value(value)
        if parsed is not None:
            finite.append(parsed)
    return finite


def _float_value(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _metric_direction(metric: str) -> str:
    if metric in HIGHER_IS_BETTER_METRICS:
        return "higher_is_better"
    if metric in LOWER_IS_BETTER_METRICS:
        return "lower_is_better"
    return "context_dependent"


def _delta_interpretation(metric_direction: str) -> str:
    if metric_direction == "higher_is_better":
        return "positive_delta_favors_comparison_policy"
    if metric_direction == "lower_is_better":
        return "negative_delta_favors_comparison_policy"
    return "delta_requires_metric_specific_interpretation"


def _statistics_manifest(
    *,
    source_results_path: str | Path,
    source_manifest_path: str | Path,
    source_manifest: Mapping[str, Any],
    output_prefix: str,
    metric_path: Path,
    paired_path: Path,
    manifest_path: Path,
    metric_rows: Sequence[Mapping[str, Any]],
    paired_rows: Sequence[Mapping[str, Any]],
    claim_scope: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "result_scope": claim_scope,
        "claim_boundary": (
            "Confidence intervals summarize seed-replication variability in the "
            "current scaffold outputs. They do not certify calibrated real-world "
            "accuracy, field validation, or operational routing readiness."
        ),
        "source_results_path": _display_path(source_results_path),
        "source_manifest_path": _display_path(source_manifest_path),
        "source_run_profile": source_manifest.get("run_profile", ""),
        "source_row_count": source_manifest.get("row_count", ""),
        "source_summary_row_count": source_manifest.get("summary_row_count", ""),
        "source_graph_scale": source_manifest.get("graph_scale", {}),
        "output_prefix": output_prefix,
        "outputs": {
            "metric_ci": _display_path(metric_path),
            "paired_delta_ci": _display_path(paired_path),
            "manifest": _display_path(manifest_path),
        },
        "metric_ci_row_count": len(metric_rows),
        "paired_delta_ci_row_count": len(paired_rows),
        "metric_columns": list(METRIC_COLUMNS),
        "baseline_policy_id": "bus_only",
        "ci_method": "normal_approximation_mean_plus_minus_1_96_standard_errors",
        "multiple_comparison_method": DEFAULT_MULTIPLE_COMPARISON_BOUNDARY,
        "pairing": (
            "Policy deltas are paired by region, graph source, scenario, and seed "
            "against bus_only when both rows are present."
        ),
    }


def _write_csv(path: Path, fieldnames: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _load_json_object(path: str | Path) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        return {}
    with filepath.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _round_float(value: float) -> float:
    return round(value, 6)


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _validate_output_prefix(output_prefix: str) -> None:
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_")
    if not output_prefix or any(character not in allowed for character in output_prefix):
        raise ValueError("output_prefix must use lowercase letters, digits, and underscores only")


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "DEFAULT_PILOT_FULL_MANIFEST_PATH",
    "DEFAULT_PILOT_FULL_RESULTS_PATH",
    "DEFAULT_PILOT_TABLE_DIR",
    "DEFAULT_STATISTICS_SCOPE",
    "DEFAULT_MULTIPLE_COMPARISON_BOUNDARY",
    "METRIC_CI_COLUMNS",
    "PAIRED_DELTA_CI_COLUMNS",
    "build_metric_ci_rows",
    "build_paired_delta_ci_rows",
    "load_pilot_result_rows",
    "write_pilot_statistics_outputs",
]
