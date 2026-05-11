#!/usr/bin/env python
"""Generate report-specific figures from experiment outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
FIGURE_DIR = RESULTS_DIR / "report_figures"

BUS_COLOR = "#24476b"
MULTI_COLOR = "#5f8f3f"
RISK_COLOR = "#b0413e"
NEUTRAL_COLOR = "#e9eef3"
TEXT_COLOR = "#1f2933"


def main() -> None:
    """Create all deterministic figures used by the narrative report."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    phase1 = pd.read_csv(RESULTS_DIR / "phase1_summary.csv")

    _setup_style()
    _plot_pipeline_overview()
    _plot_time_efficiency_summary(phase1)
    _plot_undelivered_risk(phase1)
    _plot_decision_lens()


def _setup_style() -> None:
    """Use a Korean-capable font when available and set a quiet report style."""
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    font = "Malgun Gothic" if "Malgun Gothic" in available_fonts else "DejaVu Sans"
    plt.rcParams.update(
        {
            "font.family": font,
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#c7d0d9",
            "axes.labelcolor": TEXT_COLOR,
            "xtick.color": TEXT_COLOR,
            "ytick.color": TEXT_COLOR,
            "text.color": TEXT_COLOR,
        }
    )


STAGE_COLOR = "#24476b"
STAGE_ALT_COLOR = "#5f8f3f"
STAGE_AUX_COLOR = "#b0413e"
UNCERTAINTY_COLOR = "#f3e8d2"


def _plot_pipeline_overview() -> None:
    """Render the implementation pipeline that matches the current design.

    The diagram lists the actual data sources, libraries, and analysis steps
    documented in the report's "구현 기술 스택 및 시뮬레이션 설계" section.
    """

    fig, ax = plt.subplots(figsize=(13.2, 6.6))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.text(
        0.5,
        0.955,
        "위기상황 지역 인력 이동 시뮬레이션 구현 파이프라인",
        ha="center",
        va="center",
        fontsize=17,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.905,
        "공개 지도 자료를 추출하여 그래프로 변환하고, 이산사건 시뮬레이션과 민감도 분석을 거쳐 검토용 산출물을 만든다.",
        ha="center",
        va="center",
        fontsize=10.5,
        color="#516170",
    )

    stages = [
        (
            "입력 자료",
            STAGE_COLOR,
            [
                "OpenStreetMap (Overpass API)",
                "KTDB GTFS · 9호선 (선택)",
                "시범 권역 YAML",
            ],
        ),
        (
            "네트워크 구축",
            STAGE_COLOR,
            [
                "NetworkX MultiDiGraph",
                "GraphML 캐시",
                "13,268 노드 / 28,947 간선",
            ],
        ),
        (
            "시뮬레이션 엔진",
            STAGE_ALT_COLOR,
            [
                "SimPy 이산사건",
                "BPR α=0.15, β=4",
                "Bernoulli 도로 장애",
                "LogNormal 지각",
                "공통난수 시드 페어링",
            ],
        ),
        (
            "분석 · 검증",
            STAGE_AUX_COLOR,
            [
                "SALib Morris 민감도",
                "OSRM 캐시 벤치마크 (선택)",
                "접근성 손실 진단",
            ],
        ),
        (
            "산출물",
            STAGE_COLOR,
            [
                "pandas KPI 표 (CSV)",
                "matplotlib · seaborn 그림",
                "python-docx 보고서",
            ],
        ),
    ]

    n = len(stages)
    margin_x = 0.035
    gap = 0.014
    box_top = 0.78
    box_bottom = 0.28
    box_h = box_top - box_bottom
    total_w = 1 - 2 * margin_x - (n - 1) * gap
    box_w = total_w / n

    for i, (title, color, items) in enumerate(stages):
        x = margin_x + i * (box_w + gap)
        _rounded_box(ax, x, box_bottom, box_w, box_h, color, alpha=1.0)
        ax.text(
            x + box_w / 2,
            box_top - 0.04,
            title,
            ha="center",
            va="center",
            fontsize=12.5,
            fontweight="bold",
            color="white",
        )
        line_y = box_top - 0.085
        line_step = (box_h - 0.11) / max(len(items), 1)
        for item in items:
            ax.text(
                x + box_w / 2,
                line_y,
                item,
                ha="center",
                va="top",
                fontsize=10,
                color="white",
            )
            line_y -= line_step

        if i < n - 1:
            arrow_x = x + box_w + gap / 2
            ax.annotate(
                "",
                xy=(arrow_x + 0.006, (box_top + box_bottom) / 2),
                xytext=(arrow_x - 0.006, (box_top + box_bottom) / 2),
                arrowprops=dict(arrowstyle="-|>", color="#516170", lw=1.4),
            )

    _rounded_box(ax, margin_x, 0.10, 1 - 2 * margin_x, 0.13, UNCERTAINTY_COLOR, alpha=1.0)
    ax.text(
        margin_x + 0.015,
        0.195,
        "불확실성 입력",
        ha="left",
        va="center",
        fontsize=11.5,
        fontweight="bold",
        color="#8a5a1e",
    )
    uncertainty_items = [
        "집결 지연 (LogNormal μ=2.0, σ∈{0.3, 0.5, 0.7, 1.0})",
        "혼잡 척도 5수준 (0.8~2.0)",
        "도로 장애 확률 7수준 (×0.0~3.0)",
        "장애 모드: 차단 / 용량 저하",
        "환승 처리 시간",
    ]
    item_x = margin_x + 0.14
    item_w = (1 - 2 * margin_x - 0.14) / len(uncertainty_items)
    for i, item in enumerate(uncertainty_items):
        ax.text(
            item_x + i * item_w + item_w / 2,
            0.135,
            item,
            ha="center",
            va="center",
            fontsize=9.5,
            color="#5a4214",
        )

    ax.text(
        0.5,
        0.035,
        "현재 산출물은 추상 네트워크와 시범 캐시에서 나온 조건부 결과로, 보정된 실제 지역 성과나 운영 지침이 아니다.",
        ha="center",
        va="center",
        fontsize=9.5,
        color="#7a8794",
        fontstyle="italic",
    )

    fig.savefig(FIGURE_DIR / "figure0_pipeline_overview.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def _plot_time_efficiency_summary(phase1: pd.DataFrame) -> None:
    """Show the headline trade-off under the matched-redundancy setting."""
    subset = phase1[
        (phase1["network_variant"] == "matched_redundancy")
        & (phase1["failure_mode"] == "capacity_reduction")
    ]
    if subset.empty:
        subset = phase1

    values = {
        "bus_time": subset["bus_makespan_mean"].mean(),
        "multi_time": subset["multi_makespan_mean"].mean(),
        "bus_eff": subset["bus_passengers_per_total_service_minute_mean"].mean(),
        "multi_eff": subset["multi_passengers_per_total_service_minute_mean"].mean(),
    }

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))

    axes[0].bar(
        ["버스 단독", "복합 수송"],
        [values["bus_time"], values["multi_time"]],
        color=[BUS_COLOR, MULTI_COLOR],
        width=0.55,
    )
    axes[0].set_title("평균 완료시간(분)", fontsize=14, fontweight="bold", pad=12)
    axes[0].grid(axis="y", alpha=0.25)
    _annotate_bars(axes[0], suffix="분", decimals=0)

    axes[1].bar(
        ["버스 단독", "복합 수송"],
        [values["bus_eff"], values["multi_eff"]],
        color=[BUS_COLOR, MULTI_COLOR],
        width=0.55,
    )
    axes[1].set_title("자원 효율(인원/수단 운행분)", fontsize=14, fontweight="bold", pad=12)
    axes[1].grid(axis="y", alpha=0.25)
    _annotate_bars(axes[1], suffix="", decimals=2)

    fig.suptitle("신속성과 자원 효율은 서로 다른 판단을 요구한다", fontsize=16, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(FIGURE_DIR / "figure1_time_efficiency_summary.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def _plot_undelivered_risk(phase1: pd.DataFrame) -> None:
    """Plot undelivered personnel as disruption severity grows."""
    subset = phase1[
        (phase1["network_variant"] == "baseline")
        & (phase1["failure_mode"] == "blocked")
    ]
    if subset.empty:
        subset = phase1[phase1["failure_mode"] == "blocked"]

    grouped = (
        subset.groupby("p_fail_scale", as_index=False)[
            ["bus_censored_count_mean", "multi_censored_count_mean"]
        ]
        .mean()
        .sort_values("p_fail_scale")
    )

    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    ax.plot(
        grouped["p_fail_scale"],
        grouped["bus_censored_count_mean"],
        marker="o",
        linewidth=2.5,
        color=BUS_COLOR,
        label="버스 단독",
    )
    ax.plot(
        grouped["p_fail_scale"],
        grouped["multi_censored_count_mean"],
        marker="s",
        linewidth=2.5,
        color=RISK_COLOR,
        label="복합 수송",
    )

    ax.set_title("장애가 커질 때 목적지에 도착하지 못한 인원", fontsize=15, fontweight="bold", pad=12)
    ax.set_xlabel("장애 강도 가정")
    ax.set_ylabel("평균 인원")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "figure2_undelivered_risk.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def _plot_decision_lens() -> None:
    """Create a compact executive interpretation matrix."""
    fig, ax = plt.subplots(figsize=(10.8, 5.2))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.text(
        0.5,
        0.94,
        "의사결정 관점에서 본 두 대안",
        ha="center",
        va="center",
        fontsize=17,
        fontweight="bold",
    )

    columns = [
        ("신속성", "버스 단독 우세"),
        ("안정성", "도로 연결성이 핵심"),
        ("자원 효율", "복합 수송 장점 존재"),
    ]
    rows = [
        ("버스 단독", BUS_COLOR, ["약 30분 빠른 경향", "도로 장애에 직접 노출", "차량 운행 부담 큼"]),
        ("복합 수송", MULTI_COLOR, ["환승·대기 시간 발생", "접근·마지막 구간 취약", "철도 활용 시 효율 개선"]),
    ]

    left_margin = 0.07
    top = 0.78
    row_h = 0.23
    label_w = 0.18
    col_w = (0.88 - label_w) / 3

    for i, (title, subtitle) in enumerate(columns):
        x = left_margin + label_w + i * col_w
        ax.text(x + col_w / 2, top + 0.08, title, ha="center", fontsize=13, fontweight="bold")
        ax.text(x + col_w / 2, top + 0.035, subtitle, ha="center", fontsize=10, color="#516170")

    for r, (row_name, color, texts) in enumerate(rows):
        y = top - (r + 1) * row_h
        _rounded_box(ax, left_margin, y, label_w - 0.015, row_h - 0.035, color, alpha=1.0)
        ax.text(
            left_margin + (label_w - 0.015) / 2,
            y + (row_h - 0.035) / 2,
            row_name,
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color="white",
        )
        for c, text in enumerate(texts):
            x = left_margin + label_w + c * col_w
            _rounded_box(ax, x, y, col_w - 0.018, row_h - 0.035, NEUTRAL_COLOR, alpha=1.0)
            ax.text(
                x + (col_w - 0.018) / 2,
                y + (row_h - 0.035) / 2,
                text,
                ha="center",
                va="center",
                fontsize=11.5,
                wrap=True,
            )

    ax.text(
        0.5,
        0.1,
        "핵심은 수단 선택 자체보다 접근 도로, 마지막 도로 구간, 환승 처리 능력을 함께 보는 것이다.",
        ha="center",
        va="center",
        fontsize=11.5,
        color="#516170",
    )
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "figure3_decision_lens.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def _rounded_box(ax, x: float, y: float, w: float, h: float, color: str, alpha: float) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        linewidth=0,
        facecolor=color,
        alpha=alpha,
    )
    ax.add_patch(box)


def _annotate_bars(ax, *, suffix: str, decimals: int) -> None:
    for patch in ax.patches:
        value = patch.get_height()
        if decimals == 0:
            label = f"{value:.0f}{suffix}"
        else:
            label = f"{value:.{decimals}f}{suffix}"
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            value,
            label,
            ha="center",
            va="bottom",
            fontsize=10.5,
            fontweight="bold",
        )


if __name__ == "__main__":
    main()
