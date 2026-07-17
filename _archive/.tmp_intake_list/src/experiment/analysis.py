"""Experiment result analysis: confidence intervals, break-even estimation."""

import numpy as np
import pandas as pd


CI_STAT_COLUMNS = [
    "mean",
    "std",
    "count",
    "ci_lower",
    "ci_upper",
    "finite_count",
    "nonfinite_count",
]

EXPERIMENT_CONTEXT_COLUMNS = [
    "network_variant",
    "failure_mode",
    "capacity_reduction_factor",
]

PHASE1_MEAN_COLUMNS = {
    "bus_makespan": "bus_makespan_mean",
    "multi_makespan": "multi_makespan_mean",
    "delta_makespan": "delta_mean",
    "bus_success_rate": "bus_sr_mean",
    "multi_success_rate": "multi_sr_mean",
    "bus_leftover": "bus_leftover_mean",
    "multi_leftover": "multi_leftover_mean",
    "bus_penalized_makespan": "bus_penalized_makespan_mean",
    "multi_penalized_makespan": "multi_penalized_makespan_mean",
    "delta_penalized_makespan": "delta_penalized_makespan_mean",
    "bus_success_count": "bus_success_count_mean",
    "multi_success_count": "multi_success_count_mean",
    "bus_completion_rate": "bus_completion_rate_mean",
    "multi_completion_rate": "multi_completion_rate_mean",
    "delta_completion_rate": "delta_completion_rate_mean",
    "bus_censored_count": "bus_censored_count_mean",
    "multi_censored_count": "multi_censored_count_mean",
    "bus_resource_eff": "bus_resource_eff_mean",
    "multi_resource_eff": "multi_resource_eff_mean",
    "delta_resource_eff": "delta_resource_eff_mean",
    "bus_total_personnel": "bus_total_personnel_mean",
    "multi_total_personnel": "multi_total_personnel_mean",
    "bus_bus_trips": "bus_bus_trips_mean",
    "multi_bus_trips": "multi_bus_trips_mean",
    "bus_train_trips": "bus_train_trips_mean",
    "multi_train_trips": "multi_train_trips_mean",
    "bus_bus_minutes": "bus_bus_minutes_mean",
    "multi_bus_minutes": "multi_bus_minutes_mean",
    "bus_train_minutes": "bus_train_minutes_mean",
    "multi_train_minutes": "multi_train_minutes_mean",
    "bus_lastmile_minutes": "bus_lastmile_minutes_mean",
    "multi_lastmile_minutes": "multi_lastmile_minutes_mean",
    "bus_lastmile_vehicle_minutes": "bus_lastmile_vehicle_minutes_mean",
    "multi_lastmile_vehicle_minutes": "multi_lastmile_vehicle_minutes_mean",
    "bus_road_vehicle_service_minutes": "bus_road_vehicle_service_minutes_mean",
    "multi_road_vehicle_service_minutes": "multi_road_vehicle_service_minutes_mean",
    "bus_train_service_minutes": "bus_train_service_minutes_mean",
    "multi_train_service_minutes": "multi_train_service_minutes_mean",
    "bus_total_service_minutes": "bus_total_service_minutes_mean",
    "multi_total_service_minutes": "multi_total_service_minutes_mean",
    "bus_passenger_travel_minutes": "bus_passenger_travel_minutes_mean",
    "multi_passenger_travel_minutes": "multi_passenger_travel_minutes_mean",
    "bus_passengers_per_vehicle_minute": "bus_passengers_per_vehicle_minute_mean",
    "multi_passengers_per_vehicle_minute": "multi_passengers_per_vehicle_minute_mean",
    "bus_passengers_per_total_service_minute": (
        "bus_passengers_per_total_service_minute_mean"
    ),
    "multi_passengers_per_total_service_minute": (
        "multi_passengers_per_total_service_minute_mean"
    ),
}

PHASE1_STD_COLUMNS = {
    "delta_makespan": "delta_std",
    "delta_penalized_makespan": "delta_penalized_makespan_std",
    "delta_completion_rate": "delta_completion_rate_std",
    "delta_resource_eff": "delta_resource_eff_std",
    "delta_road_vehicle_service_minutes": "delta_road_vehicle_service_minutes_std",
    "delta_train_service_minutes": "delta_train_service_minutes_std",
    "delta_total_service_minutes": "delta_total_service_minutes_std",
    "delta_passenger_travel_minutes": "delta_passenger_travel_minutes_std",
    "delta_passengers_per_vehicle_minute": "delta_passengers_per_vehicle_minute_std",
    "delta_passengers_per_total_service_minute": (
        "delta_passengers_per_total_service_minute_std"
    ),
}


def _finite_values(values: pd.Series) -> np.ndarray:
    """Return numeric finite values, dropping NaN and +/-inf."""
    numeric = pd.to_numeric(values, errors="coerce").astype(float)
    array = numeric.to_numpy()
    return array[np.isfinite(array)]


def _finite_mean(values: pd.Series) -> float:
    finite = _finite_values(values)
    if len(finite) == 0:
        return float("nan")
    return float(np.mean(finite))


def _finite_std(values: pd.Series) -> float:
    finite = _finite_values(values)
    if len(finite) <= 1:
        return float("nan")
    return float(np.std(finite, ddof=1))


def compute_ci(
    df: pd.DataFrame,
    metric: str,
    group_cols: list[str] | str | None,
    confidence: float = 0.95,
) -> pd.DataFrame:
    """Compute mean, std, and confidence interval for a metric grouped by columns.

    Args:
        df: results DataFrame
        metric: column name to analyze
        group_cols: columns to group by
        confidence: confidence level (default 0.95)

    Returns:
        DataFrame with mean, std, ci_lower, ci_upper columns
    """
    if group_cols is None:
        group_cols = []
    elif isinstance(group_cols, str):
        group_cols = [group_cols]
    else:
        group_cols = list(group_cols)
    group_cols = _expand_experiment_group_cols(df, group_cols)
    if metric not in df.columns:
        raise KeyError(f"Metric column not found: {metric}")
    missing_group_cols = [col for col in group_cols if col not in df.columns]
    if missing_group_cols:
        raise KeyError(f"Group column(s) not found: {missing_group_cols}")

    z = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}.get(confidence, 1.96)

    def stats_for(values: pd.Series) -> dict:
        numeric = pd.to_numeric(values, errors="coerce").astype(float)
        array = numeric.to_numpy()
        finite = array[np.isfinite(array)]
        count = len(finite)
        nonfinite_count = len(array) - count

        if count == 0:
            return {
                "mean": float("nan"),
                "std": float("nan"),
                "count": 0,
                "ci_lower": float("nan"),
                "ci_upper": float("nan"),
                "finite_count": 0,
                "nonfinite_count": int(nonfinite_count),
            }

        mean = float(np.mean(finite))
        if count == 1:
            std = 0.0
            margin = 0.0
        else:
            std = float(np.std(finite, ddof=1))
            margin = z * std / np.sqrt(count)

        return {
            "mean": mean,
            "std": std,
            "count": int(count),
            "ci_lower": mean - margin,
            "ci_upper": mean + margin,
            "finite_count": int(count),
            "nonfinite_count": int(nonfinite_count),
        }

    if not group_cols:
        return pd.DataFrame([stats_for(df[metric])])

    rows = []
    for group_key, values in df.groupby(group_cols, dropna=False)[metric]:
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        row = dict(zip(group_cols, group_key))
        row.update(stats_for(values))
        rows.append(row)

    if not rows:
        return pd.DataFrame(columns=[*group_cols, *CI_STAT_COLUMNS])
    return pd.DataFrame(rows)


def find_breakeven(
    df: pd.DataFrame,
    s_value: float,
    metric: str | None = None,
    filters: dict[str, object] | None = None,
) -> float | None:
    """Find break-even p_fail* where the selected delta metric crosses zero.

    Uses linear interpolation between adjacent grid points.

    Args:
        df: Phase 1 results with 's', 'p_fail_scale', and a delta metric
        s_value: specific congestion scale to analyze
        metric: delta column to interpolate. Defaults to
            ``delta_penalized_makespan`` when available, then ``delta_makespan``.
        filters: Optional context filters, such as
            ``{"network_variant": "baseline", "failure_mode": "blocked"}``.

    Returns:
        Estimated p_fail* or None if no crossing found
    """
    metric = _select_delta_metric(df, metric)
    required = {"s", "p_fail_scale", metric}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Required column(s) not found: {sorted(missing)}")

    subset = df[df["s"] == s_value].copy()
    subset = _apply_context_filters(subset, filters)
    if len(subset) == 0:
        return None
    if _has_ambiguous_context(subset, filters):
        return None

    # Average finite delta values across replications.
    avg = subset.groupby("p_fail_scale", dropna=False)[metric].apply(_finite_mean)
    avg = avg.reset_index(name="delta")
    avg["p_fail_scale"] = pd.to_numeric(avg["p_fail_scale"], errors="coerce").astype(float)
    avg["delta"] = pd.to_numeric(avg["delta"], errors="coerce").astype(float)
    avg = avg[np.isfinite(avg["p_fail_scale"]) & np.isfinite(avg["delta"])]
    avg = avg.sort_values("p_fail_scale")
    if len(avg) == 0:
        return None

    p_values = avg["p_fail_scale"].to_numpy()
    delta_values = avg["delta"].to_numpy()

    # Find sign change
    for i in range(len(delta_values) - 1):
        if delta_values[i] * delta_values[i + 1] <= 0:
            # Linear interpolation
            p1, p2 = p_values[i], p_values[i + 1]
            d1, d2 = delta_values[i], delta_values[i + 1]
            if d2 - d1 == 0:
                return float(p1)
            p_star = p1 + (p2 - p1) * (-d1) / (d2 - d1)
            return float(p_star)

    return None


def summarize_phase1(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize Phase 1 results by experiment context and grid point."""
    required = {"s", "p_fail_scale"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Required column(s) not found: {sorted(missing)}")
    group_cols = _phase1_group_cols(df)

    rows = []
    for group_key, group in df.groupby(group_cols, dropna=False):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        row = dict(zip(group_cols, group_key))

        for source, target in PHASE1_MEAN_COLUMNS.items():
            if source in group.columns:
                row[target] = _finite_mean(group[source])

        for source, target in PHASE1_STD_COLUMNS.items():
            if source in group.columns:
                row[target] = _finite_std(group[source])

        rows.append(row)

    if not rows:
        columns = group_cols
        columns.extend(PHASE1_MEAN_COLUMNS.values())
        columns.extend(PHASE1_STD_COLUMNS.values())
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows)


def _select_delta_metric(df: pd.DataFrame, metric: str | None) -> str:
    if metric is not None:
        return metric
    if "delta_penalized_makespan" in df.columns:
        return "delta_penalized_makespan"
    return "delta_makespan"


def _phase1_group_cols(df: pd.DataFrame) -> list[str]:
    context_cols = [col for col in EXPERIMENT_CONTEXT_COLUMNS if col in df.columns]
    return [*context_cols, "s", "p_fail_scale"]


def _expand_experiment_group_cols(
    df: pd.DataFrame,
    group_cols: list[str],
) -> list[str]:
    """Preserve context columns when grouping known experiment axes."""
    experiment_axes = {"s", "p_fail_scale", "sigma", "policy"}
    if not (set(group_cols) & experiment_axes):
        return group_cols

    expanded = list(group_cols)
    for col in EXPERIMENT_CONTEXT_COLUMNS:
        if col in df.columns and col not in expanded:
            expanded.append(col)
    return expanded


def _apply_context_filters(
    df: pd.DataFrame,
    filters: dict[str, object] | None,
) -> pd.DataFrame:
    if not filters:
        return df

    subset = df
    for column, value in filters.items():
        if column not in subset.columns:
            raise KeyError(f"Filter column not found: {column}")
        if value is None or (isinstance(value, float) and np.isnan(value)):
            subset = subset[subset[column].isna()]
        else:
            subset = subset[subset[column] == value]
    return subset


def _has_ambiguous_context(
    df: pd.DataFrame,
    filters: dict[str, object] | None,
) -> bool:
    filtered_cols = set(filters or {})
    for column in EXPERIMENT_CONTEXT_COLUMNS:
        if column not in df.columns or column in filtered_cols:
            continue
        if df[column].nunique(dropna=False) > 1:
            return True
    return False
