"""Figure 6 — Phase 3 counterfactual lever-sweep heatmap (headline).

Loads ``results/phase3_lever_sweep.csv`` (Phase 3 paired-CRN sweep over
``rail_headway_min`` x ``lastmile_fleet_size`` x ``rail_capacity_pax_per_train``
x ``p_fail_scale``) and renders a 3-panel diverging heatmap of mean
``delta_penalized_makespan`` at the disruption stress level
``p_fail_scale = 1.5``.

Panels:
  - One panel per ``rail_capacity_pax_per_train`` level (500 / 1000 / 2000).
  - Within each panel, Y-axis = ``rail_headway_min`` (분),
    X-axis = ``lastmile_fleet_size`` (대).
  - Cell color = mean Δ penalized_makespan (bus − multi). Diverging colormap
    ``RdBu_r`` centered at 0: blue = bus dominant (Δ < 0), red = multi
    dominant (Δ > 0).
  - A ``✕`` annotation marks any cell whose 95% paired-t CI of the mean
    crosses zero (candidate sign-flip → multimodal viability).

Outputs:
  - ``manuscript/figures/figure6_phase3_lever.png``
  - ``manuscript/figures/figure6_caption_ko.md``
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.colors import TwoSlopeNorm

try:
    from scipy import stats  # type: ignore

    _HAS_SCIPY = True
except Exception:  # pragma: no cover - fallback if scipy unavailable
    _HAS_SCIPY = False


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "phase3_lever_sweep.csv"
FIG_DIR = ROOT / "manuscript" / "figures"
FIG_PATH = FIG_DIR / "figure6_phase3_lever.png"
CAPTION_PATH = FIG_DIR / "figure6_caption_ko.md"

METRIC = "delta_penalized_makespan"
STRESS_P = 1.5

CAP_LEVELS = [500, 1000, 2000]


def _set_korean_font() -> None:
    preferred = ["Malgun Gothic", "NanumGothic", "Gulim", "Yu Gothic", "MS Gothic"]
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in installed:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


def _t_crit(df: int, alpha: float = 0.05) -> float:
    if _HAS_SCIPY:
        return float(stats.t.ppf(1 - alpha / 2.0, df=df))
    # Approximation for df=14 (R-1 with R=15): 95% two-sided t = 2.145
    # Fall back to a small lookup for typical R values.
    lut = {9: 2.262, 14: 2.145, 19: 2.093, 29: 2.045, 49: 2.010}
    if df in lut:
        return lut[df]
    # Last-resort normal approx
    return 1.96


def _paired_ci(values: np.ndarray) -> tuple[float, float, float, int]:
    """Return (mean, ci_lower, ci_upper, n_finite) for a one-sample t CI."""
    finite = values[np.isfinite(values)]
    n = int(finite.size)
    if n == 0:
        return float("nan"), float("nan"), float("nan"), 0
    mean = float(finite.mean())
    if n < 2:
        return mean, mean, mean, n
    se = float(finite.std(ddof=1) / np.sqrt(n))
    tcrit = _t_crit(df=n - 1)
    half = tcrit * se
    return mean, mean - half, mean + half, n


def _aggregate_stress(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate mean + CI at the stress p_fail_scale level."""
    sub = df[df["p_fail_scale"] == STRESS_P]
    rows: list[dict] = []
    grouped = sub.groupby(
        ["rail_capacity_pax_per_train", "rail_headway_min", "lastmile_fleet_size"]
    )
    for (cap, headway, fleet), grp in grouped:
        mean, lo, hi, n = _paired_ci(grp[METRIC].to_numpy())
        rows.append({
            "rail_capacity_pax_per_train": float(cap),
            "rail_headway_min": float(headway),
            "lastmile_fleet_size": float(fleet),
            "mean_delta": mean,
            "ci_lower": lo,
            "ci_upper": hi,
            "n": n,
            "ci_straddles_zero": bool(np.isfinite(lo) and np.isfinite(hi) and lo <= 0.0 <= hi),
        })
    return pd.DataFrame(rows)


def _build_matrices(
    agg: pd.DataFrame,
    cap_level: float,
    headways: list[float],
    fleets: list[float],
) -> tuple[np.ndarray, np.ndarray]:
    """Build mean & sign-flip mask matrices for a single capacity panel."""
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


def _plot(agg: pd.DataFrame) -> None:
    _set_korean_font()

    headways = sorted({float(v) for v in agg["rail_headway_min"]}, reverse=True)
    fleets = sorted({float(v) for v in agg["lastmile_fleet_size"]})

    # Symmetric diverging norm centered at 0
    finite_means = agg["mean_delta"].to_numpy()
    finite_means = finite_means[np.isfinite(finite_means)]
    if finite_means.size == 0:
        vmax_abs = 1.0
    else:
        vmax_abs = float(np.max(np.abs(finite_means)))
        if vmax_abs == 0.0:
            vmax_abs = 1.0
    norm = TwoSlopeNorm(vmin=-vmax_abs, vcenter=0.0, vmax=vmax_abs)
    cmap = plt.get_cmap("RdBu_r")

    fig, axes = plt.subplots(1, 3, figsize=(15.0, 5.4), sharey=True)
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])

    im = None
    for ax, cap in zip(axes, CAP_LEVELS):
        mean_mat, flip_mat = _build_matrices(agg, float(cap), headways, fleets)
        im = ax.imshow(mean_mat, cmap=cmap, norm=norm, aspect="auto", origin="upper")

        ax.set_xticks(range(len(fleets)))
        ax.set_xticklabels([f"{int(f)}" for f in fleets])
        ax.set_yticks(range(len(headways)))
        ax.set_yticklabels([f"{h:g}" for h in headways])
        ax.set_xlabel("lastmile_fleet_size (대)")
        ax.set_title(f"rail_capacity = {cap} pax/train", fontsize=11)

        # Annotate cells with mean value + sign-flip cross
        for i in range(mean_mat.shape[0]):
            for j in range(mean_mat.shape[1]):
                val = mean_mat[i, j]
                if not np.isfinite(val):
                    ax.text(j, i, "n/a", ha="center", va="center", fontsize=8, color="grey")
                    continue
                # Choose text color for contrast against cell background
                rgba = cmap(norm(val))
                luminance = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
                txt_color = "white" if luminance < 0.5 else "black"
                ax.text(
                    j,
                    i,
                    f"{val:,.0f}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=txt_color,
                )
                if flip_mat[i, j]:
                    ax.text(
                        j,
                        i + 0.32,
                        "✕",  # ✕
                        ha="center",
                        va="center",
                        fontsize=14,
                        color="black",
                        fontweight="bold",
                    )

    axes[0].set_ylabel("rail_headway_min (분)")

    fig.suptitle(
        "Figure 6 — Phase 3 반사실 레버 스윕 "
        "(Δ penalized_makespan at p_fail_scale=1.5)",
        fontsize=13,
    )

    # Shared colorbar
    fig.subplots_adjust(right=0.90, top=0.88, bottom=0.12, wspace=0.08)
    cbar_ax = fig.add_axes([0.92, 0.14, 0.018, 0.72])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label("Δ penalized_makespan (분, bus − multi)", fontsize=10)

    # Footnote explaining the cross
    fig.text(
        0.5,
        0.02,
        "✕ 표시 = 평균 Δ의 95% paired-t CI가 0을 가로지르는 셀 (부호 반전 후보).",
        ha="center",
        fontsize=9,
        color="#333333",
    )

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _write_caption() -> None:
    caption = """# Figure 6 — Phase 3 반사실 레버 스윕 (헤드라인 그림)

**제목.** Phase 3 반사실 레버 스윕 — Δ penalized_makespan at p_fail_scale=1.5.

**패널 구성.** 본 그림은 Phase 3 반사실 그리드(3×3×3×3 = 81 셀, 셀당 R=15 페어드 CRN 반복)의 disruption 스트레스 수준 `p_fail_scale=1.5`에 대한 평균 Δ penalized_makespan(= bus − multi)을 3개 패널로 분할한 발산형(diverging) 히트맵이다. 패널은 `rail_capacity_pax_per_train ∈ {500, 1000, 2000}` 세 수준을 좌→우로 배치하고, 각 패널 내부에서 Y축은 `rail_headway_min (분) ∈ {15, 7.5, 3}`(상→하), X축은 `lastmile_fleet_size (대) ∈ {23, 50, 100}`(좌→우)이다. 셀 색상은 `RdBu_r` 컬러맵으로 0에서 발산하며, 청색(Δ<0)은 직행버스 우위, 적색(Δ>0)은 multimodal 우위를 나타낸다.

**헤드라인 해석.** 기저 (rail_headway=15분, lastmile=23, rail_capacity=500)에서는 Δ < 0 (직행버스 우위). 어느 셀에서 Δ ≥ 0 (multimodal 우위)으로 부호 반전이 일어나는가가 본 그림의 핵심이다. `✕` 마커는 95% paired-t CI가 0을 가로지르는 셀(부호 반전 후보)을 표시한다.

**핵심 수치 (TODO — 통합 에이전트가 `manuscript/tables/table6_lever_conditions_summary.json`에서 채울 것).** TODO: multi_dominant 셀 수, 가장 좁은 격차 셀의 (headway, fleet, capacity) 조합 및 평균 Δ, 부호 반전 후보 셀의 수를 본 캡션에 삽입.

**기타 주.** 사이드카 통계 (셀별 평균·95% CI·분류 라벨)는 `manuscript/tables/table6_lever_conditions.md`와 `manuscript/tables/table6_lever_conditions_summary.json` 참조. CI는 paired-t (df = R−1 = 14) 기반이며, 비유한값(±inf)은 평균·CI 계산 전 제거했다.
"""
    CAPTION_PATH.write_text(caption, encoding="utf-8")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Figure 6 (Phase 3 heatmap).")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to phase3_lever_sweep.csv (default: results/phase3_lever_sweep.csv).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    if not args.input.exists():
        print(
            f"ERROR: Phase 3 lever-sweep CSV not found at {args.input}. "
            "Run Phase 3 first (results/phase3_lever_sweep.csv).",
            file=sys.stderr,
        )
        return 2

    df = pd.read_csv(args.input)
    required = {
        "rail_headway_min",
        "lastmile_fleet_size",
        "rail_capacity_pax_per_train",
        "p_fail_scale",
        METRIC,
    }
    missing = required - set(df.columns)
    if missing:
        print(
            f"ERROR: Phase 3 CSV missing required columns: {sorted(missing)}",
            file=sys.stderr,
        )
        return 3

    agg = _aggregate_stress(df)
    _plot(agg)
    _write_caption()
    print(f"Wrote {FIG_PATH}")
    print(f"Wrote {CAPTION_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
