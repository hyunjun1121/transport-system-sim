"""Generate Figure 4 (English-labeled, v0.7) — Quantile arrival & completion curves.

Outputs:
  - manuscript/figures/figure4_success_vs_disruption_en.png

Run from kci/ project root:
    python scripts/make_figure4_v07_en.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "results" / "phase1a_origin_A.csv"
OUTPUT_PNG = ROOT / "manuscript" / "figures" / "figure4_success_vs_disruption_en.png"

DEADLINE_MIN = 1500
BUS_COLOR = "#1f77b4"
MULTI_COLOR = "#d62728"

matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["axes.unicode_minus"] = False


def _ci(values):
    n = values.size
    mean = float(np.mean(values))
    if n <= 1: return mean, mean, mean
    sd = float(np.std(values, ddof=1)); se = sd / np.sqrt(n) if sd > 0 else 0.0
    if sd == 0.0: return mean, mean, mean
    tcrit = float(stats.t.ppf(0.975, df=n - 1))
    half = tcrit * se
    return mean, mean - half, mean + half


def _summarize(df, col):
    out = []
    for p, g in df.groupby("p_fail_scale"):
        vals = g[col].to_numpy(dtype=float)
        mean, lo, hi = _ci(vals)
        out.append({"p_fail_scale": float(p), "n": int(vals.size), "mean": mean, "ci_lo": lo, "ci_hi": hi})
    return pd.DataFrame(out).sort_values("p_fail_scale").reset_index(drop=True)


def _plot_pair(ax, x, bus, multi, *, ylabel, title):
    ax.fill_between(x, bus["ci_lo"].to_numpy(), bus["ci_hi"].to_numpy(), color=BUS_COLOR, alpha=0.18, linewidth=0)
    ax.plot(x, bus["mean"].to_numpy(), marker="o", color=BUS_COLOR, linewidth=2.0, markersize=6, label="Bus_only")
    ax.fill_between(x, multi["ci_lo"].to_numpy(), multi["ci_hi"].to_numpy(), color=MULTI_COLOR, alpha=0.18, linewidth=0)
    ax.plot(x, multi["mean"].to_numpy(), marker="s", color=MULTI_COLOR, linewidth=2.0, markersize=6, label="Multimodal")
    ax.set_xlabel("Road-link failure intensity p_fail_scale", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12, pad=8)
    ax.set_xticks(x); ax.set_xticklabels([f"{v:g}" for v in x])
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.legend(loc="best", fontsize=9, framealpha=0.9)


def main() -> int:
    if not INPUT_CSV.exists():
        print(f"ERROR: {INPUT_CSV} missing", file=sys.stderr); return 1
    df = pd.read_csv(INPUT_CSV)
    bus_q90 = _summarize(df, "bus_arrival_q90_min")
    multi_q90 = _summarize(df, "multi_arrival_q90_min")
    bus_pc = _summarize(df, "bus_prob_completion_within_window")
    multi_pc = _summarize(df, "multi_prob_completion_within_window")
    x = bus_q90["p_fail_scale"].to_numpy()

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.5, 5.4))
    _plot_pair(axA, x, bus_q90, multi_q90,
               ylabel="q90 arrival time (min)",
               title="(A) q90 arrival time vs p_fail_scale (Origin A, R=30)")
    _plot_pair(axB, x, bus_pc, multi_pc,
               ylabel=f"P(complete ≤ deadline={DEADLINE_MIN} min)",
               title=f"(B) P(complete ≤ {DEADLINE_MIN} min) vs p_fail_scale")
    axB.set_ylim(0.0, 1.05)
    axB.axhline(1.0, color="black", linestyle="--", linewidth=1.0, alpha=0.7)
    axB.text(x.max(), 1.0, " P=1.0", va="bottom", ha="right", fontsize=9)
    fig.suptitle("Figure 4. Phase 1a quantile arrival time and probability of completion within deadline",
                 fontsize=13, y=1.00)
    fig.tight_layout()
    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUTPUT_PNG} ({OUTPUT_PNG.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
