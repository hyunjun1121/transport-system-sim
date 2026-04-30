"""Visualization: heatmaps, Pareto curves, contour plots."""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for Termux
import matplotlib.pyplot as plt
import seaborn as sns


def plot_delta_heatmap(df: pd.DataFrame, output_dir: str = "results") -> str:
    """Plot delta_makespan heatmap: s (x) vs p_fail_scale (y).

    Positive delta = bus slower = multimodal wins.
    Negative delta = multimodal slower.
    """
    pivot = df.pivot_table(
        index="p_fail_scale", columns="s",
        values="delta_makespan", aggfunc="mean",
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        pivot, annot=True, fmt=".1f", cmap="RdBu_r", center=0,
        linewidths=0.5, ax=ax,
    )
    ax.set_title("Delta Makespan (Bus - Multimodal) [min]\nPositive = Multimodal Wins")
    ax.set_xlabel("Congestion Scale (s)")
    ax.set_ylabel("Failure Rate Scale")

    path = os.path.join(output_dir, "delta_heatmap.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_success_rate_comparison(df: pd.DataFrame, output_dir: str = "results") -> str:
    """Plot success rate comparison for bus vs multimodal."""
    pivot_bus = df.pivot_table(
        index="p_fail_scale", columns="s",
        values="bus_success_rate", aggfunc="mean",
    )
    pivot_multi = df.pivot_table(
        index="p_fail_scale", columns="s",
        values="multi_success_rate", aggfunc="mean",
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sns.heatmap(pivot_bus, annot=True, fmt=".2f", cmap="YlOrRd", ax=axes[0], vmin=0, vmax=1)
    axes[0].set_title("Bus-Only Success Rate")

    sns.heatmap(pivot_multi, annot=True, fmt=".2f", cmap="YlOrRd", ax=axes[1], vmin=0, vmax=1)
    axes[1].set_title("Multimodal Success Rate")

    fig.suptitle("Success Rate Comparison")
    path = os.path.join(output_dir, "success_rate_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_policy_pareto(df: pd.DataFrame, output_dir: str = "results") -> str:
    """Plot Pareto curve: makespan vs leftover (undelivered) for each policy."""
    fig, ax = plt.subplots(figsize=(8, 6))

    for policy_name in df["policy"].unique():
        subset = df[df["policy"] == policy_name]
        avg = subset.groupby("sigma").agg({
            "bus_makespan": "mean",
            "bus_leftover": "mean",
        }).reset_index()

        ax.scatter(avg["bus_leftover"], avg["bus_makespan"], label=f"{policy_name} (Bus)", marker="o")
        ax.plot(avg["bus_leftover"], avg["bus_makespan"], "--", alpha=0.5)

        avg_m = subset.groupby("sigma").agg({
            "multi_makespan": "mean",
            "multi_leftover": "mean",
        }).reset_index()

        ax.scatter(avg_m["multi_leftover"], avg_m["multi_makespan"], label=f"{policy_name} (Multi)", marker="s")
        ax.plot(avg_m["multi_leftover"], avg_m["multi_makespan"], "--", alpha=0.5)

    ax.set_xlabel("Undelivered Personnel")
    ax.set_ylabel("Makespan (min)")
    ax.set_title("Policy Pareto: Makespan vs Undelivered")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    path = os.path.join(output_dir, "policy_pareto.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_breakeven_line(
    breakeven_results: dict[float, float | None],
    output_dir: str = "results",
) -> str:
    """Plot break-even p* vs congestion scale s."""
    s_vals = sorted(breakeven_results.keys())
    p_vals = [breakeven_results[s] for s in s_vals]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(s_vals, p_vals, "bo-", markersize=8)
    ax.set_xlabel("Congestion Scale (s)")
    ax.set_ylabel("Break-even p_fail*")
    ax.set_title("Break-even Failure Rate vs Congestion Scale\n(Above line: Multimodal wins)")
    ax.grid(True, alpha=0.3)

    path = os.path.join(output_dir, "breakeven_line.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path
