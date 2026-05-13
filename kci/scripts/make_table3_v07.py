"""Build Table 3 v0.7 — Phase 2 single-mode parametric sweep."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "phase2_singlemode.csv"
OUT = ROOT / "manuscript" / "tables" / "table3_phase2_policy_pareto.md"


def mean_ci(x, alpha=0.05):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n == 0:
        return np.nan, np.nan, np.nan, 0
    m = x.mean()
    if n < 2:
        return m, np.nan, np.nan, n
    se = x.std(ddof=1) / np.sqrt(n)
    tcrit = stats.t.ppf(1 - alpha / 2, n - 1)
    return m, m - tcrit * se, m + tcrit * se, n


def fmt_num(v, digits=1):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "NA"
    return f"{v:,.{digits}f}"


def fmt_pct(v, digits=3):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "NA"
    return f"{v:.{digits}f}"


def main():
    df = pd.read_csv(SRC)
    grp_cols = ["bus_fleet_size", "bus_dispatch_interval_min", "p_fail_scale"]
    df = df.sort_values(["p_fail_scale", "bus_fleet_size", "bus_dispatch_interval_min"])

    rows = []
    for (fleet, dispatch, pfail), g in df.groupby(grp_cols, sort=False):
        bus_pm_mean = g["bus_penalized_makespan"].replace([np.inf, -np.inf], np.nan).mean()
        d_mean, d_lo, d_hi, n = mean_ci(g["delta_penalized_makespan"].values)
        bus_q90 = g["bus_arrival_q90_min"].replace([np.inf, -np.inf], np.nan).mean()
        bus_pcomp = g["bus_prob_completion_within_window"].replace([np.inf, -np.inf], np.nan).mean()
        rows.append({
            "bus_fleet_size": int(fleet),
            "dispatch_min": int(dispatch),
            "p_fail_scale": float(pfail),
            "bus_pm_mean": bus_pm_mean,
            "d_mean": d_mean,
            "d_lo": d_lo,
            "d_hi": d_hi,
            "bus_q90": bus_q90,
            "bus_pcomp": bus_pcomp,
            "n": n,
        })

    tbl = pd.DataFrame(rows)
    tbl = tbl.sort_values(["p_fail_scale", "bus_fleet_size", "dispatch_min"]).reset_index(drop=True)
    assert len(tbl) == 45, f"Expected 45 rows, got {len(tbl)}"

    # Footnote stats: baseline (fleet=23, dispatch=5) vs (fleet=80, dispatch=3) per p_fail level
    baseline = tbl[(tbl.bus_fleet_size == 23) & (tbl.dispatch_min == 5)]
    tuned = tbl[(tbl.bus_fleet_size == 80) & (tbl.dispatch_min == 3)]
    reduce_lines = []
    for pf in sorted(tbl.p_fail_scale.unique()):
        b = baseline[baseline.p_fail_scale == pf].bus_pm_mean.values[0]
        t = tuned[tuned.p_fail_scale == pf].bus_pm_mean.values[0]
        pct = (b - t) / b * 100.0 if np.isfinite(b) and b != 0 else np.nan
        reduce_lines.append((pf, b, t, pct))

    # Does tuning close the gap? Sign of d_mean for tuned cell per p_fail
    gap_lines = []
    for pf in sorted(tbl.p_fail_scale.unique()):
        t_row = tuned[tuned.p_fail_scale == pf].iloc[0]
        gap_lines.append((pf, t_row.d_mean, t_row.d_lo, t_row.d_hi))

    # Compose Markdown
    lines = []
    lines.append("**<표 3> Phase 2 단일수단 매개변수 스윕: bus.fleet_size × dispatch_interval × p_fail_scale (R = 20, paired-t df = 19)**")
    lines.append("(Phase 2 Single-Mode Parametric Sweep: bus fleet × dispatch interval × p_fail_scale)")
    lines.append("")
    lines.append("| `bus_fleet_size` | `dispatch_min` | `p_fail_scale` | bus_penalized_makespan (분, 평균) | Δ penalized_makespan [평균, 95% CI] | bus_q90 도착 (분, 평균) | bus_P(완료) (평균) |")
    lines.append("|---|---|---|---|---|---|---|")
    for _, r in tbl.iterrows():
        bus_pm = fmt_num(r.bus_pm_mean, 1)
        d_cell = f"{fmt_num(r.d_mean,1)} [{fmt_num(r.d_lo,1)}, {fmt_num(r.d_hi,1)}]"
        q90 = fmt_num(r.bus_q90, 1)
        pcomp = fmt_pct(r.bus_pcomp, 3)
        lines.append(f"| {int(r.bus_fleet_size)} | {int(r.dispatch_min)} | {r.p_fail_scale:.1f} | {bus_pm} | {d_cell} | {q90} | {pcomp} |")

    lines.append("")
    lines.append("**각주 (Notes):**")
    lines.append("- Δ 정의: `Δ = bus_only − multimodal` (코드 `_safe_delta` 정의; 음수 = 직행버스 우위, 양수 = 멀티모달 우위).")
    lines.append("- Source: `results/phase2_singlemode.csv`, R = 20 paired CRN (공통 난수), paired-t df = 19, 95% CI = mean ± t_{0.975,19} · SE.")
    lines.append("- 단위: penalized_makespan 및 q90 도착시간은 분(min), P(완료)는 [0,1] 비율.")

    obs_parts = []
    for pf, b, t, pct in reduce_lines:
        obs_parts.append(f"p_fail={pf:.1f}에서 {pct:.1f}% 감소 ({b:,.1f}분 → {t:,.1f}분)")
    lines.append(
        "- **핵심 관찰 — 단일수단 fleet/dispatch 튜닝의 robustness gain**: baseline (fleet=23, dispatch=5) 대비 fleet=80 + dispatch=3에서 bus_penalized_makespan이 "
        + "; ".join(obs_parts) + "."
    )

    # Gap closing analysis
    closed = []
    for pf, dm, dlo, dhi in gap_lines:
        sign = "직행버스 우위" if dm < 0 else "멀티모달 우위"
        ci_excludes_zero = (dlo > 0) or (dhi < 0)
        closed.append((pf, dm, dlo, dhi, sign, ci_excludes_zero))
    gap_str = "; ".join(
        f"p_fail={pf:.1f}: Δ={dm:,.1f} 분 [{dlo:,.1f}, {dhi:,.1f}] ({sign}, 95% CI {'0 제외' if excl else '0 포함'})"
        for pf, dm, dlo, dhi, sign, excl in closed
    )
    # Determine overall verdict
    all_bus_dominates = all(dhi < 0 for _, _, _, dhi, _, _ in closed)
    all_multi_dominates = all(dlo > 0 for _, _, dlo, _, _, _ in closed)
    if all_bus_dominates:
        verdict = "결론: Phase 2 단일수단 튜닝 (fleet=80, dispatch=3)으로 모든 p_fail 수준에서 멀티모달 대비 직행버스가 우위 (CI 0 제외) — multi-bus 격차가 해소(closure)됨."
    elif all_multi_dominates:
        verdict = "결론: 튜닝 후에도 모든 p_fail 수준에서 멀티모달이 우위 (CI 0 제외) — Phase 2 단일수단 튜닝만으로는 multi-bus 격차를 좁히지 못함 (refute)."
    else:
        verdict = "결론: 일부 p_fail 수준에서만 격차 해소가 관찰되며, 단일수단 튜닝의 효과는 신뢰성(p_fail) 의존적임 — 부분적 확인(partial confirm)."
    lines.append(f"- **격차 해소 검정 (Confirm/Refute)**: 가장 공격적 튜닝셀(fleet=80, dispatch=3)의 Δ는 {gap_str}. {verdict}")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} ({len(tbl)} rows)")
    print("\n--- key stats ---")
    for pf, b, t, pct in reduce_lines:
        print(f"p_fail={pf}: baseline bus_pm={b:.2f}, tuned bus_pm={t:.2f}, reduction={pct:.2f}%")
    print("\n--- gap stats (tuned cell) ---")
    for pf, dm, dlo, dhi, sign, excl in closed:
        print(f"p_fail={pf}: delta_pm mean={dm:.2f} CI=[{dlo:.2f},{dhi:.2f}] {sign} CI_excludes_zero={excl}")


if __name__ == "__main__":
    main()
