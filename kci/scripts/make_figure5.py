"""Generate Figure 5: Origin robustness — Δ penalized_makespan by origin candidate.

Compares the four candidate origins (A reference + B, C, D variants) across the
common 2×3 grid (s∈{1.0,1.5} × p∈{0.0,1.0,2.0}). Origin D is visually flagged
because its public-source attribution remains unverified per user instruction.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIG_DIR = ROOT / "manuscript" / "figures"
FIG_PATH = FIG_DIR / "figure5_origin_robustness.png"
CAPTION_PATH = FIG_DIR / "figure5_caption_ko.md"

ORIGINS = ["A", "B", "C", "D"]
ORIGIN_LABELS = {
    "A": "A — 잠실역 (reference, R=10)",
    "B": "B — 한강 르네상스 코엑스 (R=5)",
    "C": "C — 잠실대교 남단 (R=5)",
    "D": "D — 출처 미확인 가정",
}
ORIGIN_COLORS = {
    "A": "#1f77b4",
    "B": "#2ca02c",
    "C": "#ff7f0e",
    "D": "#d62728",  # red border + paler face below
}
COMMON_S = [1.0, 1.5]
COMMON_P = [0.0, 1.0, 2.0]
METRIC = "delta_penalized_makespan"


def _set_korean_font() -> None:
    """Pick the first installed Korean-capable font for matplotlib labels."""

    preferred = ["Malgun Gothic", "NanumGothic", "Gulim", "Yu Gothic", "MS Gothic"]
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in installed:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


def _mean_ci(values: np.ndarray) -> tuple[float, float]:
    """Return (mean, half-width of 95% CI via t-approx with normal fallback).

    For small samples (n<2) the CI half-width collapses to 0. Inf/-Inf values
    (full failure cases) are dropped before aggregation so a single censored
    replicate cannot dominate the mean — robustness against the multimodal
    delta distribution.
    """

    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return float("nan"), 0.0
    mean = float(finite.mean())
    if finite.size < 2:
        return mean, 0.0
    std_err = float(finite.std(ddof=1) / np.sqrt(finite.size))
    # 95% normal approx (n is small but consistent with reporting in main text)
    return mean, 1.96 * std_err


def _load() -> dict[str, pd.DataFrame]:
    return {
        o: pd.read_csv(RESULTS / f"phase1_origin_{o}.csv") for o in ORIGINS
    }


def _aggregate(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for origin, df in frames.items():
        mask = df["s"].isin(COMMON_S) & df["p_fail_scale"].isin(COMMON_P)
        sub = df.loc[mask, ["s", "p_fail_scale", METRIC]]
        for (s, p), grp in sub.groupby(["s", "p_fail_scale"]):
            mean, ci = _mean_ci(grp[METRIC].to_numpy())
            rows.append({
                "origin": origin,
                "s": float(s),
                "p_fail_scale": float(p),
                "mean": mean,
                "ci95": ci,
                "n": int(np.isfinite(grp[METRIC].to_numpy()).sum()),
            })
    return pd.DataFrame(rows)


def _plot(agg: pd.DataFrame) -> None:
    _set_korean_font()
    fig, axes = plt.subplots(1, len(COMMON_S), figsize=(11.5, 5.0), sharey=True)

    bar_w = 0.18
    x = np.arange(len(COMMON_P))

    for ax, s in zip(axes, COMMON_S):
        for j, origin in enumerate(ORIGINS):
            slice_ = (
                agg[(agg["origin"] == origin) & (agg["s"] == s)]
                .set_index("p_fail_scale")
                .reindex(COMMON_P)
            )
            means = slice_["mean"].to_numpy()
            errs = slice_["ci95"].to_numpy()
            offset = (j - (len(ORIGINS) - 1) / 2) * bar_w
            color = ORIGIN_COLORS[origin]
            if origin == "D":
                # paler face + red edge + hatch to flag unverified origin
                bars = ax.bar(
                    x + offset,
                    means,
                    width=bar_w,
                    yerr=errs,
                    capsize=3,
                    color="#f4b6b8",
                    edgecolor="#a30000",
                    linewidth=1.6,
                    hatch="///",
                    label=ORIGIN_LABELS[origin] if s == COMMON_S[0] else None,
                )
            else:
                ax.bar(
                    x + offset,
                    means,
                    width=bar_w,
                    yerr=errs,
                    capsize=3,
                    color=color,
                    edgecolor="black",
                    linewidth=0.6,
                    label=ORIGIN_LABELS[origin] if s == COMMON_S[0] else None,
                )

        ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
        ax.set_xticks(x)
        ax.set_xticklabels([f"p = {p}" for p in COMMON_P])
        ax.set_title(f"s = {s}")
        ax.set_xlabel("p_fail_scale")
        ax.grid(axis="y", alpha=0.3)

    axes[0].set_ylabel("Δ penalized_makespan (분, bus - multi)")

    # Build legend manually so D's styling is reflected
    handles = [
        Patch(facecolor=ORIGIN_COLORS["A"], edgecolor="black", label=ORIGIN_LABELS["A"]),
        Patch(facecolor=ORIGIN_COLORS["B"], edgecolor="black", label=ORIGIN_LABELS["B"]),
        Patch(facecolor=ORIGIN_COLORS["C"], edgecolor="black", label=ORIGIN_LABELS["C"]),
        Patch(facecolor="#f4b6b8", edgecolor="#a30000", hatch="///", linewidth=1.6,
              label=ORIGIN_LABELS["D"]),
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.06),
        ncol=4,
        frameon=False,
        fontsize=8.5,
    )

    fig.suptitle(
        "Origin robustness — Δ penalized_makespan by origin candidate",
        fontsize=13,
        y=0.98,
    )

    footnote = (
        "Origin D (잠실종합운동장): public-source unverified per user instruction; "
        "included as a robustness variant only."
    )
    fig.text(
        0.5,
        0.005,
        footnote,
        ha="center",
        va="bottom",
        fontsize=8,
        color="#a30000",
        style="italic",
    )

    fig.tight_layout(rect=(0, 0.16, 1, 0.94))
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _write_caption() -> None:
    caption = """# Figure 5 — Origin robustness (Δ penalized_makespan)

**제목.** Origin robustness — Δ penalized_makespan by origin candidate.

**해석.** 본 그림은 출발지 후보 4종(A: 잠실역 — 본문 기준, R=10; B: 한강 르네상스/코엑스, R=5; C: 잠실대교 남단, R=5; D: 잠실종합운동장, R=5)에 대해 공통 그리드 셀(s∈{1.0, 1.5} × p∈{0.0, 1.0, 2.0})에서의 Δ penalized_makespan 평균과 95% 신뢰구간(정규 근사)을 비교한다. 동일 셀에서 네 후보가 거의 같은 부호와 크기를 보이면, 본문 결과가 출발지 선택에 강건함을 시사한다.

**Origin D 주의(중요).** Origin D(잠실종합운동장)는 공개 자료에서 사용자가 요청한 출처(연구계획 부속자료)가 확인되지 않은 가정치이며, 본문 분석에는 사용하지 않았다. 그림에서는 빨간 테두리·해치(///)·연한 채움 색으로 시각적으로 분리해 표시했으며, 범례 또한 "D — 출처 미확인 가정"으로 표기한다. 본 그림에서의 포함은 오직 **민감도/강건성 점검(robustness variant)** 목적이며, 본문 수치·결론은 A(잠실역)에 한정된다.

**기타 주.** Δ = (bus-only) − (multi-modal). 음(−)의 값은 multi-modal 대안이 더 큰 penalized_makespan을 보임을 뜻한다. p=1.0 이상에서 발생하는 완전 실패(failure) 케이스는 penalized_makespan 페널티(=1,441,440 분)로 들어가며, 본 집계에서 비유한값(±inf)은 사전 제거 후 평균·CI를 계산했다.
"""
    CAPTION_PATH.write_text(caption, encoding="utf-8")


def main() -> int:
    frames = _load()
    agg = _aggregate(frames)
    # Persist aggregate alongside figure for reproducibility / audit trail
    agg.to_csv(FIG_DIR / "figure5_origin_robustness.csv", index=False)
    _plot(agg)
    _write_caption()
    print(f"Wrote {FIG_PATH}")
    print(f"Wrote {CAPTION_PATH}")
    print(f"Wrote {FIG_DIR / 'figure5_origin_robustness.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
