"""CRN paired experiment runner.

Runs paired comparisons (same seed for Scenario 1 & 2) across parameter grid.
Inspired by inventory-simulation's run_experiments() pattern.
"""

import os
import pandas as pd
import numpy as np
import networkx as nx

from src.network import build_network
from src.scenario import run_scenario
from src.policies import StrictPolicy, build_policies
from src.experiment.doe import phase1_grid, phase2_grid


def run_phase1(config: dict, G: nx.DiGraph = None, verbose: bool = True) -> pd.DataFrame:
    """Run Phase 1: s x p_fail break-even search.

    For each (s, p_fail) combination, run R paired replications
    using the same seed for bus_only and multimodal scenarios.
    Uses STRICT policy and base sigma.
    """
    if G is None:
        G = build_network(config)

    grid = phase1_grid(config)
    R = config["experiment"]["R"]
    seed_base = config["experiment"]["seed_base"]
    policy = StrictPolicy()
    sigma = config["lateness"]["sigma_levels"][0]  # default sigma (first level)

    results = []
    total = len(grid) * R
    count = 0

    for s, p_fail_scale in grid:
        for r in range(R):
            seed = seed_base + r
            params = {"s": s, "p_fail_scale": p_fail_scale, "sigma": sigma}

            bus = run_scenario(G, config, "bus_only", policy, params, seed)
            multi = run_scenario(G, config, "multimodal", policy, params, seed)

            results.append({
                "s": s,
                "p_fail_scale": p_fail_scale,
                "rep": r,
                "seed": seed,
                "bus_makespan": bus["makespan"],
                "multi_makespan": multi["makespan"],
                "delta_makespan": bus["makespan"] - multi["makespan"],
                "bus_success_rate": bus["success_rate"],
                "multi_success_rate": multi["success_rate"],
                "bus_resource_eff": bus["resource_efficiency"],
                "multi_resource_eff": multi["resource_efficiency"],
                "bus_leftover": bus["leftover_count"],
                "multi_leftover": multi["leftover_count"],
            })
            count += 1
            if verbose and count % 50 == 0:
                print(f"  Phase 1: {count}/{total}")

    return pd.DataFrame(results)


def run_phase2(config: dict, G: nx.DiGraph = None, verbose: bool = True) -> pd.DataFrame:
    """Run Phase 2: sigma x policy trade-off analysis.

    Uses representative s and p_fail values from Phase 1 results.
    """
    if G is None:
        G = build_network(config)

    grid = phase2_grid(config)
    R = config["experiment"]["R"]
    seed_base = config["experiment"]["seed_base"]

    # Representative Phase 1 values
    s = config["congestion_scale"]["levels"][len(config["congestion_scale"]["levels"]) // 2]
    p_fail_scale = config["failure_rate"]["levels"][len(config["failure_rate"]["levels"]) // 2]

    results = []
    total = len(grid) * R
    count = 0

    for sigma, policy in grid:
        for r in range(R):
            seed = seed_base + r
            params = {"s": s, "p_fail_scale": p_fail_scale, "sigma": sigma}

            bus = run_scenario(G, config, "bus_only", policy, params, seed)
            multi = run_scenario(G, config, "multimodal", policy, params, seed)

            results.append({
                "sigma": sigma,
                "policy": policy.name(),
                "rep": r,
                "seed": seed,
                "bus_makespan": bus["makespan"],
                "multi_makespan": multi["makespan"],
                "delta_makespan": bus["makespan"] - multi["makespan"],
                "bus_success_rate": bus["success_rate"],
                "multi_success_rate": multi["success_rate"],
                "bus_leftover": bus["leftover_count"],
                "multi_leftover": multi["leftover_count"],
            })
            count += 1
            if verbose and count % 50 == 0:
                print(f"  Phase 2: {count}/{total}")

    return pd.DataFrame(results)


def save_results(df: pd.DataFrame, path: str) -> None:
    """Save results DataFrame to CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Results saved to {path} ({len(df)} rows)")
