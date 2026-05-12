"""Generate Figure 4 for the KCI manuscript.

Phase 1 success-rate (completion-rate) vs disruption (p_fail_scale) curves
for Bus vs Multimodal policies, grouped by congestion scale s in
{0.8, 1.2, 2.0}. Includes 95% CIs over the 10 reps.

Outputs:
    manuscript/figures/figure4_success_vs_disruption.png  (300 dpi)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import stats


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = REPO_ROOT / "results" / "phase1_origin_A.csv"
OUTPUT_PNG = REPO_ROOT / "manuscript" / "figures" / "figure4_success_vs_disruption.png"

S_LEVELS = [0.8, 1.2, 2.0]
S_LABELS = {0.8: "s=0.8 (저혼잡)", 1.2: "s=1.2 (기준)", 2.0: "s=2.0 (고혼잡)"}
S_COLORS = {0.8: "#1f77b4", 1.2: "#2ca02c", 2.0: "#d62728"}


def _configure_korean_font() -> None:
    rcParams["font.family"] = "Malgun Gothic"
    rcParams["axes.unicode_minus"] = False


def _mean_ci(values: np.ndarray, alpha: float = 0.05) -> tuple[float, float, float]:
    """Return mean and (lo, hi) 95% CI using a t-distribution."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    n = values.size
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    mean = float(values.mean())
    if n < 2:
        return mean, mean, mean
    se = float(values.std(ddof=1) / np.sqrt(n))
    if se == 0.0:
        return mean, mean, mean
    half = stats.t.ppf(1 - alpha / 2, df=n - 1) * se
    return mean, mean - half, mean + half


def _paired_diff_ci(
    a: np.ndarray, b: np.ndarray, alpha: float = 0.05
) -> tuple[float, float, float]:
    """Paired mean(a-b) with 95% CI; aligned by index order (rep)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b)
    diff = a[mask] - b[mask]
    n = diff.size
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    mean = float(diff.mean())
    if n < 2:
        return mean, mean, mean
    se = float(diff.std(ddof=1) / np.sqrt(n))
    if se == 0.0:
        return mean, mean, mean
    half = stats.t.ppf(1 - alpha / 2, df=n - 1) * se
    return mean, mean - half, mean + half


def _summary_by_group(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (s_val, p_val), grp in df.groupby(["s", "p_fail_scale"]):
        grp_sorted = grp.sort_values("rep")
        bus = grp_sorted["bus_completion_rate"].to_numpy()
        multi = grp_sorted["multi_completion_rate"].to_numpy()
        bm, blo, bhi = _mean_ci(bus)
        mm, mlo, mhi = _mean_ci(multi)
        dm, dlo, dhi = _paired_diff_ci(multi, bus)
        rows.append(
            dict(
                s=s_val,
                p_fail_scale=p_val,
                n=len(grp_sorted),
                bus_mean=bm,
                bus_lo=blo,
                bus_hi=bhi,
                multi_mean=mm,
                multi_lo=mlo,
                multi_hi=mhi,
                delta_mean=dm,
                delta_lo=dlo,
                delta_hi=dhi,
            )
        )
    return pd.DataFrame(rows).sort_values(["s", "p_fail_scale"]).reset_index(drop=True)


def _plot_completion_panel(ax, summary: pd.DataFrame) -> None:
    for s_val in S_LEVELS:
        sub = summary[np.isclose(summary["s"], s_val)].sort_values("p_fail_scale")
        if sub.empty:
            continue
        color = S_COLORS[s_val]
        label_base = S_LABELS[s_val]
        x = sub["p_fail_scale"].to_numpy()

        ax.plot(
            x,
            sub["bus_mean"].to_numpy(),
            color=color,
            linestyle="--",
            marker="o",
            markersize=5,
            linewidth=1.6,
            label=f"Bus, {label_base}",
        )
        ax.fill_between(
            x,
            sub["bus_lo"].to_numpy(),
            sub["bus_hi"].to_numpy(),
            color=color,
            alpha=0.10,
            linewidth=0,
        )

        ax.plot(
            x,
            sub["multi_mean"].to_numpy(),
            color=color,
            linestyle="-",
            marker="s",
            markersize=5,
            linewidth=2.0,
            label=f"Multimodal, {label_base}",
        )
        ax.fill_between(
            x,
            sub["multi_lo"].to_numpy(),
            sub["multi_hi"].to_numpy(),
            color=color,
            alpha=0.18,
            linewidth=0,
        )

    ax.set_xlabel("p_fail_scale")
    ax.set_ylabel("완수율")
    ax.set_title("(a) 정책별 평균 완수율 ± 95% CI")
    ax.set_xlim(-0.05, 3.05)
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(fontsize=8, loc="lower left", ncol=1, framealpha=0.9)


def _plot_paired_delta_panel(ax, summary: pd.DataFrame) -> None:
    ax.axhline(0.0, color="black", linewidth=0.8, linestyle="-")
    for s_val in S_LEVELS:
        sub = summary[np.isclose(summary["s"], s_val)].sort_values("p_fail_scale")
        if sub.empty:
            continue
        color = S_COLORS[s_val]
        x = sub["p_fail_scale"].to_numpy()
        ax.plot(
            x,
            sub["delta_mean"].to_numpy(),
            color=color,
            marker="D",
            markersize=5,
            linewidth=1.8,
            label=S_LABELS[s_val],
        )
        ax.fill_between(
            x,
            sub["delta_lo"].to_numpy(),
            sub["delta_hi"].to_numpy(),
            color=color,
            alpha=0.18,
            linewidth=0,
        )

    ax.set_xlabel("p_fail_scale")
    ax.set_ylabel("완수율 차이 (Multimodal - Bus)")
    ax.set_title("(b) 쌍체비교: 멀티모달 우위 (95% CI)")
    ax.set_xlim(-0.05, 3.05)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(fontsize=9, loc="best", framealpha=0.9)


def main() -> Path:
    _configure_korean_font()
    df = pd.read_csv(INPUT_CSV)

    df = df[df["s"].isin(S_LEVELS)].copy()
    summary = _summary_by_group(df)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    _plot_completion_panel(axes[0], summary)
    _plot_paired_delta_panel(axes[1], summary)

    fig.suptitle(
        "Phase 1: 도로 장애 강도별 완수율 비교 (Bus vs Multimodal)",
        fontsize=13,
        y=1.02,
    )
    fig.tight_layout()

    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return OUTPUT_PNG


if __name__ == "__main__":
    out = main()
    print(f"Wrote {out}")
