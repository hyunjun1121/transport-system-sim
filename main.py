r"""Transport System Simulation command-line entry point.

Usage on Windows:
    .\.venv\Scripts\python main.py              # Full experiment
    .\.venv\Scripts\python main.py --phase 1    # Phase 1 only
    .\.venv\Scripts\python main.py --phase 2    # Phase 2 only
    .\.venv\Scripts\python main.py --quick      # Quick smoke test
    .\.venv\Scripts\python main.py --test       # Single scenario test
"""

import argparse
from copy import deepcopy
from pathlib import Path
import time

import numpy as np
import pandas as pd
import yaml

from src.network import build_network, print_network
from src.experiment.runner import run_phase1, run_phase2, save_results
from src.experiment.analysis import compute_ci, find_breakeven, summarize_phase1
from src.visualize.plots import (
    plot_delta_heatmap,
    plot_success_rate_comparison,
    plot_policy_pareto,
    plot_breakeven_line,
)


PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"
RESULTS_DIR = PROJECT_ROOT / "results"


def run_full(config: dict, quick: bool = False) -> None:
    """Run full experiment pipeline."""
    if quick:
        config = _quick_config(config)

    print("=" * 60)
    print("Transport System Simulation - Micro-Simulation Experiment")
    print("=" * 60)
    if quick:
        print("[QUICK MODE] Reduced grid and R=3")

    # Build network
    G = build_network(config)
    print("\nNetwork:")
    print_network(G)

    df1 = run_phase1_pipeline(config, G, RESULTS_DIR)
    run_phase2_pipeline(config, G, RESULTS_DIR)

    # Verification check
    print("\n--- Verification ---")
    _verify_phase1_results(df1)

    print("\nDone!")


def run_phase(config: dict, phase: int, quick: bool = False) -> None:
    """Run one experiment phase."""
    if quick:
        config = _quick_config(config)

    print("=" * 60)
    print(f"Transport System Simulation - Phase {phase}")
    print("=" * 60)
    if quick:
        print("[QUICK MODE] Reduced grid and R=3")

    G = build_network(config)
    print("\nNetwork:")
    print_network(G)

    if phase == 1:
        run_phase1_pipeline(config, G, RESULTS_DIR)
    else:
        run_phase2_pipeline(config, G, RESULTS_DIR)


def run_phase1_pipeline(config: dict, G, output_dir: Path) -> pd.DataFrame:
    """Run Phase 1, analysis, and plots."""
    print("\n--- Phase 1: Break-even Search ---")
    t0 = time.time()
    df1 = run_phase1(config, G)
    print(f"Phase 1 complete: {time.time() - t0:.1f}s, {len(df1)} rows")

    save_results(df1, output_dir / "phase1_results.csv")

    comparison_metric = _comparison_metric(df1)
    print(f"  Analysis metric: {comparison_metric}")
    ci1 = compute_ci(df1, comparison_metric, ["s", "p_fail_scale"])
    save_results(ci1, output_dir / "phase1_ci.csv")

    summary1 = summarize_phase1(df1)
    save_results(summary1, output_dir / "phase1_summary.csv")

    context_filters = _active_context_filters(config)
    context_df = _filter_context_rows(df1, context_filters)
    if len(context_df) == 0:
        context_df = df1
        print("  WARNING: active context filter matched no Phase 1 rows; plotting all rows")
    else:
        print(f"  Plot/break-even context: {_format_context_filters(context_filters)}")

    print("\n--- Break-even Analysis ---")
    breakeven = {}
    for s in config["congestion_scale"]["levels"]:
        p_star = find_breakeven(
            df1,
            s,
            metric=comparison_metric,
            filters=context_filters,
        )
        breakeven[s] = p_star
        if p_star is not None:
            print(f"  s={s}: break-even p_fail_scale = {p_star:.4f}")
        else:
            print(f"  s={s}: no crossing found")

    print("\n--- Generating Plots ---")
    plot_delta_heatmap(context_df, output_dir=output_dir, metric=comparison_metric)
    plot_success_rate_comparison(context_df, output_dir=output_dir)
    plot_breakeven_line(breakeven, output_dir=output_dir)
    print(f"  Phase 1 plots saved to {output_dir}")
    return df1


def run_phase2_pipeline(config: dict, G, output_dir: Path) -> pd.DataFrame:
    """Run Phase 2, analysis, and plots."""
    print("\n--- Phase 2: Policy Trade-off Analysis ---")
    t0 = time.time()
    df2 = run_phase2(config, G)
    print(f"Phase 2 complete: {time.time() - t0:.1f}s, {len(df2)} rows")

    save_results(df2, output_dir / "phase2_results.csv")

    comparison_metric = _comparison_metric(df2)
    print(f"  Analysis metric: {comparison_metric}")
    ci2 = compute_ci(df2, comparison_metric, ["sigma", "policy"])
    save_results(ci2, output_dir / "phase2_ci.csv")

    plot_policy_pareto(df2, output_dir=output_dir)
    print(f"  Phase 2 plots saved to {output_dir}")
    return df2


def run_single_test(config: dict) -> None:
    """Run a single scenario test for debugging."""
    from src.scenario import run_scenario
    from src.policies import StrictPolicy

    G = build_network(config)
    print_network(G)

    params = {"s": 1.0, "p_fail_scale": 0.05, "sigma": 0.5}
    policy = StrictPolicy()

    print("\n--- Bus Only ---")
    bus = run_scenario(G, config, "bus_only", policy, params, seed=42)
    for k, v in bus.items():
        print(f"  {k}: {v}")

    print("\n--- Multimodal ---")
    multi = run_scenario(G, config, "multimodal", policy, params, seed=42)
    for k, v in multi.items():
        print(f"  {k}: {v}")

    print(f"\nDelta makespan: {bus['makespan'] - multi['makespan']:.2f} min")


def _quick_config(config: dict) -> dict:
    """Return a reduced experiment config for smoke runs."""
    quick = deepcopy(config)
    quick["experiment"]["R"] = 3
    quick["congestion_scale"]["levels"] = [1.0, 2.0]
    quick["failure_rate"]["levels"] = [0.0, 0.10]
    quick["lateness"]["sigma_levels"] = [0.5]
    return quick


def _comparison_metric(df: pd.DataFrame) -> str:
    """Prefer censoring-aware delta when the new model exposes it."""
    if "delta_penalized_makespan" in df.columns:
        return "delta_penalized_makespan"
    if "delta_makespan" in df.columns:
        return "delta_makespan"
    raise KeyError("No delta makespan metric found in experiment results")


def _active_context_filters(config: dict) -> dict[str, object]:
    """Return the active experiment context used for default plots."""
    failure = config.get("failure", {})
    mode = failure.get("mode", "blocked")
    factor = None
    if mode == "capacity_reduction":
        factor = failure.get("capacity_reduction_factor")
    return {
        "network_variant": config.get("network", {}).get("variant", "baseline"),
        "failure_mode": mode,
        "capacity_reduction_factor": factor,
    }


def _filter_context_rows(df: pd.DataFrame, filters: dict[str, object]) -> pd.DataFrame:
    """Filter result rows to one network/failure context when columns exist."""
    subset = df
    for column, value in filters.items():
        if column not in subset.columns:
            continue
        if value is None:
            subset = subset[subset[column].isna()]
        else:
            subset = subset[subset[column] == value]
    return subset


def _format_context_filters(filters: dict[str, object]) -> str:
    """Return a compact context string for CLI output."""
    return ", ".join(f"{key}={value}" for key, value in filters.items())


def _verify_phase1_results(df: pd.DataFrame) -> None:
    """Print lightweight sanity checks for experiment output."""
    negative_cols = [
        "bus_makespan",
        "multi_makespan",
        "bus_penalized_makespan",
        "multi_penalized_makespan",
    ]
    for col in negative_cols:
        if col not in df.columns:
            continue
        numeric = pd.to_numeric(df[col], errors="coerce").astype(float).to_numpy()
        bad_rows = df[np.isfinite(numeric) & (numeric < 0)]
        for _, row in bad_rows.iterrows():
            print(
                "  WARNING: Negative "
                f"{col} at s={row['s']}, p={row['p_fail_scale']}"
            )

    if "delta_makespan" in df.columns:
        delta_values = pd.to_numeric(df["delta_makespan"], errors="coerce").astype(float)
        nonfinite_delta = int((~np.isfinite(delta_values.to_numpy())).sum())
        if nonfinite_delta:
            print(
                "  INFO: "
                f"{nonfinite_delta} raw delta_makespan rows are non-finite; "
                "penalized KPIs are used for analysis when available."
            )


def load_config(path: Path = CONFIG_PATH) -> dict:
    """Load YAML config from a deterministic project-relative path."""
    try:
        with path.open(encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError as exc:
        raise SystemExit(f"Config file not found: {path}") from exc

    if not isinstance(config, dict):
        raise SystemExit(f"Config file did not contain a YAML mapping: {path}")
    return config


def main():
    parser = argparse.ArgumentParser(description="Transport System Simulation")
    parser.add_argument("--phase", type=int, choices=[1, 2], help="Run specific phase only")
    parser.add_argument("--quick", action="store_true", help="Quick smoke test (R=3)")
    parser.add_argument("--test", action="store_true", help="Single scenario test")
    args = parser.parse_args()

    config = load_config()

    if args.test:
        if args.quick:
            print("[QUICK MODE] Ignored for --test")
        run_single_test(config)
    elif args.phase:
        run_phase(config, args.phase, quick=args.quick)
    else:
        run_full(config, quick=args.quick)


if __name__ == "__main__":
    main()
