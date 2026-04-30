"""Experiment result analysis: confidence intervals, break-even estimation."""

import numpy as np
import pandas as pd


def compute_ci(
    df: pd.DataFrame,
    metric: str,
    group_cols: list[str],
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
    z = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}.get(confidence, 1.96)

    grouped = df.groupby(group_cols)[metric]
    stats = grouped.agg(["mean", "std", "count"])
    stats.columns = ["mean", "std", "count"]
    stats["ci_lower"] = stats["mean"] - z * stats["std"] / np.sqrt(stats["count"])
    stats["ci_upper"] = stats["mean"] + z * stats["std"] / np.sqrt(stats["count"])
    return stats.reset_index()


def find_breakeven(df: pd.DataFrame, s_value: float) -> float | None:
    """Find break-even p_fail* where delta_makespan crosses zero.

    Uses linear interpolation between adjacent grid points.

    Args:
        df: Phase 1 results with 's', 'p_fail_scale', 'delta_makespan'
        s_value: specific congestion scale to analyze

    Returns:
        Estimated p_fail* or None if no crossing found
    """
    subset = df[df["s"] == s_value].copy()
    if len(subset) == 0:
        return None

    # Average delta across replications
    avg = subset.groupby("p_fail_scale")["delta_makespan"].mean().sort_index()
    p_values = avg.index.values
    delta_values = avg.values

    # Find sign change
    for i in range(len(delta_values) - 1):
        if delta_values[i] * delta_values[i + 1] <= 0:
            # Linear interpolation
            p1, p2 = p_values[i], p_values[i + 1]
            d1, d2 = delta_values[i], delta_values[i + 1]
            if d2 - d1 == 0:
                return p1
            p_star = p1 + (p2 - p1) * (-d1) / (d2 - d1)
            return float(p_star)

    return None


def summarize_phase1(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize Phase 1 results: mean KPIs per (s, p_fail_scale)."""
    summary = df.groupby(["s", "p_fail_scale"]).agg({
        "bus_makespan": "mean",
        "multi_makespan": "mean",
        "delta_makespan": ["mean", "std"],
        "bus_success_rate": "mean",
        "multi_success_rate": "mean",
        "bus_leftover": "mean",
        "multi_leftover": "mean",
    }).reset_index()
    summary.columns = [
        "s", "p_fail_scale",
        "bus_makespan_mean", "multi_makespan_mean",
        "delta_mean", "delta_std",
        "bus_sr_mean", "multi_sr_mean",
        "bus_leftover_mean", "multi_leftover_mean",
    ]
    return summary
