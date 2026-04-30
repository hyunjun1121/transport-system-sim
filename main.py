"""Transport System Simulation - Main Entry Point.

전시 동원예비군 수송체계 Micro-Simulation 실험
비교: 버스 단독 vs 철도-버스 복합 수송

Usage:
    python main.py              # Full experiment (Phase 1 + Phase 2)
    python main.py --phase 1    # Phase 1 only
    python main.py --phase 2    # Phase 2 only
    python main.py --quick      # Quick smoke test (R=3)
    python main.py --test       # Single scenario test
"""

import argparse
import yaml
import time

from src.network import build_network, print_network
from src.experiment.runner import run_phase1, run_phase2, save_results
from src.experiment.analysis import compute_ci, find_breakeven, summarize_phase1
from src.visualize.plots import (
    plot_delta_heatmap,
    plot_success_rate_comparison,
    plot_policy_pareto,
    plot_breakeven_line,
)


def run_full(config: dict, quick: bool = False) -> None:
    """Run full experiment pipeline."""
    if quick:
        config["experiment"]["R"] = 3
        config["congestion_scale"]["levels"] = [1.0, 2.0]
        config["failure_rate"]["levels"] = [0.0, 0.10]
        config["lateness"]["sigma_levels"] = [0.5]
        print("[QUICK MODE] Reduced grid and R=3")

    print("=" * 60)
    print("Transport System Simulation - Micro-Simulation Experiment")
    print("=" * 60)

    # Build network
    G = build_network(config)
    print("\nNetwork:")
    print_network(G)

    # Phase 1: s x p_fail break-even search
    print("\n--- Phase 1: Break-even Search ---")
    t0 = time.time()
    df1 = run_phase1(config, G)
    print(f"Phase 1 complete: {time.time() - t0:.1f}s, {len(df1)} rows")

    save_results(df1, "results/phase1_results.csv")

    # Analysis
    ci1 = compute_ci(df1, "delta_makespan", ["s", "p_fail_scale"])
    save_results(ci1, "results/phase1_ci.csv")

    summary1 = summarize_phase1(df1)
    save_results(summary1, "results/phase1_summary.csv")

    # Break-even estimation
    print("\n--- Break-even Analysis ---")
    breakeven = {}
    for s in config["congestion_scale"]["levels"]:
        p_star = find_breakeven(df1, s)
        breakeven[s] = p_star
        if p_star is not None:
            print(f"  s={s}: break-even p_fail* = {p_star:.4f}")
        else:
            print(f"  s={s}: no crossing found")

    # Visualizations
    print("\n--- Generating Plots ---")
    plot_delta_heatmap(df1)
    plot_success_rate_comparison(df1)
    plot_breakeven_line(breakeven)
    print("  Phase 1 plots saved to results/")

    # Phase 2: sigma x policy trade-off
    print("\n--- Phase 2: Policy Trade-off Analysis ---")
    t0 = time.time()
    df2 = run_phase2(config, G)
    print(f"Phase 2 complete: {time.time() - t0:.1f}s, {len(df2)} rows")

    save_results(df2, "results/phase2_results.csv")

    ci2 = compute_ci(df2, "delta_makespan", ["sigma", "policy"])
    save_results(ci2, "results/phase2_ci.csv")

    plot_policy_pareto(df2)
    print("  Phase 2 plots saved to results/")

    # Verification check
    print("\n--- Verification ---")
    for _, row in df1.iterrows():
        total_bus = row["bus_makespan"]
        total_multi = row["multi_makespan"]
        if total_bus < 0 or total_multi < 0:
            print(f"  WARNING: Negative makespan at s={row['s']}, p={row['p_fail_scale']}")

    print("\nDone!")


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


def main():
    parser = argparse.ArgumentParser(description="Transport System Simulation")
    parser.add_argument("--phase", type=int, choices=[1, 2], help="Run specific phase only")
    parser.add_argument("--quick", action="store_true", help="Quick smoke test (R=3)")
    parser.add_argument("--test", action="store_true", help="Single scenario test")
    args = parser.parse_args()

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    if args.test:
        run_single_test(config)
    else:
        run_full(config, quick=args.quick)


if __name__ == "__main__":
    main()
