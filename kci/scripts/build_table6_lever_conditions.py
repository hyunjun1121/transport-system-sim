"""Table 6 builder — conditions under which multimodal becomes viable.

Loads ``results/phase3_lever_sweep.csv``, aggregates each lever cell
(``rail_headway_min`` x ``lastmile_fleet_size`` x ``rail_capacity_pax_per_train``
x ``p_fail_scale``) with mean + 95% paired-t CI for three metrics
(``delta_penalized_makespan``, ``delta_arrival_q90_min``,
``delta_prob_completion_within_window``), classifies each cell as one of
``bus_dominant`` / ``inconclusive`` / ``multi_dominant`` on the
penalized-makespan metric, and emits:

  - ``manuscript/tables/table6_lever_conditions.md`` — Korean markdown table
    listing all multi_dominant cells (or, if none, the 5 cells closest to
    sign-flip).
  - ``manuscript/tables/table6_lever_conditions_summary.json`` — sidecar JSON
    consumed by downstream D3/D4/D5 agents for canonical headline numbers.

Classification rule (penalized_makespan):
  - ``bus_dominant``: mean Δ < 0 and CI upper < 0.
  - ``inconclusive``: CI straddles 0.
  - ``multi_dominant``: mean Δ > 0 and CI lower > 0.

Sign convention: Δ = bus − multi (negative = bus dominates / multi inferior).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from scipy import stats  # type: ignore

    _HAS_SCIPY = True
except Exception:  # pragma: no cover
    _HAS_SCIPY = False


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "phase3_lever_sweep.csv"
TABLES_DIR = ROOT / "manuscript" / "tables"
TABLE_PATH = TABLES_DIR / "table6_lever_conditions.md"
JSON_PATH = TABLES_DIR / "table6_lever_conditions_summary.json"

LEVER_COLS = [
    "rail_headway_min",
    "lastmile_fleet_size",
    "rail_capacity_pax_per_train",
    "p_fail_scale",
]
METRICS = [
    "delta_penalized_makespan",
    "delta_arrival_q90_min",
    "delta_prob_completion_within_window",
]
CLASS_METRIC = "delta_penalized_makespan"


def _t_crit(df: int, alpha: float = 0.05) -> float:
    if _HAS_SCIPY:
        return float(stats.t.ppf(1 - alpha / 2.0, df=df))
    lut = {9: 2.262, 14: 2.145, 19: 2.093, 29: 2.045, 49: 2.010}
    if df in lut:
        return lut[df]
    return 1.96


def _paired_ci(values: np.ndarray) -> tuple[float, float, float, int]:
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


def _classify(mean: float, lo: float, hi: float) -> str:
    if not (np.isfinite(mean) and np.isfinite(lo) and np.isfinite(hi)):
        return "inconclusive"
    if mean < 0 and hi < 0:
        return "bus_dominant"
    if mean > 0 and lo > 0:
        return "multi_dominant"
    return "inconclusive"


def _aggregate(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for keys, grp in df.groupby(LEVER_COLS):
        row: dict[str, Any] = dict(zip(LEVER_COLS, [float(k) for k in keys]))
        row["n"] = int(len(grp))
        for metric in METRICS:
            vals = grp[metric].to_numpy() if metric in grp.columns else np.array([])
            mean, lo, hi, n_finite = _paired_ci(vals)
            row[f"{metric}_mean"] = mean
            row[f"{metric}_ci_lower"] = lo
            row[f"{metric}_ci_upper"] = hi
            row[f"{metric}_n_finite"] = n_finite
        row["classification"] = _classify(
            row[f"{CLASS_METRIC}_mean"],
            row[f"{CLASS_METRIC}_ci_lower"],
            row[f"{CLASS_METRIC}_ci_upper"],
        )
        # Gap heuristic for fallback ranking: smaller |mean|/se = closer to flip
        mean = row[f"{CLASS_METRIC}_mean"]
        lo = row[f"{CLASS_METRIC}_ci_lower"]
        hi = row[f"{CLASS_METRIC}_ci_upper"]
        if np.isfinite(mean):
            row["abs_mean"] = abs(mean)
        else:
            row["abs_mean"] = float("inf")
        if np.isfinite(lo) and np.isfinite(hi):
            # CI half-width; larger = more overlap potential
            row["ci_half_width"] = (hi - lo) / 2.0
            # Distance from 0 normalized by CI half-width (smaller = closer to flip)
            half = (hi - lo) / 2.0
            row["flip_distance"] = abs(mean) / half if half > 0 else float("inf")
        else:
            row["ci_half_width"] = float("nan")
            row["flip_distance"] = float("inf")
        rows.append(row)
    return pd.DataFrame(rows)


def _fmt_num(x: float, decimals: int = 1) -> str:
    if not np.isfinite(x):
        return "n/a"
    return f"{x:,.{decimals}f}"


def _markdown_table(agg: pd.DataFrame, subset: pd.DataFrame, fallback: bool) -> str:
    header_note = (
        "본 표는 multimodal이 단일수단보다 통계적으로 유의하게 더 우수해지는 "
        "(혹은 가장 근접한) 반사실 레버 조건을 나열한다. 빈 부분집합은 어떤 "
        "셀도 multimodal에 결정적 우위를 부여하지 않음을 의미한다."
    )
    n_total = int(len(agg))
    n_bus = int((agg["classification"] == "bus_dominant").sum())
    n_inc = int((agg["classification"] == "inconclusive").sum())
    n_multi = int((agg["classification"] == "multi_dominant").sum())

    lines: list[str] = []
    lines.append(
        "**<표 6> 반사실 레버 적용 조건 — multimodal 우위 (혹은 부호 반전 근접) 셀**"
    )
    lines.append("")
    lines.append(f"*주.* {header_note}")
    lines.append("")
    lines.append(
        f"전체 셀 수: **{n_total}** | bus_dominant: **{n_bus}** | "
        f"inconclusive: **{n_inc}** | multi_dominant: **{n_multi}**"
    )
    lines.append("")
    if fallback:
        lines.append(
            "*비고.* multi_dominant 셀이 발견되지 않아, 부호 반전에 가장 "
            "근접한 5개 셀 (|평균 Δ| / CI 반폭 최소)을 대신 나열한다."
        )
        lines.append("")

    lines.append(
        "| rail_headway_min | lastmile_fleet_size | rail_capacity | p_fail_scale | "
        "평균 Δ penalized_makespan (분) [95% CI] | 평균 Δ q90 (분) [95% CI] | "
        "평균 Δ P(완료) [95% CI] | 분류 |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")

    if subset.empty:
        lines.append("| — | — | — | — | — | — | — | — |")
    else:
        for _, row in subset.iterrows():
            pen_str = (
                f"{_fmt_num(row['delta_penalized_makespan_mean'])}  "
                f"[{_fmt_num(row['delta_penalized_makespan_ci_lower'])}, "
                f"{_fmt_num(row['delta_penalized_makespan_ci_upper'])}]"
            )
            q90_str = (
                f"{_fmt_num(row['delta_arrival_q90_min_mean'])}  "
                f"[{_fmt_num(row['delta_arrival_q90_min_ci_lower'])}, "
                f"{_fmt_num(row['delta_arrival_q90_min_ci_upper'])}]"
            )
            pc_str = (
                f"{_fmt_num(row['delta_prob_completion_within_window_mean'], 3)}  "
                f"[{_fmt_num(row['delta_prob_completion_within_window_ci_lower'], 3)}, "
                f"{_fmt_num(row['delta_prob_completion_within_window_ci_upper'], 3)}]"
            )
            lines.append(
                f"| {row['rail_headway_min']:g} | {int(row['lastmile_fleet_size'])} | "
                f"{int(row['rail_capacity_pax_per_train'])} | {row['p_fail_scale']:g} | "
                f"{pen_str} | {q90_str} | {pc_str} | {row['classification']} |"
            )

    lines.append("")
    lines.append(
        "*해석.* Δ = bus − multi (음수 = 직행버스 우위 / multimodal 열등; "
        "양수 = multimodal 우위). 분류는 penalized_makespan 기준 95% paired-t "
        "CI (df = R−1 = 14)로 산출: `bus_dominant`(CI upper < 0), "
        "`multi_dominant`(CI lower > 0), `inconclusive`(CI가 0을 포함)."
    )
    lines.append("")
    return "\n".join(lines)


def _row_to_summary_dict(row: pd.Series) -> dict[str, Any]:
    return {
        "rail_headway_min": float(row["rail_headway_min"]),
        "lastmile_fleet_size": int(row["lastmile_fleet_size"]),
        "rail_capacity_pax_per_train": int(row["rail_capacity_pax_per_train"]),
        "p_fail_scale": float(row["p_fail_scale"]),
        "classification": str(row["classification"]),
        "delta_penalized_makespan_mean": float(row["delta_penalized_makespan_mean"]),
        "delta_penalized_makespan_ci_lower": float(
            row["delta_penalized_makespan_ci_lower"]
        ),
        "delta_penalized_makespan_ci_upper": float(
            row["delta_penalized_makespan_ci_upper"]
        ),
        "delta_arrival_q90_min_mean": float(row["delta_arrival_q90_min_mean"]),
        "delta_arrival_q90_min_ci_lower": float(row["delta_arrival_q90_min_ci_lower"]),
        "delta_arrival_q90_min_ci_upper": float(row["delta_arrival_q90_min_ci_upper"]),
        "delta_prob_completion_within_window_mean": float(
            row["delta_prob_completion_within_window_mean"]
        ),
        "delta_prob_completion_within_window_ci_lower": float(
            row["delta_prob_completion_within_window_ci_lower"]
        ),
        "delta_prob_completion_within_window_ci_upper": float(
            row["delta_prob_completion_within_window_ci_upper"]
        ),
        "n_reps": int(row["n"]),
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Table 6 (lever conditions).")
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
    required = set(LEVER_COLS) | set(METRICS)
    missing = required - set(df.columns)
    if missing:
        print(
            f"ERROR: Phase 3 CSV missing required columns: {sorted(missing)}",
            file=sys.stderr,
        )
        return 3

    agg = _aggregate(df)

    multi_cells = agg[agg["classification"] == "multi_dominant"].copy()
    if not multi_cells.empty:
        subset = multi_cells.sort_values(
            "delta_penalized_makespan_mean", ascending=False
        )
        fallback = False
    else:
        # Fallback: 5 cells closest to sign-flip
        subset = agg.sort_values("flip_distance", ascending=True).head(5)
        fallback = True

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    md = _markdown_table(agg, subset, fallback)
    TABLE_PATH.write_text(md, encoding="utf-8")

    # Narrowest gap cell — smallest |mean Δ penalized_makespan|
    narrowest_idx = agg["abs_mean"].idxmin() if not agg.empty else None
    narrowest = (
        _row_to_summary_dict(agg.loc[narrowest_idx]) if narrowest_idx is not None else None
    )

    summary: dict[str, Any] = {
        "n_cells_total": int(len(agg)),
        "n_bus_dominant": int((agg["classification"] == "bus_dominant").sum()),
        "n_inconclusive": int((agg["classification"] == "inconclusive").sum()),
        "n_multi_dominant": int((agg["classification"] == "multi_dominant").sum()),
        "multi_dominant_cells": [
            _row_to_summary_dict(r) for _, r in multi_cells.iterrows()
        ],
        "narrowest_gap_cell": narrowest,
        "fallback_used": fallback,
        "input_csv": str(args.input),
    }
    JSON_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {TABLE_PATH}")
    print(f"Wrote {JSON_PATH}")
    print(
        f"Cells: total={summary['n_cells_total']}, "
        f"bus={summary['n_bus_dominant']}, inc={summary['n_inconclusive']}, "
        f"multi={summary['n_multi_dominant']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
