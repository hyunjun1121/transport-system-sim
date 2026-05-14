"""Figure 6 (English-labeled) — Phase 3 counterfactual lever-sweep heatmap.

Outputs:
  - manuscript/figures/figure6_phase3_lever_en.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

try:
    from scipy import stats
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "results" / "phase3_lever_sweep.csv"
FIG_PATH = ROOT / "manuscript" / "figures" / "figure6_phase3_lever_en.png"

METRIC = "delta_penalized_makespan"
STRESS_P = 1.5
CAP_LEVELS = [500, 1000, 2000]

matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["axes.unicode_minus"] = False


def _t_crit(df: int, alpha: float = 0.05) -> float:
    if _HAS_SCIPY:
        return float(stats.t.ppf(1 - alpha / 2.0, df=df))
    return {9: 2.262, 14: 2.145, 19: 2.093, 29: 2.045, 49: 2.010}.get(df, 1.96)


def _paired_ci(values):
    finite = values[np.isfinite(values)]
    n = int(finite.size)
    if n == 0: return float("nan"), float("nan"), float("nan"), 0
    mean = float(finite.mean())
    if n < 2: return mean, mean, mean, n
    se = float(finite.std(ddof=1) / np.sqrt(n))
    half = _t_crit(df=n - 1) * se
    return mean, mean - half, mean + half, n


def _aggregate_stress(df):
    sub = df[df["p_fail_scale"] == STRESS_P]
    rows = []
    grouped = sub.groupby(["rail_capacity_pax_per_train", "rail_headway_min", "lastmile_fleet_size"])
    for (cap, headway, fleet), grp in grouped:
        mean, lo, hi, n = _paired_ci(grp[METRIC].to_numpy())
        rows.append({
            "rail_capacity_pax_per_train": float(cap), "rail_headway_min": float(headway),
            "lastmile_fleet_size": float(fleet),
            "mean_delta": mean, "ci_lower": lo, "ci_upper": hi, "n": n,
            "ci_straddles_zero": bool(np.isfinite(lo) and np.isfinite(hi) and lo <= 0.0 <= hi),
        })
    return pd.DataFrame(rows)


def _build_matrices(agg, cap_level, headways, fleets):
    mean_mat = np.full((len(headways), len(fleets)), np.nan, dtype=float)
    flip_mat = np.zeros((len(headways), len(fleets)), dtype=bool)
    sub = agg[agg["rail_capacity_pax_per_train"] == cap_level]
    for _, row in sub.iterrows():
        try:
            i = headways.index(float(row["rail_headway_min"]))
            j = fleets.index(float(row["lastmile_fleet_size"]))
        except ValueError:
            continue
        mean_mat[i, j] = row["mean_delta"]
        flip_mat[i, j] = bool(row["ci_straddles_zero"])
    return mean_mat, flip_mat


def _plot(agg):
    headways = sorted({float(v) for v in agg["rail_headway_min"]}, reverse=True)
    fleets = sorted({float(v) for v in agg["lastmile_fleet_size"]})

    finite_means = agg["mean_delta"].to_numpy()
    finite_means = finite_means[np.isfinite(finite_means)]
    vmax_abs = float(np.max(np.abs(finite_means))) if finite_means.size > 0 else 1.0
    if vmax_abs == 0.0: vmax_abs = 1.0
    norm = TwoSlopeNorm(vmin=-vmax_abs, vcenter=0.0, vmax=vmax_abs)
    cmap = plt.get_cmap("RdBu_r")

    fig, axes = plt.subplots(1, 3, figsize=(15.0, 5.4), sharey=True)
    if not isinstance(axes, np.ndarray): axes = np.array([axes])

    im = None
    for ax, cap in zip(axes, CAP_LEVELS):
        mean_mat, flip_mat = _build_matrices(agg, float(cap), headways, fleets)
        im = ax.imshow(mean_mat, cmap=cmap, norm=norm, aspect="auto", origin="upper")
        ax.set_xticks(range(len(fleets))); ax.set_xticklabels([f"{int(f)}" for f in fleets])
        ax.set_yticks(range(len(headways))); ax.set_yticklabels([f"{h:g}" for h in headways])
        ax.set_xlabel("lastmile_fleet_size (vehicles)")
        ax.set_title(f"rail_capacity = {cap} pax/train", fontsize=11)
        for i in range(mean_mat.shape[0]):
            for j in range(mean_mat.shape[1]):
                val = mean_mat[i, j]
                if not np.isfinite(val):
                    ax.text(j, i, "n/a", ha="center", va="center", fontsize=8, color="grey")
                    continue
                rgba = cmap(norm(val))
                luminance = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
                txt_color = "white" if luminance < 0.5 else "black"
                ax.text(j, i, f"{val:,.0f}", ha="center", va="center", fontsize=8, color=txt_color)
                if flip_mat[i, j]:
                    ax.text(j, i + 0.32, "X", ha="center", va="center", fontsize=14, color="black", fontweight="bold")

    axes[0].set_ylabel("rail_headway_min (min)")

    fig.suptitle("Figure 6 — Phase 3 counterfactual lever sweep "
                 "(Δ penalized_makespan at p_fail_scale=1.5)", fontsize=13)
    fig.subplots_adjust(right=0.90, top=0.88, bottom=0.12, wspace=0.08)
    cbar_ax = fig.add_axes([0.92, 0.14, 0.018, 0.72])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label("Δ penalized_makespan (min, bus_only − multimodal)", fontsize=10)
    fig.text(0.5, 0.02,
             "X marker: cells whose 95% paired-t CI of the mean crosses zero (sign-reversal candidates).",
             ha="center", fontsize=9, color="#333333")
    FIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    if not INPUT_CSV.exists():
        print(f"ERROR: {INPUT_CSV} missing", file=sys.stderr); return 2
    df = pd.read_csv(INPUT_CSV)
    required = {"rail_headway_min", "lastmile_fleet_size", "rail_capacity_pax_per_train", "p_fail_scale", METRIC}
    missing = required - set(df.columns)
    if missing:
        print(f"ERROR: missing columns {sorted(missing)}", file=sys.stderr); return 3
    agg = _aggregate_stress(df)
    _plot(agg)
    print(f"Wrote {FIG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
