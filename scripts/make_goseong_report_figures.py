"""Generate Goseong report figures (figure1-3) from the pilot summary CSV.

Claim-disciplined: descriptive decision-support only. Replaces stale Jun-5 PNGs.
figure0 (pipeline concept diagram) is region-agnostic and left in place.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "results" / "realworld_pilot" / "pilot_full_summary.csv"
OUT_DIR = ROOT / "results" / "report_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Korean font
for cand in ("Malgun Gothic", "NanumGothic", "NanumSquare", "Gulim"):
    try:
        font_manager.findfont(cand, fallback_to_default=False)
        rcParams["font.family"] = cand
        break
    except Exception:
        continue
rcParams["axes.unicode_minus"] = False


def load() -> dict:
    """{(scenario_id, mode): {makespan, cr, censored, penalized}} for baseline policies."""
    g: dict = defaultdict(lambda: defaultdict(list))
    with open(SUMMARY, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["policy_id"] not in ("bus_only", "baseline_multimodal"):
                continue
            key = (r["scenario_id"], r["mode"])
            for col in ("mean_makespan", "mean_completion_rate",
                        "mean_censored_count", "mean_penalized_makespan"):
                try:
                    g[key][col].append(float(r[col]))
                except (TypeError, ValueError):
                    pass
    out = {}
    for key, d in g.items():
        out[key] = {col: (statistics.mean(v) if v else None) for col, v in d.items()}
    return out


def scenario_label(sc: str) -> str:
    return {
        "no_disruption": "정상",
        "goseong_access_origin_to_destination": "접근도로(A→D)",
        "goseong_access_origin_to_station": "접근도로(A→S)",
        "goseong_last_mile_station_to_destination": "라스트마일(R→D)",
        "goseong_rail_station_access": "역 접근도로",
        "goseong_random_capacity_reduction": "무작위 용량축소",
        "goseong_rail_capacity_reduction": "철도 용량축소",
        "goseong_rail_delay_mild": "철도지연(경)",
        "goseong_rail_delay": "철도지연(중)",
        "goseong_rail_delay_severe": "철도지연(중증)",
        "goseong_rail_combined_stress_mild": "복합스트레스(경)",
        "goseong_rail_combined_stress": "복합스트레스(중)",
        "goseong_rail_combined_stress_severe": "복합스트레스(중증)",
        "goseong_rail_unavailable": "철도사용불가",
        "goseong_combo_access_rail_capacity": "접근도로+철도용량",
        "goseong_spatial_assembly_egress": "집결지 공통구간",
        "goseong_critical_link_blockage": "핵심연결 차단",
        "goseong_random_blockage": "무작위 차단",
    }.get(sc, sc)


def ordered_scenarios(data: dict) -> list[str]:
    scs = sorted({sc for sc, _ in data})
    # put no_disruption first, collapses last
    head = [s for s in ("no_disruption",) if s in scs]
    tail_collapse = [s for s in scs if s in
                     ("goseong_critical_link_blockage", "goseong_random_blockage")]
    mid = [s for s in scs if s not in head and s not in tail_collapse]
    return head + sorted(mid) + sorted(tail_collapse)


def fig1_time_efficiency(data: dict) -> None:
    scs = ordered_scenarios(data)
    bus = [data.get((s, "bus_only"), {}).get("mean_makespan") for s in scs]
    mul = [data.get((s, "multimodal"), {}).get("mean_makespan") for s in scs]
    labels = [scenario_label(s) for s in scs]
    x = range(len(scs))
    w = 0.4
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.bar([i - w / 2 for i in x], [b if b else 0 for b in bus], w,
           label="버스 단독", color="#4C78A8")
    ax.bar([i + w / 2 for i in x], [m if m else 0 for m in mul], w,
           label="복합모드(레일+버스)", color="#F58518")
    for i, (b, m) in enumerate(zip(bus, mul)):
        if not b:
            ax.text(i - w / 2, 10, "붕괴", ha="center", fontsize=8, color="#B22222", rotation=90)
        if not m:
            ax.text(i + w / 2, 10, "붕괴", ha="center", fontsize=8, color="#B22222", rotation=90)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=9)
    ax.set_ylabel("평균 완료시간 (분)")
    ax.set_title("그림 1. 시나리오별 수송 방식 완료시간 비교 (기본 정책, 30시드 평균)")
    ax.legend()
    ax.set_ylim(0, 520)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "figure1_time_efficiency_summary.png", dpi=150)
    plt.close()


def fig2_undelivered_risk(data: dict) -> None:
    scs = ordered_scenarios(data)
    bus = [data.get((s, "bus_only"), {}).get("mean_completion_rate") or 0 for s in scs]
    mul = [data.get((s, "multimodal"), {}).get("mean_completion_rate") or 0 for s in scs]
    labels = [scenario_label(s) for s in scs]
    x = range(len(scs))
    w = 0.4
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.bar([i - w / 2 for i in x], bus, w, label="버스 단독", color="#4C78A8")
    ax.bar([i + w / 2 for i in x], mul, w, label="복합모드", color="#F58518")
    ax.axhline(1.0, color="#888", lw=0.8, ls="--")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=9)
    ax.set_ylabel("평균 완료율")
    ax.set_title("그림 2. 시나리오별 완료율 (미도착 위험 지표)")
    ax.legend(loc="lower left")
    ax.set_ylim(0, 1.08)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "figure2_undelivered_risk.png", dpi=150)
    plt.close()


def fig3_decision_lenses(data: dict) -> None:
    """delta = multimodal - bus makespan (min). negative => multimodal faster."""
    scs = ordered_scenarios(data)
    deltas = []
    labels = []
    for s in scs:
        b = data.get((s, "bus_only"), {}).get("mean_makespan")
        m = data.get((s, "multimodal"), {}).get("mean_makespan")
        if b and m:
            deltas.append(m - b)
            labels.append(scenario_label(s))
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#54A24B" if d < 0 else "#E45756" for d in deltas]
    y = range(len(deltas))
    ax.barh(list(y), deltas, color=colors)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9)
    ax.axvline(0, color="#333", lw=0.8)
    ax.set_xlabel("완료시간 차 (복합모드 - 버스, 분)  ·  음수 = 복합모드가 빠름")
    ax.set_title("그림 3. 판단 관점: 수송 방식별 완료시간 차이")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "figure3_decision_lens.png", dpi=150)
    plt.close()


def main() -> int:
    data = load()
    fig1_time_efficiency(data)
    fig2_undelivered_risk(data)
    fig3_decision_lenses(data)
    print(f"wrote 3 figures to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
