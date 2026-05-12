"""Build the 5 KCI manuscript tables in markdown.

Output: kci/manuscript/tables/table{1..5}_*.md
"""

import pandas as pd
import numpy as np
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "manuscript" / "tables"
OUT.mkdir(parents=True, exist_ok=True)


def fmt_num(x):
    """Format to 2-3 sig figs. Scientific if very large / small."""
    if x is None:
        return "-"
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return "-"
    ax = abs(x)
    if ax == 0:
        return "0"
    if ax >= 1e4 or ax < 1e-2:
        return f"{x:.2e}"
    if ax >= 100:
        return f"{x:.1f}"
    if ax >= 10:
        return f"{x:.2f}"
    if ax >= 1:
        return f"{x:.3f}"
    return f"{x:.3g}"


# =====================================================================
# TABLE 1: DoE 실험 설계 격자
# =====================================================================
def build_table1():
    lines = []
    lines.append("**<표 1> 실험 설계 격자 (Experimental Design Grid)**")
    lines.append("")
    lines.append("| 단계 (Phase) | 요인 (Factor) | 수준 (Levels) | 수준 수 (k) | 셀 수 (Cells) | R per cell | 총 실행 (Total runs) |")
    lines.append("|---|---|---|---|---|---|---|")
    lines.append("| Phase 1 (main) | s (수요 배수) | 0.8, 1.0, 1.2, 1.5, 2.0 | 5 | - | - | - |")
    lines.append("| Phase 1 (main) | p_fail_scale | 0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0 | 7 | 35 | 10¹ | 350 |")
    lines.append("| Phase 2 (main) | σ (수요 불확실성) | 0.3, 0.5, 0.7, 1.0 | 4 | - | - | - |")
    lines.append("| Phase 2 (main) | 정책 (policy) | STRICT, GRACE_W{15,30,60}_T{0.8,0.9} | 7 | 28 | 10¹ | 280 |")
    lines.append("| 강건성 (Robustness) | 원점 (origin) × s × p | B,C,D × {1.0,1.5} × {0.0,1.0,2.0} | 18 (6 cells × 3 origins) | 18 | 5¹ | 90 |")
    lines.append("| Morris 민감도 | 파라미터 수 (k) | 14 | 14 | - | - | - |")
    lines.append("| Morris 민감도 | 궤적 × 수준 (Trajectories × Levels) | 50 × 4¹ | - | - | - | 750¹ |")
    lines.append("")
    lines.append("*주.* ¹ 계획된 R=30 → 실행 R=10 (메인 실험), R=5 (강건성 실험); Morris 궤적 200 → 50으로 축소. 축소 사유: 송파 코리도어 약 18,000(18k) 노드 규모로 인한 단위 시뮬레이션 실행 시간 제약. Phase 1 메인은 5×7=35 셀 × 10 = 350개, Phase 2 메인은 4×7=28 셀 × 10 = 280개, 강건성은 3개 원점 × 2×3=6 셀 × 5 = 90개, Morris는 (k+1)×T = (14+1)×50 = 750 표본/구성을 평가. s = 수요 배수, p_fail_scale = 마지막-마일 접근 실패 확률 스케일, σ = 수요 도착 변동성, R = 셀당 반복 수.")
    (OUT / "table1_doe_design.md").write_text("\n".join(lines), encoding="utf-8")
    return len(lines)


# =====================================================================
# TABLE 2: Phase 1 Origin-A means + 95% paired CI
# =====================================================================
def build_table2():
    ci = pd.read_csv(REPO / "results" / "phase1_ci.csv")
    ci = ci.sort_values(["s", "p_fail_scale"]).reset_index(drop=True)

    lines = []
    lines.append("**<표 2> Phase 1 원점-A 페널라이즈드 메이크스팬 차이의 평균 및 95% 페어드 신뢰구간**")
    lines.append("(Phase 1 Origin-A Mean Δ Penalized Makespan with 95 % Paired CI)")
    lines.append("")
    lines.append("| s | p_fail_scale | Mean Δ (분) | 95% CI 하한 | 95% CI 상한 | 통계적 유의성 (Significance) |")
    lines.append("|---|---|---|---|---|---|")
    breakeven = 0
    bus_better = 0
    multi_better = 0
    for _, r in ci.iterrows():
        lo, hi, m = r["ci_lower"], r["ci_upper"], r["mean"]
        if hi < 0:
            sig = "버스-단독 우위 (Bus-only better)"
            bus_better += 1
        elif lo > 0:
            sig = "다중-수단 우위 (Multimodal better)"
            multi_better += 1
        else:
            sig = "구분 불가 (Indistinguishable)"
            breakeven += 1
        lines.append(f"| {r['s']:.1f} | {r['p_fail_scale']:.2f} | {fmt_num(m)} | {fmt_num(lo)} | {fmt_num(hi)} | {sig} |")
    lines.append("")
    lines.append("*주.* Δ = 버스-단독 페널라이즈드 메이크스팬 − 다중-수단 페널라이즈드 메이크스팬 (분). 음수 = 버스-단독이 더 빠름. 95% CI는 셀당 R=10의 페어드(동일 seed) 표본에 대한 t-기반 구간. p_fail_scale = 0 셀은 결정론적 (변동성 없음) 시나리오로 신뢰구간 폭이 0에 수렴함. 페널티는 censored 인원에 대해 미완료 거리/속도 기반으로 부과 (Phase 0 정의).")
    (OUT / "table2_phase1_means_ci.md").write_text("\n".join(lines), encoding="utf-8")
    return {"rows": len(ci), "breakeven": breakeven, "bus_better": bus_better, "multi_better": multi_better}


# =====================================================================
# TABLE 3: Phase 2 policy trade-off
# =====================================================================
def build_table3():
    p2 = pd.read_csv(REPO / "results" / "phase2_origin_A.csv")
    agg = p2.groupby(["sigma", "policy"]).agg(
        mean_dpm=("delta_penalized_makespan", "mean"),
        sd_dpm=("delta_penalized_makespan", "std"),
        mean_dre=("delta_resource_eff", "mean"),
        sd_dre=("delta_resource_eff", "std"),
        n=("delta_penalized_makespan", "size"),
    ).reset_index().sort_values(["sigma", "policy"])

    lines = []
    lines.append("**<표 3> Phase 2 정책 트레이드오프: σ × 정책별 Δ 페널라이즈드 메이크스팬 및 Δ 자원효율**")
    lines.append("(Phase 2 Policy Trade-off: Mean Δ Penalized Makespan and Δ Resource Efficiency by σ × Policy)")
    lines.append("")
    lines.append("| σ | 정책 (Policy) | Mean Δ 페널라이즈드 메이크스팬 (분) | SD | Mean Δ 자원효율 | SD | n |")
    lines.append("|---|---|---|---|---|---|---|")
    for _, r in agg.iterrows():
        lines.append(f"| {r['sigma']:.1f} | {r['policy']} | {fmt_num(r['mean_dpm'])} | {fmt_num(r['sd_dpm'])} | {fmt_num(r['mean_dre'])} | {fmt_num(r['sd_dre'])} | {int(r['n'])} |")
    lines.append("")
    lines.append("*주.* Phase 2는 s=1.2, p_fail_scale=1.0의 단일 셀에서 σ × 정책 (7수준)을 R=10회 반복. Δ 페널라이즈드 메이크스팬 = 버스-단독 − 다중-수단 (분, 음수 = 버스-단독 우위). Δ 자원효율 = 다중-수단 자원효율 − 버스-단독 자원효율 (양수 = 다중-수단 우위). 정책 표기 GRACE_W{w}_T{θ}: 그레이스 윈도우 w분 + 임계치 θ. σ = 도착 변동성 (포아송 분산 배수). ±4.6×10⁵ 수준의 큰 표준편차는 censored 페널티가 결과를 지배하는 셀에서 관찰됨.")
    (OUT / "table3_phase2_policy_pareto.md").write_text("\n".join(lines), encoding="utf-8")
    return len(agg)


# =====================================================================
# TABLE 4: Origin robustness (B/C/D vs A on common cells)
# =====================================================================
def build_table4():
    common_s = [1.0, 1.5]
    common_p = [0.0, 1.0, 2.0]
    origin_data = {}
    for o in ['A', 'B', 'C', 'D']:
        df_o = pd.read_csv(REPO / "results" / f"phase1_origin_{o}.csv")
        sub = df_o[df_o['s'].isin(common_s) & df_o['p_fail_scale'].isin(common_p)]
        origin_data[o] = sub.groupby(['s', 'p_fail_scale']).agg(
            mean_dpm=('delta_penalized_makespan', 'mean'),
            n=('delta_penalized_makespan', 'size'),
        ).reset_index()

    rows = []
    for s_val in common_s:
        for p_val in common_p:
            row = {"s": s_val, "p_fail_scale": p_val}
            for o in ['A', 'B', 'C', 'D']:
                sub = origin_data[o]
                m = sub[(sub['s'] == s_val) & (sub['p_fail_scale'] == p_val)]
                if len(m):
                    row[f"mean_{o}"] = m['mean_dpm'].iloc[0]
                    row[f"n_{o}"] = int(m['n'].iloc[0])
                else:
                    row[f"mean_{o}"] = np.nan
                    row[f"n_{o}"] = 0
            rows.append(row)
    rob = pd.DataFrame(rows)

    lines = []
    lines.append("**<표 4> 원점 강건성: B/C/D 대(對) A의 평균 Δ 페널라이즈드 메이크스팬**")
    lines.append("(Origin Robustness: Mean Δ Penalized Makespan, B/C/D vs A on Common Cells)")
    lines.append("")
    lines.append("| s | p_fail_scale | Mean Δ (A, R=10) | Mean Δ (B, R=5) | Mean Δ (C, R=5) | Mean Δ (D, R=5)² |")
    lines.append("|---|---|---|---|---|---|")
    for _, r in rob.iterrows():
        lines.append(f"| {r['s']:.1f} | {r['p_fail_scale']:.2f} | {fmt_num(r['mean_A'])} | {fmt_num(r['mean_B'])} | {fmt_num(r['mean_C'])} | {fmt_num(r['mean_D'])} |")
    lines.append("")
    lines.append("*주.* Δ = 버스-단독 페널라이즈드 메이크스팬 − 다중-수단 페널라이즈드 메이크스팬 (분, 음수 = 버스-단독 우위). 공통 셀: s ∈ {1.0, 1.5} × p_fail_scale ∈ {0.0, 1.0, 2.0}. 원점 A는 송파 메인 시나리오, B·C·D는 인접 동원 거점에서의 동일 코리도어 재실행. ² **원점 D 미검증 경고**: smoke 검증(`results/smoke_D.json`)에서 censored 페널티가 다른 원점 대비 약 4배(−1.15 × 10⁶ vs A의 −2.88 × 10⁵) 폭증하여 송파 도로망 네트워크 모델링 가정의 외삽 한계를 시사함. 본 표의 D 열은 *참고용*이며, 차후 데이터 보정 전까지 정량 결론에는 포함하지 않음.")
    (OUT / "table4_origin_robustness.md").write_text("\n".join(lines), encoding="utf-8")
    return len(rob)


# =====================================================================
# TABLE 5: Morris μ* and σ (top-ranked)
# =====================================================================
def build_table5():
    mor = pd.read_csv(REPO / "results" / "sensitivity" / "morris_summary.csv")
    agg5 = mor.groupby("parameter_id").agg(
        mu_star_mean=("mu_star", "mean"),
        mu_star_max=("mu_star", "max"),
        sigma_mean=("sigma", "mean"),
        mu_star_conf_mean=("mu_star_conf", "mean"),
        n_records=("mu_star", "size"),
    ).reset_index().sort_values("mu_star_mean", ascending=False)

    lines = []
    lines.append("**<표 5> Morris 전역 민감도: 파라미터별 μ* 및 σ (상위 순위)**")
    lines.append("(Morris Global Sensitivity: Parameter μ* and σ, Top-Ranked)")
    lines.append("")
    lines.append("| 순위 (Rank) | 파라미터 (Parameter) | μ* 평균 (Mean μ*) | μ* 최대 (Max μ*) | σ 평균 (Mean σ) | μ* 95% CI 폭 평균 | 집계 레코드 수 (n) |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, r in enumerate(agg5.itertuples(index=False), start=1):
        lines.append(f"| {i} | {r.parameter_id} | {fmt_num(r.mu_star_mean)} | {fmt_num(r.mu_star_max)} | {fmt_num(r.sigma_mean)} | {fmt_num(r.mu_star_conf_mean)} | {int(r.n_records)} |")
    lines.append("")
    lines.append("*주.* SALib Morris elementary-effects 방법, 궤적(trajectories) = 50, 수준(levels) = 4, 14개 파라미터에 대해 (k+1) × T = (14+1) × 50 = 750 표본/구성으로 평가. μ* = |elementary effect|의 평균 (영향력 크기), σ = elementary effects의 표준편차 (비선형/상호작용 강도). 본 표의 값은 7개 출력 지표 (완료율, censored 인원, 페널라이즈드 메이크스팬, p80·p95 도착시간, 총 운영분, 단위 운영분당 수송 인원) × 2개 정책 (`baseline_multimodal`, `bus_only`) × 2개 시나리오 (`songpa_last_mile_station_to_destination`, `songpa_random_capacity_reduction`)에 대한 평균. Morris 결과는 파일럿 스캐폴드 (`results/sensitivity/morris_summary.csv`의 claim_scope 필드 참고)로, 보정된 운영-환경 민감도 추정치는 아님.")
    (OUT / "table5_morris_mu_star.md").write_text("\n".join(lines), encoding="utf-8")
    return {"rows": len(agg5), "top3": agg5.head(3)[["parameter_id", "mu_star_mean"]].values.tolist()}


if __name__ == "__main__":
    r1 = build_table1()
    r2 = build_table2()
    r3 = build_table3()
    r4 = build_table4()
    r5 = build_table5()
    print("Table 1 lines:", r1)
    print("Table 2:", r2)
    print("Table 3 rows:", r3)
    print("Table 4 rows:", r4)
    print("Table 5:", r5)
