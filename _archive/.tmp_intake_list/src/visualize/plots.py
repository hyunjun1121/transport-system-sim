"""Visualization: heatmaps, Pareto curves, contour plots."""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless Windows/CI runs
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import seaborn as sns


def plot_delta_heatmap(
    df: pd.DataFrame,
    output_dir: str | Path = "results",
    metric: str | None = None,
) -> str:
    """Plot delta KPI heatmap: s (x) vs p_fail_scale (y).

    Positive delta = bus slower = multimodal wins.
    Negative delta = multimodal slower.
    """
    metric = metric or _first_existing(
        df,
        ["delta_penalized_makespan", "delta_makespan"],
    )
    pivot = _pivot_finite_mean(
        df,
        index="p_fail_scale",
        columns="s",
        values=metric,
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    if _has_plot_values(pivot):
        sns.heatmap(
            pivot, annot=True, fmt=".1f", cmap="RdBu_r", center=0,
            linewidths=0.5, ax=ax,
        )
    else:
        ax.text(
            0.5, 0.5, "No finite delta values",
            ha="center", va="center", transform=ax.transAxes,
        )
    ax.set_title(f"{_metric_label(metric)}\nPositive = Multimodal Lower")
    ax.set_xlabel("Congestion Scale (s)")
    ax.set_ylabel("Failure-Rate Scale (p_fail_scale)")

    path = _output_path(output_dir, "delta_heatmap.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def plot_success_rate_comparison(
    df: pd.DataFrame,
    output_dir: str | Path = "results",
) -> str:
    """Plot completion/success rate comparison for bus vs multimodal."""
    if {"bus_completion_rate", "multi_completion_rate"} <= set(df.columns):
        bus_metric = "bus_completion_rate"
        multi_metric = "multi_completion_rate"
        metric_label = "Completion Rate"
    else:
        bus_metric = "bus_success_rate"
        multi_metric = "multi_success_rate"
        metric_label = "Success Rate"

    pivot_bus = _pivot_finite_mean(
        df,
        index="p_fail_scale",
        columns="s",
        values=bus_metric,
    )
    pivot_multi = _pivot_finite_mean(
        df,
        index="p_fail_scale",
        columns="s",
        values=multi_metric,
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    _plot_rate_heatmap(pivot_bus, axes[0])
    axes[0].set_title(f"Bus-Only {metric_label}")
    axes[0].set_xlabel("Congestion Scale (s)")
    axes[0].set_ylabel("Failure-Rate Scale (p_fail_scale)")

    _plot_rate_heatmap(pivot_multi, axes[1])
    axes[1].set_title(f"Multimodal {metric_label}")
    axes[1].set_xlabel("Congestion Scale (s)")
    axes[1].set_ylabel("Failure-Rate Scale (p_fail_scale)")

    fig.suptitle(f"{metric_label} Comparison")
    path = _output_path(output_dir, "success_rate_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def plot_policy_pareto(df: pd.DataFrame, output_dir: str | Path = "results") -> str:
    """Plot Pareto curve: completion time vs undelivered for each policy."""
    fig, ax = plt.subplots(figsize=(8, 6))
    use_penalized = {
        "bus_penalized_makespan",
        "multi_penalized_makespan",
    } <= set(df.columns)
    bus_time_col = "bus_penalized_makespan" if use_penalized else "bus_makespan"
    multi_time_col = "multi_penalized_makespan" if use_penalized else "multi_makespan"
    y_label = "Penalized Makespan (min)" if use_penalized else "Observed Makespan (min)"

    use_censored = {"bus_censored_count", "multi_censored_count"} <= set(df.columns)
    bus_undelivered_col = "bus_censored_count" if use_censored else "bus_leftover"
    multi_undelivered_col = "multi_censored_count" if use_censored else "multi_leftover"
    x_label = "Censored Personnel" if use_censored else "Undelivered Personnel"

    plotted_any = False
    for policy_name in sorted(df["policy"].dropna().unique(), key=str):
        subset = df[df["policy"] == policy_name]
        avg = _group_finite_mean(
            subset,
            "sigma",
            [bus_time_col, bus_undelivered_col],
        )
        avg = avg.dropna(subset=[bus_time_col, bus_undelivered_col])
        avg = avg.sort_values("sigma")

        if len(avg) > 0:
            ax.scatter(
                avg[bus_undelivered_col],
                avg[bus_time_col],
                label=f"{policy_name} (Bus)",
                marker="o",
            )
            ax.plot(avg[bus_undelivered_col], avg[bus_time_col], "--", alpha=0.5)
            plotted_any = True

        avg_m = _group_finite_mean(
            subset,
            "sigma",
            [multi_time_col, multi_undelivered_col],
        )
        avg_m = avg_m.dropna(subset=[multi_time_col, multi_undelivered_col])
        avg_m = avg_m.sort_values("sigma")

        if len(avg_m) > 0:
            ax.scatter(
                avg_m[multi_undelivered_col],
                avg_m[multi_time_col],
                label=f"{policy_name} (Multi)",
                marker="s",
            )
            ax.plot(avg_m[multi_undelivered_col], avg_m[multi_time_col], "--", alpha=0.5)
            plotted_any = True

    if not plotted_any:
        ax.text(
            0.5, 0.5, "No finite policy trade-off values",
            ha="center", va="center", transform=ax.transAxes,
        )

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(f"Policy Trade-off: {y_label} vs {x_label}")
    if plotted_any:
        ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    path = _output_path(output_dir, "policy_pareto.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def plot_breakeven_line(
    breakeven_results: dict[float, float | None],
    output_dir: str | Path = "results",
) -> str:
    """Plot break-even p* vs congestion scale s."""
    s_vals = sorted(breakeven_results.keys())
    valid_points = [
        (s, breakeven_results[s])
        for s in s_vals
        if breakeven_results[s] is not None and np.isfinite(breakeven_results[s])
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    if valid_points:
        plot_s, plot_p = zip(*valid_points)
        ax.plot(plot_s, plot_p, "bo-", markersize=8)
    else:
        ax.text(
            0.5, 0.5, "No break-even crossings found",
            ha="center", va="center", transform=ax.transAxes,
        )
    ax.set_xlabel("Congestion Scale (s)")
    ax.set_ylabel("Break-even Failure-Rate Scale (p_fail_scale)")
    ax.set_title("Break-even Failure-Rate Scale vs Congestion Scale")
    ax.grid(True, alpha=0.3)

    path = _output_path(output_dir, "breakeven_line.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def _output_path(output_dir: str | Path, filename: str) -> Path:
    """Create the plot directory and return the target path."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path / filename


def _first_existing(df: pd.DataFrame, columns: list[str]) -> str:
    """Return the first listed column present in the DataFrame."""
    for column in columns:
        if column in df.columns:
            return column
    raise KeyError(f"None of the required columns exist: {columns}")


def _finite_mean(values: pd.Series) -> float:
    """Mean of finite numeric values only."""
    numeric = pd.to_numeric(values, errors="coerce").astype(float).to_numpy()
    finite = numeric[np.isfinite(numeric)]
    if len(finite) == 0:
        return float("nan")
    return float(np.mean(finite))


def _pivot_finite_mean(
    df: pd.DataFrame,
    *,
    index: str,
    columns: str,
    values: str,
) -> pd.DataFrame:
    """Create a pivot table using finite means to avoid inf-tainted plots."""
    missing = [col for col in (index, columns, values) if col not in df.columns]
    if missing:
        raise KeyError(f"Plot column(s) not found: {missing}")
    pivot = df.pivot_table(
        index=index,
        columns=columns,
        values=values,
        aggfunc=_finite_mean,
        dropna=False,
    )
    return pivot.replace([np.inf, -np.inf], np.nan)


def _group_finite_mean(
    df: pd.DataFrame,
    group_col: str,
    value_cols: list[str],
) -> pd.DataFrame:
    """Group by one column and compute finite means for selected values."""
    missing = [col for col in [group_col, *value_cols] if col not in df.columns]
    if missing:
        raise KeyError(f"Plot column(s) not found: {missing}")
    rows = []
    for group_value, group in df.groupby(group_col, dropna=False):
        row = {group_col: group_value}
        for value_col in value_cols:
            row[value_col] = _finite_mean(group[value_col])
        rows.append(row)
    return pd.DataFrame(rows, columns=[group_col, *value_cols])


def _plot_rate_heatmap(pivot: pd.DataFrame, ax: Axes) -> None:
    """Draw a bounded rate heatmap or an empty-data message."""
    if _has_plot_values(pivot):
        sns.heatmap(
            pivot,
            annot=True,
            fmt=".2f",
            cmap="YlOrRd",
            ax=ax,
            vmin=0,
            vmax=1,
        )
    else:
        ax.text(
            0.5, 0.5, "No finite rate values",
            ha="center", va="center", transform=ax.transAxes,
        )


def _has_plot_values(values: pd.DataFrame) -> bool:
    """Return True when a matrix contains at least one finite value."""
    if values.empty:
        return False
    numeric = values.apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    return bool(np.isfinite(numeric).any())


def _metric_label(metric: str) -> str:
    """Human-readable label for plot titles."""
    labels = {
        "delta_penalized_makespan": "Delta Penalized Makespan (Bus - Multimodal) [min]",
        "delta_makespan": "Delta Observed Makespan (Bus - Multimodal) [min]",
    }
    return labels.get(metric, metric.replace("_", " ").title())
