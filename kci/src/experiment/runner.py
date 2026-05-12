"""CRN paired experiment runner.

Runs paired comparisons (same seed for Scenario 1 & 2) across parameter grid.
Inspired by inventory-simulation's run_experiments() pattern.
"""

from copy import deepcopy
from pathlib import Path

import pandas as pd
import numpy as np
import networkx as nx

from src.network import build_network, config_for_network_variant
from src.scenario import run_scenario
from src.policies import StrictPolicy
from src.experiment.doe import phase1_grid, phase2_grid


SCENARIO_KPI_COLUMNS = {
    "makespan": "makespan",
    "penalized_makespan": "penalized_makespan",
    "success_count": "success_count",
    "success_rate": "success_rate",
    "completion_rate": "completion_rate",
    "resource_efficiency": "resource_eff",
    "leftover_count": "leftover",
    "censored_count": "censored_count",
    "total_personnel": "total_personnel",
    "bus_trips": "bus_trips",
    "train_trips": "train_trips",
    "bus_minutes": "bus_minutes",
    "train_minutes": "train_minutes",
    "lastmile_minutes": "lastmile_minutes",
    "lastmile_vehicle_minutes": "lastmile_vehicle_minutes",
    "road_vehicle_service_minutes": "road_vehicle_service_minutes",
    "train_service_minutes": "train_service_minutes",
    "total_service_minutes": "total_service_minutes",
    "passenger_travel_minutes": "passenger_travel_minutes",
    "passengers_per_vehicle_minute": "passengers_per_vehicle_minute",
    "passengers_per_total_service_minute": "passengers_per_total_service_minute",
}

DELTA_KPIS = {
    "makespan": "delta_makespan",
    "penalized_makespan": "delta_penalized_makespan",
    "success_rate": "delta_success_rate",
    "completion_rate": "delta_completion_rate",
    "resource_efficiency": "delta_resource_eff",
    "road_vehicle_service_minutes": "delta_road_vehicle_service_minutes",
    "train_service_minutes": "delta_train_service_minutes",
    "total_service_minutes": "delta_total_service_minutes",
    "passenger_travel_minutes": "delta_passenger_travel_minutes",
    "passengers_per_vehicle_minute": "delta_passengers_per_vehicle_minute",
    "passengers_per_total_service_minute": (
        "delta_passengers_per_total_service_minute"
    ),
}


def run_phase1(config: dict, G: nx.DiGraph = None, verbose: bool = True) -> pd.DataFrame:
    """Run Phase 1: s x p_fail break-even search.

    For each (s, p_fail) combination, run R paired replications
    using the same seed for bus_only and multimodal scenarios.
    Uses STRICT policy and base sigma.
    """
    grid = phase1_grid(config)
    R = config["experiment"]["R"]
    seed_base = config["experiment"]["seed_base"]
    policy = StrictPolicy()
    sigma = config["lateness"]["sigma_levels"][0]  # default sigma (first level)
    context_cache = _ContextCache(config, G)

    results = []
    total = len(grid) * R
    count = 0

    for point in grid:
        run_config, run_graph = context_cache.get(
            point.network_variant,
            point.failure_mode,
            point.capacity_reduction_factor,
        )
        for r in range(R):
            seed = seed_base + r
            params = {
                "s": point.s,
                "p_fail_scale": point.p_fail_scale,
                "sigma": sigma,
            }

            bus = run_scenario(run_graph, run_config, "bus_only", policy, params, seed)
            multi = run_scenario(run_graph, run_config, "multimodal", policy, params, seed)

            results.append(_paired_result_row({
                "s": point.s,
                "p_fail_scale": point.p_fail_scale,
                "network_variant": point.network_variant,
                "failure_mode": point.failure_mode,
                "capacity_reduction_factor": point.capacity_reduction_factor,
                "rep": r,
                "seed": seed,
            }, bus, multi))
            count += 1
            if verbose and count % 50 == 0:
                print(f"  Phase 1: {count}/{total}")

    return pd.DataFrame(results)


def run_phase2(config: dict, G: nx.DiGraph = None, verbose: bool = True) -> pd.DataFrame:
    """Run Phase 2: sigma x policy trade-off analysis.

    Uses representative s and p_fail values from Phase 1 results.
    """
    grid = phase2_grid(config)
    R = config["experiment"]["R"]
    seed_base = config["experiment"]["seed_base"]
    context_cache = _ContextCache(config, G)

    # Representative Phase 1 values
    s = config["congestion_scale"]["levels"][len(config["congestion_scale"]["levels"]) // 2]
    p_fail_scale = config["failure_rate"]["levels"][len(config["failure_rate"]["levels"]) // 2]

    results = []
    total = len(grid) * R
    count = 0

    for point in grid:
        run_config, run_graph = context_cache.get(
            point.network_variant,
            point.failure_mode,
            point.capacity_reduction_factor,
        )
        for r in range(R):
            seed = seed_base + r
            params = {"s": s, "p_fail_scale": p_fail_scale, "sigma": point.sigma}

            bus = run_scenario(run_graph, run_config, "bus_only", point.policy, params, seed)
            multi = run_scenario(run_graph, run_config, "multimodal", point.policy, params, seed)

            results.append(_paired_result_row({
                "sigma": point.sigma,
                "policy": point.policy.name(),
                "s": s,
                "p_fail_scale": p_fail_scale,
                "network_variant": point.network_variant,
                "failure_mode": point.failure_mode,
                "capacity_reduction_factor": point.capacity_reduction_factor,
                "rep": r,
                "seed": seed,
            }, bus, multi))
            count += 1
            if verbose and count % 50 == 0:
                print(f"  Phase 2: {count}/{total}")

    return pd.DataFrame(results)


def save_results(df: pd.DataFrame, path: str | Path) -> None:
    """Save results DataFrame to CSV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Results saved to {output_path} ({len(df)} rows)")


class _ContextCache:
    """Cache variant/failure-specific scenario configs and graphs."""

    def __init__(self, config: dict, provided_graph: nx.DiGraph | None = None) -> None:
        self.config = config
        self.provided_graph = provided_graph
        self._cache: dict[tuple[str, str, float | None], tuple[dict, nx.DiGraph]] = {}

    def get(
        self,
        network_variant: str,
        failure_mode: str,
        capacity_reduction_factor: float | None,
    ) -> tuple[dict, nx.DiGraph]:
        key = (network_variant, failure_mode, capacity_reduction_factor)
        if key not in self._cache:
            run_config = _config_for_context(
                self.config,
                network_variant,
                failure_mode,
                capacity_reduction_factor,
            )
            graph = self._provided_graph_for(network_variant) or build_network(run_config)
            self._cache[key] = (run_config, graph)
        return self._cache[key]

    def _provided_graph_for(self, network_variant: str) -> nx.DiGraph | None:
        if self.provided_graph is None:
            return None
        if self.provided_graph.graph.get("network_variant") != network_variant:
            return None
        return self.provided_graph


def _config_for_context(
    config: dict,
    network_variant: str,
    failure_mode: str,
    capacity_reduction_factor: float | None,
) -> dict:
    """Return a config resolved to one network variant and failure semantics."""
    run_config = config_for_network_variant(config, network_variant)
    run_config["failure"] = deepcopy(run_config.get("failure", {}))
    run_config["failure"]["mode"] = failure_mode
    if capacity_reduction_factor is not None:
        run_config["failure"]["capacity_reduction_factor"] = capacity_reduction_factor
    return run_config


def _paired_result_row(base: dict, bus: dict, multi: dict) -> dict:
    """Build one paired replication row from scenario KPI dictionaries."""
    row = dict(base)
    for source_key, output_name in SCENARIO_KPI_COLUMNS.items():
        row[f"bus_{output_name}"] = _numeric_value(bus.get(source_key, np.nan))
        row[f"multi_{output_name}"] = _numeric_value(multi.get(source_key, np.nan))
        if source_key in DELTA_KPIS:
            row[DELTA_KPIS[source_key]] = _safe_delta(
                bus.get(source_key, np.nan),
                multi.get(source_key, np.nan),
            )

    return row


def _numeric_value(value) -> float:
    """Convert numeric KPI-like values while preserving non-finite markers."""
    if value is None:
        return float("nan")
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _safe_delta(left, right) -> float:
    """Return left-right, using NaN when both sides are the same infinity."""
    left_value = _numeric_value(left)
    right_value = _numeric_value(right)
    if np.isnan(left_value) or np.isnan(right_value):
        return float("nan")
    if (
        not np.isfinite(left_value)
        and not np.isfinite(right_value)
        and np.sign(left_value) == np.sign(right_value)
    ):
        return float("nan")
    return float(left_value - right_value)
