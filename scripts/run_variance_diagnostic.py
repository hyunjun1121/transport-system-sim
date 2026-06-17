#!/usr/bin/env python
"""Phase T2: Variance diagnostic for B+C stochasticity only.

Runs 5 representative (policy, scenario) pairs at 9 parameter combos
(3 sigma x 3 lambda) with 10 seeds each. Reports unique makespan counts,
ranges, and CI widths to verify road noise and turnaround noise are the
sole within-scenario variance sources.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.realworld.pilot_experiments import (
    PilotInputs,
    apply_pilot_demand_fleet_profiles,
    build_policy_config_variant,
    graph_with_forced_disruption_probabilities,
    load_pilot_inputs,
    make_pilot_base_config,
    select_disruption_cases,
    select_policy_alternatives,
    _config_with_case_failure,
    _profile_run_sigma,
    _result_row,
    DEFAULT_DEMAND_PROFILES_PATH,
    DEFAULT_FLEET_PROFILES_PATH,
    DEFAULT_POLICY_ALTERNATIVES_PATH,
    DEFAULT_SCENARIO_PATH,
    CLAIM_SCOPE,
)
from src.realworld.disruption_scenarios import load_disruption_scenarios
from src.scenario import run_scenario as scenario_module_run
from src.policies import StrictPolicy
from src.realworld import pilot_experiments
from src import scenario as scenario_module

OUTPUT_DIR = PROJECT_ROOT / "results" / "realworld_pilot"
OUTPUT_CSV = OUTPUT_DIR / "variance_diagnostic.csv"
OUTPUT_MANIFEST = OUTPUT_DIR / "variance_diagnostic_manifest.json"

REPRESENTATIVE_PAIRS = [
    ("bus_only", "no_disruption"),
    ("baseline_multimodal", "no_disruption"),
    ("heavy_congestion_bus", "songpa_spatial_tancheon_corridor"),
    ("baseline_multimodal", "songpa_critical_link_blockage"),
    ("severe_congestion_bus", "songpa_rail_delay"),
]

SIGMA_VALUES = [0.0, 0.05, 0.10]
LAMBDA_VALUES = [0.0, 0.2, 0.4]
NUM_SEEDS = 10
SEED_BASE = 1


def run_variance_diagnostic() -> None:
    inputs = load_pilot_inputs()
    all_policies = load_policies(inputs)
    all_cases = load_cases(inputs)

    base_config, _ = apply_pilot_demand_fleet_profiles(
        make_pilot_base_config(inputs.region)
    )
    profile_sigma = _profile_run_sigma(base_config)

    rows: list[dict] = []
    for policy_id, scenario_id in REPRESENTATIVE_PAIRS:
        policy = find_policy(all_policies, policy_id)
        case = find_case(all_cases, scenario_id)
        for sigma_val in SIGMA_VALUES:
            for lambda_val in LAMBDA_VALUES:
                for seed_idx in range(NUM_SEEDS):
                    seed = SEED_BASE + seed_idx
                    metrics = run_single(
                        inputs=inputs,
                        base_config=base_config,
                        policies=all_policies,
                        policy=policy,
                        case=case,
                        sigma_val=sigma_val,
                        lambda_val=lambda_val,
                        profile_sigma=profile_sigma,
                        seed=seed,
                    )
                    makespan = metrics.get("penalized_makespan", float("inf"))
                    row = {
                        "policy_id": policy_id,
                        "scenario_id": scenario_id,
                        "road_noise_sigma": sigma_val,
                        "turnaround_noise_lambda": lambda_val,
                        "seed": seed,
                        "penalized_makespan": makespan,
                        "completion_rate": metrics.get("completion_rate", 0.0),
                        "censored_count": metrics.get("censored_count", 0),
                    }
                    rows.append(row)

    summary_rows = summarize(rows)
    write_outputs(rows, summary_rows)
    print_summary(summary_rows)


def load_policies(inputs: PilotInputs):
    from src.realworld.policy_alternatives import load_policy_alternatives
    return load_policy_alternatives(DEFAULT_POLICY_ALTERNATIVES_PATH)


def load_cases(inputs: PilotInputs):
    scenarios = load_disruption_scenarios(DEFAULT_SCENARIO_PATH)
    return select_disruption_cases(
        inputs.graph, scenarios, sample=False,
    )


def find_policy(policies, policy_id: str):
    for p in policies:
        if p.policy_id == policy_id:
            return p
    raise KeyError(f"policy not found: {policy_id}")


def find_case(cases, scenario_id: str):
    for c in cases:
        if c.scenario_id == scenario_id:
            return c
    raise KeyError(f"scenario not found: {scenario_id}")


def run_single(
    *,
    inputs: PilotInputs,
    base_config: dict,
    policies,
    policy,
    case,
    sigma_val: float,
    lambda_val: float,
    profile_sigma: float,
    seed: int,
) -> dict:
    import json as json_mod
    import copy

    config = copy.deepcopy(dict(base_config))
    config.setdefault("stochastic", {})
    config["stochastic"]["road_noise_sigma"] = sigma_val
    config["stochastic"]["turnaround_noise_lambda"] = lambda_val

    variant = build_policy_config_variant(config, policy, policies)
    run_config = _config_with_case_failure(variant.config, case)

    disrupted_graph = graph_with_forced_disruption_probabilities(
        inputs.graph, case,
        force_deterministic=True,
    )

    metrics = scenario_module.run_scenario(
        G=disrupted_graph,
        config=run_config,
        scenario_type=variant.scenario_type,
        policy=StrictPolicy(),
        params={
            "s": 1.0,
            "p_fail_scale": case.p_fail_scale,
            "sigma": profile_sigma,
        },
        seed=seed,
    )
    return metrics


def summarize(rows: list[dict]) -> list[dict]:
    from collections import defaultdict

    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        key = (row["policy_id"], row["scenario_id"],
               row["road_noise_sigma"], row["turnaround_noise_lambda"])
        grouped[key].append(row)

    summary_rows: list[dict] = []
    for key, group in sorted(grouped.items()):
        policy_id, scenario_id, sigma_val, lambda_val = key
        makespans = [r["penalized_makespan"] for r in group]
        finite = [m for m in makespans if math.isfinite(m)]
        unique_vals = sorted(set(finite)) if finite else []

        ci_width = 0.0
        if len(finite) >= 3:
            mean_val = statistics.mean(finite)
            stdev = statistics.stdev(finite) if len(finite) >= 2 else 0.0
            ci_width = 1.96 * stdev / math.sqrt(len(finite))

        summary_rows.append({
            "policy_id": policy_id,
            "scenario_id": scenario_id,
            "road_noise_sigma": sigma_val,
            "turnaround_noise_lambda": lambda_val,
            "n_seeds": len(makespans),
            "n_finite": len(finite),
            "n_inf": len(makespans) - len(finite),
            "n_unique_finite": len(unique_vals),
            "makespan_min": min(finite) if finite else "",
            "makespan_max": max(finite) if finite else "",
            "makespan_mean": round(statistics.mean(finite), 4) if finite else "",
            "ci_width_95": round(ci_width, 4) if ci_width else 0.0,
        })
    return summary_rows


def write_outputs(rows: list[dict], summary_rows: list[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_runs": len(rows),
        "representative_pairs": REPRESENTATIVE_PAIRS,
        "sigma_values": SIGMA_VALUES,
        "lambda_values": LAMBDA_VALUES,
        "num_seeds": NUM_SEEDS,
        "claim_boundary": (
            "Exploratory variance diagnostic only; not calibrated uncertainty "
            "or operational forecast."
        ),
        "outputs": {
            "csv": str(OUTPUT_CSV.relative_to(PROJECT_ROOT)),
            "manifest": str(OUTPUT_MANIFEST.relative_to(PROJECT_ROOT)),
        },
    }
    with OUTPUT_MANIFEST.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    summary_path = OUTPUT_DIR / "variance_diagnostic_summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)


def print_summary(summary_rows: list[dict]) -> None:
    print("\n=== Variance Diagnostic Summary ===\n")
    print(f"{'Policy':<30} {'Scenario':<40} {'Sig':>5} {'Lam':>5} {'NFin':>5} {'NUniq':>6} {'Min':>10} {'Max':>10} {'CI95':>8}")
    print("-" * 125)
    for row in summary_rows:
        print(
            f"{row['policy_id']:<30} {row['scenario_id']:<40} "
            f"{row['road_noise_sigma']:>5.2f} {row['turnaround_noise_lambda']:>5.2f} "
            f"{row['n_finite']:>5} {row['n_unique_finite']:>6} "
            f"{str(row['makespan_min']):>10} {str(row['makespan_max']):>10} "
            f"{row['ci_width_95']:>8.4f}"
        )
    print(f"\nTotal runs: {sum(r['n_seeds'] for r in summary_rows)}")
    print(f"Output: {OUTPUT_CSV}")


if __name__ == "__main__":
    run_variance_diagnostic()
