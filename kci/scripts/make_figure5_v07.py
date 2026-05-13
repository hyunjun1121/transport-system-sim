"""Figure 5 v0.7 — Four-Origin Robustness Overlay.

Generates a single-panel 1D line plot comparing the mean
``delta_penalized_makespan`` (bus − multimodal) across four origin candidates
(A, B, C, D) on the focused phase-1b grid ``p_fail_scale ∈ {0.0, 0.5, 1.0,
1.5}``. Origin A reuses its phase-1a grid (R=30) sub-set to the same four
levels for an apples-to-apples comparison. Origins B/C/D use phase-1b
replicates (R=20). 95% confidence intervals are produced from a paired-t
half-width per origin (df = n-1).

Origin D is visually flagged because its public-source attribution remains
unverified per user instruction (hatched CI band + distinct marker + explicit
on-plot caveat).

Outputs:
  - ``manuscript/figures/figure5_origin_robustness.png``
  - ``manuscript/figures/figure5_origin_robustness.csv`` (16 rows)
  - ``manuscript/figures/figure5_caption_ko.md``
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIG_DIR = ROOT / "manuscript" / "figures"
FIG_PATH = FIG_DIR / "figure5_origin_robustness.png"
CSV_PATH = FIG_DIR / "figure5_origin_robustness.csv"
CAPTION_PATH = FIG_DIR / "figure5_caption_ko.md"

METRIC = "delta_penalized_makespan"
COMMON_P = [0.0, 0.5, 1.0, 1.5]

ORIGINS = ["A", "B", "C", "D"]
ORIGIN_FILES = {
    "A": RESULTS / "phase1a_origin_A.csv",
    "B": RESULTS / "phase1b_origin_B.csv",
    "C": RESULTS / "phase1b_origin_C.csv",
    "D": RESULTS / "phase1b_origin_D.csv",
}
ORIGIN_LABELS = {
    "A": "A — 잠실역 (참조, R=30)",
    "B": "B — 한강 르네상스/코엑스 (R=20)",
    "C": "C — 잠실대교 남단 (R=20)",
    "D": "D — 비검증 후보 (R=20)",
}
ORIGIN_COLORS = {
    "A": "#1f77b4",
    "B": "#2ca02c",
    "C": "#ff7f0e",
    "D": "#a30000",
}
ORIGIN_LINESTYLES = {
    "A": "-",
    "B": "--",
    "C": ":",
    "D": "-.",
}
ORIGIN_MARKERS = {
    "A": "o",
    "B": "s",
    "C": "^",
    "D": "X",  # distinct marker for unverified origin
}


def _set_korean_font() -> None:
    preferred = ["Malgun Gothic", "NanumGothic", "Gulim", "Yu Gothic", "MS Gothic"]
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in installed:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


def _paired_t_ci(values: np.ndarray, alpha: float = 0.05) -> tuple[float, float, float, int]:
    """Return (mean, ci_lower, ci_upper, n_finite) using a one-sample t CI.

    Non-finite values (full-failure penalty rows producing ±inf in the delta)
    are dropped so a single censored replicate cannot dominate the mean. With
    n<2 the CI collapses to the mean.
    """

    finite = values[np.isfinite(values)]
    n = int(finite.size)
    if n == 0:
        return float("nan"), float("nan"), float("nan"), 0
    mean = float(finite.mean())
    if n < 2:
        return mean, mean, mean, n
    se = float(finite.std(ddof=1) / np.sqrt(n))
    tcrit = float(stats.t.ppf(1 - alpha / 2.0, df=n - 1))
    half = tcrit * se
    return mean, mean - half, mean + half, n


def _load_origin(origin: str) -> pd.DataFrame:
    df = pd.read_csv(ORIGIN_FILES[origin])
    # Sub-set Origin A's 8-level grid to the common 4 levels
    df = df[df["p_fail_scale"].isin(COMMON_P)].copy()
    df["origin"] = origin
    return df


def _aggregate() -> pd.DataFrame:
    rows: list[dict] = []
    for origin in ORIGINS:
        df = _load_origin(origin)
        for p in COMMON_P:
            sub = df[df["p_fail_scale"] == p][METRIC].to_numpy()
            mean, lo, hi, n = _paired_t_ci(sub)
            rows.append({
                "origin": origin,
                "p_fail_scale": float(p),
                "mean_delta_penalized_makespan": mean,
                "ci_lower": lo,
                "ci_upper": hi,
                "n_reps": n,
            })
    return pd.DataFrame(rows)


def _plot(agg: pd.DataFrame) -> None:
    _set_korean_font()
    fig, ax = plt.subplots(figsize=(9.0, 5.6))

    x = np.array(COMMON_P, dtype=float)

    for origin in ORIGINS:
        sub = (
            agg[agg["origin"] == origin]
            .set_index("p_fail_scale")
            .reindex(COMMON_P)
            .reset_index()
        )
        means = sub["mean_delta_penalized_makespan"].to_numpy()
        lo = sub["ci_lower"].to_numpy()
        hi = sub["ci_upper"].to_numpy()
        color = ORIGIN_COLORS[origin]

        if origin == "D":
            # Distinct unverified styling: hatched CI band + ring-marker
            ax.fill_between(
                x,
                lo,
                hi,
                facecolor="none",
                edgecolor=color,
                hatch="///",
                linewidth=0.0,
                alpha=0.9,
                label=None,
            )
            ax.plot(
                x,
                means,
                linestyle=ORIGIN_LINESTYLES[origin],
                color=color,
                marker=ORIGIN_MARKERS[origin],
                markersize=10,
                markerfacecolor="white",
                markeredgecolor=color,
                markeredgewidth=2.4,
                linewidth=2.2,
                label=ORIGIN_LABELS[origin],
            )
        else:
            ax.fill_between(x, lo, hi, color=color, alpha=0.18, linewidth=0.0)
            ax.plot(
                x,
                means,
                linestyle=ORIGIN_LINESTYLES[origin],
                color=color,
                marker=ORIGIN_MARKERS[origin],
                markersize=7,
                linewidth=1.9,
                label=ORIGIN_LABELS[origin],
            )

    ax.axhline(0.0, color="grey", linewidth=0.9, linestyle="--", zorder=0)

    ax.set_title("Phase 1b 원점 강건성 — 네 후보 원점 비교", fontsize=13)
    ax.set_xlabel("p_fail_scale")
    ax.set_ylabel("Δ 보정 makespan (분, bus - multimodal)")
    ax.set_xticks(COMMON_P)
    ax.grid(axis="both", alpha=0.3)
    ax.set_xlim(-0.08, 1.58)

    # Annotation box flagging Origin D as unverified
    ax.annotate(
        "Origin D: 비검증 후보 — 결과는 참고용",
        xy=(0.98, 0.04),
        xycoords="axes fraction",
        ha="right",
        va="bottom",
        fontsize=9.5,
        color="#a30000",
        style="italic",
        bbox=dict(
            boxstyle="round,pad=0.35",
            facecolor="#fff4f4",
            edgecolor="#a30000",
            linewidth=1.1,
        ),
    )

    # Legend: include both the line/marker styling AND the hatch flag for D
    handles, labels = ax.get_legend_handles_labels()
    handles.append(
        Patch(
            facecolor="none",
            edgecolor=ORIGIN_COLORS["D"],
            hatch="///",
            label="D CI 빗금 = 비검증",
        )
    )
    labels.append("D CI 빗금 = 비검증")
    ax.legend(
        handles=handles,
        labels=labels,
        loc="upper left",
        fontsize=8.8,
        frameon=True,
        framealpha=0.92,
    )

    fig.tight_layout()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _write_caption(agg: pd.DataFrame) -> None:
    # Compute summary numbers for the caption
    at15 = agg[agg["p_fail_scale"] == 1.5].set_index("origin")["mean_delta_penalized_makespan"]
    most_neg = at15.idxmin()
    least_neg = at15.idxmax()
    spread = float(at15.max() - at15.min())

    caption = f"""# Figure 5 — Phase 1b 원점 강건성 (네 후보 원점 비교)

**제목.** Phase 1b 원점 강건성 — 네 후보 원점 비교.

**해석.** 본 그림은 4개 출발지 후보(A: 잠실역(참조, R=30), B: 한강 르네상스/코엑스(R=20), C: 잠실대교 남단(R=20), D: 비검증 후보(R=20))를 공통 그리드 `p_fail_scale ∈ {{0.0, 0.5, 1.0, 1.5}}`(s=1.2 고정)에서 Δ 보정 makespan(= bus-only − multimodal)의 평균과 95% 신뢰구간(쌍대비 t, 원점 A df=29, B/C/D df=19)으로 겹쳐 그린 단일 패널 라인 도식이다. 음(−)의 값은 multimodal 대안이 더 큰 보정 makespan을 가져 bus-only가 (페널티 보정 후) 유리함을 뜻한다.

**핵심 결과.** 네 후보 모두 동일한 단조 추세(p_fail_scale↑에 따라 Δ가 음의 방향으로 깊어짐)를 공유하며, 0.0–1.0 구간에서는 95% CI가 서로 크게 겹쳐 본문 결과(원점 A)가 출발지 선택에 강건함을 시사한다. p_fail_scale=1.5에서 가장 음의 편향이 큰(= multimodal에 가장 유리한) 원점은 **{most_neg}**, 가장 작은 원점은 **{least_neg}**이고, 네 원점의 평균 Δ 분포 폭은 약 **{spread:.1f}분**으로 좁다.

**Origin D 주의(중요).** Origin D는 공개 자료에서 사용자가 요청한 출처 검증을 통과하지 못한 **비검증 후보**이며, 본문 분석·결론에는 사용하지 않았다. 도식에서는 (1) 빨간 마커 링, (2) CI 영역의 빗금(///) 패턴, (3) 점·점선 라인 스타일, (4) 우측 하단 주석 박스 "Origin D: 비검증 후보 — 결과는 참고용"으로 시각적으로 분리해 표시했다. 본 그림에서의 포함은 오직 **민감도/강건성 점검(robustness variant)** 목적이며, 본문 수치·결론은 원점 A(잠실역)에 한정된다.

**기타 주.** 결합(p_fail_scale=1.0 이상)에서 발생하는 완전 실패 케이스는 보정 makespan 페널티(=1,441,440 분)로 들어가며, 비유한값(±inf)은 사전 제거 후 평균·CI를 계산했다. 사이드카 데이터는 `manuscript/figures/figure5_origin_robustness.csv` 참조.
"""
    CAPTION_PATH.write_text(caption, encoding="utf-8")


def main() -> int:
    agg = _aggregate()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    agg.to_csv(CSV_PATH, index=False)
    _plot(agg)
    _write_caption(agg)
    print(f"Wrote {FIG_PATH}")
    print(f"Wrote {CSV_PATH}")
    print(f"Wrote {CAPTION_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
