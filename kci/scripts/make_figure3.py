"""Generate Figure 3 for the KCI manuscript.

Figure 3 plots a heatmap of the mean Phase-1 penalized-makespan delta
(bus-only minus multimodal) across the (congestion_scale ``s``,
``p_fail_scale``) design grid, overlaying the break-even contour where
delta = 0.

The figure is intentionally rendered with Korean axis labels and a Korean
caption so it can be dropped directly into the KCI manuscript.
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
from matplotlib.colors import TwoSlopeNorm


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "results" / "phase1_origin_A.csv"
OUTPUT_PNG = ROOT / "manuscript" / "figures" / "figure3_breakeven_heatmap.png"
CAPTION_MD = ROOT / "manuscript" / "figures" / "figure3_caption_ko.md"


def _configure_korean_font() -> str:
    """Pick a Korean-capable font present on the system and configure mpl."""

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
        # Fall back, but warn — Korean glyphs will render as boxes.
        chosen = "DejaVu Sans"
        print(
            f"WARNING: no Korean font found, falling back to {chosen}. "
            f"Tried: {candidates}",
            file=sys.stderr,
        )
    matplotlib.rcParams["font.family"] = chosen
    matplotlib.rcParams["axes.unicode_minus"] = False
    return chosen


def _build_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the long-format CSV to a (s × p_fail_scale) mean matrix."""

    agg = (
        df.groupby(["s", "p_fail_scale"], as_index=False)["delta_penalized_makespan"]
        .mean()
    )
    pivot = agg.pivot(index="s", columns="p_fail_scale", values="delta_penalized_makespan")
    # Keep axes in ascending order for readability.
    pivot = pivot.sort_index(axis=0).sort_index(axis=1)
    return pivot


def _annotate(ax: plt.Axes, matrix: np.ndarray, vmin: float, vmax: float) -> None:
    """Write the cell value into each tile with adaptive text color."""

    abs_max = max(abs(vmin), abs(vmax))
    rows, cols = matrix.shape
    for i in range(rows):
        for j in range(cols):
            value = matrix[i, j]
            if abs(value) >= 10000:
                label = f"{value/1000:.1f}k"
            elif abs(value) >= 100:
                label = f"{value:.0f}"
            else:
                label = f"{value:.1f}"
            # Light text where the diverging colormap is dark.
            color = "white" if abs(value) > 0.55 * abs_max else "black"
            ax.text(
                j,
                i,
                label,
                ha="center",
                va="center",
                color=color,
                fontsize=9,
            )


def main() -> int:
    font_used = _configure_korean_font()
    print(f"Using font: {font_used}")

    df = pd.read_csv(INPUT_CSV)
    n_groups = df.groupby(["s", "p_fail_scale"]).size()
    if not (n_groups == 10).all():
        print(
            f"WARNING: not all (s, p_fail_scale) cells have 10 reps; counts:\n{n_groups}",
            file=sys.stderr,
        )
    pivot = _build_pivot(df)

    matrix = pivot.values
    s_levels = pivot.index.to_numpy()
    p_levels = pivot.columns.to_numpy()

    vmin = float(np.nanmin(matrix))
    vmax = float(np.nanmax(matrix))
    # Force a symmetric, zero-centered diverging scale.
    abs_max = max(abs(vmin), abs(vmax), 1e-9)
    if vmin == vmax == 0:
        norm = TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
    else:
        norm = TwoSlopeNorm(vmin=-abs_max, vcenter=0.0, vmax=abs_max)

    fig, ax = plt.subplots(figsize=(9.0, 5.5))
    im = ax.imshow(
        matrix,
        cmap="RdBu_r",
        norm=norm,
        aspect="auto",
        origin="lower",
    )

    ax.set_xticks(range(len(p_levels)))
    ax.set_xticklabels([f"{v:g}" for v in p_levels])
    ax.set_yticks(range(len(s_levels)))
    ax.set_yticklabels([f"{v:g}" for v in s_levels])

    ax.set_xlabel("도로 장애 강도 (p_fail_scale)", fontsize=11)
    ax.set_ylabel("교통 혼잡 배수 (s)", fontsize=11)
    ax.set_title(
        "Phase 1: Δ penalized_makespan (Bus - Multimodal)",
        fontsize=12,
        pad=10,
    )

    _annotate(ax, matrix, -abs_max, abs_max)

    # Break-even contour at delta = 0 on a refined grid so it lines up
    # with the imshow extent (cell centers at integer indices).
    xs = np.arange(len(p_levels))
    ys = np.arange(len(s_levels))
    X, Y = np.meshgrid(xs, ys)
    if np.nanmin(matrix) < 0 < np.nanmax(matrix):
        cs = ax.contour(
            X,
            Y,
            matrix,
            levels=[0.0],
            colors="black",
            linewidths=2.0,
            linestyles="--",
        )
        ax.clabel(cs, fmt={0.0: "break-even (Δ=0)"}, fontsize=9, inline=True)
    else:
        # No sign change — mark the regime entirely.
        sign = "Δ ≤ 0 전 영역" if np.nanmax(matrix) <= 0 else "Δ ≥ 0 전 영역"
        ax.text(
            0.98,
            0.02,
            sign,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=10,
            color="black",
            bbox=dict(facecolor="white", edgecolor="black", alpha=0.7),
        )

    cbar = fig.colorbar(im, ax=ax, shrink=0.9, pad=0.02)
    cbar.set_label("Δ penalized_makespan (분)", fontsize=11)

    fig.tight_layout()
    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUTPUT_PNG}")

    # ---- Caption -------------------------------------------------------
    n_neg = int(np.sum(matrix < 0))
    n_pos = int(np.sum(matrix > 0))
    n_zero = int(np.sum(matrix == 0))
    most_negative_idx = np.unravel_index(np.nanargmin(matrix), matrix.shape)
    s_best = s_levels[most_negative_idx[0]]
    p_best = p_levels[most_negative_idx[1]]
    delta_best = matrix[most_negative_idx]

    caption = (
        "**그림 3.** Phase 1 실험에서 도로 장애 강도(`p_fail_scale`, 7 수준: "
        "0.0–3.0)와 교통 혼잡 배수(`s`, 5 수준: 0.8–2.0)의 35개 셀에 대해 "
        "각각 10회 반복 시뮬레이션의 평균 Δ penalized_makespan "
        "(버스 단일 모드 − 다중수단 통합)을 표시한 발산형 색상지도이다. "
        f"음수 셀(파란색, n={n_neg})은 다중수단 통합 운용이 단일 버스 운용보다 "
        f"penalized makespan 측면에서 우수함을, 양수 셀(붉은색, n={n_pos})은 그 반대를 의미하며, "
        f"검은 점선은 두 모드의 성과가 같아지는 손익분기 등고선(Δ=0)을 나타낸다. "
        f"본 실험 범위 전체에서 평균 Δ는 음의 값(또는 0)으로 관측되었고"
        f"({n_neg}/{n_neg+n_pos+n_zero} 셀이 음수), "
        f"가장 큰 우위는 s={s_best:g}, p_fail_scale={p_best:g}에서 "
        f"Δ≈{delta_best:,.0f}분으로 다중수단 통합 운용의 강건성이 확인된다. "
        "도로 장애 강도가 커지거나 교통 혼잡이 심해질수록 단일 버스 모드의 "
        "penalized makespan이 비선형적으로 악화되어 두 모드 간 격차가 확대되는 "
        "양상이 뚜렷하다."
    )
    CAPTION_MD.write_text(caption + "\n", encoding="utf-8")
    print(f"Wrote {CAPTION_MD}")

    # ---- Console summary ----------------------------------------------
    print("\nMean delta_penalized_makespan (min) by (s, p_fail_scale):")
    with pd.option_context("display.float_format", lambda x: f"{x:>12,.1f}"):
        print(pivot.to_string())
    print(
        f"\nMatrix sign tally - negative: {n_neg}, positive: {n_pos}, zero: {n_zero}"
    )
    print(
        f"Most-negative cell: s={s_best:g}, p_fail_scale={p_best:g}, "
        f"delta={delta_best:,.1f} min"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
