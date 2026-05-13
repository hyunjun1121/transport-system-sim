"""Generate Figure 4 (v0.7) — Quantile Arrival & Completion Curves.

Two-panel figure summarizing v0.7 quantile KPIs across the
``p_fail_scale`` design grid for Origin A (R=30 paired reps per level):

  * Panel A: q90 arrival time (minutes) — bus-only vs multimodal lines
    with paired-t 95% CI bands.
  * Panel B: P(완료 ≤ 1500 min) — bus-only vs multimodal lines with
    paired-t 95% CI bands; horizontal reference at y=1.0.

Replaces the v0.6 PNG at
``manuscript/figures/figure4_success_vs_disruption.png``.

Run from the project root (``kci/``):

    python scripts/make_figure4_v07.py
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "results" / "phase1a_origin_A.csv"
OUTPUT_PNG = ROOT / "manuscript" / "figures" / "figure4_success_vs_disruption.png"
CAPTION_MD = ROOT / "manuscript" / "figures" / "figure4_caption_ko.md"

DEADLINE_MIN = 1500
BUS_COLOR = "#1f77b4"      # blue
MULTI_COLOR = "#d62728"    # red


def _configure_korean_font() -> str:
    candidates = [
        "Malgun Gothic",
        "NanumGothic",
        "Nanum Gothic",
        "AppleGothic",
        "Hancom Gothic",
        "Noto Sans CJK KR",
    ]
    installed = {f.name for f in fm.fontManager.ttflist}
    chosen = next((c for c in candidates if c in installed), None)
    if chosen is None:
        chosen = "DejaVu Sans"
        print(
            f"WARNING: no Korean font found, falling back to {chosen}.",
            file=sys.stderr,
        )
    matplotlib.rcParams["font.family"] = chosen
    matplotlib.rcParams["axes.unicode_minus"] = False
    return chosen


def _ci(values: np.ndarray) -> tuple[float, float, float]:
    """Return (mean, ci_lo, ci_hi) using paired-t (df=n-1)."""
    n = values.size
    mean = float(np.mean(values))
    if n <= 1:
        return mean, mean, mean
    sd = float(np.std(values, ddof=1))
    se = sd / np.sqrt(n) if sd > 0 else 0.0
    if sd == 0.0:
        return mean, mean, mean
    tcrit = float(stats.t.ppf(0.975, df=n - 1))
    half = tcrit * se
    return mean, mean - half, mean + half


def _summarize(df: pd.DataFrame, col: str) -> pd.DataFrame:
    out = []
    for p, g in df.groupby("p_fail_scale"):
        vals = g[col].to_numpy(dtype=float)
        mean, lo, hi = _ci(vals)
        out.append(
            {
                "p_fail_scale": float(p),
                "n": int(vals.size),
                "mean": mean,
                "ci_lo": lo,
                "ci_hi": hi,
            }
        )
    return pd.DataFrame(out).sort_values("p_fail_scale").reset_index(drop=True)


def _plot_pair(
    ax: plt.Axes,
    x: np.ndarray,
    bus: pd.DataFrame,
    multi: pd.DataFrame,
    *,
    ylabel: str,
    title: str,
) -> None:
    ax.fill_between(
        x,
        bus["ci_lo"].to_numpy(),
        bus["ci_hi"].to_numpy(),
        color=BUS_COLOR,
        alpha=0.18,
        linewidth=0,
    )
    ax.plot(
        x,
        bus["mean"].to_numpy(),
        marker="o",
        color=BUS_COLOR,
        linewidth=2.0,
        markersize=6,
        label="버스 단일",
    )

    ax.fill_between(
        x,
        multi["ci_lo"].to_numpy(),
        multi["ci_hi"].to_numpy(),
        color=MULTI_COLOR,
        alpha=0.18,
        linewidth=0,
    )
    ax.plot(
        x,
        multi["mean"].to_numpy(),
        marker="s",
        color=MULTI_COLOR,
        linewidth=2.0,
        markersize=6,
        label="복합수단",
    )

    ax.set_xlabel("도로 링크 고장 강도 p_fail_scale", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12, pad=8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{v:g}" for v in x])
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.legend(loc="best", fontsize=9, framealpha=0.9)


def main() -> int:
    font_used = _configure_korean_font()
    print(f"Using font: {font_used}")

    if not INPUT_CSV.exists():
        print(f"ERROR: missing input {INPUT_CSV}", file=sys.stderr)
        return 1

    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} rows from {INPUT_CSV.name}")

    required = [
        "p_fail_scale",
        "bus_arrival_q90_min",
        "multi_arrival_q90_min",
        "bus_prob_completion_within_window",
        "multi_prob_completion_within_window",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"ERROR: missing columns {missing}", file=sys.stderr)
        return 1

    bus_q90 = _summarize(df, "bus_arrival_q90_min")
    multi_q90 = _summarize(df, "multi_arrival_q90_min")
    bus_pc = _summarize(df, "bus_prob_completion_within_window")
    multi_pc = _summarize(df, "multi_prob_completion_within_window")

    print("\nPanel A - bus_arrival_q90_min:")
    print(bus_q90.to_string(index=False))
    print("\nPanel A - multi_arrival_q90_min:")
    print(multi_q90.to_string(index=False))
    print("\nPanel B - bus_prob_completion_within_window:")
    print(bus_pc.to_string(index=False))
    print("\nPanel B - multi_prob_completion_within_window:")
    print(multi_pc.to_string(index=False))

    x = bus_q90["p_fail_scale"].to_numpy()

    # ------------------------------------------------------------------
    # Plot — two-panel (side by side)
    # ------------------------------------------------------------------
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.5, 5.4))

    _plot_pair(
        axA,
        x,
        bus_q90,
        multi_q90,
        ylabel="도착 시간 q90 (분)",
        title="(A) q90 도착 시간 vs p_fail_scale (Origin A, R=30)",
    )

    _plot_pair(
        axB,
        x,
        bus_pc,
        multi_pc,
        ylabel=f"P(완료 ≤ deadline={DEADLINE_MIN}min)",
        title=f"(B) 마감 {DEADLINE_MIN}분 내 완료 확률 vs p_fail_scale",
    )
    axB.set_ylim(0.0, 1.05)
    axB.axhline(
        1.0,
        color="black",
        linestyle="--",
        linewidth=1.0,
        alpha=0.7,
    )
    axB.text(
        x.max(),
        1.0,
        " P=1.0",
        va="bottom",
        ha="right",
        fontsize=9,
        color="black",
    )

    fig.suptitle(
        "그림 4. Phase 1a 분위 도착 시간 및 마감 내 완료 확률 곡선",
        fontsize=13,
        y=1.00,
    )
    fig.tight_layout()

    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=200, bbox_inches="tight")
    plt.close(fig)
    sz = OUTPUT_PNG.stat().st_size
    print(f"\nWrote {OUTPUT_PNG} ({sz:,} bytes)")

    # ------------------------------------------------------------------
    # Caption (Korean, 3-4 sentences)
    # ------------------------------------------------------------------
    def _row(s: pd.DataFrame, p: float) -> pd.Series:
        return s.loc[s["p_fail_scale"] == p].iloc[0]

    bq0, bq2 = _row(bus_q90, 0.0), _row(bus_q90, 2.0)
    mq0, mq2 = _row(multi_q90, 0.0), _row(multi_q90, 2.0)
    bp0, bp2 = _row(bus_pc, 0.0), _row(bus_pc, 2.0)
    mp0, mp2 = _row(multi_pc, 0.0), _row(multi_pc, 2.0)

    caption = (
        "**그림 4.** Phase 1a 분위 도착 시간 및 마감 내 완료 확률 곡선. "
        "Origin A에서 도로 링크 고장 강도 `p_fail_scale`을 8수준(0.0, 0.10, 0.25, "
        "0.50, 0.75, 1.0, 1.5, 2.0)으로 변화시키며 각 수준에서 R=30회 페어드 "
        "반복한 시뮬레이션 결과를, 패널 A는 q90 도착 시간(분), 패널 B는 "
        f"마감 {DEADLINE_MIN}분 내 완료 확률 P(완료 ≤ deadline)로 나타내고, "
        "각각 paired-t 분포(자유도 29) 기반 95% 신뢰구간을 음영 띠로 표시한다 "
        "(파란색=버스 단일, 빨간색=복합수단). "
        f"패널 A에서 버스 단일의 q90 도착 시간은 p_fail_scale=0.0에서 {bq0['mean']:,.1f}분 → "
        f"p_fail_scale=2.0에서 {bq2['mean']:,.1f}분으로 증가하고, 복합수단은 "
        f"{mq0['mean']:,.1f}분 → {mq2['mean']:,.1f}분으로 증가하여 두 모드 모두 "
        "장애 강도가 커질수록 꼬리 도착 시간이 비선형적으로 늘어난다. "
        f"패널 B에서는 버스 단일의 마감 내 완료 확률이 {bp0['mean']:.3f} → {bp2['mean']:.3f}, "
        f"복합수단은 {mp0['mean']:.3f} → {mp2['mean']:.3f}로 변화하며, "
        "관측 전 구간에서 버스 단일이 복합수단보다 마감 내 완료 확률을 동등하거나 "
        "더 높게 유지함을 보여준다 (검은 점선 y=1.0은 완전 완료 기준)."
    )
    CAPTION_MD.write_text(caption + "\n", encoding="utf-8")
    print(f"Wrote {CAPTION_MD}")

    print(
        f"\nHeadline: bus_q90 @p=0.0 = {bq0['mean']:.2f} min, @p=2.0 = {bq2['mean']:.2f} min"
    )
    print(
        f"          multi_q90 @p=0.0 = {mq0['mean']:.2f} min, @p=2.0 = {mq2['mean']:.2f} min"
    )
    print(
        f"          bus_prob_completion @p=0.0 = {bp0['mean']:.4f}, @p=2.0 = {bp2['mean']:.4f}"
    )
    print(
        f"          multi_prob_completion @p=0.0 = {mp0['mean']:.4f}, @p=2.0 = {mp2['mean']:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
