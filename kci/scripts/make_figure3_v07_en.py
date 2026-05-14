"""Generate Figure 3 (English-labeled, v0.7) — Phase 1a Robustness Curve.

Outputs:
  - manuscript/figures/figure3_robustness_curve_en.png

Run from kci/ project root:
    python scripts/make_figure3_v07_en.py
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
OUTPUT_PNG = ROOT / "manuscript" / "figures" / "figure3_robustness_curve_en.png"

matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["axes.unicode_minus"] = False


def _summarize(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for p, g in df.groupby("p_fail_scale"):
        vals = g["delta_penalized_makespan"].to_numpy()
        n = vals.size
        mean = float(np.mean(vals))
        sd = float(np.std(vals, ddof=1)) if n > 1 else 0.0
        se = sd / np.sqrt(n) if n > 0 else 0.0
        if n > 1 and sd > 0:
            tcrit = stats.t.ppf(0.975, df=n - 1)
            half = tcrit * se
        else:
            half = 0.0
        out.append({
            "p_fail_scale": float(p), "n": int(n), "mean": mean, "sd": sd, "se": se,
            "ci_lo": mean - half, "ci_hi": mean + half,
        })
    return pd.DataFrame(out).sort_values("p_fail_scale").reset_index(drop=True)


def main() -> int:
    if not INPUT_CSV.exists():
        print(f"ERROR: {INPUT_CSV} missing", file=sys.stderr); return 1
    df = pd.read_csv(INPUT_CSV)
    summary = _summarize(df)
    x, y = summary["p_fail_scale"].to_numpy(), summary["mean"].to_numpy()
    lo, hi = summary["ci_lo"].to_numpy(), summary["ci_hi"].to_numpy()

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.fill_between(x, lo, hi, color="#1f77b4", alpha=0.20, linewidth=0,
                    label="95% CI (paired-t, df=29)")
    ax.plot(x, y, marker="o", color="#1f77b4", linewidth=2.0, markersize=6,
            label="Mean Δ (bus_only - multimodal)")
    ax.axhline(0.0, color="black", linestyle="--", linewidth=1.0, alpha=0.7)
    ax.text(x.max(), 0.0, " Δ=0 (break-even)", va="bottom", ha="right",
            fontsize=9, color="black")
    ax.set_xlabel("Road-link failure intensity p_fail_scale", fontsize=11)
    ax.set_ylabel("Δ penalized makespan (min, bus_only − multimodal)", fontsize=11)
    ax.set_title("Phase 1a robustness curve — Δ(penalized makespan) vs p_fail_scale (Origin A, R=30)",
                 fontsize=12, pad=10)
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.set_xticks(x); ax.set_xticklabels([f"{v:g}" for v in x])
    if bool(np.all(y < 0)) or bool(np.all(y > 0)):
        ax.text(0.02, 0.04, "bus_only dominates across all observed disruption levels",
                transform=ax.transAxes, ha="left", va="bottom", fontsize=10,
                bbox=dict(facecolor="white", edgecolor="black", alpha=0.85))
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    fig.tight_layout()
    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUTPUT_PNG} ({OUTPUT_PNG.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
